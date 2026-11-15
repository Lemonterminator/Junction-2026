"""Defect decision from an anomaly score: normal, defective, or uncertain.

The loop never feeds a raw anomaly score to the action policy. :func:`decide` turns a score into one of three labels
with an explicit threshold and an optional uncertain band around it; a missing, non-finite or failed score is
``uncertain``, which the loop answers by observing again rather than by guessing. :class:`OpenVinoScorer` reads the
``pred_score`` output of an Anomalib model exported to OpenVINO (Anomalib normalises it so that 0.5 is the
model's own threshold); OpenVINO is imported only when a scorer is created.

A brick counts as defective when it is not one solid colour (tape, marker marks). Before scoring, :func:`isolate_object`
keeps only the brick: the table is covered in the same grey tape that marks a defect, so removing "tape" would also
remove the defect. The object is found by saturation, and the convex hull of its saturated pixels is kept, which
keeps grey tape inside the brick's outline. :func:`off_colour_fraction` is a transparent colour-purity score on that
crop, used as a baseline next to Padim. :func:`grouped_folds` and :func:`choose_threshold` support evaluations where
frames of one episode never cross a split and the threshold is chosen on data the test never sees.

The ``train`` command fits Padim on a folder of good crops and exports it to OpenVINO (``anomaly`` extra)::

	uv run --extra anomaly python -m defect_sorter.inspection train --data artifacts/twin/crops --out artifacts/twin/padim
"""

from __future__ import annotations

import argparse
import logging
import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np

logger = logging.getLogger(__name__)

Label = Literal["normal", "defective", "uncertain"]
INPUT_SIZE = 256


@dataclass(frozen=True)
class DefectDecision:
	"""One inspection result.

	Parameters
	----------
	label : {"normal", "defective", "uncertain"}
		Decision used by the loop.
	score : float or None
		Raw score from the scorer, or None when no score was produced.
	threshold : float
		Threshold the score was compared with.
	model : str
		Identifier of the scorer, recorded for traceability.
	"""

	label: Label
	score: float | None
	threshold: float
	model: str


def decide(score: float | None, threshold: float, band: float = 0.0) -> Label:
	"""Label a score: ``defective`` at or above ``threshold + band``, ``normal`` below ``threshold - band``.

	Scores inside the band, and missing or non-finite scores, are ``uncertain``. With ``band = 0`` a score equal to
	the threshold counts as defective, so a borderline brick is never passed as good.
	"""
	if score is None or not math.isfinite(score):
		return "uncertain"
	if band > 0 and abs(score - threshold) <= band:
		return "uncertain"
	return "defective" if score >= threshold else "normal"


class ThresholdInspector:
	"""Score a crop with any callable and label it with :func:`decide`.

	Parameters
	----------
	scorer : callable
		Maps an image (H x W x 3 array) to an anomaly score.
	threshold, band : float
		Decision threshold and half-width of the uncertain band.
	model : str
		Identifier recorded in every decision.
	"""

	def __init__(
		self, scorer: Callable[[np.ndarray], float], threshold: float, band: float = 0.0, model: str = "unnamed"
	) -> None:
		self._scorer = scorer
		self.threshold = threshold
		self.band = band
		self.model = model

	def inspect(self, crop: np.ndarray | None) -> DefectDecision:
		"""Decide on one crop; no crop or a scorer error gives ``uncertain`` with no score."""
		score: float | None = None
		if crop is not None:
			try:
				score = float(self._scorer(crop))
			except Exception:  # an inspection failure must stop the action, not crash the loop
				logger.exception("anomaly scorer %s failed", self.model)
		return DefectDecision(decide(score, self.threshold, self.band), score, self.threshold, self.model)


def crop_around(image: np.ndarray, centre_px: tuple[int, int], half: int) -> np.ndarray | None:
	"""Square ``2*half`` window centred on ``(x, y)``, or None when it would leave the image."""
	x, y = centre_px
	if x - half < 0 or y - half < 0 or x + half > image.shape[1] or y + half > image.shape[0]:
		return None
	return image[y - half : y + half, x - half : x + half]


@dataclass(frozen=True)
class IsolateConfig:
	"""Settings of :func:`isolate_object`; defaults fit the wrist camera with a held brick.

	Parameters
	----------
	min_saturation, min_value : int
		OpenCV HSV limits (0-255) for a pixel to count as brick colour.
	excluded_hues : tuple of (int, int)
		Inclusive OpenCV hue ranges (0-179) never taken as the object, such as the blue gripper jaws.
	min_area_px : int
		Smallest saturated component considered.
	anchor : tuple of float
		Expected object centre as a fraction of image width and height.
	distance_scale_px : float
		Distance from the anchor at which a component's area counts half.
	dilate_px : int
		Growth of the hull, so tape on the brick's corners stays in the crop.
	fill : int
		Grey value written outside the kept region.
	size : int
		Side of the square output crop.
	core : tuple of float or None
		Ellipse ``(cx, cy, rx, ry)`` as fractions of image width and height that is always kept, whatever its
		colour. With the wrist camera a held brick sits at the same place in every frame, so the core keeps tape
		that covers a whole side, which the hull of the coloured pixels alone would cut off.
	"""

	min_saturation: int = 90
	min_value: int = 60
	excluded_hues: tuple[tuple[int, int], ...] = ((104, 135),)
	min_area_px: int = 1500
	anchor: tuple[float, float] = (0.55, 0.8)
	distance_scale_px: float = 150.0
	dilate_px: int = 3
	fill: int = 128
	size: int = INPUT_SIZE
	core: tuple[float, float, float, float] | None = None


@dataclass(frozen=True)
class IsolatedObject:
	"""Result of :func:`isolate_object`.

	Parameters
	----------
	crop : numpy.ndarray
		``size`` x ``size`` x 3 BGR image, ``fill`` outside the kept region.
	mask : numpy.ndarray
		``size`` x ``size`` bool, the kept region (dilated hull) in crop coordinates.
	box : tuple of int
		Square source window ``(x, y, side)``; it may extend past the image, padded with ``fill``.
	area_px : int
		Saturated pixels of the chosen component in the source image.
	"""

	crop: np.ndarray
	mask: np.ndarray
	box: tuple[int, int, int]
	area_px: int


def _colour_pixels(hsv: np.ndarray, min_saturation: int, min_value: int) -> np.ndarray:
	return (hsv[..., 1] >= min_saturation) & (hsv[..., 2] >= min_value)


def isolate_object(bgr: np.ndarray, cfg: IsolateConfig | None = None) -> IsolatedObject | None:
	"""Square crop of the saturated object nearest ``cfg.anchor``, everything outside its hull set to ``cfg.fill``.

	Components are ranked by area divided by ``1 + (distance / distance_scale_px) ** 2``, so a large bowl at the
	image edge loses to the brick between the jaws. Returns None when no component is large enough.
	"""
	import cv2

	cfg = cfg or IsolateConfig()
	hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
	colour = _colour_pixels(hsv, cfg.min_saturation, cfg.min_value)
	for lo, hi in cfg.excluded_hues:
		colour &= ~((hsv[..., 0] >= lo) & (hsv[..., 0] <= hi))
	binary = cv2.morphologyEx(colour.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
	count, labels, stats, centres = cv2.connectedComponentsWithStats(binary)
	h, w = binary.shape
	ax, ay = cfg.anchor[0] * w, cfg.anchor[1] * h
	best, best_score = 0, -1.0
	for k in range(1, count):
		area = int(stats[k, cv2.CC_STAT_AREA])
		if area < cfg.min_area_px:
			continue
		d = math.hypot(centres[k][0] - ax, centres[k][1] - ay) / cfg.distance_scale_px
		score = area / (1.0 + d * d)
		if score > best_score:
			best, best_score = k, score
	if best == 0:
		return None
	hull = cv2.convexHull(cv2.findNonZero((labels == best).astype(np.uint8)))
	mask = np.zeros((h, w), np.uint8)
	cv2.fillConvexPoly(mask, hull, 1)
	if cfg.core is not None:
		cx, cy, rx, ry = cfg.core
		centre = (round(cx * w), round(cy * h))
		axes = (max(1, round(rx * w)), max(1, round(ry * h)))
		cv2.ellipse(mask, centre, axes, 0, 0, 360, 1, thickness=-1)
	if cfg.dilate_px > 0:
		side_k = 2 * cfg.dilate_px + 1
		mask = cv2.dilate(mask, np.ones((side_k, side_k), np.uint8))
	x, y, bw, bh = cv2.boundingRect(mask)
	side = max(bw, bh)
	x0, y0 = x + bw // 2 - side // 2, y + bh // 2 - side // 2
	kept = np.where(mask[..., None] > 0, bgr, np.uint8(cfg.fill))
	padded = cv2.copyMakeBorder(kept, side, side, side, side, cv2.BORDER_CONSTANT, value=(cfg.fill,) * 3)
	padded_mask = cv2.copyMakeBorder(mask, side, side, side, side, cv2.BORDER_CONSTANT, value=0)
	window = (slice(y0 + side, y0 + 2 * side), slice(x0 + side, x0 + 2 * side))
	crop = cv2.resize(padded[window], (cfg.size, cfg.size), interpolation=cv2.INTER_AREA)
	crop_mask = cv2.resize(padded_mask[window], (cfg.size, cfg.size), interpolation=cv2.INTER_NEAREST) > 0
	crop[~crop_mask] = cfg.fill
	return IsolatedObject(crop, crop_mask, (int(x0), int(y0), int(side)), int(stats[best, cv2.CC_STAT_AREA]))


def off_colour_fraction(
	bgr: np.ndarray,
	mask: np.ndarray,
	min_saturation: int = 90,
	min_value: int = 60,
	hue_tol: int = 12,
	erode_px: int = 3,
) -> float | None:
	"""Share of masked pixels that are not the object's dominant colour; None for an empty mask.

	The dominant hue is the most common hue among saturated pixels. A pixel is off-colour when it is grey or
	white (low saturation), dark (low value, such as a marker line) or of another hue. Brightness changes of the
	same hue, such as shading, are not off-colour. The mask is eroded by ``erode_px`` so the hull's boundary,
	which can include background, does not count.
	"""
	import cv2

	region = mask.astype(np.uint8)
	if erode_px > 0:
		side_k = 2 * erode_px + 1
		region = cv2.erode(region, np.ones((side_k, side_k), np.uint8))
	inside = region > 0
	if not inside.any():
		return None
	hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
	colour = _colour_pixels(hsv, min_saturation, min_value) & inside
	if not colour.any():
		return 1.0
	hue = hsv[..., 0].astype(int)
	dominant = int(np.argmax(np.bincount(hue[colour], minlength=180)))
	diff = np.abs(hue - dominant)
	same = colour & (np.minimum(diff, 180 - diff) <= hue_tol)
	return float(1.0 - same[inside].mean())


def grouped_folds(groups: Sequence[str], labels: Sequence[str], k: int, seed: int) -> dict[str, int]:
	"""Assign each group (such as an episode) to one of ``k`` folds, spreading every label evenly.

	Groups of each label are shuffled with ``seed`` and dealt round-robin, the next label continuing where the
	previous one stopped, so fold sizes differ by at most one. A group with two labels raises ``ValueError``.
	"""
	label_of: dict[str, str] = {}
	for g, lab in zip(groups, labels, strict=True):
		if label_of.setdefault(g, lab) != lab:
			raise ValueError(f"group {g!r} has more than one label")
	rng = np.random.default_rng(seed)
	folds: dict[str, int] = {}
	slot = 0
	for lab in sorted(set(label_of.values())):
		members = sorted(g for g, gl in label_of.items() if gl == lab)
		for i in rng.permutation(len(members)):
			folds[members[i]] = slot % k
			slot += 1
	return folds


def choose_threshold(normal_scores: Sequence[float], defect_scores: Sequence[float]) -> float:
	"""Threshold with the best balanced accuracy for "defective at or above"; ties take the lowest threshold.

	Candidates are the midpoints between neighbouring distinct scores, so the result never sits on a sample.
	The lowest of equally good thresholds is taken because passing a defective brick costs more than a recheck.
	"""
	normal = np.asarray(normal_scores, dtype=float)
	defect = np.asarray(defect_scores, dtype=float)
	if normal.size == 0 or defect.size == 0:
		raise ValueError("choose_threshold needs scores of both classes")
	values = np.unique(np.concatenate([normal, defect]))
	candidates = np.concatenate([[values[0] - 1e-6], (values[:-1] + values[1:]) / 2, [values[-1] + 1e-6]])
	best_t, best_acc = float(candidates[0]), -1.0
	for t in candidates:
		acc = 0.5 * (float(np.mean(defect >= t)) + float(np.mean(normal < t)))
		if acc > best_acc + 1e-12:
			best_t, best_acc = float(t), acc
	return best_t


def to_model_input(rgb: np.ndarray, size: int = INPUT_SIZE) -> np.ndarray:
	"""RGB uint8 H x W x 3 → float32 1 x 3 x size x size in [0, 1], the layout Anomalib exports expect."""
	import cv2

	resized = cv2.resize(rgb, (size, size), interpolation=cv2.INTER_AREA)
	return (resized.astype(np.float32) / 255.0).transpose(2, 0, 1)[None]


class OpenVinoScorer:
	"""``pred_score`` of an Anomalib OpenVINO export, compiled for one device with a static input shape.

	Parameters
	----------
	model_xml : Path
		Exported ``model.xml``.
	device : str
		OpenVINO device. GPU needs ``f32`` precision for Padim: the default FP16 output is wrong (see
		``docs/infrastructure/HARDWARE_PROFILING.md``), so the hint is set for every GPU device.
	"""

	def __init__(self, model_xml: Path, device: str = "CPU") -> None:
		import openvino as ov

		core = ov.Core()
		model = core.read_model(model_xml)
		port = model.inputs[0]
		batch_dim = port.partial_shape[0]
		# Some exports (PatchCore) bake their trace batch into the graph; keep it and fix only the image size.
		batch = batch_dim.get_length() if batch_dim.is_static else 1
		self.input_shape = (batch, 3, INPUT_SIZE, INPUT_SIZE)
		model.reshape({port.any_name: list(self.input_shape)})
		config = {"INFERENCE_PRECISION_HINT": "f32"} if device.startswith("GPU") else {}
		self._compiled = core.compile_model(model, device, config)
		self._output = self._compiled.output("pred_score")
		self.name = f"{model_xml.parent.name}@{device}"

	def __call__(self, rgb: np.ndarray) -> float:
		"""Score one RGB uint8 crop (repeated to fill a fixed export batch)."""
		x = to_model_input(rgb)
		if self.input_shape[0] > 1:
			x = np.repeat(x, self.input_shape[0], axis=0)
		return float(np.asarray(self._compiled(x)[self._output]).ravel()[0])


MODELS = ("padim", "patchcore")


def train_padim(
	data: Path, out: Path, model_name: str = "padim", accelerator: str = "cpu", coreset_ratio: float = 0.1
) -> Path:
	"""Fit an Anomalib model on ``data/train/good`` (tested on ``data/test/{good,defect}``) and export it to OpenVINO.

	``model_name`` is ``padim`` (resnet18, layers 1-2) or ``patchcore`` (wide_resnet50, layers 2-3, coreset of
	``coreset_ratio`` of the training patches; the greedy coreset at 10 % takes about 25 min per fit on the CPU, so
	use ``accelerator="gpu"`` with a CUDA build of PyTorch for it). PatchCore keeps a memory bank of normal
	patches, so several brick colours do not have to share one Gaussian per position as in Padim.

	Returns
	-------
	Path
		The exported ``model.xml``.
	"""
	if model_name not in MODELS:
		raise ValueError(f"unknown model {model_name!r}, expected one of {MODELS}")
	from anomalib.data import Folder
	from anomalib.deploy import ExportType
	from anomalib.engine import Engine
	from anomalib.models import Padim, Patchcore

	datamodule = Folder(
		name="crops",
		root=data,
		normal_dir="train/good",
		abnormal_dir="test/defect",
		normal_test_dir="test/good",
		train_batch_size=16,
		eval_batch_size=16,
		num_workers=0,
	)
	if model_name == "padim":
		model = Padim(backbone="resnet18", layers=["layer1", "layer2"])
	else:
		model = Patchcore(backbone="wide_resnet50_2", layers=["layer2", "layer3"], coreset_sampling_ratio=coreset_ratio)
	engine = Engine(default_root_dir=out / "results", accelerator=accelerator, devices=1, max_epochs=1)
	engine.fit(model=model, datamodule=datamodule)
	engine.test(model=model, datamodule=datamodule)
	return Path(engine.export(model=model, export_type=ExportType.OPENVINO, export_root=out / "export"))


def main(argv: list[str] | None = None) -> int:
	"""``train`` subcommand: fit and export Padim on a crop folder."""
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	sub = parser.add_subparsers(dest="command", required=True)
	train = sub.add_parser("train", help="fit Padim or PatchCore on good crops and export to OpenVINO")
	train.add_argument("--data", type=Path, required=True)
	train.add_argument("--out", type=Path, required=True)
	train.add_argument("--model", choices=MODELS, default="padim")
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
	logger.info("exported %s", train_padim(args.data, args.out, args.model))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
