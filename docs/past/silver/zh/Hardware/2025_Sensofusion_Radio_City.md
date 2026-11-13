# [2025] Sensofusion — 无线电城市

## 元数据

- **年份**: 2025
- **挑战合作方**: Sensofusion
- **原始历史赛道**: Entertainment
- **2026 对应赛道**: Hardware Track (by Arduino)
- **技术细分方向**: 毫米波雷达与高速机器视觉传感器 (Millimeter-Wave Radar & High-Speed Machine Vision Sensors)
- **核心主题**: 三维城市环境中移动电台、车载与无人机射频无线电波（Radio Waves）物理传播与多径反射仿真
- **归类理由**: 虽原属 Entertainment 赛道，但由反无人机射频侦测硬件厂商 Sensofusion 发起，聚焦无线电波在真实物理城市建筑间的传播损耗、反射与遮挡物理建模。

---

## 挑战完整题目

无线电城市

## 挑战描述 (Description)

无线电波：它们环绕着我们，穿透着我们；它们将星系紧密相连。向我们展示它们吧。

无线电悄然驱动着我们日常生活的方方面面。本次挑战提供了一种平易近人的方式来掌握基础知识。利用一个3D城市模型，让无形的无线电世界变得可见。展示无线电发射器何时何地能被听到——以及何时会消失。

使用提供的香港3D模型，演示无线电波如何传播。在地图上放置假想的移动无线电源：例如，街上行走的手机用户、街道上行驶的汽车或空中飞行的无人机——或者想出其他来源。然后可视化这些源发出的无线电传输如何传播。您将演示无线电波如何从墙壁反射，以及地理障碍如何阻挡无线电。我们将寻找基于物理的模拟与富有创意的视觉效果。您需要理解无线电的行为方式。理想情况下，您的可视化也能帮助他人学习。如果能为故事增色，请随意添加交互性和引入其他数据。可视化无线电波有多种不同方式。本次挑战没有唯一正确答案；有多种创意方式展示您的结果。

## 挑战洞察 (Challenge Insights)

背景与来源：
https://en.wikipedia.org/wiki/Radio https://en.wikipedia.org/wiki/Radio_wave 
https://en.wikipedia.org/wiki/Radio_propagation 
https://en.wikipedia.org/wiki/Line-of-sight_propagation
https://en.wikipedia.org/wiki/Ray_tracing_(graphics)
https://en.wikipedia.org/wiki/Free-space_path_loss
https://en.wikipedia.org/wiki/Computational_electromagnetics
https://en.wikipedia.org/wiki/ITU_terrain_model

一些可视化想法：
https://wifi-solver.com/
https://wigle.net/
https://www.youtube.com/watch?v=qHLaFV86XmM

## 评审标准 (Judging Criteria)

我们希望看到无线电波在3D城市中的样子。向我们展示一个交互式演示或制作一段视频。让它炫目。让我们惊叹。如果您愿意，甚至可以把它变成一个3D游戏。以清晰、可信和精致的方式将您的想法变为现实，展现对细节的关注。

## 奖项设置 (Prizes)

由Sensofusion导师选出的获胜团队将获得DJI Mini 3无人机作为奖励。获胜团队的每位成员都将获得一架无人机。

## 可用资源 (Resources)

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

## 关于合作方 (About Company)

Sensofusion的使命是通过我们的Airfence产品保护人员和基础设施免受无人机威胁。我们的系统已准备就绪、经过测试并正在交付。Sensofusion在欧洲、北美、中东和亚洲拥有政府客户。

---

## 历届获奖方案与验证项目

- **赛题第一名兼 Junction 2025 全场总冠军 🏆**：**WAVELET**（Rudrrayan Manna、Arjun Juneja、Keanu Czirjak、Akshith Alluri）`[L1]` — 使用纯手写 C++20 与 OpenGL 4.6 Compute Shaders 在 GPU 显存内构建 60 FPS 实时 FDTD 麦克斯韦波动方程求解器，基于香港三维城市网格实时演算射频多径反射、建筑物边缘绕射与无线电发射源反向三角定位（单步 `< 16 ms`）。
- **Bronze & Gold 参考**：[`2025_Sensofusion_WAVELET.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2025_Sensofusion_WAVELET.md) | [Gold 硬件赛道 (`hardware.md`)](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/gold/zh/hardware.md)
