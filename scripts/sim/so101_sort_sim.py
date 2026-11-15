"""MuJoCo sorting cell for synthetic data: SO-101, two bowls, a brick (optionally with a marker cross), randomised cameras.

Runs in a Linux environment with ``mujoco`` (WSL2 on the training PC: ``MUJOCO_GL=egl`` and
``MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA``). The robot model is MuJoCo Menagerie ``robotstudio_so101`` at commit
``370c43965323c0944b433b202aac5058b5f907a9``; ``--menagerie`` points at that directory.

Everything is expressed in the robot base frame (metres, table top at z = 0). Camera images follow dataset
sort-depth-v2:

* ``top_rgb_v2`` / ``top_depth_v2``: the D415 colour view rendered at 640x480 and cropped to x 96..608, y 0..416, as the
  depth bridge does (``--crop 96 0 512 416``). The depth image uses the bridge's ``layers`` encoding: R = height above
  the table 0 → 4 cm, G = 0 → 30 cm, B = 255 where depth is valid.
* ``front`` and ``wrist``: 640x480 colour.

Joint values are written in Studio's normalised units (body joints -100…100, gripper 0…100) using the follower
calibration that recorded sort-depth-v2 (Studio robot payload, read on 2026-11-14). The mapping assumes Studio's
"zero at range midpoint" convention and the Menagerie joint zero; the camera fit (``fit-camera``) is the check.

Subcommands
-----------
``fit-camera``
	Fit the top camera pose to real ``top_depth_v2`` frames by matching the arm silhouette rendered at the recorded
	joint state (needs the dataset copy).
``layout-prior``
	Measure bowl centres and brick positions on the real first and last top frames (input for ``simulate --prior``).
``simulate``
	Run a scripted pick-and-place per episode with physics grasping and store the full 3D state per frame (``qpos``),
	the actions and the layout. Nothing is rendered here.
``render``
	Replay the stored trajectories under random but plausible cameras and appearances, and write
	``offline_pipeline``-style episodes (``index.json`` + ``*.npz``) that ``lerobot_export.py`` turns into LeRobot v3.

Rendering is fastest on the CPU rasteriser in WSL (``LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe``, about 90 ms
per 640x480 colour frame against about 215 ms through the D3D12 GPU path) with several ``--workers``.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

os.environ.setdefault("MUJOCO_GL", "egl")
import mujoco

logger = logging.getLogger(__name__)

FPS = 30
SUBSTEPS = 16
JOINTS = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper")
STATE_NAMES = [f"{j}.pos" for j in JOINTS]
TASKS = {
	"green": "Pick up the brick and place it in the green bowl.",
	"pink": "Pick up the brick and place it in the pink bowl.",
}

# Follower calibration used for sort-depth-v2 (Studio project robot payload, ticks).
CALIBRATION = {
	"shoulder_pan": (1267, 3200),
	"shoulder_lift": (894, 3251),
	"elbow_flex": (849, 3045),
	"wrist_flex": (788, 3115),
	"wrist_roll": (2040, 3961),
	"gripper": (2041, 3508),
}
# Joint zero offsets from the camera-based joint calibration (robot.json), degrees: model = reading + offset.
OFFSETS_DEG = {"shoulder_lift": 1.5816, "elbow_flex": -4.6851, "wrist_flex": -1.3997}
TICKS_PER_DEG = 4096 / 360
GRIPPER_RAD = (-0.17453, 1.74533)  # Menagerie gripper range; assumed 0 = closed, 100 = open

TOP_FULL = (640, 480)
TOP_CROP = (96, 0, 512, 416)
FINE_MAX_M = 0.04
COARSE_MAX_M = 0.30
# Depth bridge plane-v2: camera 0.508 m above the table, optical axis 25.8 deg from vertical.
PLANE_HEIGHT_M = 0.508
PLANE_TILT_DEG = math.degrees(math.acos(0.8996))


def normalized_to_rad(u: np.ndarray) -> np.ndarray:
	"""Studio normalised joint values (6,) → Menagerie joint angles in radians."""
	u = np.asarray(u, dtype=np.float64)
	out = np.empty(6)
	for i, name in enumerate(JOINTS[:5]):
		lo, hi = CALIBRATION[name]
		deg = u[i] / 100.0 * (hi - lo) / 2.0 / TICKS_PER_DEG + OFFSETS_DEG.get(name, 0.0)
		out[i] = math.radians(deg)
	out[5] = GRIPPER_RAD[0] + np.clip(u[5], 0, 100) / 100.0 * (GRIPPER_RAD[1] - GRIPPER_RAD[0])
	return out


def rad_to_normalized(q: np.ndarray) -> np.ndarray:
	"""Inverse of :func:`normalized_to_rad`."""
	q = np.asarray(q, dtype=np.float64)
	out = np.empty(6)
	for i, name in enumerate(JOINTS[:5]):
		lo, hi = CALIBRATION[name]
		deg = math.degrees(q[i]) - OFFSETS_DEG.get(name, 0.0)
		out[i] = deg * TICKS_PER_DEG * 2.0 / (hi - lo) * 100.0
	out[5] = (q[5] - GRIPPER_RAD[0]) / (GRIPPER_RAD[1] - GRIPPER_RAD[0]) * 100.0
	return out.astype(np.float32)


def layered_height_image(height_m: np.ndarray, valid: np.ndarray) -> np.ndarray:
	"""Height above the table → RGB uint8 in the depth bridge ``layers`` encoding (R fine, G coarse, B valid)."""
	h = np.clip(np.where(valid, height_m, 0.0), 0.0, None)
	out = np.empty((*h.shape, 3), np.uint8)
	out[..., 0] = np.rint(255.0 * np.minimum(h / FINE_MAX_M, 1.0))
	out[..., 1] = np.rint(255.0 * np.minimum(h / COARSE_MAX_M, 1.0))
	out[..., 2] = np.where(valid, 255, 0)
	out[~valid, :2] = 0
	return out


@dataclass
class CameraPose:
	"""A camera above the table: horizontal position, height, view yaw, tilt from vertical, roll, focal length."""

	x: float
	y: float
	height: float = PLANE_HEIGHT_M
	yaw_deg: float = 0.0
	tilt_deg: float = PLANE_TILT_DEG
	roll_deg: float = 0.0
	focal_px: float = 615.0

	def axes(self) -> tuple[np.ndarray, np.ndarray]:
		"""MuJoCo camera x (image right) and y (image up) axes in the world."""
		t, p = math.radians(self.tilt_deg), math.radians(self.yaw_deg)
		forward = np.array([math.sin(t) * math.cos(p), math.sin(t) * math.sin(p), -math.cos(t)])
		up = np.array([math.cos(t) * math.cos(p), math.cos(t) * math.sin(p), math.sin(t)])
		right = np.cross(forward, up)
		r = math.radians(self.roll_deg)
		right, up = math.cos(r) * right + math.sin(r) * up, -math.sin(r) * right + math.cos(r) * up
		return right, up

	def mjcf(self, name: str, resolution: tuple[int, int]) -> str:
		right, up = self.axes()
		xy = " ".join(f"{v:.6f}" for v in (*right, *up))
		return (
			f'<camera name="{name}" pos="{self.x:.5f} {self.y:.5f} {self.height:.5f}" xyaxes="{xy}" '
			f'resolution="{resolution[0]} {resolution[1]}" focalpixel="{self.focal_px:.2f} {self.focal_px:.2f}" '
			f'sensorsize="{resolution[0] * 1e-5:.6f} {resolution[1] * 1e-5:.6f}"/>'
		)


def look_from(
	target: tuple[float, float], distance_xy: float, height: float, yaw_deg: float, **kw: float
) -> CameraPose:
	"""A camera ``distance_xy`` behind ``target`` (along -yaw) at ``height``, tilted to look at the target."""
	p = math.radians(yaw_deg)
	tilt = math.degrees(math.atan2(distance_xy, height))
	return CameraPose(
		target[0] - distance_xy * math.cos(p),
		target[1] - distance_xy * math.sin(p),
		height,
		yaw_deg,
		tilt,
		**kw,
	)


@dataclass
class Layout:
	"""Bowl centres, brick pose and appearance for one episode (base frame, metres / degrees)."""

	green: tuple[float, float]
	pink: tuple[float, float]
	brick_xy: tuple[float, float]
	brick_yaw_deg: float
	defective: bool
	brick_rgb: tuple[float, float, float] = (0.85, 0.1, 0.1)
	table_rgb: tuple[float, float, float] = (0.55, 0.5, 0.45)
	light_dir: tuple[float, float, float] = (0.0, 0.0, -1.0)
	light_level: float = 0.7
	distractors: list[tuple[float, float, float, float, float, float]] = field(default_factory=list)
	brick_size: tuple[float, float, float] = (0.0318, 0.0318, 0.0192)
	clutter: list[tuple[float, float, float, float, float, float]] = field(default_factory=list)
	markers: list[tuple[int, float, float, float, float]] = field(default_factory=list)
	tile_m: float = 0.30
	top: CameraPose | None = None
	front: CameraPose | None = None


GRASP_RADIUS_M = 0.03
# Real cell: plates about 20 cm across, Duplo-size bricks (2x2: 31.8 mm square, 19.2 mm high; 2x4: 63.6 mm long).
BOWL_R = 0.10
BOWL_H = 0.022
DUPLO_2X2 = (0.0318, 0.0318, 0.0192)
DUPLO_2X4 = (0.0636, 0.0318, 0.0192)
STUD_PITCH = 0.016
BRICK_COLOURS = ((0.95, 0.4, 0.05), (0.95, 0.8, 0.1), (0.1, 0.45, 0.85), (0.85, 0.1, 0.1), (0.55, 0.8, 0.15))
# Printed markers seen in the cell (defect_sorter.markers): id, black-square side in metres.
CELL_MARKERS = {10: 0.040, 11: 0.040, 16: 0.060, 17: 0.060}


def _bowl(name: str, xy: tuple[float, float], rgba: str) -> str:
	segs = []
	n = 64
	for k in range(n):
		a = 2 * math.pi * k / n
		cx, cy = xy[0] + BOWL_R * math.cos(a), xy[1] + BOWL_R * math.sin(a)
		half = BOWL_R * math.pi / n * 1.05
		segs.append(
			f'<geom type="box" size="0.003 {half:.4f} {BOWL_H / 2:.4f}" pos="{cx:.4f} {cy:.4f} {BOWL_H / 2:.4f}" '
			f'euler="0 -0.35 {a:.4f}" rgba="{rgba}"/>'
		)
	bottom = f'<geom type="cylinder" size="{BOWL_R:.3f} 0.0015" pos="{xy[0]:.4f} {xy[1]:.4f} 0.0015" rgba="{rgba}"/>'
	return f'<body name="{name}">{bottom}{"".join(segs)}</body>'


def _studs(size: tuple[float, float, float], rgba: str) -> str:
	"""Duplo studs on top of a brick of ``size`` (full extents), as visual-only cylinders."""
	nx, ny = max(1, round(size[0] / STUD_PITCH)), max(1, round(size[1] / STUD_PITCH))
	out = []
	for i in range(nx):
		for j in range(ny):
			x, y = (i - (nx - 1) / 2) * STUD_PITCH, (j - (ny - 1) / 2) * STUD_PITCH
			out.append(
				f'<geom type="cylinder" size="0.0047 0.0022" pos="{x:.4f} {y:.4f} {size[2] / 2 + 0.0022:.4f}" '
				f'rgba="{rgba}" contype="0" conaffinity="0" mass="0"/>'
			)
	return "".join(out)


def _brick(layout: Layout) -> str:
	sx, sy, sz = (v / 2 for v in layout.brick_size)
	rgba = " ".join(f"{c:.3f}" for c in layout.brick_rgb) + " 1"
	studs = [_studs(layout.brick_size, rgba)]
	cross = ""
	if layout.defective:
		for a in (0.785, -0.785):
			cross += (
				f'<geom type="box" size="{0.7 * sy:.4f} 0.0015 0.0003" pos="0 0 {sz + 0.0047:.4f}" euler="0 0 {a}" '
				f'rgba="0.05 0.05 0.08 1" contype="0" conaffinity="0" mass="0"/>'
			)
	yaw = math.radians(layout.brick_yaw_deg)
	return (
		f'<body name="brick" pos="{layout.brick_xy[0]:.4f} {layout.brick_xy[1]:.4f} {sz + 0.0005:.4f}" '
		f'euler="0 0 {yaw:.4f}"><freejoint name="brick"/>'
		f'<geom name="brick" type="box" size="{sx:.4f} {sy:.4f} {sz:.4f}" mass="0.008" friction="1.5 0.02 0.002" '
		f'rgba="{rgba}" solref="0.004 1"/>{"".join(studs)}{cross}</body>'
	)


def scene_xml(layout: Layout) -> str:
	"""MJCF for one episode; include it next to Menagerie's ``so101.xml``."""
	table = " ".join(f"{c:.3f}" for c in layout.table_rgb)
	tile2 = " ".join(f"{0.97 * c:.3f}" for c in layout.table_rgb)
	grout = " ".join(f"{0.72 * c:.3f}" for c in layout.table_rgb)
	ld = " ".join(f"{c:.3f}" for c in layout.light_dir)
	lv = layout.light_level
	distractors = "".join(
		f'<geom type="box" size="{sx:.3f} {sy:.3f} {sz:.3f}" pos="{x:.3f} {y:.3f} {sz:.3f}" '
		f'rgba="{0.2 + 0.6 * ((x * 37) % 1):.2f} {0.2 + 0.6 * ((y * 53) % 1):.2f} 0.5 1"/>'
		for x, y, sx, sy, sz, _ in layout.distractors
	)
	clutter = "".join(
		f'<body pos="{x:.4f} {y:.4f} {DUPLO_2X2[2] / 2 + 0.003:.4f}" euler="0 0 {yaw:.3f}">'
		f'<geom type="box" size="{DUPLO_2X2[0] / 2:.4f} {DUPLO_2X2[1] / 2:.4f} {DUPLO_2X2[2] / 2:.4f}" '
		f'rgba="{r:.2f} {g:.2f} {b:.2f} 1"/>{_studs(DUPLO_2X2, f"{r:.2f} {g:.2f} {b:.2f} 1")}</body>'
		for x, y, yaw, r, g, b in layout.clutter
	)
	marker_assets = "".join(
		f'<texture name="m{i}" type="2d" file="_marker_{i}.png"/><material name="m{i}" texture="m{i}" specular="0"/>'
		for i in sorted({m[0] for m in layout.markers})
	)
	marker_geoms = "".join(
		f'<geom type="box" size="{s / 2 * 1.25:.4f} {s / 2 * 1.25:.4f} 0.0004" pos="{x:.4f} {y:.4f} {z + 0.0004:.4f}" '
		f'euler="0 0 {yaw:.3f}" material="m{i}" contype="0" conaffinity="0"/>'
		for i, x, y, z, yaw in layout.markers
		for s in (CELL_MARKERS[i],)
	)
	cams = ""
	if layout.top:
		cams += layout.top.mjcf("top", TOP_FULL)
	if layout.front:
		cams += layout.front.mjcf("front", (640, 480))
	return f"""<mujoco model="sorting_cell">
  <include file="so101.xml"/>
  <option timestep="{1.0 / FPS / SUBSTEPS:.6f}" cone="elliptic" impratio="10"/>
  <visual><headlight diffuse="{0.3 * lv:.2f} {0.3 * lv:.2f} {0.3 * lv:.2f}" ambient="{0.35 * lv:.2f} {0.35 * lv:.2f} {0.35 * lv:.2f}" specular="0 0 0"/>
    <global offwidth="640" offheight="480"/><quality shadowsize="1024"/></visual>
  <asset>
    <texture name="sky" type="skybox" builtin="gradient" rgb1="0.75 0.75 0.78" rgb2="0.45 0.45 0.5" width="256" height="1536"/>
    <texture name="table" type="2d" builtin="checker" rgb1="{table}" rgb2="{tile2}" mark="edge" markrgb="{grout}" width="512" height="512"/>
    <material name="table" texture="table" texuniform="true" texrepeat="{1 / (2 * layout.tile_m):.3f} {1 / (2 * layout.tile_m):.3f}" reflectance="0"/>
    {marker_assets}
  </asset>
  <worldbody>
    <light pos="0.2 0 1.2" dir="{ld}" directional="true" diffuse="{0.6 * lv:.2f} {0.6 * lv:.2f} {0.6 * lv:.2f}" castshadow="true"/>
    <geom name="table" type="plane" size="3 3 0.05" material="table"/>
    {_bowl("green_bowl", layout.green, "0.25 0.65 0.3 1")}
    {_bowl("pink_bowl", layout.pink, "0.95 0.55 0.72 1")}
    {_brick(layout)}
    {distractors}
    {clutter}
    {marker_geoms}
    {cams}
  </worldbody>
</mujoco>
"""


def write_marker_textures(directory: Path, ids: set[int]) -> None:
	"""ArUco 4x4_50 images (black square plus a white margin of a quarter side) for the marker geoms."""
	import cv2

	dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
	for i in ids:
		path = directory / f"_marker_{i}.png"
		if not path.exists():
			img = cv2.aruco.generateImageMarker(dictionary, i, 192)
			cv2.imwrite(str(path), cv2.copyMakeBorder(img, 24, 24, 24, 24, cv2.BORDER_CONSTANT, value=255))


class Cell:
	"""One episode's MuJoCo model with renderers for the dataset cameras."""

	def __init__(self, layout: Layout, menagerie: Path) -> None:
		write_marker_textures(menagerie, {m[0] for m in layout.markers})
		path = menagerie / f"_sorting_cell_{os.getpid()}.xml"
		path.write_text(scene_xml(layout), encoding="utf-8")
		self.layout = layout
		self.model = mujoco.MjModel.from_xml_path(str(path))
		self.data = mujoco.MjData(self.model)
		self.site = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_SITE, "gripperframe")
		self.brick_body = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, "brick")
		self.renderer = mujoco.Renderer(self.model, 480, 640)
		self.qadr = [self.model.joint(j).qposadr[0] for j in JOINTS]
		self.held: tuple[np.ndarray, np.ndarray] | None = None

	def set_joints(self, q: np.ndarray) -> None:
		self.data.qpos[self.qadr] = q
		self.data.ctrl[:6] = q
		mujoco.mj_forward(self.model, self.data)

	def set_camera(self, name: str, pose: CameraPose) -> None:
		"""Move an existing camera in place (no recompilation)."""
		cid = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_CAMERA, name)
		right, up = pose.axes()
		mat = np.column_stack([right, up, np.cross(right, up)])
		quat = np.zeros(4)
		mujoco.mju_mat2Quat(quat, mat.flatten())
		self.model.cam_pos[cid] = (pose.x, pose.y, pose.height)
		self.model.cam_quat[cid] = quat
		width = self.model.cam_resolution[cid][0]
		self.model.cam_intrinsic[cid][:2] = pose.focal_px * self.model.cam_sensorsize[cid][0] / width
		mujoco.mj_forward(self.model, self.data)

	def joints(self) -> np.ndarray:
		return self.data.qpos[self.qadr].copy()

	def step(self, ctrl: np.ndarray) -> None:
		self.data.ctrl[:6] = ctrl
		mujoco.mj_step(self.model, self.data, nstep=SUBSTEPS)

	def update_grasp(self, gripper_cmd: float) -> None:
		"""Assisted grasp: once the jaws are commanded closed with the brick between them, the brick follows the
		gripper rigidly until the jaws are commanded open again. Contact physics still positions the brick while the
		jaws close; holding it is not left to friction, which makes the scripted demonstrations reliable."""
		m, d = self.model, self.data
		grip_body = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "gripper")
		if self.held is None:
			closed = gripper_cmd < 0.0 and d.qpos[self.qadr[5]] < 0.35
			near = np.linalg.norm(self.brick_pos() - d.site_xpos[self.site]) < GRASP_RADIUS_M
			if closed and near:
				rot_g = d.xmat[grip_body].reshape(3, 3)
				rot_b = d.xmat[self.brick_body].reshape(3, 3)
				self.held = (rot_g.T @ (self.brick_pos() - d.xpos[grip_body]), rot_g.T @ rot_b)
			return
		if gripper_cmd > 0.3:
			self.held = None
			return
		rel_p, rel_r = self.held
		rot_g = d.xmat[grip_body].reshape(3, 3)
		adr = m.joint("brick").qposadr[0]
		vadr = m.joint("brick").dofadr[0]
		d.qpos[adr : adr + 3] = d.xpos[grip_body] + rot_g @ rel_p
		quat = np.zeros(4)
		mujoco.mju_mat2Quat(quat, (rot_g @ rel_r).flatten())
		d.qpos[adr + 3 : adr + 7] = quat
		d.qvel[vadr : vadr + 6] = 0.0
		mujoco.mj_forward(m, d)

	def brick_pos(self) -> np.ndarray:
		return self.data.xpos[self.brick_body].copy()

	def rgb(self, camera: str) -> np.ndarray:
		self.renderer.disable_depth_rendering()
		self.renderer.update_scene(self.data, camera)
		return self.renderer.render().copy()

	def height(self, camera: str) -> tuple[np.ndarray, np.ndarray]:
		"""Height above the table per pixel of ``camera`` (full resolution) and a validity mask."""
		self.renderer.enable_depth_rendering()
		self.renderer.update_scene(self.data, camera)
		depth = self.renderer.render().astype(np.float64)
		self.renderer.disable_depth_rendering()
		cid = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_CAMERA, camera)
		pos, mat = self.data.cam_xpos[cid], self.data.cam_xmat[cid].reshape(3, 3)
		f = self.model.cam_intrinsic[cid][0] / self.model.cam_sensorsize[cid][0] * 640
		hgt, wid = depth.shape
		u, v = np.meshgrid(np.arange(wid) + 0.5, np.arange(hgt) + 0.5)
		ray = np.stack([(u - wid / 2) / f, -(v - hgt / 2) / f, -np.ones_like(u)], axis=-1)
		world_z = pos[2] + (ray @ mat.T)[..., 2] * depth
		valid = depth < 5.0
		return world_z, valid

	def top_images(self) -> tuple[np.ndarray, np.ndarray]:
		"""(top_rgb_v2, top_depth_v2) cropped like the depth bridge."""
		x, y, w, h = TOP_CROP
		rgb = self.rgb("top")[y : y + h, x : x + w]
		z, valid = self.height("top")
		depth = layered_height_image(z[y : y + h, x : x + w], valid[y : y + h, x : x + w])
		return rgb, depth


# --- inverse kinematics and the scripted expert -------------------------------------------------------------


def ik(cell: Cell, target: np.ndarray, q0: np.ndarray, roll: float, iters: int = 200) -> np.ndarray:
	"""Joint angles putting ``gripperframe`` at ``target`` with the jaws pointing down (damped least squares)."""
	m, d = cell.model, cell.data
	q = q0.copy()
	jacp = np.zeros((3, m.nv))
	jacr = np.zeros((3, m.nv))
	lo = m.jnt_range[[m.joint(j).id for j in JOINTS[:5]], 0]
	hi = m.jnt_range[[m.joint(j).id for j in JOINTS[:5]], 1]
	saved = d.qpos.copy()
	for _ in range(iters):
		d.qpos[cell.qadr[:5]] = q[:5]
		mujoco.mj_kinematics(m, d)
		mujoco.mj_comPos(m, d)
		err_p = target - d.site_xpos[cell.site]
		approach = d.site_xmat[cell.site].reshape(3, 3)[:, 0]
		err_r = np.cross(approach, np.array([0.0, 0.0, -1.0]))
		mujoco.mj_jacSite(m, d, jacp, jacr, cell.site)
		cols = [m.joint(j).dofadr[0] for j in JOINTS[:4]]
		j = np.vstack([jacp[:, cols], 0.3 * jacr[:, cols]])
		e = np.concatenate([err_p, 0.3 * err_r])
		dq = j.T @ np.linalg.solve(j @ j.T + 1e-4 * np.eye(6), e)
		q[:4] = np.clip(q[:4] + dq, lo[:4], hi[:4])
		if np.linalg.norm(err_p) < 5e-4:
			break
	q[4] = np.clip(roll, lo[4], hi[4])
	d.qpos[:] = saved
	mujoco.mj_forward(m, d)
	return q


def jaw_direction(cell: Cell, q: np.ndarray) -> np.ndarray:
	"""Horizontal unit vector from the fixed jaw (``gripperframe``) towards the moving jaw at joint angles ``q``."""
	m, d = cell.model, cell.data
	saved = d.qpos.copy()
	d.qpos[cell.qadr] = q
	mujoco.mj_kinematics(m, d)
	jaw = d.xipos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "moving_jaw_so101_v1")]
	v = (jaw - d.site_xpos[cell.site])[:2]
	d.qpos[:] = saved
	mujoco.mj_forward(m, d)
	return v / max(np.linalg.norm(v), 1e-9)


def best_roll(cell: Cell, q: np.ndarray, axis_xy: np.ndarray) -> tuple[float, float]:
	"""Wrist roll that lines the jaw opening up with ``axis_xy`` (either sign), and that sign."""
	lo, hi = cell.model.jnt_range[cell.model.joint("wrist_roll").id]
	best = (-np.inf, 0.0, 1.0)
	for roll in np.linspace(lo, hi, 181):
		qq = q.copy()
		qq[4] = roll
		qq[5] = 0.75
		c = float(jaw_direction(cell, qq) @ axis_xy)
		score = abs(c) - 0.02 * abs(roll)
		if score > best[0]:
			best = (score, float(roll), math.copysign(1.0, c))
	return best[1], best[2]


def min_jerk(n: int) -> np.ndarray:
	s = np.linspace(0.0, 1.0, n)
	return 10 * s**3 - 15 * s**4 + 6 * s**5


RELEASE_REACH_M = 0.34


def release_point(bowl: tuple[float, float]) -> tuple[float, float]:
	"""Where to open the jaws over a bowl: its centre, or the point on the near side within easy reach (at most
	0.6 bowl radii from the centre), as the operator does for the far bowl in the real recordings."""
	c = np.asarray(bowl, dtype=np.float64)
	r = float(np.hypot(*c))
	shift = min(max(r - RELEASE_REACH_M, 0.0), 0.6 * BOWL_R)
	p = c - shift * c / max(r, 1e-9)
	return float(p[0]), float(p[1])


def expert_plan(cell: Cell, rest: np.ndarray, rng: np.random.Generator) -> list[np.ndarray]:
	"""Joint targets (radians, one per frame) for hover → grasp → lift → bowl → release → rest."""
	lay = cell.layout
	bowl = release_point(lay.pink if lay.defective else lay.green)
	bx, by = lay.brick_xy
	yaw = math.radians(lay.brick_yaw_deg)
	short_axis = np.array([-math.sin(yaw), math.cos(yaw)])
	open_g, closed_g = 1.3, -0.17
	hover = np.array([bx, by, 0.09])
	q_hover = ik(cell, hover, rest.copy(), 0.0)
	roll, sign = best_roll(cell, q_hover, short_axis)
	# gripperframe sits on the fixed jaw: put that jaw just outside the brick's long side, the moving jaw opposite.
	offset = -sign * short_axis * (lay.brick_size[1] / 2 + 0.006)
	gx, gy = bx + offset[0], by + offset[1]
	z_grip = 0.004
	q = rest.copy()
	keys: list[tuple[np.ndarray, float]] = []

	def at(x: float, y: float, z: float, g: float, secs: float) -> None:
		nonlocal q
		q = ik(cell, np.array([x, y, z]), q, roll)
		q[5] = g
		keys.append((q.copy(), secs))

	speed = rng.uniform(0.8, 1.25)
	at(gx, gy, 0.09, open_g, 2.5)
	at(gx, gy, z_grip + 0.02, open_g, 1.5)
	at(gx, gy, z_grip, open_g, 0.8)
	at(gx, gy, z_grip, closed_g, 1.0)
	at(gx, gy, 0.10, closed_g, 1.2)
	at(bowl[0], bowl[1], 0.11, closed_g, 2.2)
	at(bowl[0], bowl[1], 0.06, closed_g, 0.8)
	at(bowl[0], bowl[1], 0.06, open_g, 0.6)
	at(bowl[0], bowl[1], 0.12, open_g, 0.8)
	keys.append((rest.copy(), 2.5))
	frames = [rest.copy() for _ in range(int(FPS * rng.uniform(0.5, 1.2)))]
	prev = rest.copy()
	for target, secs in keys:
		n = max(2, int(secs * speed * FPS))
		for s in min_jerk(n)[1:]:
			frames.append(prev + s * (target - prev))
		frames.extend([target.copy()] * int(FPS * 0.2))
		prev = target
	return frames


# --- randomisation -------------------------------------------------------------------------------------------


def sample_layout(
	rng: np.random.Generator, nominal_top: CameraPose, defective: bool, prior: list[dict] | None = None
) -> Layout:
	"""A plausible random cell: bowls and brick inside reach, colours, light, clutter, markers, cameras.

	With ``prior`` (layouts measured on real first frames, see ``layout-prior``), the bowls start from a real
	episode's bowl centres and the brick from a real brick position, each jittered by a few centimetres, so the
	synthetic scenes cover the arrangements the real dataset shows. Without it, positions are uniform in reach.
	"""
	for _ in range(1000):
		if prior:
			ref = prior[rng.integers(len(prior))]
			bowls = [tuple(np.array(ref[c]) + rng.normal(0, 0.015, 2)) for c in ("green", "pink")]
			bricks = [p["brick"] for p in prior if p.get("brick")]
			brick = tuple(np.array(bricks[rng.integers(len(bricks))]) + rng.normal(0, 0.025, 2))
		else:
			r_b, a_b = rng.uniform(0.17, 0.25), rng.uniform(-0.6, 0.6)
			bowls = []
			for _ in range(2):
				r, a = rng.uniform(0.21, 0.27), rng.uniform(-1.1, 1.1)
				bowls.append((r * math.cos(a), r * math.sin(a)))
			brick = (r_b * math.cos(a_b), r_b * math.sin(a_b))
		pts = np.array([*bowls, brick])
		dist = [np.hypot(*(pts[i] - pts[j])) for i in range(3) for j in range(i + 1, 3)]
		reach = np.hypot(pts[:, 0], pts[:, 1])
		if (
			dist[0] > 2 * BOWL_R - 0.01
			and dist[1] > BOWL_R + 0.03
			and dist[2] > BOWL_R + 0.03
			and reach[2] < 0.40
			and np.hypot(*release_point(bowls[0])) < 0.40
			and np.hypot(*release_point(bowls[1])) < 0.40
			and reach.min() > 0.14
		):
			break
	else:
		raise RuntimeError("no layout satisfied the spacing and reach limits")
	size = DUPLO_2X4 if rng.random() < 0.2 else DUPLO_2X2
	distractors = []
	for _ in range(rng.integers(0, 3)):
		r, a = rng.uniform(0.33, 0.45), rng.uniform(-1.4, 1.4)
		distractors.append((r * math.cos(a), r * math.sin(a), *rng.uniform(0.01, 0.03, 3), 0.0))
	clutter = []
	for bowl in bowls:
		for _ in range(rng.integers(0, 5)):
			r, a = BOWL_R * 0.6 * math.sqrt(rng.random()), rng.uniform(0, 2 * math.pi)
			c = BRICK_COLOURS[rng.integers(len(BRICK_COLOURS))]
			clutter.append((bowl[0] + r * math.cos(a), bowl[1] + r * math.sin(a), rng.uniform(0, math.pi), *c))
	markers = []
	for i, bowl in zip((10, 11), bowls, strict=True):
		r, a = BOWL_R * rng.uniform(0.2, 0.55), rng.uniform(0, 2 * math.pi)
		markers.append((i, bowl[0] + r * math.cos(a), bowl[1] + r * math.sin(a), 0.003, rng.uniform(-0.4, 0.4)))
	for i in (16, 17):
		if rng.random() < 0.7:
			r, a = rng.uniform(0.2, 0.32), rng.uniform(-1.3, -0.5) * (1 if i == 16 else -1)
			markers.append((i, r * math.cos(a), r * math.sin(a), 0.0, rng.uniform(-0.3, 0.3)))
	top = CameraPose(
		nominal_top.x + rng.normal(0, 0.01),
		nominal_top.y + rng.normal(0, 0.01),
		nominal_top.height + rng.normal(0, 0.01),
		nominal_top.yaw_deg + rng.normal(0, 2.0),
		nominal_top.tilt_deg + rng.normal(0, 1.5),
		rng.normal(0, 1.0),
		nominal_top.focal_px * rng.uniform(0.98, 1.02),
	)
	front = look_from(
		(0.2, 0.0),
		rng.uniform(0.45, 0.65),
		rng.uniform(0.22, 0.38),
		rng.uniform(150, 210),
		focal_px=rng.uniform(480, 560),
	)
	t = rng.uniform(0.0, 1.0)
	return Layout(
		green=bowls[0],
		pink=bowls[1],
		brick_xy=brick,
		brick_yaw_deg=float(rng.uniform(-90, 90)),
		defective=defective,
		brick_rgb=BRICK_COLOURS[rng.integers(len(BRICK_COLOURS))],
		table_rgb=tuple(np.clip(0.66 + rng.normal(0, 0.05) + rng.normal(0, 0.015, 3), 0.3, 0.85)),
		tile_m=float(rng.uniform(0.25, 0.6)),
		light_dir=(float(rng.normal(0, 0.4)), float(rng.normal(0, 0.4)), -1.0),
		light_level=float(0.6 + 0.4 * t),
		distractors=distractors,
		brick_size=size,
		clutter=clutter,
		markers=markers,
		top=top,
		front=front,
	)


# --- camera fit against real frames ------------------------------------------------------------------------


def _real_frames(dataset: Path, indices: list[int]) -> tuple[np.ndarray, np.ndarray]:
	import av
	import pyarrow.parquet as pq

	table = pq.read_table(dataset / "data/chunk-000/file-000.parquet", columns=["observation.state", "index"])
	states = np.stack(table.column("observation.state").to_numpy(zero_copy_only=False))
	wanted = set(indices)
	frames = {}
	with av.open(str(dataset / "videos/observation.images.top_depth_v2/chunk-000/file-000.mp4")) as c:
		for i, f in enumerate(c.decode(video=0)):
			if i in wanted:
				frames[i] = f.to_ndarray(format="rgb24")
			if i >= max(indices):
				break
	return np.stack([frames[i] for i in indices]), states[indices]


def fit_camera(dataset: Path, menagerie: Path, indices: list[int], out: Path) -> CameraPose:
	"""Fit top camera x, y, yaw (then height, tilt, focal) so the rendered arm matches the real depth silhouettes."""
	from scipy.optimize import minimize

	real, states = _real_frames(dataset, indices)
	real_mask = real[..., 1] > int(255 * 0.04 / COARSE_MAX_M)
	layout = Layout(green=(0.0, 1.0), pink=(0.0, -1.0), brick_xy=(2.0, 2.0), brick_yaw_deg=0.0, defective=False)

	layout.top = look_from((0.2, 0.0), 0.25, PLANE_HEIGHT_M, 0.0)
	cell = Cell(layout, menagerie)

	def score(p: CameraPose) -> float:
		cell.set_camera("top", p)
		ious = []
		for k, s in enumerate(states):
			cell.set_joints(normalized_to_rad(s))
			z, valid = cell.height("top")
			x0, y0, w, h = TOP_CROP
			sim = (z[y0 : y0 + h, x0 : x0 + w] > 0.04) & valid[y0 : y0 + h, x0 : x0 + w]
			union = np.logical_or(sim, real_mask[k]).sum()
			ious.append(np.logical_and(sim, real_mask[k]).sum() / max(union, 1))
		return float(np.mean(ious))

	best = (-1.0, None)
	t0 = time.perf_counter()
	for yaw in range(0, 360, 15):
		for dist in (0.15, 0.25, 0.35):
			for tx in (0.1, 0.2, 0.3):
				for ty in (-0.15, 0.0, 0.15):
					p = look_from((tx, ty), dist, PLANE_HEIGHT_M, yaw)
					p.tilt_deg = PLANE_TILT_DEG
					s = score(p)
					if s > best[0]:
						best = (s, p)
	logger.info("grid best IoU %.3f at %s (%.0f s)", best[0], best[1], time.perf_counter() - t0)

	def loss(v: np.ndarray) -> float:
		return -score(CameraPose(v[0], v[1], v[2], v[3], v[4], v[5], v[6]))

	b = best[1]
	v0 = np.array([b.x, b.y, b.height, b.yaw_deg, b.tilt_deg, 0.0, b.focal_px])
	simplex = np.vstack([v0, v0 + np.diag([0.03, 0.03, 0.02, 6.0, 3.0, 2.0, 25.0])])
	res = minimize(loss, v0, method="Nelder-Mead", options={"maxfev": 250, "initial_simplex": simplex})
	pose = CameraPose(*res.x)
	result = {"camera": asdict(pose), "iou": -res.fun, "grid_iou": best[0], "frames": indices}
	out.parent.mkdir(parents=True, exist_ok=True)
	out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
	logger.info("refined IoU %.3f: %s", -res.fun, pose)
	return pose


# --- episode generation: simulate once, render many views ---------------------------------------------------


def sample_top_camera(rng: np.random.Generator, nominal: CameraPose) -> CameraPose:
	"""A top camera near the fitted real one (±3 cm, ±5 deg yaw, ±3 deg tilt, ±3 % focal)."""
	return CameraPose(
		nominal.x + rng.uniform(-0.03, 0.03),
		nominal.y + rng.uniform(-0.03, 0.03),
		nominal.height + rng.uniform(-0.03, 0.03),
		nominal.yaw_deg + rng.uniform(-5.0, 5.0),
		nominal.tilt_deg + rng.uniform(-3.0, 3.0),
		nominal.roll_deg + rng.uniform(-1.5, 1.5),
		nominal.focal_px * rng.uniform(0.97, 1.03),
	)


def sample_front_camera(rng: np.random.Generator) -> CameraPose:
	"""A low side camera looking across the workspace from the side opposite the robot."""
	return look_from(
		(0.22, 0.0),
		rng.uniform(0.45, 0.65),
		rng.uniform(0.22, 0.38),
		rng.uniform(155, 205),
		focal_px=rng.uniform(480, 560),
	)


def project(pose: CameraPose, points: np.ndarray, resolution: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
	"""Pixel coordinates (u right, v down) of world points, and whether each lies in front of the camera."""
	right, up = pose.axes()
	forward = np.cross(up, right)
	rel = np.asarray(points, dtype=np.float64) - np.array([pose.x, pose.y, pose.height])
	x, y, z = rel @ right, rel @ up, rel @ forward
	in_front = z > 0.05
	z = np.where(in_front, z, 1.0)
	u = resolution[0] / 2 + pose.focal_px * x / z
	v = resolution[1] / 2 - pose.focal_px * y / z
	return np.stack([u, v], axis=-1), in_front


def bowl_rim_points(xy: tuple[float, float], n: int = 16) -> np.ndarray:
	a = np.linspace(0, 2 * math.pi, n, endpoint=False)
	return np.stack([xy[0] + BOWL_R * np.cos(a), xy[1] + BOWL_R * np.sin(a), np.full(n, BOWL_H)], axis=-1)


def top_view_ok(pose: CameraPose, layout: dict, tcp_path: np.ndarray, margin_px: float = 20.0) -> tuple[bool, str]:
	"""Whether a top camera is plausible: above the table, sees bowls, brick and the gripper path inside the crop
	with a margin, and shows the brick at least 15 px across."""
	if pose.height < 0.25 or not 10.0 <= pose.tilt_deg <= 45.0:
		return False, "pose out of range"
	size = layout.get("brick_size", DUPLO_2X2)
	brick = np.array([[*layout["brick_xy"], size[2]]])
	pts = np.vstack([bowl_rim_points(layout["green"]), bowl_rim_points(layout["pink"]), brick, tcp_path])
	uv, front = project(pose, pts, TOP_FULL)
	x0, y0, w, h = TOP_CROP
	inside = (uv[:, 0] > x0 + margin_px) & (uv[:, 0] < x0 + w - margin_px) & (uv[:, 1] > y0 + margin_px)
	inside &= uv[:, 1] < y0 + h - margin_px
	if not (front.all() and inside.all()):
		return False, f"{int((~inside).sum())} key points outside the crop"
	ends, _ = project(pose, brick + np.array([[size[0] / 2, 0, 0], [-size[0] / 2, 0, 0]]), TOP_FULL)
	if np.linalg.norm(ends[0] - ends[1]) < 15.0:
		return False, "brick too small"
	return True, ""


def _decode_height(depth_rgb: np.ndarray) -> np.ndarray:
	"""Height above the table (m, NaN where invalid) from a ``layers``-encoded depth image."""
	r, g, b = (depth_rgb[..., k].astype(np.float64) for k in range(3))
	fine = g < 255 * 0.035 / COARSE_MAX_M
	h = np.where(fine, r / 255 * FINE_MAX_M, g / 255 * COARSE_MAX_M)
	return np.where(b > 128, h, np.nan)


def table_point(pose: CameraPose, u: np.ndarray, v: np.ndarray, z: float) -> np.ndarray:
	"""Where the rays through full-frame pixels (u, v) meet the horizontal plane at height ``z``."""
	right, up = pose.axes()
	forward = np.cross(up, right)
	x = (np.asarray(u, np.float64) - TOP_FULL[0] / 2) / pose.focal_px
	y = -(np.asarray(v, np.float64) - TOP_FULL[1] / 2) / pose.focal_px
	ray = x[:, None] * right + y[:, None] * up + forward
	t = (z - pose.height) / ray[:, 2]
	return np.array([pose.x, pose.y]) + t[:, None] * ray[:, :2]


def layout_prior(dataset: Path, camera_file: Path, out: Path) -> list[dict]:
	"""Bowl centres and the brick position of every real episode, measured on its first and last top frames.

	Bowls are the largest green / pink regions in ``top_rgb_v2``; their outline is projected onto the rim plane
	through the nominal top camera and fitted with a circle. The brick is where the height dropped between the
	first and last ``top_depth_v2`` frames outside the bowls (it was picked up), projected at its top face.
	Positions are only as good as the camera; rendering through the same camera puts them back where they were.
	"""
	import av
	import cv2
	import pyarrow.parquet as pq

	pose = CameraPose(**json.loads(camera_file.read_text())["camera"])
	ep = pq.read_table(dataset / "meta/episodes/chunk-000/file-000.parquet").to_pydict()
	starts, ends = list(ep["dataset_from_index"]), list(ep["dataset_to_index"])
	want = {s + 3: (e, "first") for e, s in enumerate(starts)} | {t - 3: (e, "last") for e, t in enumerate(ends)}
	frames: dict[tuple[str, int, str], np.ndarray] = {}
	for cam in ("top_rgb_v2", "top_depth_v2"):
		with av.open(str(dataset / f"videos/observation.images.{cam}/chunk-000/file-000.mp4")) as c:
			for i, f in enumerate(c.decode(video=0)):
				if i in want:
					frames[(cam, *want[i])] = f.to_ndarray(format="rgb24")
				if i >= max(want):
					break
	x0, y0 = TOP_CROP[:2]
	result = []
	for e in range(len(starts)):
		hsv = cv2.cvtColor(frames[("top_rgb_v2", e, "first")], cv2.COLOR_RGB2HSV)
		hue, sat, val = hsv[..., 0], hsv[..., 1], hsv[..., 2]
		masks = {
			"green": (hue > 45) & (hue < 90) & (sat > 80),
			"pink": ((hue > 160) | (hue < 8)) & (sat > 40) & (sat < 160) & (val > 140),
		}
		entry: dict = {"episode": e}
		for name, mask in masks.items():
			m = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
			n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
			if n < 2:
				continue
			k = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
			hull = cv2.convexHull(cv2.findNonZero((lab == k).astype(np.uint8)))[:, 0]
			w = table_point(pose, hull[:, 0] + x0, hull[:, 1] + y0, BOWL_H)
			a = np.c_[2 * w, np.ones(len(w))]
			cx, cy, c0 = np.linalg.lstsq(a, (w**2).sum(1), rcond=None)[0]
			entry[name] = [float(cx), float(cy)]
			entry[f"{name}_r"] = float(math.sqrt(max(c0 + cx * cx + cy * cy, 0.0)))
		h0 = _decode_height(frames[("top_depth_v2", e, "first")])
		h1 = _decode_height(frames[("top_depth_v2", e, "last")])
		drop = (np.nan_to_num(h0 - h1) > 0.008) & (np.nan_to_num(h0) < 0.06)
		drop = cv2.morphologyEx(drop.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
		n, lab, stats, cen = cv2.connectedComponentsWithStats(drop)
		for k in np.argsort(-stats[1:, cv2.CC_STAT_AREA]) + 1:
			if not 300 < stats[k, cv2.CC_STAT_AREA] < 4000:
				continue
			xy = table_point(pose, np.array([cen[k][0] + x0]), np.array([cen[k][1] + y0]), 0.02)[0]
			inside = [np.hypot(*(xy - entry[b])) < entry[f"{b}_r"] for b in ("green", "pink") if b in entry]
			if not any(inside):
				entry["brick"] = [float(xy[0]), float(xy[1])]
				break
		result.append(entry)
		logger.info("episode %d: %s", e, entry)
	out.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
	return result


def _simulate_one(job: tuple) -> dict:
	menagerie, nominal, prior, out, e, seed, rest_u = job
	rng = np.random.default_rng([seed, e])
	rest = normalized_to_rad(rest_u)
	defective = bool(rng.random() < 0.35)
	for _ in range(500):
		layout = sample_layout(rng, nominal, defective, prior)
		if top_view_ok(nominal, asdict(layout), np.zeros((0, 3)), margin_px=30.0)[0]:
			break
	else:
		raise RuntimeError("no layout fits the nominal top camera; check the camera file")
	start = rest + np.concatenate([rng.normal(0, 0.05, 5), [0.0]])
	cell = Cell(layout, menagerie)
	cell.set_joints(start)
	plan = expert_plan(cell, start, rng)
	qpos, state, action, tcp = [], [], [], []
	for target in plan:
		noisy = target + np.concatenate([rng.normal(0, 0.004, 5), [0.0]])
		qpos.append(cell.data.qpos.copy())
		state.append(rad_to_normalized(cell.joints()))
		action.append(rad_to_normalized(noisy))
		tcp.append(cell.data.site_xpos[cell.site].copy())
		cell.step(noisy)
		cell.update_grasp(float(target[5]))
	bowl = np.array(layout.pink if defective else layout.green)
	brick = cell.brick_pos()
	success = bool(np.hypot(*(brick[:2] - bowl)) < BOWL_R and brick[2] < 0.05)
	name = f"sim_{e:04d}"
	np.savez_compressed(
		out / f"{name}.npz",
		qpos=np.array(qpos),
		state=np.array(state, np.float32),
		action=np.array(action, np.float32),
		tcp=np.array(tcp),
	)
	entry = {
		"name": name,
		"length": len(plan),
		"success": success,
		"final_brick": brick.tolist(),
		"task": TASKS["pink" if defective else "green"],
		"defective": defective,
		"layout": {k: v for k, v in asdict(layout).items() if k not in ("top", "front")},
	}
	(out / f"{name}.json").write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
	cell.renderer.close()
	logger.info(
		"simulated %s: %d frames, %s bowl, success=%s", name, len(plan), "pink" if defective else "green", success
	)
	return entry


def _pool(workers: int):
	import multiprocessing
	from concurrent.futures import ProcessPoolExecutor

	return ProcessPoolExecutor(workers, mp_context=multiprocessing.get_context("spawn"))


def simulate(
	menagerie: Path,
	camera_file: Path,
	out: Path,
	episodes: int,
	seed: int,
	rest_u: np.ndarray,
	prior_file: Path | None = None,
	workers: int = 1,
) -> list[dict]:
	"""Run scripted episodes with physics grasping; store full 3D state per frame (qpos), actions and the layout.

	Episode ``e`` draws everything from ``default_rng([seed, e])``, so results do not depend on ``workers``.
	"""
	nominal = CameraPose(**json.loads(camera_file.read_text())["camera"])
	prior = [p for p in json.loads(prior_file.read_text()) if "green" in p and "pink" in p] if prior_file else None
	out.mkdir(parents=True, exist_ok=False)
	jobs = [(menagerie, nominal, prior, out, e, seed, rest_u) for e in range(episodes)]
	if workers <= 1:
		return [_simulate_one(j) for j in jobs]
	with _pool(workers) as pool:
		return list(pool.map(_simulate_one, jobs))


CAMERA_SHAPES = {
	"front": [480, 640, 3],
	"top_rgb_v2": [416, 512, 3],
	"top_depth_v2": [416, 512, 3],
	"wrist": [480, 640, 3],
}


def _render_one(job: tuple) -> dict | None:
	menagerie, nominal, meta_path, out, k, seed, stride = job
	meta = json.loads(meta_path.read_text())
	rng = np.random.default_rng([seed, int(meta["name"].split("_")[1]), k])
	traj = np.load(meta_path.with_suffix(".npz"))
	lay = dict(meta["layout"])
	low = traj["tcp"][traj["tcp"][:, 2] < 0.12]
	rejected, why = 0, ""
	for _ in range(200):
		top = sample_top_camera(rng, nominal)
		ok, why = top_view_ok(top, lay, low[:: max(1, len(low) // 40)])
		if ok:
			break
		rejected += 1
	else:
		logger.warning("%s view %d: no plausible top camera (%s)", meta["name"], k, why)
		return None
	layout = Layout(**{**lay, "top": top, "front": sample_front_camera(rng)})
	layout.table_rgb = tuple(np.clip(np.array(lay["table_rgb"]) + rng.normal(0, 0.03, 3), 0.3, 0.85))
	layout.light_level = float(rng.uniform(0.6, 1.0))
	layout.light_dir = (float(rng.normal(0, 0.4)), float(rng.normal(0, 0.4)), -1.0)
	cell = Cell(layout, menagerie)
	cams: dict[str, list[np.ndarray]] = {c: [] for c in CAMERA_SHAPES}
	frames = list(range(0, meta["length"], stride))
	for t in frames:
		cell.data.qpos[:] = traj["qpos"][t]
		mujoco.mj_forward(cell.model, cell.data)
		top_rgb, top_depth = cell.top_images()
		cams["top_rgb_v2"].append(top_rgb)
		cams["top_depth_v2"].append(top_depth)
		cams["front"].append(cell.rgb("front"))
		cams["wrist"].append(cell.rgb("wrist_cam"))
	cell.renderer.close()
	name = f"{meta['name']}_v{k:02d}.npz"
	np.savez_compressed(
		out / name,
		state=traj["state"][frames],
		action=traj["action"][frames],
		**{c: np.array(v, np.uint8) for c, v in cams.items()},
	)
	logger.info("rendered %s (%d frames)", name, len(frames))
	return {
		"file": name,
		"length": len(frames),
		"success": True,
		"task": meta["task"],
		"defective": meta["defective"],
		"sim_episode": meta["name"],
		"top_camera": asdict(top),
		"front_camera": asdict(layout.front),
		"rejected_cameras": rejected,
	}


def render_views(
	menagerie: Path,
	camera_file: Path,
	sim_dir: Path,
	out: Path,
	views: int,
	seed: int,
	stride: int = 1,
	workers: int = 1,
) -> dict:
	"""Replay every successful simulated episode under ``views`` random plausible cameras and appearances.

	Writes the ``offline_pipeline`` format (``index.json`` + one ``.npz`` per rendered episode), which
	``lerobot_export.py --video --robot-type SO101_Follower`` turns into a dataset shaped like sort-depth-v2.
	"""
	nominal = CameraPose(**json.loads(camera_file.read_text())["camera"])
	out.mkdir(parents=True, exist_ok=False)
	metas = [p for p in sorted(sim_dir.glob("sim_*.json")) if json.loads(p.read_text())["success"]]
	jobs = [(menagerie, nominal, p, out, k, seed, stride) for p in metas for k in range(views)]
	if workers <= 1:
		results = [_render_one(j) for j in jobs]
	else:
		with _pool(workers) as pool:
			results = list(pool.map(_render_one, jobs))
	episodes = [r for r in results if r is not None]
	index = {
		"fps": FPS // stride,
		"state_names": STATE_NAMES,
		"cameras": CAMERA_SHAPES,
		"source": "mujoco-sim",
		"menagerie_commit": "370c43965323c0944b433b202aac5058b5f907a9",
		"episodes": episodes,
		"rejected_cameras": sum(r["rejected_cameras"] for r in episodes),
	}
	(out / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
	return index


def main(argv: list[str] | None = None) -> int:
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("--menagerie", type=Path, default=Path("~/sim/mujoco_menagerie/robotstudio_so101").expanduser())
	sub = parser.add_subparsers(dest="cmd", required=True)
	f = sub.add_parser("fit-camera")
	f.add_argument("dataset", type=Path)
	f.add_argument("--frames", type=int, nargs="+", default=[300, 1500, 4000, 9000, 15000, 22000, 30000])
	f.add_argument("--out", type=Path, required=True)
	s = sub.add_parser("simulate")
	s.add_argument("--camera", type=Path, required=True)
	s.add_argument("--out", type=Path, required=True)
	s.add_argument("--episodes", type=int, default=4)
	s.add_argument("--seed", type=int, default=0)
	s.add_argument("--rest", type=float, nargs=6, default=[4.1, -98.7, 99.3, -98.2, 24.1, 33.7])
	s.add_argument("--prior", type=Path, help="layout prior JSON from the layout-prior subcommand")
	s.add_argument("--workers", type=int, default=1)
	lp = sub.add_parser("layout-prior")
	lp.add_argument("dataset", type=Path)
	lp.add_argument("--camera", type=Path, required=True)
	lp.add_argument("--out", type=Path, required=True)
	r = sub.add_parser("render")
	r.add_argument("--camera", type=Path, required=True)
	r.add_argument("--sim", type=Path, required=True)
	r.add_argument("--out", type=Path, required=True)
	r.add_argument("--views", type=int, default=3)
	r.add_argument("--seed", type=int, default=1)
	r.add_argument("--stride", type=int, default=1)
	r.add_argument("--workers", type=int, default=1)
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
	if args.cmd == "fit-camera":
		fit_camera(args.dataset, args.menagerie, args.frames, args.out)
	elif args.cmd == "simulate":
		simulate(
			args.menagerie,
			args.camera,
			args.out,
			args.episodes,
			args.seed,
			np.array(args.rest),
			args.prior,
			args.workers,
		)
	elif args.cmd == "layout-prior":
		layout_prior(args.dataset, args.camera, args.out)
	else:
		render_views(args.menagerie, args.camera, args.sim, args.out, args.views, args.seed, args.stride, args.workers)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
