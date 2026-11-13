# Intel Physical AI Challenge：赛题分析与执行建议

> 更新：2026-11-13。来源：[Silver 逐页转录](../../silver/intel_physical_ai_hackathon.md)、[原始 PDF](../../silver/Intel_Physical%20AI%20Hackathon.pdf)，共 15 页；补充 [GitHub 比赛指南](../../silver/zh/intel_physical_ai_studio_guide.md)。第 1–7 节保留 PDF 来源，第 8 节记录 GitHub 补充和冲突。“建议”是项目分析。尚未独立验证现场设备、模型兼容性或真机运行。

## 1. 已确认的赛题

**Stop Simulating, Start Moving: See It. Detect It. Act on It. The Intel Physical AI Challenge** 要求构建机器人缺陷检测与智能操作的端到端 Physical AI 系统：区分合格（perfect）和异常（defective）物体，再按 kickoff 公布的规则进行物理分拣或其他响应。（PDF p.1、p.3）

必须展示完整闭环：**PERCEIVE -> DETECT -> REASON -> ACT -> OPTIMIZE**。Intel Physical AI Studio 提供 VLA 工作流，Anomalib 提供缺陷判断与定位信号，SO-101 执行实际动作，OpenVINO 将支持的推理工作负载优化并部署到 Intel Core Ultra Series 3。（p.3-6）

PDF p.2 列出 Intel x Ignite Next 支持团队。原有 Silver 中笼统的 Hardware Lab 描述现可细化为上述正式赛题；Bronze 中关于 oneAPI、SLAM、创业孵化等奖励的早期推测，不应视作本赛题要求或承诺。

## 2. 技术要求与资源

| 环节 | 文件明确要求 | 页码 |
| :--- | :--- | :--- |
| 感知与检测 | 从机器人工作区采集图像；Anomalib 输出可供下游消费的结构化信号、标签、分数或定位区域 | 4-6 |
| 推理与规划 | Physical AI Studio 中的 VLA 根据任务指令和感知结果确定响应，输出机器人控制所需的动作意图 | 4-6 |
| 物理执行 | SO-101 将决策转换为移动、抓取、分拣或赛题指定动作 | 4-6 |
| 推理优化 | 考虑模型转换、精度、计算图、前后处理和设备选择，降低端到端延迟 | 6 |
| 端侧部署 | 在 Core Ultra Series 3 上，按工作负载和算子支持使用 NPU、GPU、CPU，保持控制可靠及应用响应 | 6 |
| 演示 | 展示采集、检测、VLA 推理到物理动作的全过程，并解释架构及优化决策 | 6、9 |

设备及软件清单按 PDF p.8 记录，属于资料中的配置声明：

- 计算机二选一：HP OmniBook Ultra (C2NM8AV)，或 Dell XPS 16 [DA16260]；均标注 Intel Core Ultra X9 Series 3 (388H) AI PC。
- LeRobot SO-ARM101，已组装 1 Leader + 1 Follower + 1 wrist camera。
- 摄像头：1 台 RealSense Depth Camera 415，1 台 Pro QHD 2K/60fps Webcam；另有支架、USB Hub、Lego/碗及打印的机器人安全指南。
- 需安装 Physical AI Studio 与 AnomaLib v2.7.0；预装项为 Ubuntu v26.04、NPU Driver、iGPU Driver；训练使用 Modal 提供的 GPU 云实例。

PDF 同时使用 SO-101 和 SO-ARM101，本文保留这两种写法。ACT、SmolVLA 在 p.9 的示意图中出现；p.11-12 还展示其他策略与机器人作为平台能力，不能据此认为比赛要求实现全部策略或适配全部硬件。

## 3. PDF 评分表：100 分（最终采用版本待确认）

| 评分项 | 分值 | 核心证据 | 页码 |
| :--- | ---: | :--- | :--- |
| End-to-End Physical AI Solution | 25 | SO-101 上从视觉检测、决策到动作的一体化闭环 | 7 |
| Defect Detection with Anomalib | 20 | 检测质量、模型集成、正常/缺陷处理及下游如何消费输出 | 7 |
| VLA & Physical AI Studio Integration | 20 | 从感知与任务指令到规划和实际操作的可见集成 | 7 |
| OpenVINO & Intel Core Ultra Series 3 Optimization | 20 | 延迟、吞吐、部署效率及 NPU/GPU/CPU 的合理分配 | 7 |
| Robotic Execution & Reliability | 10 | 定位、操作精度、重复性、稳定完成及错误/不确定检测后的恢复 | 7 |
| Innovation & Technical Demonstration | 5 | 原创性、Intel 技术使用、完整性及现场架构/优化讲解 | 7 |
| **总计** | **100** | | |

**仅按 PDF 分析：前四项合计 85 分，完整集成、检测、VLA 和端侧优化应优先完成。** GitHub 指南采用另一套评分，不能将此分值结构当成最终规则。PDF 关注同一闭环系统的工作表现。（p.7；差异见第 8 节）

## 4. 执行建议（分析，非官方附加要求）

1. **先打通最小闭环。** 以单物体、固定工作区验证相机采集、Anomalib、VLA、SO-101 动作和 OpenVINO 部署，确认实际执行结果能够回到下一轮观察。
2. **让模块交接可检查。** 建议记录物体图像、异常分数/标签/区域、任务指令、VLA 动作意图、机器人执行结果及时间戳，展示检测结果如何影响动作。
3. **先测基线，再解释优化。** 在相同输入和任务下记录优化前后的模型推理延迟、端到端耗时、吞吐及任务完成率，标明设备、精度和工作负载；按支持情况分配 CPU/GPU/NPU，避免将三者同时使用当成硬性要求。
4. **为可靠性留出演示证据。** 建议测试正常、缺陷、不确定输出和抓取失败情况，展示安全停止或恢复。p.13 提到框架具备动作限制、速度限制、急停等能力，具体现场接线与操作仍需确认。
5. **最后完善展示。** 用同一条实际任务链讲解架构、检测依据、VLA 如何选动作及优化收益，再扩展额外创意。

上述指标和实现细节是建议的自测方式；PDF 没有指定最低准确率、延迟门槛、必选模型或必须使用全部计算单元。

## 5. 必须交付的四项成果

PDF p.9 明确列出：

1. 从感知到动作的闭环 SO-101 Physical AI 工作原型。
2. VLA 机器人工作流与 Anomalib 视觉异常/缺陷检测的集成。
3. Intel Core Ultra Series 3 上经 OpenVINO 优化的推理部署。
4. 执行 Challenge-Day 任务的现场演示，解释架构与优化选择。

## 6. 待现场确认

- kickoff / Challenge-Day 的具体物体、缺陷定义、分拣规则及其他操作规则。（p.3、p.9 明确留待现场任务）
- 实际分配的电脑、摄像头位置、机械臂校准状态及设备使用安排。
- Physical AI Studio / OpenVINO 的具体版本、目标策略导出与算子支持、驱动可用性。
- 训练数据、Modal 实际兑换与实例访问、网络；PDF 仅说明提供 GPU 云实例，GitHub 的额度和时长声明见第 8 节，实际领取未核实。
- 奖项、提交格式、截止时间及详细安全流程；本文件未给出完整规定，不沿用 Bronze 的推测。

## 7. 文件中的参考入口

- Intel Robotics：<https://developer.robotics.intel.com>（p.10）。
- Physical AI Studio：<https://github.com/open-edge-platform/physical-ai-studio/>（p.12）。

以上是 PDF 中的入口；Physical AI Studio 已在后续接入中在线读取并固定为子模块。

## 8. GitHub 操作指南补充与来源冲突

来源：[固定原文](../../bronze/intel_open_edge_platform/JUNCTION2026.md)，
Studio `junction2026` 提交 `17714488fa9c7d098a056da83f7c220cf983957d`。

| GitHub 评分项 | 分值 |
| --- | ---: |
| Task Success Rate | 25 |
| Intel Tech Integration | 25 |
| Dataset & Pipeline Quality | 20 |
| System Efficiency | 20 |
| Creativity | 10 |
| **合计** | **100** |

与 PDF 的六项评分相比，GitHub 将重点组织为成功率、Intel 技术、数据流水线、效率和创意；
创意项为 10 分，PDF 的 Innovation & Technical Demonstration 为 5 分，两者名称和范围也不同。
不能逐项视为直接替换或认定后发布者自动优先；需要组织者确认最终规则。

GitHub 指南还写明每位参与者 $100 Modal 额度、按说明兑换，单作业最长 24 小时；
Anomalib 采用独立环境并建议本地 XPU 训练，Studio 支持 ACT/SmolVLA/Pi0.5 示教训练，
检测到动作的自动连接由队伍实现。这些是指南声明，不代表我们已领取额度或完成部署。

工程上已引入完整上游源码与 Docker 配置，见 [Docker 说明](../../../infrastructure/DOCKER.md)。
可选扩展和实施顺序见 [创意分析](intel_physical_ai_creativity_options.md)；均未真机验证。
