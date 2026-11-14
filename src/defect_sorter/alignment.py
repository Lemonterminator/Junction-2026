"""Cell alignment from markers: marker poses refined with depth, and comparison with a saved reference.

The top camera sees flat markers almost face-on, where the image alone pins down sideways position well but
tilt and distance poorly. :func:`refine_with_depth` takes tilt and distance from the aligned depth image
instead. :func:`compare_to_reference` tells whether anything (the robot base clamp, the bowls, the table
anchors) moved since a saved reference.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from defect_sorter.geometry import Intrinsics
from defect_sorter.markers import MarkerDetection


@dataclass(frozen=True)
class MarkerPose:
	"""Pose of a marker in the camera frame.

	Parameters
	----------
	position_m : numpy.ndarray
		Centre of the black square, metres.
	normal : numpy.ndarray
		Unit normal of the printed face, pointing towards the camera.
	yaw_deg : float
		Direction of the marker's top edge in the image, degrees; 0 = pointing right, positive = clockwise on screen.
	source : str
		``"depth"`` when tilt and distance come from the depth image, ``"image"`` when only the image was usable.
	"""

	id: int
	use: str
	size_mm: float
	position_m: np.ndarray
	normal: np.ndarray
	yaw_deg: float
	source: str


@dataclass(frozen=True)
class Delta:
	"""Change of one marker relative to the reference; angles and shift are ``None`` when the marker is missing."""

	id: int
	moved: bool
	missing: bool
	shift_mm: float | None
	yaw_deg: float | None
	tilt_deg: float | None


def tilt_deg(a: np.ndarray, b: np.ndarray) -> float:
	"""Angle between two planes given by their normals, 0-90 degrees (normal direction is ignored)."""
	cos = abs(float(np.dot(a, b))) / (float(np.linalg.norm(a)) * float(np.linalg.norm(b)))
	return float(np.degrees(np.arccos(np.clip(cos, 0.0, 1.0))))


def _edge_yaw_deg(corners_px: np.ndarray) -> float:
	dx, dy = corners_px[1] - corners_px[0]
	return float(np.degrees(np.arctan2(dy, dx)))


def refine_with_depth(
	detection: MarkerDetection,
	depth_m: np.ndarray,
	intrinsics: Intrinsics,
	*,
	shrink: float = 0.7,
	min_points: int = 30,
) -> MarkerPose:
	"""Plane fit on the depth pixels inside the marker; falls back to the image pose when depth is missing.

	Parameters
	----------
	detection : MarkerDetection
		Marker found in the colour image that ``depth_m`` is aligned to.
	depth_m : numpy.ndarray
		Aligned depth in metres; zero means no measurement.
	intrinsics : Intrinsics
		Intrinsics of the colour image.
	shrink : float
		The marker outline is shrunk towards its centre by this factor to avoid edge pixels.
	min_points : int
		Fewer valid depth pixels than this means the image pose is used.
	"""
	corners = detection.corners_px
	centre = corners.mean(axis=0)
	yaw = _edge_yaw_deg(corners)
	inner = centre + (corners - centre) * shrink
	mask = np.zeros(depth_m.shape, np.uint8)
	cv2.fillPoly(mask, [np.round(inner).astype(np.int32)], 1)
	vs, us = np.nonzero((mask > 0) & (depth_m > 0))
	if len(vs) < min_points:
		return MarkerPose(
			id=detection.id,
			use=detection.use,
			size_mm=detection.size_mm,
			position_m=np.asarray(detection.position_m, dtype=np.float64),
			normal=np.asarray(detection.rotation[:, 2], dtype=np.float64),
			yaw_deg=yaw,
			source="image",
		)
	z = depth_m[vs, us].astype(np.float64)
	pts = np.stack([(us - intrinsics.ppx) * z / intrinsics.fx, (vs - intrinsics.ppy) * z / intrinsics.fy, z], axis=1)
	centroid = pts.mean(axis=0)
	normal = np.linalg.svd(pts - centroid, full_matrices=False)[2][-1]
	if float(normal @ centroid) > 0:  # orient towards the camera at the origin
		normal = -normal
	ray = np.array([(centre[0] - intrinsics.ppx) / intrinsics.fx, (centre[1] - intrinsics.ppy) / intrinsics.fy, 1.0])
	position = ray * float(normal @ centroid) / float(normal @ ray)
	return MarkerPose(
		id=detection.id,
		use=detection.use,
		size_mm=detection.size_mm,
		position_m=position,
		normal=normal,
		yaw_deg=yaw,
		source="depth",
	)


def compare_to_reference(
	current: dict[int, MarkerPose],
	reference: dict[int, MarkerPose],
	*,
	shift_tol_mm: float = 3.0,
	yaw_tol_deg: float = 1.0,
) -> dict[int, Delta]:
	"""Compare each reference marker with its current pose.

	A marker counts as moved when its centre shifted more than ``shift_tol_mm`` or its yaw changed more than
	``yaw_tol_deg``. Tilt is reported but not used for the decision, because depth noise on small markers is
	of the order of a degree.
	"""
	out: dict[int, Delta] = {}
	for marker_id, ref in reference.items():
		cur = current.get(marker_id)
		if cur is None:
			out[marker_id] = Delta(id=marker_id, moved=False, missing=True, shift_mm=None, yaw_deg=None, tilt_deg=None)
			continue
		shift = float(np.linalg.norm(cur.position_m - ref.position_m)) * 1000.0
		yaw = (cur.yaw_deg - ref.yaw_deg + 180.0) % 360.0 - 180.0
		out[marker_id] = Delta(
			id=marker_id,
			moved=shift > shift_tol_mm or abs(yaw) > yaw_tol_deg,
			missing=False,
			shift_mm=shift,
			yaw_deg=yaw,
			tilt_deg=tilt_deg(cur.normal, ref.normal),
		)
	return out


def save_reference(path: Path, poses: dict[int, MarkerPose]) -> None:
	"""Write marker poses as the alignment reference (JSON)."""
	data = {
		"saved_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
		"markers": {
			str(p.id): {
				"use": p.use,
				"size_mm": p.size_mm,
				"position_m": [float(v) for v in p.position_m],
				"normal": [float(v) for v in p.normal],
				"yaw_deg": p.yaw_deg,
				"source": p.source,
			}
			for p in poses.values()
		},
	}
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(data, indent=1))


def load_reference(path: Path) -> dict[int, MarkerPose]:
	"""Read a reference written by :func:`save_reference`."""
	data = json.loads(path.read_text())
	return {
		int(k): MarkerPose(
			id=int(k),
			use=v["use"],
			size_mm=v["size_mm"],
			position_m=np.array(v["position_m"]),
			normal=np.array(v["normal"]),
			yaw_deg=v["yaw_deg"],
			source=v["source"],
		)
		for k, v in data["markers"].items()
	}
