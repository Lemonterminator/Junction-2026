"""Tests for defect_sorter.presentation: defect faces, show points, view scoring, pose order, camera checks."""

from __future__ import annotations

import math

import numpy as np
import pytest

from defect_sorter.presentation import (
	FACES,
	camera_view_ok,
	defect_strokes,
	face_frame,
	order_show_poses,
	show_points,
	view_cosine,
)

SIZE = (0.0636, 0.0318, 0.0192)


def test_six_faces_cover_every_axis_and_sign():
	assert sorted(FACES) == sorted((a, s) for a in range(3) for s in (-1, 1))


@pytest.mark.parametrize("face", range(6))
def test_face_frame_sits_on_the_brick_surface_with_outward_normal(face):
	axis, sign = FACES[face]
	centre, normal, u, v = face_frame(SIZE, face)
	expected_normal = np.zeros(3)
	expected_normal[axis] = sign
	np.testing.assert_allclose(normal, expected_normal)
	np.testing.assert_allclose(centre, expected_normal * SIZE[axis] / 2)
	# in-plane axes are unit, orthogonal to each other and to the normal, and right-handed with it
	for w in (u, v):
		assert math.isclose(np.linalg.norm(w), 1.0)
		assert abs(w @ normal) < 1e-12
	assert abs(u @ v) < 1e-12
	np.testing.assert_allclose(np.cross(u, v), normal)


def test_defect_strokes_form_a_cross_inside_the_face():
	# long side face (+y): in-plane extents 63.6 mm along x and 19.2 mm along z
	face = FACES.index((1, 1))
	strokes = defect_strokes(SIZE, face, fill=0.7)
	assert len(strokes) == 2
	(c1, x1, y1, half1), (c2, x2, _, half2) = strokes
	np.testing.assert_allclose(c1, [0.0, SIZE[1] / 2, 0.0])
	np.testing.assert_allclose(c2, c1)
	# strokes are perpendicular diagonals lying in the face plane, their y axis is the face normal x stroke
	assert abs(x1 @ x2) < 1e-12
	assert abs(x1[1]) < 1e-12
	assert abs(x2[1]) < 1e-12
	np.testing.assert_allclose(np.cross(x1, y1), [0, 1, 0], atol=1e-12)
	# half length: 0.7 of the smaller in-plane half extent (9.6 mm), along the diagonal
	assert math.isclose(half1, 0.7 * 0.0096 * math.sqrt(2))
	assert half1 == half2


def test_show_points_lie_near_the_optical_axis_at_the_wanted_distance_and_in_reach():
	cam = np.array([0.60, 0.0, 0.50])
	forward = np.array([-math.sin(math.radians(30)), 0.0, -math.cos(math.radians(30))])
	pts = show_points(cam, forward, distances=(0.3, 0.4, 0.5), max_off_axis_deg=10.0, reach=(0.15, 0.40), z_min=0.08)
	assert len(pts) > 0
	d = np.linalg.norm(pts - cam, axis=1)
	assert np.all((d > 0.3 - 1e-9) & (d < 0.5 + 1e-9))
	off = np.degrees(np.arccos(np.clip((pts - cam) @ forward / d, -1, 1)))
	assert np.all(off <= 10.0 + 1e-9)
	r = np.hypot(pts[:, 0], pts[:, 1])
	assert np.all((r >= 0.15) & (r <= 0.40))
	assert np.all(pts[:, 2] >= 0.08)
	# ordered: closest to the axis first
	assert np.all(np.diff(off) >= -1e-9)


def test_show_points_are_empty_when_nothing_is_in_reach():
	cam = np.array([2.0, 0.0, 0.50])
	pts = show_points(cam, np.array([0.0, 0.0, -1.0]), (0.3, 0.4), 10.0, (0.15, 0.40), 0.05)
	assert pts.shape == (0, 3)


def test_view_cosine_is_one_facing_the_camera_and_negative_facing_away():
	cam = np.array([0.0, 0.0, 1.0])
	p = np.zeros(3)
	assert math.isclose(view_cosine(np.array([0, 0, 1.0]), p, cam), 1.0)
	assert view_cosine(np.array([0, 0, -1.0]), p, cam) < 0
	assert math.isclose(view_cosine(np.array([1.0, 0, 0]), p, cam), 0.0, abs_tol=1e-12)


def test_order_show_poses_goes_by_score_and_skips_near_duplicates():
	poses = np.array([[0.0, 0.0], [0.05, 0.0], [1.0, 0.0], [0.0, 1.0], [2.0, 2.0]])
	scores = np.array([10.0, 9.0, 8.0, 1.0, 0.0])
	# pose 1 is within 0.3 rad of pose 0; pose 3 is below 0.3 x best; pose 4 shows nothing
	assert order_show_poses(poses, scores, k=3, min_sep=0.3, rel_min=0.3) == [0, 2]
	assert order_show_poses(poses, scores, k=1, min_sep=0.3, rel_min=0.3) == [0]
	assert order_show_poses(poses, np.zeros(5), k=3, min_sep=0.3, rel_min=0.3) == []


def test_camera_view_ok_needs_height_downward_view_and_clearance_from_the_arm():
	swept = np.array([[0.2, 0.0, 0.1], [0.3, 0.0, 0.2]])
	down = np.array([0.0, 0.0, -1.0])
	assert camera_view_ok(np.array([0.3, 0.0, 0.5]), down, swept, clearance=0.05)[0]
	# 4 cm from a swept point is too close
	ok, why = camera_view_ok(np.array([0.3, 0.0, 0.24]), down, swept, clearance=0.05)
	assert not ok
	assert "clearance" in why
	# below the minimum height
	assert not camera_view_ok(np.array([0.8, 0.0, 0.05]), down, swept, clearance=0.05)[0]
	# looking up or horizontally
	assert not camera_view_ok(np.array([0.8, 0.0, 0.5]), np.array([1.0, 0.0, 0.0]), swept, clearance=0.05)[0]


def test_camera_clearance_is_measured_from_the_link_surface_when_radii_are_given():
	swept = np.array([[0.3, 0.0, 0.2]])
	down = np.array([0.0, 0.0, -1.0])
	cam = np.array([0.3, 0.0, 0.32])
	# 12 cm from the link centre: fine for a point, too close for a link of 8 cm radius
	assert camera_view_ok(cam, down, swept, clearance=0.05)[0]
	ok, why = camera_view_ok(cam, down, swept, clearance=0.05, radii=np.array([0.08]))
	assert not ok
	assert "clearance" in why
