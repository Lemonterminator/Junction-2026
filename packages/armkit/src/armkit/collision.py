"""Self-collision and floor checks from bounding spheres fitted to the robot's collision meshes.

Every link carries a few spheres (centres and radii in the link frame) that together bound its mesh. A pose is
clear when no two spheres of non-neighbouring links overlap and no sphere dips below the floor plane. Bounding
spheres over-estimate the links, so a clear pose is genuinely clear; a reported contact may be a near miss, which is
the safe side for deciding where an arm may swing.

:func:`collision_from_urdf` fits the spheres from the STL files a URDF references. The result can be baked into a
robot profile as plain numbers so that runtime needs no meshes.
"""

from __future__ import annotations

import struct
import xml.etree.ElementTree as ET
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

import numpy as np

from armkit.model import RobotModel, rpy_matrix


@dataclass(frozen=True)
class LinkShape:
	"""Bounding spheres of one link: ``centers`` (n, 3) and ``radii`` (n,) in the link frame, metres."""

	centers: np.ndarray
	radii: np.ndarray


@dataclass(frozen=True)
class Clearance:
	"""Smallest gap in a pose (negative when overlapping) and the two links, or link and ``"floor"``, that set it."""

	distance_m: float
	between: tuple[str, str] | None


def fit_link_shape(points: np.ndarray, count: int, *, refinements: int = 5) -> LinkShape:
	"""Cover ``points`` with up to ``count`` spheres: farthest-point seeds, a few k-means steps, bounding radii."""
	pts = np.unique(np.asarray(points, dtype=np.float64), axis=0)
	count = max(1, min(count, len(pts)))
	centers = [pts[0]]
	gap = np.linalg.norm(pts - centers[0], axis=1)
	for _ in range(count - 1):
		pick = pts[gap.argmax()]
		centers.append(pick)
		gap = np.minimum(gap, np.linalg.norm(pts - pick, axis=1))
	c = np.array(centers)
	for _ in range(refinements):
		owner = np.linalg.norm(pts[:, None] - c[None], axis=2).argmin(axis=1)
		c = np.array([pts[owner == i].mean(axis=0) if (owner == i).any() else c[i] for i in range(count)])
	owner = np.linalg.norm(pts[:, None] - c[None], axis=2).argmin(axis=1)
	radii = np.array(
		[np.linalg.norm(pts[owner == i] - c[i], axis=1).max() if (owner == i).any() else 0.0 for i in range(count)]
	)
	keep = radii > 0
	return LinkShape(c[keep] if keep.any() else c[:1], radii[keep] if keep.any() else np.array([1e-4]))


def read_stl(path: Path) -> np.ndarray:
	"""All triangle vertices of a binary or ASCII STL as an (n, 3) array in the file's units."""
	data = path.read_bytes()
	if len(data) >= 84 and len(data) == 84 + 50 * struct.unpack("<I", data[80:84])[0]:
		n = struct.unpack("<I", data[80:84])[0]
		tri = np.frombuffer(data[84:], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]), count=n)
		return tri["v"].reshape(-1, 3).astype(np.float64)
	rows = [
		line.split()[1:4] for line in data.decode("ascii", "ignore").splitlines() if line.strip().startswith("vertex")
	]
	return np.array(rows, dtype=np.float64).reshape(-1, 3)


class CollisionModel:
	"""Sphere-based collision checker for a :class:`~armkit.model.RobotModel`.

	Parameters
	----------
	robot : RobotModel
		The kinematic chain; link names in ``shapes`` refer to ``robot.link_names``.
	shapes : mapping
		Bounding spheres per link (links without shapes never collide).
	ignore : iterable of pair of str
		Link pairs that may touch (links that are neighbours in the chain are always ignored).
	floor_z : float or None
		Height of the floor plane in the base frame, or ``None`` for no floor.
	floor_exempt : iterable of str
		Links allowed below ``floor_z`` (the base that stands on it).
	floor_extra : mapping, optional
		Extra floor height per link (see :meth:`with_floor_raised`).
	floor_area : sequence of (x, y), optional
		Polygon (base frame) where the floor is: a table with an edge. Spheres within their radius of it are checked
		against the floor; beyond it a link may go lower. ``None`` means the floor is everywhere.
	"""

	def __init__(
		self,
		robot: RobotModel,
		shapes: Mapping[str, LinkShape],
		*,
		ignore: Iterable[tuple[str, str]] = (),
		floor_z: float | None = 0.0,
		floor_exempt: Iterable[str] = (),
		floor_extra: Mapping[str, float] | None = None,
		floor_area: Sequence[tuple[float, float]] | None = None,
	) -> None:
		self.floor_area = None if floor_area is None else np.asarray(floor_area, dtype=np.float64)
		self.robot = robot
		self.floor_extra = dict(floor_extra or {})
		self.shapes = dict(shapes)
		self.floor_z = floor_z
		self.floor_exempt = frozenset(floor_exempt)
		self.ignore = frozenset(frozenset(p) for p in ignore)
		index = {name: i for i, name in enumerate(robot.link_names)}
		self._pairs = [
			(a, b)
			for a, b in combinations([n for n in robot.link_names if n in self.shapes], 2)
			if abs(index[a] - index[b]) > 1 and frozenset((a, b)) not in self.ignore
		]

	def world_spheres(self, angles_deg: Mapping[str, float]) -> dict[str, tuple[np.ndarray, np.ndarray]]:
		"""Sphere centres (in the base frame) and radii of every link with shapes."""
		frames = dict(zip(self.robot.link_names, self.robot.link_frames(angles_deg), strict=True))
		return {
			name: (shape.centers @ frames[name][:3, :3].T + frames[name][:3, 3], shape.radii)
			for name, shape in self.shapes.items()
		}

	def clearance(self, angles_deg: Mapping[str, float]) -> Clearance:
		"""Smallest gap between non-neighbouring links and to the floor in this pose."""
		world = self.world_spheres(angles_deg)
		best, between = np.inf, None
		for a, b in self._pairs:
			(ca, ra), (cb, rb) = world[a], world[b]
			gap = float((np.linalg.norm(ca[:, None] - cb[None], axis=2) - ra[:, None] - rb[None]).min())
			if gap < best:
				best, between = gap, (a, b)
		if self.floor_z is not None:
			for name, (c, r) in world.items():
				if name in self.floor_exempt:
					continue
				over = self._over_floor(c, r)
				if not over.any():
					continue
				gap = float((c[over, 2] - r[over]).min() - self.floor_z - self.floor_extra.get(name, 0.0))
				if gap < best:
					best, between = gap, (name, "floor")
		return Clearance(best, between)

	def is_clear(self, angles_deg: Mapping[str, float], margin: float = 0.0) -> bool:
		"""True when every gap in this pose exceeds ``margin`` metres."""
		return self.clearance(angles_deg).distance_m > margin

	def _over_floor(self, centers: np.ndarray, radii: np.ndarray) -> np.ndarray:
		"""Which spheres are over the floor: all of them, or those within their radius of the floor area."""
		if self.floor_area is None:
			return np.ones(len(radii), dtype=bool)
		poly = self.floor_area
		x, y = centers[:, 0], centers[:, 1]
		inside = np.zeros(len(radii), dtype=bool)
		near = np.full(len(radii), np.inf)
		for (x0, y0), (x1, y1) in zip(poly, np.roll(poly, -1, axis=0), strict=True):
			crosses = (y0 > y) != (y1 > y)
			with np.errstate(divide="ignore", invalid="ignore"):
				at = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
			inside ^= crosses & (x < at)
			dx, dy = x1 - x0, y1 - y0
			t = np.clip(((x - x0) * dx + (y - y0) * dy) / max(dx * dx + dy * dy, 1e-12), 0.0, 1.0)
			near = np.minimum(near, np.hypot(x - (x0 + t * dx), y - (y0 + t * dy)))
		return inside | (near <= radii)

	def with_floor_raised(self, by_m: float, links: Iterable[str] | None = None) -> CollisionModel:
		"""Copy whose floor is ``by_m`` higher for ``links`` (default: every link), so plans keep them that far above it."""
		extra = dict(self.floor_extra)
		for name in self.shapes if links is None else links:
			extra[name] = extra.get(name, 0.0) + by_m
		return CollisionModel(
			self.robot,
			self.shapes,
			ignore=[tuple(p) for p in self.ignore],
			floor_z=self.floor_z,
			floor_exempt=self.floor_exempt,
			floor_extra=extra,
			floor_area=None if self.floor_area is None else [tuple(v) for v in self.floor_area],
		)

	def ignoring_contacts_at(self, angles_deg: Mapping[str, float]) -> CollisionModel:
		"""Copy that also ignores link pairs overlapping in a reference pose (parts that are built to touch)."""
		world = self.world_spheres(angles_deg)
		touching = []
		for a, b in self._pairs:
			(ca, ra), (cb, rb) = world[a], world[b]
			if (np.linalg.norm(ca[:, None] - cb[None], axis=2) - ra[:, None] - rb[None]).min() <= 0:
				touching.append((a, b))
		return CollisionModel(
			self.robot,
			self.shapes,
			ignore=[*(tuple(p) for p in self.ignore), *touching],
			floor_z=self.floor_z,
			floor_exempt=self.floor_exempt,
			floor_extra=self.floor_extra,
			floor_area=None if self.floor_area is None else [tuple(v) for v in self.floor_area],
		)


def collision_from_urdf(
	path: Path,
	robot: RobotModel,
	*,
	spheres_per_link: int = 7,
	attach: Mapping[str, str] | None = None,
	stride: int = 1,
	floor_z: float | None = 0.0,
	floor_exempt: Iterable[str] | None = None,
) -> CollisionModel:
	"""Fit bounding spheres to the ``<collision>`` meshes of a URDF, link by link.

	Parameters
	----------
	path : Path
		URDF file; mesh filenames are resolved relative to it.
	robot : RobotModel
		Chain whose ``link_names`` select the links to fit.
	spheres_per_link : int
		Spheres per link; more follow the shape closer.
	attach : mapping, optional
		Branch links that are not in the chain mapped to the chain link that carries them (a gripper jaw), placed by
		its joint origin at angle 0.
	stride : int
		Use every ``stride``-th mesh vertex. The default 1 keeps all vertices, so the spheres bound the whole mesh;
		a larger stride is faster but only bounds the kept vertices.
	floor_z, floor_exempt
		Passed to :class:`CollisionModel`; ``floor_exempt`` defaults to the base link.
	"""
	root = ET.parse(path).getroot()  # noqa: S314  (a URDF the caller chose, read from disk)
	attach = dict(attach or {})
	joint_origin = {}
	for el in root.findall("joint"):
		origin = el.find("origin")
		if origin is not None:
			xyz = np.array(origin.get("xyz", "0 0 0").split(), float)
			joint_origin[el.find("child").get("link")] = (
				rpy_matrix(*map(float, origin.get("rpy", "0 0 0").split())),
				xyz,
			)
	points: dict[str, list[np.ndarray]] = {}
	for link in root.findall("link"):
		name = link.get("name")
		target = name if name in robot.link_names else attach.get(name)
		if target is None:
			continue
		for col in link.findall("collision"):
			mesh = col.find("geometry/mesh")
			if mesh is None:
				continue
			origin = col.find("origin")
			xyz = np.array(origin.get("xyz", "0 0 0").split(), float) if origin is not None else np.zeros(3)
			rpy = tuple(map(float, origin.get("rpy", "0 0 0").split())) if origin is not None else (0.0, 0.0, 0.0)
			v = read_stl(path.parent / mesh.get("filename"))[::stride] @ rpy_matrix(*rpy).T + xyz
			if target != name:
				rot, shift = joint_origin[name]
				v = v @ rot.T + shift
			points.setdefault(target, []).append(v)
	shapes = {name: fit_link_shape(np.vstack(parts), spheres_per_link) for name, parts in points.items()}
	return CollisionModel(
		robot, shapes, floor_z=floor_z, floor_exempt=[robot.link_names[0]] if floor_exempt is None else floor_exempt
	)
