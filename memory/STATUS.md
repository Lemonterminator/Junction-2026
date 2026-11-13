# Current status

Updated: 2026-11-14 (Europe/Helsinki). The source integration, shared memory, and
Docker preparation below are included in this revision. The user requested commit
and push on 14 November. Use `git status` and the remote branch to check the current
synchronization state; runtime validation remains pending as recorded below.

## Implemented

- Full Studio submodule at `external/physical-ai-studio`, pinned to
  `17714488fa9c7d098a056da83f7c220cf983957d` (`junction2026`).
- Original event guide, 70-public-repository inventory, and six pinned candidate
  README snapshots with provenance. Bilingual Silver guides/repository reviews,
  Gold creative options, and both conflicting rubrics are recorded.
- `AGENTS.md` / `CLAUDE.md` entry points and Git-tracked `memory/` with a handoff template.
- Root Compose: CPU Studio built with the upstream Dockerfile and named `libs`
  context; separate CPU Anomalib 2.7.0 tool container. Optional Intel GPU, NPU, and
  robot/camera overlays require explicit host device paths and numeric GIDs.
- Persistent per-Compose-project volumes, loopback HTTP publication, example secrets,
  local runtime/data ignores, and documented startup/remote access commands.
- Local `.env` initialized from the example without credentials. Individual secret
  configuration, accounts, and training-credit redemption remain manual.

## Validation evidence

- CPU plus tools Compose configuration parses successfully with Docker Compose v5.6.1.
- Combined Intel GPU/NPU/robot configuration parses with synthetic device paths/GIDs;
  those values test configuration only and are not host device discovery.
- Source archival script completed: 70 public repositories and seven pinned source documents.
- Final static validation passed: Node syntax, seven source hashes, 97 local document
  links, gitlink/source/example SHA alignment, whitespace checks, and rejection of an
  Intel overlay without required device variables. Local `.env` is ignored by Git.

## Runtime blocker

Docker CLI v29.9.2 is installed. Docker Desktop startup was attempted; its Linux
engine is unavailable, and `wsl --status` reports WSL is not installed. No images
were built, containers started, or HTTP health checks performed. WSL installation
and any required Windows restart remain outside this completed configuration work.
Anomalib's transitive dependencies are not fully locked or build-validated yet.

No Ubuntu deployment, device capture, GPU/NPU inference, demonstrations, policy
training, or arm motion occurred. The existing Ubuntu hardware audit is historical.
No closed-loop controller or shared camera service exists.

## Next concrete steps

1. Complete a working Docker Linux backend on Windows, or use the authorized Ubuntu
   host; follow `docs/infrastructure/DOCKER.md`. Build CPU Studio/Anomalib, check health,
   and record actual results here. Resolve dependency/build failures before claiming readiness.
2. Establish an integration deployment owner and device ownership. Inventory Linux
   device paths/groups before using overlays; verify actual OpenVINO devices and models.
3. Confirm the final judging rubric and kickoff rules with organizers.
4. Record clean demonstrations, establish the anomaly baseline, and implement a
   single-object automatic sorting loop before adding optional segmentation/fusion.
