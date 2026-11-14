"""Automatic calibration of a servo arm: find every joint's travel ends by driving into them, safely.

:func:`plan_calibration` is the dry run. It uses the arm's collision model to plan, for each joint and each end of its
travel, where the other joints must be parked so the sweep cannot hit the arm itself or the table (several stages when
no single pose is clear all the way), and how the joint returns to its rest angle afterwards. It touches no hardware.
:func:`run_calibration` executes such a plan on a :class:`~armkit.servo.ServoBus`:

1. After the operator confirms the arm stands in its rest pose, the old calibration is read and kept, the servos'
   offsets and limits are reset (so nothing clips the search) and a temporary frame is written in which the rest pose
   reads where the model says it should. Joint angles are estimated from that until a joint has been measured.
2. Joint by joint, the others are parked (checked path, step-back on contact), the joint creeps into each end
   (:func:`~armkit.endstop.find_end`), then returns to its rest angle with its zero re-derived from the measured range.
3. With the arm back at rest and the operator's confirmation, torque goes off and the new offsets and ranges are
   stored: the measured range midpoint becomes the joint's zero (reading ``HALF_TURN``). Full-turn joints keep the
   homing offset they had, since there is no stop to measure a zero by. Any failure instead puts the previous
   calibration back. A servo fault stops everything where it is and is reported, never retried.

Estimates are never trusted blindly: pose planning allows ``unmeasured_uncertainty_deg`` of error for joints not yet
measured and ``measured_uncertainty_deg`` for the others, and the collision model vetoes any search step whose
estimated pose would collide.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass, field

from armkit.calibration import HALF_TURN, TICKS_PER_DEGREE, TICKS_PER_REVOLUTION, Calibration, JointCalibration
from armkit.endstop import EndKind, EndResult, SearchLimits, find_end
from armkit.guard import GuardLimits
from armkit.motion import MoveLimits, MoveResult, linear_path, run_path
from armkit.poses import SweepStage, plan_sweep, plan_transition
from armkit.profile import ArmProfile, JointSetup
from armkit.servo import Clock, ServoBus, ServoFaultError

logger = logging.getLogger(__name__)

TPD = TICKS_PER_DEGREE
_ENDS = {1: "upper", -1: "lower"}


@dataclass(frozen=True)
class CalibrationSettings:
	"""All tunables of a calibration run; the defaults are conservative starting values to be confirmed on first use.

	Parameters
	----------
	search, guard, move : SearchLimits, GuardLimits, MoveLimits
		End-search, contact-detection and path-following limits.
	torque_limit_permille : int
		Servo torque limit while the procedure runs (restored to ``restore_torque_limit_permille`` at the end).
	margins_m : tuple of float
		Clearance margins to plan with, strictest first; the first that yields a plan is used and recorded.
	unmeasured_uncertainty_deg, measured_uncertainty_deg : float
		Assumed error of a joint's estimated angle before and after its own calibration.
	slack_deg : float
		How far past the model's travel limit the sweep must be collision-free in the plan (the real stop is within a
		few degrees of it).
	search_overrun_deg : float
		Extra distance, beyond the planned sweep and the joint's own uncertainty, a search may travel before giving
		up on finding a stop. Runtime collision checks on the estimated pose still apply there.
	end_margin_ticks : int
		Recorded range is pulled in by this much at each end so commands at the limit do not press on the stop.
	plan_step_deg, resolution_deg : float
		Angular step of collision sampling and of stage-boundary bisection in the plan.
	max_stages : int
		Most parking poses one sweep may need.
	"""

	search: SearchLimits = field(default_factory=SearchLimits)
	guard: GuardLimits = field(default_factory=GuardLimits)
	move: MoveLimits = field(default_factory=MoveLimits)
	torque_limit_permille: int = 350
	restore_torque_limit_permille: int = 1000
	margins_m: tuple[float, ...] = (0.01, 0.005, 0.0)
	unmeasured_uncertainty_deg: float = 10.0
	measured_uncertainty_deg: float = 3.0
	slack_deg: float = 3.0
	search_overrun_deg: float = 10.0
	end_margin_ticks: int = 20
	plan_step_deg: float = 5.0
	resolution_deg: float = 4.0
	max_stages: int = 4


@dataclass(frozen=True)
class EndPlan:
	"""Search of one travel end: the staged parking poses and the clearance margin they were planned with."""

	direction: int
	stages: tuple[SweepStage, ...]
	margin_m: float


@dataclass(frozen=True)
class JointPlan:
	"""Plan for one joint: its two end searches (nearest the rest pose first) and the staged return to rest."""

	name: str
	kind: str
	ends: tuple[EndPlan, ...] = ()
	return_stages: tuple[SweepStage, ...] = ()
	return_margin_m: float = 0.0


@dataclass(frozen=True)
class CalibrationPlan:
	"""Dry-run result: per-joint plans and every reason the run cannot go ahead."""

	joints: tuple[JointPlan, ...]
	issues: tuple[str, ...] = ()

	@property
	def ok(self) -> bool:
		"""True when every sweep of every joint has a collision-free plan."""
		return not self.issues

	def describe(self) -> str:
		"""Human-readable summary of the plan."""
		lines = []
		for jp in self.joints:
			if jp.kind == "full_turn":
				lines.append(f"{jp.name}: full turn, range 0..4095, no motion")
				continue
			for end in jp.ends:
				poses = " -> ".join(
					f"[{', '.join(f'{k} {v:+.0f}' for k, v in s.pose.angles_deg.items())}] over {s.span_deg[0]:+.0f}..{s.span_deg[1]:+.0f}"
					for s in end.stages
				)
				lines.append(
					f"{jp.name}: {_ENDS[end.direction]} end, margin {end.margin_m * 1000:.0f} mm, park {poses}"
				)
		lines.extend(f"ISSUE: {issue}" for issue in self.issues)
		return "\n".join(lines)


def _plan_sweep(
	profile: ArmProfile,
	setup: JointSetup,
	est: Mapping[str, float],
	unc: Mapping[str, float],
	toward: float,
	settings: CalibrationSettings,
) -> tuple[list[SweepStage], float] | None:
	for margin in settings.margins_m:
		stages = plan_sweep(
			profile.collision,
			setup.name,
			current=est,
			toward_deg=toward,
			behind_deg=unc[setup.name],
			max_stages=settings.max_stages,
			resolution_deg=settings.resolution_deg,
			preferred=setup.preferred_poses,
			vary=setup.park_joints,
			grid_points=7,
			step_deg=settings.plan_step_deg,
			margin_m=margin,
			uncertainty_deg={k: v for k, v in unc.items() if k != setup.name},
		)
		if stages is not None:
			return stages, margin
	return None


def _check_only(profile: ArmProfile, only: Collection[str] | None) -> None:
	unknown = sorted(set(only or ()) - {j.name for j in profile.joints})
	if unknown:
		raise ValueError(
			f"unknown joint(s) {', '.join(unknown)}; the profile has {', '.join(j.name for j in profile.joints)}"
		)


def plan_calibration(
	profile: ArmProfile, settings: CalibrationSettings, only: Collection[str] | None = None
) -> CalibrationPlan:
	"""Plan every search sweep and return of ``profile`` against its collision model; see the module docstring.

	With ``only``, just those joints are planned (the others are marked ``kept``: not searched, calibration unchanged).
	"""
	_check_only(profile, only)
	est = profile.rest_pose
	unc = dict.fromkeys(est, settings.unmeasured_uncertainty_deg)
	plans: list[JointPlan] = []
	issues: list[str] = []
	for setup in profile.joints:
		if only is not None and setup.name not in only:
			plans.append(JointPlan(setup.name, "kept"))
			continue
		if setup.kind == "full_turn":
			plans.append(JointPlan(setup.name, "full_turn"))
			continue
		lo, hi = profile.travel(setup.name)
		upper_first = abs(est[setup.name] - hi) < abs(est[setup.name] - lo)
		ends: list[EndPlan] = []
		for direction in (1, -1) if upper_first else (-1, 1):
			toward = hi + settings.slack_deg if direction > 0 else lo - settings.slack_deg
			planned = _plan_sweep(profile, setup, est, unc, toward, settings)
			if planned is None:
				issues.append(
					f"{setup.name}: the {_ENDS[direction]} end cannot be searched automatically: no collision-free "
					f"parking pose for the other joints (margins tried: {', '.join(f'{m * 1000:.0f} mm' for m in settings.margins_m)})"
				)
			else:
				ends.append(EndPlan(direction, tuple(planned[0]), planned[1]))
			est[setup.name] = hi if direction > 0 else lo
		unc[setup.name] = settings.measured_uncertainty_deg
		returned = _plan_sweep(profile, setup, est, unc, setup.rest_deg, settings)
		if returned is None:
			issues.append(f"{setup.name}: no collision-free way to return to its rest angle after the search")
			plans.append(JointPlan(setup.name, "limited", tuple(ends)))
		else:
			plans.append(JointPlan(setup.name, "limited", tuple(ends), tuple(returned[0]), returned[1]))
		est[setup.name] = setup.rest_deg
	return CalibrationPlan(tuple(plans), tuple(issues))


@dataclass(frozen=True)
class JointOutcome:
	"""What happened to one joint: ``status`` is ``measured``, ``full_turn``, ``kept`` or ``failed``, plus raw ends and contacts."""

	status: str
	lower: float | None = None
	upper: float | None = None
	contacts: int = 0
	notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class CalibrationRun:
	"""Result of :func:`run_calibration`.

	``calibration`` is the new calibration when everything was measured (``None`` otherwise); ``wrote`` says whether
	the servos now hold it; ``previous`` is the calibration they held before; ``at_rest`` whether the arm ended at rest.
	"""

	ok: bool
	calibration: Calibration | None
	previous: Calibration | None
	joints: dict[str, JointOutcome]
	issues: tuple[str, ...]
	wrote: bool = False
	at_rest: bool = False


def _wrap_offset(value: float) -> int:
	v = round(value) % TICKS_PER_REVOLUTION
	return v - TICKS_PER_REVOLUTION if v > TICKS_PER_REVOLUTION // 2 else v


class _Runner:
	def __init__(
		self,
		bus: ServoBus,
		profile: ArmProfile,
		settings: CalibrationSettings,
		clock: Clock,
		confirm: Callable[[str], bool],
		progress: Callable[[str], None],
	) -> None:
		self.bus, self.profile, self.settings, self.clock = bus, profile, settings, clock
		self.confirm, self.progress = confirm, progress
		self.issues: list[str] = []
		self.zero: dict[str, float] = {}
		self.temp_offset: dict[str, int] = {}
		self.unc = dict.fromkeys(profile.rest_pose, settings.unmeasured_uncertainty_deg)
		self.ends: dict[str, dict[int, EndResult]] = {}
		self.contacts: dict[str, int] = {}

	# ---- estimates -----------------------------------------------------------------------------------------------
	def deg(self, joint: str, reading: float) -> float:
		return (reading - self.zero[joint]) / TPD

	def ticks(self, joint: str, deg: float) -> int:
		return round(self.zero[joint] + deg * TPD)

	def estimate(self) -> dict[str, float]:
		return {j: self.deg(j, r) for j, r in self.bus.read_positions().items()}

	# ---- motion --------------------------------------------------------------------------------------------------
	def _play(self, path: list[dict[str, int]]) -> MoveResult:
		result = run_path(
			self.bus,
			path,
			start=self.bus.read_positions(),
			limits=self.settings.move,
			guard=self.settings.guard,
			clock=self.clock,
		)
		for event in result.events:
			self.progress(f"contact while moving ({event.kind.value}): stepped back")
		return result

	def move_joint(self, joint: str, to_deg: float) -> MoveResult:
		start = self.bus.read_positions()
		path = linear_path(
			{joint: start[joint]}, {joint: self.ticks(joint, to_deg)}, step_ticks=self.settings.move.step_ticks
		)
		return self._play(path)

	def park(self, pose: Mapping[str, float], margin: float) -> MoveResult:
		est = self.estimate()
		plan = plan_transition(
			self.profile.collision,
			est,
			{**est, **pose},
			step_deg=self.settings.move.speed_deg_s * self.settings.move.dt_s,
			margin_m=margin,
		)
		if not plan.ok:
			return MoveResult(False, plan.reason)
		moving = [j for j in pose if abs(pose[j] - est[j]) > 0.05]
		start = self.bus.read_positions()
		path = [{j: self.ticks(j, wp[j]) for j in moving} for wp in plan.path] if moving else []
		if path:
			path = linear_path(start, path[0], step_ticks=self.settings.move.step_ticks) + path[1:]
		return self._play(path)

	def _collision_veto(self, joint: str, others: Mapping[str, float]) -> Callable[[float], bool]:
		"""Predicate for :func:`~armkit.endstop.find_end`: True where the estimated pose would collide."""
		collision = self.profile.collision

		def veto(position: float) -> bool:
			return not collision.is_clear({**others, joint: self.deg(joint, position)})

		return veto

	def stage_sweep(
		self, joint: str, stages: tuple[SweepStage, ...], margin: float, search: int | None
	) -> EndResult | None:
		"""Run stages: park, then either search for an end (``search`` = direction) or just travel to the stage end."""
		for i, stage in enumerate(stages):
			parked = self.park(stage.pose.angles_deg, margin)
			if not parked.ok:
				raise _CalibrationError(f"{joint}: could not reach the parking pose for its sweep ({parked.reason})")
			target = stage.span_deg[1]
			if search is None:
				moved = self.move_joint(joint, target)
				if not moved.ok:
					raise _CalibrationError(f"{joint}: blocked while returning to its rest angle ({moved.reason})")
				continue
			here = self.deg(joint, self.bus.read_sample(joint).position)
			others = {k: v for k, v in self.estimate().items() if k != joint}
			result = find_end(
				self.bus,
				joint,
				search,
				travel_ticks=(abs(target - here) + self.unc[joint] + self.settings.search_overrun_deg) * TPD,
				limits=self.settings.search,
				guard=self.settings.guard,
				clock=self.clock,
				stop_at=self._collision_veto(joint, others),
			)
			self.contacts[joint] = self.contacts.get(joint, 0) + len(result.contacts)
			if result.found or result.kind is not EndKind.TRAVEL_CAP or i == len(stages) - 1:
				return result
		return None

	# ---- the procedure -------------------------------------------------------------------------------------------
	def frame_setup(self) -> None:
		bus, settings = self.bus, self.settings
		bus.reset_calibration()
		rest = bus.read_positions()
		temp = {}
		for setup in self.profile.joints:
			zero_raw = rest[setup.name] - setup.rest_deg * TPD
			self.temp_offset[setup.name] = _wrap_offset(zero_raw - HALF_TURN)
			temp[setup.name] = JointCalibration(
				setup.servo_id, 0, self.temp_offset[setup.name], 0, TICKS_PER_REVOLUTION - 1
			)
		bus.write_calibration(Calibration(temp))
		after = bus.read_positions()
		for setup in self.profile.joints:
			expected = HALF_TURN + setup.rest_deg * TPD
			if abs(after[setup.name] - expected) > 4:
				raise _CalibrationError(
					f"{setup.name}: homing offset did not take (reads {after[setup.name]}, expected {expected:.0f})"
				)
			self.zero[setup.name] = HALF_TURN
		bus.set_torque_limit(settings.torque_limit_permille)
		bus.hold()

	def calibrate_joint(self, plan: JointPlan, setup: JointSetup) -> JointOutcome:
		results: dict[int, EndResult] = {}
		for end in plan.ends:
			self.progress(f"{setup.name}: searching the {_ENDS[end.direction]} end")
			result = self.stage_sweep(setup.name, end.stages, end.margin_m, end.direction)
			if result is None or not result.found:
				kind = "no result" if result is None else result.kind.value
				self.issues.append(f"{setup.name}: {_ENDS[end.direction]} end not found ({kind})")
				continue
			if result.kind is EndKind.UNCONFIRMED:
				self.issues.append(f"{setup.name}: {_ENDS[end.direction]} end not confirmed by repeated contact")
			results[end.direction] = result
		self.ends[setup.name] = results
		if len(results) < 2:
			return JointOutcome("failed", contacts=self.contacts.get(setup.name, 0))
		lower, upper = results[-1].position, results[1].position
		self.zero[setup.name] = (lower + upper) / 2
		self.unc[setup.name] = self.settings.measured_uncertainty_deg
		self.progress(f"{setup.name}: range {lower:.0f}..{upper:.0f}, returning to rest")
		self.stage_sweep(setup.name, plan.return_stages, plan.return_margin_m, None)
		notes = tuple(e.kind.value for e in results.values() if e.kind is not EndKind.HARD_STOP)
		return JointOutcome("measured", lower, upper, self.contacts.get(setup.name, 0), notes)

	def go_to_rest(self) -> bool:
		est = self.estimate()
		rest = self.profile.rest_pose
		chain = {n: rest[n] for n in self.profile.robot.names}
		plan = plan_transition(
			self.profile.collision,
			est,
			{**est, **chain},
			step_deg=self.settings.move.speed_deg_s * self.settings.move.dt_s,
		)
		if not plan.ok:
			self.issues.append(f"could not return the arm to its rest pose ({plan.reason})")
			return False
		start = self.bus.read_positions()
		path = [{j: self.ticks(j, wp[j]) for j in chain} for wp in plan.path]
		if not self._play(linear_path(start, path[0], step_ticks=self.settings.move.step_ticks) + path[1:]).ok:
			self.issues.append("blocked while returning the arm to its rest pose")
			return False
		for setup in self.profile.joints:
			if setup.name not in chain and not self.move_joint(setup.name, setup.rest_deg).ok:
				self.issues.append(f"{setup.name}: blocked while returning to rest")
				return False
		return True

	def build(self, outcomes: dict[str, JointOutcome], previous: Calibration) -> Calibration:
		joints = {}
		for setup in self.profile.joints:
			offset = self.temp_offset[setup.name]
			out = outcomes[setup.name]
			if out.status == "kept":
				joints[setup.name] = previous[setup.name]
				continue
			if setup.kind == "full_turn":
				# no stop to measure the zero by: keep the one the servo already has, falling back to the rest-pose frame
				kept = previous[setup.name].homing_offset if setup.name in previous else offset
				joints[setup.name] = JointCalibration(setup.servo_id, 0, kept, 0, TICKS_PER_REVOLUTION - 1)
				continue
			shift = round((out.lower + out.upper) / 2) - HALF_TURN
			m = self.settings.end_margin_ticks
			joints[setup.name] = JointCalibration(
				setup.servo_id,
				0,
				_wrap_offset(offset + shift),
				max(0, round(out.lower + m - shift)),
				min(TICKS_PER_REVOLUTION - 1, round(out.upper - m - shift)),
			)
		return Calibration(joints)


class _CalibrationError(Exception):
	"""A step of the run failed in a way that ends the calibration but leaves the arm controllable."""


def run_calibration(
	bus: ServoBus,
	profile: ArmProfile,
	*,
	settings: CalibrationSettings | None = None,
	plan: CalibrationPlan | None = None,
	only: Collection[str] | None = None,
	clock: Clock,
	confirm: Callable[[str], bool],
	progress: Callable[[str], None] | None = None,
) -> CalibrationRun:
	"""Calibrate the arm on ``bus``; see the module docstring for the sequence and its safeguards.

	Parameters
	----------
	bus : ServoBus
		The arm's servos.
	profile : ArmProfile
		Model, collision shapes and joint setup.
	settings : CalibrationSettings, optional
		Tunables; defaults are conservative.
	plan : CalibrationPlan, optional
		A plan made earlier (from :func:`plan_calibration`); made here when omitted. A plan with issues is refused
		before anything is touched.
	only : collection of str, optional
		Calibrate just these joints; the others keep their previous calibration (a good way to try a first run).
		Ignored when ``plan`` is given (the plan already says which joints are covered).
	clock : Clock
		Time source and delay (``RealClock`` on hardware, the simulated bus in tests).
	confirm : callable
		Asked (with a message) before the arm is reset and again before torque is released to store the result;
		returning False aborts. Nothing moves or is written before the first confirmation.
	progress : callable, optional
		Receives short status lines.
	"""
	settings = settings or CalibrationSettings()
	progress = progress or (lambda message: logger.info("%s", message))
	plan = plan or plan_calibration(profile, settings, only)
	if not plan.ok:
		return CalibrationRun(False, None, None, {}, plan.issues)
	if not confirm(
		"The arm must be resting in its documented rest pose, supported and clear of people and cables. "
		"Its servo calibration will be reset (torque off) and the arm will then move on its own, slowly."
	):
		return CalibrationRun(False, None, None, {}, ("not confirmed: nothing was changed",))

	runner = _Runner(bus, profile, settings, clock, confirm, progress)
	previous = bus.read_calibration()
	outcomes: dict[str, JointOutcome] = {}
	try:
		runner.frame_setup()
		for jp, setup in zip(plan.joints, profile.joints, strict=True):
			if jp.kind in ("full_turn", "kept"):
				outcomes[setup.name] = JointOutcome(jp.kind)
				continue
			outcomes[setup.name] = runner.calibrate_joint(jp, setup)
	except ServoFaultError as fault:
		message = (
			f"servo fault: {fault}. Stopped where it is, torque left on, nothing more written. The servos may hold a "
			"temporary calibration: return the arm to its rest pose and restore the previous calibration."
		)
		return CalibrationRun(False, None, previous, outcomes, (*runner.issues, message))
	except _CalibrationError as failure:
		runner.issues.append(str(failure))
	except KeyboardInterrupt:
		bus.hold()
		runner.issues.append(
			"interrupted: holding position; the servos may hold a temporary calibration, restore the previous one"
		)
		return CalibrationRun(False, None, previous, outcomes, tuple(runner.issues))

	complete = (
		not runner.issues
		and all(o.status != "failed" for o in outcomes.values())
		and len(outcomes) == len(profile.joints)
	)
	calibration = runner.build(outcomes, previous) if complete else None
	at_rest = runner.go_to_rest()
	if not at_rest:
		runner.issues.append(
			"the arm is not at rest, so no calibration was written: bring it to rest and restore the previous one"
		)
		return CalibrationRun(
			False, calibration if complete else None, previous, outcomes, tuple(runner.issues), False, False
		)
	target = calibration if calibration is not None else previous
	if not confirm(
		"The arm is back at rest. Torque will now be released to store the "
		+ ("new" if complete else "previous")
		+ " calibration."
	):
		runner.issues.append(
			"not confirmed: torque left on; the servos hold a temporary calibration, restore the previous one"
		)
		return CalibrationRun(False, calibration, previous, outcomes, tuple(runner.issues), False, True)
	bus.set_torque(False)
	bus.write_calibration(target)
	bus.set_torque_limit(settings.restore_torque_limit_permille)
	return CalibrationRun(complete, calibration, previous, outcomes, tuple(runner.issues), complete, True)
