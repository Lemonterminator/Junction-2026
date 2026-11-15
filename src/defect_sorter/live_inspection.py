"""Inspect the newest camera frame for the dashboard: isolate the brick, score it, and time every step.

:class:`LiveInspector` wraps :mod:`defect_sorter.inspection` for one JPEG at a time, as a camera relay delivers it.
Decoding, brick isolation and model inference are timed separately, so the dashboard can show inference latency
on its own instead of a combined number. Nothing is guessed: no brick, an unreadable frame or a scorer error gives
an ``uncertain`` label with no score and a reason.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
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
