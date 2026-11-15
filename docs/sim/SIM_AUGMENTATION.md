# Simulation augmentation and LLM planner: progress report (2026-11-14)

For teammates and agents continuing the work. Plan document (Chinese, with priorities and effort):
https://claude.ai/artifact/15shyBvt3qEg7XmXrAV2BJ

## What exists

| Piece | Where | State |
|---|---|---|
| MuJoCo sorting cell (SO-101 Menagerie model, two plates, Duplo brick, clutter, ArUco markers, tiled table) | `scripts/sim/so101_sort_sim.py` | works in WSL2 |
| Scripted expert with physics grasp + assisted hold | same, `expert_plan`, `Cell.update_grasp` | works; success rate low (see open issues) |
| "Simulate once, render many": full 3D state (`qpos`) stored per frame, re-rendered under random plausible cameras | `simulate` / `render` subcommands | works |
| Real-data calibration of the top camera | `fit-camera` (arm silhouette IoU), `scripts/sim/calibration/` (grasp correspondences, joint fit) | coarse, see below |
| Layout prior from real first/last frames (bowl centres, brick position) | `layout-prior` subcommand, output `config/sim/prior_grasp.json` | works |
| Output in `offline_pipeline` format → LeRobot v3 like sort-depth-v2 | `render` → `src/defect_sorter/lerobot_export.py --video --robot-type SO101_Follower` | export path written and unit-tested; not yet run on sim output |
| LLM planner (closed action set, validator, rule fallback) | `src/defect_sorter/planner.py`, `tests/test_planner.py` | done, 13 tests |
| Local Qwen benchmark of the planner | `scripts/sim/qwen_planner_demo.py`, results `config/sim/planner_rows.json` | done |

## Key results

**Planner with local Qwen3.8-27B NVFP4 (vLLM, temperature 0, thinking off), 8 situations × 3:**
0.56 to 0.76 s per decision (first call 2.5 s). It matched the rules on clear normal, clear defect, first uncertain
look and first missed grasp. The validator rejected 3 unsafe proposals: a third inspection, a second grasp retry,
and a retry after an arm fault. In each case the planner fell back to the rules. On "placed in wrong bowl" it chose
REINSPECT and the rules chose SORT_GREEN; both are valid. Fine for one decision per brick, never for per-frame control.

**Camera calibration (top D415 view, sim base frame):**
- Arm silhouette IoU fit: `config/sim/top_camera_silhouette.json`, IoU 0.42. Height 0.56 and tilt 24.0 disagree with the measured plane-v2 (0.508 m, 25.9°).
- Grasp-correspondence fit: `config/sim/top_camera_grasp.json`. Height, tilt and focal are fixed to plane-v2 and the D415 values. Correspondences pair the brick pixel (height drop between the first and last frame) with the jaw centre from FK at the lowest point. Median error is 13 px (about 1.2 cm); IoU 0.375.
- Joint fit (IoU + grasp error + priors): `config/sim/top_camera_joint.json`, height 0.513 m, tilt 26.1°, focal 612 px, which agree with plane-v2 and the D415. IoU is 0.38 and grasp median error 12.5 px. **Use this one.**

**Rendering speed:** in WSL, the CPU rasteriser (`LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe`) is about 90 ms per 640x480 RGB frame. The D3D12 GPU path is about 215 ms because it is readback-bound. Use `--workers` (32 cores).

**Real cell, measured from 35 first frames:** plates about 18 to 20 cm across. Green is at about (0.21 to 0.26, 0.16 to 0.18) and pink at about (0.37 to 0.45, 0.19 to 0.23) in the base frame. The brick is at about (0.29 to 0.38, −0.07 to 0.05). Bricks are Duplo size (2x2, sometimes 2x4). The operator releases over the near side of the far (pink) bowl; release FK about (0.33, 0.17).

## Open issues (priority order)

1. Calibration: the camera is good to about a centimetre near the brick, worse over the bowls. Next steps: add release points as constraints, use the ArUco markers of known size (`defect_sorter.markers`) for a PnP check, and check the FK unit mapping against the Studio calibration that recorded the dataset. Studio re-calibrated at 17:34 and overwrote the wrist_roll full-turn range.
2. Expert grasp success: it was 3/10 with the old 2x1 brick, and the Duplo-size brick plus the wider opening (1.3 rad) are untested. Run `simulate` with `--prior` and tune `open_g`, the fixed-jaw offset, `z_grip` and `GRASP_RADIUS_M`.
3. Run a stride-1 (30 fps) batch, export it with `lerobot_export.py --video --robot-type SO101_Follower` in the Studio backend environment, and diff `meta/info.json` against sort-depth-v2.
4. The front camera pose in the sim is a guess; fit it like the top one.
5. Planner integration into `closed_loop.py` behind a flag (LLM optional, rules default).

## Rules that still apply

Datasets are read-only. Do not touch the cameras, the arm or the Studio settings. Never start a second vLLM server or stop the running one. Sim results are tagged `source = mujoco-sim` and never pooled with real data without the tag.
