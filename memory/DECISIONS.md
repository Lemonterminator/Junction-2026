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
