# Junction 历年硬件相关赢家：可复用技术与演示设计

核查日期：2026-11-14。范围为芬兰 Junction 主赛事中与感知、硬件控制、三维与仿真相关的获奖项目；并非所有项目都属于当年的 Hardware Track，也不是完整获奖目录。

后续落地安排见[Physical AI 详细执行计划](../plans/PHYSICAL_AI_EXECUTION_PLAN.md)：工作包、依赖、验收、数据与排期集中维护于该文档，本文保留历史证据和设计依据。

## 结论与证据边界

最值得迁移到当前 SO-101 缺陷分拣项目的组合是：轻量候选区域提取、专用缺陷模型、可观察的硬件闭环、交互式三维验证，以及完整的操作员流程。

以下“复用”是本项目的设计建议，不代表历史团队实现过机器人训练、Gemini、RL 或 sim-to-real。获奖公告证明名次；代码证明实现结构；作者描述的效果仍不是独立性能测量。本次未构建或运行任何历史项目。

本仓库 `docs/past/gold/en/hardware.md` 可作检索入口，但部分细节不能由原始来源支持，不能直接当作性能基准：

- Wavelet 的公开源码与作者声明支持 FDTD、C++/OpenGL、计算着色器及交互仿真；本次未获得足以证明“1080p/4K 稳定 60 FPS、单步低于 16 ms、商业求解器数小时对比”的可复现实验。
- Academic Menaces 的获奖线索不等于已核实其 SNN、Kalman、低于 1 ms、98% 等具体实现与指标；不据此选型。
- QuickBIM 作者确认全场第三，并表述为 KONE 赛题领先团队之一；本次来源不足以据此确认 KONE 第一。
- “获奖原因”不能只从名次反推。明确采用官方采访中的评语或作者复盘，其余标为设计推论。

## 1. Signvision，2017 全场冠军：先裁剪，再分类

**已核实**：Junction 官方采访确认全场冠军，介绍实时交通标志识别、位置记录和维护工作流，并肯定技术实现与用户体验。源码提供 OpenCV HSV 红色掩码、形态学处理、连通区域裁剪，再送入 32×32 输入的小型 CNN；训练代码的目标是停车标志二分类，不能扩大为全面缺陷识别。

**迁移到分拣**：深度桌面分割提供工件 ROI，再对 RGB 裁剪运行 Anomalib。让屏幕显示“工件位置 → 异常热图 → 分类决策 → 目标容器 → 执行结果”，减少背景对缺陷判断的干扰。

**限制**：裁剪边界与缩放需要保留目标缺陷；用真实正常/缺陷样本检验。原代码返回的 `probability` 有固定值，不能复用为可信置信度。

- [Junction 官方采访](https://medium.com/hack-junction/a-mix-of-machine-learning-and-cool-ux-won-junction-2017-15963c0ace3b)
- [候选区域源码](https://github.com/teamglados/signvision/blob/af62b831eb628b5ed5a3c855b7c5e9009da6a34e/cnn_model/utils.py)
- [模型源码](https://github.com/teamglados/signvision/blob/af62b831eb628b5ed5a3c855b7c5e9009da6a34e/cnn_model/cnn_model.py)
- [推理接口](https://github.com/teamglados/signvision/blob/af62b831eb628b5ed5a3c855b7c5e9009da6a34e/cnn_model/app.py)

## 2. Oneiro，2018 全场冠军、Ensto 挑战冠军：感知连接设备与产品流程

**已核实**：官方采访介绍共享私人充电桩，强调清楚的用途、实际原型和完整产品。仓库包含 Raspberry Pi 相机、OpenALPR、Python 后端、Ensto 设备接口、React Native 客户端与 Telia 活动数据地图。

相机脚本每轮等待 0.5 秒，上传请求设置 2 秒超时；这不是固定 2 FPS 或端到端延迟保证。`Api` 用 `live` 参数选择真实或演示设备标识，查询连接器状态，通过识别候选置信阈值调用启用接口。所读认证函数没有证明车牌与预约用户匹配；费用演示还使用随机时长，不能当作真实计费实现。

**迁移到分拣**：采用共同接口的离线回放、仿真、真实硬件适配器，让感知、前端、策略在没有机械臂时也能开发。显式标注模式，真实模式仍执行现有授权与硬件限制。

每件工件保留观察、检测结果、动作请求、设备状态与最终结果。将业务价值对应到每小时正确分拣件数、漏检/误剔除率、人工介入次数，具体收益根据实测估算。

**限制**：借鉴超时与状态查询设计；不照搬吞掉全部异常、无用户匹配的认证逻辑或随机指标。充电接口的网络节奏不能直接用于机械臂控制循环。

- [Junction 官方采访](https://medium.com/hack-junction/this-trio-has-hacked-the-hackathon-ville-andreas-and-teemu-won-junction-for-the-2nd-time-b193e9d7f7b)
- [项目说明](https://github.com/teamglados/oneiro/blob/019ac8c936f0d796ccc3ff2c7be8458fba11e422/README.md)
- [硬件 API 与模式选择](https://github.com/teamglados/oneiro/blob/019ac8c936f0d796ccc3ff2c7be8458fba11e422/server/api.py)
- [相机上传脚本](https://github.com/teamglados/oneiro/blob/019ac8c936f0d796ccc3ff2c7be8458fba11e422/raspberry/photographer.py)

## 3. LumenLoop，2019 Helvar/VTT 挑战冠军：轻量信号处理连接执行器

**已核实**：官方获奖名单确认 Making Spaces Brighter with Radar Technology 挑战第一。`live/Streamer60.py` 读取 RabbitMQ/FlatBuffers 雷达幅度，重排为 180×110 数组，每十帧用列峰值相对变化阈值估计人数，再 POST 亮度和色温设置。它是简单统计量驱动的原型，不是已验证的通用人数估计系统。

**迁移到分拣**：桌面平面、工件高度、容器颜色和放置区域等有明确几何先验的子任务，先使用可解释算法。昂贵视觉推理用于几何规则不能解决的缺陷或语义问题。

把显示、感知更新、策略推理、动作执行设为各自合适的节奏。当前建议是单相机采集服务向各消费者分发带时间戳的帧；推理速度落后时处理最新有效观察，避免积压旧帧。此分发设计是本项目建议，不是历史代码性能结论。

**限制**：原型里的同步 HTTP 调用没有设置超时；不要直接迁移到动作循环。雷达规则的准确率与鲁棒性没有在本次核查中建立。

- [Junction 官方获奖名单](https://medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f)
- [感知到灯光设置的源码](https://github.com/deniskovalenko/junction2019/blob/a6adfbe78851ad5d41819c7d8c4c57551eece36a/live/Streamer60.py)
- [作者复盘与团队确认](https://elizavetalebedeva.com/tag/junction/)

## 4. QuickBIM，2024 全场第三：复用三维转换工具，打通交互流程

**已核实**：作者复盘确认全场第三。团队找到可容器化运行的既有平面图转换项目，用 OpenCV/Blender 生成三维模型，在 Azure 部署，通过 Web 浏览、摆放电梯，再用 Flutter 应用展示 AR。公开仓库的前端源码支持 Three.js/glTF 加载、拖动与导出；公开树未包含完整转换后端，作者说明不能等同于全部后端已可从此仓库复现。

**迁移到 twin**：直接采用现成 SO-101 模型和 MuJoCo/LeIsaac，桌面及工件从简单几何开始。投入标定、状态回放、结果对照和失败重现。浏览器可视化可以单独建设，但 glTF 视觉模型不能替代带关节、质量、碰撞与接触参数的物理模型。

**限制**：平面图转建筑模型解决的是建模与销售展示，不证明机器人动力学精度或 sim-to-real 成功率。作者记录的 Docker/Azure 集成成本也说明应尽早完成环境与接口验证。

- [作者完整复盘](https://www.jemlap.fi/blog/junction-2024)
- [项目说明](https://github.com/Mankeli-Software/quickbim/blob/123fe97a44ef0693079a5c507cace3eb666d53f0/README.md)
- [三维交互与导出源码](https://github.com/Mankeli-Software/quickbim/blob/123fe97a44ef0693079a5c507cace3eb666d53f0/web_app/src/components/model.tsx)

## 5. Wavelet，2025 全场冠军、Sensofusion Radio City 冠军：让物理机制可以交互检验

**已核实**：项目 README、作者获奖声明及出题方负责人回复相互支持名次。公开代码有 FDTD 求解器、更新电场/磁场的计算着色器、几何标记、空间索引和交互 UI。README 描述 C++/OpenGL GPU 仿真、香港场景、发射节点、频率和仿真参数调整。

**迁移到 twin**：展示真实画面和仿真并排，允许在仿真中改变积木位置、容器位置或摩擦假设，观察抓取结果与轨迹变化。用预测与观察的误差解释模型在哪里可靠、哪里失效。先有可运行模型，再增加可视化。

**限制**：电磁求解器不能直接用于机器人；有物理方程和漂亮图像也不自动证明精度。当前源码可能包括赛后改动，本次固定的是检索时版本，没有把所有功能归因到赛时版本。不能把获奖归因为单个架构选择。

- [公开仓库与 README](https://github.com/ron0studios/WAVELET/blob/bae036417110e118193d3c44626908d856a36ab7/README.md)
- [FDTD 求解器接口](https://github.com/ron0studios/WAVELET/blob/bae036417110e118193d3c44626908d856a36ab7/include/fdtd_solver.h)
- [作者获奖声明及出题方回复](https://www.linkedin.com/posts/arjunjuneja_hi-again-i-just-won-one-of-europes-biggest-activity-7395862662816952321-cJR1)

## 补充：Health.io 与机器人赛题的证据范围

Movesense 官方 2018 复盘确认 Health.io 赢得 IoT Track：用心率传感器与 Bluetooth Mesh，在传统通信失效时传递患者状态。可迁移的是“本地核心功能与云端增强分开”的设计目标：Gemini 用于分析、指令和课程生成，已配置的本地分拣策略可独立执行。该目标尚需本项目实现与测试。

- [Movesense 官方复盘](https://www.movesense.com/news/2018/11/movesense-shined-in-junction-hackathon/)

2022 Cruising with Robots 的 CGI 官方文章确认 C-HAL 9000 第一、Laundry day is everyday 第二，但没有足够公开源码来核实两队具体技术路线。本研究不把基于赛题推导的架构当成获奖队实装方案。

- [CGI 官方文章](https://www.cgi.com/fi/fi/blogi/cginside/out-box-thinking-more-valuable-ever)

## 本项目可采用的三个使用案例

以下均为建议，尚未实现或测得效果。

| 优先级 | 使用案例 | 展示内容 | 判断是否值得继续的证据 |
| --- | --- | --- | --- |
| P0 | 可追溯缺陷分拣 | ROI、异常热图、目标容器、机械臂执行、放置结果与工件记录 | 真实正常/缺陷留出集；完整分拣成功率；误剔除/漏检；周期与人工介入 |
| P1 | 能解释失败的 twin | 回放失败，叠加预测与真实关节/物体位置，改变一个条件并重试仿真 | 标定留出误差；失败是否在仿真重现；仿真预测与真实结果一致率 |
| P2 | Gemini 训练教练 | 读取失败片段与记录，提出可检验假设，调用有限仿真技能生成补充训练场景 | 固定课程与 Gemini 课程对比；控制数据量/训练预算；真实留出任务增益 |

首轮落地顺序：共同数据契约与离线回放 → 单工件真实闭环及结果验证 → 对齐后的 twin → 受控故障演示 → Gemini 课程或 RL 实验。

工件记录建议包含 `episode_id`、`object_id`、帧时间、标定版本、检测模型版本、异常结果、目标容器、动作状态、结果证据和失败原因。连续视频中的同一工件需要关联身份，不能每帧生成一次新任务。

硬件效率对照使用同一批输入和相同精度要求，测量 CPU/GPU/NPU 的完整管线 P50/P95、正确率与周期；模型 kernel 延迟不等于分拣速度，配置阈值也不等于测得指标。

演示建议：先展示一次正常闭环，再引入工作区内可控的位置变化，展示重新观察或失败判断，最后回放 twin 与真实的差异。所有实机运动仍遵守仓库的单次授权与限位要求；仿真、回放、预先训练结果和现场实时功能明确标识。

## 代码复用与验证状态

本次仅查看源码与文档，未下载执行历史程序、未安装历史依赖、未操作相机或机械臂。固定的源码版本便于后续复核，不代表赛时快照。旧依赖需要现代化；未见明确许可证的仓库仅作为设计参考，直接纳入代码前先确认许可。Wavelet 仓库标注 MIT，复制相关代码时仍应保留适用声明。

未修改既有 Gold 档案；上面的具体差异作为独立核查记录保留。
