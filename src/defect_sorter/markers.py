"""ArUco markers for the sorting cell: the printed set, the print sheet, and pose detection.

The printed sizes and the detection code share :data:`MARKER_SET`, so a marker's physical size is defined once.
Poses are in the camera frame (x right, y down, z forward, metres); each marker's own frame has x to the right,
y up and z out of the printed face, centred on the black square.

Print the sheet at 100 % ("Actual size"), check the 100 mm ruler, and keep the white margin around each marker:

	uv run sorter-marker-sheet --out data/markers/aruco_sheet.pdf
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from defect_sorter.geometry import Intrinsics

logger = logging.getLogger(__name__)

DICTIONARY_ID = cv2.aruco.DICT_4X4_50
_CELLS = 6  # 4x4 data bits plus the black border


@dataclass(frozen=True)
class MarkerSpec:
	"""One printed marker.

	Parameters
	----------
	id : int
		ArUco id in :data:`DICTIONARY_ID`.
	size_mm : float
		Side of the black square as printed.
	margin_mm : float
		White margin printed around the black square; cut along the outer line.
	use : str
		Intended placement.
	"""

	id: int
	size_mm: float
	margin_mm: float
	use: str


MARKER_SET: tuple[MarkerSpec, ...] = (
	MarkerSpec(16, 60.0, 8.0, "table anchor"),
	MarkerSpec(17, 60.0, 8.0, "table anchor"),
	MarkerSpec(10, 40.0, 6.0, "green bowl"),
	MarkerSpec(11, 40.0, 6.0, "pink bowl"),
	MarkerSpec(12, 40.0, 6.0, "workspace corner"),
	MarkerSpec(13, 40.0, 6.0, "workspace corner"),
	MarkerSpec(14, 40.0, 6.0, "workspace corner"),
	MarkerSpec(15, 40.0, 6.0, "spare"),
	MarkerSpec(4, 30.0, 5.0, "gripper top"),
	MarkerSpec(5, 30.0, 5.0, "gripper side"),
	MarkerSpec(6, 30.0, 5.0, "gripper side"),
	MarkerSpec(7, 30.0, 5.0, "gripper side"),
	MarkerSpec(8, 30.0, 5.0, "forearm"),
	MarkerSpec(9, 30.0, 5.0, "upper arm"),
	MarkerSpec(18, 30.0, 5.0, "spare"),
	MarkerSpec(19, 30.0, 5.0, "spare"),
	MarkerSpec(2, 20.0, 4.0, "clamp if >28mm"),
	MarkerSpec(3, 20.0, 4.0, "spare"),
	MarkerSpec(0, 18.0, 3.5, "follower clamp"),
	MarkerSpec(1, 18.0, 3.5, "leader base"),
)
_BY_ID = {m.id: m for m in MARKER_SET}


def marker_spec(marker_id: int) -> MarkerSpec:
	"""Return the spec of a marker in :data:`MARKER_SET`; raises ``KeyError`` for unknown ids."""
	return _BY_ID[marker_id]


@dataclass(frozen=True)
class MarkerDetection:
	"""A known marker found in an image, with its pose in the camera frame."""

	id: int
	size_mm: float
	use: str
	corners_px: np.ndarray
	rotation: np.ndarray
	position_m: np.ndarray
	reprojection_px: float


def _dictionary() -> cv2.aruco.Dictionary:
	return cv2.aruco.getPredefinedDictionary(DICTIONARY_ID)


def render_marker_tile(spec: MarkerSpec, px_per_mm: float) -> np.ndarray:
	"""Grayscale image of one marker with its white margin, at ``px_per_mm`` resolution."""
	marker_px = round(spec.size_mm * px_per_mm)
	margin_px = round(spec.margin_mm * px_per_mm)
	bits = cv2.aruco.generateImageMarker(_dictionary(), spec.id, _CELLS)
	marker = cv2.resize(bits, (marker_px, marker_px), interpolation=cv2.INTER_NEAREST)
	tile = np.full((marker_px + 2 * margin_px,) * 2, 255, np.uint8)
	tile[margin_px : margin_px + marker_px, margin_px : margin_px + marker_px] = marker
	return tile


def _put_text(img: np.ndarray, text: str, org: tuple[int, int], height_px: int) -> int:
	scale = height_px / 22.0
	thickness = max(1, round(scale * 1.6))
	cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, 0, thickness, cv2.LINE_AA)
	return cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)[0][0]


def _draw_ruler(page: np.ndarray, x0: int, y0: int, px_per_mm: float) -> None:
	length = round(100 * px_per_mm)
	cv2.line(page, (x0, y0), (x0 + length, y0), 0, 3)
	for mm in range(0, 101, 10):
		x = x0 + round(mm * px_per_mm)
		cv2.line(page, (x, y0), (x, y0 - round((4 if mm % 50 == 0 else 2) * px_per_mm)), 0, 3)
	_put_text(
		page,
		"100 mm - check with a ruler; print at 100% / Actual size",
		(x0, y0 + round(6 * px_per_mm)),
		round(2.6 * px_per_mm),
	)


def render_sheet_pages(
	specs: tuple[MarkerSpec, ...] = MARKER_SET,
	*,
	dpi: int = 300,
	page_mm: tuple[float, float] = (210.0, 297.0),
	margin_mm: float = 12.0,
) -> list[np.ndarray]:
	"""Lay the markers out on A4 pages (grayscale, ``dpi`` resolution), largest first.

	Each marker gets a thin cut line around its white margin and a label with id, size and use.
	"""
	ppm = dpi / 25.4
	width, height = round(page_mm[0] * ppm), round(page_mm[1] * ppm)
	left, top = round(margin_mm * ppm), round((margin_mm + 8) * ppm)
	bottom = height - round((margin_mm + 16) * ppm)
	gap, label_h = round(5 * ppm), round(2.4 * ppm)
	cell_min_w = round(26 * ppm)

	pages: list[np.ndarray] = []
	page = None
	x = y = row_h = 0

	def new_page() -> np.ndarray:
		p = np.full((height, width), 255, np.uint8)
		pages.append(p)
		return p

	for spec in sorted(specs, key=lambda s: (-s.size_mm, s.id)):
		tile = render_marker_tile(spec, ppm)
		th, tw = tile.shape
		cell_w = max(tw, cell_min_w)
		cell_h = th + 2 * label_h + round(2.5 * ppm)
		if page is None:
			page, x, y, row_h = new_page(), left, top, 0
		if x + cell_w > width - left:
			x, y, row_h = left, y + row_h + gap, 0
		if y + cell_h > bottom:
			page, x, y, row_h = new_page(), left, top, 0
		ox = x + (cell_w - tw) // 2
		page[y : y + th, ox : ox + tw] = tile
		cv2.rectangle(page, (ox - 1, y - 1), (ox + tw, y + th), 170, 1)
		_put_text(page, f"ID {spec.id}  {spec.size_mm:g} mm", (x, y + th + label_h + round(0.6 * ppm)), label_h)
		_put_text(page, spec.use, (x, y + th + 2 * label_h + round(1.4 * ppm)), label_h)
		x += cell_w + gap
		row_h = max(row_h, cell_h)

	for i, p in enumerate(pages, start=1):
		_put_text(
			p,
			f"Junction 2026 sorting cell - ArUco DICT_4X4_50 - page {i}/{len(pages)}",
			(left, round((margin_mm + 2) * ppm)),
			round(3.2 * ppm),
		)
		_draw_ruler(p, left, height - round((margin_mm + 8) * ppm), ppm)
	return pages


def _object_points(size_mm: float) -> np.ndarray:
	h = size_mm / 2000.0
	return np.array([[-h, h, 0], [h, h, 0], [h, -h, 0], [-h, -h, 0]], dtype=np.float64)


def _best_square_pose(
	obj: np.ndarray, img_pts: np.ndarray, k: np.ndarray, dist: np.ndarray
) -> tuple[np.ndarray, np.ndarray, float] | None:
	"""Pose of a square marker, resolving the two-fold ambiguity of planar PnP.

	A square seen nearly face-on has two poses that reproject almost equally well, and IPPE returns only
	poses facing away from the camera when the square is face-on and aligned with the image. Candidates come
	from IPPE_SQUARE and SQPNP; only poses whose printed face points towards the camera are kept, then the
	lowest reprojection error wins.
	"""
	candidates: list[tuple[np.ndarray, np.ndarray]] = []
	for flag in (cv2.SOLVEPNP_IPPE_SQUARE, cv2.SOLVEPNP_SQPNP):
		n, rvecs, tvecs, _ = cv2.solvePnPGeneric(obj, img_pts, k, dist, flags=flag)
		candidates.extend(zip(rvecs[:n], tvecs[:n], strict=True))
	best = None
	for rvec, tvec in candidates:
		rotation = cv2.Rodrigues(rvec)[0]
		if rotation[2, 2] >= 0:  # face points away from the camera
			continue
		proj, _ = cv2.projectPoints(obj, rvec, tvec, k, dist)
		err = float(np.mean(np.linalg.norm(proj.reshape(4, 2) - img_pts, axis=1)))
		if best is None or err < best[2]:
			best = (rotation, tvec.ravel(), err)
	return best


def detect_markers(
	image: np.ndarray,
	intrinsics: Intrinsics,
	*,
	specs: tuple[MarkerSpec, ...] = MARKER_SET,
	dist_coeffs: np.ndarray | None = None,
) -> list[MarkerDetection]:
	"""Find markers of ``specs`` in an image and estimate each pose from its printed size.

	Parameters
	----------
	image : numpy.ndarray
		Grayscale or BGR image.
	intrinsics : Intrinsics
		Intrinsics of ``image``.
	specs : tuple of MarkerSpec
		Known markers; ids not in it are ignored.
	dist_coeffs : numpy.ndarray, optional
		Lens distortion; ``None`` for an undistorted image.

	Returns
	-------
	list of MarkerDetection
		Sorted by id. Empty when nothing known is in view.

	Notes
	-----
	Sideways position is precise (millimetres). Distance from apparent size is good to about 1 % of the range.
	Out-of-plane tilt is good to about 2 degrees for markers that are large in the image or seen at an angle,
	but only to about 10-15 degrees for small markers seen face-on (an 18 mm marker at 0.4 m). For flat
	markers under the top camera, take tilt and distance from the aligned depth image instead.
	"""
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
	params = cv2.aruco.DetectorParameters()
	params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
	corners, ids, _ = cv2.aruco.ArucoDetector(_dictionary(), params).detectMarkers(gray)
	if ids is None:
		return []
	by_id = {s.id: s for s in specs}
	k = np.array([[intrinsics.fx, 0, intrinsics.ppx], [0, intrinsics.fy, intrinsics.ppy], [0, 0, 1]], dtype=np.float64)
	dist = np.zeros(5) if dist_coeffs is None else dist_coeffs
	found: list[MarkerDetection] = []
	for marker_id, c in zip(ids.ravel().tolist(), corners, strict=True):
		spec = by_id.get(int(marker_id))
		if spec is None:
			continue
		img_pts = c.reshape(4, 2).astype(np.float64)
		pose = _best_square_pose(_object_points(spec.size_mm), img_pts, k, dist)
		if pose is None:
			continue
		rotation, position, err = pose
		found.append(
			MarkerDetection(
				id=spec.id,
				size_mm=spec.size_mm,
				use=spec.use,
				corners_px=img_pts,
				rotation=rotation,
				position_m=position,
				reprojection_px=err,
			)
		)
	return sorted(found, key=lambda d: d.id)


def in_plane_yaw_deg(rotation: np.ndarray) -> float:
	"""Angle of the marker's x axis in the image plane, in degrees (0 = pointing right, positive = clockwise on screen)."""
	return float(np.degrees(np.arctan2(rotation[1, 0], rotation[0, 0])))


def main(argv: list[str] | None = None) -> None:
	"""Write the print sheet as a PDF (pages at exact physical size)."""
	parser = argparse.ArgumentParser(description="Write the ArUco print sheet for the sorting cell")
	parser.add_argument("--out", type=Path, default=Path("data/markers/aruco_sheet.pdf"))
	parser.add_argument("--dpi", type=int, default=300)
	args = parser.parse_args(argv)
	from PIL import Image

	pages = [Image.fromarray(p) for p in render_sheet_pages(dpi=args.dpi)]
	args.out.parent.mkdir(parents=True, exist_ok=True)
	pages[0].save(args.out, save_all=True, append_images=pages[1:], resolution=float(args.dpi))
	sys.stdout.write(f"wrote {len(pages)} page(s) to {args.out}\n")
	for spec in sorted(MARKER_SET, key=lambda s: (-s.size_mm, s.id)):
		sys.stdout.write(f"  ID {spec.id:2d}  {spec.size_mm:4.0f} mm  {spec.use}\n")


if __name__ == "__main__":
	main()
