"""Per-node GPU/CPU time of an exported SmolVLA IR split by node type, kernel and name prefix.

Usage: ``python profile_other.py <smolvla.xml> <DEVICE>``. Focuses on nodes outside the named
vision, text and expert blocks, which is where reference kernels such as Select and Clamp show up.
"""

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
rows = collections.defaultdict(lambda: [0.0, 0, "", ""])
for _ in range(runs):
	req.infer(feed)
	for p in req.get_profiling_info():
		r = rows[p.node_name]
		r[0] += p.real_time.total_seconds() * 1000
		r[1] += 1
		r[2] = p.node_type
		r[3] = p.exec_type


def in_named(n):
	return bool(re.search(r"vlm_with_expert|lm_expert|state_proj|action_in_proj|action_out_proj|action_time_mlp", n))


by_type, by_exec, named = collections.Counter(), collections.Counter(), collections.Counter()
n_other = 0
for n, (t, c, ty, ex) in rows.items():
	if not in_named(n):
		by_type[ty] += t / runs
		by_exec[ex.split(" ")[0][:40]] += t / runs
		n_other += 1
print("unnamed nodes:", n_other, "of", len(rows))
print("--- unnamed by node_type (ms/inference)")
for k, v in by_type.most_common(8):
	print("  %-28s %.1f" % (k, v))
print("--- unnamed by exec kernel")
for k, v in by_exec.most_common(8):
	print("  %-40s %.1f" % (k, v))
print("--- name prefixes of unnamed top-time nodes")
pre = collections.Counter()
for n, (t, c, ty, ex) in rows.items():
	if not in_named(n):
		pre[re.sub(r"_\d+$", "", n)[:60]] += t / runs
for k, v in pre.most_common(12):
	print("  %.2f ms  %s" % (v, k))
