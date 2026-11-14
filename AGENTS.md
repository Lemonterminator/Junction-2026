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

## Secrets and machine access

- Do not read, print or copy private keys, passwords, tokens or `.env` files. Refer to them by path only.
- Access details, workarounds and machine-specific state live in the Git-ignored `.local/` folder (or `*.local.md`). Never move that content into tracked files.
- Never commit captured camera frames of people, recorded datasets, model weights or exports; `data/`, `models/`, `artifacts/` and `checkpoints/` are Git-ignored.

## Tooling and style

- Use `uv` exclusively (`uv sync`, `uv run`, `uv add`). Keep `.python-version` (3.12) and `uv.lock` committed. Heavy dependencies sit behind extras: `camera` (pyrealsense2, Linux only) and `anomaly` (Anomalib, OpenVINO, CPU torch). The default install stays light so tests run on any laptop.
- Use tabs for indentation in Python, enforced by `ruff format`. Never align code or comments with padding spaces.
- Add precise type annotations and NumPy-style docstrings to public functions and classes.
- Use `logging.getLogger(__name__)` with lazy `%` arguments. No `print` in library code; CLI output uses `sys.stdout.write` or logging.
- Hardware SDKs are imported in exactly one adapter module each (`realsense.py` for pyrealsense2). Perception logic works on plain NumPy arrays so it can be tested without hardware.

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
- `tests/test_scene.py` owns `defect_sorter.scene` (bowl detection by colour, object detection by height, object-in-bowl relation).
- `tests/test_markers.py` owns `defect_sorter.markers` (printed marker set, print sheet, marker detection and pose).
- `tests/test_alignment.py` owns `defect_sorter.alignment` (depth-refined marker poses, drift against a saved reference).
- `tests/test_training.py` owns `defect_sorter.training` and `defect_sorter.training_preflight` (local policy recipes, dataset contracts, plans, task validation and training launch preflight).

Extend the owning module by default. Add a new test file only for a new stable module boundary, and update this map in the same change.

## Architecture

- `geometry.py`: pure camera geometry and RANSAC table-plane fit. No OpenCV drawing, no hardware.
- `scene.py`: scene understanding from one aligned colour+depth frame → `Scene` (bowls, objects). Thresholds live in `SceneConfig`, not as literals scattered through the code.
- `realsense.py`: the only module importing `pyrealsense2`; returns aligned `Frame` objects and pins colour settings (fixed white balance) so colours are stable across runs.
- `live_demo.py`: debug visualisation and MJPEG web server over `scene`. Presentation only; no detection logic.
- `markers.py`: the printed ArUco set (ids, sizes, uses) as the single source for the print sheet and detection.
- `alignment.py`: marker poses refined with depth, reference save/load and drift comparison.
- `alignment_page.py`: live alignment page (camera tilt, markers, drift). Presentation only.
- `anomaly_smoke.py`: Anomalib → OpenVINO toolchain check and per-device latency benchmark.

Keep modules deep: callers use `detect_scene(...)` and `D415Camera`, not the internals. Do not fabricate detections, scores or latencies; when data is missing, return an empty or explicit failure result rather than a guess. A dependency that "supports OpenVINO" is not proof of GPU/NPU deployment; report configuration, build, runtime and hardware checks separately.

## Comments and documentation

Comments and docstrings describe what the code does now and why the design holds, not the history of how it got there. History belongs in commit messages and `memory/handoffs/`.

After every implementation, review the docs together with the diff and update `README.md`, `docs/` and `memory/STATUS.md` in the same change. Machine state and workarounds go to `.local/`, not tracked docs.

## Verification gates

Before declaring work done, run from the repository root:

```bash
uv run pytest -q
uv run ruff check src tests
uv run ruff format --check src tests
```

Do not claim a check passed unless you ran it and saw it pass. Report pre-existing failures exactly.

## Completion report

State the behavior changed and the tests written first, the commands run and their results, any hardware touched (and that the user authorized it), which docs were updated, and remaining risks.
