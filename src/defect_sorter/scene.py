"""Scene understanding for the sorting cell from one aligned colour + depth frame.

Objects are found by height above the table (depth), so a cluttered, textured table does not matter.
Bowls are found by colour, because shallow plates barely rise above the table in depth.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import cv2
import numpy as np

from defect_sorter.geometry import Intrinsics, Plane, deproject, fit_table_plane, height_above

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SceneConfig:
	"""Detection thresholds.

	Parameters
	----------
	roi_margin : tuple of float
		Fractions of width/height excluded at (left, top, right, bottom). The D415 has no depth on the far left.
	object_min_height_m, object_max_height_m : float
		Height band above the table counted as an object.
	object_min_area_px : int
		Smaller depth blobs are noise.
	saturation_min, value_min : int
		HSV (0-255) floor for bowl pixels.
	wood_hue_max, wood_hue_min_wrap : int
		OpenCV hues (0-180) at or below ``wood_hue_max`` or at or above ``wood_hue_min_wrap`` are table, red or orange
		and never bowls.
	bowl_min_area_px : int
		Minimum bowl blob area; bowls at 0.6 m are around 25 000 px.
	bowl_min_ellipse_fill : float
		Blob area divided by its fitted ellipse area.
	bowl_tall_fraction_max : float
		A coloured blob with more than this fraction of pixels above 3 cm is an object, not a bowl.
	bowl_rim_margin_px : int
		Half-width of the ring around each bowl's outline that is removed from the object mask, so raised rims are
		ignored while objects inside the bowl are still found.
	in_bowl_radius_px : float
		An object whose centre is this close to a bowl centre is reported as in that bowl.
	"""

	roi_margin: tuple[float, float, float, float] = (0.15, 0.10, 0.03, 0.03)
	object_min_height_m: float = 0.008
	object_max_height_m: float = 0.20
	object_min_area_px: int = 400
	saturation_min: int = 45
	value_min: int = 60
	wood_hue_max: int = 30
	wood_hue_min_wrap: int = 172
	bowl_min_area_px: int = 12_000
	bowl_min_ellipse_fill: float = 0.75
	bowl_tall_fraction_max: float = 0.3
	bowl_rim_margin_px: int = 12
	in_bowl_radius_px: float = 80.0


@dataclass(frozen=True)
class Bowl:
	"""A bowl found by colour."""

	colour: str
	hue: float
	px: tuple[float, float]
	ellipse: tuple[tuple[float, float], tuple[float, float], float]
	xyz_cam_m: tuple[float, float, float]


@dataclass(frozen=True)
class DetectedObject:
	"""An object standing on the table, found by height."""

	px: tuple[float, float]
	bbox: tuple[int, int, int, int]
	height_m: float
	xyz_cam_m: tuple[float, float, float]
	in_bowl: str | None
	contour: np.ndarray = field(repr=False)


@dataclass(frozen=True)
class Scene:
	"""Result of :func:`detect_scene`."""

	plane: Plane
	bowls: list[Bowl]
	objects: list[DetectedObject]
	height_m: np.ndarray = field(repr=False)
	valid: np.ndarray = field(repr=False)
	rim_mask: np.ndarray = field(repr=False)


def hue_name(hue: float) -> str:
	"""Name an OpenCV hue (0-180) of a bowl colour.

	Pink, lavender and purple all map to ``"pink"``: the pastel pink bowl's hue moves between about 125 and 157
	with the colour temperature.
	"""
	if hue >= 122:
		return "pink"
	if hue >= 100:
		return "blue"
	if hue >= 40:
		return "green"
	return "yellow"


def roi_mask(shape: tuple[int, int], margin: tuple[float, float, float, float]) -> np.ndarray:
	"""Boolean mask of the workspace rectangle inside the given fractional margins."""
	h, w = shape
	left, top, right, bottom = margin
	mask = np.zeros((h, w), bool)
	mask[int(top * h) : int((1 - bottom) * h), int(left * w) : int((1 - right) * w)] = True
	return mask


def _centre_xyz(
	u: float, v: float, region: np.ndarray, depth_m: np.ndarray, intr: Intrinsics
) -> tuple[float, float, float]:
	z_values = depth_m[region & (depth_m > 0)]
	z = float(np.median(z_values)) if z_values.size else 0.0
	return ((u - intr.ppx) * z / intr.fx, (v - intr.ppy) * z / intr.fy, z)


def _detect_bowls(
	color_bgr: np.ndarray, depth_m: np.ndarray, height: np.ndarray, roi: np.ndarray, intr: Intrinsics, cfg: SceneConfig
) -> tuple[list[Bowl], np.ndarray]:
	hsv = cv2.cvtColor(cv2.GaussianBlur(color_bgr, (7, 7), 0), cv2.COLOR_BGR2HSV)
	hue = hsv[..., 0]
	wood = (hue <= cfg.wood_hue_max) | (hue >= cfg.wood_hue_min_wrap)
	coloured = (hsv[..., 1] > cfg.saturation_min) & (hsv[..., 2] > cfg.value_min) & roi & ~wood
	mask = coloured.astype(np.uint8) * 255
	mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
	mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))

	bowls: list[Bowl] = []
	rim_mask = np.zeros(mask.shape, bool)
	ring = np.ones((2 * cfg.bowl_rim_margin_px + 1, 2 * cfg.bowl_rim_margin_px + 1), np.uint8)
	for contour in cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
		area = cv2.contourArea(contour)
		if area < cfg.bowl_min_area_px or len(contour) < 5:
			continue
		(u, v), (axis_a, axis_b), angle = cv2.fitEllipse(contour)
		if area / (np.pi * axis_a * axis_b / 4) < cfg.bowl_min_ellipse_fill:
			continue
		region_u8 = np.zeros(mask.shape, np.uint8)
		cv2.drawContours(region_u8, [contour], -1, 255, -1)
		region = region_u8 > 0
		if (height[region] > 0.03).mean() > cfg.bowl_tall_fraction_max:
			continue
		rim_mask |= (cv2.dilate(region_u8, ring) > 0) & ~(cv2.erode(region_u8, ring) > 0)
		median_hue = float(np.median(hue[region]))
		bowls.append(
			Bowl(
				colour=hue_name(median_hue),
				hue=median_hue,
				px=(u, v),
				ellipse=((u, v), (axis_a, axis_b), angle),
				xyz_cam_m=_centre_xyz(u, v, region, depth_m, intr),
			)
		)
	return bowls, rim_mask


def _detect_objects(
	depth_m: np.ndarray,
	height: np.ndarray,
	valid: np.ndarray,
	bowls: list[Bowl],
	rim_mask: np.ndarray,
	intr: Intrinsics,
	cfg: SceneConfig,
) -> list[DetectedObject]:
	band = (height > cfg.object_min_height_m) & (height < cfg.object_max_height_m) & valid & ~rim_mask
	mask = band.astype(np.uint8) * 255
	mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
	mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))

	objects: list[DetectedObject] = []
	contours = sorted(
		cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0], key=cv2.contourArea, reverse=True
	)
	for contour in contours:
		if cv2.contourArea(contour) < cfg.object_min_area_px:
			continue
		region_u8 = np.zeros(mask.shape, np.uint8)
		cv2.drawContours(region_u8, [contour], -1, 255, -1)
		region = (region_u8 > 0) & valid
		moments = cv2.moments(contour)
		u, v = moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]
		in_bowl = None
		for bowl in bowls:
			if np.hypot(u - bowl.px[0], v - bowl.px[1]) < cfg.in_bowl_radius_px:
				in_bowl = bowl.colour
		objects.append(
			DetectedObject(
				px=(u, v),
				bbox=tuple(int(x) for x in cv2.boundingRect(contour)),
				height_m=float(np.percentile(height[region], 95)),
				xyz_cam_m=_centre_xyz(u, v, region, depth_m, intr),
				in_bowl=in_bowl,
				contour=contour,
			)
		)
	return objects


def detect_scene(
	color_bgr: np.ndarray,
	depth_m: np.ndarray,
	intrinsics: Intrinsics,
	*,
	plane: Plane | None = None,
	config: SceneConfig | None = None,
) -> Scene:
	"""Detect bowls and objects in one aligned colour + depth frame.

	Parameters
	----------
	color_bgr : numpy.ndarray
		Colour image, shape (H, W, 3), BGR uint8.
	depth_m : numpy.ndarray
		Depth aligned to ``color_bgr``, metres, shape (H, W); zero means no measurement.
	intrinsics : Intrinsics
		Intrinsics of the colour image.
	plane : Plane, optional
		Table plane to reuse; fitted from the workspace pixels when omitted.
	config : SceneConfig, optional
		Thresholds; defaults to :class:`SceneConfig`.

	Returns
	-------
	Scene
		Bowls, objects (largest first) and the intermediate height map and masks.
	"""
	cfg = config or SceneConfig()
	roi = roi_mask(depth_m.shape, cfg.roi_margin)
	valid = (depth_m > 0) & roi
	points = deproject(depth_m, intrinsics)
	if plane is None:
		plane = fit_table_plane(points[valid])
		logger.debug("table plane offset %.3f m, inliers %.2f", plane.offset, plane.inlier_fraction)
	height = np.where(valid, height_above(points, plane), 0.0)
	bowls, rim_mask = _detect_bowls(color_bgr, depth_m, height, roi, intrinsics, cfg)
	objects = _detect_objects(depth_m, height, valid, bowls, rim_mask, intrinsics, cfg)
	return Scene(plane=plane, bowls=bowls, objects=objects, height_m=height, valid=valid, rim_mask=rim_mask)
