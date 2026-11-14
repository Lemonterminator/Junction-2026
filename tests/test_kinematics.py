import numpy as np
import pytest

from defect_sorter.kinematics import (
	JOINT_LIMITS_DEG,
	SO101_JOINTS,
	forward,
	inverse,
	joint_frames,
	rpy_matrix,
	tool_pose,
)


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


class TestTool:
	def test_tool_point_is_the_urdf_gripper_frame_offset_from_gripper_link(self):
		pose = {"shoulder_lift": 10.0, "elbow_flex": -20.0, "wrist_flex": 30.0, "wrist_roll": 15.0}
		link = forward(pose)
		tool = tool_pose(pose)
		offset = link[:3, :3].T @ (tool[:3, 3] - link[:3, 3])
		np.testing.assert_allclose(offset, [-0.0079, -0.000218121, -0.0981274], atol=1e-9)

	def test_tool_z_axis_points_out_of_the_jaws(self):
		# the tool frame is turned half a turn about y, so its z axis is gripper_link's -z: from wrist towards the tips
		pose = {"elbow_flex": 25.0}
		link = forward(pose)
		np.testing.assert_allclose(tool_pose(pose)[:3, 2], -link[:3, 2], atol=1e-5)  # the URDF writes pi as 3.14159


class TestInverse:
	def test_round_trip_through_forward_kinematics(self):
		rng = np.random.default_rng(7)
		for _ in range(10):
			truth = {name: rng.uniform(lo + 15, hi - 15) for name, (lo, hi) in JOINT_LIMITS_DEG.items()}
			target = tool_pose(truth)
			sol = inverse(target[:3, 3], approach=target[:3, 2], roll_deg=truth["wrist_roll"])
			assert sol.reachable, sol
			reached = tool_pose(sol.angles_deg)
			assert np.linalg.norm(reached[:3, 3] - target[:3, 3]) * 1000 < 0.5
			assert np.degrees(np.arccos(np.clip(reached[:3, 2] @ target[:3, 2], -1, 1))) < 0.5

	def test_top_down_grasp_in_front_of_the_robot(self):
		# 20 cm out along the arm's reach direction, 3 cm above the base plane, jaws pointing straight down
		zero_reach = tool_pose({})[:3, 3]
		forward_dir = np.array([zero_reach[0], zero_reach[1], 0.0]) / np.linalg.norm(zero_reach[:2])
		target = 0.20 * forward_dir + np.array([0.0, 0.0, 0.03])
		sol = inverse(target, approach=(0.0, 0.0, -1.0), roll_deg=30.0)
		assert sol.reachable, sol
		reached = tool_pose(sol.angles_deg)
		assert np.linalg.norm(reached[:3, 3] - target) * 1000 < 1.0
		np.testing.assert_allclose(reached[:3, 2], [0.0, 0.0, -1.0], atol=0.01)
		assert sol.angles_deg["wrist_roll"] == pytest.approx(30.0)

	def test_respects_joint_limits(self):
		zero_reach = tool_pose({})[:3, 3]
		sol = inverse(zero_reach * 0.8 + np.array([0.0, 0.0, 0.05]), approach=(0.0, 0.0, -1.0), roll_deg=0.0)
		for name, (lo, hi) in JOINT_LIMITS_DEG.items():
			assert lo <= sol.angles_deg[name] <= hi

	def test_out_of_reach_is_reported_not_raised(self):
		sol = inverse(np.array([1.0, 0.0, 0.1]), approach=(0.0, 0.0, -1.0), roll_deg=0.0)
		assert not sol.reachable
		assert sol.position_error_mm > 100
