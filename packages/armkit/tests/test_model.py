import numpy as np
import pytest
from armkit.model import Joint, RobotModel, load_urdf, rpy_matrix


def planar_arm() -> RobotModel:
	"""Two links of 0.3 m and 0.2 m in the x-y plane; joints turn about z; tool 0.1 m beyond the second joint."""
	return RobotModel(
		joints=(
			Joint("a", (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), lower_deg=-170, upper_deg=170),
			Joint("b", (0.3, 0.0, 0.0), (0.0, 0.0, 0.0), lower_deg=-150, upper_deg=150),
		),
		link_names=("base", "upper", "fore"),
		tool_xyz=(0.2, 0.0, 0.0),
	)


class TestForward:
	def test_straight_arm_reaches_the_sum_of_the_links(self):
		np.testing.assert_allclose(planar_arm().tool_pose({})[:3, 3], [0.5, 0.0, 0.0], atol=1e-12)

	def test_elbow_at_ninety_degrees_points_the_forearm_along_y(self):
		np.testing.assert_allclose(planar_arm().tool_pose({"b": 90.0})[:3, 3], [0.3, 0.2, 0.0], atol=1e-12)

	def test_both_joints_at_ninety_degrees_fold_the_tool_back_along_minus_x(self):
		np.testing.assert_allclose(planar_arm().tool_pose({"a": 90.0, "b": 90.0})[:3, 3], [-0.2, 0.3, 0.0], atol=1e-12)

	def test_link_frames_start_at_the_base_and_end_at_the_last_link(self):
		model = planar_arm()
		frames = model.link_frames({"a": 30.0, "b": -20.0})
		assert len(frames) == 3
		np.testing.assert_allclose(frames[0], np.eye(4))
		np.testing.assert_allclose(frames[-1], model.forward({"a": 30.0, "b": -20.0}), atol=1e-12)

	def test_a_joint_about_another_axis_turns_about_that_axis(self):
		model = RobotModel(
			joints=(Joint("j", (0, 0, 0), (0, 0, 0), axis=(1, 0, 0), lower_deg=-90, upper_deg=90),),
			link_names=("b", "l"),
			tool_xyz=(0, 1, 0),
		)
		np.testing.assert_allclose(model.tool_pose({"j": 90.0})[:3, 3], [0, 0, 1], atol=1e-12)

	def test_rpy_is_roll_then_pitch_then_yaw_about_fixed_axes(self):
		np.testing.assert_allclose(rpy_matrix(np.pi / 2, 0, np.pi / 2) @ [0, 0, 1], [1, 0, 0], atol=1e-12)


class TestInverse:
	def test_reaches_a_point_the_forward_model_produced(self):
		model = planar_arm()
		truth = {"a": 35.0, "b": -60.0}
		target = model.tool_pose(truth)[:3, 3]
		sol = model.inverse(target, approach=model.tool_pose(truth)[:3, 2], fixed={})
		assert sol.reachable
		np.testing.assert_allclose(model.tool_pose(sol.angles_deg)[:3, 3], target, atol=1e-3)

	def test_a_point_beyond_the_arm_is_not_reachable(self):
		model = planar_arm()
		sol = model.inverse(np.array([2.0, 0.0, 0.0]), approach=(0, 0, 1), fixed={})
		assert not sol.reachable

	def test_a_fixed_joint_is_held_and_must_itself_be_within_limits(self):
		model = planar_arm()
		target = model.tool_pose({"a": 10.0, "b": 40.0})[:3, 3]
		held = model.inverse(target, approach=model.tool_pose({"a": 10.0, "b": 40.0})[:3, 2], fixed={"b": 40.0})
		assert held.angles_deg["b"] == 40.0
		out_of_range = model.inverse(target, approach=(0, 0, 1), fixed={"b": 175.0})
		assert not out_of_range.reachable


URDF = """<robot name="t">
 <link name="base"/><link name="l1"/><link name="l2"/><link name="tool"/><link name="finger"/>
 <joint name="j1" type="revolute"><origin xyz="0 0 0.1" rpy="0 0 0"/><parent link="base"/><child link="l1"/>
  <axis xyz="0 0 1"/><limit lower="-1.5707963" upper="1.5707963" effort="1" velocity="1"/></joint>
 <joint name="j2" type="revolute"><origin xyz="0.3 0 0" rpy="0 0 0"/><parent link="l1"/><child link="l2"/>
  <axis xyz="0 1 0"/><limit lower="-1" upper="2" effort="1" velocity="1"/></joint>
 <joint name="tip" type="fixed"><origin xyz="0.2 0 0" rpy="0 0 0"/><parent link="l2"/><child link="tool"/></joint>
 <joint name="grip" type="revolute"><origin xyz="0 0.1 0" rpy="0 0 0"/><parent link="l2"/><child link="finger"/>
  <axis xyz="0 0 1"/><limit lower="0" upper="1" effort="1" velocity="1"/></joint>
</robot>"""


class TestUrdf:
	def test_chain_to_the_end_link_with_limits_axes_and_tool(self, tmp_path):
		path = tmp_path / "t.urdf"
		path.write_text(URDF)
		model = load_urdf(path, end_link="l2", tool_link="tool")
		assert [j.name for j in model.joints] == ["j1", "j2"]
		assert model.link_names == ("base", "l1", "l2")
		assert model.joints[1].axis == (0.0, 1.0, 0.0)
		assert model.limits_deg("j2") == pytest.approx((-57.29578, 114.59156), abs=1e-4)
		np.testing.assert_allclose(model.tool_pose({})[:3, 3], [0.5, 0.0, 0.1], atol=1e-12)

	def test_trailing_fixed_joints_become_the_tool_offset(self, tmp_path):
		path = tmp_path / "t.urdf"
		path.write_text(URDF)
		model = load_urdf(path, end_link="tool")
		assert [j.name for j in model.joints] == ["j1", "j2"]
		np.testing.assert_allclose(model.forward({})[:3, 3], [0.3, 0.0, 0.1], atol=1e-12)
		np.testing.assert_allclose(model.tool_pose({})[:3, 3], [0.5, 0.0, 0.1], atol=1e-12)

	def test_a_fixed_joint_inside_the_chain_moves_the_next_joint(self, tmp_path):
		path = tmp_path / "t.urdf"
		path.write_text(
			"""<robot name="t"><link name="b"/><link name="m"/><link name="l"/>
			<joint name="f" type="fixed"><origin xyz="0.1 0 0" rpy="0 0 1.5707963"/><parent link="b"/><child link="m"/></joint>
			<joint name="j" type="revolute"><origin xyz="0.2 0 0.05" rpy="0 0 0"/><parent link="m"/><child link="l"/>
			<axis xyz="0 0 1"/><limit lower="-1" upper="1" effort="1" velocity="1"/></joint></robot>"""
		)
		model = load_urdf(path, end_link="l")
		# the fixed joint turns the frame a quarter turn, so the joint's 0.2 m along x lands along y
		np.testing.assert_allclose(model.joint_frames({})[0][:3, 3], [0.1, 0.2, 0.05], atol=1e-6)

	def test_an_unknown_end_link_is_an_error(self, tmp_path):
		path = tmp_path / "t.urdf"
		path.write_text(URDF)
		with pytest.raises(ValueError, match="nowhere"):
			load_urdf(path, end_link="nowhere")
