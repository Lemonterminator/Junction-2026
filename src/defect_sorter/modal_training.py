"""Volume layout and cost bounds for training on Modal, without importing the Modal SDK.

The Modal app (``scripts/modal/train.py``) mounts one Volume at :data:`VOLUME_MOUNT`. Recordings live under
``datasets/<name>``, converted warm-start policies under ``warm-start/<name>``, and every run writes a fresh ``runs/<run-name>`` directory with the same contents as a local
``training.py run`` (``plan.json``, ``config.json``, Lightning CSV metrics, checkpoints), so the existing MLflow logger
reads a downloaded run unchanged.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, replace
from pathlib import PurePosixPath

from defect_sorter.training import DatasetSpec

VOLUME_NAME = "junction-training"
VOLUME_MOUNT = PurePosixPath("/vol")
_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")


def _safe_name(value: str, what: str) -> str:
	if not _NAME.fullmatch(value) or ".." in value:
		raise ValueError(f"{what} must be a single alphanumeric name")
	return value


@dataclass(frozen=True)
class VolumeLayout:
	"""Where one run reads its recording and writes its outputs, inside and outside the container."""

	dataset_name: str
	run_name: str

	def __post_init__(self) -> None:
		_safe_name(self.dataset_name, "dataset name")
		_safe_name(self.run_name, "run name")

	@property
	def dataset_path(self) -> str:
		"""Volume-relative recording directory, as ``modal volume put`` expects."""
		return f"/datasets/{self.dataset_name}"

	@property
	def run_path(self) -> str:
		"""Volume-relative run directory, as ``modal volume get`` expects."""
		return f"/runs/{self.run_name}"

	@property
	def container_dataset(self) -> str:
		"""Recording directory as seen inside the container."""
		return str(VOLUME_MOUNT / "datasets" / self.dataset_name)

	@property
	def container_runs(self) -> str:
		"""Parent of all run directories inside the container."""
		return str(VOLUME_MOUNT / "runs")

	@property
	def container_warm_start(self) -> str:
		"""Parent of converted warm-start policy directories inside the container."""
		return str(VOLUME_MOUNT / "warm-start")

	def upload_command(self, local_root: str) -> list[str]:
		"""Return the CLI command that copies a local recording into the Volume."""
		return ["modal", "volume", "put", VOLUME_NAME, local_root, self.dataset_path]

	def download_command(self, local_parent: str = "artifacts/training") -> list[str]:
		"""Return the CLI command that copies the finished run directory back."""
		return ["modal", "volume", "get", VOLUME_NAME, self.run_path, local_parent]


def warm_start_upload_command(local_dir: str, name: str) -> list[str]:
	"""Return the CLI command that copies a converted warm-start policy directory into the Volume.

	Parameters
	----------
	local_dir : str
		Directory written by ``scripts/training/ckpt_to_warm_start.py``.
	name : str
		The recipe's ``warm_start`` name.

	Returns
	-------
	list[str]
		``modal volume put`` command targeting ``/warm-start/<name>``.
	"""
	return ["modal", "volume", "put", VOLUME_NAME, local_dir, f"/warm-start/{_safe_name(name, 'warm start')}"]


def volume_dataset(dataset: DatasetSpec, layout: VolumeLayout) -> DatasetSpec:
	"""Return the same recording contract with its root moved onto the mounted Volume.

	Parameters
	----------
	dataset : DatasetSpec
		Contract loaded from a local dataset TOML.
	layout : VolumeLayout
		Run layout naming the uploaded recording.

	Returns
	-------
	DatasetSpec
		Identical camera, joint and fps contract; only ``root`` changes.
	"""
	return replace(dataset, root=layout.container_dataset)


def cost_ceiling(rate_per_hour: float, max_hours: float) -> float:
	"""Upper bound in USD of one call's GPU charge, given the call timeout.

	Parameters
	----------
	rate_per_hour : float
		GPU price per hour from ``modal billing rates``.
	max_hours : float
		Call timeout in hours; Modal stops the container at this limit.

	Returns
	-------
	float
		``rate_per_hour * max_hours``. CPU, memory and storage are billed on top.
	"""
	for value, name in ((rate_per_hour, "rate_per_hour"), (max_hours, "max_hours")):
		if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
			raise ValueError(f"{name} must be finite and positive")
	return rate_per_hour * max_hours
