"""Read actual LeRobot v3 task shards inside the isolated training environment."""

from __future__ import annotations

import sys
from pathlib import Path


def validate_tasks(labels: list[object], indices: list[object], frame_indices: list[object]) -> None:
	"""Reject empty language or task references that do not match LeRobot row lookup.

	Parameters
	----------
	labels : list[object]
		Task text in metadata row order.
	indices : list[object]
		Task IDs in metadata row order.
	frame_indices : list[object]
		Unique task IDs referenced by recorded frames.
	"""
	if not labels or any(not isinstance(label, str) or not label.strip() for label in labels):
		raise ValueError("task language must contain nonempty instructions")
	if indices != list(range(len(labels))):
		raise ValueError("task indices must match contiguous metadata row positions")
	if not frame_indices or any(
		isinstance(index, bool) or not isinstance(index, int) or index not in indices for index in frame_indices
	):
		raise ValueError("frame task references are missing or outside task metadata")


def main(argv: list[str] | None = None) -> int:
	"""Read task metadata and frame references without loading policy weights.

	Parameters
	----------
	argv : list[str] | None
		One recording-root argument, or process arguments when omitted.

	Returns
	-------
	int
		Zero when task payload validation passes. Invalid inputs raise errors.
	"""
	import pandas as pd
	import pyarrow.parquet as pq

	args = sys.argv[1:] if argv is None else argv
	if len(args) != 1:
		raise ValueError("expected one local recording root")
	root = Path(args[0])
	tasks = pd.read_parquet(root / "meta" / "tasks.parquet")
	frame_indices: set[object] = set()
	for path in sorted((root / "data").glob("chunk-*/file-*.parquet")):
		for batch in pq.ParquetFile(path).iter_batches(columns=["task_index"]):
			frame_indices.update(batch.column("task_index").to_pylist())
	validate_tasks(tasks.index.tolist(), tasks["task_index"].tolist(), list(frame_indices))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
