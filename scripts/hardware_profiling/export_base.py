"""Export lerobot/smolvla_base to OpenVINO with the checkpoint's own shapes."""

import json, logging, sys, time
from pathlib import Path
import torch
from physicalai.policies.smolvla.policy import SmolVLA

logging.basicConfig(level=logging.INFO)
out = Path(sys.argv[1])
t0 = time.time()
policy = SmolVLA(pretrained_name_or_path="lerobot/smolvla_base", dtype="float32", use_random_input_noise=True)
policy.eval()
print("loaded in %.1fs" % (time.time() - t0), flush=True)
cfg = policy.config
print(
	"chunk",
	cfg.chunk_size,
	"n_action_steps",
	cfg.n_action_steps,
	"num_steps",
	cfg.num_steps,
	"max_action_dim",
	cfg.max_action_dim,
	"img_res",
	cfg.resize_imgs_with_padding,
	"num_cameras",
	cfg.num_cameras,
	"tok_len",
	cfg.tokenizer_max_length,
	flush=True,
)
for k, v in policy._dataset_stats.items():
	print("stat", k, v.get("shape"), v.get("type"), flush=True)
print("params (M): %.1f" % (sum(p.numel() for p in policy.parameters()) / 1e6), flush=True)
t0 = time.time()
with torch.no_grad():
	policy.export(out, backend="openvino")
print("exported in %.1fs" % (time.time() - t0), flush=True)
for p in sorted(out.rglob("*")):
	if p.is_file():
		print(p.relative_to(out), p.stat().st_size, flush=True)
