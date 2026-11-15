import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from defect_sorter.kinematics import inverse, tool_pose
from defect_sorter.motion import (
	HARD_MAX_SPEED_DEG_S,
	Keyframe,
	MotionLimits,
	execute,
	gripper_ticks,
	interpolate,
	load_keyframes,
	plan_bowl_drop,
	plan_brick_hover,
	plan_joint_move,
	plan_keyframes,
	plan_lift,
	plan_move,
	save_keyframes,
	to_ticks,
)
from defect_sorter.robot_pose import RobotCalibration, readings_from_model
from defect_sorter.targeting import BowlPose, BrickPose, grasp_point

BODY = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll")
RANGES = dict.fromkeys((*BODY, "gripper"), (0, 4095))
CAL = RobotCalibration(
	offsets_deg={"shoulder_lift": 1.2, "elbow_flex": -6.6, "wrist_flex": -2.4},
	base_rotation=Rotation.from_euler("z", 63, degrees=True).as_matrix(),
	base_position_m=np.array([0.225, -0.096, 0.0]),
)
DOWN = (0.0, 0.0, -1.0)


def reach_direction_table() -> np.ndarray:
	d = CAL.base_rotation @ np.array([*tool_pose({})[:2, 3], 0.0])
	return d / np.linalg.norm(d)


def table_point(distance_m: float, height_m: float) -> np.ndarray:
	return CAL.base_position_m + distance_m * reach_direction_table() + np.array([0.0, 0.0, height_m])


def readings_at(distance_m: float, height_m: float) -> dict[str, float]:
	sol = inverse(
		CAL.to_base(table_point(distance_m, height_m)),
		approach=CAL.direction_to_base(DOWN),
		roll_deg=0.0,
		tolerance_deg=5.0,
	)
	assert sol.reachable
	return readings_from_model(sol.angles_deg, CAL)


class TestLimits:
	def test_speed_above_the_hard_cap_is_rejected(self):
		with pytest.raises(ValueError, match="speed"):
			MotionLimits(max_speed_deg_s=HARD_MAX_SPEED_DEG_S + 1)

	def test_floor_and_reach_cannot_be_switched_off(self):
		with pytest.raises(ValueError, match="floor"):
			MotionLimits(min_tool_height_m=-0.01)
		with pytest.raises(ValueError, match="reach"):
			MotionLimits(max_reach_m=0.6)

	def test_reach_defaults_to_40_cm_and_stops_at_42_cm(self):
		assert MotionLimits().max_reach_m == pytest.approx(0.40)
		assert MotionLimits(max_reach_m=0.42).max_reach_m == pytest.approx(0.42)
		with pytest.raises(ValueError, match="reach"):
			MotionLimits(max_reach_m=0.425)


class TestInterpolate:
	def test_steps_never_exceed_speed_times_dt_and_end_on_the_goal(self):
		start = {"shoulder_pan": 0.0, "elbow_flex": 10.0}
		goal = {"shoulder_pan": 30.0, "elbow_flex": 4.0}
		path = interpolate(start, goal, speed_deg_s=10.0, dt_s=0.1)
		assert len(path) == 30  # 30 degrees at 1 degree per step
		prev = start
		for wp in path:
			assert max(abs(wp[j] - prev[j]) for j in start) <= 1.0 + 1e-9
			prev = wp
		assert path[-1] == pytest.approx(goal)

	def test_all_joints_arrive_together(self):
		path = interpolate({"a": 0.0, "b": 0.0}, {"a": 10.0, "b": 5.0}, speed_deg_s=10.0, dt_s=0.1)
		assert path[len(path) // 2]["b"] == pytest.approx(path[len(path) // 2]["a"] / 2)


class TestToTicks:
	def test_inverts_the_midpoint_degree_convention(self):
		assert to_ticks({"elbow_flex": 0.0}, {"elbow_flex": (1000, 3000)}) == {"elbow_flex": 2000}
		assert to_ticks({"elbow_flex": 90.0}, {"elbow_flex": (0, 4095)})["elbow_flex"] == round(2047.5 + 1023.75)

	def test_outside_the_servo_range_raises(self):
		with pytest.raises(ValueError, match="elbow_flex"):
			to_ticks({"elbow_flex": 120.0}, {"elbow_flex": (1000, 3000)})


class TestPlanMove:
	def test_hover_above_a_reachable_point(self):
		start = readings_at(0.20, 0.05)
		target = table_point(0.22, 0.06)
		plan = plan_move(start, target, roll_deg=0.0, calibration=CAL, limits=MotionLimits(), ranges=RANGES, dt_s=0.05)
		assert plan.ok, plan.reason
		end = tool_pose(model_of(plan.path[-1]))
		np.testing.assert_allclose(CAL.to_table(end[:3, 3]), target, atol=0.002)
		assert plan.path[-1]["wrist_roll"] == pytest.approx(0.0)

	def test_out_of_reach_is_refused_with_a_reason(self):
		plan = plan_move(
			readings_at(0.20, 0.05),
			table_point(0.45, 0.08),
			roll_deg=0.0,
			calibration=CAL,
			limits=MotionLimits(),
			ranges=RANGES,
		)
		assert not plan.ok
		assert plan.path == []
		assert "reach" in plan.reason

	def test_target_below_the_floor_is_refused(self):
		plan = plan_move(
			readings_at(0.20, 0.05),
			table_point(0.22, 0.005),
			roll_deg=0.0,
			calibration=CAL,
			limits=MotionLimits(min_tool_height_m=0.02),
			ranges=RANGES,
		)
		assert not plan.ok
		assert "height" in plan.reason

	def test_starting_low_it_rises_before_travelling(self):
		# start 1 cm above the table: the first moves must go up, never further down
		start = readings_at(0.20, 0.01)
		plan = plan_move(
			start, table_point(0.23, 0.06), roll_deg=0.0, calibration=CAL, limits=MotionLimits(), ranges=RANGES
		)
		assert plan.ok, plan.reason
		heights = [CAL.to_table(tool_pose(model_of(wp))[:3, 3])[2] for wp in plan.path]
		start_h = CAL.to_table(tool_pose(model_of(start))[:3, 3])[2]
		assert min(heights) >= start_h - 0.001


def tilted(tilt_deg: float) -> np.ndarray:
	"""Straight down leaned ``tilt_deg`` out along the arm's reach direction (table frame)."""
	t = np.radians(tilt_deg)
	return np.cos(t) * np.array(DOWN) + np.sin(t) * reach_direction_table()


class TestTiltedApproach:
	def test_the_jaws_end_up_along_a_tilted_approach(self):
		target = table_point(0.24, 0.06)
		approach = tilted(40.0)

		plan = plan_move(
			readings_at(0.20, 0.05),
			target,
			roll_deg=0.0,
			calibration=CAL,
			limits=MotionLimits(),
			ranges=RANGES,
			approach_table=approach,
		)

		assert plan.ok, plan.reason
		end = tool_pose(model_of(plan.path[-1]))
		np.testing.assert_allclose(CAL.to_table(end[:3, 3]), target, atol=0.002)
		jaws_point = CAL.base_rotation @ end[:3, 2]
		assert np.degrees(np.arccos(np.clip(jaws_point @ approach, -1, 1))) < 5.0

	def test_an_unreachable_tilt_is_refused_naming_the_approach(self):
		plan = plan_move(
			readings_at(0.20, 0.05),
			table_point(0.12, 0.20),
			roll_deg=0.0,
			calibration=CAL,
			limits=MotionLimits(),
			ranges=RANGES,
			approach_table=tilted(80.0),
		)
		assert not plan.ok
		assert "approach" in plan.reason


def brick_at(distance_m: float) -> BrickPose:
	return BrickPose(table_point(distance_m, 0.026), 20.0, 0.031, 0.026, 300)


class TestPlanBrickHover:
	def test_near_brick_straight_down_to_the_standoff(self):
		brick = brick_at(0.20)

		plan, choice, reason = plan_brick_hover(
			readings_at(0.18, 0.08), brick, calibration=CAL, limits=MotionLimits(), ranges=RANGES
		)

		assert plan.ok, reason
		assert choice is not None
		assert choice.tilt_deg == 0.0
		end = CAL.to_table(tool_pose(model_of(plan.path[-1]))[:3, 3])
		np.testing.assert_allclose(end, grasp_point(brick) + np.array([0.0, 0.0, 0.06]), atol=0.002)

	def test_further_out_it_tilts_and_still_passes_every_check(self):
		far = next(
			d
			for d in np.arange(0.20, 0.30, 0.005)
			if not plan_brick_hover(
				readings_at(0.18, 0.08),
				brick_at(d),
				calibration=CAL,
				limits=MotionLimits(),
				ranges=RANGES,
				tilts_deg=(0.0,),
			)[0].ok
		)

		plan, choice, reason = plan_brick_hover(
			readings_at(0.18, 0.08), brick_at(far), calibration=CAL, limits=MotionLimits(), ranges=RANGES
		)

		assert plan.ok, reason
		assert choice is not None
		assert choice.tilt_deg > 0.0
		end = tool_pose(model_of(plan.path[-1]))
		np.testing.assert_allclose(CAL.to_table(end[:3, 3]), choice.standoff_m, atol=0.002)
		jaws_point = CAL.base_rotation @ end[:3, 2]
		assert np.degrees(np.arccos(np.clip(jaws_point @ choice.approach, -1, 1))) < 5.0

	def test_the_wrist_roll_nearest_the_middle_of_its_range_wins_whatever_the_start_roll(self):
		start = dict(readings_at(0.18, 0.08))
		start["wrist_roll"] = 80.0  # the wrist left near one end of its range
		plan, choice, reason = plan_brick_hover(
			start, brick_at(0.20), calibration=CAL, limits=MotionLimits(), ranges=RANGES
		)
		assert plan.ok, reason
		assert abs(choice.roll.roll_deg) <= 45.0 + 1e-6  # a square brick: one of the four rolls is within 45 of 0

	def test_a_brick_whose_long_side_fits_the_jaws_is_also_taken_across_it(self):
		for yaw in np.arange(-80.0, 90.0, 20.0):
			fits = BrickPose(table_point(0.20, 0.03), yaw, 0.029, 0.017, 150)  # a 2x2 Duplo lying on its side
			too_long = BrickPose(table_point(0.20, 0.03), yaw, 0.050, 0.017, 150)
			pf, cf, why = plan_brick_hover(
				readings_at(0.18, 0.08), fits, calibration=CAL, limits=MotionLimits(), ranges=RANGES
			)
			_, cl, _ = plan_brick_hover(
				readings_at(0.18, 0.08), too_long, calibration=CAL, limits=MotionLimits(), ranges=RANGES
			)
			assert pf.ok, why
			assert abs(cf.roll.roll_deg) <= 45.0 + 1e-6
			if cl is not None:
				assert abs(cf.roll.roll_deg) <= abs(cl.roll.roll_deg) + 1e-6

	def test_beyond_the_reach_limit_nothing_is_planned(self):
		plan, choice, reason = plan_brick_hover(
			readings_at(0.18, 0.08), brick_at(0.45), calibration=CAL, limits=MotionLimits(), ranges=RANGES
		)

		assert not plan.ok
		assert choice is None
		assert "reach" in reason
		assert reason.count("reach limit") == 1  # said once, not once per approach tilt
		assert "toward the robot" in reason


# The cell as calibrated on 2026-11-15 and the follower folded at rest, as read from the arm: the tool lies 3 mm
# below the table plane, 15 cm from the base. Rising straight up with the gripper already turned to the final
# approach is out of reach there; rising with its present orientation is not.
CELL = RobotCalibration(
	offsets_deg={"shoulder_lift": -5.604, "elbow_flex": -6.393, "wrist_flex": -1.207},
	base_rotation=np.array([[-0.36434, 0.93127, 0.0], [-0.93127, -0.36434, 0.0], [0.0, 0.0, 1.0]]),
	base_position_m=np.array([0.15794, 0.18984, -0.0204]),
)
CELL_RANGES = {
	"shoulder_pan": (1267, 3200),
	"shoulder_lift": (894, 3251),
	"elbow_flex": (849, 3045),
	"wrist_flex": (788, 3115),
	"wrist_roll": (2040, 3961),
	"gripper": (2041, 3508),
}
FOLDED = {
	"shoulder_pan": 32.04,
	"shoulder_lift": -102.81,
	"elbow_flex": 96.09,
	"wrist_flex": 77.41,
	"wrist_roll": 23.34,
}


def cell_tool_height(readings: dict[str, float]) -> float:
	model = {j: v + CELL.offsets_deg.get(j, 0.0) for j, v in readings.items()}
	return float(CELL.to_table(tool_pose(model)[:3, 3])[2])


class TestStartingFolded:
	def test_from_rest_it_rises_keeping_its_orientation_then_turns_to_the_approach(self):
		brick = BrickPose(np.array([0.132, -0.022, 0.028]), 2.0, 0.028, 0.014, 225)
		limits = MotionLimits(max_speed_deg_s=10.0)

		plan, choice, reason = plan_brick_hover(FOLDED, brick, calibration=CELL, limits=limits, ranges=CELL_RANGES)

		assert plan.ok, reason
		assert choice is not None
		heights = [cell_tool_height(wp) for wp in plan.path]
		risen = next(i for i, h in enumerate(heights) if h >= limits.min_tool_height_m)
		assert all(h >= cell_tool_height(FOLDED) - 0.001 for h in heights[:risen])  # never lower than at rest
		assert min(heights[risen:]) >= limits.min_tool_height_m  # once up, the normal floor holds
		end = CELL.to_table(tool_pose({j: v + CELL.offsets_deg.get(j, 0.0) for j, v in plan.path[-1].items()})[:3, 3])
		np.testing.assert_allclose(end, choice.standoff_m, atol=0.002)


def bowl_at(distance_m: float, radius_m: float = 0.09) -> BowlPose:
	centre = table_point(distance_m, 0.0)
	return BowlPose("green", np.array([centre[0], centre[1], 0.015]), radius_m, 0.015, 400)


def end_point(plan) -> np.ndarray:
	return CAL.to_table(tool_pose(model_of(plan.path[-1]))[:3, 3])


class TestPlanBowlDrop:
	def test_a_near_bowl_is_served_over_its_centre(self):
		bowl = bowl_at(0.20)

		plan, point, reason = plan_bowl_drop(
			readings_at(0.18, 0.08), bowl, calibration=CAL, limits=MotionLimits(), ranges=RANGES
		)

		assert plan.ok, reason
		np.testing.assert_allclose(point[:2], bowl.centre_m[:2], atol=1e-9)
		np.testing.assert_allclose(end_point(plan), point, atol=0.002)
		assert point[2] == pytest.approx(0.015 + 0.08)

	def test_a_bowl_centred_beyond_the_reach_limit_is_served_from_its_near_half(self):
		bowl = bowl_at(0.45)  # centre 45 cm out, reach limit 40 cm

		plan, point, reason = plan_bowl_drop(
			readings_at(0.18, 0.08), bowl, calibration=CAL, limits=MotionLimits(), ranges=RANGES
		)

		assert plan.ok, reason
		off = np.hypot(*(point[:2] - bowl.centre_m[:2]))
		assert 0.0 < off <= bowl.radius_m - 0.03 + 1e-9  # inside the rim, not over the centre
		assert np.linalg.norm(CAL.to_base(point)[:2]) <= 0.40 + 1e-9
		np.testing.assert_allclose(end_point(plan), point, atol=0.002)

	def test_a_bowl_wholly_out_of_reach_is_refused_with_a_reason(self):
		plan, point, reason = plan_bowl_drop(
			readings_at(0.18, 0.08), bowl_at(0.60), calibration=CAL, limits=MotionLimits(), ranges=RANGES
		)

		assert not plan.ok
		assert point is None
		assert "reach" in reason


def tool_height(readings: dict[str, float]) -> float:
	return float(CAL.to_table(tool_pose(model_of(readings))[:3, 3])[2])


def taught(pan: float, lift: float, elbow: float, wrist: float, roll: float = 0.0) -> dict[str, float]:
	return {"shoulder_pan": pan, "shoulder_lift": lift, "elbow_flex": elbow, "wrist_flex": wrist, "wrist_roll": roll}


POSE_A, POSE_B, POSE_C = taught(0, -20, 50, 10), taught(20, -10, 40, 30, 60), taught(-15, -25, 55, 0, -45)


class TestKeyframes:
	def test_visits_each_keyframe_in_order_holding_it_at_the_speed_limit(self):
		start, a, b = POSE_C, POSE_A, POSE_B
		limits = MotionLimits(max_speed_deg_s=10.0)

		plan = plan_keyframes(
			start, [Keyframe(a, 1.0), Keyframe(b, 0.5)], calibration=CAL, limits=limits, ranges=RANGES, dt_s=0.05
		)

		assert plan.ok, plan.reason
		at_a = [i for i, wp in enumerate(plan.path) if wp == a]
		at_b = [i for i, wp in enumerate(plan.path) if wp == b]
		assert len(at_a) == 1 + 20  # arrives, then holds 1.0 s at 0.05 s steps
		assert len(at_b) == 1 + 10
		assert max(at_a) < min(at_b)
		steps = [max(abs(q[j] - p[j]) for j in q) for p, q in zip([start, *plan.path], plan.path, strict=False)]
		assert max(steps) <= 10.0 * 0.05 + 1e-9

	def test_a_keyframe_outside_the_servo_range_is_refused(self):
		bad = {**POSE_A, "wrist_roll": 400.0}

		plan = plan_keyframes(POSE_C, [Keyframe(bad, 1.0)], calibration=CAL, limits=MotionLimits(), ranges=RANGES)

		assert not plan.ok
		assert "range" in plan.reason

	def test_a_blend_that_dips_below_both_of_its_poses_is_refused(self):
		# both poses hold the tool high; the straight joint blend between them swings it down to the table
		a, b = taught(0, 60, -30, -90), taught(0, 60, 90, 90)
		mid = {j: (a[j] + b[j]) / 2 for j in a}
		assert min(tool_height(a), tool_height(b)) > 0.15
		assert tool_height(mid) < min(tool_height(a), tool_height(b)) - 0.1

		plan = plan_keyframes(a, [Keyframe(b, 0.0)], calibration=CAL, limits=MotionLimits(), ranges=RANGES)

		assert not plan.ok
		assert "below" in plan.reason

	def test_keyframes_round_trip_through_a_file(self, tmp_path):
		frames = [Keyframe(POSE_A, 1.0), Keyframe(POSE_B, 0.0)]
		save_keyframes(tmp_path / "overview.json", frames, note="demo")

		assert load_keyframes(tmp_path / "overview.json") == frames


def model_of(readings: dict[str, float]) -> dict[str, float]:
	return {j: v + CAL.offsets_deg.get(j, 0.0) for j, v in readings.items()}


class FakeBus:
	"""Servo bus that follows commands, optionally sticking at a step (an overloaded or blocked joint)."""

	def __init__(self, start: dict[str, int], stick_after: int | None = None) -> None:
		self.present = dict(start)
		self.goals: list[dict[str, int]] = []
		self.events: list[str] = []
		self.stick_after = stick_after

	def read_ticks(self) -> dict[str, int]:
		return dict(self.present)

	def hold_and_enable_torque(self) -> None:
		self.events.append("hold")

	def write_goals(self, goals: dict[str, int]) -> None:
		if not self.events or self.events[-1] != "write":
			self.events.append("write")
		self.goals.append(dict(goals))
		if self.stick_after is None or len(self.goals) <= self.stick_after:
			self.present.update(goals)


class TestExecute:
	def test_holds_position_before_torque_then_sends_every_waypoint(self):
		path = [{"elbow_flex": 2000 + 10 * i} for i in range(1, 6)]
		bus = FakeBus({"elbow_flex": 2000, "gripper": 2500})
		result = execute(bus, path, dt_s=0.0, max_tracking_error_ticks=50, sleep=lambda s: None)
		assert result.ok
		assert bus.events[0] == "hold"
		assert bus.goals == path

	def test_stops_and_holds_where_it_is_when_the_arm_lags(self):
		path = [{"elbow_flex": 2000 + 40 * i} for i in range(1, 10)]
		bus = FakeBus({"elbow_flex": 2000}, stick_after=2)
		result = execute(bus, path, dt_s=0.0, max_tracking_error_ticks=50, sleep=lambda s: None)
		assert not result.ok
		assert "elbow_flex" in result.reason
		assert bus.goals[-1] == {"elbow_flex": bus.present["elbow_flex"]}  # last command: stay where you are
		assert len(bus.goals) < len(path) + 1


class TestPlanJointMove:
	def test_moves_between_two_checked_poses_within_the_speed_limit(self):
		start = readings_at(0.20, 0.06)
		goal = readings_at(0.22, 0.08)
		limits = MotionLimits(max_speed_deg_s=10.0)
		plan = plan_joint_move(start, goal, calibration=CAL, limits=limits, ranges=RANGES, dt_s=0.05)
		assert plan.ok, plan.reason
		assert plan.path[-1] == pytest.approx({j: goal[j] for j in BODY})
		prev = {j: start[j] for j in BODY}
		for wp in plan.path:
			assert max(abs(wp[j] - prev[j]) for j in BODY) <= 10.0 * 0.05 + 1e-9
			prev = wp

	def test_a_goal_below_the_tool_floor_is_refused(self):
		plan = plan_joint_move(
			readings_at(0.20, 0.06),
			readings_at(0.22, 0.005),
			calibration=CAL,
			limits=MotionLimits(min_tool_height_m=0.02),
			ranges=RANGES,
		)
		assert not plan.ok
		assert plan.path == []
		assert "floor" in plan.reason

	def test_a_goal_outside_the_servo_range_is_refused(self):
		goal = dict(readings_at(0.22, 0.08))
		ranges = dict(RANGES) | {"wrist_roll": (1500, 2600)}  # about +-48 degrees around the midpoint
		goal["wrist_roll"] = 70.0
		plan = plan_joint_move(readings_at(0.20, 0.06), goal, calibration=CAL, limits=MotionLimits(), ranges=ranges)
		assert not plan.ok
		assert "wrist_roll" in plan.reason


class TestGripperTicks:
	def test_studio_percent_maps_linearly_onto_the_calibrated_range(self):
		assert gripper_ticks(0.0, (2000, 3000)) == 2000
		assert gripper_ticks(100.0, (2000, 3000)) == 3000
		assert gripper_ticks(35.0, (2000, 3000)) == 2350

	def test_outside_0_to_100_is_refused(self):
		with pytest.raises(ValueError, match="gripper"):
			gripper_ticks(120.0, (2000, 3000))


class TestPlanLift:
	def test_raises_the_tool_keeping_it_over_the_same_spot_and_never_lower(self):
		start = readings_at(0.20, 0.01)
		plan = plan_lift(start, calibration=CAL, limits=MotionLimits(), ranges=RANGES, rise_m=0.05)
		assert plan.ok, plan.reason
		p0 = CAL.to_table(tool_pose(model_of(start))[:3, 3])
		heights = [CAL.to_table(tool_pose(model_of(wp))[:3, 3])[2] for wp in plan.path]
		end = CAL.to_table(tool_pose(model_of(plan.path[-1]))[:3, 3])
		assert end[2] >= p0[2] + 0.05 - 1e-3
		assert np.linalg.norm(end[:2] - p0[:2]) <= 0.02
		assert min(heights) >= p0[2] - 0.001

	def test_keeps_the_wrist_roll(self):
		start = dict(readings_at(0.20, 0.02))
		start["wrist_roll"] = 37.0
		plan = plan_lift(start, calibration=CAL, limits=MotionLimits(), ranges=RANGES)
		assert plan.ok, plan.reason
		assert plan.path[-1]["wrist_roll"] == pytest.approx(37.0)
