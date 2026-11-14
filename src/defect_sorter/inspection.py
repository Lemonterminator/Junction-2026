"""Defect decision from an anomaly score: normal, defective, or uncertain.

The loop never feeds a raw anomaly score to the action policy. :func:`decide` turns a score into one of three labels
with an explicit threshold and an optional uncertain band around it; a missing, non-finite or failed score is
``uncertain``, which the loop answers by observing again rather than by guessing. :class:`OpenVinoScorer` reads the
``pred_score`` output of an Anomalib model exported to OpenVINO (Anomalib normalises it so that 0.5 is the
model's own threshold); OpenVINO is imported only when a scorer is created.

The ``train`` command fits Padim on a folder of good crops and exports it to OpenVINO (``anomaly`` extra)::

	uv run --extra anomaly python -m defect_sorter.inspection train --data artifacts/twin/crops --out artifacts/twin/padim
"""

from __future__ import annotations

import argparse
import logging
import math
from collections.abc import Callable
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
		model.reshape({model.inputs[0].any_name: [1, 3, INPUT_SIZE, INPUT_SIZE]})
		config = {"INFERENCE_PRECISION_HINT": "f32"} if device.startswith("GPU") else {}
		self._compiled = core.compile_model(model, device, config)
		self._output = self._compiled.output("pred_score")
		self.name = f"{model_xml.parent.name}@{device}"

	def __call__(self, rgb: np.ndarray) -> float:
		"""Score one RGB uint8 crop."""
		return float(np.asarray(self._compiled(to_model_input(rgb))[self._output]).ravel()[0])


def train_padim(data: Path, out: Path) -> Path:
	"""Fit Padim on ``data/train/good`` (tested on ``data/test/{good,defect}``) and export it to OpenVINO.

	Returns
	-------
	Path
		The exported ``model.xml``.
	"""
	from anomalib.data import Folder
	from anomalib.deploy import ExportType
	from anomalib.engine import Engine
	from anomalib.models import Padim

	datamodule = Folder(
		name="twin",
		root=data,
		normal_dir="train/good",
		abnormal_dir="test/defect",
		normal_test_dir="test/good",
		train_batch_size=16,
		eval_batch_size=16,
		num_workers=0,
	)
	model = Padim(backbone="resnet18", layers=["layer1", "layer2"])
	engine = Engine(default_root_dir=out / "results", accelerator="cpu", devices=1, max_epochs=1)
	engine.fit(model=model, datamodule=datamodule)
	engine.test(model=model, datamodule=datamodule)
	return Path(engine.export(model=model, export_type=ExportType.OPENVINO, export_root=out / "export"))


def main(argv: list[str] | None = None) -> int:
	"""``train`` subcommand: fit and export Padim on a crop folder."""
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	sub = parser.add_subparsers(dest="command", required=True)
	train = sub.add_parser("train", help="fit Padim on good crops and export to OpenVINO")
	train.add_argument("--data", type=Path, required=True)
	train.add_argument("--out", type=Path, required=True)
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
	logger.info("exported %s", train_padim(args.data, args.out))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
