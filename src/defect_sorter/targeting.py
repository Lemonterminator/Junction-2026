"""Brick targets for scripted hovers: the brick's pose on the table from the top camera, and the wrist roll to grasp it.

:func:`brick_pose` turns one object found by :func:`defect_sorter.scene.detect_scene` into a pose in the table
frame (:mod:`defect_sorter.alignment`). Only the top face is used: the tilted top camera also sees the side face
nearest to it, and a centre over all of the object's pixels would be pulled several millimetres towards the
camera. Top-face pixels are deprojected and moved into the table frame, where a rotated rectangle fitted to them
gives the centre, the long-axis direction and the size; the camera's tilt and perspective do not enter.
Side-face pixels just below the top edge sit exactly above that edge in the table plane, so they do not move
the rectangle.

:func:`grasp_roll` picks the wrist roll that makes the jaws close across the brick's short side for a jaws-down
approach. The jaw direction comes from the kinematic model (:data:`JAW_AXIS_TOOL` in the tool frame), so the
answer holds wherever the robot base stands. A brick looks the same after a half turn, so of the rolls about 180°
apart the one inside the joint range and nearest to the current roll wins.

Lengths are metres in the table frame (z = height above the table), angles degrees from the table x axis.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import cv2
import numpy as np

from defect_sorter.alignment import TableFrame
from defect_sorter.geometry import Intrinsics
from defect_sorter.kinematics import JOINT_LIMITS_DEG, inverse, tool_pose
from defect_sorter.robot_pose import RobotCalibration, readings_from_model
from defect_sorter.scene import DetectedObject, Scene

logger = logging.getLogger(__name__)

JAW_AXIS_TOOL = np.array([1.0, 0.0, 0.0])
"""Direction in which the jaws close, in the tool frame (``gripper_frame_link``, z out of the jaws).

Taken from the URDF: the tool point sits between the jaws, offset from the roll axis along the gripper's x axis,
which is the tool frame's x axis turned by half a turn about y. Not yet confirmed on the real gripper; check it
in the wrist image on the first brick hover (the jaws should straddle the brick's short side).
"""

DOWN = (0.0, 0.0, -1.0)


@dataclass(frozen=True)
class BrickPose:
	"""A brick on the table.

	Parameters
	----------
	centre_m : numpy.ndarray
		Centre of the top face in the table frame; z is the top face's height above the table.
	yaw_deg : float
		Direction of the long axis in the table plane, in (-90, 90].
	length_m, width_m : float
		Sides of the rectangle fitted to the top face, long side first.
	points : int
		Number of top-face depth pixels behind the estimate.
	"""

	centre_m: np.ndarray
	yaw_deg: float
	length_m: float
	width_m: float
	points: int


@dataclass(frozen=True)
class GraspRoll:
	"""Wrist roll reading for a jaws-down grasp and the joint readings (body joints) that solve it."""

	roll_deg: float
	readings: dict[str, float]


def _axial(angle_deg: float) -> float:
	"""An undirected angle folded into (-90, 90]."""
	a = (angle_deg + 90.0) % 180.0 - 90.0
	return 90.0 if a == -90.0 else a


def _signed(angle_deg: float) -> float:
	"""An angle folded into [-180, 180)."""
	return (angle_deg + 180.0) % 360.0 - 180.0


def brick_pose(
	obj: DetectedObject,
	scene: Scene,
	depth_m: np.ndarray,
	intrinsics: Intrinsics,
	frame: TableFrame,
	*,
	top_band_m: float = 0.004,
	min_points: int = 30,
) -> BrickPose | None:
	"""Pose of one detected object's top face in the table frame.

	Parameters
	----------
	obj : DetectedObject
		One of ``scene.objects``.
	scene : Scene
		The scene the object came from (its height map and valid mask are reused).
	depth_m : numpy.ndarray
		The depth image passed to :func:`~defect_sorter.scene.detect_scene`, metres.
	intrinsics : Intrinsics
		Intrinsics of that depth image.
	frame : TableFrame
		Table frame built from the same plane and the anchor markers.
	top_band_m : float
		Pixels within this distance below the object's top height (95th percentile) count as top face.
	min_points : int
		Fewer top-face pixels than this give no pose.

	Returns
	-------
	BrickPose or None
		``None`` when the object has too few top-face pixels.
	"""
	region = np.zeros(depth_m.shape, np.uint8)
	cv2.drawContours(region, [obj.contour], -1, 255, -1)
	mask = (region > 0) & scene.valid & (depth_m > 0)
	if not mask.any():
		return None
	top_h = float(np.percentile(scene.height_m[mask], 95))
	vs, us = np.nonzero(mask & (scene.height_m >= top_h - top_band_m))
	if len(vs) < min_points:
		logger.debug("object at %s: only %d top-face pixels", obj.px, len(vs))
		return None
	z = depth_m[vs, us].astype(np.float64)
	cam = np.stack([(us - intrinsics.ppx) * z / intrinsics.fx, (vs - intrinsics.ppy) * z / intrinsics.fy, z], axis=1)
	table = (cam - frame.origin) @ frame.axes.T
	(cx, cy), (w, h), angle = cv2.minAreaRect((table[:, :2] * 1000.0).astype(np.float32))
	yaw = angle if w >= h else angle + 90.0
	return BrickPose(
		centre_m=np.array([cx / 1000.0, cy / 1000.0, float(np.median(table[:, 2]))]),
		yaw_deg=_axial(yaw),
		length_m=max(w, h) / 1000.0,
		width_m=min(w, h) / 1000.0,
		points=len(vs),
	)


def select_brick(
	poses: list[BrickPose],
	*,
	near_m: np.ndarray | None = None,
	max_height_m: float = 0.04,
	max_length_m: float = 0.06,
) -> tuple[BrickPose | None, str]:
	"""The brick to hover over, or ``None`` and the reason.

	Objects taller than ``max_height_m`` or longer than ``max_length_m`` are not bricks (the arm, a hand, a bowl
	stack). With several bricks a table-frame point ``near_m`` (x, y) must say which one; the nearest is taken.
	"""
	bricks = [p for p in poses if p.centre_m[2] <= max_height_m and p.length_m <= max_length_m]
	if not bricks:
		return None, f"no brick on the table ({len(poses)} other objects)"
	if near_m is not None:
		near = np.asarray(near_m, dtype=np.float64)[:2]
		return min(bricks, key=lambda p: float(np.hypot(*(p.centre_m[:2] - near)))), ""
	if len(bricks) > 1:
		where = ", ".join(f"({p.centre_m[0] * 1000:.0f}, {p.centre_m[1] * 1000:.0f})" for p in bricks)
		return None, f"{len(bricks)} bricks on the table at {where} mm: say which one"
	return bricks[0], ""


def combine_poses(poses: list[BrickPose]) -> tuple[BrickPose, float]:
	"""One pose from several frames of the same brick, and the largest standard deviation of its x/y centre (m).

	The centre and size are medians; the yaw is the mean of the undirected angles, so 89° and -89° average to 90°.
	"""
	if not poses:
		raise ValueError("no poses to combine")
	centres = np.array([p.centre_m for p in poses])
	doubled = np.radians([2.0 * p.yaw_deg for p in poses])
	yaw = float(np.degrees(np.arctan2(np.sin(doubled).mean(), np.cos(doubled).mean())) / 2.0)
	combined = BrickPose(
		centre_m=np.median(centres, axis=0),
		yaw_deg=_axial(yaw),
		length_m=float(np.median([p.length_m for p in poses])),
		width_m=float(np.median([p.width_m for p in poses])),
		points=int(np.median([p.points for p in poses])),
	)
	return combined, float(np.max(np.std(centres[:, :2], axis=0)))


def hover_target(brick: BrickPose, *, height_m: float = 0.06) -> np.ndarray:
	"""Table-frame tool point ``height_m`` above the brick's top face."""
	return np.asarray(brick.centre_m, dtype=np.float64) + np.array([0.0, 0.0, height_m])


def _solve_model(
	target_table_m: np.ndarray, model_roll_deg: float, cal: RobotCalibration, approach_tolerance_deg: float
) -> dict[str, float] | None:
	sol = inverse(
		cal.to_base(target_table_m),
		approach=cal.direction_to_base(DOWN),
		roll_deg=model_roll_deg,
		tolerance_deg=approach_tolerance_deg,
	)
	return sol.angles_deg if sol.reachable else None


def jaw_direction_deg(model_angles_deg: dict[str, float], calibration: RobotCalibration) -> float:
	"""Direction in which the jaws close, projected on the table, in degrees from the table x axis."""
	axis = calibration.base_rotation @ tool_pose(model_angles_deg)[:3, :3] @ JAW_AXIS_TOOL
	return float(np.degrees(np.arctan2(axis[1], axis[0])))


def grasp_roll(
	target_table_m: np.ndarray,
	brick_yaw_deg: float,
	*,
	calibration: RobotCalibration,
	current_roll_deg: float,
	approach_tolerance_deg: float = 5.0,
	tolerance_deg: float = 1.0,
) -> GraspRoll | None:
	"""Wrist roll reading that closes the jaws across the brick's short side at ``target_table_m``, jaws down.

	Parameters
	----------
	target_table_m : numpy.ndarray
		Tool point in the table frame (usually :func:`hover_target`).
	brick_yaw_deg : float
		Long-axis direction of the brick (:attr:`BrickPose.yaw_deg`); a half turn gives the same answer.
	calibration : RobotCalibration
		Joint offsets and base pose.
	current_roll_deg : float
		Present wrist roll reading; of the valid solutions the nearest is chosen, so the wrist turns least.
	approach_tolerance_deg : float
		How far from vertical the jaws may end up (as in :func:`defect_sorter.motion.plan_move`).
	tolerance_deg : float
		Largest remaining jaw-direction error accepted.

	Returns
	-------
	GraspRoll or None
		``None`` when the target is out of reach or no roll inside the joint range lines the jaws up.
	"""
	cal = calibration
	target = np.asarray(target_table_m, dtype=np.float64)
	offset = cal.offsets_deg.get("wrist_roll", 0.0)
	at_0 = _solve_model(target, offset, cal, approach_tolerance_deg)
	at_30 = _solve_model(target, 30.0 + offset, cal, approach_tolerance_deg)
	if at_0 is None or at_30 is None:
		return None
	sign = 1.0 if _signed(jaw_direction_deg(at_30, cal) - jaw_direction_deg(at_0, cal)) > 0 else -1.0
	wanted = brick_yaw_deg + 90.0
	first = sign * _axial(wanted - jaw_direction_deg(at_0, cal))
	lo, hi = (limit - offset for limit in JOINT_LIMITS_DEG["wrist_roll"])
	candidates = sorted(
		(first + 180.0 * k for k in range(-2, 3) if lo <= first + 180.0 * k <= hi),
		key=lambda roll: abs(roll - current_roll_deg),
	)
	for roll in candidates:
		for _ in range(3):
			model = _solve_model(target, roll + offset, cal, approach_tolerance_deg)
			if model is None:
				break
			error = _axial(wanted - jaw_direction_deg(model, cal))
			if abs(error) < tolerance_deg:
				readings = readings_from_model(model, cal)
				return GraspRoll(roll_deg=float(readings["wrist_roll"]), readings=readings)
			roll += sign * error
			if not lo <= roll <= hi:
				break
	return None
