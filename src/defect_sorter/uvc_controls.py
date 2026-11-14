"""Lock the image controls of the USB cameras (exposure, white balance, focus, mains frequency) through V4L2.

Auto exposure, auto white balance and autofocus make the same scene look different from one frame to the next (the
wrist camera darkens as the gripper approaches the white table), and a policy then learns from inconsistent images.
Physical AI Studio does not set these controls, and a camera forgets them when it is replugged or the machine
restarts, so ``sorter-camera-lock --apply`` re-applies a saved profile before each recording or demo session.

Setting a control does not open a video stream, so it works while Studio is capturing from the camera. This module is
the only one issuing V4L2 ioctls; the profile logic works on any object with ``get``/``set``.

	uv run sorter-camera-lock                 # show current values against the profile
	uv run sorter-camera-lock --apply         # set them and read them back
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

logger = logging.getLogger(__name__)

SYSFS = Path("/sys/class/video4linux")
DEFAULT_PROFILE = Path(__file__).parents[2] / "config" / "camera_controls.json"

_V4L2_CONTROL = struct.Struct("Ii")  # struct v4l2_control { __u32 id; __s32 value; }


def _iowr(kind: str, nr: int, size: int) -> int:
	return (3 << 30) | (size << 16) | (ord(kind) << 8) | nr


VIDIOC_G_CTRL = _iowr("V", 27, _V4L2_CONTROL.size)
VIDIOC_S_CTRL = _iowr("V", 28, _V4L2_CONTROL.size)

# Standard V4L2 control ids, named as v4l2-ctl names them.
CONTROL_IDS: dict[str, int] = {
	"brightness": 0x00980900,
	"contrast": 0x00980901,
	"saturation": 0x00980902,
	"hue": 0x00980903,
	"white_balance_automatic": 0x0098090C,
	"gamma": 0x00980910,
	"gain": 0x00980913,
	"power_line_frequency": 0x00980918,
	"white_balance_temperature": 0x0098091A,
	"sharpness": 0x0098091B,
	"backlight_compensation": 0x0098091C,
	"auto_exposure": 0x009A0901,
	"exposure_time_absolute": 0x009A0902,
	"exposure_dynamic_framerate": 0x009A0903,
	"focus_absolute": 0x009A090A,
	"focus_automatic_continuous": 0x009A090C,
}
# Mode switches go first: a camera refuses a manual value while its auto mode is on.
_MODE_CONTROLS = (
	"auto_exposure",
	"exposure_dynamic_framerate",
	"white_balance_automatic",
	"focus_automatic_continuous",
)


class ControlDevice(Protocol):
	"""Anything that reads and writes named camera controls."""

	def get(self, name: str) -> int: ...

	def set(self, name: str, value: int) -> None: ...


@dataclass(frozen=True)
class CameraProfile:
	"""Controls for one camera, found by its V4L2 device name (``/sys/class/video4linux/*/name``)."""

	device_name: str
	controls: dict[str, int]


@dataclass(frozen=True)
class ControlResult:
	"""Outcome of setting one control: the value asked for, the value read back, or the error."""

	name: str
	wanted: int
	actual: int | None
	error: str | None = None

	@property
	def ok(self) -> bool:
		return self.error is None and self.actual == self.wanted


def ordered_settings(controls: dict[str, int]) -> list[tuple[str, int]]:
	"""Controls in a safe order: auto-mode switches first, then the manual values."""
	modes = [(n, controls[n]) for n in _MODE_CONTROLS if n in controls]
	rest = [(n, v) for n, v in controls.items() if n not in _MODE_CONTROLS]
	return modes + rest


def apply_profile(device: ControlDevice, controls: dict[str, int]) -> list[ControlResult]:
	"""Set ``controls`` on ``device`` in a safe order and read each one back.

	A refused write is reported and the remaining controls are still set.
	"""
	results = []
	for name, value in ordered_settings(controls):
		try:
			device.set(name, value)
			results.append(ControlResult(name, value, device.get(name)))
		except OSError as exc:
			results.append(ControlResult(name, value, None, exc.strerror or str(exc)))
	return results


def read_profile(device: ControlDevice, controls: dict[str, int]) -> list[ControlResult]:
	"""Current values of the profile's controls, without changing anything."""
	results = []
	for name, value in ordered_settings(controls):
		try:
			results.append(ControlResult(name, value, device.get(name)))
		except OSError as exc:
			results.append(ControlResult(name, value, None, exc.strerror or str(exc)))
	return results


def find_device(device_name: str, *, sysfs: Path = SYSFS) -> Path:
	"""The capture node (``index`` 0) of the camera named ``device_name``.

	Raises
	------
	LookupError
		When no camera or more than one camera has that name.
	"""
	matches = []
	for node in sorted(sysfs.iterdir()):
		try:
			name = (node / "name").read_text().strip()
			index = int((node / "index").read_text().strip())
		except (OSError, ValueError):
			continue
		if name == device_name and index == 0:
			matches.append(Path("/dev") / node.name)
	if not matches:
		raise LookupError(f"no camera named {device_name!r}")
	if len(matches) > 1:
		raise LookupError(f"{len(matches)} cameras named {device_name!r}: {', '.join(map(str, matches))}")
	return matches[0]


def load_profile(path: Path) -> dict[str, CameraProfile]:
	"""Read a profile file: ``{camera: {"device_name": ..., "controls": {control: value}}}``."""
	data = json.loads(path.read_text())
	profile = {}
	for camera, entry in data.items():
		unknown = sorted(set(entry["controls"]) - set(CONTROL_IDS))
		if unknown:
			raise ValueError(f"{camera}: unknown controls {unknown}; known: {sorted(CONTROL_IDS)}")
		profile[camera] = CameraProfile(entry["device_name"], {k: int(v) for k, v in entry["controls"].items()})
	return profile


class V4L2Device:
	"""Named V4L2 controls on one device node, through ``VIDIOC_G_CTRL`` / ``VIDIOC_S_CTRL``."""

	def __init__(self, path: Path) -> None:
		self._fd = os.open(path, os.O_RDWR | os.O_NONBLOCK)

	def get(self, name: str) -> int:
		import fcntl

		buf = bytearray(_V4L2_CONTROL.pack(CONTROL_IDS[name], 0))
		fcntl.ioctl(self._fd, VIDIOC_G_CTRL, buf)
		return _V4L2_CONTROL.unpack(buf)[1]

	def set(self, name: str, value: int) -> None:
		import fcntl

		buf = bytearray(_V4L2_CONTROL.pack(CONTROL_IDS[name], value))
		fcntl.ioctl(self._fd, VIDIOC_S_CTRL, buf)

	def close(self) -> None:
		os.close(self._fd)


def main(argv: list[str] | None = None) -> None:
	"""``sorter-camera-lock``: show or apply the camera control profile."""
	parser = argparse.ArgumentParser(description="Lock USB camera exposure, white balance and focus (V4L2)")
	parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
	parser.add_argument("--apply", action="store_true", help="set the controls; without it only show them")
	parser.add_argument("--only", nargs="+", metavar="CAMERA", help="cameras from the profile (default: all)")
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

	profile = load_profile(args.profile)
	failed = False
	for camera, entry in profile.items():
		if args.only and camera not in args.only:
			continue
		try:
			path = find_device(entry.device_name)
		except LookupError as exc:
			sys.stdout.write(f"{camera}: {exc}\n")
			failed = True
			continue
		device = V4L2Device(path)
		try:
			results = apply_profile(device, entry.controls) if args.apply else read_profile(device, entry.controls)
		finally:
			device.close()
		sys.stdout.write(f"{camera} ({path}){' set' if args.apply else ''}:\n")
		for r in results:
			mark = "ok" if r.ok else "DIFFERS" if r.error is None else f"ERROR {r.error}"
			sys.stdout.write(f"  {r.name:<28} profile {r.wanted:>5}  camera {r.actual!s:>5}  {mark}\n")
		failed |= not all(r.ok for r in results)
	if failed:
		raise SystemExit(1)


if __name__ == "__main__":
	main()
