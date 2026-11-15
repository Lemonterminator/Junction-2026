"""Plan and launch isolated Physical AI policy training from local LeRobot recordings.

Planning needs only the light project environment. Running uses the pinned Studio
backend's separate CUDA environment and its real ``physicalai fit`` command.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import random
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_POLICIES = {"act": "ACT", "smolvla": "SmolVLA", "pi05": "Pi05"}
_RECIPE_KEYS = {
	"name",
	"policy",
	"experimental",
	"batch_size",
	"max_steps",
	"val_split",
	"split_seed",
	"precision",
	"accumulate_grad_batches",
	"model",
}
_OPTIONAL_RECIPE_KEYS = {"warm_start", "devices", "num_workers"}
_PERIODIC_CHECKPOINT_STEPS = 500
_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")


@dataclass(frozen=True)
class DatasetSpec:
	"""Explicit recording location and ordered camera/joint contract."""

	root: str
	repo_id: str
	fps: int
	camera_keys: list[str]
	joint_names: list[str]
	joint_units: list[str]


def _read_toml(path: Path) -> dict[str, Any]:
	with path.open("rb") as stream:
		return tomllib.load(stream)


def _positive(value: Any, name: str, *, integer: bool = False) -> None:
	if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
		raise ValueError(f"{name} must be finite and positive")
	if integer and not isinstance(value, int):
		raise ValueError(f"{name} must be an integer")


def load_dataset(path: Path) -> DatasetSpec:
	"""Load a dataset contract, resolving its root relative to the TOML file.

	Parameters
	----------
	path : Path
		Dataset contract TOML, containing no credentials.

	Returns
	-------
	DatasetSpec
		Recording contract with an absolute local root.
	"""
	values = _read_toml(path)
	if set(values) != {"root", "repo_id", "fps", "camera_keys", "joint_names", "joint_units"}:
		raise ValueError("dataset requires exactly root, repo_id, fps, camera_keys, joint_names, joint_units")
	for key in ("root", "repo_id"):
		if not isinstance(values[key], str) or not values[key].strip():
			raise ValueError(f"dataset {key} must be a nonempty string")
	_positive(values["fps"], "fps", integer=True)
	for key in ("camera_keys", "joint_names"):
		items = values[key]
		if not isinstance(items, list) or not items or any(not isinstance(x, str) or not x for x in items):
			raise ValueError(f"{key} must be a nonempty list of strings")
		if len(set(items)) != len(items):
			raise ValueError(f"{key} must contain unique entries")
	if any(not key.startswith("observation.images.") for key in values["camera_keys"]):
		raise ValueError("camera_keys must use full observation.images.<name> keys")
	units = values["joint_units"]
	if (
		not isinstance(units, list)
		or len(units) != len(values["joint_names"])
		or any(unit not in {"radians", "degrees", "normalized_-100_100", "normalized_0_100"} for unit in units)
	):
		raise ValueError("joint_units must declare one known unit convention per joint")
	values["root"] = str((path.resolve().parent / values["root"]).resolve())
	return DatasetSpec(**values)


def load_recipe(path: Path) -> dict[str, Any]:
	"""Read and validate a bounded recipe for the pinned Physical AI policies.

	Parameters
	----------
	path : Path
		Recipe TOML path.

	Returns
	-------
	dict[str, Any]
		Validated recipe; no optional ML libraries are imported.
	"""
	recipe = _read_toml(path)
	if not _RECIPE_KEYS <= set(recipe) <= _RECIPE_KEYS | _OPTIONAL_RECIPE_KEYS:
		raise ValueError(f"recipe requires exactly {sorted(_RECIPE_KEYS)}, optionally {sorted(_OPTIONAL_RECIPE_KEYS)}")
	devices = recipe.setdefault("devices", 1)
	if isinstance(devices, bool) or not isinstance(devices, int) or devices < 1:
		raise ValueError("devices must be a positive integer")
	workers = recipe.setdefault("num_workers", 0)
	if isinstance(workers, bool) or not isinstance(workers, int) or workers < 0:
		raise ValueError("num_workers must be a nonnegative integer")
	warm_start = recipe.setdefault("warm_start", None)
	if warm_start is not None:
		if recipe["policy"] != "smolvla":
			raise ValueError("warm_start is supported for SmolVLA recipes only")
		if not isinstance(warm_start, str) or not _NAME.fullmatch(warm_start) or ".." in warm_start:
			raise ValueError("warm_start must name a single converted policy directory")
	if recipe["policy"] not in _POLICIES:
		raise ValueError("unsupported policy")
	if not isinstance(recipe["experimental"], bool) or not isinstance(recipe["name"], str):
		raise ValueError("name must be a string and experimental must be boolean")
	for key in ("batch_size", "max_steps", "accumulate_grad_batches"):
		_positive(recipe[key], key, integer=True)
	if isinstance(recipe["split_seed"], bool) or not isinstance(recipe["split_seed"], int):
		raise ValueError("split_seed must be integer")
	_positive(recipe["val_split"], "val_split")
	if recipe["val_split"] >= 1:
		raise ValueError("val_split must be below 1")
	if recipe["precision"] not in {"32-true", "bf16-mixed"}:
		raise ValueError("precision must be 32-true or bf16-mixed")
	model = recipe["model"]
	if not isinstance(model, dict):
		raise ValueError("model must be a table")
	for key, value in model.items():
		if isinstance(value, float) and not math.isfinite(value):
			raise ValueError(f"{key} must be finite")
	_positive(model.get("optimizer_lr"), "optimizer_lr")
	if model.get("compile_model") is not False:
		raise ValueError("recipes must start with compile_model = false")
	if recipe["policy"] == "smolvla":
		if model.get("pretrained_name_or_path") != "lerobot/smolvla_base" or model.get("train_expert_only") is not True:
			raise ValueError("SmolVLA recipe must fine-tune the pretrained action expert")
	elif recipe["policy"] == "pi05":
		if model.get("pretrained_name_or_path") != "lerobot/pi05_base" or model.get("lora_enabled") is not True:
			raise ValueError("Pi05 recipe requires pretrained LoRA")
		if model.get("freeze_vision_encoder") is not False or model.get("train_expert_only") is not False:
			raise ValueError("Pi05 LoRA cannot combine with freeze/expert-only flags")
		for key in ("lora_rank", "lora_alpha"):
			_positive(model.get(key), key, integer=True)
		if not recipe["experimental"]:
			raise ValueError("Pi05 LoRA remains experimental on 32GB")
	return recipe


def validate_dataset(dataset: DatasetSpec) -> dict[str, Any]:
	"""Validate recording metadata against the declared camera/joint contract.

	Parameters
	----------
	dataset : DatasetSpec
		Expected recording contract.

	Returns
	-------
	dict[str, Any]
		Metadata, after schema checks. Payload decoding remains the trainer's job.
	"""
	info_path = Path(dataset.root) / "meta" / "info.json"
	if not info_path.is_file():
		raise ValueError(f"recording unavailable: {info_path}; plan mode does not require data")
	info = json.loads(info_path.read_text(encoding="utf-8"))
	if info.get("codebase_version") != "v3.0":
		raise ValueError("only Studio-compatible LeRobot v3.0 recordings are supported")
	total = info.get("total_episodes")
	if isinstance(total, bool) or not isinstance(total, int) or total < 2:
		raise ValueError("at least two recorded episodes required for held-out validation")
	if info.get("fps") != dataset.fps:
		raise ValueError("recording fps differs from dataset contract")
	features = info.get("features", {})
	for key in ("observation.state", "action"):
		feature = features.get(key, {})
		if feature.get("shape") != [len(dataset.joint_names)] or feature.get("names") != dataset.joint_names:
			raise ValueError(f"{key} dimension or joint order differs from contract")
		if feature.get("dtype") not in {"float32", "float64"}:
			raise ValueError(f"{key} must be floating point")
	cameras = {key for key in features if key.startswith("observation.images.")}
	if cameras != set(dataset.camera_keys):
		raise ValueError("recording camera keys differ from contract; select/remap cameras explicitly")
	for key in dataset.camera_keys:
		feature = features[key]
		shape = feature.get("shape", [])
		if feature.get("dtype") not in {"video", "image"} or len(shape) != 3 or 3 not in {shape[0], shape[-1]}:
			raise ValueError(f"{key} must be a three-channel image/video feature")
	return info


def build_plan(
	recipe: dict[str, Any],
	dataset: DatasetSpec,
	output_root: Path,
	run_name: str,
	project_root: Path,
	*,
	uv: str = "uv",
	platform: str = sys.platform,
	warm_start_root: Path | None = None,
) -> dict[str, Any]:
	"""Build an inspectable config and argument vector without creating files.

	Parameters
	----------
	recipe : dict[str, Any]
		Validated recipe.
	dataset : DatasetSpec
		Recording contract; recording may be absent while planning.
	output_root : Path
		Parent for independent run directories.
	run_name : str
		Single safe directory name.
	project_root : Path
		Checkout containing the pinned Studio submodule.
	uv : str
		uv executable name or absolute path.
	platform : str
		Target ``sys.platform``. On Windows the ``physicalai`` console script fails importing the POSIX-only
		robot CLI, so the plan runs ``fit`` through ``scripts/offline_pipeline/physicalai_without_robot_cli.py``, and videos
		are decoded with PyAV.
	warm_start_root : Path | None
		Parent of converted policy directories (``scripts/training/ckpt_to_warm_start.py``). Required when the recipe
		names ``warm_start``; SmolVLA then loads that directory's weights instead of ``lerobot/smolvla_base``, and
		normalisation statistics still come from this run's training data.

	Returns
	-------
	dict[str, Any]
		JSON-serializable plan. Metrics are explicitly unavailable.
	"""
	if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", run_name):
		raise ValueError("run name must be a single alphanumeric directory name")
	output = (output_root.resolve() / run_name).resolve()
	if output.parent != output_root.resolve():
		raise ValueError("run name must stay within output root")
	backend = project_root.resolve() / "external" / "physical-ai-studio" / "application" / "backend"
	if not (backend / "pyproject.toml").is_file():
		raise ValueError("initialize the pinned Studio submodule before planning training")
	info_path = Path(dataset.root) / "meta" / "info.json"
	info = validate_dataset(dataset) if info_path.exists() else None
	episodes = None
	if info is not None:
		total = info["total_episodes"]
		count = max(1, int(total * recipe["val_split"]))
		validation = sorted(random.Random(recipe["split_seed"]).sample(range(total), count))  # noqa: S311
		episodes = {"validation": validation, "training": sorted(set(range(total)) - set(validation))}
	model = dict(recipe["model"])
	warm_start = recipe.get("warm_start")
	if warm_start is not None:
		if warm_start_root is None:
			raise ValueError("recipe names warm_start; pass warm_start_root")
		model["pretrained_name_or_path"] = str(warm_start_root / warm_start)
	if recipe["policy"] == "smolvla":
		model.update(
			image_key_reorder_map={
				key.removeprefix("observation.images."): i for i, key in enumerate(dataset.camera_keys)
			},
			num_cameras=len(dataset.camera_keys),
		)
	fit_entry = (
		[
			"python",
			str(project_root.resolve() / "scripts" / "offline_pipeline" / "physicalai_without_robot_cli.py"),
			"fit",
		]
		if platform == "win32"
		else ["physicalai", "fit"]
	)
	config = {
		"model": {"class_path": f"physicalai.policies.{_POLICIES[recipe['policy']]}", "init_args": model},
		"data": {
			"class_path": "physicalai.data.lerobot.LeRobotDataModule",
			"init_args": {
				"repo_id": dataset.repo_id,
				"root": dataset.root,
				"data_format": "physicalai",
				"train_batch_size": recipe["batch_size"],
				"val_batch_size": recipe["batch_size"],
				"num_workers": recipe.get("num_workers", 0),
				"persistent_workers": recipe.get("num_workers", 0) > 0,
				"val_split": recipe["val_split"],
				"val_split_seed": recipe["split_seed"],
				"force_cache_sync": False,
			},
		},
		"trainer": {
			"accelerator": "gpu",
			"devices": [0] if recipe.get("devices", 1) == 1 else recipe["devices"],
			"precision": recipe["precision"],
			"max_steps": recipe["max_steps"],
			"max_epochs": -1,
			"accumulate_grad_batches": recipe["accumulate_grad_batches"],
			"default_root_dir": str(output),
			"log_every_n_steps": 1,
			"check_val_every_n_epoch": 1,
			"logger": {
				"class_path": "lightning.pytorch.loggers.CSVLogger",
				"init_args": {"save_dir": str(output), "name": "metrics"},
			},
			"callbacks": [
				{
					"class_path": "lightning.pytorch.callbacks.ModelCheckpoint",
					"init_args": {
						"dirpath": str(output / "checkpoints"),
						"filename": "best",
						"monitor": "val/loss",
						"mode": "min",
						"save_top_k": 1,
						"save_last": True,
					},
				},
				{
					# Validation runs once per epoch; this keeps a recent restart point between epochs.
					"class_path": "lightning.pytorch.callbacks.ModelCheckpoint",
					"init_args": {
						"dirpath": str(output / "checkpoints"),
						"filename": "periodic",
						"every_n_train_steps": _PERIODIC_CHECKPOINT_STEPS,
						"save_top_k": 1,
						"save_last": False,
					},
				},
			],
		},
	}
	if recipe.get("devices", 1) > 1:
		# Data parallel: one model copy per GPU. Unused trainable parameters (SmolVLA's target-time MLP without
		# SnapFlow) must not stall the gradient reduction.
		config["trainer"]["strategy"] = "ddp_find_unused_parameters_true"
	if platform == "win32":
		# torchcodec needs FFmpeg shared libraries that its Windows wheels do not ship; PyAV bundles its decoders.
		config["data"]["init_args"]["video_backend"] = "pyav"
	return {
		"recipe": recipe["name"],
		"experimental": recipe["experimental"],
		"dataset": asdict(dataset),
		"warm_start": warm_start,
		"devices": recipe.get("devices", 1),
		"dataset_status": "metadata_validated" if info is not None else "missing",
		"episodes": episodes,
		"output_dir": str(output),
		"config": config,
		"metrics": None,
		"command": [
			uv,
			"run",
			"--project",
			str(backend),
			"--extra",
			"cuda",
			"--frozen",
			*fit_entry,
			"--config",
			str(output / "config.json"),
		],
		"preflight_command": [
			uv,
			"run",
			"--project",
			str(backend),
			"--extra",
			"cuda",
			"--frozen",
			"python",
			str(project_root.resolve() / "src" / "defect_sorter" / "training_preflight.py"),
			dataset.root,
		],
		"notes": [
			"No training or export has run while planning.",
			"Payload decoding, CUDA compatibility, VRAM fit and policy quality need a real training run.",
			"Joint units are an operator declaration: LeRobot metadata does not prove their physical convention. Keep units, joint order and camera calibration identical during deployment.",
		],
	}


def warm_start_state_dict(state_dict: dict[str, Any]) -> dict[str, Any]:
	"""Select the policy-model weights of a Lightning SmolVLA checkpoint for a warm start.

	``SmolVLA._initialize_model`` loads ``model.safetensors`` into ``policy.model`` after renaming a leading
	``model.`` to ``_model.``. Lightning stores the same tensors as ``model.<policy.model key>``, so stripping the first
	``model.`` gives keys that load unchanged. Pre- and postprocessor buffers (old normalisation statistics) are dropped:
	the new run computes them from its own training data.

	Parameters
	----------
	state_dict : dict[str, Any]
		``checkpoint["state_dict"]`` of a SmolVLA Lightning checkpoint; values are passed through untouched.

	Returns
	-------
	dict[str, Any]
		``policy.model`` weights keyed as ``SmolVLA`` expects in ``model.safetensors``.
	"""
	weights = {key.removeprefix("model."): value for key, value in state_dict.items() if key.startswith("model.")}
	if not weights:
		raise ValueError("checkpoint holds no policy weights under model.")
	return weights


def run_training(plan: dict[str, Any]) -> int:
	"""Launch the real trainer after local data and non-overwrite preflight.

	Parameters
	----------
	plan : dict[str, Any]
		Plan returned by ``build_plan``.

	Returns
	-------
	int
		Trainer process exit code, including nonzero failures.
	"""
	dataset = DatasetSpec(**plan["dataset"])
	info = validate_dataset(dataset)
	output = Path(plan["output_dir"])
	if output.exists():
		raise FileExistsError(f"refusing to replace existing run: {output}")
	root = Path(dataset.root)
	if not any(path.stat().st_size for path in (root / "data").rglob("*.parquet")):
		raise ValueError("recording has no nonempty Parquet payload; metadata alone is not training data")
	for marker in (root / "meta" / "tasks.parquet", root / "meta" / "stats.json"):
		if not marker.is_file() or not marker.stat().st_size:
			raise ValueError(f"recording is missing required metadata: {marker.name}")
	if not any(path.stat().st_size for path in (root / "meta" / "episodes").glob("chunk-*/file-*.parquet")):
		raise ValueError("recording is missing episode Parquet shards")
	for key in dataset.camera_keys:
		if info["features"][key]["dtype"] == "video" and not any(
			path.stat().st_size for path in (root / "videos" / key).rglob("*.mp4")
		):
			raise ValueError(f"recording has no video payload for {key}")
	preflight = subprocess.run(plan["preflight_command"], check=False)  # noqa: S603
	if preflight.returncode:
		logger.error("runtime dataset preflight failed; no policy training started")
		return preflight.returncode
	output.mkdir(parents=True, exist_ok=False)
	(output / "config.json").write_text(json.dumps(plan["config"], indent=2, allow_nan=False) + "\n", encoding="utf-8")
	(output / "plan.json").write_text(json.dumps(plan, indent=2, allow_nan=False) + "\n", encoding="utf-8")
	logger.info("launching %s; checkpoint/metrics destination %s", plan["recipe"], output)
	return subprocess.run(plan["command"], check=False).returncode  # noqa: S603


def main(argv: list[str] | None = None) -> int:
	"""Parse the training CLI and print a plan or launch an explicit run.

	Parameters
	----------
	argv : list[str] | None
		CLI arguments, or process arguments when omitted.

	Returns
	-------
	int
		Zero for a plan, trainer status for a run, or two for invalid input.
	"""
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("mode", choices=["plan", "run"])
	parser.add_argument("--recipe", type=Path, required=True)
	parser.add_argument("--dataset", type=Path, required=True)
	parser.add_argument("--output-root", type=Path, default=Path("artifacts/training"))
	parser.add_argument("--run-name", required=True)
	parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
	parser.add_argument("--uv", default="uv")
	parser.add_argument("--warm-start-root", type=Path, default=Path("artifacts/warm-start"))
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO)
	try:
		plan = build_plan(
			load_recipe(args.recipe),
			load_dataset(args.dataset),
			args.output_root,
			args.run_name,
			args.project_root,
			uv=args.uv,
			warm_start_root=args.warm_start_root.resolve(),
		)
		if args.mode == "plan":
			sys.stdout.write(json.dumps(plan, indent=2, allow_nan=False) + "\n")
			return 0
		return run_training(plan)
	except (OSError, ValueError, TypeError, KeyError) as exc:
		logger.error("training request rejected: %s", exc)
		return 2


if __name__ == "__main__":
	raise SystemExit(main())
