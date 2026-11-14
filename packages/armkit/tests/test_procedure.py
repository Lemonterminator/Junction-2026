from typing import ClassVar

import numpy as np
import pytest
from armkit.calibration import HALF_TURN, TICKS_PER_DEGREE
from armkit.collision import CollisionModel, LinkShape
from armkit.model import Joint, RobotModel
from armkit.procedure import CalibrationSettings, plan_calibration, run_calibration
from armkit.profile import ArmProfile, JointSetup
from armkit.simulation import Obstacle, SimJoint, SimulatedBus

TPD = TICKS_PER_DEGREE


def robot() -> RobotModel:
	return RobotModel(
		joints=(
			Joint("a", (0, 0, 0), (0, 0, 0), lower_deg=-100, upper_deg=100),
			Joint("b", (0.3, 0, 0), (0, 0, 0), lower_deg=-90, upper_deg=90),
		),
		link_names=("base", "upper", "fore"),
	)


def profile(shapes=None, *, kind_b="limited") -> ArmProfile:
	collision = CollisionModel(robot(), shapes or {}, floor_z=None)
	return ArmProfile(
		"toy",
		robot(),
		collision,
		(
			JointSetup("b", 2, kind=kind_b, rest_deg=85.0, park_joints=("a",)),
			JointSetup("a", 1, rest_deg=-95.0, park_joints=("b",)),
		),
	)


class Logged(SimulatedBus):
	"""Simulated bus that records every joint's true model angle after each sleep."""

	ZERO: ClassVar[dict[str, float]] = {"a": 2200.0, "b": 2000.0}

	def __init__(self, *a, **kw):
		super().__init__(*a, **kw)
		self.angles: list[dict[str, float]] = []
		self.limits_while_powered: list[int] = []

	def sleep(self, seconds):
		super().sleep(seconds)
		self.limits_while_powered += [self.joint(n).torque_limit for n in self.joints if self.joint(n).torque]
		self.angles.append({n: (self.joint(n).encoder - self.ZERO[n]) / TPD for n in self.joints})


def arm(*, a_stops=(1000.0, 3400.0), b_stops=(1000.0, 3000.0), obstacles=(), a_offset=0, b_offset=0) -> Logged:
	"""True stops are asymmetric about the model zero; the arm starts at rest against its rest-side stops."""
	a = SimJoint(id=1, encoder=a_stops[0] + 15, stop_low=a_stops[0], stop_high=a_stops[1], offset=a_offset)
	b = SimJoint(id=2, encoder=b_stops[1] - 15, stop_low=b_stops[0], stop_high=b_stops[1], offset=b_offset)
	return Logged({"a": a, "b": b}, obstacles=obstacles)


def run(bus, prof=None, *, settings=None, confirm=lambda message: True, only=None):
	return run_calibration(
		bus, prof or profile(), settings=settings or CalibrationSettings(), clock=bus, confirm=confirm, only=only
	)


class TestRun:
	def test_finds_both_ends_of_every_joint_and_stores_a_calibration_centred_on_the_range(self):
		bus = arm()
		result = run(bus)
		assert result.ok, result.issues
		margin = CalibrationSettings().end_margin_ticks
		for name, (lo, hi) in {"a": (1000.0, 3400.0), "b": (1000.0, 3000.0)}.items():
			cal = result.calibration[name]
			mid = (lo + hi) / 2
			assert cal.homing_offset == pytest.approx(mid - HALF_TURN, abs=6)
			assert cal.range_min == pytest.approx(lo + margin - (mid - HALF_TURN), abs=6)
			assert cal.range_max == pytest.approx(hi - margin - (mid - HALF_TURN), abs=6)
		assert bus.read_calibration() == result.calibration  # what the servos hold is what was reported
		assert result.wrote

	def test_the_arm_ends_back_at_its_rest_pose(self):
		bus = arm()
		result = run(bus)
		assert result.at_rest
		cal = result.calibration
		for name, rest in {"a": -95.0, "b": 85.0}.items():
			# the rest angle, read in the new frame, sits where the measured midpoint puts it
			assert bus.read_positions()[name] == pytest.approx(cal[name].midpoint + rest * TPD, abs=3 * TPD)

	def test_an_encoder_seam_inside_the_travel_does_not_matter(self):
		# raw readings wrap in the middle of joint a's travel: stops at encoder 3500..5900 read 3500..4095 then 0..1803
		bus = arm(a_stops=(3500.0, 5900.0))
		bus.ZERO = {"a": 4700.0, "b": 2000.0}
		bus.joint("a").offset = 0
		result = run(bus)
		assert result.ok, result.issues
		mid = (3500.0 + 5900.0) / 2
		assert result.calibration["a"].homing_offset in (round(mid - HALF_TURN), round(mid - HALF_TURN) - 4096)

	def test_a_previous_calibration_does_not_clip_the_search(self):
		bus = arm()
		bus.joint("a").limit_min, bus.joint("a").limit_max, bus.joint("a").offset = 1500, 2500, 300
		result = run(bus)
		assert result.ok, result.issues
		assert result.calibration["a"].range_max - result.calibration["a"].range_min > 2000

	def test_a_temporary_obstruction_is_stepped_back_from_and_noted(self):
		bus = arm(obstacles=[Obstacle("b", position=2500.0, side=-1, clears_after_hits=1)])
		result = run(bus)
		assert result.ok, result.issues
		assert result.joints["b"].contacts >= 3
		assert result.calibration["b"].range_max - result.calibration["b"].range_min > 1900

	def test_a_full_turn_joint_gets_the_whole_range_and_keeps_its_zero_without_moving(self):
		bus = arm(
			b_offset=77
		)  # b's zero was chosen earlier by whoever calibrated it; there is no stop to measure it by
		prof = profile(kind_b="full_turn")
		before = bus.joint("b").encoder
		result = run(bus, prof)
		assert result.ok, result.issues
		assert (result.calibration["b"].range_min, result.calibration["b"].range_max) == (0, 4095)
		assert result.calibration["b"].homing_offset == 77
		assert bus.read_calibration()["b"].homing_offset == 77
		assert bus.joint("b").encoder == before


class TestSubset:
	def test_only_the_chosen_joints_are_calibrated_and_the_rest_keep_what_they_had(self):
		bus = arm(a_offset=33, b_offset=-12)
		previous = bus.read_calibration()
		result = run(bus, only=["a"])
		assert result.ok, result.issues
		assert result.joints["a"].status == "measured"
		assert result.joints["b"].status == "kept"
		assert result.calibration["b"] == previous["b"]
		assert result.calibration["a"] != previous["a"]
		assert bus.read_calibration() == result.calibration

	def test_a_dry_plan_only_covers_the_chosen_joints(self):
		plan = plan_calibration(profile(), CalibrationSettings(), only=["b"])
		assert [(j.name, j.kind) for j in plan.joints] == [("b", "limited"), ("a", "kept")]
		assert plan.ok

	def test_an_unknown_joint_name_is_refused(self):
		with pytest.raises(ValueError, match="nope"):
			plan_calibration(profile(), CalibrationSettings(), only=["nope"])


class TestSafety:
	def test_nothing_is_touched_unless_the_operator_confirms(self):
		bus = arm()
		stored = bus.read_calibration()
		result = run(bus, confirm=lambda message: False)
		assert not result.ok
		assert not result.wrote
		assert bus.read_calibration() == stored
		assert not any(bus.joint(n).torque for n in bus.joints)

	def test_a_failed_run_puts_the_previous_calibration_back(self):
		# joint a never meets a stop on its upper side within the allowed travel
		bus = arm(a_stops=(1000.0, 9000.0))
		bus.joint("a").offset = 40
		stored = bus.read_calibration()
		result = run(bus)
		assert not result.ok
		assert result.calibration is None
		assert any("a" in issue and "upper" in issue for issue in result.issues)
		assert bus.read_calibration() == stored

	def test_a_servo_fault_stops_everything_and_writes_nothing_more(self):
		bus = arm()
		stored = bus.read_calibration()
		hot = {"armed": False}
		original = bus.sleep

		def sleep(seconds):
			original(seconds)
			if bus.now() > 30.0 and not hot["armed"]:
				hot["armed"] = True
				bus.joint("b").temperature_c = 90

		bus.sleep = sleep
		result = run(bus)
		assert not result.ok
		assert any("servo fault" in issue for issue in result.issues)
		assert not result.wrote
		assert bus.read_calibration() != stored  # the temporary frame is still in place; the issue says so
		assert any("restore" in issue for issue in result.issues)

	def test_the_servos_never_run_above_the_torque_limit_while_the_arm_is_moving(self):
		bus = arm()
		result = run(bus, settings=CalibrationSettings(torque_limit_permille=300))
		assert result.ok, result.issues
		assert bus.limits_while_powered
		assert max(bus.limits_while_powered) <= 300
		assert all(bus.joint(n).torque_limit == 1000 for n in bus.joints)  # normal strength is restored afterwards


class TestCollisionAwareness:
	SHAPES: ClassVar[dict[str, LinkShape]] = {
		"base": LinkShape(np.array([[0.3, 0.3, 0.0]]), np.array([0.1])),
		"fore": LinkShape(np.array([[0.3, 0.0, 0.0]]), np.array([0.05])),
	}

	def test_the_true_pose_never_comes_within_a_collision_of_the_model_while_calibrating(self):
		bus = arm()
		prof = profile(self.SHAPES)
		result = run(bus, prof)
		assert result.ok, result.issues
		clearances = [prof.collision.clearance(a).distance_m for a in bus.angles]
		assert min(clearances) > 0.0

	def test_every_planned_sweep_is_clear_in_its_parking_pose(self):
		prof = profile(self.SHAPES)
		plan = plan_calibration(prof, CalibrationSettings())
		assert plan.ok, plan.issues
		for jp in plan.joints:
			for end in jp.ends:
				for stage in end.stages:
					lo, hi = sorted(stage.span_deg)
					assert all(
						prof.collision.is_clear({**stage.pose.angles_deg, jp.name: angle})
						for angle in np.arange(lo, hi + 0.5, 1.0)
					)


class TestPlan:
	def test_a_dry_plan_lists_both_ends_per_joint_and_touches_no_bus(self):
		plan = plan_calibration(profile(), CalibrationSettings())
		assert plan.ok
		assert [j.name for j in plan.joints] == ["b", "a"]
		assert all(len(j.ends) == 2 for j in plan.joints)
		assert {e.direction for e in plan.joints[0].ends} == {-1, 1}

	def test_the_end_nearest_the_rest_pose_is_searched_first(self):
		plan = plan_calibration(profile(), CalibrationSettings())
		assert next(e.direction for e in plan.joints[0].ends) == +1  # b rests at +85 of -90..90
		assert next(e.direction for e in plan.joints[1].ends) == -1  # a rests at -95 of -100..100

	def test_an_unsearchable_end_is_reported_instead_of_planned(self):
		blocker = {
			"base": LinkShape(np.array([[0.3, 0.0, 0.0]]), np.array([0.9])),
			"fore": LinkShape(np.array([[0.3, 0.0, 0.0]]), np.array([0.05])),
		}
		plan = plan_calibration(profile(blocker), CalibrationSettings())
		assert not plan.ok
		assert any("no collision-free" in issue for issue in plan.issues)

	def test_a_plan_that_is_not_ok_is_refused_by_the_runner(self):
		blocker = {
			"base": LinkShape(np.array([[0.3, 0.0, 0.0]]), np.array([0.9])),
			"fore": LinkShape(np.array([[0.3, 0.0, 0.0]]), np.array([0.05])),
		}
		bus = arm()
		stored = bus.read_calibration()
		result = run(bus, profile(blocker))
		assert not result.ok
		assert not result.wrote
		assert bus.read_calibration() == stored
