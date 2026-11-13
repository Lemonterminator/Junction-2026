# Physical AI Studio：Junction 2026 操作指南整理

整理日期：2026-11-13。[原文快照](../../bronze/intel_open_edge_platform/JUNCTION2026.md)、
[版本与校验值](../../bronze/intel_open_edge_platform/manifest.json)。来源是
`open-edge-platform/physical-ai-studio` 的 `junction2026` 分支，固定提交
`17714488fa9c7d098a056da83f7c220cf983957d`。本文为整理，不替代原文或现场规则。

## 指南明确的信息

- 任务：在 Intel Core Ultra AI PC 上实现 SO-101 闭环，检查桌面物体、检测缺陷并分拣。
  具体物体、缺陷和分拣规则于 kickoff 公布。
- 原生启动：`application/backend` 内执行 `uv run --extra xpu physicalai-studio serve`；
  `application/ui` 内执行 `npm install`、`npm run start`。后端 7860、UI 3000。
  Docker 是另一种启动方式，容器统一使用 7860。
- Studio 内建立 project，添加 robots、cameras，再组合为 environment。
- 指南写明每位参与者提供 $100 Modal 训练额度，按组织者说明兑换。后台进程需要
  Modal 凭证，浏览器登录不等于后端认证；随后在 Modal Provider 中部署并连接。
  GPU 可选 A10G/A100/H100，收费不同；关闭 Studio 不会停止作业收费，单作业最长 24 小时。
- Hub 策略如 SmolVLA、Pi0.5 需要模型下载权限；使用个人只读 HF token。
- Anomalib 独立虚拟环境安装，避免 PyTorch 冲突；指南建议异常模型用本机 Intel XPU
  训练，将 Modal 用于策略训练。多数异常模型用正常图像训练，覆盖正常变化很重要。
- Studio 的示教录制和训练 UI 支持 ACT、SmolVLA、Pi0.5。不同策略对语言任务的支持
  不同，需要按实际策略设计检测结果到动作的接口。
- Studio 不内置异常检测。需自行连接 Anomalib 与动作，达到无人手动选任务的闭环；
  指南推荐 OpenVINO PhysicalAI 的 `InferenceModel` 和 Anomalib OpenVINO inferencer。
- 优化需测量推理步骤与分拣周期耗时、功耗、温度，并说明 CPU/iGPU/NPU 的任务分配。

## GitHub 指南评分（100 分）

| 原始评分项 | 分值 | 关注点 |
| --- | ---: | --- |
| Task Success Rate | 25 | 准确率、周期、物体偏移和杂乱场景鲁棒性 |
| Intel Tech Integration | 25 | NPU/iGPU、OpenVINO、Robotics AI Suite |
| Dataset & Pipeline Quality | 20 | 干净示教数据、Studio 微调 |
| System Efficiency | 20 | 推理耗时、温度余量、功耗 |
| Creativity | 10 | 超出基线的原创想法 |

这与 [PDF 第 7 页](../intel_physical_ai_hackathon.md#page-7---judging-criteria)
中的六项评分不同。尚无证据证明哪一版是最终版本；保留两版并向组织者确认。

## 仓库配置补充（不是指南原文）

固定版本的 `application/backend/pyproject.toml` 限定 Python >=3.13,<3.14；
`application/docs/08-deploying-model-policies.md` 列出 UI 内 CPU/GPU 推理。
`application/docker/Dockerfile` 提供 CPU/XPU/CUDA 构建目标，且使用 `libs` 命名构建上下文。
模型支持导出不等于能在每种设备运行；本项目的 Docker 接入说明见
[DOCKER.md](../../../infrastructure/DOCKER.md)。硬件和模型未在本次任务中运行验证。
