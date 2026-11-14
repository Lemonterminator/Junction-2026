"""Compare an exported Padim OpenVINO model across CPU, GPU (FP16 and FP32) and NPU.

Usage: ``python anomalib_device_parity.py <workdir>`` where ``<workdir>`` holds the output of
``defect_sorter.anomaly_smoke`` (``export/weights/openvino/model.xml`` and
``data/test/{good,defect}/*.png``). The model is reshaped to a static 1x3x256x256 input
because the NPU needs static shapes. CPU is the reference. Nothing touches a camera or an arm.
"""

import glob
import sys
import time
from pathlib import Path

import numpy as np
import openvino as ov
from PIL import Image

SIZE = 256
TIMED_RUNS = 200
CONFIGS: list[tuple[str, dict[str, str]]] = [
	("CPU", {}),
	("GPU", {}),
	("GPU", {"INFERENCE_PRECISION_HINT": "f32"}),
	("NPU", {}),
]


def load_image(path: str) -> np.ndarray:
	"""Return an RGB image as a float32 NCHW array in [0, 1]."""
	image = Image.open(path).convert("RGB").resize((SIZE, SIZE))
	return (np.asarray(image, dtype=np.float32) / 255.0).transpose(2, 0, 1)[None]


def main() -> None:
	"""Run every configuration and print one summary line each."""
	workdir = Path(sys.argv[1])
	model_xml = str(workdir / "export" / "weights" / "openvino" / "model.xml")
	good = sorted(glob.glob(str(workdir / "data" / "test" / "good" / "*.png")))
	defect = sorted(glob.glob(str(workdir / "data" / "test" / "defect" / "*.png")))
	images = [load_image(p) for p in good + defect]
	is_defect = np.array([False] * len(good) + [True] * len(defect))
	core = ov.Core()
	ref_scores: np.ndarray | None = None
	ref_maps: np.ndarray | None = None
	for device, config in CONFIGS:
		model = core.read_model(model_xml)
		model.reshape({"input": [1, 3, SIZE, SIZE]})
		compiled = core.compile_model(model, device, config)
		scores, labels, maps = [], [], []
		for image in images:
			result = compiled(image)
			scores.append(float(result[compiled.output("pred_score")].ravel()[0]))
			labels.append(int(result[compiled.output("pred_label")].ravel()[0]))
			maps.append(np.array(result[compiled.output("anomaly_map")])[0, 0])
		score_arr, label_arr, map_arr = np.array(scores), np.array(labels), np.stack(maps)
		if ref_scores is None or ref_maps is None:
			ref_scores, ref_maps = score_arr, map_arr
		corr = np.mean(
			[
				np.corrcoef(a.ravel(), b.ravel())[0, 1]
				for a, b in zip(map_arr[is_defect], ref_maps[is_defect], strict=True)
			]
		)
		times = []
		for _ in range(TIMED_RUNS):
			start = time.perf_counter()
			compiled(images[0])
			times.append((time.perf_counter() - start) * 1000)
		sys.stdout.write(
			f"{device} {config or 'default'}: defect score mean {score_arr[is_defect].mean():.3f} "
			f"(CPU {ref_scores[is_defect].mean():.3f}); flagged good={int(label_arr[~is_defect].sum())}/{len(good)} "
			f"defect={int(label_arr[is_defect].sum())}/{len(defect)}; defect-map corr vs CPU {corr:.4f}; "
			f"median {np.median(times):.2f} ms\n",
		)


if __name__ == "__main__":
	main()
