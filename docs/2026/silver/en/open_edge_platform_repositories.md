# Open Edge Platform repository review

Reviewed 2026-11-13. [Organization](https://github.com/orgs/open-edge-platform/repositories?q=sort%3Astars);
[inventory snapshot](../../bronze/intel_open_edge_platform/repositories.json) includes
all 70 public repositories returned at retrieval time, with stars, default branches,
and archive status. Stars are dated observations, not a recommendation criterion.
Capabilities below come from [six pinned READMEs](../../bronze/intel_open_edge_platform/manifest.json).
Proposed uses and integration assessments are analysis, not runtime validation.

| Repository | Documented capability | Proposed project use | Assessment |
| --- | --- | --- | --- |
| [geti-instant-learn](https://github.com/open-edge-platform/geti-instant-learn) | Zero/few-shot visual prompting and segmentation; OpenVINO export with backbone-specific limits | Reference-example object selection and ROIs for Anomalib | First creative experiment; does not generalize grasping by itself |
| [manufacturing-ai-suite](https://github.com/open-edge-platform/manufacturing-ai-suite) | PCB anomaly, pallet defects, pipeline and monitoring samples | Reuse defect event, audit record, and UI patterns | Selective reuse; full stack has many services |
| [edge-ai-sizing-tool](https://github.com/open-edge-platform/edge-ai-sizing-tool) | Custom process CPU/GPU/NPU, memory and disk monitoring, JSON output | Baseline and optimization resource comparison | Useful tool; instrument inference/cycle time separately; Ubuntu 26.04 unverified |
| [dlstreamer](https://github.com/open-edge-platform/dlstreamer) | GStreamer/OpenVINO inference, tracking, MQTT/Kafka outputs | Multi-stream video/event pipeline | Introduce when needed; camera ownership and Studio adapters remain our work |
| [scenescape](https://github.com/open-edge-platform/scenescape) | Shared coordinates, scene graphs, multi-camera tracking and region analytics | Two fixed cameras tracking tabletop and sorting regions | Stretch goal requiring calibration; moving wrist camera is not assumed compatible |
| [robotics-ai-suite](https://github.com/open-edge-platform/robotics-ai-suite) | ACT, Pi0.5, pose estimation, visual servoing, stationary-arm references | Select localization, grasping, and optimization patterns | Check each sample's robot support; not all target SO-101 |

Supporting tools reviewed but without separate README snapshots in this batch:
[Geti](https://github.com/open-edge-platform/geti) for vision annotation/training/deployment;
[Datumaro](https://github.com/open-edge-platform/datumaro) for vision dataset conversion
and validation; [Model API](https://github.com/open-edge-platform/model_api) for vision
inference wrappers, requiring compatible metadata for generic models. These are not
general replacements for LeRobot demonstration episode management.

`geti_v2`, `geti-sdk`, and `edge-ai-tuning-kit` are archived in this snapshot.
`edge-ai-libraries` and `edge-ai-suites` are useful navigation points; verify the
actual component rather than assuming every linked project remains supported.

The organizer's encouragement to use extra repositories is user-supplied context
in the manifest, not independently verified. No evidence says repository count
itself earns points. See [creative options](../../gold/en/intel_physical_ai_creativity_options.md).
