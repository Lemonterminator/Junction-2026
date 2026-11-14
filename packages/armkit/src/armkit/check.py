"""Measure one joint's travel ends against its stored calibration, and change nothing.

:func:`check_range` is the cautious first run on real hardware. It works on a single joint, in the frame of the
calibration the servo already holds, so no other servo is read-modified, moved or re-framed. Only that joint's position
limits are widened for the search (otherwise the stored range would clip it) and put back afterwards, together with
its torque state, torque limit and position. Both ends are found with :func:`~armkit.endstop.find_end` (bounded push,
step back on contact, confirmation by a second contact) and reported next to the stored range. Nothing is stored.
"""

from __future__ import annotations

from collections.abc import Callable, Collection
from dataclasses import dataclass

from armkit.calibration import TICKS_PER_DEGREE, Calibration, JointCalibration
from armkit.endstop import EndKind, EndResult, SearchLimits, find_end
from armkit.frame import ModelFrame
from armkit.guard import Contact, GuardLimits
from armkit.motion import MoveLimits, linear_path, run_path
from armkit.poses import pose_variants, sweep_clearance
from armkit.profile import ArmProfile
from armkit.servo import Clock, ServoBus, ServoFaultError

_SLACK_DEG = 3.0
_GUARD_HEADROOM = 150
_WEIGHT_PERMILLE = 40
"""Holding load above which a joint counts as carrying weight: its torque must never go off."""
_LIMIT_GAP_TICKS = 8
"""How far short of the stored limit a weight-bearing search stops (the servo clamps its goal there)."""
"""Torque above twice the holding load kept for the contact guard, so a weight-bearing joint neither sags nor pins the guard."""
_MARGIN_M = 0.015
_TOLERANCE_M = 0.001
_OVERRUN_DEG = 25.0
"""How far past its stored end a search may go before it gives up on finding a stop."""
_POSE_UNCERTAINTY_DEG = 5.0
_SETTLE_S = 0.4
_OTHER = {"upper": "lower", "lower": "upper"}
"""Pause after EEPROM writes: the servos answer late (or not at all) for a moment afterwards."""


def _has_moved(bus: ServoBus, joint: str, home: int) -> bool:
	"""True unless the joint can be read and is still where the check found it (a failed read counts as moved)."""
	try:
		return abs(bus.read_sample(joint).position - home) > 6
	except ServoFaultError:
		return True


@dataclass(frozen=True)
class RangeCheck:
	"""Result of :func:`check_range`; ends are in the stored calibration's frame, ``None`` when not found.

	``*_difference_ticks`` is measured minus stored (positive means the stop is further up the scale).
	"""

	ok: bool
	stored: JointCalibration | None
	lower: float | None
	upper: float | None
	lower_difference_ticks: float | None
	upper_difference_ticks: float | None
	issues: tuple[str, ...]
	contacts: int = 0
	lower_contacts: tuple[Contact, ...] = ()
	upper_contacts: tuple[Contact, ...] = ()
	notes: tuple[str, ...] = ()
	"""Ends that could not be reached for a known reason (not a fault): the run is still ok."""


def check_range(
	bus: ServoBus,
	joint: str,
	*,
	clock: Clock,
	confirm: Callable[[str], bool],
	progress: Callable[[str], None] = lambda message: None,
	search: SearchLimits | None = None,
	guard: GuardLimits | None = None,
	move: MoveLimits | None = None,
	torque_limit_permille: int = 250,
	profile: ArmProfile | None = None,
	ends: Collection[str] = ("lower", "upper"),
	stored_calibration: Calibration | None = None,
	frame: ModelFrame | None = None,
) -> RangeCheck:
	"""Find ``joint``'s two travel ends and compare them with the calibration stored in its servo.

	The joint must be free to travel its whole range. ``confirm`` is asked once before anything is changed.

	With a ``profile`` and a joint of its kinematic chain, the pose of the whole arm is taken from the stored
	calibration (readings relative to each range midpoint) and the collision model is asked first whether the joint's
	sweep from that pose is clear: no closer to a collision than the arm already is (a rotation about the vertical axis
	never is), and at least 5 mm clear if it starts clearer than that. If not, nothing is moved or written and the issue
	says how far it would get. When it is clear, the search also stops wherever the model would see it get worse.
	A joint that carries weight (holding load above 40 permille) never has its torque switched off, since it would fall:
	its position limits stay as stored and its search stays inside them. Each other search goes at most 25 degrees
	past the stored end of the range. A joint that carries weight is searched at a
	torque limit of at least twice its holding load plus some headroom (never above its normal limit), so it cannot sag.

	``stored_calibration`` is the calibration already read (and trusted) by the caller; it is read here otherwise.

	``ends`` limits the check to the ``"lower"`` and/or ``"upper"`` end (for example the one end of a joint whose other
	sweep the collision model refuses from the current pose); the joint then never travels toward the other end.
	"""
	search, guard, move = search or SearchLimits(), guard or GuardLimits(), move or MoveLimits()
	calibration = stored_calibration or bus.read_calibration()
	stored = calibration[joint]
	veto = None
	clear_to: dict[int, float] = {}
	"""Per search direction (+1: readings up), the reading where the model stops calling the sweep clear."""
	if profile is not None and joint in profile.robot.names:
		if frame is None or not frame.verified or not frame.directions_known(profile.robot.names):
			return RangeCheck(
				False,
				stored,
				None,
				None,
				None,
				None,
				(
					f"{joint}: no measured model frame with checked joint directions, so the collision check could be "
					"judging a pose the arm is not in; nothing was moved (record one with 'armkit-calibrate frame')",
				),
			)
		positions = bus.read_positions()
		pose = {
			n: frame.to_model(n, calibration[n].to_degrees(positions[n]))
			for n in profile.robot.names
			if n in calibration
		}
		others = {n: v for n, v in pose.items() if n != joint}
		lo, hi = profile.travel(joint)
		now = min(
			profile.collision.clearance({**v, joint: pose[joint]}).distance_m
			for v in pose_variants(profile.collision, others, _POSE_UNCERTAINTY_DEG)
		)  # the same shifted poses the sweep is judged on, at the angle where it starts
		# the sweep is judged over everything the search may cover (the stored ends plus the overrun), which on a
		# real arm can reach past the model's joint travel: the runtime veto alone is no substitute for that check
		overrun = _OVERRUN_DEG * TICKS_PER_DEGREE
		search_ends = {
			"upper": frame.to_model(joint, stored.to_degrees(stored.range_max + overrun)),
			"lower": frame.to_model(joint, stored.to_degrees(stored.range_min - overrun)),
		}
		travel_ends = {"upper": hi + _SLACK_DEG, "lower": lo - _SLACK_DEG}
		angles = [pose[joint]]
		for name in ends:
			angles += [search_ends[name], travel_ends[name] if frame.sign(joint) > 0 else travel_ends[_OTHER[name]]]
		span = (min(angles), max(angles))
		sweep = sweep_clearance(
			profile.collision,
			joint,
			others=others,
			start_deg=pose[joint],
			span_deg=span,
			step_deg=2.0,
			margin_m=min(_MARGIN_M, now) - _TOLERANCE_M,
			uncertainty_deg=_POSE_UNCERTAINTY_DEG,
		)

		def ticks_at(model_deg: float) -> float:
			return stored.midpoint + frame.to_stored(joint, model_deg) * TICKS_PER_DEGREE

		# a sweep the model clears only part of the way is still searched if the clear part goes past the stored end
		# (only there is there anything new to measure); the search then stops where the clear part ends
		reach = sorted(ticks_at(a) for a in sweep.reach_deg)
		bound = sorted(ticks_at(a) for a in span)
		reach_by_dir, bound_by_dir = {1: reach[1], -1: reach[0]}, {1: bound[1], -1: bound[0]}

		def end_usable(name: str) -> bool:
			d = 1 if name == "upper" else -1
			stored_end = stored.range_max if d > 0 else stored.range_min
			whole_way = abs(reach_by_dir[d] - bound_by_dir[d]) < 1.0
			return whole_way or d * (reach_by_dir[d] - stored_end) >= _SLACK_DEG * TICKS_PER_DEGREE

		usable = sweep.clear or all(end_usable(name) for name in ends)
		if not sweep.clear and usable:
			clear_to = reach_by_dir
			progress(
				f"{joint}: the model calls the sweep clear only from {sweep.reach_deg[0]:.0f} to "
				f"{sweep.reach_deg[1]:.0f} deg; searching up to there (past the stored range)"
			)
		if not usable:
			worst = profile.collision.clearance(pose)
			return RangeCheck(
				False,
				stored,
				None,
				None,
				None,
				None,
				(
					f"{joint}: the model says its sweep from the current pose would collide: clear only from "
					f"{sweep.reach_deg[0]:.0f} to {sweep.reach_deg[1]:.0f} deg of {lo:.0f}..{hi:.0f} (closest pair now: "
					f"{worst.between}, {worst.distance_m * 1000:.0f} mm). Nothing was moved or written; park the other "
					"joints in a clear pose first.",
				),
			)

		def veto(position: float) -> bool:
			pose_here = {**others, joint: frame.to_model(joint, calibration[joint].to_degrees(position))}
			return profile.collision.clearance(pose_here).distance_m < min(0.0, now) - _TOLERANCE_M

	if not confirm(
		f"{joint} will move by itself through its whole range, slowly, at {torque_limit_permille} permille torque. "
		"Its stored calibration is left as it is. Keep clear of it."
	):
		return RangeCheck(False, stored, None, None, None, None, ("not confirmed: nothing was changed",))
	was_on, old_limit = bus.torque_enabled(joint), bus.torque_limit(joint)
	holding = max(abs(bus.read_sample(joint).load) for _ in range(5)) if was_on else 0
	# a joint of the arm chain may hold weight in some pose even when it reads none now (a balanced link): never switch
	# its torque off, and keep its normal limit (a lowered one lets a loaded link sag as soon as it moves; the leash and
	# the contact guard bound the push)
	weight_bearing = holding > _WEIGHT_PERMILLE or (profile is not None and joint in profile.robot.names)
	if weight_bearing:
		search_limit = old_limit
		progress(
			f"{joint}: holding load {holding} permille; it can carry weight, so its torque stays on at its normal limit "
			f"({old_limit})"
		)
	else:
		search_limit = min(old_limit, max(torque_limit_permille, 2 * holding + _GUARD_HEADROOM))
		progress(f"{joint}: holding load {holding} permille, searching at a torque limit of {search_limit}")
	home = bus.read_sample(joint).position
	issues: list[str] = []
	notes: list[str] = []
	found_ends: dict[int, EndResult] = {}
	live_widened = False
	try:
		if not weight_bearing:  # widening the limits needs torque off, which a loaded joint would fall through
			bus.set_torque(False, [joint])
			bus.write_calibration(
				Calibration({joint: JointCalibration(stored.id, stored.drive_mode, stored.homing_offset, 0, 4095)})
			)
			clock.sleep(_SETTLE_S)
		bus.set_torque_limit(search_limit, [joint])
		bus.hold([joint])
		if weight_bearing:
			# some servos take new limits while they hold: then the joint can go past its stored range without dropping
			live_widened = bus.write_limits(joint, 0, 4095)
			progress(
				f"{joint}: position limits widened with torque on; searching past the stored range"
				if live_widened
				else f"{joint}: the servo does not take new limits while holding; searching inside the stored range"
			)
		nearer_upper = abs(stored.range_max - home) < abs(home - stored.range_min)
		for direction in (1, -1) if nearer_upper else (-1, 1):
			if ("upper" if direction > 0 else "lower") not in ends:
				continue
			name = "upper" if direction > 0 else "lower"
			progress(f"{joint}: searching the {name} end")
			here = bus.read_sample(joint).position
			to_stored_end = (stored.range_max - here) if direction > 0 else (here - stored.range_min)
			if weight_bearing and not live_widened:
				cap = max(0.0, to_stored_end - _LIMIT_GAP_TICKS)
			else:
				cap = max(0.0, to_stored_end) + _OVERRUN_DEG * TICKS_PER_DEGREE
			capped_by_model = direction in clear_to and abs(clear_to[direction] - here) < cap
			if capped_by_model:
				cap = max(0.0, abs(clear_to[direction] - here))
			result = find_end(
				bus, joint, direction, travel_ticks=cap, limits=search, guard=guard, clock=clock, stop_at=veto
			)
			if result.found:
				found_ends[direction] = result
				progress(f"{joint}: {name} end found at {result.position:.0f} ({result.kind.value})")
				if result.kind is EndKind.UNCONFIRMED:
					issues.append(f"{joint}: {name} end not confirmed by repeated contact")
			elif capped_by_model and result.kind is EndKind.TRAVEL_CAP:
				issues.append(
					f"{joint}: {name} end NOT MEASURED: no stop up to {result.position:.0f}, where the collision model "
					"stops calling the sweep clear; the real end lies beyond it. Measure it from a pose that clears "
					"more of the sweep."
				)
			elif weight_bearing and not live_widened and result.kind is EndKind.TRAVEL_CAP:
				limit = stored.range_max if direction > 0 else stored.range_min
				# never accepted as it is: the stored limit is not a measurement, so the end stays open until measured
				issues.append(
					f"{joint}: {name} end NOT MEASURED: no stop inside the stored range (reached the stored limit "
					f"{limit} without contact), so the real end lies beyond it. This servo only takes new limits with "
					"torque off, which this joint cannot take while it carries weight: measure it another way (support "
					"the link, or from a pose where it hangs free)."
				)
			elif result.kind is EndKind.MODEL_LIMIT:
				notes.append(f"{joint}: {name} end not reached: {result.kind.value} (stopped at {result.position:.0f})")
			else:
				issues.append(f"{joint}: {name} end not found ({result.kind.value})")
		progress(f"{joint}: returning to where it started")
		bus.set_torque_limit(old_limit, [joint])  # the way back is the way it came: no need for the low search limit
		here = bus.read_sample(joint).position
		path = linear_path({joint: here}, {joint: home}, step_ticks=move.step_ticks)
		back = run_path(
			bus,
			path,
			start={joint: here},
			limits=move,
			guard=guard,
			clock=clock,
			loaded_joints={joint} if weight_bearing else (),
		)
		if not back.ok:
			issues.append(f"{joint}: could not return to its starting position ({back.reason})")
		try:
			if live_widened and not bus.write_limits(joint, stored.range_min, stored.range_max):
				raise RuntimeError("the servo did not take its stored limits back")
			if not weight_bearing:
				bus.set_torque(False, [joint])
				bus.write_calibration(Calibration({joint: stored}))
				clock.sleep(_SETTLE_S)
			bus.set_torque_limit(old_limit, [joint])
			if was_on:
				bus.hold([joint])
		except (ServoFaultError, RuntimeError) as problem:
			issues.append(
				f"could not restore {joint} automatically after measuring ({problem}); restore it from the saved "
				"calibration with 'armkit-calibrate restore'"
			)
	except ServoFaultError as fault:
		if _has_moved(bus, joint, home):
			issues.append(
				f"servo fault: {fault}. Stopped where it is; {joint}'s position limits may still be widened: "
				"restore them from the saved calibration with 'armkit-calibrate restore'."
			)
			return RangeCheck(False, stored, None, None, None, None, tuple(issues))
		# the joint has not moved: put the registers, torque limit and torque state back (no motion involved)
		issues.append(f"servo fault during setup: {fault}")
		try:
			if live_widened:
				bus.write_limits(joint, stored.range_min, stored.range_max)
			if not weight_bearing:
				bus.set_torque(False, [joint])
				bus.write_calibration(Calibration({joint: stored}))
				clock.sleep(_SETTLE_S)
			bus.set_torque_limit(old_limit, [joint])
			if was_on:
				bus.hold([joint])
			issues.append(f"{joint} restored to its stored calibration, torque state and torque limit; nothing moved")
		except ServoFaultError as again:
			issues.append(
				f"could not restore {joint} automatically ({again}); restore it from the saved calibration with "
				"'armkit-calibrate restore'"
			)
		return RangeCheck(False, stored, None, None, None, None, tuple(issues))
	lower = found_ends[-1].position if -1 in found_ends else None
	upper = found_ends[1].position if 1 in found_ends else None
	return RangeCheck(
		ok=not issues,
		stored=stored,
		lower=lower,
		upper=upper,
		lower_difference_ticks=None if lower is None else lower - stored.range_min,
		upper_difference_ticks=None if upper is None else upper - stored.range_max,
		issues=tuple(issues),
		notes=tuple(notes),
		contacts=sum(len(e.contacts) for e in found_ends.values()),
		lower_contacts=found_ends[-1].contacts if -1 in found_ends else (),
		upper_contacts=found_ends[1].contacts if 1 in found_ends else (),
	)


__all__ = ["RangeCheck", "check_range"]
