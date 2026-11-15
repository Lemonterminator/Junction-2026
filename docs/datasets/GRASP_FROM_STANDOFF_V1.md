# grasp-from-standoff-v1

Training data for the hybrid pick: a script brings the gripper to the standoff point in front of the brick
(`sorter-move --above-brick`, see [SCRIPTED_HOVER](../infrastructure/SCRIPTED_HOVER.md)), and a learned policy
does the grasp from there. Every episode therefore starts at a scripted standoff and contains only the pick.

| Item | Value |
| --- | --- |
| Dataset | grasp-from-standoff-v1 `6d4df092-4ffc-4af8-839e-0be62bb9d054` |
| Environment | Sorting cell + depth `82b8829f-799a-4457-bba0-4d64a3ff302d` (`front`, `wrist`, `top_rgb_v2`, `top_depth_v2`) |
| Task text | `Pick up the brick.` (one task, never changed) |
| Depth encoding | bridge plane `plane-v4.json`, crop 96 0 512 416; a moved camera means a new dataset |
| Target | 40–60 episodes |

## One episode

1. Studio environment unloaded, follower at rest, brick placed in reach (from about 4 cm behind the line
   between tags 16 and 17 to about 17 cm in front of it, i.e. up to tag 7; see the map in SCRIPTED_HOVER); hands out of the top camera's view.
2. Run the scripted hover on the workstation and confirm with Enter; it refuses positions it cannot reach.
3. Hold the leader in roughly the follower's pose, load the environment, start teleop (the follower glides to the
   leader over the grace period; match closely so the glide is small).
4. Press **Record**. Close on the brick, lift it about 5 cm, hold still about 1 s. Press **Stop**.
5. Put the brick down, teleop back to rest, unload the environment.

## Variety across episodes

- Brick position: spread over the whole reachable area, including the edges where the script tilts its approach.
- Brick yaw: all directions; square 2x2 and long 2x4 bricks; several colours.
- Keep the scene otherwise as it is: bowls, tags and lighting unchanged within the dataset.

## Do not record

- Episodes where the scripted hover was refused or stopped; episodes where the glide in step 3 was large (more than
  a few centimetres); failed grasps (drop them, or keep them out of the dataset); people in the top camera view.
