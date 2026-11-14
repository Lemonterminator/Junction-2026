"""Forward kinematics of the SO-101 follower arm.

Joint origins and axes are taken from the SO-101 URDF ``so101_new_calib`` (SO-ARM100 project, generated from the
Onshape CAD with onshape-to-robot) as bundled with Physical AI Studio's ``physicalai_so101_plugin``. In that model
every body joint's zero is the middle of its range, which matches LeRobot's "new" calibration and Studio's
degree conversion, so joint angles from :func:`defect_sorter.joint_calibration.ticks_to_degrees` can be used
directly. Only the five body joints matter for the arm pose; the gripper jaw is not part of the chain.

URDF convention: a joint's transform is ``Trans(xyz) @ Rot(rpy) @ RotZ(angle)``, with ``Rot(rpy) = Rz(yaw) @
Ry(pitch) @ Rx(roll)``; all SO-101 body joints rotate about their local z axis. Lengths are metres, angles degrees.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


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
