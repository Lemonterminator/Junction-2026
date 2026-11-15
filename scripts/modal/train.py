"""Train a policy on a Modal GPU with the same pinned Studio environment and run layout as local training.

Three steps, each cheaper than the next is expensive (see docs/infrastructure/MODAL.md):

1. Local dry run, no Modal call and no cost::

	python scripts/modal/train.py --recipe configs/training/smolvla_sort_depth_v2.toml \
		--dataset configs/training/dataset.sort_depth_v2.toml --dataset-name sort-depth-v2 --run-name modal-smoke-01

2. Remote plan on CPU (builds the image once, checks the uploaded recording, no GPU)::

	modal run scripts/modal/train.py --recipe ... --dataset ... --dataset-name sort-depth-v2 --run-name modal-smoke-01

3. Real GPU training, bounded by ``--max-hours``. A recipe with ``devices = N`` runs data parallel on N GPUs of one
   container (``--gpu`` names the type, or a comma-separated fallback order such as ``L40S,A100-80GB,H100``) and the
   cost ceiling counts all N at the most expensive listed rate::

	modal run scripts/modal/train.py ... --gpu L40S --max-hours 4 --go

The run directory lands in the ``junction-training`` Volume under ``runs/<run-name>`` and is downloaded with
``modal volume get``; MLflow logging then runs locally with ``defect_sorter.tracking``.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
from pathlib import Path

import modal

REMOTE = "/repo"
# Inside the container Modal mounts this file at /root, and the checkout's src/ lives under REMOTE.
ROOT = Path(__file__).resolve().parents[2] if modal.is_local() else Path(REMOTE)
if str(ROOT / "src") not in sys.path:
	sys.path.insert(0, str(ROOT / "src"))

from defect_sorter.modal_training import (  # noqa: E402
	VOLUME_MOUNT,
	VOLUME_NAME,
	VolumeLayout,
	cost_ceiling,
	warm_start_upload_command,
)
from defect_sorter.training import load_dataset, load_recipe, validate_dataset  # noqa: E402

# USD per GPU hour from `modal billing rates` on 2026-11-15; re-check before large runs.
GPU_RATES = {"T4": 0.59, "L4": 0.80, "A10G": 1.10, "L40S": 1.95, "A100-40GB": 2.10, "A100-80GB": 2.50, "H100": 3.95}
STUDIO = ROOT / "external" / "physical-ai-studio"
BACKEND = f"{REMOTE}/external/physical-ai-studio/application/backend"
_SOURCE_IGNORE = [".venv", "**/__pycache__", "tests", "docs", "notebooks", "benchmarks", "**/*.pyc"]

app = modal.App("junction-train")
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
image = (
	modal.Image.debian_slim(python_version="3.13")
	.apt_install("ffmpeg", "git", "libgl1", "libglib2.0-0")
	.pip_install("uv==0.13.8")
	.env({"UV_LINK_MODE": "copy"})
	.add_local_dir(
		STUDIO / "library", f"{REMOTE}/external/physical-ai-studio/library", copy=True, ignore=_SOURCE_IGNORE
	)
	.add_local_dir(STUDIO / "application" / "backend", BACKEND, copy=True, ignore=_SOURCE_IGNORE)
	# The pinned lock gives the same torch/physicalai as the 5090; the backend app itself is not needed to train.
	.run_commands(f"uv sync --project {BACKEND} --extra cuda --frozen --no-install-project")
	# Later `uv run --frozen` calls from the training plan must reuse this environment, not resync it.
	.env({"UV_NO_SYNC": "1", "HF_HOME": f"{VOLUME_MOUNT}/hf-cache"})
	.add_local_dir(ROOT / "src", f"{REMOTE}/src", ignore=["**/__pycache__"])
)


def _container_plan(recipe: dict, dataset: dict, dataset_name: str, run_name: str) -> dict:
	from defect_sorter.modal_training import volume_dataset
	from defect_sorter.training import DatasetSpec, build_plan

	layout = VolumeLayout(dataset_name, run_name)
	spec = volume_dataset(DatasetSpec(**dataset), layout)
	return build_plan(
		recipe,
		spec,
		Path(layout.container_runs),
		run_name,
		Path(REMOTE),
		platform="linux",
		warm_start_root=Path(layout.container_warm_start),
	)


@app.function(image=image, volumes={str(VOLUME_MOUNT): volume}, timeout=600)
def plan(recipe: dict, dataset: dict, dataset_name: str, run_name: str) -> dict:
	"""Build the training plan inside the container against the uploaded recording; no GPU, nothing written."""
	volume.reload()
	result = _container_plan(recipe, dataset, dataset_name, run_name)
	result["run_exists"] = Path(result["output_dir"]).exists()
	return result


@app.function(
	image=image, gpu="L40S", cpu=8, memory=32768, volumes={str(VOLUME_MOUNT): volume}, timeout=4 * 3600, retries=0
)
def train(recipe: dict, dataset: dict, dataset_name: str, run_name: str) -> dict:
	"""Run ``training.run_training`` on the GPU and commit the run directory to the Volume periodically."""
	from defect_sorter.training import run_training

	volume.reload()
	plan_ = _container_plan(recipe, dataset, dataset_name, run_name)
	stop = threading.Event()

	def commit_periodically() -> None:
		# Metrics and last.ckpt become visible to `modal volume get` while training runs.
		while not stop.wait(600):
			volume.commit()

	threading.Thread(target=commit_periodically, daemon=True).start()
	try:
		code = run_training(plan_)
	finally:
		stop.set()
		volume.commit()
	return {"returncode": code, "run_path": VolumeLayout(dataset_name, run_name).run_path}


def _local_summary(recipe_path: str, dataset_path: str, dataset_name: str, run_name: str, gpu: str, max_hours: float):
	recipe = load_recipe(Path(recipe_path))
	dataset = load_dataset(Path(dataset_path))
	layout = VolumeLayout(dataset_name, run_name)
	types = gpu.split(",")
	if any(t not in GPU_RATES for t in types):
		raise ValueError(f"gpu must be one or more comma-separated of {sorted(GPU_RATES)}")
	# A list is a fallback order; the ceiling assumes the most expensive type is the one Modal grants.
	rate = max(GPU_RATES[t] for t in types)
	info_exists = (Path(dataset.root) / "meta" / "info.json").is_file()
	if info_exists:
		validate_dataset(dataset)
	summary = {
		"recipe": recipe["name"],
		"max_steps": recipe["max_steps"],
		"local_recording": dataset.root,
		"local_recording_metadata": "validated" if info_exists else "missing",
		"volume": VOLUME_NAME,
		"upload": " ".join(layout.upload_command(dataset.root)),
		"download": " ".join(layout.download_command()),
		"gpu": gpu,
		"gpus": recipe["devices"],
		"gpu_usd_per_hour_max": rate * recipe["devices"],
		"max_hours": max_hours,
		"gpu_cost_ceiling_usd": round(cost_ceiling(rate * recipe["devices"], max_hours), 2),
		"warm_start": recipe["warm_start"],
	}
	if recipe["warm_start"] is not None:
		local_warm = ROOT / "artifacts" / "warm-start" / recipe["warm_start"]
		summary["warm_start_upload"] = " ".join(warm_start_upload_command(str(local_warm), recipe["warm_start"]))
	return recipe, dataset, layout, summary


@app.local_entrypoint()
def main(
	recipe: str,
	dataset: str,
	dataset_name: str,
	run_name: str,
	gpu: str = "L40S",
	max_hours: float = 4.0,
	go: bool = False,
) -> None:
	"""Plan remotely on CPU; with ``--go`` train on one GPU for at most ``--max-hours``."""
	from dataclasses import asdict

	recipe_, dataset_, layout, summary = _local_summary(recipe, dataset, dataset_name, run_name, gpu, max_hours)
	print(json.dumps(summary, indent=2))  # noqa: T201
	try:
		volume.listdir(layout.dataset_path)
	except FileNotFoundError:
		raise SystemExit(f"recording not in the Volume; upload first:\n  {summary['upload']}") from None
	remote_plan = plan.remote(recipe_, asdict(dataset_), dataset_name, run_name)
	print(json.dumps({k: remote_plan[k] for k in ("dataset_status", "episodes", "output_dir", "run_exists")}, indent=2))  # noqa: T201
	if remote_plan["run_exists"]:
		raise SystemExit(f"run {run_name} already exists in the Volume; choose a new --run-name")
	if not go:
		print("dry run only; add --go to train on the GPU")  # noqa: T201
		return
	gpus = recipe_["devices"]
	# Data loader workers decode video on CPU: give each GPU's workers their own cores and memory.
	cpu = max(8, gpus * (recipe_["num_workers"] + 1))
	result = train.with_options(
		gpu=[t if gpus == 1 else f"{t}:{gpus}" for t in gpu.split(",")],
		cpu=cpu,
		memory=max(32768, cpu * 4096),
		timeout=int(max_hours * 3600),
	).remote(recipe_, asdict(dataset_), dataset_name, run_name)
	print(json.dumps(result, indent=2))  # noqa: T201
	print(f"download with:\n  {summary['download']}")  # noqa: T201


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Local dry run of a Modal training request; calls nothing remote.")
	parser.add_argument("--recipe", required=True)
	parser.add_argument("--dataset", required=True)
	parser.add_argument("--dataset-name", required=True)
	parser.add_argument("--run-name", required=True)
	parser.add_argument("--gpu", default="L40S")
	parser.add_argument("--max-hours", type=float, default=4.0)
	args = parser.parse_args()
	*_, local = _local_summary(args.recipe, args.dataset, args.dataset_name, args.run_name, args.gpu, args.max_hours)
	sys.stdout.write(json.dumps(local, indent=2) + "\n")
