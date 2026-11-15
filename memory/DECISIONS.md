# Decision log

## 2026-11-13 — Git-tracked shared memory

Adopt `AGENTS.md` as the Codex entry point and `CLAUDE.md` as the Claude entry point.
Both lead to the same `memory/` documents. Reason: portable, reviewable team context
without sharing AI accounts or relying on private per-session memory. New decisions
must include date, rationale, status, and evidence when factual claims are involved.

## 2026-11-13 — Upstream source integration

Use a submodule at `external/physical-ai-studio`, branch `junction2026`, pinned to
`17714488fa9c7d098a056da83f7c220cf983957d`. This implements the user's request to bring
the whole repository into this project. Keep integration code outside the submodule.
Updating the pin is an intentional source update, followed by updating the manifest,
Compose defaults, `.env.example`, and rerunning relevant checks.

## 2026-11-13 — Container boundaries

Build Studio using its pinned upstream Dockerfile and named `libs` build context.
Provide a CPU default and opt-in Intel GPU, NPU, and robot overlays. Anomalib 2.7.0
(PDF version) gets a separate CPU container because its PyTorch environment must
stay isolated. Local XPU anomaly training remains a separate future validation.
Compose projects scope persistent storage per developer; an integration deployment
still needs a named owner. No privileged device access is enabled by default.

## 2026-11-13 — Source conflict handling

Retain both scoring rubrics and attribute them separately. Do not assume the GitHub
rubric supersedes the PDF. Ask organizers for the final rubric before score-based
prioritization. Additional repositories are optional opportunities; Instant Learn
and performance profiling are recommendations, not adopted contest requirements.
Superseded for the rubric by the 2026-11-14 kickoff answers below.

## 2026-11-14 — Kickoff answers: rubric, 5090 trainer, defect definition

Relayed by linan from the organizers; not independently verified, so correct this entry if a
teammate heard otherwise.

- **Final scoring table is the GitHub (`JUNCTION2026.md`) one**: Task Success Rate 25, Intel Tech
  Integration 25, Dataset & Pipeline Quality 20, System Efficiency 20, Creativity 10. The PDF table is
  no longer the planning baseline. The execution plan's evidence table still uses the old split and needs
  a remap.
- **A 5090 as Studio remote trainer counts** as valid training. The Studio Training Targets route in plan
  §4.4 stays the preferred path.
- **A defect is a cross drawn with a marker pen on a Lego brick.** Superseded on 2026-11-15, see below.

## 2026-11-14 — Python package and workstation runtime

`src/defect_sorter` is a uv project (`pyproject.toml`, `uv.lock`, Python 3.12) with a light default install (NumPy, OpenCV) and opt-in extras `camera` (pyrealsense2, Linux) and `anomaly` (Anomalib 2.7.0 + OpenVINO + CPU torch). Reason: tests run on any laptop while the workstation runs the same code natively with direct D415 and GPU/NPU access. Python 3.12 is what was installed and verified on the workstation (pyrealsense2, Anomalib, OpenVINO); the Docker Anomalib image uses 3.13 and remains an alternative, not yet aligned. Status: adopted on branch `feat/defect-sorter-perception`.

## 2026-11-14 — Perception: depth for objects, colour for bowls

The table background stays cluttered, so objects are found by height above a fitted table plane (D415 depth) rather than by appearance, and shallow bowls by colour. The D415 colour sensor uses a fixed 4600 K white balance because auto white balance shifted every hue under venue lighting. Evidence: live run on 2026-11-13/14 (see handoff). Status: adopted.

## 2026-11-14 — Workstation runtime layout

One checkout at `~/junction` holds our code and the Studio submodule. Studio runs from the submodule's
`application/docker` compose (compose project `docker`, profile `xpu`, privileged) with the prebuilt
`physical-ai-studio-xpu:main` image, chosen for speed over a source build. The submodule pin
(`junction2026`, `17714488`) and the running image (`main`) therefore differ; results must record which
one they used. The old `~/Downloads` copy is unused. Status: adopted.

## 2026-11-14 — SO-101 wrist roll uses the full-turn range on both arms

Wrist roll has no mechanical stop, so the recorded range depends on how far the operator turned it.
Both arms now use [0, 4095] (LeRobot's convention), keeping leader and follower on the same scale.
Re-running Studio's calibration wizard overwrites this and must be followed by the same adjustment.
Status: adopted; evidence in the 2026-11-14 hardware handoff.

## 2026-11-14 — Camera USB topology

Two uncompressed 640×480 UVC streams plus the D415 do not fit through one USB 2 hub. Keep the wrist and
front cameras on different laptop ports (separate hubs), and prefer the D415 on a USB 3 link.
Status: adopted; the D415 still enumerates as USB 2.1 and works at 640×480 colour.

## 2026-11-14 — Automatic calibration lives in a project-agnostic library

Calibration by hand in Studio is slow and error-prone, so end stops are found by driving into them. The code is the
`armkit` workspace package so other projects can reuse it, with no dependency on this repo. Safety rules: bounded push
(goal leash plus low torque limit), step back on a rapid load rise and retry slower rather than fail, park the other
joints by the 3D model's collision shapes before each sweep, never run a plan with issues, previous calibration is backed
up and restored on failure, servo faults stop everything and are never retried. Status: adopted; simulation-tested only.

## 2026-11-14 — The armkit model frame comes from the camera joint fit, not a hand-held pose

The frame recorded with the arm held "in the SO-101 zero pose" disagrees with the camera marker fit by 27° (shoulder
lift) and 21° (elbow). Evidence that the hand-held frame is the wrong one: the nose-down incident (tip on the table)
reads as tip 19 cm up in the hand frame but as contact in the camera frame and with "stored midpoint = model zero"; the
SO-101 `so101_new_calib` URDF is built so the range midpoint is the model zero, and the camera fit (26 poses, 4 mm RMS,
3.5° base tilt) agrees with that to within 7°. In the camera frame the hand-held reference pose had the forearm level
(right) but the upper arm 42° forward, not the described 14°. Planning uses the camera-based frame (lift, elbow, wrist
flex from the fit; pan and roll offsets and all directions from the hand-held checks). Consequence: plans made with
the hand frame had far less table clearance than reported (shoulder-forward check: about 2 cm by the collision spheres,
not 8.7 cm). Status: adopted for the next hardware session; verify on the arm before the first sweep.

## 2026-11-15 — Defect definition: a brick that is not one solid colour

A brick is defective when it is not a single solid colour; marker marks and stuck-on tape both count. The bricks
recorded so far carry scraps of grey duct tape on any face, and come in red, orange, yellow, lime and teal. The
table is covered in the same grey tape, so inspection isolates the brick (saturation mask, convex hull, constant
fill outside) instead of removing tape, which would also remove the defect. Status: adopted (linan).

## 2026-11-15 — scripted-move reach limit 40 cm (hard cap 42 cm)

The user raised the scripted moves' reach limit from 30 cm (hard cap 35) to 40 cm by default with a 42 cm hard cap,
after planning showed the SO-101 reaches a brick at table height to about 42 cm with a 45° approach. All other
checks are unchanged (table floors, servo ranges, speed cap, stop on tracking lag). Far moves are the least
accurate and the most loaded; the first move to a new far area is a dry run, then the operator's go.
