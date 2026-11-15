# PhysicAI sorting dashboard

The standalone UI in [`frontend/`](../../frontend/) is **Armigo**: a black/green LED-style dashboard with a product pitch, a narrated intro, a guided tour over a 3D sorting cell, the inspected brick from four viewpoints, live Physical AI Studio cameras, a typed command console, recording and replay, and an edge-performance monitor. It uses browser-native HTML, CSS and ES modules, plus a vendored three.js r160 build (`frontend/vendor/`, MIT) and two bundled OFL fonts (`frontend/assets/fonts/`); there is no package installation, build step or runtime CDN dependency. It leaves the pinned Studio submodule unchanged.

## Armigo: sources, live Studio link and replay

The header switches between three sources, and every panel says which one it shows:

- **Demo**: illustrative playback (`telemetry.mjs` demo states). Demo parts carry no timings.
- **Live**: Physical AI Studio through the dashboard server. Start it on the laptop that runs Studio:

  ```bash
  # cameras, lists and live inspection; the arm cannot move
  uv run sorter-dashboard --studio-url http://127.0.0.1:7860 --anomaly-model models/padim/model.xml --anomaly-device NPU --threshold 0.5
  # colour-purity baseline instead of a model (threshold on the off-colour share)
  uv run sorter-dashboard --studio-url http://127.0.0.1:7860 --purity --threshold 0.1
  # operator present at the cell: also allow policy runs (each stops itself after --max-run-s)
  uv run sorter-dashboard --studio-url http://127.0.0.1:7860 --anomaly-model models/padim/model.xml --anomaly-device NPU --studio-control --max-run-s 45
  ```

  `--anomaly-model` needs the `anomaly` extra (`uv run --extra anomaly sorter-dashboard …`). `--studio-project` picks a project; the default is Studio's first project.
- **Replay**: the last up to 90 s that the browser recorded in Live (camera tiles, decision and run status, 4 frames per second), labelled REPLAY everywhere. It is the fallback when the venue link or the hardware fails during a pitch. Recordings stay in that browser tab.

Camera tiles use Studio's own preview socket (`/api/cameras/ws`). A relay connects only while the page asks for frames and releases the camera after 15 s without viewers. While a Studio runtime session holds a camera, Studio refuses the preview and the tile says **HELD BY STUDIO**; during a run started from Armigo, the tiles show the run's own session frames instead.

**Typed commands** (`command.mjs`) map to a closed set: inspect, inspect-then-sort, sort to the green or pink bowl, stop. Unclear, negated or unrelated prompts are refused with a reason. The server checks the action again and only ever sends `closed_loop.DEFAULT_TASKS` texts to the policy. Inspect-then-sort scores the newest frame first; an `uncertain` result returns *review* and nothing moves.

**Arm control safeguards**: runs need `--studio-control` on the command line (the browser cannot enable it), the operator checkbox, a same-origin JSON request with the `X-Armigo-Request` header (a cross-site page cannot send one), and at most one active run. Each run sets Studio's model control with a 3 s grace and holds the arm (`set_control: null`) on STOP, on its time limit, or when any session component reports `failed`; it never retries. Studio's own action limits stay in force. The dashboard still never opens a camera or a servo bus itself.

**Inspection timings** are measured on the dashboard host: decode, isolation and inference separately. The device shown is the one the scorer was compiled for. The pitch card keeps the 14 November workstation benchmark (Padim, NPU, 8.5 ms) until measured live cycles are available.

## Local development

From the repository root, start the read-only dashboard server:

```bash
uv run sorter-dashboard
```

Open `http://127.0.0.1:8080/`. Do not open the HTML directly with a `file:` URL: browser module loading requires HTTP. Stop the server with Ctrl+C. This command serves frontend files and host counters; it does not start Studio, open a camera or connect to the arm. The default listener is loopback. Use `--port` or `--frontend` for a different port or checkout location. A static-only server remains supported, with resource monitoring unavailable.

If the frontend cannot be found, change into the checkout root (the folder containing `frontend/index.html`) or set `--frontend`. For an occupied port, stop your earlier server or change the port in both the command and browser URL.

Select a demo scenario and use **Play demo** or **Inspect next part**. The illustrative cell supports pointer rotation and keyboard arrow keys. The normal scenario uses the existing green-bowl mapping; defective parts use pink. Blue is accepted as a backend destination so the final physical setup can be reflected without deriving it from a score in the browser.

The demo passes through `perceive → detect → reason → act → verify → complete`. An uncertain decision stops at `review`, and a fault stops at `fault`. Demo scores and the synthetic crop are explicitly illustrative. Device names and timings are not synthesized. The canvas arm is a presentation illustration, not calibrated SO-101 forward kinematics or a physics simulation.

## Frontend boundary

[`telemetry.mjs`](../../frontend/telemetry.mjs) owns the v1 snapshot validator, demo state transitions and display formatting. The browser displays the supplied `label`, destination and task; it does not reproduce Python inspection or planning rules.

The integration seam is a browser event carrying one complete snapshot:

```javascript
window.dispatchEvent(new CustomEvent('sorter:telemetry', { detail: snapshot }));
```

The UI polls `/api/telemetry` and forwards received snapshots through this validated boundary. With no configured source, the endpoint returns 204 and demo playback remains available. To connect a backend's latest snapshot, run:

```bash
uv run sorter-dashboard --telemetry-file /path/to/snapshot.json
```

The producer must write a temporary file and atomically replace the snapshot file, preserve its epoch-millisecond timestamp and publish all v1 fields. The endpoint returns 503 for unreadable or partial JSON; invalid snapshots are rejected in the browser. Missing/failed updates leave the last valid snapshot visible with its stale indication. This is a file bridge, not a controller adapter, frame proxy or hardware control channel. The in-page event remains available to other adapters. Image routes must be provided by a same-origin integration; the server only serves frontend assets and the two JSON routes.

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
4. Publish the latest snapshot through the file bridge or in-page event, and provide a same-origin arrangement for frame/heatmap routes. Keep stale data visible and keep real, replay and twin provenance distinct.
5. Verify joint units, zero offsets, URDF mapping and gripper direction against a real recording. Replace the illustrative scene with calibrated measured-joint rendering before claiming a live digital twin.
6. Integrate operator commands separately after the controller and on-site operator define authorization and fault behavior. The initial buttons operate the demo only; no UI action here sends an arm command.

The backend remains responsible for uncertain-result handling, safety limits, actuation and outcome verification. The UI should receive an explicit failure or missing result when data is unavailable.

## Host resource monitor and inference timing

Run `sorter-dashboard` on the computer to monitor. `/api/system` caches one sample per second across clients. It reads OS counters, needs no heavy dependency and never opens camera/arm devices, launches a benchmark, changes permissions or enables an accelerator. The monitor describes the **server host**, including other processes. It is independent of the sorting source: a demo or replay can be visible alongside live host counters.

CPU/RAM are supported across Linux, macOS and Windows. Linux uses procfs; other hosts use native OS counters
through the small `psutil` dependency. On macOS, the CPU model comes from a read-only `sysctl` query.
Snapshots include `platform` (for example `Linux`, `Darwin` or `Windows`) and `source` (`linux-proc-sysfs`
or `psutil`). The UI displays Darwin as macOS. Non-Linux GPU/NPU/power counters remain null; Apple GPUs
are not labeled Intel. Host clocks still need to agree with the browser for freshness checks.

| Display | Measurement and limits |
| --- | --- |
| CPU | Linux: delta of aggregate `/proc/stat` busy ticks, excluding idle/iowait; guest fields are excluded from the total because user/nice already include them. Other platforms: delta of `psutil.cpu_times()`, excluding idle and duplicate interrupt/DPC/guest fields. First/reset samples are unavailable. Processor identity and logical core count are included. |
| Memory | Linux: `(MemTotal − MemAvailable) / MemTotal` from `/proc/meminfo`. Other platforms: `(total − available) / total` from `psutil.virtual_memory()`. Shows used/total GiB. |
| Intel GPU | Deltas of `drm-engine-*` nanoseconds or Xe `drm-cycles-* / drm-total-cycles-*` in readable `/proc/<pid>/fdinfo/*` for `i915`/`xe`. Clients are deduplicated by PCI device/client id, engine groups normalized by capacity, and the busiest engine is shown. Coverage includes visible clients only; unreadable clients or unsupported counters prevent a whole-host claim. No clients means unavailable. Temporary busy-counter dips retain their high-water mark. |
| Intel NPU | Delta of `npu_busy_time_us` under `/sys/bus/pci/drivers/intel_vpu/*`, divided by elapsed time. Busiest device shown; first/reset samples are unavailable. |
| CPU package power | RAPL `energy_uj` deltas for package domains under `/sys/class/powercap`, with one counter wrap handled. Reports package watts, not whole-laptop power or per-inference energy. Multiple wraps between samples cannot be resolved. Restricted counters remain unavailable. |

Sources: [Linux procfs documentation](https://www.kernel.org/doc/html/v5.15/filesystems/proc.html), [DRM usage stats](https://www.kernel.org/doc/html/latest/gpu/drm-usage-stats.html), [Xe driver counters](https://www.kernel.org/doc/html/latest/gpu/xe/xe-drm-usage-stats.html), [Intel NPU sysfs ABI](https://kernel.googlesource.com/pub/scm/linux/kernel/git/torvalds/linux/+/8c13415c8a4383447c21ec832b20b3b283f0e01a/Documentation/ABI/testing/sysfs-driver-ivpu), [powercap](https://www.kernel.org/doc/html/latest/power/powercap/powercap.html).

On Linux each sample also lists per-core CPU load (from the `cpuN` lines of `/proc/stat`) and the eight busiest processes (user+system ticks from `/proc/<pid>/stat` over the sample interval, resident memory), shown as a per-core grid and a process table. Other platforms leave both null. The frontend holds 60 resource samples. Values older than 3.5 seconds, implausibly ahead of browser time, missing, malformed or restricted stay empty; keep host/browser clocks synchronized. CPU/RAM can work while GPU/NPU/power remain unavailable. The UI makes no automatic performance-quality judgment. Cross-platform API reference: [psutil](https://psutil.io/).

Median/p95 inference uses at most 60 distinct **completed, measured, non-demo episodes**, grouped by mode and runtime-reported device. Repeated snapshots of one episode do not increase the count. Percentiles use nearest rank; the sample count is always shown. Only `timings_ms.inference` contributes: capture, combined inspection and robot motion are not relabeled inference. These recent observations are not a controlled benchmark. Missing timings produce no statistic; device activity alone does not establish model execution, correctness or accelerator deployment.

## Product introduction

**Watch the story** opens a four-chapter animated SVG explainer: the cost of missed defects, inspection and sorting in one cell, human review when uncertain, and the goal of local Intel inference. It describes the concept without invented ROI, accuracy or latency claims. It does not start sorting or change the dashboard's data source.

The viewer opens the intro, then presses **Play intro**. Narration uses four bundled PCM WAV clips in
`frontend/assets/intro/`, with one fixed English voice and no voice selector or browser speech-synthesis
dependency. Pause/resume keeps the audio position; chapter selection/reopening rewinds it. Completion of each
clip advances the chapter. The static server supports HTTP byte ranges for media seeking.

Narration can be disabled; captions, full chapter transcripts, chapter navigation and silent timed playback
work without it. Audio errors fall back to timed captions with a visible status. Close/Escape pauses the
audio and invalidates pending callbacks. Reduced-motion settings disable the SVG motion. The default player
wraps browser timer calls to preserve their required receiver. The intro is an in-browser animation with
audio, not an exported video file.

The transcript lives in `STORY` in `frontend/intro.mjs`. To regenerate the fixed narration after editing it,
run `node scripts/build_intro_audio.mjs` on macOS (uses the installed Samantha voice at 168 words/minute).
The audio clips are bundled frontend assets; playback on Linux/macOS/Windows needs no synthesis tooling.

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

They cover demo completion, review without movement, authoritative backend labels, missing scores, stale state, invalid snapshots, fault presentation, complete-image loading, resource validation/history, source/device-separated inference percentiles, and narrated/silent intro navigation/cancellation. Python tests use synthetic procfs/sysfs trees for resource math and a local HTTP fixture for asset isolation, cached resource JSON and the snapshot-file endpoint. They do not establish browser rendering, actual Linux driver readings, model correctness, camera access or robot behavior. Run the repository's Python verification gates alongside the frontend tests before completing a change:

```bash
uv run pytest -q
uv run ruff check src tests packages
uv run ruff format --check src tests packages
```

Validation after rebasing onto the latest main: thirteen frontend regression tests passed; module syntax checks passed; `uv run pytest -q` reported **573 passed, 1 skipped in 45.78 s**; `uv run ruff check src tests packages` passed; and `uv run ruff format --check src tests packages` reported **89 files already formatted**. The skip is the existing optional PyArrow-dependent episode test; the default environment does not install PyArrow. The local preview returned HTTP 200 during the initial implementation. Headless Firefox could not open its temporary profile, so browser interaction and visual QA remain unverified. These checks do not validate the candidate Studio dataset or a replay adapter.

Resource monitor/intro validation (2026-11-15): **22 frontend tests passed**; `uv run pytest -q` reported
**583 passed, 1 skipped in 47.76 s**; Ruff check passed and format check reported **93 files already formatted**.
New tests were first run failing, then passed after implementation, including Xe cycle-counter support,
counter dips and speech-error fallback. Module syntax and whitespace checks passed. Local HTTP smoke checks
returned 200 for the page/modules/styles/resource API and 204 for the unconfigured sorting snapshot API;
all 54 HTML IDs were unique. Headless Firefox again failed to open its temporary profile, including with a
pre-created profile directory, so browser layout, interaction and voice quality remain unverified. No shared
workstation, cameras or arm were used, and actual Intel Linux counters were not sampled during this change.

Playback/native-host correction (2026-11-15): the intro's default timer functions were invoked with the player
as their receiver, causing Chromium to throw `Illegal invocation` before playback. The timer receiver regression
was reproduced red, then fixed. Bundled fixed-voice WAV clips replace browser speech synthesis; audio promise
failures, cancellation, pause/resume and media byte ranges have regression coverage. Native macOS/Windows CPU/RAM
fixtures were also run red then green. `node --test frontend/tests/*.test.mjs`: **27 passed**.
`uv run pytest -q`: **587 passed, 1 skipped (47.94 s)**. Ruff check passed; format check reported
**93 files already formatted**. Module syntax and audio-file checks passed (four non-silent PCM clips).

Actual Chromium checks passed with browser speech synthesis disabled: live macOS CPU/RAM, all four audio clips,
pause/resume, seeking/completion, replay, Escape cancellation, reopening, silent captions and mobile width.
No page errors were reported. Desktop/mobile screenshots were reviewed. These results supersede the earlier
browser-verification limitation. Windows has synthetic counter coverage, not a live machine check; Linux GPU/NPU
hardware readings were not sampled. No cameras, arm, Studio service or inference workloads were touched.
