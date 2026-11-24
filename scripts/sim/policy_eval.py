"""Closed-loop evaluation of a trained policy in the MuJoCo sorting cell (``so101_sort_sim.py``).

Each episode draws its scene exactly like ``so101_sort_sim.simulate`` (layout, brick colour class, top camera near the
fitted one, start pose near rest) from ``default_rng([seed, e])``; use a seed the training data did not use (the
batch dataset was simulated with seed 0). Every frame renders the four dataset cameras (``top_rgb_v2`` and
``top_depth_v2`` cropped like the depth bridge, ``front``, ``wrist``), the policy returns one joint target in Studio's
normalised units, and the cell steps one 30 fps frame with the same assisted grasp the demonstrations used.

An episode ends when the brick has rested in a bowl for one second, when it leaves the table, or after
``max_frames``. Outcomes:

* ``correct``: brick in the bowl the task names (green for a normal brick, pink for a defective one),
* ``wrong_bowl``: brick in the other bowl,
* ``dropped``: the brick was grasped but did not end in a bowl,
* ``never_grasped``: the assisted grasp never engaged.

Results are simulated (``source = mujoco-sim``) and never pooled with real-arm results.
"""

from __future__ import annotations

import logging
import time
from dataclasses import asdict
from pathlib import Path
from typing import Protocol

import numpy as np
import so101_sort_sim as sim

logger = logging.getLogger(__name__)

REST_U = np.array([4.1, -98.7, 99.3, -98.2, 24.1, 33.7])
SETTLED_FRAMES = sim.FPS


class FramePolicy(Protocol):
	"""One normalised joint target per call from the four camera images, the joint state and the task text."""

	def reset(self) -> None: ...

	def act(self, images: dict[str, np.ndarray], state: np.ndarray, task: str) -> np.ndarray: ...


def episode_scene(
	menagerie: Path, nominal: sim.CameraPose, prior: list[dict] | None, seed: int, e: int
) -> tuple[sim.Cell, bool, np.ndarray, np.random.Generator]:
	"""Build episode ``e``'s cell the way ``so101_sort_sim._simulate_one`` does, plus a side camera.

	Returns
	-------
	tuple
		The cell (joints at the start pose), whether the brick is defective, the start pose in radians and the
		episode's random generator after scene sampling.
	"""
	rng = np.random.default_rng([seed, e])
	rest = sim.normalized_to_rad(REST_U)
	defective = bool(rng.random() < 0.35)
	for _ in range(500):
		layout = sim.sample_layout(rng, nominal, defective, prior)
		if sim.top_view_ok(nominal, asdict(layout), np.zeros((0, 3)), margin_px=30.0)[0]:
			break
	else:
		raise RuntimeError("no layout fits the nominal top camera; check the camera file")
	layout.defect_face = int(rng.integers(len(sim.FACES)))
	for _ in range(50):
		main = sim.sample_top_camera(rng, nominal)
		if sim.top_view_ok(main, asdict(layout), np.zeros((0, 3)), margin_px=20.0)[0]:
			break
	layout.top = main
	start = rest + np.concatenate([rng.normal(0, 0.05, 5), [0.0]])
	cell = sim.Cell(layout, menagerie)
	cell.set_joints(start)
	# The demonstrations reject side cameras whose view the arm's swept volume blocks; the policy's path is unknown
	# beforehand, so here the side camera only has to see the brick and both bowls.
	targets = np.array([[*layout.brick_xy, 0.02], [*layout.green, sim.BOWL_H], [*layout.pink, sim.BOWL_H]])
	for _ in range(500):
		side = sim.sample_side_camera(rng)
		uv, front = sim.project(side, targets, (640, 480))
		if front.all() and np.all((uv > 20) & (uv < np.array([620, 460]))):
			break
	cell.set_camera("front", side)
	return cell, defective, start, rng


def observe(cell: sim.Cell) -> dict[str, np.ndarray]:
	"""The four dataset cameras as HxWx3 uint8 arrays, keyed like the dataset features without the prefix."""
	top_rgb, top_depth = cell.top_images()
	return {
		"top_rgb_v2": top_rgb,
		"wrist": cell.rgb("wrist_cam"),
		"front": cell.rgb("front"),
		"top_depth_v2": top_depth,
	}


def bowl_of(cell: sim.Cell) -> str | None:
	"""``green`` or ``pink`` when the brick rests inside that bowl, else None."""
	brick = cell.brick_pos()
	if brick[2] >= 0.05:
		return None
	for name in ("green", "pink"):
		if np.hypot(*(brick[:2] - np.array(getattr(cell.layout, name)))) < sim.BOWL_R:
			return name
	return None


def run_episode(
	policy: FramePolicy,
	menagerie: Path,
	nominal: sim.CameraPose,
	prior: list[dict] | None,
	seed: int,
	e: int,
	max_frames: int,
) -> dict:
	"""Roll the policy out for one episode and classify the outcome."""
	cell, defective, _, _ = episode_scene(menagerie, nominal, prior, seed, e)
	target_bowl = "pink" if defective else "green"
	task = sim.TASKS[target_bowl]
	policy.reset()
	grasped, settled, frames, policy_s = False, 0, 0, 0.0
	t0 = time.perf_counter()
	for frames in range(1, max_frames + 1):  # noqa: B007  (frames is the episode length after the loop)
		images = observe(cell)
		t1 = time.perf_counter()
		action_u = np.asarray(policy.act(images, sim.rad_to_normalized(cell.joints()), task), dtype=np.float64)
		policy_s += time.perf_counter() - t1
		target = sim.normalized_to_rad(action_u)
		cell.step(target)
		cell.update_grasp(float(target[5]))
		grasped |= cell.held is not None
		if cell.brick_pos()[2] < -0.05:
			break
		settled = settled + 1 if cell.held is None and cell.settle_frames <= 0 and bowl_of(cell) else 0
		if settled >= SETTLED_FRAMES:
			break
	final = bowl_of(cell) if cell.held is None else None
	if final == target_bowl:
		outcome = "correct"
	elif final is not None:
		outcome = "wrong_bowl"
	else:
		outcome = "dropped" if grasped else "never_grasped"
	cell.renderer.close()
	return {
		"episode": e,
		"seed": seed,
		"task": task,
		"defective": defective,
		"outcome": outcome,
		"grasped": grasped,
		"final_bowl": final,
		"frames": frames,
		"seconds": round(time.perf_counter() - t0, 1),
		"policy_seconds": round(policy_s, 1),
		"final_brick": cell.brick_pos().round(4).tolist(),
	}


class SmolVlaPolicy:
	"""A Lightning SmolVLA checkpoint on one device; actions come from its 50-step chunk queue."""

	def __init__(self, checkpoint: Path, device: str = "cuda") -> None:
		import torch
		from physicalai.policies import SmolVLA

		self._torch = torch
		self.device = device
		self.policy = SmolVLA.load_from_checkpoint(str(checkpoint), map_location=device).to(device).eval()

	def reset(self) -> None:
		self.policy.reset()

	def act(self, images: dict[str, np.ndarray], state: np.ndarray, task: str) -> np.ndarray:
		from physicalai.data.observation import Observation

		torch = self._torch
		obs = Observation(
			images={
				k: torch.from_numpy(v).permute(2, 0, 1).float().div(255.0).unsqueeze(0).to(self.device)
				for k, v in images.items()
			},
			state=torch.from_numpy(np.asarray(state, np.float32)).unsqueeze(0).to(self.device),
			task=[task],
		)
		with torch.inference_mode():
			action = self.policy.select_action(obs)
		return action.float().reshape(-1)[:6].cpu().numpy()
