"""Log finished training runs and twin evaluations to an MLflow tracking server.

Training runs are logged after they finish, from the run directory that ``defect_sorter.training run`` writes
(``plan.json``, Lightning's ``metrics/version_*/metrics.csv``, ``checkpoints/``), so the trainer's isolated
environment does not need MLflow. Every run is tagged with its data ``source`` (``twin`` or ``real``) so twin results
never sit unlabelled next to real ones. Reading run directories needs no MLflow; logging needs the ``tracking`` extra::

	uv run --extra tracking mlflow server --host 127.0.0.1 --port 5000 \
		--backend-store-uri sqlite:///artifacts/mlflow/mlflow.db --artifacts-destination artifacts/mlflow/artifacts
	uv run --extra tracking python -m defect_sorter.tracking training artifacts/training/studio-smoke-1
	uv run --extra tracking python -m defect_sorter.tracking evaluation artifacts/twin/eval-padim-CPU
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
	return "twin" if "twin" in repo_id else "real"


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
	}
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


def main(argv: list[str] | None = None) -> int:
	"""``training`` or ``evaluation`` followed by one or more directories."""
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("kind", choices=["training", "evaluation"])
	parser.add_argument("dirs", type=Path, nargs="+")
	parser.add_argument("--uri", default=DEFAULT_URI)
	parser.add_argument("--experiment", help="defaults to defect-sorter-<kind>")
	parser.add_argument("--no-artifacts", action="store_true", help="log params and metrics only")
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
	read = training_record if args.kind == "training" else evaluation_record
	experiment = args.experiment or f"defect-sorter-{args.kind}"
	for directory in args.dirs:
		run_id = log_record(read(directory), args.uri, experiment, artifacts=not args.no_artifacts)
		sys.stdout.write(f"{directory} -> {experiment} run {run_id}\n")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
