# Hardware profiling: first round

Date: 2026-11-14. Author: linan. Scope: what the Intel workstation's CPU, GPU and NPU do with the
two inference workloads in our loop, SmolVLA and Anomalib Padim. This is a first round on synthetic
inputs. It is not a final benchmark and it does not validate the closed loop.

Scripts: [`scripts/hardware_profiling/`](../../scripts/hardware_profiling/README.md). Access and
machine-specific state stay in the untracked `.local/` folder.

## Scope and safety

- Inference only. No camera was opened, no arm moved, nothing was rebooted and no driver or kernel
  setting changed. The Studio container was not touched.
- Everything ran in a separate user account with its own virtual environments and its own downloads
  (about 2 GB for the SmolVLA checkpoint, a few GB for Anomalib and CPU PyTorch).
- All inputs are fixed-seed random tensors (SmolVLA) or generated images (Padim). Latencies are valid
  for the graph shapes tested. Output quality was not judged on real data.

## Hardware as measured

| Item | Value (OpenVINO 2026.4.1 unless noted) |
| --- | --- |
| SoC | Intel Core Ultra X9 388H (Panther Lake), 16 cores |
| GPU | Arc B390 (Xe3), `GPU_EXECUTION_UNITS_COUNT` 96; FP32, FP16, INT8; default inference precision FP16 |
| NPU | NPU 5 (arch 5010), `NPU_MAX_TILES` 3; FP16 and INT8 only; vendor rating up to 50 INT8 TOPS |
| Memory | Unified: about 61 GiB visible to the host, GPU and NPU report about 57 and 61 GiB from the same pool |
| Drivers | Ubuntu, `xe` GPU driver, `intel_vpu` NPU driver; the test account is in the `render` group |

Unified memory means moving a tensor between devices is a handover inside one pool, not a PCIe copy.
It does not make all three devices equally fast.

## Workload 1: SmolVLA (451M parameters)

Checkpoint: `lerobot/smolvla_base`, exported to OpenVINO FP32 with the Studio export path at the pinned
submodule commit (`export_base.py`). Shapes are the base checkpoint's own: three 512×512 cameras,
chunk 50, 6-D state and action, ten flow-matching steps, noise `[1, 50, 32]` as an explicit graph input.
Our robot will use two cameras (top, wrist); that shape has not been exported yet.

### Static profile (`profile_graph.py`)

32,771 graph nodes; 711.9 GFLOPs of MatMul and Convolution per chunk.

| Block | GFLOPs | Share | Weights (FP32) |
| --- | ---: | ---: | ---: |
| SigLIP vision encoder (3 images × 1024 patches, 12 layers) | 525.5 | 73.8 % | 345 MB |
| Action expert (16 layers, width 720, 10 steps) | 97.4 | 13.7 % | 393 MB |
| Text decoder (16 layers, hidden 960) | 71.4 | 10.0 % | 782 MB (includes embeddings) |
| Connector and other | 17.6 | 2.5 % | 48 MB |

The vision encoder is most of the arithmetic, and it runs once per observation.

### Latency (`bench_device.py`, median of 10 runs, LATENCY hint)

| Graph | CPU (FP32) | GPU (FP16) | NPU (FP16) |
| --- | ---: | ---: | ---: |
| Whole policy | 2268 ms | 86 ms | no result (see below) |
| Vision encoder + connector only | 1435 ms | 23.4 ms | 276 ms (compile 50 s) |

GPU speedup over CPU is about 26× for the whole policy and about 61× for the vision part.

### Findings

1. **The OpenVINO GPU plugin returns wrong ids for `Bucketize`.** The vision position embedding uses it,
   so the GPU vision output was wrong (cosine 0.53 against CPU). Not FP16 and not our patch: with the
   `Bucketize` nodes replaced by the constant ids PyTorch computes for the fixed patch grid
   (`fix_bucketize.py`, which first checks that CPU equals PyTorch), GPU matches CPU with cosine
   1.00000. The ids depend only on the patch grid, so constant folding is valid for a fixed camera
   resolution. This should be reported upstream and to whoever owns the export path.
2. **The NPU compiler rejects `Bucketize` with an i64 output** (`patch_bucketize.py` narrows it to i32).
   With the patch, the whole graph did not finish compiling in 25 minutes and was killed, so there is
   no whole-graph NPU result. The vision-only subgraph compiles in 50 s and runs in 276 ms.
3. **The NPU needs static shapes.** The text decoder and the action expert were not tried separately
   on the NPU.
4. **GPU reference kernels cost about 20 ms of the 86 ms** (`profile_other.py`): `Select` about 10.7 ms
   and `ClampFP16Output` about 9.8 ms. These are unoptimised fallbacks and a concrete optimisation
   target (graph rewrite or a different export of the masking/clamp ops).
5. **An earlier whole-graph GPU-vs-CPU parity of 0.9998 was uninformative.** With random inputs the
   final action output is insensitive to the images. Parity must be checked on the vision output, as
   done after the fix above, or on real observations.

### Pipeline split (vision on NPU, rest on GPU)

Assessed from the numbers above, not implemented. Vision on the NPU takes 276 ms against 23 ms on the
GPU, so a two-stage pipeline would have a period of at least 276 ms and would be slower than the
whole-policy GPU run at 86 ms, for both latency and throughput. Throughput is not the constraint
anyway: a 50-step chunk at 30 Hz is consumed in about 1.7 s, so the control loop needs about 0.6 chunks
per second. Keep the policy on the GPU. The NPU is worth using for a different reason, concurrency.

## Workload 2: Anomalib Padim

Padim, resnet18 backbone (`layer1`, `layer2`), exported with `sorter-anomalib-smoke` on synthetic
images, reshaped to a static 1×3×256×256 input. The comparison used 16 synthetic test images, 8 good
and 8 defect, with CPU as the reference (`anomalib_device_parity.py`). Median of 200 runs.

| Device | Latency | Defect-map correlation with CPU | Mean defect score | Images flagged (good / defect) |
| --- | ---: | ---: | ---: | --- |
| CPU | 5.0 ms | 1.0000 | 0.524 | 0/8 / 5/8 |
| GPU, default (FP16) | 1.4 ms | 0.09 (wrong) | 1.000 | 0/8 / 8/8 |
| GPU, `INFERENCE_PRECISION_HINT=f32` | 9–11 ms | 1.0000 | 0.524 | 0/8 / 5/8 |
| NPU | 6.6 ms | 0.9986 | 0.439 | 0/8 / 0/8 |

Image AUROC was 1.0 on every device.

### Findings

1. **The earlier "GPU 1.5 ms" figure measured speed only, and the default output is wrong.** At FP16
   the anomaly maps barely correlate with CPU and every defect score saturates at 1.0. With FP32 the
   result is identical to CPU but slower than CPU. The cause inside the model (Mahalanobis step or
   normalisation in FP16) was not investigated. For Anomalib, GPU is not useful as it stands.
2. **The NPU produces the right maps but about 16 % lower scores.** Ranking is preserved, but the
   label threshold baked into the exported model is calibrated for CPU scores, so no defect is flagged
   on the NPU. Using the NPU needs a per-device threshold calibrated on real data.
3. **The NPU is not faster than the CPU here** (6.6 against 5.0 ms). Its value is that it is a separate
   engine.
4. The exporter printed an ONNX opset conversion error (`No Adapter To Version $17 for Pad`) during
   export. A valid `model.xml` was still produced.

## What this suggests for device allocation (hypothesis, not a result)

| Task | Suggested device | Reason |
| --- | --- | --- |
| SmolVLA policy | GPU (FP16), `Bucketize` folded | 86 ms measured, 26× over CPU |
| Anomalib Padim | NPU with a recalibrated threshold, or CPU | NPU runs concurrently with the GPU policy; CPU is the safe fallback. Avoid GPU FP16. |
| Capture, control loop, scene detection | CPU | Needs predictable timing and no device contention |

Running Anomalib on the NPU while the VLA runs on the GPU has not been measured. Concurrent latency,
shared-memory contention and power are all open.

## Limits and risks

- Synthetic data only. Padim scores and thresholds say nothing about real parts; the CPU itself flags
  only 5 of 8 synthetic defects at the stored threshold.
- SmolVLA ran with the base checkpoint's three-camera shapes and generic normalisation statistics, not
  our robot's two cameras and dataset statistics, and with random inputs.
- No quantisation (INT8, NNCF) was tried, so none of the NPU or GPU INT8 paths are measured.
- Whole-graph NPU compile is unconfirmed rather than known to fail.
- Latencies are medians of 10 (SmolVLA) and 200 (Padim) runs on an otherwise idle machine; the GPU FP32
  Padim figure varied between 9 and 11 ms across two runs.
- Configuration, build, runtime and hardware checks are reported separately on purpose: a model that
  compiles on a device has not been shown to be correct on it, as the two GPU findings show.

## Next steps

1. Report the GPU `Bucketize` bug upstream and to the VLA training session; fold the ids in our export.
2. Re-export SmolVLA with our two-camera shapes and our dataset statistics, then compare CPU and GPU on
   real recorded observations, not random tensors.
3. Try the text decoder and the action expert on the NPU separately, and INT8 for the policy.
4. Address the `Select` and `Clamp` reference kernels on the GPU.
5. Re-run Padim on real good-object captures; calibrate the NPU threshold; investigate the GPU FP16
   failure or document FP32/CPU as the supported path.
6. Measure Anomalib on the NPU concurrently with the policy on the GPU, with the capture loop running.

## Update 2026-11-15 — Real-observation FP16, NPU contention & async pipeline follow-up

See [ASYNC_PIPELINE_BENCHMARK.md](ASYNC_PIPELINE_BENCHMARK.md) for the second-round hardware run (`scripts/hardware_profiling/bench_async_pipeline.py`) addressing items 1, 2, 5, and 6 without touching `/dev/ttyACM*` or USB `/dev/video*` cameras (reading live `:8092` `depth_bridge` streams and recorded `sort-depth-v2-10k` observations, precision reduction capped at FP32 → FP16):

- Folded `2` `Bucketize` ops in the `sort-depth-v2-10k-candidate` SmolVLA IR and compressed weights to FP16 (`compress_to_fp16=True`: PaDiM `2.00×`, PatchCore `1.9992×`, SmolVLA `.bin` `1.0083×`).
- **SmolVLA `sort-depth-v2` on GPU FP16** ran at **149.43 ms** median (`smolvla_fp32` IR) and **153.86 ms** (`smolvla_fp16` IR, p95 `156.54 ms`), vs **3889.83 ms** on CPU FP32 (~26× speedup), with `cosine_similarity >= 0.99991` and preserved green vs pink task action separation.
- **PaDiM on 8 real held-brick crops** (`4` normal, `4` defective): `GPU_f16` did not collapse on real crops (`1.776 ms` median, `0.999996` correlation vs CPU FP32, `8/8` accuracy) and `NPU_f16` matched CPU FP32 (`10.923 ms` median, `1.0` correlation, `8/8` accuracy); PatchCore failed NPU compilation (`ZE_RESULT_ERROR_INVALID_ARGUMENT`). Larger held-out validation-set parity for PaDiM `GPU_f16` remains open.
- **Concurrent GPU + NPU + CPU**: running `smolvla_fp16` (`GPU_f16`) alongside `padim_fp16` (`NPU`) and live `:8092` HTTP capture added only `+2.43 %` inspection overhead and `+3.57 %` VLA overhead vs solo runs; wrapping execution in `AsyncChunkPolicy` + `AsyncInspectionStage` reduced steady-state `policy.act()` latency to **0.0071 ms** median (`p95 = 0.0309 ms`) vs **193.78 ms** (`5.16 Hz`) synchronous serial end-to-end.
