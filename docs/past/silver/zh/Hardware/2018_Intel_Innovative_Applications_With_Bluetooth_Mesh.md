# [2018] Intel — 基于蓝牙Mesh的创新应用

## 元数据

- **年份**: 2018
- **挑战合作方**: Intel
- **原始历史赛道**: IoT & Hardware
- **2026 对应赛道**: Hardware Track (by Arduino)
- **技术细分方向**: 嵌入式系统、边缘计算与通信硬件 (Embedded Systems, Edge Computing & Connectivity)
- **核心主题**: 基于 IoT 边缘网关与 Bluetooth Mesh 无线传感器网络的智能空间控制
- **归类理由**: 原属 IoT & Hardware 赛道。要求在 IoT 边缘网关（Edge Gateway）上构建与蓝牙 Mesh（Bluetooth® Mesh）无线传感网络设备通信的智能照明、温控、安防或智能工牌系统。

---

## 挑战完整题目

基于蓝牙Mesh的创新应用

## 挑战描述 (Description)

蓝牙® Mesh组网技术为与周围环境交互创造了新机遇，无论是通过智能照明、供暖/制冷和安全系统让家庭或办公室更智能，还是构建无线传感器网络。
本挑战赛要求开发一款运行于物联网边缘网关的应用程序，该程序能够与蓝牙® Mesh网络设备通信并利用其功能。此类应用的示例包括消息板、智能徽章系统或传感器数据采集系统。

---

## 历届获奖方案与验证项目

- **Intel 赛道冠军 + IoT 总赛道冠军 + 全场总亚军 (2nd Overall)**：**Help.io / Team Health.io**（拉脱维亚大学战队：Austris Cīrulnieks、Mārcis Nīmants、Elvijs Viļķels、Aigars Cibuļskis、Dāvis Mednis — 2017 Movesense 冠军原班核心成员）`[L1]`/`[L2]` — 构建完全脱离互联网与蜂窝基站的灾害现场急救蓝牙 Mesh 分诊网络：伤员佩戴 Suunto Movesense BLE 胸带传感器（心率与 R-R 间期）-> iOS 12 收集节点执行端侧分诊评分（过滤前 5 个瞬态采样、满 15 个样本取最近 5 点窗口、HR 边界 `60..110`、RR 倍数 `> 2.0`）-> 局域网 HTTP 推送至 **Intel NUC**（BlueZ `meshd-ingas` + `nRF51_dongle` 蓝牙 5 HCI 网关）-> **4 块运行 Zephyr OS (`mesh_badge`) 的 PHYTEC `reel_board` 救援人员智能工牌**（地址 `0x0001`、`0x0002`）。
- **同届交叉获奖 (`[L2]` 马拉加大学官方报道)**：**Nokia / Intel 电动车蓝牙 Mesh 赛道第二名** — **José Manuel García**（UMA）。
- **硬件与通信经验**：通过移动终端率先收敛 Movesense GATT 外设采集再透传给 Intel NUC `meshd` 边缘守护进程，巧妙绕开了 Linux 单枚 `nRF51_dongle` 上同步并发 GATT 连接与实验性 BlueZ Mesh 的总线争用问题；同时针对现场 48 小时演示合理收紧报警阈值，确保主舞台演示 100% 稳定触发。
- **Bronze 原始档案**：[`2018_Intel_HelpIO_HealthIO_BluetoothMesh.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2018_Intel_HelpIO_HealthIO_BluetoothMesh.md)
- **原始信源**：[GitHub (`mnimants/junction2018`)](https://github.com/mnimants/junction2018) | [Intel BlueZ Mesh (`intel/Junction2018`)](https://github.com/intel/Junction2018) | [Intel 支持套件 (`feri/Junction2018_Support`)](https://github.com/feri/Junction2018_Support) | [Movesense 2018 官方回顾](https://www.movesense.com/news/2018/11/movesense-shined-in-junction-hackathon/) | [拉脱维亚大学官网报道](https://eztf.lu.lv/en/about-us/news/detail-view/t/98941/)
