"""Tests for defect_sorter.planner: closed action set, deterministic rules, validation and LLM fallback."""

from __future__ import annotations

import json

import pytest

from defect_sorter.planner import (
	Action,
	LLMPlanner,
	PlannerState,
	RulePlanner,
	parse_proposal,
	validate,
)


def state(**kw):
	base = {
		"label": "normal",
		"score": 0.2,
		"threshold": 0.5,
		"inspections": 1,
		"grasp_retries": 0,
		"last_outcome": None,
	}
	base.update(kw)
	return PlannerState(**base)


def test_rules_map_labels_to_fixed_bowls():
	rules = RulePlanner()
	assert rules.decide(state(label="normal")).action is Action.SORT_GREEN
	assert rules.decide(state(label="defective", score=0.9)).action is Action.SORT_PINK


def test_rules_reinspect_uncertain_once_then_skip():
	rules = RulePlanner()
	assert rules.decide(state(label="uncertain", inspections=1)).action is Action.REINSPECT
	assert rules.decide(state(label="uncertain", inspections=2)).action is Action.SKIP_AND_ALERT


def test_rules_retry_a_missed_grasp_once_then_skip():
	rules = RulePlanner()
	assert rules.decide(state(last_outcome="not_grasped")).action is Action.RETRY_GRASP
	assert rules.decide(state(last_outcome="not_grasped", grasp_retries=1)).action is Action.SKIP_AND_ALERT


def test_rules_stop_after_an_arm_fault():
	assert RulePlanner().decide(state(last_outcome="arm_fault")).action is Action.STOP


def test_validate_rejects_overriding_a_confident_label():
	ok, reason = validate(state(label="defective", score=0.9), Action.SORT_GREEN)
	assert not ok
	assert "label" in reason


def test_validate_rejects_a_second_reinspection_and_second_retry():
	assert not validate(state(label="uncertain", inspections=2), Action.REINSPECT)[0]
	assert not validate(state(last_outcome="not_grasped", grasp_retries=1), Action.RETRY_GRASP)[0]


def test_validate_never_allows_motion_after_an_arm_fault():
	for action in (Action.SORT_GREEN, Action.RETRY_GRASP, Action.REINSPECT):
		assert not validate(state(last_outcome="arm_fault"), action)[0]
	assert validate(state(last_outcome="arm_fault"), Action.STOP)[0]


def test_validate_always_allows_stop_and_skip():
	for s in (state(), state(label="uncertain"), state(last_outcome="not_grasped", grasp_retries=1)):
		assert validate(s, Action.STOP)[0]
		assert validate(s, Action.SKIP_AND_ALERT)[0]


def test_parse_proposal_reads_the_json_object_and_rejects_unknown_actions():
	assert parse_proposal('{"action": "REINSPECT", "reason": "score near threshold"}') == (
		Action.REINSPECT,
		"score near threshold",
	)
	assert parse_proposal('noise {"action":"SORT_PINK","reason":"x"} tail')[0] is Action.SORT_PINK
	with pytest.raises(ValueError, match="MOVE_JOINTS"):
		parse_proposal('{"action": "MOVE_JOINTS", "reason": "q=[0,1]"}')
	with pytest.raises(ValueError, match="no JSON"):
		parse_proposal("not json")


def test_llm_planner_uses_a_valid_proposal():
	planner = LLMPlanner(lambda messages: json.dumps({"action": "REINSPECT", "reason": "close to threshold"}))
	d = planner.decide(state(label="uncertain"))
	assert d.action is Action.REINSPECT
	assert d.source == "llm"
	assert d.reason == "close to threshold"


def test_llm_planner_falls_back_to_rules_when_the_proposal_is_rejected():
	planner = LLMPlanner(lambda messages: json.dumps({"action": "SORT_GREEN", "reason": "looks fine"}))
	d = planner.decide(state(label="defective", score=0.95))
	assert d.action is Action.SORT_PINK
	assert d.source == "rules"
	assert "rejected" in d.reason


def test_llm_planner_falls_back_on_errors_and_malformed_output():
	def boom(messages):
		raise TimeoutError("no answer in 3 s")

	assert LLMPlanner(boom).decide(state()).source == "rules"
	assert LLMPlanner(lambda m: "I would sort it green").decide(state()).action is Action.SORT_GREEN


def test_llm_prompt_carries_only_structured_state_and_the_allowed_actions():
	seen = {}

	def capture(messages):
		seen["messages"] = messages
		return json.dumps({"action": "SORT_GREEN", "reason": "normal"})

	LLMPlanner(capture).decide(state())
	system, user = seen["messages"]
	for action in Action:
		assert action.value in system["content"]
	assert json.loads(user["content"])["label"] == "normal"
