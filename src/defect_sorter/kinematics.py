"""Forward and inverse kinematics of the SO-101 follower arm, as functions of joint angles in degrees.

The model itself (joint origins and axes from the SO-101 URDF ``so101_new_calib``, joint limits, the tool point between
the jaws) lives in the ``armkit`` library (:mod:`armkit.profiles.so101`); this module binds it to plain functions.
Joint zero is the middle of each range, which matches LeRobot's "new" calibration and Studio's degree conversion, so
angles from :func:`defect_sorter.joint_calibration.ticks_to_degrees` can be used directly. Only the five body joints
matter for the arm pose; the gripper jaw is not part of the chain.

:func:`inverse` solves for the four positioning joints given a tool point, the direction the jaws should point and the
wrist roll; with a 5-joint arm the roll is the free choice (for a top-down grasp: the brick's orientation).
Lengths are metres, angles degrees.
"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
from armkit.model import IKSolution, rpy_matrix
from armkit.profiles.so101 import so101_robot

__all__ = [
	"JOINT_LIMITS_DEG",
	"SO101_JOINTS",
	"IKSolution",
	"forward",
	"inverse",
	"joint_frames",
	"rpy_matrix",
	"tool_pose",
]

_ROBOT = so101_robot()
SO101_JOINTS = _ROBOT.joints
JOINT_LIMITS_DEG: dict[str, tuple[float, float]] = {j.name: (j.lower_deg, j.upper_deg) for j in SO101_JOINTS}
"""URDF joint limits converted to degrees (the URDF stores radians)."""

_SEEDS = [
	{"shoulder_pan": pan, "shoulder_lift": lift, "elbow_flex": elbow, "wrist_flex": wrist}
	for pan in (-90.0, -45.0, 0.0, 45.0, 90.0)
	for lift, elbow, wrist in ((0.0, 0.0, 0.0), (-40.0, 60.0, 40.0), (40.0, -60.0, -40.0), (-60.0, 30.0, 70.0))
]


def joint_frames(angles_deg: Mapping[str, float]) -> list[np.ndarray]:
	"""Pose of each joint frame in ``base_link`` before its own rotation; column 2 is the joint axis."""
	return _ROBOT.joint_frames(angles_deg)


def forward(angles_deg: Mapping[str, float]) -> np.ndarray:
	"""4x4 pose of ``gripper_link`` (the gripper body after wrist roll) in ``base_link``; missing joints are 0."""
	return _ROBOT.forward(angles_deg)


def tool_pose(angles_deg: Mapping[str, float]) -> np.ndarray:
	"""4x4 pose of the tool point (``gripper_frame_link``, between the jaw tips) in ``base_link``."""
	return _ROBOT.tool_pose(angles_deg)


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
	return _ROBOT.inverse(
		target_m,
		approach=approach,
		fixed={"wrist_roll": roll_deg},
		tolerance_mm=tolerance_mm,
		tolerance_deg=tolerance_deg,
		seeds=_SEEDS,
	)
