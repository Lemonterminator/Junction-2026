import sys, json, numpy as np
from scipy.optimize import least_squares
sys.path.insert(0, "/mnt/c/Users/Jiang/.gemini/antigravity/scratch/hackjunction/scripts/sim")
import so101_sort_sim as sim
S = sys.argv[1]
rows = [r for r in json.load(open(S + "/grasp_points.json")) if r["arm_over_brick_m"] > 0.045 and r["px"][0] < 330]
obj = np.array([[*r["jaw_centre"][:2], r["brick_top"]] for r in rows]); img = np.array(r["px"] for r in rows) if False else np.array([r["px"] for r in rows])
init = json.load(open("/mnt/c/Users/Jiang/.gemini/antigravity/scratch/hackjunction/config/sim/top_camera_silhouette.json"))["camera"]
def make(v, free):
    x, y, yaw = v[:3]
    if free: return sim.CameraPose(x, y, v[3], yaw, v[4], v[5], v[6])
    return sim.CameraPose(x, y, sim.PLANE_HEIGHT_M, yaw, sim.PLANE_TILT_DEG, 0.0, 615.0)
def res(v, free):
    uv, _ = sim.project(make(v, free), obj, sim.TOP_FULL); return (uv - img).ravel()
best = None
for yaw0 in range(0, 360, 20):
    for x0, y0 in ((0.6, 0.0), (0.7, 0.1), (0.6, 0.3), (0.5, -0.2), (0.0, 0.0), (0.3, 0.3), (0.3, -0.3)):
        r = least_squares(res, [x0, y0, yaw0], args=(False,), loss="soft_l1", f_scale=8.0)
        if best is None or r.cost < best.cost: best = r
e = np.linalg.norm(best.fun.reshape(-1, 2), axis=1)
print("fixed h/tilt/f:", np.round(best.x, 3), "median err", np.median(e).round(1), "rms", np.sqrt((e**2).mean()).round(1))
v0 = np.r_[best.x, sim.PLANE_HEIGHT_M, sim.PLANE_TILT_DEG, 0.0, 615.0]
r2 = least_squares(res, v0, args=(True,), loss="soft_l1", f_scale=8.0,
    bounds=([-2, -2, -720, 0.45, 18, -5, 540], [2, 2, 720, 0.57, 34, 5, 680]))
e2 = np.linalg.norm(r2.fun.reshape(-1, 2), axis=1)
print("free:", np.round(r2.x, 3), "median err", np.median(e2).round(1), "rms", np.sqrt((e2**2).mean()).round(1))
print("per-episode err (fixed):", dict(zip([r["episode"] for r in rows], e.round(0))))
p = make(best.x, False)
json.dump({"camera": {k: float(v) for k, v in p.__dict__.items()}, "method": "grasp reprojection, height/tilt from plane-v2, f=615",
           "median_px": float(np.median(e)), "episodes": [r["episode"] for r in rows]}, open(S + "/top_camera_grasp.json", "w"), indent=2)
