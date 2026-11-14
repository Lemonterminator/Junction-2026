"""Replace each Bucketize with the constant index table PyTorch produces, for an IR whose patch grid is fixed.

OpenVINO's GPU plugin returns wrong bucket ids for this op; the ids depend only on the (fixed) patch grid.
"""

import sys
from pathlib import Path
import numpy as np, torch
import openvino as ov
from openvino import opset13 as ops
import openvino.properties.hint as hints

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)
core = ov.Core()
model = core.read_model(str(src / "smolvla.xml"))
bks = [o for o in model.get_ordered_ops() if o.get_type_name() == "Bucketize"]
probe = ov.Model(
	[ops.result(b.output(0)) for b in bks]
	+ [ops.result(b.input_value(0)) for b in bks]
	+ [ops.result(b.input_value(1)) for b in bks],
	model.get_parameters(),
	"probe",
)
rng = np.random.default_rng(0)
feed = {}
for i in probe.inputs:
	n, s, et = i.get_any_name(), list(i.get_shape()), i.get_element_type()
	if n.endswith("_mask") or "image_masks" in n:
		feed[n] = np.ones(s, dtype=bool)
	elif et == ov.Type.i64:
		feed[n] = rng.integers(1, 40000, size=s).astype(np.int64)
	else:
		feed[n] = rng.random(s, dtype=np.float32) if n == "images" else rng.standard_normal(s).astype(np.float32)
c = core.compile_model(probe, "CPU")
r = c.create_infer_request().infer(feed)
k = len(bks)
for j, b in enumerate(bks):
	coords, bounds = np.asarray(r[c.output(k + j)]), np.asarray(r[c.output(2 * k + j)]).ravel()
	ids = torch.bucketize(torch.from_numpy(coords), torch.from_numpy(bounds), right=True).numpy().astype(np.int64)
	assert np.array_equal(ids, np.asarray(r[c.output(j)])), "CPU result differs from torch"
	b.output(0).replace(ops.constant(ids).output(0))
	print("bucketize", j, "->", ids.shape, "constant; first row", ids[0][:5].tolist(), "...")
model.validate_nodes_and_infer_types()
ov.save_model(model, str(dst / "smolvla.xml"), compress_to_fp16=False)
