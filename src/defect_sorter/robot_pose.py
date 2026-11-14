"""Where the follower stands on the table, and how its joint readings map to the kinematic model.

A :class:`RobotCalibration` holds what the camera-based joint calibration measured: the zero offsets of the
observable joints and the pose of ``base_link`` in the table frame (:mod:`defect_sorter.alignment`). With it, a
point found by the top camera (a brick, a bowl) becomes a target in the robot's own frame for
:func:`defect_sorter.kinematics.inverse`, and the model angles that come back become joint readings to command.

The base pose is only valid while the robot stays put. A marker fixed on the base plate makes it portable: measure
the marker once next to a calibrated base (:func:`link_base_marker`), and afterwards a single detection of that
marker gives the base pose wherever the robot is moved (:func:`base_from_marker`). The joint offsets belong to the
arm and survive the move.

Angles are degrees, lengths metres. Model angle = joint reading + offset.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np


def _transform(rotation: np.ndarray, position: np.ndarray) -> np.ndarray:
	t = np.eye(4)
	t[:3, :3] = rotation
	t[:3, 3] = position
	return t


@dataclass(frozen=True)
class RobotCalibration:
	"""Joint zero offsets and the pose of ``base_link`` in the table frame.

	Parameters
	----------
	offsets_deg : dict
		Per joint, degrees to add to a reading to get the model angle; joints not listed have no offset.
	base_rotation, base_position_m : numpy.ndarray
		``base_link`` axes (columns) and origin in the table frame.
	base_marker_id : int, optional
		Marker fixed on the base plate, when linked.
	base_marker_link : numpy.ndarray, optional
		4x4 pose of ``base_link`` in that marker's frame (see :func:`link_base_marker`).
	"""

	offsets_deg: dict[str, float]
	base_rotation: np.ndarray
	base_position_m: np.ndarray
	base_marker_id: int | None = None
	base_marker_link: np.ndarray | None = None

	def to_base(self, point_table_m: np.ndarray | list[float]) -> np.ndarray:
		"""A table-frame point in ``base_link`` coordinates."""
		return self.base_rotation.T @ (np.asarray(point_table_m, dtype=np.float64) - self.base_position_m)

	def to_table(self, point_base_m: np.ndarray | list[float]) -> np.ndarray:
		"""A ``base_link`` point in table-frame coordinates."""
		return self.base_rotation @ np.asarray(point_base_m, dtype=np.float64) + self.base_position_m

	def direction_to_base(self, direction_table: np.ndarray | list[float]) -> np.ndarray:
		"""A table-frame direction (no translation) in ``base_link`` coordinates."""
		return self.base_rotation.T @ np.asarray(direction_table, dtype=np.float64)

	def relocated(self, marker_rotation: np.ndarray, marker_position_m: np.ndarray) -> RobotCalibration:
		"""The same calibration with the base pose taken from a new detection of the linked base marker."""
		if self.base_marker_link is None:
			raise ValueError("no base marker linked: run the link step next to a calibrated base first")
		r, t = base_from_marker(marker_rotation, marker_position_m, self.base_marker_link)
		return replace(self, base_rotation=r, base_position_m=t)


def link_base_marker(
	base_rotation: np.ndarray, base_position_m: np.ndarray, marker_rotation: np.ndarray, marker_position_m: np.ndarray
) -> np.ndarray:
	"""Pose of ``base_link`` in the base marker's frame, from both poses measured in the table frame."""
	return np.linalg.inv(_transform(marker_rotation, marker_position_m)) @ _transform(base_rotation, base_position_m)


def base_from_marker(
	marker_rotation: np.ndarray, marker_position_m: np.ndarray, link: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
	"""``base_link`` rotation and origin in the table frame from a base marker detection and its link."""
	t = _transform(marker_rotation, marker_position_m) @ link
	return t[:3, :3], t[:3, 3]


def model_from_readings(readings_deg: dict[str, float], calibration: RobotCalibration) -> dict[str, float]:
	"""Joint readings (Studio degrees) to kinematic-model angles."""
	return {j: v + calibration.offsets_deg.get(j, 0.0) for j, v in readings_deg.items()}


def readings_from_model(model_deg: dict[str, float], calibration: RobotCalibration) -> dict[str, float]:
	"""Kinematic-model angles to the joint readings that produce them."""
	return {j: v - calibration.offsets_deg.get(j, 0.0) for j, v in model_deg.items()}


def save_calibration(path: Path, calibration: RobotCalibration) -> None:
	"""Write a calibration as JSON."""
	path.parent.mkdir(parents=True, exist_ok=True)
	link = calibration.base_marker_link
	path.write_text(
		json.dumps(
			{
				"offsets_deg": calibration.offsets_deg,
				"base_rotation": np.asarray(calibration.base_rotation).tolist(),
				"base_position_m": np.asarray(calibration.base_position_m).tolist(),
				"base_marker_id": calibration.base_marker_id,
				"base_marker_link": None if link is None else np.asarray(link).tolist(),
			},
			indent=1,
		)
	)


def load_calibration(path: Path) -> RobotCalibration:
	"""Read a calibration written by :func:`save_calibration`."""
	d = json.loads(path.read_text())
	link = d.get("base_marker_link")
	return RobotCalibration(
		offsets_deg={k: float(v) for k, v in d["offsets_deg"].items()},
		base_rotation=np.array(d["base_rotation"]),
		base_position_m=np.array(d["base_position_m"]),
		base_marker_id=d.get("base_marker_id"),
		base_marker_link=None if link is None else np.array(link),
	)
