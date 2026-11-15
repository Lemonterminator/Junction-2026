import ast
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from defect_sorter.training import (
	build_plan,
	load_dataset,
	load_recipe,
	run_training,
	validate_dataset,
	warm_start_state_dict,
)
from defect_sorter.training_preflight import validate_tasks

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "configs" / "training"
JOINTS = ["shoulder_pan.pos", "shoulder_lift.pos", "elbow_flex.pos", "wrist_flex.pos", "wrist_roll.pos", "gripper.pos"]


def dataset_spec(tmp_path: Path) -> Path:
	path = tmp_path / "dataset.toml"
	path.write_text(
		'root = "recording"\nrepo_id = "local/sorting"\nfps = 30\n'
		'camera_keys = ["observation.images.top", "observation.images.wrist"]\n'
		f"joint_names = {json.dumps(JOINTS)}\n"
		'joint_units = ["degrees", "degrees", "degrees", "degrees", "degrees", "normalized_0_100"]\n',
		encoding="utf-8",
	)
	return path


def recording(tmp_path: Path, episodes: int = 10) -> Path:
	root = tmp_path / "recording"
	(root / "meta").mkdir(parents=True)
	features = {
		"observation.state": {"dtype": "float32", "shape": [6], "names": JOINTS},
		"action": {"dtype": "float32", "shape": [6], "names": JOINTS},
		"observation.images.top": {"dtype": "video", "shape": [480, 640, 3]},
		"observation.images.wrist": {"dtype": "video", "shape": [480, 640, 3]},
	}
	(root / "meta" / "info.json").write_text(
		json.dumps({"codebase_version": "v3.0", "total_episodes": episodes, "fps": 30, "features": features}),
		encoding="utf-8",
	)
	return root


def test_missing_recording_is_reported_in_plan_but_never_launches(tmp_path):
	dataset = load_dataset(dataset_spec(tmp_path))
	plan = build_plan(load_recipe(RECIPES / "smolvla_expert.toml"), dataset, tmp_path / "runs", "trial", ROOT)
	assert plan["dataset_status"] == "missing"
	assert plan["metrics"] is None
	assert plan["config"]["model"]["init_args"]["pretrained_name_or_path"] == "lerobot/smolvla_base"
	with pytest.raises(ValueError, match=r"info\.json"):
		run_training(plan)
	assert not (tmp_path / "runs").exists()


@pytest.mark.parametrize(
	("recipe", "class_name"),
	[("act_baseline", "ACT"), ("smolvla_expert", "SmolVLA"), ("pi05_lora", "Pi05")],
)
def test_recipes_target_real_constructor_and_deterministic_episode_split(tmp_path, recipe, class_name):
	recording(tmp_path)
	plan = build_plan(
		load_recipe(RECIPES / f"{recipe}.toml"), load_dataset(dataset_spec(tmp_path)), tmp_path / "runs", "r1", ROOT
	)
	assert plan == build_plan(
		load_recipe(RECIPES / f"{recipe}.toml"), load_dataset(tmp_path / "dataset.toml"), tmp_path / "runs", "r1", ROOT
	)
	assert plan["config"]["model"]["class_path"] == f"physicalai.policies.{class_name}"
	# random.Random(42).sample(range(10), 1) independently gives episode 1.
	assert plan["episodes"]["validation"] == [1]
	assert plan["episodes"]["training"] == [0, 2, 3, 4, 5, 6, 7, 8, 9]
	assert set(plan["episodes"]["training"]).isdisjoint(plan["episodes"]["validation"])
	assert plan["command"][-3:] == ["fit", "--config", str(tmp_path / "runs" / "r1" / "config.json")]
	assert "--extra" in plan["command"]
	assert "cuda" in plan["command"]
	assert plan["config"]["trainer"]["accelerator"] == "gpu"
	assert plan["config"]["trainer"]["devices"] == [0]
	assert not (tmp_path / "runs").exists()


def test_smol_camera_order_and_pi_lora_do_not_conflict(tmp_path):
	dataset = load_dataset(dataset_spec(tmp_path))
	smol = build_plan(load_recipe(RECIPES / "smolvla_expert.toml"), dataset, tmp_path / "runs", "smol", ROOT)
	assert smol["config"]["model"]["init_args"]["image_key_reorder_map"] == {"top": 0, "wrist": 1}
	assert smol["config"]["model"]["init_args"]["train_expert_only"] is True
	pi = build_plan(load_recipe(RECIPES / "pi05_lora.toml"), dataset, tmp_path / "runs", "pi", ROOT)
	kwargs = pi["config"]["model"]["init_args"]
	assert kwargs["lora_enabled"] is True
	assert kwargs["train_expert_only"] is False
	assert kwargs["freeze_vision_encoder"] is False
	assert pi["experimental"] is True


@pytest.mark.parametrize(
	"damage", ["wrong_joint_order", "missing_camera", "extra_camera", "wrong_fps", "one_episode", "bad_dimensions"]
)
def test_recording_schema_rejects_incompatible_inputs(tmp_path, damage):
	root = recording(tmp_path)
	info_path = root / "meta" / "info.json"
	info = json.loads(info_path.read_text())
	if damage == "wrong_joint_order":
		info["features"]["action"]["names"] = JOINTS[::-1]
	elif damage == "missing_camera":
		del info["features"]["observation.images.wrist"]
	elif damage == "extra_camera":
		info["features"]["observation.images.front"] = {"dtype": "video", "shape": [480, 640, 3]}
	elif damage == "wrong_fps":
		info["fps"] = 60
	elif damage == "one_episode":
		info["total_episodes"] = 1
	else:
		info["features"]["action"]["shape"] = [7]
	info_path.write_text(json.dumps(info))
	with pytest.raises(ValueError, match=r"contract|episodes"):
		validate_dataset(load_dataset(dataset_spec(tmp_path)))


@pytest.mark.parametrize("name", ["../escape", "a/b", "..", "C:\\oops", ""])
def test_run_names_cannot_escape_output_root(tmp_path, name):
	with pytest.raises(ValueError, match="run name"):
		build_plan(
			load_recipe(RECIPES / "act_baseline.toml"),
			load_dataset(dataset_spec(tmp_path)),
			tmp_path / "runs",
			name,
			ROOT,
		)


@pytest.mark.parametrize("bad", ["nan", "inf", "-1.0", "0.0"])
def test_nonfinite_or_nonpositive_learning_rate_is_rejected(tmp_path, bad):
	path = tmp_path / "bad.toml"
	path.write_text(
		(RECIPES / "smolvla_expert.toml").read_text().replace("optimizer_lr = 0.0001", f"optimizer_lr = {bad}")
	)
	with pytest.raises(ValueError, match="optimizer_lr"):
		load_recipe(path)


def test_metadata_is_not_mistaken_for_a_complete_recording(tmp_path):
	recording(tmp_path)
	plan = build_plan(
		load_recipe(RECIPES / "act_baseline.toml"),
		load_dataset(dataset_spec(tmp_path)),
		tmp_path / "runs",
		"trial",
		ROOT,
	)
	with pytest.raises(ValueError, match="Parquet"):
		run_training(plan)
	assert not (tmp_path / "runs").exists()


def test_existing_output_is_never_replaced(tmp_path):
	dataset_root = recording(tmp_path)
	(dataset_root / "data").mkdir()
	(dataset_root / "data" / "file.parquet").write_bytes(b"PAR1fixture")
	(dataset_root / "videos").mkdir()
	(dataset_root / "videos" / "video.mp4").write_bytes(b"fixture")
	output = tmp_path / "runs" / "trial"
	output.mkdir(parents=True)
	(output / "keep.txt").write_text("existing results")
	plan = build_plan(
		load_recipe(RECIPES / "act_baseline.toml"),
		load_dataset(dataset_spec(tmp_path)),
		tmp_path / "runs",
		"trial",
		ROOT,
	)
	with pytest.raises(FileExistsError):
		run_training(plan)
	assert (output / "keep.txt").read_text() == "existing results"


def test_cli_plan_is_real_json_without_optional_training_dependencies(tmp_path):
	result = subprocess.run(  # noqa: S603
		[
			sys.executable,
			"-m",
			"defect_sorter.training",
			"plan",
			"--recipe",
			str(RECIPES / "pi05_lora.toml"),
			"--dataset",
			str(dataset_spec(tmp_path)),
			"--run-name",
			"cli",
		],
		capture_output=True,
		text=True,
		check=False,
	)
	assert result.returncode == 0, result.stderr
	assert json.loads(result.stdout)["dataset_status"] == "missing"


def test_generated_kwargs_match_pinned_upstream_signatures(tmp_path):
	paths = {
		"act_baseline": "policies/act/policy.py",
		"smolvla_expert": "policies/smolvla/policy.py",
		"pi05_lora": "policies/pi05/policy.py",
	}
	base = ROOT / "external" / "physical-ai-studio" / "library" / "src" / "physicalai"
	for recipe, relative in paths.items():
		plan = build_plan(
			load_recipe(RECIPES / f"{recipe}.toml"),
			load_dataset(dataset_spec(tmp_path)),
			tmp_path / "runs",
			recipe,
			ROOT,
		)
		for config_key, path, class_name in [
			("model", base / relative, plan["config"]["model"]["class_path"].split(".")[-1]),
			("data", base / "data/lerobot/datamodule.py", "LeRobotDataModule"),
		]:
			tree = ast.parse(path.read_text(encoding="utf-8"))
			cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
			constructor = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "__init__")
			accepted = {arg.arg for arg in constructor.args.args + constructor.args.kwonlyargs}
			assert set(plan["config"][config_key]["init_args"]) <= accepted


def test_mapping_passes_actual_upstream_camera_layout_without_importing_torch(tmp_path):
	path = ROOT / "external/physical-ai-studio/library/src/physicalai/policies/smolvla/preprocessor.py"
	tree = ast.parse(path.read_text(encoding="utf-8"))
	method = next(
		n
		for cls in tree.body
		if isinstance(cls, ast.ClassDef)
		for n in cls.body
		if isinstance(n, ast.FunctionDef) and n.name == "_camera_slot_layout"
	)
	# Execute only the upstream pure layout method, not its heavy module imports.
	namespace = {}
	exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), "exec"), namespace)  # noqa: S102
	plan = build_plan(
		load_recipe(RECIPES / "smolvla_expert.toml"),
		load_dataset(dataset_spec(tmp_path)),
		tmp_path / "runs",
		"camera",
		ROOT,
	)
	mapping = plan["config"]["model"]["init_args"]["image_key_reorder_map"]
	preprocessor = SimpleNamespace(image_key_reorder_map={f"images.{k}": v for k, v in mapping.items()}, num_cameras=2)
	assert namespace["_camera_slot_layout"](preprocessor, ["images.wrist", "images.top"]) == [
		"images.top",
		"images.wrist",
	]


def test_units_are_explicit_operator_declarations(tmp_path):
	path = dataset_spec(tmp_path)
	dataset = load_dataset(path)
	assert dataset.joint_units[-1] == "normalized_0_100"
	path.write_text(path.read_text().replace("normalized_0_100", "guess"))
	with pytest.raises(ValueError, match="joint_units"):
		load_dataset(path)


def test_v2_dataset_rejected_instead_of_using_wrong_video_layout(tmp_path):
	root = recording(tmp_path)
	path = root / "meta" / "info.json"
	info = json.loads(path.read_text())
	info["codebase_version"] = "v2.1"
	path.write_text(json.dumps(info))
	with pytest.raises(ValueError, match=r"v3\.0"):
		validate_dataset(load_dataset(dataset_spec(tmp_path)))


@pytest.mark.parametrize(
	("labels", "indices", "frame_indices"),
	[
		([""], [0], [0]),
		(["   "], [0], [0]),
		(["sort good"], [1], [1]),
		(["sort good"], [0], [2]),
		(["sort good"], [0], []),
		(["sort good"], [0], [None]),
	],
)
def test_runtime_language_preflight_rejects_empty_labels_or_broken_task_references(labels, indices, frame_indices):
	with pytest.raises(ValueError, match="task"):
		validate_tasks(labels, indices, frame_indices)


def test_runtime_language_preflight_accepts_ordered_tasks_and_frame_references():
	validate_tasks(["place good object in green bowl", "place defective object in pink bowl"], [0, 1], [1, 0, 1])


@pytest.mark.parametrize(
	("platform", "entry"),
	[
		("linux", ["physicalai", "fit"]),
		("win32", ["python", "scripts/offline_pipeline/physicalai_without_robot_cli.py", "fit"]),
	],
)
def test_windows_plan_launches_fit_without_the_posix_only_robot_cli(tmp_path, platform, entry):
	recording(tmp_path)
	plan = build_plan(
		load_recipe(RECIPES / "smolvla_expert.toml"),
		load_dataset(dataset_spec(tmp_path)),
		tmp_path / "runs",
		"r1",
		ROOT,
		platform=platform,
	)
	tail = [str(ROOT / part) if part.endswith(".py") else part for part in entry]
	tail += ["--config", str(tmp_path / "runs" / "r1" / "config.json")]
	assert plan["command"][-len(tail) :] == tail
	assert plan["command"][:2] == ["uv", "run"]
	# torchcodec needs FFmpeg DLLs that Windows wheels do not ship; PyAV bundles its own decoders.
	expected_backend = "pyav" if platform == "win32" else None
	assert plan["config"]["data"]["init_args"].get("video_backend") == expected_backend


def warm_recipe(tmp_path: Path, extra: str = 'warm_start = "sort-depth-v2-10k"\n') -> Path:
	path = tmp_path / "warm.toml"
	path.write_text(extra + (RECIPES / "smolvla_expert.toml").read_text(encoding="utf-8"), encoding="utf-8")
	return path


def test_warm_start_loads_the_converted_policy_directory_instead_of_the_base(tmp_path):
	recipe = load_recipe(warm_recipe(tmp_path))
	dataset = load_dataset(dataset_spec(tmp_path))
	plan = build_plan(recipe, dataset, tmp_path / "runs", "warm", ROOT, warm_start_root=tmp_path / "warm-start")
	kwargs = plan["config"]["model"]["init_args"]
	assert kwargs["pretrained_name_or_path"] == str(tmp_path / "warm-start" / "sort-depth-v2-10k")
	assert kwargs["train_expert_only"] is True
	assert plan["warm_start"] == "sort-depth-v2-10k"
	assert "warm_start" not in kwargs


def test_warm_start_needs_a_root_and_a_plain_name_and_only_applies_to_smolvla(tmp_path):
	recipe = load_recipe(warm_recipe(tmp_path))
	with pytest.raises(ValueError, match="warm_start_root"):
		build_plan(recipe, load_dataset(dataset_spec(tmp_path)), tmp_path / "runs", "warm", ROOT)
	for bad in ("../escape", "a/b", ""):
		with pytest.raises(ValueError, match="warm_start"):
			load_recipe(warm_recipe(tmp_path, f'warm_start = "{bad}"\n'))
	act = tmp_path / "act.toml"
	act.write_text('warm_start = "x"\n' + (RECIPES / "act_baseline.toml").read_text(encoding="utf-8"), encoding="utf-8")
	with pytest.raises(ValueError, match="warm_start"):
		load_recipe(act)


def test_recipe_without_warm_start_is_unchanged(tmp_path):
	plan = build_plan(
		load_recipe(RECIPES / "smolvla_expert.toml"),
		load_dataset(dataset_spec(tmp_path)),
		tmp_path / "runs",
		"base",
		ROOT,
		warm_start_root=tmp_path / "warm-start",
	)
	assert plan["config"]["model"]["init_args"]["pretrained_name_or_path"] == "lerobot/smolvla_base"
	assert plan["warm_start"] is None


def test_warm_start_weights_keep_only_the_policy_model_under_its_own_names():
	state = {
		"model._model.state_proj.weight": 1,
		"model._model.vlm_with_expert.lm_expert.layers.0.mlp.weight": 2,
		"_preprocessor._state_action_normalizer.buffer_state.mean": 3,
		"_postprocessor._action_denormalizer.buffer_action.std": 4,
	}
	# SmolVLA._initialize_model loads into policy.model after renaming a leading "model." to "_model.",
	# so the stored keys must be the policy.model keys, which already start with "_model.".
	assert warm_start_state_dict(state) == {
		"_model.state_proj.weight": 1,
		"_model.vlm_with_expert.lm_expert.layers.0.mlp.weight": 2,
	}
	with pytest.raises(ValueError, match="no policy weights"):
		warm_start_state_dict({"_preprocessor.x": 1})


def scaled_recipe(tmp_path: Path, extra: str) -> Path:
	path = tmp_path / "scaled.toml"
	path.write_text(extra + (RECIPES / "smolvla_expert.toml").read_text(encoding="utf-8"), encoding="utf-8")
	return path


def test_default_recipe_trains_on_one_gpu_in_process_with_periodic_checkpoints(tmp_path):
	plan = build_plan(
		load_recipe(RECIPES / "smolvla_expert.toml"), load_dataset(dataset_spec(tmp_path)), tmp_path / "runs", "one", ROOT
	)
	trainer = plan["config"]["trainer"]
	assert trainer["devices"] == [0]
	assert "strategy" not in trainer
	assert plan["config"]["data"]["init_args"]["num_workers"] == 0
	assert plan["config"]["data"]["init_args"]["persistent_workers"] is False
	periodic = [c["init_args"] for c in trainer["callbacks"] if "every_n_train_steps" in c["init_args"]]
	assert periodic == [
		{
			"dirpath": str(tmp_path / "runs" / "one" / "checkpoints"),
			"filename": "periodic",
			"every_n_train_steps": 500,
			"save_top_k": 1,
			"save_last": False,
		}
	]


def test_several_devices_use_ddp_and_data_workers_keep_running(tmp_path):
	recipe = load_recipe(scaled_recipe(tmp_path, "devices = 8\nnum_workers = 4\n"))
	plan = build_plan(recipe, load_dataset(dataset_spec(tmp_path)), tmp_path / "runs", "ddp", ROOT)
	trainer = plan["config"]["trainer"]
	assert trainer["devices"] == 8
	# Unused trainable parameters (target-time MLP without SnapFlow) must not stop the DDP gradient reduction.
	assert trainer["strategy"] == "ddp_find_unused_parameters_true"
	data = plan["config"]["data"]["init_args"]
	assert (data["num_workers"], data["persistent_workers"]) == (4, True)
	assert plan["devices"] == 8


@pytest.mark.parametrize("extra", ["devices = 0\n", "devices = 1.5\n", "num_workers = -1\n", "num_workers = true\n"])
def test_device_and_worker_counts_must_be_whole_numbers(tmp_path, extra):
	with pytest.raises(ValueError, match="devices|num_workers"):
		load_recipe(scaled_recipe(tmp_path, extra))
