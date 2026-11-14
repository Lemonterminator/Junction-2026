"""What the calibration code needs from a serial-bus servo arm, independent of the servo family.

Positions are the servo's reported ticks (0..4095 for one revolution, after the homing offset), loads are signed
permille of maximum torque, velocities signed ticks per second. :class:`ServoBus` is implemented by
:class:`armkit.feetech.FeetechBus` for real STS/SCS servos and by :class:`armkit.simulation.SimulatedBus`.
"""

from __future__ import annotations

import time
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Protocol

from armkit.calibration import TICKS_PER_REVOLUTION, Calibration


class ServoFaultError(RuntimeError):
	"""A servo reports an error (overload protection, over-temperature, no answer). Never retried automatically."""


@dataclass(frozen=True)
class JointSample:
	"""One reading of a joint: position (ticks), velocity (ticks/s), load (permille), temperature and error flags."""

	position: int
	velocity: int
	load: int
	temperature_c: int
	error_flags: int = 0


class Clock(Protocol):
	"""Time source and delay; real or simulated."""

	def now(self) -> float: ...

	def sleep(self, seconds: float) -> None: ...


class RealClock:
	"""Wall-clock :class:`Clock`."""

	def now(self) -> float:
		return time.monotonic()

	def sleep(self, seconds: float) -> None:
		time.sleep(seconds)


class ServoBus(Protocol):
	"""Joint-level access to one arm's servos."""

	@property
	def joints(self) -> tuple[str, ...]: ...

	def read_sample(self, joint: str) -> JointSample: ...

	def read_positions(self) -> dict[str, int]: ...

	def write_goals(self, goals: Mapping[str, int]) -> None:
		"""Goal positions (reported ticks, 0..4095) for the given joints."""
		...

	def set_torque(self, enabled: bool, joints: Iterable[str] | None = None) -> None: ...

	def set_torque_limit(self, permille: int, joints: Iterable[str] | None = None) -> None: ...

	def torque_enabled(self, joint: str) -> bool: ...

	def write_limits(self, joint: str, range_min: int, range_max: int) -> bool:
		"""Change a joint's position limits without touching its torque; False (limits unchanged) if refused."""
		...

	def read_goal(self, joint: str) -> int:
		"""The goal position the joint is currently holding."""
		...

	def torque_limit(self, joint: str) -> int: ...

	def hold(self, joints: Iterable[str] | None = None) -> None:
		"""Set each goal to the present position, then enable torque: the joint stiffens where it is."""
		...

	def read_calibration(self) -> Calibration:
		"""Homing offsets and position limits currently stored in the servos."""
		...

	def reset_calibration(self) -> None:
		"""Torque off; homing offsets to 0 and position limits to the full turn (so no old range clips a search)."""
		...

	def write_calibration(self, calibration: Calibration) -> None:
		"""Store offsets and limits in the servos; torque must be off."""
		...


class Unwrapper:
	"""Turns wrapped encoder readings (0..4095) into a continuous count, assuming small steps between samples."""

	def __init__(self, first: int) -> None:
		self._last = first
		self.value = float(first)

	def __call__(self, raw: int) -> float:
		step = (raw - self._last + TICKS_PER_REVOLUTION // 2) % TICKS_PER_REVOLUTION - TICKS_PER_REVOLUTION // 2
		self._last = raw
		self.value += step
		return self.value


def check_servo(bus: ServoBus, joint: str, max_temperature_c: int) -> JointSample:
	"""Read a joint; raise :class:`ServoFaultError` on error flags or a sustained temperature at or above the limit.

	A single over-temperature reading is looked at again twice before it counts: servos do not heat by tens of degrees
	between samples, but a corrupted byte on the bus can look like it.
	"""
	sample = bus.read_sample(joint)
	if sample.error_flags:
		raise ServoFaultError(f"{joint} reports error flags {sample.error_flags:#04x}")
	if sample.temperature_c >= max_temperature_c:
		for _ in range(2):
			time.sleep(0.03)
			again = bus.read_sample(joint)
			if again.temperature_c < max_temperature_c:
				return again
		raise ServoFaultError(f"{joint} temperature {sample.temperature_c} C is at or above {max_temperature_c} C")
	return sample
