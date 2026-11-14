"""Capture and solve a camera-based joint calibration of the SO-101 follower (measure only).

Capture: the follower's torque is off, someone moves it by hand through 15-20 clearly different poses and holds
each still for about a second with the gripper marker visible to the top camera. Each still pose is recorded
once: the joint ticks plus the marker pose in the table frame. Solve: :func:`defect_sorter.joint_calibration.solve`
reports joint zero offsets, the robot base pose on the table and the fit quality. Nothing is written to the arm.

	uv run sorter-joint-calibration capture --port /dev/ttyACM0 --out data/calibration/session.jsonl
	uv run sorter-joint-calibration solve --session data/calibration/session.jsonl --save data/calibration/robot.json
	uv run sorter-joint-calibration link-base --calibration data/calibration/robot.json --marker 15
	uv run sorter-joint-calibration locate --calibration data/calibration/robot.json

``solve`` accepts several sessions of the same marker mounting and fits them together; vary the wrist roll between
poses, or the wrist_flex offset is not observable. ``link-base`` measures a marker fixed on the base plate while
the robot still stands where it was calibrated; afterwards ``locate`` finds the base from that marker alone, so
the robot can be moved without another capture.

Only one process can open the D415 and each serial port: stop the alignment page and close Studio's environment
and robot pages first.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np

from defect_sorter.joint_calibration import TICKS_PER_DEGREE, Observation, angles_from_ticks, solve
from defect_sorter.robot_pose import RobotCalibration, link_base_marker, load_calibration, save_calibration

logger = logging.getLogger(__name__)

BODY_JOINTS = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll")


class StillnessGate:
	"""Decide when to take one sample: the arm and the marker held still long enough, in a new pose.

	Parameters
	----------
	hold_s : float
		How long joints and marker must stay within tolerance.
	tick_tol : int
		Allowed joint drift while "still", ticks (12 ticks is about 1 degree: an arm held by hand trembles).
	marker_tol_mm : float
		Allowed marker drift while "still", millimetres (hand tremor plus depth noise).
	min_change_deg : float
		A new sample needs at least one body joint this far from the last recorded pose.
	"""

	def __init__(
		self, hold_s: float = 0.8, tick_tol: int = 12, marker_tol_mm: float = 4.0, min_change_deg: float = 5.0
	) -> None:
		self.hold_s, self.tick_tol, self.marker_tol_mm, self.min_change_deg = (
			hold_s,
			tick_tol,
			marker_tol_mm,
			min_change_deg,
		)
		self._anchor_ticks: dict[str, int] | None = None
		self._anchor_pos: np.ndarray | None = None
		self._since: float | None = None
		self._decided = False
		self._last_recorded: dict[str, int] | None = None

	def update(self, t: float, ticks: dict[str, int], marker_pos: np.ndarray | None) -> bool:
		"""Feed one reading; returns True exactly once per new, held pose."""
		if marker_pos is None:
			self._since = None
			return False
		moved = (
			self._anchor_ticks is None
			or self._since is None
			or any(abs(ticks[j] - self._anchor_ticks[j]) > self.tick_tol for j in BODY_JOINTS if j in ticks)
			or float(np.linalg.norm(np.asarray(marker_pos) - self._anchor_pos)) * 1000.0 > self.marker_tol_mm
		)
		if moved:
			self._anchor_ticks, self._anchor_pos, self._since, self._decided = (
				dict(ticks),
				np.asarray(marker_pos, dtype=float),
				t,
				False,
			)
			return False
		if self._decided or t - self._since < self.hold_s:
			return False
		self._decided = True
		if self._last_recorded is not None:
			change = max(abs(ticks[j] - self._last_recorded[j]) / TICKS_PER_DEGREE for j in BODY_JOINTS if j in ticks)
			if change < self.min_change_deg:
				return False
		self._last_recorded = dict(ticks)
		return True


def save_session(
	path: Path,
	ranges: dict[str, tuple[int, int]],
	raw_ticks: list[dict[str, int]],
	observations: list[Observation],
	meta: dict,
) -> None:
	"""Write a capture session as JSON lines: a header with the joint ranges, then one line per observation."""
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open("w") as fh:
		fh.write(json.dumps({"type": "header", "ranges": {k: list(v) for k, v in ranges.items()}, "meta": meta}) + "\n")
		for ticks, o in zip(raw_ticks, observations, strict=True):
			fh.write(
				json.dumps(
					{
						"type": "observation",
						"ticks": ticks,
						"angles_deg": o.angles_deg,
						"rotation": np.asarray(o.marker_rotation).tolist(),
						"position_m": np.asarray(o.marker_position_m).tolist(),
					}
				)
				+ "\n"
			)


def load_session(path: Path) -> tuple[dict[str, tuple[int, int]], list[dict[str, int]], list[Observation], dict]:
	"""Read a session written by :func:`save_session`."""
	ranges: dict[str, tuple[int, int]] = {}
	meta: dict = {}
	raw: list[dict[str, int]] = []
	obs: list[Observation] = []
	for line in path.read_text().splitlines():
		row = json.loads(line)
		if row["type"] == "header":
			ranges = {k: (int(v[0]), int(v[1])) for k, v in row["ranges"].items()}
			meta = row["meta"]
		else:
			raw.append(row["ticks"])
			obs.append(
				Observation(
					angles_deg=row["angles_deg"],
					marker_rotation=np.array(row["rotation"]),
					marker_position_m=np.array(row["position_m"]),
				)
			)
	return ranges, raw, obs, meta


def _capture(args: argparse.Namespace) -> None:
	from defect_sorter.alignment import refine_with_depth, table_frame, table_rotation
	from defect_sorter.geometry import Intrinsics, deproject, fit_table_plane
	from defect_sorter.markers import detect_markers
	from defect_sorter.realsense import D415Camera
	from defect_sorter.so101_reader import SO101Reader

	with SO101Reader(args.port) as arm:
		torque = arm.torque_enabled()
		if any(torque.values()):
			if not args.release_torque:
				sys.exit(f"torque is on ({torque}); hold the arm and rerun with --release-torque to make it limp")
			arm.release_torque()
			logger.warning("torque released: the arm is limp")
		ranges = arm.ranges()
		camera = D415Camera(1280, 720, 15, depth_size=(640, 480))
		gate = StillnessGate()
		plane = None
		raw: list[dict[str, int]] = []
		obs: list[Observation] = []
		frames = 0
		last_status = 0.0
		try:
			while len(obs) < args.count:
				frame = camera.read()
				if plane is None or frames % 15 == 0:
					i = frame.intrinsics
					pts = deproject(frame.depth_m[::4, ::4], Intrinsics(i.fx / 4, i.fy / 4, i.ppx / 4, i.ppy / 4))
					plane = fit_table_plane(pts[pts[..., 2] > 0])
				frames += 1
				poses = {
					d.id: refine_with_depth(d, frame.depth_m, frame.intrinsics)
					for d in detect_markers(frame.color_bgr, frame.intrinsics)
				}
				table = table_frame(plane, poses, anchors=(args.anchors[0], args.anchors[1]))
				ticks = arm.read_ticks()
				marker = poses.get(args.marker)
				anchors_ok = table.basis.startswith("anchors")
				usable = marker is not None and anchors_ok
				position = table.point(marker.position_m) if usable else None
				now = time.monotonic()
				if now - last_status >= 2.0:
					seen = "not seen" if marker is None else f"seen ({marker.source})"
					anchors = "ok" if anchors_ok else "NOT both visible"
					sys.stdout.write(
						f"[{len(obs)}/{args.count}] marker {args.marker}: {seen} | anchors {args.anchors[0]}+{args.anchors[1]}: {anchors}\n"
					)
					sys.stdout.flush()
					last_status = now
				if gate.update(time.monotonic(), ticks, position):
					raw.append(ticks)
					obs.append(
						Observation(
							angles_deg=angles_from_ticks(ticks, ranges),
							marker_rotation=table_rotation(marker, table),
							marker_position_m=position,
						)
					)
					angles = obs[-1].angles_deg
					sys.stdout.write(
						f"captured {len(obs)}/{args.count}: lift {angles['shoulder_lift']:+.0f}  elbow {angles['elbow_flex']:+.0f}  wrist {angles['wrist_flex']:+.0f} deg\n"
					)
					sys.stdout.flush()
		except KeyboardInterrupt:
			sys.stdout.write("stopped early\n")
		finally:
			camera.close()
			save_session(
				args.out,
				ranges,
				raw,
				obs,
				meta={
					"marker": args.marker,
					"anchors": list(args.anchors),
					"port": args.port,
					"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
				},
			)
			sys.stdout.write(f"saved {len(obs)} observations to {args.out}\n")


def _measure_marker(marker_id: int, anchors: tuple[int, int], frames: int = 30) -> tuple[np.ndarray, np.ndarray]:
	"""Average table-frame pose of one marker over a burst of top-camera frames (hardware)."""
	from scipy.spatial.transform import Rotation

	from defect_sorter.alignment import refine_with_depth, table_frame, table_rotation
	from defect_sorter.geometry import Intrinsics, deproject, fit_table_plane
	from defect_sorter.markers import detect_markers
	from defect_sorter.realsense import D415Camera

	camera = D415Camera(1280, 720, 15, depth_size=(640, 480))
	positions, rotations = [], []
	try:
		for k in range(frames + 5):
			frame = camera.read()
			if k < 5:  # let auto exposure settle
				continue
			i = frame.intrinsics
			pts = deproject(frame.depth_m[::4, ::4], Intrinsics(i.fx / 4, i.fy / 4, i.ppx / 4, i.ppy / 4))
			plane = fit_table_plane(pts[pts[..., 2] > 0])
			poses = {
				d.id: refine_with_depth(d, frame.depth_m, frame.intrinsics)
				for d in detect_markers(frame.color_bgr, frame.intrinsics)
			}
			table = table_frame(plane, poses, anchors=anchors)
			if marker_id in poses and table.basis.startswith("anchors"):
				positions.append(table.point(poses[marker_id].position_m))
				rotations.append(table_rotation(poses[marker_id], table))
	finally:
		camera.close()
	if len(positions) < frames // 2:
		sys.exit(f"marker {marker_id} with anchors {anchors} seen in only {len(positions)} of {frames} frames")
	spread_mm = float(np.max(np.std(positions, axis=0)) * 1000)
	logger.info("marker %d: %d frames, position spread %.1f mm", marker_id, len(positions), spread_mm)
	return Rotation.from_matrix(np.array(rotations)).mean().as_matrix(), np.mean(positions, axis=0)


def _link_base(args: argparse.Namespace) -> None:
	cal = load_calibration(args.calibration)
	rotation, position = _measure_marker(args.marker, tuple(args.anchors))
	link = link_base_marker(cal.base_rotation, cal.base_position_m, rotation, position)
	save_calibration(
		args.calibration, RobotCalibration(cal.offsets_deg, cal.base_rotation, cal.base_position_m, args.marker, link)
	)
	sys.stdout.write(f"linked base marker {args.marker} in {args.calibration}\n")


def _locate(args: argparse.Namespace) -> None:
	cal = load_calibration(args.calibration)
	if cal.base_marker_id is None:
		sys.exit("no base marker linked: run link-base first")
	rotation, position = _measure_marker(cal.base_marker_id, tuple(args.anchors))
	moved = cal.relocated(rotation, position)
	shift = (moved.base_position_m - cal.base_position_m) * 1000
	turn = float(np.degrees(np.arctan2(moved.base_rotation[1, 0], moved.base_rotation[0, 0])))
	sys.stdout.write(
		f"base at x {moved.base_position_m[0] * 1000:.0f} mm, y {moved.base_position_m[1] * 1000:.0f} mm, yaw {turn:.1f} deg "
		f"(moved {np.linalg.norm(shift[:2]):.0f} mm since the saved pose)\n"
	)
	if args.update:
		save_calibration(args.calibration, moved)
		sys.stdout.write(f"updated {args.calibration}\n")


def _solve(args: argparse.Namespace) -> None:
	obs: list[Observation] = []
	meta: dict = {}
	for path in args.session:
		_, _, session_obs, meta = load_session(path)
		obs.extend(session_obs)
	result = solve(obs)
	r = result.base_rotation
	base_yaw = float(np.degrees(np.arctan2(r[1, 0], r[0, 0])))
	base_tilt = float(np.degrees(np.arccos(np.clip(r[2, 2], -1.0, 1.0))))
	out = sys.stdout
	out.write(f"observations: {result.n_observations} (marker {meta.get('marker')})\n")
	out.write(f"fit: RMS {result.rms_position_mm:.1f} mm, {result.rms_rotation_deg:.1f} deg\n")
	for joint, deg in result.offsets_deg.items():
		out.write(f"  {joint:14s} offset {deg:+6.2f} deg ({deg * TICKS_PER_DEGREE:+5.0f} ticks)\n")
	pos = result.base_position_m * 1000
	out.write(
		f"robot base in table frame: x {pos[0]:.0f} mm, y {pos[1]:.0f} mm, z {pos[2]:.0f} mm, yaw {base_yaw:.1f} deg, tilt {base_tilt:.1f} deg\n"
	)
	out.write(
		"not fitted (unobservable without a squared reference): shoulder_pan zero (in base yaw), wrist_roll zero (in marker mounting)\n"
	)
	worst = max(result.per_observation, key=lambda pr: pr[0])
	out.write(f"worst observation: {worst[0]:.1f} mm, {worst[1]:.1f} deg\n")
	big = {j: d for j, d in result.offsets_deg.items() if abs(d) >= args.tolerance_deg}
	out.write(
		("offsets above tolerance: " + ", ".join(f"{j} {d:+.1f}" for j, d in big.items()) + "\n")
		if big
		else f"all fitted offsets within {args.tolerance_deg} deg: no change needed\n"
	)
	if args.save:
		save_calibration(args.save, RobotCalibration(result.offsets_deg, result.base_rotation, result.base_position_m))
		out.write(f"saved robot calibration to {args.save}\n")


def main(argv: list[str] | None = None) -> None:
	parser = argparse.ArgumentParser(description="Camera-based joint calibration of the SO-101 follower (measure only)")
	sub = parser.add_subparsers(dest="command", required=True)
	cap = sub.add_parser("capture", help="record still poses: joint ticks + gripper marker pose")
	cap.add_argument("--port", required=True, help="follower serial port, e.g. /dev/ttyACM0 (check /dev/serial/by-id)")
	cap.add_argument("--marker", type=int, default=4, help="id of the marker on the gripper")
	cap.add_argument("--count", type=int, default=18)
	cap.add_argument(
		"--anchors",
		type=int,
		nargs=2,
		default=[16, 17],
		metavar=("A", "B"),
		help="table markers that define the frame; keep one pair for a whole session",
	)
	cap.add_argument("--out", type=Path, default=Path("data/calibration/session.jsonl"))
	cap.add_argument(
		"--release-torque", action="store_true", help="switch torque off first (the arm goes limp: hold it)"
	)
	sol = sub.add_parser("solve", help="fit offsets and base pose from a recorded session")
	sol.add_argument(
		"--session", type=Path, nargs="+", default=[Path("data/calibration/session.jsonl")], help="one or more sessions"
	)
	sol.add_argument("--tolerance-deg", type=float, default=2.0)
	sol.add_argument("--save", type=Path, help="write offsets and base pose as a robot calibration (JSON)")
	for name, text in (
		("link-base", "measure the base-plate marker next to the calibrated base and store the link"),
		("locate", "find the base from the base-plate marker (after the robot was moved)"),
	):
		sp = sub.add_parser(name, help=text)
		sp.add_argument("--calibration", type=Path, default=Path("data/calibration/robot.json"))
		sp.add_argument("--anchors", type=int, nargs=2, default=[16, 17], metavar=("A", "B"))
		if name == "link-base":
			sp.add_argument("--marker", type=int, default=15, help="id of the marker on the base plate")
		else:
			sp.add_argument("--update", action="store_true", help="save the new base pose into the calibration")
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
	{"capture": _capture, "solve": _solve, "link-base": _link_base, "locate": _locate}[args.command](args)


if __name__ == "__main__":
	main()
