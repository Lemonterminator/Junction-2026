"""Servo calibration data: homing offset and recorded range per joint, in the LeRobot / Physical AI Studio layout.

A joint's calibration is what the servo reports after its homing offset is applied (``homing_offset``) plus the
recorded travel ends (``range_min`` / ``range_max``, raw ticks in that frame). The middle of the recorded range is
the joint's zero, so angles and normalised values do not depend on where the encoder seam happens to sit.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path

TICKS_PER_REVOLUTION = 4096
HALF_TURN = TICKS_PER_REVOLUTION // 2 - 1
TICKS_PER_DEGREE = (TICKS_PER_REVOLUTION - 1) / 360.0
"""Studio / LeRobot convert degrees with the full-scale count 4095, not 4096."""

_FIELDS = ("id", "drive_mode", "homing_offset", "range_min", "range_max")


@dataclass(frozen=True)
class JointCalibration:
	"""Calibration of one servo joint.

	Parameters
	----------
	id : int
		Servo bus id.
	drive_mode : int
		0 for normal direction, 1 for inverted (carried through unchanged).
	homing_offset : int
		Value subtracted from the encoder by the servo so that the middle of the range reads near ``HALF_TURN``.
	range_min, range_max : int
		Recorded travel ends in the servo's reported ticks.
	"""

	id: int
	drive_mode: int
	homing_offset: int
	range_min: int
	range_max: int

	def __post_init__(self) -> None:
		if self.range_max <= self.range_min:
			raise ValueError(f"range {self.range_min}..{self.range_max} is empty")

	@property
	def midpoint(self) -> float:
		"""Middle of the recorded range, ticks."""
		return (self.range_min + self.range_max) / 2.0

	def to_degrees(self, ticks: float) -> float:
		"""Angle from the range midpoint in degrees."""
		return (ticks - self.midpoint) / TICKS_PER_DEGREE

	def to_ticks(self, degrees: float) -> int:
		"""Raw ticks for an angle from the range midpoint (inverse of :meth:`to_degrees`)."""
		return round(self.midpoint + degrees * TICKS_PER_DEGREE)

	def to_normalized(self, ticks: float, *, unsigned: bool = False) -> float:
		"""Position across the recorded range: -100..100, or 0..100 when ``unsigned`` (grippers)."""
		fraction = (ticks - self.range_min) / (self.range_max - self.range_min)
		return fraction * 100.0 if unsigned else fraction * 200.0 - 100.0


class Calibration(Mapping[str, JointCalibration]):
	"""Named joint calibrations; saved and loaded as the JSON file Studio and LeRobot use."""

	def __init__(self, joints: Mapping[str, JointCalibration]) -> None:
		self._joints = dict(joints)

	def __getitem__(self, name: str) -> JointCalibration:
		return self._joints[name]

	def __iter__(self) -> Iterator[str]:
		return iter(self._joints)

	def __len__(self) -> int:
		return len(self._joints)

	def __eq__(self, other: object) -> bool:
		return isinstance(other, Calibration) and self._joints == other._joints

	__hash__ = None  # type: ignore[assignment]

	def to_dict(self) -> dict[str, dict[str, int]]:
		"""Plain dictionary in the file layout."""
		return {name: asdict(joint) for name, joint in self._joints.items()}

	def save(self, path: Path) -> None:
		"""Write the calibration as JSON."""
		path.write_text(json.dumps(self.to_dict(), indent=4) + "\n")

	@classmethod
	def load(cls, path: Path) -> Calibration:
		"""Read a calibration file; raises ``ValueError`` naming the joint when a field is missing."""
		joints = {}
		for name, fields in json.loads(path.read_text()).items():
			missing = [f for f in _FIELDS if f not in fields]
			if missing:
				raise ValueError(f"calibration for {name} is missing {', '.join(missing)}")
			joints[name] = JointCalibration(**{f: int(fields[f]) for f in _FIELDS})
		return cls(joints)
