# Junction 2026

Hack Junction 2026 challenge research, Intel Physical AI development environment, shared AI memory, and historical challenge archive (2017–2025).

## Intel Physical AI development

- [Full Physical AI Studio source](external/physical-ai-studio/) — Git submodule,
  `junction2026`, pinned at `17714488fa9c7d098a056da83f7c220cf983957d`.
- [Docker setup](docs/infrastructure/DOCKER.md) — CPU Studio, isolated Anomalib,
  and explicit Linux Intel/robot device overlays. Runtime validation is pending.
- [Shared AI memory](memory/README.md) — start with [project context](memory/PROJECT.md),
  [status](memory/STATUS.md), and [decisions](memory/DECISIONS.md). AI entry points:
  [AGENTS.md](AGENTS.md) and [CLAUDE.md](CLAUDE.md).
- [Upstream guide / 中文](docs/2026/silver/zh/intel_physical_ai_studio_guide.md) /
  [English](docs/2026/silver/en/intel_physical_ai_studio_guide.md).
- [Repository review / 中文](docs/2026/silver/zh/open_edge_platform_repositories.md) /
  [English](docs/2026/silver/en/open_edge_platform_repositories.md).
- [Creative options / 中文](docs/2026/gold/zh/intel_physical_ai_creativity_options.md) /
  [English](docs/2026/gold/en/intel_physical_ai_creativity_options.md).

Initialize the upstream checkout with `git submodule update --init --recursive`
(or clone this repository with `--recurse-submodules`). The GitHub event guide and
PDF contain different judging rubrics; both are retained pending organizer confirmation.

---

## 📂 Project Structure

- **`docs/2026/`**:
  - **`bronze/`**: Raw intelligence, multi-modal scraper outputs, and official LinkedIn announcements.
  - **`silver/`**: Cleaned partner profiles and challenge alignments (bilingual English / Chinese), plus archived challenge briefs and page-by-page transcripts.
  - **`gold/`**: Source-backed strategic insights and challenge synthesis (bilingual English / Chinese).
- **`docs/past/`**:
  - **`bronze/`**: Historical challenge catalog, bilingual translation mappings, and deep-dive winner retrospective reports (`winner_mateirals/`).
  - **`silver/`**: Comprehensive historical archive covering 147 challenges across 2017–2025 remapped into track categories (AI Infrastructure, Agentic AI, Data, Hardware, Healthcare, FinTech) in both English and Chinese editions.
  - **`gold/`**: Production-grade benchmark datasets for verified 2024–2025 landmark winners across the 6 tracks with strict 21-column schema (English & Chinese editions).

## Junction 2026 Challenge Briefs

Updated 2026-11-13. The Intel brief has been reviewed against all 15 rendered PDF pages, including image-based requirements and the 100-point judging table. Source facts, analysis recommendations, and unresolved event details are separated in Gold.

| Challenge | Source archive (Silver) | Analysis (Gold) |
| :--- | :--- | :--- |
| Intel Physical AI Challenge | [Original PDF](docs/2026/silver/Intel_Physical%20AI%20Hackathon.pdf) / [English transcript](docs/2026/silver/intel_physical_ai_hackathon.md) | [中文](docs/2026/gold/zh/intel_physical_ai_challenge.md) / [English](docs/2026/gold/en/intel_physical_ai_challenge.md) |

- [2026 Silver index](docs/2026/silver/README.md)
- [2026 Gold index](docs/2026/gold/README.md)

