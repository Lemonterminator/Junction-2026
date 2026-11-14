"""Measure every joint's travel ends on an arm that is already calibrated, and propose a calibration; store nothing.

:func:`measure_all` is the whole-arm pipeline built from the pieces that are safe to run on the real arm:

1. One confirmation from the operator covers the run. The stored calibration is read; it is the frame for everything.
2. Joints are measured from the bottom up: the chain joints from the base outwards, then joints outside the chain
   (a gripper). Each end of each joint is measured separately. For a chain joint the collision model first plans where
   the other joints must be parked so the sweep toward that end is clear, in several stages when one parking pose is
   not clear all the way (:func:`~armkit.poses.plan_sweep`); the arm moves there along checked paths
   (:func:`~armkit.park.run_move`) and then :func:`~armkit.check.check_range` measures that one end. A joint that
   carries weight keeps its torque and is only searched inside its stored range; ends beyond it are reported, not guessed.
3. The arm returns to the pose it started in.
4. The result is a report and a *proposed* calibration: the stored homing offsets with the measured ranges (pulled in
   by ``end_margin_ticks``); an end that was not measured keeps its stored value. Nothing is written to the servos.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass

from armkit.calibration import Calibration, JointCalibration
from armkit.check import check_range
from armkit.collision import Clearance
from armkit.frame import ModelFrame
from armkit.park import current_pose, plan_move, run_move
from armkit.poses import plan_sweep
from armkit.profile import ArmProfile
from armkit.servo import Clock, ServoBus
from armkit.simulation import SimJoint, SimulatedBus

logger = logging.getLogger(__name__)

_SLACK_DEG = 3.0
_POSE_UNCERTAINTY_DEG = 5.0
_PREVIEW_STOP_INSET_TICKS = 60


@dataclass(frozen=True)
class JointMeasurement:
	"""Measured ends of one joint (stored-calibration frame; ``None`` where an end was not measured)."""

	stored: JointCalibration
	lower: float | None
	upper: float | None


@dataclass(frozen=True)
class MeasureReport:
	"""Outcome of :func:`measure_all`: per-joint measurements, the proposed calibration and every issue."""

	ok: bool
	joints: dict[str, JointMeasurement]
	proposed: Calibration | None
	issues: tuple[str, ...]
	notes: tuple[str, ...] = ()
	"""Ends left at their stored value for a known reason (unreachable on this setup); not failures."""

	def describe(self) -> str:
		"""Table of measured against stored ends, then the issues."""
		lines = []
		for name, m in self.joints.items():

			def end(value: float | None, stored: int) -> str:
				return "not measured" if value is None else f"{value:.0f} ({value - stored:+.0f} vs stored {stored})"

			lines.append(f"{name}: lower {end(m.lower, m.stored.range_min)}, upper {end(m.upper, m.stored.range_max)}")
		lines.extend(f"NOTE: {note}" for note in self.notes)
		lines.extend(f"ISSUE: {issue}" for issue in self.issues)
		return "\n".join(lines)


def measurement_order(profile: ArmProfile) -> list[str]:
	"""Joints with travel ends, from the base outwards: the kinematic chain first, then the joints outside it."""
	limited = {j.name for j in profile.joints if j.kind == "limited"}
	chain = [n for n in profile.robot.names if n in limited]
	return chain + [j.name for j in profile.joints if j.name in limited and j.name not in chain]


def measure_all(
	bus: ServoBus,
	profile: ArmProfile,
	*,
	clock: Clock,
	confirm: Callable[[str], bool],
	progress: Callable[[str], None] = lambda message: None,
	joints: Collection[str] | None = None,
	end_margin_ticks: int = 20,
	torque_limit_permille: int = 250,
	move_torque_limit_permille: int = 600,
	margins_m: tuple[float, ...] = (0.025, 0.015),
	frame: ModelFrame | None = None,
) -> MeasureReport:
	"""Measure the travel ends of ``joints`` (default: all, bottom-up); see the module docstring."""
	order = measurement_order(profile)
	if joints is not None:
		unknown = sorted(set(joints) - set(order))
		if unknown:
			raise ValueError(f"cannot measure {', '.join(unknown)}; measurable joints: {', '.join(order)}")
		order = [n for n in order if n in joints]
	if any(n in profile.robot.names for n in order) and (frame is None or not frame.verified):
		return MeasureReport(
			False,
			{},
			None,
			(
				"no measured model frame: the parking plans could describe poses the arm is not in, so nothing was "
				"moved (record one with 'armkit-calibrate frame')",
			),
		)
	if any(n in profile.robot.names for n in order) and not frame.directions_known(profile.robot.names):
		unchecked = sorted(set(profile.robot.names) - frame.verified_directions)
		return MeasureReport(
			False,
			{},
			None,
			(
				f"the model frame has not checked the direction of {', '.join(unchecked)}: a reversed joint would put the "
				"arm somewhere the plan does not expect, so nothing was moved (record a second pose with "
				"'armkit-calibrate frame --refine')",
			),
		)
	stored = bus.read_calibration()
	if not confirm(
		f"The arm will measure {', '.join(order)} one end at a time: it parks the other joints where the collision "
		"model says the sweep is clear, then drives the joint slowly into its stop, and returns to where it started. "
		"The model does not know about clamps, camera mounts or people. Nothing is stored. Keep clear."
	):
		return MeasureReport(False, {}, None, ("not confirmed: nothing was moved",))

	def yes(message: str) -> bool:
		return True

	start = current_pose(bus, profile, stored, frame)
	issues: list[str] = []
	notes: list[str] = []
	results: dict[str, JointMeasurement] = {}
	for joint in order:
		ends: dict[str, float | None] = {"lower": None, "upper": None}
		for end in ("lower", "upper"):
			if joint in profile.robot.names and not _park_for(
				bus,
				profile,
				stored,
				frame,
				joint,
				end,
				clock,
				progress,
				issues,
				notes,
				margins_m,
				move_torque_limit_permille,
			):
				continue
			found = check_range(
				bus,
				joint,
				clock=clock,
				confirm=yes,
				progress=progress,
				torque_limit_permille=torque_limit_permille,
				profile=profile,
				ends=(end,),
				stored_calibration=stored,
				frame=frame,
			)
			ends[end] = found.lower if end == "lower" else found.upper
			issues.extend(found.issues)
			notes.extend(found.notes)
		results[joint] = JointMeasurement(stored[joint], ends["lower"], ends["upper"])

	_return_to(bus, profile, stored, frame, start, clock, progress, issues, move_torque_limit_permille)
	after = bus.read_calibration()
	changed = [n for n in stored if after.get(n) != stored[n]]
	if changed:
		issues.append(
			f"the stored calibration of {', '.join(changed)} changed during the run; restore it from the backup "
			"with 'armkit-calibrate restore'"
		)
	proposed = propose(results, stored, margin_ticks=end_margin_ticks)
	return MeasureReport(not issues, results, proposed, tuple(issues), tuple(notes))


def propose(
	measurements: Mapping[str, JointMeasurement], stored: Mapping[str, JointCalibration], *, margin_ticks: int
) -> Calibration:
	"""The stored calibration with every measured end replaced by its measurement, pulled in by ``margin_ticks``.

	An end that could not be measured keeps its stored value; homing offsets are never changed.
	"""
	out = {}
	for name, cal in stored.items():
		m = measurements.get(name)
		lower = cal.range_min if m is None or m.lower is None else round(m.lower) + margin_ticks
		upper = cal.range_max if m is None or m.upper is None else round(m.upper) - margin_ticks
		out[name] = JointCalibration(cal.id, cal.drive_mode, cal.homing_offset, lower, upper)
	return Calibration(out)


def _park_for(
	bus: ServoBus,
	profile: ArmProfile,
	stored: Calibration,
	frame: ModelFrame | None,
	joint: str,
	end: str,
	clock: Clock,
	progress: Callable[[str], None],
	issues: list[str],
	notes: list[str],
	margins_m: tuple[float, ...],
	torque_limit: int,
) -> bool:
	"""Bring the other joints (and, for staged sweeps, the joint itself) to where the sweep toward ``end`` is clear."""
	pose = current_pose(bus, profile, stored, frame)
	lo, hi = profile.travel(joint)
	toward = lo - _SLACK_DEG if end == "lower" else hi + _SLACK_DEG
	setup = profile.setup(joint)
	others_unc = {n: _POSE_UNCERTAINTY_DEG for n in pose if n != joint}
	stages = None
	for margin in margins_m:
		stages = plan_sweep(
			profile.collision,
			joint,
			current=pose,
			toward_deg=toward,
			behind_deg=_POSE_UNCERTAINTY_DEG,
			max_stages=3,
			resolution_deg=4.0,
			preferred=setup.preferred_poses,
			vary=setup.park_joints,
			grid_points=7,
			step_deg=3.0,
			margin_m=margin,
			uncertainty_deg=others_unc,
		)
		if stages is not None:
			break
	if stages is None:
		notes.append(f"{joint}: no collision-free parking pose for a sweep to its {end} end; it keeps its stored value")
		return False
	for i, stage in enumerate(stages):
		targets = {n: v for n, v in stage.pose.angles_deg.items() if n in pose and abs(v - pose[n]) > 0.5}
		if targets and not _move(
			bus, profile, stored, frame, targets, clock, progress, issues, f"parking for {joint} {end}", torque_limit
		):
			return False
		pose = current_pose(bus, profile, stored, frame)
		if i < len(stages) - 1:  # walk the joint itself to where the next parking pose takes over
			if not _move(
				bus,
				profile,
				stored,
				frame,
				{joint: stage.span_deg[1]},
				clock,
				progress,
				issues,
				f"{joint} to stage {i + 2}",
				torque_limit,
			):
				return False
			pose = current_pose(bus, profile, stored, frame)
	return True


def _move(
	bus: ServoBus,
	profile: ArmProfile,
	stored: Calibration,
	frame: ModelFrame | None,
	targets: dict[str, float],
	clock: Clock,
	progress: Callable[[str], None],
	issues: list[str],
	what: str,
	torque_limit: int,
	margin_m: float = 0.015,
) -> bool:
	start = current_pose(bus, profile, stored, frame)
	plan = plan_move(profile, start, targets, margin_m=margin_m)
	if not plan.ok:
		issues.append(f"{what}: no collision-free path ({plan.reason})")
		return False
	progress(f"{what}: " + ", ".join(f"{n} {start[n]:+.0f} -> {v:+.0f}" for n, v in targets.items()))
	result = run_move(
		bus,
		profile,
		plan,
		confirm=lambda m: True,
		progress=progress,
		clock=clock,
		torque_limit_permille=torque_limit,
		calibration=stored,
		frame=frame,
	)
	if not result.ok and "did not settle" not in result.reason:
		issues.append(f"{what}: {result.reason}")
		return False
	return True


def _return_to(
	bus: ServoBus,
	profile: ArmProfile,
	stored: Calibration,
	frame: ModelFrame | None,
	start: dict[str, float],
	clock: Clock,
	progress: Callable[[str], None],
	issues: list[str],
	torque_limit: int,
) -> None:
	now = current_pose(bus, profile, stored, frame)
	targets = {n: v for n, v in start.items() if abs(v - now[n]) > 0.5}
	if not targets:
		return
	# the start pose was occupied already, so it may be as close to a collision as it was then
	margin = min(0.015, profile.collision.clearance(start).distance_m)
	_move(
		bus,
		profile,
		stored,
		frame,
		targets,
		clock,
		progress,
		issues,
		"returning to the start pose",
		torque_limit,
		margin_m=margin,
	)


@dataclass(frozen=True)
class MeasurePreview:
	"""A dry run of :func:`measure_all` on a simulated copy of the arm: its report, its log, and the closest approach
	to a collision (in the model) over the whole simulated run."""

	report: MeasureReport
	log: tuple[str, ...]
	closest: Clearance | None


def simulated_copy(bus: ServoBus, profile: ArmProfile) -> SimulatedBus:
	"""A simulated arm that starts where the real one is: same stored calibration, same readings, and its stops just
	inside the ends of the stored ranges (5 degrees, so the simulated search has room to press on them). Only reads the
	real bus."""
	stored = bus.read_calibration()
	positions = bus.read_positions()
	joints = {}
	for name, cal in stored.items():
		joint = SimJoint(
			id=cal.id,
			encoder=float(positions[name] + cal.homing_offset),
			stop_low=float(cal.range_min + cal.homing_offset + _PREVIEW_STOP_INSET_TICKS),
			stop_high=float(cal.range_max + cal.homing_offset - _PREVIEW_STOP_INSET_TICKS),
			offset=cal.homing_offset,
		)
		joint.limit_min, joint.limit_max = cal.range_min, cal.range_max
		joints[name] = joint
	sim = SimulatedBus(joints)
	sim.hold()
	return sim


def preview_measure(
	bus: ServoBus, profile: ArmProfile, *, frame: ModelFrame | None, joints: Collection[str] | None = None
) -> MeasurePreview:
	"""Run the measurement pipeline on :func:`simulated_copy` of ``bus`` and record what it would do."""
	sim = simulated_copy(bus, profile)
	log: list[str] = []
	closest: list[Clearance] = []
	stored = sim.read_calibration()
	view = frame or ModelFrame.identity(profile)
	original_sleep = sim.sleep

	def sleep(seconds: float) -> None:
		original_sleep(seconds)
		positions = sim.read_positions()
		pose = {n: view.to_model(n, stored[n].to_degrees(positions[n])) for n in profile.robot.names}
		closest.append(profile.collision.clearance(pose))

	sim.sleep = sleep  # type: ignore[method-assign]
	report = measure_all(
		sim, profile, clock=sim, confirm=lambda m: True, progress=log.append, joints=joints, frame=frame
	)
	worst = min(closest, key=lambda c: c.distance_m) if closest else None
	return MeasurePreview(report, tuple(log), worst)
