import numpy as np

from defect_sorter.calibration_capture import StillnessGate, load_session, save_session
from defect_sorter.joint_calibration import Observation


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
