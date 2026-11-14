# PhysicAI · Junction 2026

Defect inspection and sorting with an SO-101 arm: **PERCEIVE → DETECT → REASON → ACT → OPTIMIZE**. A camera locates a Lego brick, Anomalib inspects it for a marker-pen cross, and the decision selects a fixed sorting task for the robot policy. Intel deployment and measured performance are part of the challenge.

This repository contains the Python pipeline, a standalone dashboard, the `armkit` workspace library, the pinned Physical AI Studio submodule, and the challenge research archive. Local development can start without the shared workstation or robot.

## Choose a workflow

| Goal | Start here | Requirements |
| --- | --- | --- |
| Preview the UI | [Run the dashboard](#run-the-dashboard) | uv, Python 3.12; no Docker or devices |
| Develop/test Python | [Set up a checkout](#set-up-a-checkout) | Git, Git LFS, uv, Python 3.12 |
| Generate simulated demonstrations | [Hardware-free pipeline](#run-the-hardware-free-pipeline) | Default Python environment |
| Start your own Studio | [Separate Studio instance](#start-a-separate-studio-instance) | Docker Linux engine, initialized submodule |
| Use the shared robot | [Shared workstation](#use-the-shared-workstation) | Team access and on-site operator coordination |
| Prepare policy training | [Plan training](#plan-training) | Submodule; actual training additionally needs data and CUDA |
| Review recordings | [Recorded datasets](#review-recorded-datasets) | Exported LeRobot v3 data; optional `dataset` extra |
| Inspect calibration planning | [armkit library](#armkit-library) | Default workspace environment; plan opens no device |
| Share trained models | [Tracking and model releases](#tracking-and-model-releases) | Optional `tracking` extra or authenticated release access |
| Connect dashboard data | [Backend handoff](docs/infrastructure/DASHBOARD.md) | Replay/live adapter, still to be implemented |

## Current capabilities

The Python package includes scene detection, marker/table alignment, camera-based joint calibration, guarded scripted motion, camera-control profiles, a Studio colour/depth bridge, anomaly inspection, a closed-loop controller over replaceable interfaces, and a kinematic twin with a scripted expert. `armkit` supplies reusable kinematics, collision checks and guarded calibration. Team notes record physical calibration and teleoperation, scripted hover and guarded calibration checks, Intel inference profiling, a twin-data training smoke run and a first Studio-recording SmolVLA export. These are separate pieces of evidence, not a demonstrated autonomous real-cell sorting loop.

The dashboard currently runs **illustrative demo playback**. Its camera crop is synthetic, its arm is a stylized illustration, and missing timings/device fields stay empty. Live transport, calibrated joint rendering, Studio dataset replay and hardware commands are not connected. Real-cell and runtime-policy adapters also remain integration work. See [current status](memory/STATUS.md) for dated evidence and limitations.

## Set up a checkout

Prerequisites: Git, [Git LFS](https://git-lfs.com/), [uv](https://docs.astral.sh/uv/getting-started/installation/), and Python **3.12**. uv can provision the interpreter pinned in `.python-version`. Node **22 or newer** is needed only for frontend tests; the UI has no Node build or package installation.

For a fresh checkout:

```bash
git lfs install
git clone https://github.com/Lemonterminator/Junction-2026.git
cd Junction-2026
git submodule update --init --recursive
uv sync --locked
```

For an existing checkout, first change into its root, initialize the submodule if needed, then run `uv sync --locked`. The default environment includes the local `armkit` workspace member, pytest and Ruff without installing camera SDKs, Torch or Anomalib. Root Python is 3.12; Studio's backend uses a separate Python 3.13 environment. Optional extras separate `camera`, `anomaly`, `dataset` (Parquet episode review) and `tracking` (MLflow) dependencies from this default.

The Studio submodule is pinned to `17714488fa9c7d098a056da83f7c220cf983957d` on the upstream `junction2026` line. Keep that pin during setup; do not use `git submodule update --remote`. Git LFS is required by upstream assets. The standalone dashboard can run without the submodule, but the full test suite and training planner inspect upstream files.

Run checks from the repository root:

```bash
uv run pytest -q
uv run ruff check src tests packages
uv run ruff format --check src tests packages
node --test frontend/tests/*.test.mjs
```

If your shell does not expand the wildcard (for example PowerShell), list the files explicitly:

```bash
node --test frontend/tests/telemetry.test.mjs frontend/tests/image-loader.test.mjs
```

Pytest includes both `tests/` and `packages/armkit/tests/`. Tests use synthetic data and never open cameras or move the arm. Contributor rules, TDD and hardware boundaries are in [AGENTS.md](AGENTS.md).

## Run the dashboard

**Run this from the repository root**, where `frontend/index.html` exists:

```bash
uv run python -m http.server 8080 --bind 127.0.0.1 --directory frontend
```

Open **http://127.0.0.1:8080/**. Choose a scenario and use **Play demo** or **Inspect next part**. Cases cover perfect, defective, human review and arm fault. Drag the cell to rotate it, use arrow keys while the canvas is focused, or use the reset-view button. Ctrl+C stops the server.

For example, if the checkout is under your Documents folder, change into it first:

```bash
cd ~/Documents/Dev/Junction-2026
```

Use your own checkout path on another machine. No frontend installation, build, model download or hardware service is required. Use the HTTP URL rather than double-clicking `index.html`; browser ES modules require HTTP.

### Troubleshooting

| Symptom | Fix |
| --- | --- |
| `404 File not found` at `/` | Stop the server, change into the repository root, and rerun. From `~`, `--directory frontend` points to the wrong folder. If already inside `frontend/`, omit `--directory frontend`. |
| `Address already in use` | Stop your earlier server with Ctrl+C, or use port `8082` in both command and browser URL. |
| Blocked modules or empty page | Use the HTTP URL, not `file:`, and inspect the browser console. |
| Changes do not appear | Refresh without cache and confirm the server serves this checkout. |
| No live feed or real arm movement | Expected: controls operate the demo only. See the [integration guide](docs/infrastructure/DASHBOARD.md). |

## Run the hardware-free pipeline

From the root, generate two twin demonstrations, a small synthetic crop set, and an oracle evaluation. Use **new output directories** for later experiments; these commands can overwrite their own outputs.

```bash
uv run python -m defect_sorter.offline_pipeline record --out data/twin/first-demos --episodes 2
uv run python -m defect_sorter.offline_pipeline crops --out data/twin/first-crops --train 20 --test 4
uv run python -m defect_sorter.offline_pipeline evaluate --out artifacts/twin/first-eval --episodes 2
```

Recording writes `index.json` and compressed episode `.npz` files. Evaluation writes `episodes.jsonl` and `summary.json`. Without `--model`, evaluation uses twin ground truth and a privileged scripted expert: it checks plumbing, not learned detection/policy quality. Results retain `mode = twin` and stay separate from real measurements. These outputs do not automatically appear in the dashboard.

For Padim training, OpenVINO scoring, LeRobot export and recorded twin-training smoke results, follow the [offline pipeline guide](docs/infrastructure/OFFLINE_PIPELINE.md). Anomaly training needs the heavy `anomaly` extra and may download weights; export uses the separate Studio backend environment. Keep datasets, weights and exports under ignored `data/`, `models/`, `artifacts/` or `checkpoints/` directories.

The user described two LeRobot v3.0 episodes under `datasets/50815c02-…` (`SO101_Follower`) as simulated, while the newer [offline pipeline notes](docs/infrastructure/OFFLINE_PIPELINE.md) identify that same recording as real Studio data. This dashboard work has not inspected the files, so provenance requires confirmation before replay. Newer sources also define the separate `sort-v1` and `sort-depth-v2` datasets. See [recorded datasets](#review-recorded-datasets) and the [replay handoff](docs/infrastructure/DASHBOARD.md#candidate-studio-dataset-for-replay).

## Review recorded datasets

The [sort-v1 dataset card](docs/datasets/SORT_V1.md) defines the exact green/pink task strings, recording protocol, 56-episode collection plan, review criteria and Studio identifiers. It also documents the current `sort-depth-v2` setup. A collection plan and dataset entry do not establish how many usable episodes have been recorded.

For depth sessions, `sorter-depth-bridge` owns the D415 and supplies colour and layered height-above-table MJPEG streams to Studio IP cameras. The v2 encoding uses fine height in R, coarse height in G and depth validity in B; its fixed plane, crop, camera keys and scales are part of the recording contract. The earlier `sort-depth-v1` entry was deleted with no episodes. Coordinate camera ownership before starting any bridge or changing camera controls; the dashboard does not launch them.

Copy an authorized dataset export into ignored `data/` storage before review. For an existing export at `data/sorting`, run:

```bash
uv run --extra dataset sorter-episodes data/sorting
```

This reads recorded Parquet data; it does not command hardware. The review reports task/camera issues, grasp/release events and hover pauses. It does not write a new clipped dataset or replay episodes in the dashboard. Verify camera names, units, timestamps and simulated/real provenance before building the replay adapter.

## armkit library

[`packages/armkit/`](packages/armkit/README.md) is a reusable library for serial-bus servo arms: kinematics, URDF loading, collision checks, guarded motion, calibration planning and Feetech/simulated buses. The root package uses it through the uv workspace.

The model-only calibration plan opens no device:

```bash
uv run armkit-calibrate plan
```

Team notes now include user-authorized real-arm checks and proposed calibration files, superseding the earlier simulated-only status. They also record faults and limitations; a model-only plan is not evidence that a physical sweep is clear. Follow the library guide and latest team status for measured frames, joint directions, bus ownership and operator authorization. This dashboard exposes no calibration or motion commands.

## Start a separate Studio instance

This creates **your own CPU deployment** from the pinned source, separate from the existing shared workstation. Initialize the submodule and follow [Docker setup](docs/infrastructure/DOCKER.md) for first-time ignored configuration files, host settings and secrets. Create configuration files only if absent; preserve existing settings. Docker needs a working Linux engine and Compose with `additional_contexts` and optional `env_file` support.

From the root:

```bash
docker compose config --quiet
docker compose build studio
docker compose up -d --wait studio
docker compose ps
```

Open **http://127.0.0.1:7860/** once healthy. The first build is large and needs network access. CPU defaults map no robot/camera devices. Studio's UI/API and persistent storage are separate from the dashboard on port 8080. Configuration parsing does not establish build/runtime success; this change does not validate a Docker deployment.

```bash
docker compose logs --tail 100 studio
docker compose down
```

`down` retains named volumes. Adding `-v` deletes stored data. Use the same project name and overlays throughout a deployment. Intel GPU/NPU and device overlays are explicit opt-ins in the Docker guide; listing a device does not prove model correctness on it.

## Use the shared workstation

Read the [team connection guide](docs/infrastructure/TEAM_CONNECTION_GUIDE.md), [hardware access guide](docs/infrastructure/HARDWARE_ACCESS.md), and latest [team status](memory/STATUS.md). Confirm the current account, host and service owner: access documents contain dated observations.

The recorded workstation setup uses `~/junction` and Studio's **submodule Compose deployment**, project `docker`, with a prebuilt XPU image that differs from the pinned source. Root Compose commands are not its management commands. Coordinate restarts/deployments with the on-site lead, especially during recording.

Only one process can own a camera or servo bus. Studio recording, the depth bridge, alignment and perception demos must not compete for the D415; Studio's follower worker and armkit must not share a serial port. Hardware checks are manual and outside tests. Arm motion requires an on-site operator and explicit authorization for that motion; retain limits, stop on faults and do not automatically retry.

An operator-coordinated Linux perception session uses the `camera` extra and `sorter-live-demo`, which opens the D415; follow the access guide before launching. See [marker alignment](docs/infrastructure/MARKER_ALIGNMENT.md) for print sheets/alignment and [hardware profiling](docs/infrastructure/HARDWARE_PROFILING.md) for inference correctness/latency evidence. [Tailscale changes](docs/infrastructure/TAILSCALE_REMOTE_OPERATION.md) remain proposals unless the latest status records otherwise.

## Plan training

With the submodule initialized, inspect a SmolVLA plan in the light environment:

```bash
uv run python -m defect_sorter.training plan \
  --recipe configs/training/smolvla_expert.toml \
  --dataset configs/training/dataset.example.toml --run-name smolvla-first
```

In PowerShell, put the command on one line. Planning prints configuration and dataset status, leaves metrics null and creates no run/model. Missing data is allowed during planning.

Execution needs a complete LeRobot v3 recording, verified camera keys, joint order/units and tasks, plus a separate Linux/WSL Python 3.13 CUDA environment. Follow the [training guide](docs/infrastructure/TRAINING.md) to prepare those contracts and run a short fit. Prefer Studio-managed remote training for team integration: the CLI does not create a Studio job or register its model automatically. A twin-data fit does not establish real-cell success.

## Tracking and model releases

[`tracking.py`](src/defect_sorter/tracking.py) logs completed training runs and twin evaluations to MLflow through the optional `tracking` extra, keeping source and run-kind tags. The [tracking guide](docs/infrastructure/TRAINING.md#experiment-tracking-with-mlflow) describes the local server and artifact storage; tracking is separate from training execution.

The [model release guide](docs/infrastructure/MODEL_RELEASES.md) records the private `model-smolvla-studio-smoke-1` release: 50 SmolVLA steps on a first Studio recording with two green-bowl episodes, followed by OpenVINO export and a CPU run on synthetic input. Its status is `smoke-test`, explicitly **not for the arm**; it does not establish two-task sorting or physical policy success. The released state contract uses Studio-normalized body joints (`−100…100`) and gripper (`0…100`), unlike the twin's degree-valued body joints and the dashboard v1 contract. Do not feed those values directly into the illustrative viewer.

Authenticated collaborators can follow that guide to download release assets into ignored `models/` storage and verify their hashes with `defect_sorter.model_release`. Weights and captured recordings never belong in Git.

## Repository map

| Path | Purpose |
| --- | --- |
| `frontend/` | Dashboard, illustrative scene, demo model and frontend tests |
| `src/defect_sorter/geometry.py`, `scene.py` | Camera geometry, table plane, objects and colour bowls |
| `src/defect_sorter/realsense.py` | Aligned RealSense colour/depth adapter |
| `src/defect_sorter/uvc_controls.py`, `config/camera_controls.json` | Fixed USB camera-control profiles (`sorter-camera-lock`) |
| `src/defect_sorter/depth_bridge.py` | Studio colour and layered-height MJPEG camera bridge (`sorter-depth-bridge`) |
| `src/defect_sorter/webview.py`, `live_demo.py` | Latest-frame JPEG polling and JSON state for debug pages |
| `src/defect_sorter/markers.py`, `alignment.py` | Printed markers, depth-refined poses, table frame and drift |
| `src/defect_sorter/kinematics.py`, `joint_calibration.py`, `calibration_capture.py` | SO-101 kinematics and measure-only calibration |
| `src/defect_sorter/motion.py`, `robot_pose.py`, `targeting.py` | Checked scripted moves, measured robot/model mapping and top-camera brick hover targets |
| `packages/armkit/` | Workspace library: kinematics, collision model, guarded motion/calibration and servo adapters |
| `src/defect_sorter/inspection.py`, `closed_loop.py` | Anomaly decisions and observe/inspect/plan/execute/verify loop |
| `src/defect_sorter/twin.py`, `offline_pipeline.py`, `lerobot_export.py` | Twin, synthetic demonstrations/evaluation and LeRobot export |
| `src/defect_sorter/training.py`, `training_preflight.py` | Training plans, dataset contracts and launch preflight |
| `src/defect_sorter/episodes.py`, `docs/datasets/SORT_V1.md` | Recorded-episode review, hover/grasp clip ranges and recording protocol |
| `src/defect_sorter/tracking.py`, `model_release.py` | MLflow logging and hashed private-model release manifests |
| `tests/`, `configs/training/` | Python tests, policy recipes and example dataset contracts |
| `external/physical-ai-studio/` | Pinned upstream; keep integration outside this submodule |
| `memory/` | [Context](memory/PROJECT.md), [status](memory/STATUS.md), [decisions](memory/DECISIONS.md) and handoffs |
| `docs/infrastructure/` | Setup, deployment, hardware, training and collaboration how-tos |
| `docs/2026/`, `docs/past/` | Bronze source archive, Silver summaries and Gold analysis |

The [execution plan](docs/plans/PHYSICAL_AI_EXECUTION_PLAN.md) defines deliverables and acceptance gates. The [twin study](docs/research/SO101_DIGITAL_TWIN.md) covers sim-to-real limits; [winner reuse research](docs/research/PAST_HARDWARE_WINNERS_REUSE.md) informs the direction. [Gemini/RL work](docs/plans/DEFERRED_GEMINI_RL_EXPERIMENTS.md) is deferred.

## Challenge sources

The [archived Intel brief](docs/2026/silver/intel_physical_ai_hackathon.md) and [pinned Studio event guide](external/physical-ai-studio/JUNCTION2026.md) have different judging tables. Team-relayed kickoff answers adopt the GitHub rubric; both sources are preserved. See the [decision log](memory/DECISIONS.md) for attribution and evidence limits.

| Source | English | 中文 |
| --- | --- | --- |
| Intel analysis | [Analysis](docs/2026/gold/en/intel_physical_ai_challenge.md) | [分析](docs/2026/gold/zh/intel_physical_ai_challenge.md) |
| Studio guide | [Guide](docs/2026/silver/en/intel_physical_ai_studio_guide.md) | [指南](docs/2026/silver/zh/intel_physical_ai_studio_guide.md) |
| Open Edge Platform review | [Review](docs/2026/silver/en/open_edge_platform_repositories.md) | [评估](docs/2026/silver/zh/open_edge_platform_repositories.md) |
| Creative options | [Options](docs/2026/gold/en/intel_physical_ai_creativity_options.md) | [方案](docs/2026/gold/zh/intel_physical_ai_creativity_options.md) |

Browse the [Silver index](docs/2026/silver/README.md) and [Gold index](docs/2026/gold/README.md) for the research archive.
