"""Kinematic digital twin of the sorting cell: SO-101 kinematics, one brick, two bowls, rendered cameras.

The twin implements the :class:`defect_sorter.closed_loop.Cell` protocol, so the loop, the inspector and the policy
run unchanged against it before the arm is available. It is deliberately kinematic, not a physics simulation:

* joints follow commanded targets at a bounded speed and stay inside the URDF limits;
* a brick is grasped when the gripper closes with the tool centre point (TCP) within a tolerance of the brick, and
  is carried rigidly until the gripper opens; it then lands on the table where it was released;
* the TCP going below the table raises :class:`~defect_sorter.closed_loop.ArmFaultError`, as a real collision would stop
  the attempt.

Geometry is in metres in ``base_link`` (the robot base frame), with the table top assumed at ``z = 0``. The TCP is the
URDF ``gripper_frame_joint`` origin; the jaws point along ``-z`` of ``gripper_link``. Joint state uses the dataset
contract order (:data:`STATE_NAMES`): five body joints in degrees, zero at mid-range as in Studio's calibration,
then the gripper on a 0 (closed) to 100 (open) scale. That gripper convention is the twin's own and must be checked
against a real Studio recording before twin and real data are mixed.

Cameras are orthographic views of the table drawn with OpenCV: ``top`` covers the whole cell, ``wrist`` is a
close view that follows the TCP. They exercise the data path (image keys, shapes, a visible brick and arm); they do
not reproduce the real cameras' perspective, lighting or texture, so models trained on them are pipeline checks, not
transferable policies. What is missing for transfer is listed in ``docs/infrastructure/OFFLINE_PIPELINE.md``.

:class:`ScriptedExpert` is a privileged demonstrator: it reads the brick position from the twin and moves through
inverse-kinematics waypoints. It produces demonstration episodes and is the reference policy for the loop; it is not a
learned policy.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from itertools import pairwise

import cv2
import numpy as np
from scipy.optimize import least_squares

from defect_sorter.closed_loop import DEFAULT_TASKS, ArmFaultError, CellObservation, Outcome
from defect_sorter.kinematics import SO101_JOINTS, forward, joint_frames

logger = logging.getLogger(__name__)

BODY_JOINTS: tuple[str, ...] = tuple(j.name for j in SO101_JOINTS)
STATE_NAMES: tuple[str, ...] = (*(f"{name}.pos" for name in BODY_JOINTS), "gripper.pos")
STATE_UNITS: tuple[str, ...] = ("degrees",) * len(BODY_JOINTS) + ("normalized_0_100",)

JOINT_LIMITS_DEG: dict[str, tuple[float, float]] = {
	"shoulder_pan": (-110.0, 110.0),
	"shoulder_lift": (-100.0, 100.0),
	"elbow_flex": (-96.83, 96.83),
	"wrist_flex": (-95.0, 95.0),
	"wrist_roll": (-157.21, 162.79),
}
"""URDF ``so101_follower`` revolute limits, converted from radians."""

TCP_IN_GRIPPER = np.array([-0.0079, -0.000218121, -0.0981274])
"""URDF ``gripper_frame_joint`` origin in ``gripper_link``."""

HOME_DEG: dict[str, float] = {
	"shoulder_pan": 0.0,
	"shoulder_lift": -80.0,
	"elbow_flex": 50.0,
	"wrist_flex": 90.0,
	"wrist_roll": 0.0,
}
"""Folded pose with the TCP about 9 cm above the table, short of the brick area so it does not hide the brick."""

GRIPPER_OPEN, GRIPPER_CLOSED_BELOW, GRIPPER_RELEASE_ABOVE = 100.0, 20.0, 50.0
BRICK_SIZE_M = (0.0318, 0.0158, 0.0114)
"""Lego 2x4 brick: length, width, height including studs."""

BRICK_COLOURS: tuple[tuple[int, int, int], ...] = ((200, 40, 40), (40, 80, 200), (230, 200, 40), (235, 235, 230))
MARKER_COLOURS: tuple[tuple[int, int, int], ...] = ((20, 20, 20), (20, 25, 60))
TABLE_RGB = np.array([175.0, 140.0, 100.0])
BOWL_RGB = {"green": (60, 170, 80), "pink": (230, 120, 170)}


def tcp_pose(angles_deg: dict[str, float]) -> tuple[np.ndarray, np.ndarray]:
	"""TCP position in ``base_link`` and the unit direction the jaws point along."""
	gripper = forward(angles_deg)
	return gripper[:3, :3] @ TCP_IN_GRIPPER + gripper[:3, 3], -gripper[:3, 2]


_IK_JOINTS = BODY_JOINTS[:4]


def solve_ik(
	target: np.ndarray, *, max_tilt_deg: float = 10.0, tolerance_m: float = 1e-3, wrist_roll: float = 0.0
) -> dict[str, float] | None:
	"""Joint angles (degrees) that put the TCP at ``target`` with the jaws pointing down, or None.

	Solves the four positioning joints by bounded least squares from a few seeds; ``wrist_roll`` is fixed. A solution
	is accepted when the TCP is within ``tolerance_m`` and the jaw direction within ``max_tilt_deg`` of straight
	down. Position is weighted above orientation, so near the edge of the workspace the jaws tilt before the TCP
	misses.
	"""
	lo = np.array([JOINT_LIMITS_DEG[n][0] for n in _IK_JOINTS])
	hi = np.array([JOINT_LIMITS_DEG[n][1] for n in _IK_JOINTS])
	pan = -np.degrees(np.arctan2(target[1], target[0] - SO101_JOINTS[0].xyz[0]))
	down = np.array([0.0, 0.0, -1.0])

	def angles(x: np.ndarray) -> dict[str, float]:
		return {**dict(zip(_IK_JOINTS, map(float, x), strict=True)), "wrist_roll": wrist_roll}

	def residual(x: np.ndarray) -> np.ndarray:
		position, approach = tcp_pose(angles(x))
		return np.concatenate([(position - target) * 1000.0, (approach - down) * 20.0])

	best = None
	for seed in ((pan, 0, 0, 0), (pan, -40, 40, 60), (pan, 40, -40, 60), (pan, -60, 60, 60), (pan, 20, 20, 40)):
		result = least_squares(residual, np.clip(seed, lo, hi), bounds=(lo, hi))
		if best is None or result.cost < best.cost:
			best = result
	if best is None:
		return None
	solution = angles(best.x)
	position, approach = tcp_pose(solution)
	tilt = np.degrees(np.arccos(np.clip(approach @ down, -1.0, 1.0)))
	if np.linalg.norm(position - target) > tolerance_m or tilt > max_tilt_deg:
		return None
	return solution


@dataclass(frozen=True)
class CellLayout:
	"""Bowls (centre xy, radius) and the area where the brick appears, in metres in ``base_link``."""

	bowls: dict[str, tuple[tuple[float, float], float]] = field(
		default_factory=lambda: {"green": ((0.16, 0.15), 0.055), "pink": ((0.16, -0.15), 0.055)}
	)
	spawn_x: tuple[float, float] = (0.19, 0.25)
	spawn_y: tuple[float, float] = (-0.05, 0.05)

	def __post_init__(self) -> None:
		items = list(self.bowls.items())
		for i, (name_a, (centre_a, radius_a)) in enumerate(items):
			for name_b, (centre_b, radius_b) in items[i + 1 :]:
				if np.hypot(centre_a[0] - centre_b[0], centre_a[1] - centre_b[1]) < radius_a + radius_b:
					raise ValueError(f"bowls {name_a} and {name_b} overlap")


@dataclass
class Brick:
	"""The brick's pose and look; ``z`` is the centre height."""

	xy: np.ndarray
	yaw_deg: float
	colour: tuple[int, int, int]
	defective: bool
	mark: tuple[tuple[int, int, int], np.ndarray, float] | None
	z: float = BRICK_SIZE_M[2] / 2
	held: bool = False
	grip_offset: np.ndarray = field(default_factory=lambda: np.zeros(2))


@dataclass(frozen=True)
class TopCamera:
	"""Orthographic top-down view: image column grows with ``x``, image row grows with ``-y``."""

	x_range: tuple[float, float]
	y_range: tuple[float, float]
	px_per_m: float

	@property
	def shape(self) -> tuple[int, int]:
		"""Image (rows, columns)."""
		return (
			round((self.y_range[1] - self.y_range[0]) * self.px_per_m),
			round((self.x_range[1] - self.x_range[0]) * self.px_per_m),
		)

	def to_pixel(self, x: float, y: float) -> tuple[int, int]:
		"""Pixel (column, row) of a table point."""
		return (round((x - self.x_range[0]) * self.px_per_m), round((self.y_range[1] - y) * self.px_per_m))

	@classmethod
	def centred(cls, x: float, y: float, size_m: tuple[float, float], px_per_m: float) -> TopCamera:
		"""View of ``size_m`` (along x, along y) centred on a table point."""
		return cls((x - size_m[0] / 2, x + size_m[0] / 2), (y - size_m[1] / 2, y + size_m[1] / 2), px_per_m)


TOP_CAMERA = TopCamera(x_range=(-0.02, 0.38), y_range=(-0.26, 0.26), px_per_m=600.0)
WRIST_VIEW_M, WRIST_PX_PER_M = (0.16, 0.12), 2000.0
CROP_VIEW_M, CROP_PX_PER_M = (0.032, 0.032), 4000.0


class TwinCell:
	"""Kinematic sorting cell implementing the closed-loop ``Cell`` protocol.

	Parameters
	----------
	layout : CellLayout
		Bowls and brick spawn area.
	seed : int
		Seed for the brick pose, colour, defect mark and camera noise.
	defective : bool or None
		Force the brick's ground truth; None draws it with probability one half.
	dt : float
		Control period in seconds (one ``apply`` call).
	joint_speed_deg_s, gripper_speed : float
		Speed limits for body joints (degrees per second) and the gripper (scale units per second).
	"""

	mode = "twin"

	def __init__(
		self,
		layout: CellLayout | None = None,
		seed: int = 0,
		defective: bool | None = None,
		dt: float = 1 / 30,
		joint_speed_deg_s: float = 90.0,
		gripper_speed: float = 300.0,
	) -> None:
		self.layout = layout or CellLayout()
		self.dt = dt
		self.joint_speed_deg_s = joint_speed_deg_s
		self.gripper_speed = gripper_speed
		self._rng = np.random.default_rng(seed)
		self.state = np.array([HOME_DEG[n] for n in BODY_JOINTS] + [GRIPPER_OPEN])
		self.frame_id = 0
		if defective is None:
			defective = bool(self._rng.random() < 0.5)
		xy = np.array([self._rng.uniform(*self.layout.spawn_x), self._rng.uniform(*self.layout.spawn_y)])
		mark = None
		if defective:
			colour = MARKER_COLOURS[int(self._rng.integers(len(MARKER_COLOURS)))]
			mark = (colour, self._rng.uniform(-0.004, 0.004, 2), float(self._rng.uniform(0, 90)))
		self.brick = Brick(
			xy=xy,
			yaw_deg=float(self._rng.uniform(-30, 30)),
			colour=BRICK_COLOURS[int(self._rng.integers(len(BRICK_COLOURS)))],
			defective=defective,
			mark=mark,
		)

	def angles(self) -> dict[str, float]:
		"""Current body joint angles in degrees."""
		return dict(zip(BODY_JOINTS, map(float, self.state[:5]), strict=True))

	def grasp_height(self) -> float:
		"""TCP height that centres the jaws on the brick."""
		return BRICK_SIZE_M[2] / 2

	def ground_truth(self) -> str:
		"""Independent label of the brick, known to the twin by construction."""
		return "defective" if self.brick.defective else "normal"

	def apply(self, action: np.ndarray) -> None:
		"""Move toward ``action`` (state order and units) for one control period."""
		target = np.asarray(action, dtype=float).copy()
		for i, name in enumerate(BODY_JOINTS):
			target[i] = np.clip(target[i], *JOINT_LIMITS_DEG[name])
		target[5] = np.clip(target[5], 0.0, GRIPPER_OPEN)
		limit = np.array([self.joint_speed_deg_s] * 5 + [self.gripper_speed]) * self.dt
		was_closed = self.state[5] < GRIPPER_CLOSED_BELOW
		self.state = self.state + np.clip(target - self.state, -limit, limit)
		tcp, _ = tcp_pose(self.angles())
		if tcp[2] < -0.003:
			raise ArmFaultError(f"table contact: TCP at z = {tcp[2] * 1000:.1f} mm")
		closed = self.state[5] < GRIPPER_CLOSED_BELOW
		brick = self.brick
		if closed and not was_closed and not brick.held:
			near = np.linalg.norm(tcp[:2] - brick.xy) < 0.012 and abs(tcp[2] - brick.z) < 0.012
			if near:
				brick.held = True
				brick.grip_offset = brick.xy - tcp[:2]
		elif brick.held and self.state[5] > GRIPPER_RELEASE_ABOVE:
			brick.held = False
			brick.z = BRICK_SIZE_M[2] / 2
		if brick.held:
			brick.xy = tcp[:2] + brick.grip_offset
			brick.z = tcp[2]

	def outcome(self) -> Outcome:
		"""Bowl that fully contains the brick's centre with a 1 cm margin, or None; unsettled while held."""
		if self.brick.held:
			return Outcome(bowl=None, settled=False)
		for name, (centre, radius) in self.layout.bowls.items():
			if np.linalg.norm(self.brick.xy - np.array(centre)) <= radius - 0.01:
				return Outcome(bowl=name, settled=True)
		return Outcome(bowl=None, settled=True)

	def observe(self) -> CellObservation:
		"""Render both cameras and the inspection crop (None while the brick is held)."""
		self.frame_id += 1
		tcp, _ = tcp_pose(self.angles())
		images = {
			"top": self.render(TOP_CAMERA),
			"wrist": self.render(TopCamera.centred(tcp[0], tcp[1], WRIST_VIEW_M, WRIST_PX_PER_M)),
		}
		crop = None
		if not self.brick.held:
			crop = self.render(TopCamera.centred(*self.brick.xy, CROP_VIEW_M, CROP_PX_PER_M), draw_arm=False)
		return CellObservation(self.frame_id, images, self.state.astype(np.float32), crop)

	def render(self, camera: TopCamera, *, draw_arm: bool = True) -> np.ndarray:
		"""RGB uint8 image of the cell from ``camera``, with mild sensor noise."""
		rows, cols = camera.shape
		xs = camera.x_range[0] + (np.arange(cols) + 0.5) / camera.px_per_m
		ys = camera.y_range[1] - (np.arange(rows) + 0.5) / camera.px_per_m
		grain = 12.0 * np.sin(ys[:, None] * 90.0 + 3.0 * np.sin(xs[None, :] * 25.0))
		image = np.clip(TABLE_RGB + grain[..., None], 0, 255).astype(np.uint8)
		s = camera.px_per_m
		for name, (centre, radius) in self.layout.bowls.items():
			c = camera.to_pixel(*centre)
			colour = BOWL_RGB.get(name, (150, 150, 150))
			cv2.circle(image, c, round(radius * s), colour, -1, cv2.LINE_AA)
			rim = tuple(int(v * 0.8) for v in colour)
			cv2.circle(image, c, round(radius * s), rim, max(1, round(0.004 * s)), cv2.LINE_AA)
		if not self.brick.held:
			self._draw_brick(image, camera)
		if draw_arm:
			self._draw_arm(image, camera)
		noise = self._rng.normal(0.0, 2.0, image.shape)
		return np.clip(image + noise, 0, 255).astype(np.uint8)

	def _draw_brick(self, image: np.ndarray, camera: TopCamera) -> None:
		brick, s = self.brick, camera.px_per_m
		centre = camera.to_pixel(*brick.xy)
		box = ((float(centre[0]), float(centre[1])), (BRICK_SIZE_M[0] * s, BRICK_SIZE_M[1] * s), -brick.yaw_deg)
		corners = cv2.boxPoints(box).astype(np.int32)
		cv2.fillConvexPoly(image, corners, brick.colour, cv2.LINE_AA)
		cv2.polylines(image, [corners], True, tuple(int(v * 0.6) for v in brick.colour), max(1, round(0.001 * s)))
		yaw = np.radians(brick.yaw_deg)
		along, across = np.array([np.cos(yaw), np.sin(yaw)]), np.array([-np.sin(yaw), np.cos(yaw)])
		stud = tuple(int(v * 0.8) for v in brick.colour)
		for i in (-1.5, -0.5, 0.5, 1.5):
			for j in (-0.5, 0.5):
				p = brick.xy + along * i * 0.008 + across * j * 0.008
				cv2.circle(image, camera.to_pixel(*p), max(1, round(0.0024 * s)), stud, -1, cv2.LINE_AA)
		if brick.mark is not None:
			colour, offset, angle = brick.mark
			width = max(1, round(0.002 * s))
			for theta in (angle, angle + 90.0):
				d = np.array([np.cos(np.radians(theta)), np.sin(np.radians(theta))]) * 0.006
				a, b = camera.to_pixel(*(brick.xy + offset - d)), camera.to_pixel(*(brick.xy + offset + d))
				cv2.line(image, a, b, colour, width, cv2.LINE_AA)

	def _draw_arm(self, image: np.ndarray, camera: TopCamera) -> None:
		s = camera.px_per_m
		angles = self.angles()
		points = [np.zeros(3)] + [frame[:3, 3] for frame in joint_frames(angles)]
		gripper = forward(angles)
		tcp, _ = tcp_pose(angles)
		points += [gripper[:3, 3], tcp]
		cv2.circle(image, camera.to_pixel(0.0, 0.0), round(0.035 * s), (90, 90, 95), -1, cv2.LINE_AA)
		for a, b in pairwise(points):
			shade = int(np.clip(120 + 200 * (a[2] + b[2]) / 2, 110, 200))
			cv2.line(
				image,
				camera.to_pixel(*a[:2]),
				camera.to_pixel(*b[:2]),
				(shade, shade, shade + 5),
				max(1, round(0.022 * s)),
				cv2.LINE_AA,
			)
		if self.brick.held:
			self._draw_brick(image, camera)
		opening = 0.008 + 0.03 * self.state[5] / GRIPPER_OPEN
		side = gripper[:3, 0][:2]
		side = side / (np.linalg.norm(side) + 1e-9)
		for sign in (-1.0, 1.0):
			jaw = tcp[:2] + sign * side * opening / 2
			cv2.circle(image, camera.to_pixel(*jaw), max(1, round(0.004 * s)), (80, 80, 85), -1, cv2.LINE_AA)


class ScriptedExpert:
	"""Privileged pick-and-place demonstrator for the twin.

	On ``reset`` it reads the brick position from the cell, looks up the target bowl from the task text, and plans
	joint waypoints by inverse kinematics: above the brick, down, close, lift, above the bowl, open, home. Each action
	moves the joints toward the current waypoint at ``speed_fraction`` of the twin's speed limit, so the action is the
	next commanded position, as in teleoperation recordings.

	Parameters
	----------
	cell : TwinCell
		The twin it reads the brick and bowl positions from.
	tasks : dict
		Defect label → (bowl, task text); used to find the bowl for a task.
	speed_fraction : float
		Fraction of the twin's joint speed limit used for commands.
	"""

	HOVER_M, CARRY_M, HOLD_TICKS = 0.06, 0.07, 8

	def __init__(
		self, cell: TwinCell, tasks: dict[str, tuple[str, str]] = DEFAULT_TASKS, speed_fraction: float = 0.8
	) -> None:
		self.cell = cell
		self._bowl_for_task = {task: bowl for bowl, task in tasks.values()}
		self.speed_fraction = speed_fraction
		self._waypoints: list[tuple[np.ndarray, int]] = []
		self._index = 0
		self._held_for = 0

	def _joints(self, xyz: tuple[float, float, float], gripper: float) -> np.ndarray:
		angles = solve_ik(np.array(xyz), max_tilt_deg=25.0)
		if angles is None:
			raise ValueError(f"waypoint out of reach: {xyz}")
		return np.array([angles[n] for n in BODY_JOINTS] + [gripper])

	def reset(self, task: str) -> None:
		"""Plan the waypoints for ``task``; an unknown task or unreachable brick leaves an empty plan."""
		self._index, self._held_for = 0, 0
		self._waypoints = []
		bowl = self._bowl_for_task.get(task)
		if bowl is None:
			logger.warning("expert has no bowl for task %r", task)
			return
		bx, by = self.cell.brick.xy
		gx, gy = self.cell.layout.bowls[bowl][0]
		grasp_z = self.cell.grasp_height()
		try:
			self._waypoints = [
				(self._joints((bx, by, self.HOVER_M), GRIPPER_OPEN), 0),
				(self._joints((bx, by, grasp_z), GRIPPER_OPEN), 0),
				(self._joints((bx, by, grasp_z), 0.0), self.HOLD_TICKS),
				(self._joints((bx, by, self.CARRY_M), 0.0), 0),
				(self._joints((gx, gy, self.CARRY_M), 0.0), 0),
				(self._joints((gx, gy, self.CARRY_M), GRIPPER_OPEN), self.HOLD_TICKS),
				(np.array([HOME_DEG[n] for n in BODY_JOINTS] + [GRIPPER_OPEN]), 0),
			]
		except ValueError:
			logger.warning("expert could not plan a reachable path; no motion")
			self._waypoints = []

	def done(self) -> bool:
		"""True after the last waypoint, or at once when there is no plan."""
		return self._index >= len(self._waypoints)

	def act(self, observation: CellObservation) -> np.ndarray:
		"""Next commanded joint position toward the current waypoint."""
		current = np.asarray(observation.state, dtype=float)
		target, hold = self._waypoints[self._index]
		limit = (
			np.array([self.cell.joint_speed_deg_s] * 5 + [self.cell.gripper_speed]) * self.cell.dt * self.speed_fraction
		)
		action = current + np.clip(target - current, -limit, limit)
		if np.all(np.abs(target - current) < np.r_[[0.5] * 5, 1.0]):
			self._held_for += 1
			if self._held_for > hold:
				self._index += 1
				self._held_for = 0
		return action
