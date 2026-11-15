import json
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from defect_sorter.async_pipeline import (
	AsyncChunkPolicy,
	AsyncFrameSource,
	AsyncInspectionStage,
	DryRunCell,
	InspectionSnapshot,
	LatestSlot,
	OpenVinoSmolVlaRunner,
	SmolVlaManifest,
	compress_ir_to_fp16,
	denormalize_smolvla_actions,
	fetch_http_jpeg,
	load_prompt_tokens,
	prepare_smolvla_inputs,
	resize_with_pad_smolvla,
	summarize_latencies,
)
from defect_sorter.closed_loop import CellObservation, Outcome, run_episode
from defect_sorter.inspection import ThresholdInspector
from defect_sorter.planner import Action


def test_manifest_from_dict_and_from_json(tmp_path: Path) -> None:
	sample_dict = {
		"model": {
			"preprocessors": [
				{
					"type": "smolvla_resize",
					"image_resolution": [512, 512],
					"image_key_reorder_map": {
						"top_rgb_v2": 0,
						"wrist": 1,
						"front": 2,
						"top_depth_v2": 3,
					},
					"num_cameras": 4,
				},
				{
					"type": "normalize",
					"stats": {
						"state": {
							"mean": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
							"std": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
						}
					},
				},
				{"type": "noise", "shape": [50, 32]},
			],
			"postprocessors": [
				{
					"type": "denormalize",
					"stats": {
						"action": {
							"mean": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
							"std": [2.0, 2.0, 2.0, 2.0, 2.0, 2.0],
						}
					},
				}
			],
			"input_features": [
				{"init_args": {"name": "task", "shape": [48]}},
				{"init_args": {"name": "noise", "shape": [50, 32]}},
			],
			"output_features": [
				{"init_args": {"name": "action", "shape": [50, 6]}},
			],
		}
	}
	manifest = SmolVlaManifest.from_dict(sample_dict)
	assert manifest.image_resolution == (512, 512)
	assert manifest.image_key_reorder_map == {
		"top_rgb_v2": 0,
		"wrist": 1,
		"front": 2,
		"top_depth_v2": 3,
	}
	assert manifest.num_cameras == 4
	assert manifest.chunk_size == 50
	assert manifest.action_dim == 6
	assert manifest.noise_shape == (50, 32)
	assert manifest.max_token_len == 48
	np.testing.assert_allclose(manifest.state_mean, [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
	np.testing.assert_allclose(manifest.state_std, [0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
	np.testing.assert_allclose(manifest.action_mean, [10.0, 20.0, 30.0, 40.0, 50.0, 60.0])
	np.testing.assert_allclose(manifest.action_std, [2.0, 2.0, 2.0, 2.0, 2.0, 2.0])

	# Test from_json
	json_file = tmp_path / "manifest.json"
	json_file.write_text(json.dumps(sample_dict))
	manifest_loaded = SmolVlaManifest.from_json(json_file)
	assert manifest_loaded.image_resolution == manifest.image_resolution
	assert manifest_loaded.chunk_size == manifest.chunk_size
	np.testing.assert_allclose(manifest_loaded.action_mean, manifest.action_mean)

	# Test real candidate manifest if present
	candidate_path = Path("artifacts/export/sort-depth-v2-10k-candidate/manifest.json")
	if candidate_path.exists():
		cand_manifest = SmolVlaManifest.from_json(candidate_path)
		assert cand_manifest.image_resolution == (512, 512)
		assert cand_manifest.num_cameras == 4
		assert cand_manifest.chunk_size == 50
		assert cand_manifest.action_dim == 6
		assert cand_manifest.max_token_len == 48


def test_resize_with_pad_smolvla_top_rgb() -> None:
	# 416x512x3: ratio = max(512/512, 416/512) = 1.0 -> pad_top = 96, pad_left = 0
	rgb = np.full((416, 512, 3), 255, dtype=np.uint8)
	out = resize_with_pad_smolvla(rgb, (512, 512))

	assert out.shape == (3, 512, 512)
	assert out.dtype == np.float32

	# Top 96 rows must be padded with 0 scaled to -1.0
	np.testing.assert_allclose(out[:, :96, :], -1.0)

	# Bottom 416 rows must be 255 / 255 * 2.0 - 1.0 = 1.0
	np.testing.assert_allclose(out[:, 96:, :], 1.0)


def test_resize_with_pad_smolvla_wrist_front() -> None:
	# 480x640x3: ratio = max(640/512, 480/512) = 1.25 -> resized: 384x512, pad_top = 128, pad_left = 0
	rgb = np.zeros((480, 640, 3), dtype=np.uint8)
	rgb[:, :] = [128, 64, 32]
	out = resize_with_pad_smolvla(rgb, (512, 512))

	assert out.shape == (3, 512, 512)
	assert out.dtype == np.float32

	# Top 128 rows padded with 0 scaled to -1.0
	np.testing.assert_allclose(out[:, :128, :], -1.0)

	# Resized bottom 384 rows should be in [-1.0, 1.0]
	assert np.all(out[:, 128:, :] >= -1.0)
	assert np.all(out[:, 128:, :] <= 1.0)


def test_prepare_smolvla_inputs_and_denormalize() -> None:
	manifest = SmolVlaManifest(
		image_resolution=(512, 512),
		image_key_reorder_map={
			"top_rgb_v2": 0,
			"wrist": 1,
			"front": 2,
			"top_depth_v2": 3,
		},
		num_cameras=4,
		state_mean=np.array([10.0, 20.0, 30.0, 40.0, 50.0, 60.0], dtype=np.float32),
		state_std=np.array([2.0, 4.0, 5.0, 10.0, 20.0, 25.0], dtype=np.float32),
		action_mean=np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], dtype=np.float32),
		action_std=np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0], dtype=np.float32),
		chunk_size=50,
		action_dim=6,
		noise_shape=(50, 32),
		max_token_len=48,
	)

	top_rgb = np.full((416, 512, 3), 128, dtype=np.uint8)
	wrist = np.full((480, 640, 3), 200, dtype=np.uint8)
	# Omit front and top_depth_v2 to test missing camera slots
	images_by_cam = {"top_rgb_v2": top_rgb, "wrist": wrist}
	state = np.array([12.0, 24.0, 25.0, 50.0, 70.0, 35.0], dtype=np.float32)
	tokenized_prompt = np.ones((1, 48), dtype=np.int64)
	tokenized_prompt_mask = np.ones((1, 48), dtype=bool)

	inputs = prepare_smolvla_inputs(
		images_by_cam=images_by_cam,
		state=state,
		manifest=manifest,
		tokenized_prompt=tokenized_prompt,
		tokenized_prompt_mask=tokenized_prompt_mask,
	)

	images = inputs["images"]
	image_masks = inputs["image_masks"]
	norm_state = inputs["state"]

	assert images.shape == (4, 1, 3, 512, 512)
	assert image_masks.shape == (4, 1)
	assert bool(image_masks[0, 0])  # top_rgb_v2 present
	assert bool(image_masks[1, 0])  # wrist present
	assert not bool(image_masks[2, 0])  # front missing
	assert not bool(image_masks[3, 0])  # top_depth_v2 missing

	# Missing camera slots filled with -1.0
	np.testing.assert_allclose(images[2, 0], -1.0)
	np.testing.assert_allclose(images[3, 0], -1.0)

	# State normalized: (state - mean) / (std + 1e-8)
	expected_state = (state - manifest.state_mean) / (manifest.state_std + 1e-8)
	np.testing.assert_allclose(norm_state[0], expected_state, atol=1e-5)

	# Denormalize action round-trip
	target_actions = np.random.randn(50, 6).astype(np.float32)
	norm_actions = (target_actions - manifest.action_mean) / (manifest.action_std + 1e-8)
	recovered = denormalize_smolvla_actions(norm_actions, manifest)
	np.testing.assert_allclose(recovered, target_actions, atol=1e-5)

	# Shape (1, 50, 6) input to denormalize_smolvla_actions
	recovered_batch = denormalize_smolvla_actions(norm_actions.reshape(1, 50, 6), manifest)
	assert recovered_batch.shape == (50, 6)
	np.testing.assert_allclose(recovered_batch, target_actions, atol=1e-5)


def test_latest_slot() -> None:
	slot = LatestSlot[str]()
	assert slot.version == 0
	assert slot.latest is None

	# Non-blocking put overwrites stale item and increments version
	v1 = slot.put("apple")
	assert v1 == 1
	assert slot.version == 1

	v2 = slot.put("banana")
	assert v2 == 2
	assert slot.version == 2

	# wait_newer with last_version=0 returns newest item immediately
	res = slot.wait_newer(last_version=0, timeout_s=0.5)
	assert res is not None
	ver, val = res
	assert ver == 2
	assert val == "banana"

	# wait_newer with current version times out and returns None
	assert slot.wait_newer(last_version=2, timeout_s=0.05) is None

	# Cross-thread wake-up
	def background_put() -> None:
		time.sleep(0.05)
		slot.put("cherry")

	th = threading.Thread(target=background_put)
	th.start()
	woken = slot.wait_newer(last_version=2, timeout_s=1.0)
	th.join()
	assert woken is not None
	assert woken[0] == 3
	assert woken[1] == "cherry"


def test_async_frame_source_and_inspection_stage() -> None:
	frame_counter = 0

	def fake_fetch() -> dict[str, np.ndarray]:
		nonlocal frame_counter
		frame_counter += 1
		# Mock top camera image
		return {"top_rgb_v2": np.full((100, 100, 3), 100, dtype=np.uint8)}

	source = AsyncFrameSource(fetch_fn=fake_fetch, poll_interval_s=0.01)
	inspector = ThresholdInspector(lambda crop: 0.1, threshold=0.5)

	stage = AsyncInspectionStage(
		frame_source=source,
		inspector=inspector,
		crop_fn=lambda imgs: np.zeros((32, 32, 3), dtype=np.uint8),
	)

	with source, stage:
		# Wait for at least one inspection snapshot
		snapshot_item = stage.slot.wait_newer(last_version=0, timeout_s=1.0)
		assert snapshot_item is not None
		_ver, snapshot = snapshot_item
		assert isinstance(snapshot, InspectionSnapshot)
		assert snapshot.frame_id >= 1
		assert snapshot.decision.label == "normal"
		assert snapshot.intent is not None
		assert snapshot.intent.bowl == "green"
		assert snapshot.action == Action.SORT_GREEN
		assert snapshot.capture_ms >= 0.0
		assert snapshot.inspect_ms >= 0.0
		assert snapshot.total_ms >= 0.0
		assert snapshot.timestamp_s > 0.0


def test_dry_run_cell() -> None:
	cell = DryRunCell(
		images={"wrist": np.zeros((480, 640, 3), dtype=np.uint8)},
		state=np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], dtype=np.float32),
	)
	assert cell.mode == "dry_run"

	obs = cell.observe()
	assert isinstance(obs, CellObservation)
	assert "wrist" in obs.images
	np.testing.assert_allclose(obs.state, [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])

	cell.apply(np.ones(6, dtype=np.float32))
	cell.apply(np.zeros(6, dtype=np.float32))

	assert len(cell.applied_actions) == 2
	assert len(cell.applied_timestamps) == 2

	outcome = cell.outcome()
	assert isinstance(outcome, Outcome)
	assert outcome.bowl is None
	assert outcome.settled is False


def test_async_chunk_policy_prefetch_and_timing() -> None:
	infer_calls = 0

	def slow_infer(obs: CellObservation, task: str) -> np.ndarray:
		nonlocal infer_calls
		infer_calls += 1
		time.sleep(0.025)  # 25 ms inference simulation
		return np.full((50, 6), infer_calls, dtype=np.float32)

	policy = AsyncChunkPolicy(
		infer_fn=slow_infer,
		chunk_size=50,
		prefetch_step=25,
	)
	policy.reset("Pick up the brick and place it in the green bowl.")
	assert policy.stage_generation == 1

	dummy_obs = CellObservation(
		frame_id=1,
		images={},
		state=np.zeros(6, dtype=np.float32),
		target_crop=None,
	)

	# Step 0: Initial synchronous infer call
	a0 = policy.act(dummy_obs)
	assert a0.shape == (6,)
	assert infer_calls == 1

	# Steps 1 to 24: using current chunk
	for _ in range(1, 25):
		policy.act(dummy_obs)
	assert infer_calls == 1

	# Step 25: triggers background prefetch
	policy.act(dummy_obs)

	# Allow the background prefetch thread (25 ms) to complete
	time.sleep(0.04)
	assert infer_calls == 2

	# Steps 26 to 49
	for _ in range(26, 50):
		policy.act(dummy_obs)

	# Step 50: chunk boundary switch to prefetched chunk
	t0 = time.perf_counter()
	a50 = policy.act(dummy_obs)
	boundary_ms = (time.perf_counter() - t0) * 1000.0

	assert a50.shape == (6,)
	# Value should match the second chunk
	np.testing.assert_allclose(a50, 2.0)
	# Chunk boundary transition must not block on 25ms inference
	assert boundary_ms < 10.0


def test_async_chunk_policy_stage_generation_stale_discard() -> None:
	task_a_event = threading.Event()
	infer_task_executed: list[str] = []

	def blocking_infer(obs: CellObservation, task: str) -> np.ndarray:
		infer_task_executed.append(task)
		if task == "task_A":
			task_a_event.wait(timeout=2.0)
			return np.full((50, 6), 111.0, dtype=np.float32)
		return np.full((50, 6), 222.0, dtype=np.float32)

	policy = AsyncChunkPolicy(
		infer_fn=blocking_infer,
		chunk_size=50,
		prefetch_step=25,
	)

	# Start on task_A
	policy.reset("task_A")
	assert policy.stage_generation == 1

	dummy_obs = CellObservation(
		frame_id=1,
		images={},
		state=np.zeros(6, dtype=np.float32),
		target_crop=None,
	)

	# Unblock first sync inference for task_A
	task_a_event.set()
	for _ in range(25):
		policy.act(dummy_obs)

	# Reset event so the prefetch will block inside worker
	task_a_event.clear()

	# Step 25 triggers prefetch of next task_A chunk in background
	policy.act(dummy_obs)

	# While task_A prefetch is in flight, reset to task_B
	policy.reset("task_B")
	assert policy.stage_generation == 2

	# Now unblock task_A worker
	task_a_event.set()
	time.sleep(0.02)

	# The first act on task_B must execute task_B and NOT use the stale task_A chunk
	a_b0 = policy.act(dummy_obs)
	np.testing.assert_allclose(a_b0, 222.0)


def test_async_chunk_policy_closed_loop_compatibility() -> None:
	cell = DryRunCell(
		images={"wrist": np.zeros((10, 10, 3), dtype=np.uint8)},
		state=np.zeros(6, dtype=np.float32),
		target_crop=np.zeros((10, 10, 3), dtype=np.uint8),
	)
	inspector = ThresholdInspector(lambda crop: 0.1, threshold=0.5)

	def dummy_infer(obs: CellObservation, task: str) -> np.ndarray:
		return np.zeros((50, 6), dtype=np.float32)

	policy = AsyncChunkPolicy(infer_fn=dummy_infer, chunk_size=50, prefetch_step=25, max_steps=5)

	record = run_episode(cell=cell, inspector=inspector, policy=policy, max_steps=5)
	assert record.steps == 5
	assert len(cell.applied_actions) == 5


def test_summarize_latencies() -> None:
	# Empty sequence
	empty_stats = summarize_latencies([])
	assert empty_stats["count"] == 0
	assert empty_stats["min_ms"] is None
	assert empty_stats["median_ms"] is None
	assert empty_stats["p90_ms"] is None
	assert empty_stats["p95_ms"] is None
	assert empty_stats["max_ms"] is None
	assert empty_stats["mean_ms"] is None

	# Sequence of values
	samples = [10.0, 20.0, 30.0, 40.0, 50.0]
	stats = summarize_latencies(samples)
	assert stats["count"] == 5
	assert stats["min_ms"] == 10.0
	assert stats["median_ms"] == 30.0
	assert stats["max_ms"] == 50.0
	assert stats["mean_ms"] == 30.0
	assert stats["p90_ms"] == pytest.approx(46.0)
	assert stats["p95_ms"] == pytest.approx(48.0)


def test_load_prompt_tokens(tmp_path: Path) -> None:
	data = {
		"pick_green": {
			"input_ids": [1] * 48,
			"attention_mask": [1] * 48,
		},
		"pick_pink": [
			[2] * 48,
			[1] * 48,
		],
	}
	json_path = tmp_path / "prompt_tokens.json"
	json_path.write_text(json.dumps(data))

	tokens = load_prompt_tokens(json_path)
	assert "pick_green" in tokens
	assert "pick_pink" in tokens

	ids_green, mask_green = tokens["pick_green"]
	assert ids_green.shape == (1, 48)
	assert mask_green.shape == (1, 48)
	assert ids_green[0, 0] == 1
	assert bool(mask_green[0, 0])


def test_fetch_http_jpeg() -> None:
	# Create synthetic JPEG in memory using OpenCV
	import cv2

	img = np.full((100, 100, 3), 123, dtype=np.uint8)
	ok, encoded = cv2.imencode(".jpg", img)
	assert ok
	raw_bytes = encoded.tobytes()

	with patch("urllib.request.urlopen") as mock_urlopen:
		mock_resp = MagicMock()
		mock_resp.read.return_value = raw_bytes
		mock_urlopen.return_value.__enter__.return_value = mock_resp

		result = fetch_http_jpeg("http://127.0.0.1:8080/jpeg/top")
		assert result.shape == (100, 100, 3)
		assert result.dtype == np.uint8
		# Color preserved
		np.testing.assert_allclose(result[0, 0], [123, 123, 123])


def test_openvino_smolvla_runner_mock() -> None:
	pytest.importorskip("openvino", reason="needs the anomaly extra")
	manifest = SmolVlaManifest(
		image_resolution=(512, 512),
		image_key_reorder_map={"top": 0},
		num_cameras=1,
		chunk_size=50,
		action_dim=6,
		max_token_len=48,
	)

	prompt_tokens = {"task1": (np.zeros((1, 48), dtype=np.int64), np.ones((1, 48), dtype=bool))}

	# Create a runner with mocked OpenVINO core/model
	with patch("openvino.Core") as mock_core_cls:
		mock_core = MagicMock()
		mock_core_cls.return_value = mock_core
		mock_compiled = MagicMock()
		mock_core.compile_model.return_value = mock_compiled

		# Mock output from compiled model: (1, 50, 6)
		mock_compiled.return_value = {"action": np.zeros((1, 50, 6), dtype=np.float32)}

		runner = OpenVinoSmolVlaRunner(
			model_dir="fake_dir",
			device="CPU",
			manifest=manifest,
			prompt_tokens=prompt_tokens,
		)

		images = {"top": np.zeros((416, 512, 3), dtype=np.uint8)}
		state = np.zeros(6, dtype=np.float32)

		actions, timings = runner.infer_chunk(images, state, "task1")
		assert actions.shape == (50, 6)
		assert "preprocess_ms" in timings
		assert "infer_ms" in timings
		assert "postprocess_ms" in timings
		assert "total_ms" in timings


def test_compress_ir_to_fp16(tmp_path: Path) -> None:
	pytest.importorskip("openvino", reason="needs the anomaly extra")
	src_xml = tmp_path / "src.xml"
	dst_xml = tmp_path / "dst.xml"
	src_xml.write_text("<net></net>")

	with patch("openvino.Core") as mock_core_cls, patch("openvino.save_model") as mock_save:
		mock_core = MagicMock()
		mock_core_cls.return_value = mock_core
		mock_model = MagicMock()
		mock_core.read_model.return_value = mock_model

		out_path = compress_ir_to_fp16(src_xml, dst_xml)
		assert out_path == dst_xml
		mock_save.assert_called_once_with(mock_model, str(dst_xml), compress_to_fp16=True)


def test_async_inspection_stage_default_crop_bgr_rgb_conversion() -> None:
	# Verify that AsyncInspectionStage converts RGB->BGR for isolate_object and BGR->RGB for inspector
	from defect_sorter.inspection import IsolatedObject

	mock_isolated = IsolatedObject(
		crop=np.full((32, 32, 3), 200, dtype=np.uint8),
		mask=np.ones((32, 32), dtype=bool),
		box=(0, 0, 32),
		area_px=1000,
	)

	seen_crop: list[np.ndarray] = []

	def record_crop(crop: np.ndarray | None) -> float:
		if crop is not None:
			seen_crop.append(crop)
		return 0.1

	inspector = ThresholdInspector(record_crop, threshold=0.5)

	# Red frame in RGB: (255, 0, 0)
	red_rgb = np.zeros((100, 100, 3), dtype=np.uint8)
	red_rgb[:, :, 0] = 255

	def fake_fetch() -> dict[str, np.ndarray]:
		return {"wrist": red_rgb}

	source = AsyncFrameSource(fetch_fn=fake_fetch, poll_interval_s=0.01)

	with patch("defect_sorter.async_pipeline.isolate_object") as mock_isolate:
		mock_isolate.return_value = mock_isolated
		stage = AsyncInspectionStage(
			frame_source=source,
			inspector=inspector,
			crop_fn=None,  # Exercise default branch
		)

		with source, stage:
			snapshot_item = stage.slot.wait_newer(last_version=0, timeout_s=1.0)
			assert snapshot_item is not None

		# Verify isolate_object was passed BGR: blue channel is index 0, red is index 2
		assert mock_isolate.called
		passed_bgr = mock_isolate.call_args[0][0]
		assert passed_bgr.shape == (100, 100, 3)
		assert passed_bgr[0, 0, 2] == 255  # Red in BGR is channel 2
		assert passed_bgr[0, 0, 0] == 0  # Blue in BGR is channel 0

		# Verify inspector received RGB array
		assert len(seen_crop) > 0
		assert seen_crop[0].shape == (32, 32, 3)


def test_openvino_smolvla_runner_task_newline_normalization() -> None:
	pytest.importorskip("openvino", reason="needs the anomaly extra")
	manifest = SmolVlaManifest(
		image_resolution=(512, 512),
		image_key_reorder_map={"wrist": 0},
		num_cameras=1,
		chunk_size=50,
		action_dim=6,
		max_token_len=48,
	)

	# prompt_tokens stored with trailing newline
	prompt_tokens = {
		"Pick up the brick and place it in the green bowl.\n": (
			np.full((1, 48), 123, dtype=np.int64),
			np.ones((1, 48), dtype=bool),
		)
	}

	with patch("openvino.Core") as mock_core_cls:
		mock_core = MagicMock()
		mock_core_cls.return_value = mock_core
		mock_compiled = MagicMock()
		mock_core.compile_model.return_value = mock_compiled
		mock_compiled.return_value = {"action": np.zeros((1, 50, 6), dtype=np.float32)}

		runner = OpenVinoSmolVlaRunner(
			model_dir="fake_dir",
			device="CPU",
			manifest=manifest,
			prompt_tokens=prompt_tokens,
		)

		images = {"wrist": np.zeros((480, 640, 3), dtype=np.uint8)}
		state = np.zeros(6, dtype=np.float32)

		# Query without trailing newline should match
		actions, _ = runner.infer_chunk(images, state, "Pick up the brick and place it in the green bowl.")
		assert actions.shape == (50, 6)
		# Verify that input tokenized_prompt matched 123
		call_inputs = mock_compiled.call_args[0][0]
		assert call_inputs["tokenized_prompt"][0, 0] == 123


def test_async_chunk_policy_reset_waits_for_in_flight_prefetch():
	import time

	def slow_infer(obs, task):
		time.sleep(0.05)
		return np.ones((10, 6), dtype=np.float32)

	policy = AsyncChunkPolicy(infer_fn=slow_infer, chunk_size=10, prefetch_step=2)
	policy.reset("task1")

	obs = CellObservation(images={}, state=np.zeros(6, dtype=np.float32), frame_id=0, target_crop=None)
	policy.act(obs)
	policy.act(obs)
	policy.act(obs)  # step index 2, triggers prefetch thread
	assert policy._prefetch_started is True

	t0 = time.perf_counter()
	policy.reset("task2")
	elapsed = time.perf_counter() - t0
	assert elapsed >= 0.02
	assert policy.stage_generation == 2
	assert policy._prefetch_started is False

	action = policy.act(obs)
	assert action.shape == (6,)
