import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from defect_sorter.joint_calibration import Observation, angles_from_ticks, solve, solve_base, ticks_to_degrees
from defect_sorter.kinematics import forward, joint_frames

RNG = np.random.default_rng(42)

TRUE_OFFSETS = {"shoulder_lift": 4.0, "elbow_flex": -3.0, "wrist_flex": 6.0}
TRUE_BASE_R = Rotation.from_euler("z", 140, degrees=True).as_matrix()
TRUE_BASE_T = np.array([0.25, -0.30, 0.0])
TRUE_MOUNT_R = Rotation.from_euler("xyz", [80, -10, 35], degrees=True).as_matrix()
TRUE_MOUNT_T = np.array([0.01, -0.02, -0.04])


def forearm_pose(angles: dict[str, float]) -> np.ndarray:
	"""Pose of the forearm (``lower_arm_link``): the wrist_flex joint frame, which sits on it before turning."""
	return joint_frames(angles)[3]


def make_observations(
	n: int,
	*,
	pan_offset: float = 0.0,
	roll_offset: float = 0.0,
	noise_mm: float = 0.0,
	noise_deg: float = 0.0,
	link_pose=forward,
):
	"""Marker poses in the table frame for random joint readings, generated with known offsets."""
	obs = []
	for _ in range(n):
		read = {
			"shoulder_pan": RNG.uniform(-60, 60),
			"shoulder_lift": RNG.uniform(-60, 40),
			"elbow_flex": RNG.uniform(-50, 50),
			"wrist_flex": RNG.uniform(-60, 60),
			"wrist_roll": RNG.uniform(-90, 90),
		}
		true_angles = {k: v + TRUE_OFFSETS.get(k, 0.0) for k, v in read.items()}
		true_angles["shoulder_pan"] += pan_offset
		true_angles["wrist_roll"] += roll_offset
		tip = link_pose(true_angles)
		r = TRUE_BASE_R @ tip[:3, :3] @ TRUE_MOUNT_R
		t = TRUE_BASE_R @ (tip[:3, :3] @ TRUE_MOUNT_T + tip[:3, 3]) + TRUE_BASE_T
		if noise_deg:
			r = Rotation.from_rotvec(np.radians(RNG.normal(0, noise_deg, 3))).as_matrix() @ r
		if noise_mm:
			t = t + RNG.normal(0, noise_mm / 1000, 3)
		obs.append(Observation(angles_deg=read, marker_rotation=r, marker_position_m=t))
	return obs


def test_ticks_to_degrees_uses_the_range_midpoint_lerobot_convention():
	assert ticks_to_degrees(2048, 0, 4095) == pytest.approx(0.5 * 360 / 4095)
	assert ticks_to_degrees(1000, 1000, 3000) == pytest.approx(-1000 * 360 / 4095)


def test_angles_from_ticks_per_joint_range():
	ranges = {"shoulder_lift": (839, 3191), "wrist_roll": (0, 4095)}
	angles = angles_from_ticks({"shoulder_lift": 2015, "wrist_roll": 1023}, ranges)
	assert angles["shoulder_lift"] == pytest.approx(0.0)
	assert angles["wrist_roll"] == pytest.approx((1023 - 2047.5) * 360 / 4095)
	assert set(angles) == {"shoulder_lift", "wrist_roll"}


class TestSolve:
	def test_recovers_offsets_and_base_pose_from_clean_data(self):
		result = solve(make_observations(15))

		for joint, value in TRUE_OFFSETS.items():
			assert result.offsets_deg[joint] == pytest.approx(value, abs=1e-3)
		np.testing.assert_allclose(result.base_position_m, TRUE_BASE_T, atol=1e-5)
		assert result.rms_position_mm < 1e-3

	def test_tolerates_realistic_marker_noise(self):
		result = solve(make_observations(20, noise_mm=1.5, noise_deg=1.0))

		for joint, value in TRUE_OFFSETS.items():
			assert result.offsets_deg[joint] == pytest.approx(value, abs=1.0)
		np.testing.assert_allclose(result.base_position_m, TRUE_BASE_T, atol=0.005)
		assert result.rms_position_mm < 3.0

	def test_pan_and_roll_zeros_are_absorbed_not_misattributed(self):
		# A pan offset looks like a turned base and a roll offset like a re-taped marker: the observable
		# offsets must still come out right, and the fit must stay exact.
		result = solve(make_observations(15, pan_offset=5.0, roll_offset=-12.0))

		for joint, value in TRUE_OFFSETS.items():
			assert result.offsets_deg[joint] == pytest.approx(value, abs=1e-3)
		assert result.rms_position_mm < 1e-3
		assert set(result.offsets_deg) == {"shoulder_lift", "elbow_flex", "wrist_flex"}

	def test_refuses_too_few_or_too_similar_poses(self):
		with pytest.raises(ValueError, match="at least"):
			solve(make_observations(4))
		same = make_observations(1) * 10
		with pytest.raises(ValueError, match="different poses"):
			solve(same)


class TestForearmMarker:
	"""A marker on the forearm sees the base pose and the lift zero; the elbow zero turns the forearm itself."""

	def test_recovers_the_lift_offset_and_base_pose(self):
		result = solve(make_observations(15, link_pose=forearm_pose), link="forearm")

		assert set(result.offsets_deg) == {"shoulder_lift"}
		assert result.offsets_deg["shoulder_lift"] == pytest.approx(TRUE_OFFSETS["shoulder_lift"], abs=1e-3)
		np.testing.assert_allclose(result.base_rotation, TRUE_BASE_R, atol=1e-5)
		np.testing.assert_allclose(result.base_position_m, TRUE_BASE_T, atol=1e-5)
		assert result.rms_position_mm < 1e-3

	def test_the_wrist_joints_do_not_move_a_forearm_marker(self):
		a = {"shoulder_pan": 10.0, "shoulder_lift": -20.0, "elbow_flex": 30.0, "wrist_flex": 0.0, "wrist_roll": 0.0}
		b = {**a, "wrist_flex": 70.0, "wrist_roll": -80.0}
		np.testing.assert_allclose(forearm_pose(a), forearm_pose(b), atol=1e-12)

	def test_tolerates_the_noise_of_a_small_marker(self):
		# a 20 mm marker at 0.5 m: depth keeps the position to ~2 mm, the rotation is worse
		result = solve(make_observations(20, link_pose=forearm_pose, noise_mm=2.0, noise_deg=3.0), link="forearm")

		assert result.offsets_deg["shoulder_lift"] == pytest.approx(TRUE_OFFSETS["shoulder_lift"], abs=1.0)
		np.testing.assert_allclose(result.base_position_m, TRUE_BASE_T, atol=0.005)

	def test_an_elbow_zero_error_is_invisible_to_a_forearm_marker(self):
		# the elbow offset in the data (-3 deg) is taken up by the mounting: the fit is exact without fitting it
		result = solve(make_observations(15, link_pose=forearm_pose), link="forearm")

		assert "elbow_flex" not in result.offsets_deg
		assert result.rms_position_mm < 1e-3
		assert result.rms_rotation_deg < 1e-3

	def test_unknown_marker_link_is_refused(self):
		with pytest.raises(ValueError, match="link"):
			solve(make_observations(15), link="elbow")


def shoulder_pose(angles: dict[str, float]) -> np.ndarray:
	"""Pose of the turning part of the base (``shoulder_link``): the shoulder_lift joint frame sits on it."""
	return joint_frames(angles)[1]


def tagged(obs: list[Observation], link: str) -> list[Observation]:
	return [Observation(o.angles_deg, o.marker_rotation, o.marker_position_m, link=link) for o in obs]


def studio_zero_observations(n: int, link_pose, mount_r, mount_t, *, noise_mm: float = 0.0, noise_deg: float = 0.0):
	"""Marker poses for random readings when the readings are exact (Studio's zeros are right)."""
	obs = []
	for _ in range(n):
		read = {
			"shoulder_pan": RNG.uniform(-60, 60),
			"shoulder_lift": RNG.uniform(-60, 40),
			"elbow_flex": RNG.uniform(-50, 50),
			"wrist_flex": RNG.uniform(-60, 60),
			"wrist_roll": RNG.uniform(-90, 90),
		}
		tip = link_pose(read)
		r = TRUE_BASE_R @ tip[:3, :3] @ mount_r
		t = TRUE_BASE_R @ (tip[:3, :3] @ mount_t + tip[:3, 3]) + TRUE_BASE_T
		if noise_deg:
			r = Rotation.from_rotvec(np.radians(RNG.normal(0, noise_deg, 3))).as_matrix() @ r
		if noise_mm:
			t = t + RNG.normal(0, noise_mm / 1000, 3)
		obs.append(Observation(angles_deg=read, marker_rotation=r, marker_position_m=t))
	return obs


SHOULDER_MOUNT_R = Rotation.from_euler("xyz", [-90, 0, 20], degrees=True).as_matrix()
SHOULDER_MOUNT_T = np.array([0.03, 0.0, -0.02])


class TestSolveBase:
	"""Base pose with Studio's joint zeros trusted: one tag on the turning base, one further out on the arm."""

	def test_base_pose_from_a_base_tag_and_a_gripper_tag(self):
		obs = tagged(studio_zero_observations(5, shoulder_pose, SHOULDER_MOUNT_R, SHOULDER_MOUNT_T), "shoulder")
		obs += tagged(studio_zero_observations(5, forward, TRUE_MOUNT_R, TRUE_MOUNT_T), "gripper")

		fit = solve_base(obs)

		np.testing.assert_allclose(fit.base_rotation, TRUE_BASE_R, atol=1e-5)
		np.testing.assert_allclose(fit.base_position_m, TRUE_BASE_T, atol=1e-5)
		assert fit.rms_position_mm < 1e-3
		assert set(fit.rms_by_link_mm) == {"shoulder", "gripper"}

	def test_a_few_gripper_poses_alone_are_enough(self):
		fit = solve_base(tagged(studio_zero_observations(4, forward, TRUE_MOUNT_R, TRUE_MOUNT_T), "gripper"))

		np.testing.assert_allclose(fit.base_position_m, TRUE_BASE_T, atol=1e-5)

	def test_the_base_tag_alone_cannot_give_the_heading(self):
		# it turns with shoulder_pan, so how it was stuck on and where the base points cannot be told apart
		obs = tagged(studio_zero_observations(8, shoulder_pose, SHOULDER_MOUNT_R, SHOULDER_MOUNT_T), "shoulder")
		with pytest.raises(ValueError, match="arm"):
			solve_base(obs)

	def test_realistic_noise_keeps_the_base_within_a_few_millimetres(self):
		obs = tagged(
			studio_zero_observations(6, shoulder_pose, SHOULDER_MOUNT_R, SHOULDER_MOUNT_T, noise_mm=2.0, noise_deg=2.0),
			"shoulder",
		)
		obs += tagged(
			studio_zero_observations(8, forward, TRUE_MOUNT_R, TRUE_MOUNT_T, noise_mm=2.0, noise_deg=2.0), "gripper"
		)

		fit = solve_base(obs)

		np.testing.assert_allclose(fit.base_position_m, TRUE_BASE_T, atol=0.004)
		yaw_error = np.degrees(Rotation.from_matrix(fit.base_rotation.T @ TRUE_BASE_R).magnitude())
		assert yaw_error < 1.0

	def test_the_turning_base_tag_ignores_everything_but_the_pan(self):
		a = {"shoulder_pan": 25.0, "shoulder_lift": 0.0, "elbow_flex": 0.0, "wrist_flex": 0.0, "wrist_roll": 0.0}
		b = {**a, "shoulder_lift": -50.0, "elbow_flex": 60.0, "wrist_flex": 30.0}
		np.testing.assert_allclose(shoulder_pose(a), shoulder_pose(b), atol=1e-12)

	def test_too_few_poses_are_refused(self):
		with pytest.raises(ValueError, match="poses"):
			solve_base(tagged(studio_zero_observations(1, forward, TRUE_MOUNT_R, TRUE_MOUNT_T), "gripper"))
