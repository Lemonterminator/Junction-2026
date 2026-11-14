"""Description of one arm for calibration: kinematic model, collision shapes and per-joint setup.

An :class:`ArmProfile` is plain data. ``joints`` lists the servo joints in the order they should be calibrated
(joints that are not part of the kinematic chain, such as a gripper, are listed too and need an explicit
``travel_deg``). Each :class:`JointSetup` also records where the joint sits at the arm's documented rest pose, which
is the reference every automatic calibration starts from: the arm is placed there and the joint angles are
estimated from it until each joint has been measured.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from typing import Literal

from armkit.collision import CollisionModel
from armkit.model import RobotModel

JointKind = Literal["limited", "full_turn"]


@dataclass(frozen=True)
class JointSetup:
	"""Calibration settings of one servo joint.

	Parameters
	----------
	name : str
		Joint name (a chain joint of the model, or an extra such as a gripper).
	servo_id : int
		Bus id of its servo.
	kind : {"limited", "full_turn"}
		``limited`` joints have two travel ends that the procedure searches; ``full_turn`` joints (a continuously
		rotating wrist roll) get the whole 0..4095 range without moving.
	rest_deg : float
		Joint angle (model degrees, zero in the middle of the range) at the arm's rest pose.
	travel_deg : tuple of float, optional
		Lower and upper end of travel in model degrees; defaults to the model's joint limits.
	park_joints : tuple of str, optional
		Joints allowed to move away from where they are when this joint's sweep needs clearance (default: all others).
	preferred_poses : tuple of mapping
		Parking poses to try before the automatic search.
	"""

	name: str
	servo_id: int
	kind: JointKind = "limited"
	rest_deg: float = 0.0
	travel_deg: tuple[float, float] | None = None
	park_joints: tuple[str, ...] | None = None
	preferred_poses: tuple[Mapping[str, float], ...] = ()


@dataclass(frozen=True)
class ArmProfile:
	"""Everything the calibration procedure needs to know about an arm model."""

	name: str
	robot: RobotModel
	collision: CollisionModel
	joints: tuple[JointSetup, ...]

	def setup(self, name: str) -> JointSetup:
		"""The setup of a joint by name."""
		return next(j for j in self.joints if j.name == name)

	def travel(self, name: str) -> tuple[float, float]:
		"""Lower and upper end of the joint's travel, model degrees."""
		setup = self.setup(name)
		if setup.travel_deg is not None:
			return setup.travel_deg
		return self.robot.limits_deg(name)

	@property
	def rest_pose(self) -> dict[str, float]:
		"""Every joint's model angle at the rest pose."""
		return {j.name: j.rest_deg for j in self.joints}


def with_table_clearance(profile: ArmProfile, clearance_m: float) -> ArmProfile:
	"""The same arm planned against a table ``clearance_m`` higher than the real one.

	A few degrees of error in a joint (a hand-posed reference, a sagging link, an open gripper) moves the tip by
	centimetres at full reach, so plans on real hardware keep that much air between the arm's far links and the table.
	The base and the first links turn about axes close to the table and cannot wander that way, so they keep the real
	table height.
	"""
	far = profile.robot.link_names[3:]  # beyond the second joint: where small angle errors become centimetres
	return replace(profile, collision=profile.collision.with_floor_raised(clearance_m, links=far))


def with_table_area(profile: ArmProfile, area: Sequence[tuple[float, float]]) -> ArmProfile:
	"""The same arm with the table limited to ``area`` (polygon in the base frame, metres): beyond its edge the arm may
	reach below table height."""
	c = profile.collision
	model = CollisionModel(
		c.robot,
		c.shapes,
		ignore=[tuple(p) for p in c.ignore],
		floor_z=c.floor_z,
		floor_exempt=c.floor_exempt,
		floor_extra=c.floor_extra,
		floor_area=area,
	)
	return replace(profile, collision=model)
