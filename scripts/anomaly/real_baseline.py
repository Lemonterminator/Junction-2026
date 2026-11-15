"""Real-data anomaly baseline: wrist crops of held bricks from a sort dataset, grouped 5-fold evaluation.

Labels come from the task text (green bowl = normal brick, pink bowl = defective brick). For each episode the
frames with the gripper closed on the brick are found with ``episodes.find_hold``; evenly spaced wrist frames in
that interval are cut with ``inspection.isolate_object``. Episodes are dealt into 5 folds; for fold i the test
episodes are fold i, the threshold is chosen on fold i+1, and Padim is fitted on the normal episodes of the other
three folds. No frame of a test episode is used for fitting or for the threshold. The colour-purity score
(``off_colour_fraction``) gets the same folds and thresholds, without fitting.

Run from the repository root (``anomaly`` and ``dataset`` extras; on Windows set ``PYTHONUTF8=1``)::

	uv run --extra anomaly --extra dataset python scripts/anomaly/real_baseline.py \\
		data/studio/<dataset id> --out artifacts/anomaly/real-baseline

Everything written goes under ``--out`` (Git-ignored ``artifacts/``): crops, per-frame scores, models, summary.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import shutil
import sys
import time
from pathlib import Path

import cv2
import numpy as np

from defect_sorter.episodes import TASK_BOWLS, find_hold, load_episodes
from defect_sorter.inspection import (
	IsolateConfig,
	OpenVinoScorer,
	choose_threshold,
	grouped_folds,
	isolate_object,
	off_colour_fraction,
	train_padim,
)

logger = logging.getLogger("real_baseline")
LABEL_OF_BOWL = {"green": "normal", "pink": "defective"}
CAMERA = "wrist"
# Wrist camera, 640 x 480: a held brick sits around (392, 362) px with a box side of about 240 px (median over the
# sort-depth-v2 hold frames). The core ellipse is always kept; frames whose brick box is far from this are rejected
# (the bowl or a half-lifted brick instead of the held brick).
ISOLATE = IsolateConfig(core=(392 / 640, 375 / 480, 80 / 640, 75 / 480))
EXPECTED_CENTRE = (392.0, 362.0)
MAX_OFFSET_PX = 70.0
SIDE_RANGE_PX = (150, 360)


def episode_video_spans(root: Path) -> dict[int, tuple[Path, float]]:
	"""Episode index → (wrist video file, start timestamp of the episode in that file)."""
	import pyarrow.parquet as pq

	key = f"videos/observation.images.{CAMERA}/"
	spans = {}
	for path in sorted((root / "meta" / "episodes").glob("*/*.parquet")):
		for row in pq.read_table(path).to_pylist():
			video = (
				root
				/ "videos"
				/ f"observation.images.{CAMERA}"
				/ (f"chunk-{row[key + 'chunk_index']:03d}/file-{row[key + 'file_index']:03d}.mp4")
			)
			spans[int(row["episode_index"])] = (video, float(row[key + "from_timestamp"]))
	return spans


def extract(root: Path, out: Path, frames_per_episode: int, band: tuple[float, float]) -> list[dict]:
	"""Write crops and return one record per kept frame."""
	episodes = load_episodes(root)
	spans = episode_video_spans(root)
	records: list[dict] = []
	captures: dict[Path, cv2.VideoCapture] = {}
	for index, ep in enumerate(episodes):
		bowl = TASK_BOWLS.get(ep.task.strip())
		if bowl is None:
			logger.warning("episode %d: unknown task %r, skipped", index, ep.task)
			continue
		label = LABEL_OF_BOWL[bowl]
		hold = find_hold(ep, band=band, min_s=1.0)
		if hold is None:
			logger.warning("episode %d: no hold found, skipped", index)
			continue
		t = ep.timestamps_s
		start, end = t[hold[0]] + 1.0, t[hold[1]] - 1.5  # after the lift, before the bowl comes into view
		if end <= start:
			start, end = t[hold[0]] + 0.3, t[hold[1]] - 0.3
		video, offset = spans[index]
		cap = captures.setdefault(video, cv2.VideoCapture(str(video)))
		fps = cap.get(cv2.CAP_PROP_FPS)
		kept = rejected = 0
		for when in np.linspace(start, end, frames_per_episode):
			frame_no = round(float(offset + when) * fps)
			cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
			ok, image = cap.read()
			if not ok:
				continue
			obj = isolate_object(image, ISOLATE)
			if obj is None or not plausible_box(obj.box):
				rejected += 1
				continue
			path = out / "crops" / label / f"ep{index:03d}_f{frame_no:06d}.png"
			path.parent.mkdir(parents=True, exist_ok=True)
			cv2.imwrite(str(path), obj.crop)
			records.append(
				{
					"episode": f"ep{index:03d}",
					"label": label,
					"frame": frame_no,
					"path": str(path),
					"area_px": obj.area_px,
					"off_colour": off_colour_fraction(obj.crop, obj.mask),
				}
			)
			kept += 1
		logger.info("episode %d (%s): %d crops, %d frames rejected", index, label, kept, rejected)
	for cap in captures.values():
		cap.release()
	return records


def plausible_box(box: tuple[int, int, int]) -> bool:
	"""True when the brick box matches a brick held between the jaws."""
	x, y, side = box
	off = np.hypot(x + side / 2 - EXPECTED_CENTRE[0], y + side / 2 - EXPECTED_CENTRE[1])
	return off <= MAX_OFFSET_PX and SIDE_RANGE_PX[0] <= side <= SIDE_RANGE_PX[1]


def stage_folder(dest: Path, train: list[dict], val: list[dict]) -> None:
	"""Anomalib Folder layout: train/good from ``train``; test/good and test/defect from ``val``."""
	if dest.exists():
		shutil.rmtree(dest)
	for rec in train:
		target = dest / "train" / "good" / Path(rec["path"]).name
		target.parent.mkdir(parents=True, exist_ok=True)
		shutil.copy(rec["path"], target)
	for rec in val:
		sub = "good" if rec["label"] == "normal" else "defect"
		target = dest / "test" / sub / Path(rec["path"]).name
		target.parent.mkdir(parents=True, exist_ok=True)
		shutil.copy(rec["path"], target)


AGGREGATES = {"median": np.median, "max": np.max}


def episode_scores(records: list[dict], key: str, aggregate: str) -> dict[str, tuple[str, float]]:
	"""Episode → (label, aggregated frame score). ``max`` trusts the single worst view, ``median`` the typical one."""
	frames: dict[str, list[float]] = {}
	labels: dict[str, str] = {}
	for rec in records:
		frames.setdefault(rec["episode"], []).append(float(rec[key]))
		labels[rec["episode"]] = rec["label"]
	return {e: (labels[e], float(AGGREGATES[aggregate](v))) for e, v in frames.items()}


def threshold_on(records: list[dict], key: str, aggregate: str) -> float:
	scores = episode_scores(records, key, aggregate)
	return choose_threshold(
		[s for lab, s in scores.values() if lab == "normal"], [s for lab, s in scores.values() if lab == "defective"]
	)


def frame_auroc(records: list[dict], key: str) -> float | None:
	pos = np.array([r[key] for r in records if r["label"] == "defective"], dtype=float)
	neg = np.array([r[key] for r in records if r["label"] == "normal"], dtype=float)
	if pos.size == 0 or neg.size == 0:
		return None
	greater = (pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()
	return float(greater)


METHODS = [(k, a) for k in ("model_score", "off_colour") for a in AGGREGATES]


def main(argv: list[str] | None = None) -> int:
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("dataset", type=Path)
	parser.add_argument("--out", type=Path, required=True)
	parser.add_argument("--frames", type=int, default=20, help="crops per episode")
	parser.add_argument("--band", type=float, nargs=2, default=(8.5, 26.0), help="gripper reading holding a brick")
	parser.add_argument("--folds", type=int, default=5)
	parser.add_argument("--seed", type=int, default=0)
	parser.add_argument("--model", choices=("padim", "patchcore"), default="padim")
	parser.add_argument("--accelerator", default="cpu", help="Lightning accelerator for fitting: cpu or gpu (CUDA)")
	parser.add_argument("--coreset-ratio", type=float, default=0.1, help="PatchCore memory bank share")
	parser.add_argument("--latency-devices", nargs="*", default=["CPU"])
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
	out: Path = args.out
	out.mkdir(parents=True, exist_ok=True)

	records = extract(args.dataset, out, args.frames, tuple(args.band))
	folds = grouped_folds([r["episode"] for r in records], [r["label"] for r in records], args.folds, args.seed)
	for rec in records:
		rec["fold"] = folds[rec["episode"]]

	results = []
	model_of_fold: dict[int, Path] = {}
	for test_fold in range(args.folds):
		val_fold = (test_fold + 1) % args.folds
		train = [r for r in records if r["fold"] not in (test_fold, val_fold) and r["label"] == "normal"]
		val = [r for r in records if r["fold"] == val_fold]
		test = [r for r in records if r["fold"] == test_fold]
		fold_dir = out / f"fold{test_fold}"
		stage_folder(fold_dir / "data", train, val)
		model_xml = train_padim(
			fold_dir / "data", fold_dir / args.model, args.model, args.accelerator, args.coreset_ratio
		)
		model_of_fold[test_fold] = model_xml
		scorer = OpenVinoScorer(model_xml, "CPU")
		for rec in val + test:
			rec.setdefault("model_scores", {})[test_fold] = scorer(
				cv2.cvtColor(cv2.imread(rec["path"]), cv2.COLOR_BGR2RGB)
			)
		fold_view = {
			"val": [{**r, "model_score": r["model_scores"][test_fold]} for r in val],
			"test": [{**r, "model_score": r["model_scores"][test_fold]} for r in test],
		}
		fold_result = {"fold": test_fold, "val_fold": val_fold, "train_frames": len(train)}
		for key, aggregate in METHODS:
			thr = threshold_on(fold_view["val"], key, aggregate)
			test_eps = episode_scores(fold_view["test"], key, aggregate)
			fold_result[f"{key}/{aggregate}"] = {
				"threshold": thr,
				"episodes": {
					e: {"label": lab, "score": s, "pred": "defective" if s >= thr else "normal"}
					for e, (lab, s) in test_eps.items()
				},
				"frame_auroc_test": frame_auroc(fold_view["test"], key),
			}
		results.append(fold_result)
		logger.info("fold %d done", test_fold)

	summary: dict = {"dataset": str(args.dataset), "camera": CAMERA, "frames": len(records), "episodes": len(folds)}
	for key, aggregate in METHODS:
		name = f"{key}/{aggregate}"
		confusion = {"normal->normal": 0, "normal->defective": 0, "defective->defective": 0, "defective->normal": 0}
		missed, false_alarms = [], []
		for fr in results:
			for ep, row in fr[name]["episodes"].items():
				confusion[f"{row['label']}->{row['pred']}"] += 1
				if row["label"] == "defective" and row["pred"] == "normal":
					missed.append(ep)
				if row["label"] == "normal" and row["pred"] == "defective":
					false_alarms.append(ep)
		summary[name] = {
			"episode_confusion": confusion,
			"missed_defects": sorted(missed),
			"false_alarms": sorted(false_alarms),
			"thresholds": [fr[name]["threshold"] for fr in results],
			"frame_auroc_test_per_fold": [fr[name]["frame_auroc_test"] for fr in results],
		}

	latency = {}
	sample = [cv2.cvtColor(cv2.imread(r["path"]), cv2.COLOR_BGR2RGB) for r in records[:50]]
	for device in args.latency_devices:
		try:
			scorer = OpenVinoScorer(model_of_fold[0], device)
		except Exception as exc:  # a missing device is reported, not fatal
			latency[device] = f"unavailable: {exc}"
			continue
		for img in sample[:5]:
			scorer(img)
		times = []
		for _ in range(4):
			for img in sample:
				t0 = time.perf_counter()
				scorer(img)
				times.append(time.perf_counter() - t0)
		latency[device] = {
			"median_ms": 1000 * float(np.median(times)),
			"p90_ms": 1000 * float(np.percentile(times, 90)),
			"runs": len(times),
		}
	raw = []
	for r in records[:50]:
		image = cv2.imread(r["path"])
		t0 = time.perf_counter()
		off_colour_fraction(image, np.any(image != 128, axis=2))
		raw.append(time.perf_counter() - t0)
	latency["off_colour_cpu"] = {"median_ms": 1000 * float(np.median(raw))}
	summary["latency_model_includes_resize"] = latency

	with (out / "frames.csv").open("w", newline="") as fh:
		writer = csv.DictWriter(
			fh, fieldnames=["episode", "label", "fold", "frame", "area_px", "off_colour", "model_test", "path"]
		)
		writer.writeheader()
		for r in records:
			writer.writerow(
				{k: r[k] for k in ("episode", "label", "fold", "frame", "area_px", "off_colour", "path")}
				| {"model_test": r["model_scores"][r["fold"]]}
			)
	(out / "folds.json").write_text(json.dumps(results, indent=1))
	(out / "summary.json").write_text(json.dumps(summary, indent=1))
	sys.stdout.write(json.dumps(summary, indent=1) + "\n")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
