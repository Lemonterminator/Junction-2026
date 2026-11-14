"""One sorting attempt as a state machine over replaceable parts: cell, inspector and policy.

``OBSERVE → INSPECT → PLAN → EXECUTE → VERIFY → DONE / FAILED / UNKNOWN``

The loop only talks to three protocols, so the same code runs against the kinematic twin
(:mod:`defect_sorter.twin`), a replay of recordings, or the real arm once its adapter exists:

* a :class:`Cell` observes (images, joint state, a crop of the target brick), applies actions and reports where the
  brick ended up;
* an inspector (:class:`defect_sorter.inspection.ThresholdInspector`) labels the crop normal, defective or
  uncertain;
* a :class:`Policy` turns the fixed task text into actions until it says it is done.

The defect label is mapped to a fixed task sentence that the policy saw in training (execution plan §4.3); the
policy never interprets an anomaly score. An uncertain inspection is retried by observing again, up to a limit, and
then the attempt stops as ``UNKNOWN`` without any motion. An :class:`ArmFaultError` from the cell ends the attempt at
once: there is no automatic retry of motion. Every record carries the cell's ``mode`` so twin, replay and real
results are never pooled into one success rate.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Literal, Protocol

import numpy as np

from defect_sorter.inspection import DefectDecision, ThresholdInspector

Status = Literal["DONE", "FAILED", "UNKNOWN"]

DEFAULT_TASKS: dict[str, tuple[str, str]] = {
	"normal": ("green", "Pick up the brick and place it in the green bowl."),
	"defective": ("pink", "Pick up the brick and place it in the pink bowl."),
}
"""Defect label → (target bowl, fixed task text). Example mapping until the on-site rule is frozen."""


class ArmFaultError(RuntimeError):
	"""Raised by a cell when the arm reports an error; the loop stops and never retries the motion."""


@dataclass(frozen=True)
class CellObservation:
	"""One observation of the cell.

	Parameters
	----------
	frame_id : int
		Increasing id from the source.
	images : dict of str to ndarray
		Camera images keyed by camera name (``top``, ``wrist``), RGB uint8.
	state : ndarray
		Joint state in the dataset contract order and units.
	target_crop : ndarray or None
		RGB crop of the brick to inspect, or None when no target is visible.
	"""

	frame_id: int
	images: dict[str, np.ndarray]
	state: np.ndarray
	target_crop: np.ndarray | None


@dataclass(frozen=True)
class Outcome:
	"""Where the brick ended up: a bowl name, or None when it is in no bowl; ``settled`` is False if unknown."""

	bowl: str | None
	settled: bool


@dataclass(frozen=True)
class SortIntent:
	"""Target bowl and the fixed task text sent to the policy."""

	label: str
	bowl: str
	task: str


class Cell(Protocol):
	"""Source of observations and sink of actions; ``mode`` names the data source (twin, replay, real)."""

	mode: str

	def observe(self) -> CellObservation: ...

	def apply(self, action: np.ndarray) -> None: ...

	def outcome(self) -> Outcome: ...


class Policy(Protocol):
	"""Action generator conditioned on a task sentence."""

	def reset(self, task: str) -> None: ...

	def act(self, observation: CellObservation) -> np.ndarray: ...

	def done(self) -> bool: ...


@dataclass
class EpisodeRecord:
	"""Everything needed to trace one attempt back to its evidence."""

	episode_id: str
	mode: str
	status: Status = "UNKNOWN"
	reason: str = ""
	decision: DefectDecision | None = None
	inspections: int = 0
	bowl: str | None = None
	task: str | None = None
	steps: int = 0
	outcome_bowl: str | None = None
	ground_truth: str | None = None
	correct_sort: bool | None = None
	timings_s: dict[str, float] = field(default_factory=dict)

	def to_dict(self) -> dict[str, Any]:
		"""JSON-ready dictionary."""
		return asdict(self)


def intent_for(decision: DefectDecision, tasks: dict[str, tuple[str, str]]) -> SortIntent | None:
	"""Fixed task for a normal or defective decision; None for uncertain or an unmapped label."""
	if decision.label not in tasks:
		return None
	bowl, task = tasks[decision.label]
	return SortIntent(decision.label, bowl, task)


def run_episode(
	cell: Cell,
	inspector: ThresholdInspector,
	policy: Policy,
	tasks: dict[str, tuple[str, str]] = DEFAULT_TASKS,
	*,
	max_steps: int = 600,
	reobserve_limit: int = 2,
	episode_id: str = "0",
) -> EpisodeRecord:
	"""Run one attempt and return its record.

	Parameters
	----------
	cell, inspector, policy
		The replaceable parts (see module docstring).
	tasks : dict
		Defect label → (bowl, task text).
	max_steps : int
		Upper bound on applied actions before the attempt counts as ``timeout``.
	reobserve_limit : int
		Extra observations allowed after an uncertain inspection.
	episode_id : str
		Identifier stored in the record.

	Returns
	-------
	EpisodeRecord
		Final status, reason, decision, task, outcome and per-stage wall-clock timings.
	"""
	record = EpisodeRecord(episode_id=episode_id, mode=getattr(cell, "mode", "unknown"))
	truth = getattr(cell, "ground_truth", None)
	record.ground_truth = truth() if callable(truth) else None

	start = time.perf_counter()
	intent: SortIntent | None = None
	for _ in range(reobserve_limit + 1):
		observation = cell.observe()
		record.decision = inspector.inspect(observation.target_crop)
		record.inspections += 1
		intent = intent_for(record.decision, tasks)
		if intent is not None:
			break
	record.timings_s["inspect"] = time.perf_counter() - start
	if intent is None:
		record.status, record.reason = "UNKNOWN", "uncertain_defect"
		return record
	record.bowl, record.task = intent.bowl, intent.task

	start = time.perf_counter()
	policy.reset(intent.task)
	try:
		while record.steps < max_steps and not policy.done():
			cell.apply(policy.act(cell.observe()))
			record.steps += 1
	except ArmFaultError as fault:
		record.timings_s["execute"] = time.perf_counter() - start
		record.status, record.reason = "FAILED", f"arm_fault: {fault}"
		return record
	record.timings_s["execute"] = time.perf_counter() - start
	if not policy.done():
		record.status, record.reason = "FAILED", "timeout"
		return record

	outcome = cell.outcome()
	record.outcome_bowl = outcome.bowl
	if not outcome.settled:
		record.status, record.reason = "UNKNOWN", "outcome_unverified"
	elif outcome.bowl is None:
		record.status, record.reason = "FAILED", "not_placed"
	elif outcome.bowl != intent.bowl:
		record.status, record.reason = "FAILED", "wrong_bowl"
	else:
		record.status = "DONE"
	if record.ground_truth in tasks and outcome.settled:
		record.correct_sort = outcome.bowl == tasks[record.ground_truth][0]
	return record
