import pytest
import test_procedure
from armkit.calibration import TICKS_PER_DEGREE as TPD
from armkit.frame import ModelFrame
from armkit.park import current_pose, plan_move, run_move
from armkit.simulation import SimJoint, SimulatedBus
from test_procedure import profile

TOY_FRAME = ModelFrame.trusted({"a": 0.0, "b": 0.0}, "toy")


def arm(a_deg=0.0, b_deg=0.0):
	"""Toy arm (a id 1, b id 2) whose stored calibration puts each joint's zero at the midpoint of its stops."""
	a = SimJoint(id=1, encoder=2200.0 + a_deg * TPD, stop_low=1000.0, stop_high=3400.0, torque_limit=900)
	b = SimJoint(id=2, encoder=2000.0 + b_deg * TPD, stop_low=1000.0, stop_high=3000.0, torque_limit=900)
	a.limit_min, a.limit_max = 1000, 3400
	b.limit_min, b.limit_max = 1000, 3000
	bus = SimulatedBus({"a": a, "b": b})
	bus.hold()
	return bus, profile(test_procedure.TestCollisionAwareness.SHAPES)


class TestPlan:
	def test_the_current_pose_comes_from_the_stored_calibration(self):
		bus, prof = arm(a_deg=30.0, b_deg=-20.0)
		pose = current_pose(bus, prof)
		assert pose["a"] == pytest.approx(30.0, abs=0.2)
		assert pose["b"] == pytest.approx(-20.0, abs=0.2)

	def test_a_collision_free_move_has_waypoints_no_bigger_than_the_step_and_ends_on_the_target(self):
		bus, prof = arm(a_deg=0.0)
		plan = plan_move(prof, current_pose(bus, prof), {"a": -89.0}, step_deg=0.5, margin_m=0.005)
		assert plan.ok, plan.reason
		assert plan.path[-1]["a"] == pytest.approx(-89.0)
		steps = [abs(y["a"] - x["a"]) for x, y in zip(plan.path, plan.path[1:], strict=False)]
		assert max(steps) <= 0.5 + 1e-9

	def test_a_target_that_collides_is_refused(self):
		bus, prof = arm(a_deg=-89.0)
		plan = plan_move(prof, current_pose(bus, prof), {"a": 0.0, "b": 90.0}, step_deg=0.5, margin_m=0.005)
		assert not plan.ok


class TestRun:
	def test_the_arm_follows_the_plan_and_its_torque_limits_are_put_back(self):
		bus, prof = arm(a_deg=0.0)
		plan = plan_move(prof, current_pose(bus, prof), {"a": -89.0}, step_deg=0.5, margin_m=0.005)
		result = run_move(
			bus, prof, plan, confirm=lambda m: True, clock=bus, torque_limit_permille=400, frame=TOY_FRAME
		)
		assert result.ok, result.reason
		assert current_pose(bus, prof)["a"] == pytest.approx(-89.0, abs=1.5)
		assert bus.joint("a").torque_limit == 900
		assert bus.joint("b").torque_limit == 900
		assert bus.joint("a").torque
		assert bus.joint("b").torque

	def test_without_confirmation_nothing_moves(self):
		bus, prof = arm(a_deg=0.0)
		plan = plan_move(prof, current_pose(bus, prof), {"a": -89.0}, step_deg=0.5, margin_m=0.005)
		before = bus.read_positions()
		result = run_move(bus, prof, plan, confirm=lambda m: False, clock=bus, frame=TOY_FRAME)
		assert not result.ok
		assert bus.read_positions() == before

	def test_a_plan_that_is_not_ok_is_never_run(self):
		bus, prof = arm(a_deg=-89.0)
		plan = plan_move(prof, current_pose(bus, prof), {"a": 0.0, "b": 90.0}, step_deg=0.5, margin_m=0.005)
		before = bus.read_positions()
		result = run_move(bus, prof, plan, confirm=lambda m: True, clock=bus, frame=TOY_FRAME)
		assert not result.ok
		assert bus.read_positions() == before

	def test_a_target_outside_the_stored_range_is_refused_before_moving(self):
		bus, prof = arm(a_deg=0.0)
		plan = plan_move(prof, current_pose(bus, prof), {"a": 106.0}, step_deg=0.5, margin_m=0.0)
		before = bus.read_positions()
		result = run_move(bus, prof, plan, confirm=lambda m: True, clock=bus, frame=TOY_FRAME)
		assert not result.ok
		assert "range" in result.reason
		assert bus.read_positions() == before


class TestChainJointsCountAsLoaded:
	def test_a_sticky_chain_joint_that_reads_light_at_rest_moves_without_false_contacts(self):
		bus, prof = arm(a_deg=0.0)
		bus.joint("a").deadband, bus.joint("a").stiffness = 80, 1.5  # needs a large error before it lifts off
		plan = plan_move(prof, current_pose(bus, prof, frame=TOY_FRAME), {"a": -60.0}, margin_m=0.0)
		result = run_move(
			bus, prof, plan, confirm=lambda m: True, clock=bus, frame=TOY_FRAME, torque_limit_permille=900
		)
		assert result.ok, result.reason
		assert result.events == ()
