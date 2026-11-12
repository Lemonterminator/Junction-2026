# Rokoko (Rokoko Electronics ApS) — Junction 2026 合作方深度调研报告

## 1. 公司基本概况

- **公司全称**: Rokoko Electronics ApS
- **公司总部**: 丹麦哥本哈根 (Copenhagen, Denmark)，并在美国旧金山、洛杉矶以及希腊雅典设有工程与业务中心。
- **创立背景**:
  - Rokoko 创立于 2014 年，由 **Jakob Balslev**（CEO）、**Matias Søndergaard** 与 **Anders Klok** 联合创办。
  - 公司灵感起源于丹麦国家电影学院（National Film School of Denmark）。当时，好莱坞级别的光学动作捕捉（Optical Motion Capture）系统极其昂贵（动辄数十万甚至数百万美元），且需要数十台昂贵的高速红外摄像机、反光标记点和占地数百平米的专用无光摄影棚，绝大多数独立影视制作人、独立游戏工作室和中小型动画团队根本无法企及。
  - 创始团队决定利用微机电系统（MEMS）惯性测量单元（IMU）以及高精度滤波算法，将整个动作捕捉摄影棚“穿在身上”，开创了便携、无线、不受光照与场地约束的消费级与专业级惯性动作捕捉系统。
- **行业与技术地位**:
  - **全球惯性动作捕捉与创作者工具的绝对领航者**: Rokoko 彻底打破了传统动作捕捉高不可攀的壁垒，被业内誉为“让动捕平民化的变革者”。全球已有超过 50,000+ 名创作者、游戏开发者、VFX 特效师、顶级工作室（包括 Netflix、Sony、Marvel、Warner Bros、CD Projekt Red、Ubisoft）以及全球顶级科研院校深度使用 Rokoko 产品。
  - **从动捕硬件到全栈空间智能 (Spatial Computing & Physical AI)**: 如今的 Rokoko 不仅拥有 Smartsuit Pro 这一标志性硬件，更构建了包含手部微动作手套（Smartgloves）、面部表情捕捉（Face Capture）、云端/浏览器无标记点 AI 视频动捕（Rokoko Vision）以及直接对接游戏引擎（Unreal, Unity, Blender）与机器人仿生控制的完整空间计算生态。

---

## 2. 核心产品与业务体系

Rokoko 构建了一整套从硬件传感器数据采集、数据实时清洗/重定向，到多端软件与游戏引擎实时推流的闭环工具链。

### 2.1 核心硬件产品矩阵
- **Smartsuit Pro II (旗舰级惯性动作捕捉服)**:
  - 搭载 17 至 19 组工业级高精度 9 轴 IMU 传感器（集成陀螺仪、加速度计与磁力计），覆盖人体所有核心骨骼节点。
  - **完全无线自由**: 依靠普通充电宝即可连续工作数小时，支持 2.4GHz / 5GHz 双频 Wi-Fi 实时无线串流，甚至支持板载 Hub 离线录制（脱离电脑网络在户外自由奔跑、翻滚或跳跃，事后一键同步数据）。
  - **秒级极速标定**: 穿戴者摆出标准 "T-Pose" 或 "Straight Pose"，仅需数秒即可完成全身体感骨骼标定校准。
- **Smartgloves (智能动作捕捉手套)**:
  - 针对人类极其复杂的微小手部动作专门研发，集成手腕、手掌与每一根手指关节的微型磁感应与惯性传感器，精准捕捉弹琴、握拳、手势比划与手指微动，彻底摆脱传统动画制作中逐帧手调手指骨骼的痛苦。
- **Rokoko Coil Pro (高精度全局定位基站)**:
  - 革命性电磁追踪锚点，有效消除纯惯性动捕在长时间高强度剧烈运动中不可避免的全局位置漂移（Drift），提供厘米级全局绝对坐标校准。
- **Face Capture (面部表情实时捕获)**:
  - 基于 iOS 原深感摄像头（TrueDepth）与 ARKit 52 组标准表情基底（Blendshapes），与身体动捕、手指动捕完美同步，实现“全身体态 + 微表情 + 语音口型”三位一体的实时全性能动捕（Full-Performance Capture）。

### 2.2 核心软件与算法生态
- **Rokoko Studio (桌面级动捕控制中枢)**:
  - 跨平台动捕工作站软件，支持多名演员（Multi-Actor）同台动作捕捉、实时 3D 骨骼映射可视化、传感器健康状态诊断、脚步接触锁定算法（Foot Locking, 避免滑步）以及一键导出 FBX、BVH、CSV 格式。
- **Rokoko Vision (基于 AI 的无标记点单摄动捕)**:
  - 无需任何穿戴硬件，只需普通单目网络摄像头或上传一段手机拍摄的 MP4 视频，借助先进的计算机视觉神经模型即可在浏览器中一键提取高精度的 3D 人体动作骨骼骨架。
- **Motion Library (动捕动作数字资产库)**:
  - 深度集成于 Studio 与 Audiences 中的数字资产商城，汇聚数万条由好莱坞级特技演员录制的专业战斗、跑酷、跳舞与日常体态动画片段。

### 2.3 开发者集成与实时推流工具链 (Developer SDK & Streaming)
- **游戏引擎实时数据插件 (Real-time Engine Live Link)**:
  - **Unreal Engine 插件**: 原生支持 Unreal Live Link，秒级将动捕数据映射到 Epic Games **MetaHuman** 高拟真数字人模型，支持通过 Take Recorder 进行实时虚拟制片（Virtual Production）。
  - **Unity 插件**: 通过开源的 `rokoko-studio-live-unity` 包与 `StudioManager` 脚本，监听局域网 UDP 端口，实时驱动 Unity 角色 Animator 与人形骨骼。
  - **Blender / Maya / Houdini / Cinema 4D 官方插件**: 提供三维美术师一键重定向（Retargeting）与时间线烘焙功能。
- **Rokoko Command API (远程遥控协议)**:
  - 基于 TCP/IP 的 JSON 命令控制接口，允许第三方应用程序或游戏内逻辑反向控制 Rokoko Studio：
    ```json
    { "command": "StartRecording", "filename": "Scene_01_Take_03" }
    ```
- **Rokoko Device SDK (底层直连开发包)**:
  - 允许开发者彻底绕过 Rokoko Studio 桌面客户端，直接通过 USB 或无线 Socket 与 Smartsuit Pro 硬件建立通信：
    - **RCSP (Rokoko Command Server Protocol)**: 处理设备发现、电池电量与按键事件。
    - **RGMP (Rokoko General Motion Protocol)**: 极低延迟的二进制协议，输出未经滤波的原始传感器四元数（Quaternion）、角速度与加速度。极受机器人实验室、仿生强化学习与人机协同遥操作（Teleoperation）开发者追捧。

---

## 3. Vision（愿景）与 Mission（使命）

### 3.1 官方使命 (Mission)
> *"To make professional motion capture and character animation accessible, intuitive, and affordable for all creators — from indie visionaries to world-class studios."*
> 
> （让专业的动作捕捉与 3D 角色动画技术变得人人可触及、直观易用且经济实惠——从充满创意的独立艺术家，到世界顶尖的影视游戏工作室。）

### 3.2 官方愿景 (Vision)
> *"To democratize human motion data and spatial computing — transforming how humans interact with digital worlds, virtual characters, robotics, and physical AI."*
> 
> （实现人类动作数据与空间计算技术的平权普惠——彻底重塑人类与虚拟世界、数字化身、机器人学以及物理人工智能系统之间的交互范式。）

### 3.3 核心设计哲学
- **Invisible Tech (隐形技术)**: 技术应当隐藏在创作体验之后。不需要复杂的电缆束缚与暗室搭建，穿上衣服即可肆意表演。
- **Real-Time Synchronicity (极致实时性)**: 追求微秒级延迟的数据推流，让动捕演员的每一个动作即刻显现在虚拟世界的屏幕与引擎中。
- **Bridging the Physical & Virtual (物理与数字的无缝缝合)**: 将物理世界人类身体的真实动能，作为数字世界交互与物理 AI 机器人仿生的第一输入源。

---

## 4. 所属 Category（业务与技术分类）

- **Primary Category**: Motion Capture & Spatial Computing (动作捕捉与空间计算平台)
- **Secondary Categories**:
  - 3D Character Animation & Virtual Production (三维角色动画与虚拟制片)
  - XR & Interactive Gaming (扩展现实与交互式游戏开发)
  - Physical AI, Robotics & Human Teleoperation (物理人工智能与机器人遥操作)
  - Biomechanics & Human Movement Analytics (生物力学与人体运动机能分析)

---

## 5. 在 Junction 黑客松中的角色与赛道挑战预测

### 5.1 黑客松合作方定位
Rokoko 是 Junction 2026 **Spatial Computing、Gaming & Interactive 3D / Creative Tech 赛道出题方与专业动捕设备提供方**。
在黑客松现场，Rokoko 通常会携带多套 **Smartsuit Pro II 动捕服、Smartgloves 动捕手套与脸部追踪支架**，设立现场动捕演示区（Mocap Demo Arena）。参赛队伍可以现场穿戴设备、录制专属动画数据，或者直接通过 Wi-Fi 局域网订阅动捕服实时广播的 UDP 数据流，将其注入到自己的游戏、AR/VR 体验或具身智能控制程序中。

### 5.2 赛道挑战预测与出题方向
1. **Real-time Spatial Interactions & Full-Body XR Gaming (全身沉浸式 XR 游戏与体感交互)**:
   - *课题方向*: 告别传统的键盘、鼠标或 VR 手柄按键交互，如何利用全身动捕姿态与手套微动作，设计出具有物理真实感的沉浸式体感对决、魔法施法、跑酷或武术对战体验？
   - *解题思路*: 在 Unity/Unreal 中接入 Rokoko Studio Live Link，将选手的身体姿态实时映射为受刚体物理引擎约束的虚拟角色，实现拳拳到肉的碰撞打击与躲避反馈。
2. **Physical AI, Imitation Learning & Robot Teleoperation (物理智能与机器人示教模仿学习)**:
   - *课题方向*: 人形机器人与机械臂的灵巧操作需要海量高质量的人类物理动作数据。如何利用 Smartsuit Pro 和 Smartgloves 实现对虚拟仿真机器人（如 Isaac Gym / MuJoCo）的远程低延迟精准遥控（Teleoperation）并构建模仿学习数据集？
   - *解题思路*: 利用 Rokoko Device SDK 或 UDP 广播流提取关节四元数角度，映射为人型双足机器人或机械臂关节的逆向运动学（IK）目标点，实现人体动作到机械本体的实时镜像跟随。
3. **VTuber, Digital Humans & Live Generative Entertainment (虚拟主播、数字人实时交互与生成式演艺)**:
   - *课题方向*: 结合生成式 AI 语音与大模型驱动的 NPC，创造一个既由真人演员驱动、又融合 AI 自主反应的次时代虚拟演艺或沉浸式戏剧体验。
   - *解题思路*: 利用 Rokoko 动捕服驱动 MetaHuman 角色，融合本地语音转文字（Whisper）与实时大模型生成剧情分支，打造千人千面的交互式现场 live show。
4. **Digital Health, Sports Biomechanics & Ergonomics (数字健康、运动生物力学与人体工效分析)**:
   - *课题方向*: 利用动捕传感器高频采集的骨骼关节角速度与加速度，实时评估康复患者的肢体活动度、运动员技术动作标准度或工业流水线工人的疲劳/姿势损伤风险。
   - *解题思路*: 计算脊柱弯曲度、膝关节负荷与步态对称性，构建实时三维健康看板与异常预警系统。

### 5.3 参赛队伍实战建议与快速上手 (Quickstart)
- **步骤 1 (获取实时数据流)**: 在 Rokoko Studio 中开启 **Live Stream** 功能，指定目标 IP（如 `127.0.0.1`）和端口（默认 `14043`），格式勾选 JSON 或 Rokoko Studio Data。
- **步骤 2 (极速 Python 接收测试)**:
  ```python
  import socket
  import json

  # 监听 Rokoko 广播的 UDP 数据包
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(("0.0.0.0", 14043))

  print("Listening for Rokoko motion frames...")
  while True:
      data, addr = sock.recvfrom(65535)
      mocap_frame = json.loads(data.decode("utf-8"))
      # 提取全身骨骼关节坐标与姿态四元数
      for body in mocap_frame.get("scene", {}).get("actors", []):
          head_pos = body["body"]["head"]["position"]
          print(f"Actor [{body['name']}] Head Position: {head_pos}")
  ```
- **步骤 3 (Unity 引擎快速驱动)**:
  - 导入 `rokoko-studio-live-unity` 资源包。
  - 在场景中拖入预制体 `StudioManager`，勾选 "Auto Create Actors"。
  - 穿戴动捕服的演员在现场移动，Unity 场景中的 3D 角色即刻实现 1:1 实时镜像跟随！

---

## 6. 官网与关键资源链接

- **Rokoko 官方主页**: [https://rokoko.com](https://rokoko.com)
- **Rokoko 官方知识库与帮助中心**: [https://support.rokoko.com](https://support.rokoko.com)
- **Rokoko Studio 软件下载**: [https://rokoko.com/products/studio](https://rokoko.com/products/studio)
- **Rokoko Vision (网页端 AI 视频动捕)**: [https://rokoko.com/products/vision](https://rokoko.com/products/vision)
- **Unity 插件开源 GitHub**: [https://github.com/rokoko/rokoko-studio-live-unity](https://github.com/rokoko/rokoko-studio-live-unity)
- **Unreal Engine 插件开源 GitHub**: [https://github.com/rokoko/rokoko-studio-live-unreal-engine](https://github.com/rokoko/rokoko-studio-live-unreal-engine)
- **Rokoko 开发者 Command API 与 SDK 说明**: [https://support.rokoko.com/hc/en-us/articles/4410427618577-Rokoko-Studio-Command-API](https://support.rokoko.com/hc/en-us/articles/4410427618577-Rokoko-Studio-Command-API)
