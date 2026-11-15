"""Brick targets for scripted hovers: the brick's pose on the table from the top camera, and the wrist roll to grasp it.

:func:`brick_pose` turns one object found by :func:`defect_sorter.scene.detect_scene` into a pose in the table
frame (:mod:`defect_sorter.alignment`). Only the top face is used: the tilted top camera also sees the side face
nearest to it, and a centre over all of the object's pixels would be pulled several millimetres towards the
camera. Top-face pixels are deprojected and moved into the table frame, where a rotated rectangle fitted to them
gives the centre, the long-axis direction and the size; the camera's tilt and perspective do not enter.
Side-face pixels just below the top edge sit exactly above that edge in the table plane, so they do not move
the rectangle.

:func:`choose_approach` picks how the gripper comes in: straight down where the arm reaches that way, else
tilted out along the line from the robot base by the smallest angle that reaches (the wrist flex stops at 95°, so
straight down only covers a narrow band of the table). The grasp point is half way up the brick, and the hover
(standoff) point lies back along the approach from it.

:func:`grasp_roll` picks the wrist roll that makes the jaws close across the brick's long axis, for any approach:
the jaws end up perpendicular to both the approach and the long axis. The jaw direction comes from the kinematic model (:data:`JAW_AXIS_TOOL` in the tool frame), so the
answer holds wherever the robot base stands. A long brick looks the same after a half turn and a square one after a
quarter turn (:func:`grasp_symmetry_deg`), so of the rolls that many degrees apart the one inside the joint range and
nearest to the current roll wins.

:func:`bowl_pose` finds a bowl's rim from depth: colour gives the rough region (:mod:`defect_sorter.scene`), and a
circle fitted to the raised rim pixels in the table frame gives its centre, radius and height, unmoved by bricks
lying in the bowl. :func:`drop_points` lists where to hold a brick before letting go: over the centre first, then
step by step toward the robot while staying ``margin`` inside the rim, so a far bowl is still served from its near
half.

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
from defect_sorter.scene import Bowl, DetectedObject, Scene

logger = logging.getLogger(__name__)

JAW_AXIS_TOOL = np.array([1.0, 0.0, 0.0])
"""Direction in which the jaws close, in the tool frame (``gripper_frame_link``, z out of the jaws).

Taken from the URDF: the tool point sits between the jaws, offset from the roll axis along the gripper's x axis,
which is the tool frame's x axis turned by half a turn about y. Not yet confirmed on the real gripper; check it
in the wrist image on the first brick hover (the jaws should straddle the brick's short side).
"""

DOWN = (0.0, 0.0, -1.0)

JAW_FIT_M = 0.036
"""Longest side the open jaws close across with room to spare (they open to about 50 mm at the hover)."""
SQUARE_MAX_RATIO = 1.4
"""Top faces with length/width below this are square (a 2x2 Duplo), which the jaws can take across either pair.

The fit of a real 2x2 Duplo came out 31 x 26 mm (ratio 1.2) because the studs sit inside the edges; a 2x4 brick is
2.0, so 1.4 keeps the two apart.
"""


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


def _fold(angle_deg: float, period_deg: float) -> float:
	"""An angle folded into (-period/2, period/2]."""
	half = period_deg / 2.0
	a = (angle_deg + half) % period_deg - half
	return half if a == -half else a


@dataclass(frozen=True)
class ApproachChoice:
	"""How to come in for a brick: tilt from vertical, approach direction and the two tool points (table frame)."""

	tilt_deg: float
	approach: np.ndarray
	grasp_m: np.ndarray
	standoff_m: np.ndarray
	roll: GraspRoll


@dataclass(frozen=True)
class BowlPose:
	"""A bowl in the table frame: rim centre (z = rim height), rim radius, colour and the rim pixels behind it."""

	colour: str
	centre_m: np.ndarray
	radius_m: float
	rim_height_m: float
	points: int


def _axial(angle_deg: float) -> float:
	"""An undirected angle folded into (-90, 90]."""
	return _fold(angle_deg, 180.0)


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
	exclude_xy_m: np.ndarray | None = None,
	exclude_radius_m: float = 0.12,
) -> tuple[BrickPose | None, str]:
	"""The brick to hover over, or ``None`` and the reason.

	Objects taller than ``max_height_m`` or longer than ``max_length_m`` are not bricks (the arm, a hand, a bowl
	stack), and neither is anything within ``exclude_radius_m`` of ``exclude_xy_m`` (the robot base and its clamp).
	With several bricks a table-frame point ``near_m`` (x, y) must say which one; the nearest is taken.
	"""
	bricks = [p for p in poses if p.centre_m[2] <= max_height_m and p.length_m <= max_length_m]
	if exclude_xy_m is not None:
		keep_out = np.asarray(exclude_xy_m, dtype=np.float64)[:2]
		bricks = [p for p in bricks if np.hypot(*(p.centre_m[:2] - keep_out)) > exclude_radius_m]
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


def grasp_symmetry_deg(brick: BrickPose, *, square_max_ratio: float = SQUARE_MAX_RATIO) -> float:
	"""Turn of the jaws that grasps ``brick`` just as well: 90° for a square top face, else 180°."""
	return 90.0 if brick.length_m < square_max_ratio * brick.width_m else 180.0


def grasp_point(brick: BrickPose) -> np.ndarray:
	"""Where the tool point closes on ``brick``: under its top-face centre, half way up."""
	c = np.asarray(brick.centre_m, dtype=np.float64)
	return np.array([c[0], c[1], c[2] / 2.0])


def approach_vector(target_table_m: np.ndarray, tilt_deg: float, calibration: RobotCalibration) -> np.ndarray:
	"""Unit approach direction (table frame): straight down turned ``tilt_deg`` out along the line from the base."""
	target = np.asarray(target_table_m, dtype=np.float64)
	radial = (target - calibration.base_position_m) * np.array([1.0, 1.0, 0.0])
	radial /= np.linalg.norm(radial)
	t = np.radians(tilt_deg)
	return np.cos(t) * np.asarray(DOWN) + np.sin(t) * radial


def choose_approach(
	brick: BrickPose,
	*,
	calibration: RobotCalibration,
	standoff_m: float = 0.06,
	tilts_deg: tuple[float, ...] = (0.0, 15.0, 30.0, 45.0, 60.0, 75.0),
	reach_m: float = 0.40,
	current_roll_deg: float = 0.0,
	approach_tolerance_deg: float = 5.0,
	symmetry_deg: float | None = None,
) -> tuple[ApproachChoice | None, str]:
	"""The steepest approach of ``tilts_deg`` that reaches both the grasp and the standoff point, or the reason.

	Both points must lie within ``reach_m`` (horizontally) of the robot base, the scripted moves' reach limit.
	``symmetry_deg`` overrides :func:`grasp_symmetry_deg` (90 also allows closing across the long side).
	"""
	cal = calibration
	grasp = grasp_point(brick)
	symmetry = grasp_symmetry_deg(brick) if symmetry_deg is None else symmetry_deg
	beyond = 0
	for tilt in tilts_deg:
		a = approach_vector(grasp, tilt, cal)
		standoff = grasp - standoff_m * a
		if max(np.linalg.norm(cal.to_base(p)[:2]) for p in (grasp, standoff)) > reach_m:
			beyond += 1
			continue
		roll = grasp_roll(
			standoff,
			brick.yaw_deg,
			calibration=cal,
			current_roll_deg=current_roll_deg,
			approach=a,
			approach_tolerance_deg=approach_tolerance_deg,
			symmetry_deg=symmetry,
		)
		if roll is None:
			continue
		model_roll = roll.roll_deg + cal.offsets_deg.get("wrist_roll", 0.0)
		if _solve_model(grasp, model_roll, cal, approach_tolerance_deg, a) is None:
			continue
		return ApproachChoice(float(tilt), a, grasp, standoff, roll), ""
	if beyond == len(tilts_deg):
		distance = float(np.linalg.norm(cal.to_base(grasp)[:2]))
		move_cm = max(1, int(np.ceil((distance - reach_m) * 100 - 1e-6)))
		return None, (
			f"brick is {distance * 100:.0f} cm from the robot base, beyond the {reach_m * 100:.0f} cm reach limit: "
			f"move it {move_cm} cm toward the robot"
		)
	return None, f"no approach tilted {min(tilts_deg):.0f}-{max(tilts_deg):.0f} deg reaches the brick"


def hover_target(brick: BrickPose, *, height_m: float = 0.06) -> np.ndarray:
	"""Table-frame tool point ``height_m`` above the brick's top face."""
	return np.asarray(brick.centre_m, dtype=np.float64) + np.array([0.0, 0.0, height_m])


def _solve_model(
	target_table_m: np.ndarray,
	model_roll_deg: float,
	cal: RobotCalibration,
	approach_tolerance_deg: float,
	approach_table: np.ndarray | tuple[float, float, float] = DOWN,
) -> dict[str, float] | None:
	sol = inverse(
		cal.to_base(target_table_m),
		approach=cal.direction_to_base(approach_table),
		roll_deg=model_roll_deg,
		tolerance_deg=approach_tolerance_deg,
	)
	return sol.angles_deg if sol.reachable else None


def _in_plane_deg(v: np.ndarray, approach: np.ndarray) -> float:
	"""Direction of ``v`` within the plane across ``approach``; for a downward approach, degrees from table x."""
	e1 = np.array([1.0, 0.0, 0.0]) - approach[0] * approach
	if np.linalg.norm(e1) < 1e-6:
		e1 = np.array([0.0, 1.0, 0.0]) - approach[1] * approach
	e1 /= np.linalg.norm(e1)
	e2 = np.cross(e1, approach)
	return float(np.degrees(np.arctan2(v @ e2, v @ e1)))


def _jaw_axis_table(model_angles_deg: dict[str, float], calibration: RobotCalibration) -> np.ndarray:
	return calibration.base_rotation @ tool_pose(model_angles_deg)[:3, :3] @ JAW_AXIS_TOOL


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
	approach: np.ndarray | tuple[float, float, float] = DOWN,
	approach_tolerance_deg: float = 5.0,
	tolerance_deg: float = 1.0,
	symmetry_deg: float = 180.0,
) -> GraspRoll | None:
	"""Wrist roll reading that closes the jaws across the brick's long axis at ``target_table_m``.

	Parameters
	----------
	target_table_m : numpy.ndarray
		Tool point in the table frame (a hover, standoff or grasp point).
	brick_yaw_deg : float
		Long-axis direction of the brick (:attr:`BrickPose.yaw_deg`); a half turn gives the same answer.
	calibration : RobotCalibration
		Joint offsets and base pose.
	current_roll_deg : float
		Present wrist roll reading; of the valid solutions the nearest is chosen, so the wrist turns least.
	approach : array-like
		Direction the jaws point in (table frame, unit), straight down by default (:func:`approach_vector`).
	approach_tolerance_deg : float
		How far from ``approach`` the jaws may end up (as in :func:`defect_sorter.motion.plan_move`).
	tolerance_deg : float
		Largest remaining jaw-direction error accepted.
	symmetry_deg : float
		Turn of the brick that looks the same (:func:`grasp_symmetry_deg`): 180 for a long brick, 90 for a square
		one, whose two pairs of sides are then both tried.

	Returns
	-------
	GraspRoll or None
		``None`` when the target is out of reach or no roll inside the joint range lines the jaws up.
	"""
	a = np.asarray(approach, dtype=np.float64)
	a = a / np.linalg.norm(a)
	yaws = [brick_yaw_deg] if symmetry_deg >= 180.0 else [brick_yaw_deg, brick_yaw_deg + 90.0]
	found = [
		g
		for yaw in yaws
		if (
			g := _grasp_roll_across(
				target_table_m, yaw, a, calibration, current_roll_deg, approach_tolerance_deg, tolerance_deg
			)
		)
		is not None
	]
	return min(found, key=lambda g: abs(g.roll_deg - current_roll_deg)) if found else None


def _grasp_roll_across(
	target_table_m: np.ndarray,
	long_axis_yaw_deg: float,
	a: np.ndarray,
	cal: RobotCalibration,
	current_roll_deg: float,
	approach_tolerance_deg: float,
	tolerance_deg: float,
) -> GraspRoll | None:
	"""Roll reading closing the jaws perpendicular to the approach ``a`` and the long axis, nearest to the current."""
	target = np.asarray(target_table_m, dtype=np.float64)
	y = np.radians(long_axis_yaw_deg)
	wanted = _in_plane_deg(np.cross(a, [np.cos(y), np.sin(y), 0.0]), a)

	def jaw(model: dict[str, float]) -> float:
		return _in_plane_deg(_jaw_axis_table(model, cal), a)

	offset = cal.offsets_deg.get("wrist_roll", 0.0)
	at_0 = _solve_model(target, offset, cal, approach_tolerance_deg, a)
	at_30 = _solve_model(target, 30.0 + offset, cal, approach_tolerance_deg, a)
	if at_0 is None or at_30 is None:
		return None
	sign = 1.0 if _signed(jaw(at_30) - jaw(at_0)) > 0 else -1.0
	first = sign * _axial(wanted - jaw(at_0))
	lo, hi = (limit - offset for limit in JOINT_LIMITS_DEG["wrist_roll"])
	candidates = sorted(
		(first + 180.0 * k for k in range(-2, 3) if lo <= first + 180.0 * k <= hi),
		key=lambda roll: abs(roll - current_roll_deg),
	)
	for roll in candidates:
		for _ in range(3):
			model = _solve_model(target, roll + offset, cal, approach_tolerance_deg, a)
			if model is None:
				break
			error = _axial(wanted - jaw(model))
			if abs(error) < tolerance_deg:
				readings = readings_from_model(model, cal)
				return GraspRoll(roll_deg=float(readings["wrist_roll"]), readings=readings)
			roll += sign * error
			if not lo <= roll <= hi:
				break
	return None


def _circle(points_xy: np.ndarray) -> tuple[np.ndarray, float]:
	a = np.c_[2.0 * points_xy, np.ones(len(points_xy))]
	cx, cy, c = np.linalg.lstsq(a, (points_xy**2).sum(axis=1), rcond=None)[0]
	return np.array([cx, cy]), float(np.sqrt(max(c + cx**2 + cy**2, 0.0)))


def fit_rim_circle(points_xy: np.ndarray, *, band_m: float = 0.008, iterations: int = 5) -> tuple[np.ndarray, float]:
	"""Centre and radius of the ring that most of ``points_xy`` lie on; points off the ring (bricks) are dropped.

	The first fit over all points is pulled inward by anything inside the ring, so the first pass keeps a wide band
	(a quarter of the radius) and later passes only ``band_m``.
	"""
	pts = np.asarray(points_xy, dtype=np.float64)
	centre, radius = _circle(pts)
	for k in range(iterations):
		band = max(0.25 * radius, band_m) if k == 0 else band_m
		keep = np.abs(np.hypot(*(pts - centre).T) - radius) < band
		if keep.sum() < 10:
			break
		centre, radius = _circle(pts[keep])
	return centre, radius


def bowl_pose(
	bowl: Bowl,
	scene: Scene,
	depth_m: np.ndarray,
	intrinsics: Intrinsics,
	frame: TableFrame,
	*,
	grow_px: int = 15,
	rim_min_m: float = 0.006,
	rim_max_m: float = 0.05,
	band_m: float = 0.008,
	min_points: int = 50,
) -> BowlPose | None:
	"""Rim of one bowl from :func:`~defect_sorter.scene.detect_scene` in the table frame; ``None`` without a rim.

	Pixels of the colour region (grown by ``grow_px``) that stand ``rim_min_m``..``rim_max_m`` above the table are
	moved into the table frame and a circle is fitted to them; the rim height is their median height.
	"""
	region = np.zeros(depth_m.shape, np.uint8)
	(u, v), (a, b), angle = bowl.ellipse
	cv2.ellipse(region, ((u, v), (a + 2 * grow_px, b + 2 * grow_px), angle), 255, -1)
	mask = (region > 0) & scene.valid & (scene.height_m >= rim_min_m) & (scene.height_m <= rim_max_m)
	vs, us = np.nonzero(mask)
	if len(vs) < min_points:
		return None
	z = depth_m[vs, us].astype(np.float64)
	cam = np.stack([(us - intrinsics.ppx) * z / intrinsics.fx, (vs - intrinsics.ppy) * z / intrinsics.fy, z], axis=1)
	table = (cam - frame.origin) @ frame.axes.T
	centre, radius = fit_rim_circle(table[:, :2], band_m=band_m)
	rim = np.abs(np.hypot(*(table[:, :2] - centre).T) - radius) < band_m
	if rim.sum() < min_points:
		return None
	rim_h = float(np.median(table[rim, 2]))
	return BowlPose(bowl.colour, np.array([centre[0], centre[1], rim_h]), radius, rim_h, int(rim.sum()))


def drop_points(
	bowl: BowlPose,
	base_xy_m: np.ndarray,
	*,
	clearance_m: float = 0.08,
	margin_m: float = 0.03,
	step_m: float = 0.01,
) -> list[np.ndarray]:
	"""Where to hold a brick over ``bowl`` before letting go: the centre, then steps toward the robot base.

	All lie ``clearance_m`` above the rim and at least ``margin_m`` inside it.
	"""
	centre = np.asarray(bowl.centre_m[:2], dtype=np.float64)
	toward = np.asarray(base_xy_m, dtype=np.float64)[:2] - centre
	toward /= np.linalg.norm(toward)
	z = bowl.rim_height_m + clearance_m
	limit = max(bowl.radius_m - margin_m, 0.0)
	return [np.array([*(centre + d * toward), z]) for d in np.arange(0.0, limit + 1e-9, step_m)]
