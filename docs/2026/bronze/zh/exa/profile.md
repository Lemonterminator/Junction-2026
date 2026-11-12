# Exa (Exa Labs Inc.) — Junction 2026 合作方深度调研报告

> **合作方标签**：Tech & Challenge Partner | 为 AI 与大模型而生的神经向量网络搜索引擎  
> **官方网站**：[https://exa.ai](https://exa.ai)  
> **核心定位**：Neural Search & Web Intelligence for LLMs & AI Agents（重构 AI 时代万维网检索标准的神经语义搜索引擎 API）

---

## 1. 公司基本概况

- **公司全称**：Exa Labs Inc.（品牌名 **Exa**，前身为 **Metaphor Systems Inc.** / metaphor.systems）
- **官方域名**：[https://exa.ai](https://exa.ai)
- **总部地点**：美国加利福尼亚州 旧金山（San Francisco, California, USA）
- **创立背景与创始人**：
  - Exa 创立于 2021 年（2024 年 1 月正式完成全球品牌重塑，由 Metaphor 更名为 Exa）。
  - 两位联合创始人拥有卓越的学术与算法底蕴：
    - **Will Bryk (Co-founder & CEO)**：毕业于哈佛大学（Harvard University）计算机科学与物理学专业，曾在欧洲核子研究中心（CERN）从事粒子物理前沿数据分析，长期深耕于大规模分布式系统与前沿深度学习架构。
    - **Jeffrey Wang (Co-founder & CTO)**：毕业于哈佛大学计算机专业（与 Will Bryk 为大学室友），是资深的神经信息检索与自然语言处理专家。
  - 公司成立伊始便入选全球著名创业孵化器 **Y Combinator (YC S21)**，并在随后的几年里展现出爆发式的技术迭代与商业吸金能力。
- **痛点洞察与核心技术突破**：
  - **传统搜索的局限性**：谷歌（Google）、必应（Bing）等传统搜索引擎建立于 25 年前，完全基于**“关键词倒排索引 + PageRank 网页链接图谱 + 人类点击行为反馈”**构建。其目标是让“人类用几个简短词汇检索，然后在前 10 条蓝色链接中用眼睛挑选”。随着商业化发展，现代传统搜索结果早已被冗余的 SEO 作弊农场、联盟营销博客和弹窗广告严重污染。
  - **AI 时代的范式跃迁**：Exa 敏锐预见到：**未来互联网上发起搜索的主体 99% 以上将不再是人类，而是自主协同的 AI Agents、编码助手与大语言模型（LLMs）**。AI 在检索时往往输入整段自然语言提示词、具体的业务假设或长篇复杂逻辑（例如：“找到 5 家利用合成生物学制造替代蛋白且拥有公开技术博客的欧洲初创企业”）。传统基于关键词的搜索引擎在此类场景下命中率极低。
  - **神经链接预测（Neural Link Prediction）**：Exa 团队摒弃了传统的关键词匹配技术，从零训练了数十亿参数的神经嵌入变换器模型。该模型学习的是“整段文本与全网目标网页之间的深层语义和知识因果关联”。只要给定一段概念或提示，Exa 就能精准预测并检索出在互联网深处与该思想最契合的原始高价值网页。
- **行业地位与融资历程**：
  - Exa 是当今全球公认技术最领先、估值最高的 **AI 原生搜索引擎第一梯队独角兽**。
  - 累计融资规模突破 **3.5 亿美元**，得到了全球最奢华的科技投资阵营加持：
    - **Series C (2026 年 5 月)**：由硅谷教父级风投 **Andreessen Horowitz (a16z)** 独家领投 **2.5 亿美元**，公司投后估值正式突破 **22 亿美元**。
    - **Series B (2025 年 9 月)**：由传奇风投 **Benchmark** 领投 8500 万美元（估值 7 亿美元）。
    - **Series A 与早期**：由 **Lightspeed Venture Partners** 领投，**英伟达风投部门 (NVentures)**、Y Combinator 及众多硅谷 AI 领袖持续跟投。
  - 是当红 AI 编程神器 **Cursor**、最强大脑 AI 软件工程师 **Cognition (Devin)**、**HubSpot**、**OpenRouter** 等全球数百家头部 AI 应用在知识检索方面的底层供应商。

---

## 2. 核心产品与业务体系

Exa 为 AI 开发者提供了一个纯净、低延迟、深度语义理解的现代 API，将整个万维网当成向量数据库进行实时语义检索。

### 2.1 主打核心功能与 API 架构

#### 1. Neural Search（神经语义搜索 - `POST /search`）
- **长文本与假设性提示搜索**：
  - 支持直接将用户的问题、大模型的中间思考推理（Chain-of-Thought）或一整篇段落作为查询输入。
  - 区别于传统搜索引擎只能匹配死板的关键词，Exa 能够理解抽象概念、比喻、隐性需求与因果关系。
- **天然净化 SEO 垃圾内容**：
  - 模型直接根据知识密度与语义匹配度排序，天然免疫各类关键词堆砌与垃圾营销站，优先返回高水准的技术文档、学术论文、个人独立博客、研报及 GitHub 仓库。
- **Search Type 智能模式**：
  - `neural`：启用全神经语义嵌入搜索，擅长理解复杂概念与探索性发现。
  - `keyword`：精准子串与特定标识符匹配（如特定函数名、错误码）。
  - `auto`：根据用户 Query 的长短和特征自适应动态路由至最优检索模型。

#### 2. Find Similar（相似链接挖掘 - `POST /findSimilar`）
- **以网构网的语义拓扑**：
  - 开发者只需提供一个高价值目标 URL（例如一篇顶级的系统架构论文、或者一家极具创新模式的企业官网），Exa 能够秒级在全网检索出在**技术内涵、商业模式或文体风格上高度相似**的候选页面。
  - 在竞品调查、学术文献溯源和关联知识图谱构建中具有无可替代的威力。

#### 3. Contents & Highlights Extraction（智能内容提取与高亮 - `POST /contents`）
- **端到端纯净正文返回**：
  - 支持在搜索时同步返回目标页面的纯净文本（Text）或解析后的 Markdown。
- **智能高亮与上下文压缩（Highlights）**：
  - 针对长达数万字的冗长文章，Exa 内置的摘要算法可直接抽取出与当前查询**相关性最高的核心段落与句子（Key Highlights）**。
  - 彻底解决了 RAG 系统中将海量无关内容强行灌入 LLM 导致“迷失在中间（Lost in the Middle）”和 Token 巨额消耗的行业顽疾。

#### 4. 多层级性能体验（Search Tiers）
- **Exa Fast**：专为对话机器人与亚秒级实时交互设计的极速检索通道，耗时压制在数百毫秒内。
- **Exa Auto**：平衡速度与知识广度的自适应标准通道。
- **Exa Deep**：专为深度研究（Deep Research）Agent 设计的多阶段循环检索管道，深度挖掘隐秘的边缘长尾知识。

#### 5. 丰富的多维过滤矩阵
- **域名精准白名单 / 黑名单 (`includeDomains` / `excludeDomains`)**：支持仅在权威站点（如 `github.com`, `arxiv.org`, `nature.com`）中限定检索。
- **时间范围过滤 (`startPublishedDate` / `endPublishedDate`)**：实时追踪过去 24 小时或特定时间段发生的技术突破。
- **类别过滤器 (`category`)**：支持快速指定检索类型，包括：`company`（企业主页）、`research paper`（科研论文）、`news`（权威新闻）、`pdf`（专业文档）、`github`（开源代码）、`tweet`（社交讨论）等。

---

## 3. Vision（愿景）与 Mission（使命）

### 3.1 官方使命 (Mission)
> **"To organize the world's knowledge for AI."**  
> （为人工智能时代组织全世界的知识。）  
> 就像 Google 在 PC 互联网时代“组织全球信息，供人类索阅”一样，Exa 的使命是在智能体时代，从底层神经表示出发重新梳理并组织万维网上的所有动态知识，让每一个大语言模型和自主智能体都能随时随地调用人类沉淀的最高水准智慧。

### 3.2 官方愿景 (Vision)
> **"To build the cognitive search fabric for the agentic future — where AI agents search the web exponentially more than humans, unlocking profound truths and accelerating human discovery."**  
> （构建智能体时代的认知检索基础设施网格——在这个 AI 检索量呈指数级超越人类的未来，Exa 致力于消除算法垃圾与信息茧房，为智能系统提供深邃、真实且无偏见的基础知识支撑，全面加速人类的科学发现与产业进化。）

---

## 4. 所属 Category（业务与技术分类）

- **Primary Category**：
  - **Neural Search & AI Search Engine**（神经向量搜索与 AI 原生搜索引擎）
- **Secondary Categories**：
  - **AI Knowledge Retrieval & RAG Infrastructure**（大模型知识检索与 RAG 底座）
  - **Agentic Web Discovery Platform**（面向自主智能体的网络发现平台）
  - **Semantic Information Retrieval (IR) API**（语义信息检索 API 服务）
  - **Developer Tools for AI Applications**（AI 开发者生态基础设施）

---

## 5. 在 Junction 黑客松中的角色与赛道挑战预测

### 5.1 黑客松角色定位
在 Junction 2026 黑客松中，Exa 是参赛团队打造**“高智商、强推理、零幻觉 AI 应用”的知识引擎（The Knowledge Engine）**。

在 48 小时的黑客松极限开发中，普通队伍构建的聊天机器人往往因为缺乏外部实时信息而胡说八道（Hallucination），或者使用常规搜索 API 搜出充斥着 SEO 废话的垃圾页面。接入 Exa 的队伍可以让自己的智能体瞬间拥有**“全网最高清知识雷达”**，无论是深挖前沿科研论文、精准诊断诡异代码报错、还是全网搜寻细分商业情报，Exa 都能输出直接可用的黄金上下文。

### 5.2 赛道挑战方向预测

1. **Autonomous Deep-Research & Fact-Checking Agent（自主深度研究与事实核查智能体）**：
   - **挑战题目**：构建一个对标或超越 OpenAI Deep Research / Perplexity Pro 的全自动研报撰写智能体。
   - **技术亮点**：智能体接收一个复杂前沿课题（如“对比 EU AI Act 对开源小模型的具体合规要求”），利用 Exa 的 `category="pdf"` 和 `startPublishedDate` 递归下潜检索权威法律文书与顶级律所研报，利用 `highlights` 提取核心条款并完成多方交叉事实核查，自动输出带精确引用角标的专业报告。

2. **Intelligent Competitor Landscape & Ecosystem Graph（智能商业生态与隐形竞对图谱）**：
   - **挑战题目**：输入任意初创项目或 GitHub 开源库，全自动发掘其全球技术生态与竞对矩阵。
   - **技术亮点**：深度结合 Exa 的 `findSimilar` API 和 `category="company"` 过滤器，快速探索与其技术栈、算法思想或应用场景高度相近的隐形玩家，并自动构建交互式知识图谱。

3. **Autonomous Senior Coding Agent & Debugging Copilot（深核代码助手与极端排障 Agent）**：
   - **挑战题目**：打造一个能够解决冷门技术栈踩坑与复杂底层死锁的 AI 工程师。
   - **技术亮点**：限定 `includeDomains=["github.com", "stackoverflow.com"]`，利用 Exa 的神经搜索精准定位包含相同错误日志（Error Stack）的极少被搜索引擎收录的 GitHub Issue 讨论与源码 commit，秒级给出权威修复补丁。

### 5.3 参赛者极速上手代码示例 (Quickstart)

```python
"""
Junction 2026: 3分钟使用 Exa 官方 SDK 构建神经语义搜索与高质量知识召回
安装官方库: pip install exa-py
"""
import os
from exa_py import Exa

# 初始化 Exa 客户端
EXA_API_KEY = os.environ.get("EXA_API_KEY", "your_exa_api_key_here")
exa = Exa(api_key=EXA_API_KEY)

def autonomous_research_query(prompt: str):
    print(f"[*] 正在为智能体执行神经向量语义搜索: '{prompt}'...")
    
    # 结合语义搜索 + 目标网页纯净正文 + 关键高亮自动提取
    response = exa.search_and_contents(
        prompt,
        type="neural",                      # 使用 Exa 自研神经搜索模型
        num_results=3,                      # 召回最高质量的前 3 个深度来源
        text=True,                          # 返回清洗后的纯文本
        highlights={
            "num_sentences": 3,             # 每个来源提取最贴合查询的核心高亮句子
            "highlights_per_url": 2
        },
        use_autoprompt=True                 # 自动优化为最适合检索的提示词表达
    )
    
    print("\n[+] 检索完成！高价值上下文预览:")
    for idx, result in enumerate(response.results, 1):
        print(f"\n--- [来源 {idx}] ---")
        print(f"标题: {result.title}")
        print(f"链接: {result.url}")
        print(f"发布时间: {result.published_date}")
        print("核心高亮段落:")
        for highlight in result.highlights:
            print(f" > \"{highlight}\"")

def discover_similar_innovations(url: str):
    print(f"\n[*] 正在基于 URL 进行全网相似创新挖掘: {url}...")
    response = exa.find_similar(
        url=url,
        num_results=3,
        category="company"                   # 仅过滤公司/商业产品主页
    )
    for res in response.results:
        print(f"相似产品: {res.title} ({res.url})")

if __name__ == "__main__":
    # 示例 1: 复杂科研与商业概念搜索 (传统关键词搜索引擎难以准确回答)
    autonomous_research_query("Here are the best recent open-source models for local agentic tool use and function calling")
    
    # 示例 2: 基于指定优秀产品寻找全球相似产品
    discover_similar_innovations("https://modal.com")
```

---

## 6. 官网与关键资源链接

- **官方网站**：[https://exa.ai](https://exa.ai)
- **开发者文档中心**：[https://docs.exa.ai](https://docs.exa.ai)
- **官方 API 控制台 (Dashboard)**：[https://dashboard.exa.ai](https://dashboard.exa.ai)
- **API 参考规范与 Playground**：[https://docs.exa.ai/reference](https://docs.exa.ai/reference)
- **官方 Python SDK GitHub**：[https://github.com/exa-labs/exa-py](https://github.com/exa-labs/exa-py)
- **官方 JS/TS SDK GitHub**：[https://github.com/exa-labs/exa-js](https://github.com/exa-labs/exa-js)
- **官方技术博客与前沿研究**：[https://exa.ai/blog](https://exa.ai/blog)
