import hashlib
import json

import pytest

from defect_sorter.model_release import release_manifest, verify_download


def _setup(tmp_path):
	export = tmp_path / "export"
	export.mkdir()
	(export / "smolvla.xml").write_text("<net/>", encoding="utf-8")
	(export / "smolvla.bin").write_bytes(b"\x00\x01")
	(export / "manifest.json").write_text("{}", encoding="utf-8")
	run = tmp_path / "run"
	(run / "metrics" / "version_0").mkdir(parents=True)
	plan = {
		"recipe": "smolvla-studio-smoke",
		"dataset": {
			"repo_id": "local/studio-sorting",
			"root": "/x",
			"fps": 30,
			"camera_keys": ["observation.images.top"],
		},
		"episodes": {"validation": [0], "training": [1]},
		"config": {
			"model": {"class_path": "physicalai.policies.SmolVLA", "init_args": {}},
			"trainer": {"max_steps": 50, "precision": "bf16-mixed", "accumulate_grad_batches": 2},
			"data": {"init_args": {"train_batch_size": 4}},
		},
	}
	(run / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
	(run / "metrics" / "version_0" / "metrics.csv").write_text(
		"step,train/loss,val/loss\n0,0.9,\n49,0.2,\n39,,0.8\n", encoding="utf-8"
	)
	return export, run


def test_release_manifest_hashes_every_file_and_records_training(tmp_path):
	export, run = _setup(tmp_path)
	manifest = release_manifest(export, run, status="smoke-test", commit="abc123")
	files = {f["name"]: f for f in manifest["files"]}
	assert set(files) == {"smolvla.xml", "smolvla.bin", "manifest.json"}
	assert files["smolvla.bin"]["sha256"] == hashlib.sha256(b"\x00\x01").hexdigest()
	assert files["smolvla.bin"]["bytes"] == 2
	assert manifest["status"] == "smoke-test"
	assert manifest["source"] == "real"
	assert manifest["code_commit"] == "abc123"
	assert manifest["training"]["recipe"] == "smolvla-studio-smoke"
	assert manifest["training"]["train_episodes"] == 1
	assert manifest["training"]["final_train_loss"] == pytest.approx(0.2)
	assert manifest["training"]["final_val_loss"] == pytest.approx(0.8)


def test_release_manifest_rejects_unknown_status(tmp_path):
	export, run = _setup(tmp_path)
	with pytest.raises(ValueError, match="status"):
		release_manifest(export, run, status="great", commit="abc")


def test_verify_download_reports_missing_and_corrupt_files(tmp_path):
	export, run = _setup(tmp_path)
	manifest = release_manifest(export, run, status="smoke-test", commit="abc")
	assert verify_download(export, manifest) == []
	(export / "smolvla.bin").write_bytes(b"\x00")
	(export / "smolvla.xml").unlink()
	assert sorted(verify_download(export, manifest)) == ["smolvla.bin: sha256 mismatch", "smolvla.xml: missing"]
