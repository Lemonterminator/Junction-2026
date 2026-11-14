"""Feetech STS/SCS serial-bus servos (STS3215 in the SO-101) as a :class:`~armkit.servo.ServoBus`.

This is the only module that imports the Feetech SDK (``scservo_sdk``, from the ``feetech`` extra). Register addresses
and sign-magnitude bit positions follow the STS/SMS control table used by LeRobot, and the order of calibration writes
follows what Physical AI Studio and LeRobot do: torque off and EEPROM unlocked (``Lock`` = 0) before ``Homing_Offset``
and the position limits are written, torque on and locked again afterwards. A servo reports
``Present_Position = encoder - Homing_Offset``.

Only one process can use a serial port; stop anything else that holds it first. A servo that does not answer raises
:class:`~armkit.servo.ServoFaultError`: nothing here retries.
"""

from __future__ import annotations

import contextlib
import time
from collections.abc import Callable, Iterable, Mapping
from types import ModuleType
from typing import TypeVar

from armkit.calibration import TICKS_PER_REVOLUTION, Calibration, JointCalibration
from armkit.servo import JointSample, ServoFaultError

T = TypeVar("T")

MIN_POSITION_LIMIT, MAX_POSITION_LIMIT = 9, 11
HOMING_OFFSET = 31
TORQUE_ENABLE, ACCELERATION, GOAL_POSITION, TORQUE_LIMIT, LOCK = 40, 41, 42, 48, 55
PRESENT_POSITION = 56
"""Present position, velocity, load (2 bytes each), voltage and temperature (1 byte each) are contiguous from here."""
_SAMPLE_BYTES = 8
_READ_BACK_ATTEMPTS = 6
_READ_ATTEMPTS = 4
_WRITE_ATTEMPTS = 3
_CALIBRATION_READS = 4
_MAX_TORQUE_LIMIT = 1000
SIGN_BIT_POSITION, SIGN_BIT_VELOCITY, SIGN_BIT_LOAD, SIGN_BIT_HOMING = 15, 15, 10, 11


def encode_sign_magnitude(value: int, sign_bit: int) -> int:
	"""Register value for a signed number stored as sign bit plus magnitude."""
	limit = (1 << sign_bit) - 1
	if abs(value) > limit:
		raise ValueError(f"magnitude {abs(value)} exceeds {limit}")
	return ((1 if value < 0 else 0) << sign_bit) | abs(value)


def decode_sign_magnitude(raw: int, sign_bit: int) -> int:
	"""Signed number from a sign-bit-plus-magnitude register value."""
	magnitude = raw & ((1 << sign_bit) - 1)
	return -magnitude if (raw >> sign_bit) & 1 else magnitude


class FeetechBus:
	"""Serial connection to the servos of one arm.

	Parameters
	----------
	port : str
		Serial device (prefer ``/dev/serial/by-id/...``).
	ids : mapping
		Joint name to servo id.
	baudrate : int
		Bus speed; STS3215 default 1 Mbit/s.
	acceleration : int, optional
		When given, written to every servo's ``Acceleration`` register (0-254) for gentle starts and stops.
	sdk : module, optional
		The ``scservo_sdk`` module (injectable for tests); imported when omitted.
	"""

	def __init__(
		self,
		port: str,
		ids: Mapping[str, int],
		*,
		baudrate: int = 1_000_000,
		acceleration: int | None = None,
		sdk: ModuleType | None = None,
	) -> None:
		if sdk is None:
			import scservo_sdk as sdk
		self._sdk = sdk
		self._ids = dict(ids)
		self._port = sdk.PortHandler(port)
		if not self._port.openPort() or not self._port.setBaudRate(baudrate):
			raise OSError(f"cannot open {port} at {baudrate} baud")
		self._packet = sdk.PacketHandler(0)
		self._goal = sdk.GroupSyncWrite(self._port, self._packet, GOAL_POSITION, 2)
		if acceleration is not None:
			for joint in self._ids:
				self._write(joint, ACCELERATION, acceleration, 1)

	@property
	def joints(self) -> tuple[str, ...]:
		return tuple(self._ids)

	def close(self) -> None:
		"""Release the serial port."""
		self._port.closePort()

	def __enter__(self) -> FeetechBus:
		return self

	def __exit__(self, *exc: object) -> None:
		self.close()

	# ---- register access -----------------------------------------------------------------------------------------
	def _joints(self, joints: Iterable[str] | None) -> list[str]:
		return list(self._ids) if joints is None else list(joints)

	def _check(self, joint: str, result: int, what: str) -> None:
		if result != self._sdk.COMM_SUCCESS:
			raise ServoFaultError(
				f"{joint} (id {self._ids[joint]}) did not answer {what}: {self._packet.getTxRxResult(result)}"
			)

	def _once(self, joint: str, what: str, call: Callable[[], T]) -> T:
		"""Run one idempotent read, absorbing a few missing replies; raises once the servo stays silent.

		Reading changes nothing, so repeating it is safe. A servo is briefly unresponsive after EEPROM writes and
		occasionally drops a reply; a servo that is really gone still ends in :class:`ServoFaultError` after
		``_READ_ATTEMPTS`` tries (a few tens of milliseconds), never in a silent guess.
		"""
		for attempt in range(_READ_ATTEMPTS):
			try:
				return call()
			except (ServoFaultError, IndexError):  # the SDK indexes into an empty reply instead of returning an error
				if attempt == _READ_ATTEMPTS - 1:
					raise ServoFaultError(f"{joint} (id {self._ids[joint]}): no reply to {what}") from None
				time.sleep(0.025)
		raise AssertionError("unreachable")

	def _read(self, joint: str, address: int, length: int) -> int:
		read = self._packet.read1ByteTxRx if length == 1 else self._packet.read2ByteTxRx

		def attempt() -> int:
			value, result, _ = read(self._port, self._ids[joint], address)
			self._check(joint, result, f"a read of register {address}")
			return value

		return self._once(joint, f"a read of register {address}", attempt)

	def _write(self, joint: str, address: int, value: int, length: int) -> None:
		"""Write one register. Every register written here takes an absolute value, so a write whose acknowledgement
		is missing or garbled is simply repeated (a few times) before it counts as a fault."""
		write = self._packet.write1ByteTxRx if length == 1 else self._packet.write2ByteTxRx
		for attempt in range(_WRITE_ATTEMPTS):
			result, _ = write(self._port, self._ids[joint], address, value)
			if result == self._sdk.COMM_SUCCESS:
				return
			if attempt == _WRITE_ATTEMPTS - 1:
				self._check(joint, result, f"a write to register {address}")
			time.sleep(0.025)

	def _write_eeprom(self, joint: str, address: int, value: int) -> None:
		"""Write a 2-byte EEPROM register and confirm it by reading it back.

		A servo is busy for a moment after an EEPROM write and may not acknowledge it even though the value was stored,
		so a missing acknowledgement is accepted when the read-back matches. A write the servo ignored altogether is repeated
		(EEPROM writes are idempotent) up to ``_WRITE_ATTEMPTS`` times; a value that still does not take is a fault.
		"""
		for _ in range(_WRITE_ATTEMPTS):
			with contextlib.suppress(ServoFaultError):
				self._write(joint, address, value, 2)
			for _ in range(_READ_BACK_ATTEMPTS):
				time.sleep(0.05)
				try:
					if self._read(joint, address, 2) == value:
						return
				except ServoFaultError:
					pass  # still busy: no reply, or the old value still showing; reading is harmless, so look again
		raise ServoFaultError(f"{joint}: the write to register {address} did not take (no matching read-back)")

	# ---- ServoBus ------------------------------------------------------------------------------------------------
	def read_sample(self, joint: str) -> JointSample:
		def attempt() -> tuple[list[int], int]:
			data, result, error = self._packet.readTxRx(self._port, self._ids[joint], PRESENT_POSITION, _SAMPLE_BYTES)
			self._check(joint, result, "a state read")
			if len(data) < _SAMPLE_BYTES:
				raise ServoFaultError(f"{joint}: short reply to a state read ({len(data)} of {_SAMPLE_BYTES} bytes)")
			return data, error

		data, error = self._once(joint, "a state read", attempt)
		word = [data[i] | data[i + 1] << 8 for i in (0, 2, 4)]
		return JointSample(
			position=decode_sign_magnitude(word[0], SIGN_BIT_POSITION),
			velocity=decode_sign_magnitude(word[1], SIGN_BIT_VELOCITY),
			load=decode_sign_magnitude(word[2], SIGN_BIT_LOAD),
			temperature_c=data[7],
			error_flags=error,
		)

	def read_positions(self) -> dict[str, int]:
		return {
			joint: decode_sign_magnitude(self._read(joint, PRESENT_POSITION, 2), SIGN_BIT_POSITION)
			for joint in self._ids
		}

	def write_goals(self, goals: Mapping[str, int]) -> None:
		self._goal.clearParam()
		for joint, value in goals.items():
			v = int(value)
			self._goal.addParam(self._ids[joint], [v & 0xFF, (v >> 8) & 0xFF])
		result = self._goal.txPacket()
		if result != self._sdk.COMM_SUCCESS:
			raise ServoFaultError(f"goal write failed: {self._packet.getTxRxResult(result)}")

	def set_torque(self, enabled: bool, joints: Iterable[str] | None = None) -> None:
		for joint in self._joints(joints):
			self._write(joint, TORQUE_ENABLE, 1 if enabled else 0, 1)
			self._write(joint, LOCK, 1 if enabled else 0, 1)
			for _ in range(_READ_BACK_ATTEMPTS):  # the servo reports the new state a moment later
				if self.torque_enabled(joint) == enabled:
					break
				time.sleep(0.05)
			else:
				raise ServoFaultError(
					f"{joint}: torque did not switch {'on' if enabled else 'off'} (no matching read-back)"
				)

	def set_torque_limit(self, permille: int, joints: Iterable[str] | None = None) -> None:
		if not 0 <= int(permille) <= _MAX_TORQUE_LIMIT:
			raise ValueError(f"torque limit {permille} is outside 0..{_MAX_TORQUE_LIMIT} permille")
		for joint in self._joints(joints):
			self._write(joint, TORQUE_LIMIT, int(permille), 2)

	def write_limits(self, joint: str, range_min: int, range_max: int) -> bool:
		"""Change the position limits while the joint keeps its torque: open the EEPROM lock, write and verify both
		limits, close the lock again. Returns False, with the old limits put back where possible, if the servo does not
		take them (some firmware only accepts EEPROM writes with torque off)."""
		old = (self._read(joint, MIN_POSITION_LIMIT, 2), self._read(joint, MAX_POSITION_LIMIT, 2))
		self._write(joint, LOCK, 0, 1)
		try:
			self._write_eeprom(joint, MIN_POSITION_LIMIT, range_min)
			self._write_eeprom(joint, MAX_POSITION_LIMIT, range_max)
			return True
		except ServoFaultError:
			for address, value in zip((MIN_POSITION_LIMIT, MAX_POSITION_LIMIT), old, strict=True):
				with contextlib.suppress(ServoFaultError):
					self._write(joint, address, value, 2)
			return False
		finally:
			self._write(joint, LOCK, 1, 1)  # always leave the EEPROM locked, however it was found

	def read_goal(self, joint: str) -> int:
		return decode_sign_magnitude(self._read(joint, GOAL_POSITION, 2), SIGN_BIT_POSITION)

	def torque_enabled(self, joint: str) -> bool:
		return bool(self._read(joint, TORQUE_ENABLE, 1))

	def torque_limit(self, joint: str) -> int:
		"""Present torque limit, believed only when two reads agree and it lies in 0..1000 (it is written back later)."""
		previous = None
		for _ in range(_CALIBRATION_READS):
			value = self._read(joint, TORQUE_LIMIT, 2)
			if value == previous and 0 <= value <= _MAX_TORQUE_LIMIT:
				return value
			previous = value
		raise ServoFaultError(f"{joint}: torque limit reads do not agree or are out of range (last {previous})")

	def hold(self, joints: Iterable[str] | None = None) -> None:
		names = self._joints(joints)
		self.write_goals(
			{joint: decode_sign_magnitude(self._read(joint, PRESENT_POSITION, 2), SIGN_BIT_POSITION) for joint in names}
		)
		self.set_torque(True, names)

	def reset_calibration(self) -> None:
		self.set_torque(False)
		for joint in self._ids:
			self._write_eeprom(joint, HOMING_OFFSET, 0)
			self._write_eeprom(joint, MIN_POSITION_LIMIT, 0)
			self._write_eeprom(joint, MAX_POSITION_LIMIT, TICKS_PER_REVOLUTION - 1)

	def write_calibration(self, calibration: Calibration) -> None:
		for joint in calibration:
			if self._read(joint, TORQUE_ENABLE, 1):
				raise RuntimeError(f"{joint}: torque is on; calibration registers are only written with torque off")
		for joint, cal in calibration.items():
			self._write_eeprom(joint, HOMING_OFFSET, encode_sign_magnitude(cal.homing_offset, SIGN_BIT_HOMING))
			self._write_eeprom(joint, MIN_POSITION_LIMIT, cal.range_min)
			self._write_eeprom(joint, MAX_POSITION_LIMIT, cal.range_max)

	def read_calibration(self) -> Calibration:
		"""Offsets and limits stored in the servos, believed only once two consecutive reads agree.

		On a noisy bus a reply can be paired with the wrong request; a calibration read that way and later written back
		would corrupt the servo, so a single read is never trusted.
		"""
		previous = None
		for _ in range(_CALIBRATION_READS):
			current = self._read_calibration_once()
			if current == previous:
				return current
			previous = current
		raise ServoFaultError("the stored calibration reads do not agree; the bus is too noisy to trust them")

	def _read_calibration_once(self) -> Calibration:
		return Calibration(
			{
				joint: JointCalibration(
					id=servo_id,
					drive_mode=0,
					homing_offset=decode_sign_magnitude(self._read(joint, HOMING_OFFSET, 2), SIGN_BIT_HOMING),
					range_min=self._read(joint, MIN_POSITION_LIMIT, 2),
					range_max=self._read(joint, MAX_POSITION_LIMIT, 2),
				)
				for joint, servo_id in self._ids.items()
			}
		)
