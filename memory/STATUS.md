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
