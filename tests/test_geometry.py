import numpy as np
import pytest

from defect_sorter.geometry import Intrinsics, Plane, camera_tilt, deproject, fit_table_plane, height_above

INTR = Intrinsics(fx=600.0, fy=600.0, ppx=320.0, ppy=240.0)


def tilted_table_depth(h: int = 480, w: int = 640, base: float = 0.6, slope: float = 0.1) -> np.ndarray:
	"""Depth of the plane z = base + slope * y seen by a pinhole camera at the origin."""
	v = np.arange(h, dtype=np.float64)[:, None]
	# z = base + slope * (v - ppy) * z / fy, so z = base / (1 - slope * (v - ppy) / fy)
	z = base / (1.0 - slope * (v - INTR.ppy) / INTR.fy)
	return np.repeat(z, w, axis=1).astype(np.float32)


class TestDeproject:
	def test_principal_point_maps_to_optical_axis(self):
		depth = np.full((480, 640), 0.5, np.float32)
		pts = deproject(depth, INTR)
		assert pts.shape == (480, 640, 3)
		np.testing.assert_allclose(pts[240, 320], [0.0, 0.0, 0.5], atol=1e-6)

	def test_offset_pixel_scales_with_depth(self):
		depth = np.full((480, 640), 0.6, np.float32)
		pts = deproject(depth, INTR)
		# 60 px right of centre at f=600 px -> x = 0.1 * z
		np.testing.assert_allclose(pts[240, 380], [0.06, 0.0, 0.6], atol=1e-6)


class TestTablePlane:
	def test_recovers_tilted_plane_and_orients_height_towards_camera(self):
		depth = tilted_table_depth()
		pts = deproject(depth, INTR).reshape(-1, 3)
		plane = fit_table_plane(pts)
		assert plane.inlier_fraction > 0.99
		# camera (origin) is on the positive side, at the table's perpendicular distance
		expected_normal = np.array([0.0, -0.1, 1.0]) / np.sqrt(1.01)
		np.testing.assert_allclose(np.abs(plane.normal), np.abs(expected_normal), atol=1e-3)
		assert plane.offset == pytest.approx(0.6 / np.sqrt(1.01), abs=1e-3)

	def test_box_on_table_has_its_height(self):
		depth = np.full((480, 640), 0.6, np.float32)
		depth[200:260, 300:360] = 0.55  # 5 cm box, camera looking straight down
		pts = deproject(depth, INTR)
		plane = fit_table_plane(pts.reshape(-1, 3))
		h = height_above(pts, plane)
		assert h[230, 330] == pytest.approx(0.05, abs=1e-4)
		assert h[50, 50] == pytest.approx(0.0, abs=1e-4)

	def test_fit_is_deterministic_for_a_seed(self):
		rng = np.random.default_rng(1)
		depth = (np.full((120, 160), 0.6) + rng.normal(0, 0.002, (120, 160))).astype(np.float32)
		pts = deproject(depth, INTR).reshape(-1, 3)
		a = fit_table_plane(pts, seed=7)
		b = fit_table_plane(pts, seed=7)
		np.testing.assert_array_equal(a.normal, b.normal)
		assert a.offset == b.offset

	def test_rejects_too_few_points(self):
		with pytest.raises(ValueError, match="at least 3"):
			fit_table_plane(np.zeros((2, 3)))


class TestCameraTilt:
	def test_level_camera_has_no_tilt(self):
		tilt = camera_tilt(Plane(normal=np.array([0.0, 0.0, -1.0]), offset=0.6, inlier_fraction=1.0))
		assert tilt.total_deg == pytest.approx(0.0, abs=1e-9)
		assert tilt.pitch_deg == pytest.approx(0.0, abs=1e-9)
		assert tilt.roll_deg == pytest.approx(0.0, abs=1e-9)

	def test_table_farther_at_the_bottom_of_the_image(self):
		# plane z = 0.6 + 0.1 * y: the bottom of the image (y > 0) is farther away
		pts = deproject(tilted_table_depth(), INTR).reshape(-1, 3)
		tilt = camera_tilt(fit_table_plane(pts))
		assert tilt.pitch_deg == pytest.approx(np.degrees(np.arctan(0.1)), abs=0.05)
		assert tilt.roll_deg == pytest.approx(0.0, abs=0.05)
		assert tilt.far_edge == "bottom"

	def test_table_farther_on_the_right(self):
		n = np.array([0.2, 0.0, -1.0])
		tilt = camera_tilt(Plane(normal=n / np.linalg.norm(n), offset=0.6, inlier_fraction=1.0))
		assert tilt.roll_deg == pytest.approx(np.degrees(np.arctan(0.2)), abs=1e-6)
		assert tilt.far_edge == "right"
