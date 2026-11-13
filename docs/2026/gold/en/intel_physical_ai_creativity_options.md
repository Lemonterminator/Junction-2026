# Intel Physical AI: creative options and implementation order

Updated 2026-11-13. Based on the [repository review](../../silver/en/open_edge_platform_repositories.md)
and [event guide](../../silver/en/intel_physical_ai_studio_guide.md). Everything below
is a proposal; no algorithm integration, real-model benchmark, or robot validation
has been completed.

## First experiment: show an example, inspect and sort similar objects

Reference selection -> Instant Learn segmentation -> Anomalib object-ROI inspection
-> action selection -> Studio-trained policy -> SO-101 sorting -> observe the result.
Show the reference, masks, anomaly heatmap, action decision, and outcome together.

Start with a class the policy already grasps reliably. Few-shot segmentation does
not teach new shapes or poses to the grasping policy. Keep cropping/resizing and
normal-image training consistent with inference; changing ROIs can change the anomaly
distribution. Record segmentation confidence, anomaly score, and grasp outcome
separately instead of merging them into an uncalibrated confidence value.

Validate recorded-frame segmentation first, compare full-frame/ROI anomaly results,
then measure sorting success, shifted/cluttered scenes, inference latency, and
complete cycles to establish an actual benefit.

## Supporting tool: measured Intel optimization

Use Edge AI Sizing Tool process monitoring or CLI output alongside application
timers and task outcomes. Compare CPU and supported GPU/NPU configurations using
the same inputs, policy, and scene; record model, device, precision, warmup, and
sample counts. Utilization alone does not prove energy savings or faster sorting;
power and temperature need available measurement sources. Ubuntu 26.04 and new
hardware support remain unverified.

## Stretch goal: multi-view tabletop state

After the baseline works, evaluate Scenescape with calibrated fixed cameras to track
objects moving between inspection, accepted, and rejected regions. Multi-camera
fusion does not guarantee grasp-level coordinate accuracy: measure calibration
error and latency. Moving wrist-camera poses need separate evaluation.

An independent behavior to explore is reinspection from a demonstrated viewpoint
when detection is uncertain. We must implement the state machine, poses, retry limit,
and failure handling; Scenescape does not automatically supply this behavior.

## Implementation order and gates

1. Start Studio; calibrate, record, train, and run the policy to validate the toolchain.
2. Establish normal-image/threshold baselines and autonomous sorting with outcome
   observation; handle uncertainty by stopping or reinspection.
3. Add Instant Learn only after a useful small offline experiment; retain the baseline
   input path if the extension fails.
4. Capture performance comparisons and demo evidence. Add multi-camera fusion or
   streaming infrastructure only with a stable loop and remaining time.

This order follows engineering dependencies and demo value, not assumed scores from
conflicting rubrics. Proposed integration code belongs in this project's `src/`;
no controller implementation exists yet.
