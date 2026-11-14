import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from defect_sorter.joint_calibration import Observation, angles_from_ticks, solve, ticks_to_degrees
from defect_sorter.kinematics import forward

RNG = np.random.default_rng(42)

TRUE_OFFSETS = {"shoulder_lift": 4.0, "elbow_flex": -3.0, "wrist_flex": 6.0}
TRUE_BASE_R = Rotation.from_euler("z", 140, degrees=True).as_matrix()
TRUE_BASE_T = np.array([0.25, -0.30, 0.0])
TRUE_MOUNT_R = Rotation.from_euler("xyz", [80, -10, 35], degrees=True).as_matrix()
TRUE_MOUNT_T = np.array([0.01, -0.02, -0.04])


def make_observations(
	n: int, *, pan_offset: float = 0.0, roll_offset: float = 0.0, noise_mm: float = 0.0, noise_deg: float = 0.0
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
		tip = forward(true_angles)
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
