# [2018] Vaisala — 改造桑拿

## 元数据

- **年份**: 2018
- **挑战合作方**: Vaisala
- **原始历史赛道**: Sustainability
- **2026 对应赛道**: Hardware Track (by Arduino)
- **技术细分方向**: 智能建筑、工业物联网与数字孪生 (Smart Buildings, Industrial IoT & Digital Twins)
- **核心主题**: 极端高温高湿环境下的工业级桑拿传感测量仪器（替代传统机械温度计）与数字化体验
- **归类理由**: 虽原属 Sustainability 赛道，但聚焦极端高温高湿物理环境下（桑拿房）精密温湿度测量传感器硬件的应用与数字化改造。

---

## 挑战完整题目

改造桑拿

## 挑战描述 (Description)

桑拿是传统的沐浴和放松场所。它也可能是一个对人和测量仪器都严苛的环境。几个世纪以来，桑拿体验并没有太大变化：例如，如今桑拿房内的条件仍然使用机械温度计来测量。我们觉得是时候让桑拿体验现代化了！

---

## 历届获奖方案与验证项目

- **赛题第一名 (Winner)**：**Make Sauna Great Again (MaSGA)**（Siavash H. Khajavi、Alireza Jaribion、Adriaan Knapen、Leila Abiedat、Arnab Banik）`[L1]`/`[L2]` — 通过 Google Cloud Functions 轮询 Vaisala 多空间探头（`Stove1`、`Bench1–3`、`Floor1` 采集 O2、CO2、温度、相对湿度与焓值），基于现场收集的 **22 份真实桑拿体验问卷**（`10–15 分钟` 沐浴时长）标定梯形模糊相似度模型（`quadro()`），分别针对 **普通用户模式** 与 **场馆管理员模式** 每 10 秒输出直观红黄绿体验分（`> 88%` / `> 75%` / `<= 75%`）及实体调控建议（如泼水、开窗降 CO2、调低炉温），成果后续发表于 IEEE IECON 2020 会议。
- **已验证亚军/入围项目**：**Talking Sauna** 与 **BMC – Blazing Measurements and Controls** `[L1]`。
- **硬件与工程经验**：多传感器热力学监测绝不能靠拍脑袋定阈值——结合真人问卷构建模糊数学评分并拆分“体感舒适 vs. 能耗通风控制”双视角，显著提升硬件数据的实际可执行性。
- **Bronze 原始档案**：[`2018_Vaisala_MaSGA.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2018_Vaisala_MaSGA.md)
- **原始信源**：[前端仓库 (`Addono/masga`)](https://github.com/Addono/masga) | [后端仓库 (`Addono/masga-backend`)](https://github.com/Addono/masga-backend) | [Vaisala 官方博客](https://www.vaisala.com/en/blog/2018-11/winners-vaisalas-challenges-junction-2018-hacked-weather-and-sauna) | [阿尔托大学新闻](https://www.aalto.fi/en/news/winning-team-hack-the-sauna-experience-to-a-new-level-at-junction) | [IEEE IECON 2020 (Aaltodoc)](https://aaltodoc.aalto.fi/items/44b6d03b-0849-4381-a9e4-300de579f7d3)
