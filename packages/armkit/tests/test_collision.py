import struct

import numpy as np
import pytest
from armkit.collision import CollisionModel, LinkShape, collision_from_urdf, fit_link_shape, read_stl
from armkit.model import Joint, RobotModel


def three_link_arm() -> RobotModel:
	"""Base, then two 0.3 m links turning about z at the base and at 0.3 m; used with one sphere per link."""
	return RobotModel(
		joints=(
			Joint("a", (0, 0, 0), (0, 0, 0), lower_deg=-180, upper_deg=180),
			Joint("b", (0.3, 0, 0), (0, 0, 0), lower_deg=-180, upper_deg=180),
		),
		link_names=("base", "upper", "fore"),
	)


def ball(x: float, y: float, z: float, r: float) -> LinkShape:
	return LinkShape(np.array([[x, y, z]]), np.array([r]))


def box_stl(path, lo, hi) -> None:
	"""Binary STL of an axis-aligned box (12 triangles)."""
	x0, y0, z0 = lo
	x1, y1, z1 = hi
	c = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
	faces = [
		(0, 1, 3),
		(0, 3, 2),
		(4, 5, 7),
		(4, 7, 6),
		(0, 1, 5),
		(0, 5, 4),
		(2, 3, 7),
		(2, 7, 6),
		(0, 2, 6),
		(0, 6, 4),
		(1, 3, 7),
		(1, 7, 5),
	]
	data = bytearray(80) + struct.pack("<I", len(faces))
	for f in faces:
		data += struct.pack("<3f", 0, 0, 0) + b"".join(struct.pack("<3f", *c[i]) for i in f) + b"\x00\x00"
	path.write_bytes(bytes(data))


class TestClearance:
	def test_distance_between_two_spheres_is_centre_gap_minus_both_radii(self):
		# straight arm: the fore ball sits at (0.6, 0, 0); the base ball is at (0, 0, 0.5)
		model = CollisionModel(
			three_link_arm(), {"base": ball(0, 0, 0.5, 0.1), "fore": ball(0.3, 0, 0, 0.05)}, floor_z=None
		)
		assert model.clearance({}).distance_m == pytest.approx(np.hypot(0.6, 0.5) - 0.15)
		assert model.clearance({}).between == ("base", "fore")

	def test_folding_the_forearm_onto_the_base_ball_makes_the_distance_negative(self):
		model = CollisionModel(
			three_link_arm(), {"base": ball(0.3, 0.3, 0, 0.1), "fore": ball(0.3, 0, 0, 0.05)}, floor_z=None
		)
		assert model.clearance({"b": 0.0}).distance_m == pytest.approx(np.hypot(0.3, 0.3) - 0.15)
		# b = 90 turns the forearm to point along +y: its ball lands exactly on the base ball's centre
		assert model.clearance({"b": 90.0}).distance_m == pytest.approx(-0.15)

	def test_neighbouring_links_are_never_compared(self):
		model = CollisionModel(
			three_link_arm(), {"base": ball(0, 0, 0, 0.5), "upper": ball(0, 0, 0, 0.5)}, floor_z=None
		)
		assert model.clearance({}).between is None
		assert model.is_clear({}, margin=10.0)

	def test_pairs_can_be_ignored_explicitly(self):
		shapes = {"base": ball(0, 0, 0.1, 0.1), "fore": ball(0, 0, 0.1, 0.1)}
		shapes_model = CollisionModel(three_link_arm(), shapes, floor_z=None)
		assert shapes_model.clearance({}).distance_m == pytest.approx(0.1)
		assert (
			CollisionModel(three_link_arm(), shapes, ignore=[("fore", "base")], floor_z=None).clearance({}).between
			is None
		)

	def test_the_floor_is_a_plane_the_spheres_must_stay_above(self):
		model = CollisionModel(three_link_arm(), {"fore": ball(0, 0, 0.12, 0.1)}, floor_z=0.0)
		assert model.clearance({}).distance_m == pytest.approx(0.02)
		assert model.clearance({}).between == ("fore", "floor")
		low = CollisionModel(three_link_arm(), {"fore": ball(0, 0, 0.05, 0.1)}, floor_z=0.0)
		assert not low.is_clear({})

	def test_exempt_links_may_touch_the_floor(self):
		model = CollisionModel(three_link_arm(), {"base": ball(0, 0, 0.0, 0.1)}, floor_z=0.0, floor_exempt=["base"])
		assert model.is_clear({})

	def test_pairs_overlapping_in_a_reference_pose_can_be_ignored(self):
		shapes = {"base": ball(0, 0, 0.1, 0.1), "fore": ball(0, 0, 0.1, 0.4)}
		model = CollisionModel(three_link_arm(), shapes, floor_z=None)
		assert not model.is_clear({})
		assert model.ignoring_contacts_at({}).is_clear({})


class TestFit:
	def test_every_point_lies_inside_one_of_the_spheres(self):
		rng = np.random.default_rng(1)
		points = np.column_stack([rng.uniform(0, 0.3, 500), rng.normal(0, 0.01, 500), rng.normal(0, 0.01, 500)])
		shape = fit_link_shape(points, 4)
		d = np.linalg.norm(points[:, None] - shape.centers[None], axis=2) - shape.radii[None]
		assert (d.min(axis=1) <= 1e-9).all()
		assert shape.radii.max() < 0.12

	def test_fewer_points_than_spheres_still_works(self):
		shape = fit_link_shape(np.array([[0.0, 0, 0], [0.1, 0, 0]]), 5)
		assert len(shape.radii) <= 2


class TestMeshes:
	def test_binary_stl_vertices_are_read(self, tmp_path):
		box_stl(tmp_path / "b.stl", (0, 0, 0), (1, 2, 3))
		v = read_stl(tmp_path / "b.stl")
		assert v.shape == (36, 3)
		np.testing.assert_allclose(v.min(axis=0), [0, 0, 0])
		np.testing.assert_allclose(v.max(axis=0), [1, 2, 3])

	def test_urdf_collision_meshes_follow_their_links(self, tmp_path):
		box_stl(tmp_path / "up.stl", (0.0, -0.02, 0.0), (0.3, 0.02, 0.04))
		(tmp_path / "t.urdf").write_text(
			"""<robot name="t"><link name="base"/>
			<link name="upper"><collision><origin xyz="0 0 0" rpy="0 0 0"/><geometry><mesh filename="up.stl"/></geometry></collision></link>
			<joint name="a" type="revolute"><origin xyz="0 0 0" rpy="0 0 0"/><parent link="base"/><child link="upper"/>
			<axis xyz="0 0 1"/><limit lower="-3" upper="3" effort="1" velocity="1"/></joint></robot>"""
		)
		robot = RobotModel((Joint("a", (0, 0, 0), (0, 0, 0)),), ("base", "upper"))
		model = collision_from_urdf(tmp_path / "t.urdf", robot, spheres_per_link=4, floor_z=None)
		# turned a quarter turn the box lies along +y: its corner (0.3, 0.02, 0.04) lands at (-0.02, 0.3, 0.04)
		centres, radii = model.world_spheres({"a": 90.0})["upper"]
		assert (np.linalg.norm(centres - [-0.02, 0.3, 0.04], axis=1) - radii).min() <= 1e-9


class TestRaisedFloor:
	def test_raising_the_floor_reduces_every_floor_clearance_by_that_much(self):
		model = CollisionModel(three_link_arm(), {"fore": ball(0, 0, 0.12, 0.1)}, floor_z=0.0)
		raised = model.with_floor_raised(0.015)
		assert raised.clearance({}).distance_m == pytest.approx(0.02 - 0.015)
		assert model.clearance({}).distance_m == pytest.approx(0.02)  # the original is unchanged

	def test_a_model_without_a_floor_stays_without_one(self):
		model = CollisionModel(three_link_arm(), {"fore": ball(0, 0, 0.12, 0.1)}, floor_z=None)
		assert model.with_floor_raised(0.1).floor_z is None

	def test_the_floor_can_be_raised_for_some_links_only(self):
		model = CollisionModel(
			three_link_arm(), {"upper": ball(0.1, 0, 0.12, 0.1), "fore": ball(0, 0, 0.12, 0.1)}, floor_z=0.0
		)
		raised = model.with_floor_raised(0.015, links=["fore"])
		assert raised.clearance({}).between == ("fore", "floor")
		assert raised.clearance({}).distance_m == pytest.approx(0.005)


class TestTableArea:
	"""Table covering x in [-1, 0.25] (the edge at x = 0.25 m); beyond it there is no floor."""

	AREA = ((-1.0, -1.0), (0.25, -1.0), (0.25, 1.0), (-1.0, 1.0))

	def test_a_link_below_table_height_beyond_the_edge_is_clear(self):
		model = CollisionModel(three_link_arm(), {"fore": ball(0.1, 0, -0.2, 0.05)}, floor_z=0.0, floor_area=self.AREA)
		# the fore ball sits at x = 0.4, 15 cm beyond the edge, 25 cm below table height
		assert model.is_clear({})

	def test_the_same_link_over_the_table_collides(self):
		model = CollisionModel(three_link_arm(), {"fore": ball(-0.2, 0, -0.2, 0.05)}, floor_z=0.0, floor_area=self.AREA)
		assert not model.is_clear({})  # at x = 0.1, over the table

	def test_a_link_just_beyond_the_edge_still_counts_as_over_it_by_its_radius(self):
		model = CollisionModel(
			three_link_arm(), {"fore": ball(-0.03, 0, -0.2, 0.05)}, floor_z=0.0, floor_area=self.AREA
		)
		assert not model.is_clear({})  # centre at x = 0.27, 2 cm past the edge, but 5 cm in radius

	def test_without_an_area_the_floor_is_everywhere(self):
		model = CollisionModel(three_link_arm(), {"fore": ball(0, 0, -0.2, 0.05)}, floor_z=0.0)
		assert not model.is_clear({})
