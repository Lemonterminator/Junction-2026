# Hardware-free pipeline: twin → demos → SmolVLA / Anomalib → closed loop

This guide covers running the whole sorting chain without the arm or cameras: the
same loop, inspector and training entry points the real cell will use, fed by a
kinematic digital twin. When the hardware is ready, only the data source changes:
a real `Cell` adapter replaces `TwinCell`, and Studio recordings replace twin demos.

Everything this pipeline produces is **twin data**. It shows that the data path,
training launch, export and loop logic work. It says nothing about real detection
quality, policy success or latency on the real cell.

## What runs where

```text
TwinCell (twin.py) ──record──▶ data/twin/demos (*.npz + index.json)
     │                               │ lerobot_export.py (Studio backend env, lerobot 0.6)
     │                               ▼
     │                         data/twin/lerobot (LeRobot v3, image features)
     │                               │ training.py run (smolvla_twin_smoke.toml)
     │                               ▼
     │                         artifacts/training/<run> (checkpoints, metrics)
     │
     ├──crops──▶ data/twin/crops ──inspection.py train (anomaly extra)──▶ Padim OpenVINO model.xml
     │                                                                        │
     └──evaluate: closed_loop.run_episode(TwinCell, ThresholdInspector(OpenVinoScorer), ScriptedExpert)
                    ──▶ artifacts/twin/eval-*/episodes.jsonl + summary.json
```

| Part | Module | Replaced on real hardware by |
| --- | --- | --- |
| Cell (observe / apply / outcome) | `twin.TwinCell` | a real-cell adapter: camera owner + follower driver + bowl check from `scene.detect_scene` (not written yet) |
| Inspector | `inspection.ThresholdInspector` + `OpenVinoScorer` | same code, Padim retrained on real good-brick crops |
| Policy | `twin.ScriptedExpert` (privileged, reads the brick position) | the fine-tuned SmolVLA through the OpenVINO PhysicalAI runtime (adapter not written yet) |
| Demonstrations | `offline_pipeline record` | Studio recordings (LeRobot v3) |
| Label → task | `closed_loop.DEFAULT_TASKS` | same mapping, frozen to the on-site bowl rule |

## The twin

`twin.py` is kinematic, not a physics engine (native MuJoCo is blocked on this
Windows machine by Application Control; see the twin study). Joints follow
commands at a bounded speed inside the URDF limits; the brick is grasped when the
gripper closes with the TCP within 12 mm of it and is carried rigidly until the
gripper opens; driving the TCP below the table raises `ArmFaultError`. Kinematics come
from `kinematics.py`; the TCP is the URDF `gripper_frame_joint` origin. The cameras
are orthographic drawings (top: 312×240, wrist: 240×320 following the TCP); the
inspection crop is a 128×128 close view of the brick. A defect is a dark marker
cross on the brick's top face, as in the kickoff definition.

Assumptions to check against the real cell before mixing data: table top at
`base_link` z = 0; gripper 0 = closed, 100 = open; bowl positions
(0.16, ±0.15) m; brick area x 0.19–0.25 m, y ±0.05 m.

## Commands

Light environment (Python 3.12, repo root):

```bash
uv run python -m defect_sorter.offline_pipeline record --out data/twin/demos --episodes 40
uv run python -m defect_sorter.offline_pipeline crops --out data/twin/crops
```

Anomalib (the `anomaly` extra; on Windows set `PYTHONUTF8=1`, otherwise Anomalib's
export crashes printing an emoji to a cp1252 console):

```bash
uv run --extra anomaly python -m defect_sorter.inspection train --data data/twin/crops --out artifacts/twin/padim
uv run --extra anomaly python -m defect_sorter.offline_pipeline evaluate --out artifacts/twin/eval \
  --model artifacts/twin/padim/export/weights/openvino/model.xml --device CPU
```

Omit `--model` to evaluate with the twin's ground truth (`twin-ground-truth`
inspector), which separates policy errors from detection errors.

Studio backend environment (Python 3.13, CUDA; see [TRAINING.md](TRAINING.md)):

```bash
uv run --project external/physical-ai-studio/application/backend --extra cuda --frozen \
  python src/defect_sorter/lerobot_export.py data/twin/demos data/twin/lerobot --repo-id local/twin-sorting
uv run python -m defect_sorter.training run --recipe configs/training/smolvla_twin_smoke.toml \
  --dataset configs/training/dataset.twin.toml --run-name twin-smoke-1
```

`training.py run` itself launches `physicalai fit` in the backend environment. To
keep that environment outside the checkout, set `UV_PROJECT_ENVIRONMENT` to its
path for both commands.

## Results on 2026-11-14 (Windows 11, RTX 5090, Intel Core Ultra iGPU)

All numbers are twin data from one run each; they validate the plumbing, not the
real task.

| Step | Result |
| --- | --- |
| Unit tests (light env) | 165 passed, including 47 new for inspection, loop, twin and pipeline |
| Scripted expert, `record` | 40/40 attempts DONE, 152–169 frames each at 30 fps (2 min 17 s) |
| `crops` | 200 train/good, 40 test/good, 40 test/defect |
| Padim (resnet18, CPU, 1 epoch) | Anomalib test on twin crops: image AUROC 1.0, F1 0.947; exported to OpenVINO |
| `evaluate` with Padim on CPU | 20/20 DONE; 19/20 sorted correctly (one defective brick scored normal); 18.9 ms per inspection incl. resize |
| `evaluate` with Padim on GPU.0 (Intel iGPU, f32 hint) | same 20 bricks, same decisions; 14.7 ms per inspection |
| `lerobot_export` | 40 episodes, LeRobot v3 with image features, 1.5 GB; `training.py plan` reports `metadata_validated` |
| `training.py run` preflight | task shards and frame task references read and validated in the backend env |
| SmolVLA expert fine-tune, 50 steps, batch 4 × 2, bf16, RTX 5090 | finished in 1 min 03 s; train loss 0.96 (step 2) → 0.47 (step 49); `last.ckpt` 1.7 GB |

Problems found on the way, with the workaround used:

- **`physicalai` console script fails on Windows**: it imports the robot CLI, whose
  transport lock imports POSIX-only `fcntl`. `scripts/offline_pipeline/physicalai_without_robot_cli.py`
  builds only the `fit` parser; `training.py` now uses it on Windows (see the real-data
  section). On Linux the normal path is unchanged.
- **Windows Application Control blocks freshly installed DLLs once**: the first
  import of `scipy.optimize._highspy._core` and `scipy.io._mio5_utils` in a new
  environment failed with "An Application Control policy has blocked this file";
  the same import succeeded on the next attempt. No system policy was changed.
- **No `best.ckpt` for runs shorter than one epoch**: validation runs once per
  epoch, so a 50-step run never logs `val/loss` and the checkpoint callback keeps
  only `last.ckpt`. Real runs longer than an epoch are not affected.
- **Anomalib export on a cp1252 console** crashes printing an emoji; set
  `PYTHONUTF8=1`.
- uv's managed CPython 3.13 minor-version link is broken on this machine; the
  backend environment was built with `--python` pointing at the full
  `cpython-3.13.18` interpreter.

Not run: inference with the fine-tuned checkpoint inside the loop, OpenVINO export
of the policy, NPU runs, anything on the arm or cameras.

## Real Studio recording → training (2026-11-14)

The same training path ran on the first real recording from the workstation's
Studio volume (`datasets/50815c02-…`, copied read-only into `data/studio/`):
LeRobot v3.0, 2 episodes (840 and 317 frames, 30 fps), one task ("Pick up the brick
and place it in the green bowl."), cameras `top`, `wrist` and `front` at 640×480
AV1. Contract: `configs/training/dataset.studio.toml`; recipe
`configs/training/smolvla_studio_smoke.toml`.

```bash
uv run python -m defect_sorter.training run --recipe configs/training/smolvla_studio_smoke.toml   --dataset configs/training/dataset.studio.toml --run-name studio-smoke-1
```

| Step | Result |
| --- | --- |
| `training.py plan` | `metadata_validated`; validation episode 0, training episode 1 |
| Runtime preflight (task shards, frame task references) | passed |
| SmolVLA expert fine-tune, 50 steps, three cameras, RTX 5090 | finished; train loss 0.94 → 0.16 (one training episode, so mostly memorised); held-out episode `val/loss` 0.81 at step 39; `best.ckpt` and `last.ckpt` written |

Units: Studio's SO-101 driver records body joints normalised to [−100, 100] and the
gripper to [0, 100] by default (`physicalai_so101_plugin`, `unit = "normalized"`).
The twin uses degrees for body joints, so twin and Studio data must not be mixed
until one is converted.

On Windows, `training.py` now plans `fit` through
`scripts/offline_pipeline/physicalai_without_robot_cli.py` and sets
`video_backend = "pyav"`: torchcodec's Windows wheel needs FFmpeg shared libraries
that are not installed, while PyAV bundles an AV1 decoder (dav1d). Linux plans are
unchanged.

What this shows: real recordings decode, train and checkpoint end to end on the
5090. What it does not show: a usable policy. That needs about 30–50 clean episodes
covering both tasks.

## What is still missing

- **Real-cell adapter** implementing `Cell`: one camera owner, follower commands
  with the existing speed limits, outcome from `scene.detect_scene`. Needs the arm,
  frozen camera mounts and a hardware owner.
- **SmolVLA policy adapter** for the loop: load the exported policy through the
  OpenVINO PhysicalAI runtime, send the task text, reset the action chunk per brick.
  Needs a checkpoint trained on real recordings; a twin-trained checkpoint only
  tests the plumbing.
- **Real data**: Studio recordings for both tasks (plan W2.3) and real good-brick
  crops for Padim with a threshold chosen on a validation split (plan W2.2).
- **Twin fidelity**: perspective camera models from the marker calibration,
  measured bowl/brick positions, gripper convention confirmed from a recording,
  dynamics. Until then twin-trained models are pipeline checks only.
