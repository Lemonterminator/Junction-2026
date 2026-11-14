import json
from dataclasses import dataclass, field

import numpy as np
import pytest

from defect_sorter.closed_loop import (
	DEFAULT_TASKS,
	ArmFaultError,
	CellObservation,
	Outcome,
	intent_for,
	run_episode,
)
from defect_sorter.inspection import DefectDecision, ThresholdInspector

CROP = np.zeros((8, 8, 3), np.uint8)


@dataclass
class FakeCell:
	"""Scripted cell: returns the given crops in order and lands the brick in ``lands_in``."""

	crops: list = field(default_factory=lambda: [CROP])
	lands_in: str | None = "green"
	fault_on_step: int | None = None
	truth: str = "normal"
	mode: str = "test"
	applied: list = field(default_factory=list)
	observed: int = 0

	def observe(self) -> CellObservation:
		crop = self.crops[min(self.observed, len(self.crops) - 1)]
		self.observed += 1
		return CellObservation(frame_id=self.observed, images={}, state=np.zeros(6), target_crop=crop)

	def apply(self, action: np.ndarray) -> None:
		if self.fault_on_step is not None and len(self.applied) == self.fault_on_step:
			raise ArmFaultError("overload")
		self.applied.append(action)

	def outcome(self) -> Outcome:
		return Outcome(bowl=self.lands_in, settled=True)

	def ground_truth(self) -> str:
		return self.truth


class FakePolicy:
	def __init__(self, steps: int = 3) -> None:
		self.steps = steps
		self.tasks: list[str] = []
		self.calls = 0

	def reset(self, task: str) -> None:
		self.tasks.append(task)
		self.calls = 0

	def act(self, observation: CellObservation) -> np.ndarray:
		self.calls += 1
		return np.full(6, float(self.calls))

	def done(self) -> bool:
		return self.calls >= self.steps


def inspector(label: str) -> ThresholdInspector:
	score = {"normal": 0.1, "defective": 0.9, "uncertain": 0.5}[label]
	return ThresholdInspector(lambda crop: score, threshold=0.5, band=0.05, model="fixed")


def test_intent_maps_labels_to_fixed_training_tasks():
	normal = intent_for(DefectDecision("normal", 0.1, 0.5, "m"), DEFAULT_TASKS)
	defective = intent_for(DefectDecision("defective", 0.9, 0.5, "m"), DEFAULT_TASKS)
	assert (normal.bowl, normal.task) == ("green", DEFAULT_TASKS["normal"][1])
	assert (defective.bowl, defective.task) == ("pink", DEFAULT_TASKS["defective"][1])
	assert normal.task != defective.task


def test_intent_for_uncertain_is_none():
	assert intent_for(DefectDecision("uncertain", None, 0.5, "m"), DEFAULT_TASKS) is None


def test_normal_brick_is_sent_with_green_task_and_verified():
	cell, policy = FakeCell(lands_in="green"), FakePolicy(steps=3)
	record = run_episode(cell, inspector("normal"), policy, DEFAULT_TASKS, max_steps=10)
	assert record.status == "DONE"
	assert policy.tasks == [DEFAULT_TASKS["normal"][1]]
	assert len(cell.applied) == 3
	assert record.outcome_bowl == "green"
	assert record.ground_truth == "normal"


def test_defective_brick_gets_pink_task():
	policy = FakePolicy()
	record = run_episode(FakeCell(lands_in="pink", truth="defective"), inspector("defective"), policy, DEFAULT_TASKS)
	assert record.status == "DONE"
	assert policy.tasks == [DEFAULT_TASKS["defective"][1]]


def test_uncertain_reobserves_then_stops_without_moving():
	cell, policy = FakeCell(), FakePolicy()
	record = run_episode(cell, inspector("uncertain"), policy, DEFAULT_TASKS, reobserve_limit=2)
	assert record.status == "UNKNOWN"
	assert record.reason == "uncertain_defect"
	assert cell.observed == 3
	assert policy.tasks == []
	assert cell.applied == []


def test_reobserve_recovers_when_a_later_crop_appears():
	cell, policy = FakeCell(crops=[None, CROP]), FakePolicy()
	record = run_episode(cell, inspector("normal"), policy, DEFAULT_TASKS, reobserve_limit=2)
	assert record.status == "DONE"
	assert record.inspections == 2


def test_wrong_bowl_is_a_failure():
	record = run_episode(FakeCell(lands_in="pink"), inspector("normal"), FakePolicy(), DEFAULT_TASKS)
	assert (record.status, record.reason) == ("FAILED", "wrong_bowl")


def test_brick_left_outside_bowls_is_not_placed():
	record = run_episode(FakeCell(lands_in=None), inspector("normal"), FakePolicy(), DEFAULT_TASKS)
	assert (record.status, record.reason) == ("FAILED", "not_placed")


def test_policy_that_never_finishes_times_out_as_failure():
	cell = FakeCell()
	record = run_episode(cell, inspector("normal"), FakePolicy(steps=100), DEFAULT_TASKS, max_steps=5)
	assert (record.status, record.reason) == ("FAILED", "timeout")
	assert len(cell.applied) == 5


def test_arm_fault_stops_immediately_without_retry():
	cell = FakeCell(fault_on_step=1)
	record = run_episode(cell, inspector("normal"), FakePolicy(steps=5), DEFAULT_TASKS)
	assert record.status == "FAILED"
	assert record.reason == "arm_fault: overload"
	assert len(cell.applied) == 1


def test_record_is_json_serialisable_and_tagged_with_cell_mode():
	record = run_episode(FakeCell(mode="twin"), inspector("normal"), FakePolicy(), DEFAULT_TASKS, episode_id="e1")
	data = json.loads(json.dumps(record.to_dict()))
	assert data["mode"] == "twin"
	assert data["episode_id"] == "e1"
	assert data["decision"]["label"] == "normal"
	assert data["task"] == DEFAULT_TASKS["normal"][1]
	assert data["steps"] == 3
	assert set(data["timings_s"]) >= {"inspect", "execute"}


@pytest.mark.parametrize("label", ["normal", "defective"])
def test_correct_sort_follows_ground_truth_not_decision(label):
	wrong = "defective" if label == "normal" else "normal"
	bowl = DEFAULT_TASKS[wrong][0]
	record = run_episode(FakeCell(lands_in=bowl, truth=label), inspector(wrong), FakePolicy(), DEFAULT_TASKS)
	assert record.status == "DONE"
	assert record.correct_sort is False
