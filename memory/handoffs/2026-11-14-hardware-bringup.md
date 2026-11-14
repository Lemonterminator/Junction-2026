# 2026-11-14 — Hardware bring-up: calibration and teleoperation

- Author: Matvii
- Branch and commit: `docs/hardware-bringup-status` (documentation of work done directly on the workstation)
- Scope: workstation checkout, Studio project, SO-101 motor IDs and calibration, teleoperation, camera USB layout

## Changes

- Workstation: single checkout `~/junction`; Studio runs from `external/physical-ai-studio/application/docker`
  (`docker compose -p docker`, prebuilt `physical-ai-studio-xpu:main`); the existing Studio data volume was reused.
- Follower `5AAF262737` motor IDs renumbered from reverse order to 1–6 (temporary IDs 10–12, torque off).
- Follower wrist roll: homing offset 1394 → 923, position limits [210, 3967] → [0, 4095].
  Leader `5AE7045026` wrist roll: offset 300 → 292 (neutral kept), limits [133, 3947] → [0, 4095];
  Studio's stored leader calibration updated to match. Revert values are the "before" numbers above.
- Follower shoulder pan protection: max torque 500 → 1000, torque limit 500 → 1000, protection current
  250 → 310, overload torque 25 → 80 (matches the other body joints). Leader protection values were already stock.
- Studio environments `Sorting cell` and `Arms only (teleop test)`; camera entries re-synced after USB moves.
- Workstation power: lid close ignored via a logind drop-in; GNOME idle suspend disabled.

## Evidence

- Every register write was read back; other motors' values were compared before and after (unchanged).
- Motor-ID mapping measured with a read-only position probe while joints were moved by hand; after the
  renumber, base → ID 1 and gripper → ID 6.
- Wrist direction measured: turning the follower wrist counter-clockwise (seen from the tip) decreases ticks.
- Follower bus stress test: 597/597 sync reads at 30 Hz, p50 1.2 ms, with and without a camera streaming.
- Studio logs for the failed teleop attempts: follower "Sync read failed with comm result −6" ~1 s after
  the teleop control started; no USB disconnect in the kernel log at that time.
- Three cameras streamed together on the two-hub layout (D415 29 fps); on one hub the front webcam failed
  to allocate USB bandwidth at every tested format.
- Teleoperation working: observed by the user at the arm; not measured by a script.
- Arm motion only happened when the user asked for it (one Studio identify wiggle; teleop by the user).

## Open questions and next steps

- Root cause of the earlier teleop dropouts is not proven (power dip on the first large move is the leading
  explanation). If it returns: match the leader pose to the follower before enabling teleop, check the
  follower adapter rating (12 V, ≥ 5 A expected) and read the follower's voltage and protection registers.
- Leader/follower wrist neutral agreement not checked; a constant offset can be measured and corrected.
- The D415 still links at USB 2.1; a USB 3 cable/port would leave more headroom.
- Concrete next action: freeze camera and bowl positions, record the first `Sorting cell` episode in Studio,
  then capture good-object crops for the Anomalib baseline.
