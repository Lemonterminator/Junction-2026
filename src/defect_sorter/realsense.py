"""Intel RealSense D415 capture: the only module that imports ``pyrealsense2``.

Only one process can open the camera at a time; Physical AI Studio's camera preview, recording and policy runs
hold it while active.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from defect_sorter.geometry import Intrinsics

logger = logging.getLogger(__name__)

WHITE_BALANCE_K = 4600


@dataclass(frozen=True)
class Frame:
	"""Colour image with depth aligned to it."""

	color_bgr: np.ndarray
	depth_m: np.ndarray
	intrinsics: Intrinsics


class D415Camera:
	"""Aligned colour + depth stream with fixed white balance and RealSense depth post-filters.

	Parameters
	----------
	width, height, fps : int
		Stream format used for both colour and depth.
	white_balance_k : int or None
		Fixed colour temperature. Auto white balance shifts every hue with the room lighting, which breaks
		colour-based bowl detection and changes what the anomaly model sees. ``None`` keeps auto white balance.
	warmup_frames : int
		Frames discarded after start so auto exposure and the temporal filter settle.
	"""

	def __init__(
		self,
		width: int = 640,
		height: int = 480,
		fps: int = 30,
		*,
		white_balance_k: int | None = WHITE_BALANCE_K,
		warmup_frames: int = 30,
	) -> None:
		import pyrealsense2 as rs

		self._rs = rs
		self._pipe = rs.pipeline()
		cfg = rs.config()
		cfg.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
		cfg.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
		profile = self._pipe.start(cfg)
		device = profile.get_device()
		self._depth_scale = device.first_depth_sensor().get_depth_scale()
		if white_balance_k is not None:
			color_sensor = device.first_color_sensor()
			color_sensor.set_option(rs.option.enable_auto_white_balance, 0)
			color_sensor.set_option(rs.option.white_balance, white_balance_k)
		self._align = rs.align(rs.stream.color)
		self._filters = [rs.spatial_filter(), rs.temporal_filter(), rs.hole_filling_filter()]
		logger.info(
			"D415 started: %s, USB %s, %dx%d@%d",
			device.get_info(rs.camera_info.serial_number),
			device.get_info(rs.camera_info.usb_type_descriptor),
			width,
			height,
			fps,
		)
		for _ in range(warmup_frames):
			self.read()

	def read(self) -> Frame:
		"""Block until the next aligned frame pair and return it."""
		frames = self._align.process(self._pipe.wait_for_frames())
		depth_frame = frames.get_depth_frame()
		filtered = depth_frame
		for f in self._filters:
			filtered = f.process(filtered)
		intr = depth_frame.profile.as_video_stream_profile().intrinsics
		return Frame(
			color_bgr=np.asanyarray(frames.get_color_frame().get_data()).copy(),
			depth_m=np.asanyarray(filtered.get_data()).astype(np.float32) * self._depth_scale,
			intrinsics=Intrinsics(fx=intr.fx, fy=intr.fy, ppx=intr.ppx, ppy=intr.ppy),
		)

	def close(self) -> None:
		"""Release the camera."""
		self._pipe.stop()

	def __enter__(self) -> D415Camera:
		return self

	def __exit__(self, *exc: object) -> None:
		self.close()
