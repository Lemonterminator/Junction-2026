import itertools

import pytest
from armkit.calibration import TICKS_PER_DEGREE
from armkit.guard import GuardLimits
from armkit.motion import MoveLimits, linear_path, run_path
from armkit.servo import ServoFaultError
from armkit.simulation import Obstacle, SimJoint, SimulatedBus

LIMITS = MoveLimits(speed_deg_s=10.0, max_lag_deg=6.0, backoff_deg=3.0, max_events=3)
STEP = 10.0 * TICKS_PER_DEGREE * 0.05  # ticks per waypoint at 10 deg/s and 20 Hz


class Traced(SimulatedBus):
	def __init__(self, *a, **kw):
		super().__init__(*a, **kw)
		self.trace: list[tuple[float, int, int]] = []

	def sleep(self, seconds):
		super().sleep(seconds)
		s = self.read_sample("j")
		self.trace.append((self.now(), s.position, s.load))


def make(*, obstacles=(), **joint) -> Traced:
	fields = {"id": 1, "encoder": 2000.0, "stop_low": 500.0, "stop_high": 3500.0, "torque_limit": 350, **joint}
	bus = Traced({"j": SimJoint(**fields)}, obstacles=obstacles)
	bus.hold()
	return bus


def go(bus, goal, **kw):
	path = linear_path({"j": bus.read_positions()["j"]}, {"j": goal}, step_ticks=STEP)
	return run_path(
		bus, path, start=bus.read_positions(), limits=kw.pop("limits", LIMITS), guard=GuardLimits(), clock=bus
	)


class TestLinearPath:
	def test_steps_never_exceed_the_step_size_and_end_exactly_on_the_goal(self):
		path = linear_path({"a": 0, "b": 100}, {"a": 50, "b": 100}, step_ticks=12.0)
		assert path[-1] == {"a": 50, "b": 100}
		assert max(abs(y["a"] - x["a"]) for x, y in zip([{"a": 0}, *path], path, strict=False)) <= 12
		assert len(path) == 5


class TestRunPath:
	def test_follows_a_free_path_to_its_end_without_exceeding_the_speed(self):
		bus = make()
		result = go(bus, 2600)
		assert result.ok
		assert not result.events
		assert bus.read_positions()["j"] == pytest.approx(2600, abs=4)
		pos = [p for _, p, _ in bus.trace]
		assert max(b - a for a, b in itertools.pairwise(pos)) <= STEP + 2

	def test_a_temporary_obstruction_is_stepped_back_from_and_the_move_still_completes(self):
		bus = make(obstacles=[Obstacle("j", position=2300.0, side=+1, clears_after_hits=1)])
		result = go(bus, 2600)
		assert result.ok
		assert len(result.events) == 1
		assert bus.read_positions()["j"] == pytest.approx(2600, abs=4)
		first = next(i for i, (_, p, _) in enumerate(bus.trace) if p >= 2297)
		assert min(p for _, p, _ in bus.trace[first:]) < 2300 - 3 * TICKS_PER_DEGREE + 8  # it really stepped back

	def test_a_permanent_obstruction_ends_the_move_holding_position_not_pushing(self):
		bus = make(obstacles=[Obstacle("j", position=2300.0, side=+1)])
		result = go(bus, 2600)
		assert not result.ok
		assert "blocked" in result.reason
		assert len(result.events) == 4  # one more than max_events
		assert max(abs(load) for _, _, load in bus.trace) <= 350
		# holding: the goal register equals the present position, so nothing keeps pushing
		assert bus.joint("j").goal == pytest.approx(bus.read_positions()["j"], abs=3)
		assert bus.read_positions()["j"] < 2300

	def test_a_joint_that_cannot_keep_up_is_treated_like_a_contact(self):
		bus = make(max_speed=4.0)  # too slow even at the 1/8 playback speed of the third retry
		result = go(bus, 2600)
		assert not result.ok
		assert any("lag" in e.kind.value or "stall" in e.kind.value for e in result.events)

	def test_a_servo_fault_raises(self):
		bus = make()
		bus.joint("j").temperature_c = 90
		with pytest.raises(ServoFaultError):
			go(bus, 2600)

	def test_an_empty_path_succeeds_immediately(self):
		bus = make()
		assert run_path(bus, [], start=bus.read_positions(), limits=LIMITS, guard=GuardLimits(), clock=bus).ok


class TestServoDeadband:
	def test_a_move_that_ends_a_few_ticks_short_because_of_the_servos_deadband_still_counts_as_arrived(self):
		bus = make(deadband=11)
		result = go(bus, 2600)
		assert result.ok, result.reason
		assert abs(bus.read_positions()["j"] - 2600) <= 11

	def test_a_move_that_stops_well_short_does_not(self):
		bus = make(obstacles=[Obstacle("j", position=2300.0, side=+1)], max_speed=600.0)
		assert not go(bus, 2600).ok


class TestDroopCorrection:
	def test_a_drooping_joint_is_corrected_onto_its_target_at_the_end_of_a_move(self):
		bus = make(sag=50.0)
		result = go(bus, 2600)
		assert result.ok, result.reason
		assert abs(bus.read_positions()["j"] - 2600) <= 12

	def test_the_correction_is_bounded_so_a_blocked_joint_is_not_pushed_harder(self):
		bus = make(obstacles=[Obstacle("j", position=2550.0, side=+1)], max_speed=600.0)
		result = go(bus, 2600)
		assert not result.ok
		assert bus.joint("j").goal <= 2600 + 10 * TICKS_PER_DEGREE


class TestLoadedJointMoves:
	def test_lifting_a_heavy_sticky_joint_is_not_mistaken_for_a_stall(self):
		bus = make(gravity=200, deadband=80, stiffness=1.5, torque_limit=1000)
		result = go(bus, 2600)
		assert result.ok, result.reason
		assert result.events == ()  # no false contacts: on the real arm four of them ended the move
		assert abs(bus.read_positions()["j"] - 2600) <= 60

	def test_a_joint_named_as_possibly_loaded_is_judged_as_loaded_even_when_it_reads_light_at_rest(self):
		# resting on its stop it reads no load, but it needs a large error before it lifts off
		bus = make(deadband=80, stiffness=1.5, torque_limit=1000)
		path = linear_path({"j": bus.read_positions()["j"]}, {"j": 2600}, step_ticks=STEP)
		result = run_path(
			bus, path, start=bus.read_positions(), limits=LIMITS, guard=GuardLimits(), clock=bus, loaded_joints={"j"}
		)
		assert result.ok, result.reason
		assert result.events == ()

	def test_the_same_joint_not_named_is_judged_by_its_resting_load(self):
		bus = make(deadband=80, stiffness=1.5, torque_limit=1000)
		path = linear_path({"j": bus.read_positions()["j"]}, {"j": 2600}, step_ticks=STEP)
		result = run_path(bus, path, start=bus.read_positions(), limits=LIMITS, guard=GuardLimits(), clock=bus)
		assert result.events  # without the hint the early lag looks like a stall, which is the safe default
