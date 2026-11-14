"""Cell alignment from markers: marker poses refined with depth, expressed in a table frame, compared with a reference.

The top camera does not have to look straight down. :func:`refine_with_depth` takes tilt and distance from the
aligned depth image (the image alone only pins down sideways position well). :func:`table_frame` then builds a
frame from the fitted table plane (z up) and two anchor markers (x axis), and :func:`to_table_pose` re-expresses
every marker in it, so the camera's own tilt and position drop out. :func:`compare_to_reference` tells whether
anything (the robot base clamp, the bowls) moved since a saved reference, even if the camera was bumped.

Table frame: x along anchor A to anchor B, z up out of the table, y = z cross x (right-handed). Distances in the
table frame are millimetres, angles degrees.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from defect_sorter.geometry import Intrinsics, Plane
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
	corners_m : numpy.ndarray, optional
		The four corners (top-left, top-right, bottom-right, bottom-left of the printed face) in camera space, on
		the marker's plane, shape (4, 3). Needed for :func:`to_table_pose`.
	"""

	id: int
	use: str
	size_mm: float
	position_m: np.ndarray
	normal: np.ndarray
	yaw_deg: float
	source: str
	corners_m: np.ndarray | None = None


@dataclass(frozen=True)
class TableFrame:
	"""Right-handed frame fixed to the table; ``axes`` rows are x, y, z expressed in camera coordinates."""

	origin: np.ndarray
	axes: np.ndarray
	basis: str

	def point(self, p: np.ndarray) -> np.ndarray:
		"""Camera-space point (metres) to table-frame coordinates (metres)."""
		return self.axes @ (np.asarray(p, dtype=np.float64) - self.origin)

	def direction(self, v: np.ndarray) -> np.ndarray:
		"""Camera-space direction to table-frame direction."""
		return self.axes @ np.asarray(v, dtype=np.float64)


@dataclass(frozen=True)
class TablePose:
	"""A marker in the table frame.

	Parameters
	----------
	position_mm : numpy.ndarray
		Centre of the marker, millimetres; z is the height above the table.
	tilt_deg : float
		Angle between the printed face's normal and table-up: 0 = lying flat face-up, 90 = standing upright.
	yaw_deg : float
		Direction of the marker's top edge (left to right) in the table plane, degrees from the table x axis.
	facing_deg : float or None
		Direction the face points in the table plane; ``None`` when the marker is nearly flat (under 10 degrees).
	"""

	id: int
	use: str
	size_mm: float
	position_mm: np.ndarray
	tilt_deg: float
	yaw_deg: float
	facing_deg: float | None
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


def _corners_on_plane(corners_px: np.ndarray, position: np.ndarray, normal: np.ndarray, intr: Intrinsics) -> np.ndarray:
	"""Intersect each corner's viewing ray with the marker plane (through ``position`` with ``normal``)."""
	rays = np.stack(
		[(corners_px[:, 0] - intr.ppx) / intr.fx, (corners_px[:, 1] - intr.ppy) / intr.fy, np.ones(len(corners_px))],
		axis=1,
	)
	t = float(normal @ position) / (rays @ normal)
	return rays * t[:, None]


def refine_with_depth(
	detection: MarkerDetection,
	depth_m: np.ndarray,
	intrinsics: Intrinsics,
	*,
	shrink: float = 0.7,
	min_points: int = 30,
	min_valid_fraction: float = 0.5,
	max_rms_mm: float = 3.0,
) -> MarkerPose:
	"""Plane fit on the depth pixels inside the marker; falls back to the image pose when depth is unusable.

	Depth is unusable when too few pixels inside the marker have a measurement (``min_points`` and
	``min_valid_fraction`` of the area) or when they do not lie on one plane (RMS residual above ``max_rms_mm``,
	which happens at depth edges, near the image border or on reflective surfaces). Good markers fit to under a
	millimetre.

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
	usable = len(vs) >= min_points and len(vs) >= min_valid_fraction * float(mask.sum())
	if usable:
		z0 = depth_m[vs, us].astype(np.float64)
		pts0 = np.stack(
			[(us - intrinsics.ppx) * z0 / intrinsics.fx, (vs - intrinsics.ppy) * z0 / intrinsics.fy, z0], axis=1
		)
		normal0 = np.linalg.svd(pts0 - pts0.mean(axis=0), full_matrices=False)[2][-1]
		rms_mm = float(np.sqrt(np.mean(((pts0 - pts0.mean(axis=0)) @ normal0) ** 2))) * 1000.0
		usable = rms_mm <= max_rms_mm
	if not usable:
		position = np.asarray(detection.position_m, dtype=np.float64)
		normal = np.asarray(detection.rotation[:, 2], dtype=np.float64)
		return MarkerPose(
			id=detection.id,
			use=detection.use,
			size_mm=detection.size_mm,
			position_m=position,
			normal=normal,
			yaw_deg=yaw,
			source="image",
			corners_m=_corners_on_plane(corners, position, normal, intrinsics),
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
		corners_m=_corners_on_plane(corners, position, normal, intrinsics),
	)


def table_frame(plane: Plane, poses: dict[int, MarkerPose], anchors: tuple[int, int] = (16, 17)) -> TableFrame:
	"""Build the table frame from the fitted table plane and two anchor markers.

	z is the plane normal (towards the camera, so up). x runs from the first anchor to the second, projected into
	the plane, and the origin is the first anchor's foot point. When either anchor is missing the frame is still
	level (heights and tilts are right) but its x axis follows the camera's x axis and its origin is below the
	camera, so horizontal positions are then only comparable while the camera stays put.
	"""
	z = np.asarray(plane.normal, dtype=np.float64)
	z = z / np.linalg.norm(z)
	a, b = poses.get(anchors[0]), poses.get(anchors[1])
	if a is not None and b is not None:
		v = np.asarray(b.position_m) - np.asarray(a.position_m)
		x = v - (v @ z) * z
		if np.linalg.norm(x) > 1e-9:
			foot = np.asarray(a.position_m) - (float(z @ np.asarray(a.position_m)) + plane.offset) * z
			x = x / np.linalg.norm(x)
			return TableFrame(
				origin=foot, axes=np.stack([x, np.cross(z, x), z]), basis=f"anchors {anchors[0]}->{anchors[1]}"
			)
	x = np.array([1.0, 0.0, 0.0]) - z[0] * z
	x = x / np.linalg.norm(x)
	return TableFrame(origin=-plane.offset * z, axes=np.stack([x, np.cross(z, x), z]), basis="camera x axis")


def to_table_pose(pose: MarkerPose, frame: TableFrame) -> TablePose:
	"""Express a camera-space marker pose in the table frame."""
	if pose.corners_m is None:
		raise ValueError("marker pose has no corners; use refine_with_depth")
	normal = frame.direction(pose.normal)
	tilt = float(np.degrees(np.arccos(np.clip(normal[2], -1.0, 1.0))))
	x_axis = frame.direction(pose.corners_m[1] - pose.corners_m[0])
	return TablePose(
		id=pose.id,
		use=pose.use,
		size_mm=pose.size_mm,
		position_mm=frame.point(pose.position_m) * 1000.0,
		tilt_deg=tilt,
		yaw_deg=float(np.degrees(np.arctan2(x_axis[1], x_axis[0]))),
		facing_deg=float(np.degrees(np.arctan2(normal[1], normal[0]))) if tilt >= 10.0 else None,
		source=pose.source,
	)


def table_rotation(pose: MarkerPose, frame: TableFrame) -> np.ndarray:
	"""Marker orientation in the table frame: columns are its x (top edge), y and z (face normal) axes."""
	if pose.corners_m is None:
		raise ValueError("marker pose has no corners; use refine_with_depth")
	z = frame.direction(pose.normal)
	z = z / np.linalg.norm(z)
	x = frame.direction(pose.corners_m[1] - pose.corners_m[0])
	x = x - (x @ z) * z
	x = x / np.linalg.norm(x)
	return np.stack([x, np.cross(z, x), z], axis=1)


def compare_to_reference(
	current: dict[int, TablePose],
	reference: dict[int, TablePose],
	*,
	shift_tol_mm: float = 3.0,
	yaw_tol_deg: float = 1.0,
) -> dict[int, Delta]:
	"""Compare each reference marker with its current table-frame pose.

	A marker counts as moved when its centre shifted more than ``shift_tol_mm`` or its yaw changed more than
	``yaw_tol_deg``. Tilt change is reported but not used for the decision, because depth noise on small markers is
	of the order of a degree.
	"""
	out: dict[int, Delta] = {}
	for marker_id, ref in reference.items():
		cur = current.get(marker_id)
		if cur is None:
			out[marker_id] = Delta(id=marker_id, moved=False, missing=True, shift_mm=None, yaw_deg=None, tilt_deg=None)
			continue
		shift = float(np.linalg.norm(cur.position_mm - ref.position_mm))
		yaw = (cur.yaw_deg - ref.yaw_deg + 180.0) % 360.0 - 180.0
		out[marker_id] = Delta(
			id=marker_id,
			moved=shift > shift_tol_mm or abs(yaw) > yaw_tol_deg,
			missing=False,
			shift_mm=shift,
			yaw_deg=yaw,
			tilt_deg=abs(cur.tilt_deg - ref.tilt_deg),
		)
	return out


def save_reference(path: Path, poses: dict[int, TablePose], basis: str) -> None:
	"""Write table-frame marker poses as the alignment reference (JSON); ``basis`` records how the frame was built."""
	data = {
		"saved_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
		"frame": basis,
		"markers": {
			str(p.id): {
				"use": p.use,
				"size_mm": p.size_mm,
				"position_mm": [float(v) for v in p.position_mm],
				"tilt_deg": p.tilt_deg,
				"yaw_deg": p.yaw_deg,
				"facing_deg": p.facing_deg,
				"source": p.source,
			}
			for p in poses.values()
		},
	}
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(data, indent=1))


def load_reference(path: Path) -> dict[int, TablePose]:
	"""Read a reference written by :func:`save_reference`."""
	data = json.loads(path.read_text())
	return {
		int(k): TablePose(
			id=int(k),
			use=v["use"],
			size_mm=v["size_mm"],
			position_mm=np.array(v["position_mm"]),
			tilt_deg=v["tilt_deg"],
			yaw_deg=v["yaw_deg"],
			facing_deg=v["facing_deg"],
			source=v["source"],
		)
		for k, v in data["markers"].items()
	}
