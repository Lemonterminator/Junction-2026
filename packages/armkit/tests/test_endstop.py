import itertools

import pytest
from armkit.calibration import TICKS_PER_DEGREE
from armkit.endstop import EndKind, SearchLimits, find_end
from armkit.guard import GuardLimits
from armkit.servo import ServoFaultError
from armkit.simulation import Obstacle, SimJoint, SimulatedBus

LIMITS = SearchLimits(speed_deg_s=8.0, lead_deg=3.0, backoff_deg=4.0)
BACKOFF_TICKS = 4.0 * TICKS_PER_DEGREE  # 45.5 ticks, written out so a changed default cannot move the expectation


class Recorded(SimulatedBus):
	"""Simulated bus that remembers every position and load it passed through."""

	def __init__(self, *a, **kw):
		super().__init__(*a, **kw)
		self.trace: list[tuple[float, int, int]] = []

	def sleep(self, seconds):
		super().sleep(seconds)
		s = self.read_sample("j")
		self.trace.append((self.now(), s.position, s.load))


def make(*, obstacles=(), **joint) -> Recorded:
	fields = {"id": 1, "encoder": 2000.0, "stop_low": 1000.0, "stop_high": 3000.0, "torque_limit": 350, **joint}
	bus = Recorded({"j": SimJoint(**fields)}, obstacles=obstacles)
	bus.hold()
	return bus


def search(bus, direction, **kw):
	kw.setdefault("travel_ticks", 3000.0)
	return find_end(bus, "j", direction, limits=kw.pop("limits", LIMITS), guard=GuardLimits(), clock=bus, **kw)


class TestHardStops:
	def test_finds_the_upper_stop_and_leaves_the_joint_backed_off(self):
		bus = make()
		result = search(bus, +1)
		assert result.kind is EndKind.HARD_STOP
		assert result.position == pytest.approx(3000, abs=3)
		assert len(result.contacts) >= 2
		assert bus.read_positions()["j"] == pytest.approx(3000 - BACKOFF_TICKS, abs=8)

	def test_finds_the_lower_stop(self):
		result = search(make(), -1)
		assert result.kind is EndKind.HARD_STOP
		assert result.position == pytest.approx(1000, abs=3)

	def test_the_push_never_exceeds_the_torque_limit_or_the_lead(self):
		bus = make()
		search(bus, +1)
		peak = max(abs(load) for _, _, load in bus.trace)
		assert peak <= 350
		# the goal never leads the joint by more than the 3 degree leash, so the load stays below stiffness * lead
		assert peak <= 8.0 * 3.0 * TICKS_PER_DEGREE + 20

	def test_a_joint_carrying_gravity_still_finds_the_stop_without_stopping_early(self):
		result = search(make(gravity=260), +1)
		assert result.kind is EndKind.HARD_STOP
		assert result.position == pytest.approx(3000, abs=3)


class TestStepBackWithoutFailing:
	def test_a_temporary_obstruction_makes_the_joint_step_back_and_carry_on(self):
		bus = make(obstacles=[Obstacle("j", position=2500.0, side=+1, clears_after_hits=1)])
		result = search(bus, +1)
		assert result.kind is EndKind.HARD_STOP
		assert result.position == pytest.approx(3000, abs=3)
		assert result.contacts[0].position == pytest.approx(2500, abs=3)
		# after the first contact the joint really did back off before going on
		first_contact_at = next(i for i, (_, pos, _) in enumerate(bus.trace) if pos >= 2497)
		assert min(pos for _, pos, _ in bus.trace[first_contact_at:]) < 2500 - BACKOFF_TICKS + 10

	def test_contacts_that_never_repeat_end_unconfirmed_at_the_safest_position(self):
		obstacles = [Obstacle("j", position=p, side=+1, clears_after_hits=1) for p in (2300.0, 2500.0, 2700.0)]
		result = search(make(obstacles=obstacles), +1)
		assert result.kind is EndKind.UNCONFIRMED
		assert result.position == pytest.approx(2300, abs=3)

	def test_retries_are_slower_than_the_first_approach(self):
		bus = make(obstacles=[Obstacle("j", position=2500.0, side=+1, clears_after_hits=1)])
		search(bus, +1)
		pos = [p for _, p, _ in bus.trace]
		fast = max(b - a for a, b in itertools.pairwise(pos) if 2000 < a < 2400)
		slow = max(b - a for a, b in itertools.pairwise(pos) if 2700 < a < 2900)
		assert slow < fast


class TestOtherEndings:
	def test_no_contact_within_the_allowed_travel_stops_there(self):
		bus = make(stop_high=9000.0)
		result = search(bus, +1, travel_ticks=300.0)
		assert result.kind is EndKind.TRAVEL_CAP
		assert result.position == pytest.approx(2300, abs=6)
		assert max(abs(load) for _, _, load in bus.trace) < 150

	def test_the_collision_model_can_end_a_search_early(self):
		result = search(make(), +1, stop_at=lambda pos: pos >= 2400.0)
		assert result.kind is EndKind.MODEL_LIMIT
		assert 2390 <= result.position <= 2410

	def test_the_encoder_seam_ends_a_search_because_goals_cannot_wrap(self):
		bus = make(encoder=3900.0, stop_high=9000.0, stop_low=0.0)
		result = search(bus, +1)
		assert result.kind is EndKind.SEAM
		assert result.position < 4095 - 60 + 6

	def test_an_overheated_servo_raises_instead_of_pushing_on(self):
		bus = make()
		bus.joint("j").temperature_c = 80
		with pytest.raises(ServoFaultError, match="temperature"):
			search(bus, +1)

	def test_a_servo_error_flag_raises(self):
		bus = make()
		bus.joint("j").error_flags = 0x20
		with pytest.raises(ServoFaultError, match="error"):
			search(bus, +1)


class TestTimeLimit:
	def test_a_joint_that_stops_following_its_goal_without_load_ends_the_search_instead_of_hanging(self):
		bus = make(max_speed=2.0, stop_high=9000.0)
		result = search(
			bus, +1, limits=SearchLimits(speed_deg_s=8.0, lead_deg=3.0, backoff_deg=4.0, max_duration_s=20.0)
		)
		assert result.kind in (EndKind.TIMEOUT, EndKind.NO_PROGRESS)
		assert not result.found
		assert bus.now() <= 22.0  # it ended on its own, well before any hang


class TestTemperatureReadings:
	def _spiking(self, spikes):
		bus = make()
		original = bus.read_sample
		calls = {"n": 0}

		def read(joint):
			calls["n"] += 1
			sample = original(joint)
			if calls["n"] in spikes:
				return type(sample)(sample.position, sample.velocity, sample.load, 88, sample.error_flags)
			return sample

		bus.read_sample = read
		return bus

	def test_one_corrupted_temperature_byte_does_not_stop_a_search(self):
		result = search(self._spiking({3}), +1)
		assert result.kind is EndKind.HARD_STOP

	def test_a_temperature_that_stays_high_still_stops_it(self):
		with pytest.raises(ServoFaultError, match="temperature"):
			search(self._spiking(set(range(1, 400))), +1)


class TestLoadedJointDroop:
	"""A loaded position servo settles short of its goal (here 50 ticks); a leash shorter than that never pulls it."""

	def test_a_joint_that_droops_more_than_the_leash_still_reaches_its_stop(self):
		bus = make(sag=50.0)  # the joint settles 50 ticks below its goal, i.e. against an upward search
		result = search(bus, +1)
		assert result.kind is EndKind.HARD_STOP
		assert result.position == pytest.approx(3000, abs=4)

	def test_a_drooping_joint_never_moves_backwards_when_told_to_go_forwards(self):
		bus = make(sag=50.0)
		bus.sleep(1.0)  # the droop under the initial hold is not the search's doing
		start = bus.read_positions()["j"]
		bus.trace.clear()
		search(bus, +1)
		positions = [p for _, p, _ in bus.trace]
		assert min(positions[:20]) >= start - 5


class TestStickyLoadedJoint:
	"""A loaded joint that only starts moving once its goal is more than 50 ticks away (stiction plus weight)."""

	def test_the_leash_grows_until_the_joint_moves_and_the_real_stop_is_found(self):
		bus = make(deadband=50, gravity=150, stiffness=1.5)  # about what the real elbow showed
		result = search(bus, +1)
		assert result.kind is EndKind.HARD_STOP
		assert result.position == pytest.approx(3000, abs=6)

	def test_the_leash_never_grows_past_its_cap(self):
		bus = make(deadband=50, gravity=150, stiffness=1.5)
		goals = []
		original = bus.write_goals

		def watch(g):
			goals.append(g["j"] - bus.read_positions()["j"])
			original(g)

		bus.write_goals = watch
		search(bus, +1)
		assert max(goals) <= SearchLimits().max_lead_deg * TICKS_PER_DEGREE + 10


class TestHeldWithoutProgress:
	def test_a_joint_held_at_the_longest_leash_without_moving_or_contact_load_ends_with_its_own_outcome(self):
		# the servo clamps its goal at a stored limit just past the stop: the push can never build up
		bus = make(stop_high=3000.0)
		bus.joint("j").limit_max = 3005
		result = search(bus, +1)
		assert result.kind is EndKind.NO_PROGRESS
		assert not result.found
		assert bus.now() < 60  # it did not wait for the time limit
