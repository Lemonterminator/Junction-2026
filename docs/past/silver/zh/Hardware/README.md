# 2026 Hardware Track (by Arduino) — 历年挑战重组银层档案（2017–2025）

> **数据来源**：`docs/past/bronze/challenges_translated_zh.json` 与 `challenges_full.json`（Hack Junction 2017–2025 历史挑战全集）
> **收录挑战总数**：**43 个**
> **2026 归属赛道**：`Hardware Track (by Arduino)`

---

## 一、赛道定义与重组标准 (Track Definition & Reorganization Criteria)

# 2026 Hardware Track (by Arduino) — 历史挑战重组归档（Silver 层）

## 赛道定义与重组标准 (Track Definition & Reorganization Criteria)

**2026 对应赛道**：**Hardware Track (by Arduino)**

本目录将 Hack Junction 2017–2025 年历史挑战（Bronze 层全部 147 个挑战）中所有与 **智能硬件、传感器网络、嵌入式系统、机器人与自动化控制、可穿戴设备、毫米波雷达/事件相机及物理世界数字化（IoT & Physical Computing）** 相关的赛题进行了系统性重组与清洗：

1. **完整保留历史 `IoT & Hardware` 赛道全部 11 个挑战**：涵盖可穿戴运动传感器（Suunto Movesense）、跨平台嵌入式开发（The Qt Company / Raspberry Pi）、RFID 室内外定位（Finn-ID）、窄带物联网应急通信（Ericsson NB-IoT）、智能充电桩开发板（Ensto）、蓝牙 Mesh 边缘网关（Intel）、公寓楼宇智能交互屏（Aalto University）、室内传感器网络定位（Helvar）、电梯楼宇数字孪生（KONE）以及无线桑拿物联网传感器（Harvia）。
2. **深度挖掘并汇总其他 9 个历史赛道中的 32 个硬件/传感器/机器人挑战**：
   - **毫米波雷达与高速机器视觉传感器**：Sensofusion 微秒级神经拟态事件相机（Event Camera）高速物体与无人机追踪、Sensofusion 城市无线电波传播仿真、Helvar & VTT 60GHz/24GHz 毫米波雷达室内感知与非接触生命体征提取。
   - **可穿戴设备、智能眼镜与生物传感硬件**：Snap 第五代 Spectacles AR 智能眼镜、Pixieray 12通道红外眼动追踪智能眼镜、Huawei 意法半导体（STM SensorTile）嵌入式穿戴开发套件、Movesense 运动传感器。
   - **机器人、重型机械与特种硬件装备**：Alepa 糖果抓取机器人移动控制、CGI & KONE & Meyer Turku 豪华邮轮自主服务机器人、ABB 电动化互联船舶、Valmet 造纸机辊筒微米级磨削传感器与 XR 维护、Valmet x HSY 基于工业 OPC UA 协议的污水泵站自主控制、Planmeca 3D 口腔扫描仪与数字牙科综合治疗台硬件。
   - **智能建筑、智慧水务与环境传感硬件**：Helvar 智能照明传感器房间（PIR/热成像相机/情绪指环）、Vaisala 气象仪器与高温高湿桑拿传感仪表、Oras 蓝牙智能水龙头与数字花洒、Ensto 智能电采暖硬件、KONE x Granlund 建筑机电（MEP）硬件资产盘点。
   - **边缘计算集群、车载硬件与射频终端**：SUSE 树莓派（Raspberry Pi 3B+/4B+）uMEC 边缘计算集群、Ericsson / Nokia 5G 低时延边缘硬件控制、Fleetboard 奔驰重卡实时遥测 SDK、Rightware 智能汽车数字仪表盘、DENSO 车桩互联硬件、Stora Enso 智能包装/木结构 RFID 传感器、Nexi NFC 读卡器硬件协议解析、TrueFace Chui 智能门禁硬件、Trimble HoloLens 混合现实建筑测量。


---

## 二、挑战目录汇总表 (Summary Table)

| 序号 | 年份 | 合作方 | 挑战题目 | 原始历史赛道 | 核心主题 | 详情文档 |
| :---: | :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | **2017** | **Suunto** | 追踪任何移动的事物——基于 Movesense 构建运动、健康或其他领域的追踪概念 | `IoT & Hardware` | Movesense 可编程运动传感器与 C++ 嵌入式固件开发 | [📄 查看详情](./2017_Suunto_Track_Anything_That_Moves.md) |
| 2 | **2017** | **The Qt Company** | 跨平台桌面与嵌入式开发——在多个平台上打造终身难忘的用户体验 | `IoT & Hardware` | 基于树莓派（Raspberry Pi）与 Qt 的跨平台嵌入式设备 UI 与交互开发 | [📄 查看详情](./2017_The_Qt_Company_Cross_Platform_Embedded.md) |
| 3 | **2017** | **Finn-ID Oy** | 它到底在#?!哪里？——RFID来帮忙。 - 使用RFID标签创建导航应用。 | `IoT & Hardware` | RFID 读写器、电子标签与 Vuzix M300 智能眼镜室内外物品定位导航 | [📄 查看详情](./2017_Finn_ID_RFID_Navigation.md) |
| 4 | **2018** | **Espoo** | 触手可及的分析信息 | `IoT & Hardware` | 城市与区域多源开放数据自动采集、融合分析与嵌入式可视化组件 | [📄 查看详情](./2018_Espoo_Analyzed_Information_At_Your_Fingertips.md) |
| 5 | **2018** | **Ericsson** | 物联网拯救生命 | `IoT & Hardware` | 灾区断网环境下的分布式窄带物联网（NB-IoT）部署与可穿戴传感器网关 | [📄 查看详情](./2018_Ericsson_Saved_By_IoT.md) |
| 6 | **2018** | **Ensto** | 教电动汽车充电器新技巧 | `IoT & Hardware` | 基于硬件开发板与 Ensto 物联网平台的智能电动汽车充电桩功能扩展 | [📄 查看详情](./2018_Ensto_Teach_EV_Chargers_New_Tricks.md) |
| 7 | **2018** | **Intel** | 基于蓝牙Mesh的创新应用 | `IoT & Hardware` | 基于 IoT 边缘网关与 Bluetooth Mesh 无线传感器网络的智能空间控制 | [📄 查看详情](./2018_Intel_Innovative_Applications_With_Bluetooth_Mesh.md) |
| 8 | **2019** | **Aalto University** | 智能标牌——学生为学生设计 | `IoT & Hardware` | 公寓楼宇智能信息屏（Smart Signage）硬件形态设计与暖通/水电/网络物联网数据集成 | [📄 查看详情](./2019_Aalto_University_Smart_Signage.md) |
| 9 | **2021** | **Helvar** | 更明亮的空间：智能照明 | `IoT & Hardware` | 室内运动与音频传感器网络自标定、高频人流轨迹识别与地下车库多模态感知 | [📄 查看详情](./2021_Helvar_Brighter_Spaces_Intelligent_Lighting.md) |
| 10 | **2024** | **KONE** | 人人可为任何建筑创建BIM | `IoT & Hardware` | 既有建筑与电梯机电设备的快速 3D BIM 建模、IoT 远程运维与数字孪生 | [📄 查看详情](./2024_KONE_BIM_For_Any_Building.md) |
| 11 | **2025** | **Harvia** | 桑拿智能 | `IoT & Hardware` | Harvia 无线电池供电桑拿物联网传感器（温湿度/存在检测/BLE 信标）与智能家居集成 | [📄 查看详情](./2025_Harvia_Sauna_Intelligence.md) |
| 12 | **2017** | **Helvar** | 谁还需要电灯开关？—— 自动化整个灯光控制流程 | `AI & Data` | 基于被动红外（PIR）、FLIR 热成像相机、光照传感器与 Moodmetric 情绪戒指的自动照明硬件控制 | [📄 查看详情](./2017_Helvar_Who_Needs_A_Light_Switch.md) |
| 13 | **2017** | **Planmeca Oy** | 重塑牙科护理的未来——深入技术世界，用技术革新牙科护理。 | `Health` | 数字牙科综合治疗台、3D 口腔成像设备与口内扫描仪（Intraoral Scanner）硬件数字化 | [📄 查看详情](./2017_Planmeca_Reshaping_Dental_Care.md) |
| 14 | **2017** | **Trimble** | 改变世界的建造方式！—— 打造建筑行业数字化领域的下一个重大创新。 | `AI & Data` | 物理建筑空间 3D 测量传感与 Microsoft HoloLens 混合现实硬件交互 | [📄 查看详情](./2017_Trimble_Transform_The_Way_The_World_Builds.md) |
| 15 | **2017** | **TrueFace.ai** | 面向所有人的人脸识别——使用一个或多个 TrueFace.ai 人脸识别 API 创建应用 | `AI & Data` | 基于 Chui 智能门铃与门禁终端硬件的人脸识别与防伪检测系统 | [📄 查看详情](./2017_TrueFace_Facial_Recognition_For_Everyone.md) |
| 16 | **2017** | **Stora Enso's challenge in cooperation with Siili Solutions** | 更智能地存储——你的空间里有智能生命吗？ | `Sustainability` | RFID 读写器/天线阵列与内置温湿度传感器的 CLT/LVL 智能木结构建筑组件 | [📄 查看详情](./2017_Stora_Enso_Siili_Store_Smarter.md) |
| 17 | **2018** | **Outotec** | 我听见工厂里的声音 | `Sustainability` | 冶金工厂高温重型设备的声学（Audio）与运动（Motion）传感器故障诊断与预警 | [📄 查看详情](./2018_Outotec_I_Hear_Voices_In_My_Factory.md) |
| 18 | **2018** | **Helvar** | 建筑大脑 | `AI & Data` | 打通楼宇照明控制传感器与通风暖通硬件的建筑级智能控制中枢 | [📄 查看详情](./2018_Helvar_The_Brain_Of_The_Building.md) |
| 19 | **2018** | **Alepa** | 零食机器人黑客松 | `Entertainment` | 通过移动设备远程控制实体抓取与结算糖果机器人（Pick 'n' Pay Candy Robot） | [📄 查看详情](./2018_Alepa_Munchies_Robot_Hack.md) |
| 20 | **2018** | **Fleetboard** | 卡车 X 代码 | `Urban & Mobility` | 基于梅赛德斯-奔驰重型卡车车载传感器与实时遥测数据（Live Vehicle Data）的车载应用开发 | [📄 查看详情](./2018_Fleetboard_Trucks_X_Code.md) |
| 21 | **2018** | **Rightware** | 互联汽车用户体验挑战赛 | `Sustainability` | 智能网联汽车数字仪表盘、车载多屏座舱与车内外环境感知自适应交互 | [📄 查看详情](./2018_Rightware_Connected_Car_UX.md) |
| 22 | **2018** | **Ensto** | 自适应智能电加热 | `Sustainability` | 可编程智能电采暖硬件设备（Smart Electric Heating）的自适应温控与能耗优化 | [📄 查看详情](./2018_Ensto_Adaptive_Smart_Electric_Heating.md) |
| 23 | **2018** | **ABB** | 船长会梦见电动船吗？ | `Other` | ABB 电动化、数字化与互联化未来船舶（Electric & Connected Ships）硬件与控制系统创新 | [📄 查看详情](./2018_ABB_Do_Captains_Dream_Of_Electric_Ships.md) |
| 24 | **2018** | **Nokia** | 边缘生活 | `Entertainment` | 基于 Nokia 5G 超低时延无线接入网与边缘计算（MEC）的实时硬件交互应用 | [📄 查看详情](./2018_Nokia_Living_On_The_Edge.md) |
| 25 | **2018** | **Movesense By Suunto** | 追踪一切运动之物 | `Entertainment` | 基于 Movesense 惯性测量单元（IMU）传感器的运动器械、人体、生产线与桥梁监测 | [📄 查看详情](./2018_Movesense_By_Suunto_Track_Anything_That_Moves.md) |
| 26 | **2018** | **Vaisala** | 真正有用的天气 | `Sustainability` | Vaisala 高精度气象与环境测量仪器数据在航海、农业、航空与建筑场景的融合应用 | [📄 查看详情](./2018_Vaisala_Actually_Useful_Weather.md) |
| 27 | **2018** | **Vaisala** | 改造桑拿 | `Sustainability` | 极端高温高湿环境下的工业级桑拿传感测量仪器（替代传统机械温度计）与数字化体验 | [📄 查看详情](./2018_Vaisala_Hack_The_Sauna.md) |
| 28 | **2018** | **Cisco** | Meraki - 捕捉生物 | `Entertainment` | 基于 Cisco Meraki 蓝牙信标（BLE Beacon）与 Wi-Fi 无线定位硬件的室内空间感知 | [📄 查看详情](./2018_Cisco_Meraki_Capture_The_Creature.md) |
| 29 | **2019** | **Ericsson** | 5G 绿色城市交通 | `Urban & Mobility` | 基于 5G 低时延通信网络的车队集中式实时控制与多源传感器协同调度 | [📄 查看详情](./2019_Ericsson_Greener_City_Transport_With_5G.md) |
| 30 | **2019** | **Valmet** | 未来的服务车间 | `AI & Data` | 造纸机巨型辊筒微米级磨削传感器测量数据、Node-RED 硬件仿真与 XR 头显交互 | [📄 查看详情](./2019_Valmet_Service_Workshop_Of_The_Future.md) |
| 31 | **2019** | **Helvar & VTT** | 用雷达技术点亮空间 | `AI & Data` | 60 GHz 2D 毫米波成像雷达与 24 GHz 生命体征雷达传感器 + 智能灯具硬件实时联调 | [📄 查看详情](./2019_Helvar_VTT_Making_Spaces_Brighter_With_Radar.md) |
| 32 | **2019** | **SUSE** | 开放开放城市 | `Urban & Mobility` | 基于 Raspberry Pi 3B+/4B+ 硬件集群（uMEC 边缘节点）与专用 Wi-Fi 网络的边缘计算平台 | [📄 查看详情](./2019_SUSE_Open_Open_City.md) |
| 33 | **2022** | **Oras** | 最智能的用水体验 | `Sustainability` | Oras Hydractiva 数字花洒与免接触蓝牙智能水龙头（SMART Faucets）用水传感与漏水定位 | [📄 查看详情](./2022_Oras_The_Smartest_Water_Experience.md) |
| 34 | **2022** | **CGI & KONE & Meyer Turku** | 与机器人共游 | `Other` | 大型豪华邮轮上的自主服务机器人（Service Robots）与自动化客流/物流硬件系统设计 | [📄 查看详情](./2022_CGI_KONE_Meyer_Turku_Cruising_With_Robots.md) |
| 35 | **2022** | **Nexi** | 破解支付 | `Finance` | 基于外置 NFC 读卡器硬件与移动 NFC 模块的金融 IC 卡底层通信协议解析 | [📄 查看详情](./2022_Nexi_Crack_The_Payments.md) |
| 36 | **2024** | **Pixieray** | 窥探双眼背后 | `Entertainment` | 集成单眼 6 颗红外眼动传感器、加速度计与环境光/紫外线传感器的智能眼镜硬件数据分析 | [📄 查看详情](./2024_Pixieray_Peek_Behind_The_Eyes.md) |
| 37 | **2024** | **Huawei** | 感知运动 | `AI & Data` | 基于意法半导体 STMicroelectronics SensorTile 开发套件与智能手表的实时运动/情绪传感算法 | [📄 查看详情](./2024_Huawei_Sense_The_Motion.md) |
| 38 | **2025** | **KONE x Granlund** | 现代化万亿欧元库存 | `AI & Data` | 建筑机电暖通给排水（MEP）物理设备资产的自动化巡检采集与终极数字孪生构建 | [📄 查看详情](./2025_KONE_Granlund_Modernizing_Trillion_Euro_Inventory.md) |
| 39 | **2025** | **Denso** | ChargeID：可信电动汽车服务 | `Urban & Mobility` | 汽车一级供应商 DENSO 车端硬件、智能充电桩与去中心化身份（DID）安全互联 | [📄 查看详情](./2025_Denso_ChargeID_Trusted_EV_Services.md) |
| 40 | **2025** | **Sensofusion** | 灯光，摄像，反应！ | `AI & Data` | 微秒级神经拟态事件相机（Event Camera）高速物理运动检测与无人机追踪 | [📄 查看详情](./2025_Sensofusion_Lights_Camera_Reaction.md) |
| 41 | **2025** | **Sensofusion** | 无线电城市 | `Entertainment` | 三维城市环境中移动电台、车载与无人机射频无线电波（Radio Waves）物理传播与多径反射仿真 | [📄 查看详情](./2025_Sensofusion_Radio_City.md) |
| 42 | **2025** | **Valmet x HSY** | 智能流量优化 | `Sustainability` | 基于工业自动化协议 OPC UA 与数字孪生的城市污水泵站硬件集群自主协同控制 | [📄 查看详情](./2025_Valmet_HSY_Intelligent_Flow_Optimization.md) |
| 43 | **2025** | **Snap Inc.** | 你的真实世界AI伴侣 | `AI & Data` | 基于第五代 Snap Spectacles AR 智能眼镜硬件的空间感知与全天候个人 AI 伴侣 | [📄 查看详情](./2025_Snap_Your_Real_World_AI_Companion.md) |

---

## 三、结构化汇编与详细速查 (Structured Breakdown & Consolidated Listing)

### 1. [2017] Suunto — 追踪任何移动的事物——基于 Movesense 构建运动、健康或其他领域的追踪概念

- **单题档案**: [2017_Suunto_Track_Anything_That_Moves.md](./2017_Suunto_Track_Anything_That_Moves.md)
- **原始赛道**: `IoT & Hardware` | **所属子方向**: 可穿戴设备、运动与生物传感器 (Wearables, Motion & Biometric Sensors)
- **核心主题**: Movesense 可编程运动传感器与 C++ 嵌入式固件开发
- **归类理由**: 原属 IoT & Hardware 赛道。围绕 Suunto Movesense 可编程运动传感器硬件、烧录调试夹具（Programming Jigs）及嵌入式 C++ 固件与移动端 REST/BLE 接口开发，是典型的微型传感器与可穿戴硬件开发挑战。

#### 挑战描述

世界上充满了移动的事物——无论是运动员的身体或运动装备、生产线上的机器、交通中的桥梁、我们日常生活中的任何人，还是我们能想象到的任何其他事物。通常，了解这些事物如何以及何时移动——或者不移动——会非常有价值。Movesense 提供可编程的运动传感器、API 和软件库，使您能够快速构建自己的传感器功能和移动应用程序，以追踪任何移动的事物。帮助世界保持移动！

#### 可用资源

更多信息请访问 www.movesense.com。
https://bitbucket.org/suunto/movesense-device-lib （9月初公开）
https://bitbucket.org/suunto/movesense-mobile-lib （即将公开）

#### 奖项设置

所有提交基于 Movesense 项目的团队都可以保留开发中使用的 Movesense 传感器。作为获胜奖品，我们将为三个类别中最佳解决方案的每位团队成员颁发最新的 Suunto Spartan 手表：1. 运动 2. 健康与福祉 3. 通用物联网。此外，拥有运动与日常健康商业可行解决方案的团队将有机会与 Suunto 洽谈合作选项。

---

### 2. [2017] The Qt Company — 跨平台桌面与嵌入式开发——在多个平台上打造终身难忘的用户体验

- **单题档案**: [2017_The_Qt_Company_Cross_Platform_Embedded.md](./2017_The_Qt_Company_Cross_Platform_Embedded.md)
- **原始赛道**: `IoT & Hardware` | **所属子方向**: 嵌入式系统、边缘计算与通信硬件 (Embedded Systems, Edge Computing & Connectivity)
- **核心主题**: 基于树莓派（Raspberry Pi）与 Qt 的跨平台嵌入式设备 UI 与交互开发
- **归类理由**: 原属 IoT & Hardware 赛道。官方现场提供多块 Raspberry Pi 嵌入式开发板及外设套件，要求使用 C++/Qt 构建跨桌面端与嵌入式智能硬件终端的高性能交互系统。

#### 挑战描述

创建流畅、高性能且直观的UI、应用程序和嵌入式设备——所有平台使用同一套代码库。在我们的家庭、汽车、工作场所和口袋中，智能设备无处不在。Qt确保您可以创建独特且现代的联网设备，在众多产品中脱颖而出。

#### 可用资源

您可以在以下网站找到大量Qt资源和帮助，例如：
- http://doc.qt.io
- http://forum.qt.io
以及其他qt.io网站

#### 奖项设置

本次挑战的奖品是完整的Qt开发者许可证。其他奖品将在稍后公布，请关注此页面！

---

### 3. [2017] Finn-ID Oy — 它到底在#?!哪里？——RFID来帮忙。 - 使用RFID标签创建导航应用。

- **单题档案**: [2017_Finn_ID_RFID_Navigation.md](./2017_Finn_ID_RFID_Navigation.md)
- **原始赛道**: `IoT & Hardware` | **所属子方向**: 空间定位、RFID 与智能终端硬件 (RFID, Indoor Positioning & Smart Terminals)
- **核心主题**: RFID 读写器、电子标签与 Vuzix M300 智能眼镜室内外物品定位导航
- **归类理由**: 原属 IoT & Hardware 赛道。现场提供 RFID 读写器、RFID 标签、Vuzix M300 智能眼镜、Honeywell 工业移动终端与 Toshiba 打印机，聚焦射频识别硬件与增强现实导航集成。

#### 挑战描述

如今，技术使得定位物品位置成为可能。通过使用这项技术，我们可以促进和改善人们和企业的日常生活。我们可以创建清晰的数据视图。

#### 可用资源

您将在活动期间获得所有必要的详细信息。

#### 奖项设置

团队成员奖（我们假设4-6人团队）
一等奖：团队每位成员获得100美元的Amazon礼品券
二等奖：团队每位成员获得50美元的Amazon礼品券
团队成员奖（我们假设4-6人团队）
一等奖：团队每位成员获得100美元的Amazon礼品券
二等奖：团队每位成员获得50美元的Amazon礼品券

---

### 4. [2018] Espoo — 触手可及的分析信息

- **单题档案**: [2018_Espoo_Analyzed_Information_At_Your_Fingertips.md](./2018_Espoo_Analyzed_Information_At_Your_Fingertips.md)
- **原始赛道**: `IoT & Hardware` | **所属子方向**: 智能建筑、工业物联网与数字孪生 (Smart Buildings, Industrial IoT & Digital Twins)
- **核心主题**: 城市与区域多源开放数据自动采集、融合分析与嵌入式可视化组件
- **归类理由**: 原属 2018 年 IoT & Hardware 赛道官方赛题。聚焦埃斯波（Espoo）城市级多源传感器与公共开放数据的自动化汇聚、实时更新与面向企业的嵌入式信息看板。

#### 挑战描述

开发一种或多种解决方案，通过连接、分析和可视化开放数据集来生成信息。该解决方案应能够嵌入网站、自动更新信息，并生成尤其令企业感兴趣的信息。
国家、地区和地方政府生成了不计其数的各种开放数据集。通过使用数据分析工具，这些开放数据集可以转化为有用的区域信息，埃斯波市已经在某种程度上做到了这一点。
然而，这些已经分析过的区域信息往往分散或难以找到。此外，由于财政资源有限，许多区域数据尚未得到分析。因此，各种私营主体在获取所有相关且必要的信息时遇到困难。
埃斯波市正在寻找具有成本效益的方法，将数据集转化为有用的区域信息，并将其分发给已经位于埃斯波地区或计划迁入/扩展到埃斯波地区的各种私营主体。
挑战在于开发一种或多种解决方案，通过连接、分析和可视化开放数据集来生成信息。该解决方案应生成尤其令企业感兴趣的信息。此外，该解决方案应能够嵌入不同类型的网站并自动更新信息。

---

### 5. [2018] Ericsson — 物联网拯救生命

- **单题档案**: [2018_Ericsson_Saved_By_IoT.md](./2018_Ericsson_Saved_By_IoT.md)
- **原始赛道**: `IoT & Hardware` | **所属子方向**: 嵌入式系统、边缘计算与通信硬件 (Embedded Systems, Edge Computing & Connectivity)
- **核心主题**: 灾区断网环境下的分布式窄带物联网（NB-IoT）部署与可穿戴传感器网关
- **归类理由**: 原属 IoT & Hardware 赛道。结合通信基础设施损毁场景下的分布式窄带物联网（NB-IoT）部署方案，以及利用可穿戴设备传感器实时采集生命体征并充当物联网云端网关。

#### 挑战描述

设想一个场景：自然灾害袭击了你的社区，本地通信基础设施被摧毁。在混乱之中，你如何联系家人和亲人，告诉他们你依然在这里，活蹦乱跳？或者表明你受伤了、处于危险中、需要帮助？
智能手机和可穿戴设备收集了大量数据，这些数据可以用来指示佩戴者的行踪和状况。传感器数据流可以通过云端（或其他任何合适的地方）的机器学习解决方案进行分析和解读，从而生成并提供危险、存活等指示。
这个挑战分为两部分：
- 提供（至少）一个概念性方案，并附上技术可行性证据，说明如何在本地基础设施瘫痪时创建和部署分布式窄带物联网连接。
- 构建一个应用程序，演示适用的可穿戴设备提供传感器数据并充当通往物联网云端的网关的能力。请注意，同样的解决方案也可用于本地通信基础设施完好的较小规模事件（如车祸）。

---

### 6. [2018] Ensto — 教电动汽车充电器新技巧

- **单题档案**: [2018_Ensto_Teach_EV_Chargers_New_Tricks.md](./2018_Ensto_Teach_EV_Chargers_New_Tricks.md)
- **原始赛道**: `IoT & Hardware` | **所属子方向**: 智能能源、电动出行与车载硬件 (Smart Energy, EV Charging & Mobility Hardware)
- **核心主题**: 基于硬件开发板与 Ensto 物联网平台的智能电动汽车充电桩功能扩展
- **归类理由**: 原属 IoT & Hardware 赛道。要求在现场提供的硬件开发板（Development Boards）上开发新功能，并与 Ensto 智能充电桩 IoT 后端 REST API 深度集成。

#### 挑战描述

汽车充电远不止插上电源给电池充电那么简单。汽车会在家庭、工作场所、酒店、购物中心、停车场和机场等场所充电，仅举几例，而在所有这些场所中，用户可能有不同的需求。在一个或多个细分场景中，为电动汽车驾驶员创造最佳的充电体验。利用 Ensto 平台提供的 REST API 以及在提供的开发板上开发的附加功能来实现/演示此解决方案。您还可以利用我们从后端服务中已收集的 IoT 数据来完善您的解决方案。

---

### 7. [2018] Intel — 基于蓝牙Mesh的创新应用

- **单题档案**: [2018_Intel_Innovative_Applications_With_Bluetooth_Mesh.md](./2018_Intel_Innovative_Applications_With_Bluetooth_Mesh.md)
- **原始赛道**: `IoT & Hardware` | **所属子方向**: 嵌入式系统、边缘计算与通信硬件 (Embedded Systems, Edge Computing & Connectivity)
- **核心主题**: 基于 IoT 边缘网关与 Bluetooth Mesh 无线传感器网络的智能空间控制
- **归类理由**: 原属 IoT & Hardware 赛道。要求在 IoT 边缘网关（Edge Gateway）上构建与蓝牙 Mesh（Bluetooth® Mesh）无线传感网络设备通信的智能照明、温控、安防或智能工牌系统。

#### 挑战描述

蓝牙® Mesh组网技术为与周围环境交互创造了新机遇，无论是通过智能照明、供暖/制冷和安全系统让家庭或办公室更智能，还是构建无线传感器网络。
本挑战赛要求开发一款运行于物联网边缘网关的应用程序，该程序能够与蓝牙® Mesh网络设备通信并利用其功能。此类应用的示例包括消息板、智能徽章系统或传感器数据采集系统。

---

### 8. [2019] Aalto University — 智能标牌——学生为学生设计

- **单题档案**: [2019_Aalto_University_Smart_Signage.md](./2019_Aalto_University_Smart_Signage.md)
- **原始赛道**: `IoT & Hardware` | **所属子方向**: 智能建筑、工业物联网与数字孪生 (Smart Buildings, Industrial IoT & Digital Twins)
- **核心主题**: 公寓楼宇智能信息屏（Smart Signage）硬件形态设计与暖通/水电/网络物联网数据集成
- **归类理由**: 原属 IoT & Hardware 赛道。针对 AYY 学生公寓 2600 套住房的楼道智能交互屏进行硬件与软件设计，接入楼宇暖通空调（HVAC）、水电能耗与网络负载等真实传感器数据。

#### 挑战描述

阿尔托大学学生会（AYY）拥有约2600套公寓，居住着约3500名租户。AYY一直计划在其公寓楼的楼梯间和走廊安装信息屏幕（智能标牌）。本次挑战旨在寻找这些“智能标牌”屏幕在硬件方面，但最重要的是在软件方面可以如何实现的解决方案和创意。它们可以显示哪些信息，可以包含哪些功能？

AYY希望看到关于哪些相关数据和功能可以整合到这些屏幕中的不同创意和概念。例如，这些数据可以包括建筑物的供暖、用水和用电消耗数据、网络使用数据、AYY的新闻和广告、自动更新的租户列表，以及各种有趣的功能，这些功能还可以在不同走廊和建筑物的屏幕之间运行。在最佳情况下，本次挑战的解决方案还可以改善居住在AYY住房中的学生之间的社区体验。

#### 可用资源

AYY将提供：AYY的IT团队将在周末期间在线帮助您完成挑战。我们将带来一个来自我们其中一栋建筑的匿名网络使用数据和HVAC数据包供您使用。

---

### 9. [2021] Helvar — 更明亮的空间：智能照明

- **单题档案**: [2021_Helvar_Brighter_Spaces_Intelligent_Lighting.md](./2021_Helvar_Brighter_Spaces_Intelligent_Lighting.md)
- **原始赛道**: `IoT & Hardware` | **所属子方向**: 智能建筑、工业物联网与数字孪生 (Smart Buildings, Industrial IoT & Digital Twins)
- **核心主题**: 室内运动与音频传感器网络自标定、高频人流轨迹识别与地下车库多模态感知
- **归类理由**: 原属 IoT & Hardware 赛道。基于室内照明系统的运动传感器与车库音频/运动传感器时序数据，解决大规模传感器网络在建筑平面图上的自动定位及人车行为识别。

#### 挑战描述

在这个挑战中，我们要求您利用、应用和可视化传感器数据，以了解建筑的使用情况，并优化传感器网络在建筑中的初始部署。您可以选择挑战的三个部分中的一个或全部进行工作。

所有设备在哪里？
我们通常花费大量精力在平面图上识别和定位大量传感器。我们能否简化这个过程，并利用一部分传感器的数据自动将其余传感器放置在平面图上？

每个人要去哪里？
运动传感器有助于确定空间中的活动量。我们也知道空间的类型，例如走廊或通道。鉴于传感器生成数十万个运动事件，我们能否识别建筑物中使用最频繁的路径？

神秘车库
车库中有移动的车辆和行人。我们有运动传感器和音频传感器。我们能否识别车库中正在发生的事情？是否有车辆进出？行人是走向电梯，还是上车？

#### 可用资源

我们将提供不同平面图的布局，包含设备位置以及运动和音频事件的时间序列。

数据集：
建筑物：参与者将获得来自室内场所的数据集。数据将完全匿名化。平面图将包含设备及其位置。数据集将是平面图上所有传感器的运动事件时间序列。

车库：参与者将获得来自室内车库的训练数据集，使用运动和音频传感器收集。

鼓励您使用其他数据源，并随时使用来自其他Junction挑战的数据或将您的想法与其他挑战结合，如果您认为合适。

---

### 10. [2024] KONE — 人人可为任何建筑创建BIM

- **单题档案**: [2024_KONE_BIM_For_Any_Building.md](./2024_KONE_BIM_For_Any_Building.md)
- **原始赛道**: `IoT & Hardware` | **所属子方向**: 智能建筑、工业物联网与数字孪生 (Smart Buildings, Industrial IoT & Digital Twins)
- **核心主题**: 既有建筑与电梯机电设备的快速 3D BIM 建模、IoT 远程运维与数字孪生
- **归类理由**: 原属 IoT & Hardware 赛道。聚焦电梯、扶梯等楼宇机电硬件设备的 IoT 智能维护与 3D 数字孪生（BIM）快速构建，实现物理建筑设备状态的实时远程可视化。

#### 挑战描述

变革销售：只需点击几下，即可将建筑3D建模和导出游戏化。

我们的行业正通过物联网和数字孪生迈向更智能的维护，实现远程操作以及建筑、设备和人员的实时3D可视化。但存在一个重大挑战：许多老旧建筑没有3D模型或BIM，这限制了改进维护和现代化的能力。这一差距拖慢了我们的步伐，阻碍了我们实现运营效率最大化。帮助我们为任何建筑及其设备创建3D BIM和数字孪生，以解决这一行业范围内的巨大问题，推动更智能、更快速的维护和现代化，并为完全互联、面向未来的运营打开大门。

---

### 11. [2025] Harvia — 桑拿智能

- **单题档案**: [2025_Harvia_Sauna_Intelligence.md](./2025_Harvia_Sauna_Intelligence.md)
- **原始赛道**: `IoT & Hardware` | **所属子方向**: 智能建筑、工业物联网与数字孪生 (Smart Buildings, Industrial IoT & Digital Twins)
- **核心主题**: Harvia 无线电池供电桑拿物联网传感器（温湿度/存在检测/BLE 信标）与智能家居集成
- **归类理由**: 原属 IoT & Hardware 赛道。现场提供 Harvia 最新研发的 Wi-Fi/蜂窝网络无线电池供电桑拿传感器（含温度、湿度测量、人体存在检测与蓝牙信标）及 Matter/智能家居与可穿戴设备集成接口。

#### 挑战描述

利用 AI 工具重新构想桑拿体验——展示 AI 原生编码如何加速你的解决方案。

Harvia 是桑拿和水疗解决方案领域的全球领导者，如今正从硬件制造商转型为数字健康先锋。借助全新的 IoT 桑拿传感器和 API，我们邀请开发者创建下一代桑拿和健康应用程序。在 Junction 和 Harvia，我们尤其希望看到解决方案中 AI 原生且流畅地使用 AI 工具——从构思到原型设计——展示现代开发如何加速更好的成果。无论你的概念是让桑拿更智能、更具社交性，还是全球可访问，关键都是展示真正的 AI 原生构建。

你的任务是为 Harvia 构建一个创新解决方案，将桑拿体验提升到新水平。可能使用 Harvia 的新桑拿传感器平台（Wi-Fi 或蜂窝连接的无线电池供电桑拿传感器，包括温度和湿度测量、存在检测、蓝牙信标）。挑战是开放式的：你可以创建预测模型以更顺畅地使用桑拿、个性化健康建议、与其他相关设备（例如可穿戴设备）集成、社交和游戏化体验，或全新的数字商业模式。同时，关键是在开发过程中流畅且原生地展示 AI 工具的使用——从编码到测试和迭代。放眼全球——增长最快的市场是美国，那里的桑拿文化仍在兴起。我们希望你能设计出能打动特定但相关用户群体的东西，或者能够跨文化扩展，从芬兰家庭到洛杉矶的豪华水疗中心。

#### 可用资源

我们带来的技术列表：
桑拿传感器设备（安装在 Junction 场地桑拿房中的演示单元）
Harvia GraphQL API（预发布访问）
历史桑拿会话的示例数据集
用于存在检测和游戏化的蓝牙信标功能
来自 Harvia 和 SÄDE Innovations 的现场技术导师

#### 奖项设置

Junction 获胜者获得 €1,500 现金奖金池，30 天后续竞赛额外获得 €1,500。获胜者获得 Harvia 桑拿传感器设备，以及参加为期一个月的挑战并获得扩展奖品的机会。表现最佳者还可能被直接招募到 Harvia 的新数字团队。

---

### 12. [2017] Helvar — 谁还需要电灯开关？—— 自动化整个灯光控制流程

- **单题档案**: [2017_Helvar_Who_Needs_A_Light_Switch.md](./2017_Helvar_Who_Needs_A_Light_Switch.md)
- **原始赛道**: `AI & Data` | **所属子方向**: 智能建筑、工业物联网与数字孪生 (Smart Buildings, Industrial IoT & Digital Twins)
- **核心主题**: 基于被动红外（PIR）、FLIR 热成像相机、光照传感器与 Moodmetric 情绪戒指的自动照明硬件控制
- **归类理由**: 虽原属 AI & Data 赛道，但现场搭建了真实 Smart Room 硬件环境，提供被动红外传感器（PIR）、光照度传感器、FLIR Lepton 红外热像仪、Moodmetric 皮肤电指环及物理按键与专业灯具控制 API，属于典型的多传感器融合与智能硬件控制挑战。

#### 挑战描述

人们太懒了，不想手动控制灯光！帮助我们实现整个流程的自动化，或者至少为用户提供真正无缝的控制体验。通过寻找新方法，利用智能算法和/或最新传感器来提升人们的福祉，测试你的创新能力……

#### 奖项设置

一等奖：获胜团队将获得 Hubsan H501S 四轴飞行器（或同等产品）。荣誉奖：入选团队将获得 Amazon Echo Dot 设备。

---

### 13. [2017] Planmeca Oy — 重塑牙科护理的未来——深入技术世界，用技术革新牙科护理。

- **单题档案**: [2017_Planmeca_Reshaping_Dental_Care.md](./2017_Planmeca_Reshaping_Dental_Care.md)
- **原始赛道**: `Health` | **所属子方向**: 机器人、重型装备与特种医疗硬件 (Robotics, Heavy Machinery & Specialized Medical Hardware)
- **核心主题**: 数字牙科综合治疗台、3D 口腔成像设备与口内扫描仪（Intraoral Scanner）硬件数字化
- **归类理由**: 虽原属 Health 赛道，但合作方 Planmeca 将数字牙科治疗台、3D 锥形束 CT 成像设备与高精度口内光学扫描仪硬件带到现场供参赛者测试，是医疗精密仪器硬件与三维数字孪生的结合。

#### 挑战描述

数字革命正在改变整个医疗保健领域，患者护理不再仅仅是治疗病患，而是从一开始就预防疾病。对于医疗保健专业人员来说，新技术是实现更高效、更准确、更舒适护理的途径。数字解决方案可以拓展健康和牙科护理的边界——护理路径可以在就诊前很久就开始，并在就诊后持续很久。借助先进的三维成像技术，我们已经可以创建患者的精确数字孪生，这引发了一个问题：我们是否还需要去看牙医？

#### 可用资源

更多详细信息和样本数据将很快在 Planmeca 的 Junction 网站上提供：www.planmeca.com/junction。

#### 奖项设置

奖项待公布。

---

### 14. [2017] Trimble — 改变世界的建造方式！—— 打造建筑行业数字化领域的下一个重大创新。

- **单题档案**: [2017_Trimble_Transform_The_Way_The_World_Builds.md](./2017_Trimble_Transform_The_Way_The_World_Builds.md)
- **原始赛道**: `AI & Data` | **所属子方向**: 空间定位、RFID 与智能终端硬件 (RFID, Indoor Positioning & Smart Terminals)
- **核心主题**: 物理建筑空间 3D 测量传感与 Microsoft HoloLens 混合现实硬件交互
- **归类理由**: 虽原属 AI & Data 赛道，但聚焦从物理三维世界到数字模型的传感器测量转换，并在现场提供 Microsoft HoloLens 混合现实头显与 AR/VR 硬件设备。

#### 挑战描述

我们生活在一个三维世界中，业务中需要处理大量3D数据。挑战在于从现实到数字，再回到现有世界的旅程。你是否曾用手机测量过你的房子或虚拟布置家具？现在有机会让你全力以赴，利用3D建模、图像、机器学习、传感器、增强/虚拟现实、语音识别或任何能创造神奇效果的技术，打造突破性的应用。把我传送上去吧，Scotty！

#### 可用资源

https://connect.trimble.com/developer.html

#### 奖项设置

待定待定

---

### 15. [2017] TrueFace.ai — 面向所有人的人脸识别——使用一个或多个 TrueFace.ai 人脸识别 API 创建应用

- **单题档案**: [2017_TrueFace_Facial_Recognition_For_Everyone.md](./2017_TrueFace_Facial_Recognition_For_Everyone.md)
- **原始赛道**: `AI & Data` | **所属子方向**: 空间定位、RFID 与智能终端硬件 (RFID, Indoor Positioning & Smart Terminals)
- **核心主题**: 基于 Chui 智能门铃与门禁终端硬件的人脸识别与防伪检测系统
- **归类理由**: 虽原属 AI & Data 赛道，但其核心硬件载体与优胜奖品均为 Chui 智能人脸识别门铃与实体门禁控制硬件（Facial Recognition Security & Access Control Hardware）。

#### 挑战描述

人脸识别正在席卷一切。就连 Apple 也参与其中！从刷脸支付、刷脸认证、情绪检测、面部特征检测、监控、自动签到等等，用例无穷无尽。

参与其中，应用我们深度学习驱动的人脸识别技术，打造你自己的应用。

#### 可用资源

API 文档：https://getchui.github.io/chuiaidocs/#introduction

如有任何问题，请加入我们的 Slack 频道 - https://join.slack.com/t/truefaceaicommunity/shared_invite/MjM4MTE3NDgxMTg2LTE1MDQ4NjM0NzEtNzQ4ZTczZTNjNQ

#### 奖项设置

获胜团队的每位成员将获得一台 Chui 设备。它是一套人脸识别安全系统（可用作智能门铃或门禁系统），通过应用程序进行管理。获胜团队的每位成员将获得一台 Chui 设备。它是一套人脸识别安全系统（可用作智能门铃或门禁系统），通过应用程序进行管理。

---

### 16. [2017] Stora Enso's challenge in cooperation with Siili Solutions — 更智能地存储——你的空间里有智能生命吗？

- **单题档案**: [2017_Stora_Enso_Siili_Store_Smarter.md](./2017_Stora_Enso_Siili_Store_Smarter.md)
- **原始赛道**: `Sustainability` | **所属子方向**: 空间定位、RFID 与智能终端硬件 (RFID, Indoor Positioning & Smart Terminals)
- **核心主题**: RFID 读写器/天线阵列与内置温湿度传感器的 CLT/LVL 智能木结构建筑组件
- **归类理由**: 虽原属 Sustainability 赛道，但现场提供全套 RFID 标签、读写器、天线硬件以及实体储物对象，并结合 Stora Enso 内置湿度与定位传感器的智能木结构建筑部件开展物联网开发。

#### 挑战描述

你的地下室或阁楼里有储物空间吗？你还记得里面放了什么吗？如今我们拥有的物品如此之多，对我们许多人来说，尝试整理私人或工作物品的经历颇具挑战性。问题在于，很多时候我们不记得自己拥有什么，或者不知道那些东西放在哪里，甚至不知道它们是否还能使用。

听起来很熟悉？那么，为什么不帮助我们构思一个智能储物空间呢！
你可以考虑解决这些问题，针对以下两种场景之一：
1）住宅楼（私人储物空间），或
2）学校、医院、图书馆或其他公共建筑（公共储物空间）

你的智能储物空间会是什么样子？它会有助于减少浪费（比如回收或再利用）吗？还是能跟踪并优化你物品的价值？有助于优化整体仓库管理吗？

#### 奖项设置

获胜团队将获得前往一个欧洲首都的旅程奖励，包括一些智慧城市体验以及参观Stora Enso智能建筑组件制造单位。第二名的团队将获得在Siili Academy免费任选一门课程的机会。获胜团队将获得前往一个欧洲首都的旅程奖励，包括一些智慧城市体验以及参观Stora Enso智能建筑组件制造单位。第二名的团队将获得在Siili Academy免费任选一门课程的机会。

---

### 17. [2018] Outotec — 我听见工厂里的声音

- **单题档案**: [2018_Outotec_I_Hear_Voices_In_My_Factory.md](./2018_Outotec_I_Hear_Voices_In_My_Factory.md)
- **原始赛道**: `Sustainability` | **所属子方向**: 智能建筑、工业物联网与数字孪生 (Smart Buildings, Industrial IoT & Digital Twins)
- **核心主题**: 冶金工厂高温重型设备的声学（Audio）与运动（Motion）传感器故障诊断与预警
- **归类理由**: 虽原属 Sustainability 赛道，但核心是基于工业现场声学传感器与运动振动传感器采集的物理信号，对冶金工厂重型机械进行预测性维护与故障诊断。

#### 挑战描述

在远离Junction的某个地方，有一座工厂，生产着我们日常所需的贵重金属。这是一个复杂的过程，需要消耗大量能源并处于极高温度下，其中可能出现问题，有可能对人员和设备造成损害。基于提供的音频和运动数据以及故障事件，您能否诊断工厂的运行状况，并预测未来的故障，或者预防它们？您能否将数据可视化，使其能够向操作员传达信息，帮助安全地指导他们？我们甚至不知道数据与故障之间是否存在任何关联（理论上应该存在），因此我们重视良好的尝试以及处理和可视化数据的巧妙新方法。让工厂成为更安全的工作场所！

---

### 18. [2018] Helvar — 建筑大脑

- **单题档案**: [2018_Helvar_The_Brain_Of_The_Building.md](./2018_Helvar_The_Brain_Of_The_Building.md)
- **原始赛道**: `AI & Data` | **所属子方向**: 智能建筑、工业物联网与数字孪生 (Smart Buildings, Industrial IoT & Digital Twins)
- **核心主题**: 打通楼宇照明控制传感器与通风暖通硬件的建筑级智能控制中枢
- **归类理由**: 虽原属 AI & Data 赛道，但聚焦公共建筑中照明控制传感器网络与通风系统的硬件数据互通、环境自动调节与硬件故障异常检测。

#### 挑战描述

你的建筑能有多智能？如何通过控制建筑内的照明来提升情绪和生产力？这种由大脑驱动的建筑能否自动优化室内环境、检测可能的缺陷和异常并进行补偿？如何利用机器学习和人工智能来实现这一点？借助数据的力量，你能对建筑的使用情况和状态得出哪些洞察？
许多公共建筑配备了各种控制系统来调节建筑环境，如通风、照明等。这些系统各自独立运行，不与系统外部交换信息，但它们正在收集可被更广泛利用的数据，并可作为全新数据驱动服务的基础。特别是照明控制系统正在收集建筑内人员移动的数据。通过应用合适的AI算法，你可以创建一个全新的建筑“大脑”，它能够整合来自不同来源的数据，超越照明控制的目的。

---

### 19. [2018] Alepa — 零食机器人黑客松

- **单题档案**: [2018_Alepa_Munchies_Robot_Hack.md](./2018_Alepa_Munchies_Robot_Hack.md)
- **原始赛道**: `Entertainment` | **所属子方向**: 机器人、重型装备与特种医疗硬件 (Robotics, Heavy Machinery & Specialized Medical Hardware)
- **核心主题**: 通过移动设备远程控制实体抓取与结算糖果机器人（Pick 'n' Pay Candy Robot）
- **归类理由**: 虽原属 Entertainment 赛道，但核心任务是编写移动端控制程序直接操控现场的实体抓取机器人硬件（Pick 'n' Pay Candy Robot），属于典型的机器人运动控制与人机交互挑战。

#### 挑战描述

你刚找到沙发上最舒服的位置，正沉浸在电子游戏中或只是忙自己的事，突然对甜食和美味零食的渴望猛烈袭来。然而，你懒得动弹。问题是：你的零食有多大的移动性？
我们正在寻找一种符合街头科学精神的娱乐性解决方案，来解决一个棘手的问题：如何用移动设备控制一个即选即付的糖果机器人。

---

### 20. [2018] Fleetboard — 卡车 X 代码

- **单题档案**: [2018_Fleetboard_Trucks_X_Code.md](./2018_Fleetboard_Trucks_X_Code.md)
- **原始赛道**: `Urban & Mobility` | **所属子方向**: 智能能源、电动出行与车载硬件 (Smart Energy, EV Charging & Mobility Hardware)
- **核心主题**: 基于梅赛德斯-奔驰重型卡车车载传感器与实时遥测数据（Live Vehicle Data）的车载应用开发
- **归类理由**: 虽原属 Urban & Mobility 赛道，但提供 Fleetboard 商用车车载硬件 SDK，直接读取重型卡车实时车辆总线与传感器遥测数据。

#### 挑战描述

你知道全球几乎所有道路的共同点是什么吗？卡车已经去过那里。现在，你的代码也可以到达那里！如今，开发者可以轻松获取实时卡车数据来构建应用程序。
只有你和我们的 SDK。你会选择勇敢面对命运，前往代码从未涉足的地方吗？那么，请创建一个利用我们 SDK 为 Mercedes-Benz Truck App Portal 提供的实时车辆数据的 Android 应用程序，帮助物流行业最大化其效率。

---

### 21. [2018] Rightware — 互联汽车用户体验挑战赛

- **单题档案**: [2018_Rightware_Connected_Car_UX.md](./2018_Rightware_Connected_Car_UX.md)
- **原始赛道**: `Sustainability` | **所属子方向**: 智能能源、电动出行与车载硬件 (Smart Energy, EV Charging & Mobility Hardware)
- **核心主题**: 智能网联汽车数字仪表盘、车载多屏座舱与车内外环境感知自适应交互
- **归类理由**: 虽原属 Sustainability 赛道，但由汽车数字座舱软件领军企业 Rightware（Kanzi）发起，聚焦车载数字仪表硬件显示与融合车内外传感器状态的座舱 HMI 设计。

#### 挑战描述

汽车正稳步变得更加互联，数字显示屏和用户界面开始取代模拟界面。用户体验将变得更加个性化，外部智能将被整合到车内环境中。借助合适的工具，汽车用户界面将变得情境感知，能够适应车内或车外的条件。这些趋势为汽车用户体验带来了激动人心的新可能性！
展望未来！您认为哪些服务应该被整合到明天的互联汽车中？这些服务应如何相互交互？它们应该实现什么功能，应如何实现，以及它们应该是什么样子？展现创新，让您的创造力闪耀！

---

### 22. [2018] Ensto — 自适应智能电加热

- **单题档案**: [2018_Ensto_Adaptive_Smart_Electric_Heating.md](./2018_Ensto_Adaptive_Smart_Electric_Heating.md)
- **原始赛道**: `Sustainability` | **所属子方向**: 智能能源、电动出行与车载硬件 (Smart Energy, EV Charging & Mobility Hardware)
- **核心主题**: 可编程智能电采暖硬件设备（Smart Electric Heating）的自适应温控与能耗优化
- **归类理由**: 虽原属 Sustainability 赛道，但围绕 Ensto 智能电加热器硬件与物联网温控后端展开，探索具有自学习能力的楼宇智能供暖硬件控制。

#### 挑战描述

可控的智能加热可以减少不必要的能源消耗。加热管理可以通过第三方数据和开放且可扩展的后端服务数据来实现。它可以学习和记忆。但最重要的是，它还能做些什么？

---

### 23. [2018] ABB — 船长会梦见电动船吗？

- **单题档案**: [2018_ABB_Do_Captains_Dream_Of_Electric_Ships.md](./2018_ABB_Do_Captains_Dream_Of_Electric_Ships.md)
- **原始赛道**: `Other` | **所属子方向**: 机器人、重型装备与特种医疗硬件 (Robotics, Heavy Machinery & Specialized Medical Hardware)
- **核心主题**: ABB 电动化、数字化与互联化未来船舶（Electric & Connected Ships）硬件与控制系统创新
- **归类理由**: 虽原属 Other 赛道，但由工业电气与自动化巨头 ABB 发起，聚焦电动船舶推进系统、船载物联网传感与智能航海硬件自动化。

#### 挑战描述

在ABB，我们有一个愿景：船舶应该实现电气化、数字化和互联化。通过为未来船舶打造创新方案，帮助我们在这愿景之上更进一步。

---

### 24. [2018] Nokia — 边缘生活

- **单题档案**: [2018_Nokia_Living_On_The_Edge.md](./2018_Nokia_Living_On_The_Edge.md)
- **原始赛道**: `Entertainment` | **所属子方向**: 嵌入式系统、边缘计算与通信硬件 (Embedded Systems, Edge Computing & Connectivity)
- **核心主题**: 基于 Nokia 5G 超低时延无线接入网与边缘计算（MEC）的实时硬件交互应用
- **归类理由**: 虽原属 Entertainment 赛道，但聚焦 5G 通信基础设施与超低时延边缘硬件能力验证。

#### 挑战描述

5G网络将以前所未有的水平实现高速、低延迟的移动连接。我们希望您创新应用，利用5G来展示和可视化5G网络与4G相比所带来的差异。零延迟游戏？即时下载？完美的4K视频流？或者将它们全部结合起来怎么样？跳出框框思考，召唤5G的未来。

---

### 25. [2018] Movesense By Suunto — 追踪一切运动之物

- **单题档案**: [2018_Movesense_By_Suunto_Track_Anything_That_Moves.md](./2018_Movesense_By_Suunto_Track_Anything_That_Moves.md)
- **原始赛道**: `Entertainment` | **所属子方向**: 可穿戴设备、运动与生物传感器 (Wearables, Motion & Biometric Sensors)
- **核心主题**: 基于 Movesense 惯性测量单元（IMU）传感器的运动器械、人体、生产线与桥梁监测
- **归类理由**: 虽在 2018 年被归入 Entertainment 赛道，但与 2017 年 Suunto 挑战同源，核心是利用 Movesense 可编程运动传感器硬件追踪运动员、运动器材、工业流水线设备或桥梁振动。

#### 挑战描述

世界上充满了运动的事物：运动员的身体或运动装备、生产线上的机器、交通中的桥梁、我们日常生活中的任何人，或者我们能想象到的任何其他事物。通常，了解这些事物如何以及何时运动——或者不运动——会非常有价值。你认为世界明显需要但仍缺乏的追踪解决方案是什么？构建你的演示，赢取精美的 Suunto 手表。

---

### 26. [2018] Vaisala — 真正有用的天气

- **单题档案**: [2018_Vaisala_Actually_Useful_Weather.md](./2018_Vaisala_Actually_Useful_Weather.md)
- **原始赛道**: `Sustainability` | **所属子方向**: 智能建筑、工业物联网与数字孪生 (Smart Buildings, Industrial IoT & Digital Twins)
- **核心主题**: Vaisala 高精度气象与环境测量仪器数据在航海、农业、航空与建筑场景的融合应用
- **归类理由**: 虽原属 Sustainability 赛道，但由全球顶尖气象与工业环境测量仪器制造商 Vaisala 发起，核心是将高精度气象与环境传感器数据应用于特定物理作业场景。

#### 挑战描述

市面上有大量通用的天气应用和服务——主要集中于天气预报。我们希望你们展示如何将天气数据以有意义且有用的方式用于某些特定的现实生活场景，并进行可视化。场景可以是任何内容，比如体育运动、不同的爱好（例如帆船、高尔夫、园艺、山地自行车、追风等），甚至是商业领域（农业、建筑、货运、航空等）。
我们对将天气和环境数据与现代技术相结合的新方式感兴趣，也关注这些方式如何应用于日常生活。

---

### 27. [2018] Vaisala — 改造桑拿

- **单题档案**: [2018_Vaisala_Hack_The_Sauna.md](./2018_Vaisala_Hack_The_Sauna.md)
- **原始赛道**: `Sustainability` | **所属子方向**: 智能建筑、工业物联网与数字孪生 (Smart Buildings, Industrial IoT & Digital Twins)
- **核心主题**: 极端高温高湿环境下的工业级桑拿传感测量仪器（替代传统机械温度计）与数字化体验
- **归类理由**: 虽原属 Sustainability 赛道，但聚焦极端高温高湿物理环境下（桑拿房）精密温湿度测量传感器硬件的应用与数字化改造。

#### 挑战描述

桑拿是传统的沐浴和放松场所。它也可能是一个对人和测量仪器都严苛的环境。几个世纪以来，桑拿体验并没有太大变化：例如，如今桑拿房内的条件仍然使用机械温度计来测量。我们觉得是时候让桑拿体验现代化了！

---

### 28. [2018] Cisco — Meraki - 捕捉生物

- **单题档案**: [2018_Cisco_Meraki_Capture_The_Creature.md](./2018_Cisco_Meraki_Capture_The_Creature.md)
- **原始赛道**: `Entertainment` | **所属子方向**: 空间定位、RFID 与智能终端硬件 (RFID, Indoor Positioning & Smart Terminals)
- **核心主题**: 基于 Cisco Meraki 蓝牙信标（BLE Beacon）与 Wi-Fi 无线定位硬件的室内空间感知
- **归类理由**: 虽原属 Entertainment 赛道，但底层技术完全基于 Cisco Meraki 无线网络硬件设备（BLE Beacons 与 Wi-Fi 室内定位基站）的实时物理位置追踪。

#### 挑战描述

如今，零售公司寻求新方法来提升客户忠诚度并增加实体店访问量。在本次挑战中，您将基于 Cisco Meraki 解决方案中的 BLE 信标或 Wi-Fi 定位技术，开发一款面向智能手机的室内位置感知生物捕捉游戏。该游戏旨在娱乐年轻访客，并引导其父母前往可能感兴趣的商店区域。

---

### 29. [2019] Ericsson — 5G 绿色城市交通

- **单题档案**: [2019_Ericsson_Greener_City_Transport_With_5G.md](./2019_Ericsson_Greener_City_Transport_With_5G.md)
- **原始赛道**: `Urban & Mobility` | **所属子方向**: 嵌入式系统、边缘计算与通信硬件 (Embedded Systems, Edge Computing & Connectivity)
- **核心主题**: 基于 5G 低时延通信网络的车队集中式实时控制与多源传感器协同调度
- **归类理由**: 虽原属 Urban & Mobility 赛道，但聚焦 5G 超低时延无线通信技术在智能车队控制与车路协同硬件调度中的应用。

#### 挑战描述

当前趋势显示全球人口正不断向城市地区迁移。随着城市规模扩大和密度增加，人员和货物的运输变得越来越复杂。在如此庞大的运输量下，如果我们继续沿用相同的城市交通方法，空气污染和组织管理将成为严峻问题。

5G 技术的引入将通过集中化交通决策（而不会因延迟受到太大影响）并聚合来自多个来源的信息，从而支持不同的运输模式。作为团队，你们需要找到优化不同参与者之间城市范围交通挑战的方法。

目标是尽可能多地将客户运送至目的地。在黑客松结束时，我们将把所有参与者置于同一模拟环境中，你们将争夺客户。得分更高者获胜。我们可能会进行多轮比赛。

这个挑战是展示你使用任何你喜欢的现代软件技术开发能力的绝佳平台！

#### 可用资源

Ericsson 将提供：一台带有简单 API 的服务器，你可以通过它控制你的车队并查看世界状态。此外，我们还将提供出色的导师。

---

### 30. [2019] Valmet — 未来的服务车间

- **单题档案**: [2019_Valmet_Service_Workshop_Of_The_Future.md](./2019_Valmet_Service_Workshop_Of_The_Future.md)
- **原始赛道**: `AI & Data` | **所属子方向**: 机器人、重型装备与特种医疗硬件 (Robotics, Heavy Machinery & Specialized Medical Hardware)
- **核心主题**: 造纸机巨型辊筒微米级磨削传感器测量数据、Node-RED 硬件仿真与 XR 头显交互
- **归类理由**: 虽原属 AI & Data 赛道，但针对大型造纸机械辊筒的微米级圆度测量传感器硬件（Sensor ware）、Node-RED 物联网数据流与 VR/MR 硬件头显进行开发。

#### 挑战描述

我们都记得那些木工课，当时我们汗流浃背，用太小的砂纸打磨着即将成型的勺子。现在，想象一台机器，它有相当于勺子表面100万倍的面积需要以微米级精度打磨。听起来不诱人吗？纸张、纸板和纸浆干燥机每年需要为其辊子进行数百小时的这种平滑打磨服务。一个不光滑的辊子将以每分钟50欧元的损失速度造成损失。

这个挑战非常适合对传感器硬件、可视化工具和机器学习领域最新发展感兴趣的黑客，更不用说这些是真实且非常庞大的机器。你的任务是找到方法使打磨这些辊子更有效，并在某种程度上更诱人。那么，你如何可视化那些肉眼看不见的微小事物呢？

#### 可用资源

Valmet将提供：参与者有机会在ValmetXR平台上进行开发。ValmetXR平台通过用沉浸式学习环境替代典型手册，为文档和培训构建定制用户界面提供了高效工具。ValmetXR通过智能手机、平板电脑和VR/MR头显在虚拟平台中整合了虚拟现实、混合现实和交互式增强现实体验。平台基于Unity引擎。所有3D模型、360/2D视频、文档和链接都可以配置并嵌入平台。使用Node-RED可以将模拟接入ValmetXR。

此外，Aalto和Valmet为辊子打磨、辊子行为和服务业务提供指导。还提供了演示辊子几何形状和运行中的造纸机的示例数据集。

Valmet将提供：
3D模型和XR平台
来自真实造纸机的纸幅数据集
来自造纸机辊子圆度测量的数据集

---

### 31. [2019] Helvar & VTT — 用雷达技术点亮空间

- **单题档案**: [2019_Helvar_VTT_Making_Spaces_Brighter_With_Radar.md](./2019_Helvar_VTT_Making_Spaces_Brighter_With_Radar.md)
- **原始赛道**: `AI & Data` | **所属子方向**: 毫米波雷达与高速机器视觉传感器 (Millimeter-Wave Radar & High-Speed Machine Vision Sensors)
- **核心主题**: 60 GHz 2D 毫米波成像雷达与 24 GHz 生命体征雷达传感器 + 智能灯具硬件实时联调
- **归类理由**: 虽原属 AI & Data 赛道，但现场提供 60 GHz 2D 毫米波雷达、24 GHz 毫米波雷达（可非接触提取呼吸心率等生命体征与微动）以及实体智能灯具硬件供团队实时接入演示。

#### 挑战描述

识别房间内人员存在的能力已存在很长时间，并用于自动可靠地控制灯光。但技术演进要求创新，我们的目标是创建更智能的室内空间。通过将机器学习和人工智能算法应用于雷达传感器数据，您可以开发出能够提供最先进照明的未来应用。这是创建真正智能室内系统的下一步。

想象一下整个建筑变得活跃并对居住者的行为做出反应的可能性。通过利用雷达等先进传感器，我们能否计算房间内有多少人并识别他们的位置？是否有可能识别人员是静止还是移动？如果是，他们的移动方向是什么？

同样，我们能否检测在办公桌前工作的人的行为变化，并提供个性化照明以提升他们的情绪和生产力？

此外，这不仅仅局限于人员存在。例如，是否有可能在车库中定位空停车位？我们能否识别移动车辆的方向？此类洞察具有多种应用，从购物中心的人流到建筑利用率测量以及用于照明控制的高级室内占用传感。

#### 可用资源

Helvar & VTT 将提供：演示工具、设备和数据集：我们将提供一个网页，包含环境布局上的灯具位置。参与者可以通过 API 发送命令来模拟灯光的行为。还将提供演示灯具以及雷达传感器。

车库：参与者将获得一个来自室内车库的数据集，使用 RGB 相机和 60 GHz 2D 雷达收集。数据集时间同步。从 RGB 帧中检测到的人和车辆由边界框表示，提供在图像坐标系中。雷达数据包括在平面图坐标系中显示目标的 2D 幅度图。

会议室：参与者将获得一个来自会议室的数据集，包含 60 GHz 2D 雷达成像数据和相应的 RGB 相机帧。从 RGB 帧中检测到人员及其骨架，并提供其边界框和关节坐标在图像坐标系中。雷达数据包括在平面图坐标系中显示目标的 2D 幅度图。参与者可以获得雷达的实时访问权限，用于创建在线演示。

工作场所：参与者将获得一个人使用电脑工作的数据集。数据集包括原始 24 GHz 雷达数据和相应的 RGB 相机帧。从雷达数据中提取生命体征，并从 RGB 帧中检测和提供人员的关节位置。原始雷达数据包括幅度图和相位图，可用于检测大规模和小规模运动。参与者可以获得传感器数据的实时访问权限，也可用于创建在线演示。

---

### 32. [2019] SUSE — 开放开放城市

- **单题档案**: [2019_SUSE_Open_Open_City.md](./2019_SUSE_Open_Open_City.md)
- **原始赛道**: `Urban & Mobility` | **所属子方向**: 嵌入式系统、边缘计算与通信硬件 (Embedded Systems, Edge Computing & Connectivity)
- **核心主题**: 基于 Raspberry Pi 3B+/4B+ 硬件集群（uMEC 边缘节点）与专用 Wi-Fi 网络的边缘计算平台
- **归类理由**: 虽原属 Urban & Mobility 赛道，但现场搭建了由树莓派 Raspberry Pi 3B+ 与 4B+ 开发板组成的 uMEC 边缘计算物理集群与专用 Wi-Fi 网络，运行 k3s 与 ETSI MEC 边缘硬件接口。

#### 挑战描述

未来的城市将通过创新的开放平台整合技术和基础设施，从而提高市民的生活质量。

边缘计算在全球电信行业中扮演着越来越重要的角色。边缘发展的重点领域之一是“智慧城市”。SUSE 正在参与 Akraino / uMEC 项目，该项目旨在为网络边缘设备定义并交付一个计算平台。挑战者需要展示用例，并创建一个开放数据平台的原型，该平台能够收集、分析并与市民共享天气、交通和紧急信息。

挑战的参与者将获得一个专用 WiFi 网络以及一个运行在我们 uMEC 节点（Raspberry Pi 3B+ 和 4B+ 板）上的 k3s 集群的访问权限。这个基础平台还将包括一组 MEC API，这些 API 应被用于解决挑战。参与者将在这些 API 之上开发应用程序，并将其部署到我们的集群中。更复杂的应用程序可以使用 SUSE CAP 进行实现和部署。在后一种情况下，我们希望看到强大的云原生应用部署与我们的 uMEC 网络之间的智能集成。

#### 可用资源

SUSE 将提供：我们将提供一个边缘计算节点集群，包括硬件和软件。该集群将作为挑战参与者构建的容器化应用程序的部署平台。我们将提供某些 ETSI MEC API 子集的开放实现。

更复杂的解决方案可以利用 SUSE CAP，它能够轻松实现云原生应用程序开发。这些解决方案必须与 uMEC 边缘网络上的设备和 API 进行交互。

---

### 33. [2022] Oras — 最智能的用水体验

- **单题档案**: [2022_Oras_The_Smartest_Water_Experience.md](./2022_Oras_The_Smartest_Water_Experience.md)
- **原始赛道**: `Sustainability` | **所属子方向**: 智能建筑、工业物联网与数字孪生 (Smart Buildings, Industrial IoT & Digital Twins)
- **核心主题**: Oras Hydractiva 数字花洒与免接触蓝牙智能水龙头（SMART Faucets）用水传感与漏水定位
- **归类理由**: 虽原属 Sustainability 赛道，但现场展示了 Oras 数字手持花洒与免接触蓝牙智能水龙头硬件，并提供整栋公寓楼 20 户家庭的智能水表/龙头传感器真实数据。

#### 挑战描述

我们每天都在为各种目的使用水。然而，我们可能不知道水在哪些方面使用最多，更重要的是，应该如何用水：人们应该知道他们在淋浴时用了多少水，或者多少是合理的用水量
建筑业主可以预测热水需求并优化加热过程
在洗手时，长时间的皂液搓洗（长达20秒）对于去除所有微生物至关重要
在大型建筑中，水管工快速识别漏水龙头的位置非常重要
哪些数据和洞察可以被可视化，以及应该如何展示？我们如何让每个用户更加意识到他们的用水情况，并鼓励他们做得更好？信息可以转化为目标，甚至通过游戏化实现良性竞争，从而为用户和环境带来好处。

#### 可用资源

活动期间，我们将为参赛者提供来自一栋包含20套公寓的建筑物的专有用水数据，格式为JSON。我们的专家将在整个活动期间提供支持和指导。此外，我们产品系列的最新发展，如数字手持花洒和免接触蓝牙水龙头，将在我们的展位以及线上展示：Oras Hydractiva Digital - 在淋浴中节约水和能源，以及SMART水龙头 (oras.com)

---

### 34. [2022] CGI & KONE & Meyer Turku — 与机器人共游

- **单题档案**: [2022_CGI_KONE_Meyer_Turku_Cruising_With_Robots.md](./2022_CGI_KONE_Meyer_Turku_Cruising_With_Robots.md)
- **原始赛道**: `Other` | **所属子方向**: 机器人、重型装备与特种医疗硬件 (Robotics, Heavy Machinery & Specialized Medical Hardware)
- **核心主题**: 大型豪华邮轮上的自主服务机器人（Service Robots）与自动化客流/物流硬件系统设计
- **归类理由**: 虽原属 Other 赛道，但由造船巨头 Meyer Turku、电梯与客流巨头 KONE 及 CGI 联合发起，核心是设计邮轮场景下的实体服务机器人与自动化物流硬件工作流。

#### 挑战描述

人流是指人们从地点A到地点B以及在两地之间移动的方式。良好的人流意味着人们移动顺畅、安全、舒适且无需等待。在游轮上，可以从乘客和船员的角度来发现人流。

思考一下对游轮乘客可见和不可见的服务。总之，我们希望有一个服务路径和人流的可视化展示（模型、动画等）。你可以发挥想象力，不仅使用机器人，还可以使用自动化系统。

我们鼓励你在结论中发挥创意。记得通过模型在解决方案中努力设计用户界面。

#### 可用资源

- 来自Meyer的关于游轮的有用信息（可下载的pdf）
- 来自KONE的人流和机器人专家
- 在Junction Hackathon上的指导

---

### 35. [2022] Nexi — 破解支付

- **单题档案**: [2022_Nexi_Crack_The_Payments.md](./2022_Nexi_Crack_The_Payments.md)
- **原始赛道**: `Finance` | **所属子方向**: 空间定位、RFID 与智能终端硬件 (RFID, Indoor Positioning & Smart Terminals)
- **核心主题**: 基于外置 NFC 读卡器硬件与移动 NFC 模块的金融 IC 卡底层通信协议解析
- **归类理由**: 虽原属 Finance 赛道，但官方现场提供实体 NFC 读卡器硬件（NFC Readers），要求直接读取并解析芯片卡与 POS 终端硬件之间的无线射频通信报文。

#### 挑战描述

在幕后，存在不同的通信协议、加密标准、金融行业要求、国家法规等。然而，支付系统的最终用户只看到并持有冰山一角：卡片。
卡片通过刷卡、挥卡和插卡进行操作。这些支付方式是否同样安全？你使用的卡片类型（Maestro、Visa、MasterCard）是否重要？深入研究卡片与终端之间的通信，调查支付真正的安全性！
构建使用NFC协议读取卡片数据的解决方案。理想情况下，它应显示解析的内容并识别你卡片的安全级别。解决方案应易于使用，并详细解释所发现的内容！

#### 可用资源

我们将提供NFC读取器，但你也可以使用手机进行读取。

#### 奖项设置

获胜团队将获得1500€奖金

---

### 36. [2024] Pixieray — 窥探双眼背后

- **单题档案**: [2024_Pixieray_Peek_Behind_The_Eyes.md](./2024_Pixieray_Peek_Behind_The_Eyes.md)
- **原始赛道**: `Entertainment` | **所属子方向**: 可穿戴设备、运动与生物传感器 (Wearables, Motion & Biometric Sensors)
- **核心主题**: 集成单眼 6 颗红外眼动传感器、加速度计与环境光/紫外线传感器的智能眼镜硬件数据分析
- **归类理由**: 虽原属 Entertainment 赛道，但核心数据源来自 Pixieray 智能眼镜硬件（每只眼睛配备 6 个红外传感器追踪眼动、三轴加速度计追踪头部姿态、环境光与 UV 传感器）。

#### 挑战描述

你能通过观察眼睛判断一个人是在阅读、驾驶还是疲劳吗？你的眼睛能揭示你是否感到压力吗？你能识别某人是否在说谎吗？当我们阅读、驾驶或看电影时，我们的眼睛是活跃的。Pixieray 使用带有隐形技术的优质眼镜，可以追踪眼球运动、头部运动和光照条件。

你的任务是深入挖掘数据，发现关于人类行为及其与眼球运动相关性的有趣见解。分析数据，找出眼睛能告诉你什么。

我们挑战你利用这个新颖的数据源，创造有意义、美观且有影响力的想法，对日常生活产生实际影响。

#### 可用资源

我们提供来自专用眼镜的数据，该眼镜可追踪眼球运动，并结合捕捉用户佩戴这些眼镜时行为的视频数据。你的任务是分析、解释并从这一丰富的数据集中得出有意义的见解。数据集以 JSON 格式提供，确保易于解析并与大多数数据分析工具和平台集成。- 每只眼睛上 6 个 IR 传感器的眼球运动数据，- 加速度计数据，- 环境光和紫外线水平 / 要参与此挑战并获取数据，请访问我们的展位（必须签署保密协议）

#### 奖项设置

获胜团队将获得 500 欧元，亚军将获得 300 欧元，第三名将获得 100 欧元。

奖品以亚马逊礼品卡形式发放。

---

### 37. [2024] Huawei — 感知运动

- **单题档案**: [2024_Huawei_Sense_The_Motion.md](./2024_Huawei_Sense_The_Motion.md)
- **原始赛道**: `AI & Data` | **所属子方向**: 可穿戴设备、运动与生物传感器 (Wearables, Motion & Biometric Sensors)
- **核心主题**: 基于意法半导体 STMicroelectronics SensorTile 开发套件与智能手表的实时运动/情绪传感算法
- **归类理由**: 虽原属 AI & Data 赛道，但官方现场提供 STMicroelectronics SensorTile 嵌入式传感器开发套件（STM Sensor Tile Dev Kits）及智能穿戴设备，要求实现可在穿戴端实时运行的运动与情绪感知模型。

#### 挑战描述

为移动和可穿戴设备创建创新且引人入胜的功能，以吸引年轻人，鼓励他们减少久坐行为，拥抱更积极运动的生活方式。此外，对于患有心理健康问题的人群，情绪识别有助于提高自我意识，心理健康专业人士可以将该技术整合到治疗计划中，以监测患者的情绪反应和健康状况。

#### 可用资源

在活动期间，参赛团队将创建针对可穿戴或移动设备的新颖运动和健康功能。功能、算法或模型可以使用现有数据集或实时传感器数据创建。传感器数据可以从以下来源获取（但不限于）：

- Android传感器框架
- iOS Core Motion
- STMicroelectronics传感器开发套件
- 免费在线数据集，例如来自Kaggle

我们将向参与者提供一些STM传感器开发套件用于开发，否则团队应使用自己的笔记本电脑、手机或智能手表。

#### 奖项设置

第一名：8000€ / 第二名：5000€ / 第三名：3000€

---

### 38. [2025] KONE x Granlund — 现代化万亿欧元库存

- **单题档案**: [2025_KONE_Granlund_Modernizing_Trillion_Euro_Inventory.md](./2025_KONE_Granlund_Modernizing_Trillion_Euro_Inventory.md)
- **原始赛道**: `AI & Data` | **所属子方向**: 智能建筑、工业物联网与数字孪生 (Smart Buildings, Industrial IoT & Digital Twins)
- **核心主题**: 建筑机电暖通给排水（MEP）物理设备资产的自动化巡检采集与终极数字孪生构建
- **归类理由**: 虽原属 AI & Data 赛道，但聚焦物理建筑中机械、电气与管道（MEP）硬件设备铭牌、状态与位置的自动化盘点与数字孪生。

#### 挑战描述

用AI赋能建筑世界，打造终极数字孪生

建筑是全球最大的资产类别，总价值约350万亿欧元。尽管价值巨大，但建筑内所有设备的数量、状况和位置并不总是已知的。然而，最新的设备信息是维护服务和维修规划的重要起点。目前收集这些信息非常费力，需要进行设备库存调查，由专家在现场手动收集设备数据。通过本次挑战，我们正在寻找能够自动化设备库存调查的解决方案。您能否开发一种解决方案，用于从建筑中的机械、电气和管道设备收集数据，该方案对非专家用户友好，且不依赖专用硬件？

---

### 39. [2025] Denso — ChargeID：可信电动汽车服务

- **单题档案**: [2025_Denso_ChargeID_Trusted_EV_Services.md](./2025_Denso_ChargeID_Trusted_EV_Services.md)
- **原始赛道**: `Urban & Mobility` | **所属子方向**: 智能能源、电动出行与车载硬件 (Smart Energy, EV Charging & Mobility Hardware)
- **核心主题**: 汽车一级供应商 DENSO 车端硬件、智能充电桩与去中心化身份（DID）安全互联
- **归类理由**: 虽原属 Urban & Mobility 赛道，但由全球顶级汽车零部件硬件巨头电装（DENSO）发起，围绕智能网联汽车硬件、充电桩终端与车桩可信通信展开。

#### 挑战描述

利用AI和去中心化身份重新构想半公共电动汽车充电，让驾驶员、车辆和充电点与企业无缝互动。

工作场所、车队和半公共设施中的电动汽车充电正在快速增长，但大多数基础设施仍然“笨拙”。企业无法轻松创建差异化服务，而驾驶员期望透明度和控制权。通过AI和跨驾驶员、车辆和充电点的去中心化身份，充电旅程和体验可以演变为安全、个性化且高效的服务，惠及从驾驶员到充电点运营商再到拥有车辆和充电器的企业等所有人。

如今，车队运营商、雇主或零售连锁店等企业在充电方面的创新方式有限，因为基础设施基础且数据流受限并受各方控制。驾驶员、车辆和充电点都需要可信的方式来认证、共享和与服务交互，而不依赖中心化中介。AI和去中心化身份如何使企业能够提供需求预测、成本优化或个性化充电体验等服务，同时保持所有权贴近用户和相关资产？

#### 可用资源

来自DID项目研发和创新团队的导师。

在活动期间，参与者将开发创新的半公共B2B2C电动汽车充电解决方案，结合AI和去中心化身份。挑战围绕Denso DID Agent展开，这是一个领先的身份即服务平台，为车辆及相关资产提供安全且隐私保护的连接。该技术允许在移动即服务（MaaS）场景中，驾驶员、车辆和充电点之间进行可信的匿名交互。

参与者将可以使用Denso DID Agent、其API文档以及代表车辆和充电站的样本数据集。这些资源为探索使用去中心化身份原则的认证、数据交换和服务创建提供了基础。

来自我们产品开发和研发团队的专家导师，积极参与汽车行业的DID倡议，将在整个活动期间为团队提供支持。

#### 奖项设置

我们将奖励前三名团队总计1000欧元的现金奖励，以表彰最具创意和影响力的解决方案。除奖金外，获奖者还将在行业专家中获得曝光，并获得与我们的产品和研发团队（致力于移动服务中去中心化身份）的指导机会。

---

### 40. [2025] Sensofusion — 灯光，摄像，反应！

- **单题档案**: [2025_Sensofusion_Lights_Camera_Reaction.md](./2025_Sensofusion_Lights_Camera_Reaction.md)
- **原始赛道**: `AI & Data` | **所属子方向**: 毫米波雷达与高速机器视觉传感器 (Millimeter-Wave Radar & High-Speed Machine Vision Sensors)
- **核心主题**: 微秒级神经拟态事件相机（Event Camera）高速物理运动检测与无人机追踪
- **归类理由**: 虽原属 AI & Data 赛道，但由反无人机硬件厂商 Sensofusion 在现场部署多台配不同镜头的专业级事件相机（Event Cameras，微秒级像素光强变化传感器），测算高速旋转风扇叶片与追踪无人机，优胜团队每人奖励一台 DJI Mini 3 无人机硬件。

#### 挑战描述

在普通视觉失效的时间尺度上操作——微秒级的机器视觉。

有一种你可能从未听说过的相机类型——事件相机。它们使用一种成像传感器，在像素级别检测光强度的变化，产生异步事件流而非完整帧。其关键优势包括极高的动态范围、低延迟（微秒级）、极小的运动模糊和高时间分辨率。你能想出如何使用这种相机来检测移动极快的物体吗？证明它。

你将获得现场亲身体验配备各种镜头的专业事件相机的机会——所有这些都在Junction现场提供。
你的任务：构建实时AI或ML模型，能够从这些微秒级视觉流中检测和解释运动。
从简单开始：你能计算风扇每秒旋转多少次吗？然后进一步推进——跟踪无人机、估计速度、预测运动，任何你能想象到的。
将这些传感器推向极限——记住，它们的极限非常高。

#### 可用资源

可使用安装在Junction现场的几台专业事件相机。
用于数据访问和集成的API和文档。

来自Sensofusion研发团队的导师，在视觉技术和AI方面拥有深厚专业知识。

示例脚本和数据样本，帮助团队快速上手。

#### 奖项设置

由Sensofusion导师选出的获胜团队将获得DJI Mini 3无人机奖励。获胜团队的每位成员都将获得一架无人机。

---

### 41. [2025] Sensofusion — 无线电城市

- **单题档案**: [2025_Sensofusion_Radio_City.md](./2025_Sensofusion_Radio_City.md)
- **原始赛道**: `Entertainment` | **所属子方向**: 毫米波雷达与高速机器视觉传感器 (Millimeter-Wave Radar & High-Speed Machine Vision Sensors)
- **核心主题**: 三维城市环境中移动电台、车载与无人机射频无线电波（Radio Waves）物理传播与多径反射仿真
- **归类理由**: 虽原属 Entertainment 赛道，但由反无人机射频侦测硬件厂商 Sensofusion 发起，聚焦无线电波在真实物理城市建筑间的传播损耗、反射与遮挡物理建模。

#### 挑战描述

无线电波：它们环绕着我们，穿透着我们；它们将星系紧密相连。向我们展示它们吧。

无线电悄然驱动着我们日常生活的方方面面。本次挑战提供了一种平易近人的方式来掌握基础知识。利用一个3D城市模型，让无形的无线电世界变得可见。展示无线电发射器何时何地能被听到——以及何时会消失。

使用提供的香港3D模型，演示无线电波如何传播。在地图上放置假想的移动无线电源：例如，街上行走的手机用户、街道上行驶的汽车或空中飞行的无人机——或者想出其他来源。然后可视化这些源发出的无线电传输如何传播。您将演示无线电波如何从墙壁反射，以及地理障碍如何阻挡无线电。我们将寻找基于物理的模拟与富有创意的视觉效果。您需要理解无线电的行为方式。理想情况下，您的可视化也能帮助他人学习。如果能为故事增色，请随意添加交互性和引入其他数据。可视化无线电波有多种不同方式。本次挑战没有唯一正确答案；有多种创意方式展示您的结果。

#### 可用资源

城市3D模型：香港（高楼大厦，有趣的地理环境）
单位：米
许可证：
JAXA https://earth.jaxa.jp/en/data/policy/
OpenStreetMap贡献者 https://www.openstreetmap.org/copyright

额外细节：
一个将GPS坐标映射到模型空间的python3函数：

def lat_lon_to_model_space(lat_lon):
    import math
    hong_kong_center_lat_lon = (22.268385798683745, 114.2578125)
    EARTH_RADIUS_METERS = 6371000
    delta_lat_deg = float(lat_lon[0]) - float(hong_kong_center_lat_lon[0])
    delta_lon_deg = float(lat_lon[1]) - float(hong_kong_center_lat_lon[1])

    meters_north = math.radians(delta_lat_deg) * EARTH_RADIUS_METERS

    cos_latitude = math.cos(math.radians(hong_kong_center_lat_lon[0]))
    radius_at_latitude = EARTH_RADIUS_METERS * cos_latitude
    meters_east = math.radians(delta_lon_deg) * radius_at_latitude

    # 翻转符号以匹配您的坐标系
    return [meters_north, -meters_east]

区域边界WGS84：{'north_lat': 22.59372606392931, 'south_lat': 21.943045533438177, 'west_lon': 113.90625, 'east_lon': 114.609375}

#### 奖项设置

由Sensofusion导师选出的获胜团队将获得DJI Mini 3无人机作为奖励。获胜团队的每位成员都将获得一架无人机。

---

### 42. [2025] Valmet x HSY — 智能流量优化

- **单题档案**: [2025_Valmet_HSY_Intelligent_Flow_Optimization.md](./2025_Valmet_HSY_Intelligent_Flow_Optimization.md)
- **原始赛道**: `Sustainability` | **所属子方向**: 机器人、重型装备与特种医疗硬件 (Robotics, Heavy Machinery & Specialized Medical Hardware)
- **核心主题**: 基于工业自动化协议 OPC UA 与数字孪生的城市污水泵站硬件集群自主协同控制
- **归类理由**: 虽原属 Sustainability 赛道，但要求通过工业自动化标准硬件通信协议 OPC UA 直接与污水泵站控制系统及数字孪生仿真环境交互，实现物理水泵集群的实时安全控制。

#### 挑战描述

构建一个多智能体AI，通过实时预测流入量、电价和流量动态，自主最小化废水泵送能耗——这是现代基础设施中最关键的流程之一。

每个城市都依赖看不见的系统维持运转——废水管理是其中最关键的一环。泵机不间断运行，消耗大量能源，同时面临流入量、暴雨和电价波动的混乱局面。如果这些网络能够自主思考呢？借助多智能体AI，Valmet和HSY邀请您将静态基础设施转变为能够实时预测、适应和优化废水流的活系统。

废水网络全天候运行且不能停止——但它们隐藏着智能优化的未开发潜力。每个泵站必须在恒定流量、有限存储和波动的电价之间取得平衡，同时保持对暴雨洪水的韧性。传统自动化遵循固定规则，忽略实时变化和预测。您的任务是构建一个多智能体AI系统，其中自主智能体根据每日电价规划泵送、协调泵站间的流量，并在不违反安全或工艺约束的前提下找到最节能的泵送策略。目标：让社会最关键的基础设施系统之一实现自我优化。

#### 可用资源

参与者将获得HSY的历史废水和流入数据集——涵盖多年环境变化的真实运营数据。系统通信和控制将通过OPC UA协议实现，这是安全实时数据交换的工业标准。来自Valmet、HSY和阿尔托大学的导师将在过程自动化、多智能体架构等领域提供实践指导，未来解决方案可通过数字孪生仿真进行测试。团队可自由使用任何AI框架——从强化学习环境到优化库或自定义智能体系统。

#### 奖项设置

第一名 2000€，第二名 1500€，第三名 500€

---

### 43. [2025] Snap Inc. — 你的真实世界AI伴侣

- **单题档案**: [2025_Snap_Your_Real_World_AI_Companion.md](./2025_Snap_Your_Real_World_AI_Companion.md)
- **原始赛道**: `AI & Data` | **所属子方向**: 可穿戴设备、运动与生物传感器 (Wearables, Motion & Biometric Sensors)
- **核心主题**: 基于第五代 Snap Spectacles AR 智能眼镜硬件的空间感知与全天候个人 AI 伴侣
- **归类理由**: 虽原属 AI & Data 赛道，但现场为每支参赛队伍配发一副第五代 Snap Spectacles AR 眼镜真机硬件（优胜团队每人赢得一副 Spectacles），要求利用眼镜端摄像头与空间传感器开发实时 AR/AI 应用。

#### 挑战描述

为Spectacles设计一款AIxAR体验，将AR眼镜转变为能够感知你的世界、情境和需求的智能伴侣。

像Spectacles这样的AR眼镜代表着个人技术的下一个前沿。它们能看见你所见、听见你所听，并理解你周围的世界——开启人类与AI实时协作的新方式。在欧洲最大的AI黑客松上，我们邀请你设计并构建一款Spectacles Lens，提供AI优先的体验，将Spectacles转变为针对特定真实场景的智能伴侣。超越简单的命令，创建一个与用户环境和意图深度集成的助手。卓越的项目将超越仅仅回答用户的直接问题。我们挑战你构建一个能够预测用户需求、提供空间支持，并帮助用户更投入、更专注于当前环境的AI。

为Spectacles构建一款Lens，展示引人入胜的AI优先体验。你的项目应展示真实世界的AI伴侣如何提供真正的价值并提升用户的生活。我们鼓励你思考日常生活中那些能够看见的眼镜和能够理解你的模式、习惯和互动的AI可以简化事情的时刻。

#### 可用资源

Snap工程团队成员，在Spectacles开发者体验和设计方面拥有专业知识。

参与者将使用Snap的Lens Studio工具和第五代Spectacles进行构建。Lens Studio免费且可在线下载，提供全套功能，用于创建由计算机视觉、场景理解和ML集成驱动的沉浸式实时AR体验。在整个黑客松期间，Snap导师将提供Lens Studio工作流程和设计直观、以人为本的AR体验最佳实践的实践指导。我们将提供文档、示例项目和实时指导支持，帮助你将AI伴侣变为现实。

我们带来的技术列表：
- Spectacles（每队1副）

我们将带来来自Snap Lab团队的导师，他们具有工程和设计背景，直接参与Spectacles的开发。

#### 奖项设置

奖项：
🥇 第一名：每位团队成员赢得一副Spectacles
🥈 第二名：每位团队成员赢得一个Soundview Speaker
🥉 第三名：每位团队成员赢得一个Elexa Power Bank

---

## 四、已核验历届硬核硬件获奖总表与跨赛道补全索引 (2017–2025)

除在上述对应单题 Silver 文件末尾追加的获奖实证外，Bronze 阶段专项调查（[2017–2018 总账](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2017_2018_Hardware_Investigation_Log.md)、[2019–2020 总账](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2019_2020_Hardware_Investigation_Log.md)、[2021–2023 总账](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2021_2023_Hardware_Investigation_Log.md)）还抢救出了原 `challenges_full.json` 漏录或位于跨赛道中的已验证硬件/边缘计算/CV 冠军：

| 年份 | 合作伙伴 / 赛道 | 项目与团队 | 已证实奖项 | 核心硬件 / 边缘技术栈 | Bronze 与 Gold 索引 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2017** | **STARA / 全场总赛** | **Signvision** (Team Glados: Andreas Urbanski, Teemu Taskula, Ville Toiviainen) | **全场总冠军 🏆 (€20k)** + STARA 第2名 | 手机摄像头+GPS -> `uWs`/`Koa` -> OpenCV HSV + TF 1.4.0 `32x32` CNN (GTSRB) -> AWS ECS | [`2017_Stara_Signvision_Glados.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2017_Stara_Signvision_Glados.md) |
| **2018** | **Intel (`Bluetooth Mesh`)** | **Help.io / Team Health.io** (拉脱维亚大学) | **Intel 1st** + **IoT 总冠军** + **全场亚军** | Suunto Movesense BLE -> iOS 12 分诊 -> Intel NUC BlueZ `meshd-ingas` + `nRF51_dongle` -> 4x PHYTEC `reel_board`s (Zephyr) | [`2018_Intel_HelpIO_HealthIO_BluetoothMesh.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2018_Intel_HelpIO_HealthIO_BluetoothMesh.md) / [Gold](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/gold/zh/hardware.md) |
| **2018** | **Future Cities 赛道** | **GuideMe** (Makers UPV) | **Future Cities 第1 (€1k)** + **全场第4** | Wemos `ESP8266` (`115200` UART) + `BBC micro:bit` (磁力计、5x5 LED、震动) + 3D打印 `.STL` 手杖手柄 + PHP/GMaps | [`2018_FutureCities_GuideMe_MakersUPV.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2018_FutureCities_GuideMe_MakersUPV.md) / [Gold](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/gold/zh/hardware.md) |
| **2019** | **QOCO (`Smooth Travels`)** | **Luggage Love** (`ryojimatsuzaki` 原型) | **QOCO 第1** (19队中) | 无源 **NFC 芯片**  luggage 标签与手机快速配对 *(修正原 JSON 错标 2020)* | [`2019_QOCO_SmoothTravels_NFC_Baggage.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2019_QOCO_SmoothTravels_NFC_Baggage.md) |
| **2020** | **OP / 全场总赛** | **Saavi – Healthy Finance** (Alexander Zimin 等) | **全场总冠军 🏆** | 原生 Apple `ARKit` 识别实体银行卡 (`ist_card.arreferenceimage`) + 角速度甩卡切换手势 + `scikit-learn` | [`2020_OverallWinner_Saavi_HealthyFinance_ARKit.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2020_OverallWinner_Saavi_HealthyFinance_ARKit.md) |
| **2021** | **CGI x KONE (`Sky(scraper)`)** | **ElevAI** (Team Glados) & **S.H.I.E.L.D** | **Model奖 + Top-10** / **Out-of-the-Box奖** | Ray Tune + `XGBoost` F2 (`0.9722`) + SHAP + AR 预检 / 嵌入式照明智能安全帽 + AR 摄像头 + STT + 手势 | [`2021_CGI_KONE_SkyScraper_ElevAI_SHIELD.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2021_CGI_KONE_SkyScraper_ElevAI_SHIELD.md) |
| **2023** | **Huawei (`Sense the Motion`)** | **J-mp** (Mankeli Solutions) *(+ 对照 `Motion Potion`, `Vital`)* | **Huawei 第2名** | Flutter `sensors_plus` (`x+y+z > 30.0`)、`Vibration.vibrate`、`flutter_compass`、`geolocator`、QR、Firebase、Next.js | [`2023_Huawei_SenseTheMotion_Jmp_MotionPotion_Vital.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2023_Huawei_SenseTheMotion_Jmp_MotionPotion_Vital.md) / [Gold](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/gold/zh/hardware.md) |

---
