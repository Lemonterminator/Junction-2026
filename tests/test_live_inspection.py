import json

import cv2
import numpy as np
import pytest

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


# ------------------------------------------------------------------------------------------------ per-camera models


def _frame(value):
	"""A flat 640 x 480 frame whose brightness the fake model reads back as its score."""
	return _jpeg(np.full((480, 640, 3), value, np.uint8))


def _mean_model(batch):
	"""Fake PatchCore: the mean of the model input times 100, so a frame of value v scores about v / 255 * 100."""
	return float(batch.mean() * 100)


def _models(**thresholds):
	from defect_sorter.live_inspection import CameraModel

	roi = {"front": (40 / 640, 0.0, 560 / 640, 300 / 480), "wrist": (120 / 640, 330 / 480, 520 / 640, 1.0)}
	return {cam: CameraModel(cam, roi[cam], thr, _mean_model) for cam, thr in thresholds.items()}


class TestCameraRegion:
	def test_the_region_is_cut_resized_to_256_and_scaled_to_one_like_the_training_crops(self):
		from defect_sorter.live_inspection import roi_input

		image = np.zeros((480, 640, 3), np.uint8)
		image[0:300, 40:560] = (255, 0, 0)  # blue in BGR inside the front region, black outside
		x = roi_input(image, (40 / 640, 0.0, 560 / 640, 300 / 480))
		assert x.shape == (1, 3, 256, 256)
		assert x.dtype == np.float32
		np.testing.assert_allclose(x[0, 2].mean(), 1.0, atol=1e-6)  # RGB order: blue is the last channel
		np.testing.assert_allclose(x[0, :2].max(), 0.0, atol=1e-6)

	def test_the_region_scales_with_the_frame_size(self):
		from defect_sorter.live_inspection import roi_input

		small = np.zeros((240, 320, 3), np.uint8)
		small[0:150, 20:280] = 255
		np.testing.assert_allclose(roi_input(small, (40 / 640, 0.0, 560 / 640, 300 / 480)).mean(), 1.0, atol=1e-6)


class TestCameraVerdict:
	def test_within_ten_percent_of_the_threshold_is_unsure(self):
		from defect_sorter.live_inspection import camera_verdict

		assert camera_verdict(30.0, 40.0) == "normal"
		assert camera_verdict(37.0, 40.0) == "uncertain"
		assert camera_verdict(43.0, 40.0) == "uncertain"
		assert camera_verdict(45.0, 40.0) == "defective"


class TestCameraModelInspector:
	def test_each_camera_takes_its_worst_frame_against_its_own_threshold(self):
		from defect_sorter.live_inspection import CameraModelInspector

		inspector = CameraModelInspector(_models(front=40.0, wrist=60.0), device="NPU", clock=Ticks())
		result = inspector.inspect({"front": [_frame(60), _frame(120)], "wrist": [_frame(120)]})
		front, wrist = result["cameras"]["front"], result["cameras"]["wrist"]
		assert front["score"] == pytest.approx(120 / 255 * 100, abs=0.6)
		assert front["frames"] == 2
		assert front["verdict"] == "defective"  # 47 > 40 * 1.1
		assert wrist["verdict"] == "normal"  # 47 < 60 * 0.9
		assert result["label"] == "defective"
		assert result["score"] == pytest.approx(front["score"] / 40.0 / 2, abs=1e-6), (
			"the worst camera, 0.5 at its threshold"
		)
		assert result["thresholds"] == {"normal_below": 0.45, "defective_above": 0.55}
		assert result["device"] == "NPU"
		assert result["timings_ms"]["inference"] > 0
		assert result["crop_jpeg"][:2] == b"\xff\xd8"

	def test_all_cameras_clear_is_normal(self):
		from defect_sorter.live_inspection import CameraModelInspector

		result = CameraModelInspector(_models(front=60.0, wrist=60.0)).inspect(
			{"front": [_frame(60)], "wrist": [_frame(60)]}
		)
		assert result["label"] == "normal"

	def test_a_camera_without_frames_makes_the_view_unsure(self):
		from defect_sorter.live_inspection import CameraModelInspector

		result = CameraModelInspector(_models(front=60.0, wrist=60.0)).inspect({"front": [_frame(60)], "wrist": []})
		assert result["label"] == "uncertain"
		assert "wrist" in result["reason"]
		assert result["cameras"]["wrist"]["verdict"] == "uncertain"

	def test_an_unreadable_frame_or_a_model_error_is_unsure_not_a_crash(self):
		from defect_sorter.live_inspection import CameraModel, CameraModelInspector

		def broken(batch):
			raise RuntimeError("NPU lost")

		inspector = CameraModelInspector({"front": CameraModel("front", (0.0, 0.0, 1.0, 1.0), 40.0, broken)})
		result = inspector.inspect({"front": [b"not a jpeg", _frame(60)]})
		assert result["label"] == "uncertain"
		assert result["score"] is None
		assert "NPU lost" in result["reason"]


def test_camera_models_load_from_the_training_summary(tmp_path):
	from defect_sorter.live_inspection import load_camera_models

	(tmp_path / "summary.json").write_text(
		json.dumps(
			{
				"cameras": {
					"front": {"export": "f.xml", "threshold": 43.5},
					"wrist": {"export": "w.xml", "threshold": 40.2},
				}
			}
		)
	)
	compiled = []

	def compile_model(path, device):
		compiled.append((path, device))
		return _mean_model

	models = load_camera_models(tmp_path / "summary.json", "NPU", compile_model=compile_model)
	assert sorted(models) == ["front", "wrist"]
	assert models["front"].threshold == pytest.approx(43.5)
	assert models["wrist"].roi == pytest.approx((120 / 640, 330 / 480, 520 / 640, 1.0))
	assert compiled == [(tmp_path / "f.xml", "NPU"), (tmp_path / "w.xml", "NPU")], "relative exports sit next to it"
