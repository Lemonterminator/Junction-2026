import numpy as np
import pytest

from defect_sorter.alignment import (
	MarkerPose,
	TablePose,
	compare_to_reference,
	held_table_frame,
	load_reference,
	load_table_frame,
	refine_with_depth,
	save_reference,
	save_table_frame,
	table_frame,
	table_rotation,
	tilt_deg,
	to_table_pose,
)
from defect_sorter.geometry import Intrinsics, Plane
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


def pose(marker_id: int, xyz: tuple[float, float, float], normal=(0.0, 0.0, -1.0), corners=None) -> MarkerPose:
	return MarkerPose(
		id=marker_id,
		use="test",
		size_mm=40.0,
		position_m=np.array(xyz, dtype=float),
		normal=np.array(normal, dtype=float),
		yaw_deg=0.0,
		source="depth",
		corners_m=None if corners is None else np.array(corners, dtype=float),
	)


def table_pose(marker_id: int, xyz_mm: tuple[float, float, float], yaw: float = 0.0, tilt: float = 0.0) -> TablePose:
	return TablePose(
		id=marker_id,
		use="test",
		size_mm=40.0,
		position_mm=np.array(xyz_mm, dtype=float),
		tilt_deg=tilt,
		yaw_deg=yaw,
		facing_deg=None,
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

	def test_depth_with_a_step_inside_the_marker_is_rejected(self):
		depth = tilted_depth(0.0)
		depth[:, 640:] += 1.2  # a depth edge runs through the middle of the marker
		det = detection([(600, 320), (680, 320), (680, 400), (600, 400)])

		p = refine_with_depth(det, depth, INTR)

		assert p.source == "image"

	def test_mostly_missing_depth_is_rejected(self):
		depth = tilted_depth(0.0)
		depth[300:420, 620:700] = 0.0
		depth[:, :] = np.where(np.arange(1280)[None, :] % 3 == 0, depth, 0.0)  # two thirds of the pixels invalid
		det = detection([(600, 320), (680, 320), (680, 400), (600, 400)])

		assert refine_with_depth(det, depth, INTR, min_points=10).source == "image"

	def test_small_depth_noise_is_accepted(self):
		rng = np.random.default_rng(0)
		depth = tilted_depth(5.0) + rng.normal(0, 0.0007, (720, 1280)).astype(np.float32)
		det = detection([(600, 320), (680, 320), (680, 400), (600, 400)])

		assert refine_with_depth(det, depth, INTR).source == "depth"

	def test_corners_get_3d_coordinates_on_the_marker_plane(self):
		depth = tilted_depth(10.0)
		det = detection([(600, 320), (680, 320), (680, 400), (600, 400)])

		p = refine_with_depth(det, depth, INTR)

		assert p.corners_m.shape == (4, 3)
		off_plane = (p.corners_m - p.position_m) @ p.normal
		np.testing.assert_allclose(off_plane, 0.0, atol=1e-9)
		# 80 px at ~0.6 m with f=900 px is ~53 mm along the top edge
		assert np.linalg.norm(p.corners_m[1] - p.corners_m[0]) == pytest.approx(80 * 0.6 / 900, rel=0.03)

	def test_corners_exist_in_the_image_fallback_too(self):
		det = detection([(600, 320), (680, 320), (680, 400), (600, 400)])

		p = refine_with_depth(det, np.zeros((720, 1280), np.float32), INTR)

		assert p.source == "image"
		assert p.corners_m.shape == (4, 3)

	def test_yaw_follows_the_top_edge(self):
		depth = tilted_depth(0.0)
		# top edge points down-right at 45 degrees in the image
		det = detection([(600, 300), (660, 360), (600, 420), (540, 360)])

		assert refine_with_depth(det, depth, INTR).yaw_deg == pytest.approx(45.0, abs=1e-6)


class TestCompareToReference:
	def test_reports_moved_marker_and_still_ones(self):
		reference = {16: table_pose(16, (0.0, 0.0, 0.0)), 0: table_pose(0, (100.0, 50.0, 20.0))}
		current = {16: table_pose(16, (0.5, 0.0, 0.0)), 0: table_pose(0, (104.0, 50.0, 20.0), yaw=1.5)}

		deltas = compare_to_reference(current, reference)

		assert deltas[16].moved is False
		assert deltas[0].moved is True
		assert deltas[0].shift_mm == pytest.approx(4.0, abs=1e-6)
		assert deltas[0].yaw_deg == pytest.approx(1.5, abs=1e-9)

	def test_yaw_difference_wraps(self):
		reference = {12: table_pose(12, (0, 0, 0), yaw=179.0)}
		current = {12: table_pose(12, (0, 0, 0), yaw=-179.0)}
		assert compare_to_reference(current, reference)[12].yaw_deg == pytest.approx(2.0, abs=1e-9)

	def test_marker_missing_now_is_reported_as_missing(self):
		reference = {16: table_pose(16, (0, 0, 0))}
		assert compare_to_reference({}, reference)[16].missing is True


def test_reference_round_trips_through_json(tmp_path):
	poses = {
		0: TablePose(
			id=0,
			use="follower clamp",
			size_mm=18.0,
			position_mm=np.array([100.0, 50.0, 20.0]),
			tilt_deg=88.5,
			yaw_deg=12.5,
			facing_deg=-77.0,
			source="depth",
		)
	}
	path = tmp_path / "ref.json"

	save_reference(path, poses, basis="anchors 16->17")
	loaded = load_reference(path)

	assert set(loaded) == {0}
	np.testing.assert_allclose(loaded[0].position_mm, poses[0].position_mm)
	assert loaded[0].tilt_deg == 88.5
	assert loaded[0].yaw_deg == 12.5
	assert loaded[0].facing_deg == -77.0


# ---- table frame: the camera's own pose must not matter -------------------------------------------------------


def _rot_x(deg: float) -> np.ndarray:
	a = np.radians(deg)
	return np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])


def _rot_z(deg: float) -> np.ndarray:
	a = np.radians(deg)
	return np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])


def _camera_view(rotation: np.ndarray, translation: np.ndarray):
	"""Table-frame world (x right, y forward, z up) seen by a camera whose pose is (rotation, translation).

	Returns the table plane and a function placing a marker, given in table coordinates, into camera coordinates.
	"""
	normal = rotation @ np.array([0.0, 0.0, 1.0])  # table up, as seen by the camera
	plane = Plane(normal=normal, offset=-float(normal @ translation), inlier_fraction=1.0)
	assert plane.offset > 0, "camera must be on the positive side of the table"

	def place(
		marker_id: int, pos_table_m, yaw_deg: float = 0.0, tilt_deg_: float = 0.0, size_m: float = 0.04
	) -> MarkerPose:
		# marker frame: x along the printed top edge, z out of the printed face; tilt about the marker's x axis
		r_marker = _rot_z(yaw_deg) @ _rot_x(tilt_deg_)
		half = size_m / 2
		local = np.array([[-half, half, 0], [half, half, 0], [half, -half, 0], [-half, -half, 0]])
		corners_table = np.asarray(pos_table_m) + local @ r_marker.T
		corners_cam = corners_table @ rotation.T + translation
		return MarkerPose(
			id=marker_id,
			use="test",
			size_mm=size_m * 1000,
			position_m=rotation @ np.asarray(pos_table_m, dtype=float) + translation,
			normal=rotation @ (r_marker @ np.array([0.0, 0.0, 1.0])),
			yaw_deg=0.0,
			source="depth",
			corners_m=corners_cam,
		)

	return plane, place


# a camera 0.7 m from the table looking across it (tilted 30 degrees), and a second, different mounting
CAMERA_A = (_rot_x(180.0 - 30.0), np.array([0.0, 0.0, 0.0]) + _rot_x(180.0 - 30.0) @ np.array([0.0, 0.0, -0.7]))
CAMERA_B = (
	_rot_z(25.0) @ _rot_x(180.0 + 12.0),
	np.array([0.05, -0.02, 0.0]) + (_rot_z(25.0) @ _rot_x(180.0 + 12.0)) @ np.array([0.1, 0.2, -0.9]),
)


class TestTableFrame:
	@pytest.mark.parametrize("camera", [CAMERA_A, CAMERA_B])
	def test_recovers_table_coordinates_whatever_the_camera_pose(self, camera):
		plane, place = _camera_view(*camera)
		poses = {
			16: place(16, (0.0, 0.0, 0.0)),
			17: place(17, (0.40, 0.0, 0.0)),
			10: place(10, (0.12, 0.25, 0.0), yaw_deg=30.0),
			0: place(0, (0.20, -0.15, 0.03), yaw_deg=-20.0, tilt_deg_=90.0),
		}

		frame = table_frame(plane, poses)
		got = {i: to_table_pose(p, frame) for i, p in poses.items()}

		assert frame.basis == "anchors 16->17"
		np.testing.assert_allclose(got[16].position_mm, [0, 0, 0], atol=1e-6)
		np.testing.assert_allclose(got[17].position_mm, [400, 0, 0], atol=1e-6)
		np.testing.assert_allclose(got[10].position_mm, [120, 250, 0], atol=1e-6)
		np.testing.assert_allclose(got[0].position_mm, [200, -150, 30], atol=1e-6)
		assert got[10].tilt_deg == pytest.approx(0.0, abs=1e-6)
		assert got[10].yaw_deg == pytest.approx(30.0, abs=1e-6)
		assert got[10].facing_deg is None  # flat marker: no horizontal facing direction
		assert got[0].tilt_deg == pytest.approx(90.0, abs=1e-6)

	def test_two_camera_mountings_give_identical_poses_and_no_drift(self):
		world = {16: ((0.0, 0.0, 0.0), 0.0, 0.0), 17: ((0.40, 0.0, 0.0), 0.0, 0.0), 12: ((0.15, 0.18, 0.0), 45.0, 0.0)}
		tables = []
		for camera in (CAMERA_A, CAMERA_B):
			plane, place = _camera_view(*camera)
			poses = {i: place(i, pos, yaw, tilt) for i, (pos, yaw, tilt) in world.items()}
			frame = table_frame(plane, poses)
			tables.append({i: to_table_pose(p, frame) for i, p in poses.items()})

		deltas = compare_to_reference(tables[1], tables[0])

		assert all(not d.moved and not d.missing for d in deltas.values())
		assert all(d.shift_mm < 1e-6 for d in deltas.values())

	def test_a_marker_that_really_moved_is_flagged_after_the_camera_was_moved_too(self):
		plane_a, place_a = _camera_view(*CAMERA_A)
		reference_poses = {
			16: place_a(16, (0, 0, 0)),
			17: place_a(17, (0.4, 0, 0)),
			0: place_a(0, (0.2, -0.15, 0.03), yaw_deg=-20.0, tilt_deg_=90.0),
		}
		reference = {i: to_table_pose(p, table_frame(plane_a, reference_poses)) for i, p in reference_poses.items()}

		plane_b, place_b = _camera_view(*CAMERA_B)
		now_poses = {
			16: place_b(16, (0, 0, 0)),
			17: place_b(17, (0.4, 0, 0)),
			0: place_b(0, (0.2, -0.15 + 0.010, 0.03), yaw_deg=-20.0, tilt_deg_=90.0),
		}
		now = {i: to_table_pose(p, table_frame(plane_b, now_poses)) for i, p in now_poses.items()}

		deltas = compare_to_reference(now, reference)

		assert deltas[16].moved is False
		assert deltas[0].moved is True
		assert deltas[0].shift_mm == pytest.approx(10.0, abs=1e-6)

	def test_vertical_marker_reports_which_way_it_faces(self):
		plane, place = _camera_view(*CAMERA_A)
		poses = {
			16: place(16, (0, 0, 0)),
			17: place(17, (0.4, 0, 0)),
			0: place(0, (0.1, 0.1, 0.03), yaw_deg=0.0, tilt_deg_=90.0),
		}
		frame = table_frame(plane, poses)

		clamp = to_table_pose(poses[0], frame)

		# tilting a flat marker by 90 degrees about its x axis turns its face towards -y of the table frame
		assert clamp.facing_deg == pytest.approx(-90.0, abs=1e-6)

	def test_without_anchors_the_frame_is_level_but_uses_the_camera_x_axis(self):
		plane, place = _camera_view(*CAMERA_A)
		poses = {10: place(10, (0.12, 0.25, 0.0))}

		frame = table_frame(plane, poses)
		got = to_table_pose(poses[10], frame)

		assert frame.basis == "camera x axis"
		assert got.position_mm[2] == pytest.approx(0.0, abs=1e-6)  # height is still correct
		assert got.tilt_deg == pytest.approx(0.0, abs=1e-6)


def test_table_rotation_of_a_flat_yawed_marker_and_an_upright_one():
	plane, place = _camera_view(*CAMERA_A)
	poses = {
		16: place(16, (0, 0, 0)),
		17: place(17, (0.4, 0, 0)),
		10: place(10, (0.1, 0.2, 0), yaw_deg=30.0),
		0: place(0, (0.2, 0.1, 0.03), yaw_deg=0.0, tilt_deg_=90.0),
	}
	frame = table_frame(plane, poses)

	np.testing.assert_allclose(table_rotation(poses[10], frame), _rot_z(30.0), atol=1e-9)
	np.testing.assert_allclose(table_rotation(poses[0], frame), _rot_x(90.0), atol=1e-9)


FLAT = Plane(normal=np.array([0.0, 0.0, -1.0]), offset=0.6, inlier_fraction=1.0)
FIXED = {16: (-0.10, 0.05, 0.6), 17: (0.17, 0.05, 0.6), 18: (0.03, 0.12, 0.6), 7: (0.03, 0.20, 0.6)}


def seen(*ids: int, shift=(0.0, 0.0, 0.0)) -> dict[int, MarkerPose]:
	return {i: pose(i, tuple(np.add(FIXED[i], shift))) for i in ids}


class TestHeldTableFrame:
	def test_saved_frame_round_trips(self, tmp_path):
		frame = table_frame(FLAT, seen(16, 17))
		save_table_frame(tmp_path / "frame.json", frame, seen(16, 17, 18, 7))

		loaded, markers = load_table_frame(tmp_path / "frame.json")

		np.testing.assert_allclose(loaded.origin, frame.origin)
		np.testing.assert_allclose(loaded.axes, frame.axes)
		assert loaded.basis == frame.basis
		assert set(markers) == {16, 17, 18, 7}

	def test_a_hidden_anchor_is_bridged_while_the_other_fixed_tags_have_not_moved(self, tmp_path):
		frame = table_frame(FLAT, seen(16, 17))
		save_table_frame(tmp_path / "frame.json", frame, seen(16, 17, 18, 7))
		saved, markers = load_table_frame(tmp_path / "frame.json")

		held = held_table_frame(saved, markers, seen(17, 18, 7, shift=(0.002, -0.001, 0.0)))  # 16 hidden

		assert held is not None
		np.testing.assert_allclose(held.origin, frame.origin)
		assert "held" in held.basis

	def test_a_moved_camera_is_not_bridged(self, tmp_path):
		frame = table_frame(FLAT, seen(16, 17))
		save_table_frame(tmp_path / "frame.json", frame, seen(16, 17, 18, 7))
		saved, markers = load_table_frame(tmp_path / "frame.json")

		assert held_table_frame(saved, markers, seen(17, 18, 7, shift=(0.012, 0.0, 0.0))) is None

	def test_one_visible_tag_is_not_enough_proof(self, tmp_path):
		frame = table_frame(FLAT, seen(16, 17))
		save_table_frame(tmp_path / "frame.json", frame, seen(16, 17, 18, 7))
		saved, markers = load_table_frame(tmp_path / "frame.json")

		assert held_table_frame(saved, markers, seen(17)) is None
