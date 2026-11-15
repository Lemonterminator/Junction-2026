import json

import cv2
import numpy as np
import pytest

from defect_sorter.closed_loop import DEFAULT_TASKS
from defect_sorter.lerobot_export import lerobot_features
from defect_sorter.offline_pipeline import evaluate, oracle_inspector, record_episodes, summarise, write_crops
from defect_sorter.twin import STATE_NAMES, STATE_UNITS


def test_record_episodes_writes_aligned_frames_and_an_index(tmp_path):
	index = record_episodes(tmp_path, episodes=2, seed=0)
	on_disk = json.loads((tmp_path / "index.json").read_text(encoding="utf-8"))
	assert on_disk == index
	assert index["source"] == "twin"
	assert index["fps"] == 30
	assert index["state_names"] == list(STATE_NAMES)
	assert index["state_units"] == list(STATE_UNITS)
	assert set(index["cameras"]) == {"top", "wrist"}
	assert len(index["episodes"]) == 2
	for entry in index["episodes"]:
		assert entry["success"] is True
		assert entry["task"] == DEFAULT_TASKS[entry["label"]][1]
		data = np.load(tmp_path / entry["file"])
		length = entry["length"]
		assert data["state"].shape == (length, 6)
		assert data["action"].shape == (length, 6)
		for camera, shape in index["cameras"].items():
			assert data[camera].shape == (length, *shape)
			assert data[camera].dtype == np.uint8
		# The action is the next commanded position, so it leads the state that follows it.
		np.testing.assert_allclose(data["state"][1:, :5], data["action"][:-1, :5], atol=1e-3)


def test_write_crops_builds_an_anomalib_folder_dataset(tmp_path):
	counts = write_crops(tmp_path, n_train=3, n_test=2, seed=0)
	assert counts == {"train/good": 3, "test/good": 2, "test/defect": 2}
	for folder, count in counts.items():
		files = sorted((tmp_path / folder).glob("*.png"))
		assert len(files) == count
		image = cv2.imread(str(files[0]))
		assert image is not None
		assert image.shape[2] == 3


def test_evaluate_with_oracle_sorts_every_brick_correctly():
	records = evaluate(episodes=2, seed=100, inspector_factory=oracle_inspector)
	assert [r.status for r in records] == ["DONE", "DONE"]
	assert all(r.correct_sort for r in records)
	assert all(r.decision.model == "twin-ground-truth" for r in records)


def test_summarise_counts_statuses_and_confusion():
	records = evaluate(episodes=2, seed=100, inspector_factory=oracle_inspector)
	summary = summarise(records)
	assert summary["attempts"] == 2
	assert summary["status"] == {"DONE": 2}
	assert summary["correct_sort_rate"] == 1.0
	assert sum(summary["confusion"].values()) == 2
	assert summary["modes"] == ["twin"]


def test_summarise_refuses_to_pool_modes():
	records = evaluate(episodes=1, seed=100, inspector_factory=oracle_inspector)
	records[0].mode = "real"
	records += evaluate(episodes=1, seed=101, inspector_factory=oracle_inspector)
	with pytest.raises(ValueError, match="mode"):
		summarise(records)


def test_lerobot_features_follow_the_recording_index():
	index = {
		"state_names": list(STATE_NAMES),
		"cameras": {"top": [312, 240, 3], "wrist": [240, 320, 3]},
	}
	features = lerobot_features(index)
	assert features["observation.state"] == {"dtype": "float32", "shape": (6,), "names": list(STATE_NAMES)}
	assert features["action"] == features["observation.state"]
	assert features["observation.images.top"] == {
		"dtype": "image",
		"shape": (312, 240, 3),
		"names": ["height", "width", "channels"],
	}
	assert set(features) == {"observation.state", "action", "observation.images.top", "observation.images.wrist"}


def test_lerobot_features_can_store_cameras_as_video_like_studio_recordings():
	index = {"state_names": list(STATE_NAMES), "cameras": {"top_depth_v2": [416, 512, 3]}}
	features = lerobot_features(index, video=True)
	assert features["observation.images.top_depth_v2"]["dtype"] == "video"
	assert features["observation.images.top_depth_v2"]["shape"] == (416, 512, 3)
	assert features["observation.state"]["dtype"] == "float32"
