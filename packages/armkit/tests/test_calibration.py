import json

import pytest
from armkit.calibration import TICKS_PER_DEGREE, Calibration, JointCalibration


def _cal() -> Calibration:
	return Calibration(
		{
			"shoulder_pan": JointCalibration(id=1, drive_mode=0, homing_offset=-312, range_min=800, range_max=3300),
			"gripper": JointCalibration(id=6, drive_mode=0, homing_offset=15, range_min=2000, range_max=3200),
		}
	)


class TestJointCalibration:
	def test_midpoint_is_zero_degrees_and_ends_are_half_the_span_away(self):
		j = JointCalibration(id=1, drive_mode=0, homing_offset=0, range_min=1000, range_max=3000)
		assert j.to_degrees(2000) == pytest.approx(0.0)
		assert j.to_degrees(3000) == pytest.approx(1000 / TICKS_PER_DEGREE)
		assert j.to_degrees(1000) == pytest.approx(-1000 / TICKS_PER_DEGREE)

	def test_ticks_round_trip_through_degrees(self):
		j = JointCalibration(id=1, drive_mode=0, homing_offset=0, range_min=1000, range_max=3000)
		assert j.to_ticks(j.to_degrees(2345)) == 2345

	def test_normalised_range_runs_minus_100_to_100_and_gripper_zero_to_100(self):
		j = JointCalibration(id=1, drive_mode=0, homing_offset=0, range_min=1000, range_max=3000)
		assert [j.to_normalized(t) for t in (1000, 2000, 3000)] == pytest.approx([-100.0, 0.0, 100.0])
		assert [j.to_normalized(t, unsigned=True) for t in (1000, 2000, 3000)] == pytest.approx([0.0, 50.0, 100.0])

	def test_an_empty_or_inverted_range_is_rejected(self):
		with pytest.raises(ValueError, match="range"):
			JointCalibration(id=1, drive_mode=0, homing_offset=0, range_min=2000, range_max=2000)


class TestCalibrationFile:
	def test_json_uses_the_lerobot_layout_that_studio_imports(self, tmp_path):
		path = tmp_path / "arm.json"
		_cal().save(path)
		raw = json.loads(path.read_text())
		assert raw["shoulder_pan"] == {
			"id": 1,
			"drive_mode": 0,
			"homing_offset": -312,
			"range_min": 800,
			"range_max": 3300,
		}

	def test_load_returns_what_was_saved(self, tmp_path):
		path = tmp_path / "arm.json"
		_cal().save(path)
		assert Calibration.load(path) == _cal()

	def test_a_file_missing_a_field_is_refused(self, tmp_path):
		path = tmp_path / "arm.json"
		path.write_text(json.dumps({"gripper": {"id": 6, "drive_mode": 0}}))
		with pytest.raises(ValueError, match="gripper"):
			Calibration.load(path)
