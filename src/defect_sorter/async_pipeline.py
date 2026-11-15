"""Asynchronous inference and inspection pipeline for closed-loop defect sorting.

Connects camera feeds, anomaly inspection, and SmolVLA action-chunk policies through
non-blocking versioned slots (:class:`LatestSlot`) and background worker threads,
allowing real-time sorting loops to run at full camera and execution rates without
stalling on neural network latency.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, NamedTuple, TypeVar

import cv2
import numpy as np

from defect_sorter.closed_loop import (
	DEFAULT_TASKS,
	CellObservation,
	Outcome,
	SortIntent,
	intent_for,
)
from defect_sorter.inspection import DefectDecision, ThresholdInspector, isolate_object
from defect_sorter.planner import Action, PlannerState, RulePlanner

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass(frozen=True)
class SmolVlaManifest:
	"""Pre- and post-processing metadata for SmolVLA policy models.

	Parameters
	----------
	image_resolution : tuple of int
		Target (height, width) for image inputs.
	image_key_reorder_map : dict of str to int
		Mapping of camera names to camera slot indices.
	num_cameras : int
		Total number of camera slots expected by the model.
	state_mean : ndarray
		Mean vector for state normalization (shape: [6]).
	state_std : ndarray
		Standard deviation vector for state normalization (shape: [6]).
	action_mean : ndarray
		Mean vector for action denormalization (shape: [6]).
	action_std : ndarray
		Standard deviation vector for action denormalization (shape: [6]).
	chunk_size : int
		Number of action steps generated per inference chunk.
	action_dim : int
		Dimension of each action vector (e.g. 6 for SO-101 arm).
	noise_shape : tuple of int
		Shape of the diffusion noise tensor (chunk_size, noise_dim).
	max_token_len : int
		Maximum token sequence length for language prompts.
	"""

	image_resolution: tuple[int, int] = (512, 512)
	image_key_reorder_map: dict[str, int] = field(default_factory=dict)
	num_cameras: int = 4
	state_mean: np.ndarray = field(default_factory=lambda: np.zeros(6, dtype=np.float32))
	state_std: np.ndarray = field(default_factory=lambda: np.ones(6, dtype=np.float32))
	action_mean: np.ndarray = field(default_factory=lambda: np.zeros(6, dtype=np.float32))
	action_std: np.ndarray = field(default_factory=lambda: np.ones(6, dtype=np.float32))
	chunk_size: int = 50
	action_dim: int = 6
	noise_shape: tuple[int, int] = (50, 32)
	max_token_len: int = 48

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> SmolVlaManifest:
		"""Parse manifest data dictionary.

		Parameters
		----------
		data : dict
			Dictionary parsed from manifest JSON.

		Returns
		-------
		SmolVlaManifest
			Constructed manifest metadata.
		"""
		image_res = (512, 512)
		reorder_map: dict[str, int] = {}
		num_cams = 4
		state_mean = np.zeros(6, dtype=np.float32)
		state_std = np.ones(6, dtype=np.float32)
		action_mean = np.zeros(6, dtype=np.float32)
		action_std = np.ones(6, dtype=np.float32)
		chunk_sz = 50
		act_dim = 6
		noise_shp = (50, 32)
		max_tokens = 48

		model_dict = data.get("model", {})
		preprocessors = model_dict.get("preprocessors", [])
		for prep in preprocessors:
			ptype = prep.get("type")
			if ptype == "smolvla_resize":
				res = prep.get("image_resolution", [512, 512])
				image_res = (int(res[0]), int(res[1]))
				reorder_map = {str(k): int(v) for k, v in prep.get("image_key_reorder_map", {}).items()}
				num_cams = int(prep.get("num_cameras", len(reorder_map) or 4))
			elif ptype == "normalize":
				st = prep.get("stats", {}).get("state", {})
				if "mean" in st:
					state_mean = np.asarray(st["mean"], dtype=np.float32)
				if "std" in st:
					state_std = np.asarray(st["std"], dtype=np.float32)
			elif ptype == "noise":
				shp = prep.get("shape", [50, 32])
				noise_shp = (int(shp[0]), int(shp[1]))

		postprocessors = model_dict.get("postprocessors", [])
		for post in postprocessors:
			if post.get("type") == "denormalize":
				act = post.get("stats", {}).get("action", {})
				if "mean" in act:
					action_mean = np.asarray(act["mean"], dtype=np.float32)
				if "std" in act:
					action_std = np.asarray(act["std"], dtype=np.float32)

		input_features = model_dict.get("input_features", [])
		for feat in input_features:
			args = feat.get("init_args", feat)
			if args.get("name") == "task" or args.get("ftype") == "LANGUAGE":
				shp = args.get("shape", [48])
				max_tokens = int(shp[0])
			elif args.get("name") == "noise":
				shp = args.get("shape", [50, 32])
				noise_shp = (int(shp[0]), int(shp[1]))

		output_features = model_dict.get("output_features", [])
		for feat in output_features:
			args = feat.get("init_args", feat)
			if args.get("name") == "action" or args.get("ftype") == "ACTION":
				shp = args.get("shape", [50, 6])
				chunk_sz = int(shp[0])
				act_dim = int(shp[1])

		# Fallback to top-level fields if explicitly passed
		if "image_resolution" in data:
			image_res = tuple(data["image_resolution"])
		if "image_key_reorder_map" in data:
			reorder_map = data["image_key_reorder_map"]
		if "num_cameras" in data:
			num_cams = int(data["num_cameras"])
		if "chunk_size" in data:
			chunk_sz = int(data["chunk_size"])
		if "action_dim" in data:
			act_dim = int(data["action_dim"])
		if "noise_shape" in data:
			noise_shp = tuple(data["noise_shape"])
		if "max_token_len" in data:
			max_tokens = int(data["max_token_len"])

		return cls(
			image_resolution=image_res,
			image_key_reorder_map=reorder_map,
			num_cameras=num_cams,
			state_mean=state_mean,
			state_std=state_std,
			action_mean=action_mean,
			action_std=action_std,
			chunk_size=chunk_sz,
			action_dim=act_dim,
			noise_shape=noise_shp,
			max_token_len=max_tokens,
		)

	@classmethod
	def from_json(cls, path_or_str: Path | str) -> SmolVlaManifest:
		"""Load manifest from JSON file or JSON string.

		Parameters
		----------
		path_or_str : Path or str
			File path to manifest.json, or raw JSON text string.

		Returns
		-------
		SmolVlaManifest
			Constructed manifest metadata.
		"""
		p = Path(path_or_str) if isinstance(path_or_str, (str, Path)) else None
		content = p.read_text(encoding="utf-8") if p is not None and p.exists() and p.is_file() else str(path_or_str)
		data = json.loads(content)
		return cls.from_dict(data)


def resize_with_pad_smolvla(
	rgb: np.ndarray,
	target_size: tuple[int, int] = (512, 512),
) -> np.ndarray:
	"""Resize image preserving aspect ratio and pad left/top before scaling.

	Resizes preserving aspect ratio with `ratio = max(w / target_w, h / target_h)`,
	bilinear resizes to `(int(h / ratio), int(w / ratio))`, pads on left and top
	with 0 before scaling `canvas * 2.0 - 1.0`, returning `(3, target_h, target_w)`
	in `float32`.

	Parameters
	----------
	rgb : ndarray
		Input image in RGB order, uint8 in [0, 255] or float32 in [0.0, 1.0].
	target_size : tuple of int, default=(512, 512)
		Target (height, width) dimensions.

	Returns
	-------
	ndarray
		Output array of shape `(3, target_h, target_w)` in float32.
	"""
	h, w = rgb.shape[:2]
	target_h, target_w = target_size
	ratio = max(w / target_w, h / target_h)
	new_h = int(h / ratio)
	new_w = int(w / ratio)

	if new_h == h and new_w == w:
		resized = rgb.astype(np.float32) / 255.0 if rgb.dtype == np.uint8 else rgb.astype(np.float32)
	elif rgb.dtype == np.uint8:
		resized = cv2.resize(rgb, (new_w, new_h), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0
	else:
		resized = cv2.resize(rgb.astype(np.float32), (new_w, new_h), interpolation=cv2.INTER_LINEAR)

	if resized.ndim == 2:
		resized = np.repeat(resized[:, :, None], 3, axis=2)
	elif resized.shape[2] == 1:
		resized = np.repeat(resized, 3, axis=2)

	pad_top = target_h - new_h
	pad_left = target_w - new_w

	canvas = np.zeros((target_h, target_w, 3), dtype=np.float32)
	canvas[pad_top : pad_top + new_h, pad_left : pad_left + new_w] = resized
	scaled = canvas * 2.0 - 1.0
	return np.transpose(scaled, (2, 0, 1)).astype(np.float32)


def prepare_smolvla_inputs(
	images_by_cam: dict[str, np.ndarray],
	state: np.ndarray,
	manifest: SmolVlaManifest,
	tokenized_prompt: np.ndarray,
	tokenized_prompt_mask: np.ndarray,
	noise: np.ndarray | None = None,
) -> dict[str, np.ndarray]:
	"""Order and normalize inputs for OpenVINO SmolVLA inference.

	Parameters
	----------
	images_by_cam : dict of str to ndarray
		Camera images keyed by camera name (e.g. ``top_rgb_v2``, ``wrist``).
	state : ndarray
		Joint state vector of shape `(6,)`.
	manifest : SmolVlaManifest
		Model metadata containing normalization stats and camera slot mapping.
	tokenized_prompt : ndarray
		Tokenized prompt ids of shape `(1, max_token_len)` or `(max_token_len,)`.
	tokenized_prompt_mask : ndarray
		Attention mask of shape `(1, max_token_len)` or `(max_token_len,)`.
	noise : ndarray or None, optional
		Diffusion noise tensor of shape `(1, chunk_size, noise_dim)` or `(chunk_size, noise_dim)`.

	Returns
	-------
	dict of str to ndarray
		OpenVINO input dictionary with keys `images`, `image_masks`, `state`,
		`tokenized_prompt`, `tokenized_prompt_mask`, and `noise`.
	"""
	target_h, target_w = manifest.image_resolution
	images = np.full((manifest.num_cameras, 1, 3, target_h, target_w), -1.0, dtype=np.float32)
	image_masks = np.zeros((manifest.num_cameras, 1), dtype=bool)

	for cam_name, slot_idx in manifest.image_key_reorder_map.items():
		if 0 <= slot_idx < manifest.num_cameras and cam_name in images_by_cam:
			raw_img = images_by_cam[cam_name]
			processed = resize_with_pad_smolvla(raw_img, manifest.image_resolution)
			images[slot_idx, 0] = processed
			image_masks[slot_idx, 0] = True

	state_arr = np.asarray(state, dtype=np.float32).reshape(-1)
	norm_state = (state_arr - manifest.state_mean) / (manifest.state_std + 1e-8)
	norm_state = norm_state.reshape(1, -1).astype(np.float32)

	tok_arr = np.asarray(tokenized_prompt, dtype=np.int64).reshape(1, manifest.max_token_len)
	tok_mask_arr = np.asarray(tokenized_prompt_mask, dtype=bool).reshape(1, manifest.max_token_len)

	if noise is None:
		noise_arr = np.zeros((1, manifest.chunk_size, manifest.noise_shape[1]), dtype=np.float32)
	else:
		noise_arr = np.asarray(noise, dtype=np.float32).reshape(1, manifest.chunk_size, manifest.noise_shape[1])

	return {
		"images": images,
		"image_masks": image_masks,
		"state": norm_state,
		"tokenized_prompt": tok_arr,
		"tokenized_prompt_mask": tok_mask_arr,
		"noise": noise_arr,
	}


def denormalize_smolvla_actions(
	raw_action: np.ndarray,
	manifest: SmolVlaManifest,
) -> np.ndarray:
	"""Denormalize raw policy action output to joint space units.

	Parameters
	----------
	raw_action : ndarray
		Model output tensor of shape `(1, chunk_size, action_dim)` or `(chunk_size, action_dim)`.
	manifest : SmolVlaManifest
		Model metadata containing action mean and standard deviation.

	Returns
	-------
	ndarray
		Denormalized actions of shape `(chunk_size, action_dim)` in float32.
	"""
	raw = np.asarray(raw_action, dtype=np.float32)
	if raw.ndim == 3 and raw.shape[0] == 1:
		raw = raw[0]
	actions = raw * manifest.action_std + manifest.action_mean
	return actions.astype(np.float32)


class SlotItem(NamedTuple):
	"""Versioned container item."""

	version: int
	value: Any


class LatestSlot[T]:
	"""Thread-safe single-element slot with monotonically increasing version numbers.

	Overwrites unread values without blocking, and allows consumers to wake only
	when an item newer than a known version arrives.
	"""

	def __init__(self) -> None:
		self._lock = threading.Lock()
		self._condition = threading.Condition(self._lock)
		self._version: int = 0
		self._value: T | None = None

	@property
	def version(self) -> int:
		"""Latest version index stored in the slot."""
		with self._lock:
			return self._version

	@property
	def latest(self) -> SlotItem | None:
		"""Return (version, value) of the latest item, or None if empty."""
		with self._lock:
			if self._version == 0:
				return None
			return SlotItem(self._version, self._value)

	def put(self, value: T) -> int:
		"""Place value into slot, overwrite previous unread value, and increment version.

		Parameters
		----------
		value : T
			Item to store.

		Returns
		-------
		int
			New version index.
		"""
		with self._condition:
			self._value = value
			self._version += 1
			ver = self._version
			self._condition.notify_all()
			return ver

	def wait_newer(self, last_version: int = 0, timeout_s: float | None = None) -> SlotItem | None:
		"""Wait until an item with version > last_version arrives.

		Parameters
		----------
		last_version : int, default=0
			Last version observed by the caller.
		timeout_s : float or None, optional
			Maximum duration in seconds to wait before returning None.

		Returns
		-------
		SlotItem or None
			Named tuple `(version, value)` if a newer item arrived, or None on timeout.
		"""
		with self._condition:
			if self._version > last_version:
				return SlotItem(self._version, self._value)
			if timeout_s is not None and timeout_s <= 0:
				return None

			def has_newer() -> bool:
				return self._version > last_version

			if not self._condition.wait_for(has_newer, timeout=timeout_s):
				return None
			return SlotItem(self._version, self._value)


@dataclass(frozen=True)
class FramePacket:
	"""Captured camera frame package with timing metadata.

	Parameters
	----------
	frame_id : int
		Monotonically increasing sequence id.
	images : dict of str to ndarray
		RGB camera frames keyed by camera name.
	capture_ms : float
		Duration taken by frame acquisition in milliseconds.
	timestamp_s : float
		Epoch timestamp in seconds when frame was captured.
	"""

	frame_id: int
	images: dict[str, np.ndarray]
	capture_ms: float
	timestamp_s: float


class AsyncFrameSource:
	"""Background worker capturing camera frames into a LatestSlot.

	Parameters
	----------
	fetch_fn : callable
		Zero-argument callable returning a dictionary of RGB images keyed by camera name.
	poll_interval_s : float, default=0.005
		Interval between frame acquisition loops in seconds.
	slot : LatestSlot or None, optional
		Destination slot for captured frames; created if omitted.
	"""

	def __init__(
		self,
		fetch_fn: Callable[[], dict[str, np.ndarray]],
		poll_interval_s: float = 0.005,
		slot: LatestSlot[FramePacket] | None = None,
	) -> None:
		self.fetch_fn = fetch_fn
		self.poll_interval_s = poll_interval_s
		self.slot = slot if slot is not None else LatestSlot[FramePacket]()
		self._running = False
		self._thread: threading.Thread | None = None

	def start(self) -> None:
		"""Start frame acquisition thread."""
		if self._running:
			return
		self._running = True
		self._thread = threading.Thread(target=self._worker_loop, daemon=True)
		self._thread.start()

	def stop(self) -> None:
		"""Stop frame acquisition thread and wait for completion."""
		self._running = False
		if self._thread is not None and self._thread.is_alive():
			self._thread.join(timeout=1.0)
		self._thread = None

	def __enter__(self) -> AsyncFrameSource:
		self.start()
		return self

	def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
		self.stop()

	def _worker_loop(self) -> None:
		frame_counter = 0
		while self._running:
			try:
				t0 = time.perf_counter()
				images = self.fetch_fn()
				capture_ms = (time.perf_counter() - t0) * 1000.0
				frame_counter += 1
				packet = FramePacket(
					frame_id=frame_counter,
					images=images,
					capture_ms=capture_ms,
					timestamp_s=time.time(),
				)
				self.slot.put(packet)
			except Exception as exc:
				logger.warning("Error fetching frame: %s", exc)
			if self.poll_interval_s > 0:
				time.sleep(self.poll_interval_s)


@dataclass(frozen=True)
class InspectionSnapshot:
	"""Inspection and intent decision published for a frame.

	Parameters
	----------
	frame_id : int
		Identifier of the analyzed frame.
	decision : DefectDecision
		Anomaly classification result.
	intent : SortIntent or None
		Resolved sorting intent and task text.
	capture_ms : float
		Frame capture duration in milliseconds.
	inspect_ms : float
		Inspection inference duration in milliseconds.
	total_ms : float
		Total elapsed duration from frame capture to inspection completion in milliseconds.
	timestamp_s : float
		Epoch timestamp in seconds when snapshot was published.
	action : Action or None, optional
		High-level planner action.
	reason : str, default=""
		Decision rationale from planner.
	"""

	frame_id: int
	decision: DefectDecision
	intent: SortIntent | None
	capture_ms: float
	inspect_ms: float
	total_ms: float
	timestamp_s: float
	action: Action | None = None
	reason: str = ""


class AsyncInspectionStage:
	"""Background worker consuming frames and publishing inspection snapshots.

	Parameters
	----------
	frame_source : AsyncFrameSource or LatestSlot
		Frame provider or slot supplying FramePacket objects.
	inspector : ThresholdInspector
		Anomaly detector comparing crop anomaly scores against a threshold.
	planner : RulePlanner or None, optional
		Deterministic action planner; created if omitted.
	tasks : dict of str to tuple of str, default=DEFAULT_TASKS
		Mapping of defect label to (bowl, task text).
	crop_fn : callable or None, optional
		Callable extracting target crop from frame images; uses isolate_object if omitted.
	"""

	def __init__(
		self,
		frame_source: AsyncFrameSource | LatestSlot[FramePacket],
		inspector: ThresholdInspector,
		planner: RulePlanner | None = None,
		tasks: dict[str, tuple[str, str]] = DEFAULT_TASKS,
		crop_fn: Callable[[dict[str, np.ndarray]], np.ndarray | None] | None = None,
	) -> None:
		self.frame_slot = frame_source.slot if isinstance(frame_source, AsyncFrameSource) else frame_source
		self.inspector = inspector
		self.planner = planner if planner is not None else RulePlanner()
		self.tasks = tasks
		self.crop_fn = crop_fn
		self.slot = LatestSlot[InspectionSnapshot]()
		self._running = False
		self._thread: threading.Thread | None = None

	def start(self) -> None:
		"""Start background inspection worker thread."""
		if self._running:
			return
		self._running = True
		self._thread = threading.Thread(target=self._worker_loop, daemon=True)
		self._thread.start()

	def stop(self) -> None:
		"""Stop background inspection worker thread."""
		self._running = False
		if self._thread is not None and self._thread.is_alive():
			self._thread.join(timeout=1.0)
		self._thread = None

	def __enter__(self) -> AsyncInspectionStage:
		self.start()
		return self

	def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
		self.stop()

	def _worker_loop(self) -> None:
		last_version = 0
		while self._running:
			item = self.frame_slot.wait_newer(last_version, timeout_s=0.05)
			if item is None:
				continue
			last_version, packet = item.version, item.value
			t0 = time.perf_counter()

			crop: np.ndarray | None = None
			if self.crop_fn is not None:
				crop = self.crop_fn(packet.images)
			else:
				img = packet.images.get("wrist", packet.images.get("top_rgb_v2", packet.images.get("top")))
				if img is not None:
					try:
						bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) if img.ndim == 3 and img.shape[2] == 3 else img
						isolated = isolate_object(bgr)
						if isolated is not None and isolated.crop is not None:
							crop = cv2.cvtColor(isolated.crop, cv2.COLOR_BGR2RGB)
					except Exception as exc:
						logger.debug("Failed isolating object: %s", exc)
						crop = None

			decision = self.inspector.inspect(crop)
			planner_state = PlannerState(
				label=decision.label,
				score=decision.score,
				threshold=decision.threshold,
				inspections=1,
				grasp_retries=0,
				last_outcome=None,
			)
			plan_decision = self.planner.decide(planner_state)
			intent = intent_for(decision, self.tasks)
			t1 = time.perf_counter()
			inspect_ms = (t1 - t0) * 1000.0
			total_ms = packet.capture_ms + inspect_ms

			snapshot = InspectionSnapshot(
				frame_id=packet.frame_id,
				decision=decision,
				intent=intent,
				capture_ms=packet.capture_ms,
				inspect_ms=inspect_ms,
				total_ms=total_ms,
				timestamp_s=time.time(),
				action=plan_decision.action,
				reason=plan_decision.reason,
			)
			self.slot.put(snapshot)


class DryRunCell:
	"""Cell implementation for dry-run testing and latency benchmarking without hardware.

	Implements the :class:`defect_sorter.closed_loop.Cell` protocol.

	Parameters
	----------
	images : dict of str to ndarray or None, optional
		Synthetic or replay camera frames.
	state : ndarray or None, optional
		Synthetic joint state vector.
	target_crop : ndarray or None, optional
		Synthetic target crop.
	mode : str, default="dry_run"
		Cell mode identifier tag.
	"""

	def __init__(
		self,
		images: dict[str, np.ndarray] | None = None,
		state: np.ndarray | None = None,
		target_crop: np.ndarray | None = None,
		mode: str = "dry_run",
	) -> None:
		self.mode = mode
		self._images = dict(images) if images is not None else {}
		self._state = np.asarray(state if state is not None else np.zeros(6, dtype=np.float32), dtype=np.float32)
		self._target_crop = target_crop
		self._frame_id = 0
		self.applied_actions: list[np.ndarray] = []
		self.applied_timestamps: list[float] = []

	def observe(self) -> CellObservation:
		"""Return current observation without hardware interaction."""
		self._frame_id += 1
		return CellObservation(
			frame_id=self._frame_id,
			images=dict(self._images),
			state=self._state.copy(),
			target_crop=self._target_crop,
		)

	def apply(self, action: np.ndarray) -> None:
		"""Record commanded action without moving hardware.

		Parameters
		----------
		action : ndarray
			Action vector commanded by the policy.
		"""
		self.applied_actions.append(np.asarray(action, dtype=np.float32).copy())
		self.applied_timestamps.append(time.time())

	def outcome(self) -> Outcome:
		"""Return dry run outcome indicating no settled placement."""
		return Outcome(bowl=None, settled=False)


class AsyncChunkPolicy:
	"""Action policy executing action chunks with background prefetching.

	Implements the :class:`defect_sorter.closed_loop.Policy` protocol.
	Prefetches the next action chunk in a background thread once execution reaches
	`prefetch_step`, preventing boundary transition latency.

	Parameters
	----------
	infer_fn : callable
		Callable generating `(chunk_size, 6)` actions given observation and task.
	chunk_size : int, default=50
		Number of steps in each action chunk.
	prefetch_step : int, default=25
		Step index within current chunk that triggers background prefetch of next chunk.
	max_steps : int or None, optional
		Upper bound on total steps before done() returns True.
	"""

	def __init__(
		self,
		infer_fn: Callable[..., np.ndarray | tuple[np.ndarray, Any]],
		chunk_size: int = 50,
		prefetch_step: int = 25,
		max_steps: int | None = None,
	) -> None:
		self.infer_fn = infer_fn
		self.chunk_size = chunk_size
		self.prefetch_step = prefetch_step
		self.max_steps = max_steps
		self.stage_generation: int = 0
		self.task: str = ""

		self._lock = threading.Lock()
		self._current_chunk: np.ndarray | None = None
		self._current_idx: int = 0
		self._next_chunk: np.ndarray | None = None
		self._prefetch_started: bool = False
		self._prefetch_thread: threading.Thread | None = None
		self._prefetch_event = threading.Event()
		self._total_steps_executed: int = 0
		self._done: bool = False

	def reset(self, task: str) -> None:
		"""Reset policy state for a new sorting task.

		Increments `stage_generation` and clears any active or buffered chunks,
		ensuring in-flight prefetch jobs from previous tasks are discarded.

		Parameters
		----------
		task : str
			Fixed task instruction string.
		"""
		# If a background prefetch thread is currently running, wait briefly for it to finish
		# to ensure infer requests are not busy when a new chunk is requested.
		th = self._prefetch_thread
		if th is not None and th.is_alive():
			th.join(timeout=2.0)

		with self._lock:
			self.stage_generation += 1
			self.task = task
			self._current_chunk = None
			self._current_idx = 0
			self._next_chunk = None
			self._prefetch_started = False
			self._prefetch_thread = None
			self._prefetch_event.clear()
			self._total_steps_executed = 0
			self._done = False
			self._next_chunk = None
			self._prefetch_started = False
			self._prefetch_event.clear()
			self._total_steps_executed = 0
			self._done = False

	def done(self) -> bool:
		"""Whether policy has reached completion or maximum steps."""
		with self._lock:
			if self.max_steps is not None and self._total_steps_executed >= self.max_steps:
				return True
			return self._done

	def _call_infer(self, observation: CellObservation, task: str) -> np.ndarray:
		"""Invoke user infer_fn with flexible parameter conventions."""
		if hasattr(self.infer_fn, "infer_chunk"):
			res = self.infer_fn.infer_chunk(observation.images, observation.state, task)
		else:
			try:
				res = self.infer_fn(observation, task)
			except TypeError:
				try:
					res = self.infer_fn(observation.images, observation.state, task)
				except TypeError:
					res = self.infer_fn(observation)

		actions = res[0] if isinstance(res, tuple) else res
		return np.asarray(actions, dtype=np.float32)

	def _prefetch_worker(self, observation: CellObservation, task: str, generation: int) -> None:
		"""Background worker prefetching next action chunk."""
		try:
			chunk = self._call_infer(observation, task)
			with self._lock:
				if self.stage_generation == generation:
					self._next_chunk = chunk
				else:
					logger.debug(
						"Discarded prefetch from stale generation %d (current %d)",
						generation,
						self.stage_generation,
					)
		except Exception as exc:
			logger.warning("Error in background chunk prefetch: %s", exc)
		finally:
			with self._lock:
				if self.stage_generation == generation:
					self._prefetch_event.set()

	def act(self, observation: CellObservation) -> np.ndarray:
		"""Compute or pull next action step for the current observation.

		Parameters
		----------
		observation : CellObservation
			Current cell observation.

		Returns
		-------
		ndarray
			Single action step vector of shape `(6,)`.
		"""
		# Check if current chunk is missing or exhausted
		if self._current_chunk is None:
			if self._prefetch_started:
				self._prefetch_event.wait(timeout=5.0)
				with self._lock:
					if self._next_chunk is not None:
						self._current_chunk = self._next_chunk
						self._next_chunk = None
						self._current_idx = 0
						self._prefetch_started = False

			# If still None (first call or stale prefetch discarded)
			if self._current_chunk is None:
				chunk = self._call_infer(observation, self.task)
				with self._lock:
					self._current_chunk = chunk
					self._current_idx = 0
					self._prefetch_started = False

		# Trigger prefetch if past prefetch_step and not yet running
		with self._lock:
			if self._current_idx >= self.prefetch_step and not self._prefetch_started and self._next_chunk is None:
				self._prefetch_started = True
				self._prefetch_event.clear()
				gen = self.stage_generation
				th = threading.Thread(
					target=self._prefetch_worker,
					args=(observation, self.task, gen),
					daemon=True,
				)
				self._prefetch_thread = th
				th.start()

		# Retrieve action for the current step
		with self._lock:
			action = self._current_chunk[self._current_idx]
			self._current_idx += 1
			self._total_steps_executed += 1

			if self.max_steps is not None and self._total_steps_executed >= self.max_steps:
				self._done = True

			# If current chunk reached end, clear to trigger swap on next act()
			if self._current_idx >= len(self._current_chunk):
				self._current_chunk = None

		return np.asarray(action, dtype=np.float32)


def summarize_latencies(samples_ms: Sequence[float] | np.ndarray) -> dict[str, Any]:
	"""Compute descriptive summary statistics for latency samples in milliseconds.

	Parameters
	----------
	samples_ms : sequence of float or ndarray
		Recorded latency samples in milliseconds.

	Returns
	-------
	dict of str to Any
		Dictionary containing count, min_ms, median_ms, p90_ms, p95_ms, max_ms,
		and mean_ms. If samples_ms is empty, metric values are None.
	"""
	if len(samples_ms) == 0:
		return {
			"count": 0,
			"min_ms": None,
			"median_ms": None,
			"p90_ms": None,
			"p95_ms": None,
			"max_ms": None,
			"mean_ms": None,
		}
	arr = np.asarray(samples_ms, dtype=np.float64)
	return {
		"count": len(arr),
		"min_ms": float(np.min(arr)),
		"median_ms": float(np.median(arr)),
		"p90_ms": float(np.percentile(arr, 90)),
		"p95_ms": float(np.percentile(arr, 95)),
		"max_ms": float(np.max(arr)),
		"mean_ms": float(np.mean(arr)),
	}


def fetch_http_jpeg(url: str, timeout_s: float = 2.0) -> np.ndarray:
	"""Fetch JPEG frame from an HTTP endpoint and decode into RGB uint8 array.

	Parameters
	----------
	url : str
		HTTP endpoint serving raw JPEG bytes.
	timeout_s : float, default=2.0
		Socket timeout in seconds.

	Returns
	-------
	ndarray
		Decoded RGB image array of shape `(H, W, 3)` in uint8.
	"""
	import urllib.request

	if not (url.startswith("http://") or url.startswith("https://")):
		raise ValueError(f"URL must start with http:// or https://: {url}")

	req = urllib.request.Request(url, headers={"User-Agent": "defect-sorter/1.0"})  # noqa: S310
	with urllib.request.urlopen(req, timeout=timeout_s) as resp:  # noqa: S310
		raw_bytes = resp.read()
	buf = np.frombuffer(raw_bytes, dtype=np.uint8)
	bgr = cv2.imdecode(buf, cv2.IMREAD_COLOR)
	if bgr is None:
		raise ValueError(f"Failed to decode JPEG image from {url}")
	return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def load_prompt_tokens(path: Path | str) -> dict[str, tuple[np.ndarray, np.ndarray]]:
	"""Load pre-tokenized language prompts from JSON.

	Parameters
	----------
	path : Path or str
		Path to prompt_tokens.json file.

	Returns
	-------
	dict of str to tuple of ndarray
		Mapping of task text to `(input_ids[1, max_len], attention_mask[1, max_len])`.
	"""
	p = Path(path)
	data = json.loads(p.read_text(encoding="utf-8"))
	results: dict[str, tuple[np.ndarray, np.ndarray]] = {}
	for task, val in data.items():
		if isinstance(val, dict):
			ids = np.asarray(val.get("input_ids", []), dtype=np.int64).reshape(1, -1)
			mask_data = val.get("attention_mask", val.get("tokenized_prompt_mask", val.get("mask", [])))
			mask = np.asarray(mask_data, dtype=bool).reshape(1, -1)
		elif isinstance(val, (list, tuple)) and len(val) >= 2:
			ids = np.asarray(val[0], dtype=np.int64).reshape(1, -1)
			mask = np.asarray(val[1], dtype=bool).reshape(1, -1)
		else:
			raise ValueError(f"Unrecognized prompt tokens format for task {task!r}")
		results[str(task)] = (ids, mask)
	return results


class OpenVinoSmolVlaRunner:
	"""OpenVINO runtime runner for SmolVLA policy models.

	Parameters
	----------
	model_dir : Path or str
		Directory containing smolvla.xml, manifest.json, and tokenizer/prompt tokens.
	device : str, default="CPU"
		OpenVINO target device (e.g. "CPU", "GPU").
	precision_hint : str or None, optional
		Inference precision hint (e.g. "f16" or "f32").
	manifest : SmolVlaManifest or None, optional
		Pre-loaded manifest metadata; loaded from manifest.json if omitted.
	prompt_tokens : dict or None, optional
		Pre-tokenized prompt tokens mapping; loaded from prompt_tokens.json if omitted.
	"""

	def __init__(
		self,
		model_dir: Path | str,
		device: str = "CPU",
		precision_hint: str | None = None,
		manifest: SmolVlaManifest | None = None,
		prompt_tokens: dict[str, tuple[np.ndarray, np.ndarray]] | None = None,
		compiled_model: Any | None = None,
	) -> None:
		self.model_dir = Path(model_dir)
		self.device = device
		self.precision_hint = precision_hint
		self._infer_lock = threading.Lock()

		if manifest is not None:
			self.manifest = manifest
		elif (self.model_dir / "manifest.json").exists():
			self.manifest = SmolVlaManifest.from_json(self.model_dir / "manifest.json")
		else:
			self.manifest = SmolVlaManifest()

		self.prompt_tokens = prompt_tokens
		if self.prompt_tokens is None:
			tokens_file = self.model_dir / "prompt_tokens.json"
			if tokens_file.exists():
				self.prompt_tokens = load_prompt_tokens(tokens_file)

		self.compiled_tokenizer = None
		if self.prompt_tokens is None:
			tok_file = self.model_dir / "tokenizer.xml"
			if tok_file.exists():
				try:
					import openvino as ov
					import openvino_tokenizers  # noqa: F401

					core = ov.Core()
					tok_model = core.read_model(str(tok_file))
					self.compiled_tokenizer = core.compile_model(tok_model, device_name="CPU")
				except Exception as exc:
					logger.warning("Could not load OpenVINO tokenizer: %s", exc)

		if compiled_model is not None:
			self.compiled_model = compiled_model
		else:
			import openvino as ov

			core = ov.Core()
			config: dict[str, str] = {"PERFORMANCE_HINT": "LATENCY"}
			if precision_hint:
				config["INFERENCE_PRECISION_HINT"] = precision_hint.lower()

			xml_path = (
				self.model_dir / "smolvla.xml"
				if (self.model_dir.is_dir() or self.model_dir.suffix != ".xml")
				else self.model_dir
			)
			if xml_path.exists() or not self.model_dir.exists():
				try:
					model = core.read_model(str(xml_path))
					self.compiled_model = core.compile_model(model, device_name=device, config=config)
				except Exception as exc:
					logger.debug("Could not compile OpenVINO model from %s: %s", xml_path, exc)
					self.compiled_model = None
			else:
				self.compiled_model = None

	def infer_chunk(
		self,
		images_by_cam: dict[str, np.ndarray],
		state: np.ndarray,
		task: str,
		noise: np.ndarray | None = None,
	) -> tuple[np.ndarray, dict[str, float]]:
		"""Run one model inference pass to produce a chunk of denormalized actions.

		Parameters
		----------
		images_by_cam : dict of str to ndarray
			Current camera frames keyed by camera name.
		state : ndarray
			Current joint state vector.
		task : str
			Instruction text for the sorting task.
		noise : ndarray or None, optional
			Diffusion noise tensor.

		Returns
		-------
		actions : ndarray
			Denormalized action chunk of shape `(chunk_size, action_dim)`.
		timings : dict of str to float
			Breakdown of preprocess_ms, infer_ms, postprocess_ms, and total_ms.
		"""
		t0 = time.perf_counter()
		tokens: np.ndarray | None = None
		mask: np.ndarray | None = None

		if self.prompt_tokens is not None:
			if task in self.prompt_tokens:
				tokens, mask = self.prompt_tokens[task]
			elif not task.endswith("\n") and f"{task}\n" in self.prompt_tokens:
				tokens, mask = self.prompt_tokens[f"{task}\n"]
			elif task.endswith("\n") and task[:-1] in self.prompt_tokens:
				tokens, mask = self.prompt_tokens[task[:-1]]

		if tokens is None and self.compiled_tokenizer is not None:
			tok_out = self.compiled_tokenizer([task])
			tok_ids = tok_out["input_ids"] if "input_ids" in tok_out else next(iter(tok_out.values()))
			tok_mask = tok_out["attention_mask"] if "attention_mask" in tok_out else np.ones_like(tok_ids, dtype=bool)

			pad_len = self.manifest.max_token_len
			raw_ids = np.asarray(tok_ids, dtype=np.int64).reshape(-1)
			raw_mask = np.asarray(tok_mask, dtype=bool).reshape(-1)
			tokens = np.zeros((1, pad_len), dtype=np.int64)
			mask = np.zeros((1, pad_len), dtype=bool)
			n_copy = min(len(raw_ids), pad_len)
			tokens[0, :n_copy] = raw_ids[:n_copy]
			mask[0, :n_copy] = raw_mask[:n_copy]

		if tokens is None:
			tokens = np.zeros((1, self.manifest.max_token_len), dtype=np.int64)
			mask = np.ones((1, self.manifest.max_token_len), dtype=bool)

		inputs = prepare_smolvla_inputs(
			images_by_cam=images_by_cam,
			state=state,
			manifest=self.manifest,
			tokenized_prompt=tokens,
			tokenized_prompt_mask=mask,
			noise=noise,
		)
		t1 = time.perf_counter()
		preprocess_ms = (t1 - t0) * 1000.0

		t_infer_0 = time.perf_counter()
		if self.compiled_model is not None:
			with self._infer_lock:
				outputs = self.compiled_model(inputs)
			if "action" in outputs:
				raw_action = outputs["action"]
			elif len(outputs) > 0:
				raw_action = next(iter(outputs.values()))
			else:
				raw_action = np.zeros((1, self.manifest.chunk_size, self.manifest.action_dim), dtype=np.float32)
		else:
			raw_action = np.zeros((1, self.manifest.chunk_size, self.manifest.action_dim), dtype=np.float32)
		t_infer_1 = time.perf_counter()
		infer_ms = (t_infer_1 - t_infer_0) * 1000.0

		t_post_0 = time.perf_counter()
		actions = denormalize_smolvla_actions(raw_action, self.manifest)
		t_post_1 = time.perf_counter()
		postprocess_ms = (t_post_1 - t_post_0) * 1000.0
		total_ms = (t_post_1 - t0) * 1000.0

		timings = {
			"preprocess_ms": preprocess_ms,
			"infer_ms": infer_ms,
			"postprocess_ms": postprocess_ms,
			"total_ms": total_ms,
		}
		return actions, timings


def compress_ir_to_fp16(src_xml: Path | str, dst_xml: Path | str) -> Path:
	"""Convert and compress OpenVINO IR model weights to half-precision FP16.

	Parameters
	----------
	src_xml : Path or str
		Source OpenVINO .xml model file path.
	dst_xml : Path or str
		Destination path for the compressed FP16 .xml model file.

	Returns
	-------
	Path
		Path to the saved FP16 model file.
	"""
	import openvino as ov

	core = ov.Core()
	model = core.read_model(str(src_xml))
	dst = Path(dst_xml)
	dst.parent.mkdir(parents=True, exist_ok=True)
	ov.save_model(model, str(dst), compress_to_fp16=True)
	return dst
