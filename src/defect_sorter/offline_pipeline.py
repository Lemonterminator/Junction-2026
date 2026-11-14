"""Hardware-free pipeline over the kinematic twin: demonstrations, anomaly crops and closed-loop evaluation.

Three commands share the loop in :mod:`defect_sorter.closed_loop`:

``record``
	Run the scripted expert on twin bricks and save each attempt (both camera streams, joint state, commanded action,
	task text) as compressed NumPy files plus ``index.json``. :mod:`defect_sorter.lerobot_export` converts them to a
	LeRobot v3 dataset for the policy trainer.
``crops``
	Write an Anomalib folder dataset (``train/good``, ``test/good``, ``test/defect``) of brick crops.
``evaluate``
	Run sorting attempts with a chosen inspector (an Anomalib OpenVINO model, or the twin's ground truth to isolate
	the policy) and write ``episodes.jsonl`` and ``summary.json``.

All outputs are twin data, tagged ``source``/``mode`` ``twin``; they are never real results. Example::

	uv run python -m defect_sorter.offline_pipeline record --out data/twin/demos --episodes 40
	uv run python -m defect_sorter.offline_pipeline crops --out data/twin/crops
	uv run --extra anomaly python -m defect_sorter.offline_pipeline evaluate --out artifacts/twin/eval \
		--model artifacts/twin/padim/export/weights/openvino/model.xml
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from defect_sorter.closed_loop import DEFAULT_TASKS, CellObservation, EpisodeRecord, Policy, run_episode
from defect_sorter.inspection import ThresholdInspector
from defect_sorter.twin import STATE_NAMES, STATE_UNITS, ScriptedExpert, TwinCell

logger = logging.getLogger(__name__)

TRAIN_SEED, EVAL_SEED = 0, 100_000
"""Default seed bases; evaluation bricks never reuse training seeds unless asked to."""


class RecordingPolicy:
	"""Wraps a policy and keeps every observation it acted on together with the action it returned."""

	def __init__(self, policy: Policy) -> None:
		self.policy = policy
		self.frames: list[tuple[CellObservation, np.ndarray]] = []

	def reset(self, task: str) -> None:
		self.frames = []
		self.policy.reset(task)

	def act(self, observation: CellObservation) -> np.ndarray:
		action = self.policy.act(observation)
		self.frames.append((observation, np.asarray(action, dtype=np.float32)))
		return action

	def done(self) -> bool:
		return self.policy.done()


def oracle_inspector(cell: TwinCell) -> ThresholdInspector:
	"""Inspector that reads the twin's ground truth; isolates policy errors from detection errors."""
	return ThresholdInspector(
		lambda crop: 1.0 if cell.ground_truth() == "defective" else 0.0, threshold=0.5, model="twin-ground-truth"
	)


def record_episodes(out: Path, episodes: int, seed: int = TRAIN_SEED, max_steps: int = 900) -> dict[str, Any]:
	"""Record expert demonstrations in the twin; the demonstrator knows the true label, like a teleoperator.

	Returns
	-------
	dict
		The index written to ``out/index.json``.
	"""
	out.mkdir(parents=True, exist_ok=True)
	index: dict[str, Any] = {
		"source": "twin",
		"fps": 30,
		"state_names": list(STATE_NAMES),
		"state_units": list(STATE_UNITS),
		"cameras": {},
		"episodes": [],
	}
	for i in range(episodes):
		cell = TwinCell(seed=seed + i)
		policy = RecordingPolicy(ScriptedExpert(cell))
		record = run_episode(
			cell, oracle_inspector(cell), policy, DEFAULT_TASKS, max_steps=max_steps, episode_id=str(i)
		)
		if not policy.frames:
			logger.warning("episode %d produced no frames (%s %s)", i, record.status, record.reason)
			continue
		observations = [obs for obs, _ in policy.frames]
		arrays = {
			"state": np.stack([obs.state for obs in observations]).astype(np.float32),
			"action": np.stack([action for _, action in policy.frames]),
		}
		for camera in observations[0].images:
			arrays[camera] = np.stack([obs.images[camera] for obs in observations])
			index["cameras"][camera] = list(arrays[camera].shape[1:])
		name = f"episode_{i:04d}.npz"
		np.savez_compressed(out / name, **arrays)
		index["episodes"].append(
			{
				"file": name,
				"seed": seed + i,
				"label": record.ground_truth,
				"task": record.task,
				"length": len(observations),
				"success": record.status == "DONE",
				"status": record.status,
				"reason": record.reason,
			}
		)
		logger.info("episode %d: %s, %d frames", i, record.status, len(observations))
	(out / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
	return index


def write_crops(out: Path, n_train: int = 200, n_test: int = 40, seed: int = TRAIN_SEED) -> dict[str, int]:
	"""Write brick crops as an Anomalib folder dataset; test seeds follow the training seeds."""
	plan = [("train/good", False, n_train), ("test/good", False, n_test), ("test/defect", True, n_test)]
	counts: dict[str, int] = {}
	next_seed = seed
	for folder, defective, count in plan:
		(out / folder).mkdir(parents=True, exist_ok=True)
		for i in range(count):
			crop = TwinCell(seed=next_seed, defective=defective).observe().target_crop
			next_seed += 1
			if crop is None:
				raise RuntimeError("a brick on the table must give an inspection crop")
			cv2.imwrite(str(out / folder / f"{i:04d}.png"), cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))
		counts[folder] = count
	return counts


def evaluate(
	episodes: int,
	seed: int = EVAL_SEED,
	inspector_factory: Callable[[TwinCell], ThresholdInspector] = oracle_inspector,
	policy_factory: Callable[[TwinCell], Policy] = ScriptedExpert,
	max_steps: int = 900,
) -> list[EpisodeRecord]:
	"""Run sorting attempts on fresh twin bricks and return their records."""
	records = []
	for i in range(episodes):
		cell = TwinCell(seed=seed + i)
		records.append(
			run_episode(
				cell,
				inspector_factory(cell),
				policy_factory(cell),
				DEFAULT_TASKS,
				max_steps=max_steps,
				episode_id=str(i),
			)
		)
	return records


def summarise(records: list[EpisodeRecord]) -> dict[str, Any]:
	"""Counts by status and reason, correct-sort rate, truth/decision confusion and inspection latency.

	Raises
	------
	ValueError
		When the records come from more than one mode; twin, replay and real results are reported separately.
	"""
	modes = sorted({r.mode for r in records})
	if len(modes) > 1:
		raise ValueError(f"records mix modes {modes}; summarise each mode separately")
	judged = [r.correct_sort for r in records if r.correct_sort is not None]
	inspect_ms = [r.timings_s["inspect"] * 1000 / max(r.inspections, 1) for r in records if "inspect" in r.timings_s]
	return {
		"modes": modes,
		"attempts": len(records),
		"status": dict(Counter(r.status for r in records)),
		"reasons": dict(Counter(r.reason for r in records if r.reason)),
		"correct_sort_rate": sum(judged) / len(judged) if judged else None,
		"confusion": dict(Counter(f"{r.ground_truth}->{r.decision.label if r.decision else 'none'}" for r in records)),
		"mean_inspect_ms": float(np.mean(inspect_ms)) if inspect_ms else None,
		"inspector": sorted({r.decision.model for r in records if r.decision}),
	}


def _openvino_inspector_factory(model: Path, device: str, threshold: float, band: float):
	from defect_sorter.inspection import OpenVinoScorer

	scorer = OpenVinoScorer(model, device)

	def factory(cell: TwinCell) -> ThresholdInspector:
		return ThresholdInspector(scorer, threshold=threshold, band=band, model=scorer.name)

	return factory


def main(argv: list[str] | None = None) -> int:
	"""Command-line entry point; see the module docstring."""
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	sub = parser.add_subparsers(dest="command", required=True)
	rec = sub.add_parser("record", help="record scripted twin demonstrations")
	rec.add_argument("--out", type=Path, required=True)
	rec.add_argument("--episodes", type=int, default=40)
	rec.add_argument("--seed", type=int, default=TRAIN_SEED)
	crops = sub.add_parser("crops", help="write an Anomalib folder dataset of brick crops")
	crops.add_argument("--out", type=Path, required=True)
	crops.add_argument("--train", type=int, default=200)
	crops.add_argument("--test", type=int, default=40)
	crops.add_argument("--seed", type=int, default=TRAIN_SEED)
	ev = sub.add_parser("evaluate", help="run closed-loop attempts in the twin")
	ev.add_argument("--out", type=Path, required=True)
	ev.add_argument("--episodes", type=int, default=20)
	ev.add_argument("--seed", type=int, default=EVAL_SEED)
	ev.add_argument("--model", type=Path, help="Anomalib OpenVINO model.xml; omit to use the twin's ground truth")
	ev.add_argument("--device", default="CPU")
	ev.add_argument("--threshold", type=float, default=0.5)
	ev.add_argument("--band", type=float, default=0.0)
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

	if args.command == "record":
		index = record_episodes(args.out, args.episodes, args.seed)
		ok = sum(e["success"] for e in index["episodes"])
		sys.stdout.write(f"{ok}/{len(index['episodes'])} successful episodes in {args.out}\n")
	elif args.command == "crops":
		sys.stdout.write(json.dumps(write_crops(args.out, args.train, args.test, args.seed)) + "\n")
	else:
		factory = (
			_openvino_inspector_factory(args.model, args.device, args.threshold, args.band)
			if args.model
			else oracle_inspector
		)
		records = evaluate(args.episodes, args.seed, factory)
		args.out.mkdir(parents=True, exist_ok=True)
		with (args.out / "episodes.jsonl").open("w", encoding="utf-8") as stream:
			for record in records:
				stream.write(json.dumps(record.to_dict()) + "\n")
		summary = summarise(records)
		(args.out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
		sys.stdout.write(json.dumps(summary, indent=2) + "\n")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
