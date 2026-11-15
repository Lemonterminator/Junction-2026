import math

import numpy as np
import pytest

from defect_sorter.inspection import (
	DefectDecision,
	IsolateConfig,
	ThresholdInspector,
	choose_threshold,
	crop_around,
	decide,
	grouped_folds,
	isolate_object,
	off_colour_fraction,
)

ORANGE = (0, 120, 255)  # BGR, OpenCV hue about 14
GREY = (150, 150, 150)
JAW_BLUE = (200, 80, 20)  # BGR, OpenCV hue about 113
BACKGROUND = (235, 235, 235)


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


def wrist_scene(*, patch: bool = False, bowl: bool = False) -> np.ndarray:
	"""640 x 480 BGR: white table with grey tape scraps, blue jaws, an orange brick at x, y 300-400."""
	img = np.full((480, 640, 3), BACKGROUND, np.uint8)
	img[50:80, 50:120] = (110, 110, 110)  # tape scrap on the table
	img[420:450, 560:620] = (110, 110, 110)
	img[300:480, 230:290] = JAW_BLUE
	img[300:480, 410:470] = JAW_BLUE
	img[300:400, 300:400] = ORANGE
	if patch:
		img[340:360, 330:370] = GREY  # tape inside the brick's outline
	if bowl:
		img[0:200, 440:640] = (60, 160, 40)  # large green bowl far from the anchor
	return img


class TestIsolateObject:
	def test_keeps_the_brick_and_tape_on_it_and_drops_table_tape_and_jaws(self):
		obj = isolate_object(wrist_scene(patch=True), IsolateConfig(dilate_px=0, size=100))
		assert obj is not None
		x, y, side = obj.box
		assert (x, y, side) == (300, 300, 100)
		assert obj.mask[50, 50]  # the grey patch stays inside the hull of the orange pixels
		assert obj.mask.mean() == pytest.approx(1.0, abs=0.05)
		assert tuple(obj.crop[50, 50]) == GREY

	def test_fills_everything_outside_the_object_with_a_constant(self):
		img = wrist_scene()
		img[300:400, 360:400] = BACKGROUND  # brick 60 wide, 100 tall: the square box shows table beside it
		img[330:340, 300:320] = (110, 110, 110)  # a dark notch would be off-colour, not background
		obj = isolate_object(img, IsolateConfig(dilate_px=0, size=100))
		assert obj is not None
		assert obj.crop.shape == (100, 100, 3)
		assert obj.box == (280, 300, 100)  # square box centred on the 60 x 100 brick
		assert obj.mask[:, 25:75].all()
		assert not obj.mask[:, :15].any()
		assert not obj.mask[:, 85:].any()
		assert np.all(obj.crop[~obj.mask] == 128)

	def test_core_region_keeps_tape_that_covers_a_whole_side_of_the_brick(self):
		img = wrist_scene()
		img[350:400, 300:400] = GREY  # lower half of the brick taped: outside the hull of the orange pixels
		without = isolate_object(img, IsolateConfig(dilate_px=0, size=100))
		assert without is not None
		assert without.box == (300, 275, 100)  # hull covers only the orange rows 300-350
		core = IsolateConfig(dilate_px=0, size=100, core=(350 / 640, 362 / 480, 45 / 640, 35 / 480))
		with_core = isolate_object(img, core)
		assert with_core is not None
		x, y, side = with_core.box
		assert y + side >= 395  # the taped rows are inside the kept region
		row = 380 - y  # source row in the taped half, mapped to the crop
		col = 350 - x
		scale = 100 / side
		assert with_core.mask[int(row * scale), int(col * scale)]
		assert tuple(with_core.crop[int(row * scale), int(col * scale)]) == GREY

	def test_prefers_the_object_near_the_anchor_over_a_larger_far_one(self):
		obj = isolate_object(wrist_scene(bowl=True), IsolateConfig(dilate_px=0))
		assert obj is not None
		assert obj.box[:2] == (300, 300)

	def test_no_saturated_object_gives_none(self):
		img = np.full((480, 640, 3), BACKGROUND, np.uint8)
		img[300:480, 230:290] = JAW_BLUE  # jaws alone are excluded by hue
		assert isolate_object(img) is None


class TestOffColourFraction:
	def test_plain_brick_is_pure(self):
		crop = np.full((100, 100, 3), ORANGE, np.uint8)
		assert off_colour_fraction(crop, np.ones((100, 100), bool), erode_px=0) == pytest.approx(0.0)

	def test_grey_patch_counts_by_its_area(self):
		crop = np.full((100, 100, 3), ORANGE, np.uint8)
		crop[:, :10] = GREY
		assert off_colour_fraction(crop, np.ones((100, 100), bool), erode_px=0) == pytest.approx(0.10)

	def test_dark_marker_cross_counts(self):
		crop = np.full((100, 100, 3), ORANGE, np.uint8)
		crop[45:55, :] = (20, 20, 20)
		crop[:, 45:55] = (20, 20, 20)
		assert off_colour_fraction(crop, np.ones((100, 100), bool), erode_px=0) == pytest.approx(0.19)

	def test_shading_of_the_same_hue_is_not_off_colour(self):
		v = np.linspace(130, 255, 100).astype(np.uint8)
		hsv = np.zeros((100, 100, 3), np.uint8)
		hsv[..., 0] = 14
		hsv[..., 1] = 255
		hsv[..., 2] = v[None, :]
		import cv2

		crop = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
		assert off_colour_fraction(crop, np.ones((100, 100), bool), erode_px=0) == pytest.approx(0.0)

	def test_only_pixels_inside_the_mask_count(self):
		crop = np.full((100, 100, 3), ORANGE, np.uint8)
		crop[:, :50] = GREY
		mask = np.zeros((100, 100), bool)
		mask[:, 50:] = True
		assert off_colour_fraction(crop, mask, erode_px=0) == pytest.approx(0.0)
		assert off_colour_fraction(crop, np.zeros((100, 100), bool)) is None


class TestGroupedFolds:
	def test_every_group_lands_in_one_fold_and_labels_spread_evenly(self):
		groups = [f"ep{i}" for i in range(35)]
		labels = ["normal"] * 23 + ["defective"] * 12
		folds = grouped_folds(groups, labels, k=5, seed=0)
		assert set(folds) == set(groups)
		assert set(folds.values()) == set(range(5))
		for f in range(5):
			members = [g for g in groups if folds[g] == f]
			defects = sum(labels[groups.index(g)] == "defective" for g in members)
			assert defects in (2, 3)
			assert len(members) in (7,)

	def test_repeated_frames_of_one_group_share_a_fold(self):
		folds = grouped_folds(["a", "a", "b", "c"], ["normal", "normal", "defective", "normal"], k=2, seed=1)
		assert set(folds) == {"a", "b", "c"}

	def test_conflicting_labels_for_one_group_are_rejected(self):
		with pytest.raises(ValueError, match="more than one label"):
			grouped_folds(["a", "a"], ["normal", "defective"], k=2, seed=0)


class TestChooseThreshold:
	def test_separable_scores_give_a_threshold_between_the_classes(self):
		t = choose_threshold([0.1, 0.2, 0.3], [0.5, 0.6])
		assert 0.3 < t <= 0.5
		assert decide(0.5, t) == "defective"
		assert decide(0.3, t) == "normal"

	def test_overlap_maximises_balanced_accuracy_and_ties_favour_catching_defects(self):
		# 0.45 passes all normals and catches one defect (0.75); 0.25 catches both and flags one normal (0.83)
		t = choose_threshold([0.1, 0.2, 0.4], [0.3, 0.5])
		assert decide(0.3, t) == "defective"
		assert decide(0.2, t) == "normal"

	def test_needs_both_classes(self):
		with pytest.raises(ValueError, match="both classes"):
			choose_threshold([0.1], [])


def _mean_model(path, batch):
	"""OpenVINO model: input [batch, 3, ?, ?] -> pred_score = per-image mean.

	The batch is baked into a Reshape constant, as in the PatchCore export, so the model only runs at that batch.
	"""
	ov = pytest.importorskip("openvino")
	ops = pytest.importorskip("openvino.opset13")
	param = ops.parameter(ov.PartialShape([batch, 3, -1, -1]), ov.Type.f32, name="input")
	flat = ops.reshape(param, ops.constant(np.array([batch, -1], dtype=np.int64)), special_zero=False)
	mean = ops.reduce_mean(flat, ops.constant(np.array([1], dtype=np.int64)), keep_dims=False)
	mean.output(0).get_tensor().set_names({"pred_score"})
	model = ov.Model([mean], [param], "mean")
	ov.save_model(model, str(path))
	return path


@pytest.mark.parametrize("batch", [1, 2])
def test_openvino_scorer_keeps_a_fixed_export_batch_and_scores_one_crop(tmp_path, batch):
	from defect_sorter.inspection import OpenVinoScorer

	scorer = OpenVinoScorer(_mean_model(tmp_path / "model.xml", batch), "CPU")
	assert scorer.input_shape == (batch, 3, 256, 256)  # the export's own batch, only the image size is fixed
	crop = np.full((40, 30, 3), 51, np.uint8)  # 51 / 255 = 0.2 after scaling to [0, 1]
	assert scorer(crop) == pytest.approx(0.2, abs=1e-4)


def test_training_rejects_an_unknown_model_before_loading_anomalib(tmp_path):
	from defect_sorter.inspection import MODELS, train_padim

	assert MODELS == ("padim", "patchcore")
	with pytest.raises(ValueError, match="unknown model"):
		train_padim(tmp_path, tmp_path, "resnet")
