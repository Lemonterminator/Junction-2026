import cv2
import numpy as np
import pytest

from defect_sorter.geometry import Intrinsics
from defect_sorter.scene import PAPER_CELL, SceneConfig, detect_scene, hue_name

INTR = Intrinsics(fx=600.0, fy=600.0, ppx=320.0, ppy=240.0)
TABLE_Z = 0.6
# BGR colours with hand-computed OpenCV hues (0-180 scale):
WOOD = (90, 140, 190)  # H = 30 deg -> 15, excluded as wood
PINK = (220, 150, 240)  # H = 313 deg -> 157, S = 96
GREEN = (120, 150, 0)  # H = 168 deg -> 84, S = 255
RED_BRICK = (40, 40, 200)  # H = 0, excluded from bowls by hue


def blank_scene() -> tuple[np.ndarray, np.ndarray]:
	color = np.zeros((480, 640, 3), np.uint8)
	color[:] = WOOD
	depth = np.full((480, 640), TABLE_Z, np.float32)
	return color, depth


def add_bowl(color: np.ndarray, centre: tuple[int, int], radius: int, bgr: tuple[int, int, int]) -> None:
	cv2.circle(color, centre, radius, bgr, -1)


def add_box(color: np.ndarray, depth: np.ndarray, x: int, y: int, w: int, h: int, height_m: float) -> None:
	color[y : y + h, x : x + w] = RED_BRICK
	depth[y : y + h, x : x + w] = TABLE_Z - height_m


class TestHueName:
	@pytest.mark.parametrize(
		("hue", "name"),
		[
			(84.0, "green"),
			(89.0, "green"),
			(110.0, "blue"),
			(125.0, "pink"),
			(141.0, "pink"),
			(157.0, "pink"),
			(30.0, "yellow"),
		],
	)
	def test_names(self, hue: float, name: str):
		assert hue_name(hue) == name


class TestDetectScene:
	def test_finds_two_bowls_by_colour_and_one_object_by_height(self):
		color, depth = blank_scene()
		add_bowl(color, (300, 320), 80, PINK)
		add_bowl(color, (500, 300), 80, GREEN)
		add_box(color, depth, 380, 100, 40, 50, 0.05)

		scene = detect_scene(color, depth, INTR)

		bowls = {b.colour: b for b in scene.bowls}
		assert set(bowls) == {"pink", "green"}
		assert bowls["pink"].px == pytest.approx((300, 320), abs=2)
		assert bowls["green"].px == pytest.approx((500, 300), abs=2)
		assert len(scene.objects) == 1
		obj = scene.objects[0]
		assert obj.px == pytest.approx((400, 125), abs=2)
		assert obj.height_m == pytest.approx(0.05, abs=0.003)
		# 3D centre: pixel (400,125) at z = 0.55 -> x = 80*0.55/600, y = -115*0.55/600
		np.testing.assert_allclose(obj.xyz_cam_m, [0.0733, -0.1054, 0.55], atol=2e-3)
		assert obj.in_bowl is None

	def test_raised_bowl_rim_is_not_an_object(self):
		color, depth = blank_scene()
		add_bowl(color, (300, 300), 80, PINK)
		rim = np.zeros(depth.shape, np.uint8)
		cv2.circle(rim, (300, 300), 80, 255, 6)
		depth[rim > 0] = TABLE_Z - 0.014

		scene = detect_scene(color, depth, INTR)

		assert [b.colour for b in scene.bowls] == ["pink"]
		assert scene.objects == []

	def test_object_inside_bowl_is_related_to_it(self):
		color, depth = blank_scene()
		add_bowl(color, (450, 300), 80, GREEN)
		add_box(color, depth, 430, 280, 40, 40, 0.04)

		scene = detect_scene(color, depth, INTR)

		assert len(scene.objects) == 1
		assert scene.objects[0].in_bowl == "green"

	def test_missing_depth_is_not_reported_as_an_object(self):
		color, depth = blank_scene()
		depth[200:260, 300:360] = 0.0  # no depth returned (e.g. shiny surface)

		scene = detect_scene(color, depth, INTR)

		assert scene.objects == []

	def test_clutter_outside_workspace_is_ignored(self):
		color, depth = blank_scene()
		add_box(color, depth, 5, 5, 60, 30, 0.05)  # top-left corner, outside default ROI

		scene = detect_scene(color, depth, INTR)

		assert scene.objects == []

	def test_small_colour_patch_is_not_a_bowl(self):
		color, depth = blank_scene()
		add_bowl(color, (300, 300), 30, GREEN)  # ~2800 px, far below bowl size

		scene = detect_scene(color, depth, INTR)

		assert scene.bowls == []

	def test_reuses_given_plane(self):
		color, depth = blank_scene()
		add_box(color, depth, 380, 100, 40, 50, 0.05)
		first = detect_scene(color, depth, INTR)

		again = detect_scene(color, depth, INTR, plane=first.plane, config=SceneConfig())

		assert again.plane is first.plane
		assert len(again.objects) == 1


PAPER = (205, 205, 205)


def paper_scene() -> tuple[np.ndarray, np.ndarray]:
	color = np.zeros((480, 640, 3), np.uint8)
	color[:] = PAPER
	return color, np.full((480, 640), TABLE_Z, np.float32)


# Per-channel (B, G, R) gains of tinted room light on a camera with fixed white balance.
BLUE_LIGHT = (1.0, 0.81, 0.72)  # evening light in the hall: the white table measured BGR 127, 103, 91
GREEN_LIGHT = (0.72, 1.0, 0.78)  # fluorescent: the white table takes the green bowl's hue


def tinted(color: np.ndarray, gains: tuple[float, float, float]) -> np.ndarray:
	return np.clip(color.astype(np.float64) * gains, 0, 255).astype(np.uint8)


class TestPaperCell:
	def test_touching_bowls_of_two_colours_are_two_bowls(self):
		color, depth = paper_scene()
		add_bowl(color, (300, 300), 80, PINK)
		add_bowl(color, (460, 300), 80, GREEN)

		bowls = {b.colour: b for b in detect_scene(color, depth, INTR, config=PAPER_CELL).bowls}

		assert set(bowls) == {"pink", "green"}
		assert bowls["pink"].px == pytest.approx((300, 300), abs=3)
		assert bowls["green"].px == pytest.approx((460, 300), abs=3)

	@pytest.mark.parametrize("light", [BLUE_LIGHT, GREEN_LIGHT])
	def test_tinted_light_on_the_white_table_still_gives_both_bowls(self, light: tuple[float, float, float]):
		color, depth = paper_scene()
		add_bowl(color, (250, 300), 80, PINK)
		add_bowl(color, (480, 300), 80, GREEN)
		add_box(color, depth, 280, 290, 30, 30, 0.02)
		cast = tinted(color, light)
		hsv_table = cv2.cvtColor(cast[:1, :1], cv2.COLOR_BGR2HSV)[0, 0]
		assert hsv_table[1] > SceneConfig().saturation_min  # the cast table itself looks coloured

		scene = detect_scene(cast, depth, INTR, config=PAPER_CELL)

		assert {b.colour for b in scene.bowls} == {"pink", "green"}
		assert len(scene.objects) == 1
		assert scene.objects[0].in_bowl is not None

	def test_a_bowl_reaching_the_top_of_the_image_is_kept(self):
		color, depth = paper_scene()
		add_bowl(color, (420, 70), 80, GREEN)

		bowls = detect_scene(color, depth, INTR, config=PAPER_CELL).bowls

		assert [b.colour for b in bowls] == ["green"]
