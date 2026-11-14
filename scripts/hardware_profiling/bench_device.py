"""Compile an exported SmolVLA OpenVINO IR on one device, time it, save the output.

Inputs are fixed-seed synthetic tensors: nothing touches a camera or an arm.
"""

import json, statistics, sys, time, traceback
from pathlib import Path
import numpy as np
import openvino as ov
import openvino.properties.hint as hints

export_dir, device = Path(sys.argv[1]), sys.argv[2]
iters = int(sys.argv[3]) if len(sys.argv) > 3 else 10
res = {"device": device, "export": str(export_dir)}
core = ov.Core()
model = core.read_model(str(export_dir / "smolvla.xml"))
rng = np.random.default_rng(0)
feed = {}
for i in model.inputs:
	name, shape, et = i.get_any_name(), list(i.get_shape()), i.get_element_type()
	if "image_masks" in name or name.endswith("_mask"):
		feed[name] = np.ones(shape, dtype=bool)
	elif et == ov.Type.i64:
		feed[name] = rng.integers(1, 40000, size=shape).astype(np.int64)
	else:
		feed[name] = (
			rng.random(shape, dtype=np.float32) if name == "images" else rng.standard_normal(shape).astype(np.float32)
		)
try:
	t0 = time.time()
	compiled = core.compile_model(model, device, {hints.performance_mode: hints.PerformanceMode.LATENCY})
	res["compile_s"] = round(time.time() - t0, 2)
	for prop in ("INFERENCE_PRECISION_HINT", "EXECUTION_DEVICES"):
		try:
			res[prop] = str(compiled.get_property(prop))
		except Exception:
			pass
	req = compiled.create_infer_request()
	t0 = time.time()
	out = req.infer(feed)
	res["first_infer_s"] = round(time.time() - t0, 3)
	for _ in range(2):
		req.infer(feed)
	times = []
	for _ in range(iters):
		t0 = time.perf_counter()
		out = req.infer(feed)
		times.append((time.perf_counter() - t0) * 1000)
	arr = np.asarray(out[compiled.output(0)])
	np.save(export_dir / ("out_%s.npy" % device), arr)
	res.update(
		status="ok",
		iters=iters,
		median_ms=round(statistics.median(times), 1),
		min_ms=round(min(times), 1),
		max_ms=round(max(times), 1),
		out_shape=list(arr.shape),
		out_finite=bool(np.isfinite(arr).all()),
	)
except Exception as e:
	res.update(status="fail", error=("%s: %s" % (type(e).__name__, str(e)))[:1500])
	traceback.print_exc()
print("RESULT " + json.dumps(res), flush=True)
