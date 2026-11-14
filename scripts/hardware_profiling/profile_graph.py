"""Static profile of an exported SmolVLA IR: op histogram, GEMM FLOPs and weight bytes per block."""

import re, sys, collections
import numpy as np
import openvino as ov

model = ov.Core().read_model(sys.argv[1])
ops = model.get_ordered_ops()
hist = collections.Counter(o.get_type_name() for o in ops)
print("TOTAL ops", len(ops))
print("OPHIST", hist.most_common(14))


def bucket(name):
	m = re.search(r"vlm_with_expert\.vlm\.model\.(vision_model|connector|text_model)", name)
	if m:
		b = m.group(1)
		l = re.search(r"layers\.(\d+)", name)
		return b if b != "text_model" or not l else "text_model.L%02d" % int(l.group(1))
	m = re.search(r"lm_expert", name)
	if m:
		l = re.search(r"layers\.(\d+)", name)
		return "expert.L%02d" % int(l.group(1)) if l else "expert.other"
	for k in ("state_proj", "action_in_proj", "action_out_proj", "action_time_mlp", "embed_tokens"):
		if k in name:
			return k
	return "other"


flops, wbytes, nmm = collections.Counter(), collections.Counter(), collections.Counter()
for o in ops:
	t, n = o.get_type_name(), o.get_friendly_name()
	if t == "MatMul":
		a = o.input(0).get_partial_shape().get_shape() if o.input(0).get_partial_shape().is_static else None
		out = o.output(0).get_partial_shape()
		if a is None or not out.is_static:
			continue
		ta = o.get_attributes().get("transpose_a", False)
		k = a[-2] if ta else a[-1]
		flops[bucket(n)] += 2 * int(np.prod(out.get_shape())) * int(k)
		nmm[bucket(n)] += 1
	elif t == "Convolution":
		out, w = o.output(0).get_partial_shape(), o.input(1).get_partial_shape()
		if out.is_static and w.is_static:
			ws = w.get_shape()
			flops[bucket(n)] += 2 * int(np.prod(out.get_shape())) * int(np.prod(ws[1:]))
			nmm[bucket(n)] += 1
	elif t == "Constant":
		wbytes[bucket(n)] += o.get_byte_size()
tot = sum(flops.values())
print("TOTAL GFLOPs (MatMul+Conv)", round(tot / 1e9, 1))


def key(b):
	return (b.split(".")[0], b)


rows = sorted(set(flops) | set(wbytes), key=key)
print("BUCKET\tGFLOPs\t%\tGEMMs\tWeightMB")
agg = collections.defaultdict(lambda: [0, 0, 0])
for b in rows:
	g = b.split(".")[0]
	agg[g][0] += flops[b]
	agg[g][1] += nmm[b]
	agg[g][2] += wbytes[b]
	print("%s\t%.1f\t%.1f\t%d\t%.1f" % (b, flops[b] / 1e9, 100 * flops[b] / tot, nmm[b], wbytes[b] / 1e6))
print("--- GROUPS")
for g, (f, c, w) in agg.items():
	print("%s\t%.1f GFLOPs\t%.1f%%\t%d GEMMs\t%.1f MB" % (g, f / 1e9, 100 * f / tot, c, w / 1e6))
