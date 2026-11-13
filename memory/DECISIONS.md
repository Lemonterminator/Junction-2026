# Decision log

## 2026-11-13 — Git-tracked shared memory

Adopt `AGENTS.md` as the Codex entry point and `CLAUDE.md` as the Claude entry point.
Both lead to the same `memory/` documents. Reason: portable, reviewable team context
without sharing AI accounts or relying on private per-session memory. New decisions
must include date, rationale, status, and evidence when factual claims are involved.

## 2026-11-13 — Upstream source integration

Use a submodule at `external/physical-ai-studio`, branch `junction2026`, pinned to
`17714488fa9c7d098a056da83f7c220cf983957d`. This implements the user's request to bring
the whole repository into this project. Keep integration code outside the submodule.
Updating the pin is an intentional source update, followed by updating the manifest,
Compose defaults, `.env.example`, and rerunning relevant checks.

## 2026-11-13 — Container boundaries

Build Studio using its pinned upstream Dockerfile and named `libs` build context.
Provide a CPU default and opt-in Intel GPU, NPU, and robot overlays. Anomalib 2.7.0
(PDF version) gets a separate CPU container because its PyTorch environment must
stay isolated. Local XPU anomaly training remains a separate future validation.
Compose projects scope persistent storage per developer; an integration deployment
still needs a named owner. No privileged device access is enabled by default.

## 2026-11-13 — Source conflict handling

Retain both scoring rubrics and attribute them separately. Do not assume the GitHub
rubric supersedes the PDF. Ask organizers for the final rubric before score-based
prioritization. Additional repositories are optional opportunities; Instant Learn
and performance profiling are recommendations, not adopted contest requirements.

## 2026-11-14 — Python package and workstation runtime

`src/defect_sorter` is a uv project (`pyproject.toml`, `uv.lock`, Python 3.12) with a light default install (NumPy, OpenCV) and opt-in extras `camera` (pyrealsense2, Linux) and `anomaly` (Anomalib 2.7.0 + OpenVINO + CPU torch). Reason: tests run on any laptop while the workstation runs the same code natively with direct D415 and GPU/NPU access. Python 3.12 is what was installed and verified on the workstation (pyrealsense2, Anomalib, OpenVINO); the Docker Anomalib image uses 3.13 and remains an alternative, not yet aligned. Status: adopted on branch `feat/defect-sorter-perception`.

## 2026-11-14 — Perception: depth for objects, colour for bowls

The table background stays cluttered, so objects are found by height above a fitted table plane (D415 depth) rather than by appearance, and shallow bowls by colour. The D415 colour sensor uses a fixed 4600 K white balance because auto white balance shifted every hue under venue lighting. Evidence: live run on 2026-11-13/14 (see handoff). Status: adopted.
