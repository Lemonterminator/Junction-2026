"""A simulated servo bus with hard stops, obstructions, gravity and a torque limit.

:class:`SimulatedBus` implements :class:`~armkit.servo.ServoBus` and :class:`~armkit.servo.Clock`: ``sleep`` advances
the physics, so procedures run in simulated time. Each powered joint chases its goal like a position-controlled
servo: speed proportional to the error up to ``max_speed``, no wrap-around awareness (the goal register only holds
0..4095, as on the real devices), motion clamped by mechanical stops and obstacles, and a load that is gravity plus
a little friction while free and ``stiffness`` permille per tick of error while pressing on a stop (capped by the
torque limit). It exists to exercise procedures safely and deterministically; it models no servo precisely.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field

from armkit.calibration import TICKS_PER_REVOLUTION, Calibration, JointCalibration
from armkit.servo import JointSample

_SUBSTEP_S = 0.01
_KP_PER_S = 10.0


@dataclass
class SimJoint:
	"""One simulated joint. ``encoder`` and the stops are unwrapped shaft positions in ticks."""

	id: int
	encoder: float
	stop_low: float
	stop_high: float
	offset: int = 0
	gravity: int = 0
	max_speed: float = 600.0
	stiffness: float = 8.0
	deadband: int = 0
	sag: float = 0.0
	"""Ticks a powered joint settles below its goal (a loaded position servo's steady-state droop)."""
	torque_limit: int = 1000
	limit_min: int = 0
	limit_max: int = TICKS_PER_REVOLUTION - 1
	temperature_c: int = 35
	error_flags: int = 0
	torque: bool = False
	goal: int = 0
	load: int = 0
	velocity: float = 0.0


@dataclass
class Obstacle:
	"""A temporary stop at ``position`` blocking motion beyond it on ``side`` (+1 above, -1 below).

	It is touched each time the joint arrives at it; after ``clears_after_hits`` touches it is gone once the joint
	has backed away. ``None`` means it never goes away.
	"""

	joint: str
	position: float
	side: int
	clears_after_hits: int | None = None
	hits: int = 0
	touching: bool = field(default=False, repr=False)

	@property
	def active(self) -> bool:
		return self.clears_after_hits is None or self.hits < self.clears_after_hits or self.touching


class SimulatedBus:
	"""Physics-stepped stand-in for an arm's servos; see the module docstring."""

	def __init__(self, joints: Mapping[str, SimJoint], *, obstacles: Sequence[Obstacle] = ()) -> None:
		self._joints = dict(joints)
		self._obstacles = list(obstacles)
		self.live_limit_writes = False
		"""Whether position limits may be changed while a joint holds (servos differ; tests choose)."""
		self._time = 0.0
		for j in self._joints.values():
			j.goal = self._reading(j)

	@property
	def joints(self) -> tuple[str, ...]:
		return tuple(self._joints)

	def joint(self, name: str) -> SimJoint:
		"""The underlying simulated joint (to inspect or perturb it in a test)."""
		return self._joints[name]

	def now(self) -> float:
		return self._time

	def sleep(self, seconds: float) -> None:
		remaining = seconds
		while remaining > 1e-12:
			dt = min(_SUBSTEP_S, remaining)
			for name, joint in self._joints.items():
				self._step(name, joint, dt)
			self._time += dt
			remaining -= dt

	@staticmethod
	def _reading(joint: SimJoint) -> int:
		return round(joint.encoder - joint.offset) % TICKS_PER_REVOLUTION

	def _step(self, name: str, joint: SimJoint, dt: float) -> None:
		if not joint.torque:
			joint.load, joint.velocity = 0, 0.0
			return
		error = joint.goal - joint.sag - self._reading(joint)
		pressing = 0.0  # error the servo pushes with while it has not yet overcome friction and weight
		if abs(error) <= joint.deadband:
			pressing, error = error, 0
		velocity = max(-joint.max_speed, min(joint.max_speed, _KP_PER_S * error))
		target = joint.encoder + velocity * dt
		low, high = joint.stop_low, joint.stop_high
		blocking = []
		for ob in self._obstacles:
			if ob.joint == name and ob.active:
				blocking.append(ob)
				low, high = (
					(max(low, ob.position) if ob.side < 0 else low),
					(min(high, ob.position) if ob.side > 0 else high),
				)
		blocked = (target >= high and error > 0) or (target <= low and error < 0)
		joint.encoder = max(low, min(high, target))
		for ob in blocking:
			at_stop = blocked and abs(joint.encoder - ob.position) < 1e-9
			if at_stop and not ob.touching:
				ob.hits += 1
			ob.touching = at_stop
		for ob in self._obstacles:
			if ob.joint == name and ob not in blocking:
				ob.touching = False
		if blocked:
			joint.velocity = 0.0
			push = joint.gravity + joint.stiffness * abs(error)  # weight and push both rest on the stop
			joint.load = int(min(joint.torque_limit, push)) * (1 if error > 0 else -1)
		else:
			joint.velocity = velocity
			joint.load = min(
				joint.torque_limit, joint.gravity + int(0.05 * abs(velocity) + joint.stiffness * abs(pressing))
			)

	def read_sample(self, joint: str) -> JointSample:
		j = self._joints[joint]
		return JointSample(self._reading(j), round(j.velocity), j.load, j.temperature_c, j.error_flags)

	def read_positions(self) -> dict[str, int]:
		return {n: self._reading(j) for n, j in self._joints.items()}

	def write_goals(self, goals: Mapping[str, int]) -> None:
		for name, value in goals.items():
			j = self._joints[name]
			j.goal = max(j.limit_min, min(j.limit_max, int(value)))

	def _select(self, joints: Iterable[str] | None) -> list[SimJoint]:
		return [self._joints[n] for n in (self.joints if joints is None else joints)]

	def set_torque(self, enabled: bool, joints: Iterable[str] | None = None) -> None:
		for j in self._select(joints):
			j.torque = enabled

	def set_torque_limit(self, permille: int, joints: Iterable[str] | None = None) -> None:
		for j in self._select(joints):
			j.torque_limit = permille

	def write_limits(self, joint: str, range_min: int, range_max: int) -> bool:
		j = self._joints[joint]
		if j.torque and not self.live_limit_writes:
			return False
		j.limit_min, j.limit_max = range_min, range_max
		return True

	def read_goal(self, joint: str) -> int:
		return self._joints[joint].goal

	def torque_enabled(self, joint: str) -> bool:
		return self._joints[joint].torque

	def torque_limit(self, joint: str) -> int:
		return self._joints[joint].torque_limit

	def hold(self, joints: Iterable[str] | None = None) -> None:
		for j in self._select(joints):
			j.goal = self._reading(j)
			j.torque = True
			j.load = min(j.torque_limit, j.gravity)  # a powered joint carries its weight at once

	def reset_calibration(self) -> None:
		self.set_torque(False)
		for j in self._joints.values():
			j.offset, j.limit_min, j.limit_max = 0, 0, TICKS_PER_REVOLUTION - 1

	def write_calibration(self, calibration: Calibration) -> None:
		if any(self._joints[name].torque for name in calibration):
			raise RuntimeError("calibration registers can only be written with torque off")
		for name, cal in calibration.items():
			j = self._joints[name]
			j.offset, j.limit_min, j.limit_max = cal.homing_offset, cal.range_min, cal.range_max

	def read_calibration(self) -> Calibration:
		return Calibration(
			{n: JointCalibration(j.id, 0, j.offset, j.limit_min, j.limit_max) for n, j in self._joints.items()}
		)
