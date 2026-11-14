"""Contact detection from a servo's load readings: the signal to step back before something is pushed too hard.

:class:`ContactGuard` watches one joint while it is driven in one direction and reports a :class:`Contact` for

* a **rapid rise** of the load (it grew by ``rise_permille`` within ``rise_window_s`` and is itself meaningful),
* a **hard load** above ``hard_load_permille``, whatever the history,
* a **stall**: the joint is being commanded forward, carries some load and has not advanced.

A constant load (gravity on a lifted arm) or a slow ramp never counts as a rise, so the guard works the same
for joints that carry weight and joints that do not. Loads are the servo's 0.1 % of maximum torque units; the sign
(direction of the torque) is ignored. The guard only decides; stepping back is the caller's job.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import StrEnum

_EPS = 1e-6


class ContactKind(StrEnum):
	"""Why the guard fired."""

	RISE = "rapid load rise"
	HIGH = "load above the ceiling"
	STALL = "stalled while pushing"
	LAG = "lagging behind its command"


@dataclass(frozen=True)
class GuardLimits:
	"""Thresholds of :class:`ContactGuard`; loads in permille of the servo's maximum torque.

	Parameters
	----------
	rise_permille : int
		Load increase within ``rise_window_s`` that counts as a rapid rise.
	rise_window_s : float
		Time over which a rise is measured.
	min_load_permille : int
		A rapid rise only fires once the load itself reaches this.
	hard_load_permille : int
		Load that always fires.
	stall_window_s : float
		How long a joint may be commanded forward without advancing before it counts as stalled.
	stall_progress_ticks : float
		Advance over the stall window below which the joint counts as not advancing.
	stall_min_load_permille : int
		A stall only fires with at least this much load behind it (a joint that is merely idle carries none).
	"""

	rise_permille: int = 150
	rise_window_s: float = 0.25
	min_load_permille: int = 120
	hard_load_permille: int = 400
	stall_window_s: float = 0.3
	stall_progress_ticks: float = 2.0
	stall_min_load_permille: int = 80


@dataclass(frozen=True)
class Contact:
	"""A detected contact: why, the load and raw position at that sample, and when."""

	kind: ContactKind
	load: int
	position: float
	time_s: float


class ContactGuard:
	"""Contact detector for one joint travelling in ``direction`` (+1 or -1 along the position axis)."""

	def __init__(self, limits: GuardLimits, direction: int) -> None:
		self._limits = limits
		self._direction = 1 if direction > 0 else -1
		self._window = max(limits.rise_window_s, limits.stall_window_s) + _EPS
		self._samples: deque[tuple[float, float, int]] = deque()
		self._pushing_since: float | None = None

	def update(self, time_s: float, position: float, load: int, pushing: bool) -> Contact | None:
		"""Feed one sample; ``pushing`` says the joint is being commanded forward. Returns a contact or ``None``."""
		lim = self._limits
		magnitude = abs(load)
		self._samples.append((time_s, position * self._direction, magnitude))
		while time_s - self._samples[0][0] > self._window:
			self._samples.popleft()
		self._pushing_since = (time_s if self._pushing_since is None else self._pushing_since) if pushing else None

		def fired(kind: ContactKind) -> Contact:
			return Contact(kind, magnitude, position, time_s)

		if magnitude >= lim.hard_load_permille:
			return fired(ContactKind.HIGH)
		recent = [s for s in self._samples if time_s - s[0] <= lim.rise_window_s + _EPS]
		if magnitude >= lim.min_load_permille and magnitude - min(s[2] for s in recent) >= lim.rise_permille:
			return fired(ContactKind.RISE)
		if (
			pushing
			and magnitude >= lim.stall_min_load_permille
			and self._pushing_since is not None
			and time_s - self._pushing_since >= lim.stall_window_s - _EPS
		):
			oldest = next(s for s in self._samples if time_s - s[0] <= lim.stall_window_s + _EPS)
			if self._samples[-1][1] - oldest[1] < lim.stall_progress_ticks:
				return fired(ContactKind.STALL)
		return None
