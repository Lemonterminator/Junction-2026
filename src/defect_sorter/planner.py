"""High-level planner for one brick: a closed action set chosen by rules or by an LLM, always validated.

The inspection result drives the robot: :class:`RulePlanner` maps the label to a fixed action with no person in the
loop. :class:`LLMPlanner` may propose a different action from the same closed set (for example to re-inspect an
uncertain brick or retry a missed grasp), but every proposal goes through :func:`validate`, and anything rejected,
malformed, late or failing falls back to the rules. The LLM never produces joint commands: actions are names that the
loop turns into fixed task texts or into stopping, and the low-level policy keeps its own speed and workspace limits.

Validation rules:

* a confident ``normal`` / ``defective`` label cannot be overridden (sorting must go to the mapped bowl);
* at most one re-inspection and one grasp retry per brick;
* after an arm fault only ``STOP`` is allowed, and nothing here can resume motion;
* ``STOP`` and ``SKIP_AND_ALERT`` are always allowed.

The LLM sees only the structured state below, never camera images or text read from the scene.
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Callable
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Literal

logger = logging.getLogger(__name__)

Outcome = Literal["placed_correct", "placed_wrong", "not_grasped", "arm_fault"] | None
MAX_INSPECTIONS = 2
MAX_GRASP_RETRIES = 1


class Action(StrEnum):
	"""The only things the planner can ask for."""

	SORT_GREEN = "SORT_GREEN"
	SORT_PINK = "SORT_PINK"
	REINSPECT = "REINSPECT"
	RETRY_GRASP = "RETRY_GRASP"
	SKIP_AND_ALERT = "SKIP_AND_ALERT"
	STOP = "STOP"


SORT_FOR_LABEL = {"normal": Action.SORT_GREEN, "defective": Action.SORT_PINK}


@dataclass(frozen=True)
class PlannerState:
	"""What the planner knows about the current brick.

	Parameters
	----------
	label : {"normal", "defective", "uncertain"}
		Latest inspection decision.
	score, threshold : float or None, float
		Anomaly score and the threshold it was compared with.
	inspections : int
		Inspections done for this brick so far.
	grasp_retries : int
		Grasp retries already used for this brick.
	last_outcome : str or None
		Result of the last execution: ``placed_correct``, ``placed_wrong``, ``not_grasped``, ``arm_fault`` or None
		before any execution.
	"""

	label: str
	score: float | None
	threshold: float
	inspections: int
	grasp_retries: int
	last_outcome: Outcome


@dataclass(frozen=True)
class Decision:
	"""The action to take, why, and whether it came from the LLM or the rules."""

	action: Action
	reason: str
	source: Literal["rules", "llm"]


def validate(state: PlannerState, action: Action) -> tuple[bool, str]:
	"""Whether ``action`` is allowed in ``state``; the second item explains a rejection."""
	if action in (Action.STOP, Action.SKIP_AND_ALERT):
		return True, ""
	if state.last_outcome == "arm_fault":
		return False, "arm fault: only STOP is allowed"
	if action in (Action.SORT_GREEN, Action.SORT_PINK):
		expected = SORT_FOR_LABEL.get(state.label)
		if expected is None:
			return False, f"label {state.label!r} does not allow sorting"
		if action is not expected:
			return False, f"label {state.label!r} requires {expected.value}"
		return True, ""
	if action is Action.REINSPECT:
		if state.inspections >= MAX_INSPECTIONS:
			return False, "re-inspection limit reached"
		return True, ""
	if action is Action.RETRY_GRASP:
		if state.last_outcome != "not_grasped":
			return False, "retry only after a missed grasp"
		if state.grasp_retries >= MAX_GRASP_RETRIES:
			return False, "grasp retry limit reached"
		return True, ""
	return False, f"unknown action {action}"


class RulePlanner:
	"""Deterministic planner: the inspection label alone decides."""

	def decide(self, state: PlannerState) -> Decision:
		"""Rule decision for ``state``."""
		if state.last_outcome == "arm_fault":
			return Decision(Action.STOP, "arm fault", "rules")
		if state.last_outcome == "not_grasped":
			if validate(state, Action.RETRY_GRASP)[0]:
				return Decision(Action.RETRY_GRASP, "grasp missed", "rules")
			return Decision(Action.SKIP_AND_ALERT, "grasp missed again", "rules")
		if state.label in SORT_FOR_LABEL:
			return Decision(SORT_FOR_LABEL[state.label], f"label {state.label}", "rules")
		if validate(state, Action.REINSPECT)[0]:
			return Decision(Action.REINSPECT, "uncertain inspection", "rules")
		return Decision(Action.SKIP_AND_ALERT, "still uncertain after re-inspection", "rules")


_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


def parse_proposal(text: str) -> tuple[Action, str]:
	"""Read ``{"action": ..., "reason": ...}`` from model output; raises ValueError if absent or not allowed."""
	match = _JSON_OBJECT.search(text)
	if not match:
		raise ValueError("no JSON object in model output")
	try:
		obj = json.loads(match.group(0))
		return Action(obj["action"]), str(obj.get("reason", ""))[:300]
	except (json.JSONDecodeError, KeyError, TypeError) as exc:
		raise ValueError(f"malformed proposal: {exc}") from exc


SYSTEM_PROMPT = (
	"You supervise a robot arm that sorts Lego bricks. A defect detector has already inspected the brick. "
	"Choose exactly one action from this list: "
	+ ", ".join(a.value for a in Action)
	+ ". SORT_GREEN sends a normal brick to the green bowl, SORT_PINK a defective brick to the pink bowl. "
	"REINSPECT looks at the brick again (use it when the detector is uncertain or the score is close to the "
	"threshold). RETRY_GRASP repeats a missed grasp. SKIP_AND_ALERT stops and calls a person. STOP halts the arm. "
	"Never contradict a confident detector label. Answer with one JSON object only: "
	'{"action": "<one of the list>", "reason": "<one short sentence>"}'
)


def messages_for(state: PlannerState) -> list[dict[str, str]]:
	"""Chat messages for ``state``: the fixed system prompt plus the structured state as JSON."""
	return [
		{"role": "system", "content": SYSTEM_PROMPT},
		{"role": "user", "content": json.dumps(asdict(state))},
	]


class LLMPlanner:
	"""LLM proposes, :func:`validate` disposes, :class:`RulePlanner` covers every failure.

	Parameters
	----------
	complete : callable
		Takes chat messages and returns the model's text. It should enforce its own timeout; any exception it raises
		makes the planner use the rules.
	"""

	def __init__(self, complete: Callable[[list[dict[str, str]]], str]) -> None:
		self.complete = complete
		self.rules = RulePlanner()

	def decide(self, state: PlannerState) -> Decision:
		"""Validated LLM decision, or the rule decision with the reason it was used."""
		try:
			action, reason = parse_proposal(self.complete(messages_for(state)))
		except Exception as exc:
			logger.warning("LLM planner failed (%s); using rules", exc)
			fallback = self.rules.decide(state)
			return Decision(fallback.action, f"{fallback.reason} (LLM failed: {exc})", "rules")
		ok, why = validate(state, action)
		if ok:
			return Decision(action, reason, "llm")
		fallback = self.rules.decide(state)
		logger.info("LLM proposal %s rejected: %s", action.value, why)
		return Decision(fallback.action, f"{fallback.reason} (LLM {action.value} rejected: {why})", "rules")


def openai_compatible(
	base_url: str, model: str, timeout_s: float = 3.0, max_tokens: int = 80
) -> Callable[[list[dict[str, str]]], str]:
	"""A ``complete`` function for an OpenAI-compatible chat endpoint (vLLM, OpenVINO Model Server)."""
	import urllib.request

	if not base_url.startswith(("http://", "https://")):
		raise ValueError(f"planner endpoint must be http(s): {base_url}")

	def complete(messages: list[dict[str, str]]) -> str:
		body = json.dumps(
			{
				"model": model,
				"messages": messages,
				"temperature": 0,
				"max_tokens": max_tokens,
				"response_format": {"type": "json_object"},
				"chat_template_kwargs": {"enable_thinking": False},
			}
		).encode()
		request = urllib.request.Request(  # noqa: S310 - scheme checked above
			f"{base_url.rstrip('/')}/chat/completions", body, {"Content-Type": "application/json"}
		)
		with urllib.request.urlopen(request, timeout=timeout_s) as response:  # noqa: S310
			return json.loads(response.read())["choices"][0]["message"]["content"]

	return complete
