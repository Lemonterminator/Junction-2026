> **2026-11-13 更新 / Audit update:** AI Infrastructure 与 Agentic AI 已按 2021–2025 年重新核验，采用 21 列且明确标注未知、奖项级别及证据来源。原两赛道版本已移至 [Bronze 存档](../bronze/winner_mateirals/legacy_gold_unaudited_2026-11-13/)，其中含错误及未证实内容。以下旧版 31 项总数、两个赛道的项目数及“全面验证”表述不再适用于这两个更新后的文件；其他赛道尚未在本次工作中核查。

# Hack Junction Historical Challenges (2024–2025) — Gold Layer
# 历史赛题与获奖案例金层总览（2024–2025 双语基准数据集）

本目录包含历届项目的金层基准资料。AI Infrastructure 与 Agentic AI 已按证据重新核验；其他赛道仍保留旧版内容，尚未在本次工作中复核。

---

## 📁 目录结构导航 (Directory Navigation)

```
docs/past/gold/
├── en/                          # 全英文版 (Full English Edition)
│   ├── agentic_ai.md            # 6 audited cases, including a runner-up and adjacent challenges
│   ├── ai_infrastructure.md     # 3 audited related cases
│   ├── data.md                  # 8 Verified Winner Landmark Projects
│   ├── fintech.md               # 4 Verified Winner Landmark Projects
│   ├── hardware.md              # 6 audited cases, including a runner-up and adjacent challenges
│   └── healthcare.md            # 6 Verified Winner Landmark Projects
│
└── zh/                          # 全中文版 (Full Chinese Edition)
    ├── agentic_ai.md            # 6 个已核查案例（含亚军和相邻赛题）
    ├── ai_infrastructure.md     # 3 个已核查相关案例
    ├── data.md                  # 8 个已验证的里程碑式获奖项目
    ├── fintech.md               # 4 个已验证的里程碑式获奖项目
    ├── hardware.md              # 6 个已核查案例（含亚军和相邻赛题）
    └── healthcare.md            # 6 个已验证的里程碑式获奖项目
```

---

## 📊 标准 21 列 Schema 规范 (21-Column Benchmark Schema)

每个赛道均采用严格统一的 21 列基准元数据定义：

1. `event_id`: 赛事唯一标识（如 `junction-2024`, `junction-2025`）
2. `event_name`: 赛事标准名称
3. `year`: 举办年份（视赛道范围而定）
4. `organizer`: 主办方与出题企业
5. `challenge`: 赛题原名
6. `category`: 归一化派别（`Agentic AI` / `AI Infrastructure` / `Data` / `FinTech` / `Hardware` / `Healthcare`）
7. `judging_criteria`: 评审团核心标准
8. `project_id`: 项目唯一 Slug 标识
9. `project_name`: 获奖项目名称
10. `award`: 获奖荣誉与奖金
11. `solution_summary`: 解决方案摘要与核心创新
12. `tech_stack`: 完整工程技术栈
13. `architecture`: 端到端数据流与系统架构
14. `key_decisions`: 48 小时极限黑客松核心权衡决策
15. `metrics_and_baseline`: 量化指标对比与基准突破
16. `demo_highlights`: 现场演示爆点与高光时刻
17. `team_background`: 获胜团队与核心成员背景
18. `winning_hypothesis`: 评审团青睐原因与得胜假设
19. `reusable_lessons`: 可复用方法论与启发
20. `source_urls`: 领英动态、GitHub 开源仓库与官方报道链接
21. `evidence_level`: 事实可信度级别（L1_Verified / L2_Documented）
