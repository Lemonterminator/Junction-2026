"""Copy an exported IR with every Bucketize output narrowed to i32 (then converted back to i64)."""

import sys
from pathlib import Path
import openvino as ov
from openvino import opset13 as ops

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)
model = ov.Core().read_model(str(src / "smolvla.xml"))
n = 0
for op in [o for o in model.get_ops() if o.get_type_name() == "Bucketize"]:
	if op.get_attributes()["output_type"] != "i64":
		continue
	new = ops.bucketize(
		op.input_value(0), op.input_value(1), "i32", with_right_bound=op.get_attributes()["with_right_bound"]
	)
	conv = ops.convert(new, "i64")
	op.output(0).replace(conv.output(0))
	n += 1
model.validate_nodes_and_infer_types()
ov.save_model(model, str(dst / "smolvla.xml"), compress_to_fp16=False)
print("patched Bucketize nodes:", n)
