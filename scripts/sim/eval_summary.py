"""Outcome summary of closed-loop sim evaluations (no MuJoCo import, so the local Modal entrypoint can use it)."""

from __future__ import annotations

import json
from pathlib import Path

OUTCOMES = ("correct", "wrong_bowl", "dropped", "never_grasped")


def summarize(results: list[dict]) -> dict:
	"""Outcome counts and rates over finished episodes."""
	n = len(results)
	counts = {k: sum(r["outcome"] == k for r in results) for k in OUTCOMES}
	return {
		"episodes": n,
		"counts": counts,
		"success_rate": counts["correct"] / n if n else None,
		"grasp_rate": sum(r["grasped"] for r in results) / n if n else None,
		"source": "mujoco-sim",
	}


def write_results(out: Path, label: str, results: list[dict]) -> dict:
	"""Write ``<label>.jsonl`` and ``<label>.summary.json`` and return the summary."""
	out.mkdir(parents=True, exist_ok=True)
	with (out / f"{label}.jsonl").open("w", encoding="utf-8") as stream:
		for r in sorted(results, key=lambda r: r["episode"]):
			stream.write(json.dumps(r) + "\n")
	summary = {"label": label, **summarize(results)}
	(out / f"{label}.summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
	return summary
