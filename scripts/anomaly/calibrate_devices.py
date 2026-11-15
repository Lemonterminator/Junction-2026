"""Choose one threshold per OpenVINO device for a fold model of the real anomaly baseline.

For fold ``i`` the model was fitted without the test fold ``i`` and the validation fold ``i + 1``. Each device scores
the validation crops, ``inspection.choose_threshold`` picks the threshold on those episodes (median of frame
scores), and the test episodes are judged with it. Scores differ by device, so every device gets its own threshold
and its own latency. A device that cannot compile the model is reported, not skipped silently.

Run it where the devices are, with the baseline's ``frames.csv`` and ``crops/`` next to it::

	python calibrate_devices.py --model model.xml --frames frames.csv --fold 0 --devices CPU GPU.0 NPU --out result.json
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
import time
from pathlib import Path

import cv2
import numpy as np

from defect_sorter.inspection import OpenVinoScorer, choose_threshold


def episode_medians(rows: list[dict], scores: list[float]) -> dict[str, tuple[str, float]]:
	"""Episode -> (label, median frame score)."""
	grouped: dict[str, list[float]] = {}
	labels: dict[str, str] = {}
	for row, score in zip(rows, scores, strict=True):
		grouped.setdefault(row["episode"], []).append(score)
		labels[row["episode"]] = row["label"]
	return {ep: (labels[ep], statistics.median(vals)) for ep, vals in grouped.items()}


def calibrate(model_xml: Path, rows: list[dict], root: Path, fold: int, folds: int, device: str) -> dict:
	"""Threshold, test confusion and latency of one device."""
	try:
		scorer = OpenVinoScorer(model_xml, device)
	except Exception as exc:  # a missing or unsupported device is a result
		return {"error": f"{type(exc).__name__}: {exc}"[:300]}
	val_fold = (fold + 1) % folds

	def load(row: dict) -> np.ndarray:
		name = Path(row["path"].replace("\\", "/")).parts[-2:]
		return cv2.cvtColor(cv2.imread(str(root / "crops" / name[0] / name[1])), cv2.COLOR_BGR2RGB)

	picked = [r for r in rows if int(r["fold"]) in (fold, val_fold)]
	images = [load(r) for r in picked]
	for image in images[:5]:
		scorer(image)
	scores, times = [], []
	for image in images:
		start = time.perf_counter()
		scores.append(scorer(image))
		times.append(time.perf_counter() - start)
	val_rows = [r for r in picked if int(r["fold"]) == val_fold]
	test_rows = [r for r in picked if int(r["fold"]) == fold]
	val = episode_medians(val_rows, [s for r, s in zip(picked, scores, strict=True) if int(r["fold"]) == val_fold])
	test = episode_medians(test_rows, [s for r, s in zip(picked, scores, strict=True) if int(r["fold"]) == fold])
	threshold = choose_threshold(
		[s for lab, s in val.values() if lab == "normal"], [s for lab, s in val.values() if lab == "defective"]
	)
	confusion = {"normal->normal": 0, "normal->defective": 0, "defective->defective": 0, "defective->normal": 0}
	for lab, score in test.values():
		confusion[f"{lab}->{'defective' if score >= threshold else 'normal'}"] += 1
	return {
		"threshold": threshold,
		"test_episode_confusion": confusion,
		"test_scores": {ep: {"label": lab, "score": s} for ep, (lab, s) in sorted(test.items())},
		"latency_ms": {
			"median": 1000 * statistics.median(times),
			"p90": 1000 * float(np.percentile(times, 90)),
			"runs": len(times),
		},
	}


def main(argv: list[str] | None = None) -> int:
	"""Write one JSON result with a block per device."""
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("--model", type=Path, required=True)
	parser.add_argument("--frames", type=Path, required=True)
	parser.add_argument("--fold", type=int, default=0)
	parser.add_argument("--folds", type=int, default=5)
	parser.add_argument("--devices", nargs="+", default=["CPU", "GPU.0", "NPU"])
	parser.add_argument("--out", type=Path, required=True)
	args = parser.parse_args(argv)
	with args.frames.open(encoding="utf-8") as stream:
		rows = list(csv.DictReader(stream))
	result = {
		"model": str(args.model),
		"fold": args.fold,
		"devices": {d: calibrate(args.model, rows, args.frames.parent, args.fold, args.folds, d) for d in args.devices},
	}
	args.out.write_text(json.dumps(result, indent=1), encoding="utf-8")
	sys.stdout.write(json.dumps(result["devices"], indent=1)[:4000] + "\n")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
