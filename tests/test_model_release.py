import hashlib
import json

import pytest

from defect_sorter.model_release import anomaly_manifest, release_manifest, verify_download


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


def _anomaly_setup(tmp_path):
	base = tmp_path / "real-baseline-v2"
	fold_export = base / "fold0" / "padim" / "export" / "weights" / "openvino"
	fold_export.mkdir(parents=True)
	(fold_export / "model.xml").write_text("<net/>", encoding="utf-8")
	(fold_export / "model.bin").write_bytes(b"\x07\x08")
	confusion = {"normal->normal": 11, "normal->defective": 12, "defective->defective": 9, "defective->normal": 3}
	summary = {
		"dataset": "data/studio/af9b173a",
		"camera": "wrist",
		"frames": 612,
		"episodes": 35,
		"padim_score/median": {
			"episode_confusion": confusion,
			"thresholds": [0.45],
			"frame_auroc_test_per_fold": [0.74],
		},
		"latency_padim_includes_resize": {"CPU": {"median_ms": 4.0, "p90_ms": 4.4, "runs": 200}},
	}
	folds = [
		{
			"fold": 0,
			"val_fold": 1,
			"train_frames": 200,
			"padim_score/median": {"threshold": 0.45, "frame_auroc_test": 0.74},
		}
	]
	(base / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
	(base / "folds.json").write_text(json.dumps(folds), encoding="utf-8")
	release = tmp_path / "release"
	release.mkdir()
	for name in ("model.xml", "model.bin"):
		(release / name).write_bytes((fold_export / name).read_bytes())
	return release, base


def test_anomaly_manifest_records_cpu_threshold_results_and_files(tmp_path):
	release, base = _anomaly_setup(tmp_path)
	manifest = anomaly_manifest(release, base, 0, status="baseline", commit="abc")
	assert manifest["status"] == "baseline"
	assert manifest["source"] == "real"
	assert manifest["code_commit"] == "abc"
	inspection = manifest["inspection"]
	assert inspection["model"] == "padim"
	assert inspection["thresholds"] == {"CPU": pytest.approx(0.45)}
	assert inspection["aggregate"] == "median"
	assert inspection["fold"] == 0
	assert inspection["train_frames"] == 200
	assert inspection["results"]["defects_caught"] == 9
	assert inspection["results"]["defects_total"] == 12
	assert inspection["results"]["normals_passed"] == 11
	assert inspection["results"]["normals_total"] == 23
	assert inspection["latency_ms"]["CPU"]["median_ms"] == pytest.approx(4.0)
	files = {f["name"]: f for f in manifest["files"]}
	assert set(files) == {"model.xml", "model.bin"}
	assert files["model.bin"]["sha256"] == hashlib.sha256(b"\x07\x08").hexdigest()
	assert verify_download(release, manifest) == []


def test_anomaly_manifest_rejects_a_release_whose_model_differs_from_the_fold_export(tmp_path):
	release, base = _anomaly_setup(tmp_path)
	(release / "model.bin").write_bytes(b"other")
	with pytest.raises(ValueError, match=r"model\.bin"):
		anomaly_manifest(release, base, 0, status="baseline", commit="abc")
