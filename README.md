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

## Code: `defect_sorter`

Python package for the Intel Physical AI Challenge pipeline (PERCEIVE → DETECT → REASON → ACT → OPTIMIZE). Agent and contributor rules (TDD, uv, tabs, hardware safety) are in [AGENTS.md](AGENTS.md).

| Module | Role |
| :--- | :--- |
| `src/defect_sorter/geometry.py` | Camera intrinsics, deprojection, RANSAC table plane, height above table |
| `src/defect_sorter/scene.py` | Bowls by colour, objects by height, object-in-bowl relation (`detect_scene`) |
| `src/defect_sorter/realsense.py` | D415 aligned colour + depth with fixed white balance |
| `src/defect_sorter/live_demo.py` | Live MJPEG debug page for the top camera |
| `src/defect_sorter/markers.py` | Printed ArUco marker set, print sheet (`sorter-marker-sheet`), marker pose detection |
| `src/defect_sorter/alignment.py` | Depth-refined marker poses and drift against a saved reference |
| `src/defect_sorter/alignment_page.py` | Live alignment page: camera tilt, markers, drift (`sorter-alignment`) |
| `src/defect_sorter/anomaly_smoke.py` | Anomalib → OpenVINO export and CPU/GPU/NPU latency check |

```bash
uv sync                                   # light install: tests run anywhere
uv run pytest -q && uv run ruff check . && uv run ruff format --check .

# on the Intel workstation (Ubuntu, Python 3.12)
uv sync --extra camera --extra anomaly
uv run sorter-live-demo --host <tailscale-ip> --port 8090
uv run sorter-anomalib-smoke --workdir data/smoke
```

Only one process can open the D415: stop the live demo before Physical AI Studio previews, records or runs a policy. Workstation setup is tracked in [docs/infrastructure/SETUP_STATUS.md](docs/infrastructure/SETUP_STATUS.md).

## Local policy training and digital twin

[Local training guide](docs/infrastructure/TRAINING.md) provides ACT imitation-learning,
SmolVLA expert fine-tuning, and experimental Pi0.5 LoRA recipes for a separate CUDA
environment. Plan generation and synthetic metadata/task tests run in the light
project environment; no real dataset, model training, GPU-memory fit, or exported
policy has been validated by these tests.

```bash
uv run python -m defect_sorter.training plan \
  --recipe configs/training/smolvla_expert.toml \
  --dataset configs/training/dataset.example.toml --run-name smolvla-first
```

The [SO-101 digital twin study](docs/research/SO101_DIGITAL_TWIN.md) describes model
sources, simulator choices, calibration, state synchronization, and validation gates.

The [Physical AI execution plan](docs/plans/PHYSICAL_AI_EXECUTION_PLAN.md) turns the
[historical hardware winner study](docs/research/PAST_HARDWARE_WINNERS_REUSE.md) into
staged work packages: calibration and Studio recording, Studio-managed training on
the local 5090, defect-conditioned SmolVLA, Intel Runtime deployment, clutter tests,
and power/temperature measurements. Twin playback is capped at G3a after the core
deliverables pass; [Gemini/RL research](docs/plans/DEFERRED_GEMINI_RL_EXPERIMENTS.md)
is deferred. The plan includes dependencies, acceptance gates and scope reductions.

## Junction 2026 Challenge Briefs

Updated 2026-11-13. The Intel brief has been reviewed against all 15 rendered PDF pages, including image-based requirements and the 100-point judging table. Source facts, analysis recommendations, and unresolved event details are separated in Gold.

| Challenge | Source archive (Silver) | Analysis (Gold) |
| :--- | :--- | :--- |
| Intel Physical AI Challenge | [Original PDF](docs/2026/silver/Intel_Physical%20AI%20Hackathon.pdf) / [English transcript](docs/2026/silver/intel_physical_ai_hackathon.md) | [中文](docs/2026/gold/zh/intel_physical_ai_challenge.md) / [English](docs/2026/gold/en/intel_physical_ai_challenge.md) |

- [2026 Silver index](docs/2026/silver/README.md)
- [2026 Gold index](docs/2026/gold/README.md)

