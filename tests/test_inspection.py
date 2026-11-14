import math

import numpy as np
import pytest

from defect_sorter.inspection import DefectDecision, ThresholdInspector, crop_around, decide


def test_decide_labels_scores_against_threshold_with_uncertain_band():
	assert decide(0.2, threshold=0.5, band=0.1) == "normal"
	assert decide(0.8, threshold=0.5, band=0.1) == "defective"
	assert decide(0.45, threshold=0.5, band=0.1) == "uncertain"
	assert decide(0.55, threshold=0.5, band=0.1) == "uncertain"


def test_decide_without_band_puts_threshold_on_the_defective_side():
	assert decide(0.5, threshold=0.5, band=0.0) == "defective"
	assert decide(0.4999, threshold=0.5, band=0.0) == "normal"


@pytest.mark.parametrize("score", [math.nan, math.inf, None])
def test_decide_marks_missing_or_invalid_scores_uncertain(score):
	assert decide(score, threshold=0.5, band=0.0) == "uncertain"


def test_threshold_inspector_records_score_threshold_and_model():
	inspector = ThresholdInspector(lambda image: float(image.mean()), threshold=0.5, band=0.05, model="mean-v1")
	decision = inspector.inspect(np.full((4, 4, 3), 0.9, dtype=np.float32))
	assert decision == DefectDecision(label="defective", score=pytest.approx(0.9), threshold=0.5, model="mean-v1")


def test_threshold_inspector_without_crop_is_uncertain_and_never_scores():
	calls = []
	inspector = ThresholdInspector(lambda image: calls.append(image) or 0.0, threshold=0.5)
	decision = inspector.inspect(None)
	assert decision.label == "uncertain"
	assert decision.score is None
	assert calls == []


def test_threshold_inspector_turns_scorer_failure_into_uncertain():
	def broken(image):
		raise RuntimeError("device lost")

	decision = ThresholdInspector(broken, threshold=0.5).inspect(np.zeros((4, 4, 3), np.uint8))
	assert decision.label == "uncertain"
	assert decision.score is None


def test_crop_around_returns_square_window_centred_on_pixel():
	image = np.arange(20 * 30).reshape(20, 30)
	crop = crop_around(image, (15, 10), half=3)
	assert crop.shape == (6, 6)
	assert crop[3, 3] == image[10, 15]


def test_crop_around_rejects_windows_leaving_the_image():
	image = np.zeros((20, 30))
	assert crop_around(image, (1, 10), half=3) is None
	assert crop_around(image, (15, 18), half=3) is None
