# Anomaly detection on real recordings: first baseline

Date: 2026-11-15. Author: linan. Data: Studio dataset `sort-depth-v2` (`af9b173a-…`, 35 episodes, 23 green bowl,
12 pink bowl), copied read-only from the workstation. No camera was opened and no arm moved; training ran on the
CPU and, for PatchCore, on the RTX 5090 of the Windows PC in a separate CUDA environment.

Script: [`scripts/anomaly/real_baseline.py`](../../scripts/anomaly/real_baseline.py). Outputs (crops, scores,
models) stay in the Git-ignored `artifacts/anomaly/`.

## Defect and labels

A brick is defective when it is not one solid colour (`memory/DECISIONS.md`, 2026-11-15). The recorded defective
bricks carry scraps of grey duct tape on any face. Labels come from the task text: green bowl = normal, pink bowl =
defective. The task text labels the episode, not each view.

## Pipeline

1. **Held-brick frames.** `episodes.find_hold` takes the longest run with the gripper reading in 8.5–26 (closed on
   a brick; an empty close reads 2–8, open 30–90). 20 evenly spaced wrist frames from 1.0 s after the start of the
   hold to 1.5 s before its end.
2. **Brick isolation.** `inspection.isolate_object`: saturated pixels without the blue jaw hue, the component nearest
   the expected brick position, its convex hull plus a fixed core ellipse where the held brick always sits, dilated
   3 px, everything else set to grey 128. The table is covered in the same grey tape, so the brick is cut out rather
   than tape removed. The core keeps tape that covers a whole side (the hull of coloured pixels alone cut it off).
   Frames whose brick box is more than 70 px from the usual position, or outside 150–360 px, are dropped (bowl in
   view, brick half-lifted). Result: 612 crops from 35 episodes.
3. **Scores.** Padim (resnet18, layers 1–2), PatchCore (wide_resnet50, layers 2–3, 10 % coreset), both exported to
   OpenVINO and scored with `OpenVinoScorer`; and `off_colour_fraction`, the share of brick pixels that are not its
   dominant hue (grey, dark or another hue), with no training.
4. **Evaluation.** Episodes dealt into 5 folds, stratified by label (`grouped_folds`). For fold *i*: test on fold
   *i*, threshold chosen on fold *i*+1 (`choose_threshold`, best balanced accuracy, ties to the lower threshold),
   model fitted on the normal episodes of the other three folds. Every episode is tested exactly once and never
   seen in fitting or thresholding. Episode score = median of its frame scores (the max was also tried; it adds
   false alarms for every method).

## Results (episode level, all 35 episodes tested once)

| Method | Defects caught | Normals passed | Frame AUROC per test fold | Latency per crop |
| --- | ---: | ---: | --- | --- |
| PatchCore 10 % | **11 / 12** | 14 / 23 | 0.76, 0.85, 0.74, 0.64, 0.90 | CPU 306 ms, Intel iGPU 136 ms |
| Colour purity | 7 / 12 | **17 / 23** | 0.62, 0.93, 0.96, 0.56, 0.91 | CPU 0.7–1.9 ms |
| Padim | 9 / 12 | 11 / 23 | 0.74, 0.64, 0.58, 0.69, 0.59 | CPU 4.0 ms, Intel iGPU 1.8 ms |

Latency is the median of 200 OpenVINO calls on the Windows PC (Core Ultra CPU, Intel iGPU as `GPU.0` with the
f32 hint) including resize; the PatchCore export has a fixed batch of 2, so each call scores the crop twice. The
Intel workstation's NPU was not measured in this round.

Missed defects: PatchCore `ep034`; colour purity `ep025`, `ep027`, `ep031`, `ep032`, `ep034`; Padim `ep025`,
`ep028`, `ep032`. False alarms concentrate on yellow, lime and teal bricks (`ep015`–`ep021`), colours with few
normal training episodes (episodes 0–9 are all one orange brick).

An earlier round without the core ellipse and frame gate (310 crops, 31 episodes, max score) gave Padim test AUROC
0.56–0.77 with 13 of 21 normals flagged.

## What the numbers mean

- **About half the defective episodes show no tape to the wrist camera.** Judged by eye from the crops, the tape is visible
  in `ep023`, `ep024`, `ep026`, `ep028`, `ep029`, `ep030`, `ep033`; in `ep025`, `ep027`, `ep031`, `ep032`, `ep034`
  it is on a face the jaws cover or that faces away. Colour purity misses exactly those five, which is the
  physically expected result. One wrist view cannot meet a "no missed defect" goal.
- **PatchCore also flags episodes without visible tape, so part of its score may not be the defect.** All 23 normal
  episodes were recorded before all 12 defective ones (episode index 0–22 against 23–34), so lighting, background
  and brick handling differ by session as well as by label. Until normal and defective bricks are recorded
  interleaved, a high PatchCore score on an invisible-tape episode cannot be credited to the tape.
- **35 episodes are a small test.** One episode moves a rate by 3–9 points. These are first baselines, not
  accuracy claims.
- **Latency:** Padim and colour purity fit any loop budget; PatchCore at 136–306 ms per view does not need the
  NPU to be useful but is the slowest stage after the policy.

## Next steps

1. Use the inspection recordings (`a9ea91fe-…`, "show it to the front camera", 38 episodes): tape faces a camera on
   purpose. They need per-episode labels first; the task text does not carry them.
2. Record normal and defective bricks interleaved, with all five colours, so labels stop correlating with session.
3. Combine views per brick (wrist plus front) before deciding; keep "uncertain" when no view shows the faces.
4. Export PatchCore with batch 1 and a smaller memory bank, then measure CPU, GPU and NPU on the workstation;
   calibrate the threshold per device.
