import json

import pytest

from defect_sorter.tracking import evaluation_record, training_record


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
