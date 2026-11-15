# Dataset inspect-v1: pick up, show to the camera, then place

Teleoperated episodes for the inspect-then-sort loop. From the top camera alone, Anomalib (PatchCore) reaches a
mean AUROC of only 0.78 under episode-level cross-validation on sort-depth-v2, because tape on a brick's side or
underside is invisible from above. In this loop the robot first shows the brick to the front camera, turning it so
the sides and the bottom face the camera. Anomalib scores that close view, and the result selects the place task:

```text
"Pick up the brick and show it to the front camera."   (policy)  ->  brick held still at the inspection pose
        Anomalib on the front-camera frames of the hold    ->  good / defective / uncertain
"Place the brick in the green bowl." | "...pink bowl."  (policy, chosen by the result)
```

This matches the brief's reference flow (one policy acts on the object, Anomalib observes, SmolVLA branches) and
keeps the defect decision outside the policy: the policy never has to recognise a defect.

## Studio identifiers

| Item | Value |
| --- | --- |
| Project | Defect Sorting (Intel Challenge) `4288b76c-bcbe-4717-9f3c-e0a58bba7c9c` |
| Environment | Sorting cell + depth `82b8829f-799a-4457-bba0-4d64a3ff302d` (`front`, `wrist`, `top_rgb_v2`, `top_depth_v2`) |
| Dataset | inspect-v1 `a9ea91fe-9417-449c-85ff-197665f62ea9` (default task: the show task) |
| Depth bridge | as for sort-depth-v3 in [SORT_V1.md](SORT_V1.md) (`plane-v3.json`, same crop) |
| Recording rate | 30 fps |

## Task text (exactly one of three strings, set before each episode)

| Episode | Task text |
| --- | --- |
| Show | `Pick up the brick and show it to the front camera.` |
| Place, good brick | `Place the brick in the green bowl.` |
| Place, defective brick | `Place the brick in the pink bowl.` |

The place texts differ from sort-v1's ("Pick up the brick and place it in ...") on purpose: a place episode starts
with the brick already in the gripper, so it is a different task and must not be mixed with the whole-task one.

## One brick = two episodes

1. **Show episode** (task: show). Start with the arm at rest and the brick on the table.
   1. Pick the brick up (approach from above, jaws down, as in sort-v1).
   2. Bring it to the **inspection pose**: in the middle of the front camera's image, about 20–25 cm in front of
      it and 8–12 cm above the table, so the brick fills roughly a fifth of the image width with white table behind
      it.
   3. **Hold still 1 s.** Roll the wrist about +90°, **hold 1 s**; roll to about −90°, **hold 1 s**; tilt the
      wrist so the bottom faces the camera, **hold 1 s**; return to level.
   4. End the episode while still holding the brick at the inspection pose.
2. **Place episode** (task: green or pink, from the plan below, not from what the operator sees). Start holding
   the brick at the inspection pose; put it in the bowl, open the gripper, return to rest; end the episode.

Keep the leader still between the two episodes so the place episode starts from the pose where the show episode
ended. If Studio cannot start the next episode without letting go, put the brick down, end the pair, and note the
pair number; do not record a place episode that starts from the table.

## Before each session

- Front camera mount fixed (its view changed between sort-depth-v2 sessions); nothing behind the inspection pose
  but the white table, no hands or people in its view during the holds.
- `sorter-camera-lock --apply` on the workstation; every line `ok` (exposure, white balance, focus, 50 Hz).
- Depth bridge running with `plane-v3.json`; check alignment drift as in SORT_V1.md.
- Two practice pairs first, then check them (task text, the four holds, the place episode's start) before
  recording the plan.

## Recording plan (40 bricks = 80 episodes)

Blocks of 8 bricks, 4 good and 4 defective in a non-alternating order; bowl layout **A** (pink left, green right)
and **B** (swapped) by block. Defective bricks are the taped ones; **tape face** is how the brick lies on the table
before the pick: tape on top, on a side, or underneath. That spread is what the front-camera view has to cover.
Positions and yaws as in sort-v1 (3 × 3 grid, near ≈ 12 cm, mid ≈ 18 cm, far ≈ 24 cm, left/right ≈ ±8 cm).

| # | Layout | Brick | Colour | Tape face | Position | Yaw | Place task |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | A | good | orange | — | near-left | 0° | green |
| 2 | A | defective | any taped | top | mid-centre | 45° | pink |
| 3 | A | defective | any taped | side | far-right | 90° | pink |
| 4 | A | good | red | — | near-centre | 135° | green |
| 5 | A | defective | any taped | bottom | mid-right | 0° | pink |
| 6 | A | good | yellow | — | far-left | 45° | green |
| 7 | A | good | blue | — | near-right | 90° | green |
| 8 | A | defective | any taped | side | mid-left | 135° | pink |
| 9 | B | good | lime | — | far-centre | 45° | green |
| 10 | B | defective | any taped | top | near-left | 90° | pink |
| 11 | B | defective | any taped | side | mid-centre | 135° | pink |
| 12 | B | good | orange | — | far-right | 0° | green |
| 13 | B | defective | any taped | bottom | near-centre | 45° | pink |
| 14 | B | good | yellow 2x4 | — | mid-right | 90° | green |
| 15 | B | good | yellow | — | far-left | 135° | green |
| 16 | B | defective | any taped | side | near-right | 0° | pink |
| 17 | A | good | blue | — | mid-left | 90° | green |
| 18 | A | defective | any taped | top | far-centre | 135° | pink |
| 19 | A | defective | any taped | side | near-left | 0° | pink |
| 20 | A | good | lime | — | mid-centre | 45° | green |
| 21 | A | defective | any taped | bottom | far-right | 90° | pink |
| 22 | A | good | orange | — | near-centre | 135° | green |
| 23 | A | good | red | — | mid-right | 0° | green |
| 24 | A | defective | any taped | side | far-left | 45° | pink |
| 25 | B | good | yellow | — | near-right | 135° | green |
| 26 | B | defective | any taped | top | mid-left | 0° | pink |
| 27 | B | defective | any taped | side | far-centre | 45° | pink |
| 28 | B | good | yellow 2x4 | — | near-left | 90° | green |
| 29 | B | defective | any taped | bottom | mid-centre | 135° | pink |
| 30 | B | good | lime | — | far-right | 0° | green |
| 31 | B | good | orange | — | near-centre | 45° | green |
| 32 | B | defective | any taped | side | mid-right | 90° | pink |
| 33 | A | good | red | — | far-left | 0° | green |
| 34 | A | defective | any taped | top | near-right | 45° | pink |
| 35 | A | defective | any taped | side | mid-left | 90° | pink |
| 36 | A | good | yellow | — | far-centre | 135° | green |
| 37 | A | defective | any taped | bottom | near-left | 0° | pink |
| 38 | A | good | blue | — | mid-centre | 45° | green |
| 39 | A | good | lime | — | far-right | 90° | green |
| 40 | A | defective | any taped | side | near-centre | 135° | pink |

Use every taped brick in turn for the "any taped" rows. A failed pick or a dropped brick: discard both episodes of
that pair and redo the row.

## How the dataset is used

| Use | Taken from inspect-v1 |
| --- | --- |
| Show policy (ACT or SmolVLA) | Show episodes |
| Place policy (SmolVLA, two texts) | Place episodes; the Anomalib result picks the text at run time |
| Anomalib, front view | Front-camera frames of the four holds: good bricks train, taped bricks test (split by brick) |
| Anomalib, top view | Top-camera frames before the pick, as for sort-depth-v2 |

Episodes stay in Studio storage and are never committed: the front and wrist cameras can see people.
