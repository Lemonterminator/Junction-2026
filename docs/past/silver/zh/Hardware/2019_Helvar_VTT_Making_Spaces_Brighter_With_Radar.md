# [2019] Helvar & VTT — 用雷达技术点亮空间

## 元数据

- **年份**: 2019
- **挑战合作方**: Helvar & VTT
- **原始历史赛道**: AI & Data
- **2026 对应赛道**: Hardware Track (by Arduino)
- **技术细分方向**: 毫米波雷达与高速机器视觉传感器 (Millimeter-Wave Radar & High-Speed Machine Vision Sensors)
- **核心主题**: 60 GHz 2D 毫米波成像雷达与 24 GHz 生命体征雷达传感器 + 智能灯具硬件实时联调
- **归类理由**: 虽原属 AI & Data 赛道，但现场提供 60 GHz 2D 毫米波雷达、24 GHz 毫米波雷达（可非接触提取呼吸心率等生命体征与微动）以及实体智能灯具硬件供团队实时接入演示。

---

## 挑战完整题目

用雷达技术点亮空间

## 挑战描述 (Description)

识别房间内人员存在的能力已存在很长时间，并用于自动可靠地控制灯光。但技术演进要求创新，我们的目标是创建更智能的室内空间。通过将机器学习和人工智能算法应用于雷达传感器数据，您可以开发出能够提供最先进照明的未来应用。这是创建真正智能室内系统的下一步。

想象一下整个建筑变得活跃并对居住者的行为做出反应的可能性。通过利用雷达等先进传感器，我们能否计算房间内有多少人并识别他们的位置？是否有可能识别人员是静止还是移动？如果是，他们的移动方向是什么？

同样，我们能否检测在办公桌前工作的人的行为变化，并提供个性化照明以提升他们的情绪和生产力？

此外，这不仅仅局限于人员存在。例如，是否有可能在车库中定位空停车位？我们能否识别移动车辆的方向？此类洞察具有多种应用，从购物中心的人流到建筑利用率测量以及用于照明控制的高级室内占用传感。

## 可用资源 (Resources)

Helvar & VTT 将提供：演示工具、设备和数据集：我们将提供一个网页，包含环境布局上的灯具位置。参与者可以通过 API 发送命令来模拟灯光的行为。还将提供演示灯具以及雷达传感器。

车库：参与者将获得一个来自室内车库的数据集，使用 RGB 相机和 60 GHz 2D 雷达收集。数据集时间同步。从 RGB 帧中检测到的人和车辆由边界框表示，提供在图像坐标系中。雷达数据包括在平面图坐标系中显示目标的 2D 幅度图。

会议室：参与者将获得一个来自会议室的数据集，包含 60 GHz 2D 雷达成像数据和相应的 RGB 相机帧。从 RGB 帧中检测到人员及其骨架，并提供其边界框和关节坐标在图像坐标系中。雷达数据包括在平面图坐标系中显示目标的 2D 幅度图。参与者可以获得雷达的实时访问权限，用于创建在线演示。

工作场所：参与者将获得一个人使用电脑工作的数据集。数据集包括原始 24 GHz 雷达数据和相应的 RGB 相机帧。从雷达数据中提取生命体征，并从 RGB 帧中检测和提供人员的关节位置。原始雷达数据包括幅度图和相位图，可用于检测大规模和小规模运动。参与者可以获得传感器数据的实时访问权限，也可用于创建在线演示。

---

## 历届获奖方案与验证项目

- **赛题第一名 (Winner)**：**LumenLoop**（Denys Kovalenko 与 Elizaveta Lebedeva，两人队）`[L1]` — 构建了基于 VTT 60 GHz FMCW 实时成像雷达（`160 deg` 视场、`5 cm` 距离分辨率 / `3.5 deg` 角度分辨率）与 Helvar DALI 蓝牙 Mesh 实体灯具（`EC22`）的闭环控制系统。通过 RabbitMQ (`10.84.110.2`, `radar60`) 订阅 FlatBuffers 流，采用轻量径向峰值相对跃变判据（每 10 帧统计 `diff / max > 0.13`）估计占用人数（`0`–`3+` 人），经 `pyserial` USB-Serial 网关向实体灯具下发去重后的 DALI HEX 查找表控制指令（`5% / 6500K` -> `60% / 3450K`），并配备 React 手动预设控制面板与 Elasticsearch 审计日志。
- **赛题第二名 (1st Runner-up)**：**Brighten your way** `[L1]` *(团队名单与代码仓库未公开归档)*。
- **赛题第三名 (2nd Runner-up)**：**figvam**（HSE 计算机系战队：Timofey Smirnov、Igor Zverev、Ainur Nuriev、Aldar Danilov；指导老师 Maxim Dyakov）`[L1]`/`[L2]` — 融合雷达感知理念与 WiFi 指纹室内定位，并开发了困倦闪烁唤醒与入睡自动熄灯节律照明模式。
- **硬件与工程经验**：在 48 小时现场实操中，优先打通真实雷达流到实体灯具的端到端硬件闭环（并用内存缓存防串口总线泛洪、将交互滑块与审计日志接口解耦），比耗时折腾时间错位的离线数据集微调大模型更稳健。
- **Bronze 原始档案**：[`2019_Helvar_VTT_Radar_LumenLoop.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2019_Helvar_VTT_Radar_LumenLoop.md)
- **原始信源**：[Junction 2019 官方获奖公告 (Medium)](https://medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f) | [LumenLoop 开源仓库 (`deniskovalenko/junction2019`)](https://github.com/deniskovalenko/junction2019) | [HSE 新闻报道](https://www.hse.ru/en/news/323373069.html)
