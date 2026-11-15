import sys, json, numpy as np
sys.path.insert(0, "/mnt/c/Users/Jiang/.gemini/antigravity/scratch/hackjunction/scripts/sim")
import so101_sort_sim as sim
from pathlib import Path
DS = Path("/mnt/c/Users/Jiang/.gemini/antigravity/scratch/hackjunction/data/studio/af9b173a-ee59-4e24-97c8-be71dba701ce")
idx = [3217, 3539, 3861, 11405, 11575, 11746, 20154, 20324, 20494, 29892, 30038, 30184, 36322, 36421, 36520]
real, states = sim._real_frames(DS, idx)
real_mask = real[..., 1] > int(255 * 0.04 / sim.COARSE_MAX_M)
layout = sim.Layout(green=(0.0, 1.0), pink=(0.0, -1.0), brick_xy=(2.0, 2.0), brick_yaw_deg=0.0, defective=False)
layout.top = sim.look_from((0.2, 0.0), 0.25, sim.PLANE_HEIGHT_M, 0.0)
cell = sim.Cell(layout, Path("/home/linan/sim/mujoco_menagerie/robotstudio_so101"))
def score(p):
    cell.set_camera("top", p); ious = []
    for k, s in enumerate(states):
        cell.set_joints(sim.normalized_to_rad(s)); z, valid = cell.height("top")
        x0, y0, w, h = sim.TOP_CROP
        m = (z[y0:y0+h, x0:x0+w] > 0.04) & valid[y0:y0+h, x0:x0+w]
        ious.append((m & real_mask[k]).sum() / max((m | real_mask[k]).sum(), 1))
    return float(np.mean(ious))
for f in []:
    p = sim.CameraPose(**json.load(open(f))["camera"]); print(f, round(score(p), 3))
from scipy.optimize import minimize
S = "/mnt/c/Users/Jiang/.gemini/antigravity/scratch/hackjunction/config/sim"
rows = [r for r in json.load(open(S + "/grasp_points.json")) if r["arm_over_brick_m"] > 0.045 and r["px"][0] < 330]
obj = np.array([[*r["jaw_centre"][:2], r["brick_top"]] for r in rows]); img = np.array([r["px"] for r in rows])
def parts(v):
    p = sim.CameraPose(*v); uv, _ = sim.project(p, obj, sim.TOP_FULL)
    e = np.linalg.norm(uv - img, axis=1)
    return p, score(p), float(np.median(e))
def loss(v):
    p, iou, med = parts(v)
    prior = ((v[2] - sim.PLANE_HEIGHT_M) / 0.02) ** 2 + ((v[4] - sim.PLANE_TILT_DEG) / 2.0) ** 2 + ((v[6] - 615) / 30) ** 2
    return -iou + med / 50.0 + 0.02 * prior
starts = [json.load(open(S + "/top_camera_grasp.json"))["camera"], json.load(open("/mnt/c/Users/Jiang/.gemini/antigravity/scratch/hackjunction/config/sim/top_camera_silhouette.json"))["camera"]]
best = None
for c in starts:
    v0 = np.array([c[k] for k in ("x", "y", "height", "yaw_deg", "tilt_deg", "roll_deg", "focal_px")])
    simplex = np.vstack([v0, v0 + np.diag([0.03, 0.03, 0.02, 6.0, 3.0, 2.0, 25.0])])
    r = minimize(loss, v0, method="Nelder-Mead", options={"maxfev": 220, "initial_simplex": simplex})
    p, iou, med = parts(r.x); print("start", c["x"], "->", np.round(r.x, 3), "iou", round(iou, 3), "median px", round(med, 1), flush=True)
    if best is None or r.fun < best[0]: best = (r.fun, p, iou, med)
_, p, iou, med = best
json.dump({"camera": {k: float(v) for k, v in p.__dict__.items()}, "iou": iou, "grasp_median_px": med,
           "method": "arm silhouette IoU + grasp reprojection, priors from plane-v2 height/tilt and D415 focal"},
          open("/home/linan/sim/out/top_camera_joint.json", "w"), indent=2)
print("saved", p)
