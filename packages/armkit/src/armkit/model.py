"""Kinematic model of a serial arm: forward kinematics, a URDF loader and numerical inverse kinematics.

A :class:`RobotModel` is an ordered chain of revolute joints, each placed by ``xyz`` and ``rpy`` in the frame of
the previous link and turning about its own ``axis``, plus a fixed tool offset behind the last link. Conventions
follow URDF: a joint's transform is ``Trans(xyz) @ Rot(rpy) @ Rot(axis, angle)`` with
``Rot(rpy) = Rz(yaw) @ Ry(pitch) @ Rx(roll)``. Angles are degrees, lengths metres. The tool's z axis is its pointing
direction (for a gripper: out of the jaws).
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares


def rpy_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
	"""URDF fixed-axis roll-pitch-yaw rotation, radians: ``Rz(yaw) @ Ry(pitch) @ Rx(roll)``."""
	cr, sr, cp, sp, cy, sy = np.cos(roll), np.sin(roll), np.cos(pitch), np.sin(pitch), np.cos(yaw), np.sin(yaw)
	rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
	ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
	rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
	return rz @ ry @ rx


def _rpy_of(rotation: np.ndarray) -> tuple[float, float, float]:
	pitch = -math.asin(max(-1.0, min(1.0, float(rotation[2, 0]))))
	if abs(math.cos(pitch)) > 1e-9:
		return (
			math.atan2(rotation[2, 1], rotation[2, 2]),
			pitch,
			math.atan2(rotation[1, 0], rotation[0, 0]),
		)
	return 0.0, pitch, math.atan2(-rotation[0, 1], rotation[1, 1])


def _transform(xyz: Sequence[float], rpy: Sequence[float]) -> np.ndarray:
	t = np.eye(4)
	t[:3, :3] = rpy_matrix(*rpy)
	t[:3, 3] = xyz
	return t


def _turn(axis: np.ndarray, degrees: float) -> np.ndarray:
	"""Homogeneous rotation about a unit ``axis`` (Rodrigues)."""
	a = np.radians(degrees)
	k = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
	t = np.eye(4)
	t[:3, :3] = np.eye(3) + np.sin(a) * k + (1 - np.cos(a)) * (k @ k)
	return t


@dataclass(frozen=True)
class Joint:
	"""A revolute joint placed by ``xyz`` / ``rpy`` in the previous link's frame, with its limits in degrees."""

	name: str
	xyz: tuple[float, float, float]
	rpy: tuple[float, float, float]
	axis: tuple[float, float, float] = (0.0, 0.0, 1.0)
	lower_deg: float = -180.0
	upper_deg: float = 180.0


@dataclass(frozen=True)
class IKSolution:
	"""Result of :meth:`RobotModel.inverse`: angles (degrees) and how closely they reach the target.

	``reachable`` is False when the best solution within the joint limits misses the target by more than the
	tolerances; the angles are then only the closest attempt and must not be commanded.
	"""

	angles_deg: dict[str, float]
	position_error_mm: float
	approach_error_deg: float
	reachable: bool


@dataclass(frozen=True)
class RobotModel:
	"""Serial chain of revolute joints with named links and a tool offset.

	Parameters
	----------
	joints : tuple of Joint
		Movable joints from the base outwards.
	link_names : tuple of str
		The base link followed by the link driven by each joint (``len(joints) + 1`` names).
	tool_xyz, tool_rpy : tuple of float
		Pose of the tool frame in the last link's frame.
	"""

	joints: tuple[Joint, ...]
	link_names: tuple[str, ...]
	tool_xyz: tuple[float, float, float] = (0.0, 0.0, 0.0)
	tool_rpy: tuple[float, float, float] = (0.0, 0.0, 0.0)

	def __post_init__(self) -> None:
		if len(self.link_names) != len(self.joints) + 1:
			raise ValueError("link_names needs the base link plus one link per joint")

	@property
	def names(self) -> tuple[str, ...]:
		"""Joint names in chain order."""
		return tuple(j.name for j in self.joints)

	def limits_deg(self, name: str) -> tuple[float, float]:
		"""Lower and upper limit of a joint, degrees."""
		joint = self.joints[self.names.index(name)]
		return joint.lower_deg, joint.upper_deg

	@cached_property
	def _origins(self) -> tuple[np.ndarray, ...]:
		return tuple(_transform(j.xyz, j.rpy) for j in self.joints)

	@cached_property
	def _axes(self) -> tuple[np.ndarray, ...]:
		return tuple(np.asarray(j.axis, float) / np.linalg.norm(j.axis) for j in self.joints)

	@cached_property
	def _tool(self) -> np.ndarray:
		return _transform(self.tool_xyz, self.tool_rpy)

	def joint_frames(self, angles_deg: Mapping[str, float]) -> list[np.ndarray]:
		"""Pose of every joint frame in the base frame before its own rotation (column 2 of a z-axis joint)."""
		frames, t = [], np.eye(4)
		for joint, origin, axis in zip(self.joints, self._origins, self._axes, strict=True):
			t = t @ origin
			frames.append(t.copy())
			t = t @ _turn(axis, angles_deg.get(joint.name, 0.0))
		return frames

	def link_frames(self, angles_deg: Mapping[str, float]) -> list[np.ndarray]:
		"""Pose of every link in the base frame: the base first, then the link behind each joint."""
		frames, t = [np.eye(4)], np.eye(4)
		for joint, origin, axis in zip(self.joints, self._origins, self._axes, strict=True):
			t = t @ origin @ _turn(axis, angles_deg.get(joint.name, 0.0))
			frames.append(t.copy())
		return frames

	def forward(self, angles_deg: Mapping[str, float]) -> np.ndarray:
		"""4x4 pose of the last link; joints missing from ``angles_deg`` are at 0."""
		return self.link_frames(angles_deg)[-1]

	def tool_pose(self, angles_deg: Mapping[str, float]) -> np.ndarray:
		"""4x4 pose of the tool frame in the base frame."""
		return self.forward(angles_deg) @ self._tool

	def inverse(
		self,
		target_m: np.ndarray,
		*,
		approach: Sequence[float] | np.ndarray,
		fixed: Mapping[str, float],
		tolerance_mm: float = 1.0,
		tolerance_deg: float = 1.0,
		seeds: Sequence[Mapping[str, float]] | None = None,
	) -> IKSolution:
		"""Joint angles that put the tool at ``target_m`` with its z axis along ``approach``.

		Parameters
		----------
		target_m : numpy.ndarray
			Tool position in the base frame, metres.
		approach : array-like
			Direction the tool's z axis should point in (normalised here).
		fixed : mapping
			Joints held at a given angle (for example the wrist roll of a 5-joint arm). Every other joint is solved.
		tolerance_mm, tolerance_deg : float
			Largest position and approach error still counted as reachable.
		seeds : sequence of mapping, optional
			Starting configurations of the free joints. By default the centre of the limits and a fixed pseudo-random
			set inside them, so the result is reproducible.

		Returns
		-------
		IKSolution
			Best solution over the seeds, always within the joint limits of the free joints.
		"""
		target = np.asarray(target_m, dtype=np.float64)
		direction = np.asarray(approach, dtype=np.float64)
		direction = direction / np.linalg.norm(direction)
		free = [n for n in self.names if n not in fixed]
		lo = np.array([self.limits_deg(n)[0] for n in free])
		hi = np.array([self.limits_deg(n)[1] for n in free])

		def angles_of(x: np.ndarray) -> dict[str, float]:
			return {**{n: float(v) for n, v in zip(free, x, strict=True)}, **fixed}

		def residuals(x: np.ndarray) -> np.ndarray:
			pose = self.tool_pose(angles_of(x))
			# position in mm, direction error as a small-angle vector in degrees: both weigh about the same
			return np.concatenate([(pose[:3, 3] - target) * 1000.0, np.degrees(pose[:3, 2] - direction)])

		if seeds is None:
			rng = np.random.default_rng(0)
			starts = [(lo + hi) / 2, *(lo + (hi - lo) * rng.random(len(free)) for _ in range(40))]
		else:
			starts = [np.array([s[n] for n in free], dtype=float) for s in seeds]
		best = None
		for start in starts:
			seed = np.clip(start, lo + 1e-6, hi - 1e-6)
			fit = least_squares(residuals, seed, bounds=(lo, hi), x_scale=10.0, max_nfev=200)
			if best is None or fit.cost < best.cost:
				best = fit
			if 2 * best.cost < (0.1 * tolerance_mm) ** 2:
				break

		angles = angles_of(best.x)
		pose = self.tool_pose(angles)
		pos_err = float(np.linalg.norm(pose[:3, 3] - target) * 1000.0)
		ang_err = float(np.degrees(np.arccos(np.clip(pose[:3, 2] @ direction, -1.0, 1.0))))
		fixed_ok = all(self.limits_deg(n)[0] <= v <= self.limits_deg(n)[1] for n, v in fixed.items())
		return IKSolution(angles, pos_err, ang_err, pos_err <= tolerance_mm and ang_err <= tolerance_deg and fixed_ok)


def _floats(text: str | None, default: str) -> tuple[float, ...]:
	return tuple(float(v) for v in (text or default).split())


def load_urdf(path: Path, *, end_link: str, tool_link: str | None = None) -> RobotModel:
	"""Build a :class:`RobotModel` from a URDF: the chain from the root link to ``end_link``.

	Revolute and continuous joints become model joints. Fixed joints between them are folded into the next joint's
	origin; fixed joints after the last movable joint (and the ones leading on to ``tool_link``) form the tool offset.
	"""
	root = ET.parse(path).getroot()  # noqa: S314  (a URDF the caller chose, read from disk)
	by_child = {j.find("child").get("link"): j for j in root.findall("joint")}
	children = set(by_child)
	roots = [lk.get("name") for lk in root.findall("link") if lk.get("name") not in children]

	def chain_to(link: str) -> list[ET.Element]:
		out: list[ET.Element] = []
		while link in by_child:
			out.append(by_child[link])
			link = by_child[link].find("parent").get("link")
		return out[::-1]

	if end_link not in by_child and end_link not in roots:
		raise ValueError(f"link {end_link} is nowhere in {path.name}")
	path_joints = chain_to(tool_link or end_link)
	if tool_link is not None and chain_to(end_link) != path_joints[: len(chain_to(end_link))]:
		raise ValueError(f"tool link {tool_link} is not behind {end_link}")

	joints: list[Joint] = []
	links = [path_joints[0].find("parent").get("link") if path_joints else end_link]
	pending = np.eye(4)
	for el in path_joints:
		origin = el.find("origin")
		t = _transform(
			_floats(origin.get("xyz") if origin is not None else None, "0 0 0"),
			_floats(origin.get("rpy") if origin is not None else None, "0 0 0"),
		)
		kind = el.get("type")
		if kind == "fixed":
			pending = pending @ t
			continue
		if kind not in ("revolute", "continuous"):
			raise ValueError(f"joint {el.get('name')} has unsupported type {kind}")
		placed = pending @ t
		pending = np.eye(4)
		limit = el.find("limit")
		lower, upper = (-180.0, 180.0)
		if kind == "revolute" and limit is not None:
			lower, upper = math.degrees(float(limit.get("lower"))), math.degrees(float(limit.get("upper")))
		axis = el.find("axis")
		joints.append(
			Joint(
				el.get("name"),
				tuple(float(v) for v in placed[:3, 3]),
				_rpy_of(placed[:3, :3]),
				tuple(float(v) for v in _floats(axis.get("xyz") if axis is not None else None, "0 0 1")),
				lower,
				upper,
			)
		)
		links.append(el.find("child").get("link"))
	return RobotModel(tuple(joints), tuple(links), tuple(float(v) for v in pending[:3, 3]), _rpy_of(pending[:3, :3]))
