# [2021] Helvar — 更明亮的空间：智能照明

## 元数据

- **年份**: 2021
- **挑战合作方**: Helvar
- **原始历史赛道**: IoT & Hardware
- **2026 对应赛道**: Hardware Track (by Arduino)
- **技术细分方向**: 智能建筑、工业物联网与数字孪生 (Smart Buildings, Industrial IoT & Digital Twins)
- **核心主题**: 室内运动与音频传感器网络自标定、高频人流轨迹识别与地下车库多模态感知
- **归类理由**: 原属 IoT & Hardware 赛道。基于室内照明系统的运动传感器与车库音频/运动传感器时序数据，解决大规模传感器网络在建筑平面图上的自动定位及人车行为识别。

---

## 挑战完整题目

更明亮的空间：智能照明

## 挑战描述 (Description)

在这个挑战中，我们要求您利用、应用和可视化传感器数据，以了解建筑的使用情况，并优化传感器网络在建筑中的初始部署。您可以选择挑战的三个部分中的一个或全部进行工作。

所有设备在哪里？
我们通常花费大量精力在平面图上识别和定位大量传感器。我们能否简化这个过程，并利用一部分传感器的数据自动将其余传感器放置在平面图上？

每个人要去哪里？
运动传感器有助于确定空间中的活动量。我们也知道空间的类型，例如走廊或通道。鉴于传感器生成数十万个运动事件，我们能否识别建筑物中使用最频繁的路径？

神秘车库
车库中有移动的车辆和行人。我们有运动传感器和音频传感器。我们能否识别车库中正在发生的事情？是否有车辆进出？行人是走向电梯，还是上车？

## 可用资源 (Resources)

我们将提供不同平面图的布局，包含设备位置以及运动和音频事件的时间序列。

数据集：
建筑物：参与者将获得来自室内场所的数据集。数据将完全匿名化。平面图将包含设备及其位置。数据集将是平面图上所有传感器的运动事件时间序列。

车库：参与者将获得来自室内车库的训练数据集，使用运动和音频传感器收集。

鼓励您使用其他数据源，并随时使用来自其他Junction挑战的数据或将您的想法与其他挑战结合，如果您认为合适。

---

## 历届获奖方案与验证项目

- **赛题获胜者 & 全场 Top-10 总决赛入围（200+ 项目中）**：**Lumen Loop 3.0**（Elizaveta Lebedeva、Denys Kovalenko、Carlos Bentes — 2019 Helvar 雷达冠军原班核心再战）`[L1]`/`[L2]` — 定位 *“智能照明领域的 AirTag”*，主攻子题 1 *“设备都在哪？”*：将稀疏异步 PIR/音频触发事件按 5 秒窗口分桶（`CombinedCorrelator`），基于 `scipy` 皮尔逊共现相关性反推未标定灯具坐标，持久化 5 座建筑模型（`.pickle`），并提供 64 px 建筑平面瓦片图与人工复核推荐工作流（Flask `/tiles` + `/recommendations`）。
- **赛题获胜记录（Helvar 获奖团队）**：**FloorMagic (Healthy Mind Tech)**（Paula Petcu、Troels Nielsen、Martin Basterrechea、Kim Ng）`[L1]`/`[L2]` — 基于人员移动传感数据预测楼宇未定位传感器物理坐标 *(源码未公开)*。
- **硬件与工程经验**：面对建筑 PIR/声学等稀疏非均匀触发事件流，利用多尺度粗粒度时间分桶（如 `5s`）结合加权相关性比复杂序列模型更稳健；将预测直接落成“建筑瓦片地图 + Top-K 点位人工确认”的施工端到端闭环是打动工业评委的关键。
- **Bronze 原始档案**：[`2021_Helvar_BrighterSpaces_LumenLoop3_FloorMagic.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2021_Helvar_BrighterSpaces_LumenLoop3_FloorMagic.md)
- **原始信源**：[GitHub (`LizaLebedeva/junction-2021`)](https://github.com/LizaLebedeva/junction-2021) | [YouTube 演示](https://www.youtube.com/watch?v=dX27x6s6wl4) | [Healthy Mind Tech 官网](https://healthymindtech.com/) | [Junction Medium 复盘](https://hackjunction.medium.com/junction-2021-intelligent-lighting-as-the-engine-for-brighter-spaces-1926e69eed6b)
