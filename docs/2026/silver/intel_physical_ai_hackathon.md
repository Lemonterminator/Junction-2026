# Intel Physical AI Challenge - PDF transcription

Source: [Intel_Physical AI Hackathon.pdf](./Intel_Physical%20AI%20Hackathon.pdf) (15 pages). Transcribed by a GPT-6 Luna sub-agent and reviewed against all rendered pages by the parent agent on 2026-11-13. Transcribed in page order. Text on image-based slides was transcribed from rendered pages. Line wrapping, heading hierarchy, and multi-column reading order are normalized; trademark symbols, non-visible slide-editor guide instructions, repeated page numbers, copyright lines, and logos are omitted. QR codes are noted as visual elements; they have not been decoded. The PDF contains no URI link annotations.

## Page 1 - Intel Physical AI Challenge

**Stop Simulating, Start Moving: See It. Detect It. Act on It. The Intel Physical AI Challenge**

**Visual description:** Industrial robotic-arm cover illustration with the Intel logo and challenge title.

## Page 2 - Intel x Ignite Next Hackathon Support Team

Names, arranged left to right by row:

- Albert van Houten
- Daniil Lyakhov
- Jayabalaji Sathiyamoorthi
- Olinca Beltran
- Rajesh Gangireddy
- Ada Betancourt
- Marvin Mueller
- Ricky Watts

**Visual description:** Eight headshots arranged in two rows of four, with each name below its portrait.

## Page 3 - Intel's Challenge Overview

Build an end-to-end Physical AI solution for robotic defect detection and intelligent manipulation using the Intel Physical AI Studio, Anomalib, and OpenVINO software stack.

Participants will design a robotics workflow that combines Vision-Language-Action (VLA) capabilities through Intel Physical AI Studio with Anomalib-based visual anomaly and defect detection.

The solution should enable the robot to perceive objects, identify defects, reason about the required action, and execute the appropriate manipulation task.

The completed solution will then be optimized and deployed on Intel Core Ultra Series 3 using OpenVINO, leveraging available CPU, GPU, and NPU acceleration to improve inference performance, latency, and deployment efficiency.

**Primary task:** Distinguish acceptable ("perfect") from anomalous ("defective") objects, then physically sort or otherwise respond according to the rules revealed at kickoff.

**Closed-loop sequence:** PERCEIVE -> DETECT -> REASON -> ACT -> OPTIMIZE and demonstrate the entire pipeline.

## Page 4 - Required Technology Stack

1. **SO-101 Robotic Arm**
   - Physical manipulation platform used to execute the challenge task. The arm closes the loop from AI perception and reasoning to real-world action.
2. **Intel Physical AI Studio**
   - Design and integrate the VLA-based robotics workflow, connecting perception, task reasoning, robot control, and application orchestration.
   - Label: VLA WORKFLOW
3. **Anomalib**
   - Provide visual anomaly and defect detection, producing defect decisions and localization signals that can be consumed by the VLA / robot workflow.
   - Label: DEFECT DETECTION
4. **OpenVINO + Intel Core Ultra Series 3**
   - Optimize and deploy supported AI workloads with OpenVINO. Map inference across the integrated NPU, GPU, and CPU to improve latency and on-device efficiency.
   - Label: OPTIMIZE + DEPLOY

**Visual description:** Four numbered technology cards in a two-by-two grid; a photograph of an SO-101 robotic arm appears in the first card.

## Page 5 - End-to-End Technical Workflow

The solution is a closed-loop robotics pipeline: perception identifies defects, VLA reasoning determines the required response, the robot executes the action, and OpenVINO optimizes deployment for Intel on-device compute.

1. **PERCEIVE** - Camera input and object observations
2. **DETECT** - Anomalib anomaly score / localization
3. **REASON** - VLA task reasoning in Physical AI Studio
4. **ACT** - SO-101 executes the manipulation response
5. **OPTIMIZE** - OpenVINO deployment on Core Ultra 3

## Page 6 - Technical Implementation Expectations

### 1. Perception & Defect Detection

Capture object imagery from the robot workspace and apply Anomalib to identify anomalous or defective objects. The defect output should be available to the downstream robotics policy as a structured signal, label, score, or localized region.

### 2. VLA Reasoning & Task Planning

Use Intel Physical AI Studio to construct the VLA-driven application flow. The VLA layer interprets the task instruction and perception results, determines the appropriate response, and produces the action intent required by the robot controller.

### 3. SO-101 Robot Execution

Convert the selected action into executable robot behavior on the SO-101 arm. The implementation should connect AI decisions to robot motion, grasping, sorting, or other challenge-specific manipulation actions.

### 4. OpenVINO Optimization

Optimize supported models and inference stages with OpenVINO. Teams should consider model conversion, precision, graph optimization, preprocessing / postprocessing efficiency, and device selection to reduce end-to-end latency.

### 5. Intel Core Ultra Series 3 Deployment

Deploy the optimized solution on Intel Core Ultra Series 3. Use the integrated NPU, GPU, and CPU according to workload characteristics and operator support, while maintaining reliable robot control and application responsiveness.

### 6. Closed-Loop Demonstration

Demonstrate the full sequence from image acquisition and defect detection through VLA reasoning and physical robot action, followed by a concise explanation of the architecture and optimization decisions.

## Page 7 - Judging Criteria

Solutions will be evaluated on technical integration, robotics execution, and efficient Intel deployment.

| Criteria | Description | Points (100) |
|---|---|---:|
| End-to-End Physical AI Solution | Demonstrates a complete workflow from visual perception and defect detection through decision-making and robotic action using the SO-101 arm. The solution should operate as one integrated closed-loop system rather than as independent component demonstrations. | 25 |
| Defect Detection with Anomalib | Effective use of Anomalib for visual anomaly and defect detection. Evaluation considers detection quality, model integration, handling of normal versus defective objects, and how defect outputs are exposed to and consumed by the downstream robotics workflow. | 20 |
| VLA & Physical AI Studio Integration | Demonstrates effective use of Intel Physical AI Studio and VLA-based reasoning to translate perception results and task instructions into appropriate robot actions. Integration across perception, reasoning, planning, and manipulation should be clearly demonstrated. | 20 |
| OpenVINO & Intel Core Ultra Series 3 Optimization | Optimizes and deploys supported AI workloads with OpenVINO on Intel Core Ultra Series 3. Evaluation considers inference latency, throughput, deployment efficiency, and appropriate use of the integrated NPU, GPU, and CPU for the implemented workload. | 20 |
| Robotic Execution & Reliability | Quality and robustness of SO-101 execution, including object localization, manipulation accuracy, repeatability, stable task completion, and recovery from incorrect or uncertain defect detections during the Challenge Day demonstration. | 10 |
| Innovation & Technical Demonstration | Originality of the approach, effective use of Intel technologies, overall technical completeness, and clarity of the live demonstration, system architecture, and optimization decisions. | 5 |
| **Total** | Overall Challenge Score | **100** |

## Page 8 - HW/SW at-a-Glance

### Hardware

- **Compute: one of either of the below**
  - HP OmniBook Ultra (C2NM8AV) Intel Core Ultra X9 Series 3 (388H) AI PC
  - Dell XPS 16 [DA16260] Intel Core Ultra X9 Series 3 (388H) AI PC
- **Arm:** LeRobot SO-ARM101 robotic arm; assembled 1 Leader + 1 Follower + 1 wrist camera
- **Cameras:** one (1) RealSense Depth Camera 415 and one (1) Pro QHD 2K/60fps Webcam
- **Additional equipment:** camera desk mounts, USB Hub, Legos/bowls, robot safety printed guidelines

### Software

- **Needs to be installed as part of the challenge**
  - Physical AI Studio
  - AnomaLib v2.7.0
- **Pre-installed SW:** Ubuntu v26.04, NPU Driver, iGPU Driver
- **Training:** GPU Cloud Instance provided via Modal

**Visual description:** Photographs show the robot setup and sample objects. A QR code is displayed; its destination was not available as a PDF link annotation and has not been decoded.

## Page 9 - End Goal

**Diagram flow, left to right:**

1. **ACT** - Robot acts on the objects.
2. **Anomalib** - The robot/camera workspace observes an object for anomaly detection.
3. **SmolVLA** - The workflow branches to two outcomes:
   - Defective objects
   - Perfect objects

### What Teams Must Deliver

- Working Physical AI prototype: closed-loop SO-101 solution from perception to action.
- VLA + Anomalib integration: VLA robotics workflow with visual anomaly / defect detection.
- OpenVINO-optimized deployment: optimized inference pipeline on Intel Core Ultra Series 3.
- Live demonstration: execute the Challenge-Day task and explain the architecture and optimization choices.

**Visual description:** A left-hand robot-workspace photograph leads via an arrow labeled ACT to a central photograph labeled Anomalib. Arrows then branch toward two photographs labeled Defective objects and Perfect objects; SmolVLA is written near the branching area. These labels and their placement describe the illustration, not an additional prescribed execution architecture.

## Page 10 - Happy Hacking

https://developer.robotics.intel.com

### Build Intelligent Robotics at the Edge

Build intelligent robots faster with Robotics AI Suite. Pre-validated components, specialized reference applications, and hardware-aware optimizations help you integrate AI perception with deterministic control, optimize workloads across Intel CPUs, GPUs, and NPUs, and scale from prototype to production.

- Accelerate development for all kinds of robotics
- Innovate and scale fast with an open ecosystem
- Reduce Complexity, Improve TCO

### Explore the Intel Robotics Ecosystem

- **Intel Robotics** - See how Intel enables intelligent robotics solutions
- **Open Edge Platform** - Discover the modular AI software stack behind the Robotics AI Suite
- **Edge AI Systems** - Explore validated edge AI systems to scale robotics deployments

**Visual description:** Left side says "Happy Hacking," shows the developer URL, and includes a QR code. The right side shows the promotional copy and three ecosystem links/cards. QR destination was not available as a PDF link annotation and has not been decoded.

## Page 11 - End-to-End Physical AI Workflows

A universal runtime that connects models, backends, and robots to standardize and scale deployment.

### Physical AI Studio

#### Fine-tune imitation learning

- **Imitation Learning:** teach robots to perform tasks through from human demonstrations
- **State-of-the-Art Policies:** run ACT, SmolVLA, GR00T, LeRobot and Pi0.5 with support for Hugging Face
- **Low-code visual interface:** build physical AI workflows in an intuitive 3D experience

### Robotics AI Suite

#### Standardize workflows

- **Plug-and-play integration:** calibrate data from diverse inputs with integrations across diverse hardware set-ups
- **ROS 2 Ready:** optimized workflows, reference applications and demos, with SLAM and control libraries
- **Hardware integration:** eliminate need to build foundational plumbing from scratch with support for DevKits, Inputs

### OpenVINO Physical AI Framework

#### Deploy VLA policies to production

- **Inference to production:** in a few lines of Python
- **Heterogeneous compute:** optimized for Intel Core and Intel Core Ultra processors with CPU, built-in GPU, and NPU; processing what each engine does best automatically
- **Sustain deterministic control loops** with asynchronous and real-time chunking even as model complexity scales

**Visual description:** Three columns pair Physical AI Studio with fine-tuning imitation learning, Robotics AI Suite with standardized workflows, and OpenVINO Physical AI Framework with deployment of VLA policies to production.

## Page 12 - Physical AI Studio

Open-source, end-to-end framework to simplify development of Intel-optimized Physical AI models. Leverages emerging techniques, e.g., imitation learning, and streamlines the entire VLA lifecycle - from robot calibration and data collection, through model fine-tuning, to optimized model export for inference on Intel.

Learn more: https://github.com/open-edge-platform/physical-ai-studio/

### Key Features

- Data collection based on imitation learning
- Simple / modular API and CLI for training, inference, and benchmarking Vision-Language-Action policies
- Export models to OpenVINO, ONNX, or Torch formats for accelerated inference
- Benchmark policies on standardized simulation environments like LIBERO and PushT
- Unified inference API across all export backends

### Supported Policies

- ACT
- SmolVLA
- Pi0, Pi0.5
- GR00T N1
- And many more

### Supported Robots

- Trossen WidowX AI
- SO-ARM101
- AlohaMini
- LeKiwi
- And many more

**Visual description:** Three columns show Key Features, Supported Policies, and Supported Robots, in that order. Robot images appear alongside the Supported Robots list.

## Page 13 - OpenVINO Physical AI Framework

**Tagline:** Build once, deploy everywhere. Brought to Physical AI inference and deployment.

### Physical AI Studio/LeRobot/Other workflows

Robot Calibration -> Dataset Collection -> VLA Training -> Optimization -> Export

### OpenVINO Physical AI Framework

Robot State -> Camera -> Observation -> Preprocess -> Infer -> Postprocess -> Robot Action

### Reducing Deployment Brittleness Across Industry

- Unifying cameras, robots, safety in one runtime
- Safety not as afterthought - Action clamping, velocity limits, emergency stops, etc. built into the framework.
- Model predictive control loop, diffusion-based action generation, multi-modal pipelines as modular plugins to runtime
- Enabling deployments to leverage hybrid, as well as asynchronous compute components

## Page 14 - Robotics AI Suite

Adapt and scale physical AI on Intel for fast time to value.

### Accelerate development for all kinds of robotics

- Industrial, service, mobile and humanoid robotics
- Locomotion, Perception, and Imitation Learning
- Run vision AI, media analytics, and Gen AI workloads with real-time controls

### Innovate and scale fast with an open ecosystem

- Validated systems, SDK, and vision AI use cases for accelerate time to value
- Near zero-touch deployment and remote device management
- Rely on Intel's proven long-standing Robotics Expertise

### Reduce Complexity, Improve TCO

- Latest generation processors for best possible performance
- Integrated CPUs, GPUs, NPUs for robotics performance across form factors
- Drive real-time controls & AI/perception from one platform

### SDKs Content

- Vision libraries
- Real-Time Control Frameworks
- AI Inference Engines
- Orchestration-Ready Modules
- Hardware-Aware Tuning
- ROS 2 & Open Standards

**Visual description:** Three stacked advantage groups appear at left, with an SDKs Content list to the right. The central product stack shows Robotics AI Suite above Vision, AI Models, and Control, followed by ROS 2 and Open Standards, Hardware-Aware Tuning, and Intel Core Ultra hardware.

## Page 15 - Intel Core Ultra Processors

All-in-one Compute Platform for real-time control + AI workloads.

**Up to 180 TOPS**

### CPU - Fast Response

- Ideal for low-latency AI workloads via OpenVINO
- Intel Time Coordinated Computing:
  - Resource partitioning (cache/mem)
  - Deterministic power management
  - Cross-silicon time synch (Intel TCC+TSN)

### NPU - Low Power

- Ideal for sustained, complex AI workloads with excellent AI perf/watt efficiency
- 50 TOPS AI compute
- Fast deployment via OpenVINO

### GPU - High Throughput

- Up to 12 Xe3 Cores
- AI deployment via OpenVINO
- Computing acceleration via oneAPI

**Performance footnote:** Performance varies by use, configuration, and other factors. Learn more at intel.com/processor claims: Intel Core Ultra processors, Edge. Results may vary.
