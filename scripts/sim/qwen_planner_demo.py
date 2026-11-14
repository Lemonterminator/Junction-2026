"""Run the LLM planner against a local OpenAI-compatible server on a fixed set of situations and time each call.

	uv run python scripts/sim/qwen_planner_demo.py --base-url http://127.0.0.1:8000/v1 --model qwen3.8-vllm

Each situation is decided by the rules and by the LLM planner; the table shows the action, whether the LLM proposal
was used or rejected, and the latency. Writes the rows as JSON to ``--out`` when given.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

from defect_sorter.planner import LLMPlanner, PlannerState, RulePlanner, openai_compatible

SITUATIONS = {
	"clear normal": PlannerState("normal", 0.12, 0.5, 1, 0, None),
	"clear defect": PlannerState("defective", 0.93, 0.5, 1, 0, None),
	"uncertain first look": PlannerState("uncertain", 0.49, 0.5, 1, 0, None),
	"uncertain after re-inspection": PlannerState("uncertain", 0.51, 0.5, 2, 0, None),
	"missed grasp": PlannerState("defective", 0.88, 0.5, 1, 0, "not_grasped"),
	"missed grasp twice": PlannerState("defective", 0.88, 0.5, 1, 1, "not_grasped"),
	"placed in wrong bowl": PlannerState("normal", 0.2, 0.5, 1, 0, "placed_wrong"),
	"arm fault": PlannerState("normal", 0.2, 0.5, 1, 0, "arm_fault"),
}


def main(argv: list[str] | None = None) -> int:
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
	parser.add_argument("--model", default="qwen3.8-vllm")
	parser.add_argument("--timeout", type=float, default=10.0)
	parser.add_argument("--repeats", type=int, default=3)
	parser.add_argument("--out", type=Path)
	args = parser.parse_args(argv)
	llm = LLMPlanner(openai_compatible(args.base_url, args.model, args.timeout))
	rules = RulePlanner()
	rows = []
	for name, state in SITUATIONS.items():
		for k in range(args.repeats):
			t0 = time.perf_counter()
			d = llm.decide(state)
			ms = (time.perf_counter() - t0) * 1e3
			rows.append(
				{
					"situation": name,
					"repeat": k,
					"rules": rules.decide(state).action.value,
					"action": d.action.value,
					"source": d.source,
					"reason": d.reason,
					"latency_ms": round(ms, 1),
					"state": asdict(state),
				}
			)
			sys.stdout.write(
				f"{name:32s} rules={rows[-1]['rules']:15s} llm={d.action.value:15s} {d.source:5s} {ms:7.0f} ms  {d.reason}\n"
			)
	if args.out:
		args.out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
