import json

import pytest

from defect_sorter.uvc_controls import (
	CONTROL_IDS,
	VIDIOC_G_CTRL,
	VIDIOC_S_CTRL,
	apply_profile,
	find_device,
	load_profile,
	ordered_settings,
)


class FakeDevice:
	"""Mimics a UVC camera: manual values are refused while their auto mode is on."""

	def __init__(self) -> None:
		self.values = {
			"auto_exposure": 3,
			"exposure_time_absolute": 166,
			"white_balance_automatic": 1,
			"white_balance_temperature": 4600,
			"power_line_frequency": 2,
		}
		self.writes: list[str] = []

	def get(self, name: str) -> int:
		return self.values[name]

	def set(self, name: str, value: int) -> None:
		if name == "exposure_time_absolute" and self.values["auto_exposure"] != 1:
			raise OSError(13, "Permission denied")  # what V4L2 returns for an inactive control
		if name == "white_balance_temperature" and self.values["white_balance_automatic"]:
			raise OSError(13, "Permission denied")
		self.values[name] = value
		self.writes.append(name)


def test_ioctl_numbers_match_the_kernel_headers():
	# _IOWR('V', 27 / 28, struct v4l2_control), the struct being two 32-bit fields
	assert VIDIOC_G_CTRL == 0xC008561B
	assert VIDIOC_S_CTRL == 0xC008561C


def test_control_ids_match_what_the_cameras_report():
	# ids read from the workstation's front and wrist cameras
	assert CONTROL_IDS["white_balance_automatic"] == 9963788
	assert CONTROL_IDS["white_balance_temperature"] == 9963802
	assert CONTROL_IDS["power_line_frequency"] == 9963800
	assert CONTROL_IDS["auto_exposure"] == 10094849
	assert CONTROL_IDS["exposure_time_absolute"] == 10094850
	assert CONTROL_IDS["exposure_dynamic_framerate"] == 10094851
	assert CONTROL_IDS["focus_absolute"] == 10094858
	assert CONTROL_IDS["focus_automatic_continuous"] == 10094860


def test_auto_modes_are_switched_before_their_manual_values():
	settings = {"exposure_time_absolute": 100, "white_balance_temperature": 4600, "auto_exposure": 1, "gain": 0}
	names = [name for name, _ in ordered_settings(settings)]
	assert names.index("auto_exposure") < names.index("exposure_time_absolute")
	assert set(names) == set(settings)


def test_apply_locks_a_camera_and_reports_the_read_back():
	device = FakeDevice()
	settings = {
		"exposure_time_absolute": 100,
		"auto_exposure": 1,
		"white_balance_temperature": 4600,
		"white_balance_automatic": 0,
		"power_line_frequency": 1,
	}
	results = apply_profile(device, settings)
	assert device.values["auto_exposure"] == 1
	assert device.values["exposure_time_absolute"] == 100
	assert device.values["power_line_frequency"] == 1
	assert all(r.ok for r in results)
	assert {r.name: (r.wanted, r.actual) for r in results}["exposure_time_absolute"] == (100, 100)


def test_apply_reports_a_value_the_camera_did_not_keep():
	class Clamping(FakeDevice):
		def set(self, name: str, value: int) -> None:
			super().set(name, min(value, 50) if name == "exposure_time_absolute" else value)

	results = apply_profile(Clamping(), {"auto_exposure": 1, "exposure_time_absolute": 100})
	bad = [r for r in results if not r.ok]
	assert [(r.name, r.wanted, r.actual) for r in bad] == [("exposure_time_absolute", 100, 50)]


def test_apply_reports_a_refused_write_and_continues():
	results = apply_profile(FakeDevice(), {"exposure_time_absolute": 100, "power_line_frequency": 1})
	by_name = {r.name: r for r in results}
	assert not by_name["exposure_time_absolute"].ok  # auto exposure was left on, so the camera refuses it
	assert "denied" in by_name["exposure_time_absolute"].error
	assert by_name["power_line_frequency"].ok


def _fake_sysfs(root, devices):
	for node, (name, index) in devices.items():
		d = root / node
		d.mkdir(parents=True)
		(d / "name").write_text(name + "\n")
		(d / "index").write_text(f"{index}\n")


def test_find_device_picks_the_capture_node_of_the_named_camera(tmp_path):
	_fake_sysfs(
		tmp_path,
		{
			"video10": ("Webcam Audio: Webcam", 0),
			"video11": ("Webcam Audio: Webcam", 1),
			"video12": ("USB2.0_CAM1: USB2.0_CAM1", 0),
			"video13": ("USB2.0_CAM1: USB2.0_CAM1", 1),
		},
	)
	assert str(find_device("USB2.0_CAM1: USB2.0_CAM1", sysfs=tmp_path)) == "/dev/video12"
	assert str(find_device("Webcam Audio: Webcam", sysfs=tmp_path)) == "/dev/video10"


def test_find_device_refuses_a_missing_or_ambiguous_camera(tmp_path):
	_fake_sysfs(tmp_path, {"video0": ("Cam", 0), "video2": ("Cam", 0)})
	with pytest.raises(LookupError, match="2 cameras"):
		find_device("Cam", sysfs=tmp_path)
	with pytest.raises(LookupError, match="no camera"):
		find_device("Other", sysfs=tmp_path)


def test_load_profile_rejects_unknown_controls(tmp_path):
	good = tmp_path / "good.json"
	good.write_text(
		json.dumps({"wrist": {"device_name": "USB2.0_CAM1: USB2.0_CAM1", "controls": {"auto_exposure": 1}}})
	)
	profile = load_profile(good)
	assert profile["wrist"].device_name == "USB2.0_CAM1: USB2.0_CAM1"
	assert profile["wrist"].controls == {"auto_exposure": 1}

	bad = tmp_path / "bad.json"
	bad.write_text(json.dumps({"wrist": {"device_name": "x", "controls": {"exposure": 100}}}))
	with pytest.raises(ValueError, match="exposure"):
		load_profile(bad)


def test_the_tracked_profile_locks_both_cameras():
	from pathlib import Path

	profile = load_profile(Path(__file__).parents[1] / "config" / "camera_controls.json")
	for name in ("front", "wrist"):
		controls = profile[name].controls
		assert controls["auto_exposure"] == 1  # manual
		assert controls["white_balance_automatic"] == 0
		assert controls["power_line_frequency"] == 1  # 50 Hz mains
	assert profile["wrist"].controls["exposure_dynamic_framerate"] == 0
	assert profile["front"].controls["focus_automatic_continuous"] == 0
