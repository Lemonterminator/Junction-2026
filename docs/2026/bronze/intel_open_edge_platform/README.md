# Intel / Open Edge Platform source archive

Archived on 2026-11-13; exact UTC retrieval times, source URLs, revisions, and
SHA-256 hashes are in [manifest.json](manifest.json). Source text retains its
upstream authorship and license; archiving does not change its license.

- [JUNCTION2026.md](JUNCTION2026.md): copied from the pinned Studio submodule.
- [repositories.json](repositories.json): all 70 public organization repositories
  returned by GitHub Search at retrieval time, sorted by stars. Includes coverage,
  default branches, archived status, licenses when provided, and star snapshot.
- `repositories/<name>/README.md`: commit-pinned READMEs for the six reviewed
  candidates: Instant Learn, Manufacturing AI Suite, Edge AI Sizing Tool,
  DL Streamer, Scenescape, and Robotics AI Suite.

The organizer encouragement is user-supplied chat context and is attributed as
such in the manifest. It was not independently obtained from an official page.

Refresh intentionally from the root with `node scripts/archive_open_edge_platform.mjs`
(Node 22+, Git, public network access). The script fetches public data without
credentials; GitHub API limits can prevent a refresh. Review the diff before
committing. Upstream Studio source updates require a separate submodule pin update.

Silver: [中文指南](../../silver/zh/intel_physical_ai_studio_guide.md) /
[English guide](../../silver/en/intel_physical_ai_studio_guide.md),
[中文仓库清单](../../silver/zh/open_edge_platform_repositories.md) /
[English repository review](../../silver/en/open_edge_platform_repositories.md).
