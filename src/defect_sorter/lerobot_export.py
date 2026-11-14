"""Convert recorded episodes (``offline_pipeline record`` output) into a LeRobot v3 dataset.

Runs inside the pinned Studio backend environment, which provides ``lerobot`` 0.6; the root environment only uses
:func:`lerobot_features`. Images are stored as image features, not MP4, so no video encoder is needed. Only
successful episodes are written unless ``--include-failures`` is given. The output directory must not exist::

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


def lerobot_features(index: dict[str, Any]) -> dict[str, dict[str, Any]]:
	"""LeRobot feature specification for a recording index (state/action names and camera shapes)."""
	names = list(index["state_names"])
	vector = {"dtype": "float32", "shape": (len(names),), "names": names}
	features: dict[str, dict[str, Any]] = {"observation.state": dict(vector), "action": dict(vector)}
	for camera, shape in index["cameras"].items():
		features[f"observation.images.{camera}"] = {
			"dtype": "image",
			"shape": tuple(shape),
			"names": ["height", "width", "channels"],
		}
	return features


def export(record_dir: Path, out: Path, repo_id: str, include_failures: bool = False) -> int:
	"""Write the episodes under ``record_dir`` to a new LeRobot dataset at ``out``; returns the episode count."""
	import numpy as np
	from lerobot.datasets.lerobot_dataset import LeRobotDataset

	if out.exists():
		raise FileExistsError(f"refusing to replace existing dataset: {out}")
	index = json.loads((record_dir / "index.json").read_text(encoding="utf-8"))
	dataset = LeRobotDataset.create(
		repo_id=repo_id,
		fps=index["fps"],
		features=lerobot_features(index),
		root=out,
		robot_type="so101_follower",
		use_videos=False,
		image_writer_threads=8,
	)
	written = 0
	for entry in index["episodes"]:
		if not entry["success"] and not include_failures:
			continue
		data = np.load(record_dir / entry["file"])
		for t in range(entry["length"]):
			frame = {"observation.state": data["state"][t], "action": data["action"][t], "task": entry["task"]}
			for camera in index["cameras"]:
				frame[f"observation.images.{camera}"] = data[camera][t]
			dataset.add_frame(frame)
		dataset.save_episode()
		written += 1
		logger.info("wrote %s (%d frames)", entry["file"], entry["length"])
	dataset.finalize()
	return written


def main(argv: list[str] | None = None) -> int:
	"""Command-line entry point."""
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("record_dir", type=Path)
	parser.add_argument("out", type=Path)
	parser.add_argument("--repo-id", default="local/twin-sorting")
	parser.add_argument("--include-failures", action="store_true")
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
	count = export(args.record_dir, args.out, args.repo_id, args.include_failures)
	sys.stdout.write(f"{count} episodes written to {args.out}\n")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
