# Current status

## Update 2026-11-15 — Modal as overflow GPU

- `scripts/modal/train.py` runs the `defect_sorter.training` plan on a Modal GPU in
  an image built from the pinned Studio lock (`uv sync --frozen --extra cuda`).
  Recordings and runs live in the Volume `junction-training`; runs are downloaded
  and logged to MLflow locally. `defect_sorter.modal_training` holds the pure
  Volume layout and cost ceiling; guide in `docs/infrastructure/MODAL.md`.
- The Modal CLI on the training PC is authenticated (workspace `jianglinan1030`).
  The first T4 check failed with `workspace has exceeded its spend limit` at $0
  spent: the workspace spend limit must be raised before any remote call. No image
  build, upload, remote plan or GPU run has happened; only the local dry run ran.
- Tests: `tests/test_modal_training.py` (15 tests) written first and seen failing.

## Update 2026-11-15 — inspect-then-sort implementation plan

- Added the detailed [three-skill plan](../docs/plans/INSPECT_THEN_SORT_PLAN.md):
  pick and inspect, controlled holding handoff, Anomalib decision, green/pink
  held-placement and physical outcome verification. The current controller still
  scores before executing a complete pick-and-place task; no runtime behavior changed.
- Defined a 50-source-cycle / 100-skill-clip pilot, grouped train/validation/test
  splits, inspection coverage and quality gates, stale action/result cancellation,
  threshold validation, module/test ownership and staged acceptance targets.
- Linked README, the overall plan, dataset protocol and training guide. Existing
  full-task recordings and recipes keep their original semantics; no new Studio
  dataset, recipe or checkpoint was created.
- Documentation only; no new behavior tests were added. No camera access, arm
  motion, training or device deployment.
- Verification on Windows: `uv sync --locked` passed; `uv run pytest -q` finished
  with 571 passed, 2 failed and 1 skipped (the optional pyarrow episode-loader test).
  Both failures are in unchanged baseline code:
  `tests/test_depth_bridge.py::TestMjpegStream::test_each_part_carries_its_publish_time_for_latency_checks`
  rounds the HTTP timestamp to six decimals, below the test's full-precision lower
  bound; `tests/test_uvc_controls.py::test_find_device_picks_the_capture_node_of_the_named_camera`
  expects `/dev/video12` but Windows returns a path with backslash separators. A diagnostic
  `uv run pytest -q -x` also reproduced the timestamp failure (58 passed before it).
- `uv run ruff check src tests packages` passed; `uv run ruff format --check src tests packages`
  passed (89 files). All 96 local links across the six changed documents resolve;
  `git diff --check` passed. No source, test or dependency lock files changed.

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

## Update 2026-11-14 — workstation runtime and perception package

Supersedes the "No Ubuntu deployment, device capture, GPU/NPU inference" lines above for the shared Ubuntu workstation (branch `feat/defect-sorter-perception`). Details: [handoff](handoffs/2026-11-14-workstation-runtime-and-perception.md).

- Workstation runs upstream Studio via its own `application/docker` compose (profile `xpu`, privileged) at port 7860; devices plugged in after container start are invisible until `docker compose restart`.
- Studio project "Defect Sorting (Intel Challenge)": cameras `wrist` (USB2.0_CAM1), `front` (webcam), `top` (RealSense D415, colour); follower `5AAF262737` and leader `5AE7045026` added and online; environment "Sorting cell" pairs them. Arms are **not calibrated**; no teleoperation or recording yet.
- Host Intel runtimes installed (OpenCL/Level Zero GPU, NPU user-space driver 1.38.0). OpenVINO lists CPU, GPU and NPU; a Padim (resnet18) OpenVINO export ran on all three: CPU 5.0 ms, GPU 1.5 ms, NPU 8.5 ms per 1×3×256×256 inference. NPU needs a static input shape.  Latency only: the default GPU FP16 output was later found wrong, see [hardware profiling](../docs/infrastructure/HARDWARE_PROFILING.md).
- `src/defect_sorter`: uv package with TDD tests (20 passing). `detect_scene` finds objects by height above a RANSAC table plane and bowls by colour; live D415 run detected both bowls and two bricks at ~34 fps.

Next: calibrate both arms (needs a person), fix camera mounts, teleop dry run, record demonstrations; collect good-object crops for the Anomalib baseline.

## Update 2026-11-14 — local policy recipes and digital twin research

Local work on `feat/local-finetune-and-digital-twin`; not committed or pushed by this
update. Earlier workstation observations above were not re-verified remotely.

- Added ACT baseline, SmolVLA action-expert fine-tuning and experimental Pi0.5 LoRA
  recipes, with a light `python -m defect_sorter.training plan|run` entry point.
  Actual execution delegates to the pinned Studio backend's isolated CUDA/Python
  3.13 environment; root perception/tests remain Python 3.12.
- Metadata validation requires LeRobot v3.0, matching camera keys, state/action joint
  order, fps and explicit operator-declared units. Runtime preflight checks task
  language and frame task references before policy loading. Existing runs cannot
  be overwritten. Pi0.5 fitting 32GB VRAM is not established.
- Parent validation: 54 tests passed (20 existing, 34 new); Ruff lint and format
  checks passed. All three CLI plans report missing data, null metrics and no
  created run directory; a missing-data run exits 2 before starting training.
- A separate synthetic Parquet check in a temporary Windows pandas/pyarrow
  environment stalled during pandas extension import; the first helper was stopped
  and a bounded diagnostic retry timed out after 30 seconds. No Parquet payload was
  decoded. Root tests do not validate the heavy parser, model imports, gradients,
  CUDA memory use, training quality or export.
- [Training guide](../docs/infrastructure/TRAINING.md) and
  [SO-101 digital twin study](../docs/research/SO101_DIGITAL_TWIN.md) added; README
  and AGENTS test ownership updated. The twin study pins official/Menagerie assets,
  compares MuJoCo and LeIsaac, and specifies joint, gripper, camera, contact, timing
  and sim-to-real validation requirements.
- Native MuJoCo research smoke failed at import with WinError 4551 (Application
  Control blocked DLL loading); no model loading, simulation steps or rendering
  completed. No system-policy changes, camera capture or arm motion occurred.

Next: prepare the independent CUDA environment on Linux/WSL, verify runtime task
preflight and a short real-data fit/export; separately start the twin with calibrated
joint/unit mapping and offline trajectory playback before synthetic-data expansion.

## Update 2026-11-14 — historical hardware winner research

- Added [winner reuse study](../docs/research/PAST_HARDWARE_WINNERS_REUSE.md), checking
  Signvision (2017), Oneiro (2018), LumenLoop (2019), QuickBIM (2024), and Wavelet
  (2025) against public code, organizer announcements and author reports. Recorded
  source revisions, evidence limits, and concrete defect-sorting/twin reuse ideas.
- Identified unsupported performance details in the existing hardware Gold archive;
  the study records these limits without treating archive narratives as benchmarks.
  QuickBIM's overall third place is confirmed; KONE challenge first is not established
  by the sources checked. No historical project was built or benchmarked.
- Research only: no training, deployment, camera access or robot motion occurred.

## Update 2026-11-14 — detailed Physical AI execution plan

- Added [execution plan](../docs/plans/PHYSICAL_AI_EXECUTION_PLAN.md) based on the
  historical winner study, current source constraints, training guide and twin study.
  It defines staged work packages, data contracts, acceptance gates, ownership roles,
  approximate effort, missing-data tasks, evaluation protocols and scope reductions.
- Prioritizes the real single-object sorting loop and Intel deployment evidence;
  twin playback follows, with Gemini curriculum and RL as optional gated experiments.
  Proposed module names, numeric targets and effort budgets are plans, not results.
- Linked the plan from README and the winner study. Documentation only; no training,
  runtime setup, deployment, camera access or robot motion was performed.
- Validation after the plan was written: 12 local links checked across the plan,
  winner study and STATUS; 54 tests passed; Ruff lint and format checks passed;
  `git diff --check` passed. These checks do not validate the planned hardware work.

## Update 2026-11-14 — scoring gap revision

- Revised the execution plan using the user-provided gap summary and pinned event,
  Studio/trainer, SmolVLA and Runtime sources. The linked external report could not be
  fetched; its unquoted sections were not reviewed.
- Made calibration → teleoperation → first Studio recording the immediate critical
  path. Selected defect-label-to-fixed-task mapping with behavioral verification,
  and Studio-managed 5090 remote training as the preferred integration path.
- Added device allocation, power/temperature/energy measurement boundaries, explicit
  OpenVINO PhysicalAI Runtime/Suite evidence, and a stratified clutter/shift/occlusion
  evaluation. Both scoring tables remain attributed pending organizer confirmation.
- Capped optional twin work at G3a and 4 person-hours after core gates; moved Gemini/RL
  tasks to a deferred plan. Updated README and training guidance. Documentation only;
  no runtime setup, model training, deployment or hardware access occurred.
- Validation: 57 local document links checked, 54 tests passed, Ruff lint/format and
  whitespace checks passed. Hardware, trainer and Runtime integration remain planned.
- Audit against the full gap analysis: plan matches the PDF deliverables and both rubrics;
  added W2.9 (re-inspection after placement when a detection may be wrong) and removed an
  unreachable report link. 59 local document links resolve. Tests and Ruff were not rerun
  for the audit; the last recorded run is the one above.

## Update 2026-11-14 — hardware bring-up: calibration and teleoperation

Shared Ubuntu workstation, branch `docs/hardware-bringup-status`. Details, register values and
revert values: [handoff](handoffs/2026-11-14-hardware-bringup.md). Supersedes "arms uncalibrated"
in the earlier entries and in plan §3.1.

- **Single checkout:** the workstation runs everything from `~/junction` (this repository, submodule
  at `17714488`). Studio starts from the submodule's `application/docker` compose under project name
  `docker`, using the prebuilt `physical-ai-studio-xpu:main` image (not built from the pinned source).
- **Studio project** "Defect Sorting (Intel Challenge)": Follower `5AAF262737` (clamped), Leader
  `5AE7045026`; Studio resolves them by serial because `/dev/ttyACM*` numbers change on re-plug.
  Environments: `Sorting cell` (both arms + wrist/front/top cameras) and `Arms only (teleop test)`.
- **Follower motor IDs were reversed** (base = 6 … gripper = 1). Renumbered to 1–6 through temporary
  IDs with torque off; verified by moving joints by hand and reading which ID changed.
- **Both arms calibrated** with Studio's wizard. Wrist roll uses the full-turn range [0, 4095] on both
  arms (board and Studio copy), so the same wrist twist maps to the same normalized value.
- **3D preview caveat:** the setup wizard feeds normalized values to the model as degrees (wrist roll
  shows ~56 % of the real rotation); the regular viewer maps them onto the URDF limits (wrist roll
  −157°…+163°). A wrist mismatch in the preview is not by itself a calibration error.
- **Follower base motor** carried gripper-style protection (max torque 500, protection current 250,
  overload torque 25): Studio's driver writes those to whichever servo has ID 6, and the base had
  ID 6 before the renumber. Reset to the stock body-joint values (1000 / 310 / 80).
- **Teleoperation works** (user-observed, 2026-11-14 morning). Two earlier attempts failed about 1 s
  after enabling (follower "Sync read failed with comm result −6"), while the follower bus was healthy
  at idle (597/597 reads at 30 Hz). It worked after the follower power connector was reseated and the
  USB devices were split. Root cause not proven; leading explanation is a supply dip on the first large
  move, since the driver sends the leader pose with no slew limit (`goal_time` is ignored).
- **USB:** one USB 2 hub could not carry wrist + front webcam + D415 (the webcam failed to allocate
  bandwidth at every format). With two hubs on two laptop ports, all three streamed together
  (D415 colour 640×480 at 29 fps, still enumerating as USB 2.1).
- The workstation keeps running with the lid closed (lid switch ignored, idle suspend off).

Not done: camera and bowl positions frozen, first Studio recording, check of leader/follower wrist
neutral agreement, real Anomalib data. No dataset, training or policy run has happened.

Next: first recorded episode in `Sorting cell` (plan §3.1), then good-object captures for the Anomalib
baseline. Proposal, not started: top-camera joint calibration with ArUco markers on base and gripper and
a URDF forward-kinematics fit, which would also give the camera-to-robot transform.

## Update 2026-11-14 — Tailscale remote operation plan and kickoff answers

Branch `docs/tailscale-remote-operation`; details and the open questions for the team:
[handoff](handoffs/2026-11-14-tailscale-and-team-questions.md).

- Added [Tailscale remote operation plan](../docs/infrastructure/TAILSCALE_REMOTE_OPERATION.md). Teleoperation
  stays local to the workstation; the tailnet carries Studio (7860), SSH, the alignment/live pages (8090/8091)
  and the Studio → 5090 trainer link. **Not applied**: no tailnet policy, name, tag, SSH service or port
  binding was changed.
- One operator laptop joined the tailnet and reached the workstation (direct after DERP, 8 ms; TCP 22 and
  7860 open, 443 closed). One point-in-time test; the tailnet has no 5090 node yet.
- Open risk: the submodule's Studio compose publishes 7860 on all interfaces with no login. Docker-published
  ports bypass UFW, so the fix is a loopback binding plus `tailscale serve`, which recreates the container
  and needs the on-site lead in a no-recording window.
- Kickoff answers relayed by linan (not independently verified): the final scoring table is the GitHub one,
  a 5090 remote trainer counts, and a defect is a marker-pen cross on a Lego brick. Recorded in
  [DECISIONS](DECISIONS.md); the execution plan's evidence table still needs a remap to the GitHub rubric.
- Nine questions for teammates (W1 owner, first recording, power/slew limit, markers, tailnet admin, 5090
  environment, 7860 window, defect details, remaining kickoff items) are in the handoff.

Documentation only; no hardware, arm motion or training.

## Update 2026-11-14 — marker alignment

Branch `feat/table-frame-alignment` (PR #7); brief: [MARKER_ALIGNMENT.md](../docs/infrastructure/MARKER_ALIGNMENT.md).

- ArUco print sheet, depth-refined marker poses and a live alignment page exist. A level **table frame**
  (table-plane normal as up, anchors 16 → 17 as the x axis) removes the camera's tilt and position, so the
  camera can stay tilted (~29°) and the drift check only fires when something really moved.
- Checked on the real cell: table markers read −4…+3 mm height; anchor distance equal in camera and table
  space (523.0 mm). Self-consistency only; no ground-truth accuracy measurement yet.
- Open: clamp marker (side of the base) not yet detected (image edge / facing away); no reference saved yet;
  marker-based joint calibration is a proposal, not built.

## Update 2026-11-14 — hardware profiling, first round

Branch `docs/hardware-profiling`; full write-up in
[HARDWARE_PROFILING](../docs/infrastructure/HARDWARE_PROFILING.md), scripts in `scripts/hardware_profiling/`.
Inference only on synthetic inputs, run in a separate account on the workstation; no camera, arm or
Studio container was touched.

- **SmolVLA base (451M, 711.9 GFLOPs/chunk, 74 % in the vision encoder):** CPU 2268 ms, GPU 86 ms
  whole policy; vision only CPU 1435, GPU 23.4, NPU 276 ms. The whole-graph NPU compile did not finish
  in 25 minutes (no result). Splitting vision onto the NPU would be slower than the GPU alone.
- **OpenVINO GPU plugin bug:** `Bucketize` returns wrong ids, corrupting the vision position embedding.
  Folding the ids into constants fixes it (GPU matches CPU, cosine 1.00000). The NPU compiler also
  rejects `Bucketize` with an i64 output. Not yet reported upstream.
- **Padim (static 1×3×256×256, synthetic):** CPU 5.0 ms, NPU 6.6 ms with correct maps (corr 0.9986) but
  about 16 % lower scores, so the CPU-calibrated threshold flags no defect. **GPU FP16 (default) is
  numerically wrong** (corr 0.09, all scores 1.0) and the earlier "GPU 1.5 ms" figure measured speed
  only; GPU FP32 is exact but 9–11 ms.
- Not done: our two-camera shapes and dataset statistics, real observations, INT8, text decoder or
  action expert on the NPU, concurrent Anomalib-NPU plus VLA-GPU run.

## Update 2026-11-14 — hardware-free pipeline over a kinematic twin

Branch `feat/offline-closed-loop`; guide and full results:
[OFFLINE_PIPELINE](../docs/infrastructure/OFFLINE_PIPELINE.md). Run on linan's Windows PC (RTX 5090, Intel iGPU);
no arm, camera or workstation was touched.

- New modules: `closed_loop.py` (observe → inspect → plan → execute → verify over replaceable cell, inspector and
  policy), `inspection.py` (score → normal/defective/uncertain, OpenVINO scorer, Padim training), `twin.py`
  (kinematic SO-101 cell with FK/IK, grasp, rendered top/wrist cameras, scripted expert), `offline_pipeline.py`
  and `lerobot_export.py`. 165 tests pass (47 new); Ruff lint and format clean.
- Twin results (pipeline evidence only): 40/40 scripted demos; Padim on twin crops AUROC 1.0; closed loop with the
  Padim OpenVINO inspector 20/20 DONE, 19/20 sorted correctly on CPU and on the Intel iGPU; demos exported to
  LeRobot v3 pass the training contract; SmolVLA expert fine-tune 50 steps on the 5090, loss 0.96 → 0.47.
- Windows blockers found: the `physicalai` CLI imports `fcntl` (worked around with
  `scripts/offline_pipeline/physicalai_without_robot_cli.py`); Application Control blocks fresh DLLs on first import.

Next: real-cell `Cell` adapter and SmolVLA runtime policy adapter (both need hardware/real recordings); replace twin
demos with Studio recordings and twin crops with real good-brick crops; the rest of the chain stays.

Later the same day: the first real Studio recording (2 episodes, green-bowl task only, three cameras, units
normalised −100…100 / 0…100) was copied read-only from the workstation and trained for 50 SmolVLA steps on the
5090 through `training.py run` (train loss 0.94 → 0.16, held-out `val/loss` 0.81). On Windows the plan now uses a
fit-only launcher and PyAV video decoding. A usable policy still needs ~30–50 episodes covering both tasks.

MLflow: a local tracking server runs on the training PC (loopback :5000, store under `artifacts/mlflow/`).
`defect_sorter.tracking` logged today's two training runs (with checkpoints) and two twin evaluations, each tagged
`source` twin/real. Guide: [TRAINING.md](../docs/infrastructure/TRAINING.md#experiment-tracking-with-mlflow).

Model sharing: the studio-smoke-1 SmolVLA checkpoint was exported to OpenVINO (runs on CPU, ~295 ms per 50×6
chunk with synthetic input) and published as the private pre-release `model-smolvla-studio-smoke-1` with a
`release.json` manifest (`defect_sorter.model_release`); a fresh `gh release download` plus `verify` reported ok.
Status `smoke-test`: not for the arm. Guide: [MODEL_RELEASES](../docs/infrastructure/MODEL_RELEASES.md).
MLflow is still loopback-only: `tailscale serve` needs Serve enabled for the tailnet in the admin console, and
direct binding to the tailnet IP is blocked by the PC's inbound firewall (left unchanged).

## Update 2026-11-14 — camera lag in Studio's live view

Diagnosis (read-only): the multi-second lag came from the network, not the cameras. Studio's session socket pushed
four JPEG streams at 20 Hz (~19 Mbit/s) to a laptop on the same venue guest Wi-Fi (ping 27–636 ms, 10% loss);
every session that day logged 0.4–15 s send stalls. Camera side measured tens of ms (D415 bridge: read 26 ms, depth
image 7 ms, encode 1 ms, local HTTP 0.4 ms). Added `docker/studio-preview.override.yaml`, which mounts a patched
`runtime_ws.py` plus `preview_limits.py` into the upstream image (no rebuild) and caps the preview at 10 Hz / JPEG 60.
Fix and recreate command: [TROUBLESHOOTING](../docs/infrastructure/TROUBLESHOOTING.md). Wired Ethernet or the
workstation's own screen remains the first choice.

## Update 2026-11-14 — robot localisation and inverse kinematics

Branch `feat/base-localisation-ik` (on top of PR #9). Plan: geometry (top camera, ArUco, calibration, IK) moves
the gripper above the brick and to the bowl; a wrist-camera ACT policy does only the grasp, so moving the robot
base, the front camera or the bowls needs no new training.

- Joint calibration run on the real follower: lift +1.2°, elbow −6.6°, wrist flex −2.4° (26 poses, RMS 4.0 mm /
  4.4°). Kept in our kinematics, not in Studio's calibration. Details in
  [MARKER_ALIGNMENT.md](../docs/infrastructure/MARKER_ALIGNMENT.md).
- Marker 15 (40 mm) is flat on the follower base plate; `robot_pose` links it to the base so `locate` finds the
  robot after a move.
- `kinematics.inverse`: tool point + approach direction + wrist roll → joint angles within URDF limits, with an
  explicit `reachable` flag. Synthetic round-trip tests only; never commanded on the arm.
- Studio dataset **grasp** created (project "Defect Sorting", environment "Sorting cell", task "Grasp the brick
  and lift it."): short episodes from a jaws-down hover ~8 cm above the brick to the lifted brick.
- `motion.py` / `sorter-move`: plans a jaws-down move of the tool point (IK, rise first when low, ≤10°/s by
  default, hard cap 30°/s), checks every waypoint (tool never lower than 2 cm once below it, elbow/wrist joints
  ≥1 cm, reach ≤30 cm, servo ranges) and, only with `--go`, executes it: goals set to the present position before
  torque comes on, stop and hold when a joint lags more than 10°, no retries, torque stays on at the end.
- Dry run on the real follower (reads only): from rest (tool 9 mm up) to 6 cm above a point 22 cm out → plan ok,
  160 steps, 8 s. Jaws-down hover is limited by the model's 95° wrist-flex stop: about 8 cm high at 18–22 cm out.
- First real move (`--go`, user's go, someone at the arm): rest → 6 cm above (323, 100) mm in 8 s at 10°/s, no
  stop; joints within 1° of plan except the elbow, 2.4° short (gravity sag). Tip error not measured yet: the top
  camera cannot see the jaw tips or marker 4 in a jaws-down pose. The wrist camera sees the table, the bowl rim and
  the jaw tips from the hover pose. Next accuracy check: hover above table marker 12 and read its offset in the
  wrist image.
- Open: grasp recordings, ACT training on the wrist camera, Anomalib, brick target from the top camera.

## Update 2026-11-14 — `armkit` library: automatic guarded calibration

- New uv workspace member `packages/armkit/` (no reference to this project): generic revolute-chain model and URDF
  loader, sphere collision model fitted from Studio's SO-101 follower URDF meshes, staged parking/sweep planning,
  contact guard (rapid load rise / ceiling / stall) with step-back instead of failure, leashed end-stop search,
  guarded path playback, Feetech adapter, simulated bus, LeRobot/Studio-format calibration files, `armkit-calibrate`.
- `defect_sorter.kinematics` is now a thin wrapper over it; its existing tests pass unchanged (cross-check of FK/IK,
  tool pose agrees with the old table to 1e-11 m).
- Dry run `armkit-calibrate plan` finds a collision-free plan for every SO-101 joint end from Studio's rest pose; the
  shoulder-lift forward swing is the tightest (two stages, 0 mm margin).
- **Not run on the real arm.** Thresholds, torque limit and the rest pose (Studio wizard "home") are starting values.
  First hardware run, only when asked: `armkit-calibrate run --port ... --only gripper --go`, watching the load.
- Wrist roll keeps its existing homing offset and gets 0..4095 (see the full-turn decision).
- Known: `tests/test_training.py` has two failures because the submodule checkout (`8f13241`) is not the pinned
  commit (`1771448`) and lacks files those tests read; unrelated to this change.

## Update 2026-11-14 — new cell layout, recalibration, sort-v1 dataset

- The cell was rearranged (white paper, pink bowl left, green right, anchors 16+17 with 13+14 as a spare pair).
  Recalibrated with 14 hand-held poses (anchors 16+17): lift +1.6°, elbow −4.7°, wrist flex −1.4° (wrist only
  weakly constrained: roll covered −53…−3°). RMS 2.8 mm. Marker 15 re-linked; the link agrees with the old layout
  within 2 mm sideways / 7 mm in height. Alignment reference saved (`data/alignment/reference-sort-v1.json`, 10
  markers). Old-layout files kept under `data/calibration/old-layout-2026-11-14/`.
- Studio dataset **sort-v1** (`7a4864a0-f49c-4fc5-adaa-5f88b74eea58`) created; dataset card and the 56-episode
  recording plan: [docs/datasets/SORT_V1.md](../docs/datasets/SORT_V1.md). One dataset serves the whole-task
  policy, SmolVLA (task text per episode) and the hybrid's grasp clips (cut at a 1 s hover pause).
- `episodes.py` / `sorter-episodes`: reviews episodes (task text, cameras, grasp/release, hover pause) and finds
  grasp-clip frame ranges. On practice-1: 2 of 2 usable, 1 with a detectable pause (no pause was asked for then).
  Writing the cut clips as a new dataset is not built yet.
- First hardware contact (2026-11-14, user-authorised, follower gripper only, `armkit-calibrate check`): reads of all six
  servos work. The check stopped before any motion: the gripper's `Min_Position_Limit` write was not acknowledged
  (servo busy after an EEPROM write) although it took effect. The gripper's calibration and torque were restored and
  verified identical to the saved backup for all six joints. Fix: EEPROM writes are now verified by read-back (a lost
  acknowledgement with a matching value is accepted). The gripper search itself has not run yet.
- Hardware result (2026-11-14, follower gripper, `armkit-calibrate check`, user-authorised, nothing stored): both hard
  stops found and each confirmed by two contacts, reproducible to the tick over 4 runs: upper 3501 / lower 2031 vs the
  stored 3492 / 2040 (+/-9 ticks = 0.8 deg). Stored calibration of all six joints verified identical to the backup after
  every run (original backup also in `.local/`). The attempt exposed servo behaviour now handled in `armkit.feetech`:
  EEPROM writes are acknowledged late or dropped (verify by read-back, repeat the write), replies go missing or come
  short (bounded read retry), torque changes read back late, a lone corrupted temperature byte must not abort a run.
  Remaining: the gripper ends a few ticks (~0.7 deg) short of its start after each check; full `run` not tried on hardware.
- `armkit-calibrate check` now gates body joints on the collision model: the arm's pose is taken from the stored
  calibration and the joint's sweep must be clear, otherwise nothing is moved. On the real follower (pan -37, lift -38,
  elbow 75, wrist flex 29, roll -17 deg) the model puts the gripper link 19 mm below the floor, so a wrist-flex check was
  refused (verified live, read-only). Checking wrist flex needs the other joints parked first, i.e. the full procedure's
  parking moves on hardware, which have not been run. The check also returns at the joint's normal torque limit now.
- Hardware result (2026-11-14, follower shoulder_pan, `armkit-calibrate check`, user-authorised, nothing stored): both
  ends confirmed by two contacts each: lower 1304 / upper 3234 vs stored 1253 / 3451 (+4.5 deg / -19.1 deg). The upper end
  is 19 deg short of Studio's stored range: either a real stop or an obstruction on that side (cable, camera mount,
  clamp); to be looked at physically. Calibration of all six joints verified identical to the backup afterwards; pan
  returned within 2 ticks of its start. The gate allows a sweep that is no closer to a collision than the arm already is.
- Hardware result (2026-11-14, follower shoulder_lift, `check --ends lower --torque-limit 500`, user-authorised): lower end
  found at 838 (stored 839, -1 tick), confirmed by two contacts; calibration of all six joints identical to the backup
  afterwards, lift back within 1 tick of its start. The upper end (forward swing) is refused by the collision model from the
  current pose (gripper link already 19 mm under the floor in the model; the forward swing would meet the table), so it needs
  the other joints parked first. `check` takes `--ends lower|upper` for exactly this case.
- Correction (user, 2026-11-14): the pan's upper stop at 3234 was not the clamp; the arm hit nothing there. Cause unknown
  (cable drag / friction / false contact). `check` now reports every contact (kind, load, position) so it can be judged.
  Going further to Studio's stored 3451 would hit the clamp unless the rest of the arm is straightened first.
- New `armkit-calibrate move --set joint=deg ...` (dry run by default; `--go` runs it with the guarded path mover at a
  limited torque). Planned, not run: shoulder_lift/elbow_flex/wrist_flex to 0 deg from the current pose is a direct
  150-waypoint, ~8 s path whose closest approach is the start pose itself (gripper 18 mm under the floor in the model).
  The model does not contain the clamp, camera mounts or people.
- Hardware (2026-11-14, user-authorised): `move --set shoulder_lift=0 elbow_flex=0 wrist_flex=0 --go` ran: the arm is now
  straightened (lift +0.3, elbow +3.6, wrist flex +1.5 deg; elbow ends 41 ticks short, the extended arm sags a little at
  600 permille). No contact events; torque limits restored to their old values; calibration of all joints identical to the
  backup. Pan upper-end check from this pose with contact diagnostics is the next step.
- Hardware results continued (2026-11-14, user-authorised, nothing stored):
  - pan upper end again from the straightened arm: 3231 (stall, load 148, both contacts), so it does not depend on the
    arm's pose; Studio's stored 3451 is not reachable. Real pan travel about 1304..3231 (~170 deg, Studio assumes ~193).
  - wrist_flex both ends: 874 / 3192 vs stored 874 / 3185.
  - elbow_flex lower-end attempt: the FOREARM DROPPED about 42 deg twice, because `check` switched the elbow's torque off
    to widen its limit registers while the elbow held the forearm (holding load ~170 permille). Nothing was reported hit;
    the arm now holds at elbow +45 deg; calibration unchanged. Fixed: a joint with holding load > 40 permille never has
    its torque switched off; it is searched inside its stored range and ends beyond it are reported.
- New `armkit-calibrate measure` pipeline (bottom-up, automatic parking per end, one-end checks, return to start,
  proposed calibration file; stores nothing). Simulation-tested (true pose never collides); not yet run on hardware.
- Remaining hardware checks: elbow both ends (inside stored range), shoulder_lift upper end (needs parking), then a full
  `measure` run. Possible check before widening a loaded joint's limits: whether the STS3215 accepts EEPROM writes with
  torque on and Lock=0 (not tried; needs explicit permission).
- Hardware (2026-11-14): first full `measure` run. pan 1304/3231, wrist flex lower 874, gripper lower 2031 reproduced;
  but the run ended with the arm NOSE DOWN ON THE TABLE (lift +103 stored-frame deg) and every move to raise it stalled.
  Root cause (user photo): the planner assumed stored-range midpoints are the model's zeros; on this arm the elbow is off
  by roughly 90 deg, so the planner thought the arm was stretched up when it was L-shaped, and tipping the shoulder
  forward drove the gripper into the table. Also found: a garbled read of the gripper's stored calibration was written
  back (offset 1281 / min 1303); restored and verified identical to the backup.
- Fixes: planning (`measure`, `move`, body-joint `check`) now refuses without a measured `ModelFrame`
  (`armkit-calibrate frame --pose so101-zero [--release] --go`); hardware margins at least 15 mm; stored calibration is
  only believed when two reads agree and the pipeline reuses one verified copy; the end of a run verifies the stored
  calibration is unchanged.
- Next (needs the operator): free the arm from its nose-down pose (hold it while torque is released), set it in the
  SO-101 zero pose by hand and record the frame; then re-run `measure` with `--frame`.
- Hardware (2026-11-14): reference-pose frame recorded by hand (offsets pan +38.9, lift -26.2, elbow +14.6, wrist flex
  -5.3, roll +52.9 deg). Second full `measure` run: pan 1303 / 3231 again; then the gripper tip hit the table during a
  sweep because this arm's WRIST FLEX turns the opposite way to the URDF (photo: tip on the table where the model put it
  13 cm up; a reversed wrist puts it at 0.7 cm). A one-pose frame cannot see a reversed joint. Stopped on the operator's
  word; wrist torque limit restored, its limit registers still widened (0..4095) pending a supported restore.
- Fixes: frames now carry per-joint directions, checked with a second hand-held pose (`frame --refine frame.json --pose
  so101-second`); planning refuses unless every chain joint's direction is checked; all plans keep 8 cm of air above
  the table (`--table-clearance`).

- `depth_bridge.py` / `sorter-depth-bridge`: owns the D415 and serves colour + a depth image as MJPEG; Studio records
  them as IP cameras `top_rgb` and `top_depth` (environment "Sorting cell + depth"). Measured on the workstation: 29.8 fps
  camera loop, ≈30 fps read from inside the Studio container. Not yet verified: a full Studio recording through the IP
  cameras.
  - **sort-depth-v1** (grey `height` image at 0–10 cm, not 6 cm as noted before) was deleted from Studio with its
    environment and the `top_rgb`/`top_depth` cameras; it held no episodes.
  - Depth encoding v2 (2026-11-14): default `layers` mode (R 0–4 cm, G 0–30 cm, B valid), table plane held from the
    first frame and saved/checked with `--plane`, `--crop` on colour and depth, 4:4:4 JPEG, `motion` camera filter
    profile (`D415Camera(filters=..., preset=...)`). Ran once on the camera from an uncommitted copy in
    `~/depth-v2` on the workstation (`~/junction` is on `main` without the bridge): brick 1.91 cm read as 1.9 cm,
    plane `data/depth/plane-v2.json` (92 % inliers). Studio: environment "Sorting cell + depth v2", IP cameras
    `top_rgb_v2`/`top_depth_v2` at 512×416, dataset **sort-depth-v2**, no episodes yet. Next: check the gripper stays
    inside the crop over the whole brick grid, record, and get the branch merged so the workstation runs it from
    `~/junction`. IDs in `docs/datasets/SORT_V1.md`.
- `uvc_controls.py` / `sorter-camera-lock` (2026-11-14, applied on the workstation, every control read back ok):
  profile `config/camera_controls.json` locks `front` (Webcam; was auto exposure, auto WB, continuous autofocus,
  **60 Hz**) and `wrist` (USB2.0_CAM1; was auto exposure, auto WB, **dynamic framerate on**) to manual exposure 30 ms
  (a multiple of the 10 ms mains period, under the 33 ms frame), gain 0, 50 Hz; front 4600 K (neutral on the table,
  mean grey 121 vs 147 on auto, nothing clipped; its gain has no visible effect), wrist 3500 K (closest to neutral;
  4600 K turned it green); front focus fixed at 270 (its last autofocus position). The wrist values were judged
  with the gripper pointing at the ceiling: re-check them with the camera looking at the table. Studio does not
  set these controls (its USB payload passes only width/height/fps). Both cameras delivered ≈22–23 fps in a short
  OpenCV grab, auto or locked: check the real recorded fps. Studio's stored USB bus fingerprints for both cameras
  no longer match their ports.
- Finding (2026-11-14): Studio's robot worker was connected to the follower while armkit used the same serial port
  (Studio log: 'Sync read failed with comm result -7', worker stopped 15:37). Two processes on one bus garble each
  other's packets: the likely cause of the lost acknowledgements, short replies and the garbled calibration read seen
  earlier. Before any armkit run: disconnect the follower in Studio (and close the tab that auto-reconnects) and check
  `sudo fuser -v <port>` shows nothing.
- New: `armkit-calibrate frame --directions --refine frame.json --go` (release the arm, move each joint by hand in its
  described direction, directions read from the sampled readings) and `measure --preview` (the whole pipeline on a
  simulated copy of the arm built from its stored calibration and readings; only reads the arm).
- Hardware (2026-11-14, user-authorised): joint directions recorded by hand (`frame --directions`): all same as the
  URDF except wrist_roll (reversed); the earlier "wrist flex reversed" reading of the photo was wrong. Elbow lower end:
  three runs failed because the elbow (resting load ~200) does not move until its goal leads by ~5 deg, more than the
  3 deg leash, so the guard saw a stall; fixed with droop compensation (goal register vs position), an adaptive leash
  up to 12 deg and a stall threshold above the resting load. After the fix the elbow travelled its whole stored range
  to 875 with no contact (stop at or beyond Studio's value). Chain joints now never lose torque and search at their
  normal torque limit; the extra table clearance applies to the far links only.
- Per-joint results so far (stored-calibration ticks, nothing stored): pan 1303..3231 (stored 1253..3451); lift lower
  838 (839); elbow lower >= 875 (875); wrist flex 874 / 3192 (874 / 3185); gripper 2031 / 3501 (2040 / 3492).
  Not reachable with the table as an infinite plane: lift upper (forward), elbow upper, wrist flex upper.
- Hardware (2026-11-14, user-authorised): first complete `measure` run finished and wrote
  ~/armkit-run/calibration-proposed.json on the workstation (pan 1322..3229 and gripper 2060..3508 proposed; others
  kept at Studio values). It left the arm leaning fully back: lifting a near-horizontal arm off its back stop looked
  like a stall to the path mover (the joint read light while resting on the stop). The operator lifted it by hand;
  calibration still identical to the backup. Also found: a garbled read of the gripper's torque limit was written back
  as 62721 (fixed to 500; torque limits now need two agreeing in-range reads, and out-of-range writes are refused).
- Fix: the path mover treats every chain joint as possibly loaded (resting-load-relative stall threshold, up to 12 deg
  of lag), as the end search already did.
- Still open: lift forward end, elbow and wrist-flex upper ends point into the table; measurable only if the arm can
  point off the table edge (`--table-area`), otherwise Studio's values stay.
- Conclusion (2026-11-14): the base rotation is mechanically limited to about 170 deg, all of it over the table (operator).
  That matches the measured pan range 1302..3249 (~171 deg), so Studio's stored pan range (1253..3451) is wider than the
  arm can turn. The arm cannot point past the table edge, so shoulder-lift forward, elbow upper and wrist-flex upper
  cannot reach their stops without touching the table; they keep Studio's values. Result of the pipeline:
  ~/armkit-run/calibration-proposed.json on the workstation (pan 1322..3229, gripper 2060..3508, the rest unchanged);
  nothing written to the servos or Studio. Storing it later: `armkit-calibrate restore --from <file> --go` with the arm
  supported, then update Studio's stored copy.
- Complete proposed calibration (all six joints) built from every end measured this session with `armkit.measure.propose`
  (measured ends pulled in by 20 ticks, unmeasured ends keep Studio's value, homing offsets unchanged):
  ~/armkit-run/calibration-complete-proposed.json on the workstation, copy in .local/. pan 1322..3229, lift 858..3191,
  elbow 875..3081, wrist flex 894..3172, gripper 2060..3508, roll 0..4095. Not written to the servos or Studio.
  Open point: the gripper's upper end read 3501 in four checks but 3528 in the last full run; recheck before storing.
- Second complete `measure` run (2026-11-14, user-authorised) finished cleanly and returned to its start pose: pan
  1301..3249, gripper 2040..3528, elbow and wrist-flex lower ends reach the stored limits without contact. Ends that
  cannot be reached on this setup are now NOTES, not failures. Gripper recheck on the clean bus: closed 2040 every time,
  open end compliant (3501 / 3528 / 3536 depending on push force), so the proposal uses the lowest clean value.
  Final proposal (calibration-complete-proposed.json, copy in .local/): pan 1321..3229, lift 858..3191,
  elbow 875..3081, wrist flex 894..3172, gripper 2060..3508, roll 0..4095; homing offsets unchanged; not stored.
- Rule (AGENTS.md): calibration never falls back to Studio's stored limits. `check` now widens a weight-bearing
  joint's limits with torque ON (EEPROM lock opened, limits verified by read-back, torque untouched) so it can search
  past the stored range; if the servo refuses, the end is an issue (`NOT MEASURED`), not a note. First hardware run
  (2026-11-14, user-authorised): the STS3215 takes new limits with torque on. Elbow lower end measured at 870
  (stored 875): its own stop with the forearm straight up, two contacts within 2 ticks, nothing touched; limits and
  calibration restored. Shoulder-lift forward (upper) end measured at 3197 (stored 3191) from a pose with the elbow
  folded up and the wrist down (`check` with `--table-clearance 0.04`: the forearm's elbow end is the lowest point and
  depends almost only on the shoulder angle); the gate now accepts a sweep the model clears only partly, if the clear
  part goes past the stored end. Shoulder-lift lower 838 (earlier run with widened limits) is a real stop.
  Open ends: elbow upper, wrist-flex both, gripper open.


## Update 2026-11-14 — brick hover target from the top camera

- New `targeting.py`: brick top-face pose in the table frame (centre, long-axis yaw, size) from one `detect_scene`
  object. Only top-face pixels are used, so the side face the tilted camera sees does not pull the centre towards it
  (a synthetic tilted view shows the naive blob centre off by more than 3 mm; the top-face centre within 1.5 mm).
  `select_brick` skips tall or large objects and asks for `--near X Y` with several bricks; `combine_poses` takes
  medians over frames, yaw averaged as an undirected angle.
- `grasp_roll`: wrist roll that closes the jaws across the brick's short side, jaws down, nearest the current roll
  inside the joint range; checked against forward kinematics. The two solutions are about 177°, not 180°, apart
  (tool point off the roll axis). The jaw closing axis (`JAW_AXIS_TOOL`, tool x) is read from the URDF and not yet
  confirmed on the gripper.
- `sorter-move --above-brick [--near X Y] [--height mm]`: 10 top-camera frames with the arm at rest → brick pose →
  hover target and grasp roll → the existing checked plan; dry run unless `--go`. Not yet run on hardware (no camera
  or arm used).
- Next, with the user's go: dry run `--above-brick`, then a real hover and a wrist-image check of the jaw direction
  and the tip offset; then the wrist-camera correction step (reference image, pixel offset → table correction).
- Full suite: 499 passed, 2 failed in `test_training.py` because the Studio submodule's working tree is missing
  `library/` (staged deletions inside the submodule, not from this change).

## Update 2026-11-14 — initial sorting dashboard

Work prepared on `feat/sorting-dashboard`; check Git and the remote for publication state. Added a standalone dashboard in
`frontend/` with an illustrative cell, synthetic crop, score gauge, decision panel and sorting stages.
Demo scenarios cover normal, defective, uncertain and arm-fault states; missing timings remain blank.
The v1 telemetry model keeps backend decisions authoritative and distinguishes demo, twin, replay and real sources.

The [dashboard guide](../docs/infrastructure/DASHBOARD.md) records local startup, the snapshot fields,
the in-page adapter boundary and backend integration tasks. README and AGENTS test ownership are updated.
The initial UI has no live transport, calibrated real-joint rendering or hardware command integration.
No camera, arm, Studio service or shared workstation was touched. Validation: thirteen frontend regression tests passed;
`uv run pytest -q` passed 165 tests in 24.04 s; `uv run ruff check src tests` passed; and
`uv run ruff format --check src tests` reported 34 files already formatted. Module syntax checks and local
preview HTTP 200 passed. Headless Firefox could not open its temporary profile; browser visual and interaction
QA remains unverified. The initial fetch was blocked by GitHub 403. After account authentication was fixed,
the branch was rebased onto the latest main, preserving the armkit, camera, dataset and training changes.

The PR review added complete-image loading with newest-frame coalescing, error recovery and resets, avoiding
cancelled downloads at high telemetry rates. README now separates checkout setup, the local dashboard,
hardware-free generation/evaluation, a fresh CPU Studio deployment, shared-workstation access and training plans.
It documents Git LFS, Python/Node prerequisites, expected outputs and the working-directory 404 fix.
README smoke checks passed with temporary outputs: two twin demonstrations completed, crop generation wrote
20 training and eight test images, two oracle-evaluated attempts completed with `mode = twin`, and the example
training plan reported missing data and null metrics without creating a run. These are pipeline checks, not
learned-policy or physical-task evidence. All 43 local README/dashboard links and anchors resolve.

The user reports a Studio-volume dataset `datasets/50815c02-…`, LeRobot v3.0, robot type
`SO101_Follower`, containing two episodes described as simulated. The newer offline pipeline guide describes the
same shortened identifier as the first real recording used in a training smoke run. Confirm the full identifier and
provenance before replay integration; this dashboard work has not accessed or validated the files. Next: obtain
the export location, inspect metadata, joint units, media and time alignment, then add replay preserving confirmed
source provenance. No anomaly scores, model timings or verified outcomes may
be inferred merely from the presence of a recording; the reader and calibrated playback remain unimplemented.

After rebase onto main `79e38b9`: 573 Python tests passed, one existing optional PyArrow episode test skipped
(45.78 s); thirteen frontend tests and four module syntax checks passed. Ruff checks over `src tests packages`
passed, with all 89 files formatted. No hardware was touched during verification.

## Update 2026-11-14 — dashboard telemetry corrections

An unavailable verified outcome no longer marks a completed cycle as placed or confirmed. Snapshot thresholds and
joint readings may be null, with absent thresholds shown explicitly and without coloured gauge arcs; joint units
must be null with absent joints. Regression tests cover unverified completion and missing measurements. Dashboard
transport and real robot integration remain unimplemented.

Validation on Windows: 15 frontend tests passed; Ruff check and format check passed. After initializing the pinned
Studio submodule, the full Python suite reported 572 passed, one skipped and one failure: the existing
`test_find_device_picks_the_capture_node_of_the_named_camera` compares a Windows-formatted `Path` to a POSIX path.
No hardware was touched.

## Update 2026-11-14 evening: sort-depth-v2 dataset and SmolVLA training

- Studio dataset `sort-depth-v2` (35 episodes, 37,515 frames, 23 green-bowl + 12 pink-bowl, cameras front/wrist
  640×480 and top_rgb_v2/top_depth_v2 512×416, AV1) was copied read-only to the RTX 5090 training PC. No long frozen
  video runs (longest 2 repeated frames); top_rgb_v2 effectively ~23 fps. Older Studio datasets (practice-1, sort-v1,
  sort-depth-v1) are no longer listed in Studio; check whether that was intended.
- Run `sort-depth-v2-3k` (SmolVLA expert, 3k steps, 19 min): train loss 0.31 → 0.15 per 500-step average, still
  falling; shorter than one epoch, so no validation and only `last.ckpt`. Logged to MLflow (`defect-sorter-training`).
- Run `sort-depth-v2-10k` started 20:24 UTC with `configs/training/smolvla_sort_depth_v2.toml` (validation episodes
  6, 15, 19, 25, 30). Handoff and what to do when it finishes:
  [handoff](handoffs/2026-11-14-camera-latency-and-sort-depth-training.md).

## Update 2026-11-15 — dashboard host performance and product intro

Prepared on the existing `feat/sorting-dashboard` branch at the user's request. No commit or push requested.

- Added `sorter-dashboard`, a loopback-by-default server for frontend assets, one-second cached
  `/api/system` samples and optional read-only `/api/telemetry` from `--telemetry-file`.
- Linux resource cards show CPU, RAM, visible Intel GPU clients (i915 nanoseconds and Xe busy/total cycles),
  NPU job activity and CPU package watts where readable. Counters use procfs/sysfs only, with null values for
  unavailable/reset/restricted data. Charts retain 60 samples; stale readings clear. GPU client coverage and
  server-host scope are explicit. Monitoring does not prove model execution or correctness.
- Inference median/p95 use up to 60 measured completed episodes per source/device, deduplicated by episode id;
  demo values never contribute. Actual timings/device reporting still require backend instrumentation and a
  v1 snapshot producer. The file bridge is transport, not a real-cell adapter or frame proxy.
- Added **Meet PhysicAI**, an optional four-chapter animated SVG introduction: missed-defect business costs,
  inspection/sorting, human review and local Intel inference. Browser narration has an English voice selector,
  captions, transcripts, silent/error fallback, cancellation on close and reduced-motion support. No recorded
  narration/video file is bundled; voice quality depends on the browser/OS. The local voiceover app service
  was unreachable, so no external voice asset was produced.
- Updated README, dashboard guide and AGENTS architecture/test ownership. New deterministic regression tests
  were run red then green for resource math, duplicate handles/cycle counters/counter dips, HTTP path isolation,
  snapshot reads, stale data, timing provenance and intro playback/cancellation/error fallback.

Validation: `uv run pytest -q` **583 passed, 1 skipped (47.76 s)**; `node --test frontend/tests/*.test.mjs`
**22 passed**; `uv run ruff check src tests packages` passed; `uv run ruff format --check src tests packages`
reported **93 files already formatted**. Module syntax/whitespace checks and local HTTP smoke checks passed.
Firefox could not open its temporary profile, so browser visual/interaction and voice-quality QA remain
unverified. No shared workstation, cameras, arm or inference workload was touched; Linux hardware sampling
remains to be verified on the inference laptop. Launch from the checkout root with `uv run sorter-dashboard`.

## Update 2026-11-15 — intro playback fix and portable system resources

Supersedes the intro voice-selector and non-Linux resource limitations in the previous entry.

- Reproduced Chromium's `Illegal invocation` on Play: default browser timers were called with the player
  as their receiver. Added a failing receiver regression and fixed timer wrappers.
- Replaced speech synthesis with four bundled English PCM narration clips and one fixed default voice.
  **Meet PhysicAI** opens paused; **Play intro** starts audio. Removed the voice selector. Pause/resume,
  chapter navigation, replay, close/Escape and silent captions have explicit handling. The server now
  serves WAV and byte ranges; browser end-seeking initially exposed the missing range support, covered
  by a failing HTTP regression before implementation. Transcript-driven regeneration is in
  `scripts/build_intro_audio.mjs` (macOS-only build tooling; playback is portable).
- Added small `psutil` dependency/lock update for native CPU/RAM on macOS/Windows and other supported OSes,
  with OS/CPU/core identity. Linux retains procfs/sysfs accelerator readings. Unsupported non-Linux
  GPU/NPU/power stay null and are not labeled Intel. Native counter failures preserve other available data.
- Updated README, dashboard guide and AGENTS test/architecture notes.

Validation: new failures observed before fixes; **27 frontend tests passed**; full `uv run pytest -q`
**587 passed, 1 skipped (47.94 s)**; Ruff check passed; Ruff format check reported **93 files already formatted**.
Module syntax and four non-silent PCM asset checks passed. Actual Chromium checks (speech synthesis disabled)
passed for live macOS CPU/RAM, all chapters/audio, pause/resume, seeking/completion, replay, Escape, reopening,
silent mode and mobile width with no page errors. Desktop/mobile screenshots reviewed. Windows counters have
synthetic coverage only; real Intel Linux accelerator readings remain unverified here. No robot, cameras,
Studio service or inference workload was touched. The user requested an additional commit and publication
to the existing dashboard pull request on 2026-11-15; use Git and the PR to check synchronization state.
## 2026-11-14: simulation augmentation and LLM planner (Linan)

- MuJoCo sorting cell in WSL2 (`scripts/sim/so101_sort_sim.py`). It simulates once and stores full 3D state per frame, then renders many random but plausible cameras into the `offline_pipeline` format. The real layout prior comes from the first and last frames of sort-depth-v2. Calibration of the top camera from real data (`config/sim/`, `scripts/sim/calibration/`) is coarse: about 1 cm near the brick; the joint fit `config/sim/top_camera_joint.json` (height 0.513 m, tilt 26.1°, IoU 0.38, grasp median error 12.5 px) is the one to use.
- `defect_sorter.planner`: closed action set, deterministic validator, rule fallback. Local Qwen (vLLM) takes about 0.6 s per decision, and the validator caught 3 unsafe proposals.
- `lerobot_export.py --video --robot-type` writes cameras as video like Studio recordings.
- Open: expert grasp success, the 30 fps batch plus export, and the front camera fit. Details are in `docs/sim/SIM_AUGMENTATION.md` and `memory/handoffs/2026-11-14-sim-augmentation-handoff.md`.
- Full suite: 587 passed, 1 failed (`test_uvc_controls.py::test_find_device_picks_the_capture_node_of_the_named_camera`, which also fails on Windows without this change).

## Update 2026-11-15 — sort-depth-v2 10k run finished

Read from the run directory on the training PC (`artifacts/training/sort-depth-v2-10k/`, Git-ignored) and the local
MLflow server; no new training, camera access or arm motion.

- The run reached `max_steps=10000` and wrote `best.ckpt` and `last.ckpt` (1.7 GB each). MLflow has it as FINISHED
  next to the 3k run.
- Train loss, mean per 2000 steps: 0.280, 0.186, 0.132, 0.101, 0.080; the last step reads 0.025.
- Held-out `val/loss` (5 episodes, one value per epoch of ~4120 steps): 0.292 after epoch 0, 0.303 after epoch 1.
  Train loss kept falling while validation loss did not move, so the model fits the 35 recorded episodes but there is
  no sign yet that it generalises to unseen ones. Loss is not a sorting success rate.
- Not checked: which step `best.ckpt` holds, a comparison with the 3k run (it had no validation), the OpenVINO
  export, a model release, and any run of the policy on the arm (needs a person asking for that motion).
- Open from the handoff: about 10 more pink-bowl episodes to balance the tasks (23 green, 12 pink), and whether
  Studio's older datasets disappeared on purpose.
