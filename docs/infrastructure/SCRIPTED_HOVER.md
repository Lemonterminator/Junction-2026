# Scripted brick hover: calibration and run

How the follower is brought to a brick seen by the top camera, ready for a grasp: the robot calibration from a
short recorded touch episode, then a checked move to the standoff point in front of the brick. Every move is a
dry run unless `--go`; never run `--go` without someone at the arm.

## What is measured

| Item | From | Module |
| --- | --- | --- |
| Table frame | Anchor markers 16 → 17 and the fitted table plane | `alignment` |
| Brick pose (centre, long-axis yaw, size, top height) | Top camera colour + depth, top face only | `targeting.brick_pose` |
| Robot base pose and lift/elbow/wrist zeros | Jaw-tip touches on table markers in a recorded episode | `episode_calibration --touch` |
| Approach and wrist roll | Kinematic model and the calibration | `targeting.choose_approach`, `motion.plan_brick_hover` |

## 1. Calibrate (one short recording)

1. Create an empty dataset in Studio for the touch episode; the robot must not move afterwards (re-record if it
   does).
2. Record one or two episodes: start at rest, **close the gripper**, put the closed jaw tip on the centre of each
   reachable table marker (16, 17, 18, 7 in the current cell) and hold still about 2 s; return to rest. Touch every
   marker in two different arm postures (once with the gripper steep, once leaning): the lift, elbow and wrist zeros
   only separate when one point is reached with different joint angles.
3. Run the fit inside Studio's backend environment (it has PyAV), with the bridge's plane file and the D415
   intrinsics:

```bash
python -m defect_sorter.episode_calibration <dataset dir> --touch --targets 16 17 18 7 \
  --plane <plane file> --intrinsics FX FY PPX PPY --crop 96 0 --ranges <Studio robots JSON> \
  [--target-at ID X Y Z ...] --save data/calibration/robot.json
```

It prints, per touch, which marker it matched, the fitted error and the **unseen** (leave-one-out) error, then the
base pose and the joint zeros. Judge the calibration by the unseen errors: they are what a move will miss by.
`--target-at` gives a marker's table position (mm) when the arm hid it in every hold; `--trust-zeros` keeps
Studio's zeros and fits only the base.

Measured in the current cell (2026-11-15, 8 touches): zeros lift −5.6°, elbow −6.4°, wrist −1.2°; fitted RMS
8.1 mm; unseen errors 6–17 mm, mean 11 mm. Studio's own zeros, trusted, missed by 22 mm RMS.

## 2. Hover in front of a brick

```bash
sorter-move --port <follower port> --calibration data/calibration/robot.json --above-brick \
  --bridge http://<bridge host>:8092 [--near X Y] [--approach auto|down] [--standoff 60]
```

- The brick is measured over 10 frames through the running depth bridge, so Studio can keep recording; objects
  within 12 cm of the robot base are never taken for the brick.
- The table frame is saved (`--frame-file`) whenever anchors 16 and 17 are both seen; while one is hidden (the arm
  standing near it) the saved frame is used if at least two fixed tags in view (16, 17, 18, 7) are within 5 mm of
  where they were, i.e. the camera has not moved.
- The grasp point is half way up the brick. `--approach auto` tries 0, 15, 30, 45, 60 and 75° from vertical,
  leaning out along the line from the base, and takes the steepest one whose whole path passes the checks; the
  standoff point lies `--standoff` mm back along that approach. The wrist roll closes the jaws across the brick's
  long axis (either pair of sides for a square 2x2 Duplo), turning the wrist least.
- Every waypoint is checked: tool and wrist/elbow floors, the reach limit (40 cm by default, `--reach` up to the
  42 cm hard cap), the servo ranges. A refusal says
  which approach failed and why. Studio must not hold the follower's port (unload the environment first).

## Where the brick may lie (current cell, from the folded rest pose)

Planned for real with the 2026-11-15 calibration and the 40 cm reach limit; the number is the approach chosen
(degrees from vertical), `.` is refused. Table millimetres: x along anchor 16 → 17, y negative toward the camera
(tag 18 is at y −78, tag 7 at y −164).

```
 x:  -20  10  40  70 100 130 160 190 220 250 280
 40   15   0   0  15  15   .   .  15  15   0   0
 10   15  15   0   0   0  15  15   0   0   0  15
-20   15  15  15   0   0   0   0   0   0  15  15
-50   15  15  15  15  15  15  15  15  15  15  15
-80   15  15  15  15  15  15  15  15  15  15  15
-110  30  15  15  15  15  15  15  15  15  15  15
-140  30  30  30  30  15  15  15  15  30  30  30
-170   .  30  30  30  30  30  30  30  30  30  30
-200   .   .   .  45  45  30  30  45  45   .   .
-230   .   .   .   .   .   .   .   .   .   .   .
```

From rest the arm first lifts with the gripper as it is, then turns it to the approach; after the lift the normal
floors (tool 20 mm, joints 10 mm) apply again.

## 3. Hold over a bowl (as if to let go of a brick)

```bash
sorter-move --port <follower port> --calibration data/calibration/robot.json --above-bowl green|pink \
  --bridge http://<bridge host>:8092 [--clearance 80] [--reach 420]
```

- Colour finds each bowl's region; depth finds its rim: the pixels standing 6–50 mm above the table there are moved
  into the table frame and a circle is fitted to them, robustly, so bricks lying in the bowl do not move it. Result:
  rim centre, radius and height (`--measure-only` prints them without touching the arm).
- The drop point is the bowl's centre if reachable, else the first point toward the robot, 1 cm at a time, that the
  whole path passes the checks for; always at least 3 cm inside the rim and `--clearance` mm above it. The wrist
  roll is left as it is.
- Measured in the current cell (2026-11-15): green rim (7, −235) mm, pink (264, −252) mm, both 90 mm radius, rim
  10 mm high, repeatable to 1 mm. Their nearest drop points are just past 40 cm from the base: use `--reach 420`
  (the hard cap). Dry runs then pass: drop points 40 mm from each centre toward the robot, 90 mm high.

## 4. Overview: show the held brick to the cameras

Taught by demonstration: record one Studio episode holding the brick, pausing about 1 s at each view. The pauses
become keyframes (`episode_calibration.still_moments`), the path between them is kept as waypoints wherever a joint
moved 10°, and the sequence is saved with `motion.save_keyframes` (here `data/sequences/overview.json`, from
overview-demo-v1: views #0, #2, #3, #4, #6, ending at the last one).

```bash
sorter-move --port <follower port> --calibration data/calibration/robot.json --play data/sequences/overview.json [--speed 20]
```

`motion.plan_keyframes` trusts the taught poses and checks the blends between them: no step may take the tool or the
elbow/wrist joints lower than the lower of its two poses, the reach limit, the servo ranges and the speed limit hold,
and every view is held for its time. Only body joints move; the gripper keeps its grip. First run (2026-11-15):
51 poses, 5 held, 69.5 s at 10°/s, completed.

Version 2 (`data/sequences/overview-v2.json`, the default of the operator wrapper) is partly computed: at view #0's
arm pose the wrist rolls to 0°, −83°, back through 0° and to +83° (the calibrated wrist range is about ±84°, so ±90°
cannot be commanded; passing back through 0° keeps every swing from dipping below both of its poses), then the
bottom of the brick is shown square to the front camera: view #6's point with the jaw axis turned exactly horizontal
in the same direction (pan 32°, lift −13.5°, elbow 67.4°, wrist −40.7°). At #0 the jaw axis points at the front
camera (25° below horizontal), so the roll mostly spins the bottom face in view; for the four side faces the jaws
would have to point straight down there. Dry run from the arm's pose: 47 s at 10°/s, tool never below 89 mm.

## Limits of the current cell

- With the jaws straight down the arm reaches only a band about 17–25 cm from the base (the wrist flex stops at
  95°); tilted approaches (up to 45° here) extend that to the 40 cm reach limit. The arm plans to about 42 cm;
  far out it is most loaded and the calibration error grows with distance. The bowl markers, about 50 cm from the
  base, stay out of reach.
- Tilted hover measured with the touch calibration (2026-11-15): brick 6 cm beyond the jaws-down band, 15°
  approach, gripper (+10, −12, +15) mm from the planned standoff.
- Hover accuracy measured with the jaws-down calibration: height within 3 mm; sideways 3–17 mm along the anchor line
  and a constant ~22 mm toward the camera, part of which is how the depth camera sees the front of the jaws. A
  wrist-camera check settles how much of that offset is real.
