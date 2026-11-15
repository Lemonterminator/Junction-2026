"""Top camera pose from grasp correspondences: brick pixel (first vs last frame height drop) <-> jaw centre by FK."""
import sys, json, math, numpy as np, cv2, av, pyarrow.parquet as pq
sys.path.insert(0, "/mnt/c/Users/Jiang/.gemini/antigravity/scratch/hackjunction/scripts/sim")
import so101_sort_sim as sim
from pathlib import Path
DS = Path(sys.argv[1]); S = sys.argv[2]
ep = pq.read_table(DS / "meta/episodes/chunk-000/file-000.parquet").to_pydict()
starts, ends = list(ep["dataset_from_index"]), list(ep["dataset_to_index"])
tab = pq.read_table(DS / "data/chunk-000/file-000.parquet", columns=["observation.state", "index"]).to_pydict()
state = np.asarray(tab["observation.state"], float)
def height(dep):
    r, g, b = [dep[..., i].astype(float) for i in range(3)]
    h = np.where(g < 0.035 / sim.COARSE_MAX_M * 255, r / 255 * sim.FINE_MAX_M, g / 255 * sim.COARSE_MAX_M)
    return np.where(b > 128, h, np.nan)
want = {}
for e, (s, t) in enumerate(zip(starts, ends)):
    want[s + 3] = (e, "first"); want[t - 3] = (e, "last")
frames = {}
with av.open(str(DS / "videos/observation.images.top_depth_v2/chunk-000/file-000.mp4")) as c:
    for i, f in enumerate(c.decode(video=0)):
        if i in want: frames[want[i]] = f.to_ndarray(format="rgb24")
        if i > max(want): break
layout = sim.Layout(green=(0.0, 1.0), pink=(0.0, -1.0), brick_xy=(2.0, 2.0), brick_yaw_deg=0.0, defective=False)
layout.top = sim.look_from((0.2, 0.0), 0.25, sim.PLANE_HEIGHT_M, 0.0)
cell = sim.Cell(layout, Path("/home/linan/sim/mujoco_menagerie/robotstudio_so101"))
jaw = cell.model.body("moving_jaw_so101_v1").id
obj, img, rows = [], [], []
for e, (s, t) in enumerate(zip(starts, ends)):
    g = state[s:t, 5]
    zs, cs = [], []
    for k in range(t - s):
        cell.set_joints(sim.normalized_to_rad(state[s + k]))
        tip = cell.data.site_xpos[cell.site]; mj = cell.data.xipos[jaw]
        cs.append(0.5 * (tip + mj)); zs.append(cs[-1][2])
    zs = np.array(zs)
    # grasp: the gripper's closing that ends most closed while low; take the lowest jaw point before the
    # gripper reaches its tightest value in the first 70 % of the episode
    half = int(0.55 * len(g)); c = int(np.argmin(zs[:half])); kopen = c; kmin = c
    centre = cs[c]
    h0, h1 = height(frames[(e, "first")]), height(frames[(e, "last")])
    drop = np.nan_to_num(h0 - h1) > 0.008
    drop &= np.nan_to_num(h0) < 0.06
    drop = cv2.morphologyEx(drop.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(drop)
    if n < 2: print(e, "no drop blob"); continue
    i = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); a = st[i, cv2.CC_STAT_AREA]
    ys, xs = np.nonzero(lab == i); top = float(np.nanmedian(h0[ys, xs]))
    u, v = cen[i][0] + sim.TOP_CROP[0], cen[i][1] + sim.TOP_CROP[1]
    rows.append({"episode": e, "grasp_frame": c, "abs_frame": s + c, "px": [float(u), float(v)], "area": int(a), "brick_top": top,
                 "jaw_centre": centre.tolist()})
    obj.append([centre[0], centre[1], top]); img.append([u, v])
    print(e, f"open={kopen} close={kmin} g=({g[kopen]:.0f},{g[kmin]:.0f}) c={c} px=({u:.0f},{v:.0f}) area={a} top={top*100:.1f}cm jaw=({centre[0]:.3f},{centre[1]:.3f},{centre[2]:.3f})")
obj = np.array(obj); img = np.array(img)
gw = {r["abs_frame"]: r for r in rows}
with av.open(str(DS / "videos/observation.images.top_depth_v2/chunk-000/file-000.mp4")) as cc:
    for i, f in enumerate(cc.decode(video=0)):
        if i in gw:
            r = gw[i]; hg = height(f.to_ndarray(format="rgb24"))
            u, v = int(r["px"][0] - sim.TOP_CROP[0]), int(r["px"][1])
            win = hg[max(0, v - 20):v + 20, max(0, u - 20):u + 20]
            r["arm_over_brick_m"] = float(np.nanmax(win)) if np.isfinite(win).any() else 0.0
        if i > max(gw): break
for r in rows: print(r["episode"], "arm height over brick px", round(r["arm_over_brick_m"], 3))
json.dump(rows, open(S + "/grasp_points.json", "w"), indent=1)
np.savez(S + "/grasp_points.npz", obj=obj, img=img)
