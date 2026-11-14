"""Pose planning against the collision model: sweep checks, clearance poses and collision-free transitions.

Calibrating one joint means driving it through its whole travel while the others stand still, so the others must be
parked where that sweep cannot hit the arm itself or the table. :func:`sweep_clearance` answers whether a sweep is
clear (and how far from the start it is), :func:`find_clearance_pose` looks for a parking pose of the other joints
with a clear sweep, and :func:`plan_transition` finds a speed-checked path into it, moving joints one at a time
when the direct path would pass too close.

Joint angles here are model degrees. During a calibration they are only estimates, which is what ``uncertainty_deg``
is for: every other joint is also tried offset by that much each way.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import permutations

import numpy as np

from armkit.collision import CollisionModel

_TOLERANCE_M = 1e-3


@dataclass(frozen=True)
class SweepCheck:
	"""Outcome of :func:`sweep_clearance`.

	``reach_deg`` is the contiguous clear interval around the start; ``clear`` is True when it spans the whole
	requested interval.
	"""

	clear: bool
	reach_deg: tuple[float, float]


@dataclass(frozen=True)
class ClearancePose:
	"""Where to park the joints other than the one being swept."""

	angles_deg: dict[str, float]


@dataclass(frozen=True)
class TransitionPlan:
	"""Waypoints from a start pose to a goal pose (every joint in each waypoint), or a refusal with its reason.

	``order`` is empty for a direct move, otherwise the sequence in which single joints move.
	"""

	ok: bool
	order: tuple[str, ...] = ()
	path: tuple[dict[str, float], ...] = ()
	reason: str = ""


Uncertainty = float | Mapping[str, float]


def pose_variants(
	collision: CollisionModel, others: Mapping[str, float], uncertainty_deg: Uncertainty
) -> list[dict[str, float]]:
	"""The nominal pose plus each joint shifted by its uncertainty either way, never beyond the joint's own limits."""
	out = [dict(others)]
	for name in others:
		u = uncertainty_deg.get(name, 0.0) if isinstance(uncertainty_deg, Mapping) else uncertainty_deg
		if u <= 0:
			continue
		lo, hi = collision.robot.limits_deg(name) if name in collision.robot.names else (-math.inf, math.inf)
		for sign in (-1.0, 1.0):
			shifted = min(max(others[name] + sign * u, lo), hi)
			if shifted != others[name]:
				out.append({**others, name: shifted})
	return out


def sweep_clearance(
	collision: CollisionModel,
	joint: str,
	*,
	others: Mapping[str, float],
	start_deg: float,
	span_deg: tuple[float, float],
	step_deg: float = 3.0,
	margin_m: float = 0.0,
	uncertainty_deg: Uncertainty = 0.0,
) -> SweepCheck:
	"""How far ``joint`` can swing from ``start_deg`` inside ``span_deg`` with the other joints parked at ``others``.

	A sample counts as clear when every gap exceeds ``margin_m`` for the nominal ``others`` and for each of them
	shifted by its ``uncertainty_deg`` (one number for all, or per joint) either way.
	"""
	lo, hi = span_deg
	variants = pose_variants(collision, others, uncertainty_deg)

	def clear(angle: float) -> bool:
		return all(collision.is_clear({**v, joint: angle}, margin_m) for v in variants)

	def walk(direction: float, bound: float) -> float:
		angle = start_deg
		if not clear(angle):
			return angle
		while angle != bound:
			nxt = min(angle + step_deg, bound) if direction > 0 else max(angle - step_deg, bound)
			if not clear(nxt):
				break
			angle = nxt
		return angle

	reach = (walk(-1.0, lo), walk(1.0, hi))
	return SweepCheck(reach[0] <= lo and reach[1] >= hi, reach)


def find_clearance_pose(
	collision: CollisionModel,
	joint: str,
	*,
	current: Mapping[str, float],
	span_deg: tuple[float, float],
	preferred: Sequence[Mapping[str, float]] = (),
	vary: Sequence[str] | None = None,
	grid_points: int = 5,
	step_deg: float = 3.0,
	margin_m: float = 0.0,
	uncertainty_deg: Uncertainty = 0.0,
) -> ClearancePose | None:
	"""A parking pose of the other joints from which ``joint`` can sweep ``span_deg`` without a collision.

	The ``current`` pose is tried first (no move is the best move), then the ``preferred`` poses (joints they omit stay
	at ``current``), then a grid over the ``vary`` joints'
	limits (2 degrees inside each; default every other joint) is searched nearest-to-``current`` first, so the transition into
	the pose stays short; joints not in ``vary`` stay at ``current``. Returns ``None`` when no candidate has a clear
	sweep.
	"""
	others = [n for n in collision.robot.names if n != joint]
	start = min(max(current[joint], span_deg[0]), span_deg[1])
	candidates = [
		{n: float(current[n]) for n in others},
		*({n: float(p.get(n, current[n])) for n in others} for p in preferred),
	]
	varied = [n for n in others if vary is None or n in vary]
	axes = [
		np.linspace(collision.robot.limits_deg(n)[0] + 2.0, collision.robot.limits_deg(n)[1] - 2.0, grid_points)
		for n in varied
	]
	combos = np.array(np.meshgrid(*axes)).reshape(len(varied), -1).T if varied else np.zeros((1, 0))
	grid = [
		{**{n: float(current[n]) for n in others}, **dict(zip(varied, (float(v) for v in combo), strict=True))}
		for combo in combos
	]
	grid.sort(key=lambda c: sum(abs(c[n] - current[n]) for n in others))
	for candidate in [*candidates, *grid]:
		check = sweep_clearance(
			collision,
			joint,
			others=candidate,
			start_deg=start,
			span_deg=span_deg,
			step_deg=step_deg,
			margin_m=margin_m,
			uncertainty_deg=uncertainty_deg,
		)
		if check.clear:
			return ClearancePose(candidate)
	return None


@dataclass(frozen=True)
class SweepStage:
	"""One leg of a staged sweep: park the other joints at ``pose``, then sweep over ``span_deg`` (start first)."""

	span_deg: tuple[float, float]
	pose: ClearancePose


def plan_sweep(
	collision: CollisionModel,
	joint: str,
	*,
	current: Mapping[str, float],
	toward_deg: float,
	behind_deg: float = 0.0,
	max_stages: int = 4,
	resolution_deg: float = 4.0,
	preferred: Sequence[Mapping[str, float]] = (),
	vary: Sequence[str] | None = None,
	grid_points: int = 5,
	step_deg: float = 3.0,
	margin_m: float = 0.0,
	uncertainty_deg: Uncertainty = 0.0,
) -> list[SweepStage] | None:
	"""Plan a sweep of ``joint`` from ``current[joint]`` toward ``toward_deg`` in as few parking poses as it takes.

	One parking pose is tried for the whole sweep. When none is clear, the sweep is cut at the farthest point one
	pose still covers (found by bisection to ``resolution_deg``) and the rest is planned from there, so the arm
	re-parks where both poses are clear. ``behind_deg`` extends each stage backwards past its start to allow for
	the joint's own position estimate being off. Returns the stages in order, or ``None`` when some stretch has no
	parking pose or more than ``max_stages`` would be needed.
	"""
	here = float(current[joint])
	sign = 1.0 if toward_deg >= here else -1.0
	park = {n: float(v) for n, v in current.items()}
	stages: list[SweepStage] = []

	def pose_for(start: float, end: float) -> ClearancePose | None:
		lo, hi = (start - behind_deg, end) if sign > 0 else (end, start + behind_deg)
		return find_clearance_pose(
			collision,
			joint,
			current={**park, joint: start},
			span_deg=(lo, hi),
			preferred=preferred,
			vary=vary,
			grid_points=grid_points,
			step_deg=step_deg,
			margin_m=margin_m,
			uncertainty_deg=uncertainty_deg,
		)

	while len(stages) < max_stages:
		whole = pose_for(here, toward_deg)
		if whole is not None:
			return [*stages, SweepStage((here, toward_deg), whole)]
		good, bad = here, toward_deg
		best = pose_for(here, here + sign * resolution_deg)
		if best is None:
			return None
		good = here + sign * resolution_deg
		while abs(bad - good) > resolution_deg:
			mid = (good + bad) / 2
			pose = pose_for(here, mid)
			if pose is None:
				bad = mid
			else:
				good, best = mid, pose
		stages.append(SweepStage((here, good), best))
		park = {**park, **best.angles_deg}
		here = good
	return None


def _segment(a: Mapping[str, float], b: Mapping[str, float], step_deg: float) -> list[dict[str, float]]:
	largest = max((abs(b[j] - a[j]) for j in b), default=0.0)
	n = max(1, math.ceil(largest / step_deg - 1e-9))
	return [{j: a[j] + (b[j] - a[j]) * k / n for j in b} for k in range(1, n + 1)]


def plan_transition(
	collision: CollisionModel,
	start: Mapping[str, float],
	goal: Mapping[str, float],
	*,
	step_deg: float = 3.0,
	margin_m: float = 0.0,
) -> TransitionPlan:
	"""Path from ``start`` to ``goal`` in steps of at most ``step_deg`` with every pose clear by ``margin_m``.

	The direct joint-space line is tried first, then every order of moving the changing joints one at a time. A pose
	may be no closer than the start pose already is (an arm resting folded touches itself by design), but the goal
	must meet that same bound.
	"""
	names = [n for n in collision.robot.names if n in start or n in goal]
	a = {n: float(start.get(n, goal.get(n, 0.0))) for n in names}
	b = {n: float(goal.get(n, a[n])) for n in names}
	allowed = min(margin_m, collision.clearance(a).distance_m) - _TOLERANCE_M
	if collision.clearance(b).distance_m < allowed:
		return TransitionPlan(
			False, reason="the goal pose is closer to a collision than the start pose or the margin allows"
		)
	moving = [n for n in names if abs(b[n] - a[n]) > 1e-9]
	if not moving:
		return TransitionPlan(True, path=(dict(b),))

	def attempt(order: tuple[str, ...]) -> list[dict[str, float]] | None:
		path: list[dict[str, float]] = []
		here = dict(a)
		for stage in order or (None,):
			target = dict(b) if stage is None else {**here, stage: b[stage]}
			path.extend(_segment(here, target, step_deg))
			here = target
		if any(collision.clearance(wp).distance_m < allowed for wp in path):
			return None
		path[-1] = dict(b)
		return path

	for order in ((), *permutations(moving)):
		path = attempt(order)
		if path is not None:
			return TransitionPlan(True, order=tuple(order), path=tuple(path))
	return TransitionPlan(
		False, reason=f"no collision-free route (tried the direct path and {math.factorial(len(moving))} joint orders)"
	)
