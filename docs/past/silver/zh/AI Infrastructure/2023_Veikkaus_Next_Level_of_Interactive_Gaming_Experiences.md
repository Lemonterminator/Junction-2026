# [2023] Veikkaus — 互动游戏体验的下一个层次

## 元数据

- **年份**: 2023
- **挑战合作方**: Veikkaus
- **原始历史赛道**: Entertainment
- **2026 对应赛道**: AI Infrastructure Track (by Verda)
- **技术细分方向**: 三、边缘计算、5G 网络与端侧/WebGPU 高性能计算底座 (Edge Computing, 5G & On-Device/WebGPU Runtime)
- **核心主题**: 基于 WebGPU 与 WebWorker 的浏览器端底层 GPU 并行计算与渲染架构
- **归类理由**: 源自 Entertainment 赛道，要求用新一代 WebGPU API 和 WebWorker 替代老旧 WebGL，在浏览器无依赖环境下直接调度系统底层 GPU 执行高负载计算与渲染。

---

## 挑战完整题目

互动游戏体验的下一个层次

## 挑战描述 (Description)

Veikkaus 一直处于提供负责任在线赌博的前沿，通过有趣且安全的游戏体验。作为一家科技公司，我们不断面临提供新颖创新解决方案的挑战，尤其是在线即时游戏方面。我们看到了用 WebGPU 替代 WebGL 的有趣可能性，为开发者提供更高效利用 GPU 的机会，从而实现比旧技术（WebGL）更沉浸、更复杂的游戏体验。这是我们正在处理的真实挑战，我们很想听听您将如何解决它！挑战在于利用 WebGPU 和 WebWorker 技术创建一个技术 POC。我们更倾向于 POC 的性质看起来像在线即时/刮刮游戏，但也非常欢迎任何其他利用这些技术的实现。我们将提供一份精选的学习资源列表和现有游戏的参考，供您进行基准测试。除此之外，我们还将有行业领先的专家在场，帮助您就下一代在线即时游戏的概念以及可能的技术问题进行交流。

## 挑战洞察 (Challenge Insights)

所有在线即时和刮刮游戏的基本原理相同；玩家点击或“刮擦”以揭示符号或其组合，匹配或揭示获胜结果。获胜的赔率在后端计算，但游戏玩法的实际用户界面应尽可能有趣和沉浸，让玩家保持参与和娱乐直到最后。提供 UI 的传统方式主要是使用 WebGL，随着现代技术能够更高效地利用现有强大的系统 GPU，这种方式开始显现出老态。

## 评审标准 (Judging Criteria)

提交作品将根据 WebGPU 和 WebWorker 技术的利用程度进行评估。

## 奖项设置 (Prizes)

Verkkokauppa 礼品卡：第一名：2000€ / 第二名：1000€ / 第三名：500€

## 可用资源 (Resources)

挑战在于利用 WebGPU 和 WebWorker 技术创建一个技术 POC。我们更倾向于 POC 的性质看起来像在线即时/刮刮游戏，但也非常欢迎任何其他利用这些技术的实现。在构思您的 POC 时，您可以从 demoscene（粒子效果致胜）或需要复杂、CPU 密集型任务的场景（如计算获胜的棋步）中汲取灵感。您将找到一些关于这些技术的现有文档链接以及可供基准测试的现有游戏链接。我们将有行业领先的专家在场，帮助您就下一代在线即时游戏的概念以及创建 POC 可能的技术问题进行交流。

关于技术实现，我们希望您在可能的情况下避免外部依赖。我们还希望您的参赛作品能直接在浏览器和 iFrame 中运行。

技术：

WebGPU 暴露了一个 API，用于在图形处理单元上执行渲染和计算等操作。不需要熟悉其他图形 API，如 WebGL、Metal、Vulkan 或 Direct3D，但如果您有相关经验，您可能会注意到与 WebGPU 的许多相似之处，这可能有助于快速入门！

- https://en.wikipedia.org/wiki/WebGPU
- https://www.w3.org/TR/webgpu/
- https://codelabs.developers.google.com/your-first-webgpu-app

游戏/概念：

- https://www.veikkaus.fi/fi/nettikasino（芬兰语）
- https://www.veikkaus.fi/fi/nettiarvat（芬兰语）
- https://www.fennicagaming.com/
