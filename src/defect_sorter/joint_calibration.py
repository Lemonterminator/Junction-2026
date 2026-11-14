"""Joint calibration from the camera: fit joint zero offsets and the robot's pose on the table.

Each :class:`Observation` pairs the follower's joint readings (degrees, from :func:`ticks_to_degrees`) with the pose
of a marker on the gripper, measured in the table frame (:mod:`defect_sorter.alignment`). :func:`solve` fits

* the zero offsets of ``shoulder_lift``, ``elbow_flex`` and ``wrist_flex``,
* the pose of the robot base in the table frame (the camera-to-robot transform),
* how the marker sits on the gripper,

so that forward kinematics (:mod:`defect_sorter.kinematics`) reproduces every measured marker pose.

Two zeros cannot be observed this way and are deliberately not fitted: a ``shoulder_pan`` offset is
indistinguishable from the base being turned on the table, and a ``wrist_roll`` offset from the marker being taped
on at another angle. They are absorbed into the base yaw and the marker mounting. Fixing them needs a reference
with known geometry (a marker squared to the base edge, or to a modelled face of the gripper).

The result is a measurement; nothing here writes to the arms.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

from defect_sorter.kinematics import forward

SOLVED_JOINTS: tuple[str, ...] = ("shoulder_lift", "elbow_flex", "wrist_flex")
MIN_OBSERVATIONS = 6
TICKS_PER_DEGREE = 4095 / 360


def ticks_to_degrees(ticks: float, range_min: float, range_max: float) -> float:
	"""Joint angle in degrees from raw ticks, zero at the calibrated range midpoint (LeRobot / Studio convention)."""
	return (ticks - (range_min + range_max) / 2.0) / TICKS_PER_DEGREE


def angles_from_ticks(ticks: dict[str, float], ranges: dict[str, tuple[float, float]]) -> dict[str, float]:
	"""Convert raw ticks to degrees for every joint that has a calibrated range."""
	return {name: ticks_to_degrees(ticks[name], *ranges[name]) for name in ticks if name in ranges}


@dataclass(frozen=True)
class Observation:
	"""Joint readings (degrees) and the gripper marker's measured pose in the table frame (metres)."""

	angles_deg: dict[str, float]
	marker_rotation: np.ndarray
	marker_position_m: np.ndarray


@dataclass(frozen=True)
class CalibrationResult:
	"""Fitted offsets (degrees, to add to the readings), base and marker poses, and fit quality."""

	offsets_deg: dict[str, float]
	base_rotation: np.ndarray
	base_position_m: np.ndarray
	mount_rotation: np.ndarray
	mount_position_m: np.ndarray
	rms_position_mm: float
	rms_rotation_deg: float
	per_observation: list[tuple[float, float]]
	n_observations: int


def _unpack(x: np.ndarray):
	offsets = dict(zip(SOLVED_JOINTS, x[:3], strict=True))
	return (
		offsets,
		Rotation.from_rotvec(x[3:6]).as_matrix(),
		x[6:9],
		Rotation.from_rotvec(x[9:12]).as_matrix(),
		x[12:15],
	)


def _predict(x: np.ndarray, angles: dict[str, float]) -> tuple[np.ndarray, np.ndarray]:
	offsets, base_r, base_t, mount_r, mount_t = _unpack(x)
	tip = forward({k: v + offsets.get(k, 0.0) for k, v in angles.items()})
	return base_r @ tip[:3, :3] @ mount_r, base_r @ (tip[:3, :3] @ mount_t + tip[:3, 3]) + base_t


def _errors(x: np.ndarray, observations: list[Observation]) -> tuple[np.ndarray, np.ndarray]:
	pos, rot = [], []
	for o in observations:
		r, t = _predict(x, o.angles_deg)
		pos.append((t - o.marker_position_m) * 1000.0)
		rot.append(np.degrees(Rotation.from_matrix(o.marker_rotation.T @ r).as_rotvec()))
	return np.array(pos), np.array(rot)


def _residuals(x: np.ndarray, observations: list[Observation], rot_weight: float) -> np.ndarray:
	pos, rot = _errors(x, observations)
	return np.concatenate([pos.ravel(), rot.ravel() * rot_weight])


def _distinct_poses(observations: list[Observation], tol_deg: float = 2.0) -> int:
	keys = {tuple(round(o.angles_deg.get(j, 0.0) / tol_deg) for j in SOLVED_JOINTS) for o in observations}
	return len(keys)


def _initial_guess(observations: list[Observation], yaw_deg: float) -> np.ndarray:
	base_r = Rotation.from_euler("z", yaw_deg, degrees=True).as_matrix()
	centre = np.mean([o.marker_position_m for o in observations], axis=0)
	base_t = np.array([centre[0], centre[1], 0.0])
	# chordal mean of the mounting rotation implied by each observation for this base guess
	acc = np.zeros((3, 3))
	for o in observations:
		acc += (base_r @ forward(o.angles_deg)[:3, :3]).T @ o.marker_rotation
	u, _, vt = np.linalg.svd(acc)
	mount_r = u @ np.diag([1, 1, np.sign(np.linalg.det(u @ vt))]) @ vt
	return np.concatenate(
		[
			np.zeros(3),
			Rotation.from_matrix(base_r).as_rotvec(),
			base_t,
			Rotation.from_matrix(mount_r).as_rotvec(),
			np.zeros(3),
		]
	)


def solve(
	observations: list[Observation],
	*,
	rot_weight_mm_per_deg: float = 2.0,
	yaw_starts: int = 12,
	good_enough_mm: float = 0.5,
) -> CalibrationResult:
	"""Fit the observable joint offsets, the base pose and the marker mounting.

	Parameters
	----------
	observations : list of Observation
		At least :data:`MIN_OBSERVATIONS` poses that differ in the solved joints.
	rot_weight_mm_per_deg : float
		How many millimetres of position error one degree of marker rotation error is worth.
	yaw_starts : int
		Base yaw starting guesses spread over the full turn; the best fit wins.
	good_enough_mm : float
		Stop trying further starting guesses once a fit has this RMS position error or better.

	Raises
	------
	ValueError
		With too few observations or too few different poses to constrain the fit.
	"""
	if len(observations) < MIN_OBSERVATIONS:
		raise ValueError(f"need at least {MIN_OBSERVATIONS} observations, got {len(observations)}")
	if _distinct_poses(observations) < MIN_OBSERVATIONS:
		raise ValueError(f"need at least {MIN_OBSERVATIONS} different poses of the lift, elbow and wrist joints")

	best = None
	yaws = np.linspace(0.0, 360.0, yaw_starts, endpoint=False)
	for yaw in yaws:
		fit = least_squares(
			_residuals,
			_initial_guess(observations, float(yaw)),
			args=(observations, rot_weight_mm_per_deg),
			loss="soft_l1",
			f_scale=5.0,
			x_scale="jac",
			max_nfev=400,
		)
		if best is None or fit.cost < best.cost:
			best = fit
		pos, _ = _errors(best.x, observations)
		if float(np.sqrt(np.mean(np.sum(pos**2, axis=1)))) <= good_enough_mm:
			break

	offsets, base_r, base_t, mount_r, mount_t = _unpack(best.x)
	pos, rot = _errors(best.x, observations)
	pos_norm = np.linalg.norm(pos, axis=1)
	rot_norm = np.linalg.norm(rot, axis=1)
	return CalibrationResult(
		offsets_deg={k: float(v) for k, v in offsets.items()},
		base_rotation=base_r,
		base_position_m=np.asarray(base_t, dtype=np.float64),
		mount_rotation=mount_r,
		mount_position_m=np.asarray(mount_t, dtype=np.float64),
		rms_position_mm=float(np.sqrt(np.mean(pos_norm**2))),
		rms_rotation_deg=float(np.sqrt(np.mean(rot_norm**2))),
		per_observation=[(float(p), float(r)) for p, r in zip(pos_norm, rot_norm, strict=True)],
		n_observations=len(observations),
	)
