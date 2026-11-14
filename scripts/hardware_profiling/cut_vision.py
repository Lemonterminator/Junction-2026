"""Cut the vision encoder + connector out of an exported SmolVLA IR as a standalone model."""

import sys
from pathlib import Path
import openvino as ov
from openvino import opset13 as ops

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)
model = ov.Core().read_model(str(src / "smolvla.xml"))
order = model.get_ordered_ops()
conn = [o for o in order if "vlm.model.connector" in o.get_friendly_name() and o.get_type_name() != "Constant"]
last = conn[-1]
print("connector last op:", last.get_friendly_name(), last.get_type_name(), last.output(0).get_partial_shape())
res = ops.result(last.output(0))
params = model.get_parameters()
try:
	sub = ov.Model([res], params, "vision")
except Exception as e:
	print("ctor failed with all params:", e)
	raise
sub.validate_nodes_and_infer_types()
print("sub inputs:", [(i.get_any_name(), i.get_partial_shape()) for i in sub.inputs])
print("sub ops:", len(sub.get_ops()))
ov.save_model(sub, str(dst / "smolvla.xml"), compress_to_fp16=False)
