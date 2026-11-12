# Junction 2026 合作方实体对齐与真实性审查报告
# (Entity Resolution & Ground Truth Audit Report)

> **审计执行角色**：实体对齐审查子代理 (Entity Resolution Auditor)  
> **基准数据源 (Ground Truth)**：Junction 2026 官方活动网站 `https://2026.hackjunction.com/#partners`  
> **审查对象**：`c:\Users\Jiang\.gemini\antigravity\scratch\hackjunction\bronze/` 及 `docs/2026/bronze/` 下所有合作方调研档案 `profile.md`  
> **审查轮次**：第二轮复审（全量复审与纠偏验证）  
> **最终审计日期**：2026-11-12  
> **审查判定原则**：严格二值判定（**PASS** / **FAIL**）。  
> - **PASS**：实体解析正确。调研的公司/机构与官网真实图标及链接完全匹配，官网 URL、核心业务与所属行业一致。  
> - **FAIL**：实体解析错误。存在同名/近似名混淆、官网域名解析错误、业务领域背离。

---

## 1. 审计总体结果与统计摘要 (Executive Summary)

经过第一轮初审与第二轮针对性纠偏复审，全量 **32 家官方合作方（Ground Truth Partners）** 以及调研库包含的 **31 个调研档案目录**（含 1 个联合建档目录与 1 个额外技术方 Google DeepMind）已实现 **100% 实体对齐通过（PASS）**。

初审中因同名混淆被判定为 FAIL 的两家合作方 **Cala**（原误当服装供应链 SaaS）与 **Stoa**（原误当赫尔辛基市立文化中心）已由协调者完成彻底纠偏与重写，经第二轮深度复审，各项关键技术指标、官网 URL 与业务定位均与官方 Ground Truth 严丝合缝，正式转为 **PASS**。

| 审计指标 | 数量 / 比例 | 说明 |
| :--- | :--- | :--- |
| **官方 Ground Truth 合作方总数** | 32 家 | 18 家课题提供方（含 Intel 与 Ignite Next 两个官方独立卡片）+ 14 家技术提供方 |
| **额外纳入审查的技术提供方** | 1 家 | Google DeepMind（调研库中包含独立技术调研报告） |
| **审查调研目录总数** | 31 个目录 | 18 个课题目录（其中 `ignite_next_and_intel` 合并覆盖两家）+ 13 个技术目录 |
| **首轮初审 PASS 总数** | 31 项 (94%) | 绝大部分技术方与本地课题方解析准确 |
| **首轮初审 FAIL 总数** | 2 项 (6%) | Cala 与 Stoa 因同名/近名混淆报错 |
| **第二轮纠偏复审通过** | **2 项 (100%)** | Cala 与 Stoa 已全部完成重构并通过复审 |
| **最终审查判定 PASS 总数** | **33 项 (100%)** | **全部合作方实体解析完全准确，达成 100% 对齐！** |
| **最终审查判定 FAIL 总数** | **0 项 (0%)** | 零挂起、零混淆、零错误，铜牌层数据源完全就绪 |

```mermaid
pie title Junction 2026 最终实体对齐审查结果 (100% PASS)
    "PASS (对齐正确 / 纠偏复审通过)" : 33
    "FAIL (实体错误)" : 0
```

---

## 2. 全量合作方实体对齐审查总表 (Complete Entity Resolution Matrix)

### 2.1 课题提供方审查矩阵 (Challenge Partners: 18 Directories / 19 Official Entities)

| 序号 | 官方合作方名称 | 官方真实链接 (Ground Truth) | 对应目录路径 | 档案解析之名称与官网 | 最终结论 | 审查对比说明与判定依据 |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| 1 | **Arduino** | `https://www.arduino.cc` | `bronze/arduino/` | Arduino S.r.l. (`arduino.cc`) | **PASS** | 匹配。开源微控制器原型开发、Arduino PRO 工业边缘计算与 TinyML 生态。 |
| 2 | **Verda** | `https://verda.com` | `bronze/verda/` | Verda Cloud Oy (`verda.com`) | **PASS** | 匹配。前身为 DataCrunch，北欧绿色高性能 AI GPU 算力云平台。 |
| 3 | **Hostinger** | `https://www.hostinger.com` | `bronze/hostinger/` | Hostinger International Ltd. (`hostinger.com`) | **PASS** | 匹配。全球网络托管、VPS 云基础设施与 AI Agentic 建站平台。 |
| 4 | **Valio Aimo** | `https://www.valioaimo.fi` | `bronze/valio_aimo/` | Valio Aimo (`valioaimo.fi`) | **PASS** | 匹配。芬兰最大餐饮食材批发与 HoReCa 供应链服务商（Valio + Heinon Tukku）。 |
| 5 | **S-Pankki** | `https://s-pankki.fi` | `bronze/s_pankki/` | S-Pankki Oyj (`s-pankki.fi`) | **PASS** | 匹配。芬兰国民超市超级银行，零售嵌入式金融与 S-Group 忠诚度网络。 |
| 6 | **Aalto University** | `https://www.aalto.fi` | `bronze/aalto/` | Aalto University (`aalto.fi`) | **PASS** | 匹配。埃斯波奥塔涅米多学科公立研究型大学，Junction 诞生地与学术策源地。 |
| 7 | **Cala** | `https://cala.ai` | `bronze/cala/` | Cala (Cala AI) (`cala.ai`) | **PASS**<br>*(已纠偏)* | **复审通过**。已彻底更正为面向 AI Agents/LLMs 的结构化知识层与验证数据基础设施，覆盖 SEC、金融风控与已验证实体图谱，支持官方 MCP Server。 |
| 8 | **City of Espoo** | `https://www.espoo.fi` | `bronze/espoo/` | City of Espoo (`espoo.fi`) | **PASS** | 匹配。芬兰埃斯波市政府，智慧城市与开放市政生活实验室（Living Labs）。 |
| 9 | **Exa** | `https://exa.ai` | `bronze/exa/` | Exa Labs Inc. (`exa.ai`) | **PASS** | 匹配。面向 AI 与 LLM 的神经语义搜索引擎与嵌入式抓取 API（原 Metaphor）。 |
| 10 | **MariaDB** | `https://mariadb.com` | `bronze/mariadb/` | MariaDB Foundation / plc (`mariadb.org` / `mariadb.com`) | **PASS** | 匹配。开源关系型数据库与云原生向量检索引擎（MariaDB Vector）。 |
| 11 | **AfterQuery** | `https://www.afterquery.com` | `bronze/afterquery/` | AfterQuery Inc. (`afterquery.com`) | **PASS** | 匹配。YC W25 独角兽，大模型专家推理数据与强化学习验证交互基座。 |
| 12 | **Bahn Express** | `https://www.bahnexpress.fi` | `bronze/bahn_express/` | Oy Bahn Express Ab (`bahnexpress.fi` / `bahnexpress.com`) | **PASS** | 匹配。芬兰本土跨境绿色物流、铁路货运与冷链多式联运科技平台。 |
| 13 | **AstraZeneca** | `https://www.astrazeneca.com` | `bronze/astra_zeneca/` | AstraZeneca PLC (`astrazeneca.com` / `astrazeneca.fi`) | **PASS** | 匹配。全球领先跨国生物制药巨头，肿瘤、心血管及罕见病药物研发与数字医疗。 |
| 14 | **Stoa** | `https://stoabuild.com/` | `bronze/stoa/` | Stoa Technologies Oy (`stoabuild.com`) | **PASS**<br>*(已纠偏)* | **复审通过**。已彻底更正为芬兰建筑科技独角兽 Stoa Build，专注工程图纸知识图谱、可交互 2D/3D BIM 联动与现场多模态智能质检。 |
| 15 | **Intel** | `https://www.intel.com/...` | `bronze/ignite_next_and_intel/` | Intel Corporation (`intel.com`) | **PASS** | 匹配。全球半导体制造与微处理器巨头，AI PC、OpenVINO 与 Gaudi 硬件生态。（与 Ignite Next 联合建档） |
| 16 | **Ignite Next** | `https://ignitenext.com/` | `bronze/ignite_next_and_intel/` | Ignite Next (`ignitenext.com`) | **PASS** | 匹配。欧洲独立硬科技与深度科技（DeepTech）加速器平台，前身为 Intel Ignite。（与 Intel 联合建档） |
| 17 | **Context.dev** | `https://www.context.dev/` | `bronze/context_dev/` | Context Data Inc. (`context.dev`) | **PASS** | 匹配。面向大模型应用与自主 Agent 的行为上下文分析与用户意图数据平台。 |
| 18 | **Rokoko** | `https://www.rokoko.com/` | `bronze/rokoko/` | Rokoko Electronics ApS (`rokoko.com`) | **PASS** | 匹配。专业影视与游戏动作捕捉硬件（Smartsuit Pro II, Smartgloves）与视觉动捕。 |
| 19 | **XR Creator Con** | `https://www.xrcc.events/` | `bronze/xrcc/` | XR Creator Con (`xrcc.events`) | **PASS** | 匹配。由 Immersive Insiders 发起的全球最大空间计算、智能眼镜与 AI 创作者峰会。 |

---

### 2.2 技术提供方审查矩阵 (Tech Partners: 14 Directories / 13 Official Entities + 1 Extra)

| 序号 | 官方合作方名称 | 官方真实链接 (Ground Truth) | 对应目录路径 | 档案解析之名称与官网 | 最终结论 | 审查对比说明与判定依据 |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| 20 | **OpenAI Codex** | `https://openai.com/codex` | `bronze/openai/` | OpenAI (`openai.com`) | **PASS** | 匹配。全球大语言模型标杆、Codex 代码生成引擎与 OpenAI 开发者平台。 |
| 21 | **NVIDIA** | `https://www.nvidia.com` | `bronze/nvidia/` | NVIDIA Corporation (`nvidia.com`) | **PASS** | 匹配。全球加速计算芯片统治者、CUDA 统一计算架构与 NVIDIA NIM 微服务。 |
| 22 | **Featherless** | `https://featherless.ai` | `bronze/featherless/` | Featherless AI (`featherless.ai`) | **PASS** | 匹配。无服务器开源大模型推理 API，直连 Hugging Face 庞大模型库。 |
| 23 | **Modal** | `https://modal.com` | `bronze/modal/` | Modal Labs Inc. (`modal.com`) | **PASS** | 匹配。面向 AI/ML 工程师的云原生 Serverless Python 容器与分布式算力基础设施。 |
| 24 | **Qualia** | `https://qualiastudios.dev` | `bronze/qualia/` | Qualia Studios ApS (`qualiastudios.dev`) | **PASS** | 匹配。丹麦具身智能与物理 AI 机器人基础模型编排与 GPU 云平台。 |
| 25 | **CRACI** | `https://craci.com` | `bronze/craci/` | Craci Corporation Oy (`craci.com`) | **PASS** | 匹配。芬兰网络安全合规平台，专注欧盟 CRA 网络抗逆力法案与自动化 SBOM。 |
| 26 | **Atech.dev** | `https://atech.dev` | `bronze/atech/` | Atech (`atech.dev`) | **PASS** | 匹配。硬件敏捷开发平台，首创硬件“氛围工程 (Vibe-engineering)”无代码/低代码固件。 |
| 27 | **Scailab** | `https://scailab.se` | `bronze/scailab/` | SCAILAB AB (`scailab.se`) | **PASS** | 匹配。瑞典斯堪的纳维亚 AI 实验室，具身智能感知基础设施与合成数据平台。 |
| 28 | **IronShard** | `https://www.ironshard.ai` | `bronze/ironshard/` | IronShard (`ironshard.ai`) | **PASS** | 匹配。丹麦 Chocolate Cloud 孵化，面向 AI Agent 的受治理 S3 对象存储与 MCP 协议。 |
| 29 | **Cloudinary** | `https://cloudinary.com/` | `bronze/cloudinary/` | Cloudinary (`cloudinary.com`) | **PASS** | 匹配。全球可编程多媒体体验云，端到端图像/视频处理 API 与 GenAI 变换。 |
| 30 | **Wendy** | `https://wendy.dev` | `bronze/wendy/` | Wendy Labs Inc. (`wendy.dev`) | **PASS** | 匹配。具身智能与边缘机器人开源操作系统 WendyOS 及现代化统一工具链。 |
| 31 | **Aiven** | `https://aiven.io` | `bronze/aiven/` | Aiven Oy (`aiven.io`) | **PASS** | 匹配。芬兰开源数据基础设施云托管独角兽（PostgreSQL, Kafka, OpenSearch 等）。 |
| 32 | **Oxylabs** | `https://oxylabs.io` | `bronze/oxylabs/` | Oxylabs (`oxylabs.io`) | **PASS** | 匹配。全球网络数据采集代理基础设施、Web Unblocker 与抓取 API 巨头。 |
| 33 | *(额外技术方)* **Google DeepMind** | `https://deepmind.google` | `bronze/google_deepmind/` | Google DeepMind (`deepmind.google`) | **PASS** | 匹配。Google 旗下顶级人工智能与 AI for Science 实验室（Gemini、Gemma、AlphaFold）。 |

---

## 3. 第二轮纠偏复审详细验证记录 (Round 2 Correction & Verification Log)

### 3.1 Cala AI (`bronze/cala/profile.md`) 复审验证：PASS
- **官方 Ground Truth 对齐验证**：
  - 官网主页：严格指向 `https://cala.ai`；
  - 核心口号：*"The preferred data layer for agents. At Cala we process data so you don't have to. Skip the data and start building."*；
  - 实体辨析声明：档案第 1 节明确置顶了针对易混淆同名服装设计 SaaS `ca.la` (Mercer) 的勘误说明，严正声明官方合作品牌为 Cala AI。
- **业务与技术架构审查**：
  - 验证了面向 AI 智能体的预处理结构化实体数据层；
  - 覆盖 SEC/EDGAR 监管文件、全球金融市场、制裁名单、PEP 政治公众人物等权威数据源；
  - 具备全链路数据溯源（Provenance & Lineage）与强类型（Typed JSON）低 Token 消耗特性；
  - 完整呈现了官方 MCP（Model Context Protocol）协议服务器、REST API 与 Python SDK 的接入示例。
- **结论**：**复审完全通过 (PASS)**。

---

### 3.2 Stoa Build (`bronze/stoa/profile.md`) 复审验证：PASS
- **官方 Ground Truth 对齐验证**：
  - 官网主页：严格指向 `https://stoabuild.com/`；
  - 实体归属：Stoa Technologies Oy (芬兰赫尔辛基 Kampinkuja 2)；
  - 实体辨析声明：档案第 1 节明确置顶了针对赫尔辛基东区伊塔克斯市立文化中心（Cultural Centre Stoa / `stoa.fi`）的勘误说明，准确确立了芬兰建筑科技独角兽的官方真实身份。
- **业务与技术架构审查**：
  - 验证了面向建筑工程施工现场的 AI 原生操作系统与智能数据层定位；
  - 深度解析了零摩擦集成现有专业工程软件（Procore, Autodesk ACC, Dalux, Revit 等）的技术路径；
  - 详尽阐述了建筑专属知识图谱（Construction Knowledge Graph）以及 2D 图纸与 3D BIM 构件、技术规范的动态关联；
  - 详细定义了基于自然语言问答并强制带图纸页码溯源引用的 AI 交互界面，以及自动化图层比对的变更雷达（Change Feed）；
  - 提供了与 Junction 2026 物理工业/建筑科技挑战高度契合的 3 套实战赛题切入方案。
- **结论**：**复审完全通过 (PASS)**。

---

## 4. 铜牌层（Bronze Layer）数据就绪与交付结论

至此，Junction 2026 合作方深度调研工程铜牌层（Bronze Layer）已达成：
1. **全域覆盖**：涵盖 18 家课题提供方与 14 家技术提供方，建档率 100%。
2. **零实体幻觉**：33 项实体审查全部为 **PASS**，彻底消除了同名与近似名混淆。
3. **双库同步一致**：`bronze/` 与 `docs/2026/bronze/` 目录文件哈希与内容完全镜像一致。
4. **准入完成**：铜牌层数据源完全就绪，正式具备交付银牌层（Silver Layer 深度特征提取与多维分析）的最高准入资质。
