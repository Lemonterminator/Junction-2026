# Open Edge Platform 仓库筛选

整理日期：2026-11-13。[组织入口](https://github.com/orgs/open-edge-platform/repositories?q=sort%3Astars)；
[清单快照](../../bronze/intel_open_edge_platform/repositories.json) 覆盖抓取时公开搜索返回的全部
70 个仓库，含 stars、默认分支和归档状态。stars 仅是带时间的快照，不是推荐依据。
下表能力来自 [六份固定提交 README](../../bronze/intel_open_edge_platform/manifest.json)；
“用途”和“接入判断”是分析建议，未部署验证。

| 仓库 | 来源明确的能力 | 本项目用途（建议） | 接入判断（分析） |
| --- | --- | --- | --- |
| [geti-instant-learn](https://github.com/open-edge-platform/geti-instant-learn) | 零/少样本视觉提示、检测分割、OpenVINO 导出；部分 backbone 有限制 | 框选一个样例后识别同类物体，向 Anomalib 提供物体 ROI | 优先小规模验证；不自动解决新物体抓取 |
| [manufacturing-ai-suite](https://github.com/open-edge-platform/manufacturing-ai-suite) | PCB 异常检测、托盘缺陷检测、流水线和监控参考应用 | 借鉴检测事件、缺陷记录及界面 | 选择性复用；完整套件的服务较多 |
| [edge-ai-sizing-tool](https://github.com/open-edge-platform/edge-ai-sizing-tool) | 自定义应用进程监测，CPU/GPU/NPU、内存和磁盘指标，JSON 输出 | 做资源使用基线和优化对照 | 优先工具；仍需自行记录推理和分拣耗时；Ubuntu 26.04 兼容性待测 |
| [dlstreamer](https://github.com/open-edge-platform/dlstreamer) | GStreamer/OpenVINO 视频推理、跟踪、MQTT/Kafka 输出 | 多路视频与事件流水线 | 需要时引入；相机归属和 Studio 接口需自己处理 |
| [scenescape](https://github.com/open-edge-platform/scenescape) | 多传感器统一坐标、场景图、多相机跟踪和区域分析 | 两台固定相机的桌面物体位置与分拣区域变化 | 进阶；需要标定，不假定移动腕部相机可直接接入 |
| [robotics-ai-suite](https://github.com/open-edge-platform/robotics-ai-suite) | ACT、Pi0.5、姿态估计、视觉伺服和固定机械臂参考实现 | 按需参考定位、抓取和 Intel 优化方案 | 逐项确认硬件；示例并非都适配 SO-101 |

辅助仓库（功能入口已阅读，未在本批次保存独立 README 快照）：
[Geti](https://github.com/open-edge-platform/geti) 用于视觉标注、训练和部署；
[Datumaro](https://github.com/open-edge-platform/datumaro) 用于视觉数据集整理、转换和质量检查；
[Model API](https://github.com/open-edge-platform/model_api) 简化视觉推理前后处理，通用模型需要匹配元数据。
这些不是 LeRobot 示教 episode 的通用替代工具。

`geti_v2`、`geti-sdk`、`edge-ai-tuning-kit` 在快照中已归档。
`edge-ai-libraries` 和 `edge-ai-suites` 可作组件导航，评估时应继续进入实际子项目，
避免仅因聚合 README 中存在链接就认定组件仍活跃或兼容。

组织者鼓励使用额外仓库的原话由用户提供，记录于 manifest，未独立核实。
没有证据说明使用更多仓库本身获得额外分数。下一步参见
[创意方案评估](../../gold/zh/intel_physical_ai_creativity_options.md)。
