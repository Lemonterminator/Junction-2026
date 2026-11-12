# Cala (cala.ai) — Junction 2026 课题提供方深度调研报告

## 1. 公司基本概况

- **公司全名**: Cala (Cala AI)
- **官方主页**: [https://cala.ai](https://cala.ai)
- **公司总部**: 欧洲 / 跨国远程 (European / US Distributed)
- **行业地位**: 面向自主智能体（AI Agents）与大语言模型（LLMs）的结构化知识层与验证数据基础设施（The Knowledge Layer & Verified Data Infrastructure for AI Agents and LLMs）。
- **核心定位**: *"The preferred data layer for agents. At Cala we process data so you don't have to. Skip the data and start building."*（专为智能体打造的优质数据层。在 Cala，我们预先处理海量公开数据，让你免去数据清洗与格式转换之苦，直接专注构建智能体。）
- **与易混淆实体的辨析说明**:
  > [!IMPORTANT]
  > **实体对齐关键勘误 (Ground Truth Verified)**:
  > 本课题提供方为 **Cala AI (`https://cala.ai`)**，是智能体数据基础设施提供商；**绝非**同名的服装设计与供应链 SaaS `ca.la` (现已更名升级为 Mercer)。官方在 Junction 2026 官网 Partners 展区直接指向 `https://cala.ai`。

---

## 2. 核心产品与业务体系

Cala 专注于解决现代自主智能体（Autonomous Agents）在检索网络信息时面临的核心痛点：传统网页搜索返回大量充满噪声、广告、时效错乱且缺乏格式约束的非结构化散文（HTML/Prose），导致 Agent 在推理时频繁出现上下文幻觉、字段解析崩溃以及昂贵的多余 Token 开销。

### 2.1 结构化世界知识底座 (The World's Knowledge, Structured)
- **预先验证与事实化 (Verified Facts vs. Web Chaos)**: Cala 预先对全球公开权威信息进行实体抽取、清洗、对齐与时效性标注，使 Agent 能够直接查询确定性的实体与事实，而非在混乱的网页中无序摸索。
- **超高 Token 效率 (Token Efficiency)**: 结构化强类型数据（Typed Results）比冗长的网页自然语言减少 70%~85% 的无用 Token 消耗，直接降低大模型 API 账单。
- **全链路溯源保障 (Data Provenance & Lineage)**: 每个数据属性（Property）均具备精确的时间戳、有效区间（Validity）与不可篡改的权威信源出处（Source Citations），彻底消除 Agent 决策幻觉。

### 2.2 覆盖核心行业与权威数据源 (One Endpoint, Any Industry)
- **金融、风控与监管合规 (Finance, Compliance & KYC)**:
  - **SEC / EDGAR 权威监管文件**: 10-K（年报）、10-Q（季报）、8-K（重大事件）、Proxy Statements 及内部人持股变动（Form 4）。
  - **市场行情与流动性数据**: 交易所行情、CBOE、FINRA TRACE 债券成交数据、美联储经济数据库（FRED）。
  - **信用与主权评级**: Moody's、S&P、Fitch 发行人公开评级，FDIC 银行评级与美联储压力测试报告。
  - **全球制裁与观察清单**: OFAC SDN、欧盟综合制裁清单、联合国安理会制裁名单、FinCEN 洗钱警示。
  - **公司商业登记与最终受益人（UBO）**: 英国 Companies House、美国各州州务卿备案与全球穿透式实际控制人图谱。
  - **司法诉讼记录**: 美国联邦法院 PACER、CourtListener 及多国法院公开判决。
  - **央行与宏观监管**: 美联储 H 系列报告、欧洲央行（ECB）统计数据仓库、国际清算银行（BIS）银行统计。
  - **政治公众人物（PEP）**: 联合国、欧盟及各国官方公报权威名录。
- **医疗健康 (Healthcare)**: 药物数据库、临床指南、公共卫生监管准则与科研论文元数据。
- **法律与法务 (Legal)**: 法条变更、监管框架、合同范本基准与合规条款对比。
- **人力资源 (HR)** 与 **农业科技 (Agro)** 等跨行业领域拓展。

### 2.3 AI 原生集成支持
- **原生 Model Context Protocol (MCP) 端点**:
  - 官方提供高可用 MCP 服务器（`https://api.cala.ai/mcp/`），支持通过标准 `mcp.json` 零代码直接挂载至 Cursor、Claude Code、Antigravity、Claude Desktop、n8n、LangChain、OpenClaw 等任意主流 Agent 运行时环境。
  ```json
  {
    "mcpServers": {
      "cala": {
        "url": "https://api.cala.ai/mcp/",
        "headers": {
          "X-API-KEY": "YOUR_CALA_API_KEY"
        }
      }
    }
  }
  ```
- **细粒度链式属性查询 API**:
  - 支持按实体、时间范围、财务科目等细粒度属性进行确定性检索（例如：`Acme.Financials.NetIncomeLoss.From=2016.To=2026`）。

---

## 3. Vision（愿景）与 Mission（使命）

### Vision (愿景)
*"To build the global knowledge layer for the agentic era — where every AI agent queries verified truth instead of digital noise."*  
（打造智能体时代的全球可信知识层，终结大模型网络搜索的噪声与幻觉时代，让智能体在确定、严密、高密度的结构化知识网络中协同决策。）

### Mission (使命)
*"At Cala we process data so you don't have to. Skip the data and start building."*  
（在 Cala，我们预先处理数据，让你无需重复造轮子。彻底抹平大模型获取结构化世界知识的工程摩擦，消除脆弱的数据抓取与清洗管道，为全球 AI 开发者提供开箱即用、具备全生命周期溯源的知识底座。）

---

## 4. 所属 Category

- **AI Agent Data Infrastructure** (智能体数据基础设施)
- **Structured Knowledge Graph & Truth Engine** (结构化知识图谱与事实引擎)
- **Model Context Protocol (MCP) Fact Provider** (MCP 协议事实提供商)
- **Regulatory, Financial & Firmographics Intelligence** (监管合规与金融商业情报)

---

## 5. 在 Junction 黑客松中的角色与赛道挑战预测

### 对应赛道
- **Agentic AI Track** (自主智能体赛道)
- **FinTech & Corporate Due-Diligence Track** (金融科技与企业尽调赛道)
- **Data & Real-Time Intelligence Track** (数据与实时洞察赛道)

### 黑客松痛点破解
黑客松参赛者在构建 Agent 时，往往耗费大量时间在 BeautifulSoup、Playwright 爬虫与正则表达式上，且现场网络经常触发反爬风控。通过挂载 Cala MCP 服务器，参赛队伍可以**在 1 分钟内为 Agent 赋予跨越十年历史金融底稿、全球制裁名单与公司穿透股权的超级专家视角**。

### 挑战课题预测
1. **自主企业尽调与制裁穿透审计 Agent (Autonomous KYC & Deep Due-Diligence Agent)**:
   - 利用 Cala 的 SEC 文件、UBO 最终受益人穿透与 OFAC/欧盟制裁名单 MCP 工具，Agent 接收目标公司名称后，自主构建股权树、审查关联交易并输出符合机构级审计标准的合规备忘录。
2. **高频宏观经济与产业链传导因果分析智能体 (Macro Supply-Chain Shock Navigator)**:
   - 结合 Cala 的央行报告、FRED 宏观指标与大宗商品/供应链数据，对突发地缘政治或利率决议事件进行分钟级的影响传导推演。
3. **基于 MCP 协议的多 Agent 协同投研智库 (Swarm Equity Analyst)**:
   - 部署由行业研究员、法务审查员和财务建模员组成的 Agent Swarm，所有 Agent 共享 Cala MCP 数据管道，实现秒级高精度跨年度财务对比与异常估值预警。

---

## 6. 官网与关键资源链接

- **官方网站**: [https://cala.ai](https://cala.ai)
- **开发者文档**: [https://cala.ai/docs](https://cala.ai/docs)
- **MCP 服务器连接端点**: `https://api.cala.ai/mcp/`
- **在线体验与 Playground**: [https://cala.ai/try](https://cala.ai/try)
