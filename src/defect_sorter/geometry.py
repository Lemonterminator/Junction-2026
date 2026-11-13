"""Pinhole camera geometry and table-plane estimation.

All distances are metres in the camera frame: x right, y down, z forward along the optical axis.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Intrinsics:
	"""Pinhole intrinsics of the image the depth map is aligned to.

	Parameters
	----------
	fx, fy : float
		Focal lengths in pixels.
	ppx, ppy : float
		Principal point in pixels.
	"""

	fx: float
	fy: float
	ppx: float
	ppy: float


@dataclass(frozen=True)
class Plane:
	"""Plane ``normal . p + offset = 0`` with the camera origin on the positive side.

	Parameters
	----------
	normal : numpy.ndarray
		Unit normal, shape (3,).
	offset : float
		Signed offset; equals the camera's perpendicular distance to the plane.
	inlier_fraction : float
		Fraction of the fitted points within the inlier tolerance.
	"""

	normal: np.ndarray
	offset: float
	inlier_fraction: float


def deproject(depth_m: np.ndarray, intrinsics: Intrinsics) -> np.ndarray:
	"""Back-project a depth map to camera-frame points.

	Parameters
	----------
	depth_m : numpy.ndarray
		Depth in metres, shape (H, W). Zero means no measurement.
	intrinsics : Intrinsics
		Intrinsics of the depth map's pixel grid.

	Returns
	-------
	numpy.ndarray
		Points, shape (H, W, 3). Pixels without depth map to the origin.
	"""
	h, w = depth_m.shape
	v, u = np.mgrid[0:h, 0:w]
	z = depth_m.astype(np.float64)
	x = (u - intrinsics.ppx) * z / intrinsics.fx
	y = (v - intrinsics.ppy) * z / intrinsics.fy
	return np.stack([x, y, z], axis=-1)


def fit_table_plane(
	points: np.ndarray,
	*,
	inlier_tol_m: float = 0.006,
	iterations: int = 300,
	sample_limit: int = 50_000,
	seed: int = 0,
) -> Plane:
	"""Fit the dominant plane with RANSAC and refine it by least squares on the inliers.

	Parameters
	----------
	points : numpy.ndarray
		Candidate points, shape (N, 3). Callers should pass only pixels with valid depth.
	inlier_tol_m : float
		Maximum point-to-plane distance counted as an inlier.
	iterations : int
		Number of random three-point hypotheses.
	sample_limit : int
		Hypotheses are scored on at most this many randomly chosen points.
	seed : int
		Random seed; the same seed and input give the same plane.

	Returns
	-------
	Plane
		The plane oriented so the camera origin has positive height.

	Raises
	------
	ValueError
		If fewer than three points are given or every hypothesis is degenerate.
	"""
	pts = np.asarray(points, dtype=np.float64).reshape(-1, 3)
	if len(pts) < 3:
		raise ValueError("need at least 3 points to fit a plane")
	rng = np.random.default_rng(seed)
	scored = pts if len(pts) <= sample_limit else pts[rng.choice(len(pts), sample_limit, replace=False)]

	best_normal, best_offset, best_count = None, 0.0, -1
	for _ in range(iterations):
		a, b, c = scored[rng.choice(len(scored), 3, replace=False)]
		normal = np.cross(b - a, c - a)
		norm = np.linalg.norm(normal)
		if norm < 1e-12:
			continue
		normal /= norm
		offset = -float(normal @ a)
		count = int((np.abs(scored @ normal + offset) < inlier_tol_m).sum())
		if count > best_count:
			best_normal, best_offset, best_count = normal, offset, count
	if best_normal is None:
		raise ValueError("all plane hypotheses were degenerate")

	inliers = pts[np.abs(pts @ best_normal + best_offset) < inlier_tol_m]
	centroid = inliers.mean(axis=0)
	_, _, vt = np.linalg.svd(inliers - centroid, full_matrices=False)
	normal = vt[-1]
	offset = -float(normal @ centroid)
	if offset < 0:
		normal, offset = -normal, -offset
	fraction = float((np.abs(pts @ normal + offset) < inlier_tol_m).mean())
	return Plane(normal=normal, offset=offset, inlier_fraction=fraction)


def height_above(points: np.ndarray, plane: Plane) -> np.ndarray:
	"""Signed height of each point above the plane, positive towards the camera.

	Parameters
	----------
	points : numpy.ndarray
		Points, shape (..., 3).
	plane : Plane
		Table plane from :func:`fit_table_plane`.

	Returns
	-------
	numpy.ndarray
		Heights in metres, shape (...).
	"""
	return points @ plane.normal + plane.offset
