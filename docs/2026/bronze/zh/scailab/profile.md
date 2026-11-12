# Scailab (Scandinavian AI Laboratory) — Junction 2026 技术合作方调研报告

> **调研分类**：Junction 2026 Bronze 级技术合作方（Tech Partner Profile）  
> **公司标签**：具身智能感知基础设施 (Perception Infrastructure for Physical AI) | 合成数据生成 (Synthetic Data Platform) | 机器人与自主系统训练 (Autonomous Systems & Robotics AI)  
> **报告归档路径**：`bronze/scailab/profile.md` & `docs/2026/bronze/scailab/profile.md`  

---

## 1. 公司基本概况 (Company Overview)

| 项目 | 详细信息 |
| :--- | :--- |
| **公司全称** | SCAILAB AB (商业品牌：Scailab / Scandinavian AI Laboratory) |
| **公司官网** | [scailab.se](https://scailab.se) |
| **总部地址** | 瑞典 · 韦斯特罗斯 / 斯德哥尔摩 (Västerås & Stockholm, Sweden) |
| **创立年份** | 2024 年 |
| **创立背景与学术孵化** | 孵化自瑞典著名工科名校**梅拉达伦大学（Mälardalen University, MDU）**嵌入式系统与智能机器人研究团队，由 MDU Holding 重点孵化投资，并获得瑞典国家创新署 (Vinnova)、Idélab 及 Creates 创新孵化器的深度支持 |
| **核心创始人团队** | - **Dr. Lukas Dust** (Co-Founder & CEO，MDU 机器人与电子工程博士，研究方向为分布式机器人网络形式化验证与边缘 AI，曾受邀赴卡耐基梅隆大学 CMU 进行学术访问与合作)<br>- **Dr. Moritz Schmidt** (Co-Founder & COO，MDU 电子学博士，专精于医疗自主系统、人机协作 HRI 与机电一体化设计)<br>- **Dr. Giovanni Burresi** (Co-Founder & CTO，信息工程博士，长期专注于工业物联网 IIoT、边缘计算与高保真合成数据管线架构设计) |
| **融资背景与支持机构** | 由 **MDU Holding** 种子期直投，获得瑞典区域深科技孵化基金（Creates、Idélab）、北欧工业天使投资人以及瑞典国家级科研商业化创新资助 |
| **团队基因** | 兼备顶尖学术严谨性与工业级系统落地能力，专注攻克物理世界中自主系统的数据稀缺与仿真到现实（Sim-to-Real）失真难题 |

---

## 2. Vision（愿景）与 Mission（使命）(Vision & Mission)

### 🌟 愿景 (Vision)
> **"To establish the definitive perception and synthetic simulation foundation for physical AI, enabling robots and autonomous machines to perceive, understand, and safely interact with the real world without prohibitive real-world data collection barriers."**  
> *(构建物理智能领域的标杆级感知与合成仿真地基，让机器人与自主设备能够在无需承受高昂物理采集成瘾的前提下，精准感知、深度理解并安全融入现实物理世界。)*

Scailab 认为，当前机器人与工业 AI 落地面临的最严重瓶颈并非算法架构，而是**长尾边缘数据（Edge-Case Data）的严重缺失**与**真实世界数据采集的高危、昂贵与低效**。物理世界的意外场景（如极端暴雨逆光、工业管道破裂、人员跌倒碰撞）在现实中极难采集合成，Scailab 的愿景是通过物理高保真的虚拟感知世界，为整个物理 AI 产业提供可信数据供给。

### 🎯 使命 (Mission)
> **"To remove time, cost, and complexity barriers so that real-world AI can be built faster, safer, and with better operational reliability — enabling every developer to gather the right data and bring a robot or perception model into the field in one night."**  
> *(消除时间、成本与复杂度阻碍，让现实世界 AI 能够更快速、更安全、更可靠地被构建出来 — 赋能每一位开发者在短短一个晚上即可完成高质量数据收集并将机器人感知模型推向现场。)*

Scailab 旨在打破大厂与顶尖实验室垄断机器人训练数据的壁垒，通过开箱即用的合成数据工具，让任何开发者只需几个小时就能获得数万张带精准三维标注的训练集。

---

## 3. 所属 Category（业务与技术分类）(Industry & Tech Category)

### 📌 核心分类 (Primary Category)
- **Perception Infrastructure for Physical AI**（物理 AI 感知基础设施）
- **Synthetic Data Generation & Simulation Platform**（合成数据生成与物理仿真平台）
- **Autonomous Systems & Robotics AI Training**（自主系统与机器人训练平台）

### 🏷️ 细分技术标签 (Tech Tags & Taxonomies)
`Multi-Modal Synthetic Sensor Data` `Sim-to-Real Transfer` `Photorealistic Rendering` `RGB / RGB-D / LiDAR / Thermal / Event Cameras` `ROS 2 Middleware Introspection` `Edge AI Optimization` `Industrial Quality Inspection` `Edge Case Generation`

### 💡 行业生态位对比 (Ecosystem Positioning)
- **对比通用 3D 渲染/游戏引擎（如 Unity / Unreal Engine）**：通用游戏引擎注重人类肉眼的视觉逼真度，往往忽略了传感器内部物理噪声、快门畸变、激光雷达波束散射与红外辐射热效应；Scailab 从学术底层**精准模拟真实工业级传感器的光学物理特性**。
- **对比昂贵的物理采集团队**：传统采集需要真实卡车搭载数十万激光雷达环路采集数月并人工打标；Scailab 在数小时内通过程序化生成参数（光照、材质、天气、障碍物）导出 100% 具备自动精确三维包围框、分割掩码与法线图的高保真数据。

---

## 4. 核心产品与服务 (Core Products & Architecture)

### 4.1 主打平台：Scailab Intelligence Lab Platform
Scailab 平台为物理智能开发者提供了一个一站式的感知合成与模型验证环境，整体架构分为三大中枢：

```
+─────────────────────────────────────────────────────────────────────────────+
|                         Scailab Intelligence Studio                         |
|        (Web-based Scenario Builder / Parameter Sweeper / Edge-Case Wizard)   |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
+─────────────────────────────────────────────────────────────────────────────+
|                      Procedural World Generation Core                       |
|   - Multi-Domain Assets: Smart Warehouses, Harsh Mining, Automated Highway  |
|   - Dynamic Agents: Procedural Pedestrians, Forklifts, AGVs, Debris, Fog    |
|   - Environmental Sweeps: Sun Angle, Rain, Snow, Lens Smudge, Occlusions    |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
+─────────────────────────────────────────────────────────────────────────────+
|                    Physics-Calibrated Sensor Simulation                     |
|  - Multi-Camera Systems: Monocular RGB, Stereo Vision, Fisheye, RGB-D Depth  |
|  - Active Sensors: 16/64/128-beam LiDAR, FMCW Radar, Ultrasonic Transducers  |
|  - Specialized Sensors: Long-Wave Infrared (Thermal) & Neuromorphic Events  |
|  - Ground Truth Outputs: 3D Bounding Boxes, Semantic Mask, Depth Maps, ODOM |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
+─────────────────────────────────────────────────────────────────────────────+
|                     Edge Runtime & Verification Engine                      |
|         - ROS 2 Timing Introspection (AROSpect Timing Analysis)             |
|         - Quantized Model Export: TensorRT, ONNX, Edge TPU                  |
+─────────────────────────────────────────────────────────────────────────────+
```

### 4.2 关键特性与竞争优势 (Key Features)
1. **合成世界光速生成 (Synthetic-World Speed)**：
   - 传统物理采集成百上千小时的异常长尾数据，在 Scailab 平台仅需勾选参数（如“夜间 + 大雨 + 激光雷达溅水反射 + 穿反光背心的工人倒地”），几分钟内批量渲染出上万帧带完美标注的数据。
2. **物理级真实度弥合 Sim-to-Real 鸿沟 (Physical-World Accuracy)**：
   - 算法结合 MDU 博士团队多年的传感器硬件校准成果，将镜头畸变、CMOS 滚动快门条纹、LiDAR 反射率衰减与环境噪声深度建模，模型在虚拟数据上训练后可直接在真实硬件部署（Zero-Shot 或少样本迁移）。
3. **部署信心与极端安全合规 (Deployment Confidence)**：
   - 针对无人机、无人仓储车和协作机械臂，系统能自动化进行“边际失效测试”（Stress-Testing），测量目标检测模型在极端逆光或大雾下的性能衰减曲线，输出具备可解释性的安全可靠度报告。
4. **边缘运行时时序验证 (AROSpect ROS 2 Integration)**：
   - 不仅关注感知准确度，还引入底层计算延迟与通信抖动分析工具，确保深度学习检测模型在 Jetson 或工控机上能在规定硬实时毫秒窗口内交付推理结果。

---

## 5. 在 Junction 2026 黑客松中的角色与开发者赋能 (Junction 2026 Role & Hacker Enablement)

### 5.1 黑客松角色定位
- **定位**：Junction 2026 Bronze 级技术合作方（Tech Partner）。
- **黑客松痛点直击**：在 48 小时的极限黑客松中，绝大多数做硬件、机器人和视觉 AI 的团队都受阻于“缺乏足够的高质量标注图片/点云”，耗费整个周六人工拍照打标。Scailab 为参赛者提供现成的**合成感知数据金矿**。

### 5.2 推荐参赛赛道 (Recommended Tracks)
- **AI Infrastructure Track (by Verda)**：展示如何用高效的合成数据生成引擎大幅缩减训练计算开销与碳足迹。
- **Agentic AI Track**：让空间 Agent 拥有高保真虚拟观察源，在仿真世界中实现自主探索、目标追踪与障碍回避。
- **Hardware Track (by Arduino)**：配合 Arduino / ESP32 摄像头模块或小车底盘，使用 Scailab 预生成的轻量级边缘模型在微型硬件上实现高精度工业质检或寻轨巡线。

### 5.3 参赛黑客典型落地场景 (Hackathon Ideas)
- **工业生产线微小瑕疵质检系统 (Zero-Shot Industrial Defect Inspector)**：
  - 无需采集真实次品（因为真实次品罕见），参赛者使用 Scailab 平台生成 5000 张带有各种表面划痕、凹坑和裂纹的金属齿轮合成图像，训练轻量 YOLO/DETR 并在本地运行实时检测。
- **搜救无人机极端恶劣天气侦测 (Adverse-Weather Drone Search & Rescue)**：
  - 利用 Scailab 生成由暴雪、大雾、夜间热成像构成的复杂灾害场景，结合热红外（Thermal）和可见光双模态数据训练受困人员快速识别模型。
- **自主移动机器人室内避障与路径规划 (Warehouse AMR Safe Navigator)**：
  - 调用 Scailab 生成的仓库内部 RGB-D 与 LiDAR 点云，训练机器人避开突发掉落货物、地面油渍和行人走动，在 48 小时内演示逼真的端到端仿真或遥控小车导航。

---

## 6. 官网与关键资源链接 (Official Links & Key Resources)

- **官方主页 (Website)**：[https://scailab.se](https://scailab.se)
- **学术与孵化支持背景 (Academic & Ecosystem Links)**：
  - Mälardalen University (MDU) 官方创业报道: [mdu.se/en/malardalen-university](https://www.mdu.se)
  - MDU Holding 投资孵化主页: [mduholding.se](https://mduholding.se)
- **学术研究与开源技术参考 (Research & Tech Papers)**：
  - 核心创始人有关 ROS 2 时序内省（AROSpect）与轻量化边缘 AI 质量检测的同行评议科研文献
- **Junction 2026 大赛官方主页**：[https://hackjunction.com](https://hackjunction.com) | [https://hackjunction.app](https://hackjunction.app)
