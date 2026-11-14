# Dataset sort-v1: teleoperated brick sorting

One dataset of full sorting episodes recorded with the leader arm in Physical AI Studio. It is meant to train three
kinds of policy from the same recordings, so the open control-split decision does not block recording:

| Use | What it takes from sort-v1 |
| --- | --- |
| Whole-task policy (one learned policy for everything) | Whole episodes; ACT has no text input, so one ACT per bowl (filter by task) |
| Language-conditioned VLA (SmolVLA) | Whole episodes with their task text; the defect result picks the text at run time |
| Hybrid (scripted hover, learned grasp) | The clip from the hover pause to the lift, cut automatically |

## Studio identifiers

| Item | Value |
| --- | --- |
| Project | Defect Sorting (Intel Challenge) `4288b76c-bcbe-4717-9f3c-e0a58bba7c9c` |
| Environment | Sorting cell `876c0839-30ea-4c86-9eb2-be9451e2c411` (follower, leader, cameras `top`, `wrist`, `front`) |
| Dataset | sort-v1 `7a4864a0-f49c-4fc5-adaa-5f88b74eea58` |
| Recording rate | 30 fps (Studio default) |
| Alignment reference | `data/alignment/reference-sort-v1.json` on the workstation (anchors 16 → 17); check drift before each session |

## Depth variants

Studio records the RealSense in colour only. For a depth input, `sorter-depth-bridge` owns the D415 and serves
colour and a depth image as MJPEG streams; Studio records them as two IP cameras. While the bridge runs, the direct
RealSense camera `top` (and so the plain "Sorting cell" environment) cannot open; record in one environment per
session. A depth dataset is a superset: a colour-only policy simply leaves `top_depth` out at training time. Never mix
depth encodings in one dataset; the bridge logs mode, scales, plane, crop and filters at start.

### sort-depth-v1 (deleted)

The first depth setup (environment "Sorting cell + depth", IP cameras `top_rgb`/`top_depth` at 640×480, dataset
sort-depth-v1) was deleted from Studio on 2026-11-14 with no episodes recorded. Its encoding was one grey channel,
height above the table on a fixed 0–10 cm scale, plane refitted every 10 s; v2 replaces it.

### sort-depth-v2 (record here)

| Item | Value |
| --- | --- |
| Environment | Sorting cell + depth v2 `f0ad6d59-9baf-4e8f-9915-8d5370ba8346`: `front`, `wrist`, `top_rgb_v2`, `top_depth_v2` |
| Cameras | `top_rgb_v2` `5a8f2704-5fd7-41e6-9a3f-c3444fc71962` → `/top.mjpg`; `top_depth_v2` `ccf35db6-3ada-4aa9-ad88-d1b441f8c8fb` → `/top_depth.mjpg`; both IP cameras at 512×416, 30 fps |
| Dataset | sort-depth-v2 `a3b5452e-0693-47e6-8902-5f1efdc82515` |
| Bridge | `sorter-depth-bridge --host 100.76.18.70 --port 8092 --plane data/depth/plane-v2.json --crop 96 0 512 416` (defaults: `layers`, R 0–4 cm, G 0–30 cm, `motion` filters, camera preset) |
| Table plane | `data/depth/plane-v2.json` on the workstation: 92 % inliers, camera 508 mm above the table |

Studio resizes every IP-camera frame to the declared size, so the declared 512×416 must match the crop; a different
crop means new camera entries and a new dataset. Measured on the first v2 frame: brick peak R 122 (1.91 cm for the
1.9 cm brick), table R ≈ 2, 3.5 % of pixels without depth.

What changed from v1 and why:

| Change | Why |
| --- | --- |
| `layers` image: R height 0–4 cm, G height 0–30 cm, B depth valid | Brick detail and gripper height both readable; missing depth is not confused with the table |
| Table plane fitted once and held, saved to `--plane`, a moved camera refused | Same height gives the same value in every episode and session |
| `motion` camera filters (disparity-domain spatial, light temporal, no persistence, no hole filling) | No trails behind the moving arm, no invented depth at its edges |
| `--crop` applied to colour and depth alike, at native size | More of the policy's input pixels on the work area; the left ≈80 px of the D415 depth are dead |
| JPEG 4:4:4 chroma | Detail that differs between the channels survives encoding |

## Task text (exactly one of two strings)

| Brick | Bowl | Task text |
| --- | --- | --- |
| Good (no mark) | green | `Pick up the brick and place it in the green bowl.` |
| Defective (marker-pen cross) | pink | `Pick up the brick and place it in the pink bowl.` |

Type or paste the string when starting the episode; nothing else, no variations. A wrong text can be corrected
afterwards per episode (`PATCH /api/dataset/<id>/episodes/<index>`), so a mistake is not a reason to re-record.

## Episode protocol

Before each session (and after replugging a camera or restarting the workstation) run `uv run sorter-camera-lock
--apply` and check every line says `ok`: it fixes exposure, white balance, focus and 50 Hz mains on `front` and
`wrist`, which otherwise drift with what the camera sees.

1. **Rest.** Follower in its rest pose, gripper open. Press Start in Studio.
2. **Approach and hover.** Bring the gripper above the brick with the jaws pointing straight down, about 6 cm
   above it, jaws turned to match the brick. **Hold still for one second.** This pause is where the hybrid's
   grasp clip starts; without it the episode is still usable for the whole-task policies.
3. **Grasp.** Lower, close the gripper, lift about 5 cm.
4. **Carry and release.** Move above the bowl named in the task text and open the gripper inside it.
5. **Return** towards rest, then press Stop / save.

Move smoothly and not too fast: the policy imitates the speed. Keep the brick in the wrist camera's view during
the approach. Do not touch the follower or the brick by hand during an episode.

## Variation

| Factor | Values | Why |
| --- | --- | --- |
| Brick position | 9 spots on a 3 × 3 grid in front of the robot: near ≈ 12 cm, mid ≈ 18 cm, far ≈ 24 cm from the base; left / centre / right ≈ ±8 cm | Position robustness; jaws-down grasps work up to ~28 cm |
| Brick yaw | 0°, 45°, 90°, 135° relative to the arm's straight-ahead direction | Wrist-roll alignment |
| Bowl layout | **A**: pink left, green right · **B**: swapped | Stops the policy from learning "left = green" |
| Clutter | A second brick placed outside the grasp area, every 4th episode | Judged robustness to clutter |
| Brick type | Good and marked, balanced per block of 14 | Balanced tasks |

Use more than one physical brick of each kind if available, and alternate them.

## Recording plan (56 episodes, 4 blocks of 14)

Swap the bowls between blocks (A → B → A → B) without moving the anchors (13, 14, 16, 17) or the robot base.
Positions and yaws are a guide; close is good enough.

| # | Layout | Brick | Spot | Yaw | Clutter | Bowl |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | A | good | mid-centre | 45° |  | green |
| 2 | A | marked | far-right | 90° |  | pink |
| 3 | A | good | mid-left | 135° |  | green |
| 4 | A | marked | far-centre | 0° | yes | pink |
| 5 | A | marked | near-right | 45° |  | pink |
| 6 | A | good | far-left | 90° |  | green |
| 7 | A | marked | near-centre | 135° |  | pink |
| 8 | A | good | mid-right | 0° | yes | green |
| 9 | A | good | near-left | 45° |  | green |
| 10 | A | marked | mid-centre | 90° |  | pink |
| 11 | A | marked | far-right | 135° |  | pink |
| 12 | A | marked | mid-left | 0° | yes | pink |
| 13 | A | good | far-centre | 45° |  | green |
| 14 | A | good | near-right | 90° |  | green |
| 15 | B | marked | far-left | 0° |  | pink |
| 16 | B | marked | near-centre | 45° | yes | pink |
| 17 | B | good | mid-right | 90° |  | green |
| 18 | B | good | near-left | 135° |  | green |
| 19 | B | good | mid-centre | 0° |  | green |
| 20 | B | marked | far-right | 45° | yes | pink |
| 21 | B | marked | mid-left | 90° |  | pink |
| 22 | B | marked | far-centre | 135° |  | pink |
| 23 | B | good | near-right | 0° |  | green |
| 24 | B | marked | far-left | 45° | yes | pink |
| 25 | B | good | near-centre | 90° |  | green |
| 26 | B | marked | mid-right | 135° |  | pink |
| 27 | B | good | near-left | 0° |  | green |
| 28 | B | good | mid-centre | 45° | yes | green |
| 29 | A | marked | far-right | 135° |  | pink |
| 30 | A | good | mid-left | 0° |  | green |
| 31 | A | marked | far-centre | 45° |  | pink |
| 32 | A | good | near-right | 90° | yes | green |
| 33 | A | marked | far-left | 135° |  | pink |
| 34 | A | marked | near-centre | 0° |  | pink |
| 35 | A | good | mid-right | 45° |  | green |
| 36 | A | marked | near-left | 90° | yes | pink |
| 37 | A | good | mid-centre | 135° |  | green |
| 38 | A | marked | far-right | 0° |  | pink |
| 39 | A | good | mid-left | 45° |  | green |
| 40 | A | marked | far-centre | 90° | yes | pink |
| 41 | A | good | near-right | 135° |  | green |
| 42 | A | good | far-left | 0° |  | green |
| 43 | B | marked | near-centre | 90° |  | pink |
| 44 | B | good | mid-right | 135° | yes | green |
| 45 | B | good | near-left | 0° |  | green |
| 46 | B | marked | mid-centre | 45° |  | pink |
| 47 | B | marked | far-right | 90° |  | pink |
| 48 | B | good | mid-left | 135° | yes | green |
| 49 | B | marked | far-centre | 0° |  | pink |
| 50 | B | good | near-right | 45° |  | green |
| 51 | B | good | far-left | 90° |  | green |
| 52 | B | good | near-centre | 135° | yes | green |
| 53 | B | marked | mid-right | 0° |  | pink |
| 54 | B | marked | near-left | 45° |  | pink |
| 55 | B | marked | mid-centre | 90° |  | pink |
| 56 | B | good | far-right | 135° | yes | green |

## Quality rules

Discard and re-record an episode when:

- a camera dropped out (Studio discards these itself) or the wrist view froze;
- the grasp failed, the brick fell, or it landed outside the bowl;
- the task text does not match the brick (or fix the text instead);
- someone touched the arm or the brick during the episode;
- the episode is under 5 s or over 60 s.

After recording, the episode review tool (`defect_sorter.episodes`) reports per episode: length, missing camera
streams, whether the gripper closed and opened, whether a hover pause was found, and the task text. The cut for the
hybrid's grasp clips uses the same pause and gripper events.

## What is and is not stored in Git

The recordings stay in Studio's storage on the workstation (`/app/storage/datasets/<id>` in the container) and are
never committed: the front and top cameras can see people. This card, the review tool and the derived statistics are
committed.
