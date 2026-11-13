# Intel Physical AI Challenge: analysis and execution guidance

> Updated: 2026-11-13. Sources: [Silver page-by-page transcript](../../silver/intel_physical_ai_hackathon.md), [original PDF](../../silver/Intel_Physical%20AI%20Hackathon.pdf), 15 pages, and the supplementary [GitHub event guide](../../silver/en/intel_physical_ai_studio_guide.md). Sections 1–7 retain PDF attribution; section 8 records GitHub additions and conflicts. Recommendations are analysis. On-site equipment, model compatibility, and robot execution have not been independently validated.

## 1. Confirmed challenge

**Stop Simulating, Start Moving: See It. Detect It. Act on It. The Intel Physical AI Challenge** calls for an end-to-end robotics solution for defect detection and intelligent manipulation. Distinguish acceptable (perfect) objects from anomalous (defective) objects, then physically sort or otherwise respond under the rules revealed at kickoff. (PDF pp.1, 3)

Demonstrate the complete loop: **PERCEIVE -> DETECT -> REASON -> ACT -> OPTIMIZE**. Intel Physical AI Studio supplies the VLA workflow, Anomalib supplies defect decisions and localization, SO-101 performs physical actions, and OpenVINO optimizes and deploys supported inference workloads on Intel Core Ultra Series 3. (pp.3-6)

The Intel x Ignite Next support team appears on p.2. This brief makes the earlier generic Hardware Lab description more specific. Bronze predictions about oneAPI, SLAM, incubation, or prizes are not confirmed requirements or commitments for this challenge.

## 2. Technical requirements and resources

| Stage | Requirement stated in the brief | Pages |
| :--- | :--- | :--- |
| Perception and detection | Capture workspace images; expose Anomalib output as a structured signal, label, score, or localized region to downstream robotics | 4-6 |
| Reasoning and planning | Use Physical AI Studio for a VLA flow that interprets instructions and perception results, selects a response, and produces action intent for the controller | 4-6 |
| Physical execution | Convert decisions into SO-101 motion, grasping, sorting, or challenge-specific manipulation | 4-6 |
| Optimization | Consider conversion, precision, graph optimization, preprocessing/postprocessing, and device selection to reduce end-to-end latency | 6 |
| Deployment | Deploy on Core Ultra Series 3; use NPU, GPU, and CPU according to workload characteristics and operator support, preserving reliable control and responsiveness | 6 |
| Demonstration | Show acquisition, detection, VLA reasoning, and physical action; explain architecture and optimization decisions | 6, 9 |

The following are configuration claims recorded on p.8:

- One compute option: HP OmniBook Ultra (C2NM8AV) or Dell XPS 16 [DA16260], both labeled Intel Core Ultra X9 Series 3 (388H) AI PCs.
- LeRobot SO-ARM101: assembled 1 Leader + 1 Follower + 1 wrist camera.
- One RealSense Depth Camera 415 and one Pro QHD 2K/60fps Webcam; camera mounts, USB hub, Legos/bowls, and printed robot safety guidelines.
- Install Physical AI Studio and AnomaLib v2.7.0. Preinstalled: Ubuntu v26.04, NPU driver, iGPU driver. Training: GPU cloud instance provided via Modal.

The source uses both SO-101 and SO-ARM101; both spellings are retained. ACT and SmolVLA appear in the p.9 illustration. Other policies and robots on pp.11-12 describe platform capabilities, not a requirement to implement every policy or support every robot.

## 3. PDF judging rubric: 100 points (final authority unconfirmed)

| Criterion | Points | Evidence emphasized | Page |
| :--- | ---: | :--- | :--- |
| End-to-End Physical AI Solution | 25 | One integrated SO-101 loop from visual detection through decisions to action | 7 |
| Defect Detection with Anomalib | 20 | Detection quality, model integration, normal/defective handling, and consumption of outputs downstream | 7 |
| VLA & Physical AI Studio Integration | 20 | Visible integration of perception, instructions, reasoning, planning, and manipulation | 7 |
| OpenVINO & Intel Core Ultra Series 3 Optimization | 20 | Latency, throughput, deployment efficiency, and appropriate NPU/GPU/CPU use | 7 |
| Robotic Execution & Reliability | 10 | Localization, accuracy, repeatability, stable completion, and recovery from incorrect or uncertain detections | 7 |
| Innovation & Technical Demonstration | 5 | Originality, Intel technology use, completeness, and clear live architecture/optimization explanation | 7 |
| **Total** | **100** | | |

**PDF-only analysis: the first four criteria total 85 points, emphasizing integration, detection, VLA, and deployment optimization.** The GitHub guide has a different rubric; this point distribution is not established as final. The PDF emphasizes integrated system performance. (p.7; see section 8.)

## 4. Execution recommendations (analysis, not extra official requirements)

1. **Complete a minimal loop first.** Start with one object in a fixed workspace and connect capture, Anomalib, VLA, SO-101 action, and OpenVINO deployment. Observe the physical result in the next iteration.
2. **Make handoffs inspectable.** Record images, defect scores/labels/regions, task instructions, VLA action intent, execution results, and timestamps so judges can see how detection influences action.
3. **Measure a baseline before optimization.** Compare inference latency, end-to-end time, throughput, and task completion rate on the same input/task. Record device, precision, and workload. Assign supported workloads to CPU/GPU/NPU; using all three simultaneously is not stated as a requirement.
4. **Gather reliability evidence.** Test normal, defective, uncertain, and failed-grasp cases, showing safe stopping or recovery. Page 13 describes framework action clamping, velocity limits, and emergency stops; confirm actual on-site setup and procedures.
5. **Polish the demonstration after integration.** Explain the architecture, detection evidence, VLA action choice, and measured optimization benefit through one real task sequence before adding optional features.

These metrics and implementation details are proposed self-checks. The PDF does not specify minimum accuracy, latency thresholds, a mandatory policy model, or mandatory use of every compute engine.

## 5. Four required deliverables

Page 9 explicitly lists:

1. A working closed-loop SO-101 Physical AI prototype from perception to action.
2. VLA robotics workflow integrated with Anomalib visual anomaly/defect detection.
3. OpenVINO-optimized inference deployment on Intel Core Ultra Series 3.
4. A live Challenge-Day task demonstration with an explanation of architecture and optimization choices.

## 6. Open questions for the event

- Actual objects, defect definitions, sorting rules, and other kickoff / Challenge-Day task rules. (pp.3, 9 explicitly defer to the event task.)
- Assigned computer, camera placement, calibration status, and equipment access arrangements.
- Physical AI Studio / OpenVINO versions, policy export and operator support, and working drivers.
- Training data, actual Modal credit redemption and instance access, and network access. The PDF only states that a GPU cloud instance is provided; GitHub credit/time statements appear in section 8 and redemption is unverified.
- Prizes, submission format, deadlines, and detailed safety procedures; the brief does not fully specify these, and Bronze predictions do not fill the gap.

## 7. Reference entry points in the source

- Intel Robotics: <https://developer.robotics.intel.com> (p.10).
- Physical AI Studio: <https://github.com/open-edge-platform/physical-ai-studio/> (p.12).

These references are reproduced from the PDF; Physical AI Studio was subsequently read online and integrated as a pinned submodule.

## 8. GitHub guide additions and source conflict

Source: [pinned original](../../bronze/intel_open_edge_platform/JUNCTION2026.md),
Studio `junction2026` commit `17714488fa9c7d098a056da83f7c220cf983957d`.

| GitHub criterion | Points |
| --- | ---: |
| Task Success Rate | 25 |
| Intel Tech Integration | 25 |
| Dataset & Pipeline Quality | 20 |
| System Efficiency | 20 |
| Creativity | 10 |
| **Total** | **100** |

GitHub groups judging into success, Intel integration, dataset/pipeline, efficiency,
and creativity. Creativity is 10 points, while the PDF's differently scoped
Innovation & Technical Demonstration category is 5. These are not direct one-to-one
replacements. File recency alone does not establish precedence; organizers must
confirm the final rubric.

The guide states $100 Modal credit per participant, redeemed as instructed, with a
24-hour maximum per job. It recommends isolated Anomalib/local XPU training, lists
ACT/SmolVLA/Pi0.5 demonstration training, and leaves detection-to-action integration
to teams. These are source statements, not proof of redeemed credit or a running system.

The full upstream source and Docker configuration are now integrated; see the
[Docker guide](../../../infrastructure/DOCKER.md). See [creative options](intel_physical_ai_creativity_options.md)
for proposals and sequencing; no robot validation has been completed.
