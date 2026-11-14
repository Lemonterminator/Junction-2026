import cv2
import numpy as np
import pytest

from defect_sorter.geometry import Intrinsics
from defect_sorter.markers import (
	DICTIONARY_ID,
	MARKER_SET,
	detect_markers,
	marker_spec,
	render_marker_tile,
	render_sheet_pages,
)

DPI = 300
PX_PER_MM = DPI / 25.4
CAM = Intrinsics(fx=900.0, fy=900.0, ppx=640.0, ppy=360.0)


def _detect_raw(gray: np.ndarray) -> dict[int, np.ndarray]:
	detector = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(DICTIONARY_ID), cv2.aruco.DetectorParameters())
	corners, ids, _ = detector.detectMarkers(gray)
	return {} if ids is None else {int(i): c.reshape(4, 2) for i, c in zip(ids.ravel(), corners, strict=True)}


def _rotation(yaw_deg: float, tilt_deg: float) -> np.ndarray:
	"""Marker facing the camera (marker z towards -camera z), yawed in the image and tilted about camera x."""
	facing = np.diag([1.0, -1.0, -1.0])
	yaw = np.deg2rad(yaw_deg)
	rz = np.array([[np.cos(yaw), -np.sin(yaw), 0], [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]])
	t = np.deg2rad(tilt_deg)
	rx = np.array([[1, 0, 0], [0, np.cos(t), -np.sin(t)], [0, np.sin(t), np.cos(t)]])
	return rx @ rz @ facing


def _synthetic_view(marker_id: int, rotation: np.ndarray, translation_m: np.ndarray) -> np.ndarray:
	"""Project one printed tile into a 1280x720 camera image at a known pose."""
	spec = marker_spec(marker_id)
	tile = render_marker_tile(spec, px_per_mm=20.0)
	half_tile_m = tile.shape[0] / 20.0 / 1000.0 / 2.0
	corners_3d = np.array([[-1, 1, 0], [1, 1, 0], [1, -1, 0], [-1, -1, 0]], dtype=np.float64) * half_tile_m
	k = np.array([[CAM.fx, 0, CAM.ppx], [0, CAM.fy, CAM.ppy], [0, 0, 1]])
	rvec, _ = cv2.Rodrigues(rotation)
	img_pts, _ = cv2.projectPoints(corners_3d, rvec, translation_m, k, None)
	src = np.array([[0, 0], [tile.shape[1], 0], [tile.shape[1], tile.shape[0]], [0, tile.shape[0]]], dtype=np.float32)
	h = cv2.getPerspectiveTransform(src, img_pts.reshape(4, 2).astype(np.float32))
	canvas = np.full((720, 1280), 90, np.uint8)
	warped = cv2.warpPerspective(tile, h, (1280, 720), flags=cv2.INTER_LINEAR, borderValue=0)
	mask = cv2.warpPerspective(np.full(tile.shape, 255, np.uint8), h, (1280, 720), flags=cv2.INTER_NEAREST)
	canvas[mask > 0] = warped[mask > 0]
	return canvas


class TestMarkerSet:
	def test_ids_are_unique_and_valid_for_the_dictionary(self):
		ids = [m.id for m in MARKER_SET]
		assert len(ids) == len(set(ids))
		assert all(0 <= i < 50 for i in ids)

	def test_clamp_marker_fits_a_25_mm_face_with_its_margin(self):
		clamp = marker_spec(0)
		assert clamp.size_mm + 2 * clamp.margin_mm <= 25.0

	def test_unknown_id_raises(self):
		with pytest.raises(KeyError):
			marker_spec(49)


class TestSheet:
	def test_every_marker_is_printed_once_at_its_exact_size(self):
		pages = render_sheet_pages(dpi=DPI)
		found: dict[int, float] = {}
		for page in pages:
			assert page.shape == (round(297 * PX_PER_MM), round(210 * PX_PER_MM))
			for mid, c in _detect_raw(page).items():
				assert mid not in found, f"marker {mid} printed twice"
				found[mid] = float(np.mean([np.linalg.norm(c[i] - c[(i + 1) % 4]) for i in range(4)]))
		assert set(found) == {m.id for m in MARKER_SET}
		for m in MARKER_SET:
			assert found[m.id] == pytest.approx(m.size_mm * PX_PER_MM, abs=2.0)


class TestDetectMarkers:
	# Normal tolerance: a small marker seen face-on only constrains its out-of-plane tilt to ~10-15 degrees.
	@pytest.mark.parametrize(
		("marker_id", "yaw", "tilt", "t", "normal_tol_deg"),
		[
			(0, 0.0, 0.0, (0.0, 0.0, 0.40), 15.0),
			(10, 30.0, 0.0, (0.05, -0.03, 0.60), 2.0),
			(16, -20.0, 25.0, (-0.10, 0.05, 0.70), 2.0),
		],
	)
	def test_recovers_known_pose(
		self, marker_id: int, yaw: float, tilt: float, t: tuple[float, float, float], normal_tol_deg: float
	):
		rotation = _rotation(yaw, tilt)
		image = _synthetic_view(marker_id, rotation, np.array(t))

		found = detect_markers(image, CAM)

		assert [d.id for d in found] == [marker_id]
		d = found[0]
		# Sideways position is precise; distance from apparent size is only good to about 1 % of the range.
		np.testing.assert_allclose(d.position_m[:2], t[:2], atol=0.003)
		assert d.position_m[2] == pytest.approx(t[2], rel=0.01)
		assert d.rotation[2, 2] < 0, "printed face must point towards the camera"
		cos = np.clip(np.dot(d.rotation[:, 2], rotation[:, 2]), -1, 1)
		assert np.degrees(np.arccos(cos)) < normal_tol_deg
		assert d.size_mm == marker_spec(marker_id).size_mm

	def test_unknown_ids_in_view_are_ignored(self):
		image = np.full((720, 1280), 255, np.uint8)
		stray = cv2.aruco.generateImageMarker(cv2.aruco.getPredefinedDictionary(DICTIONARY_ID), 49, 120)
		image[300:420, 600:720] = stray

		assert detect_markers(image, CAM) == []

	def test_nothing_in_view_returns_empty(self):
		assert detect_markers(np.full((720, 1280), 128, np.uint8), CAM) == []
