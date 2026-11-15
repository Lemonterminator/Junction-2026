"""Access to an SO-101 arm's servos: the only module that imports ``scservo_sdk``.

:class:`SO101Reader` is read-only: present positions, torque state and the calibrated position limits. It never
enables torque and never writes positions; :meth:`SO101Reader.release_torque` (explicit, opt-in) only switches
torque off so the arm can be moved by hand, which makes a follower limp: hold it first.

:class:`SO101Driver` adds the two writes that :func:`defect_sorter.motion.execute` needs: hold the present position
and enable torque, and write goal positions. It is only constructed by the motion command, which plans and checks
every path first. Only one process can use a serial port; close Studio's environment or robot page first.
"""

from __future__ import annotations

JOINTS: tuple[str, ...] = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper")
_IDS = dict(zip(JOINTS, range(1, 7), strict=True))
_PRESENT_POSITION, _TORQUE_ENABLE, _MIN_LIMIT, _MAX_LIMIT, _GOAL_POSITION = 56, 40, 9, 11, 42


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

	def read_ticks(self, attempts: int = 3) -> dict[str, int]:
		"""Present position of every joint, raw ticks; raises if the servos do not answer in ``attempts`` reads.

		A single lost status packet on the shared bus is common; reading again is harmless (nothing is written).
		"""
		for _ in range(attempts):
			result = self._sync.txRxPacket()
			if result == self._scs.COMM_SUCCESS:
				break
		else:
			raise OSError(f"sync read failed {attempts} times: {self._packet.getTxRxResult(result)}")
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


class SO101Driver(SO101Reader):
	"""Reader plus goal-position writes. Use only through :func:`defect_sorter.motion.execute`."""

	def __init__(self, port: str, baudrate: int = 1_000_000) -> None:
		super().__init__(port, baudrate)
		self._goal = self._scs.GroupSyncWrite(self._port, self._packet, _GOAL_POSITION, 2)

	def write_goals(self, goals: dict[str, int]) -> None:
		"""Goal position for the given joints, raw ticks, in one sync write."""
		self._goal.clearParam()
		for name, value in goals.items():
			v = int(value)
			self._goal.addParam(_IDS[name], [v & 0xFF, (v >> 8) & 0xFF])
		result = self._goal.txPacket()
		if result != self._scs.COMM_SUCCESS:
			raise OSError(f"goal write failed: {self._packet.getTxRxResult(result)}")

	def hold_and_enable_torque(self) -> None:
		"""Set every goal to the present position, then enable torque: the arm stiffens where it is."""
		self.write_goals(self.read_ticks())
		for servo_id in _IDS.values():
			self._packet.write1ByteTxRx(self._port, servo_id, _TORQUE_ENABLE, 1)
