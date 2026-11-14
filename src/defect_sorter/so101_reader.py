"""Read-only access to an SO-101 arm's servos: the only module that imports ``scservo_sdk``.

Reads present positions, torque state and the calibrated position limits. It never enables torque and never
writes positions; :meth:`SO101Reader.release_torque` (explicit, opt-in) only switches torque off so the arm can be
moved by hand, which makes a follower limp: hold it first. Only one process can use a serial port; close Studio's
environment or robot page before opening the port here.
"""

from __future__ import annotations

JOINTS: tuple[str, ...] = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper")
_IDS = dict(zip(JOINTS, range(1, 7), strict=True))
_PRESENT_POSITION, _TORQUE_ENABLE, _MIN_LIMIT, _MAX_LIMIT = 56, 40, 9, 11


def _signed(value: int) -> int:
	return -(value & 0x7FFF) if value & 0x8000 else value


class SO101Reader:
	"""Serial connection to the six STS3215 servos of one arm (ids 1-6, 1 Mbit/s)."""

	def __init__(self, port: str, baudrate: int = 1_000_000) -> None:
		import scservo_sdk as scs

		self._scs = scs
		self._port = scs.PortHandler(port)
		if not self._port.openPort() or not self._port.setBaudRate(baudrate):
			raise OSError(f"cannot open {port} at {baudrate} baud")
		self._packet = scs.PacketHandler(0)
		self._sync = scs.GroupSyncRead(self._port, self._packet, _PRESENT_POSITION, 2)
		for servo_id in _IDS.values():
			self._sync.addParam(servo_id)

	def read_ticks(self) -> dict[str, int]:
		"""Present position of every joint, raw ticks; raises if any servo does not answer."""
		result = self._sync.txRxPacket()
		if result != self._scs.COMM_SUCCESS:
			raise OSError(f"sync read failed: {self._packet.getTxRxResult(result)}")
		return {name: _signed(self._sync.getData(servo_id, _PRESENT_POSITION, 2)) for name, servo_id in _IDS.items()}

	def _read(self, servo_id: int, address: int, length: int) -> int:
		read = self._packet.read1ByteTxRx if length == 1 else self._packet.read2ByteTxRx
		value, result, _ = read(self._port, servo_id, address)
		if result != self._scs.COMM_SUCCESS:
			raise OSError(f"read of register {address} on servo {servo_id} failed")
		return value

	def torque_enabled(self) -> dict[str, bool]:
		return {name: bool(self._read(servo_id, _TORQUE_ENABLE, 1)) for name, servo_id in _IDS.items()}

	def ranges(self) -> dict[str, tuple[int, int]]:
		"""Calibrated position limits stored on the servos (the range Studio's calibration recorded)."""
		return {name: (self._read(i, _MIN_LIMIT, 2), self._read(i, _MAX_LIMIT, 2)) for name, i in _IDS.items()}

	def release_torque(self) -> None:
		"""Switch torque off on every servo. The arm goes limp."""
		for servo_id in _IDS.values():
			self._packet.write1ByteTxRx(self._port, servo_id, _TORQUE_ENABLE, 0)

	def close(self) -> None:
		self._port.closePort()

	def __enter__(self) -> SO101Reader:
		return self

	def __exit__(self, *exc: object) -> None:
		self.close()
