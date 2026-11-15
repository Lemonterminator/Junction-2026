import numpy as np
import pytest

from defect_sorter.episodes import (
	GREEN_TASK,
	PINK_TASK,
	EpisodeData,
	ReviewConfig,
	find_grasp,
	find_hold,
	find_hover_pause,
	grasp_clip,
	review_episode,
)

FPS = 30.0
JOINTS = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll")


def synthetic_episode(*, pause: bool = True, grasp: bool = True, length_s: float = 10.0, noise: float = 0.05):
	"""Rest → approach (0-2 s) → hover still (2-3.2 s) → descend (3.2-4 s) → close at 4.2 s → carry → open at 8 s."""
	t = np.arange(0, length_s, 1 / FPS)
	rng = np.random.default_rng(3)
	body = np.zeros((len(t), len(JOINTS)))

	def ramp(a, b):
		return np.clip((t - a) / (b - a), 0, 1)

	hover_end = 3.2 if pause else 2.0
	body[:, 1] = 30 * ramp(0, 2) - 10 * ramp(hover_end, hover_end + 0.8) + 15 * ramp(4.5, 6.0)
	body[:, 2] = -20 * ramp(0, 2) + 12 * ramp(hover_end, hover_end + 0.8) - 25 * ramp(4.5, 6.0) + 33 * ramp(8.5, 10)
	body[:, 0] = 40 * ramp(4.5, 7.5) - 40 * ramp(8.5, 10)
	body += rng.normal(0, noise, body.shape)
	gripper = np.full(len(t), 30.0)
	if grasp:
		gripper -= 25 * ramp(4.2, 4.5)
		gripper += 25 * ramp(8.0, 8.3)
	return EpisodeData(
		timestamps_s=t,
		body_deg=body,
		gripper=gripper,
		task=GREEN_TASK,
		cameras=("top", "wrist", "front"),
	)


class TestHoverPause:
	def test_finds_the_still_hover_before_the_grasp(self):
		ep = synthetic_episode()
		pause = find_hover_pause(ep, ReviewConfig())
		assert pause is not None
		start, end = pause
		assert ep.timestamps_s[start] == pytest.approx(2.0, abs=0.15)
		assert ep.timestamps_s[end] == pytest.approx(3.2, abs=0.15)

	def test_no_pause_returns_none(self):
		assert find_hover_pause(synthetic_episode(pause=False), ReviewConfig()) is None

	def test_the_still_start_at_rest_is_not_a_hover(self):
		ep = synthetic_episode()
		start, _ = find_hover_pause(ep, ReviewConfig())
		assert ep.timestamps_s[start] > 1.0


class TestGrasp:
	def test_close_and_release_times(self):
		ep = synthetic_episode()
		close, release = find_grasp(ep, ReviewConfig())
		assert ep.timestamps_s[close] == pytest.approx(4.2, abs=0.15)
		assert ep.timestamps_s[release] == pytest.approx(8.0, abs=0.2)

	def test_gripper_that_never_closes(self):
		assert find_grasp(synthetic_episode(grasp=False), ReviewConfig()) is None


def test_grasp_clip_runs_from_hover_start_to_after_the_close():
	ep = synthetic_episode()
	clip = grasp_clip(ep, ReviewConfig(lift_s=1.5))
	assert clip is not None
	a, b = clip
	assert ep.timestamps_s[a] == pytest.approx(2.0, abs=0.15)
	assert ep.timestamps_s[b] == pytest.approx(4.2 + 1.5, abs=0.15)
	assert grasp_clip(synthetic_episode(pause=False), ReviewConfig()) is None


def held_brick_episode(hold_value: float = 17.0) -> EpisodeData:
	"""Gripper as recorded on the follower: closed empty (3), opened (45), closed on a brick (hold_value) 4-9 s, opened (70)."""
	t = np.arange(0, 10, 1 / FPS)
	gripper = np.select([t < 2, t < 4, t < 9], [3.0, 45.0, hold_value], 70.0)
	return EpisodeData(
		timestamps_s=t,
		body_deg=np.zeros((len(t), len(JOINTS))),
		gripper=gripper,
		task=PINK_TASK,
		cameras=("top", "wrist", "front"),
	)


class TestHold:
	def test_hold_is_the_interval_with_the_gripper_closed_on_the_brick(self):
		ep = held_brick_episode()
		start, end = find_hold(ep, band=(12.0, 24.0))
		assert ep.timestamps_s[start] == pytest.approx(4.0, abs=1 / FPS)
		assert ep.timestamps_s[end] == pytest.approx(9.0 - 1 / FPS, abs=1 / FPS)

	def test_short_passes_through_the_band_do_not_count(self):
		ep = held_brick_episode()
		g = ep.gripper.copy()
		g[(ep.timestamps_s >= 1.0) & (ep.timestamps_s < 1.2)] = 18.0
		ep = EpisodeData(ep.timestamps_s, ep.body_deg, g, ep.task, ep.cameras)
		start, _ = find_hold(ep, band=(12.0, 24.0))
		assert ep.timestamps_s[start] == pytest.approx(4.0, abs=1 / FPS)

	def test_no_hold_when_the_gripper_never_rests_in_the_band(self):
		assert find_hold(held_brick_episode(hold_value=40.0), band=(12.0, 24.0)) is None

	def test_hold_shorter_than_the_minimum_is_rejected(self):
		assert find_hold(held_brick_episode(), band=(12.0, 24.0), min_s=6.0) is None


class TestReview:
	def test_clean_episode_passes(self):
		report = review_episode(synthetic_episode(), ReviewConfig())
		assert report.ok, report.problems
		assert report.bowl == "green"
		assert report.warnings == []

	def test_missing_pause_is_a_warning_not_a_failure(self):
		report = review_episode(synthetic_episode(pause=False), ReviewConfig())
		assert report.ok
		assert any("hover pause" in w for w in report.warnings)

	def test_problems_are_listed(self):
		ep = synthetic_episode(grasp=False)
		bad = EpisodeData(ep.timestamps_s, ep.body_deg, ep.gripper, task="put it somewhere", cameras=("top", "front"))
		report = review_episode(bad, ReviewConfig())
		assert not report.ok
		joined = " | ".join(report.problems)
		assert "task text" in joined
		assert "wrist" in joined
		assert "gripper" in joined

	def test_too_short(self):
		report = review_episode(synthetic_episode(length_s=4.0), ReviewConfig())
		assert any("short" in p for p in report.problems)

	def test_pink_task_maps_to_the_pink_bowl(self):
		ep = synthetic_episode()
		pink = EpisodeData(ep.timestamps_s, ep.body_deg, ep.gripper, task=PINK_TASK, cameras=ep.cameras)
		assert review_episode(pink, ReviewConfig()).bowl == "pink"


def _write_lerobot(root, episodes):
	"""Minimal LeRobot v3 layout: info.json, tasks.parquet, one data parquet."""
	import json

	pa = pytest.importorskip("pyarrow")
	pq = pytest.importorskip("pyarrow.parquet")
	(root / "meta").mkdir(parents=True)
	(root / "data" / "chunk-000").mkdir(parents=True)
	names = [f"{j}.pos" for j in (*JOINTS, "gripper")]
	features = {"observation.state": {"dtype": "float32", "names": names, "shape": [6]}}
	for cam in ("top", "wrist", "front"):
		features[f"observation.images.{cam}"] = {"dtype": "video"}
	(root / "meta" / "info.json").write_text(json.dumps({"codebase_version": "v3.0", "fps": 30, "features": features}))
	tasks = sorted({ep.task for ep in episodes})
	pq.write_table(pa.table({"task": tasks, "task_index": list(range(len(tasks)))}), root / "meta" / "tasks.parquet")
	cols = {"observation.state": [], "timestamp": [], "episode_index": [], "task_index": []}
	for i, ep in enumerate(episodes):
		for k in range(len(ep.timestamps_s)):
			cols["observation.state"].append([*ep.body_deg[k].tolist(), float(ep.gripper[k])])
			cols["timestamp"].append(float(ep.timestamps_s[k]))
			cols["episode_index"].append(i)
			cols["task_index"].append(tasks.index(ep.task))
	pq.write_table(pa.table(cols), root / "data" / "chunk-000" / "file-000.parquet")


def test_load_episodes_from_a_lerobot_v3_dataset(tmp_path):
	from defect_sorter.episodes import load_episodes

	a = synthetic_episode()
	b = synthetic_episode(pause=False)
	b = EpisodeData(b.timestamps_s, b.body_deg, b.gripper, task=PINK_TASK, cameras=b.cameras)
	_write_lerobot(tmp_path, [a, b])

	loaded = load_episodes(tmp_path)

	assert [e.task for e in loaded] == [GREEN_TASK, PINK_TASK]
	assert set(loaded[0].cameras) == {"top", "wrist", "front"}
	np.testing.assert_allclose(loaded[0].body_deg, a.body_deg, atol=1e-4)
	np.testing.assert_allclose(loaded[1].gripper, b.gripper, atol=1e-4)
	assert review_episode(loaded[0], ReviewConfig()).ok
