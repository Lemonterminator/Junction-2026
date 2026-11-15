"""Joint calibration from the camera: fit joint zero offsets and the robot's pose on the table.

Each :class:`Observation` pairs the follower's joint readings (degrees, from :func:`ticks_to_degrees`) with the pose
of a marker on the arm, measured in the table frame (:mod:`defect_sorter.alignment`). :func:`solve` fits

* the zero offsets of the joints between the base and the marker (:data:`MARKER_LINKS`),
* the pose of the robot base in the table frame (the camera-to-robot transform),
* how the marker sits on its link,

so that forward kinematics (:mod:`defect_sorter.kinematics`) reproduces every measured marker pose.

The zero of the joint that turns the marker's own link is never observable: a constant error in it looks exactly
like the marker stuck on at another angle, and the fitted mounting absorbs it. So a marker on the gripper sees
``shoulder_lift``, ``elbow_flex`` and ``wrist_flex``, while a marker on the forearm (``lower_arm_link``, turned by
``elbow_flex``) sees only ``shoulder_lift`` besides the base pose; the elbow and wrist zeros then need another
measurement, such as the jaw tip held on known table points.

Two zeros cannot be observed this way and are deliberately not fitted: a ``shoulder_pan`` offset is
indistinguishable from the base being turned on the table, and a ``wrist_roll`` offset from the marker being taped
on at another angle. They are absorbed into the base yaw and the marker mounting. Fixing them needs a reference
with known geometry (a marker squared to the base edge, or to a modelled face of the gripper).

The result is a measurement; nothing here writes to the arms.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

from defect_sorter.kinematics import forward, joint_frames

SOLVED_JOINTS: tuple[str, ...] = ("shoulder_lift", "elbow_flex", "wrist_flex")


@dataclass(frozen=True)
class MarkerLink:
	"""Where a calibration marker can sit: the link's pose from the joint angles and the zeros it can observe."""

	pose: Callable[[Mapping[str, float]], np.ndarray]
	solved_joints: tuple[str, ...]


def _shoulder_pose(angles_deg: Mapping[str, float]) -> np.ndarray:
	# the shoulder_lift joint frame is fixed on shoulder_link, the part of the base that turns with shoulder_pan
	return joint_frames(angles_deg)[1]


def _forearm_pose(angles_deg: Mapping[str, float]) -> np.ndarray:
	# the wrist_flex joint frame is fixed on lower_arm_link until wrist_flex itself turns
	return joint_frames(angles_deg)[3]


MARKER_LINKS: dict[str, MarkerLink] = {
	"shoulder": MarkerLink(_shoulder_pose, ()),
	"gripper": MarkerLink(forward, SOLVED_JOINTS),
	"forearm": MarkerLink(_forearm_pose, ("shoulder_lift",)),
}
"""Marker placements :func:`solve` understands."""

_POSE_JOINTS = {
	"shoulder": ("shoulder_pan",),
	"gripper": SOLVED_JOINTS,
	"forearm": ("shoulder_pan", "shoulder_lift", "elbow_flex"),
}
"""Joints whose variety makes poses count as different for each placement."""
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
	"""Joint readings (degrees) and one marker's measured pose in the table frame (metres).

	``link`` names where that marker sits (a key of :data:`MARKER_LINKS`).
	"""

	angles_deg: dict[str, float]
	marker_rotation: np.ndarray
	marker_position_m: np.ndarray
	link: str = "gripper"


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


def _unpack(x: np.ndarray, link: MarkerLink):
	n = len(link.solved_joints)
	offsets = dict(zip(link.solved_joints, x[:n], strict=True))
	return (
		offsets,
		Rotation.from_rotvec(x[n : n + 3]).as_matrix(),
		x[n + 3 : n + 6],
		Rotation.from_rotvec(x[n + 6 : n + 9]).as_matrix(),
		x[n + 9 : n + 12],
	)


def _predict(x: np.ndarray, angles: dict[str, float], link: MarkerLink) -> tuple[np.ndarray, np.ndarray]:
	offsets, base_r, base_t, mount_r, mount_t = _unpack(x, link)
	tip = link.pose({k: v + offsets.get(k, 0.0) for k, v in angles.items()})
	return base_r @ tip[:3, :3] @ mount_r, base_r @ (tip[:3, :3] @ mount_t + tip[:3, 3]) + base_t


def _errors(x: np.ndarray, observations: list[Observation], link: MarkerLink) -> tuple[np.ndarray, np.ndarray]:
	pos, rot = [], []
	for o in observations:
		r, t = _predict(x, o.angles_deg, link)
		pos.append((t - o.marker_position_m) * 1000.0)
		rot.append(np.degrees(Rotation.from_matrix(o.marker_rotation.T @ r).as_rotvec()))
	return np.array(pos), np.array(rot)


def _residuals(x: np.ndarray, observations: list[Observation], rot_weight: float, link: MarkerLink) -> np.ndarray:
	pos, rot = _errors(x, observations, link)
	return np.concatenate([pos.ravel(), rot.ravel() * rot_weight])


def _distinct_poses(observations: list[Observation], joints: tuple[str, ...], tol_deg: float = 2.0) -> int:
	keys = {tuple(round(o.angles_deg.get(j, 0.0) / tol_deg) for j in joints) for o in observations}
	return len(keys)


def _initial_guess(observations: list[Observation], yaw_deg: float, link: MarkerLink) -> np.ndarray:
	base_r = Rotation.from_euler("z", yaw_deg, degrees=True).as_matrix()
	centre = np.mean([o.marker_position_m for o in observations], axis=0)
	base_t = np.array([centre[0], centre[1], 0.0])
	# chordal mean of the mounting rotation implied by each observation for this base guess
	acc = np.zeros((3, 3))
	for o in observations:
		acc += (base_r @ link.pose(o.angles_deg)[:3, :3]).T @ o.marker_rotation
	u, _, vt = np.linalg.svd(acc)
	mount_r = u @ np.diag([1, 1, np.sign(np.linalg.det(u @ vt))]) @ vt
	return np.concatenate(
		[
			np.zeros(len(link.solved_joints)),
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
	link: str = "gripper",
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
	link : str
		Where the marker sits, a key of :data:`MARKER_LINKS`; it decides which offsets are fitted.

	Raises
	------
	ValueError
		With an unknown ``link``, too few observations or too few different poses to constrain the fit.
	"""
	if link not in MARKER_LINKS:
		raise ValueError(f"unknown marker link {link!r}; use one of {sorted(MARKER_LINKS)}")
	spec = MARKER_LINKS[link]
	if len(observations) < MIN_OBSERVATIONS:
		raise ValueError(f"need at least {MIN_OBSERVATIONS} observations, got {len(observations)}")
	if _distinct_poses(observations, _POSE_JOINTS[link]) < MIN_OBSERVATIONS:
		raise ValueError(f"need at least {MIN_OBSERVATIONS} different poses of {', '.join(_POSE_JOINTS[link])}")

	best = None
	yaws = np.linspace(0.0, 360.0, yaw_starts, endpoint=False)
	for yaw in yaws:
		fit = least_squares(
			_residuals,
			_initial_guess(observations, float(yaw), spec),
			args=(observations, rot_weight_mm_per_deg, spec),
			loss="soft_l1",
			f_scale=5.0,
			x_scale="jac",
			max_nfev=400,
		)
		if best is None or fit.cost < best.cost:
			best = fit
		pos, _ = _errors(best.x, observations, spec)
		if float(np.sqrt(np.mean(np.sum(pos**2, axis=1)))) <= good_enough_mm:
			break

	offsets, base_r, base_t, mount_r, mount_t = _unpack(best.x, spec)
	pos, rot = _errors(best.x, observations, spec)
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


@dataclass(frozen=True)
class BaseFit:
	"""Robot base pose in the table frame from markers on the arm, with the joint zeros taken as given."""

	base_rotation: np.ndarray
	base_position_m: np.ndarray
	mounts: dict[str, tuple[np.ndarray, np.ndarray]]
	rms_position_mm: float
	rms_rotation_deg: float
	rms_by_link_mm: dict[str, float]
	n_observations: int


def solve_base(
	observations: list[Observation],
	*,
	offsets_deg: Mapping[str, float] | None = None,
	rot_weight_mm_per_deg: float = 2.0,
	yaw_starts: int = 12,
	min_poses: int = 3,
) -> BaseFit:
	"""Fit the robot base pose and each marker's mounting, trusting the joint zeros (Studio's calibration).

	Markers may sit on several links (``Observation.link``); all of them share one base pose. A marker on the
	turning base (``shoulder``) pins the base position as it circles the pan axis, but cannot give the heading on
	its own: how it was stuck on and where the base points are interchangeable. At least one marker further out on
	the arm (``forearm`` or ``gripper``) is needed for that.

	Parameters
	----------
	observations : list of Observation
		Marker poses with the joint readings at the same moment.
	offsets_deg : mapping, optional
		Joint zero corrections to apply to the readings; none (Studio's zeros) by default.
	rot_weight_mm_per_deg : float
		How many millimetres of position error one degree of marker rotation error is worth.
	yaw_starts : int
		Base yaw starting guesses spread over the full turn; the best fit wins.
	min_poses : int
		Fewest different arm poses accepted from the markers further out on the arm.

	Raises
	------
	ValueError
		For an unknown link, with no marker further out on the arm, or with too few different poses.
	"""
	unknown = {o.link for o in observations} - set(MARKER_LINKS)
	if unknown:
		raise ValueError(f"unknown marker link(s) {sorted(unknown)}; use {sorted(MARKER_LINKS)}")
	arm = [o for o in observations if o.link != "shoulder"]
	if not arm:
		raise ValueError("a marker on the turning base cannot give the heading: add a marker further out on the arm")
	arm_poses = _distinct_poses(arm, ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"))
	if arm_poses < min_poses:
		raise ValueError(f"need at least {min_poses} different arm poses with a marker on the arm, got {arm_poses}")
	offsets = dict(offsets_deg or {})
	links = sorted({o.link for o in observations})
	corrected = [
		Observation(
			{k: v + offsets.get(k, 0.0) for k, v in o.angles_deg.items()},
			o.marker_rotation,
			o.marker_position_m,
			o.link,
		)
		for o in observations
	]

	def unpack(x: np.ndarray):
		base_r, base_t = Rotation.from_rotvec(x[:3]).as_matrix(), x[3:6]
		mounts = {
			link: (Rotation.from_rotvec(x[6 + 6 * k : 9 + 6 * k]).as_matrix(), x[9 + 6 * k : 12 + 6 * k])
			for k, link in enumerate(links)
		}
		return base_r, base_t, mounts

	def errors(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
		base_r, base_t, mounts = unpack(x)
		pos, rot = [], []
		for o in corrected:
			mount_r, mount_t = mounts[o.link]
			pose = MARKER_LINKS[o.link].pose(o.angles_deg)
			r = base_r @ pose[:3, :3] @ mount_r
			t = base_r @ (pose[:3, :3] @ mount_t + pose[:3, 3]) + base_t
			pos.append((t - o.marker_position_m) * 1000.0)
			rot.append(np.degrees(Rotation.from_matrix(o.marker_rotation.T @ r).as_rotvec()))
		return np.array(pos), np.array(rot)

	def residuals(x: np.ndarray) -> np.ndarray:
		pos, rot = errors(x)
		return np.concatenate([pos.ravel(), rot.ravel() * rot_weight_mm_per_deg])

	def guess(yaw_deg: float) -> np.ndarray:
		base_r = Rotation.from_euler("z", yaw_deg, degrees=True).as_matrix()
		centre = np.mean([o.marker_position_m for o in corrected], axis=0)
		parts = [Rotation.from_matrix(base_r).as_rotvec(), np.array([centre[0], centre[1], 0.0])]
		for link in links:
			acc = np.zeros((3, 3))
			for o in corrected:
				if o.link == link:
					acc += (base_r @ MARKER_LINKS[link].pose(o.angles_deg)[:3, :3]).T @ o.marker_rotation
			u, _, vt = np.linalg.svd(acc)
			mount_r = u @ np.diag([1, 1, np.sign(np.linalg.det(u @ vt))]) @ vt
			parts += [Rotation.from_matrix(mount_r).as_rotvec(), np.zeros(3)]
		return np.concatenate(parts)

	best = None
	for yaw in np.linspace(0.0, 360.0, yaw_starts, endpoint=False):
		fit = least_squares(residuals, guess(float(yaw)), loss="soft_l1", f_scale=5.0, x_scale="jac", max_nfev=600)
		if best is None or fit.cost < best.cost:
			best = fit
	base_r, base_t, mounts = unpack(best.x)
	pos, rot = errors(best.x)
	pos_norm = np.linalg.norm(pos, axis=1)
	by_link = {
		link: float(np.sqrt(np.mean([p**2 for p, o in zip(pos_norm, corrected, strict=True) if o.link == link])))
		for link in links
	}
	return BaseFit(
		base_rotation=base_r,
		base_position_m=np.asarray(base_t, dtype=np.float64),
		mounts=mounts,
		rms_position_mm=float(np.sqrt(np.mean(pos_norm**2))),
		rms_rotation_deg=float(np.sqrt(np.mean(np.linalg.norm(rot, axis=1) ** 2))),
		rms_by_link_mm=by_link,
		n_observations=len(observations),
	)
