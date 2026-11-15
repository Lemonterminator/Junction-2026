"""Package an exported policy for a private GitHub release, and verify a download against its manifest.

``release_manifest`` records what a release contains and where it came from: every exported file with its size and
SHA-256, the training run (recipe, data source, episode counts, steps, final losses), the code commit and an explicit
``status``. Teammates download with ``gh`` and check the files with ``verify``::

	uv run python -m defect_sorter.model_release manifest artifacts/export/<run> artifacts/training/<run> \
		--status smoke-test --out artifacts/export/<run>/release.json
	gh release download <tag> --repo Lemonterminator/Junction-2026 --dir models/<tag>
	uv run python -m defect_sorter.model_release verify models/<tag>
	uv run python -m defect_sorter.model_release anomaly-manifest artifacts/release/<tag> \\
		artifacts/anomaly/real-baseline-v2 --fold 0 --status baseline --out artifacts/release/<tag>/release.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from defect_sorter.tracking import anomaly_record, parse_params, training_record

STATUSES = ("smoke-test", "baseline", "candidate", "demo")
"""``smoke-test``: proves the path, not usable on the arm; ``baseline``: first model on real data with known data
limits, not validated for the arm; ``candidate``: trained on real data, under evaluation; ``demo``: frozen for the
judged run."""

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
	files = _files(export_dir)
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


def _files(export_dir: Path) -> list[dict[str, Any]]:
	return [
		{"name": path.name, "bytes": path.stat().st_size, "sha256": _sha256(path)}
		for path in sorted(export_dir.iterdir())
		if path.is_file() and path.name != MANIFEST_NAME
	]


def anomaly_manifest(
	export_dir: Path,
	baseline_dir: Path,
	fold: int,
	*,
	status: str,
	commit: str,
	params: dict[str, Any] | None = None,
) -> dict[str, Any]:
	"""Describe a release of one fold model from an anomaly baseline run (see :func:`tracking.anomaly_record`).

	``export_dir`` holds the staged ``model.xml`` and ``model.bin``; they must be byte-identical to the fold's export,
	so the threshold and results in the manifest belong to the released file. Only the CPU threshold is recorded:
	scores differ by device, so other devices are calibrated on their own before use.

	Raises
	------
	ValueError
		For a status outside :data:`STATUSES`, or a staged model that differs from the fold export.
	"""
	if status not in STATUSES:
		raise ValueError(f"status must be one of {STATUSES}")
	record = anomaly_record(baseline_dir, fold, params)
	for source in record.artifacts[:2]:
		staged = export_dir / source.name
		if not staged.is_file() or _sha256(staged) != _sha256(source):
			raise ValueError(f"{source.name} in {export_dir} is not the fold {fold} export")
	summary = json.loads((baseline_dir / "summary.json").read_text(encoding="utf-8"))
	latency = next((v for k, v in summary.items() if k.startswith("latency_")), {})
	values = {key: series[0][1] for key, series in record.metrics.items()}
	return {
		"status": status,
		"source": record.tags["source"],
		"code_commit": commit,
		"inspection": {
			"run": record.name,
			**{key: record.params[key] for key in ("model", "dataset", "camera", "fold", "val_fold", "train_frames")},
			"aggregate": record.params["aggregate"],
			"thresholds": {"CPU": record.params["threshold_cpu"]},
			"params": params or {},
			"results": {
				**{
					key: int(values[key])
					for key in ("defects_caught", "defects_total", "normals_passed", "normals_total")
				},
				"frame_auroc_test_per_fold": summary[next(k for k in summary if k.endswith("_score/median"))][
					"frame_auroc_test_per_fold"
				],
			},
			"latency_ms": {
				device: v
				for device, v in latency.items()
				if isinstance(v, dict) and not device.startswith("off_colour")
			},
		},
		"files": _files(export_dir),
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
	anomaly = sub.add_parser("anomaly-manifest", help="manifest for one fold model of an anomaly baseline run")
	anomaly.add_argument("export_dir", type=Path)
	anomaly.add_argument("baseline_dir", type=Path)
	anomaly.add_argument("--fold", type=int, default=0)
	anomaly.add_argument("--param", action="append", default=[], help="extra KEY=VALUE training setting")
	anomaly.add_argument("--status", choices=STATUSES, required=True)
	anomaly.add_argument("--out", type=Path, required=True)
	check = sub.add_parser("verify")
	check.add_argument("directory", type=Path)
	args = parser.parse_args(argv)
	if args.command in ("manifest", "anomaly-manifest"):
		commit = subprocess.run(
			["git", "rev-parse", "HEAD"],  # noqa: S607
			capture_output=True,
			text=True,
			check=True,
		).stdout.strip()
		if args.command == "manifest":
			manifest = release_manifest(args.export_dir, args.run_dir, status=args.status, commit=commit)
		else:
			manifest = anomaly_manifest(
				args.export_dir,
				args.baseline_dir,
				args.fold,
				status=args.status,
				commit=commit,
				params=parse_params(args.param),
			)
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
