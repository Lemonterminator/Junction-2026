# Hardware profiling scripts

Manual, inference-only checks used for the first-round profiling in
[`docs/infrastructure/HARDWARE_PROFILING.md`](../../docs/infrastructure/HARDWARE_PROFILING.md).
They run on the Intel workstation, not in the default test suite. Inputs are fixed-seed
synthetic tensors or synthetic images: no script opens a camera or moves the arm.

The SmolVLA scripts need the `physicalai` environment of `external/physical-ai-studio`
(`library/.venv`, OpenVINO 2026.4). `anomalib_device_parity.py` needs the `anomaly` extra.
Run each in its own virtual environment so the Studio container and its environment stay untouched.

| Script | Purpose |
| --- | --- |
| `export_base.py <out_dir>` | Export `lerobot/smolvla_base` to an OpenVINO IR with the checkpoint's own shapes. |
| `bench_device.py <export_dir> <DEVICE> [iters]` | Compile on `CPU`/`GPU`/`NPU`, time inference, save the output as `out_<DEVICE>.npy`, print `RESULT {json}`. |
| `profile_graph.py <smolvla.xml>` | Static op histogram, MatMul/Conv FLOPs and weight bytes per block. |
| `profile_runtime.py <smolvla.xml> <DEVICE>` | Per-block runtime from OpenVINO per-node counters. |
| `profile_other.py <smolvla.xml> <DEVICE>` | Time of the nodes outside the named blocks, by node type and kernel. |
| `cut_vision.py <export_dir> <out_dir>` | Cut the vision encoder and connector out as a standalone IR for per-block device tests. |
| `fix_bucketize.py <export_dir> <out_dir>` | Replace each `Bucketize` with the constant ids PyTorch computes (GPU plugin workaround). |
| `patch_bucketize.py <export_dir> <out_dir>` | Narrow `Bucketize` outputs to i32 so the NPU compiler accepts them. |
| `anomalib_device_parity.py <workdir>` | Compare a Padim OpenVINO model on CPU, GPU FP16, GPU FP32 and NPU. |

Benchmark all three devices for one export, one process per device so a compile failure
or timeout on the NPU cannot hide the other results:

```bash
for dev in CPU GPU NPU; do
	timeout 1500 python bench_device.py "$EXPORT_DIR" "$dev" 10 > "bench_$dev.log" 2>&1
done
```

Padim parity, after `uv run --extra anomaly sorter-anomalib-smoke --workdir "$WORKDIR"`:

```bash
python anomalib_device_parity.py "$WORKDIR"
```
