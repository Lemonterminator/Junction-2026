# MariaDB (MariaDB Foundation & MariaDB plc) — Junction 2026 合作方深度调研报告

## 1. 公司/机构基本概况

- **机构全称**: 
  - **MariaDB Foundation**（非营利开源基金会，代码中立托管方）
  - **MariaDB plc / Corporation**（商业实体，现由 K1 Investment Management 控股支持）
- **机构总部**: 芬兰埃斯波 (Espoo, Finland) 与 美国加州红木城 (Redwood City, CA, USA)
- **创立背景**:
  - MariaDB 诞生于 2009 年，由世界级开源传奇领袖、**MySQL 原作者 Michael "Monty" Widenius**（MariaDB 基金会 CTO）率领原 MySQL 核心研发班底创办。
  - **诞生使命与历史转折**: 2009 年，甲骨文公司（Oracle）收购拥有 MySQL 的 Sun Microsystems，全球开源界对 MySQL 的独立性与开源前途产生了极大担忧。为了捍卫自由软件信仰与全球技术主权，Monty 与核心工程师共同将 MySQL 源代码进行分支克隆（Fork），并以其小女儿 Maria 的名字将其命名为 **MariaDB**，誓言“永远开源、永远自由”。
  - 2012 年，为了确保 MariaDB 代码库永不被单一商业公司私有化控制，团队正式成立了独立的非营利组织 **MariaDB Foundation**，作为代码所有权的永久中立信托人。
- **行业地位与全球影响**:
  - 全球排名前列的最顶尖开源关系型数据库系统之一（DB-Engines 榜单长期稳居全球顶级开源数据库之列）。
  - **全球 Linux 生态默认基准**: 几乎所有主流的企业级与开源 Linux 发行版（包括 Red Hat Enterprise Linux, CentOS, Debian, Ubuntu, Fedora, openSUSE, Arch Linux）均已将默认的关系型数据库由 MySQL 切换为 MariaDB。
  - **全球关键企业基础设施**: 承载着包括维基百科（Wikimedia / Wikipedia 全库事务底座）、Google、ServiceNow、欧洲核子研究中心（CERN）、全球顶级金融与电信巨头等数以亿计的生产事务负载。

---

## 2. 核心产品与业务体系

MariaDB 提供兼具强一致性事务（ACID）、超大规模高并发能力与现代化 AI 向量检索的原生通用数据库系统。

### 2.1 主打核心技术与产品矩阵

1. **MariaDB Server (社区版与企业版)**:
   - 基于 GPLv2 开源协议发布的全球级关系型数据库，完全原生兼容 MySQL 协议与驱动语法。
   - 具备业内首屈一指的多存储引擎可拔插架构（Pluggable Storage Engine Architecture）：
     - **InnoDB**: 高性能高并发 ACID 事务处理引擎。
     - **ColumnStore**: 极速列式分析（OLAP）引擎，专为海量实时大数据分析设计。
     - **Spider**: 分布式透明分库分表引擎，支持 PB 级水平横向切片。
     - **Aria / MyRocks / S3 Engine**: 分别满足缓存、极高写入压缩及冷数据分层归档场景。

2. **MariaDB Vector（原生 AI 向量搜索引擎，全新里程碑）**:
   - 从 **MariaDB 11.4 / 11.8 LTS** 起，MariaDB 正式将**高维向量处理能力深度内置于数据库核心引擎**中，彻底颠覆了以往需要额外安装第三方不稳定插件的痛点。
   - **原生数据类型与海量维度**: 原生支持 `VECTOR(N)` 类型，支持高达 **16,383 维度**的高维向量存储（完全适配 OpenAI `text-embedding-3`、BGE、Cohere 等前沿大模型）。
   - **自研改良版 HNSW (Hierarchical Navigable Small World) 索引**: 实现毫秒级 Approximate Nearest Neighbor (ANN) 近似最近邻语义检索。
   - **原生内置向量距离函数**:
     - `VEC_DISTANCE_EUCLIDEAN()`: 欧几里得距离。
     - `VEC_DISTANCE_COSINE()`: 余弦相似度。
     - `VEC_FromText()`: 快速文本向量转换接口。
   - **单语句事务-向量混合查询 (Unified Transactional + Semantic SQL)**:
     ```sql
     SELECT id, title, author, price 
     FROM tech_library 
     WHERE category = 'AI' AND price < 50.0 
     ORDER BY VEC_DISTANCE_COSINE(embedding, VEC_FromText('[0.021, -0.432, ...]')) 
     LIMIT 5;
     ```

3. **MariaDB MaxScale（企业级智能数据库中枢代理）**:
   - 具备智能查询路由、透明读写分离、毫秒级自动故障自愈（Failover）、SQL 注入动态拦截与防火墙防御功能。

4. **AI 与现代开发框架生态集成**:
   - 深度兼容 **Spring AI**（官方 `spring-ai-starter-vector-store-mariadb`）、**LangChain**、**LlamaIndex** 以及主流 Python/Go/Node.js ORM（SQLAlchemy, Prisma, GORM 等）。

---

## 3. Vision（愿景）与 Mission（使命）

### 3.1 官方声明

- **MariaDB Foundation 使命 (Mission)**:
  > *"The MariaDB Foundation guarantees continuity and open collaboration in the MariaDB ecosystem. It is the custodian of the code and the steward of the open-source community, ensuring that MariaDB Server remains free, accessible, and community-driven forever under GPLv2."*
  > （MariaDB 基金会保障 MariaDB 生态系统的长久持续性与开放协作。作为核心代码的守护者和开源社区的引领者，确保 MariaDB Server 在 GPLv2 协议下永远自由、开放、普惠且由社区共同驱动。）

- **MariaDB Vector / AI 战略愿景 (Vision - The Bridge That Matters)**:
  > *"MariaDB's vision is to be the vital bridge that really matters between real-world operational transactional data and modern AI systems. Instead of juggling fragmented standalone vector databases, developers should be empowered to build GenAI and RAG applications directly within the robust, ACID-compliant relational database they already know and trust."*
  > （MariaDB 的愿景是成为真实业务运营事务数据与现代 AI 系统之间最关键的坚固桥梁。开发者无需在割裂孤立的单一专用向量数据库之间疲于奔命，而是能够直接在早已熟知且值得信赖的高可用、强一致性关系型数据库中，优雅构建生成式 AI 与 RAG 智能应用。）

### 3.2 核心技术哲学与开源价值观
- **通用融合优于碎片化孤岛 (General-Purpose Beats Special-Purpose)**: 单独维护一套向量数据库会带来数据同步延迟、双重权限管理及运维复杂度爆炸。统一的 SQL + 向量引擎才是企业级智能的终局。
- **杜绝商业锁定与技术霸权 (Open Source Sovereignty)**: 坚持 GPLv2 自由软件基因，赋予开发者完全的数据所有权与基础设施自主掌控力。

---

## 4. 所属 Category（业务与技术分类）

- **Primary Category**: Open-Source Relational & Vector Database System (开源关系型与原生向量数据库系统)
- **Secondary Categories**:
  - AI Retrieval-Augmented Generation (RAG) & Semantic Search Infrastructure (AI 检索增强生成与语义检索基建)
  - Database-as-a-Service (DBaaS / 数据库即服务) & Cloud-Native Storage (云原生存储)
  - Mission-Critical Transactional Engine (高并发强一致性核心事务引擎)
  - Open Source Community Governance & Tech Foundation (开源治理与技术基金会)

---

## 5. 在 Junction 黑客松中的角色与赛道挑战预测

### 5.1 黑客松角色定位
MariaDB 是 Junction（欧洲顶级黑客松，起源并常设于芬兰阿尔托大学）不可撼动的**“欧洲开源技术旗帜与统一数据基座（European Open Source Legend & Unified AI Bedrock）”**。
在黑客松的 48 小时极限原型开发中，选手们构建 RAG、推荐系统或智能体工作流时，往往会面临“关系型业务数据存在 PostgreSQL/MySQL 中，而文本向量却被迫存入 Pinecone/Chroma，导致复杂的多表关联与权限验证无法协同”的巨大痛点。MariaDB 带着其全新的 **MariaDB Vector**，为参赛者提供了开箱即用的“事务 + 语义一站式数据库底座”。

### 5.2 赛道挑战预测与题目方向

#### 赛道预测 1: Enterprise RAG with Fine-Grained ACID Access Control (具备强一致性与企业级权限控制的混合 RAG 系统)
- **挑战概述**: 专用向量数据库几乎无法支持复杂的 SQL 联表权限过滤。如何利用 MariaDB 11.4+ 原生 Vector 能力，构建一个能够满足欧洲严格合规要求（如 GDPR、多租户行级安全隔离）的企业级智能文档中枢？在单次 SQL 查询中同时完成语义相似度搜索与组织架构层级权限判定。
- **技术要点**:
  - 利用 MariaDB `VECTOR` 字段结合 InnoDB 多表外键关联与事务锁。
  - 构建支持百毫秒级响应的防幻觉企业问答机器人。

#### 赛道预测 2: Autonomous Agent Long-Term Episodic Memory (基于原生 MariaDB Vector 的智能体长期因果记忆中枢)
- **挑战概述**: 现有的 AI 智能体（AI Agents）受限于 Context Window，缺乏持久化记忆与时间序列推理能力。参赛团队需要设计一个高效的智能体记忆系统：将智能体的对话历史、工具调用记录、环境反馈同时存储为“结构化时间戳属性”与“向量语义切片”，实现精准的遗忘衰减与情境唤醒。
- **技术要点**:
  - 利用 MariaDB SQL 对时间戳、置信度等指标进行数值过滤，结合 `VEC_DISTANCE_COSINE()` 进行语义唤醒。
  - 打造高可靠的 Multi-Agent Swarm 状态协同共享库。

#### 赛道预测 3: European Open Tech Sovereignty & Edge AI (欧洲开源主权：离线可用的本地智能数据库)
- **挑战概述**: 在医疗、工业制造或高安全性场景下，企业要求数据严禁出境或脱网运行。参赛团队结合轻量级开源本地小模型（如 Llama 3 / Mistral / Gemma）与本地轻量级部署的 MariaDB Server，打造一个 100% 本地闭环运行的高性能智能工单分析或边缘预警系统。

### 5.3 参赛者快速实战代码示例 (MariaDB Vector Quickstart)

```sql
-- 1. 创建包含高维向量与业务属性的统一数据表 (以 1536 维 text-embedding-3-small 为例)
CREATE TABLE knowledge_nodes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id INT NOT NULL,
    access_level VARCHAR(20) NOT NULL,
    document_title VARCHAR(255) NOT NULL,
    chunk_content TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    VECTOR INDEX hnsw_idx (embedding)
) ENGINE=InnoDB;

-- 2. 插入业务数据与向量 (通过客户端直接绑定)
INSERT INTO knowledge_nodes (tenant_id, access_level, document_title, chunk_content, embedding)
VALUES (101, 'Confidential', 'Junction 2026 Rulebook', 'MariaDB provides native vector capabilities...', VEC_FromText('[0.012, -0.045, ...]'));

-- 3. 单次 SQL 兼具权限过滤与语义相似度召回
SELECT id, document_title, chunk_content, 
       VEC_DISTANCE_COSINE(embedding, VEC_FromText('[:query_vector]')) AS distance
FROM knowledge_nodes
WHERE tenant_id = 101 AND access_level IN ('Public', 'Confidential')
ORDER BY distance ASC
LIMIT 5;
```

---

## 6. 官网与关键资源链接

- **MariaDB Foundation 官方主页**: [https://mariadb.org](https://mariadb.org)
- **MariaDB 商业与企业服务主页**: [https://mariadb.com](https://mariadb.com)
- **MariaDB Vector 官方技术文档**: [https://mariadb.org/documentation/](https://mariadb.org/documentation/)
- **MariaDB 官方 GitHub 仓库**: [https://github.com/MariaDB/server](https://github.com/MariaDB/server)
- **Spring AI MariaDB 向量存储集成指南**: [Spring AI - MariaDB Vector Store](https://docs.spring.io/spring-ai/reference/api/vectordbs/mariadb.html)
- **MariaDB 官方开发者交流社区与 Zulip 讨论区**: [https://mariadb.org/community/](https://mariadb.org/community/)
