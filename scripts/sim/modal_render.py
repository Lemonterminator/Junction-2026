"""Render simulated episodes on Modal: one container per (episode, view), many in parallel.

Same output as ``so101_sort_sim.py render`` (same seeds give the same cameras), written to the Modal volume
``so101-sim`` under ``<run>/render``. Inputs are staged locally first:

* ``--sim-dir``: the ``simulate`` output (``sim_*.json`` + ``sim_*.npz``),
* ``--menagerie-dir``: Menagerie ``robotstudio_so101`` at commit ``370c43965323c0944b433b202aac5058b5f907a9``.

Run (``--mode gpu`` renders through EGL on an NVIDIA GPU, ``--mode cpu`` through Mesa llvmpipe)::

	modal run scripts/sim/modal_render.py --sim-dir STAGE/sim --menagerie-dir STAGE/menagerie --run batch_v1 \
		--camera config/sim/top_camera_joint.json --views 2 --seed 11 --mode gpu

Then fetch the results with ``modal volume get so101-sim <run>/render <local dir>``. The entrypoint writes
``index.json`` there; every episode also has its ``.json`` entry, so a rerun skips finished episodes.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import modal

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1] if len(HERE.parents) > 1 else HERE  # inside the container the file sits in /root

app = modal.App("so101-sim-render")
volume = modal.Volume.from_name("so101-sim", create_if_missing=True)

image = (
	modal.Image.debian_slim(python_version="3.12")
	.apt_install("libegl1", "libgl1", "libgl1-mesa-dri", "libegl-mesa0", "libglvnd0", "libgles2")
	.pip_install("mujoco==4.0.1", "numpy==2.5.4", "scipy==1.18.1", "opencv-python-headless")
	.env({"NVIDIA_DRIVER_CAPABILITIES": "all", "PYTHONUNBUFFERED": "1"})
	.add_local_file(HERE / "so101_sort_sim.py", "/repo/scripts/sim/so101_sort_sim.py")
	.add_local_file(REPO / "src/defect_sorter/__init__.py", "/repo/src/defect_sorter/__init__.py")
	.add_local_file(REPO / "src/defect_sorter/presentation.py", "/repo/src/defect_sorter/presentation.py")
)


def _render(job: dict, mode: str) -> dict:
	if mode == "cpu":
		os.environ.update({"MUJOCO_GL": "egl", "LIBGL_ALWAYS_SOFTWARE": "1", "GALLIUM_DRIVER": "llvmpipe"})
	else:
		os.environ["MUJOCO_GL"] = "egl"
	sys.path.insert(0, "/repo/scripts/sim")
	import shutil

	import so101_sort_sim as sim

	menagerie = Path("/tmp/menagerie")
	if not menagerie.exists():
		shutil.copytree(f"/vol/{job['run']}/menagerie", menagerie)
	out = Path(f"/vol/{job['run']}/render")
	out.mkdir(parents=True, exist_ok=True)
	nominal = sim.CameraPose(**job["camera"])
	meta = Path(f"/vol/{job['run']}/sim/{job['episode']}.json")
	t0 = time.perf_counter()
	entry = sim._render_one((menagerie, nominal, meta, out, job["view"], job["seed"], job["stride"]))
	volume.commit()
	return {"entry": entry, "seconds": time.perf_counter() - t0, "job": job}


@app.function(image=image, gpu=["L4", "A10G", "T4", "L40S"], cpu=4, memory=8192, volumes={"/vol": volume}, timeout=3600, max_containers=100)
def render_gpu(job: dict) -> dict:
	"""Render one (episode, view) through EGL on the container's GPU."""
	return _render(job, "gpu")


@app.function(image=image, cpu=8, memory=8192, volumes={"/vol": volume}, timeout=3600, max_containers=100)
def render_cpu(job: dict) -> dict:
	"""Render one (episode, view) with Mesa llvmpipe on the container's CPUs."""
	return _render(job, "cpu")


@app.local_entrypoint()
def main(
	sim_dir: str,
	menagerie_dir: str,
	run: str,
	camera: str,
	views: int = 2,
	seed: int = 11,
	stride: int = 1,
	mode: str = "gpu",
	limit: int = 0,
	upload: bool = True,
) -> None:
	sim_path = Path(sim_dir)
	if upload:
		with volume.batch_upload(force=True) as batch:
			batch.put_directory(str(sim_path), f"/{run}/sim")
			batch.put_directory(menagerie_dir, f"/{run}/menagerie")
	cam = json.loads(Path(camera).read_text())["camera"]
	metas = [p for p in sorted(sim_path.glob("sim_*.json")) if json.loads(p.read_text())["success"]]
	jobs = [
		{"run": run, "episode": p.stem, "view": k, "seed": seed, "stride": stride, "camera": cam}
		for p in metas
		for k in range(views)
	]
	if limit:
		jobs = jobs[:limit]
	fn = render_gpu if mode == "gpu" else render_cpu
	t0 = time.perf_counter()
	results = []
	for r in fn.map(jobs, return_exceptions=True):
		if isinstance(r, Exception):
			sys.stdout.write(f"failed: {r}\n")
			continue
		results.append(r)
		done = len(results)
		sys.stdout.write(f"[{done}/{len(jobs)}] {r['job']['episode']} v{r['job']['view']}: {r['seconds']:.0f} s\n")
	entries = [r["entry"] for r in results if r["entry"] is not None]
	sys.stdout.write(
		f"{len(entries)} of {len(jobs)} rendered in {time.perf_counter() - t0:.0f} s "
		f"(median {sorted(r['seconds'] for r in results)[len(results) // 2] if results else 0:.0f} s per episode)\n"
	)
	sys.path.insert(0, str(HERE))
	index = {
		"fps": 30 // stride,
		"state_names": ["shoulder_pan.pos", "shoulder_lift.pos", "elbow_flex.pos", "wrist_flex.pos", "wrist_roll.pos", "gripper.pos"],
		"cameras": {"front": [480, 640, 3], "top_rgb_v2": [416, 512, 3], "top_depth_v2": [416, 512, 3], "wrist": [480, 640, 3]},
		"source": "mujoco-sim",
		"menagerie_commit": "370c43965323c0944b433b202aac5058b5f907a9",
		"render_backend": f"modal-{mode}",
		"episodes": sorted(entries, key=lambda e: e["file"]),
		"rejected_cameras": sum(e["rejected_cameras"] for e in entries),
	}
	Path(f"modal_index_{run}.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
