"""Convert a SmolVLA Lightning checkpoint into a policy directory that a recipe's ``warm_start`` can load.

Run in the pinned Studio backend environment (torch, safetensors, huggingface_hub)::

	uv run --project external/physical-ai-studio/application/backend --extra cuda --frozen \
		python scripts/training/ckpt_to_warm_start.py artifacts/training/sort-depth-v2-10k/checkpoints/best.ckpt \
		artifacts/warm-start/sort-depth-v2-10k

The directory holds ``model.safetensors`` (policy-model weights only, see
``defect_sorter.training.warm_start_state_dict``), ``config.json`` from ``lerobot/smolvla_base`` (same architecture;
the recipe still overrides the training settings) and ``source.json`` naming the checkpoint it came from.
Normalisation statistics are not carried over: the warm-started run computes them from its own training data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import torch
from huggingface_hub import hf_hub_download
from safetensors.torch import save_file

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from defect_sorter.training import warm_start_state_dict

BASE = "lerobot/smolvla_base"


def _sha256(path: Path) -> str:
	digest = hashlib.sha256()
	with path.open("rb") as stream:
		for block in iter(lambda: stream.read(1 << 24), b""):
			digest.update(block)
	return digest.hexdigest()


def main() -> int:
	"""Write the warm-start directory; refuses to overwrite an existing one."""
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("checkpoint", type=Path)
	parser.add_argument("output", type=Path)
	args = parser.parse_args()
	if args.output.exists():
		raise SystemExit(f"{args.output} exists; choose a new directory")
	checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False, mmap=True)
	if checkpoint.get("hparams_name") is None or "vlm_model_name" not in checkpoint.get("hyper_parameters", {}):
		raise SystemExit("not a SmolVLA Lightning checkpoint")
	weights = {
		key: value.detach().clone().contiguous()
		for key, value in warm_start_state_dict(checkpoint["state_dict"]).items()
	}
	args.output.mkdir(parents=True)
	save_file(weights, str(args.output / "model.safetensors"))
	shutil.copyfile(hf_hub_download(BASE, "config.json"), args.output / "config.json")  # nosec B615
	source = {
		"checkpoint": str(args.checkpoint),
		"checkpoint_sha256": _sha256(args.checkpoint),
		"global_step": checkpoint.get("global_step"),
		"epoch": checkpoint.get("epoch"),
		"tensors": len(weights),
		"config_from": BASE,
	}
	(args.output / "source.json").write_text(json.dumps(source, indent=2) + "\n", encoding="utf-8")
	sys.stdout.write(json.dumps(source, indent=2) + "\n")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
