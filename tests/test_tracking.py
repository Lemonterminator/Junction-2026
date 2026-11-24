import json

import pytest

from defect_sorter.tracking import anomaly_record, evaluation_record, parse_params, training_record


def _run_dir(tmp_path, metrics_csv: str):
	run = tmp_path / "run1"
	(run / "metrics" / "version_0").mkdir(parents=True)
	(run / "checkpoints").mkdir()
	(run / "checkpoints" / "last.ckpt").write_bytes(b"x")
	plan = {
		"recipe": "smolvla-smoke",
		"experimental": False,
		"dataset": {"root": "/data/rec", "repo_id": "local/rec", "fps": 30, "camera_keys": ["observation.images.top"]},
		"episodes": {"validation": [0], "training": [1, 2]},
		"config": {
			"model": {"class_path": "physicalai.policies.SmolVLA", "init_args": {"optimizer_lr": 0.0001}},
			"trainer": {"max_steps": 50, "precision": "bf16-mixed", "accumulate_grad_batches": 2},
			"data": {"init_args": {"train_batch_size": 4}},
		},
	}
	(run / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
	(run / "metrics" / "version_0" / "metrics.csv").write_text(metrics_csv, encoding="utf-8")
	return run


def test_training_record_reads_params_metrics_and_checkpoints(tmp_path):
	run = _run_dir(
		tmp_path,
		"epoch,lr-AdamW,step,train/loss,val/loss\n,0.0001,0,,\n0,,0,0.9,\n0,,1,0.7,\n0,,1,,0.8\n",
	)
	record = training_record(run)
	assert record.name == "run1"
	assert record.params["recipe"] == "smolvla-smoke"
	assert record.params["policy"] == "physicalai.policies.SmolVLA"
	assert record.params["max_steps"] == 50
	assert record.params["batch_size"] == 4
	assert record.params["dataset_repo_id"] == "local/rec"
	assert record.params["train_episodes"] == 2
	assert record.params["val_episodes"] == 1
	assert record.metrics["train/loss"] == [(0, 0.9), (1, 0.7)]
	assert record.metrics["val/loss"] == [(1, 0.8)]
	assert record.metrics["lr-AdamW"] == [(0, 0.0001)]
	assert [p.name for p in record.artifacts] == ["last.ckpt"]
	assert record.tags["source"] == "real"


def test_training_record_tags_twin_data(tmp_path):
	run = _run_dir(tmp_path, "step,train/loss\n0,1.0\n")
	plan = json.loads((run / "plan.json").read_text(encoding="utf-8"))
	plan["dataset"]["repo_id"] = "local/twin-sorting"
	(run / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
	assert training_record(run).tags["source"] == "twin"


def test_training_record_tags_simulated_data_and_keeps_its_warm_start(tmp_path):
	run = _run_dir(tmp_path, "step,train/loss\n0,1.0\n")
	plan = json.loads((run / "plan.json").read_text(encoding="utf-8"))
	plan["dataset"]["repo_id"] = "local/sim-batch-v1"
	plan["warm_start"] = "sort-depth-v2-10k"
	plan["devices"] = 8
	(run / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
	record = training_record(run)
	assert record.tags["source"] == "sim"
	assert record.params["warm_start"] == "sort-depth-v2-10k"
	assert record.params["devices"] == 8


def test_training_record_without_plan_is_rejected(tmp_path):
	with pytest.raises(FileNotFoundError):
		training_record(tmp_path)


def test_evaluation_record_flattens_summary(tmp_path):
	(tmp_path / "summary.json").write_text(
		json.dumps(
			{
				"modes": ["twin"],
				"attempts": 20,
				"status": {"DONE": 19, "FAILED": 1},
				"correct_sort_rate": 0.95,
				"mean_inspect_ms": 18.9,
				"inspector": ["openvino@CPU"],
				"confusion": {"normal->normal": 10},
			}
		),
		encoding="utf-8",
	)
	(tmp_path / "episodes.jsonl").write_text("{}\n", encoding="utf-8")
	record = evaluation_record(tmp_path)
	assert record.tags == {"source": "twin", "kind": "evaluation"}
	assert record.params["inspector"] == "openvino@CPU"
	assert record.metrics["correct_sort_rate"] == [(0, 0.95)]
	assert record.metrics["status_DONE"] == [(0, 19.0)]
	assert record.metrics["mean_inspect_ms"] == [(0, 18.9)]
	assert {p.name for p in record.artifacts} == {"summary.json", "episodes.jsonl"}


def _baseline_dir(tmp_path, model="patchcore", score_key="model_score"):
	base = tmp_path / "real-baseline-v3-patchcore"
	export = base / "fold0" / model / "export" / "weights" / "openvino"
	export.mkdir(parents=True)
	(export / "model.xml").write_text("<net/>", encoding="utf-8")
	(export / "model.bin").write_bytes(b"\x00\x01\x02")
	summary = {
		"dataset": r"data\studio\af9b173a-ee59",
		"camera": "wrist",
		"frames": 612,
		"episodes": 35,
		f"{score_key}/median": {
			"episode_confusion": {
				"normal->normal": 14,
				"normal->defective": 9,
				"defective->defective": 11,
				"defective->normal": 1,
			},
			"thresholds": [0.40, 0.50],
			"frame_auroc_test_per_fold": [0.75, 0.85],
		},
		f"{score_key}/max": {"thresholds": [0.9, 0.9], "frame_auroc_test_per_fold": [0.1, 0.1]},
		"off_colour/median": {"thresholds": [0.2, 0.2]},
		"latency_model_includes_resize": {
			"CPU": {"median_ms": 306.0, "p90_ms": 368.0, "runs": 200},
			"GPU.0": {"median_ms": 135.0, "p90_ms": 141.0, "runs": 200},
			"NPU": "unavailable: no device",
			"off_colour_cpu": {"median_ms": 1.9},
		},
	}
	folds = [
		{
			"fold": 0,
			"val_fold": 1,
			"train_frames": 210,
			f"{score_key}/median": {"threshold": 0.40, "frame_auroc_test": 0.75},
		},
		{
			"fold": 1,
			"val_fold": 0,
			"train_frames": 220,
			f"{score_key}/median": {"threshold": 0.50, "frame_auroc_test": 0.85},
		},
	]
	(base / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
	(base / "folds.json").write_text(json.dumps(folds), encoding="utf-8")
	return base


def test_anomaly_record_reads_one_fold_model_with_its_threshold_and_cross_fold_results(tmp_path):
	base = _baseline_dir(tmp_path)
	record = anomaly_record(base, 0, params={"coreset_ratio": 0.1})
	assert record.name == "patchcore-real-baseline-v3-patchcore-fold0"
	assert record.params["model"] == "patchcore"
	assert record.params["fold"] == 0
	assert record.params["val_fold"] == 1
	assert record.params["train_frames"] == 210
	assert record.params["threshold_cpu"] == pytest.approx(0.40)
	assert record.params["aggregate"] == "median"
	assert record.params["dataset"] == "af9b173a-ee59"
	assert record.params["camera"] == "wrist"
	assert record.params["coreset_ratio"] == 0.1
	assert record.metrics["fold_frame_auroc_test"] == [(0, 0.75)]
	assert record.metrics["defects_caught"] == [(0, 11.0)]
	assert record.metrics["defects_total"] == [(0, 12.0)]
	assert record.metrics["normals_passed"] == [(0, 14.0)]
	assert record.metrics["normals_total"] == [(0, 23.0)]
	assert record.metrics["frame_auroc_mean"][0][1] == pytest.approx(0.80)
	assert record.metrics["latency_CPU_median_ms"] == [(0, 306.0)]
	assert record.metrics["latency_GPU.0_p90_ms"] == [(0, 141.0)]
	assert not any(key.startswith("latency_NPU") or "off_colour" in key for key in record.metrics)
	assert record.tags == {"source": "real", "kind": "anomaly", "model": "patchcore", "status": "baseline"}
	assert {p.name for p in record.artifacts} == {"model.xml", "model.bin", "summary.json", "folds.json"}


def test_anomaly_record_accepts_per_model_score_keys(tmp_path):
	record = anomaly_record(_baseline_dir(tmp_path, model="padim", score_key="padim_score"), 0)
	assert record.params["model"] == "padim"
	assert record.params["threshold_cpu"] == pytest.approx(0.40)
	assert record.metrics["defects_caught"] == [(0, 11.0)]


def test_anomaly_record_without_an_exported_model_is_rejected(tmp_path):
	with pytest.raises(FileNotFoundError):
		anomaly_record(_baseline_dir(tmp_path), 1)


def test_parse_params_keeps_numbers_and_rejects_pairs_without_value():
	assert parse_params(["coreset_ratio=0.1", "backbone=wide_resnet50_2", "batch=2"]) == {
		"coreset_ratio": 0.1,
		"backbone": "wide_resnet50_2",
		"batch": 2,
	}
	with pytest.raises(ValueError, match="KEY=VALUE"):
		parse_params(["coreset_ratio"])
