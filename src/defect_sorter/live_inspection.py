"""Inspect camera frames for the dashboard: one frame with brick isolation, or a show view with per-camera models.

:class:`LiveInspector` wraps :mod:`defect_sorter.inspection` for one JPEG at a time, as a camera relay delivers it.
:class:`CameraModelInspector` scores a show view the way the per-camera PatchCore models (inspect-v3) were trained:
a fixed region of each camera's frame, each camera against its own threshold.
Decoding, brick isolation and model inference are timed separately, so the dashboard can show inference latency
on its own instead of a combined number. Nothing is guessed: no brick, an unreadable frame or a scorer error gives
an ``uncertain`` label with no score and a reason.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from defect_sorter.inspection import IsolateConfig, decide, isolate_object, off_colour_fraction

logger = logging.getLogger(__name__)


def purity_scorer(cfg: IsolateConfig | None = None) -> Callable[[np.ndarray], float]:
	"""Colour-purity baseline as a scorer: the off-colour share of the isolated brick, 0 for one solid colour.

	It needs no model file. It works on the crop the inspector passes in (RGB, grey outside the brick), so it
	re-derives the brick mask from the crop's non-fill pixels.
	"""
	fill = (cfg or IsolateConfig()).fill

	def score(rgb: np.ndarray) -> float:
		mask = np.any(rgb != fill, axis=2)
		value = off_colour_fraction(rgb[..., ::-1].copy(), mask)
		if value is None:
			raise ValueError("empty brick mask")
		return value

	return score


class LiveInspector:
	"""Score one camera JPEG with a callable and label it against an explicit threshold.

	Parameters
	----------
	scorer : callable
		RGB uint8 crop to anomaly score (an :class:`~defect_sorter.inspection.OpenVinoScorer` or
		:func:`purity_scorer`).
	threshold, band : float
		Decision threshold and half-width of the uncertain band (see :func:`~defect_sorter.inspection.decide`).
	device : str or None
		Device the scorer was compiled for, as reported by its runtime; None when not applicable.
	model : str
		Identifier shown with every result.
	isolate : IsolateConfig or None
		Brick isolation settings.
	clock : callable
		High-resolution seconds (``time.perf_counter``).
	"""

	def __init__(
		self,
		scorer: Callable[[np.ndarray], float],
		threshold: float,
		band: float = 0.0,
		device: str | None = None,
		model: str = "unnamed",
		isolate: IsolateConfig | None = None,
		clock: Callable[[], float] = time.perf_counter,
	) -> None:
		self._scorer = scorer
		self.threshold = threshold
		self.band = band
		self.device = device
		self.model = model
		self._isolate = isolate
		self._clock = clock

	def _result(self, **values: Any) -> dict[str, Any]:
		base: dict[str, Any] = {
			"label": "uncertain",
			"score": None,
			"reason": None,
			"thresholds": {"normal_below": self.threshold - self.band, "defective_above": self.threshold + self.band},
			"device": self.device,
			"model": self.model,
			"timings_ms": {"decode": None, "isolate": None, "inference": None},
			"crop_jpeg": None,
		}
		base.update(values)
		return base

	def inspect_jpeg(self, jpeg: bytes) -> dict[str, Any]:
		"""Decode, isolate and score one frame.

		Returns
		-------
		dict
			``label``, ``score``, ``reason``, ``thresholds``, ``device``, ``model``, ``timings_ms`` (decode, isolate,
			inference; None for a step that did not run) and ``crop_jpeg`` (the scored crop, or None).
		"""
		import cv2

		timings: dict[str, float | None] = {"decode": None, "isolate": None, "inference": None}
		t0 = self._clock()
		bgr = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR) if jpeg else None
		timings["decode"] = round((self._clock() - t0) * 1000, 3)
		if bgr is None:
			return self._result(reason="camera frame could not be decoded", timings_ms=timings)
		t0 = self._clock()
		isolated = isolate_object(bgr, self._isolate)
		timings["isolate"] = round((self._clock() - t0) * 1000, 3)
		if isolated is None:
			return self._result(reason="no brick found in the frame", timings_ms=timings)
		ok, encoded = cv2.imencode(".jpg", isolated.crop, [cv2.IMWRITE_JPEG_QUALITY, 85])
		crop_jpeg = encoded.tobytes() if ok else None
		rgb = np.ascontiguousarray(isolated.crop[..., ::-1])
		try:
			t0 = self._clock()
			score = float(self._scorer(rgb))
			timings["inference"] = round((self._clock() - t0) * 1000, 3)
		except Exception as error:  # an inspection failure must hold the arm, not crash the server
			logger.exception("live scorer %s failed", self.model)
			return self._result(reason=f"scorer failed: {error}", timings_ms=timings, crop_jpeg=crop_jpeg)
		return self._result(
			label=decide(score, self.threshold, self.band), score=score, timings_ms=timings, crop_jpeg=crop_jpeg
		)


# ------------------------------------------------------------------------------------------------ per-camera models

UNSURE_MARGIN = 0.10
"""A camera's score within this fraction of its threshold is unsure, either side."""

INSPECT_V3_ROI: dict[str, tuple[float, float, float, float]] = {
	"front": (40 / 640, 0.0, 560 / 640, 300 / 480),
	"wrist": (120 / 640, 330 / 480, 520 / 640, 1.0),
}
"""Where the held brick is in each camera during the show (x0, y0, x1, y1 as fractions of the frame): the regions the
inspect-v3 PatchCore models were trained on (640 x 480 pixels 40..560 x 0..300 front, 120..520 x 330..480 wrist)."""


@dataclass(frozen=True)
class CameraModel:
	"""One camera's anomaly model.

	Parameters
	----------
	camera : str
		Camera key (``front``, ``wrist``).
	roi : tuple of float
		Region scored, ``(x0, y0, x1, y1)`` as fractions of the frame.
	threshold : float
		Raw score at which the brick counts as defective (chosen on the training run).
	score : callable
		Model input (1 x 3 x 256 x 256 float32 RGB in [0, 1]) to the raw ``pred_score``.
	"""

	camera: str
	roi: tuple[float, float, float, float]
	threshold: float
	score: Callable[[np.ndarray], float]


def roi_input(bgr: np.ndarray, roi: tuple[float, float, float, float], size: int = 256) -> np.ndarray:
	"""The model input for one frame: the region cut out, resized (bilinear) to ``size``, RGB in [0, 1], 1 x 3 x H x W.

	The same preprocessing the per-camera models were trained and thresholded with.
	"""
	import cv2

	h, w = bgr.shape[:2]
	x0, y0, x1, y1 = (round(f * n) for f, n in zip(roi, (w, h, w, h), strict=True))
	crop = cv2.resize(bgr[y0:y1, x0:x1], (size, size))
	return (cv2.cvtColor(crop, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0).transpose(2, 0, 1)[None]


def camera_verdict(score: float, threshold: float, margin: float = UNSURE_MARGIN) -> str:
	"""``defective`` above the threshold, ``normal`` below it, ``uncertain`` within ``margin`` of it either side."""
	if abs(score - threshold) < margin * threshold:
		return "uncertain"
	return "defective" if score > threshold else "normal"


_SEVERITY = {"normal": 0, "uncertain": 1, "defective": 2}


class CameraModelInspector:
	"""Score one show view from several cameras, each with its own model and threshold.

	Each camera takes its worst (highest) frame; a camera without a readable, scored frame is unsure. The view's
	label is the worst camera's. Its ``score`` puts every camera on one scale for the page: the worst camera's raw
	score divided by its threshold, halved, so 0.5 is the threshold and the unsure band is ``0.5 +- margin / 2``.

	Parameters
	----------
	models : dict
		Camera key to :class:`CameraModel`.
	margin : float
		Unsure band around each threshold, as a fraction of it.
	device : str or None
		Device the models run on, reported with every result.
	clock : callable
		High-resolution seconds.
	"""

	def __init__(
		self,
		models: dict[str, CameraModel],
		*,
		margin: float = UNSURE_MARGIN,
		device: str | None = None,
		model: str = "per-camera PatchCore",
		clock: Callable[[], float] = time.perf_counter,
	) -> None:
		self.models = models
		self.margin = margin
		self.device = device
		self.model = model
		self._clock = clock

	@property
	def thresholds(self) -> dict[str, float]:
		"""The unsure band on the page's scale."""
		return {"normal_below": round((1 - self.margin) / 2, 6), "defective_above": round((1 + self.margin) / 2, 6)}

	def inspect(self, frames: dict[str, list[bytes]]) -> dict[str, Any]:
		"""Score the JPEG frames of each camera.

		Returns
		-------
		dict
			``label``, ``score`` (see the class), ``reason``, ``thresholds``, ``cameras`` (per camera ``score``,
			``threshold``, ``verdict``, ``frames``), ``device``, ``model``, ``timings_ms`` (``inference``: mean per
			frame) and ``crop_jpeg`` (the first camera's scored region of its worst frame).
		"""
		import cv2

		cameras: dict[str, dict[str, Any]] = {}
		problems: list[str] = []
		spent, count = 0.0, 0
		crop_jpeg = None
		for camera, model in self.models.items():
			best: tuple[float, np.ndarray] | None = None
			for jpeg in frames.get(camera, []):
				bgr = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR) if jpeg else None
				if bgr is None:
					problems.append(f"{camera}: unreadable frame")
					continue
				try:
					t0 = self._clock()
					score = float(model.score(roi_input(bgr, model.roi)))
					spent += self._clock() - t0
					count += 1
				except Exception as error:  # the arm holds the brick; an inspection failure only makes it unsure
					logger.exception("%s model failed", camera)
					problems.append(f"{camera}: model failed: {error}")
					continue
				if best is None or score > best[0]:
					best = (score, bgr)
			if best is None:
				problems.append(f"no scored frame from {camera}")
				cameras[camera] = {"score": None, "threshold": model.threshold, "verdict": "uncertain", "frames": 0}
				continue
			cameras[camera] = {
				"score": round(best[0], 3),
				"threshold": model.threshold,
				"verdict": camera_verdict(best[0], model.threshold, self.margin),
				"frames": sum(1 for _ in frames.get(camera, [])),
			}
			if crop_jpeg is None:
				h, w = best[1].shape[:2]
				x0, y0, x1, y1 = (round(f * n) for f, n in zip(model.roi, (w, h, w, h), strict=True))
				ok, encoded = cv2.imencode(".jpg", best[1][y0:y1, x0:x1], [cv2.IMWRITE_JPEG_QUALITY, 85])
				crop_jpeg = encoded.tobytes() if ok else None
		label = max((c["verdict"] for c in cameras.values()), key=_SEVERITY.__getitem__, default="uncertain")
		ratios = [
			c["score"] / c["threshold"] for c in cameras.values() if c["score"] is not None and c["threshold"] > 0
		]
		return {
			"label": label,
			"score": round(max(ratios) / 2, 6) if ratios else None,
			"reason": "; ".join(problems) or None,
			"thresholds": self.thresholds,
			"cameras": cameras,
			"device": self.device,
			"model": self.model,
			"timings_ms": {"inference": round(spent / count * 1000, 3) if count else None},
			"crop_jpeg": crop_jpeg,
		}


def _openvino_score(model_xml: Path, device: str) -> Callable[[np.ndarray], float]:
	"""``pred_score`` of an Anomalib OpenVINO export, compiled with a static batch of 2 (the NPU needs a static shape)."""
	import openvino as ov

	core = ov.Core()
	model = core.read_model(model_xml)
	model.reshape({model.inputs[0].get_any_name(): [2, 3, 256, 256]})
	compiled = core.compile_model(model, device)
	output = compiled.output("pred_score")

	def score(batch: np.ndarray) -> float:
		return float(np.asarray(compiled(np.concatenate([batch, batch]))[output]).reshape(-1)[0])

	return score


def load_camera_models(
	summary: Path,
	device: str,
	*,
	roi: dict[str, tuple[float, float, float, float]] | None = None,
	compile_model: Callable[[Path, str], Callable[[np.ndarray], float]] = _openvino_score,
) -> dict[str, CameraModel]:
	"""Per-camera models from a training summary (``{"cameras": {cam: {"export": ..., "threshold": ...}}}``).

	A relative ``export`` path is taken next to the summary. Cameras without a known region are skipped with a
	warning.
	"""
	import json

	regions = roi or INSPECT_V3_ROI
	models = {}
	for camera, entry in json.loads(summary.read_text())["cameras"].items():
		if camera not in regions:
			logger.warning("no region known for camera %s; it is not inspected", camera)
			continue
		export = Path(entry["export"])
		if not export.is_absolute():
			export = summary.parent / export
		models[camera] = CameraModel(camera, regions[camera], float(entry["threshold"]), compile_model(export, device))
	return models
