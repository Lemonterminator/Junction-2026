import cv2
import numpy as np

from defect_sorter.live_inspection import LiveInspector, purity_scorer


def _jpeg(image):
	ok, data = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 95])
	assert ok
	return data.tobytes()


def _brick(marked=False):
	"""Grey table, a solid red brick near the wrist-camera anchor, optionally with a black marker stripe."""
	image = np.full((480, 640, 3), 128, np.uint8)
	image[300:440, 270:430] = (30, 30, 220)
	if marked:
		image[340:400, 300:400] = (20, 20, 20)
	return image


class Ticks:
	"""Fake perf counter: every call advances by 1 ms, so each timed span is exactly measurable."""

	def __init__(self):
		self.t = 0.0

	def __call__(self):
		self.t += 0.001
		return self.t


def test_scores_the_isolated_brick_and_times_each_step():
	seen = []

	def scorer(rgb):
		seen.append(rgb.shape)
		return 0.8

	result = LiveInspector(scorer, threshold=0.5, device="NPU", model="padim", clock=Ticks()).inspect_jpeg(
		_jpeg(_brick())
	)
	assert seen == [(256, 256, 3)], "the scorer receives the 256 x 256 RGB crop"
	assert result["label"] == "defective"
	assert result["score"] == 0.8
	assert result["thresholds"] == {"normal_below": 0.5, "defective_above": 0.5}
	assert result["device"] == "NPU"
	assert result["model"] == "padim"
	# decode, isolate and inference are separate spans of two ticks each (start and end call).
	assert result["timings_ms"] == {"decode": 1.0, "isolate": 1.0, "inference": 1.0}
	assert result["crop_jpeg"][:2] == b"\xff\xd8"


def test_uncertain_band_and_normal_label():
	inspector = LiveInspector(lambda rgb: 0.45, threshold=0.5, band=0.1, model="m")
	assert inspector.inspect_jpeg(_jpeg(_brick()))["label"] == "uncertain"
	assert LiveInspector(lambda rgb: 0.2, threshold=0.5, model="m").inspect_jpeg(_jpeg(_brick()))["label"] == "normal"


def test_no_brick_or_failed_scorer_is_uncertain_without_a_score():
	empty = np.full((480, 640, 3), 128, np.uint8)
	result = LiveInspector(lambda rgb: 0.1, threshold=0.5, model="m").inspect_jpeg(_jpeg(empty))
	assert result["label"] == "uncertain"
	assert result["score"] is None
	assert result["reason"] == "no brick found in the frame"
	assert result["timings_ms"]["inference"] is None

	def broken(rgb):
		raise RuntimeError("device lost")

	failed = LiveInspector(broken, threshold=0.5, model="m").inspect_jpeg(_jpeg(_brick()))
	assert failed["label"] == "uncertain"
	assert failed["score"] is None
	assert "device lost" in failed["reason"]


def test_unreadable_jpeg_is_reported():
	result = LiveInspector(lambda rgb: 0.1, threshold=0.5, model="m").inspect_jpeg(b"not a jpeg")
	assert result["label"] == "uncertain"
	assert result["reason"] == "camera frame could not be decoded"


def test_purity_scorer_separates_a_solid_brick_from_a_marked_one():
	inspector = LiveInspector(purity_scorer(), threshold=0.1, model="colour-purity")
	clean = inspector.inspect_jpeg(_jpeg(_brick()))
	marked = inspector.inspect_jpeg(_jpeg(_brick(marked=True)))
	assert clean["label"] == "normal"
	assert clean["score"] < 0.1
	# The stripe covers 60 x 100 of the 140 x 160 brick, about 27 % of it.
	assert marked["label"] == "defective"
	assert 0.15 < marked["score"] < 0.4
