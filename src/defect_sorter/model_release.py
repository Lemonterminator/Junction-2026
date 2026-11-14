"""Package an exported policy for a private GitHub release, and verify a download against its manifest.

``release_manifest`` records what a release contains and where it came from: every exported file with its size and
SHA-256, the training run (recipe, data source, episode counts, steps, final losses), the code commit and an explicit
``status``. Teammates download with ``gh`` and check the files with ``verify``::

	uv run python -m defect_sorter.model_release manifest artifacts/export/<run> artifacts/training/<run> \
		--status smoke-test --out artifacts/export/<run>/release.json
	gh release download <tag> --repo Lemonterminator/Junction-2026 --dir models/<tag>
	uv run python -m defect_sorter.model_release verify models/<tag>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from defect_sorter.tracking import training_record

STATUSES = ("smoke-test", "candidate", "demo")
"""``smoke-test``: proves the path, not usable on the arm; ``candidate``: trained on real data, under evaluation;
``demo``: frozen for the judged run."""

MANIFEST_NAME = "release.json"


def _sha256(path: Path) -> str:
	digest = hashlib.sha256()
	with path.open("rb") as stream:
		for block in iter(lambda: stream.read(1 << 20), b""):
			digest.update(block)
	return digest.hexdigest()


def release_manifest(export_dir: Path, run_dir: Path, *, status: str, commit: str) -> dict[str, Any]:
	"""Describe the files in ``export_dir`` and the training run in ``run_dir``.

	Raises
	------
	ValueError
		For a status outside :data:`STATUSES`.
	"""
	if status not in STATUSES:
		raise ValueError(f"status must be one of {STATUSES}")
	record = training_record(run_dir)
	last = {key: series[-1][1] for key, series in record.metrics.items() if series}
	files = [
		{"name": path.name, "bytes": path.stat().st_size, "sha256": _sha256(path)}
		for path in sorted(export_dir.iterdir())
		if path.is_file() and path.name != MANIFEST_NAME
	]
	return {
		"status": status,
		"source": record.tags["source"],
		"code_commit": commit,
		"training": {
			"run": record.name,
			"recipe": record.params["recipe"],
			"policy": record.params["policy"],
			"dataset_repo_id": record.params["dataset_repo_id"],
			"camera_keys": record.params["camera_keys"],
			"train_episodes": record.params["train_episodes"],
			"val_episodes": record.params["val_episodes"],
			"max_steps": record.params["max_steps"],
			"final_train_loss": last.get("train/loss"),
			"final_val_loss": last.get("val/loss"),
		},
		"files": files,
	}


def verify_download(directory: Path, manifest: dict[str, Any]) -> list[str]:
	"""Problems with the files in ``directory`` compared with ``manifest``; empty when everything matches."""
	problems = []
	for entry in manifest["files"]:
		path = directory / entry["name"]
		if not path.is_file():
			problems.append(f"{entry['name']}: missing")
		elif path.stat().st_size != entry["bytes"] or _sha256(path) != entry["sha256"]:
			problems.append(f"{entry['name']}: sha256 mismatch")
	return problems


def main(argv: list[str] | None = None) -> int:
	"""``manifest`` writes a release manifest; ``verify`` checks a downloaded directory (exit 1 on problems)."""
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	sub = parser.add_subparsers(dest="command", required=True)
	make = sub.add_parser("manifest")
	make.add_argument("export_dir", type=Path)
	make.add_argument("run_dir", type=Path)
	make.add_argument("--status", choices=STATUSES, required=True)
	make.add_argument("--out", type=Path, required=True)
	check = sub.add_parser("verify")
	check.add_argument("directory", type=Path)
	args = parser.parse_args(argv)
	if args.command == "manifest":
		commit = subprocess.run(
			["git", "rev-parse", "HEAD"],  # noqa: S607
			capture_output=True,
			text=True,
			check=True,
		).stdout.strip()
		manifest = release_manifest(args.export_dir, args.run_dir, status=args.status, commit=commit)
		args.out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
		sys.stdout.write(f"wrote {args.out} ({len(manifest['files'])} files)\n")
		return 0
	manifest = json.loads((args.directory / MANIFEST_NAME).read_text(encoding="utf-8"))
	problems = verify_download(args.directory, manifest)
	for problem in problems:
		sys.stdout.write(problem + "\n")
	sys.stdout.write("ok\n" if not problems else f"{len(problems)} problem(s)\n")
	return 1 if problems else 0


if __name__ == "__main__":
	raise SystemExit(main())
