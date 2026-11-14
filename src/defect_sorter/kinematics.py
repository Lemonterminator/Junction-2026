"""Forward kinematics of the SO-101 follower arm.

Joint origins and axes are taken from the SO-101 URDF ``so101_new_calib`` (SO-ARM100 project, generated from the
Onshape CAD with onshape-to-robot) as bundled with Physical AI Studio's ``physicalai_so101_plugin``. In that model
every body joint's zero is the middle of its range, which matches LeRobot's "new" calibration and Studio's
degree conversion, so joint angles from :func:`defect_sorter.joint_calibration.ticks_to_degrees` can be used
directly. Only the five body joints matter for the arm pose; the gripper jaw is not part of the chain.

The tool point is the URDF ``gripper_frame_link``: between the jaw tips, with its z axis pointing out of the jaws.
:func:`inverse` solves for the four positioning joints given a tool point, the direction the jaws should point and
the wrist roll; with a 5-joint arm the roll is the free choice (for a top-down grasp: the brick's orientation).

URDF convention: a joint's transform is ``Trans(xyz) @ Rot(rpy) @ RotZ(angle)``, with ``Rot(rpy) = Rz(yaw) @
Ry(pitch) @ Rx(roll)``; all SO-101 body joints rotate about their local z axis. Lengths are metres, angles degrees.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares


@dataclass(frozen=True)
class JointSpec:
	"""A revolute joint about its local z axis, placed by ``xyz`` and ``rpy`` in its parent link."""

	name: str
	xyz: tuple[float, float, float]
	rpy: tuple[float, float, float]


SO101_JOINTS: tuple[JointSpec, ...] = (
	JointSpec("shoulder_pan", (0.0388353, -8.97657e-09, 0.0624), (3.14159, 4.18253e-17, -3.14159)),
	JointSpec("shoulder_lift", (-0.0303992, -0.0182778, -0.0542), (-1.5708, -1.5708, 0.0)),
	JointSpec("elbow_flex", (-0.11257, -0.028, 1.73763e-16), (-3.63608e-16, 8.74301e-16, 1.5708)),
	JointSpec("wrist_flex", (-0.1349, 0.0052, 3.62355e-17), (4.02456e-15, 8.67362e-16, -1.5708)),
	JointSpec("wrist_roll", (5.55112e-17, -0.0611, 0.0181), (1.5708, 0.0486795, 3.14159)),
)


JOINT_LIMITS_DEG: dict[str, tuple[float, float]] = {
	"shoulder_pan": (-110.0, 110.0),
	"shoulder_lift": (-100.0, 100.0),
	"elbow_flex": (-96.83, 96.83),
	"wrist_flex": (-95.0, 95.0),
	"wrist_roll": (-157.21, 162.79),
}
"""URDF joint limits converted to degrees (the URDF stores radians)."""

TOOL_XYZ = (-0.0079, -0.000218121, -0.0981274)
TOOL_RPY = (0.0, 3.14159, 0.0)

_POSITIONING = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex")


def rpy_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
	"""URDF fixed-axis roll-pitch-yaw rotation, radians: ``Rz(yaw) @ Ry(pitch) @ Rx(roll)``."""
	cr, sr, cp, sp, cy, sy = np.cos(roll), np.sin(roll), np.cos(pitch), np.sin(pitch), np.cos(yaw), np.sin(yaw)
	rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
	ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
	rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
	return rz @ ry @ rx


def _origin(spec: JointSpec) -> np.ndarray:
	t = np.eye(4)
	t[:3, :3] = rpy_matrix(*spec.rpy)
	t[:3, 3] = spec.xyz
	return t


def _rot_z(deg: float) -> np.ndarray:
	a = np.radians(deg)
	t = np.eye(4)
	t[:2, :2] = [[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]]
	return t


_ORIGINS = tuple(_origin(j) for j in SO101_JOINTS)


def joint_frames(angles_deg: dict[str, float]) -> list[np.ndarray]:
	"""Pose of each joint frame in ``base_link`` before its own rotation; column 2 is the joint axis."""
	frames = []
	t = np.eye(4)
	for spec, origin in zip(SO101_JOINTS, _ORIGINS, strict=True):
		t = t @ origin
		frames.append(t.copy())
		t = t @ _rot_z(angles_deg.get(spec.name, 0.0))
	return frames


def forward(angles_deg: dict[str, float]) -> np.ndarray:
	"""4x4 pose of ``gripper_link`` (the gripper body after wrist roll) in ``base_link``; missing joints are 0."""
	t = np.eye(4)
	for spec, origin in zip(SO101_JOINTS, _ORIGINS, strict=True):
		t = t @ origin @ _rot_z(angles_deg.get(spec.name, 0.0))
	return t


_TOOL = np.eye(4)
_TOOL[:3, :3] = rpy_matrix(*TOOL_RPY)
_TOOL[:3, 3] = TOOL_XYZ


def tool_pose(angles_deg: dict[str, float]) -> np.ndarray:
	"""4x4 pose of the tool point (``gripper_frame_link``, between the jaw tips) in ``base_link``."""
	return forward(angles_deg) @ _TOOL


@dataclass(frozen=True)
class IKSolution:
	"""Result of :func:`inverse`: joint angles (degrees) and how closely they reach the target.

	``reachable`` is False when the best solution within the joint limits misses the target by more than the
	tolerances; the angles are then only the closest attempt and must not be commanded.
	"""

	angles_deg: dict[str, float]
	position_error_mm: float
	approach_error_deg: float
	reachable: bool


def inverse(
	target_m: np.ndarray,
	*,
	approach: tuple[float, float, float] | np.ndarray,
	roll_deg: float,
	tolerance_mm: float = 1.0,
	tolerance_deg: float = 1.0,
) -> IKSolution:
	"""Joint angles that put the tool point at ``target_m`` with the jaws pointing along ``approach``.

	Parameters
	----------
	target_m : numpy.ndarray
		Tool point in ``base_link``, metres.
	approach : array-like
		Direction the jaws should point in ``base_link`` (normalised here); ``(0, 0, -1)`` is straight down.
	roll_deg : float
		Wrist roll to hold; it turns the jaws about the approach direction.
	tolerance_mm, tolerance_deg : float
		Largest position and approach error still counted as reachable.

	Returns
	-------
	IKSolution
		The best solution over several starting configurations, always within :data:`JOINT_LIMITS_DEG`.
	"""
	target = np.asarray(target_m, dtype=np.float64)
	direction = np.asarray(approach, dtype=np.float64)
	direction = direction / np.linalg.norm(direction)
	roll_lo, roll_hi = JOINT_LIMITS_DEG["wrist_roll"]
	lo = np.array([JOINT_LIMITS_DEG[j][0] for j in _POSITIONING])
	hi = np.array([JOINT_LIMITS_DEG[j][1] for j in _POSITIONING])

	def angles_of(x: np.ndarray) -> dict[str, float]:
		return {**dict(zip(_POSITIONING, (float(v) for v in x), strict=True)), "wrist_roll": float(roll_deg)}

	def residuals(x: np.ndarray) -> np.ndarray:
		pose = tool_pose(angles_of(x))
		# position in mm, direction error as a small-angle vector in degrees: both weigh about the same
		return np.concatenate([(pose[:3, 3] - target) * 1000.0, np.degrees(pose[:3, 2] - direction)])

	best = None
	for pan in (-90.0, -45.0, 0.0, 45.0, 90.0):
		for lift, elbow, wrist in ((0.0, 0.0, 0.0), (-40.0, 60.0, 40.0), (40.0, -60.0, -40.0), (-60.0, 30.0, 70.0)):
			seed = np.clip([pan, lift, elbow, wrist], lo + 1e-6, hi - 1e-6)
			fit = least_squares(residuals, seed, bounds=(lo, hi), x_scale=10.0, max_nfev=200)
			if best is None or fit.cost < best.cost:
				best = fit
		if best is not None and 2 * best.cost < (0.1 * tolerance_mm) ** 2:
			break

	angles = angles_of(best.x)
	pose = tool_pose(angles)
	pos_err = float(np.linalg.norm(pose[:3, 3] - target) * 1000.0)
	ang_err = float(np.degrees(np.arccos(np.clip(pose[:3, 2] @ direction, -1.0, 1.0))))
	roll_ok = roll_lo <= roll_deg <= roll_hi
	return IKSolution(angles, pos_err, ang_err, pos_err <= tolerance_mm and ang_err <= tolerance_deg and roll_ok)
