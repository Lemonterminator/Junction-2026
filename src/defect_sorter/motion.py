"""Slow, checked point-to-point moves of the follower: plan in degrees, check against the table, then execute.

:func:`plan_move` turns a table-frame target for the tool point (between the jaws) into a joint path: inverse
kinematics for the goal, a straight rise first when the jaws start below the travel height, and small joint
steps limited by :class:`MotionLimits`. Every waypoint is checked before anything moves: the tool and the elbow
and wrist joints never go lower once they are below the floor heights, the tool stays inside the reach limit, and
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
from collections.abc import Callable
from dataclasses import dataclass, field
from itertools import pairwise
from pathlib import Path
from typing import Protocol

import numpy as np

from defect_sorter.joint_calibration import TICKS_PER_DEGREE
from defect_sorter.kinematics import inverse, joint_frames, tool_pose
from defect_sorter.robot_pose import RobotCalibration, model_from_readings, readings_from_model
from defect_sorter.targeting import BrickPose

logger = logging.getLogger(__name__)

BODY_JOINTS: tuple[str, ...] = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll")
HARD_MAX_SPEED_DEG_S = 30.0
HARD_MAX_REACH_M = 0.35
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
	max_reach_m: float = 0.30
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
	target_table: np.ndarray, roll_deg: float, cal: RobotCalibration, tolerance_deg: float
) -> dict[str, float] | None:
	sol = inverse(
		cal.to_base(target_table), approach=cal.direction_to_base(DOWN), roll_deg=roll_deg, tolerance_deg=tolerance_deg
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
) -> MovePlan:
	"""Plan a jaws-down move of the tool point to ``target_table_m`` and check it; see the module docstring.

	``approach_tolerance_deg`` is how far from vertical the jaws may end up. The model's wrist flex stops at 95°,
	which limits a strictly vertical approach to low hover heights; a few degrees of tilt widen the region.
	"""
	cal = calibration
	target = np.asarray(target_table_m, dtype=np.float64)
	if target[2] < limits.min_tool_height_m:
		return MovePlan(False, reason=f"target height {target[2] * 1000:.0f} mm is below the tool floor")
	if np.linalg.norm(cal.to_base(target)[:2]) > limits.max_reach_m:
		return MovePlan(False, reason=f"target is beyond the {limits.max_reach_m * 100:.0f} cm reach limit")
	goal = _solve(target, roll_deg, cal, approach_tolerance_deg)
	if goal is None:
		return MovePlan(False, reason="target is out of reach for a jaws-down approach")

	start = {j: float(start_readings[j]) for j in BODY_JOINTS}
	start_tool, start_h, start_links = _heights(start, cal)
	stops = [start]
	if start_h < target[2] - 0.01:
		rise = _solve(np.array([start_tool[0], start_tool[1], target[2]]), roll_deg, cal, approach_tolerance_deg)
		if rise is None:
			return MovePlan(False, reason="cannot rise straight up from the current pose; raise the arm first")
		stops.append(rise)
	stops.append(goal)

	path: list[dict[str, float]] = []
	for a, b in pairwise(stops):
		path.extend(interpolate(a, b, speed_deg_s=limits.max_speed_deg_s, dt_s=dt_s))

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


def _measure_brick(anchors: tuple[int, int], near_m: np.ndarray | None, frames: int = 10) -> BrickPose:
	"""Brick pose in the table frame from a burst of top-camera frames, arm at rest (hardware)."""
	from defect_sorter.alignment import refine_with_depth, table_frame
	from defect_sorter.geometry import Intrinsics, deproject, fit_table_plane
	from defect_sorter.markers import detect_markers
	from defect_sorter.realsense import D415Camera
	from defect_sorter.scene import detect_scene
	from defect_sorter.targeting import brick_pose, combine_poses, select_brick

	camera = D415Camera(1280, 720, 15, depth_size=(640, 480))
	poses, reasons = [], []
	try:
		for k in range(frames + 5):
			frame = camera.read()
			if k < 5:  # let auto exposure settle
				continue
			i = frame.intrinsics
			pts = deproject(frame.depth_m[::4, ::4], Intrinsics(i.fx / 4, i.fy / 4, i.ppx / 4, i.ppy / 4))
			plane = fit_table_plane(pts[pts[..., 2] > 0])
			markers = {
				d.id: refine_with_depth(d, frame.depth_m, frame.intrinsics)
				for d in detect_markers(frame.color_bgr, frame.intrinsics)
			}
			table = table_frame(plane, markers, anchors=anchors)
			if not table.basis.startswith("anchors"):
				reasons.append(f"anchors {anchors} not seen")
				continue
			scene = detect_scene(frame.color_bgr, frame.depth_m, frame.intrinsics, plane=plane)
			found = [
				p
				for obj in scene.objects
				if obj.in_bowl is None
				and (p := brick_pose(obj, scene, frame.depth_m, frame.intrinsics, table)) is not None
			]
			chosen, reason = select_brick(found, near_m=near_m)
			if chosen is None:
				reasons.append(reason)
			else:
				poses.append(chosen)
	finally:
		camera.close()
	if len(poses) < frames // 2:
		sys.exit(f"brick found in only {len(poses)} of {frames} frames: {'; '.join(sorted(set(reasons)))}")
	brick, spread_m = combine_poses(poses)
	logger.info("brick: %d frames, centre spread %.1f mm", len(poses), spread_m * 1000)
	return brick


def main(argv: list[str] | None = None) -> None:
	"""``sorter-move``: plan (default) or run one checked jaws-down move of the follower's tool point.

	Without ``--go`` nothing moves: it reads the joints, plans and prints the checks. With ``--go`` it executes the
	checked plan. Targets are table-frame millimetres (``--to``), a point above a table marker (``--above-marker``)
	or a point above the brick on the table (``--above-brick``, wrist roll chosen to close the jaws across the
	brick's short side); the last two need the top camera, and for the brick the arm must be at rest so it does not
	hide or look like an object. Studio must not hold the follower's port.
	"""
	from defect_sorter.joint_calibration import angles_from_ticks
	from defect_sorter.robot_pose import load_calibration
	from defect_sorter.so101_reader import SO101Driver, SO101Reader

	parser = argparse.ArgumentParser(description="Plan or run one slow, checked move of the follower (jaws down)")
	parser.add_argument("--port", required=True, help="follower serial port (check /dev/serial/by-id)")
	parser.add_argument("--calibration", type=Path, default=Path("data/calibration/robot.json"))
	target = parser.add_mutually_exclusive_group(required=True)
	target.add_argument("--to", type=float, nargs=3, metavar=("X", "Y", "Z"), help="table frame, mm")
	target.add_argument("--above-marker", type=int, metavar="ID", help="hover above this table marker")
	target.add_argument("--above-brick", action="store_true", help="hover above the brick on the table")
	parser.add_argument("--near", type=float, nargs=2, metavar=("X", "Y"), help="with several bricks: the one near")
	parser.add_argument("--height", type=float, default=60.0, help="hover height above the marker or brick, mm")
	parser.add_argument("--anchors", type=int, nargs=2, default=[16, 17], metavar=("A", "B"))
	parser.add_argument(
		"--roll", type=float, help="wrist roll reading at the goal, degrees (default 0, or the grasp roll for a brick)"
	)
	parser.add_argument("--speed", type=float, default=10.0, help=f"deg/s, at most {HARD_MAX_SPEED_DEG_S:.0f}")
	parser.add_argument("--go", action="store_true", help="execute the plan (the arm moves)")
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

	cal = load_calibration(args.calibration)
	if args.above_marker is not None:
		from defect_sorter.calibration_capture import _measure_marker

		_, position = _measure_marker(args.above_marker, tuple(args.anchors))
		goal = position + np.array([0.0, 0.0, args.height / 1000])
	elif args.above_brick:
		from defect_sorter.targeting import hover_target

		near = None if args.near is None else np.array(args.near) / 1000
		brick = _measure_brick(tuple(args.anchors), near)
		goal = hover_target(brick, height_m=args.height / 1000)
		sys.stdout.write(
			f"brick at ({brick.centre_m[0] * 1000:.0f}, {brick.centre_m[1] * 1000:.0f}) mm, top "
			f"{brick.centre_m[2] * 1000:.0f} mm, yaw {brick.yaw_deg:+.0f} deg, "
			f"{brick.length_m * 1000:.0f} x {brick.width_m * 1000:.0f} mm\n"
		)
	else:
		goal = np.array(args.to) / 1000
	limits = MotionLimits(max_speed_deg_s=args.speed)
	dt = 0.05
	out = sys.stdout
	with (SO101Driver if args.go else SO101Reader)(args.port) as arm:
		ranges = arm.ranges()
		start = angles_from_ticks(arm.read_ticks(), ranges)
		roll = 0.0 if args.roll is None else args.roll
		if args.above_brick and args.roll is None:
			from defect_sorter.targeting import grasp_roll

			grasp = grasp_roll(goal, brick.yaw_deg, calibration=cal, current_roll_deg=start["wrist_roll"])
			if grasp is None:
				sys.exit("refused: no wrist roll inside the joint range lines the jaws up with the brick")
			roll = grasp.roll_deg
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
