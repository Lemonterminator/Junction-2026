# Dataset place-v1: place the held brick in the bowl the instruction names

The language-conditioned step of the hybrid cycle. After the scripted show, the brick is held level in front of the
front camera; Anomalib's result picks the instruction, and a SmolVLA policy trained on this dataset carries the
brick to that bowl and lets go. This is where the defect decision reaches the robot as language through a VLA.

| Item | Value |
| --- | --- |
| Dataset | place-v1 `1da12999-cc46-42f7-a72a-2783fc9c5c08` |
| Environment | Sorting cell + depth `82b8829f-799a-4457-bba0-4d64a3ff302d` (bridge `plane-v4.json`, crop 96 0 512 416) |
| Task text | exactly `Place the brick in the green bowl.` or `Place the brick in the pink bowl.` (default: green) |
| Target | 30 episodes, 15 per bowl, about 8–10 s each |

sort-depth-v2's place motions cannot be reused: that dataset was recorded in an earlier layout of the cell (the top
camera looked at another part of the table and the bowls stood elsewhere). inspect-v1 and today's cell share one
layout, so the bowls must stay exactly where they are now (green left, pink right, seen from the top camera).

## One episode

1. Start pose: the brick held level in front of the front camera, where the show routine ends
   (`hybrid.SHOW_ROUTINE`, "return": pan 42, lift −19, elbow 59, wrist flex 0, roll 0 in Studio units). Hold the
   leader there, gripper closed on the brick; small differences from episode to episode are good.
2. Set the task text for this episode, then press **Record**.
3. Carry the brick to the named bowl at a steady pace without pauses, lower it to a few centimetres above the bowl,
   open the gripper, lift about 5 cm. Press **Stop**.
4. Take the brick out, return the leader to the start pose with the brick for the next episode.

## Plan

Alternate the bowl in an irregular order (for example G P P G P G G P …), never more than three of one in a row,
so the instruction, not the episode order, decides the bowl. Use several brick colours, good and taped: the bowl
must follow the text, not the brick's look. Discard episodes with a drop, a regrip or a long pause.
