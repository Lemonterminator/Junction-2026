import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from defect_sorter.calibration_capture import StillnessGate, load_session, main, save_session
from defect_sorter.joint_calibration import Observation, angles_from_ticks
from defect_sorter.kinematics import forward
from defect_sorter.robot_pose import load_calibration


def ticks(lift: int, elbow: int = 2000, wrist: int = 2000) -> dict[str, int]:
	return {
		"shoulder_pan": 2000,
		"shoulder_lift": lift,
		"elbow_flex": elbow,
		"wrist_flex": wrist,
		"wrist_roll": 2000,
		"gripper": 2500,
	}


POS = np.array([0.1, 0.2, 0.05])


class TestStillnessGate:
	def test_records_once_after_holding_still_long_enough(self):
		gate = StillnessGate(hold_s=1.0, tick_tol=3, marker_tol_mm=1.0, min_change_deg=5.0)
		assert gate.update(0.0, ticks(2000), POS) is False
		assert gate.update(0.5, ticks(2001), POS) is False
		assert gate.update(1.1, ticks(2002), POS) is True
		assert gate.update(1.5, ticks(2001), POS) is False  # same pose: no second sample

	def test_motion_restarts_the_hold_timer(self):
		gate = StillnessGate(hold_s=1.0, tick_tol=3, marker_tol_mm=1.0, min_change_deg=5.0)
		gate.update(0.0, ticks(2000), POS)
		gate.update(0.8, ticks(2100), POS)  # moved
		assert gate.update(1.2, ticks(2100), POS) is False
		assert gate.update(1.9, ticks(2101), POS) is True

	def test_marker_jitter_counts_as_motion(self):
		gate = StillnessGate(hold_s=1.0, tick_tol=3, marker_tol_mm=1.0, min_change_deg=5.0)
		gate.update(0.0, ticks(2000), POS)
		assert gate.update(1.2, ticks(2000), POS + np.array([0.003, 0, 0])) is False

	def test_needs_a_new_pose_after_a_sample(self):
		gate = StillnessGate(hold_s=1.0, tick_tol=3, marker_tol_mm=1.0, min_change_deg=5.0)
		gate.update(0.0, ticks(2000), POS)
		assert gate.update(1.1, ticks(2000), POS) is True
		# 30 ticks is ~2.6 degrees: too close to the recorded pose
		gate.update(2.0, ticks(2030), POS)
		assert gate.update(3.5, ticks(2030), POS) is False
		# 120 ticks is ~10.5 degrees: a new pose
		gate.update(4.0, ticks(2120), POS)
		assert gate.update(5.5, ticks(2120), POS) is True

	def test_missing_marker_never_records(self):
		gate = StillnessGate(hold_s=1.0, tick_tol=3, marker_tol_mm=1.0, min_change_deg=5.0)
		gate.update(0.0, ticks(2000), None)
		assert gate.update(2.0, ticks(2000), None) is False


def test_session_round_trips_through_jsonl(tmp_path):
	ranges = {"shoulder_lift": (839, 3191)}
	obs = [
		Observation(
			angles_deg={"shoulder_lift": 12.5}, marker_rotation=np.eye(3), marker_position_m=np.array([0.1, 0.2, 0.3])
		)
	]
	raw = [{"shoulder_lift": 2157}]
	path = tmp_path / "session.jsonl"

	save_session(path, ranges, raw, obs, meta={"marker": 4})
	loaded_ranges, loaded_raw, loaded_obs, meta = load_session(path)

	assert loaded_ranges == {"shoulder_lift": (839, 3191)}
	assert loaded_raw == raw
	assert meta == {"marker": 4}
	assert loaded_obs[0].angles_deg == {"shoulder_lift": 12.5}
	np.testing.assert_allclose(loaded_obs[0].marker_position_m, [0.1, 0.2, 0.3])
	np.testing.assert_allclose(loaded_obs[0].marker_rotation, np.eye(3))


def _synthetic_session(path, offsets, base_r, base_t, seed):
	"""Session file whose marker poses follow from known offsets and base pose (marker taped at the tool point)."""
	rng = np.random.default_rng(seed)
	ranges = dict.fromkeys(("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"), (1000, 3000))
	raw, obs = [], []
	for _ in range(8):
		t = {j: int(rng.integers(1400, 2600)) for j in ranges}
		read = angles_from_ticks(t, ranges)
		tip = forward({j: v + offsets.get(j, 0.0) for j, v in read.items()})
		raw.append(t)
		obs.append(Observation(read, base_r @ tip[:3, :3], base_r @ tip[:3, 3] + base_t))
	save_session(path, ranges, raw, obs, meta={"marker": 4})


def test_solve_combines_sessions_and_saves_a_robot_calibration(tmp_path):
	offsets = {"shoulder_lift": 1.0, "elbow_flex": -6.0, "wrist_flex": 2.0}
	base_r = Rotation.from_euler("z", 63, degrees=True).as_matrix()
	base_t = np.array([0.226, -0.096, 0.0])
	_synthetic_session(tmp_path / "a.jsonl", offsets, base_r, base_t, seed=1)
	_synthetic_session(tmp_path / "b.jsonl", offsets, base_r, base_t, seed=2)
	out = tmp_path / "robot.json"

	main(["solve", "--session", str(tmp_path / "a.jsonl"), str(tmp_path / "b.jsonl"), "--save", str(out)])

	cal = load_calibration(out)
	for joint, value in offsets.items():
		assert cal.offsets_deg[joint] == pytest.approx(value, abs=0.05)
	np.testing.assert_allclose(cal.base_position_m, base_t, atol=1e-3)
