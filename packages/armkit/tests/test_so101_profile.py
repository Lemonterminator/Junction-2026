import numpy as np
import pytest
from armkit.procedure import CalibrationSettings, plan_calibration
from armkit.profiles.so101 import REST_DEG, so101_profile


class TestModel:
	def test_joint_limits_are_the_urdf_limits_in_degrees(self):
		robot = so101_profile().robot
		assert robot.limits_deg("shoulder_pan") == (-110.0, 110.0)
		assert robot.limits_deg("shoulder_lift") == (-100.0, 100.0)
		assert robot.limits_deg("elbow_flex") == pytest.approx((-96.83, 96.83))
		assert robot.limits_deg("wrist_flex") == (-95.0, 95.0)

	def test_the_tool_point_at_the_zero_pose_is_where_the_urdf_puts_it(self):
		# 0.391 m forward and 0.226 m up, read off the follower URDF's joint chain independently of this code
		np.testing.assert_allclose(so101_profile().robot.tool_pose({})[:3, 3], [0.391, 0.0, 0.226], atol=1e-3)

	def test_the_zero_pose_clears_everything_with_room_to_spare(self):
		assert so101_profile().collision.clearance({}).distance_m > 0.015

	def test_pan_turns_the_arm_about_the_vertical_axis_so_the_floor_clearance_does_not_change(self):
		collision = so101_profile().collision
		pose = {"shoulder_lift": 40.0, "elbow_flex": -20.0, "wrist_flex": 10.0}
		assert collision.clearance({**pose, "shoulder_pan": 0.0}).distance_m == pytest.approx(
			collision.clearance({**pose, "shoulder_pan": 70.0}).distance_m, abs=1e-9
		)

	def test_pushing_the_forearm_down_into_the_table_is_a_collision(self):
		assert not so101_profile().collision.is_clear({"shoulder_lift": 100.0, "elbow_flex": 96.0, "wrist_flex": -90.0})


class TestProfile:
	def test_servo_ids_and_calibration_order(self):
		profile = so101_profile()
		assert [(j.name, j.servo_id) for j in profile.joints] == [
			("gripper", 6),
			("wrist_flex", 4),
			("elbow_flex", 3),
			("shoulder_lift", 2),
			("shoulder_pan", 1),
			("wrist_roll", 5),
		]

	def test_the_gripper_has_its_own_travel_and_the_roll_is_a_full_turn(self):
		profile = so101_profile()
		assert profile.travel("gripper") == (-10.0, 100.0)
		assert profile.setup("wrist_roll").kind == "full_turn"

	def test_the_rest_pose_is_the_one_studios_wizard_shows(self):
		assert so101_profile().rest_pose == REST_DEG
		assert REST_DEG["shoulder_lift"] == -90.0
		assert REST_DEG["elbow_flex"] == 90.0


class TestPlan:
	def test_every_joint_end_has_a_collision_free_staged_plan_from_the_rest_pose(self):
		plan = plan_calibration(so101_profile(), CalibrationSettings())
		assert plan.ok, plan.describe()
		limited = [j for j in plan.joints if j.kind == "limited"]
		assert [j.name for j in limited] == ["gripper", "wrist_flex", "elbow_flex", "shoulder_lift", "shoulder_pan"]
		assert all(len(j.ends) == 2 and j.return_stages for j in limited)


class TestTableClearance:
	def test_the_profile_can_keep_the_arm_a_set_height_above_the_table(self):
		from armkit.profile import with_table_clearance

		profile = with_table_clearance(so101_profile(), 0.08)
		low = {"shoulder_lift": -20.0, "elbow_flex": 45.0, "wrist_flex": 30.0}  # gripper 28 mm above the table
		assert so101_profile().collision.is_clear(low)
		assert not profile.collision.is_clear(low)
		assert profile.collision.is_clear({})  # the zero pose is far above it

	def test_the_extra_air_applies_to_the_far_links_not_to_the_upper_arm_at_the_shoulder(self):
		from armkit.profile import with_table_clearance

		profile = with_table_clearance(so101_profile(), 0.08)
		# arm leaning back: only the upper arm's root is near 8 cm, and it turns about the shoulder axis 12 cm up
		pose = {"shoulder_lift": -85.0, "elbow_flex": -95.0, "wrist_flex": 0.0}
		real_floor = so101_profile().collision.clearance(pose)
		assert real_floor.distance_m > 0.0
		assert profile.collision.clearance(pose).between != ("upper_arm_link", "floor")
