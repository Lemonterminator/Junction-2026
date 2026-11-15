"""Review recorded sorting episodes and find the moments that the training recipes cut on.

Every sort-v1 episode (``docs/datasets/SORT_V1.md``) follows one protocol: rest, approach, a still hover above the
brick, grasp, carry, release in the bowl named by the task text. This module works on plain arrays (timestamps,
body joint angles, gripper value) so it is testable without Studio or the arm:

* :func:`find_hover_pause` — the still interval right before the grasp, where a hybrid grasp clip starts;
* :func:`find_grasp` — when the gripper starts closing and when it starts opening again;
* :func:`find_hold` — the frames with the gripper closed on the brick (absolute gripper band), for inspection crops;
* :func:`grasp_clip` — frame range from the hover pause to shortly after the close (the lift);
* :func:`review_episode` — problems that make an episode unusable, and warnings that only limit its use;
* :func:`load_episodes` — read a LeRobot v3 dataset as Studio writes it (needs the ``dataset`` extra).

``sorter-episodes <dataset dir>`` prints the review per episode and a summary. Studio's datasets live in a Docker
volume; copy one out first (``docker cp physical-ai-studio-xpu:/app/storage/datasets/<id> /tmp/<name>``).

Speeds are central differences over a short window, so sensor jitter does not break a still interval. The gripper
is judged relative to its value at the start of the episode, so the direction and unit of its reading do not
matter.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

GREEN_TASK = "Pick up the brick and place it in the green bowl."
PINK_TASK = "Pick up the brick and place it in the pink bowl."
TASK_BOWLS: dict[str, str] = {GREEN_TASK: "green", PINK_TASK: "pink"}
REQUIRED_CAMERAS: tuple[str, ...] = ("top", "wrist", "front")


@dataclass(frozen=True)
class EpisodeData:
	"""One episode as arrays: timestamps (s), body joints (degrees, shape (n, joints)), gripper value per frame."""

	timestamps_s: np.ndarray
	body_deg: np.ndarray
	gripper: np.ndarray
	task: str
	cameras: tuple[str, ...]


@dataclass(frozen=True)
class ReviewConfig:
	"""Thresholds for :func:`review_episode`; defaults fit teleoperation at 30 fps.

	Parameters
	----------
	still_deg_s : float
		Fastest joint speed that still counts as holding still.
	min_pause_s : float
		Shortest still interval accepted as the hover pause.
	speed_window_s : float
		Half-width of the central difference used for joint speed.
	gripper_change : float
		Change of the gripper reading from its start value that counts as closed.
	gripper_tol : float
		Change that marks the start of a gripper motion.
	lift_s : float
		How long after the close a grasp clip continues (the lift).
	min_length_s, max_length_s : float
		Accepted episode length.
	"""

	still_deg_s: float = 3.0
	min_pause_s: float = 0.6
	speed_window_s: float = 0.17
	gripper_change: float = 10.0
	gripper_tol: float = 2.0
	lift_s: float = 1.5
	min_length_s: float = 5.0
	max_length_s: float = 60.0


@dataclass(frozen=True)
class EpisodeReport:
	"""Outcome of :func:`review_episode`; ``ok`` is False when any problem was found."""

	ok: bool
	length_s: float
	bowl: str | None
	hover: tuple[int, int] | None
	grasp: tuple[int, int | None] | None
	problems: list[str] = field(default_factory=list)
	warnings: list[str] = field(default_factory=list)


def _joint_speed(ep: EpisodeData, cfg: ReviewConfig) -> np.ndarray:
	t = ep.timestamps_s
	n = len(t)
	dt = float(np.median(np.diff(t))) if n > 1 else 1.0
	w = max(1, round(cfg.speed_window_s / dt))
	lo = np.clip(np.arange(n) - w, 0, n - 1)
	hi = np.clip(np.arange(n) + w, 0, n - 1)
	span = np.maximum(t[hi] - t[lo], dt)
	return np.max(np.abs(ep.body_deg[hi] - ep.body_deg[lo]), axis=1) / span


def _still_runs(still: np.ndarray) -> list[tuple[int, int]]:
	runs, start = [], None
	for i, s in enumerate(still):
		if s and start is None:
			start = i
		elif not s and start is not None:
			runs.append((start, i - 1))
			start = None
	if start is not None:
		runs.append((start, len(still) - 1))
	return runs


def find_grasp(ep: EpisodeData, cfg: ReviewConfig) -> tuple[int, int | None] | None:
	"""Frame where the gripper starts closing and where it starts opening again (None if it never reopens)."""
	g = np.asarray(ep.gripper, dtype=float)
	ref = float(np.median(g[: max(1, int(0.5 / max(np.median(np.diff(ep.timestamps_s)), 1e-6)))]))
	dev = np.abs(g - ref)
	over = np.flatnonzero(dev > cfg.gripper_change)
	if len(over) == 0:
		return None
	close = int(over[0])
	while close > 0 and dev[close - 1] > cfg.gripper_tol:
		close -= 1
	peak = dev[close]
	for i in range(close, len(g)):
		peak = max(peak, dev[i])
		if i > over[0] and dev[i] < peak - cfg.gripper_tol:
			return close, i
	return close, None


def find_hover_pause(ep: EpisodeData, cfg: ReviewConfig) -> tuple[int, int] | None:
	"""The still interval after the arm first moved and before the grasp; None when there is none."""
	speed = _joint_speed(ep, cfg)
	moving = np.flatnonzero(speed > 2 * cfg.still_deg_s)
	if len(moving) == 0:
		return None
	grasp = find_grasp(ep, cfg)
	limit = grasp[0] if grasp else len(speed)
	t = ep.timestamps_s
	runs = [
		(a, b)
		for a, b in _still_runs(speed < cfg.still_deg_s)
		if a > moving[0] and b < limit and t[b] - t[a] >= cfg.min_pause_s
	]
	return runs[-1] if runs else None


def find_hold(ep: EpisodeData, band: tuple[float, float], min_s: float = 0.5) -> tuple[int, int] | None:
	"""Longest run of frames with the gripper reading inside ``band`` (inclusive), as (first, last) frame.

	A gripper closed on a brick stops short of closing fully, so its reading rests in a band that an empty
	close or an open gripper does not reach. Unlike :func:`find_grasp` this needs the band of the actual
	follower and brick; it returns None when no run lasts ``min_s``.
	"""
	g = np.asarray(ep.gripper, dtype=float)
	runs = _still_runs((g >= band[0]) & (g <= band[1]))
	if not runs:
		return None
	start, end = max(runs, key=lambda r: r[1] - r[0])
	if ep.timestamps_s[end] - ep.timestamps_s[start] < min_s:
		return None
	return start, end


def grasp_clip(ep: EpisodeData, cfg: ReviewConfig) -> tuple[int, int] | None:
	"""Frames from the hover pause start to ``lift_s`` after the gripper starts closing (inclusive)."""
	pause, grasp = find_hover_pause(ep, cfg), find_grasp(ep, cfg)
	if pause is None or grasp is None:
		return None
	close, release = grasp
	t = ep.timestamps_s
	end = int(np.searchsorted(t, t[close] + cfg.lift_s, side="right") - 1)
	if release is not None:
		end = min(end, release)
	return pause[0], min(end, len(t) - 1)


def review_episode(ep: EpisodeData, cfg: ReviewConfig) -> EpisodeReport:
	"""Check one episode against the sort-v1 protocol."""
	problems: list[str] = []
	warnings: list[str] = []
	length = float(ep.timestamps_s[-1] - ep.timestamps_s[0]) if len(ep.timestamps_s) else 0.0
	if length < cfg.min_length_s:
		problems.append(f"too short ({length:.1f} s)")
	if length > cfg.max_length_s:
		problems.append(f"too long ({length:.1f} s)")
	bowl = TASK_BOWLS.get(ep.task.strip())
	if bowl is None:
		problems.append(f"unknown task text: {ep.task!r}")
	for cam in REQUIRED_CAMERAS:
		if cam not in ep.cameras:
			problems.append(f"missing camera stream: {cam}")
	grasp = find_grasp(ep, cfg)
	if grasp is None:
		problems.append("gripper never closed")
	elif grasp[1] is None:
		problems.append("gripper never reopened (no release)")
	hover = find_hover_pause(ep, cfg)
	if hover is None:
		warnings.append("no hover pause found: usable for whole-task policies, not for grasp clips")
	return EpisodeReport(not problems, length, bowl, hover, grasp, problems, warnings)


def load_episodes(root: Path) -> list[EpisodeData]:
	"""Episodes of a LeRobot v3 dataset: joint state, gripper, timestamps, task text and camera streams."""
	import pyarrow.parquet as pq

	info = json.loads((root / "meta" / "info.json").read_text())
	features = info["features"]
	names = features["observation.state"]["names"]
	gripper_col = names.index("gripper.pos")
	body_cols = [i for i in range(len(names)) if i != gripper_col]
	cameras = tuple(k.removeprefix("observation.images.") for k, v in features.items() if v.get("dtype") == "video")
	tasks_table = pq.read_table(root / "meta" / "tasks.parquet").to_pydict()
	task_names = {int(i): t for t, i in zip(tasks_table["task"], tasks_table["task_index"], strict=True)}

	states, stamps, ep_ids, task_ids = [], [], [], []
	for path in sorted((root / "data").glob("*/*.parquet")):
		cols = pq.read_table(
			path, columns=["observation.state", "timestamp", "episode_index", "task_index"]
		).to_pydict()
		states += cols["observation.state"]
		stamps += cols["timestamp"]
		ep_ids += cols["episode_index"]
		task_ids += cols["task_index"]
	state = np.asarray(states, dtype=np.float64)
	stamp = np.asarray(stamps, dtype=np.float64)
	ep = np.asarray(ep_ids)
	episodes = []
	for e in sorted(set(ep.tolist())):
		rows = np.flatnonzero(ep == e)
		rows = rows[np.argsort(stamp[rows], kind="stable")]
		episodes.append(
			EpisodeData(
				timestamps_s=stamp[rows],
				body_deg=state[rows][:, body_cols],
				gripper=state[rows][:, gripper_col],
				task=task_names[int(task_ids[rows[0]])],
				cameras=cameras,
			)
		)
	return episodes


def main(argv: list[str] | None = None) -> None:
	"""``sorter-episodes``: review every episode of a recorded dataset against the sort-v1 protocol."""
	parser = argparse.ArgumentParser(description="Review recorded sorting episodes (LeRobot v3 dataset folder)")
	parser.add_argument("dataset", type=Path, help="dataset folder copied out of Studio's storage")
	args = parser.parse_args(argv)
	cfg = ReviewConfig()
	out = sys.stdout
	episodes = load_episodes(args.dataset)
	counts = {"green": 0, "pink": 0}
	ok = clips = 0
	for i, ep in enumerate(episodes):
		r = review_episode(ep, cfg)
		clip = grasp_clip(ep, cfg)
		ok += r.ok
		clips += clip is not None and r.ok
		if r.ok and r.bowl:
			counts[r.bowl] += 1
		status = "ok " if r.ok else "BAD"
		hover = f"hover {ep.timestamps_s[r.hover[0]]:.1f}s" if r.hover else "no hover"
		out.write(
			f"{i:3d} {status} {r.length_s:5.1f}s {r.bowl or '?':5s} {hover:12s} {'; '.join(r.problems + r.warnings)}\n"
		)
	out.write(
		f"\n{len(episodes)} episodes: {ok} usable (green {counts['green']}, pink {counts['pink']}), "
		f"{clips} with a grasp clip\n"
	)


if __name__ == "__main__":
	main()
