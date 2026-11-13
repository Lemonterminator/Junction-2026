# Junction 2026 working instructions

This repository holds Intel Physical AI Challenge research, shared project memory,
and an integration environment. Reply in the user's language (normally Chinese).

## Read at the start of a task

1. `memory/PROJECT.md`: confirmed facts, sources, and unresolved questions.
2. `memory/STATUS.md`: current implementation and validation status.
3. `memory/DECISIONS.md`: durable choices and their rationale.
4. Read relevant entries in `memory/handoffs/` when continuing someone's work.

These are Git-tracked team memory. Other chats and private AI memories are not
automatically synchronized. Check the current files and working tree before acting.

## Repository boundaries

- Keep the Bronze (source snapshots), Silver (source-backed summaries), and Gold
  (analysis and recommendations) distinction. Maintain English/Chinese pairs when
  changing the 2026 Silver/Gold material.
- `external/physical-ai-studio` is an upstream submodule on `junction2026`, pinned
  by the parent repository's gitlink. Prefer integration code in `src/`; coordinate
  any intentional upstream changes and record commit changes in the source manifest.
- Preserve both PDF and GitHub judging rubrics until organizers resolve the conflict.
  Attribute claims to their actual source and date; a newer file is not proof of authority.
- Dependencies and models supporting OpenVINO do not establish NPU support or
  successful deployment. Report configuration, build, runtime, and hardware checks separately.

## Working agreements

- Inspect `git status` first and preserve other people's changes. Use explicit file
  paths when staging. Do not commit or push unless requested.
- Keep credentials, private SSH keys, account caches, datasets, model weights, and
  runtime logs out of Git and shared memory. Each developer uses their own account,
  secrets file, clone, Compose project name, and storage volumes.
- The robot/camera workstation is shared. Coordinate device ownership and live
  demo changes; never start arm motion, take over a camera, replace drivers, or
  reboot the workstation as an incidental setup step.
- Run checks proportionate to the actual change. Do not start paid Modal jobs or
  claim inference works on the basis of a successful Compose parse.
- Update `memory/STATUS.md` for meaningful changes. Record durable decisions in
  `memory/DECISIONS.md`. Use a separate dated file in `memory/handoffs/` for a handoff,
  with changes, evidence, open questions, and concrete next steps. Label proposals
  and unverified observations instead of promoting them to confirmed facts.

## Environment entry points

See `docs/infrastructure/DOCKER.md` and `docs/infrastructure/AI_SHARED_MEMORY.md`.
Default Docker environment: CPU Studio at `http://127.0.0.1:7860`; isolated Anomalib
workspace through the optional `tools` profile. Intel GPU/NPU and robot access use
explicit Linux-only Compose overlays with inventoried paths and numeric group IDs.
