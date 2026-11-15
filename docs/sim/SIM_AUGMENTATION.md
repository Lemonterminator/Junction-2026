# Simulation augmentation and LLM planner: progress report (2026-11-14)

For teammates and agents continuing the work. Plan document (Chinese, with priorities and effort):
https://claude.ai/artifact/15shyBvt3qEg7XmXrAV2BJ

## What exists

| Piece | Where | State |
|---|---|---|
| MuJoCo sorting cell (SO-101 Menagerie model, two plates, Duplo brick, clutter, ArUco markers, tiled table) | `scripts/sim/so101_sort_sim.py` | works in WSL2 |
| Scripted expert with physics grasp + assisted hold: pick → present → handoff → place | same, `expert_pick` / `presentation_search` / `expert_present` / `expert_handoff` / `expert_place` | works: 35/40 episodes sorted correctly (36/40 grasped) |
| Presentation to the inspection camera (defect on any face, show points 0.3 to 0.5 m in front of the top camera, wrist flex × roll search scored by visible defect pixels × cosine) | same, geometry in `src/defect_sorter/presentation.py` (`tests/test_presentation.py`) | works; every grasped brick was presented |
| Privileged per-frame labels: expert phase, defect and brick pixels visible in `top_rgb_v2` | `render` → `.npz` → `lerobot_export.py` → `meta/privileged.parquet` | works |
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

## Presentation stage (2026-11-15)

The arm now shows the brick to the main inspection camera (the top D415, `top_rgb_v2`) before it sorts:

1. **Defect on any face.** `Layout.defect_face` picks one of six faces; the defect is a dark cross on that face
   (`defect_strokes`). A normal brick carries the same cross in the hidden geom group 5, so the planner can score views
   of "the face to inspect" without the cross ever being rendered.
2. **Main camera fixed before simulating.** Each episode samples its main camera near the fitted one (±3 cm, ±5°)
   and keeps it only if a show point is reachable: points 0.30 to 0.50 m from the camera, at most 12° off its optical
   axis, 0.12 to 0.40 m from the base and at least 0.10 m above the table (`show_points`). The pose is stored in the
   episode JSON (`top_camera`).
3. **Search.** After the lift, a 7 × 9 wrist flex × wrist roll grid is solved (shoulder pan, lift and elbow put the
   held brick's centre on the show point). A pose counts when the moving links stay 2 cm above the table, the brick is
   inside the crop and at least half of it is not hidden by the arm (segmentation renders with and without the arm).
   Score = visible defect pixels × cosine between the face normal and the view direction.
4. **Presentation.** Two or three distinct poses (at least 0.6 rad apart in flex/roll, score ≥ 0.3 × best) in score
   order, each held 0.3 to 0.5 s; then the standard holding pose `HANDOFF_Q` (same joints in every episode, as the
   handoff in `docs/plans/INSPECT_THEN_SORT_PLAN.md`), then the bowl.
5. **Rendering.** The main camera is only perturbed (±5 mm, ±0.5°, ±0.5 % focal) and the show frames are re-checked
   (brick in the crop, ≤ 50 % occluded, defect visible at least once for a defective brick); after 20 failed
   perturbations the simulated camera is used as is. The side camera (`front`) is fully random: any yaw, 0.20 to
   0.70 m high, looking down, at least 5 cm from the arm's swept volume (collision geoms over the whole trajectory, as
   bounding spheres), with brick and both bowls in view.
6. **Labels.** Each rendered frame stores `phase` (index into `rest, approach, grasp, lift, show_move, show_hold,
   handoff, place, return`), `defect_px` (defect pixels visible in `top_rgb_v2`, 0 for a normal brick) and `brick_px`.

Also fixed on the way: placing into the far (pink) bowl used jaws-down IK that cannot reach it, so the arm released
elsewhere; `ik_reach` now relaxes the jaws-down weight step by step. A brick released while overlapping a jaw or bowl
clutter could be ejected by contact forces; its speed is capped for 15 frames after release. The top-view check no
longer requires full bowl rims or the gripper path above 6 cm inside the crop, because the real top view cuts both.

**Results (joint camera, layout prior re-measured with it, 40 episodes, seed 0):** 36 grasped, 36 presented, 35 sorted
into the correct bowl (87.5 %). The 4 grasp misses are bricks 0.30 to 0.37 m out; one brick fell out of the bowl.
Show poses reach 100 to 220 visible defect pixels at cosine 0.85 to 0.99 for side faces; the top face scores lower
(cosine about 0.4) because the wrist cannot tilt it fully towards the camera.

## Open issues (priority order)

1. Calibration: the camera is good to about a centimetre near the brick, worse over the bowls. Next steps: add release points as constraints, use the ArUco markers of known size (`defect_sorter.markers`) for a PnP check, and check the FK unit mapping against the Studio calibration that recorded the dataset. Studio re-calibrated at 17:34 and overwrote the wrist_roll full-turn range.
2. Grasp misses on far bricks (0.30 to 0.37 m): tune the fixed-jaw offset and `z_grip` there.
3. The jaws-down IK (`ik`) is weak near the base: the wrist flex limit (1.66 rad) stops it, so the handoff pose is a
   fixed joint vector instead of a Cartesian target.
4. Only the top camera is the inspection camera; if the real cell inspects with the front camera (as the inspect-then-
   sort plan says), fit the front camera first and point `presentation_search` at it.
5. Planner integration into `closed_loop.py` behind a flag (LLM optional, rules default).

## Rules that still apply

Datasets are read-only. Do not touch the cameras, the arm or the Studio settings. Never start a second vLLM server or stop the running one. Sim results are tagged `source = mujoco-sim` and never pooled with real data without the tag.
