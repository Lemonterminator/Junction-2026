import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from defect_sorter.robot_pose import (
	RobotCalibration,
	base_from_marker,
	link_base_marker,
	load_calibration,
	model_from_readings,
	readings_from_model,
	save_calibration,
)

BASE_R = Rotation.from_euler("z", 90, degrees=True).as_matrix()
BASE_T = np.array([0.1, 0.2, 0.0])


def make_calibration(**kw) -> RobotCalibration:
	args = {
		"offsets_deg": {"shoulder_lift": 1.2, "elbow_flex": -6.6, "wrist_flex": -2.4},
		"base_rotation": BASE_R,
		"base_position_m": BASE_T,
	}
	args.update(kw)
	return RobotCalibration(**args)


class TestFrames:
	def test_table_point_to_base_frame(self):
		# base x axis points along table +y (yaw 90) and the base sits at (0.1, 0.2): table (0.1, 0.3) is 10 cm ahead
		cal = make_calibration()
		np.testing.assert_allclose(cal.to_base([0.1, 0.3, 0.0]), [0.1, 0.0, 0.0], atol=1e-12)

	def test_base_and_table_conversions_invert_each_other(self):
		cal = make_calibration(base_rotation=Rotation.from_euler("xyz", [3, -2, 140], degrees=True).as_matrix())
		p = np.array([0.31, -0.12, 0.05])
		np.testing.assert_allclose(cal.to_table(cal.to_base(p)), p, atol=1e-12)

	def test_directions_rotate_without_the_offset(self):
		cal = make_calibration()
		np.testing.assert_allclose(cal.direction_to_base([0.0, 0.0, -1.0]), [0.0, 0.0, -1.0], atol=1e-12)
		np.testing.assert_allclose(cal.direction_to_base([0.0, 1.0, 0.0]), [1.0, 0.0, 0.0], atol=1e-12)


class TestBaseMarker:
	def test_link_then_locate_recovers_the_base(self):
		marker_r = Rotation.from_euler("xyz", [1, -1, 37], degrees=True).as_matrix()
		marker_t = np.array([0.24, -0.11, 0.07])
		link = link_base_marker(BASE_R, BASE_T, marker_r, marker_t)
		r, t = base_from_marker(marker_r, marker_t, link)
		np.testing.assert_allclose(r, BASE_R, atol=1e-12)
		np.testing.assert_allclose(t, BASE_T, atol=1e-12)

	def test_moving_the_robot_moves_marker_and_base_together(self):
		# the base marker is bolted to the base: shift and turn both by the same motion, the link still finds the base
		marker_r = Rotation.from_euler("z", 10, degrees=True).as_matrix()
		marker_t = np.array([0.20, 0.25, 0.07])
		link = link_base_marker(BASE_R, BASE_T, marker_r, marker_t)
		move_r = Rotation.from_euler("z", -30, degrees=True).as_matrix()
		move_t = np.array([0.05, -0.08, 0.0])
		r, t = base_from_marker(move_r @ marker_r, move_r @ marker_t + move_t, link)
		np.testing.assert_allclose(r, move_r @ BASE_R, atol=1e-12)
		np.testing.assert_allclose(t, move_r @ BASE_T + move_t, atol=1e-12)


class TestReadings:
	def test_model_angle_is_reading_plus_offset(self):
		cal = make_calibration()
		model = model_from_readings({"shoulder_pan": 5.0, "elbow_flex": 10.0}, cal)
		assert model == {"shoulder_pan": 5.0, "elbow_flex": pytest.approx(3.4)}

	def test_readings_invert_model_angles(self):
		cal = make_calibration()
		readings = {"shoulder_pan": 5.0, "shoulder_lift": -20.0, "elbow_flex": 10.0, "wrist_flex": 40.0}
		assert readings_from_model(model_from_readings(readings, cal), cal) == pytest.approx(readings)


def test_save_and_load_round_trip(tmp_path):
	cal = make_calibration(base_marker_id=15, base_marker_link=np.arange(16.0).reshape(4, 4))
	path = tmp_path / "robot.json"
	save_calibration(path, cal)
	loaded = load_calibration(path)
	assert loaded.offsets_deg == cal.offsets_deg
	np.testing.assert_allclose(loaded.base_rotation, cal.base_rotation)
	np.testing.assert_allclose(loaded.base_position_m, cal.base_position_m)
	assert loaded.base_marker_id == 15
	np.testing.assert_allclose(loaded.base_marker_link, cal.base_marker_link)


class TestRelocated:
	def test_new_base_marker_detection_moves_the_base_and_keeps_the_offsets(self):
		marker_r = np.eye(3)
		marker_t = np.array([0.24, -0.11, 0.07])
		cal = make_calibration(base_marker_id=15, base_marker_link=link_base_marker(BASE_R, BASE_T, marker_r, marker_t))
		moved = cal.relocated(marker_r, marker_t + np.array([0.0, 0.1, 0.0]))
		np.testing.assert_allclose(moved.base_position_m, BASE_T + np.array([0.0, 0.1, 0.0]), atol=1e-12)
		assert moved.offsets_deg == cal.offsets_deg

	def test_without_a_linked_marker_it_refuses(self):
		with pytest.raises(ValueError, match="no base marker linked"):
			make_calibration().relocated(np.eye(3), np.zeros(3))
