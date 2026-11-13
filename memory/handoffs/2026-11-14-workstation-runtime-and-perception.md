# 2026-11-14 — Workstation runtime and perception package

- Author: Matvii
- Branch and commit: `feat/defect-sorter-perception` (rebased onto `2a9e000`)
- Scope: shared Ubuntu workstation runtime, Studio project setup, `src/defect_sorter` perception package

## Changes

- `src/defect_sorter/`: `geometry` (deprojection, RANSAC table plane, height), `scene` (objects by height, bowls by colour, object-in-bowl; only rims are masked so objects inside bowls are found), `realsense` (D415 capture, fixed white balance), `live_demo` (MJPEG debug page), `anomaly_smoke` (Anomalib→OpenVINO + device latency).
- `tests/test_geometry.py`, `tests/test_scene.py`: synthetic-frame tests, written first.
- `pyproject.toml`, `uv.lock`, `.python-version`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `README.md`, `docs/infrastructure/SETUP_STATUS.md`.

## Evidence

- `uv run pytest -q`: 20 passed (macOS and workstation). `ruff check`/`ruff format --check` on `src tests`: clean.
- Hardware actually used: D415 depth/colour capture (USB 3.2) via `sorter-live-demo` on the workstation, bound to the Tailscale address; OpenVINO inference on CPU/GPU/NPU with a synthetic Padim model. One user-requested Studio identify wiggle on the follower (`5AAF262737`), which reported a gripper overload error after moving.
- Live scene: table 0.60 m, pink and green bowls, two Duplo bricks (6.2 cm, 3.8 cm), ~34 fps.

## Open questions and next steps

- Arms are uncalibrated; check the follower gripper still moves freely after the identify error.
- Only one process can open the D415: stop `sorter-live-demo` before Studio previews, records or runs a policy. A shared-frame approach is needed for the live loop.
- Camera mounts not final (`front` aimed at people, `wrist` out of focus).
- Next action: calibrate arms in Studio, then teleop dry run and demonstrations; capture good-object crops for an Anomalib baseline.
