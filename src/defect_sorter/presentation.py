"""Geometry for presenting a held brick to the inspection camera.

Pure NumPy, no simulator: the MuJoCo cell (``scripts/sim/so101_sort_sim.py``) uses these to put a defect on any face
of the brick, find show points in front of the main camera that the arm can reach, order the presentation poses by
how much of the defect they show, and accept or reject randomised cameras. All positions are in the robot base
frame (metres, table top at z = 0); brick-local quantities are in the brick body frame with its centre at the origin.
"""

from __future__ import annotations

import math

import numpy as np

FACES: tuple[tuple[int, int], ...] = ((0, 1), (0, -1), (1, 1), (1, -1), (2, 1), (2, -1))
"""Brick faces as (axis, sign) in the brick frame; index 4 is the top face (+z), 5 the bottom."""


def face_frame(size: tuple[float, float, float], face: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
	"""Centre, outward normal and in-plane axes (u, v with u x v = normal) of one face of a box.

	Parameters
	----------
	size
		Full extents of the brick body along its x, y and z axes (studs not included).
	face
		Index into :data:`FACES`.
	"""
	axis, sign = FACES[face]
	normal = np.zeros(3)
	normal[axis] = float(sign)
	u = np.zeros(3)
	u[(axis + 1) % 3] = 1.0
	v = np.cross(normal, u)
	return normal * size[axis] / 2.0, normal, u, v


def defect_strokes(
	size: tuple[float, float, float], face: int, fill: float = 0.7
) -> list[tuple[np.ndarray, np.ndarray, np.ndarray, float]]:
	"""The two strokes of a cross drawn on ``face``: centre, stroke axis, side axis (normal x stroke), half length.

	The strokes run along the face diagonals of the largest centred square, and reach ``fill`` of its half side.
	"""
	centre, normal, u, v = face_frame(size, face)
	axis = FACES[face][0]
	half = min(size[(axis + 1) % 3], size[(axis + 2) % 3]) / 2.0
	length = fill * half * math.sqrt(2.0)
	strokes = []
	for d in ((u + v) / math.sqrt(2.0), (u - v) / math.sqrt(2.0)):
		strokes.append((centre.copy(), d, np.cross(normal, d), length))
	return strokes


def show_points(
	cam_pos: np.ndarray,
	forward: np.ndarray,
	distances: tuple[float, ...],
	max_off_axis_deg: float,
	reach: tuple[float, float],
	z_min: float,
	steps: int = 4,
	azimuths: int = 8,
) -> np.ndarray:
	"""Candidate show points in front of a camera, closest to its optical axis first.

	Points lie at the given distances from the camera, along rays at most ``max_off_axis_deg`` from the optical axis,
	with horizontal distance from the robot base inside ``reach`` (min, max) and height at least ``z_min``. Points on
	the axis come first, then by increasing off-axis angle, then by distance from the middle of ``distances``.
	"""
	cam_pos = np.asarray(cam_pos, dtype=np.float64)
	f = np.asarray(forward, dtype=np.float64)
	f = f / np.linalg.norm(f)
	a = np.array([0.0, 0.0, 1.0]) if abs(f[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
	e1 = np.cross(f, a)
	e1 /= np.linalg.norm(e1)
	e2 = np.cross(f, e1)
	mid = (min(distances) + max(distances)) / 2.0
	cands: list[tuple[float, float, np.ndarray]] = []
	for i in range(steps + 1):
		off = math.radians(max_off_axis_deg) * i / steps
		for j in range(azimuths if i else 1):
			phi = 2 * math.pi * j / azimuths
			ray = math.cos(off) * f + math.sin(off) * (math.cos(phi) * e1 + math.sin(phi) * e2)
			for d in distances:
				p = cam_pos + d * ray
				r = math.hypot(p[0], p[1])
				if reach[0] <= r <= reach[1] and p[2] >= z_min:
					cands.append((off, abs(d - mid), p))
	cands.sort(key=lambda c: (round(c[0], 9), c[1]))
	return np.array([c[2] for c in cands]).reshape(-1, 3)


def view_cosine(normal: np.ndarray, point: np.ndarray, cam_pos: np.ndarray) -> float:
	"""Cosine between a surface normal at ``point`` and the direction from ``point`` to the camera."""
	to_cam = np.asarray(cam_pos, dtype=np.float64) - np.asarray(point, dtype=np.float64)
	n = np.asarray(normal, dtype=np.float64)
	return float(n @ to_cam / (np.linalg.norm(n) * np.linalg.norm(to_cam)))


def order_show_poses(poses: np.ndarray, scores: np.ndarray, k: int, min_sep: float, rel_min: float) -> list[int]:
	"""Indices of up to ``k`` poses to present, best score first.

	A pose is skipped when its score is not positive, below ``rel_min`` times the best score, or within ``min_sep``
	(Euclidean, in the pose coordinates, e.g. radians of wrist flex and roll) of a pose already chosen.
	"""
	poses = np.asarray(poses, dtype=np.float64)
	scores = np.asarray(scores, dtype=np.float64)
	if scores.size == 0 or scores.max() <= 0:
		return []
	chosen: list[int] = []
	for i in np.argsort(-scores, kind="stable"):
		if len(chosen) == k or scores[i] <= 0 or scores[i] < rel_min * scores.max():
			break
		if all(np.linalg.norm(poses[i] - poses[c]) >= min_sep for c in chosen):
			chosen.append(int(i))
	return chosen


def camera_view_ok(
	cam_pos: np.ndarray,
	forward: np.ndarray,
	swept: np.ndarray,
	clearance: float,
	z_min: float = 0.15,
	min_down_deg: float = 10.0,
	radii: np.ndarray | None = None,
) -> tuple[bool, str]:
	"""Whether a camera is above the table, looks down and keeps ``clearance`` from the arm's swept points.

	``swept`` holds points on the arm surface over the whole trajectory (for example link geometry sampled per frame),
	so the clearance is measured from the arm itself. With ``radii`` (one per point, e.g. the bounding radius of the
	link geometry centred there) the clearance is measured from those spheres instead of their centres.
	"""
	cam_pos = np.asarray(cam_pos, dtype=np.float64)
	f = np.asarray(forward, dtype=np.float64)
	if cam_pos[2] < z_min:
		return False, f"camera {cam_pos[2]:.2f} m above the table, below {z_min:.2f} m"
	if -f[2] / np.linalg.norm(f) < math.sin(math.radians(min_down_deg)):
		return False, "camera does not look down"
	swept = np.asarray(swept, dtype=np.float64).reshape(-1, 3)
	if len(swept):
		dist = np.linalg.norm(swept - cam_pos, axis=1)
		if radii is not None:
			dist = dist - np.asarray(radii, dtype=np.float64).reshape(-1)
		gap = float(np.min(dist))
		if gap < clearance:
			return False, f"clearance {gap:.3f} m from the arm, below {clearance:.3f} m"
	return True, ""
