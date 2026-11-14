"""Slow, guarded execution of joint paths: the same step-back behaviour as the end search, for moves between poses.

:func:`run_path` plays a list of waypoints (goal ticks per joint, one per sample period) into a servo bus. Each
moving joint is watched by a :class:`~armkit.guard.ContactGuard`, and a joint that lags its command by more than
``max_lag_deg`` counts as a contact too. On a contact the arm does not give up: it holds, steps back ``backoff_deg``
from where the joint actually is, and plays the path again from there at a lower speed. After ``max_events``
contacts it steps back one last time and returns a failed :class:`MoveResult` holding its position; it never keeps
pushing and never retries on its own after that. Servo faults raise.
"""

from __future__ import annotations

import math
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass, field, replace

from armkit.calibration import TICKS_PER_DEGREE
from armkit.guard import Contact, ContactGuard, ContactKind, GuardLimits
from armkit.servo import Clock, ServoBus, check_servo

_LOADED_PERMILLE = 40


@dataclass(frozen=True)
class MoveLimits:
	"""Speed, tracking and step-back settings of :func:`run_path`.

	Parameters
	----------
	speed_deg_s : float
		Joint speed the path is meant to be played at (sets the sleep per waypoint together with ``dt_s``).
	max_lag_deg : float
		How far a joint may fall behind its command before that counts as a contact.
	backoff_deg : float
		How far to step back from a contact.
	max_events : int
		Contacts tolerated; the next one ends the move.
	retry_speed_factor : float
		Playback speed multiplier per contact so far.
	dt_s : float
		Waypoint period.
	settle_s : float
		Longest wait for a step back or the final approach.
	max_loaded_lag_deg : float
		Lag allowed for a joint that carries weight (resting load above 40 permille) before it counts as a contact.
	max_droop_deg : float
		Largest shortfall at the end of a move that is corrected once (a loaded servo's droop); a larger one is
		reported as not arrived.
	arrival_ticks : int
		A move counts as arrived when it ends within this many ticks of its goal after ``settle_s`` (servos have a
		deadband and hold less tightly at low torque).
	max_temperature_c : int
		Servo temperature that raises :class:`~armkit.servo.ServoFaultError`.
	"""

	speed_deg_s: float = 10.0
	max_lag_deg: float = 6.0
	backoff_deg: float = 3.0
	max_events: int = 3
	retry_speed_factor: float = 0.5
	dt_s: float = 0.05
	settle_s: float = 1.0
	max_temperature_c: int = 65
	arrival_ticks: int = 12
	max_loaded_lag_deg: float = 12.0
	max_droop_deg: float = 8.0

	@property
	def step_ticks(self) -> float:
		"""Joint travel per waypoint at the nominal speed."""
		return self.speed_deg_s * TICKS_PER_DEGREE * self.dt_s


@dataclass(frozen=True)
class MoveResult:
	"""Whether the path completed; on failure why. ``events`` lists every contact that made the arm step back."""

	ok: bool
	reason: str = ""
	events: tuple[Contact, ...] = field(default=())


def linear_path(start: Mapping[str, float], goal: Mapping[str, float], *, step_ticks: float) -> list[dict[str, int]]:
	"""Waypoints from ``start`` to ``goal`` (ticks per joint) with no joint moving more than ``step_ticks`` per step."""
	largest = max((abs(goal[j] - start[j]) for j in goal), default=0.0)
	n = max(1, math.ceil(largest / step_ticks - 1e-9)) if largest > 0 else 0
	path = [{j: round(start[j] + (goal[j] - start[j]) * k / n) for j in goal} for k in range(1, n + 1)]
	if path:
		path[-1] = {j: round(goal[j]) for j in goal}
	return path


def run_path(
	bus: ServoBus,
	path: Sequence[Mapping[str, int]],
	*,
	start: Mapping[str, int],
	limits: MoveLimits,
	guard: GuardLimits,
	clock: Clock,
	loaded_joints: Collection[str] = (),
) -> MoveResult:
	"""Play ``path`` from the pose ``start`` (ticks); see the module docstring for the step-back behaviour."""
	if not path:
		return MoveResult(True)
	tpd = TICKS_PER_DEGREE
	max_lag, backoff = limits.max_lag_deg * tpd, limits.backoff_deg * tpd
	# A joint that carries weight needs more error before its servo moves it, and its load sits high already: judge it
	# against its own resting load and give it more lag, or lifting it would look like a stall.
	joints = sorted({j for wp in path for j in wp})
	resting = {j: abs(check_servo(bus, j, limits.max_temperature_c).load) for j in joints}
	# a joint resting on a stop reads light until it lifts off, so the caller may name joints that can carry weight
	loaded = {j for j in joints if resting[j] > _LOADED_PERMILLE or j in loaded_joints}
	joint_guard = {
		j: replace(
			guard,
			stall_min_load_permille=max(
				guard.stall_min_load_permille, min(resting[j] + guard.rise_permille, int(0.8 * bus.torque_limit(j)))
			),
		)
		for j in joints
	}
	joint_lag = {j: max(max_lag, limits.max_loaded_lag_deg * tpd) if j in loaded else max_lag for j in joints}
	guards: dict[tuple[str, int], ContactGuard] = {}
	events: list[Contact] = []

	def previous(i: int) -> Mapping[str, int]:
		return path[i - 1] if i > 0 else start

	def hold(joints: Sequence[str]) -> dict[str, int]:
		present = {j: check_servo(bus, j, limits.max_temperature_c).position for j in joints}
		bus.write_goals(present)
		return present

	def step_back(i: int, joints: Sequence[str], present: Mapping[str, int]) -> int:
		"""Retreat to the last waypoint that is at least ``backoff`` behind the joints' present position."""
		lead = max(joints, key=lambda j: abs(path[i][j] - previous(i)[j]))
		sign = 1 if path[i][lead] >= previous(i)[lead] else -1
		k = i
		while k > 0 and not ((path[k - 1][lead] - present[lead]) * sign <= -backoff):
			k -= 1
		target = dict(path[k - 1]) if k > 0 else dict(start)
		bus.write_goals({j: target[j] for j in joints})
		waited = 0.0
		while waited < limits.settle_s:
			clock.sleep(limits.dt_s)
			waited += limits.dt_s
			if all(abs(check_servo(bus, j, limits.max_temperature_c).position - target[j]) <= 4 for j in joints):
				break
		hold(joints)
		return k

	i = 0
	while i < len(path):
		goals, before = path[i], previous(i)
		moving = [j for j in goals if goals[j] != before[j]]
		bus.write_goals(goals)
		clock.sleep(limits.dt_s / (limits.retry_speed_factor ** len(events)))
		contact = None
		for j in moving:
			sample = check_servo(bus, j, limits.max_temperature_c)
			direction = 1 if goals[j] > before[j] else -1
			lag = (goals[j] - sample.position) * direction
			key = (j, direction)
			if key not in guards:
				guards[key] = ContactGuard(joint_guard[j], direction)
			found = guards[key].update(clock.now(), sample.position, sample.load, lag > joint_lag[j] / 3)
			if found is None and lag > joint_lag[j]:
				found = Contact(ContactKind.LAG, sample.load, sample.position, clock.now())
			contact = contact or found
		if contact is None:
			i += 1
			continue
		events.append(contact)
		present = hold(moving)
		resume = step_back(i, moving, present)
		guards.clear()
		if len(events) > limits.max_events:
			return MoveResult(
				False, f"blocked at waypoint {i} of {len(path)} ({contact.kind.value}); holding position", tuple(events)
			)
		i = resume
	waited = 0.0
	final = path[-1]
	corrected = False
	while True:
		present = {j: check_servo(bus, j, limits.max_temperature_c).position for j in final}
		off = max(abs(present[j] - final[j]) for j in final)
		if off <= 3 or (waited >= limits.settle_s and off <= limits.arrival_ticks):
			return MoveResult(True, events=tuple(events))
		if waited >= limits.settle_s:
			# A loaded servo settles short of its goal; ask once for the shortfall on top, if it looks like droop
			# (bounded) and not like a joint that is held back by something.
			if not corrected and off <= limits.max_droop_deg * TICKS_PER_DEGREE:
				bus.write_goals({j: final[j] + (final[j] - present[j]) for j in final})
				corrected, waited = True, 0.0
				continue
			return MoveResult(False, f"did not settle on the final waypoint (still {off} ticks off)", tuple(events))
		clock.sleep(limits.dt_s)
		waited += limits.dt_s
