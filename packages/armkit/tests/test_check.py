import numpy as np
import pytest
from armkit.calibration import TICKS_PER_DEGREE, JointCalibration
from armkit.check import check_range
from armkit.servo import ServoFaultError
from armkit.simulation import Obstacle, SimJoint, SimulatedBus

TPD = TICKS_PER_DEGREE


def _zero(profile):
	from armkit.frame import ModelFrame

	return ModelFrame.trusted(dict.fromkeys(profile.robot.names, 0.0), "toy: midpoints are model zeros by construction")


def arm(*, stops=(1900.0, 3400.0), offset=120, limits=(2000, 3300), start=2600.0, **kw):
	"""A gripper whose true stops are 1900..3400 (encoder), calibrated earlier as 2000..3300 readings with offset 120,
	plus a neighbour that must not be touched."""
	gripper = SimJoint(id=6, encoder=start, stop_low=stops[0], stop_high=stops[1], offset=offset, **kw)
	gripper.limit_min, gripper.limit_max = limits
	wrist = SimJoint(id=5, encoder=2100.0, stop_low=900.0, stop_high=3300.0, offset=-40)
	wrist.limit_min, wrist.limit_max = 100, 4000
	bus = SimulatedBus({"gripper": gripper, "wrist": wrist})
	bus.hold(["wrist"])
	bus.hold(["gripper"])
	return bus


def check(bus, **kw):
	kw.setdefault("confirm", lambda message: True)
	return check_range(bus, "gripper", clock=bus, **kw)


class TestMeasurement:
	def test_reports_both_stops_in_the_frame_of_the_stored_calibration(self):
		bus = arm()
		result = check(bus)
		assert result.ok, result.issues
		# true stops are encoder 1900 and 3400; the stored frame subtracts the offset 120
		assert result.lower == pytest.approx(1780, abs=4)
		assert result.upper == pytest.approx(3280, abs=4)
		assert result.stored == JointCalibration(6, 0, 120, 2000, 3300)
		assert result.lower_difference_ticks == pytest.approx(1780 - 2000, abs=4)
		assert result.upper_difference_ticks == pytest.approx(3280 - 3300, abs=4)

	def test_the_search_can_go_past_the_stored_limits(self):
		bus = arm()
		check(bus)
		assert bus.joint("gripper").limit_min == 2000  # ...and they are back afterwards
		assert bus.joint("gripper").limit_max == 3300

	def test_a_temporary_obstruction_is_stepped_back_from(self):
		bus = arm(start=2600.0)
		bus._obstacles.append(Obstacle("gripper", position=3000.0, side=+1, clears_after_hits=1))
		result = check(bus)
		assert result.ok, result.issues
		assert result.upper == pytest.approx(3280, abs=4)

	def test_a_stop_that_is_not_found_is_reported_not_guessed(self):
		bus = arm(stops=(1900.0, 9000.0))
		result = check(bus)
		assert not result.ok
		assert result.upper is None
		assert any("upper" in issue for issue in result.issues)
		assert bus.joint("gripper").limit_max == 3300


class TestNothingIsChanged:
	def test_registers_torque_and_position_end_as_they_began(self):
		bus = arm()
		before = bus.read_calibration()
		position = bus.read_positions()["gripper"]
		check(bus)
		assert bus.read_calibration() == before
		assert bus.joint("gripper").torque
		assert bus.joint("gripper").torque_limit == 1000
		assert bus.read_positions()["gripper"] == pytest.approx(position, abs=4)

	def test_other_joints_are_never_touched(self):
		bus = arm()
		wrist = bus.joint("wrist")
		snapshot = (
			wrist.encoder,
			wrist.goal,
			wrist.torque,
			wrist.torque_limit,
			wrist.offset,
			wrist.limit_min,
			wrist.limit_max,
		)
		check(bus)
		assert (
			wrist.encoder,
			wrist.goal,
			wrist.torque,
			wrist.torque_limit,
			wrist.offset,
			wrist.limit_min,
			wrist.limit_max,
		) == snapshot

	def test_a_joint_whose_torque_was_off_is_left_with_torque_off(self):
		bus = arm()
		bus.set_torque(False, ["gripper"])
		check(bus)
		assert not bus.joint("gripper").torque

	def test_without_confirmation_nothing_happens(self):
		bus = arm()
		before = bus.read_calibration()
		result = check(bus, confirm=lambda message: False)
		assert not result.ok
		assert bus.read_calibration() == before
		assert bus.joint("gripper").encoder == 2600.0


class TestSafety:
	def test_the_torque_limit_stays_low_while_it_searches(self):
		bus = arm()
		seen = []
		searching = {"on": True}
		original = bus.sleep

		def sleep(seconds):
			original(seconds)
			if searching["on"] and bus.joint("gripper").torque:
				seen.append(bus.joint("gripper").torque_limit)

		bus.sleep = sleep
		check(
			bus,
			torque_limit_permille=300,
			progress=lambda m: searching.update(on="returning" not in m and searching["on"]),
		)
		assert seen
		assert max(seen) <= 300

	def test_a_servo_fault_stops_and_says_what_to_restore(self):
		bus = arm()
		bus.joint("gripper").temperature_c = 90
		result = check(bus)
		assert not result.ok
		assert any("servo fault" in issue for issue in result.issues)


class TestSetupFaults:
	def test_a_fault_before_anything_moved_restores_the_joint_by_itself(self):
		bus = arm()
		before = bus.read_calibration()
		position = bus.read_positions()["gripper"]
		original = bus.write_calibration
		calls = {"n": 0}

		def flaky(calibration):
			calls["n"] += 1
			original(calibration)
			if calls["n"] == 1:  # the widening write lands, but the servo then stops answering
				raise ServoFaultError("gripper (id 6): no reply to a read of register 11")

		bus.write_calibration = flaky
		result = check(bus)
		assert not result.ok
		assert any("restored" in issue for issue in result.issues)
		assert bus.read_calibration() == before
		assert bus.joint("gripper").torque
		assert bus.joint("gripper").torque_limit == 1000
		assert bus.read_positions()["gripper"] == position

	def test_a_fault_after_the_joint_has_moved_stops_and_leaves_things_alone(self):
		bus = arm()
		original = bus.sleep

		def sleep(seconds):
			original(seconds)
			if bus.joint("gripper").encoder > 2700:  # well into the first sweep
				bus.joint("gripper").error_flags = 0x20

		bus.sleep = sleep
		result = check(bus)
		assert not result.ok
		assert any("servo fault" in issue for issue in result.issues)
		assert not any("restored" in issue for issue in result.issues)
		assert bus.joint("gripper").limit_max == 4095  # left as it was found; the issue says how to restore


class TestWhenNothingMoved:
	def test_a_fault_in_the_first_search_read_still_restores_because_the_joint_never_moved(self):
		bus = arm()
		before = bus.read_calibration()
		bus.joint("gripper").error_flags = 0x20  # the very first sample of the search reports an error
		result = check(bus)
		assert not result.ok
		assert any("restored" in issue for issue in result.issues)
		assert bus.read_calibration() == before
		assert bus.joint("gripper").torque


class TestResultsSurviveCleanupProblems:
	def test_measurements_are_kept_and_reported_even_if_the_final_restore_fails(self):
		bus = arm()
		original = bus.write_calibration
		calls = {"n": 0}

		def write(calibration):
			calls["n"] += 1
			if calls["n"] == 2:  # the restore at the end
				raise RuntimeError("calibration registers can only be written with torque off")
			original(calibration)

		bus.write_calibration = write
		result = check(bus)
		assert result.lower == pytest.approx(1780, abs=4)
		assert result.upper == pytest.approx(3280, abs=4)
		assert not result.ok
		assert any("could not restore" in issue for issue in result.issues)

	def test_each_end_is_announced_as_soon_as_it_is_found(self):
		messages = []
		check(arm(), progress=messages.append)
		assert any("lower end found at" in m for m in messages)
		assert any("upper end found at" in m for m in messages)


class TestCollisionGate:
	"""Toy two-joint arm: ball B at (0.3, 0.3) on the base, ball F on the forearm; joint b's sweep hits B near b = 90
	when a = 0 and is clear when a = -89 (see test_poses). The simulated joints stand for a (id 1) and b (id 2)."""

	def _setup(self, a_deg, b_deg=0.0):
		import test_procedure
		from test_procedure import profile

		a = SimJoint(id=1, encoder=2200.0 + a_deg * TPD, stop_low=1000.0, stop_high=3400.0)
		b = SimJoint(id=2, encoder=2000.0 + b_deg * TPD, stop_low=1000.0, stop_high=3000.0)
		bus = SimulatedBus({"a": a, "b": b})
		bus.hold()
		# stored calibration: zero (range midpoint) at the true mid of each joint's stops
		# stored ranges a little wider than the stops, as when they were recorded by pushing to the stops
		a.limit_min, a.limit_max, a.offset = 950, 3450, 0
		b.limit_min, b.limit_max, b.offset = 950, 3050, 0
		return bus, profile(test_procedure.TestCollisionAwareness.SHAPES)

	def test_a_sweep_the_model_says_would_collide_is_refused_without_moving_anything(self):
		bus, prof = self._setup(a_deg=0.0)  # with a at 0 the forearm hits the ball near b = +61
		before = bus.read_calibration()
		position = bus.read_positions()
		result = check_range(bus, "b", clock=bus, confirm=lambda m: True, profile=prof, frame=_zero(prof))
		assert not result.ok
		assert any("collide" in issue for issue in result.issues)
		assert bus.read_calibration() == before
		assert bus.read_positions() == position

	def test_a_clear_sweep_is_measured_as_usual(self):
		bus, prof = self._setup(a_deg=-89.0)
		result = check_range(bus, "b", clock=bus, confirm=lambda m: True, profile=prof, frame=_zero(prof))
		assert result.ok, result.issues
		assert result.upper == pytest.approx(3000, abs=6)
		assert result.lower == pytest.approx(1000, abs=6)

	def test_without_a_profile_nothing_is_checked_as_before(self):
		bus, _ = self._setup(a_deg=0.0)
		assert check_range(bus, "b", clock=bus, confirm=lambda m: True).ok


class TestReturnStrength:
	def test_the_joint_returns_at_its_normal_torque_limit_not_the_low_search_one(self):
		bus = arm()
		phase = {"name": ""}
		seen = []
		original = bus.sleep

		def sleep(seconds):
			original(seconds)
			if phase["name"] == "return" and bus.joint("gripper").torque:
				seen.append(bus.joint("gripper").torque_limit)

		bus.sleep = sleep
		check(
			bus, progress=lambda m: phase.update(name="return") if "returning" in m else None, torque_limit_permille=250
		)
		assert seen
		assert set(seen) == {1000}


class TestRotationAboutTheVertical:
	"""A pan-like joint p (axis z) carrying a ball that is already 4 cm below the floor in the model. Turning p never
	changes that, so the sweep is no closer to a collision than the arm already is."""

	def _setup(self, stops=(1000.0, 3000.0)):
		from armkit.collision import CollisionModel, LinkShape
		from armkit.model import Joint, RobotModel
		from armkit.profile import ArmProfile, JointSetup

		robot = RobotModel((Joint("p", (0, 0, 0), (0, 0, 0), lower_deg=-88, upper_deg=88),), ("base", "arm"))
		shapes = {"arm": LinkShape(np.array([[0.2, 0.0, 0.01]]), np.array([0.05]))}
		profile = ArmProfile("pan-toy", robot, CollisionModel(robot, shapes, floor_z=0.0), (JointSetup("p", 1),))
		p = SimJoint(id=1, encoder=2000.0, stop_low=stops[0], stop_high=stops[1])
		p.limit_min, p.limit_max = 950, 3050  # stored a little wider than the stops
		bus = SimulatedBus({"p": p})
		bus.hold()
		return bus, profile

	def test_a_sweep_that_is_no_closer_to_a_collision_than_the_arm_already_is_allowed(self):
		bus, profile = self._setup()
		result = check_range(bus, "p", clock=bus, confirm=lambda m: True, profile=profile, frame=_zero(profile))
		assert result.ok, result.issues
		assert result.upper == pytest.approx(3000, abs=6)
		assert result.lower == pytest.approx(1000, abs=6)

	def test_a_chain_joint_with_no_stop_inside_its_stored_range_never_goes_past_that_range(self):
		bus, profile = self._setup(stops=(0.0, 9000.0))
		result = check_range(bus, "p", clock=bus, confirm=lambda m: True, profile=profile, frame=_zero(profile))
		assert result.upper is None
		assert not result.ok  # an end left at the stored limit is unmeasured, never accepted as it is
		assert any("upper" in issue and "stored limit" in issue for issue in result.issues)
		assert bus.joint("p").encoder <= 3050
		assert bus.read_calibration()["p"].range_max == 3050


class TestRotationWithUncertainNeighbours:
	"""Joint p (vertical axis) below a joint q (axis y) whose angle is uncertain: a ball on the far side of q is 4 cm
	under the floor, and +-3 degrees of q move it by about 1 cm. Turning p changes none of that."""

	def test_the_baseline_includes_the_same_pose_uncertainty_as_the_sweep(self):
		from armkit.collision import CollisionModel, LinkShape
		from armkit.model import Joint, RobotModel
		from armkit.profile import ArmProfile, JointSetup

		robot = RobotModel(
			(
				Joint("p", (0, 0, 0), (0, 0, 0), lower_deg=-88, upper_deg=88),
				Joint("q", (0, 0, 0), (0, 0, 0), axis=(0, 1, 0), lower_deg=-60, upper_deg=60),
			),
			("base", "mid", "arm"),
		)
		shapes = {"arm": LinkShape(np.array([[0.2, 0.0, 0.01]]), np.array([0.05]))}
		profile = ArmProfile(
			"toy", robot, CollisionModel(robot, shapes, floor_z=0.0), (JointSetup("p", 1), JointSetup("q", 2))
		)
		p = SimJoint(id=1, encoder=2000.0, stop_low=1000.0, stop_high=3000.0)
		q = SimJoint(id=2, encoder=2000.0, stop_low=1000.0, stop_high=3000.0)
		for j in (p, q):
			j.limit_min, j.limit_max = 950, 3050
		bus = SimulatedBus({"p": p, "q": q})
		bus.hold()
		result = check_range(bus, "p", clock=bus, confirm=lambda m: True, profile=profile, frame=_zero(profile))
		assert result.ok, result.issues


class TestOneSidedCheck:
	"""Same toy as TestCollisionGate: with a = 0 joint b's sweep hits the ball on the upward side (b about +61) but the
	downward side is clear."""

	def _setup(self):
		return TestCollisionGate()._setup(a_deg=0.0)

	def test_both_ends_are_refused_but_the_clear_end_alone_is_measured(self):
		bus, prof = self._setup()
		both = check_range(bus, "b", clock=bus, confirm=lambda m: True, profile=prof, frame=_zero(prof))
		assert not both.ok
		lower = check_range(
			bus, "b", clock=bus, confirm=lambda m: True, profile=prof, frame=_zero(prof), ends=("lower",)
		)
		assert lower.ok, lower.issues
		assert lower.lower == pytest.approx(1000, abs=6)
		assert lower.upper is None
		assert lower.upper_difference_ticks is None

	def test_the_end_that_collides_is_still_refused_when_it_alone_is_asked_for(self):
		bus, prof = self._setup()
		before = bus.read_positions()
		result = check_range(
			bus, "b", clock=bus, confirm=lambda m: True, profile=prof, frame=_zero(prof), ends=("upper",)
		)
		assert not result.ok
		assert bus.read_positions() == before

	def test_the_joint_never_goes_toward_the_end_that_was_not_asked_for(self):
		bus, prof = self._setup()
		start = bus.read_positions()["b"]
		peak = {"v": start}
		original = bus.sleep

		def sleep(seconds):
			original(seconds)
			peak["v"] = max(peak["v"], bus.read_positions()["b"])

		bus.sleep = sleep
		check_range(bus, "b", clock=bus, confirm=lambda m: True, profile=prof, frame=_zero(prof), ends=("lower",))
		assert peak["v"] <= start + 8


class TestContactDiagnostics:
	def test_every_contact_is_reported_with_its_kind_load_and_position(self):
		result = check(arm())
		assert len(result.upper_contacts) >= 2
		assert len(result.lower_contacts) >= 2
		first = result.upper_contacts[0]
		assert first.position == pytest.approx(3280, abs=6)
		assert first.load > 100
		assert first.kind.value

	def test_the_cli_prints_a_line_per_contact(self):
		from armkit.cli import describe_contacts

		lines = describe_contacts("upper", check(arm()).upper_contacts)
		assert lines[0].startswith("upper contact 1:")
		assert "load" in lines[0]
		assert "at 32" in lines[0]


class TestHoldingLoad:
	def test_a_joint_that_carries_weight_gets_a_torque_limit_it_can_hold_with(self):
		bus = arm(gravity=176, stops=(2220.0, 3370.0))  # stops inside the stored range
		seen = []
		searching = {"on": True}
		original = bus.sleep

		def sleep(seconds):
			original(seconds)
			if searching["on"] and bus.joint("gripper").torque:
				seen.append(bus.joint("gripper").torque_limit)

		bus.sleep = sleep
		messages = []

		def progress(m):
			messages.append(m)
			searching["on"] = searching["on"] and "returning" not in m

		result = check(bus, torque_limit_permille=250, progress=progress)
		assert result.ok, result.issues
		assert min(seen) >= 2 * 176 + 150
		assert any("holding load" in m for m in messages)

	def test_a_light_joint_keeps_the_requested_low_limit(self):
		bus = arm(gravity=20)
		seen = []
		original = bus.sleep

		def sleep(seconds):
			original(seconds)
			if bus.joint("gripper").torque and bus.joint("gripper").torque_limit != 1000:
				seen.append(bus.joint("gripper").torque_limit)

		bus.sleep = sleep
		check(bus, torque_limit_permille=250)
		assert set(seen) == {250}

	def test_the_raised_limit_never_exceeds_the_joints_normal_limit(self):
		bus = arm(gravity=600, torque_limit=700)
		seen = []
		original = bus.sleep

		def sleep(seconds):
			original(seconds)
			if bus.joint("gripper").torque:
				seen.append(bus.joint("gripper").torque_limit)

		bus.sleep = sleep
		check(bus, torque_limit_permille=250)
		assert max(seen) <= 700


class TestWeightBearingJoints:
	"""A joint that holds weight would drop if its torque went off, so its torque stays on and its registers untouched."""

	def _watched(self, **kw):
		bus = arm(gravity=168, **kw)
		log = {"torque_off": 0, "writes": 0}
		set_torque, write = bus.set_torque, bus.write_calibration

		def watch_torque(enabled, joints=None):
			if not enabled and (joints is None or "gripper" in joints):
				log["torque_off"] += 1
			set_torque(enabled, joints)

		def watch_write(calibration):
			log["writes"] += 1
			write(calibration)

		bus.set_torque, bus.write_calibration = watch_torque, watch_write
		return bus, log

	def test_torque_never_goes_off_and_no_register_is_written(self):
		bus, log = self._watched()
		check(bus)
		assert log == {"torque_off": 0, "writes": 0}
		assert bus.joint("gripper").torque

	def test_a_stop_inside_the_stored_range_is_still_found(self):
		# stops at 2100..3250 readings (encoder - 120): inside the stored 2000..3300
		bus, _ = self._watched(stops=(2220.0, 3370.0))
		result = check(bus)
		assert result.upper == pytest.approx(3250, abs=6)
		assert result.lower == pytest.approx(2100, abs=6)

	def test_reaching_the_stored_limit_without_contact_is_reported_not_mistaken_for_a_stop(self):
		bus, _ = self._watched()  # true stops 1780 / 3280 readings: the lower one lies outside the stored 2000..3300
		result = check(bus)
		assert result.lower is None
		assert not result.ok
		assert any("lower" in n and "stored limit" in n for n in result.issues)
		assert bus.read_positions()["gripper"] >= 1995  # never pushed past the stored limit


class TestFrameGate:
	def test_a_chain_joint_is_refused_without_a_measured_frame(self):
		bus, prof = TestCollisionGate()._setup(a_deg=-89.0)
		before = bus.read_positions()
		result = check_range(bus, "b", clock=bus, confirm=lambda m: True, profile=prof)
		assert not result.ok
		assert any("frame" in i for i in result.issues)
		assert bus.read_positions() == before


class TestChainJointsKeepTheirTorque:
	def test_a_chain_joint_never_loses_torque_even_when_it_happens_to_read_no_load(self):
		bus, prof = TestCollisionGate()._setup(a_deg=-89.0)  # joint b: no gravity in the simulation, holding load 0
		off = []
		original = bus.set_torque

		def watch(enabled, joints=None):
			if not enabled:
				off.append(joints)
			original(enabled, joints)

		bus.set_torque = watch
		result = check_range(bus, "b", clock=bus, confirm=lambda m: True, profile=prof, frame=_zero(prof))
		assert result.ok, result.issues
		assert off == []

	def test_a_chain_joint_searches_at_its_normal_torque_limit_so_it_cannot_sag(self):
		bus, prof = TestCollisionGate()._setup(a_deg=-89.0)
		bus.joint("b").torque_limit = 900
		seen = []
		original = bus.sleep

		def sleep(seconds):
			original(seconds)
			if bus.joint("b").torque:
				seen.append(bus.joint("b").torque_limit)

		bus.sleep = sleep
		check_range(
			bus, "b", clock=bus, confirm=lambda m: True, profile=prof, frame=_zero(prof), torque_limit_permille=250
		)
		assert seen
		assert set(seen) == {900}


class TestLimitsWidenedWithTorqueOn:
	"""Servos whose position limits can be changed while they hold (only the EEPROM lock is opened)."""

	def _watched(self, live):
		bus = arm(gravity=168, stops=(1900.0, 3400.0))  # weight-bearing; the lower stop lies outside the stored range
		bus.live_limit_writes = live
		off = []
		original = bus.set_torque

		def watch(enabled, joints=None):
			if not enabled:
				off.append(joints)
			original(enabled, joints)

		bus.set_torque = watch
		return bus, off

	def test_a_loaded_joint_is_measured_past_its_stored_range_without_ever_losing_torque(self):
		bus, off = self._watched(live=True)
		before = bus.read_calibration()
		result = check(bus)
		assert result.lower == pytest.approx(1780, abs=6)  # the real stop, 220 ticks below the stored 2000
		assert off == []
		assert bus.read_calibration() == before  # and the limits are back as they were

	def test_a_servo_that_refuses_the_live_write_leaves_the_end_unmeasured_as_an_issue(self):
		bus, off = self._watched(live=False)
		result = check(bus)
		assert result.lower is None
		assert off == []
		assert not result.ok
		assert any("stored limit" in n for n in result.issues)


class TestPartlyClearSweep:
	"""Same toy as TestCollisionGate (a = 0: with the pose uncertainty, joint b's upward sweep is clear to b = +50 deg), but b's stored
	range is narrower than its stops, so the clear part of the sweep already goes past the stored end."""

	def _setup(self, stored, b_stop_high=3000.0):
		bus, prof = TestCollisionGate()._setup(a_deg=0.0)
		b = bus.joint("b")
		b.limit_min, b.limit_max = stored  # symmetric about 2000, so b's model zero stays at encoder 2000
		b.stop_high = b_stop_high
		bus.live_limit_writes = True
		return bus, prof

	def _check(self, bus, prof):
		return check_range(
			bus, "b", clock=bus, confirm=lambda m: True, profile=prof, frame=_zero(prof), ends=("upper",)
		)

	def test_a_stop_inside_the_clear_part_past_the_stored_end_is_found(self):
		bus, prof = self._setup(stored=(1600, 2400), b_stop_high=2500.0)  # stored end +35 deg, stop at +44
		result = self._check(bus, prof)
		assert result.ok, result.issues
		assert result.upper == pytest.approx(2500, abs=6)

	def test_with_the_stop_beyond_the_clear_part_it_searches_up_to_there_and_reports_not_measured(self):
		bus, prof = self._setup(stored=(1600, 2400))  # stored end +35 deg, clear to +50, stop at +88
		peak = {"v": 0.0}
		original = bus.sleep

		def sleep(seconds):
			original(seconds)
			peak["v"] = max(peak["v"], bus.joint("b").encoder)

		bus.sleep = sleep
		result = self._check(bus, prof)
		assert not result.ok
		assert result.upper is None
		assert any("NOT MEASURED" in issue for issue in result.issues)
		assert peak["v"] > 2400 + 5 * TPD  # it did search past the stored end...
		assert peak["v"] < 2000 + 61 * TPD  # ...but never into the ball
		assert bus.read_calibration()["b"].range_max == 2400  # limits back as stored


class TestStoppedByTheModel:
	def test_the_sweep_is_checked_over_the_whole_search_not_only_the_model_travel(self):
		# with a = -31 the sweep is clear past b's model travel (90) and the forearm meets the ball further on, before
		# the stop at encoder 3400 (+123 deg): the search must end where the model stops calling it clear, and say so
		bus, prof = TestCollisionGate()._setup(a_deg=-31.0)
		bus.joint("b").stop_high = 3400.0
		bus.live_limit_writes = True
		result = check_range(
			bus, "b", clock=bus, confirm=lambda m: True, profile=prof, frame=_zero(prof), ends=("upper",)
		)
		assert result.upper is None
		assert not result.ok
		assert any("NOT MEASURED" in issue and "collision model" in issue for issue in result.issues)
