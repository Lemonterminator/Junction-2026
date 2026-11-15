from pathlib import Path

import pytest

from defect_sorter.modal_training import (
	VOLUME_NAME,
	VolumeLayout,
	cost_ceiling,
	volume_dataset,
	warm_start_upload_command,
)
from defect_sorter.training import DatasetSpec

DATASET = DatasetSpec(
	root=str(Path("C:/data/studio/af9b")),
	repo_id="local/sort-depth-v2",
	fps=30,
	camera_keys=["observation.images.top_rgb_v2", "observation.images.wrist"],
	joint_names=["shoulder_pan.pos", "gripper.pos"],
	joint_units=["normalized_-100_100", "normalized_0_100"],
)


def test_volume_dataset_moves_only_the_root_onto_the_mount():
	moved = volume_dataset(DATASET, VolumeLayout("sort-depth-v2", "smolvla-01"))
	assert moved.root == "/vol/datasets/sort-depth-v2"
	assert (moved.repo_id, moved.fps, moved.camera_keys, moved.joint_names, moved.joint_units) == (
		DATASET.repo_id,
		DATASET.fps,
		DATASET.camera_keys,
		DATASET.joint_names,
		DATASET.joint_units,
	)


def test_layout_paths_and_cli_commands_agree():
	layout = VolumeLayout("sort-depth-v2", "smolvla-01")
	assert layout.container_runs == "/vol/runs"
	assert layout.upload_command("data/studio/af9b") == [
		"modal",
		"volume",
		"put",
		VOLUME_NAME,
		"data/studio/af9b",
		"/datasets/sort-depth-v2",
	]
	assert layout.download_command() == [
		"modal",
		"volume",
		"get",
		VOLUME_NAME,
		"/runs/smolvla-01",
		"artifacts/training",
	]


@pytest.mark.parametrize("name", ["", "../x", "a/b", "a..b", "-x", "a b"])
def test_layout_rejects_names_that_escape_their_directory(name):
	with pytest.raises(ValueError, match="dataset name"):
		VolumeLayout(name, "run")
	with pytest.raises(ValueError, match="run name"):
		VolumeLayout("data", name)


def test_cost_ceiling_is_rate_times_timeout():
	# L40S at $1.95/h with a 4 h timeout: 1.95 * 4 = 7.80.
	assert cost_ceiling(1.95, 4) == pytest.approx(7.8)


@pytest.mark.parametrize(("rate", "hours"), [(0, 1), (1, 0), (-1, 1), (float("nan"), 1), (1, float("inf")), (True, 1)])
def test_cost_ceiling_rejects_unbounded_or_invalid_input(rate, hours):
	with pytest.raises(ValueError, match="finite and positive"):
		cost_ceiling(rate, hours)


def test_warm_start_policies_live_beside_datasets_in_the_volume():
	layout = VolumeLayout("sim-batch-v1", "smolvla-sim-v1-01")
	assert layout.container_warm_start == "/vol/warm-start"
	assert warm_start_upload_command("artifacts/warm-start/sort-depth-v2-10k", "sort-depth-v2-10k") == [
		"modal",
		"volume",
		"put",
		VOLUME_NAME,
		"artifacts/warm-start/sort-depth-v2-10k",
		"/warm-start/sort-depth-v2-10k",
	]
	with pytest.raises(ValueError, match="warm start"):
		warm_start_upload_command("x", "../x")
