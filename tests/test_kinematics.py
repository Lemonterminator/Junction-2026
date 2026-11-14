import numpy as np
import pytest

from defect_sorter.kinematics import SO101_JOINTS, forward, joint_frames, rpy_matrix


def _rotation_angle_about(axis: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
	"""Signed angle from a to b around axis (all vectors already perpendicular to axis)."""
	return float(np.degrees(np.arctan2(np.dot(np.cross(a, b), axis), np.dot(a, b))))


class TestRpy:
	def test_yaw_turns_x_into_y(self):
		np.testing.assert_allclose(rpy_matrix(0, 0, np.pi / 2) @ [1, 0, 0], [0, 1, 0], atol=1e-12)

	def test_urdf_order_is_roll_then_pitch_then_yaw_about_fixed_axes(self):
		# R = Rz(yaw) Ry(pitch) Rx(roll): z goes to -y under roll 90, then to +x under yaw 90
		np.testing.assert_allclose(rpy_matrix(np.pi / 2, 0, np.pi / 2) @ [0, 0, 1], [1, 0, 0], atol=1e-12)


class TestForward:
	def test_chain_has_the_five_body_joints_in_order(self):
		assert [j.name for j in SO101_JOINTS] == [
			"shoulder_pan",
			"shoulder_lift",
			"elbow_flex",
			"wrist_flex",
			"wrist_roll",
		]

	def test_zero_pose_is_within_the_arm_reach(self):
		tip = forward({})
		assert 0.05 < np.linalg.norm(tip[:3, 3]) < 0.5
		np.testing.assert_allclose(tip[:3, :3] @ tip[:3, :3].T, np.eye(3), atol=1e-9)

	def test_first_joint_frame_is_its_urdf_origin(self):
		frames = joint_frames({})
		np.testing.assert_allclose(frames[0][:3, 3], [0.0388353, -8.97657e-09, 0.0624], atol=1e-9)

	def test_pan_rotates_everything_downstream_about_the_pan_axis(self):
		pose = {"shoulder_lift": 20.0, "elbow_flex": -35.0, "wrist_flex": 10.0, "wrist_roll": 40.0}
		frames = joint_frames(pose)
		axis = frames[0][:3, 2]
		origin = frames[0][:3, 3]
		before = forward(pose)[:3, 3] - origin
		after = forward({**pose, "shoulder_pan": 30.0})[:3, 3] - origin
		radial_before = before - np.dot(before, axis) * axis
		radial_after = after - np.dot(after, axis) * axis
		assert np.dot(after, axis) == pytest.approx(np.dot(before, axis), abs=1e-9)
		assert np.linalg.norm(radial_after) == pytest.approx(np.linalg.norm(radial_before), abs=1e-9)
		assert _rotation_angle_about(axis, radial_before, radial_after) == pytest.approx(30.0, abs=1e-6)

	def test_wrist_roll_spins_the_gripper_in_place(self):
		pose = {"shoulder_lift": -15.0, "elbow_flex": 25.0, "wrist_flex": -20.0}
		a = forward({**pose, "wrist_roll": 0.0})
		b = forward({**pose, "wrist_roll": 90.0})
		np.testing.assert_allclose(a[:3, 3], b[:3, 3], atol=1e-12)
		np.testing.assert_allclose(a[:3, 2], b[:3, 2], atol=1e-12)  # roll axis unchanged
		assert np.dot(a[:3, 0], b[:3, 0]) == pytest.approx(0.0, abs=1e-9)  # x turned by 90 degrees

	def test_angles_are_degrees(self):
		np.testing.assert_allclose(forward({"elbow_flex": 360.0}), forward({}), atol=1e-12)
