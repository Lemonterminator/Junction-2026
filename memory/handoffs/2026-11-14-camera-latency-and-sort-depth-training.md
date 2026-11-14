# 2026-11-14 — Camera latency fix and sort-depth-v2 training

- Author: linan
- Branch and commit: `claude/project-thread-kxonxt` (this pull request); the preview fix itself is already merged
  (pull request #13).
- Scope: Studio camera lag on the Intel workstation, the new `sort-depth-v2` dataset, SmolVLA training on the
  RTX 5090 PC ("Monster AI", Tailscale 100.86.110.62). Written for teammates and for the next agent taking over.

## Changes

- `docker/studio-preview.override.yaml` + `docker/studio-patches/` (merged in #13): Studio's live session preview is
  capped at 10 Hz and JPEG quality 60; `STUDIO_PREVIEW_SKIP` can drop cameras. The workstation's Studio container was
  recreated with it (compose files: Studio `docker-compose.yaml`, `~/junction/docker/studio-tailnet.override.yaml`,
  `~/junction/docker/studio-preview.override.yaml`; command in `docs/infrastructure/TROUBLESHOOTING.md`).
- `configs/training/dataset.sort_depth_v2.toml` and `configs/training/smolvla_sort_depth_v2.toml`: the dataset
  contract and the 10k-step recipe with a validation set that contains both tasks.

## Evidence

- Camera lag root cause: Studio's session socket pushed four JPEG streams at 20 Hz (~19 Mbit/s) to a laptop on the
  same venue guest Wi-Fi (ping 27–636 ms, 10% loss); every session logged `session-sampler ... missed` stalls of
  0.4–15 s. Camera side measured tens of ms. After the fix the sampler runs at 10 Hz (seen in the logs); bandwidth
  under a real session was not measured because the environment's IP cameras were down at the time.
- Dataset copy: `data/studio/af9b173a-ee59-4e24-97c8-be71dba701ce` on the 5090 PC, data parquet sha256 matches the
  workstation copy.
- `sort-depth-v2-3k`: 3000 steps, 19 min, ~2.5 it/s, ~8.7 GB VRAM; train loss per 500 steps 0.31, 0.31, 0.25, 0.21,
  0.18, 0.15. Only `last.ckpt` (1.7 GB). MLflow run `6e624c9e5eb0443686e66741fc84fd1f` in experiment
  `defect-sorter-training` (status set to FINISHED by hand after MLflow's emoji output crashed on the cp1252 console).
- Hardware touched, with the user's approval: Studio container recreated (no recording in progress), depth bridge
  start attempted (failed: D415 unplugged at the time). No arm motion.

## Open questions and next steps

The 10k run is in progress on the 5090 PC (started about 20:23 UTC; step 1528 at 20:35 UTC, so expect it to end around 21:45 UTC):

- Run dir: `artifacts/training/sort-depth-v2-10k/` (plan.json, config.json, `checkpoints/`, Lightning CSV in
  `metrics/version_0/metrics.csv`, `val/loss` appears after each epoch). Console log:
  `artifacts/logs/sort-depth-v2-10k.log`.
- It runs as a child of the session that launched it. If that session's process tree is closed the run stops. Do
  not start a second run on the same GPU while it runs. Check it is alive:
  `Get-CimInstance Win32_Process -Filter "CommandLine like '%sort-depth-v2-10k%'"`.
- If it died, restart under a new run name (run directories are never reused), detached so it survives:
  `uv run python -m defect_sorter.training run --recipe configs/training/smolvla_sort_depth_v2.toml --dataset configs/training/dataset.sort_depth_v2.toml --run-name sort-depth-v2-10k-b`
  (unset `VIRTUAL_ENV` first; set `PYTHONIOENCODING=utf-8`).
- When it finishes: read `val/loss` and the train-loss trend from `metrics.csv`; log it with
  `PYTHONIOENCODING=utf-8 uv run --extra tracking python -m defect_sorter.tracking training artifacts/training/sort-depth-v2-10k`
  (MLflow server on 127.0.0.1:5000 must be up); compare with `sort-depth-v2-3k`; post the numbers to the team.
- Then: export with `physicalai export` to OpenVINO (see `docs/infrastructure/TRAINING.md`) and, only after a
  person reviews it, a release via `docs/infrastructure/MODEL_RELEASES.md`. Never run a policy on the arm without a
  person asking for that motion in the current conversation.
- Data: add ~10 pink-bowl episodes to balance the tasks. Studio's older datasets disappeared from its list; ask the
  team whether that was intended.
- Workstation: plug in wired Ethernet or operate from its own screen; restart the depth bridge
  (`defect_sorter.depth_bridge`, port 8092) when the D415 is connected, otherwise environments using
  top_rgb/top_depth fail to load.
- Remote hosting: the 5090 PC is reachable over Tailscale; keep MLflow on loopback (inbound firewall unchanged).

Never include credentials, private chat transcripts, or model/dataset contents.
