# Verda (原 DataCrunch / Verda Cloud) — Junction 2026 合作方深度调研报告

## 1. 公司基本概况

- **公司全称**: Verda Cloud Oy (前身为 DataCrunch Oy)
- **公司总部**: 芬兰赫尔辛基 (Helsinki, Finland)，并在冰岛及北欧多地建有绿色超算与 AI 数据中心。
- **创立背景**:
  - Verda 由 **Ruben Bryon**（Founder & CEO）于 2020 年在芬兰赫尔辛基创立。
  - 公司源自赫尔辛基当地的机器学习技术社群（Machine Learning Meetups）。在当时，许多研究人员与初创开发者在训练大模型和复杂神经网络时，遭遇了主流公有云巨头高昂的 GPU 定价、漫长的配额审批以及复杂的配置流程。
  - 创始团队决定从底层服务器硬件与绿色数据中心自主搭建起步，为全球 AI 工程师提供“开箱即用、极速供给、价格透明且百分之百绿电”的高性能 GPU 云服务。
  - **品牌升级**: 2025 年底，随着业务从最初的裸金属 GPU 租赁扩展为涵盖算力集群、无服务器容器（Serverless Containers）和高速存储的全栈 AI 云平台，DataCrunch 正式升级重构为 **Verda**。“Verda”源自西班牙语的“真实”（Verdad/Verda）与世界语的“绿色”（Verda），象征着算力透明与绿色环保计算。
- **行业与技术地位**:
  - **欧洲新晋独角兽 (European AI Unicorn)**: Verda 完成由硅谷知名风投 Emergence Capital 领投的 B 轮融资，并获得芬兰国家工业投资机构 Tesi、Lifeline Ventures、byFounders、J12 Ventures 等顶级资本持续加持，企业估值突破 10 亿美元大关，成为欧洲发展最迅猛的 AI 算力基础设施独角兽之一。
  - **欧洲主权与绿色 AI 超级算力代表 (Sovereign Green AI Hyperscaler)**: 与依赖化石能源或高碳排放的传统数据中心不同，Verda 在芬兰和冰岛的数据中心实现 100% 水电与风电可再生能源供电，拥有极低的 PUE（电源使用效率），并将服务器运行产生的工业余热回流输入赫尔辛基及当地市政集中供暖管网（District Heating System），引领全球可持续计算标杆。
  - **第一梯队前沿硬件供给**: 深度拥抱 NVIDIA 最新一代计算架构，在欧洲率先规模化提供 NVIDIA H100、H200、L40S 以及最新的 Blackwell 系列（B200 / GB300）超算集群与高速 InfiniBand 互联服务。

---

## 2. 核心产品与业务体系

Verda 构建了专为 AI/ML 研发全生命周期打造的高性能云基础设施，贯穿从单卡轻量原型开发到千卡分布式大模型训练与低延迟推理。

### 2.1 主打算力产品
- **GPU 云虚拟机 (GPU Virtual Machines)**:
  - 提供开箱即用的秒级弹性 GPU 实例，预装最新版 Ubuntu、NVIDIA Drivers、CUDA、cuDNN 以及 Docker/NVIDIA Container Toolkit。
  - 支持按需随时启动、关机与销毁，按秒/按小时计费，无强制长期绑定合约。
- **裸金属服务器 (Bare Metal GPU Servers)**:
  - 面向极致性能追求者，提供物理机级别的独占硬件访问，彻底消除虚拟化损耗（Zero Hypervisor Overhead），支持直通 PCIe Gen5 与 NVLink 高速总线。
- **高吞吐 AI 超算集群 (Instant Multi-Node Clusters)**:
  - 搭载 NVIDIA Quantum-2 800Gb/s InfiniBand 互联架构，提供极低延迟与极高双向带宽，专门支撑超大规模预训练、多模态基础模型训练与分布式微调任务（如 DeepSpeed、Megatron-LM、FSDP）。
- **无服务器 AI 推理与容器 (Serverless AI Containers)**:
  - 允许开发者直接提交 Docker 镜像或模型权重，平台自动负责冷启动、自动扩缩容（Scale-to-Zero）与负载均衡，降低线上常驻成本。
- **高性能并行存储 (AI-Optimized NVMe Storage)**:
  - 针对计算机视觉与海量语料训练提供千万级 IOPS 的分布式 NVMe 共享文件系统，消除训练过程中的数据加载 I/O 瓶颈。

### 2.2 开发者平台与生态工具链
- **Verda CLI (`verda-cli`)**:
  - 基于 Go 语言编写的高性能官方命令行工具，支持跨平台（Linux、macOS、Windows Scoop）一键安装与运维：
    ```bash
    # 查看算力可用区与规格
    verda availability --location FIN-01

    # 脚本化一键创建 GPU 实例
    verda vm create --kind gpu --instance-type 1V100.6V \
        --location FIN-01 --os ubuntu-24.04-cuda-13.0-open-docker \
        --os-volume-size 100 --hostname junction-ai-node

    # 查看实时账户余额与运行扣费速率
    verda cost running
    verda cost balance
    ```
- **RESTful API & SDK**:
  - 提供规范清晰的 API，能够轻松与 CI/CD 流水线、Kubernetes 集群（K8s Operator）、Ray、Slurm 等工作流调度引擎对接。
- **Verda Cloud Console**:
  - 现代化 Web 控制面板，提供集群健康监控、实时 GPU 温度与利用率曲线、SSH 密钥管理及计费监控仪表盘。

---

## 3. Vision（愿景）与 Mission（使命）

### 3.1 官方使命 (Mission)
> *"To make access to cutting-edge GPU compute as easy and frictionless as possible without compromising user experience, data protection, regulatory compliance, or sustainability."*
> 
> （在绝不牺牲极致用户体验、数据安全隐私、合规性与环境可持续性的前提下，让获取全球最前沿的 GPU 算力变得前所未有的简单与零摩擦。）

### 3.2 官方愿景 (Vision)
> *"To build Europe's premier sovereign, full-stack, 100% green-energy AI hyperscaler — delivering high-performance, cost-effective, and environmentally responsible computing power to empower global builders and researchers to solve humanity's greatest challenges."*
> 
> （打造欧洲领先的自主、全栈且百分之百绿电驱动的 AI 超级算力云底座——以卓越性能、极高性价比和环境负责任的计算能力，赋能全球开发者与科研探索者攻克人类社会的重大命题。）

### 3.3 核心价值观 (Core Philosophy)
- **Sustainability First (绿电先行)**: 坚持北欧自然冷却与余热市政回收，拒绝高碳足迹的盲目算力扩张。
- **Developer Frictionless (开发者零摩擦)**: 摒除公有云繁琐冗余的官僚审批与隐藏账单，实现几分钟内拉起算力集群。
- **European Data Sovereignty (欧洲数据主权)**: 严格恪守欧盟 GDPR 与 AI Act 标准，为企业与研究者提供安全可信的主权算力保障。

---

## 4. 所属 Category（业务与技术分类）

- **Primary Category**: AI Infrastructure & GPU Cloud (人工智能基础设施与 GPU 云计算)
- **Secondary Categories**:
  - High-Performance Computing (HPC / 高性能计算集群)
  - Green Computing & Sustainable Data Centers (绿色计算与可持续数据中心)
  - Serverless AI Workload Orchestration (无服务器 AI 负载编排)
  - Cloud Platform-as-a-Service (PaaS / 算力云平台)

---

## 5. 在 Junction 黑客松中的角色与赛道挑战预测

### 5.1 黑客松合作方定位
Verda 是 Junction 2026 欧洲科技复兴（European Tech Renaissance）核心的 **AI Infrastructure 赛道出题方与算力底座支持方**。
在 48 小时的黑客松冲刺中，选手常常面临本地笔记本算力不足、大模型加载显存溢出（OOM）或者公有云部署极度耗时的困境。Verda 为参赛队伍提供免绑卡、大额度的绿色云 GPU 资源与 CLI 工具，让团队能够在短时间内完成开源大模型微调、多模态 Diffusion 生成或复杂强化学习训练。

### 5.2 赛道挑战预测与出题方向
1. **Green AI & Sustainable Inference Challenge (绿色高效 AI 与低碳推理挑战)**:
   - *课题方向*: 随着生成式 AI 能耗暴增，如何利用模型量化（AWQ、GGUF、FP8/FP4）、投机采样（Speculative Decoding）或智能动态批处理，最大化单位能耗下的 Token 吞吐量？
   - *解题思路*: 队伍可部署开源模型于 Verda 芬兰绿色节点，对比优化前后推理延迟、能耗估算与显存占用，构建“绿色 AI 指标监控与推理网关”。
2. **Serverless AI Agents & Real-Time Orchestration (无服务器 AI 智能体编排)**:
   - *课题方向*: 构建一套能够根据高并发请求秒级拉起专用微调模型（LoRA / Adapter）并在闲置时缩容至零的智能 Agent 后端。
   - *解题思路*: 借助 Verda CLI 与 API 编写动态编排控制器，实现从用户提示词到动态加载特定领域模型的完整自动化流水线。
3. **Physical & Scientific AI Supercomputing (物理与科学智能计算)**:
   - *课题方向*: 结合北欧在材料科学、流体力学模拟或气象预测方面的领先优势，在 Verda 多卡集群上加速开源物理科学基础模型（如 OpenFold、ClimaX）。
   - *解题思路*: 利用 Verda 极速 InfiniBand 多卡环境进行分布式仿真计算，并通过 WebUI 展示实时模拟成果。

### 5.3 参赛队伍实战建议与快速上手 (Quickstart)
- **步骤 1**: 在 Verda 控制台注册并通过 Junction 专属通道激活 Hackathon 专属算力 Coupon。
- **步骤 2**: 安装 `verda-cli`，添加公钥并配置自动化脚本：
  ```bash
  # 快速创建带 CUDA 驱动的推理实例
  verda vm create --kind gpu --instance-type 1H100.80GB \
      --location FIN-01 --hostname junction-ai-core
  ```
- **步骤 3**: 直接运行 Docker 容器加载 vLLM、TGI 或 Ollama，即可对外提供兼容 OpenAI 协议的高速推理端点：
  ```bash
  docker run --gpus all -v /data:/models -p 8000:8000 \
      vllm/vllm-openai:latest --model mistralai/Mistral-7B-Instruct-v0.3
  ```

---

## 6. 官网与关键资源链接

- **Verda 官方网站**: [https://verda.com](https://verda.com)
- **Verda 控制台 Console**: [https://console.verda.com](https://console.verda.com)
- **开发者文档中心 Docs**: [https://docs.verda.com](https://docs.verda.com)
- **Verda 官方 CLI 仓库**: [https://github.com/verda-cloud/verda-cli](https://github.com/verda-cloud/verda-cli)
- **API 参考文档**: [https://docs.verda.com/api-reference](https://docs.verda.com/api-reference)
- **实例规格与定价页面**: [https://verda.com/pricing](https://verda.com/pricing)
- **绿色可持续算力白皮书**: [https://verda.com/sustainability](https://verda.com/sustainability)
