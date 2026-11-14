# Junction 2026 Silver Layer (清洗层与赛题对齐数据库)

本目录为 Junction 2026 挑战合作方与赛题信息清洗层（Silver Layer），基于 Bronze 原始层、LinkedIn 官方贴文抓取结果及用户提供的赛题文件构建。具体事实以各文件标注的来源为准。

## 📁 文件索引 (Files Index)
- [🇨🇳 中文主表：challenge_partners.md](./challenge_partners.md)
- [🇨🇳 中文子目录归档：zh/challenge_partners.md](./zh/challenge_partners.md)
- [🇺🇸 英文版主表：en/challenge_partners.md](./en/challenge_partners.md)
- [📂 原始贴文 Bronze 归档：../bronze/linkedin_posts_raw.md](../bronze/linkedin_posts_raw.md)

## 赛题文件归档 / Challenge Briefs

| 赛题 | 原始文件 | 清洗转录 | Gold 分析 |
| :--- | :--- | :--- | :--- |
| Intel Physical AI Challenge | [PDF](./Intel_Physical%20AI%20Hackathon.pdf) | [英文逐页 Markdown](./intel_physical_ai_hackathon.md) | [中文](../gold/zh/intel_physical_ai_challenge.md) / [English](../gold/en/intel_physical_ai_challenge.md) |

Intel 文件于 2026-11-13 归档，共 15 页。Markdown 保留原文页序及完整评分表，图片内正文经渲染核对后转录；图片以文字说明表达，视觉细节以 PDF 为准。不可见的幻灯片模板提示与重复装饰页脚省略。二维码未解码，其目标地址不作推断。

本次已用该 PDF 更新中英文合作方表中的 Intel 与 Ignite Next 赛题描述。其他合作方仍沿用原有来源，未在本次任务中重新核实。

## 参赛者手册 / Participant Guidebook

[Junction 2026 Participant Guidebook (PDF, 24 页 / pages)](./Junction_2026_Participant_Guidebook.pdf)：日程、提交要求、互评与规则。关键规则摘要见 / Key rules: [memory/PROJECT.md](../../../memory/PROJECT.md#event-rules-participant-guidebook)。

## Physical AI Studio 与组织仓库 / Upstream and ecosystem

| 资料 / Material | 中文 | English | 来源 / Source |
| --- | --- | --- | --- |
| Junction 2026 操作指南 | [整理](zh/intel_physical_ai_studio_guide.md) | [Guide](en/intel_physical_ai_studio_guide.md) | [原文快照](../bronze/intel_open_edge_platform/JUNCTION2026.md) |
| Open Edge Platform 仓库筛选 | [清单](zh/open_edge_platform_repositories.md) | [Review](en/open_edge_platform_repositories.md) | [70 个公开仓库快照](../bronze/intel_open_edge_platform/repositories.json) / [来源清单](../bronze/intel_open_edge_platform/manifest.json) |

GitHub 指南和 PDF 的评分不同，保留两版并待组织者确认。仓库推荐是分析；未声明算法或硬件已验证。
The rubrics conflict and remain unresolved. Repository recommendations are analysis, not runtime validation.
