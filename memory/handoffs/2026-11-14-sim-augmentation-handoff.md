# Handoff: simulation augmentation, camera calibration, LLM planner (2026-11-14)

Author: Linan. Written for the next agent taking over remotely on the Monster AI 5090 PC. Read
`docs/sim/SIM_AUGMENTATION.md` first for the results; this file covers how to run, what is still running, and the
traps.

## Machine and environments

- Windows 11 PC with an RTX 5090. The repo is at `C:\Users\Jiang\.gemini\antigravity\scratch\hackjunction`, and it is shared with other threads: check `git status` and stage explicit paths.
- MuJoCo does not run natively on Windows because Smart App Control blocks it. It runs in **WSL2 Ubuntu-22.04**:
  - venv: `~/mjenv` (Python 3.12, mujoco, numpy, scipy, opencv-python-headless, av, pyarrow);
  - Menagerie `robotstudio_so101` @ `370c43965323c0944b433b202aac5058b5f907a9` in `~/sim/mujoco_menagerie/robotstudio_so101`;
  - outputs in `~/sim/out`.
- Call WSL from PowerShell with script files (LF line endings). Git Bash mangles `/mnt/...` paths.
- Real dataset (read-only): `data/studio/af9b173a-ee59-4e24-97c8-be71dba701ce` (sort-depth-v2, 35 episodes, 30 fps). In WSL it is `/mnt/c/Users/Jiang/.gemini/antigravity/scratch/hackjunction/data/studio/af9b173a-...`.

## Still running at handoff: leave them alone

- **vLLM** at `http://127.0.0.1:8000/v1`, model id `qwen3.8-vllm` (nvidia/Qwen3.8-27B-NVFP4), shared with other sessions.
  - Check: `curl -s http://127.0.0.1:8000/v1/models`.
  - Never start a second server, never stop it, and never kill Ollama or other GPU jobs without the user's OK.
  - Restart (only with the user's OK): `~\.codex\skills\vllm-subagent-launcher\scripts\start_vllm.ps1`.
  - If the KV cache OOMs at start, another training job holds GPU memory; wait for it to finish.
- **Joint camera fit** (WSL, CPU and GPU, about 10 to 15 min):
  - writes `/home/linan/sim/out/top_camera_joint.json`;
  - check: `wsl -d Ubuntu-22.04 -- bash -lc "ps aux | grep fit_joint\|joint.py | grep -v grep; cat ~/sim/out/top_camera_joint.json"`;
  - rerun: `scripts/sim/calibration/fit_joint_camera.py` with the env below.

## Commands (inside WSL, from `~`)

```bash
export MUJOCO_GL=egl LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe   # CPU rasteriser: faster than the D3D12 GPU path here
R=/mnt/c/Users/Jiang/.gemini/antigravity/scratch/hackjunction
DS=$R/data/studio/af9b173a-ee59-4e24-97c8-be71dba701ce
SIM=$R/scripts/sim/so101_sort_sim.py
CAM=$R/config/sim/top_camera_joint.json   # recommended joint fit: IoU 0.38, grasp median 12.5 px

~/mjenv/bin/python $SIM layout-prior $DS --camera $CAM --out ~/sim/out/prior.json
~/mjenv/bin/python $SIM simulate --camera $CAM --prior ~/sim/out/prior.json --out ~/sim/out/sim_a --episodes 40 --workers 8
~/mjenv/bin/python $SIM render --camera $CAM --sim ~/sim/out/sim_a --out ~/sim/out/render_a --views 3 --stride 1 --workers 6
```

Export to LeRobot v3 in the Studio backend environment (where `lerobot` is installed):
`python src/defect_sorter/lerobot_export.py <render_dir> <out_dataset> --video --robot-type SO101_Follower`. Then compare
`meta/info.json` with the real dataset (features, fps, camera keys, state names).

Planner benchmark (Windows, repo root): `uv run python scripts/sim/qwen_planner_demo.py --model qwen3.8-vllm --repeats 3 --timeout 30`.
For the GPU path, use `MUJOCO_GL=egl MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA`; without the adapter name, EGL renders on the AMD iGPU.

## Next steps (in order)

1. Pick the camera: compare the joint fit with `top_camera_grasp.json` (IoU and grasp median px), and rerun `layout-prior` with the winner.
2. Raise expert grasp success with the Duplo brick (target ≥ 80 %), using `simulate` with `--prior` and 10 episodes. Inspect failures by rendering a few frames around the grasp. Knobs: `open_g`, the fixed-jaw offset in `expert_plan`, `z_grip`, `GRASP_RADIUS_M`, `release_point`.
3. Render a 30 fps batch, export it, and do a training smoke run with sim + real mixed (sim tagged `mujoco-sim`).
4. Refine the calibration further: release points, ArUco PnP check, FK unit mapping vs the recording calibration.
5. Wire `planner.LLMPlanner` into `closed_loop.py` as an option, with the rules staying the default.

## Traps

- Each `Cell` writes `_sorting_cell_<pid>.xml` and `_marker_<id>.png` into the Menagerie directory (the model includes `so101.xml` by relative path). Do not clean that directory while jobs run.
- Positions measured on real frames are only as good as the camera. Rendering through the same camera puts them back at the right pixels, but reachability depends on the absolute accuracy.
- `tests/test_uvc_controls.py::test_find_device_picks_the_capture_node_of_the_named_camera` fails on Windows. It already failed before this change; it is Linux-only behaviour.
- The scripts under `scripts/sim/calibration/` are research scripts with hard-coded WSL paths. Run them from WSL.

## New requirement (Linan, 2026-11-14): present the brick to the inspection camera

The arm should deliberately rotate the brick so the main inspection camera sees its faces. All cameras sit above the table.

- Put the defect on a random face, not only the top.
- After the lift, move to a show point on the main camera's optical axis, 0.3 to 0.5 m from it. It must lie inside the D415 depth range and inside reach.
- Search a wrist_roll × wrist_flex grid. Score each pose by the defect pixels left unoccluded in a segmentation render, times the cosine between face normal and view direction. Hold each pose 0.3 to 0.5 s in score order, then sort.
- Log the visible defect pixels per frame as a privileged label.
- Camera sampling:
  - The main camera must be fixed before simulating, either re-simulated per pose or only perturbed slightly and the show frames re-checked.
  - Other cameras stay fully random.
  - All cameras above the table and looking down.
  - Keep at least 5 cm clearance from the arm's swept volume.
  - The brick must be unoccluded and in range in the show frames.
  - Reject a camera with no reachable show point.
