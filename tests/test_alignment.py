import numpy as np
import pytest

from defect_sorter.alignment import (
	MarkerPose,
	compare_to_reference,
	load_reference,
	refine_with_depth,
	save_reference,
	tilt_deg,
)
from defect_sorter.geometry import Intrinsics
from defect_sorter.markers import MarkerDetection

INTR = Intrinsics(fx=900.0, fy=900.0, ppx=640.0, ppy=360.0)


def tilted_depth(tilt_deg_about_x: float, base_m: float = 0.6, shape: tuple[int, int] = (720, 1280)) -> np.ndarray:
	"""Depth of the plane z = base + tan(tilt) * y seen by the camera."""
	slope = np.tan(np.radians(tilt_deg_about_x))
	v = np.arange(shape[0], dtype=np.float64)[:, None]
	z = base_m / (1.0 - slope * (v - INTR.ppy) / INTR.fy)
	return np.repeat(z, shape[1], axis=1).astype(np.float32)


def detection(corners: list[tuple[float, float]], marker_id: int = 0) -> MarkerDetection:
	return MarkerDetection(
		id=marker_id,
		size_mm=18.0,
		use="follower clamp",
		corners_px=np.array(corners, dtype=np.float64),
		rotation=np.diag([1.0, -1.0, -1.0]),
		position_m=np.array([0.0, 0.0, 0.5]),
		reprojection_px=0.1,
	)


def pose(marker_id: int, xyz: tuple[float, float, float], yaw: float = 0.0, normal=(0.0, 0.0, -1.0)) -> MarkerPose:
	return MarkerPose(
		id=marker_id,
		use="test",
		size_mm=40.0,
		position_m=np.array(xyz),
		normal=np.array(normal),
		yaw_deg=yaw,
		source="depth",
	)


class TestTiltDeg:
	def test_parallel_and_flipped_normals_are_zero(self):
		assert tilt_deg(np.array([0, 0, -1.0]), np.array([0, 0, 1.0])) == pytest.approx(0.0, abs=1e-9)

	def test_ten_degrees(self):
		n = np.array([0.0, np.sin(np.radians(10)), -np.cos(np.radians(10))])
		assert tilt_deg(n, np.array([0, 0, -1.0])) == pytest.approx(10.0, abs=1e-6)


class TestRefineWithDepth:
	def test_flat_tilted_marker_gets_plane_tilt_and_centre_distance_from_depth(self):
		depth = tilted_depth(10.0)
		det = detection([(600, 320), (680, 320), (680, 400), (600, 400)])

		p = refine_with_depth(det, depth, INTR)

		assert p.source == "depth"
		assert tilt_deg(p.normal, np.array([0, 0, -1.0])) == pytest.approx(10.0, abs=0.3)
		assert p.normal[2] < 0
		# centre pixel (640, 360) is on the optical axis, where the plane is at 0.6 m
		np.testing.assert_allclose(p.position_m, [0.0, 0.0, 0.6], atol=0.002)
		assert p.yaw_deg == pytest.approx(0.0, abs=1e-6)

	def test_falls_back_to_image_pose_without_depth(self):
		depth = np.zeros((720, 1280), np.float32)
		det = detection([(600, 320), (680, 320), (680, 400), (600, 400)])

		p = refine_with_depth(det, depth, INTR)

		assert p.source == "image"
		np.testing.assert_allclose(p.position_m, det.position_m)
		np.testing.assert_allclose(p.normal, det.rotation[:, 2])

	def test_yaw_follows_the_top_edge(self):
		depth = tilted_depth(0.0)
		# top edge points down-right at 45 degrees in the image
		det = detection([(600, 300), (660, 360), (600, 420), (540, 360)])

		assert refine_with_depth(det, depth, INTR).yaw_deg == pytest.approx(45.0, abs=1e-6)


class TestCompareToReference:
	def test_reports_moved_marker_and_still_ones(self):
		reference = {16: pose(16, (0.0, 0.0, 0.6)), 0: pose(0, (0.10, 0.05, 0.62))}
		current = {16: pose(16, (0.0005, 0.0, 0.6)), 0: pose(0, (0.104, 0.05, 0.62), yaw=1.5)}

		deltas = compare_to_reference(current, reference)

		assert deltas[16].moved is False
		assert deltas[0].moved is True
		assert deltas[0].shift_mm == pytest.approx(4.0, abs=1e-6)
		assert deltas[0].yaw_deg == pytest.approx(1.5, abs=1e-9)

	def test_yaw_difference_wraps(self):
		reference = {12: pose(12, (0, 0, 0.6), yaw=179.0)}
		current = {12: pose(12, (0, 0, 0.6), yaw=-179.0)}
		assert compare_to_reference(current, reference)[12].yaw_deg == pytest.approx(2.0, abs=1e-9)

	def test_marker_missing_now_is_reported_as_missing(self):
		reference = {16: pose(16, (0, 0, 0.6))}
		assert compare_to_reference({}, reference)[16].missing is True


def test_reference_round_trips_through_json(tmp_path):
	poses = {0: pose(0, (0.1, 0.05, 0.62), yaw=12.5, normal=(0.0, 0.1, -0.995))}
	path = tmp_path / "ref.json"

	save_reference(path, poses)
	loaded = load_reference(path)

	assert set(loaded) == {0}
	np.testing.assert_allclose(loaded[0].position_m, poses[0].position_m)
	np.testing.assert_allclose(loaded[0].normal, poses[0].normal)
	assert loaded[0].yaw_deg == 12.5
