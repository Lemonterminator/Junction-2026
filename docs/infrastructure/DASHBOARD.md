# PhysicAI sorting dashboard

The standalone UI in [`frontend/`](../../frontend/) presents the sorting cell, inspection evidence, decision, progress and cycle timings. The initial implementation uses browser-native HTML, CSS, ES modules and canvas; it has no frontend package installation, build step or runtime CDN dependency. It leaves the pinned Studio submodule unchanged.

## Local development

From the repository root, start the static server:

```bash
uv run python -m http.server 8080 --bind 127.0.0.1 --directory frontend
```

Open `http://127.0.0.1:8080/`. Do not open the HTML directly with a `file:` URL: browser module loading requires HTTP. Stop the server with Ctrl+C. This command serves frontend files only and does not start Studio, open a camera or connect to the arm.

If `/` returns 404, the server may have been started from your home folder: `--directory frontend` is relative to the terminal's current directory. Stop it, change into the checkout root (the folder containing `frontend/index.html`), and rerun. If already inside `frontend/`, omit `--directory frontend`. For an occupied port, stop your earlier server or change the port in both the command and browser URL.

Select a demo scenario and use **Play demo** or **Inspect next part**. The illustrative cell supports pointer rotation and keyboard arrow keys. The normal scenario uses the existing green-bowl mapping; defective parts use pink. Blue is accepted as a backend destination so the final physical setup can be reflected without deriving it from a score in the browser.

The demo passes through `perceive → detect → reason → act → verify → complete`. An uncertain decision stops at `review`, and a fault stops at `fault`. Demo scores and the synthetic crop are explicitly illustrative. Device names and timings are not synthesized. The canvas arm is a presentation illustration, not calibrated SO-101 forward kinematics or a physics simulation.

## Frontend boundary

[`telemetry.mjs`](../../frontend/telemetry.mjs) owns the v1 snapshot validator, demo state transitions and display formatting. The browser displays the supplied `label`, destination and task; it does not reproduce Python inspection or planning rules.

The integration seam is a browser event carrying one complete snapshot:

```javascript
window.dispatchEvent(new CustomEvent('sorter:telemetry', { detail: snapshot }));
```

This is an in-page adapter boundary, not an HTTP endpoint or a connection to the workstation. The backend integration must add a transport adapter that obtains snapshots and forwards valid data through this boundary. No polling or WebSocket transport is connected by this initial UI. Non-demo snapshots are for telemetry display; hardware controls and calibrated joint visualization remain separate integration work.

The camera image loader finishes the current request before loading the newest pending frame URL, coalescing intermediate updates. This avoids repeatedly cancelling slow downloads when joint telemetry arrives faster than images. A missing image URL clears the view; image errors are reported and queued updates can continue. Heatmap URLs are reserved in the snapshot contract but are not rendered by this initial UI.

## Snapshot v1

Every snapshot contains the following fields. Missing measurements use `null`, never a guessed value. Timestamps and all durations have explicit units.

| Field | Contract |
| --- | --- |
| `schema_version` | Integer `1`. |
| `episode_id` | String identifying the current attempt. |
| `mode` | `demo`, `twin`, `replay` or `real`; retain provenance through recording and display. |
| `timestamp` | Finite Unix epoch timestamp in **milliseconds**, representing this snapshot. |
| `stage` | `perceive`, `detect`, `reason`, `act`, `verify`, `complete`, `review` or `fault`. |
| `label` | Backend decision: `normal`, `defective` or `uncertain`. |
| `score` | Finite normalized score from `0` to `1`, or `null` when unavailable. |
| `thresholds` | `{ normal_below, defective_above }`, finite ordered boundaries within `0…1`, or `null` if unavailable. These describe the active inspector; the demo's `0.40` and `0.60` are not deployment settings. |
| `destination` | `green`, `blue`, `pink` or `null`; supplied by the backend's task mapping. |
| `task` | Task sentence actually selected by the backend, or `null`. |
| `joints` | Six finite values ordered `shoulder_pan`, `shoulder_lift`, `elbow_flex`, `wrist_flex`, `wrist_roll`, `gripper`, matching the twin's `STATE_NAMES` order; `null` when unavailable. |
| `joint_unit` | Literal `degrees_and_gripper_0_100` when joints are supplied, otherwise `null`: first five values in degrees; gripper on a `0…100` scale. Physical calibration and the gripper convention must be verified before real pose rendering. |
| `frame_id` | Nonnegative integer identifying the associated image. |
| `camera_url`, `heatmap_url` | Same-origin absolute paths beginning with a single `/`, with no backslashes, control characters or whitespace, or `null`. A heatmap must come from model output; the initial demo does not establish model heatmap support. |
| `outcome` | Verified destination (`green`, `blue`, `pink`) or `null` while missing/unverified. A planned destination is not placement evidence. |
| `device` | Runtime-reported inference device string, or `null`; hardware availability alone does not establish model execution on that device. |
| `timings_ms` | `{ capture, inference, placement }`; each duration is finite, nonnegative milliseconds or `null`. |
| `fault` | Fault description string or `null`. Fault handling must stop the controller; the UI does not retry motion. |

A missing score displays as `—`; missing thresholds are explicitly unavailable and have no coloured threshold arcs. A completed stage with a null outcome does not claim placement or verification. Data older than three seconds is stale. Transport integration must preserve capture timestamps and frame identifiers so the browser can show delays rather than silently treat old data as live.

## Backend integration tasks

1. Add progress events around observation, inspection, planning, execution and verification in the controller. `run_episode` currently returns a final `EpisodeRecord`; it is not a stream of stage updates.
2. Convert records into complete v1 snapshots. Convert `EpisodeRecord.timings_s` from seconds where appropriate, and instrument capture and inference separately; the combined inspection duration is not an inference-only benchmark.
3. Choose one owner for each camera. Consume that owner's published frames; the dashboard must not start a second D415 capture alongside Studio. Existing [`webview.py`](../../src/defect_sorter/webview.py) provides latest-frame JPEG polling and JSON state that an adapter can reuse where that service owns capture.
4. Agree on the telemetry transport, same-origin proxy arrangement, frame/heatmap routes and reconnect behavior. Keep stale data visible and keep real, replay and twin provenance distinct.
5. Verify joint units, zero offsets, URDF mapping and gripper direction against a real recording. Replace the illustrative scene with calibrated measured-joint rendering before claiming a live digital twin.
6. Integrate operator commands separately after the controller and on-site operator define authorization and fault behavior. The initial buttons operate the demo only; no UI action here sends an arm command.

The backend remains responsible for uncertain-result handling, safety limits, actuation and outcome verification. The UI should receive an explicit failure or missing result when data is unavailable.

## Candidate Studio dataset for replay

The user identified `datasets/50815c02-…` in a Studio volume as a LeRobot v3.0 dataset with robot type `SO101_Follower` and two simulated episodes. Later team documentation in [OFFLINE_PIPELINE.md](OFFLINE_PIPELINE.md) describes the same shortened identifier as the first real Studio recording. Confirm the full identifier and provenance before labeling replay data; the dashboard work has not accessed or validated these files. This remains a candidate source for the first recorded-data adapter, requiring a readable export location.

Before adding playback, inspect `meta/info.json`, episode metadata, state/action feature names and units, camera media references, frame rate and timestamps. Verify which fields are measured observations and which are commanded actions. Convert the recording to the dashboard's joint order and units only after confirming the source convention; robot type alone does not establish that mapping.

The [model release guide](MODEL_RELEASES.md) records Studio-normalized body joints (`−100…100`) for the first Studio smoke recording, whereas snapshot v1 expects body degrees. Do not relabel normalized values as degrees. A replay adapter needs a verified calibration/unit conversion or an explicitly extended snapshot contract before pose rendering.

Use `mode = replay` for playback and retain the dataset's confirmed provenance (simulated or real recording) in its source description and replay metadata. Keep recorded frame time separate from playback publication time, so a historical recording does not imply a live sensor stream. Recorded media and model files stay under ignored data/artifact directories. No access to Studio's devices or arm motion is necessary to read an exported dataset.

Replay can populate camera views, joint telemetry and recorded task text. It must not invent anomaly scores, heatmaps, inference devices, cycle timings, verified outcomes or intermediate controller stages when the recording does not contain them. An adapter should explicitly mark absent evidence and publish a compatible snapshot; scored replay requires a separate actual inspection run. The initial UI does not yet implement this dataset reader or calibrated joint playback.

## Verification

The deterministic model tests use synthetic snapshots and no hardware, network, browser or external dependencies:

```bash
node --test frontend/tests/*.test.mjs
```

They cover demo completion, review without movement, authoritative backend labels, missing scores, stale state, invalid snapshots, fault presentation, and complete-image loading with newest-frame coalescing, error recovery and resets. They do not establish browser rendering, live transport, model correctness, camera access or robot behavior. Run the repository's Python verification gates alongside the frontend tests before completing a change:

```bash
uv run pytest -q
uv run ruff check src tests packages
uv run ruff format --check src tests packages
```

Validation after rebasing onto the latest main: thirteen frontend regression tests passed; module syntax checks passed; `uv run pytest -q` reported **573 passed, 1 skipped in 45.78 s**; `uv run ruff check src tests packages` passed; and `uv run ruff format --check src tests packages` reported **89 files already formatted**. The skip is the existing optional PyArrow-dependent episode test; the default environment does not install PyArrow. The local preview returned HTTP 200 during the initial implementation. Headless Firefox could not open its temporary profile, so browser interaction and visual QA remain unverified. These checks do not validate the candidate Studio dataset or a replay adapter.
