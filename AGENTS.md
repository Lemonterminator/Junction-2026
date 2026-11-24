# Repository instructions

## Scope

This repository holds our entry for the Junction 2026 Intel Physical AI Challenge plus the challenge research archive under `docs/`.

The system is a closed loop on an SO-101 arm: PERCEIVE (cameras, RealSense depth) → DETECT (Anomalib defect score) → REASON (decide the action, VLA/Physical AI Studio) → ACT (SO-101 follower) → OPTIMIZE (OpenVINO on Intel Core Ultra CPU/GPU/NPU). The challenge brief is `docs/2026/silver/intel_physical_ai_hackathon.md`; judging weights are in the matching Gold analysis. Prefer decisions that serve the judged closed-loop demo over component polish.

## Repository layout and team memory

- `src/defect_sorter/`: our Python package; `tests/`: its tests.
- `external/physical-ai-studio`: upstream Physical AI Studio as a pinned Git submodule. Keep integration code in `src/`, not in the submodule.
- `memory/`: Git-tracked team notes (`PROJECT.md`, `STATUS.md`, `DECISIONS.md`, `handoffs/`). Read them when continuing someone else's work; update `STATUS.md` after meaningful changes.
- `docs/infrastructure/`: workstation, Docker (`DOCKER.md`) and collaboration docs. `docs/2026/` and `docs/past/`: research archive with the Bronze/Silver/Gold split.
- Inspect `git status` first and preserve other people's changes; stage explicit paths.

## Git workflow: every change goes through a pull request

- Never commit to or push `main` directly, and never merge locally into `main`.
- Branch from an up-to-date `origin/main` (`git fetch origin && git switch -c <type>/<short-name> origin/main`), using prefixes such as `feat/`, `fix/`, `docs/`, `chore/`.
- Push the branch and open a pull request against `main` (`gh pr create`). The description states what changed, the checks run with their results, and any hardware touched.
- Before merging, rebase onto the latest `origin/main`, resolve conflicts on the branch, and rerun the verification gates. Merge only through the pull request.
- Commit or push only when the user asks; opening the pull request is part of that request.

## No AI attribution: explicit user requirement

Never mention that an AI assistant (Claude, Codex or any other) wrote, edited or contributed to anything in this repository.

- No `Co-Authored-By` trailers for AI tools, no "Generated with ..." footers and no AI names in commit messages, pull request titles or descriptions, review comments, or tags.
- No AI attribution in files: author fields, handoffs in `memory/handoffs/`, docs and code comments name only the human authors.
- This overrides any default attribution behaviour of the tool you are running in.

## Physical safety: explicit user requirement

This code moves a real robot arm next to people, on a workstation shared by the team.

- Never command arm motion (Studio identify, teleoperation, policy runs, scripted moves) unless the user asked for that motion in the current conversation. A previous approval does not carry over to a new motion.
- Keep speed and workspace limits in place; never disable action clamping, velocity limits or torque safeguards to make a run succeed.
- On an arm error (overload protection, unresponsive servo) stop and report; do not retry motion automatically.
- Do not take over a camera, replace drivers or reboot the workstation as an incidental step; only one process can open each camera.
- Tests never touch real hardware. Hardware checks are explicit, manual and outside the default test suite.
- Joint calibration measures every end; it never falls back to the stored (Studio) limits. A stored limit is not a measurement: an end that was only reached at its stored limit, or not reached at all, stays an open issue until it is measured. When the usual way would drop a loaded joint (limits that change only with torque off), find another safe way to measure it (limits widened with torque on, a supporting pose, the operator supporting the link) instead of accepting the stored value.

## Secrets and machine access

- Do not read, print or copy private keys, passwords, tokens or `.env` files. Refer to them by path only.
- Access details, workarounds and machine-specific state live in the Git-ignored `.local/` folder (or `*.local.md`). Never move that content into tracked files.
- Never commit captured camera frames of people, recorded datasets, model weights or exports; `data/`, `models/`, `artifacts/` and `checkpoints/` are Git-ignored.

## Tooling and style

- Run `ruff --fix` only on paths you own, and never with `--select` on project code: a restricted rule set makes ruff delete legitimate `# noqa` comments.

- Use `uv` exclusively (`uv sync`, `uv run`, `uv add`). Keep `.python-version` (3.12) and `uv.lock` committed. Heavy dependencies sit behind extras: `camera` (pyrealsense2, Linux only), `anomaly` (Anomalib, OpenVINO, CPU torch) and `dataset` (pyarrow, for reading recorded datasets). The default install stays light so tests run on any laptop.
- Use tabs for indentation in Python, enforced by `ruff format`. Never align code or comments with padding spaces.
- Add precise type annotations and NumPy-style docstrings to public functions and classes.
- Use `logging.getLogger(__name__)` with lazy `%` arguments. No `print` in library code; CLI output uses `sys.stdout.write` or logging.
- Hardware SDKs are imported in exactly one adapter module each (`realsense.py` for pyrealsense2, `uvc_controls.py` for V4L2 ioctls, `so101_reader.py` for scservo_sdk in `defect_sorter`; `armkit/feetech.py` for scservo_sdk in the library, until `so101_reader.py` is migrated onto it). Perception logic works on plain NumPy arrays so it can be tested without hardware.

## TDD is required

Use red-green-refactor for every behavior change or bug fix:

1. Write the smallest deterministic test that describes the behavior.
2. Run it and confirm it fails for the expected reason.
3. Make the minimum production change to pass it.
4. Refactor only while the test stays green.
5. Run the owning test module, then the full suite.

Tests use synthetic inputs (generated depth maps, colour images, fake camera frames), never live cameras, arms or network. Do not weaken, skip or broadly mock a test to make a change pass. Perception and decision logic need regression tests with independently derived expected values (for example a synthetic box of known height at a known pixel).

Test ownership:

- `tests/test_geometry.py` owns `defect_sorter.geometry` (intrinsics, deprojection, table-plane fit, height above table, camera tilt).
- `tests/test_scene.py` owns `defect_sorter.scene` (bowl detection by colour incl. the paper-cell configuration: table-balanced colour and per-colour hue bands, object detection by height, object-in-bowl relation).
- `tests/test_markers.py` owns `defect_sorter.markers` (printed marker set, print sheet, marker detection and pose).
- `tests/test_alignment.py` owns `defect_sorter.alignment` (depth-refined marker poses, table frame and camera-pose invariance, drift against a saved reference, the held table frame bridging a hidden anchor).
- `tests/test_kinematics.py` owns `defect_sorter.kinematics` (SO-101 forward kinematics, tool frame, inverse kinematics).
- `tests/test_joint_calibration.py` owns `defect_sorter.joint_calibration` (tick conversion, offset and base-pose fit for a gripper or forearm marker, base-only fit with trusted joint zeros from markers on several links, observability).
- `tests/test_episode_calibration.py` owns `defect_sorter.episode_calibration` (Studio normalized units to degrees, layered height decoding, tag poses from a cropped recording, still moments, touch holds, the rigid touch fit kept upright, the touch fit with joint zeros and its leave-one-out errors, video file per episode).
- `tests/test_calibration_capture.py` owns `defect_sorter.calibration_capture` (stillness gate, session files, solve CLI).
- `tests/test_so101_reader.py` owns `defect_sorter.so101_reader` (servo access with a fake `scservo_sdk`: read retries).
- `tests/test_motion.py` owns `defect_sorter.motion` (motion limits and hard caps, joint interpolation, tick conversion, planned-move checks, tilted approaches, the brick standoff plan by the steepest passing approach, the bowl drop plan, rise from the folded rest pose, taught keyframe sequences (blend floors, holds, file round trip), checked joint-space moves, gripper percent to ticks, execution with a fake servo bus).
- `tests/test_hybrid.py` owns `defect_sorter.hybrid` (grasp monitor: held, missed, timeout; normalized units to degrees; show routine and rest inside the ranges and off the roll end stops; Studio runtime-session messages, release monitor, place instruction texts, port holders, gripper ramp).
- `tests/test_targeting.py` owns `defect_sorter.targeting` (brick top-face pose in the table frame from a tilted top camera, brick selection, multi-frame combination, hover target, grasp point, approach direction and choice, grasp symmetry of long and square bricks, grasp wrist roll for any approach, the robot base kept out of brick candidates, bowl rim from depth (robust circle fit), drop points).
- `tests/test_depth_bridge.py` owns `defect_sorter.depth_bridge` (fixed-scale depth images incl. the layered height image, held table plane and its file check, crop, JPEG encoding, MJPEG/JPEG stream endpoints, raw frame feed `/raw.npz` and its client, publish loop).
- `tests/test_uvc_controls.py` owns `defect_sorter.uvc_controls` (V4L2 ioctl numbers and control ids, safe setting order, apply with read-back, device lookup by name, profile file).
- `tests/test_episodes.py` owns `defect_sorter.episodes` (episode review against the sort-v1 protocol incl. the v2 camera names, hover pause, grasp events, held-brick interval, grasp clips, LeRobot v3 loading).
- `tests/test_robot_pose.py` owns `defect_sorter.robot_pose` (table/base frames, base-marker link and relocation, readings vs model angles, calibration files).
- `tests/test_webview.py` owns `defect_sorter.webview` (frame buffer, page, frame polling and action endpoints).
- `packages/armkit/tests/` owns the standalone `armkit` library (one test module per library module: `test_model.py`, `test_collision.py`, `test_poses.py`, `test_guard.py`, `test_endstop.py`, `test_guarded_motion.py`, `test_procedure.py`, `test_check.py`, `test_park.py`, `test_measure.py`, `test_feetech.py`, `test_simulation.py`, `test_calibration.py`, `test_so101_profile.py`, `test_cli.py`, `test_independence.py`). The library must not name or import this project.
- `tests/test_training.py` owns `defect_sorter.training` and `defect_sorter.training_preflight` (local policy recipes, dataset contracts, plans, task validation and training launch preflight, warm-start recipes, checkpoint weight selection, multi-GPU and data-worker settings, periodic checkpoints).
- `tests/test_inspection.py` owns `defect_sorter.inspection` (score to normal/defective/uncertain decision, crops, brick isolation, colour purity, grouped folds, threshold choice).
- `tests/test_closed_loop.py` owns `defect_sorter.closed_loop` (label-to-task mapping, attempt state machine, records).
- `tests/test_planner.py` owns `defect_sorter.planner` (closed action set, rule planner, validation, LLM proposal parsing and fallback).
- `tests/test_async_pipeline.py` owns `defect_sorter.async_pipeline` (SmolVLA manifest/preprocessing, `LatestSlot`, async frame/inspection threads, `DryRunCell`, `AsyncChunkPolicy` prefetch and `stage_generation` invalidation, OpenVINO runner and FP16 IR compression).
- `tests/test_presentation.py` owns `defect_sorter.presentation` (defect faces and cross strokes, show points in front of a camera, view cosine, show-pose order, camera height/direction/arm-clearance check).
- `tests/test_twin.py` owns `defect_sorter.twin` (kinematic twin: TCP, IK, rate limits, grasp/release, cameras, scripted expert).
- `tests/test_offline_pipeline.py` owns `defect_sorter.offline_pipeline` and the pure part of `defect_sorter.lerobot_export` (demo recording, anomaly crops, twin evaluation, LeRobot features, privileged sim labels).
- `tests/test_tracking.py` owns `defect_sorter.tracking` (reading run and evaluation directories into MLflow records, twin/sim/real source tags).
- `tests/test_model_release.py` owns `defect_sorter.model_release` (release manifest and download verification).
- `tests/test_modal_training.py` owns `defect_sorter.modal_training` (Modal Volume layout, recording root on the Volume, warm-start upload, GPU cost ceiling).
- `tests/test_studio_preview_patch.py` owns `docker/studio-patches` (Studio live-preview rate, JPEG quality and skipped cameras).
- `tests/test_system_metrics.py` owns `defect_sorter.system_metrics` (cross-platform CPU/RAM with fake native counters, plus Linux Intel DRM/NPU and package power with synthetic procfs/sysfs fixtures).
- `tests/test_dashboard.py` owns `defect_sorter.dashboard` (static files, audio byte ranges, fonts, cached host resources, read-only snapshot file, path isolation, Studio routes and the same-origin JSON guard on commands).
- `tests/test_studio_link.py` owns `defect_sorter.studio_link` (websocket client against a loopback server, runtime observation parsing, camera relay, environment draft, fixed-task action set, policy run lifecycle with stop/time limit/fault, and the dashboard's Studio hub).
- `tests/test_live_inspection.py` owns `defect_sorter.live_inspection` (one-JPEG inspection: isolation, timed decode/isolate/inference, labels, failures and the colour-purity scorer).

- `frontend/tests/telemetry.test.mjs` owns `frontend/telemetry.mjs` and the state-driven pose behavior of `frontend/scene.mjs` (demo transitions, telemetry validation, missing data, display state and fault freeze); run with `node --test frontend/tests/telemetry.test.mjs`.
- `frontend/tests/image-loader.test.mjs` owns `frontend/image-loader.mjs` (complete-image loading, newest-frame coalescing, errors and resets). Run all frontend tests with `node --test frontend/tests/*.test.mjs`.
- `frontend/tests/performance.test.mjs` owns `frontend/performance.mjs` (resource validation/history, stale values and measured inference percentiles by source/device).
- `frontend/tests/command.test.mjs` owns `frontend/command.mjs` (typed prompt to the closed action set, refusals and plans).
- `frontend/tests/studio.test.mjs` owns `frontend/studio.mjs` (Studio link display state, camera feed states, run text, live inspection snapshots and the replay recorder).
- `frontend/tests/intro.test.mjs` owns `frontend/intro.mjs` (product story, browser timer receivers, bundled narration, pause/resume, silent/error playback, chapter navigation and cancellation).

Extend the owning module by default. Add a new test file only for a new stable module boundary, and update this map in the same change.

## Architecture

- `geometry.py`: pure camera geometry and RANSAC table-plane fit. No OpenCV drawing, no hardware.
- `scene.py`: scene understanding from one aligned colour+depth frame → `Scene` (bowls, objects). Thresholds live in `SceneConfig`, not as literals scattered through the code; `PAPER_CELL` is the configuration of the cell as built (white paper, green and pink bowls).
- `realsense.py`: the only module importing `pyrealsense2`; returns aligned `Frame` objects and pins colour settings (fixed white balance) so colours are stable across runs.
- `live_demo.py`: debug visualisation over `scene`, served through `webview`. Presentation only; no detection logic.
- `markers.py`: the printed ArUco set (ids, sizes, uses) as the single source for the print sheet and detection.
- `alignment.py`: marker poses refined with depth (with a fit-quality guard), the table frame (level, anchored on markers 16 and 17) that removes the camera's own tilt and position, reference save/load and drift comparison in that frame.
- `alignment_page.py`: live alignment page (camera tilt, markers, drift). Presentation only.
- `kinematics.py`: thin functions over `armkit` (SO-101 forward kinematics from the URDF joint table, the tool point between the jaws, inverse kinematics with position + approach direction, wrist roll given, within the URDF joint limits).
- `packages/armkit/` (uv workspace member, project-agnostic): kinematics, sphere collision model, guarded automatic joint calibration (`armkit-calibrate`: `check` one joint, `move` to a pose, `measure` the whole arm into a proposed calibration, `run` the full from-scratch procedure, `restore` a file; everything is a dry run unless `--go`), Feetech bus adapter and simulated bus. Run its calibration on hardware only when the user asks for that motion in the current conversation, first with `--only <one joint>`.
- `joint_calibration.py`: measure-only fit of joint zero offsets and the robot base pose from marker observations; `solve_base` fits only the base pose with Studio's joint zeros trusted, from markers on the turning base and further out on the arm.
- `robot_pose.py`: the saved robot calibration (joint offsets, base pose in the table frame, base-plate marker link); converts table points to robot targets and model angles to joint readings.
- `episode_calibration.py`: robot calibration from recorded Studio episodes, no capture session: jaw-tip touches on table markers fit the base pose and the lift/elbow/wrist zeros (`--touch`, with leave-one-out errors), or tags on the arm at still moments fit the base pose (`solve_base`).
- `calibration_capture.py`: capture/solve/link-base/locate CLI (`sorter-joint-calibration`); `so101_reader.py`: servo access. `SO101Reader` is read-only and never enables torque; `SO101Driver` adds hold-then-enable-torque and goal writes and is used only by `motion.execute`.
- `depth_bridge.py`: owns the D415 and serves colour and fixed-scale depth as MJPEG streams (`sorter-depth-bridge`), which Studio records as two IP cameras; the table plane is held for a run and checked against a saved file, so a dataset keeps one encoding. `/raw.npz` serves the uncropped frame (colour, millimetre depth, intrinsics) so measurements such as `sorter-move --bridge` run while Studio records.
- `uvc_controls.py`: the only module issuing V4L2 ioctls; locks USB camera exposure, white balance, focus and mains frequency from `config/camera_controls.json` (`sorter-camera-lock`, show unless `--apply`). Cameras forget these on replug or reboot, so apply before each session.
- `episodes.py`: review of recorded LeRobot v3 episodes (`sorter-episodes`, needs the `dataset` extra): task text, camera streams, grasp and release, hover pause, held-brick interval, grasp-clip frame ranges. Protocol in `docs/datasets/SORT_V1.md`.
- `motion.py`: slow, checked moves (`sorter-move`, dry run unless `--go`): IK goal with the jaws along a given approach (straight down by default; for a brick the steepest tilt that passes every check, `plan_brick_hover`), rise first when low, speed-limited joint steps, floor/reach/servo-range checks on every waypoint, stop-and-hold on tracking lag. Limits have hard caps.
- `hybrid.py`: one hybrid sort cycle (`sorter-hybrid`, dry run unless `--go`): scripted hover, the grasp policy run in a Studio runtime session until `GraspMonitor` sees the brick held and lifted (or a miss: rise, rest, measure again, retry), scripted show to the front camera (`SHOW_ROUTINE`, poses from the operators' holds in inspect-v1) with the gripper kept closed on the brick, and either a scripted bowl drop or (`--place policy`) the language-conditioned SmolVLA place policy, run on the Intel GPU through Studio with the instruction the bowl choice selects (`place_instruction`) until `ReleaseMonitor` sees the gripper open. The serial port alternates between our driver and Studio; never both (`wait_for_port`).
- `targeting.py`: brick targets for scripted hovers: top-face pose (centre, long-axis yaw, size) in the table frame from one detected object, brick selection, the grasp point half way up it, the approach (straight down where the 95° wrist flex allows, else tilted out from the base by the smallest angle that reaches, standoff back along it) and the wrist roll that closes the jaws across its long axis for that approach, or across either pair of sides for a square 2x2 Duplo (`sorter-move --above-brick [--bridge URL] [--approach auto|down] [--standoff mm] [--measure-only]`).
- `webview.py`: shared HTTP plumbing for the live pages; the browser pulls one complete JPEG at a time, so a slow link cannot freeze the view.
- `system_metrics.py`: read-only host CPU/RAM on Linux/macOS/Windows, using procfs or native psutil counters, plus Linux visible Intel DRM clients, NPU busy time and RAPL package power. Missing/restricted counters stay null; host activity does not establish model deployment.
- `dashboard.py`: serves the standalone frontend (Armigo), cached host samples (including per-core load and the busiest processes on Linux), an optional backend-written snapshot JSON file and, with `--studio-url`, the Studio link. It moves the arm only when the operator started it with `--studio-control`, and then only through `studio_link`'s fixed tasks.
- `studio_link.py`: Physical AI Studio over its own HTTP/websocket API: a dependency-free websocket client, camera preview relays (connect while watched, release when idle), and `PolicyRun`, one runtime session that loads a saved environment and a model export, runs one fixed task text and sets control to None on stop, time limit or any failed component, without retrying. `StudioHub` is the dashboard's view of one project.
- `live_inspection.py`: inspects one camera JPEG for the dashboard (decode, `isolate_object`, scorer) with each step timed separately; no brick, an unreadable frame or a scorer error is `uncertain` with no score.
- `anomaly_smoke.py`: Anomalib → OpenVINO toolchain check and per-device latency benchmark.
- `inspection.py`: anomaly score → normal/defective/uncertain with an explicit threshold; brick isolation (saturation, convex hull, constant fill) and a colour-purity score; grouped folds and threshold choice for evaluations; OpenVINO scorer for Anomalib exports; Padim training on a crop folder. The real-data experiment is `scripts/anomaly/real_baseline.py`; `scripts/anomaly/calibrate_devices.py` picks one threshold per OpenVINO device.
- `closed_loop.py`: one sorting attempt (observe → inspect → plan → execute → verify) over replaceable `Cell`, inspector and `Policy` protocols; defect labels map to fixed task texts.
- `planner.py`: high-level action for one brick from a closed set (sort green/pink, re-inspect, retry grasp, skip and alert, stop); rules decide by default, an LLM may propose, `validate` always checks, failures fall back to the rules. Never joint commands.
- `async_pipeline.py`: asynchronous camera-to-policy pipeline (`AsyncFrameSource`, `AsyncInspectionStage`, `AsyncChunkPolicy` with chunk prefetch and monotonic `stage_generation` invalidation, `OpenVinoSmolVlaRunner`, `compress_ir_to_fp16`) and open-loop `DryRunCell` (`Cell` adapter without `/dev/ttyACM*` access).
- `presentation.py`: pure geometry for presenting a held brick to the inspection camera, used by the MuJoCo cell (`scripts/sim/so101_sort_sim.py`): defect on any face, reachable show points near the camera's optical axis, pose order by visible defect, camera acceptance.
- `twin.py`: kinematic digital twin of the cell (no physics engine) implementing `Cell`, plus a privileged scripted expert. Twin results are tagged `mode = twin` and never pooled with real ones.
- `offline_pipeline.py`: hardware-free CLI (record demos, write anomaly crops, evaluate the loop); `lerobot_export.py`: demos → LeRobot v3, run in the Studio backend environment.
- `tracking.py`: logs finished training runs and twin evaluations to MLflow (`tracking` extra), tagged by data source.
- `model_release.py`: manifest (file hashes, training run, status) for private GitHub model releases and verification of a download against it.
- `modal_training.py`: Volume layout and cost bound for training on Modal, without importing the Modal SDK; the Modal app is `scripts/modal/train.py` (dry run unless `--go`, GPU time capped by `--max-hours`). Guide in `docs/infrastructure/MODAL.md`.

Keep modules deep: callers use `detect_scene(...)` and `D415Camera`, not the internals. Do not fabricate detections, scores or latencies; when data is missing, return an empty or explicit failure result rather than a guess. A dependency that "supports OpenVINO" is not proof of GPU/NPU deployment; report configuration, build, runtime and hardware checks separately.

## Comments and documentation

Comments and docstrings describe what the code does now and why the design holds, not the history of how it got there. History belongs in commit messages and `memory/handoffs/`.

After every implementation, review the docs together with the diff and update `README.md`, `docs/` and `memory/STATUS.md` in the same change. Machine state and workarounds go to `.local/`, not tracked docs.

## Verification gates

Before declaring work done, run from the repository root:

```bash
uv run pytest -q
uv run ruff check src tests packages
uv run ruff format --check src tests packages
```

Do not claim a check passed unless you ran it and saw it pass. Report pre-existing failures exactly.

## Completion report

State the behavior changed and the tests written first, the commands run and their results, any hardware touched (and that the user authorized it), which docs were updated, and remaining risks.
