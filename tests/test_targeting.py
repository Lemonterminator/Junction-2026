import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from defect_sorter.alignment import TableFrame
from defect_sorter.geometry import Intrinsics, Plane
from defect_sorter.kinematics import JOINT_LIMITS_DEG, tool_pose
from defect_sorter.robot_pose import RobotCalibration, model_from_readings
from defect_sorter.scene import PAPER_CELL, detect_scene
from defect_sorter.targeting import (
	JAW_AXIS_TOOL,
	BrickPose,
	approach_vector,
	bowl_pose,
	brick_pose,
	choose_approach,
	combine_poses,
	drop_points,
	fit_rim_circle,
	grasp_point,
	grasp_roll,
	grasp_symmetry_deg,
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


class TestGraspSymmetry:
	def test_a_square_duplo_can_be_grasped_across_either_pair_of_sides(self):
		square = BrickPose(np.array([0.2, 0.1, 0.019]), 10.0, 0.0318, 0.0312, 200)
		assert grasp_symmetry_deg(square) == 90.0

	def test_a_duplo_measured_through_its_studs_is_still_square(self):
		# the top-face fit of the real 2x2 Duplo at 0.5 m came out 31 x 26 mm (the studs sit inside the edges)
		measured = BrickPose(np.array([0.15, -0.05, 0.016]), 12.0, 0.031, 0.026, 300)
		assert grasp_symmetry_deg(measured) == 90.0

	def test_a_long_brick_only_across_its_short_side(self):
		assert grasp_symmetry_deg(pose(0.2, 0.1)) == 180.0


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

	@pytest.mark.parametrize("brick_yaw", [0.0, 30.0, 60.0, -75.0])
	def test_a_square_brick_turns_the_wrist_at_most_an_eighth_turn(self, brick_yaw: float):
		g = grasp_roll(target_out(0.2), brick_yaw, calibration=CAL, current_roll_deg=0.0, symmetry_deg=90.0)

		assert g is not None
		jaw = jaw_axis_angle_table(g.readings)
		assert abs((jaw - brick_yaw + 45.0) % 90.0 - 45.0) < 2.0  # across one pair of sides
		assert abs(g.roll_deg) <= 47.0  # 45 deg plus the tool point's small offset from the roll axis

	def test_a_square_brick_needs_less_turn_than_a_long_one(self):
		long = grasp_roll(target_out(0.2), 0.0, calibration=CAL, current_roll_deg=90.0)
		square = grasp_roll(target_out(0.2), 0.0, calibration=CAL, current_roll_deg=90.0, symmetry_deg=90.0)

		assert long is not None
		assert square is not None
		assert abs(long.roll_deg - 90.0) > 47.0  # the half-turn solutions are 28 and 208 deg
		assert abs(square.roll_deg - 90.0) <= 47.0  # a quarter turn on: 117 deg

	def test_unreachable_target_gives_none(self):
		assert grasp_roll(target_out(0.6), 0.0, calibration=CAL, current_roll_deg=0.0) is None


def tool_axes_table(readings: dict[str, float]) -> tuple[np.ndarray, np.ndarray]:
	"""Approach (tool z, out of the jaws) and jaw closing axis of a solution, in the table frame."""
	r = CAL.base_rotation @ tool_pose(model_from_readings(readings, CAL))[:3, :3]
	return r[:, 2], r @ JAW_AXIS_TOOL


def angle_deg(a: np.ndarray, b: np.ndarray) -> float:
	return float(np.degrees(np.arccos(np.clip(a @ b / np.linalg.norm(a) / np.linalg.norm(b), -1.0, 1.0))))


def long_axis(yaw_deg: float) -> np.ndarray:
	return np.array([np.cos(np.radians(yaw_deg)), np.sin(np.radians(yaw_deg)), 0.0])


class TestApproachVector:
	def test_zero_tilt_is_straight_down(self):
		np.testing.assert_allclose(approach_vector(target_out(0.2), 0.0, CAL), [0.0, 0.0, -1.0], atol=1e-12)

	def test_tilt_leans_out_along_the_line_from_the_base(self):
		target = target_out(0.2)
		radial = (target - CAL.base_position_m) * [1, 1, 0]
		radial /= np.linalg.norm(radial)

		a = approach_vector(target, 45.0, CAL)

		np.testing.assert_allclose(a, np.sqrt(0.5) * (radial + np.array([0.0, 0.0, -1.0])), atol=1e-12)
		assert np.linalg.norm(a) == pytest.approx(1.0)


class TestGraspPoint:
	def test_half_way_up_the_brick_under_its_top_face_centre(self):
		np.testing.assert_allclose(grasp_point(pose(0.2, 0.1, height=0.026)), [0.2, 0.1, 0.013])


class TestTiltedGraspRoll:
	@pytest.mark.parametrize("brick_yaw", [0.0, 40.0, 90.0, -60.0])
	def test_jaws_close_across_the_long_axis_on_a_tilted_approach(self, brick_yaw: float):
		target = target_out(0.22, height_m=0.05)
		a = approach_vector(target, 40.0, CAL)

		g = grasp_roll(target, brick_yaw, calibration=CAL, current_roll_deg=0.0, approach=a)

		assert g is not None
		approach, jaws = tool_axes_table(g.readings)
		assert angle_deg(approach, a) < 5.0
		assert abs(90.0 - angle_deg(jaws, long_axis(brick_yaw))) < 2.0

	def test_a_square_brick_takes_whichever_pair_of_sides_turns_the_wrist_less(self):
		target = target_out(0.22, height_m=0.05)
		a = approach_vector(target, 40.0, CAL)

		g = grasp_roll(target, 30.0, calibration=CAL, current_roll_deg=0.0, approach=a, symmetry_deg=90.0)
		long_only = grasp_roll(target, 30.0, calibration=CAL, current_roll_deg=0.0, approach=a)
		short_only = grasp_roll(target, 120.0, calibration=CAL, current_roll_deg=0.0, approach=a)

		assert g is not None
		assert long_only is not None
		assert short_only is not None
		assert abs(g.roll_deg) == pytest.approx(min(abs(long_only.roll_deg), abs(short_only.roll_deg)), abs=0.5)


class TestChooseApproach:
	def test_straight_down_when_it_reaches(self):
		brick = BrickPose(target_out(0.20, height_m=0.026), 0.0, 0.03, 0.03, 300)

		choice, reason = choose_approach(brick, calibration=CAL)

		assert choice is not None, reason
		assert choice.tilt_deg == 0.0
		np.testing.assert_allclose(choice.grasp_m, grasp_point(brick))
		np.testing.assert_allclose(choice.standoff_m, grasp_point(brick) - 0.06 * choice.approach)

	def test_the_steepest_reachable_tilt_further_out(self):
		# the first distance where straight down no longer reaches, inside the reach limit
		def brick_at(d: float) -> BrickPose:
			return BrickPose(target_out(d, height_m=0.026), 0.0, 0.03, 0.03, 300)

		far = next(
			d
			for d in np.arange(0.20, 0.30, 0.005)
			if choose_approach(brick_at(d), calibration=CAL, tilts_deg=(0.0,))[0] is None
		)
		brick = brick_at(far)

		choice, reason = choose_approach(brick, calibration=CAL)

		assert choice is not None, reason
		assert choice.tilt_deg > 0.0
		approach, _ = tool_axes_table(choice.roll.readings)
		assert angle_deg(approach, choice.approach) < 5.0
		steeper = [t for t in (0.0, 15.0, 30.0, 45.0, 60.0, 75.0) if t < choice.tilt_deg]
		for t in steeper:  # every steeper tilt was really out of reach
			assert choose_approach(brick, calibration=CAL, tilts_deg=(t,))[0] is None

	def test_nothing_beyond_the_reach_limit(self):
		brick = BrickPose(target_out(0.33, height_m=0.026), 0.0, 0.03, 0.03, 300)

		choice, reason = choose_approach(brick, calibration=CAL, reach_m=0.30)

		assert choice is None
		assert "reach" in reason

	def test_the_refusal_says_how_far_to_move_the_brick(self):
		brick = BrickPose(target_out(0.33, height_m=0.026), 0.0, 0.03, 0.03, 300)

		_, reason = choose_approach(brick, calibration=CAL, reach_m=0.30)

		assert "33 cm from the robot base" in reason
		assert "move it 3 cm toward the robot" in reason


class TestBaseIsNotABrick:
	def test_objects_next_to_the_robot_base_are_ignored(self):
		near_base = pose(0.24, -0.05)  # 5 cm from the base at (0.225, -0.096)
		brick = pose(0.30, 0.10)

		chosen, _ = select_brick([near_base, brick], exclude_xy_m=CAL.base_position_m[:2], exclude_radius_m=0.12)

		assert chosen is brick


# A bowl seen by a camera straight above the table (simplest exact depth: distance minus height).
TOP_INTR = Intrinsics(fx=600.0, fy=600.0, ppx=320.0, ppy=240.0)
TOP_H = 0.60
R_TOP = np.array([[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])  # columns: camera x, y, z in table coords
TOP_FRAME = TableFrame(origin=-R_TOP.T @ np.array([0.0, 0.0, TOP_H]), axes=R_TOP, basis="anchors 16->17")
TOP_PLANE = Plane(normal=R_TOP.T @ np.array([0.0, 0.0, 1.0]), offset=TOP_H, inlier_fraction=1.0)
BOWL_C, BOWL_R, RIM_H = np.array([0.03, -0.02]), 0.09, 0.015


def render_bowl(bricks: list[tuple[float, float]] = ()) -> tuple[np.ndarray, np.ndarray]:
	"""Colour and depth: a green plate (floor 3 mm, rim 15 mm over its outer 8 mm), optional bricks on its floor."""
	h, w = 480, 640
	v, u = np.mgrid[0:h, 0:w]
	x = (u - TOP_INTR.ppx) * TOP_H / TOP_INTR.fx
	y = -(v - TOP_INTR.ppy) * TOP_H / TOP_INTR.fy
	r = np.hypot(x - BOWL_C[0], y - BOWL_C[1])
	height = np.where(r < BOWL_R - 0.008, 0.003, np.where(r < BOWL_R, RIM_H, 0.0))
	for bx, by in bricks:
		height = np.where((abs(x - bx) < 0.016) & (abs(y - by) < 0.016), 0.03, height)
	color = np.full((h, w, 3), 205, np.uint8)
	color[r < BOWL_R] = (120, 150, 0)
	return color, (TOP_H - height).astype(np.float32)


class TestRimCircle:
	def test_a_ring_with_points_inside_it_gives_the_ring(self):
		rng = np.random.default_rng(0)
		a = rng.uniform(0, 2 * np.pi, 400)
		ring = np.c_[0.1 + 0.09 * np.cos(a), -0.2 + 0.09 * np.sin(a)] + rng.normal(0, 0.002, (400, 2))
		inside = rng.uniform(-0.03, 0.03, (120, 2)) + np.array([0.1, -0.2])  # bricks lying in the bowl

		centre, radius = fit_rim_circle(np.vstack([ring, inside]))

		np.testing.assert_allclose(centre, [0.1, -0.2], atol=0.001)
		assert radius == pytest.approx(0.09, abs=0.001)


class TestBowlPose:
	def test_rim_centre_radius_and_height_from_depth(self):
		color, depth = render_bowl()
		scene = detect_scene(color, depth, TOP_INTR, plane=TOP_PLANE, config=PAPER_CELL)

		bowls = [bowl_pose(b, scene, depth, TOP_INTR, TOP_FRAME) for b in scene.bowls]

		assert len(bowls) == 1
		b = bowls[0]
		assert b is not None
		assert b.colour == "green"
		np.testing.assert_allclose(b.centre_m[:2], BOWL_C, atol=0.003)
		assert b.radius_m == pytest.approx(BOWL_R - 0.004, abs=0.004)  # the rim band's middle
		assert b.rim_height_m == pytest.approx(RIM_H, abs=0.002)

	def test_bricks_lying_in_the_bowl_do_not_move_the_rim(self):
		color, depth = render_bowl(bricks=[(0.05, -0.01), (0.0, -0.04)])
		scene = detect_scene(color, depth, TOP_INTR, plane=TOP_PLANE, config=PAPER_CELL)

		b = bowl_pose(scene.bowls[0], scene, depth, TOP_INTR, TOP_FRAME)

		assert b is not None
		np.testing.assert_allclose(b.centre_m[:2], BOWL_C, atol=0.003)


class TestDropPoints:
	def test_centre_first_then_toward_the_robot_inside_the_rim(self):
		color, depth = render_bowl()
		scene = detect_scene(color, depth, TOP_INTR, plane=TOP_PLANE, config=PAPER_CELL)
		bowl = bowl_pose(scene.bowls[0], scene, depth, TOP_INTR, TOP_FRAME)
		base_xy = np.array([0.03, 0.40])

		points = drop_points(bowl, base_xy, clearance_m=0.08, margin_m=0.03)

		np.testing.assert_allclose(points[0][:2], bowl.centre_m[:2], atol=1e-9)
		assert all(p[2] == pytest.approx(bowl.rim_height_m + 0.08) for p in points)
		toward = [np.hypot(*(p[:2] - base_xy)) for p in points]
		assert toward == sorted(toward, reverse=True)  # each one closer to the robot
		assert max(np.hypot(*(p[:2] - bowl.centre_m[:2])) for p in points) <= bowl.radius_m - 0.03 + 1e-9
