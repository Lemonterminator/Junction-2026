"""Convert recorded episodes (``offline_pipeline record`` output) into a LeRobot v3 dataset.

Runs inside the pinned Studio backend environment, which provides ``lerobot`` 0.6; the root environment only uses
:func:`lerobot_features`. Images are stored as image features by default, so no video encoder is needed; ``--video``
stores them as encoded video like Studio recordings, so the result has the same feature types as a real dataset and
the two can be trained together. ``--robot-type`` sets the dataset's robot type (Studio writes ``SO101_Follower``).
Per-frame privileged labels of simulated episodes (``phase``, ``defect_px``, ``brick_px``) are not dataset features,
so sim and real datasets keep the same features; they go to ``meta/privileged.parquet``, keyed by the dataset's
``episode_index``, ``frame_index`` and global ``index``. The recording's provenance (``source``, e.g. ``mujoco-sim``)
is copied to ``meta/source.json`` so a simulated dataset stays tagged.
Only successful episodes are written unless ``--include-failures`` is given. The output directory must not exist::

	uv run --project external/physical-ai-studio/application/backend --extra cuda --frozen \
		python src/defect_sorter/lerobot_export.py data/twin/demos data/twin/lerobot --repo-id local/twin-sorting
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def lerobot_features(index: dict[str, Any], video: bool = False) -> dict[str, dict[str, Any]]:
	"""LeRobot feature specification for a recording index (state/action names and camera shapes).

	With ``video`` the cameras are declared as video features, as in Studio recordings.
	"""
	names = list(index["state_names"])
	vector = {"dtype": "float32", "shape": (len(names),), "names": names}
	features: dict[str, dict[str, Any]] = {"observation.state": dict(vector), "action": dict(vector)}
	for camera, shape in index["cameras"].items():
		features[f"observation.images.{camera}"] = {
			"dtype": "video" if video else "image",
			"shape": tuple(shape),
			"names": ["height", "width", "channels"],
		}
	return features


PRIVILEGED = ("phase", "defect_px", "brick_px")


def privileged_rows(data: Any, episode_index: int, first_index: int, length: int) -> dict[str, list[int]]:
	"""Columns of privileged per-frame labels for one episode, aligned with the dataset's frame indices.

	Returns an empty dict when the recording has none of :data:`PRIVILEGED`.
	"""
	keys = [k for k in PRIVILEGED if k in data]
	if not keys:
		return {}
	rows: dict[str, list[int]] = {
		"episode_index": [episode_index] * length,
		"frame_index": list(range(length)),
		"index": list(range(first_index, first_index + length)),
	}
	for k in keys:
		rows[k] = [int(v) for v in data[k][:length]]
	return rows


def export(
	record_dir: Path,
	out: Path,
	repo_id: str,
	include_failures: bool = False,
	video: bool = False,
	robot_type: str = "so101_follower",
) -> int:
	"""Write the episodes under ``record_dir`` to a new LeRobot dataset at ``out``; returns the episode count."""
	import numpy as np
	from lerobot.datasets.lerobot_dataset import LeRobotDataset

	if out.exists():
		raise FileExistsError(f"refusing to replace existing dataset: {out}")
	index = json.loads((record_dir / "index.json").read_text(encoding="utf-8"))
	dataset = LeRobotDataset.create(
		repo_id=repo_id,
		fps=index["fps"],
		features=lerobot_features(index, video=video),
		root=out,
		robot_type=robot_type,
		use_videos=video,
		image_writer_threads=8,
	)
	written = 0
	frames_written = 0
	privileged: dict[str, list[int]] = {}
	for entry in index["episodes"]:
		if not entry["success"] and not include_failures:
			continue
		with np.load(record_dir / entry["file"]) as archive:
			data = {key: archive[key] for key in archive.files}
		for t in range(entry["length"]):
			frame = {"observation.state": data["state"][t], "action": data["action"][t], "task": entry["task"]}
			for camera in index["cameras"]:
				frame[f"observation.images.{camera}"] = data[camera][t]
			dataset.add_frame(frame)
		dataset.save_episode()
		for k, v in privileged_rows(data, written, frames_written, entry["length"]).items():
			privileged.setdefault(k, []).extend(v)
		frames_written += entry["length"]
		written += 1
		logger.info("wrote %s (%d frames)", entry["file"], entry["length"])
	dataset.finalize()
	if privileged:
		import pyarrow as pa
		import pyarrow.parquet as pq

		pq.write_table(pa.table(privileged), out / "meta" / "privileged.parquet")
	provenance = {k: index[k] for k in ("source", "menagerie_commit", "privileged") if k in index}
	if provenance:
		(out / "meta" / "source.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
	return written


def main(argv: list[str] | None = None) -> int:
	"""Command-line entry point."""
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("record_dir", type=Path)
	parser.add_argument("out", type=Path)
	parser.add_argument("--repo-id", default="local/twin-sorting")
	parser.add_argument("--include-failures", action="store_true")
	parser.add_argument("--video", action="store_true", help="store cameras as video like Studio recordings")
	parser.add_argument("--robot-type", default="so101_follower")
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
	count = export(args.record_dir, args.out, args.repo_id, args.include_failures, args.video, args.robot_type)
	sys.stdout.write(f"{count} episodes written to {args.out}\n")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
