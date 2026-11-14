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
FILTER_PROFILES = ("static", "motion")
VISUAL_PRESETS = ("default", "high_accuracy", "high_density")


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
		Colour stream format; depth uses the same unless ``depth_size`` is given.
	depth_size : tuple of int, optional
		Depth resolution when it differs from colour (USB 2 links only allow 640x480 depth with 1280x720
		colour). Depth is always aligned to the colour image.
	white_balance_k : int or None
		Fixed colour temperature. Auto white balance shifts every hue with the room lighting, which breaks
		colour-based bowl detection and changes what the anomaly model sees. ``None`` keeps auto white balance.
	warmup_frames : int
		Frames discarded after start so auto exposure and the temporal filter settle.
	filters : str
		Depth post-filter profile. ``static`` (perception on a still scene): spatial, strong temporal and hole
		filling, so depth is smooth and complete but lags and smears anything moving. ``motion`` (recording a
		moving arm for a policy): spatial and a light temporal filter in the disparity domain, no temporal
		persistence and no hole filling, so each frame shows where things are now and missing depth stays missing.
	preset : str or None
		D400 visual preset (``default``, ``high_accuracy``, ``high_density``); ``None`` keeps the camera's setting.
	"""

	def __init__(
		self,
		width: int = 640,
		height: int = 480,
		fps: int = 30,
		*,
		depth_size: tuple[int, int] | None = None,
		white_balance_k: int | None = WHITE_BALANCE_K,
		warmup_frames: int = 30,
		filters: str = "static",
		preset: str | None = None,
	) -> None:
		if filters not in FILTER_PROFILES:
			raise ValueError(f"filters must be one of {FILTER_PROFILES}")
		if preset is not None and preset not in VISUAL_PRESETS:
			raise ValueError(f"preset must be one of {VISUAL_PRESETS}")
		import pyrealsense2 as rs

		self._rs = rs
		self._pipe = rs.pipeline()
		cfg = rs.config()
		depth_w, depth_h = depth_size or (width, height)
		cfg.enable_stream(rs.stream.depth, depth_w, depth_h, rs.format.z16, fps)
		cfg.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
		profile = self._pipe.start(cfg)
		device = profile.get_device()
		depth_sensor = device.first_depth_sensor()
		self._depth_scale = depth_sensor.get_depth_scale()
		if preset is not None:
			depth_sensor.set_option(rs.option.visual_preset, float(getattr(rs.rs400_visual_preset, preset)))
		if white_balance_k is not None:
			color_sensor = device.first_color_sensor()
			color_sensor.set_option(rs.option.enable_auto_white_balance, 0)
			color_sensor.set_option(rs.option.white_balance, white_balance_k)
		self._align = rs.align(rs.stream.color)
		if filters == "static":
			self._filters = [rs.spatial_filter(), rs.temporal_filter(), rs.hole_filling_filter()]
		else:
			temporal = rs.temporal_filter()
			temporal.set_option(rs.option.filter_smooth_alpha, 0.8)  # 0.8 of each value comes from the new frame
			temporal.set_option(rs.option.filter_smooth_delta, 20)
			temporal.set_option(rs.option.holes_fill, 0)  # persistence off: never repeat an old value into a hole
			self._filters = [
				rs.disparity_transform(True),
				rs.spatial_filter(),
				temporal,
				rs.disparity_transform(False),
			]
		logger.info(
			"D415 started: %s, USB %s, %dx%d@%d, filters %s, preset %s",
			device.get_info(rs.camera_info.serial_number),
			device.get_info(rs.camera_info.usb_type_descriptor),
			width,
			height,
			fps,
			filters,
			preset or "camera setting",
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
