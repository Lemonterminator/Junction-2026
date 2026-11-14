# Marker alignment: printed markers, a self-levelling table frame, drift checks

Short brief for the team. Code: `src/defect_sorter/markers.py`, `alignment.py`, `alignment_page.py`
(PRs #4 and #7). Live page: `uv run sorter-alignment --host <tailscale-ip> --port 8091`.

## The problem

The top camera (RealSense D415) cannot look straight down at the work area; it sits across the table at a
tilt of about 29°. Positions measured in the camera's own coordinates therefore change whenever the camera is
tilted, moved or bumped, and so would anything built on them: bowl and object positions, where the robot base
is, a "did the base move" check, and the data we record for the policy and the defect model. We also want a way
to find the robot's position without measuring it by hand.

## The idea

1. **Print ArUco markers** (small black-and-white squares that OpenCV recognises, each with an id) and tape them
   to fixed things: two **table anchors** (60 mm, ids 16 and 17), the two **bowls**, the **robot clamp**, and the
   **gripper**. Print them with `uv run sorter-marker-sheet`; the sheet has a 100 mm ruler to check the print scale.
2. **Take tilt and distance from depth, not from the picture.** A flat marker seen nearly face-on gives its
   sideways position precisely but its tilt only to about 10–15° from the image. The D415's aligned depth image
   gives the marker's plane directly, to under a millimetre of residual.
3. **Self-levelling.** Fit the table plane from the depth scan. Its normal is "up", whatever the camera's tilt.
   The anchors 16 → 17 give the horizontal x axis. Every marker is then reported in this **table frame**:
   x and y in mm, **height above the table**, tilt from flat, heading, and the facing direction for upright
   markers (the clamp marker on the side of the base).
4. **Drift check.** The reference is saved in the table frame. Bump the camera and nothing looks moved; move the
   robot base or a bowl by more than 3 mm (or turn it by more than 1°) and its marker turns red on the page.

```
camera view (tilted 29°)  --depth plane fit-->  level table frame  --markers-->  x, y, height, tilt, heading
```

## What each marker is for

| Ids | Size | Where | Needed for |
| --- | --- | --- | --- |
| 16, 17 | 60 mm | flat on the table, far apart | defines the table frame (required) |
| 0 or 2 | 18–20 mm | side of the follower's clamp | robot base position and facing direction |
| 10, 11 | 40 mm | on the bowls | bowl positions, "did a bowl move" |
| 4 (5–9) | 30 mm | follower gripper bracket, arm | planned joint calibration (see below) |
| 12–15, 18, 19, 3 | 20–40 mm | free | spares, extra reference points |

The roles are a convention in `MARKER_SET`; the code only requires 16 and 17 for the frame.

## What was measured (2026-11-14, real cell, camera tilted 28.5°)

- Markers lying on the table read **−4 to +3 mm** height and 0–7° tilt in the table frame.
- The distance between the two anchors is **523.0 mm** both in camera space and in the table frame.
- A marker on the upper arm reads about 155 mm above the table; one on the forearm about 216 mm.
- Tests prove the invariance with synthetic views: two different camera mountings give identical table poses and
  no drift, and a 10 mm marker shift is still detected after the camera was moved.
- Depth under a marker is checked; unusable depth (too few pixels, or plane RMS above 3 mm) falls back to the
  image pose and the page labels the marker `[image]`. On the real frame a marker at the image edge read −447 mm
  from a depth jump before this check existed.

## Limits, stated plainly

- These checks show the method is **self-consistent** (flat things read flat, distances agree). They are **not**
  an accuracy measurement against an independent ground truth such as a ruler on the table.
- Markers only help while detected. The clamp marker is on a vertical face and was at the image edge in the last
  look, so it was not yet detected; the camera, or the marker position, still needs adjusting.
- Without both anchors in view the frame is still level (heights and tilts are right) but its horizontal axes follow
  the camera, so horizontal positions are then only comparable while the camera stays put. The page says so.
- Small face-on markers seen without usable depth have poorly known tilt (10–15°).
- Only one process can open the D415: stop the page before Studio records.

## Not built yet (proposal)

**Joint calibration from the camera.** With markers on the follower's gripper and arm, record about 15 poses
(motor readings plus the marker poses in the table frame) and fit each joint's zero offset against the arm's
forward kinematics from the URDF. That would give correct joint zeros, the wrist roll included, without judging
angles by eye, and the camera-to-robot transform for a scripted fallback pick. Estimated 2–3 hours; time-boxed.
The leader arm needs no markers: it can be matched to the corrected follower through teleoperation.

## 中文摘要

- **问题**：顶部相机不能垂直向下看，约倾斜 29°；相机坐标会随相机倾斜或被碰动而变化。
- **做法**：打印 ArUco 标记贴在桌面（锚点 16、17）、碗、机械臂底座夹具和夹爪上；用 D415 深度图拟合桌面，得到
  水平的“向上”方向，再以锚点 16→17 作为 x 轴，建立**桌面坐标系**。所有标记都以此坐标系报告：x、y（毫米）、
  离桌面高度、倾斜角、朝向。相机倾斜因此被“自动找平”。
- **漂移检测**：参考值保存在桌面坐标系中；相机被碰动不会误报，底座或碗真的移动超过 3 mm（或转过 1°）才会标红。
- **实测**：贴在桌面上的标记高度在 −4 到 +3 mm；两个锚点距离在相机坐标与桌面坐标中一致（523.0 mm）。
  这只是自洽性检查，**不是**与独立真值对比的精度测量。
- **未完成**：夹具侧面标记尚未被检测到；基于标记的关节标定只是方案，尚未实现。
