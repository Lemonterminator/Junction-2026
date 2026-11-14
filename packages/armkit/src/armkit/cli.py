"""``armkit-calibrate``: plan, run and restore the automatic calibration of an arm.

``plan`` prints what the procedure would do (parking poses, sweeps, margins) from the collision model alone and never
opens a serial port. ``run`` and ``restore`` are dry runs unless ``--go`` is given; with ``--go`` the arm moves (``run``)
or its servos lose torque (both), so each asks for a typed ``YES`` first. ``run`` saves the servos' previous calibration
to ``--backup`` before it changes anything and the new one to ``--out`` afterwards.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import TextIO

from armkit.calibration import TICKS_PER_DEGREE, Calibration
from armkit.check import check_range
from armkit.frame import ModelFrame, capture_frame, directions_from_trace, refine_frame, with_directions
from armkit.guard import Contact
from armkit.measure import measure_all, measurement_order, preview_measure
from armkit.motion import MoveLimits
from armkit.park import current_pose, plan_move, run_move
from armkit.procedure import CalibrationSettings, plan_calibration, run_calibration
from armkit.profile import ArmProfile, with_table_area, with_table_clearance
from armkit.profiles.so101 import so101_profile
from armkit.servo import Clock, RealClock, ServoBus

PROFILES: dict[str, Callable[[], ArmProfile]] = {"so101": so101_profile}
REFERENCE_POSES: dict[str, tuple[dict[str, float], str]] = {
	"so101-zero": (
		{"shoulder_pan": 0.0, "shoulder_lift": 0.0, "elbow_flex": 0.0, "wrist_flex": 0.0, "wrist_roll": 0.0},
		"SO-101 model zero (the 'centred' pose of Studio's setup wizard): base turned straight ahead; upper arm nearly "
		"vertical, leaning about 14 deg forward; forearm level, pointing straight ahead; wrist in line with the forearm; "
		"jaws upright (not rolled).",
	),
	"so101-second": (
		{"shoulder_pan": 45.0, "shoulder_lift": -30.0, "elbow_flex": -45.0, "wrist_flex": 45.0, "wrist_roll": 90.0},
		"Second pose, to check each joint's direction; start from the reference pose and change every joint: base "
		"turned about 45 deg so the arm points to the robot's RIGHT; upper arm tilted about 30 deg further BACK; forearm "
		"bent about 45 deg UP at the elbow; gripper bent about 45 deg DOWN at the wrist, relative to the forearm; jaws "
		"rolled a quarter turn COUNTER-CLOCKWISE seen from behind the gripper looking out along it.",
	),
}
"""Named reference poses for ``armkit-calibrate frame``: model angles and how the pose looks."""

DIRECTION_HINTS: dict[str, dict[str, str]] = {
	"so101": {
		"shoulder_pan": "turn the whole arm to the robot's RIGHT",
		"shoulder_lift": "tilt the upper arm FORWARD, toward the table in front",
		"elbow_flex": "bend the forearm DOWN at the elbow",
		"wrist_flex": "bend the gripper DOWN at the wrist",
		"wrist_roll": "roll the jaws COUNTER-CLOCKWISE, seen from behind the gripper looking out along it",
	},
}
"""Per profile: how to move each chain joint by hand in the model's positive direction (``frame --directions``)."""


def _open_bus(port: str, profile: ArmProfile, acceleration: int | None) -> ServoBus:
	from armkit.feetech import FeetechBus

	return FeetechBus(port, {j.name: j.servo_id for j in profile.joints}, acceleration=acceleration)


def _ask(message: str) -> bool:
	sys.stdout.write(f"\n{message}\nType YES to continue: ")
	sys.stdout.flush()
	return sys.stdin.readline().strip() == "YES"


def _clock(bus: ServoBus) -> Clock:
	return bus if hasattr(bus, "now") and hasattr(bus, "sleep") else RealClock()  # type: ignore[return-value]


def describe_contacts(name: str, contacts: tuple[Contact, ...]) -> list[str]:
	"""One line per detected contact: what the guard saw (kind, load in permille) and where."""
	return [
		f"{name} contact {i}: {c.kind.value}, load {c.load} at {c.position:.0f}"
		for i, c in enumerate(contacts, start=1)
	]


def _parse_area(text: str) -> list[tuple[float, float]]:
	"""Table polygon from ``"x,y; x,y; ..."`` (metres, robot base frame)."""
	corners = [tuple(float(v) for v in part.split(",")) for part in text.split(";") if part.strip()]
	if len(corners) < 3 or any(len(c) != 2 for c in corners):
		raise ValueError("a table area needs at least three x,y corners")
	return [(c[0], c[1]) for c in corners]


def _record_directions(args: argparse.Namespace, profile: ArmProfile, out: TextIO) -> int:
	"""``frame --directions``: release the arm, sample the readings while the operator moves each joint by hand in its
	described direction, then hold the arm again and save the frame with the directions it showed."""
	if not args.refine:
		sys.exit("--directions needs --refine FRAME (a frame recorded in a reference pose)")
	first = ModelFrame.load(args.refine)
	hints = DIRECTION_HINTS.get(args.profile, {})
	chain = list(profile.robot.names)
	text = "; ".join(f"{j}: {hints.get(j, 'its positive direction')}" for j in chain)
	out.write(f"directions to move, one joint at a time, about 30 deg and back: {text}\n")
	if not args.go:
		out.write("dry run: nothing read or released (add --go)\n")
		return 0
	bus = _open_bus(args.port, profile, None)
	calibration = bus.read_calibration()
	if not _ask(f"Hold the arm: torque on {', '.join(chain)} will be switched off so you can move it by hand."):
		out.write("aborted: nothing released\n")
		return 1
	bus.set_torque(False, chain)
	trace: list[dict[str, float]] = []
	stop = threading.Event()

	def sample() -> None:
		while not stop.is_set():
			positions = bus.read_positions()
			trace.append({j: calibration[j].to_degrees(positions[j]) for j in chain})
			time.sleep(0.02)

	sampler = threading.Thread(target=sample, daemon=True)
	sampler.start()
	try:
		_ask(f"Move each joint by hand, ONE AT A TIME, about 30 deg in this direction and back: {text}.")
	finally:
		stop.set()
		sampler.join()
		bus.hold(chain)
	signs = directions_from_trace(trace, chain)
	for joint in chain:
		if joint in signs:
			out.write(f"{joint}: {'same direction as the model' if signs[joint] > 0 else 'reversed'}\n")
		else:
			out.write(f"{joint}: not moved far enough to tell\n")
	missing = [j for j in chain if j not in signs]
	if missing:
		out.write(f"not moved: {', '.join(missing)}; nothing saved, try again\n")
		return 1
	with_directions(first, signs).save(args.out)
	out.write(f"frame with checked directions saved to {args.out}\n")
	return 0


def _parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(prog="armkit-calibrate", description=__doc__.split("\n\n")[0])
	sub = parser.add_subparsers(dest="command", required=True)
	common = argparse.ArgumentParser(add_help=False)
	common.add_argument("--profile", default="so101", help="arm profile (default so101)")
	framed = argparse.ArgumentParser(add_help=False)
	framed.add_argument(
		"--table-area",
		help="where the table is, as 'x,y; x,y; ...' corners in metres in the robot base frame (default: everywhere)",
	)
	framed.add_argument(
		"--table-clearance",
		type=float,
		default=0.08,
		help="keep the arm this far above the table in every plan, metres",
	)
	framed.add_argument(
		"--frame", type=Path, help="measured model frame (armkit-calibrate frame); planning refuses without one"
	)
	selection = argparse.ArgumentParser(add_help=False)
	selection.add_argument(
		"--only", nargs="+", metavar="JOINT", help="calibrate just these joints; the others keep theirs"
	)
	sub.add_parser("plan", parents=[common, selection], help="print the plan; touches no hardware")
	chk = sub.add_parser(
		"check",
		parents=[common, framed],
		help="measure one joint's travel ends against its stored calibration; stores nothing",
	)
	chk.add_argument("--port", required=True, help="serial port (prefer /dev/serial/by-id/...)")
	chk.add_argument("--joint", required=True, help="the joint to measure (it moves through its whole range)")
	chk.add_argument("--go", action="store_true", help="really do it: the joint moves")
	chk.add_argument(
		"--backup",
		type=Path,
		default=Path("calibration-before.json"),
		help="where to save every joint's stored calibration first",
	)
	chk.add_argument(
		"--ends", nargs="+", choices=("lower", "upper"), default=("lower", "upper"), help="measure only these ends"
	)
	chk.add_argument("--torque-limit", type=int, default=250, help="permille of max torque while searching")
	chk.add_argument("--acceleration", type=int, default=40, help="servo acceleration register, 0-254")
	ms = sub.add_parser(
		"measure",
		parents=[common, framed],
		help="measure every joint's ends bottom-up and propose a calibration; stores nothing",
	)
	ms.add_argument("--port", required=True, help="serial port (prefer /dev/serial/by-id/...)")
	ms.add_argument("--joints", nargs="+", metavar="JOINT", help="measure only these joints (default: all, bottom-up)")
	ms.add_argument(
		"--out", type=Path, default=Path("calibration-proposed.json"), help="where to save the proposed calibration"
	)
	ms.add_argument(
		"--backup",
		type=Path,
		default=Path("calibration-before.json"),
		help="where to save the stored calibration first",
	)
	ms.add_argument("--go", action="store_true", help="really do it: the arm moves")
	ms.add_argument(
		"--preview", action="store_true", help="run the pipeline on a simulated copy of the arm; only reads it"
	)
	fr = sub.add_parser(
		"frame", parents=[common], help="record how servo readings map onto the model, in a reference pose"
	)
	fr.add_argument("--port", required=True, help="serial port (prefer /dev/serial/by-id/...)")
	fr.add_argument("--pose", help="the reference pose the arm is put in (see REFERENCE_POSES)")
	fr.add_argument("--out", type=Path, default=Path("frame.json"), help="where to save the frame")
	fr.add_argument(
		"--directions",
		action="store_true",
		help="check joint directions: you move each joint by hand while the readings are sampled (needs --refine)",
	)
	fr.add_argument(
		"--refine", type=Path, help="a frame from the first pose: record a second pose to check joint directions"
	)
	fr.add_argument(
		"--release",
		action="store_true",
		help="switch the arm joints' torque off so the pose can be set by hand (hold the arm!)",
	)
	fr.add_argument(
		"--go", action="store_true", help="really do it: read the arm (and with --release switch its torque off)"
	)
	mv = sub.add_parser(
		"move", parents=[common, framed], help="plan (and with --go run) a collision-checked move to a pose"
	)
	mv.add_argument("--port", required=True, help="serial port (prefer /dev/serial/by-id/...)")
	mv.add_argument(
		"--set",
		nargs="+",
		required=True,
		metavar="JOINT=DEG",
		help="target model angles in degrees (the kinematic model's joint angles, through --frame)",
	)
	mv.add_argument("--margin", type=float, default=0.005, help="clearance to keep from collisions, metres")
	mv.add_argument("--torque-limit", type=int, default=600, help="permille of max torque while moving")
	mv.add_argument("--go", action="store_true", help="really do it: the arm moves")
	for name, text in (
		("run", "calibrate the arm (dry run unless --go)"),
		("restore", "write a saved calibration back (dry run unless --go)"),
	):
		p = sub.add_parser(name, parents=[common, *([selection] if name == "run" else [])], help=text)
		p.add_argument("--port", required=True, help="serial port (prefer /dev/serial/by-id/...)")
		p.add_argument("--go", action="store_true", help="really do it: the arm moves / torque is released")
		if name == "run":
			p.add_argument(
				"--out", type=Path, default=Path("calibration.json"), help="where to save the new calibration"
			)
			p.add_argument(
				"--backup",
				type=Path,
				default=Path("calibration-before.json"),
				help="where to save the previous one first",
			)
			p.add_argument(
				"--torque-limit",
				type=int,
				default=CalibrationSettings().torque_limit_permille,
				help="permille of max torque",
			)
			p.add_argument(
				"--acceleration", type=int, default=40, help="servo acceleration register, 0-254 (lower is gentler)"
			)
		else:
			p.add_argument("--from", dest="source", type=Path, required=True, help="calibration file to write")
	return parser


def main(argv: list[str] | None = None) -> int:
	"""Entry point; returns the process exit code."""
	args = _parser().parse_args(argv)
	logging.basicConfig(
		level=logging.DEBUG if os.environ.get("ARMKIT_DEBUG") else logging.INFO,
		format="%(asctime)s %(levelname)s %(name)s: %(message)s",
	)
	if args.profile not in PROFILES:
		sys.exit(f"unknown profile {args.profile!r}; available: {', '.join(PROFILES)}")
	profile = PROFILES[args.profile]()
	out = sys.stdout
	settings = CalibrationSettings()
	frame = ModelFrame.load(args.frame) if getattr(args, "frame", None) else None
	if getattr(args, "table_area", None):
		profile = with_table_area(profile, _parse_area(args.table_area))
	if getattr(args, "table_clearance", None):
		profile = with_table_clearance(profile, args.table_clearance)

	if args.command == "frame" and args.directions:
		return _record_directions(args, profile, out)

	if args.command == "frame":
		if not args.pose:
			sys.exit("give --pose (a reference pose) or --directions")
		if args.pose not in REFERENCE_POSES:
			sys.exit(f"unknown reference pose {args.pose!r}; available: {', '.join(REFERENCE_POSES)}")
		pose, description = REFERENCE_POSES[args.pose]
		out.write(f"reference pose {args.pose}: {description}\n")
		if not args.go:
			out.write("dry run: nothing read or released (add --go)\n")
			return 0
		bus = _open_bus(args.port, profile, None)
		chain = [n for n in profile.robot.names if n in pose]
		if args.release:
			if not _ask(f"Hold the arm: torque on {', '.join(chain)} will be switched off so you can pose it by hand."):
				out.write("aborted: nothing released\n")
				return 1
			bus.set_torque(False, chain)
		try:
			if not _ask("Put the arm in the reference pose described above and keep it there."):
				out.write("aborted: nothing recorded\n")
				return 1
			if args.refine:
				captured = refine_frame(ModelFrame.load(args.refine), bus, profile, pose, reference=args.pose)
			else:
				captured = capture_frame(bus, profile, pose, reference=args.pose)
		finally:
			if args.release:
				bus.hold(chain)
		captured.save(args.out)
		for joint, offset in captured.offsets_deg.items():
			if joint not in captured.verified_directions:
				direction = "direction not checked yet"
			else:
				direction = "reversed" if captured.sign(joint) < 0 else "same direction"
			out.write(
				f"{joint}: model = {captured.sign(joint):+d} x stored-midpoint angle {offset:+.1f} deg ({direction})\n"
			)
		out.write(f"frame saved to {args.out}\n")
		return 0

	if args.command == "measure":
		order = [n for n in measurement_order(profile) if args.joints is None or n in args.joints]
		out.write(f"measuring, bottom-up: {', '.join(order)}\n")
		if args.preview:
			preview = preview_measure(_open_bus(args.port, profile, None), profile, frame=frame, joints=args.joints)
			out.write("preview on a simulated copy of the arm (nothing moved):\n")
			for line in preview.log:
				out.write(f"  {line}\n")
			out.write(preview.report.describe() + "\n")
			if preview.closest is not None:
				out.write(
					f"closest approach over the whole run: {preview.closest.distance_m * 1000:.0f} mm "
					f"({preview.closest.between}), with the table clearance included\n"
				)
			return 0 if preview.report.ok else 1
		if not args.go:
			out.write("dry run: nothing moved and no port was opened (add --go to measure on the arm)\n")
			return 0
		bus = _open_bus(args.port, profile, 40)
		args.backup.parent.mkdir(parents=True, exist_ok=True)
		bus.read_calibration().save(args.backup)
		out.write(f"stored calibration saved to {args.backup}\n")
		report = measure_all(
			bus,
			profile,
			clock=_clock(bus),
			confirm=_ask,
			progress=lambda m: out.write(m + "\n"),
			joints=args.joints,
			frame=frame,
		)
		out.write(report.describe() + "\n")
		if report.proposed is not None:
			report.proposed.save(args.out)
			out.write(f"proposed calibration saved to {args.out} (not stored in the servos)\n")
		return 0 if report.ok else 1

	if args.command == "move":
		targets = {}
		for item in args.set:
			joint, _, value = item.partition("=")
			if joint not in profile.robot.names:
				sys.exit(f"unknown joint {joint!r}")
			targets[joint] = float(value)
		bus = _open_bus(args.port, profile, None)
		start = current_pose(bus, profile, frame=frame)
		plan = plan_move(profile, start, targets, margin_m=args.margin)
		out.write("current pose: " + ", ".join(f"{j} {v:+.1f}" for j, v in start.items()) + "\n")
		out.write("target     : " + ", ".join(f"{j} {v:+.1f}" for j, v in targets.items()) + "\n")
		if not plan.ok:
			out.write(f"plan not ok: {plan.reason}\nREFUSED: nothing was moved\n")
			return 1
		for joint, value in targets.items():
			out.write(f"  {joint}: {start[joint]:+.1f} -> {value:+.1f} deg\n")
		closest = min((profile.collision.clearance(wp) for wp in plan.path), key=lambda c: c.distance_m)
		order = "direct" if not plan.order else "one joint at a time: " + ", ".join(plan.order)
		seconds = len(plan.path) * MoveLimits().dt_s
		out.write(
			f"plan ok: {len(plan.path)} waypoints ({order}), about {seconds:.0f} s; closest approach along the path "
			f"{closest.distance_m * 1000:.0f} mm ({closest.between}). The model knows the arm and the floor only: "
			"not a clamp, camera mounts or people.\n"
		)
		if not args.go:
			out.write("dry run: nothing moved (add --go to run the plan)\n")
			return 0
		result = run_move(
			bus,
			profile,
			plan,
			confirm=_ask,
			clock=_clock(bus),
			progress=lambda m: out.write(m + "\n"),
			torque_limit_permille=args.torque_limit,
			frame=frame,
		)
		out.write("done\n" if result.ok else f"STOPPED: {result.reason}\n")
		return 0 if result.ok else 1

	if args.command == "check":
		if args.joint not in {j.name for j in profile.joints}:
			sys.exit(f"unknown joint {args.joint!r}; available: {', '.join(j.name for j in profile.joints)}")
		if not args.go:
			out.write(
				f"dry run: would measure both travel ends of {args.joint} on {args.port}, changing nothing (add --go)\n"
			)
			return 0
		bus = _open_bus(args.port, profile, args.acceleration)
		args.backup.parent.mkdir(parents=True, exist_ok=True)
		bus.read_calibration().save(args.backup)
		out.write(f"stored calibration of every joint saved to {args.backup}\n")
		found = check_range(
			bus,
			args.joint,
			clock=_clock(bus),
			confirm=_ask,
			progress=lambda m: out.write(m + "\n"),
			torque_limit_permille=args.torque_limit,
			profile=profile,
			ends=args.ends,
			frame=frame,
		)
		if found.stored is not None:
			s = found.stored
			out.write(f"stored : offset {s.homing_offset}, range {s.range_min}..{s.range_max}\n")
		for label, value, diff in (
			("lower", found.lower, found.lower_difference_ticks),
			("upper", found.upper, found.upper_difference_ticks),
		):
			text = (
				"not found"
				if value is None
				else f"{value:.0f} ({diff:+.0f} ticks = {diff / TICKS_PER_DEGREE:+.1f} deg vs stored)"
			)
			out.write(f"{label}  : {text}\n")
		for name, contacts in (("lower", found.lower_contacts), ("upper", found.upper_contacts)):
			for line in describe_contacts(name, contacts):
				out.write(line + "\n")
		for note in found.notes:
			out.write(f"NOTE: {note}\n")
		for issue in found.issues:
			out.write(f"ISSUE: {issue}\n")
		return 0 if found.ok else 1

	if args.command == "restore":
		calibration = Calibration.load(args.source)
		if not args.go:
			out.write(
				f"dry run: would release torque and write {args.source} to the servos of {profile.name} (add --go)\n"
			)
			return 0
		bus = _open_bus(args.port, profile, None)
		if not _ask("Torque will be released on every joint: the arm must rest on its stops or be held."):
			out.write("aborted: nothing changed\n")
			return 1
		bus.set_torque(False)
		bus.write_calibration(calibration)
		out.write("calibration written\n")
		return 0

	if args.command == "run":
		settings = CalibrationSettings(torque_limit_permille=args.torque_limit)
	plan = plan_calibration(profile, settings, getattr(args, "only", None))
	out.write(plan.describe() + "\n")
	if args.command == "plan":
		return 0 if plan.ok else 1
	if not plan.ok:
		out.write("the plan has issues; nothing was run\n")
		return 1
	if not args.go:
		out.write("dry run: nothing moved and no port was opened (add --go to run the plan on the arm)\n")
		return 0

	bus = _open_bus(args.port, profile, args.acceleration)
	args.backup.parent.mkdir(parents=True, exist_ok=True)
	bus.read_calibration().save(args.backup)
	out.write(f"previous calibration saved to {args.backup}\n")
	result = run_calibration(
		bus,
		profile,
		settings=settings,
		plan=plan,
		clock=_clock(bus),
		confirm=_ask,
		progress=lambda m: out.write(m + "\n"),
	)
	for issue in result.issues:
		out.write(f"ISSUE: {issue}\n")
	if result.calibration is not None:
		result.calibration.save(args.out)
		out.write(f"new calibration saved to {args.out}\n")
	out.write(
		"done: calibration stored in the servos\n"
		if result.wrote
		else "NOT stored: see the issues above; previous calibration backup is " + str(args.backup) + "\n"
	)
	return 0 if result.ok else 1


if __name__ == "__main__":
	sys.exit(main())
