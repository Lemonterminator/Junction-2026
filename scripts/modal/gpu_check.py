"""Smallest Modal GPU check: allocate one GPU for a few seconds and report what it is.

Run from the repository root (cost is a few seconds of GPU time):

	modal run scripts/modal/gpu_check.py --gpu T4
"""

from __future__ import annotations

import subprocess

import modal

app = modal.App("junction-gpu-check")
image = modal.Image.debian_slim(python_version="3.12")


def _query() -> str:
	return subprocess.run(
		["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],  # noqa: S607
		check=True,
		capture_output=True,
		text=True,
	).stdout.strip()


@app.function(image=image, gpu="T4", timeout=120)
def check_t4() -> str:
	"""Report the allocated T4."""
	return _query()


@app.function(image=image, gpu="L4", timeout=120)
def check_l4() -> str:
	"""Report the allocated L4."""
	return _query()


@app.local_entrypoint()
def main(gpu: str = "T4") -> None:
	"""Run the check on one GPU type (T4 or L4)."""
	result = {"T4": check_t4, "L4": check_l4}[gpu.upper()].remote()
	print(f"{gpu}: {result}")  # noqa: T201
