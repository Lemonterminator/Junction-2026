"""Slow, checked point-to-point moves of the follower: plan in degrees, check against the table, then execute.

:func:`plan_move` turns a table-frame target for the tool point (between the jaws) into a joint path: inverse
kinematics for the goal with the jaws pointing along a given approach (straight down by default), a straight rise
first when the jaws start below the travel height (turned to the goal's approach, or keeping the present orientation
where that is out of reach, as from the folded rest pose), and small joint steps limited by :class:`MotionLimits`.
Every waypoint is checked before anything moves: during the rise the tool and the elbow and wrist joints never go
lower than they started, after it they stay above the floor heights; the tool stays inside the reach limit, and
every joint stays inside the servo's calibrated range. A refused plan has an empty path and a reason.

:func:`execute` sends a checked path to a servo bus. Before torque comes on, every goal is set to the present
position, so enabling torque cannot make the arm jump. If a joint lags behind its command by more than the
tracking limit (a collision, an overload, a blocked joint) it stops, commands the present position and reports;
it never retries. Torque stays on afterwards: switching it off would drop the arm.

The limits have hard caps that callers cannot raise. Angles are degrees (Studio readings), lengths metres.
"""

from __future__ import annotations

import argparse
import logging
import math
import sys
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from itertools import pairwise
from pathlib import Path
from typing import Protocol

import numpy as np

from defect_sorter.geometry import Intrinsics
from defect_sorter.joint_calibration import TICKS_PER_DEGREE
from defect_sorter.kinematics import inverse, joint_frames, tool_pose
from defect_sorter.robot_pose import RobotCalibration, model_from_readings, readings_from_model
from defect_sorter.targeting import ApproachChoice, BowlPose, BrickPose

logger = logging.getLogger(__name__)

BODY_JOINTS: tuple[str, ...] = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll")
HARD_MAX_SPEED_DEG_S = 30.0
HARD_MAX_REACH_M = 0.42
HARD_MAX_TRACKING_ERROR_DEG = 20.0
DOWN = (0.0, 0.0, -1.0)


@dataclass(frozen=True)
class MotionLimits:
	"""Speed and workspace limits for scripted moves; values beyond the hard caps are rejected.

	Parameters
	----------
	max_speed_deg_s : float
		Fastest joint speed, degrees per second (capped at :data:`HARD_MAX_SPEED_DEG_S`).
	min_tool_height_m : float
		Floor for the tool point above the table; a path may not go lower once below it.
	min_link_height_m : float
		Floor for the elbow, wrist-flex and wrist-roll joints.
	max_reach_m : float
		Largest horizontal distance of the tool point from the robot base (capped at :data:`HARD_MAX_REACH_M`).
	max_tracking_error_deg : float
		How far a joint may lag its command during :func:`execute` before the move stops.
	"""

	max_speed_deg_s: float = 15.0
	min_tool_height_m: float = 0.02
	min_link_height_m: float = 0.01
	max_reach_m: float = 0.40
	max_tracking_error_deg: float = 10.0

	def __post_init__(self) -> None:
		if not 0 < self.max_speed_deg_s <= HARD_MAX_SPEED_DEG_S:
			raise ValueError(f"max speed must be in (0, {HARD_MAX_SPEED_DEG_S}] deg/s")
		if self.min_tool_height_m < 0 or self.min_link_height_m < 0:
			raise ValueError("floor heights must not be negative")
		if not 0 < self.max_reach_m <= HARD_MAX_REACH_M:
			raise ValueError(f"reach limit must be in (0, {HARD_MAX_REACH_M}] m")
		if not 0 < self.max_tracking_error_deg <= HARD_MAX_TRACKING_ERROR_DEG:
			raise ValueError(f"tracking limit must be in (0, {HARD_MAX_TRACKING_ERROR_DEG}] deg")


@dataclass(frozen=True)
class MovePlan:
	"""Joint path (Studio readings, body joints only) from the current pose to the goal, or a refusal."""

	ok: bool
	path: list[dict[str, float]] = field(default_factory=list)
	reason: str = ""


def interpolate(
	start: dict[str, float], goal: dict[str, float], *, speed_deg_s: float, dt_s: float
) -> list[dict[str, float]]:
	"""Waypoints after ``start`` up to ``goal``; no joint moves more than ``speed_deg_s * dt_s`` per step."""
	step = speed_deg_s * dt_s
	largest = max(abs(goal[j] - start[j]) for j in goal)
	n = max(1, math.ceil(largest / step - 1e-9))
	return [{j: start[j] + (goal[j] - start[j]) * k / n for j in goal} for k in range(1, n + 1)]


def to_ticks(readings_deg: dict[str, float], ranges: dict[str, tuple[int, int]]) -> dict[str, int]:
	"""Studio degrees to raw ticks (zero at the range midpoint); raises outside the servo's calibrated range."""
	ticks = {}
	for joint, deg in readings_deg.items():
		lo, hi = ranges[joint]
		value = round((lo + hi) / 2 + deg * TICKS_PER_DEGREE)
		if not lo <= value <= hi:
			raise ValueError(f"{joint} {deg:+.1f} deg is outside its calibrated range")
		ticks[joint] = value
	return ticks


def _heights(readings: dict[str, float], cal: RobotCalibration) -> tuple[np.ndarray, float, list[float]]:
	model = model_from_readings(readings, cal)
	tool = cal.to_table(tool_pose(model)[:3, 3])
	links = [float(cal.to_table(f[:3, 3])[2]) for f in joint_frames(model)[2:]]
	return tool, float(tool[2]), links


def _solve(
	target_table: np.ndarray,
	roll_deg: float,
	cal: RobotCalibration,
	tolerance_deg: float,
	approach_table: np.ndarray | tuple[float, float, float] = DOWN,
) -> dict[str, float] | None:
	sol = inverse(
		cal.to_base(target_table),
		approach=cal.direction_to_base(approach_table),
		roll_deg=roll_deg,
		tolerance_deg=tolerance_deg,
	)
	if not sol.reachable:
		return None
	return {j: v for j, v in readings_from_model(sol.angles_deg, cal).items() if j in BODY_JOINTS}


def plan_move(
	start_readings: dict[str, float],
	target_table_m: np.ndarray,
	*,
	roll_deg: float,
	calibration: RobotCalibration,
	limits: MotionLimits,
	ranges: dict[str, tuple[int, int]],
	dt_s: float = 0.05,
	approach_tolerance_deg: float = 5.0,
	approach_table: np.ndarray | tuple[float, float, float] = DOWN,
) -> MovePlan:
	"""Plan a move of the tool point to ``target_table_m`` and check it; see the module docstring.

	The jaws end up pointing along ``approach_table`` (unit, table frame; straight down by default, see
	:func:`defect_sorter.targeting.approach_vector` for tilted ones), at most ``approach_tolerance_deg`` off. The
	model's wrist flex stops at 95°, which limits a strictly vertical approach to a narrow band of the table.
	"""
	cal = calibration
	target = np.asarray(target_table_m, dtype=np.float64)
	if target[2] < limits.min_tool_height_m:
		return MovePlan(False, reason=f"target height {target[2] * 1000:.0f} mm is below the tool floor")
	if np.linalg.norm(cal.to_base(target)[:2]) > limits.max_reach_m:
		return MovePlan(False, reason=f"target is beyond the {limits.max_reach_m * 100:.0f} cm reach limit")
	approach = np.asarray(approach_table, dtype=np.float64)
	approach = approach / np.linalg.norm(approach)
	tilt = float(np.degrees(np.arccos(np.clip(-approach[2], -1.0, 1.0))))
	goal = _solve(target, roll_deg, cal, approach_tolerance_deg, approach)
	if goal is None:
		return MovePlan(False, reason=f"target is out of reach for this approach ({tilt:.0f} deg from vertical)")

	start = {j: float(start_readings[j]) for j in BODY_JOINTS}
	start_tool, start_h, start_links = _heights(start, cal)
	stops = [start]
	if start_h < target[2] - 0.01:
		above = np.array([start_tool[0], start_tool[1], target[2]])
		rise = _solve(above, roll_deg, cal, approach_tolerance_deg, approach)
		if rise is None:  # e.g. from the folded rest pose: lift first as the gripper is, turn it afterwards
			present = cal.base_rotation @ tool_pose(model_from_readings(start, cal))[:3, 2]
			rise = _solve(above, start["wrist_roll"], cal, approach_tolerance_deg, present)
		if rise is None:
			return MovePlan(False, reason="cannot rise straight up from the current pose; raise the arm first")
		stops.append(rise)
	stops.append(goal)

	path: list[dict[str, float]] = []
	risen_at = None
	for a, b in pairwise(stops):
		path.extend(interpolate(a, b, speed_deg_s=limits.max_speed_deg_s, dt_s=dt_s))
		if risen_at is None and len(stops) == 3:
			risen_at = len(path)  # waypoints from here on come after the rise

	rise_tool_floor = min(limits.min_tool_height_m, start_h) - 0.001
	rise_link_floors = [min(limits.min_link_height_m, h) - 0.001 for h in start_links]
	for i, wp in enumerate(path):
		tool, h, links = _heights(wp, cal)
		after_rise = risen_at is not None and i >= risen_at
		tool_floor = limits.min_tool_height_m - 0.001 if after_rise else rise_tool_floor
		link_floors = [limits.min_link_height_m - 0.001] * len(links) if after_rise else rise_link_floors
		if h < tool_floor:
			return MovePlan(False, reason=f"step {i}: tool height {h * 1000:.0f} mm would go below the floor")
		if any(z < f for z, f in zip(links, link_floors, strict=True)):
			return MovePlan(False, reason=f"step {i}: a wrist or elbow joint would go below its height floor")
		if np.linalg.norm(cal.to_base(tool)[:2]) > limits.max_reach_m + 0.01:
			return MovePlan(False, reason=f"step {i}: tool would leave the reach limit")
		try:
			to_ticks(wp, ranges)
		except ValueError as exc:
			return MovePlan(False, reason=f"step {i}: {exc}")
	return MovePlan(True, path=path)


def plan_joint_move(
	start_readings: dict[str, float],
	goal_readings: dict[str, float],
	*,
	calibration: RobotCalibration,
	limits: MotionLimits,
	ranges: dict[str, tuple[int, int]],
	dt_s: float = 0.05,
) -> MovePlan:
	"""Plan a straight joint-space move to ``goal_readings`` (body joints, Studio degrees) and check every waypoint.

	For poses given as joint angles, such as the inspection holds in front of the camera. The checks are those of
	:func:`plan_move`: the tool and the elbow and wrist joints stay above their floors (or, when the arm starts below
	one, never lower than they start), the tool inside the reach limit and every joint inside its servo range.
	"""
	cal = calibration
	start = {j: float(start_readings[j]) for j in BODY_JOINTS}
	goal = {j: float(goal_readings[j]) for j in BODY_JOINTS}
	path = interpolate(start, goal, speed_deg_s=limits.max_speed_deg_s, dt_s=dt_s)
	_, start_h, start_links = _heights(start, cal)
	tool_floor = min(limits.min_tool_height_m, start_h) - 0.001
	link_floors = [min(limits.min_link_height_m, h) - 0.001 for h in start_links]
	for i, wp in enumerate(path):
		tool, h, links = _heights(wp, cal)
		if h < tool_floor:
			return MovePlan(False, reason=f"step {i}: tool height {h * 1000:.0f} mm would go below the floor")
		if any(z < f for z, f in zip(links, link_floors, strict=True)):
			return MovePlan(False, reason=f"step {i}: a wrist or elbow joint would go below its height floor")
		if np.linalg.norm(cal.to_base(tool)[:2]) > limits.max_reach_m + 0.01:
			return MovePlan(False, reason=f"step {i}: tool would leave the reach limit")
		try:
			to_ticks(wp, ranges)
		except ValueError as exc:
			return MovePlan(False, reason=f"step {i}: {exc}")
	return MovePlan(True, path=path)


def plan_lift(
	start_readings: dict[str, float],
	*,
	calibration: RobotCalibration,
	limits: MotionLimits,
	ranges: dict[str, tuple[int, int]],
	rise_m: float = 0.05,
	max_drift_m: float = 0.02,
	dt_s: float = 0.05,
) -> MovePlan:
	"""Raise the tool by ``rise_m`` over the same spot (within ``max_drift_m``), as from a grasp low at the table.

	Unlike the straight rise of :func:`plan_move`, the jaws need not keep an exact approach direction, so it also works
	where inverse kinematics cannot hold one (near the edge of the reach). Small shoulder-lift and elbow changes are
	searched, the wrist flex taking up their sum so the gripper keeps its pitch and the roll is untouched; the smallest
	change that rises enough wins, and the move goes through :func:`plan_joint_move`'s checks.
	"""
	cal = calibration
	start = {j: float(start_readings[j]) for j in BODY_JOINTS}
	p0, h0, _ = _heights(start, cal)
	candidates = []
	steps = np.arange(-30.0, 30.0 + 1e-9, 2.0)
	for d_lift in steps:
		for d_elbow in steps:
			goal = dict(start)
			goal["shoulder_lift"] += d_lift
			goal["elbow_flex"] += d_elbow
			goal["wrist_flex"] -= d_lift + d_elbow
			p, h, _ = _heights(goal, cal)
			if h - h0 >= rise_m and np.linalg.norm(p[:2] - p0[:2]) <= max_drift_m:
				candidates.append((max(abs(d_lift), abs(d_elbow), abs(d_lift + d_elbow)), goal))
	if not candidates:
		return MovePlan(False, reason=f"no small shoulder/elbow change raises the tool {rise_m * 1000:.0f} mm in place")
	last = ""
	for _, goal in sorted(candidates, key=lambda c: c[0])[:20]:
		plan = plan_joint_move(start, goal, calibration=cal, limits=limits, ranges=ranges, dt_s=dt_s)
		if plan.ok:
			return plan
		last = plan.reason
	return MovePlan(False, reason=f"every lift candidate failed its checks (last: {last})")


def gripper_ticks(percent: float, gripper_range: tuple[int, int]) -> int:
	"""Studio's gripper reading (0 closed .. 100 open over the calibrated tick range) as a raw goal in ticks."""
	if not 0.0 <= percent <= 100.0:
		raise ValueError(f"gripper {percent:.1f} is outside 0..100")
	lo, hi = gripper_range
	return round(lo + percent / 100.0 * (hi - lo))


APPROACH_TILTS_DEG: tuple[float, ...] = (0.0, 15.0, 30.0, 45.0, 60.0, 75.0)


def plan_brick_hover(
	start_readings: dict[str, float],
	brick: BrickPose,
	*,
	calibration: RobotCalibration,
	limits: MotionLimits,
	ranges: dict[str, tuple[int, int]],
	tilts_deg: tuple[float, ...] = APPROACH_TILTS_DEG,
	standoff_m: float = 0.06,
	dt_s: float = 0.05,
	approach_tolerance_deg: float = 5.0,
	preferred_roll_deg: float = 0.0,
) -> tuple[MovePlan, ApproachChoice | None, str]:
	"""Checked move to the standoff point before a brick grasp, by the steepest approach that passes every check.

	Each tilt in turn: :func:`defect_sorter.targeting.choose_approach` (grasp and standoff reachable, wrist roll
	across the brick), then :func:`plan_move` to the standoff point along that approach. The first tilt with a plan
	that passes wins. Of the jaw orientations that grasp the brick (across its short side; also across the long side
	when that fits the jaws, :data:`~defect_sorter.targeting.JAW_FIT_M`), the wrist roll nearest ``preferred_roll_deg``
	(the middle of the range) is taken, so the wrist does not start the grasp at an end stop. Returns the plan, the
	approach (``None`` when nothing passed) and the reasons tilts were refused.
	"""
	from defect_sorter.targeting import JAW_FIT_M, choose_approach, grasp_symmetry_deg

	symmetries = [grasp_symmetry_deg(brick)]
	if symmetries[0] > 90.0 and brick.length_m <= JAW_FIT_M:
		symmetries.append(90.0)
	reasons = []
	for tilt in tilts_deg:
		passed = []
		for symmetry in symmetries:
			choice, why = choose_approach(
				brick,
				calibration=calibration,
				standoff_m=standoff_m,
				tilts_deg=(tilt,),
				reach_m=limits.max_reach_m,
				current_roll_deg=preferred_roll_deg,
				approach_tolerance_deg=approach_tolerance_deg,
				symmetry_deg=symmetry,
			)
			if choice is None:
				reasons.append(f"{tilt:.0f} deg: {why}")
				continue
			plan = plan_move(
				start_readings,
				choice.standoff_m,
				roll_deg=choice.roll.roll_deg,
				calibration=calibration,
				limits=limits,
				ranges=ranges,
				dt_s=dt_s,
				approach_tolerance_deg=approach_tolerance_deg,
				approach_table=choice.approach,
			)
			if plan.ok:
				passed.append((abs(choice.roll.roll_deg - preferred_roll_deg), plan, choice))
			else:
				reasons.append(f"{tilt:.0f} deg: {plan.reason}")
		if passed:
			_, plan, choice = min(passed, key=lambda p: p[0])
			return plan, choice, ""
	# the same refusal for every tilt (out of reach) is said once
	unique = list(dict.fromkeys(r.split(": ", 1)[1] for r in reasons))
	why = unique[0] if len(unique) == 1 else "; ".join(reasons)
	return MovePlan(False, reason=why), None, why


DROP_TILTS_DEG: tuple[float, ...] = (0.0, 15.0, 30.0, 45.0, 60.0)


def plan_bowl_drop(
	start_readings: dict[str, float],
	bowl: BowlPose,
	*,
	calibration: RobotCalibration,
	limits: MotionLimits,
	ranges: dict[str, tuple[int, int]],
	tilts_deg: tuple[float, ...] = DROP_TILTS_DEG,
	clearance_m: float = 0.08,
	margin_m: float = 0.03,
	dt_s: float = 0.05,
	approach_tolerance_deg: float = 5.0,
) -> tuple[MovePlan, np.ndarray | None, str]:
	"""Checked move to a point over ``bowl`` to let go of a brick: as central as the reach allows.

	Drop points come from :func:`defect_sorter.targeting.drop_points` (the centre first, then toward the robot,
	``margin_m`` inside the rim, ``clearance_m`` above it); for each, the steepest approach whose whole path passes
	:func:`plan_move` wins. The wrist roll stays as it is. Returns the plan, the drop point and the reason when
	nothing passed.
	"""
	from defect_sorter.targeting import approach_vector, drop_points

	cal = calibration
	points = drop_points(bowl, cal.base_position_m[:2], clearance_m=clearance_m, margin_m=margin_m)
	in_reach = [pt for pt in points if np.linalg.norm(cal.to_base(pt)[:2]) <= limits.max_reach_m]
	if not in_reach:
		nearest = min(np.linalg.norm(cal.to_base(pt)[:2]) for pt in points)
		why = (
			f"the {bowl.colour} bowl's nearest drop point is {nearest * 100:.0f} cm from the robot base, beyond the "
			f"{limits.max_reach_m * 100:.0f} cm reach limit"
		)
		return MovePlan(False, reason=why), None, why
	last = ""
	for point in in_reach:
		for tilt in tilts_deg:
			plan = plan_move(
				start_readings,
				point,
				roll_deg=float(start_readings["wrist_roll"]),
				calibration=cal,
				limits=limits,
				ranges=ranges,
				dt_s=dt_s,
				approach_tolerance_deg=approach_tolerance_deg,
				approach_table=approach_vector(point, tilt, cal),
			)
			if plan.ok:
				return plan, point, ""
			last = plan.reason
	why = f"no drop point over the {bowl.colour} bowl passes the checks (last: {last})"
	return MovePlan(False, reason=why), None, why


@dataclass(frozen=True)
class Keyframe:
	"""A taught arm pose (Studio readings, body joints) and how long to hold it, seconds (0: pass through)."""

	readings: dict[str, float]
	hold_s: float = 0.0


def save_keyframes(path: Path, keyframes: list[Keyframe], note: str = "") -> None:
	"""Write a taught sequence as JSON."""
	import json

	path.parent.mkdir(parents=True, exist_ok=True)
	data = {"note": note, "keyframes": [{"readings": k.readings, "hold_s": k.hold_s} for k in keyframes]}
	path.write_text(json.dumps(data, indent=1))


def load_keyframes(path: Path) -> list[Keyframe]:
	"""Read a sequence written by :func:`save_keyframes`."""
	import json

	data = json.loads(path.read_text())
	return [Keyframe({j: float(v) for j, v in k["readings"].items()}, float(k["hold_s"])) for k in data["keyframes"]]


def plan_keyframes(
	start_readings: dict[str, float],
	keyframes: list[Keyframe],
	*,
	calibration: RobotCalibration,
	limits: MotionLimits,
	ranges: dict[str, tuple[int, int]],
	dt_s: float = 0.05,
) -> MovePlan:
	"""Checked path through taught poses in order, holding each for its ``hold_s``.

	The taught poses are trusted (someone showed them), the blends between them are not: no step between two poses
	may take the tool or the elbow and wrist joints lower than the lower of those two poses, every step stays inside
	the reach limit and the servo ranges, and no joint moves faster than the speed limit. The gripper is not part of
	a keyframe and is never moved.
	"""
	cal = calibration
	prev = {j: float(start_readings[j]) for j in BODY_JOINTS}
	path: list[dict[str, float]] = []
	for k, frame in enumerate(keyframes):
		goal = {j: float(frame.readings[j]) for j in BODY_JOINTS}
		_, h_a, links_a = _heights(prev, cal)
		_, h_b, links_b = _heights(goal, cal)
		tool_floor = min(h_a, h_b) - 0.001
		link_floors = [min(x, y) - 0.001 for x, y in zip(links_a, links_b, strict=True)]
		segment = interpolate(prev, goal, speed_deg_s=limits.max_speed_deg_s, dt_s=dt_s)
		for wp in segment:
			tool, h, links = _heights(wp, cal)
			if h < tool_floor:
				return MovePlan(False, reason=f"keyframe {k}: the blend would take the tool below both of its poses")
			if any(z < f for z, f in zip(links, link_floors, strict=True)):
				return MovePlan(False, reason=f"keyframe {k}: the blend would take a joint below both of its poses")
			if np.linalg.norm(cal.to_base(tool)[:2]) > limits.max_reach_m + 0.01:
				return MovePlan(False, reason=f"keyframe {k}: the tool would leave the reach limit")
			try:
				to_ticks(wp, ranges)
			except ValueError as exc:
				return MovePlan(False, reason=f"keyframe {k}: {exc}")
		path.extend(segment)
		path.extend(dict(goal) for _ in range(round(frame.hold_s / dt_s)))
		prev = goal
	return MovePlan(True, path=path)


class ServoBus(Protocol):
	"""What :func:`execute` needs from the arm (implemented by :class:`defect_sorter.so101_reader.SO101Driver`)."""

	def read_ticks(self) -> dict[str, int]: ...

	def hold_and_enable_torque(self) -> None: ...

	def write_goals(self, goals: dict[str, int]) -> None: ...


@dataclass(frozen=True)
class ExecutionResult:
	"""Whether the whole path ran; on a stop, why and after how many steps."""

	ok: bool
	steps_done: int
	reason: str = ""


def execute(
	bus: ServoBus,
	path_ticks: list[dict[str, int]],
	*,
	dt_s: float,
	max_tracking_error_ticks: int,
	sleep: Callable[[float], None] = time.sleep,
) -> ExecutionResult:
	"""Run a checked path; stop and hold at the present position on excessive lag or Ctrl+C. Never retries."""
	bus.hold_and_enable_torque()
	for i, goals in enumerate(path_ticks):
		try:
			bus.write_goals(goals)
			sleep(dt_s)
			present = bus.read_ticks()
		except KeyboardInterrupt:
			present = bus.read_ticks()
			bus.write_goals({j: present[j] for j in goals})
			return ExecutionResult(False, i, "interrupted: holding the present position")
		lag = {j: abs(present[j] - goals[j]) for j in goals}
		worst = max(lag, key=lag.get)
		if lag[worst] > max_tracking_error_ticks:
			bus.write_goals({j: present[j] for j in goals})
			reason = f"{worst} lagged {lag[worst] / TICKS_PER_DEGREE:.1f} deg behind at step {i}: stopped, holding"
			logger.warning("%s", reason)
			return ExecutionResult(False, i, reason)
	return ExecutionResult(True, len(path_ticks))


def _top_camera_frames(bridge_url: str | None, frames: int) -> Iterator[tuple[np.ndarray, np.ndarray, Intrinsics]]:
	"""``frames`` top-camera frames (colour, depth, intrinsics): from a running depth bridge, else the D415 itself."""
	if bridge_url is not None:
		from defect_sorter.depth_bridge import fetch_raw, fresh_frames

		for f in fresh_frames(lambda: fetch_raw(bridge_url), frames):
			yield f.color_bgr, f.depth_m, f.intrinsics
		return
	from defect_sorter.realsense import D415Camera

	camera = D415Camera(1280, 720, 15, depth_size=(640, 480))
	try:
		for k in range(frames + 5):
			frame = camera.read()
			if k >= 5:  # let auto exposure settle
				yield frame.color_bgr, frame.depth_m, frame.intrinsics
	finally:
		camera.close()


def _measure_brick(
	anchors: tuple[int, int],
	near_m: np.ndarray | None,
	bridge_url: str | None = None,
	frames: int = 10,
	exclude_xy_m: np.ndarray | None = None,
	frame_file: Path | None = None,
	fixed_markers: tuple[int, ...] = (16, 17, 18, 7),
) -> BrickPose:
	"""Brick pose in the table frame from a burst of top-camera frames (hardware).

	With ``frame_file`` the table frame is saved whenever both anchors are seen, and used while one is hidden (by
	the arm, a hand) as long as the ``fixed_markers`` in view show the camera has not moved.
	"""
	from defect_sorter.alignment import (
		held_table_frame,
		load_table_frame,
		refine_with_depth,
		save_table_frame,
		table_frame,
	)
	from defect_sorter.geometry import deproject, fit_table_plane
	from defect_sorter.markers import detect_markers
	from defect_sorter.scene import PAPER_CELL, detect_scene
	from defect_sorter.targeting import brick_pose, combine_poses, select_brick

	poses, reasons = [], []
	saved_now = False
	for color, depth, i in _top_camera_frames(bridge_url, frames):
		pts = deproject(depth[::4, ::4], Intrinsics(i.fx / 4, i.fy / 4, i.ppx / 4, i.ppy / 4))
		plane = fit_table_plane(pts[pts[..., 2] > 0])
		markers = {d.id: refine_with_depth(d, depth, i) for d in detect_markers(color, i)}
		table = table_frame(plane, markers, anchors=anchors)
		if table.basis.startswith("anchors") and frame_file is not None and not saved_now:
			save_table_frame(frame_file, table, {m: markers[m] for m in fixed_markers if m in markers})
			saved_now = True
		if not table.basis.startswith("anchors") and frame_file is not None and frame_file.exists():
			held = held_table_frame(*load_table_frame(frame_file), markers)
			if held is not None:
				table = held
		if not table.basis.startswith("anchors"):
			reasons.append(f"anchors {anchors} not seen (saw {sorted(markers)}) and no held table frame confirmed")
			continue
		scene = detect_scene(color, depth, i, plane=plane, config=PAPER_CELL)
		found = [
			p
			for obj in scene.objects
			if obj.in_bowl is None and (p := brick_pose(obj, scene, depth, i, table)) is not None
		]
		chosen, reason = select_brick(found, near_m=near_m, exclude_xy_m=exclude_xy_m)
		if chosen is None:
			reasons.append(reason)
		else:
			poses.append(chosen)
	if len(poses) < frames // 2:
		sys.exit(f"brick found in only {len(poses)} of {frames} frames: {'; '.join(sorted(set(reasons)))}")
	brick, spread_m = combine_poses(poses)
	logger.info("brick: %d frames, centre spread %.1f mm", len(poses), spread_m * 1000)
	return brick


def _measure_bowls(
	anchors: tuple[int, int],
	bridge_url: str | None,
	frames: int = 10,
	frame_file: Path | None = None,
	fixed_markers: tuple[int, ...] = (16, 17, 18, 7),
) -> dict[str, BowlPose]:
	"""Bowl rims in the table frame from a burst of top-camera frames, the median per colour (hardware)."""
	from defect_sorter.alignment import held_table_frame, load_table_frame, refine_with_depth, table_frame
	from defect_sorter.geometry import deproject, fit_table_plane
	from defect_sorter.markers import detect_markers
	from defect_sorter.scene import PAPER_CELL, detect_scene
	from defect_sorter.targeting import bowl_pose

	seen: dict[str, list[BowlPose]] = {}
	for color, depth, i in _top_camera_frames(bridge_url, frames):
		pts = deproject(depth[::4, ::4], Intrinsics(i.fx / 4, i.fy / 4, i.ppx / 4, i.ppy / 4))
		plane = fit_table_plane(pts[pts[..., 2] > 0])
		markers = {d.id: refine_with_depth(d, depth, i) for d in detect_markers(color, i)}
		table = table_frame(plane, markers, anchors=anchors)
		if not table.basis.startswith("anchors") and frame_file is not None and frame_file.exists():
			table = held_table_frame(*load_table_frame(frame_file), markers) or table
		if not table.basis.startswith("anchors"):
			continue
		scene = detect_scene(color, depth, i, plane=plane, config=PAPER_CELL)
		for bowl in scene.bowls:
			if (pose := bowl_pose(bowl, scene, depth, i, table)) is not None:
				seen.setdefault(pose.colour, []).append(pose)
	out = {}
	for colour, poses in seen.items():
		if len(poses) >= frames // 2:
			centre = np.median([p.centre_m for p in poses], axis=0)
			out[colour] = BowlPose(
				colour,
				centre,
				float(np.median([p.radius_m for p in poses])),
				float(centre[2]),
				int(np.median([p.points for p in poses])),
			)
	return out


def main(argv: list[str] | None = None) -> None:
	"""``sorter-move``: plan (default) or run one checked move of the follower's tool point.

	Without ``--go`` nothing moves: it reads the joints, plans and prints the checks. With ``--go`` it executes the
	checked plan. Targets are table-frame millimetres (``--to``) or a point above a table marker (``--above-marker``),
	both jaws down, or the standoff point before grasping the brick on the table (``--above-brick``): the steepest
	approach that passes every check (:func:`plan_brick_hover`), the wrist roll closing the jaws across the brick.
	The marker and brick targets need the top camera; the arm must not hide the brick. Objects next to the robot
	base are never taken for the brick. Studio must not hold the follower's port.
	"""
	from defect_sorter.joint_calibration import angles_from_ticks
	from defect_sorter.robot_pose import load_calibration
	from defect_sorter.so101_reader import SO101Driver, SO101Reader

	parser = argparse.ArgumentParser(description="Plan or run one slow, checked move of the follower")
	parser.add_argument("--port", help="follower serial port (check /dev/serial/by-id); not needed with --measure-only")
	parser.add_argument("--calibration", type=Path, default=Path("data/calibration/robot.json"))
	target = parser.add_mutually_exclusive_group(required=True)
	target.add_argument("--to", type=float, nargs=3, metavar=("X", "Y", "Z"), help="table frame, mm")
	target.add_argument("--above-marker", type=int, metavar="ID", help="hover above this table marker")
	target.add_argument("--above-brick", action="store_true", help="hover above the brick on the table")
	target.add_argument("--play", type=Path, metavar="FILE", help="play a taught keyframe sequence (save_keyframes)")
	target.add_argument(
		"--above-bowl",
		choices=("green", "pink"),
		help="hold over this bowl as if to let go of a brick (rim from depth)",
	)
	parser.add_argument("--near", type=float, nargs=2, metavar=("X", "Y"), help="with several bricks: the one near")
	parser.add_argument("--height", type=float, default=60.0, help="hover height above the marker, mm")
	parser.add_argument(
		"--standoff", type=float, default=60.0, help="brick: distance back from the grasp point along the approach, mm"
	)
	parser.add_argument(
		"--approach",
		choices=("auto", "down"),
		default="auto",
		help="brick: steepest tilt that passes, or only straight down",
	)
	parser.add_argument("--anchors", type=int, nargs=2, default=[16, 17], metavar=("A", "B"))
	parser.add_argument(
		"--frame-file",
		type=Path,
		default=Path("data/depth/table-frame.json"),
		help="table frame saved while both anchors are seen, used while one is hidden (fixed tags must agree)",
	)
	parser.add_argument(
		"--bridge", metavar="URL", help="read the top camera from a running sorter-depth-bridge (http://host:port)"
	)
	parser.add_argument(
		"--measure-only", action="store_true", help="with --above-brick/--above-bowl: print what is seen, no arm"
	)
	parser.add_argument("--clearance", type=float, default=80.0, help="bowl: height above the rim to let go at, mm")
	parser.add_argument(
		"--roll", type=float, help="wrist roll reading at the goal, degrees (default 0, or the grasp roll for a brick)"
	)
	parser.add_argument("--speed", type=float, default=10.0, help=f"deg/s, at most {HARD_MAX_SPEED_DEG_S:.0f}")
	parser.add_argument(
		"--reach",
		type=float,
		default=400.0,
		help=f"reach limit from the base, mm, at most {HARD_MAX_REACH_M * 1000:.0f}",
	)
	parser.add_argument("--go", action="store_true", help="execute the plan (the arm moves)")
	args = parser.parse_args(argv)
	if args.measure_only and not (args.above_brick or args.above_bowl):
		parser.error("--measure-only goes with --above-brick or --above-bowl")
	if args.port is None and not args.measure_only:
		parser.error("--port is required")
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

	cal = None if args.measure_only and not args.calibration.exists() else load_calibration(args.calibration)
	if args.above_marker is not None:
		from defect_sorter.calibration_capture import _measure_marker

		_, position = _measure_marker(args.above_marker, tuple(args.anchors))
		goal = position + np.array([0.0, 0.0, args.height / 1000])
	elif args.above_brick:
		from defect_sorter.targeting import grasp_symmetry_deg

		near = None if args.near is None else np.array(args.near) / 1000
		base_xy = None if cal is None else cal.base_position_m[:2]
		brick = _measure_brick(tuple(args.anchors), near, args.bridge, exclude_xy_m=base_xy, frame_file=args.frame_file)
		goal = None
		symmetry = grasp_symmetry_deg(brick)
		sys.stdout.write(
			f"brick at ({brick.centre_m[0] * 1000:.0f}, {brick.centre_m[1] * 1000:.0f}) mm, top "
			f"{brick.centre_m[2] * 1000:.0f} mm, yaw {brick.yaw_deg:+.0f} deg, "
			f"{brick.length_m * 1000:.0f} x {brick.width_m * 1000:.0f} mm "
			f"({'square' if symmetry == 90.0 else 'long'}), {brick.points} top-face points\n"
		)
		if args.measure_only:
			return
	elif args.above_bowl:
		bowls = _measure_bowls(tuple(args.anchors), args.bridge, frame_file=args.frame_file)
		for b in bowls.values():
			sys.stdout.write(
				f"{b.colour} bowl: rim centre ({b.centre_m[0] * 1000:.0f}, {b.centre_m[1] * 1000:.0f}) mm, radius "
				f"{b.radius_m * 1000:.0f} mm, rim {b.rim_height_m * 1000:.0f} mm high, {b.points} rim points\n"
			)
		if args.above_bowl not in bowls:
			sys.exit(f"refused: the {args.above_bowl} bowl was not found in at least half the frames")
		if args.measure_only:
			return
		bowl = bowls[args.above_bowl]
		goal = None
	elif args.play is not None:
		keyframes = load_keyframes(args.play)
		goal = None
	else:
		goal = np.array(args.to) / 1000
	limits = MotionLimits(max_speed_deg_s=args.speed, max_reach_m=args.reach / 1000)
	dt = 0.05
	out = sys.stdout
	with (SO101Driver if args.go else SO101Reader)(args.port) as arm:
		ranges = arm.ranges()
		start = angles_from_ticks(arm.read_ticks(), ranges)
		if args.above_brick:
			plan, choice, why = plan_brick_hover(
				start,
				brick,
				calibration=cal,
				limits=limits,
				ranges=ranges,
				tilts_deg=APPROACH_TILTS_DEG if args.approach == "auto" else (0.0,),
				standoff_m=args.standoff / 1000,
				dt_s=dt,
			)
			if choice is None:
				sys.exit(f"refused: {why}")
			goal, roll = choice.standoff_m, choice.roll.roll_deg
			out.write(
				f"approach {choice.tilt_deg:.0f} deg from vertical; grasp point ({choice.grasp_m[0] * 1000:.0f}, "
				f"{choice.grasp_m[1] * 1000:.0f}, {choice.grasp_m[2] * 1000:.0f}) mm, standoff {args.standoff:.0f} mm\n"
			)
		elif args.play is not None:
			plan = plan_keyframes(start, keyframes, calibration=cal, limits=limits, ranges=ranges, dt_s=dt)
			holds = sum(1 for k in keyframes if k.hold_s > 0)
			out.write(f"sequence {args.play.name}: {len(keyframes)} poses, {holds} held\n")
			goal = _heights(keyframes[-1].readings, cal)[0]
			roll = keyframes[-1].readings["wrist_roll"]
		elif args.above_bowl:
			plan, goal, why = plan_bowl_drop(
				start, bowl, calibration=cal, limits=limits, ranges=ranges, clearance_m=args.clearance / 1000, dt_s=dt
			)
			if goal is None:
				sys.exit(f"refused: {why}")
			roll = start["wrist_roll"]
			off = np.hypot(*(goal[:2] - bowl.centre_m[:2])) * 1000
			out.write(f"drop point {off:.0f} mm from the {bowl.colour} bowl's centre toward the robot\n")
		else:
			roll = 0.0 if args.roll is None else args.roll
			plan = plan_move(start, goal, roll_deg=roll, calibration=cal, limits=limits, ranges=ranges, dt_s=dt)
		start_tool, start_h, _ = _heights({j: start[j] for j in BODY_JOINTS}, cal)
		out.write(f"from tool at ({start_tool[0] * 1000:.0f}, {start_tool[1] * 1000:.0f}, {start_h * 1000:.0f}) mm\n")
		out.write(f"to   ({goal[0] * 1000:.0f}, {goal[1] * 1000:.0f}, {goal[2] * 1000:.0f}) mm, roll {roll:+.0f} deg\n")
		if not plan.ok:
			sys.exit(f"refused: {plan.reason}")
		lowest = min(_heights(wp, cal)[1] for wp in plan.path)
		out.write(
			f"plan ok: {len(plan.path)} steps, {len(plan.path) * dt:.1f} s at {args.speed:.0f} deg/s, "
			f"lowest tool point {lowest * 1000:.0f} mm\n"
		)
		out.write("goal readings: " + ", ".join(f"{j} {v:+.1f}" for j, v in plan.path[-1].items()) + "\n")
		if not args.go:
			out.write("dry run: nothing moved (add --go to execute)\n")
			return
		path_ticks = [to_ticks(wp, ranges) for wp in plan.path]
		result = execute(
			arm,
			path_ticks,
			dt_s=dt,
			max_tracking_error_ticks=round(limits.max_tracking_error_deg * TICKS_PER_DEGREE),
		)
		out.write(("done: arm holds the goal (torque on)\n") if result.ok else f"STOPPED: {result.reason}\n")


if __name__ == "__main__":
	main()
