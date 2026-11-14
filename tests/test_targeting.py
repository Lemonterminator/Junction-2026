import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from defect_sorter.alignment import TableFrame
from defect_sorter.geometry import Intrinsics, Plane
from defect_sorter.kinematics import JOINT_LIMITS_DEG, tool_pose
from defect_sorter.robot_pose import RobotCalibration, model_from_readings
from defect_sorter.scene import detect_scene
from defect_sorter.targeting import (
	JAW_AXIS_TOOL,
	BrickPose,
	brick_pose,
	combine_poses,
	grasp_roll,
	hover_target,
	select_brick,
)

# A 2x4 brick seen by a tilted top camera at the D415's aligned colour resolution.
INTR = Intrinsics(fx=900.0, fy=900.0, ppx=640.0, ppy=360.0)
SHAPE = (720, 1280)
CAMERA_TABLE = np.array([0.25, -0.30, 0.45])
LOOK_AT_TABLE = np.array([0.25, 0.10, 0.0])
BRICK_L, BRICK_W, BRICK_H = 0.0318, 0.0158, 0.019


def camera_rotation() -> np.ndarray:
	"""Columns: camera x (image right), y (image down), z (optical axis) in table coordinates."""
	z = LOOK_AT_TABLE - CAMERA_TABLE
	z /= np.linalg.norm(z)
	x = np.cross(z, [0.0, 0.0, 1.0])
	x /= np.linalg.norm(x)
	return np.stack([x, np.cross(z, x), z], axis=1)


R_TC = camera_rotation()
FRAME = TableFrame(origin=-R_TC.T @ CAMERA_TABLE, axes=R_TC, basis="anchors 16->17")
PLANE = Plane(normal=R_TC.T @ np.array([0.0, 0.0, 1.0]), offset=float(CAMERA_TABLE[2]), inlier_fraction=1.0)


def render_depth(boxes: list[tuple[float, float, float]]) -> np.ndarray:
	"""Ray-cast the table (z = 0) and bricks given as (x, y, yaw_deg) in table metres; depth along the optical axis."""
	h, w = SHAPE
	v, u = np.mgrid[0:h, 0:w]
	d_cam = np.stack([(u - INTR.ppx) / INTR.fx, (v - INTR.ppy) / INTR.fy, np.ones((h, w))], axis=-1)
	d = d_cam @ R_TC.T
	t = -CAMERA_TABLE[2] / d[..., 2]
	half = np.array([BRICK_L / 2, BRICK_W / 2, BRICK_H / 2])
	for x, y, yaw in boxes:
		r = Rotation.from_euler("z", yaw, degrees=True).as_matrix()
		o = r.T @ (CAMERA_TABLE - np.array([x, y, BRICK_H / 2]))
		dl = d @ r
		with np.errstate(divide="ignore", invalid="ignore"):
			t1, t2 = (-half - o) / dl, (half - o) / dl
		near = np.nanmax(np.minimum(t1, t2), axis=-1)
		far = np.nanmin(np.maximum(t1, t2), axis=-1)
		hit = (near <= far) & (near > 0)
		t = np.where(hit & (near < t), near, t)
	return t.astype(np.float32)


def detect(boxes: list[tuple[float, float, float]]) -> list[BrickPose]:
	depth = render_depth(boxes)
	color = np.full((*SHAPE, 3), (90, 140, 190), np.uint8)
	scene = detect_scene(color, depth, INTR, plane=PLANE)
	return [p for obj in scene.objects if (p := brick_pose(obj, scene, depth, INTR, FRAME)) is not None]


def axial_diff_deg(a: float, b: float) -> float:
	return abs((a - b + 90.0) % 180.0 - 90.0)


class TestBrickPose:
	@pytest.mark.parametrize("yaw", [0.0, 30.0, 90.0, 135.0])
	def test_top_face_centre_yaw_and_size_of_a_brick_seen_at_a_tilt(self, yaw: float):
		poses = detect([(0.27, 0.12, yaw)])

		assert len(poses) == 1
		p = poses[0]
		np.testing.assert_allclose(p.centre_m, [0.27, 0.12, BRICK_H], atol=0.0015)
		assert axial_diff_deg(p.yaw_deg, yaw) < 2.0
		assert -90.0 < p.yaw_deg <= 90.0
		assert p.length_m == pytest.approx(BRICK_L, abs=0.002)
		assert p.width_m == pytest.approx(BRICK_W, abs=0.002)

	def test_the_visible_side_face_does_not_pull_the_centre_towards_the_camera(self):
		depth = render_depth([(0.27, 0.12, 0.0)])
		scene = detect_scene(np.full((*SHAPE, 3), 128, np.uint8), depth, INTR, plane=PLANE)
		blob_centre = FRAME.point(np.array(scene.objects[0].xyz_cam_m))

		top = brick_pose(scene.objects[0], scene, depth, INTR, FRAME)

		assert top is not None
		assert np.hypot(*(blob_centre[:2] - [0.27, 0.12])) > 0.003  # the naive centre is biased
		assert np.hypot(*(top.centre_m[:2] - [0.27, 0.12])) < 0.0015

	def test_too_few_top_face_points_give_no_pose(self):
		depth = render_depth([(0.27, 0.12, 0.0)])
		scene = detect_scene(np.full((*SHAPE, 3), 128, np.uint8), depth, INTR, plane=PLANE)

		assert brick_pose(scene.objects[0], scene, depth, INTR, FRAME, min_points=100_000) is None


def pose(x: float, y: float, yaw: float = 0.0, height: float = BRICK_H) -> BrickPose:
	return BrickPose(np.array([x, y, height]), yaw, BRICK_L, BRICK_W, 200)


class TestSelectBrick:
	def test_single_brick_is_chosen(self):
		chosen, reason = select_brick([pose(0.2, 0.1)])
		assert chosen is not None
		assert reason == ""

	def test_two_bricks_need_a_hint(self):
		chosen, reason = select_brick([pose(0.2, 0.1), pose(0.3, 0.1)])
		assert chosen is None
		assert "2 bricks" in reason

	def test_hint_picks_the_nearest(self):
		chosen, _ = select_brick([pose(0.2, 0.1), pose(0.3, 0.1)], near_m=np.array([0.29, 0.12]))
		assert chosen is not None
		assert chosen.centre_m[0] == pytest.approx(0.3)

	def test_tall_or_large_things_are_not_bricks(self):
		tall = pose(0.2, 0.1, height=0.08)
		large = BrickPose(np.array([0.3, 0.1, 0.02]), 0.0, 0.12, 0.06, 900)
		chosen, reason = select_brick([tall, large])
		assert chosen is None
		assert "no brick" in reason


class TestCombinePoses:
	def test_median_centre_and_yaw_across_the_180_degree_wrap(self):
		frames = [pose(0.200, 0.1, 89.0), pose(0.202, 0.1, -89.0), pose(0.201, 0.1, 88.0)]

		combined, spread_m = combine_poses(frames)

		assert combined.centre_m[0] == pytest.approx(0.201)
		assert axial_diff_deg(combined.yaw_deg, 89.3) < 0.5
		assert spread_m == pytest.approx(np.std([0.200, 0.202, 0.201]), abs=1e-6)


class TestHoverTarget:
	def test_hover_height_is_above_the_top_face(self):
		np.testing.assert_allclose(hover_target(pose(0.2, 0.1), height_m=0.06), [0.2, 0.1, BRICK_H + 0.06])


CAL = RobotCalibration(
	offsets_deg={"shoulder_lift": 1.2, "elbow_flex": -6.6, "wrist_flex": -2.4},
	base_rotation=Rotation.from_euler("z", 63, degrees=True).as_matrix(),
	base_position_m=np.array([0.225, -0.096, 0.0]),
)


def target_out(distance_m: float, height_m: float = 0.08) -> np.ndarray:
	d = CAL.base_rotation @ np.array([*tool_pose({})[:2, 3], 0.0])
	d /= np.linalg.norm(d)
	return CAL.base_position_m + distance_m * d + np.array([0.0, 0.0, height_m])


def jaw_axis_angle_table(solution_readings: dict[str, float]) -> float:
	r_base_tool = tool_pose(model_from_readings(solution_readings, CAL))[:3, :3]
	axis = CAL.base_rotation @ r_base_tool @ JAW_AXIS_TOOL
	return float(np.degrees(np.arctan2(axis[1], axis[0])))


class TestGraspRoll:
	@pytest.mark.parametrize("brick_yaw", [0.0, 45.0, 90.0, 135.0, -30.0])
	def test_jaws_close_across_the_short_side(self, brick_yaw: float):
		g = grasp_roll(target_out(0.2), brick_yaw, calibration=CAL, current_roll_deg=0.0)

		assert g is not None
		assert axial_diff_deg(jaw_axis_angle_table(g.readings), brick_yaw + 90.0) < 2.0
		lo, hi = JOINT_LIMITS_DEG["wrist_roll"]
		assert lo <= g.roll_deg <= hi
		assert g.readings["wrist_roll"] == pytest.approx(g.roll_deg)

	def test_a_half_turn_of_the_brick_gives_the_same_roll(self):
		a = grasp_roll(target_out(0.2), 20.0, calibration=CAL, current_roll_deg=0.0)
		b = grasp_roll(target_out(0.2), 200.0, calibration=CAL, current_roll_deg=0.0)
		assert a is not None
		assert b is not None
		assert a.roll_deg == pytest.approx(b.roll_deg, abs=0.5)

	def test_picks_the_solution_nearest_the_current_roll(self):
		near_zero = grasp_roll(target_out(0.2), 0.0, calibration=CAL, current_roll_deg=0.0)
		assert near_zero is not None
		other = near_zero.roll_deg + (180.0 if near_zero.roll_deg < 0 else -180.0)

		from_other = grasp_roll(target_out(0.2), 0.0, calibration=CAL, current_roll_deg=other)

		# The tool point is off the roll axis, so the two solutions differ by a little less or more than 180 deg.
		assert from_other is not None
		assert abs(from_other.roll_deg - near_zero.roll_deg) > 170.0
		assert abs(from_other.roll_deg - other) < 5.0

	def test_unreachable_target_gives_none(self):
		assert grasp_roll(target_out(0.6), 0.0, calibration=CAL, current_roll_deg=0.0) is None
