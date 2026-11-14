"""Per-block runtime profile of an exported SmolVLA IR using OpenVINO per-node performance counters."""

import re, sys, collections
import numpy as np
import openvino as ov
import openvino.properties as props
import openvino.properties.hint as hints

path, device = sys.argv[1], sys.argv[2]
core = ov.Core()
model = core.read_model(path)
rng = np.random.default_rng(0)
feed = {}
for i in model.inputs:
	n, s, et = i.get_any_name(), list(i.get_shape()), i.get_element_type()
	if n.endswith("_mask") or "image_masks" in n:
		feed[n] = np.ones(s, dtype=bool)
	elif et == ov.Type.i64:
		feed[n] = rng.integers(1, 40000, size=s).astype(np.int64)
	else:
		feed[n] = rng.standard_normal(s).astype(np.float32)
comp = core.compile_model(
	model, device, {hints.performance_mode: hints.PerformanceMode.LATENCY, props.enable_profiling: True}
)
req = comp.create_infer_request()
req.infer(feed)
req.get_profiling_info()
runs = 5
acc = collections.Counter()
total = 0.0
for _ in range(runs):
	req.infer(feed)
	for p in req.get_profiling_info():
		t = p.real_time.total_seconds() * 1000
		acc[p.node_name] += t
		total += t


def bucket(name):
	m = re.search(r"vlm_with_expert\.vlm\.model\.(vision_model|connector|text_model)", name)
	if m:
		return m.group(1)
	if "lm_expert" in name:
		return "expert"
	for k in ("state_proj", "action_in_proj", "action_out_proj", "action_time_mlp"):
		if k in name:
			return "expert_io"
	return "other"


by = collections.Counter()
for n, t in acc.items():
	by[bucket(n)] += t
print("DEVICE", device, "sum of per-node times per inference: %.1f ms" % (total / runs))
for b, t in by.most_common():
	print("%-12s %7.1f ms  %5.1f%%" % (b, t / runs, 100 * t / total))
other = sorted(((t, n) for n, t in acc.items() if bucket(n) == "other"), reverse=True)[:6]
print("top 'other' nodes:")
for t, n in other:
	print("  %.2f ms  %s" % (t / runs, n[:110]))
