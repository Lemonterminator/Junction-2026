import cv2
import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from defect_sorter.depth_bridge import layered_height_image
from defect_sorter.episode_calibration import (
	fit_touches,
	fit_touches_with_zeros,
	layered_height_m,
	normalized_to_degrees,
	point_at_height,
	rigid_fit,
	state_degrees,
	still_moments,
	tag_poses,
	touch_holds,
	video_file,
)
from defect_sorter.geometry import Intrinsics, Plane
from defect_sorter.joint_calibration import TICKS_PER_DEGREE
from defect_sorter.markers import marker_spec, render_marker_tile

# The D415 colour stream as the bridge reads it, and the bridge's crop.
INTR = Intrinsics(fx=605.2, fy=604.7, ppx=324.1, ppy=258.6)
SHAPE = (480, 640)
CROP = (96, 0, 512, 416)
# Camera above the table, looking down and forward like the cell's top camera; table frame = world here,
# because anchor 16 lies at the origin and anchor 17 on the +x axis.
CAMERA_W = np.array([0.14, -0.33, 0.42])
LOOK_AT_W = np.array([0.14, -0.05, 0.0])


def camera_rotation() -> np.ndarray:
	"""Columns: camera x (image right), y (image down), z (optical axis) in world coordinates."""
	z = LOOK_AT_W - CAMERA_W
	z /= np.linalg.norm(z)
	x = np.cross(z, [0.0, 0.0, 1.0])
	x /= np.linalg.norm(x)
	return np.stack([x, np.cross(z, x), z], axis=1)


R_WC = camera_rotation()
PLANE = Plane(normal=R_WC.T @ np.array([0.0, 0.0, 1.0]), offset=float(CAMERA_W[2]), inlier_fraction=1.0)


def to_camera(p_w: np.ndarray) -> np.ndarray:
	return R_WC.T @ (np.asarray(p_w) - CAMERA_W)


def render(tags: list[tuple[int, np.ndarray, np.ndarray]]) -> tuple[np.ndarray, np.ndarray]:
	"""Colour image and height-above-table map (m) for tags given as (id, rotation in world, centre in world)."""
	k = np.array([[INTR.fx, 0, INTR.ppx], [0, INTR.fy, INTR.ppy], [0, 0, 1]])
	color = np.full((*SHAPE, 3), 200, np.uint8)
	height = np.zeros(SHAPE, np.float64)
	for marker_id, r_wm, centre_w in tags:
		tile = render_marker_tile(marker_spec(marker_id), px_per_mm=20.0)
		half = tile.shape[0] / 20.0 / 1000.0 / 2.0
		corners_m = np.array([[-1, 1, 0], [1, 1, 0], [1, -1, 0], [-1, -1, 0]], dtype=np.float64) * half
		rvec, _ = cv2.Rodrigues(R_WC.T @ r_wm)
		img, _ = cv2.projectPoints(corners_m, rvec, to_camera(centre_w), k, None)
		src = np.array([[0, 0], [tile.shape[1], 0], [tile.shape[1], tile.shape[0]], [0, tile.shape[0]]], np.float32)
		h = cv2.getPerspectiveTransform(src, img.reshape(4, 2).astype(np.float32))
		warped = cv2.warpPerspective(tile, h, SHAPE[::-1], flags=cv2.INTER_LINEAR, borderValue=0)
		mask = cv2.warpPerspective(np.full(tile.shape, 255, np.uint8), h, SHAPE[::-1], flags=cv2.INTER_NEAREST) > 0
		color[mask] = warped[mask][:, None]
		height[mask] = centre_w[2]
	return color, height


def crop(image: np.ndarray) -> np.ndarray:
	x, y, w, h = CROP
	return image[y : y + h, x : x + w]


FLAT = np.eye(3)
ANCHORS = [(16, FLAT, np.array([0.0, 0.0, 0.0])), (17, FLAT, np.array([0.27, 0.0, 0.0]))]


class TestUnits:
	def test_normalized_body_joint_to_degrees_around_the_range_midpoint(self):
		assert normalized_to_degrees(0.0, 1000, 3000) == pytest.approx(0.0)
		assert normalized_to_degrees(100.0, 1000, 3000) == pytest.approx(1000 / TICKS_PER_DEGREE)
		assert normalized_to_degrees(-50.0, 1000, 3000) == pytest.approx(-500 / TICKS_PER_DEGREE)

	def test_state_vector_to_body_joint_degrees_without_the_gripper(self):
		names = ["shoulder_pan.pos", "shoulder_lift.pos", "gripper.pos"]
		ranges = {"shoulder_pan": (1000, 3000), "shoulder_lift": (900, 3100), "gripper": (2000, 3500)}

		got = state_degrees([10.0, -20.0, 55.0], names, ranges)

		assert set(got) == {"shoulder_pan", "shoulder_lift"}
		assert got["shoulder_pan"] == pytest.approx(100 / TICKS_PER_DEGREE)
		assert got["shoulder_lift"] == pytest.approx(-220 / TICKS_PER_DEGREE)


class TestHeights:
	def test_layered_image_decodes_back_to_metres(self):
		h = np.array([[0.0, 0.012, 0.035], [0.08, 0.21, np.nan]])
		img = layered_height_image(h, fine_max_m=0.04, coarse_max_m=0.30)

		got = layered_height_m(img)

		np.testing.assert_allclose(got[0], [0.0, 0.012, 0.035], atol=0.0002)  # fine channel: 0.16 mm steps
		np.testing.assert_allclose(got[1, :2], [0.08, 0.21], atol=0.0007)  # coarse channel: 1.2 mm steps
		assert np.isnan(got[1, 2])

	def test_a_point_at_a_known_height_is_found_on_its_pixel_ray(self):
		p_w = np.array([0.20, -0.10, 0.065])
		p_c = to_camera(p_w)
		u, v = INTR.fx * p_c[0] / p_c[2] + INTR.ppx, INTR.fy * p_c[1] / p_c[2] + INTR.ppy

		np.testing.assert_allclose(point_at_height(u, v, 0.065, INTR, PLANE), p_c, atol=1e-9)


class TestTagPoses:
	def test_a_raised_tilted_arm_tag_in_the_table_frame_from_the_cropped_recording(self):
		r_tag = Rotation.from_euler("xyz", [25, -10, 40], degrees=True).as_matrix()
		centre = np.array([0.16, -0.12, 0.09])
		color, height = render([*ANCHORS, (4, r_tag, centre)])
		depth_img = layered_height_image(height, fine_max_m=0.04, coarse_max_m=0.30)

		frame, tags = tag_poses(crop(color), crop(depth_img), intrinsics=INTR, crop_xy=CROP[:2], plane=PLANE)

		assert frame is not None
		r, p = tags[4]
		np.testing.assert_allclose(p, centre, atol=0.003)
		assert np.degrees(Rotation.from_matrix(r.T @ r_tag).magnitude()) < 3.0

	def test_without_both_anchors_there_is_no_table_frame(self):
		color, height = render([ANCHORS[0], (4, FLAT, np.array([0.16, -0.12, 0.05]))])
		depth_img = layered_height_image(height, fine_max_m=0.04, coarse_max_m=0.30)

		frame, tags = tag_poses(crop(color), crop(depth_img), intrinsics=INTR, crop_xy=CROP[:2], plane=PLANE)

		assert frame is None
		assert tags == {}


class TestStillMoments:
	def test_one_frame_from_the_middle_of_each_long_enough_still_interval(self):
		fps = 30
		t = np.arange(0, 6.0, 1 / fps)
		pan = np.interp(t, [0, 1, 2, 3, 3.2, 4, 6], [0, 30, 30, 60, 60, 90, 90])  # still 1-2 s, 3-3.2 s, 4-6 s
		body = np.stack([pan, np.zeros_like(t)], axis=1)

		got = still_moments(t, body, hold_s=0.5)

		assert len(got) == 2
		assert t[got[0]] == pytest.approx(1.5, abs=0.15)
		assert t[got[1]] == pytest.approx(5.0, abs=0.2)


TRUE_R = Rotation.from_euler("z", 97, degrees=True).as_matrix()
TRUE_T = np.array([0.14, 0.11, 0.0])
TOUCHED = {
	16: np.array([0.0, 0.0, 0.0]),
	17: np.array([0.273, 0.0, 0.0]),
	10: np.array([0.017, -0.29, 0.001]),
	11: np.array([0.169, -0.254, 0.002]),
}


def tips_in_base(markers: dict[int, np.ndarray]) -> dict[int, np.ndarray]:
	"""Where the jaw tip is, in the robot base frame, while it touches each table point."""
	return {mid: TRUE_R.T @ (p - TRUE_T) for mid, p in markers.items()}


class TestRigidFit:
	def test_recovers_rotation_and_translation(self):
		src = np.random.default_rng(0).uniform(-0.3, 0.3, (5, 3))
		r, t, rms = rigid_fit(src, src @ TRUE_R.T + TRUE_T)
		np.testing.assert_allclose(r, TRUE_R, atol=1e-9)
		np.testing.assert_allclose(t, TRUE_T, atol=1e-9)
		assert rms < 1e-9


class TestFitTouches:
	def test_finds_the_base_and_which_touch_was_which_marker(self):
		tips = tips_in_base(TOUCHED)
		order = [11, 16, 10, 17]  # touched in some order the fit is not told

		fit = fit_touches([tips[m] for m in order], TOUCHED)

		np.testing.assert_allclose(fit.base_rotation, TRUE_R, atol=1e-6)
		np.testing.assert_allclose(fit.base_position_m, TRUE_T, atol=1e-6)
		assert fit.assignment == order
		assert fit.rms_mm < 1e-6

	def test_hand_placement_noise_shows_up_as_the_residual(self):
		rng = np.random.default_rng(1)
		tips = tips_in_base(TOUCHED)
		noisy = [tips[m] + rng.normal(0, 0.002, 3) for m in (16, 17, 10, 11)]

		fit = fit_touches(noisy, TOUCHED)

		assert fit.assignment == [16, 17, 10, 11]
		np.testing.assert_allclose(fit.base_position_m, TRUE_T, atol=0.005)
		assert 0.5 < fit.rms_mm < 5.0

	def test_a_near_symmetric_layout_is_not_solved_with_the_base_upside_down(self):
		# 16, 17 and 18 are almost isosceles: swapping 16 and 17 fits nearly as well with the base flipped over
		layout = {16: np.array([0.0, 0.0, 0.0]), 17: np.array([0.273, 0.0, 0.0]), 18: np.array([0.142, -0.078, 0.0])}
		tips = tips_in_base(layout)
		rng = np.random.default_rng(3)
		noisy = [tips[m] + rng.normal(0, 0.002, 3) for m in (16, 17, 18)]

		fit = fit_touches(noisy, layout)

		assert fit.assignment == [16, 17, 18]
		assert fit.base_rotation[2, 2] > 0.9

	def test_three_touches_are_the_minimum(self):
		tips = tips_in_base(TOUCHED)
		with pytest.raises(ValueError, match="3"):
			fit_touches([tips[16], tips[17]], TOUCHED)


ZERO_ERRORS = {"shoulder_lift": -6.0, "elbow_flex": -5.0, "wrist_flex": -2.0}
CELL_R = Rotation.from_euler("z", -110, degrees=True).as_matrix()
CELL_T = np.array([0.155, 0.19, -0.021])
CELL_TAGS = {16: np.array([0.0, 0.0, 0.0]), 17: np.array([0.273, 0.0, 0.0]), 18: np.array([0.142, -0.078, 0.0])}


def touch_readings(point_table: np.ndarray, tilt_deg: float) -> dict[str, float] | None:
	"""Readings putting the true jaw tip on ``point_table``, leaning ``tilt_deg`` out from the base, when the readings
	carry ZERO_ERRORS; None where the arm cannot hold that posture."""
	from defect_sorter.kinematics import inverse

	base_point = CELL_R.T @ (point_table - CELL_T)
	radial = np.array([base_point[0], base_point[1], 0.0]) / np.hypot(*base_point[:2])
	t = np.radians(tilt_deg)
	approach = np.cos(t) * np.array([0.0, 0.0, -1.0]) + np.sin(t) * radial
	sol = inverse(base_point, approach=approach, roll_deg=0.0, tolerance_deg=5)
	return {j: v - ZERO_ERRORS.get(j, 0.0) for j, v in sol.angles_deg.items()} if sol.reachable else None


def two_postures(point_table: np.ndarray) -> list[dict[str, float]]:
	"""The steepest reachable posture and one at least 20 deg flatter."""
	found = [(t, r) for t in range(0, 80, 5) if (r := touch_readings(point_table, float(t))) is not None]
	second = next(f for f in found if f[0] >= found[0][0] + 20)
	return [found[0][1], second[1]]


def cell_touches(noise_m: float = 0.0, seed: int = 0) -> tuple[list[dict[str, float]], dict[int, np.ndarray]]:
	"""Two touches per tag in postures at least 20 deg apart; the tags as the camera sees them, with noise."""
	rng = np.random.default_rng(seed)
	angles = [a for p in CELL_TAGS.values() for a in two_postures(p)]
	seen = {m: p + rng.normal(0, noise_m, 3) * [1, 1, 0] for m, p in CELL_TAGS.items()}
	return angles, seen


class TestFitTouchesWithZeros:
	def test_recovers_the_base_and_the_joint_zero_errors(self):
		angles, tags = cell_touches()

		fit = fit_touches_with_zeros(angles, tags)

		assert fit.assignment == [16, 16, 17, 17, 18, 18]
		for joint, error in ZERO_ERRORS.items():
			assert fit.offsets_deg[joint] == pytest.approx(error, abs=0.05)
		np.testing.assert_allclose(fit.base_position_m, CELL_T, atol=0.0005)
		np.testing.assert_allclose(fit.base_rotation, CELL_R, atol=1e-3)
		assert fit.rms_mm < 0.1

	def test_trusting_wrong_zeros_shows_up_as_a_large_residual(self):
		angles, tags = cell_touches()

		trusted = fit_touches_with_zeros(angles, tags, joints=())

		assert trusted.offsets_deg == {}
		assert trusted.rms_mm > 5.0

	def test_leave_one_out_errors_measure_how_well_unseen_touches_are_predicted(self):
		angles, tags = cell_touches(noise_m=0.002, seed=3)

		fit = fit_touches_with_zeros(angles, tags)

		assert len(fit.leave_one_out_mm) == len(angles)
		assert max(fit.leave_one_out_mm) < 15.0
		assert np.mean(fit.leave_one_out_mm) > fit.rms_mm  # unseen points are predicted worse than fitted ones

	def test_too_few_touches_for_the_unknowns_are_refused(self):
		angles, tags = cell_touches()
		with pytest.raises(ValueError, match="touches"):
			fit_touches_with_zeros(angles[:2], tags)


class TestVideoFile:
	def test_each_episode_names_its_own_video_file_and_start_time(self, tmp_path):
		episodes = {
			"videos/observation.images.top/chunk_index": [0, 0],
			"videos/observation.images.top/file_index": [0, 1],
			"videos/observation.images.top/from_timestamp": [0.0, 12.5],
		}

		path, t0 = video_file(tmp_path, episodes, "top", 1)

		assert path == tmp_path / "videos" / "observation.images.top" / "chunk-000" / "file-001.mp4"
		assert t0 == 12.5


class TestTouchHolds:
	def test_holds_in_the_air_and_second_pauses_on_the_same_spot_are_dropped(self):
		angles, _ = cell_touches()  # two postures per tag; their tips (readings as they are) lie ~6 mm apart
		in_the_air = dict.fromkeys(angles[0], 0.0)  # zero pose: tip 23 cm above the base

		got = touch_holds([in_the_air, *angles], max_height_m=0.06, merge_m=0.02)

		assert got == [angles[0], angles[2], angles[4]]
