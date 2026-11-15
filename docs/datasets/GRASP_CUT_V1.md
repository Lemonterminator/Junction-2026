# Dataset grasp-cut-v1: grasp-from-hover clips cut from recorded episodes

Training data for the learned step of the hybrid cycle (`sorter-hybrid`, `src/defect_sorter/hybrid.py`): a scripted
move brings the open jaws about 6 cm above the brick, turned across it, and a policy does the rest of the grasp. No new
recording was needed: every clean grasp in sort-depth-v2 and inspect-v1 already contains that motion.

sort-depth-v2 was recorded in an earlier layout of the cell: its top camera looked at another part of the table and
the bowls stood elsewhere. Only its wrist view matches today's cell; grasp-cut-inspect (inspect-v1 only) matches
today's layout in every camera, which is why both variants are trained and compared on inspect-v1 held-out clips.

These clips bootstrap the grasp policy. Their start states only approximate the script's standoff (operators came
in from above and rarely paused), so episodes recorded from the real standoff
([grasp-from-standoff-v1](GRASP_FROM_STANDOFF_V1.md)) are the better data and should be added once recorded.

## Studio identifiers

| Dataset | Source episodes | Episodes | Frames | Studio id |
| --- | --- | --- | --- | --- |
| grasp-cut-both | inspect-v1 (30) + sort-depth-v2 (32) | 62 | 9 495 | `74bb9fa4-dfe2-4f6d-8bea-8467fb92b745` |
| grasp-cut-inspect | inspect-v1 (30) | 30 | 4 437 | `99f5fd88-12ee-4afc-ae54-c744c954e728` |
| grasp-cut-holdout | inspect-v1 episodes 2, 8, 15, 21, 28, 34 | 6 | 924 | not in Studio (offline comparison only) |

Environment: Sorting cell + depth. Cameras: `wrist`, `top_rgb_v2`, `top_depth_v2` (the front camera plays no part in a
grasp). Task text: `Pick up the brick.` 30 fps, the follower calibration of both sources is the same Studio robot entry.

## How a clip is cut

1. **Grasp**: the gripper, after having been open wider, settles at a brick-width opening (9..21, steady for 1 s), and
   the jaw tip then rises at least 30 mm within 3 s. Half-open approaches and regrips are therefore not taken for a
   grasp. 68 of 73 episodes have one (5 rejected: failed or fumbled grasps).
2. **Start**: the last frame, at most 4 s before the gripper starts closing, where the jaw tip is 65 mm above its height
   at the close (the hover script's 60 mm above the brick top, plus the tip sitting a little below the top when it
   grips). The tip height comes from `armkit` forward kinematics of the recorded joints (Studio normalized units to
   degrees around the range midpoint). Operators rarely paused at a hover, so many clips start mid-descent; in some
   sort-depth-v2 episodes the operator spent more than 4 s aligning at the brick and the clip starts low.
3. **End**: 10 frames after the brick is 40 mm up, at most 2 s after the close.

Videos were decoded from the source and encoded again with Studio's codec (AV1, yuv420p, GOP 2) at CRF 20 instead of
30, so the second encoding costs as little of the depth image's precision as possible (the recorded layered height
image keeps about 2 mm on the table). A contact sheet of every clip's first and last wrist frame was checked: each clip
starts with the brick ahead of the open jaws and ends with it held.

The cutting script (`cut_grasps.py`) and the offline comparison (`eval_grasp.py`: where the policy closes the gripper
against where the operator did, in millimetres, on the held-out clips) are exploration tools kept on the workstation in
`~/policy-eval/`; they are not part of the package yet.

Episodes stay in Studio storage and are never committed: the cameras can see people.
