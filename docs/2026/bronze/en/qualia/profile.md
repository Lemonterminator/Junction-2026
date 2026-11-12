# Qualia (Qualia Studios) — Junction 2026 Partner In-Depth Research Report

> **Partner Badges**: Junction 2026 Bronze Tech Partner  
> **Company Tags**: Robotics Foundation Models | Embodied AI | Robotics GPU Cloud  
> **Report Archive Paths**: `bronze/en/qualia/profile.md` & `docs/2026/bronze/en/qualia/profile.md`  

---

## 1. Company Overview

| Metric / Attribute | Detailed Information |
| :--- | :--- |
| **Full Corporate Name** | Qualia Studios ApS (Commercial Brand: Qualia / Qualia Studios) |
| **Official Website** | [qualiastudios.dev](https://qualiastudios.dev) |
| **Headquarters Location** | Copenhagen, Denmark |
| **Founding Year** | 2025 |
| **Founding Leadership** | - **Fabian Kerj** (Co-Founder & CEO, veteran tech and executive leader across Nordic scale-ups)<br>- **Oscar Cortina** (Co-Founder & Technical Lead)<br>- **Max Fällström** (Co-Founder & Infrastructure Lead)<br>- **Ludvig Brangstrup** (Co-Founder & Research Lead) |
| **Financing & Capital Raised** | **Seed Round completed at €7.5M (approx. $8.0M–$8.7M USD)** |
| **Key Institutional Investors** | **BlackWood**, **Wave Ventures**, **Heartcore Capital**, **The Nordic Web Ventures**, **Florent Venture Partners**, alongside strategic and angel backing led by **Perplexity** |
| **Core Engineering DNA** | Frontier robotics foundation models, distributed GPU compute orchestration, physics simulation, and multimodal embodied action policy development |

---

## 2. Core Products & Technical Architecture

### 2.1 Core Platform: Qualia Robotics Cloud Platform
Qualia has architected a dedicated R&D cloud platform engineered specifically for physical intelligence researchers and embodied AI engineers, structured across four robust layers:

```
+---------------------------------------------------------------------------------+
|                       Qualia Embodied Developer Studio                          |
|    (Model Fine-Tuning CLI / Web Dashboard / Evaluation & Telemetry Hub)         |
+---------------------------------------------------------------------------------+
                                       │
+---------------------------------------------------------------------------------+
|                    Model & Policy Orchestration Layer                           |
|  - Vision-Language-Action (OpenVLA, Octo, RT-X, π0) Policy Serving              |
|  - Visual Action Models (VAM) & Diffusion Policy Accelerators                   |
|  - Robotics Reward Models & Failure Mode Detection                             |
+---------------------------------------------------------------------------------+
                                       │
+---------------------------------------------------------------------------------+
|                     Data & Sim-to-Real Pipeline Layer                           |
|  - Multi-Sensor Time-Sync & Kinematic Ingestion (RGB, Depth, Gripper Trajectories) |
|  - Open X-Embodiment & Hugging Face LeRobot Format Normalization                |
|  - Simulation Connectors (NVIDIA Isaac Sim, MuJoCo, Gazebo, Genesis)            |
+---------------------------------------------------------------------------------+
                                       │
+---------------------------------------------------------------------------------+
|                    High-Throughput GPU Compute Infrastructure                    |
|       Dedicated NVIDIA H100/H200/B200 Clusters with Low-Latency Interconnect     |
+---------------------------------------------------------------------------------+
```

### 2.2 Key Features & Technical Advantages
1. **Turnkey VLA / VAM Fine-Tuning Pipelines (Turnkey Model Adaptation)**:
   - Built-in support for leading robotics policy models (including OpenVLA, Diffusion Policy, ACT, Octo, and Flow Matching policies). Enables developers to fine-tune specialized manipulation or assembly policies in the cloud with as few as several dozen teleoperation demonstration trajectories.
2. **Unified Trajectory & Kinematic Formatting**:
   - Native ingestion and normalization for Open X-Embodiment and Hugging Face `lerobot` dataset standards. Automatically parses and standardizes teleoperation logs from diverse robot arms (Franka Emika, Universal Robots, AgileX, SO-100 / ALOHA), eliminating days of fragile custom data cleaning.
3. **Sim-to-Real Evaluation Loop**:
   - Enables developers to run automated, batch simulation benchmarks across MuJoCo or Isaac Sim in the cloud to evaluate grasp success rates, collision risks, and control latency before exporting quantized policies to edge hardware (e.g., NVIDIA Jetson Orin or embedded controllers) with a single command.
4. **Robotics-Specific Reward & Failure Diagnostics**:
   - Deploys multimodal reward models to evaluate task completion objectively, automatically flagging end-effector slippage, kinematic singularities, and collision anomalies to deliver a closed-loop training feedback cycle.

---

## 3. Vision and Mission

### 3.1 Vision
> **"To become the de-facto orchestration and reasoning operating system for robots, serving as the essential infrastructure layer for the next generation of spatial agents and physical AI."**

Qualia observes that just as Databricks and LangChain unified chaotic foundation models, prompt engineering, and vector search into production-grade infrastructure for NLP and LLMs, **Physical AI and robotics urgently require their own standardized orchestration and compute substrate**. Qualia bridges the critical chasm between general-purpose foundation models and physical robot hardware.

### 3.2 Mission
> **"To provide a research-driven robot foundation model cloud infrastructure platform that makes foundation models actually work in the physical world — turning hours of data formatting and dependency management into minutes."**

Qualia is dedicated to eliminating the crushing operational burden of heterogeneous hardware drivers, fragmented GPU clusters, sensor spatiotemporal calibration, and fragile system dependencies—liberating robotics researchers to focus purely on policy iteration, world models, and high-level task planning.

---

## 4. Category & Classification

- **Primary Category**: Robotics AI Foundation Model Infrastructure & Embodied AI Platform
- **Secondary Categories**:
  - Spatial AI & Physical Intelligence Operating System
  - Robotics GPU Cloud & Distributed Compute Orchestration
  - Sim-to-Real Deployment & Policy Serving
- **Tech Taxonomies & Keywords**:
  `VLA (Vision-Language-Action) Models` `VAM (Visual Action Models)` `Robotics GPU Cloud` `Spatial AI` `Reinforcement Learning from Human Feedback (RLHF) / Reward Modeling` `Open X-Embodiment` `LeRobot Integration` `ROS 2 Orchestration` `Sim-to-Real Deployment`

### 4.1 Ecosystem Positioning Comparison
- **Compared to Generic GPU Clouds (AWS / RunPod / Lambda)**: Generic clouds merely provision raw compute VMs lacking spatial-temporal alignment for multimodal robotics data (e.g., synchronized joint encoders, end-effector poses, torque telemetry, and multi-angle camera feeds). Qualia provides native robotics data pipelines and custom distributed training container runtimes.
- **Compared to Physics Simulators (Isaac Sim / MuJoCo)**: Qualia does not replace underlying physics engines; rather, it functions as the **central cloud brain** orchestrating upstream VLA/VAM pre-training/fine-tuning and downstream simulation benchmarking and hardware testing.

---

## 5. Role at Junction 2026 & Challenge Tracks Prediction

### 5.1 Partner Positioning at Junction
- **Positioning**: Junction 2026 Bronze Tech Partner.
- **Enablement Mission**: Rescue hackers from spending 40 hours wrestling with ROS dependencies, broken CUDA drivers, and GPU out-of-memory errors—empowering teams to build, train, and demonstrate **end-to-end embodied intelligence policies within a 48-hour sprint**.

### 5.2 Aligned Challenge Tracks
- **AI Infrastructure Track (by Verda)**: Demonstrating specialized GPU acceleration, scheduling, and memory optimization tailored for non-text physical modalities (actions, 3D point clouds, physical torques).
- **Agentic AI Track**: Architecting embodied agents equipped with spatial reasoning, environmental perception, tool manipulation, and autonomous decision-making.
- **Hardware Track (by Arduino)**: Interfacing Arduino/Raspberry Pi microcontrollers and low-cost open-source robot arms (e.g., SO-100, Koch v1.1) with cloud-trained Qualia VLA policies for affordable physical automation.

### 5.3 Recommended Hackathon Project Concepts
- **1-Day Low-Cost Arm Teleoperation & Policy Training**:
  - Use a 3D-printed robot arm or miniature simulator, record 50 teleoperation demonstrations via webcam or hand gesture tracking, upload trajectories to Qualia to train a Diffusion Policy on cloud GPUs, and achieve autonomous sorting within 4 hours.
- **Voice-Conditioned VLA Manipulation**:
  - Couple audio models (e.g., Whisper / Gemini Live) with Qualia-hosted OpenVLA action policies: users give natural language commands (e.g., "Place the red bottle onto the left tray"), and the policy executes end-to-end trajectory inference.
- **Robotics Self-Healing Agent**:
  - When a robotic arm encounters an unexpected collision or slippage, Qualia's multimodal spatial diagnostic layer detects the failure mode, prompting the agent to adjust grasp orientation or request human guidance.

---

## 6. Official Links & Key Resources

- **Official Website**: [https://qualiastudios.dev](https://qualiastudios.dev)
- **Investor & Media Coverage**:
  - BlackWood VC In-Depth Feature: *Qualia: The Missing OS for Embodied AI*
  - The Hub Startup Profile: [https://thehub.io/startups/qualia-studios](https://thehub.io/startups/qualia-studios)
- **Ecosystem & Open Source Repositories**:
  - OpenVLA (Vision-Language-Action Models): [https://github.com/openvla/openvla](https://github.com/openvla/openvla)
  - Hugging Face LeRobot (State-of-the-Art Robotics): [https://github.com/huggingface/lerobot](https://github.com/huggingface/lerobot)
  - Open X-Embodiment Project: [https://robotics-transformer-x.github.io](https://robotics-transformer-x.github.io)
- **Junction 2026 Official Portals**: [https://hackjunction.com](https://hackjunction.com) | [https://hackjunction.app](https://hackjunction.app)
