"""Log finished training runs and twin evaluations to an MLflow tracking server.

Training runs are logged after they finish, from the run directory that ``defect_sorter.training run`` writes
(``plan.json``, Lightning's ``metrics/version_*/metrics.csv``, ``checkpoints/``), so the trainer's isolated
environment does not need MLflow. Every run is tagged with its data ``source`` (``twin``, ``sim`` or ``real``) so twin
and simulated results never sit unlabelled next to real ones. Reading run directories needs no MLflow; logging needs the ``tracking`` extra::

	uv run --extra tracking mlflow server --host 127.0.0.1 --port 5000 \
		--backend-store-uri sqlite:///artifacts/mlflow/mlflow.db --artifacts-destination artifacts/mlflow/artifacts
	uv run --extra tracking python -m defect_sorter.tracking training artifacts/training/studio-smoke-1
	uv run --extra tracking python -m defect_sorter.tracking evaluation artifacts/twin/eval-padim-CPU
	uv run --extra tracking python -m defect_sorter.tracking anomaly artifacts/anomaly/real-baseline-v2 --fold 0

Anomaly models from ``scripts/anomaly/real_baseline.py`` are logged one fold model at a time with the threshold chosen on
that fold's validation episodes, tagged ``status = baseline``.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_URI = "http://127.0.0.1:5000"


@dataclass
class RunRecord:
	"""What gets logged as one MLflow run: params, step-indexed metric series, tags and files."""

	name: str
	params: dict[str, Any] = field(default_factory=dict)
	metrics: dict[str, list[tuple[int, float]]] = field(default_factory=dict)
	tags: dict[str, str] = field(default_factory=dict)
	artifacts: list[Path] = field(default_factory=list)


def _source(repo_id: str) -> str:
	if "twin" in repo_id:
		return "twin"
	return "sim" if "sim" in repo_id else "real"


def training_record(run_dir: Path) -> RunRecord:
	"""Read a ``training.py run`` directory: plan parameters, Lightning CSV metrics and the checkpoint to keep.

	The kept checkpoint is ``best.ckpt`` when validation produced one, otherwise ``last.ckpt``.

	Raises
	------
	FileNotFoundError
		When ``plan.json`` is missing; only planned runs are logged.
	"""
	plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))
	config = plan["config"]
	dataset = plan["dataset"]
	episodes = plan.get("episodes") or {}
	params: dict[str, Any] = {
		"recipe": plan["recipe"],
		"experimental": plan.get("experimental", False),
		"policy": config["model"]["class_path"],
		"max_steps": config["trainer"]["max_steps"],
		"precision": config["trainer"]["precision"],
		"accumulate_grad_batches": config["trainer"]["accumulate_grad_batches"],
		"batch_size": config["data"]["init_args"]["train_batch_size"],
		"dataset_repo_id": dataset["repo_id"],
		"dataset_root": dataset["root"],
		"fps": dataset["fps"],
		"camera_keys": ",".join(dataset["camera_keys"]),
		"train_episodes": len(episodes.get("training", [])),
		"val_episodes": len(episodes.get("validation", [])),
		"devices": plan.get("devices", 1),
	}
	if plan.get("warm_start"):
		params["warm_start"] = plan["warm_start"]
	for key, value in config["model"].get("init_args", {}).items():
		if isinstance(value, (str, int, float, bool)):
			params[f"model.{key}"] = value
	metrics: dict[str, list[tuple[int, float]]] = {}
	for path in sorted((run_dir / "metrics").glob("version_*/metrics.csv")):
		with path.open(encoding="utf-8") as stream:
			for row in csv.DictReader(stream):
				step = int(row["step"])
				for key, value in row.items():
					if key in {"step", "epoch"} or not value:
						continue
					metrics.setdefault(key, []).append((step, float(value)))
	checkpoints = run_dir / "checkpoints"
	kept = next((checkpoints / n for n in ("best.ckpt", "last.ckpt") if (checkpoints / n).is_file()), None)
	return RunRecord(
		name=run_dir.name,
		params=params,
		metrics=metrics,
		tags={"source": _source(dataset["repo_id"]), "kind": "training"},
		artifacts=[kept] if kept else [],
	)


def evaluation_record(eval_dir: Path) -> RunRecord:
	"""Read an ``offline_pipeline evaluate`` directory (``summary.json``, ``episodes.jsonl``)."""
	summary = json.loads((eval_dir / "summary.json").read_text(encoding="utf-8"))
	metrics: dict[str, list[tuple[int, float]]] = {"attempts": [(0, float(summary["attempts"]))]}
	for key in ("correct_sort_rate", "mean_inspect_ms"):
		if summary.get(key) is not None:
			metrics[key] = [(0, float(summary[key]))]
	for status, count in summary.get("status", {}).items():
		metrics[f"status_{status}"] = [(0, float(count))]
	return RunRecord(
		name=eval_dir.name,
		params={
			"inspector": ",".join(summary.get("inspector", [])),
			"confusion": json.dumps(summary.get("confusion", {})),
		},
		metrics=metrics,
		tags={"source": ",".join(summary.get("modes", [])) or "unknown", "kind": "evaluation"},
		artifacts=[p for p in (eval_dir / "summary.json", eval_dir / "episodes.jsonl") if p.is_file()],
	)


ANOMALY_STATUS = "baseline"
"""Status tag of anomaly models from the grouped-fold baseline: real data, but not validated for the arm."""


def _anomaly_export(fold_dir: Path) -> tuple[str, Path]:
	for model_dir in sorted(p for p in fold_dir.glob("*") if p.is_dir()):
		xml = model_dir / "export" / "weights" / "openvino" / "model.xml"
		if xml.is_file():
			return model_dir.name, xml
	raise FileNotFoundError(f"no OpenVINO export under {fold_dir}")


def anomaly_record(baseline_dir: Path, fold: int, params: dict[str, Any] | None = None) -> RunRecord:
	"""Read one fold model of a ``scripts/anomaly/real_baseline.py`` run as a deployable baseline.

	The fold model keeps the threshold chosen on its own validation fold (episode median of frame scores, scored on
	the CPU), which is the only threshold the evaluation validated for that file. Cross-fold episode results and the
	latency measured on the fold-0 export are logged next to it; failed latency devices are left out.

	Parameters
	----------
	baseline_dir : Path
		Output directory of the baseline script (``summary.json``, ``folds.json``, ``fold<i>/<model>/export``).
	fold : int
		Test fold whose model is logged.
	params : dict, optional
		Training settings the run directory does not record, such as ``coreset_ratio``.

	Raises
	------
	FileNotFoundError
		When the fold has no OpenVINO export.
	"""
	model, xml = _anomaly_export(baseline_dir / f"fold{fold}")
	summary = json.loads((baseline_dir / "summary.json").read_text(encoding="utf-8"))
	fold_result = next(
		r for r in json.loads((baseline_dir / "folds.json").read_text(encoding="utf-8")) if r["fold"] == fold
	)
	score = next(key for key in summary if key.endswith("_score/median"))
	overall = summary[score]
	confusion = overall["episode_confusion"]
	aurocs = [a for a in overall["frame_auroc_test_per_fold"] if a is not None]
	metrics: dict[str, list[tuple[int, float]]] = {
		"fold_frame_auroc_test": [(0, float(fold_result[score]["frame_auroc_test"]))],
		"defects_caught": [(0, float(confusion["defective->defective"]))],
		"defects_total": [(0, float(confusion["defective->defective"] + confusion["defective->normal"]))],
		"normals_passed": [(0, float(confusion["normal->normal"]))],
		"normals_total": [(0, float(confusion["normal->normal"] + confusion["normal->defective"]))],
		"frame_auroc_mean": [(0, sum(aurocs) / len(aurocs))],
	}
	latency = next((v for k, v in summary.items() if k.startswith("latency_")), {})
	for device, values in latency.items():
		if device.startswith("off_colour") or not isinstance(values, dict):
			continue
		for stat in ("median_ms", "p90_ms"):
			if stat in values:
				metrics[f"latency_{device}_{stat}"] = [(0, float(values[stat]))]
	return RunRecord(
		name=f"{model}-{baseline_dir.name}-fold{fold}",
		params={
			"model": model,
			"dataset": summary["dataset"].replace("\\", "/").rsplit("/", 1)[-1],
			"camera": summary["camera"],
			"frames": summary["frames"],
			"episodes": summary["episodes"],
			"fold": fold,
			"val_fold": fold_result["val_fold"],
			"train_frames": fold_result["train_frames"],
			"aggregate": "median",
			"threshold_cpu": float(fold_result[score]["threshold"]),
			**(params or {}),
		},
		metrics=metrics,
		tags={"source": "real", "kind": "anomaly", "model": model, "status": ANOMALY_STATUS},
		artifacts=[xml, xml.with_suffix(".bin"), baseline_dir / "summary.json", baseline_dir / "folds.json"],
	)


def log_record(record: RunRecord, uri: str, experiment: str, *, artifacts: bool = True) -> str:
	"""Create one MLflow run from ``record`` and return its run id."""
	import mlflow

	mlflow.set_tracking_uri(uri)
	mlflow.set_experiment(experiment)
	with mlflow.start_run(run_name=record.name) as run:
		mlflow.set_tags(record.tags)
		mlflow.log_params(record.params)
		for key, series in record.metrics.items():
			for step, value in series:
				mlflow.log_metric(key, value, step=step)
		if artifacts:
			for path in record.artifacts:
				logger.info("uploading %s (%.1f MB)", path, path.stat().st_size / 1e6)
				mlflow.log_artifact(str(path))
		return run.info.run_id


def parse_params(pairs: list[str]) -> dict[str, Any]:
	"""``KEY=VALUE`` strings to a dict; values that parse as JSON numbers or booleans keep that type."""
	params: dict[str, Any] = {}
	for pair in pairs:
		key, sep, value = pair.partition("=")
		if not sep or not key:
			raise ValueError(f"expected KEY=VALUE, got {pair!r}")
		try:
			params[key] = json.loads(value)
		except json.JSONDecodeError:
			params[key] = value
	return params


def main(argv: list[str] | None = None) -> int:
	"""``training``, ``evaluation`` or ``anomaly`` followed by one or more directories."""
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("kind", choices=["training", "evaluation", "anomaly"])
	parser.add_argument("dirs", type=Path, nargs="+")
	parser.add_argument("--uri", default=DEFAULT_URI)
	parser.add_argument("--experiment", help="defaults to defect-sorter-<kind>")
	parser.add_argument("--no-artifacts", action="store_true", help="log params and metrics only")
	parser.add_argument("--fold", type=int, default=0, help="anomaly: fold model to log")
	parser.add_argument("--param", action="append", default=[], help="anomaly: extra KEY=VALUE training setting")
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
	if args.kind == "anomaly":
		extra = parse_params(args.param)

		def read(directory: Path) -> RunRecord:
			return anomaly_record(directory, args.fold, extra)
	else:
		read = training_record if args.kind == "training" else evaluation_record
	experiment = args.experiment or f"defect-sorter-{args.kind}"
	for directory in args.dirs:
		run_id = log_record(read(directory), args.uri, experiment, artifacts=not args.no_artifacts)
		sys.stdout.write(f"{directory} -> {experiment} run {run_id}\n")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
