# 2026-11-13 — Source integration, shared memory, and Docker preparation

- Author: Codex.
- Branch: main; local uncommitted work. No commit or push performed.
- Scope: user requested the whole Studio repository, ecosystem research capture,
  shared AI memory, and Docker preparation.

## Changes

- Added the pinned `junction2026` submodule and archived upstream guide, six candidate
  READMEs, and 70-repository public inventory. Source hashes and revisions are in
  `docs/2026/bronze/intel_open_edge_platform/manifest.json`.
- Added bilingual guide/repository reviews and creative options. Preserved the PDF
  rubric and appended the different GitHub rubric, without choosing final authority.
- Added shared memory and AI entry points. Added CPU Studio, isolated CPU Anomalib,
  explicit Linux device overlays, local configuration examples, and setup documentation.
- Submodule initially cloned shallow main only; explicitly fetched `junction2026`,
  checked it out, registered the gitlink, and set its remote branch tracking.

## Evidence and limits

Compose parses the CPU/tools and combined Intel/robot variants. Hardware variants
were checked with synthetic values only. Docker Linux engine startup failed and
WSL is absent, so build/runtime/health/device checks remain pending. Source capture
completed without account tokens. No cloud training, Ubuntu deployment, camera use,
or arm motion was started.

Final static checks passed: seven source hashes, 97 local document links, submodule
gitlink/source/example revision alignment, Node syntax, Git whitespace checks, and
missing-device-variable rejection. The local `.env` is ignored by Git.

## Next action

Read `memory/STATUS.md`; establish a working Linux Docker backend, build CPU images,
check Studio health and Anomalib imports, then update status with observed evidence.
Do not report the environment as running until those checks actually pass.
