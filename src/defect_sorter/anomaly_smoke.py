"""Anomalib → OpenVINO toolchain check with per-device latency.

Trains Padim on synthetic images (a blue block on a dark mat; defects are a dark scratch), exports to OpenVINO,
then times a static-shape model on CPU, GPU and NPU. It proves the toolchain, not detection quality.

	uv run --extra anomaly sorter-anomalib-smoke --workdir data/smoke
"""

from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)

INPUT_SHAPE = (1, 3, 256, 256)


def make_synthetic_dataset(root: Path, n_good: int = 40, n_test: int = 8) -> None:
	"""Write ``train/good``, ``test/good`` and ``test/defect`` PNGs under ``root``."""
	for sub in ("train/good", "test/good", "test/defect"):
		(root / sub).mkdir(parents=True, exist_ok=True)

	def image(defect: bool, seed: int) -> Image.Image:
		rng = np.random.default_rng(seed)
		im = Image.fromarray(rng.normal(40, 6, (256, 256, 3)).clip(0, 255).astype(np.uint8))
		draw = ImageDraw.Draw(im)
		x, y = 100 + int(rng.integers(-10, 10)), 100 + int(rng.integers(-10, 10))
		draw.rectangle([x, y, x + 60, y + 60], fill=(30, 110, 220))
		if defect:
			draw.line([x + 5, y + 10, x + 55, y + 50], fill=(10, 10, 10), width=5)
		return im

	for i in range(n_good):
		image(False, i).save(root / "train/good" / f"{i:03d}.png")
	for i in range(n_test):
		image(False, 1000 + i).save(root / "test/good" / f"{i:03d}.png")
		image(True, 2000 + i).save(root / "test/defect" / f"{i:03d}.png")


def benchmark_devices(model_xml: Path, devices: list[str], runs: int = 50) -> dict[str, float | str]:
	"""Compile a static-shape copy of the model per device and return mean latency in ms or the error text.

	The NPU compiler rejects Anomalib's dynamic ``[?,3,?,?]`` export, so the model is reshaped to ``INPUT_SHAPE``.
	"""
	import openvino as ov

	core = ov.Core()
	model = core.read_model(model_xml)
	model.reshape({model.inputs[0].any_name: list(INPUT_SHAPE)})
	x = np.random.default_rng(0).random(INPUT_SHAPE, dtype=np.float32)
	results: dict[str, float | str] = {}
	for device in devices:
		try:
			compiled = core.compile_model(model, device, {"PERFORMANCE_HINT": "LATENCY"})
			request = compiled.create_infer_request()
			request.infer({0: x})
			t0 = time.perf_counter()
			for _ in range(runs):
				request.infer({0: x})
			results[device] = (time.perf_counter() - t0) / runs * 1000
		except Exception as exc:  # report every device, even when one fails
			results[device] = f"failed: {exc}"
	return results


def main(argv: list[str] | None = None) -> None:
	"""Train, export and benchmark."""
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("--workdir", type=Path, default=Path("data/smoke"))
	args = parser.parse_args(argv)
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

	import openvino as ov
	from anomalib.data import Folder
	from anomalib.deploy import ExportType
	from anomalib.engine import Engine
	from anomalib.models import Padim

	data = args.workdir / "data"
	make_synthetic_dataset(data)
	datamodule = Folder(
		name="smoke",
		root=data,
		normal_dir="train/good",
		abnormal_dir="test/defect",
		normal_test_dir="test/good",
		train_batch_size=8,
		eval_batch_size=8,
		num_workers=0,
	)
	model = Padim(backbone="resnet18", layers=["layer1", "layer2"])
	engine = Engine(default_root_dir=args.workdir / "results", accelerator="cpu", devices=1, max_epochs=1)
	engine.fit(model=model, datamodule=datamodule)
	engine.test(model=model, datamodule=datamodule)
	model_xml = Path(engine.export(model=model, export_type=ExportType.OPENVINO, export_root=args.workdir / "export"))
	logger.info("exported %s", model_xml)

	for device, result in benchmark_devices(model_xml, ov.Core().available_devices).items():
		if isinstance(result, float):
			logger.info("%s: %.2f ms/inference (static %s)", device, result, INPUT_SHAPE)
		else:
			logger.warning("%s: %s", device, result)


if __name__ == "__main__":
	main()
