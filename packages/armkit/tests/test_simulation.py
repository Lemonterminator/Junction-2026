import pytest
from armkit.calibration import Calibration, JointCalibration
from armkit.servo import Unwrapper
from armkit.simulation import Obstacle, SimJoint, SimulatedBus


def bus(**kw) -> SimulatedBus:
	return SimulatedBus({"j": SimJoint(id=1, encoder=2000.0, stop_low=1000.0, stop_high=3000.0, **kw)})


class TestMotion:
	def test_torque_off_means_no_motion_and_no_load(self):
		b = bus()
		b.write_goals({"j": 2500})
		b.sleep(1.0)
		assert b.read_sample("j").position == 2000
		assert b.read_sample("j").load == 0

	def test_the_joint_slews_toward_the_goal_at_its_maximum_speed(self):
		b = bus(max_speed=400.0)
		b.hold()
		b.write_goals({"j": 2900})
		b.sleep(1.0)
		assert b.read_sample("j").position == pytest.approx(2400, abs=15)
		b.sleep(2.0)
		assert b.read_sample("j").position == pytest.approx(2900, abs=3)

	def test_a_hard_stop_holds_the_joint_and_the_load_grows_with_the_commanded_lead(self):
		b = bus(stiffness=8.0)
		b.hold()
		b.write_goals({"j": 3040})  # 40 ticks beyond the stop at 3000
		b.sleep(2.0)
		s = b.read_sample("j")
		assert s.position == pytest.approx(3000, abs=1)
		assert s.load == pytest.approx(320, abs=10)  # 8 permille per tick of error
		assert s.velocity == 0

	def test_the_torque_limit_caps_the_load(self):
		b = bus(stiffness=8.0)
		b.set_torque_limit(250)
		b.hold()
		b.write_goals({"j": 3100})
		b.sleep(2.0)
		assert b.read_sample("j").load == 250

	def test_gravity_loads_a_powered_joint_even_when_it_is_free(self):
		b = bus(gravity=140)
		b.hold()
		b.sleep(0.5)
		assert b.read_sample("j").load == 140

	def test_positions_wrap_at_the_encoder_seam(self):
		b = SimulatedBus({"j": SimJoint(id=1, encoder=4090.0, stop_low=0.0, stop_high=9000.0)})
		b.hold()
		assert b.read_sample("j").position == 4090
		b.write_goals({"j": 4095})
		b.sleep(1.0)
		b.sleep(1.0)
		# the goal register only holds 0..4095, so the joint cannot be told to cross the seam
		assert b.read_sample("j").position == 4095

	def test_the_homing_offset_shifts_the_reported_position(self):
		b = bus(offset=500)
		assert b.read_positions() == {"j": 1500}


class TestObstacles:
	def test_an_obstacle_acts_like_a_stop_until_it_has_been_touched_enough_times(self):
		b = SimulatedBus(
			{"j": SimJoint(id=1, encoder=2000.0, stop_low=1000.0, stop_high=3000.0)},
			obstacles=[Obstacle("j", position=2400.0, side=+1, clears_after_hits=1)],
		)
		b.hold()
		b.write_goals({"j": 2500})
		b.sleep(1.0)
		assert b.read_sample("j").position == pytest.approx(2400, abs=1)
		b.write_goals({"j": 2300})  # back away; the touch is over
		b.sleep(1.0)
		b.write_goals({"j": 2500})
		b.sleep(1.0)
		assert b.read_sample("j").position == pytest.approx(2500, abs=2)


class TestCalibrationRegisters:
	def test_goals_are_clamped_to_the_position_limits_in_the_servo(self):
		b = bus()
		b.write_calibration(Calibration({"j": JointCalibration(1, 0, 0, 1800, 2200)}))
		b.hold()
		b.write_goals({"j": 2900})
		b.sleep(3.0)
		assert b.read_sample("j").position == pytest.approx(2200, abs=2)
		b.set_torque(False)
		b.reset_calibration()
		b.hold()
		b.write_goals({"j": 2900})
		b.sleep(3.0)
		assert b.read_sample("j").position == pytest.approx(2900, abs=2)

	def test_calibration_can_only_be_written_with_torque_off(self):
		b = bus()
		b.hold()
		with pytest.raises(RuntimeError, match="torque"):
			b.write_calibration(Calibration({"j": JointCalibration(1, 0, 0, 1800, 2200)}))


class TestUnwrapper:
	def test_follows_the_encoder_across_the_seam_in_both_directions(self):
		u = Unwrapper(4090)
		assert [u(v) for v in (4094, 3, 10)] == [4094, 4099, 4106]
		d = Unwrapper(5)
		assert [d(v) for v in (1, 4094, 4000)] == [1, -2, -96]


class TestReadCalibration:
	def test_what_was_written_can_be_read_back(self):
		b = bus()
		cal = Calibration({"j": JointCalibration(1, 0, 120, 1800, 2200)})
		b.write_calibration(cal)
		assert b.read_calibration() == cal


class TestSag:
	def test_a_sagging_joint_settles_that_many_ticks_below_its_goal(self):
		b = bus(sag=50.0)
		b.hold()
		b.write_goals({"j": 2500})
		b.sleep(3.0)
		assert b.read_positions()["j"] == pytest.approx(2450, abs=2)


class TestGoalReadSim:
	def test_the_goal_written_is_the_goal_read(self):
		b = bus()
		b.hold()
		b.write_goals({"j": 2222})
		assert b.read_goal("j") == 2222


class TestLiveLimitWrites:
	def test_limits_can_be_written_while_holding_when_the_servo_allows_it(self):
		b = bus()
		b.hold()
		b.live_limit_writes = True
		assert b.write_limits("j", 0, 4095)
		assert (b.joint("j").limit_min, b.joint("j").limit_max) == (0, 4095)

	def test_a_servo_that_does_not_allow_it_reports_so_and_keeps_its_limits(self):
		b = bus()
		b.hold()
		b.joint("j").limit_min, b.joint("j").limit_max = 1800, 2200
		assert not b.write_limits("j", 0, 4095)
		assert (b.joint("j").limit_min, b.joint("j").limit_max) == (1800, 2200)
