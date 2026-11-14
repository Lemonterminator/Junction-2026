import pytest
from armkit.calibration import Calibration, JointCalibration
from armkit.feetech import FeetechBus, decode_sign_magnitude, encode_sign_magnitude
from armkit.servo import ServoFaultError

IDS = {"a": 1, "b": 2}


class FakeSdk:
	"""Byte-addressed register memory per servo id behind the handful of scservo_sdk calls the adapter uses."""

	COMM_SUCCESS = 0
	COMM_TX_FAIL = -1001

	def __init__(self):
		self.mem = {i: {} for i in IDS.values()}
		self.errors = dict.fromkeys(IDS.values(), 0)
		self.silent: set[int] = set()
		self.stale_reads = 0  # after an EEPROM write the next reads still return the previous value
		self.stale: dict[tuple[int, int], tuple[int, int]] = {}
		self.stale_torque_reads: dict[int, int] = {}
		self.flaky_reads = 0  # the next reads crash the way scservo_sdk does when a reply is missing
		self.lose_ack: set[int] = set()  # addresses whose write is stored but never acknowledged
		self.drop: set[int] = set()  # addresses whose write is ignored
		self.drop_first: dict[int, int] = {}  # address -> how many writes are ignored before one takes
		self.writes: list[tuple[int, int, int]] = []  # (servo id, address, value) in order, sync writes included
		sdk = self

		class PortHandler:
			def __init__(self, port):
				self.port = port

			def openPort(self):
				return True

			def setBaudRate(self, baudrate):
				return True

			def closePort(self):
				pass

		class PacketHandler:
			def __init__(self, version):
				pass

			def getTxRxResult(self, result):
				return f"result {result}"

			def readTxRx(self, port, servo_id, address, length):
				if servo_id in sdk.silent:
					return [], sdk.COMM_TX_FAIL, 0
				return (
					[sdk.mem[servo_id].get(address + k, 0) for k in range(length)],
					sdk.COMM_SUCCESS,
					sdk.errors[servo_id],
				)

			def read1ByteTxRx(self, port, servo_id, address):
				if sdk.stale_torque_reads.get(servo_id, 0) > 0 and address == 40:
					sdk.stale_torque_reads[servo_id] -= 1
					return 1, sdk.COMM_SUCCESS, 0  # still reports torque on
				data, result, error = self.readTxRx(port, servo_id, address, 1)
				return (data[0] if data else 0), result, error

			def read2ByteTxRx(self, port, servo_id, address):
				if sdk.flaky_reads > 0:
					sdk.flaky_reads -= 1
					raise IndexError("list index out of range")
				if (servo_id, address) in sdk.stale:
					old, left = sdk.stale[(servo_id, address)]
					sdk.stale[(servo_id, address)] = (old, left - 1)
					if left > 0:
						return old, sdk.COMM_SUCCESS, 0
				data, result, error = self.readTxRx(port, servo_id, address, 2)
				return (data[0] | data[1] << 8 if data else 0), result, error

			def write1ByteTxRx(self, port, servo_id, address, value):
				sdk.mem[servo_id][address] = value
				sdk.writes.append((servo_id, address, value))
				return sdk.COMM_SUCCESS, 0

			def write2ByteTxRx(self, port, servo_id, address, value):
				if sdk.stale_reads:
					before = sdk.mem[servo_id].get(address, 0) | sdk.mem[servo_id].get(address + 1, 0) << 8
					sdk.stale[(servo_id, address)] = (before, sdk.stale_reads)
				if sdk.drop_first.get(address, 0) > 0:
					sdk.drop_first[address] -= 1
				elif address not in sdk.drop:
					sdk.mem[servo_id][address], sdk.mem[servo_id][address + 1] = value & 0xFF, value >> 8
				sdk.writes.append((servo_id, address, value))
				return (sdk.COMM_TX_FAIL if address in sdk.lose_ack else sdk.COMM_SUCCESS), 0

		class GroupSyncWrite:
			def __init__(self, port, packet, address, length):
				self.address, self.params = address, {}

			def clearParam(self):
				self.params = {}

			def addParam(self, servo_id, data):
				self.params[servo_id] = data
				return True

			def txPacket(self):
				for servo_id, data in self.params.items():
					value = data[0] | data[1] << 8
					sdk.mem[servo_id][self.address], sdk.mem[servo_id][self.address + 1] = data
					sdk.writes.append((servo_id, self.address, value))
				return sdk.COMM_SUCCESS

		self.PortHandler, self.PacketHandler, self.GroupSyncWrite = PortHandler, PacketHandler, GroupSyncWrite

	def put(self, servo_id, address, value, length=2):
		for k in range(length):
			self.mem[servo_id][address + k] = (value >> (8 * k)) & 0xFF


def bus(sdk=None, **kw):
	sdk = sdk or FakeSdk()
	return FeetechBus("/dev/null", IDS, sdk=sdk, **kw), sdk


class TestSignMagnitude:
	def test_negative_values_set_the_sign_bit_and_keep_the_magnitude(self):
		assert encode_sign_magnitude(-300, 11) == 2048 | 300
		assert encode_sign_magnitude(300, 11) == 300
		assert decode_sign_magnitude(2048 | 300, 11) == -300

	def test_a_magnitude_that_does_not_fit_is_refused(self):
		with pytest.raises(ValueError, match="2047"):
			encode_sign_magnitude(2048, 11)


class TestReading:
	def test_a_sample_decodes_position_velocity_load_temperature_and_flags(self):
		b, sdk = bus()
		sdk.put(1, 56, 2345)  # position
		sdk.put(1, 58, 0x8000 | 120)  # velocity: sign bit 15
		sdk.put(1, 60, 0x0400 | 210)  # load: sign bit 10
		sdk.put(1, 63, 41, length=1)  # temperature
		sdk.errors[1] = 0x20
		s = b.read_sample("a")
		assert (s.position, s.velocity, s.load, s.temperature_c, s.error_flags) == (2345, -120, -210, 41, 0x20)

	def test_an_unanswered_servo_is_a_fault_not_a_zero(self):
		b, sdk = bus()
		sdk.silent.add(2)
		with pytest.raises(ServoFaultError, match="b"):
			b.read_sample("b")

	def test_positions_of_all_joints(self):
		b, sdk = bus()
		sdk.put(1, 56, 1000)
		sdk.put(2, 56, 3000)
		assert b.read_positions() == {"a": 1000, "b": 3000}


class TestCommands:
	def test_goals_go_to_the_goal_position_register_little_endian(self):
		b, sdk = bus()
		b.write_goals({"a": 0x0A12, "b": 77})
		assert (1, 42, 0x0A12) in sdk.writes
		assert (2, 42, 77) in sdk.writes

	def test_torque_off_also_unlocks_the_eeprom_and_torque_on_locks_it_again(self):
		b, sdk = bus()
		b.set_torque(False)
		assert [w for w in sdk.writes if w[0] == 1] == [(1, 40, 0), (1, 55, 0)]
		sdk.writes.clear()
		b.set_torque(True, ["a"])
		assert sdk.writes == [(1, 40, 1), (1, 55, 1)]

	def test_hold_sets_goal_to_the_present_position_before_torque_comes_on(self):
		b, sdk = bus()
		sdk.put(1, 56, 1234)
		sdk.put(2, 56, 2222)
		b.hold()
		order = [(w[0], w[1]) for w in sdk.writes]
		assert order.index((1, 42)) < order.index((1, 40))
		assert (1, 42, 1234) in sdk.writes
		assert (2, 42, 2222) in sdk.writes

	def test_the_torque_limit_goes_to_its_own_register(self):
		b, sdk = bus()
		b.set_torque_limit(350)
		assert (1, 48, 350) in sdk.writes
		assert (2, 48, 350) in sdk.writes

	def test_acceleration_can_be_set_for_gentle_starts(self):
		_, sdk = bus(acceleration=30)
		assert (1, 41, 30) in sdk.writes
		assert (2, 41, 30) in sdk.writes


class TestCalibrationRegisters:
	def test_reset_switches_torque_off_then_clears_offsets_and_opens_the_limits(self):
		b, sdk = bus()
		b.reset_calibration()
		order = [(w[1], w[2]) for w in sdk.writes if w[0] == 1]
		assert order[:2] == [(40, 0), (55, 0)]
		assert (31, 0) in order
		assert (9, 0) in order
		assert (11, 4095) in order

	def test_a_negative_homing_offset_is_stored_sign_magnitude(self):
		b, sdk = bus()
		b.set_torque(False)
		sdk.writes.clear()
		b.write_calibration(Calibration({"a": JointCalibration(1, 0, -300, 800, 3300)}))
		assert (1, 31, 2048 | 300) in sdk.writes
		assert (1, 9, 800) in sdk.writes
		assert (1, 11, 3300) in sdk.writes

	def test_calibration_is_refused_while_torque_is_on(self):
		b, sdk = bus()
		sdk.put(1, 40, 1, length=1)
		with pytest.raises(RuntimeError, match="torque"):
			b.write_calibration(Calibration({"a": JointCalibration(1, 0, 0, 800, 3300)}))
		assert not [w for w in sdk.writes if w[1] in (31, 9, 11)]

	def test_what_the_servos_hold_can_be_read_back(self):
		b, sdk = bus()
		sdk.put(1, 31, 2048 | 77)
		sdk.put(1, 9, 700)
		sdk.put(1, 11, 3400)
		sdk.put(2, 9, 0)
		sdk.put(2, 11, 4095)
		cal = b.read_calibration()
		assert cal["a"] == JointCalibration(1, 0, -77, 700, 3400)
		assert cal["b"] == JointCalibration(2, 0, 0, 0, 4095)


class TestEepromWrites:
	def test_a_lost_acknowledgement_is_fine_when_the_value_reads_back(self):
		b, sdk = bus()
		b.set_torque(False)
		sdk.lose_ack = {9, 11, 31}
		b.write_calibration(Calibration({"a": JointCalibration(1, 0, 40, 800, 3300)}))
		assert (b._read("a", 31, 2), b._read("a", 9, 2), b._read("a", 11, 2)) == (40, 800, 3300)

	def test_a_write_that_did_not_take_is_a_fault(self):
		b, sdk = bus()
		b.set_torque(False)
		sdk.drop = {9}
		with pytest.raises(ServoFaultError, match="did not take"):
			b.write_calibration(Calibration({"a": JointCalibration(1, 0, 40, 800, 3300)}))


class TestMissingReplies:
	def test_an_sdk_crash_on_a_missing_reply_becomes_a_servo_fault(self):
		b, sdk = bus()
		sdk.flaky_reads = 50
		with pytest.raises(ServoFaultError, match="no reply"):
			b._read("a", 56, 2)

	def test_the_read_back_after_an_eeprom_write_waits_for_a_busy_servo(self):
		b, sdk = bus()
		b.set_torque(False)
		sdk.flaky_reads = 2  # the servo is still busy for the first two read attempts
		b.write_calibration(Calibration({"a": JointCalibration(1, 0, 40, 800, 3300)}))
		assert (b._read("a", 31, 2), b._read("a", 9, 2), b._read("a", 11, 2)) == (40, 800, 3300)


class TestBusyServo:
	def test_a_stale_value_right_after_an_eeprom_write_is_waited_out(self):
		b, sdk = bus()
		sdk.put(1, 11, 3492)
		b.set_torque(False)
		sdk.stale_reads = 2  # the first two read-backs still show the old limit
		b.write_calibration(Calibration({"a": JointCalibration(1, 0, 0, 0, 4095)}))
		sdk.stale_reads = 0
		assert b._read("a", 11, 2) == 4095


class TestTransientTimeouts:
	def test_a_reply_missing_once_or_twice_is_absorbed_because_reading_is_harmless(self):
		b, sdk = bus()
		sdk.put(1, 56, 1234)
		sdk.flaky_reads = 2
		assert b._read("a", 56, 2) == 1234

	def test_a_state_read_survives_a_short_silence_too(self):
		b, sdk = bus()
		sdk.put(1, 56, 777)
		calls = {"n": 0}
		original = b._packet.readTxRx

		def flaky(port, servo_id, address, length):
			calls["n"] += 1
			if calls["n"] <= 2:
				return [], sdk.COMM_TX_FAIL, 0
			return original(port, servo_id, address, length)

		b._packet.readTxRx = flaky
		assert b.read_sample("a").position == 777

	def test_a_servo_that_stays_silent_is_still_a_fault(self):
		b, sdk = bus()
		sdk.silent.add(1)
		with pytest.raises(ServoFaultError):
			b.read_sample("a")


class TestShortReplies:
	def _short_then_good(self, b, sdk, short_times):
		calls = {"n": 0}
		original = b._packet.readTxRx

		def read(port, servo_id, address, length):
			calls["n"] += 1
			if calls["n"] <= short_times:
				return [1, 2, 3], sdk.COMM_SUCCESS, 0  # "success" with too few bytes
			return original(port, servo_id, address, length)

		b._packet.readTxRx = read

	def test_a_short_state_reply_is_retried_like_a_missing_one(self):
		b, sdk = bus()
		sdk.put(1, 56, 4000)
		self._short_then_good(b, sdk, 2)
		assert b.read_sample("a").position == 4000

	def test_replies_that_stay_short_are_a_fault_not_a_crash(self):
		b, sdk = bus()
		self._short_then_good(b, sdk, 99)
		with pytest.raises(ServoFaultError, match="state read"):
			b.read_sample("a")


class TestDroppedWrites:
	def test_an_eeprom_write_the_servo_ignored_is_repeated_until_it_takes(self):
		b, sdk = bus()
		b.set_torque(False)
		sdk.drop_first = {11: 2}
		b.write_calibration(Calibration({"a": JointCalibration(1, 0, 40, 800, 3300)}))
		assert b._read("a", 11, 2) == 3300
		assert len([w for w in sdk.writes if w[:2] == (1, 11)]) == 3

	def test_a_write_that_never_takes_is_a_fault_after_a_few_tries(self):
		b, sdk = bus()
		b.set_torque(False)
		sdk.drop = {11}
		with pytest.raises(ServoFaultError, match="did not take"):
			b.write_calibration(Calibration({"a": JointCalibration(1, 0, 40, 800, 3300)}))
		assert len([w for w in sdk.writes if w[:2] == (1, 11)]) == 3


class TestNoisyWrites:
	def _fail_first(self, b, sdk, times):
		calls = {"n": 0}
		original = b._packet.write1ByteTxRx

		def write(port, servo_id, address, value):
			calls["n"] += 1
			if calls["n"] <= times:
				return -2000, 0  # "incorrect status packet"
			return original(port, servo_id, address, value)

		b._packet.write1ByteTxRx = write

	def test_a_garbled_acknowledgement_on_a_register_write_is_repeated(self):
		b, sdk = bus()
		self._fail_first(b, sdk, 2)
		b.set_torque(True, ["a"])
		assert (1, 40, 1) in sdk.writes
		assert (1, 55, 1) in sdk.writes

	def test_a_register_that_never_answers_is_a_fault(self):
		b, sdk = bus()
		self._fail_first(b, sdk, 99)
		with pytest.raises(ServoFaultError, match="register 40"):
			b.set_torque(True, ["a"])


class TestTorqueConfirmation:
	def test_torque_off_waits_until_the_servo_reports_it(self):
		b, sdk = bus()
		sdk.put(1, 40, 1, length=1)
		sdk.stale_torque_reads = {1: 3}  # the first three reads still say torque is on
		b.set_torque(False, ["a"])
		assert not b.torque_enabled("a")
		b.write_calibration(
			Calibration({"a": JointCalibration(1, 0, 5, 100, 4000)})
		)  # would raise if torque were still on

	def test_torque_that_never_switches_is_a_fault(self):
		b, sdk = bus()
		sdk.put(1, 40, 1, length=1)
		sdk.stale_torque_reads = {1: 10_000}
		with pytest.raises(ServoFaultError, match="torque"):
			b.set_torque(False, ["a"])


class TestCalibrationReadsMustAgree:
	def _garble_first_reads(self, b, sdk, times):
		calls = {"n": 0}
		original = b._packet.read2ByteTxRx

		def read(port, servo_id, address):
			calls["n"] += 1
			value, result, error = original(port, servo_id, address)
			if calls["n"] <= times:
				return (value + 777) & 0xFFF, result, error  # a reply that belonged to another request
			return value, result, error

		b._packet.read2ByteTxRx = read

	def _stored(self, sdk):
		for servo, (off, lo, hi) in {1: (40, 800, 3300), 2: (0, 100, 4000)}.items():
			sdk.put(servo, 31, off)
			sdk.put(servo, 9, lo)
			sdk.put(servo, 11, hi)

	def test_a_garbled_read_is_not_believed_until_two_reads_agree(self):
		b, sdk = bus()
		self._stored(sdk)
		self._garble_first_reads(b, sdk, 1)
		assert b.read_calibration()["a"] == JointCalibration(1, 0, 40, 800, 3300)

	def test_reads_that_never_agree_are_a_fault(self):
		b, sdk = bus()
		self._stored(sdk)
		state = {"n": 0}
		original = b._packet.read2ByteTxRx

		def read(port, servo_id, address):
			state["n"] += 1
			value, result, error = original(port, servo_id, address)
			return (value + state["n"]) & 0xFFF, result, error

		b._packet.read2ByteTxRx = read
		with pytest.raises(ServoFaultError, match="agree"):
			b.read_calibration()


class TestGoalRead:
	def test_the_goal_register_is_read_back_with_its_sign_bit(self):
		b, sdk = bus()
		sdk.put(1, 42, 2345)
		assert b.read_goal("a") == 2345


class TestTorqueLimitSanity:
	def test_a_torque_limit_outside_0_to_1000_is_never_written(self):
		b, sdk = bus()
		with pytest.raises(ValueError, match="1000"):
			b.set_torque_limit(62721, ["a"])
		assert not [w for w in sdk.writes if w[1] == 48]

	def test_a_garbled_torque_limit_read_is_not_believed(self):
		b, sdk = bus()
		sdk.put(1, 48, 500)
		calls = {"n": 0}
		original = b._packet.read2ByteTxRx

		def read(port, servo_id, address):
			calls["n"] += 1
			value, result, error = original(port, servo_id, address)
			return (62721 if calls["n"] == 1 else value), result, error

		b._packet.read2ByteTxRx = read
		assert b.torque_limit("a") == 500


class TestLiveLimitWritesFeetech:
	def test_the_lock_is_opened_the_limits_written_and_verified_then_the_lock_closed_again_with_torque_left_on(self):
		b, sdk = bus()
		sdk.put(1, 40, 1, length=1)  # torque on
		sdk.put(1, 55, 1, length=1)  # locked
		assert b.write_limits("a", 0, 4095)
		addresses = [w[1] for w in sdk.writes if w[0] == 1]
		assert addresses[0] == 55  # unlock first
		assert addresses[-1] == 55  # lock last
		assert 40 not in addresses  # torque never touched
		assert (b._read("a", 9, 2), b._read("a", 11, 2)) == (0, 4095)

	def test_a_write_the_servo_ignores_is_reported_and_the_lock_closed(self):
		b, sdk = bus()
		sdk.put(1, 40, 1, length=1)
		sdk.put(1, 9, 800)
		sdk.drop = {9, 11}
		assert not b.write_limits("a", 0, 4095)
		assert sdk.mem[1][55] == 1
