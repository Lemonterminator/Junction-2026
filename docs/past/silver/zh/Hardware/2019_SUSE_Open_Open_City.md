# [2019] SUSE — 开放开放城市

## 元数据

- **年份**: 2019
- **挑战合作方**: SUSE
- **原始历史赛道**: Urban & Mobility
- **2026 对应赛道**: Hardware Track (by Arduino)
- **技术细分方向**: 嵌入式系统、边缘计算与通信硬件 (Embedded Systems, Edge Computing & Connectivity)
- **核心主题**: 基于 Raspberry Pi 3B+/4B+ 硬件集群（uMEC 边缘节点）与专用 Wi-Fi 网络的边缘计算平台
- **归类理由**: 虽原属 Urban & Mobility 赛道，但现场搭建了由树莓派 Raspberry Pi 3B+ 与 4B+ 开发板组成的 uMEC 边缘计算物理集群与专用 Wi-Fi 网络，运行 k3s 与 ETSI MEC 边缘硬件接口。

---

## 挑战完整题目

开放开放城市

## 挑战描述 (Description)

未来的城市将通过创新的开放平台整合技术和基础设施，从而提高市民的生活质量。

边缘计算在全球电信行业中扮演着越来越重要的角色。边缘发展的重点领域之一是“智慧城市”。SUSE 正在参与 Akraino / uMEC 项目，该项目旨在为网络边缘设备定义并交付一个计算平台。挑战者需要展示用例，并创建一个开放数据平台的原型，该平台能够收集、分析并与市民共享天气、交通和紧急信息。

挑战的参与者将获得一个专用 WiFi 网络以及一个运行在我们 uMEC 节点（Raspberry Pi 3B+ 和 4B+ 板）上的 k3s 集群的访问权限。这个基础平台还将包括一组 MEC API，这些 API 应被用于解决挑战。参与者将在这些 API 之上开发应用程序，并将其部署到我们的集群中。更复杂的应用程序可以使用 SUSE CAP 进行实现和部署。在后一种情况下，我们希望看到强大的云原生应用部署与我们的 uMEC 网络之间的智能集成。

## 可用资源 (Resources)

SUSE 将提供：我们将提供一个边缘计算节点集群，包括硬件和软件。该集群将作为挑战参与者构建的容器化应用程序的部署平台。我们将提供某些 ETSI MEC API 子集的开放实现。

更复杂的解决方案可以利用 SUSE CAP，它能够轻松实现云原生应用程序开发。这些解决方案必须与 uMEC 边缘网络上的设备和 API 进行交互。

---

## 历届获奖方案与验证项目

- **赛题第一名 (Winner)**：**Flowify** `[L1]` *(团队成员与代码仓库未公开归档)*
- **赛题第二名 (1st Runner-up)**：**suseXcity** `[L1]`
- **赛题第三名 (2nd Runner-up)**：**Ravenholm** `[L1]`
- **现场边缘集群硬件实况 (`[L2]` LF Edge / Akraino MicroMEC 复盘)**：SUSE 联合 Nokia 与 Arm 在比赛现场部署了物理微边缘集群——由多块 **Raspberry Pi 3B+ / 4B (`<= 4 GB RAM`)** 搭建轻量 **k3s**、**OpenFaaS Cloud** 以及 **ETSI MEC API** 子集，并通过独立局域 Wi-Fi 供团队现场本地部署测试。
- **硬件与工程经验**：多团队在 Junction 2019 树莓派节点上高频部署容器暴露出 SD 卡严重的 I/O 瓶颈与损坏隐患，直接促使 SUSE/Nokia/Arm 在随后的 Akraino R3 版本中转向 **PXE 网络启动 + 共享 iSCSI 存储**；赛前务必预备好 `arm64`/`armhf` 多架构容器构建。
- **Bronze 原始档案**：[`2019_SUSE_OpenOpenCity_Flowify.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2019_SUSE_OpenOpenCity_Flowify.md)
- **原始信源**：[Junction 2019 官方获奖公告 (Medium)](https://medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f) | [LF Edge Akraino MicroMEC 技术复盘](https://www.lfedge.org/2020/08/13/micromec-now-available-with-the-akraino-r3-release/)
