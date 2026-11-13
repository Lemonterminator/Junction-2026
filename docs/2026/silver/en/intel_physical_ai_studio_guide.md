# Physical AI Studio: Junction 2026 operational guide summary

Reviewed 2026-11-13. [Original snapshot](../../bronze/intel_open_edge_platform/JUNCTION2026.md)
and [provenance](../../bronze/intel_open_edge_platform/manifest.json). The Studio
`junction2026` branch is pinned at `17714488fa9c7d098a056da83f7c220cf983957d`.
This summary does not replace the source or on-site rules.

## Statements in the guide

- Build a closed-loop SO-101 inspection, defect detection, and sorting system on
  an Intel Core Ultra AI PC. Actual objects, defects, and rules are revealed at kickoff.
- Native startup: run `uv run --extra xpu physicalai-studio serve` in
  `application/backend`; run `npm install` then `npm run start` in `application/ui`.
  Backend: 7860; UI: 3000. Docker is an alternative, serving the combined app on 7860.
- Create a project, robots, cameras, and an environment in Studio.
- The guide states $100 of Modal training credit per participant, redeemed as the
  organizers instruct. Authenticate the backend, not just the browser, then deploy
  and connect the Modal Provider. A10G/A100/H100 prices differ; closing Studio does
  not stop billing for running jobs. Maximum job duration is 24 hours.
- Use a personal read-only HF token for Hub-backed policies such as SmolVLA/Pi0.5.
- Keep Anomalib in its own environment to avoid PyTorch conflicts. The guide
  recommends local Intel XPU anomaly training and Modal policy training. Most
  anomaly models use good images; include ordinary variation in that training set.
- The demonstration/training UI supports ACT, SmolVLA, and Pi0.5. Language-task
  support differs by policy, affecting the detection-to-action interface.
- Studio does not implement anomaly detection. Teams must connect detection to
  autonomous action. Suggested components are OpenVINO PhysicalAI `InferenceModel`
  and the Anomalib OpenVINO inferencer.
- Measure inference-step latency, sorting-cycle time, power, and temperature;
  explain CPU/iGPU/NPU workload assignment.

## GitHub guide rubric (100 points)

| Criterion | Points | Focus |
| --- | ---: | --- |
| Task Success Rate | 25 | Accuracy, cycle time, shifted objects and clutter |
| Intel Tech Integration | 25 | NPU/iGPU, OpenVINO, Robotics AI Suite |
| Dataset & Pipeline Quality | 20 | Clean demonstrations and Studio fine-tuning |
| System Efficiency | 20 | Inference latency, thermal headroom, power |
| Creativity | 10 | Original ideas beyond the baseline |

The [PDF transcript](../intel_physical_ai_hackathon.md) contains a different
six-category rubric on p.7. Neither source has been established as the final
authority; retain both and ask organizers to resolve the conflict.

## Repository configuration observations (not guide text)

At the pinned revision, the backend requires Python >=3.13,<3.14. The UI deployment
guide lists CPU/GPU inference. The Dockerfile supplies CPU/XPU/CUDA build targets
and requires a named `libs` context. Export capability does not establish that a
model runs on every device. See the project's [Docker instructions](../../../infrastructure/DOCKER.md).
Hardware and models have not been runtime-validated during this integration.
