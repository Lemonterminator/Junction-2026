# [2025 Winner Case Study] n8n — AI Consensus Engine

## 1. 元数据概览 (Metadata)
- **对应赛题文件**: `2025_n8n_Agentic_AI_with_the_flexibility_of_code_and_easyness_of.md`
- **出题方 (Partner)**: n8n
- **赛题名称**: Agentic AI with the flexibility of code and easyness of no-code
- **获奖项目**: **AI Consensus Engine: Solving Hallucinations in Multi-Agent Workflows**
- **获胜者**: **Mychel Garzon Trujillo** ([LinkedIn Profile](https://www.linkedin.com/in/mychel-garzon-trujillo/))
- **获奖领英动态**: [Post on LinkedIn](https://lnkd.in/p/dqntQJw6)
- **获奖荣誉**: Junction 2025 n8n Tech Challenge Winner (第一名)

---

## 2. 方案与技术架构
- **核心解决痛点**: 工业级多智能体工作流中的 LLM 幻觉与单点故障。
- **技术实现**: 在 n8n 中编排 OpenAI、Anthropic、Google Gemini 与 Groq 多个异构大模型，搭建基于 Jaccard + Cosine 相似度的统计共识引擎，只有通过共识阈值的决策才会向下游系统分发。
