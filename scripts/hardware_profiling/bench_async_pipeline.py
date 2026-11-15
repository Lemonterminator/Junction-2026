"""Benchmark script for the asynchronous inference and inspection pipeline on Intel Core Ultra.

Evaluates FP16 weight compression, per-device accuracy/latency parity across CPU, GPU,
and NPU, multi-device concurrent contention, synchronous serial loop vs asynchronous
overlapped pipeline.
"""

from __future__ import annotations

import json
import logging
import shutil
import sys
import threading
import time
from pathlib import Path
from typing import Any

import cv2
import numpy as np

# Ensure repository root and package are resolvable
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT / "src") not in sys.path:
	sys.path.insert(0, str(REPO_ROOT / "src"))

from defect_sorter.async_pipeline import (  # noqa: E402
	AsyncChunkPolicy,
	AsyncFrameSource,
	AsyncInspectionStage,
	DryRunCell,
	OpenVinoSmolVlaRunner,
	SmolVlaManifest,
	compress_ir_to_fp16,
	fetch_http_jpeg,
	load_prompt_tokens,
	summarize_latencies,
)
from defect_sorter.closed_loop import (  # noqa: E402
	DEFAULT_TASKS,
	intent_for,
)
from defect_sorter.inspection import (  # noqa: E402
	INPUT_SIZE,
	ThresholdInspector,
	isolate_object,
	to_model_input,
)
from defect_sorter.planner import PlannerState, RulePlanner  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("bench_async_pipeline")


def _file_sizes(xml_path: Path) -> dict[str, int]:
	bin_path = xml_path.with_suffix(".bin")
	xml_b = xml_path.stat().st_size if xml_path.exists() else 0
	bin_b = bin_path.stat().st_size if bin_path.exists() else 0
	return {
		"xml_bytes": xml_b,
		"bin_bytes": bin_b,
		"total_bytes": xml_b + bin_b,
	}


def stage_a_compression(exp_dir: Path) -> dict[str, Any]:
	"""Fold Bucketize ops and compress IR weights to FP16 half-precision."""
	import openvino as ov
	import torch
	from openvino import opset13 as ops

	logger.info("=== Stage A: Bucketize Folding & FP16 Compression ===")
	candidate_dir = exp_dir / "candidate"
	smolvla_xml = candidate_dir / "smolvla.xml"

	core = ov.Core()
	model = core.read_model(str(smolvla_xml))
	bks = [o for o in model.get_ordered_ops() if o.get_type_name() == "Bucketize"]
	logger.info("Found %d Bucketize ops in %s", len(bks), smolvla_xml)

	fp32_fixed_dir = exp_dir / "smolvla_fp32_fixed"
	fp32_fixed_dir.mkdir(parents=True, exist_ok=True)
	fp32_fixed_xml = fp32_fixed_dir / "smolvla.xml"

	if bks:
		logger.info("Folding %d Bucketize ops to constant tables using PyTorch verification...", len(bks))
		probe = ov.Model(
			[ops.result(b.output(0)) for b in bks]
			+ [ops.result(b.input_value(0)) for b in bks]
			+ [ops.result(b.input_value(1)) for b in bks],
			model.get_parameters(),
			"probe",
		)
		rng = np.random.default_rng(0)
		feed: dict[str, Any] = {}
		for i in probe.inputs:
			n = i.get_any_name()
			s = list(i.get_shape())
			et = i.get_element_type()
			if n.endswith("_mask") or "image_masks" in n:
				feed[n] = np.ones(s, dtype=bool)
			elif et == ov.Type.i64:
				feed[n] = rng.integers(1, 40000, size=s).astype(np.int64)
			else:
				feed[n] = (
					rng.random(s, dtype=np.float32) if n == "images" else rng.standard_normal(s).astype(np.float32)
				)

		compiled_probe = core.compile_model(probe, "CPU")
		r = compiled_probe.create_infer_request().infer(feed)
		k = len(bks)
		for j, b in enumerate(bks):
			cpu_ids = np.asarray(r[compiled_probe.output(j)])
			expected = np.tile(np.arange(32, dtype=np.int64), (cpu_ids.shape[0], 1))
			if not np.array_equal(cpu_ids, expected):
				coords = np.asarray(r[compiled_probe.output(k + j)])
				bounds = np.asarray(r[compiled_probe.output(2 * k + j)]).ravel()
				torch_ids = (
					torch.bucketize(torch.from_numpy(coords), torch.from_numpy(bounds), right=True)
					.numpy()
					.astype(np.int64)
				)
				if not np.array_equal(cpu_ids, torch_ids):
					raise RuntimeError(f"Bucketize op {j} CPU result differs from expected patch grid")
			b.output(0).replace(ops.constant(cpu_ids).output(0))

		model.validate_nodes_and_infer_types()
		ov.save_model(model, str(fp32_fixed_xml), compress_to_fp16=False)
		logger.info("Saved smolvla_fp32_fixed to %s", fp32_fixed_xml)
	else:
		logger.info("No Bucketize ops found; saving smolvla.xml to %s", fp32_fixed_xml)
		ov.save_model(model, str(fp32_fixed_xml), compress_to_fp16=False)

	# Copy companion files (manifest, prompt_tokens, tokenizer)
	for fname in ["manifest.json", "prompt_tokens.json", "tokenizer.xml", "tokenizer.bin"]:
		src = candidate_dir / fname
		if src.exists():
			shutil.copy(src, fp32_fixed_dir / fname)

	# FP16 Compression
	fp16_fixed_dir = exp_dir / "smolvla_fp16_fixed"
	fp16_fixed_xml = fp16_fixed_dir / "smolvla.xml"
	compress_ir_to_fp16(fp32_fixed_xml, fp16_fixed_xml)
	for fname in ["manifest.json", "prompt_tokens.json", "tokenizer.xml", "tokenizer.bin"]:
		src = candidate_dir / fname
		if src.exists():
			shutil.copy(src, fp16_fixed_dir / fname)
	logger.info("Saved smolvla_fp16_fixed to %s", fp16_fixed_xml)

	# Padim FP16
	padim_fp32_xml = exp_dir / "padim" / "model.xml"
	padim_fp16_xml = exp_dir / "padim_fp16" / "model.xml"
	compress_ir_to_fp16(padim_fp32_xml, padim_fp16_xml)
	logger.info("Saved padim_fp16 to %s", padim_fp16_xml)

	# Patchcore FP16
	patchcore_fp32_xml = exp_dir / "patchcore" / "model.xml"
	patchcore_fp16_xml = exp_dir / "patchcore_fp16" / "model.xml"
	compress_ir_to_fp16(patchcore_fp32_xml, patchcore_fp16_xml)
	logger.info("Saved patchcore_fp16 to %s", patchcore_fp16_xml)

	# Record sizes and compression ratios
	sizes = {
		"smolvla_fp32": _file_sizes(fp32_fixed_xml),
		"smolvla_fp16": _file_sizes(fp16_fixed_xml),
		"padim_fp32": _file_sizes(padim_fp32_xml),
		"padim_fp16": _file_sizes(padim_fp16_xml),
		"patchcore_fp32": _file_sizes(patchcore_fp32_xml),
		"patchcore_fp16": _file_sizes(patchcore_fp16_xml),
	}

	for k in ["smolvla", "padim", "patchcore"]:
		b32 = sizes[f"{k}_fp32"]["bin_bytes"]
		b16 = sizes[f"{k}_fp16"]["bin_bytes"]
		ratio = (b32 / b16) if b16 > 0 else 1.0
		sizes[f"{k}_bin_compression_ratio"] = round(ratio, 4)

	return {
		"bucketize_ops_folded": len(bks),
		"file_sizes": sizes,
	}


def _score_anomalib_crop(compiled_model: Any, output_port: Any, rgb_crop: np.ndarray, batch_size: int) -> float:
	x = to_model_input(rgb_crop, size=INPUT_SIZE)
	if batch_size > 1:
		x = np.repeat(x, batch_size, axis=0)
	res = compiled_model(x)
	val = res[output_port]
	return float(np.asarray(val).ravel()[0])


def stage_b_benchmarks(exp_dir: Path, live_camera_url: str = "http://100.76.18.70:8092") -> dict[str, Any]:
	"""Benchmark D415 camera capture, Anomalib inspection models, and SmolVLA policy."""
	import openvino as ov

	logger.info("=== Stage B: Real-Frame Per-Model Accuracy & Latency Parity ===")
	core = ov.Core()

	# 1. D415 HTTP Capture Latency
	logger.info("Benchmarking HTTP D415 camera capture from %s...", live_camera_url)
	top_url = f"{live_camera_url}/top.jpg"
	depth_url = f"{live_camera_url}/top_depth.jpg"

	fetch_times_ms: list[float] = []
	live_top_rgb = None
	live_top_depth = None

	for i in range(30):
		t0 = time.perf_counter()
		rgb = fetch_http_jpeg(top_url, timeout_s=3.0)
		depth = fetch_http_jpeg(depth_url, timeout_s=3.0)
		dt_ms = (time.perf_counter() - t0) * 1000.0
		fetch_times_ms.append(dt_ms)
		if i == 0:
			live_top_rgb = rgb
			live_top_depth = depth
			if rgb.shape != (416, 512, 3):
				raise RuntimeError(f"Unexpected top_rgb shape {rgb.shape}")
			if depth.shape != (416, 512, 3):
				raise RuntimeError(f"Unexpected top_depth shape {depth.shape}")

	http_stats = summarize_latencies(fetch_times_ms)
	logger.info(
		"Live HTTP capture 30 fetches: median=%.2f ms, p95=%.2f ms", http_stats["median_ms"], http_stats["p95_ms"]
	)

	# Load 8 real crops (4 normal, 4 defective)
	test_data_dir = exp_dir / "test_data"
	crops_dir = test_data_dir / "crops"
	normal_paths = sorted((crops_dir / "normal").glob("*.png"))[:4]
	defective_paths = sorted((crops_dir / "defective").glob("*.png"))[:4]
	if len(normal_paths) != 4:
		raise RuntimeError(f"Expected 4 normal crops, got {len(normal_paths)}")
	if len(defective_paths) != 4:
		raise RuntimeError(f"Expected 4 defective crops, got {len(defective_paths)}")

	normal_crops = [cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB) for p in normal_paths]
	defective_crops = [cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB) for p in defective_paths]
	all_crops = normal_crops + defective_crops

	# Load thresholds
	thresholds_file = exp_dir / "thresholds.json"
	thresholds_data = json.loads(thresholds_file.read_text(encoding="utf-8")) if thresholds_file.exists() else {}

	# 2. Benchmark Anomalib Padim and PatchCore across devices
	models_to_bench = [
		("padim", "FP32", exp_dir / "padim" / "model.xml"),
		("padim", "FP16", exp_dir / "padim_fp16" / "model.xml"),
		("patchcore", "FP32", exp_dir / "patchcore" / "model.xml"),
		("patchcore", "FP16", exp_dir / "patchcore_fp16" / "model.xml"),
	]

	device_targets = [
		("CPU", "f32"),
		("GPU", "f32"),
		("GPU", "f16"),
		("NPU", "f16"),
	]

	anomalib_results: dict[str, Any] = {}

	for model_name, precision_str, xml_path in models_to_bench:
		model_key = f"{model_name}_{precision_str.lower()}"
		anomalib_results[model_key] = {}
		cpu_f32_scores: list[float] | None = None

		for dev, hint in device_targets:
			target_name = f"{dev}_{hint}"
			logger.info("Evaluating Anomalib %s (%s) on %s...", model_name, precision_str, target_name)
			config: dict[str, str] = {"PERFORMANCE_HINT": "LATENCY"}
			if hint:
				config["INFERENCE_PRECISION_HINT"] = hint

			compile_start = time.perf_counter()
			try:
				model_ov = core.read_model(str(xml_path))
				port = model_ov.inputs[0]
				batch_dim = port.partial_shape[0]
				batch_size = batch_dim.get_length() if batch_dim.is_static else 1
				input_shape = (batch_size, 3, INPUT_SIZE, INPUT_SIZE)
				model_ov.reshape({port.any_name: list(input_shape)})
				compiled = core.compile_model(model_ov, dev, config)
				compile_time_s = time.perf_counter() - compile_start
				output_port = compiled.output("pred_score")
			except Exception as exc:
				compile_time_s = time.perf_counter() - compile_start
				logger.warning("Failed compiling %s on %s: %s", model_key, target_name, exc)
				anomalib_results[model_key][target_name] = {
					"status": "failed",
					"error": str(exc),
					"compile_time_s": round(compile_time_s, 4),
				}
				continue

			# Warmup runs
			warmup_crop = all_crops[0]
			for _ in range(5):
				_score_anomalib_crop(compiled, output_port, warmup_crop, batch_size)

			# 100 timed runs on warmup crop
			timed_ms: list[float] = []
			for _ in range(100):
				t0 = time.perf_counter()
				_score_anomalib_crop(compiled, output_port, warmup_crop, batch_size)
				timed_ms.append((time.perf_counter() - t0) * 1000.0)

			lat_stats = summarize_latencies(timed_ms)

			# Score all 8 real crops
			scores: list[float] = []
			for c in all_crops:
				s = _score_anomalib_crop(compiled, output_port, c, batch_size)
				scores.append(round(s, 6))

			normal_scores = scores[:4]
			defective_scores = scores[4:]
			mean_normal = float(np.mean(normal_scores))
			mean_defective = float(np.mean(defective_scores))

			# Compare against CPU f32 baseline of the FP32 IR
			if target_name == "CPU_f32" and precision_str == "FP32":
				cpu_f32_scores = scores
				pearson = 1.0
				max_abs_diff = 0.0
			elif cpu_f32_scores is not None:
				diffs = [abs(a - b) for a, b in zip(scores, cpu_f32_scores, strict=True)]
				max_abs_diff = float(max(diffs))
				if np.std(scores) > 1e-9 and np.std(cpu_f32_scores) > 1e-9:
					r_mat = np.corrcoef(scores, cpu_f32_scores)
					pearson = float(r_mat[0, 1])
				else:
					pearson = 1.0
			else:
				pearson = None
				max_abs_diff = None

			th = thresholds_data.get(model_name, {}).get("threshold", 0.5)
			acc = 0.5 * (
				float(np.mean([s < th for s in normal_scores])) + float(np.mean([s >= th for s in defective_scores]))
			)

			anomalib_results[model_key][target_name] = {
				"status": "success",
				"compile_time_s": round(compile_time_s, 4),
				"latency_ms": lat_stats,
				"scores": {
					"normal": normal_scores,
					"defective": defective_scores,
					"mean_normal": round(mean_normal, 4),
					"mean_defective": round(mean_defective, 4),
					"threshold": th,
					"accuracy": round(acc, 4),
				},
				"parity_vs_cpu_fp32": {
					"pearson_correlation": round(pearson, 6) if pearson is not None else None,
					"max_abs_diff": round(max_abs_diff, 6) if max_abs_diff is not None else None,
				},
			}
			logger.info(
				"Anomalib %s %s on %s: median=%.2f ms, p95=%.2f ms, mean normal=%.3f, mean defective=%.3f",
				model_name,
				precision_str,
				target_name,
				lat_stats["median_ms"],
				lat_stats["p95_ms"],
				mean_normal,
				mean_defective,
			)

	# 3. Benchmark SmolVLA policy models
	logger.info("Benchmarking SmolVLA sort-depth-v2-10k on CPU and GPU...")
	manifest = SmolVlaManifest.from_json(exp_dir / "candidate" / "manifest.json")
	prompt_tokens = load_prompt_tokens(exp_dir / "candidate" / "prompt_tokens.json")

	# Assemble real observation
	real_obs_images = {
		"wrist": np.load(test_data_dir / "normal_wrist.npy"),
		"front": np.load(test_data_dir / "normal_front.npy"),
		"top_rgb_v2": live_top_rgb if live_top_rgb is not None else np.load(test_data_dir / "normal_top_rgb_v2.npy"),
		"top_depth_v2": (
			live_top_depth if live_top_depth is not None else np.load(test_data_dir / "normal_top_depth_v2.npy")
		),
	}
	real_state = np.load(test_data_dir / "normal_state.npy")

	green_task = "Pick up the brick and place it in the green bowl.\n"
	pink_task = "Pick up the brick and place it in the pink bowl.\n"

	smolvla_models = [
		("smolvla_fp32", exp_dir / "smolvla_fp32_fixed"),
		("smolvla_fp16", exp_dir / "smolvla_fp16_fixed"),
	]

	smolvla_targets = [
		("CPU", "f32"),
		("GPU", "f16"),
		("GPU", "f32"),
	]

	smolvla_results: dict[str, Any] = {}
	cpu_fp32_raw_action: np.ndarray | None = None
	cpu_fp32_denorm_action: np.ndarray | None = None

	for model_tag, mdir in smolvla_models:
		smolvla_results[model_tag] = {}
		for dev, hint in smolvla_targets:
			target_name = f"{dev}_{hint}"
			logger.info("Evaluating SmolVLA %s on %s...", model_tag, target_name)
			t0_comp = time.perf_counter()
			runner = OpenVinoSmolVlaRunner(
				model_dir=mdir,
				device=dev,
				precision_hint=hint,
				manifest=manifest,
				prompt_tokens=prompt_tokens,
			)
			compile_time_s = time.perf_counter() - t0_comp

			# Warmup
			for _ in range(3):
				runner.infer_chunk(real_obs_images, real_state, green_task)

			# 20 timed runs
			preprocess_list: list[float] = []
			infer_list: list[float] = []
			postprocess_list: list[float] = []
			last_action = None

			for _ in range(20):
				actions, timings = runner.infer_chunk(real_obs_images, real_state, green_task)
				preprocess_list.append(timings["preprocess_ms"])
				infer_list.append(timings["infer_ms"])
				postprocess_list.append(timings["postprocess_ms"])
				last_action = actions

			# Also run pink task for action contrast
			pink_action, _ = runner.infer_chunk(real_obs_images, real_state, pink_task)

			infer_stats = summarize_latencies(infer_list)
			prep_stats = summarize_latencies(preprocess_list)
			post_stats = summarize_latencies(postprocess_list)

			# Parity vs CPU FP32
			if model_tag == "smolvla_fp32" and target_name == "CPU_f32":
				cpu_fp32_denorm_action = last_action
				# Recover raw action by normalizing back
				cpu_fp32_raw_action = (last_action - manifest.action_mean) / (manifest.action_std + 1e-8)
				cos_sim = 1.0
				max_raw_err = 0.0
				max_denorm_err = 0.0
			elif cpu_fp32_denorm_action is not None and last_action is not None:
				raw_curr = (last_action - manifest.action_mean) / (manifest.action_std + 1e-8)
				max_raw_err = float(np.max(np.abs(raw_curr - cpu_fp32_raw_action)))
				max_denorm_err = float(np.max(np.abs(last_action - cpu_fp32_denorm_action)))

				v1 = last_action.ravel()
				v2 = cpu_fp32_denorm_action.ravel()
				cos_sim = float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9))
			else:
				cos_sim = None
				max_raw_err = None
				max_denorm_err = None

			smolvla_results[model_tag][target_name] = {
				"compile_time_s": round(compile_time_s, 4),
				"preprocess_ms": prep_stats,
				"infer_ms": infer_stats,
				"postprocess_ms": post_stats,
				"parity_vs_cpu_fp32": {
					"cosine_similarity": round(cos_sim, 6) if cos_sim is not None else None,
					"max_abs_raw_error": round(max_raw_err, 6) if max_raw_err is not None else None,
					"max_abs_denorm_joint_error": round(max_denorm_err, 6) if max_denorm_err is not None else None,
				},
				"sample_actions": {
					"green_step0": [round(float(v), 4) for v in last_action[0]],
					"pink_step0": [round(float(v), 4) for v in pink_action[0]],
				},
			}
			logger.info(
				"SmolVLA %s on %s: infer median=%.2f ms, p95=%.2f ms, cosine sim=%.6f",
				model_tag,
				target_name,
				infer_stats["median_ms"],
				infer_stats["p95_ms"],
				cos_sim if cos_sim is not None else 1.0,
			)

	return {
		"http_d415_capture": http_stats,
		"anomalib": anomalib_results,
		"smolvla": smolvla_results,
	}


def stage_c_contention_and_pipeline(
	exp_dir: Path,
	live_camera_url: str = "http://100.76.18.70:8092",
) -> dict[str, Any]:
	"""Measure multi-device contention, serial loop, and asynchronous overlapped pipeline."""
	logger.info("=== Stage C: Contention & End-to-End Pipeline Benchmarks ===")

	test_data_dir = exp_dir / "test_data"
	manifest = SmolVlaManifest.from_json(exp_dir / "candidate" / "manifest.json")
	prompt_tokens = load_prompt_tokens(exp_dir / "candidate" / "prompt_tokens.json")

	# Prepare runners
	# 1. SmolVLA on GPU f16 (FP16 model)
	smolvla_runner = OpenVinoSmolVlaRunner(
		model_dir=exp_dir / "smolvla_fp16_fixed",
		device="GPU",
		precision_hint="f16",
		manifest=manifest,
		prompt_tokens=prompt_tokens,
	)

	# 2. Anomalib Padim on CPU
	padim_cpu_xml = exp_dir / "padim_fp16" / "model.xml"
	import openvino as ov

	core = ov.Core()
	padim_model = core.read_model(str(padim_cpu_xml))
	padim_port = padim_model.inputs[0]
	padim_model.reshape({padim_port.any_name: [1, 3, INPUT_SIZE, INPUT_SIZE]})
	padim_compiled_cpu = core.compile_model(padim_model, "CPU", {"PERFORMANCE_HINT": "LATENCY"})
	padim_out_cpu = padim_compiled_cpu.output("pred_score")

	def padim_cpu_score(crop_rgb: np.ndarray) -> float:
		return _score_anomalib_crop(padim_compiled_cpu, padim_out_cpu, crop_rgb, 1)

	# Try NPU for Padim if supported
	padim_compiled_npu = None
	padim_out_npu = None
	try:
		padim_compiled_npu = core.compile_model(padim_model, "NPU", {"PERFORMANCE_HINT": "LATENCY"})
		padim_out_npu = padim_compiled_npu.output("pred_score")
		logger.info("Successfully compiled Padim on NPU")
	except Exception as exc:
		logger.info("NPU not used for Padim: %s", exc)

	def padim_npu_score(crop_rgb: np.ndarray) -> float:
		if padim_compiled_npu is not None:
			return _score_anomalib_crop(padim_compiled_npu, padim_out_npu, crop_rgb, 1)
		return padim_cpu_score(crop_rgb)

	anomalib_score_fn = padim_npu_score if padim_compiled_npu is not None else padim_cpu_score
	anomalib_device_tag = "NPU" if padim_compiled_npu is not None else "CPU"

	# Load real test observation
	top_url = f"{live_camera_url}/top.jpg"
	depth_url = f"{live_camera_url}/top_depth.jpg"

	obs_images = {
		"wrist": np.load(test_data_dir / "normal_wrist.npy"),
		"front": np.load(test_data_dir / "normal_front.npy"),
		"top_rgb_v2": np.load(test_data_dir / "normal_top_rgb_v2.npy"),
		"top_depth_v2": np.load(test_data_dir / "normal_top_depth_v2.npy"),
	}
	obs_state = np.load(test_data_dir / "normal_state.npy")
	first_crop_path = next(iter((test_data_dir / "crops" / "normal").glob("*.png")))
	test_crop = cv2.cvtColor(cv2.imread(str(first_crop_path)), cv2.COLOR_BGR2RGB)

	task = "Pick up the brick and place it in the green bowl.\n"

	# Warmups
	smolvla_runner.infer_chunk(obs_images, obs_state, task)
	anomalib_score_fn(test_crop)

	# --- 1. Multi-Device Concurrent Contention (20 cycles) ---
	logger.info("Measuring concurrent contention across devices (20 cycles)...")

	def run_contention_benchmark(inspect_fn: Any, inspect_tag: str) -> dict[str, Any]:
		solo_camera_ms: list[float] = []
		solo_inspect_ms: list[float] = []
		solo_vla_ms: list[float] = []

		conc_camera_ms: list[float] = []
		conc_inspect_ms: list[float] = []
		conc_vla_ms: list[float] = []
		conc_cycle_ms: list[float] = []

		for _ in range(20):
			# Solo camera
			t0 = time.perf_counter()
			fetch_http_jpeg(top_url, timeout_s=3.0)
			fetch_http_jpeg(depth_url, timeout_s=3.0)
			solo_camera_ms.append((time.perf_counter() - t0) * 1000.0)

			# Solo inspect
			t0 = time.perf_counter()
			inspect_fn(test_crop)
			solo_inspect_ms.append((time.perf_counter() - t0) * 1000.0)

			# Solo vla
			t0 = time.perf_counter()
			smolvla_runner.infer_chunk(obs_images, obs_state, task)
			solo_vla_ms.append((time.perf_counter() - t0) * 1000.0)

			# Concurrent execution container
			thread_timings: dict[str, float] = {}

			def thread_cam(out_dict: dict[str, float]) -> None:
				t_start = time.perf_counter()
				fetch_http_jpeg(top_url, timeout_s=3.0)
				fetch_http_jpeg(depth_url, timeout_s=3.0)
				out_dict["cam"] = (time.perf_counter() - t_start) * 1000.0

			def thread_insp(out_dict: dict[str, float]) -> None:
				t_start = time.perf_counter()
				inspect_fn(test_crop)
				out_dict["insp"] = (time.perf_counter() - t_start) * 1000.0

			def thread_vla(out_dict: dict[str, float]) -> None:
				t_start = time.perf_counter()
				smolvla_runner.infer_chunk(obs_images, obs_state, task)
				out_dict["vla"] = (time.perf_counter() - t_start) * 1000.0

			t_cycle_0 = time.perf_counter()
			th1 = threading.Thread(target=thread_cam, args=(thread_timings,))
			th2 = threading.Thread(target=thread_insp, args=(thread_timings,))
			th3 = threading.Thread(target=thread_vla, args=(thread_timings,))

			th1.start()
			th2.start()
			th3.start()

			th1.join()
			th2.join()
			th3.join()
			t_cycle_1 = time.perf_counter()

			conc_camera_ms.append(thread_timings.get("cam", 0.0))
			conc_inspect_ms.append(thread_timings.get("insp", 0.0))
			conc_vla_ms.append(thread_timings.get("vla", 0.0))
			conc_cycle_ms.append((t_cycle_1 - t_cycle_0) * 1000.0)

		return {
			"inspect_device": inspect_tag,
			"solo": {
				"camera_ms": summarize_latencies(solo_camera_ms),
				"inspect_ms": summarize_latencies(solo_inspect_ms),
				"vla_ms": summarize_latencies(solo_vla_ms),
			},
			"concurrent": {
				"camera_ms": summarize_latencies(conc_camera_ms),
				"inspect_ms": summarize_latencies(conc_inspect_ms),
				"vla_ms": summarize_latencies(conc_vla_ms),
				"cycle_ms": summarize_latencies(conc_cycle_ms),
			},
			"overhead_ratio": {
				"vla_overhead": round(
					float(np.median(conc_vla_ms)) / max(float(np.median(solo_vla_ms)), 1e-6),
					4,
				),
				"inspect_overhead": round(
					float(np.median(conc_inspect_ms)) / max(float(np.median(solo_inspect_ms)), 1e-6),
					4,
				),
			},
		}

	contention_config1 = run_contention_benchmark(anomalib_score_fn, anomalib_device_tag)
	contention_config2 = run_contention_benchmark(padim_cpu_score, "CPU_f32")

	# --- 2. Synchronous Serial Closed-Loop (20 cycles) ---
	logger.info("Measuring synchronous serial closed-loop latency (20 cycles)...")
	inspector = ThresholdInspector(padim_cpu_score, threshold=0.5238, model="padim")
	planner = RulePlanner()

	serial_cam_ms: list[float] = []
	serial_crop_ms: list[float] = []
	serial_inspect_ms: list[float] = []
	serial_plan_ms: list[float] = []
	serial_vla_ms: list[float] = []
	serial_total_ms: list[float] = []

	for _ in range(20):
		t_total_0 = time.perf_counter()

		# Capture
		t0 = time.perf_counter()
		top_img = fetch_http_jpeg(top_url, timeout_s=3.0)
		top_depth = fetch_http_jpeg(depth_url, timeout_s=3.0)
		t1 = time.perf_counter()
		serial_cam_ms.append((t1 - t0) * 1000.0)

		# Crop / isolate
		t0 = time.perf_counter()
		wrist_img = obs_images["wrist"]
		bgr = cv2.cvtColor(wrist_img, cv2.COLOR_RGB2BGR)
		isolated = isolate_object(bgr)
		crop = cv2.cvtColor(isolated.crop, cv2.COLOR_BGR2RGB) if isolated is not None else None
		t1 = time.perf_counter()
		serial_crop_ms.append((t1 - t0) * 1000.0)

		# Inspect
		t0 = time.perf_counter()
		decision = inspector.inspect(crop)
		t1 = time.perf_counter()
		serial_inspect_ms.append((t1 - t0) * 1000.0)

		# Plan & intent
		t0 = time.perf_counter()
		pstate = PlannerState(
			label=decision.label,
			score=decision.score,
			threshold=decision.threshold,
			inspections=1,
			grasp_retries=0,
			last_outcome=None,
		)
		planner.decide(pstate)
		intent = intent_for(decision, DEFAULT_TASKS)
		t1 = time.perf_counter()
		serial_plan_ms.append((t1 - t0) * 1000.0)

		# SmolVLA Infer
		t0 = time.perf_counter()
		current_obs = {
			"wrist": wrist_img,
			"front": obs_images["front"],
			"top_rgb_v2": top_img,
			"top_depth_v2": top_depth,
		}
		smolvla_runner.infer_chunk(current_obs, obs_state, intent.task)
		t1 = time.perf_counter()
		serial_vla_ms.append((t1 - t0) * 1000.0)

		t_total_1 = time.perf_counter()
		serial_total_ms.append((t_total_1 - t_total_0) * 1000.0)

	serial_stats = {
		"camera_capture_ms": summarize_latencies(serial_cam_ms),
		"crop_isolate_ms": summarize_latencies(serial_crop_ms),
		"anomalib_inspect_ms": summarize_latencies(serial_inspect_ms),
		"planner_and_intent_ms": summarize_latencies(serial_plan_ms),
		"smolvla_infer_ms": summarize_latencies(serial_vla_ms),
		"total_serial_end_to_end_ms": summarize_latencies(serial_total_ms),
		"effective_chunk_rate_hz": round(1000.0 / float(np.median(serial_total_ms)), 2),
	}
	logger.info(
		"Serial loop: total median=%.2f ms (effective %.2f Hz chunk rate)",
		serial_stats["total_serial_end_to_end_ms"]["median_ms"],
		serial_stats["effective_chunk_rate_hz"],
	)

	# --- 3. Asynchronous Overlapped Pipeline (200 ticks / 4 chunks) ---
	logger.info("Measuring asynchronous overlapped pipeline over 200 ticks with stage switch...")

	# Replay frame provider fetching live camera
	def fetch_live_frames() -> dict[str, np.ndarray]:
		return {
			"wrist": obs_images["wrist"],
			"front": obs_images["front"],
			"top_rgb_v2": fetch_http_jpeg(top_url, timeout_s=3.0),
			"top_depth_v2": fetch_http_jpeg(depth_url, timeout_s=3.0),
		}

	frame_source = AsyncFrameSource(fetch_fn=fetch_live_frames, poll_interval_s=0.01)
	inspection_stage = AsyncInspectionStage(
		frame_source=frame_source,
		inspector=inspector,
		crop_fn=lambda imgs: test_crop,
	)

	policy = AsyncChunkPolicy(
		infer_fn=smolvla_runner,
		chunk_size=50,
		prefetch_step=25,
		max_steps=200,
	)

	cell = DryRunCell(
		images=obs_images,
		state=obs_state,
	)

	act_latencies_ms: list[float] = []
	reset_latency_ms: float = 0.0

	with frame_source, inspection_stage:
		# Wait for inspection snapshot to establish background flow
		time.sleep(0.1)
		policy.reset(task)

		step_count = 0
		while not policy.done() and step_count < 200:
			obs = cell.observe()
			t0 = time.perf_counter()
			action = policy.act(obs)
			dt_ms = (time.perf_counter() - t0) * 1000.0
			act_latencies_ms.append(dt_ms)
			cell.apply(action)
			step_count += 1

			# Mid-test stage switch at step 100
			if step_count == 100:
				t_reset_0 = time.perf_counter()
				policy.reset("Place the held brick in the pink bowl.\n")
				# First act call after reset must fetch immediately
				action_reset = policy.act(cell.observe())
				reset_latency_ms = (time.perf_counter() - t_reset_0) * 1000.0
				cell.apply(action_reset)
				step_count += 1

			# Emulate 30 Hz control loop tick pacing (33.3 ms per tick)
			time.sleep(0.001)

	async_step_stats = summarize_latencies(act_latencies_ms)
	snap_item = inspection_stage.slot.latest
	latest_snap = snap_item.value if snap_item is not None else None

	async_stats = {
		"act_step_ms": async_step_stats,
		"first_chunk_after_reset_ms": round(reset_latency_ms, 2),
		"stage_generation_count": policy.stage_generation,
		"total_ticks_executed": step_count,
		"background_inspection_sample": {
			"frame_id": latest_snap.frame_id if latest_snap else None,
			"capture_ms": round(latest_snap.capture_ms, 2) if latest_snap else None,
			"inspect_ms": round(latest_snap.inspect_ms, 2) if latest_snap else None,
			"total_ms": round(latest_snap.total_ms, 2) if latest_snap else None,
		},
	}
	logger.info(
		"Async pipeline: steady-state act() median=%.4f ms, p95=%.4f ms, max=%.2f ms, reset latency=%.2f ms",
		async_step_stats["median_ms"],
		async_step_stats["p95_ms"],
		async_step_stats["max_ms"],
		reset_latency_ms,
	)

	return {
		"contention_config1_npu_or_cpu": contention_config1,
		"contention_config2_cpu": contention_config2,
		"synchronous_serial_loop": serial_stats,
		"asynchronous_overlapped_pipeline": async_stats,
	}


def main() -> None:
	"""Main entry point for async pipeline hardware benchmark."""
	logger.info("Starting Async Inference Pipeline Hardware Profiling...")
	exp_dir = Path("/home/dev2/work/async_pipeline_exp")
	if not exp_dir.exists():
		exp_dir = REPO_ROOT / "artifacts" / "async_pipeline_exp"

	t0_total = time.time()
	results: dict[str, Any] = {
		"timestamp_epoch": time.time(),
		"experiment_dir": str(exp_dir),
	}

	# Stage A
	stage_a_res = stage_a_compression(exp_dir)
	results["stage_a_compression"] = stage_a_res

	# Stage B
	stage_b_res = stage_b_benchmarks(exp_dir)
	results["stage_b_benchmarks"] = stage_b_res

	# Stage C
	stage_c_res = stage_c_contention_and_pipeline(exp_dir)
	results["stage_c_pipeline"] = stage_c_res

	results["total_benchmark_duration_s"] = round(time.time() - t0_total, 2)

	# Save results.json
	out_file = exp_dir / "results.json"
	out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
	logger.info("Saved benchmark results to %s in %.2fs", out_file, results["total_benchmark_duration_s"])


if __name__ == "__main__":
	main()
