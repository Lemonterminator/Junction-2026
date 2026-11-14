import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from defect_sorter.kinematics import inverse, tool_pose
from defect_sorter.motion import (
	HARD_MAX_SPEED_DEG_S,
	MotionLimits,
	execute,
	interpolate,
	plan_move,
	to_ticks,
)
from defect_sorter.robot_pose import RobotCalibration, readings_from_model

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
