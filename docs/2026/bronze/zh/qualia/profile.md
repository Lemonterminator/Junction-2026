# Qualia (Qualia Studios) — Junction 2026 技术合作方调研报告

> **调研分类**：Junction 2026 Bronze 级技术合作方（Tech Partner Profile）  
> **公司标签**：机器人基础模型 (Robotics Foundation Models) | 物理具身智能 (Embodied AI) | GPU 云基础设施 (Robotics GPU Cloud)  
> **报告归档路径**：`bronze/qualia/profile.md` & `docs/2026/bronze/qualia/profile.md`  

---

## 1. 公司基本概况 (Company Overview)

| 项目 | 详细信息 |
| :--- | :--- |
| **公司全称** | Qualia Studios ApS (商业品牌：Qualia / Qualia Studios) |
| **公司官网** | [qualiastudios.dev](https://qualiastudios.dev) |
| **总部地址** | 丹麦 · 哥本哈根 (Copenhagen, Denmark) |
| **创立年份** | 2025 年 |
| **核心创始人团队** | - **Fabian Kerj** (Co-Founder & CEO，曾于北欧多家高成长初创担任技术与业务管理职务)<br>- **Oscar Cortina** (Co-Founder & Technical Lead)<br>- **Max Fällström** (Co-Founder & Infrastructure Lead)<br>- **Ludvig Brangstrup** (Co-Founder & Research Lead) |
| **融资轮次与金额** | **种子轮融资（Seed Round）已完成 €7.5M（约合 800 万至 870 万美元）** |
| **主要投资机构** | **BlackWood**、**Wave Ventures**、**Heartcore Capital**、**The Nordic Web Ventures**、**Florent Venture Partners** 以及 **Perplexity** 领衔的天使与战略资本支持 |
| **团队基因** | 专注于机器人前沿 AI 基础模型、分布式 GPU 加速集群调度、物理仿真以及多模态具身动作策略研发 |

---

## 2. Vision（愿景）与 Mission（使命）(Vision & Mission)

### 🌟 愿景 (Vision)
> **"To become the de-facto orchestration and reasoning operating system for robots, serving as the essential infrastructure layer for the next generation of spatial agents and physical AI."**  
> *(成为全球机器人与物理具身智能事实上的编排与推理中枢，充当新一代空间智能体（Spatial Agents）和具身 AI 不可或缺的“缺失的操作系统”。)*

Qualia 认为，正如 Databricks 与 LangChain 在大语言模型（LLM/NLP）时代将混乱的基础模型、提示词工程与向量检索重组为成熟的生产级基础设施，**物理世界与机器人领域（Physical AI）同样迫切需要属于自己的标准编排与调度层**。Qualia 旨在填补通用基础模型与物理实体机器人本体之间的巨大断层。

### 🎯 使命 (Mission)
> **"To provide a research-driven robot foundation model cloud infrastructure platform that makes foundation models actually work in the physical world — turning hours of data formatting and dependency management into minutes."**  
> *(提供由前沿科研驱动的机器人基础模型云基础设施平台，让基础模型真正能够在物理世界中运转 — 将数小时繁重的数据格式化与依赖配置压缩到数分钟内完成。)*

Qualia 致力于解除机器人工程师与科研人员在异构硬件、GPU 资源碎片化、传感器时空同步及复杂环境依赖上的巨大负担，让开发者能专注于机器人动作策略、世界模型与任务决策本身的迭代。

---

## 3. 所属 Category（业务与技术分类）(Industry & Tech Category)

### 📌 核心分类 (Primary Category)
- **Robotics AI Foundation Model Infrastructure**（机器人 AI 基础模型云基础设施）
- **Embodied AI & Physical Intelligence Platform**（具身智能与物理智能平台）

### 🏷️ 细分技术标签 (Tech Tags & Taxonomies)
`VLA (Vision-Language-Action) Models` `VAM (Visual Action Models)` `Robotics GPU Cloud` `Spatial AI` `Reinforcement Learning from Human Feedback (RLHF) / Reward Modeling` `Open X-Embodiment` `LeRobot Integration` `ROS 2 Orchestration` `Sim-to-Real Deployment`

### 💡 行业生态位对比 (Ecosystem Positioning)
- **对比传统 GPU 云（如 AWS/RunPod/Lambda）**：传统通用云仅提供裸裸的算力虚机，缺乏对多模态机器人数据集（如关节角度、末端位姿、力矩传感器、相机多重视角）的时空对齐和数据加载优化；Qualia 提供原生机器人数据管线与专有分布式训练镜像。
- **对比机器人仿真软件（如 Isaac Sim / MuJoCo）**：Qualia 并不替代底层物理仿真引擎，而是作为向上承接前沿 VLA/VAM 模型预训练与微调、向下调度仿真与实体机器人测试闭环的**云端大脑中枢**。

---

## 4. 核心产品与服务 (Core Products & Architecture)

### 4.1 主打平台：Qualia Robotics Cloud Platform
Qualia 构建了一个专门为物理智能研究员和具身工程师量身定制的研发云平台，核心技术架构涵盖四层：

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

### 4.2 关键特性与竞争优势 (Key Features)
1. **开箱即用的 VLA / VAM 微调管线 (Turnkey Model Adaptation)**：
   - 内置主流前沿机器人策略模型（如 OpenVLA、Diffusion Policy、ACT、Octo、Flow Matching 策略），支持仅用几十条遥控示教（Teleoperation）轨迹即可在云端一键完成特定装配或抓取任务的微调。
2. **异构轨迹数据标准化处理 (Unified Trajectory Formatting)**：
   - 原生支持 Open X-Embodiment 和 Hugging Face `lerobot` 数据集规范，能自动将各品牌机械臂（Franka Emika, UR, AgileX, SO-100/ALOHA）的遥控操作日志转换并标准化，省去数天手写格式清洗代码的时间。
3. **仿真评估与实体端无缝穿梭 (Sim-to-Real Evaluation Loop)**：
   - 开发者可先在云端无缝对接 MuJoCo 或 Isaac Sim 进行批量自动化 Benchmark 测试，评估抓取成功率、碰撞率和响应延迟，再一键导出量化模型到边缘端（如 Jetson Orin / 实体控制器）进行实物部署。
4. **机器人专属奖励模型与监控 (Reward & Failure Diagnostics)**：
   - 引入专用多模态奖励模型，能够自动化评判机器人执行任务是否成功，捕捉末端打滑、虚位碰撞和死锁异常，提供闭环反馈。

---

## 5. 在 Junction 2026 黑客松中的角色与开发者赋能 (Junction 2026 Role & Hacker Enablement)

### 5.1 黑客松角色定位
- **定位**：Junction 2026 Bronze 级前沿技术合作方（Tech Partner）。
- **赋能使命**：将参赛者从“耗费 40 小时配置 ROS 环境、CUDA 驱动与显存爆仓”的恶劣体验中拯救出来，让极客团队在 48 小时内完成**端到端具身智能策略训练与演示**。

### 5.2 推荐参赛赛道 (Recommended Tracks)
- **AI Infrastructure Track (by Verda)**：展示专门针对非文本模态（动作、三维空间、物理力矩）的高性能 AI 算力优化与调度。
- **Agentic AI Track**：构建具备物理环境感知、空间推理、工具操作和自主决策能力的具身智能体（Embodied Agents）。
- **Hardware Track (by Arduino)**：将 Arduino / 树莓派传感器、低成本开源机械臂（如 SO-100、Koch 机械臂）与 Qualia 云端训练的 VLA 策略相连接，实现低成本具身控制。

### 5.3 参赛黑客典型落地场景 (Hackathon Ideas)
- **极速低成本机械臂操作 (1-Day Low-Cost Arm Teleop & Policy Training)**：
  - 利用开源 3D 打印机械臂或小型仿真臂，通过网络摄像头或手势追踪记录 50 条操作轨迹，上传至 Qualia 平台调用云端 GPU 训练 Diffusion Policy，4 小时内完成自主分拣。
- **语音控制家庭/实验室协作机器人 (Voice-Conditioned VLA Manipulation)**：
  - 结合语音大模型（如 Whisper / Gemini Live）与 Qualia 托管的 OpenVLA 动作模型，参赛者只需发出自然语言指令（如“请把红色药瓶放到左侧托盘”），模型即可预测端到端末端轨迹。
- **空间故障诊断与智能体反馈闭环 (Robotics Self-Healing Agent)**：
  - 在机械臂受挫或卡死时，利用 Qualia 平台的多模态空间监控检测失败原因，并通过强化提示重试或向人类操作员请求示范。

---

## 6. 官网与关键资源链接 (Official Links & Key Resources)

- **官方主页 (Website)**：[https://qualiastudios.dev](https://qualiastudios.dev)
- **融资与官方报道 (Investor Coverage)**：
  - BlackWood VC 独家深度专访：《Qualia: The Missing OS for Embodied AI》
  - The Hub 官方公司库：[https://thehub.io/startups/qualia-studios](https://thehub.io/startups/qualia-studios)
- **生态与工具链兼容库 (Recommended Open Source Repositories)**：
  - OpenVLA (Vision-Language-Action Models): [https://github.com/openvla/openvla](https://github.com/openvla/openvla)
  - Hugging Face LeRobot (State-of-the-art Robotics): [https://github.com/huggingface/lerobot](https://github.com/huggingface/lerobot)
  - Open X-Embodiment Project: [https://robotics-transformer-x.github.io](https://robotics-transformer-x.github.io)
- **Junction 2026 大赛官方主页**：[https://hackjunction.com](https://hackjunction.com) | [https://hackjunction.app](https://hackjunction.app)
