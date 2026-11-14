"""Find a joint's travel end by creeping into it, stepping back on contact, and confirming it.

The joint is driven in one direction with a *leashed* goal: the goal advances at a fixed slow speed but never gets
more than ``lead_deg`` (plus the joint's own measured droop under load, when that works against the travel) ahead of
the shaft, so what pushes on an obstruction is bounded by the servo's gain times that
lead (and by the torque limit the caller sets), however long the contact lasts. Every sample goes through a
:class:`~armkit.guard.ContactGuard`. When it fires, the joint steps back ``backoff_deg`` and approaches again, slower.
An end counts as found (:attr:`EndKind.HARD_STOP`) when two contacts agree within ``confirm_tolerance_deg``. A contact
that does not repeat (a hand, a cable, a loose part that moved) is not an error: the search backs off and goes on,
and after ``max_contacts`` it settles for the most conservative contact seen (:attr:`EndKind.UNCONFIRMED`) so the
caller can carry on and flag it.

Searches also end without contact: after ``travel_ticks`` of travel (no stop where one was expected), when
``stop_at`` says the collision model forbids going further, at the encoder seam (goal registers cannot wrap), or
when ``max_duration_s`` runs out (a joint that no longer follows its goal).
Only a servo fault (error flags, over-temperature) raises, and it is never retried here.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from enum import StrEnum

from armkit.calibration import TICKS_PER_DEGREE, TICKS_PER_REVOLUTION
from armkit.guard import Contact, ContactGuard, GuardLimits
from armkit.servo import Clock, ServoBus, Unwrapper, check_servo

logger = logging.getLogger(__name__)


class EndKind(StrEnum):
	"""How a search ended."""

	HARD_STOP = "hard stop, contact confirmed"
	UNCONFIRMED = "contacts did not repeat; most conservative one used"
	TRAVEL_CAP = "no contact within the allowed travel"
	MODEL_LIMIT = "the collision model forbids going further"
	SEAM = "encoder seam reached"
	TIMEOUT = "search ran out of time"
	NO_PROGRESS = "held at the longest leash without moving and without a contact load (a servo limit, or too heavy)"


@dataclass(frozen=True)
class SearchLimits:
	"""Speeds, distances and fault limits of an end search.

	Parameters
	----------
	speed_deg_s : float
		Creep speed of the goal on the first approach.
	lead_deg : float
		Largest distance the goal may be ahead of the shaft (the leash).
	backoff_deg : float
		How far to step back from a contact.
	max_contacts : int
		Contacts after which an unconfirmed end is accepted.
	confirm_tolerance_deg : float
		Two contacts closer than this confirm an end.
	retry_speed_factor : float
		Speed multiplier applied for each further approach.
	dt_s : float
		Sample and command period.
	settle_s : float
		Longest wait for a step back to complete.
	max_temperature_c : int
		Servo temperature at which the search raises :class:`~armkit.servo.ServoFaultError`.
	max_lead_deg, lead_step_deg : float
		How far the leash may grow, and by how much at a time, while a loaded joint is held at the leash without moving
		and without a contact load (the servo needs more error to overcome weight and friction).
	seam_margin_ticks : int
		Distance kept from the 0 / 4095 seam of the encoder.
	max_duration_s : float
		Longest a single search may take; a joint that stops following its goal without load ends it here.
	"""

	speed_deg_s: float = 8.0
	lead_deg: float = 3.0
	backoff_deg: float = 4.0
	max_contacts: int = 3
	confirm_tolerance_deg: float = 2.0
	retry_speed_factor: float = 0.5
	dt_s: float = 0.05
	settle_s: float = 0.5
	max_temperature_c: int = 65
	seam_margin_ticks: int = 60
	max_lead_deg: float = 12.0
	lead_step_deg: float = 1.0
	max_duration_s: float = 180.0


@dataclass(frozen=True)
class EndResult:
	"""Outcome of :func:`find_end`.

	``position`` is the end (or where the search stopped) in unwrapped ticks relative to the encoder reading the
	search started from; ``contacts`` lists every contact in order.
	"""

	direction: int
	position: float
	kind: EndKind
	contacts: tuple[Contact, ...] = field(default=())

	@property
	def found(self) -> bool:
		"""True when the position is a contact rather than only the place the search stopped."""
		return self.kind in (EndKind.HARD_STOP, EndKind.UNCONFIRMED)


def find_end(
	bus: ServoBus,
	joint: str,
	direction: int,
	*,
	travel_ticks: float,
	limits: SearchLimits,
	guard: GuardLimits,
	clock: Clock,
	stop_at: Callable[[float], bool] | None = None,
) -> EndResult:
	"""Creep ``joint`` in ``direction`` (+1 or -1) until its end is found; see the module docstring.

	The joint must already hold its position with torque on, and the caller sets the torque limit. ``travel_ticks``
	caps the distance from where the search starts; ``stop_at(position)`` (unwrapped ticks) may veto further travel.
	"""
	sign = 1 if direction > 0 else -1
	tpd = TICKS_PER_DEGREE
	lead, backoff, tolerance = limits.lead_deg * tpd, limits.backoff_deg * tpd, limits.confirm_tolerance_deg * tpd
	# A loaded position servo settles short of the goal it holds. Measure that droop (held goal minus present position,
	# once the joint has settled) and lengthen the leash by the part that works against the direction of travel, or the
	# goal could never pull the joint forward and it would creep backwards instead.
	clock.sleep(limits.settle_s)
	resting = check_servo(bus, joint, limits.max_temperature_c)
	first = resting.position
	droop = bus.read_goal(joint) - first
	if abs(droop) > TICKS_PER_REVOLUTION // 2:  # across the encoder seam
		droop -= TICKS_PER_REVOLUTION if droop > 0 else -TICKS_PER_REVOLUTION
	against = max(0.0, sign * droop)
	lead += against
	max_lead = max(lead, limits.max_lead_deg * tpd)
	# a contact means the load rose clearly above what the joint carries at rest: a loaded joint that merely has not
	# started moving yet is given a longer leash instead (below)
	guard = replace(
		guard,
		stall_min_load_permille=max(
			guard.stall_min_load_permille,
			min(abs(resting.load) + guard.rise_permille, int(0.8 * bus.torque_limit(joint))),
		),
	)
	logger.debug("%s: held goal droop %d ticks, leash %.0f ticks, resting load %d", joint, droop, lead, resting.load)
	unwrap = Unwrapper(first)
	start = unwrap.value
	position = start
	deadline = clock.now() + limits.max_duration_s
	contacts: list[Contact] = []
	speed = limits.speed_deg_s * tpd

	def hold(at: float) -> None:
		bus.write_goals({joint: round(at)})

	def stopped(kind: EndKind) -> EndResult:
		hold(position)
		return EndResult(sign, position, kind, tuple(contacts))

	while True:
		goal = position + sign * against  # start from what the joint holds, not from where it droops to
		approach = ContactGuard(guard, sign)
		moved_at, moved_from = clock.now(), position
		while True:
			ahead = goal + sign * speed * limits.dt_s
			goal = position + sign * lead if (ahead - position) * sign > lead else ahead
			if not limits.seam_margin_ticks <= goal <= TICKS_PER_REVOLUTION - 1 - limits.seam_margin_ticks:
				return stopped(EndKind.SEAM)
			bus.write_goals({joint: round(goal)})
			clock.sleep(limits.dt_s)
			sample = check_servo(bus, joint, limits.max_temperature_c)
			position = unwrap(sample.position)
			contact = approach.update(clock.now(), position, sample.load, (goal - position) * sign > lead / 2)
			logger.debug(
				"%s %+d: goal %.0f position %.0f load %d lead %.0f%s",
				joint,
				sign,
				goal,
				position,
				sample.load,
				lead,
				f" CONTACT {contact.kind.value}" if contact else "",
			)
			if contact is not None:
				break
			if (position - moved_from) * sign >= guard.stall_progress_ticks:
				moved_at, moved_from = clock.now(), position
			elif clock.now() - moved_at >= guard.stall_window_s and (goal - position) * sign >= lead - 1:
				if lead >= max_lead:
					return stopped(EndKind.NO_PROGRESS)
				# held at the leash without moving and without a contact load: the servo needs more error to overcome
				# the joint's weight and friction, so let the goal lead a little further
				lead = min(lead + limits.lead_step_deg * tpd, max_lead)
				moved_at = clock.now()
			if (position - start) * sign >= travel_ticks:
				return stopped(EndKind.TRAVEL_CAP)
			if clock.now() > deadline:
				return stopped(EndKind.TIMEOUT)
			if stop_at is not None and stop_at(position):
				return stopped(EndKind.MODEL_LIMIT)
		contacts.append(contact)
		retreat = position - sign * backoff
		hold(retreat)
		waited = 0.0
		while waited < limits.settle_s:
			clock.sleep(limits.dt_s)
			waited += limits.dt_s
			position = unwrap(check_servo(bus, joint, limits.max_temperature_c).position)
			if abs(position - retreat) <= 4.0:
				break
		hold(position)
		if len(contacts) >= 2 and abs(contacts[-1].position - contacts[-2].position) <= tolerance:
			end = (contacts[-1].position + contacts[-2].position) / 2
			return EndResult(sign, end, EndKind.HARD_STOP, tuple(contacts))
		if len(contacts) >= limits.max_contacts:
			safest = min(contacts, key=lambda c: (c.position - start) * sign)
			return EndResult(sign, safest.position, EndKind.UNCONFIRMED, tuple(contacts))
		speed = max(speed * limits.retry_speed_factor, 0.25 * limits.speed_deg_s * tpd)
