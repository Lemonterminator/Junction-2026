"""Evaluate trained policies in the MuJoCo sorting cell on Modal GPUs, one container per episode.

The image is the training image (pinned Studio backend environment with CUDA torch and ``physicalai``) plus MuJoCo
and EGL. Checkpoints are read from the ``junction-training`` Volume (``runs/<run>/checkpoints/<file>``), the Menagerie
model from the ``so101-sim`` Volume (``batch_v1/menagerie``). Results land in ``junction-training`` under
``evals/<name>/`` and are printed as a summary per policy::

	modal run scripts/sim/modal_policy_eval.py --name sim-eval-01 \
		--policies smolvla-sim-ddp8-01=runs/smolvla-sim-ddp8-01/checkpoints/best.ckpt,sort-depth-v2-10k=runs/sort-depth-v2-10k/checkpoints/best.ckpt \
		--episodes 40 --seed 2026

Every policy sees the same scenes (same ``--seed`` and episode indices). The batch dataset was simulated with seed 0,
so any other seed gives held-out scenes. Results are tagged ``source = mujoco-sim``.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import modal

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] if modal.is_local() else Path("/repo")
STUDIO = ROOT / "external" / "physical-ai-studio"
REMOTE = "/repo"
BACKEND = f"{REMOTE}/external/physical-ai-studio/application/backend"
_SOURCE_IGNORE = [".venv", "**/__pycache__", "tests", "docs", "notebooks", "benchmarks", "**/*.pyc"]

app = modal.App("junction-sim-policy-eval")
training = modal.Volume.from_name("junction-training")
simvol = modal.Volume.from_name("so101-sim")
image = (
	modal.Image.debian_slim(python_version="3.13")
	.apt_install(
		"ffmpeg", "git", "libgl1", "libglib2.0-0", "libegl1", "libgl1-mesa-dri", "libegl-mesa0", "libglvnd0", "libgles2"
	)
	.pip_install("uv==0.13.8")
	.env({"UV_LINK_MODE": "copy"})
	.add_local_dir(
		STUDIO / "library", f"{REMOTE}/external/physical-ai-studio/library", copy=True, ignore=_SOURCE_IGNORE
	)
	.add_local_dir(STUDIO / "application" / "backend", BACKEND, copy=True, ignore=_SOURCE_IGNORE)
	.run_commands(f"uv sync --project {BACKEND} --extra cuda --frozen --no-install-project")
	# MuJoCo and the sim's helpers go into the same environment as the policy; numpy stays the backend's.
	.run_commands(
		f"uv pip install --python {BACKEND}/.venv/bin/python mujoco==4.0.1 scipy opencv-contrib-python-headless"
	)
	.env(
		{
			"UV_NO_SYNC": "1",
			"HF_HOME": "/vol/hf-cache",
			"MUJOCO_GL": "egl",
			"NVIDIA_DRIVER_CAPABILITIES": "all",
			"PYTHONUNBUFFERED": "1",
		}
	)
	.add_local_dir(ROOT / "src", f"{REMOTE}/src", ignore=["**/__pycache__"])
	.add_local_file(HERE / "so101_sort_sim.py", f"{REMOTE}/scripts/sim/so101_sort_sim.py")
	.add_local_file(HERE / "policy_eval.py", f"{REMOTE}/scripts/sim/policy_eval.py")
	.add_local_dir(ROOT / "config" / "sim", f"{REMOTE}/config/sim")
)


@app.function(
	image=image,
	gpu="L4",
	cpu=4,
	memory=16384,
	volumes={"/vol": training, "/sim": simvol},
	timeout=3600,
	max_containers=40,
)
def evaluate_episode(job: dict) -> dict:
	"""Run one (policy, episode) rollout; the policy loads once per container."""
	import shutil
	import subprocess

	# The backend environment holds torch, physicalai and mujoco; run there and return its JSON line.
	menagerie = Path("/tmp/menagerie")  # noqa: S108  (container-local copy)
	if not menagerie.exists():
		shutil.copytree("/sim/batch_v1/menagerie", menagerie)
	code = (
		"import json,sys,logging;"
		f"sys.path[:0]=['{REMOTE}/scripts/sim','{REMOTE}/src'];"
		"logging.basicConfig(level=logging.WARNING);"
		"import policy_eval as pe, so101_sort_sim as sim;"
		"from pathlib import Path;"
		"j=json.loads(sys.argv[1]);"
		"nominal=sim.CameraPose(**json.loads(Path(j['camera']).read_text())['camera']);"
		"prior=[p for p in json.loads(Path(j['prior']).read_text()) if 'green' in p and 'pink' in p];"
		"pol=pe.SmolVlaPolicy(Path('/vol')/j['checkpoint']);"
		"r=pe.run_episode(pol,Path('/tmp/menagerie'),nominal,prior,j['seed'],j['episode'],j['max_frames']);"
		"print('RESULT '+json.dumps(r))"
	)
	proc = subprocess.run(  # noqa: S603
		[f"{BACKEND}/.venv/bin/python", "-c", code, json.dumps(job)], capture_output=True, text=True, check=False
	)
	line = next((ln for ln in proc.stdout.splitlines() if ln.startswith("RESULT ")), None)
	if line is None:
		raise RuntimeError(f"episode {job['episode']} of {job['label']} failed:\n{proc.stderr[-3000:]}")
	return {**json.loads(line.removeprefix("RESULT ")), "label": job["label"]}


@app.local_entrypoint()
def main(name: str, policies: str, episodes: int = 40, seed: int = 2026, max_frames: int = 1200) -> None:
	"""``--policies label=volume/path.ckpt,label2=...``: every policy runs the same ``--episodes`` scenes."""
	sys.path[:0] = [str(HERE)]
	import eval_summary

	pairs = dict(item.split("=", 1) for item in policies.split(","))
	jobs = [
		{
			"label": label,
			"checkpoint": ckpt,
			"episode": e,
			"seed": seed,
			"max_frames": max_frames,
			"camera": f"{REMOTE}/config/sim/top_camera_joint.json",
			"prior": f"{REMOTE}/config/sim/prior_grasp.json",
		}
		for label, ckpt in pairs.items()
		for e in range(episodes)
	]
	t0 = time.perf_counter()
	results: dict[str, list[dict]] = {label: [] for label in pairs}
	for r in evaluate_episode.map(jobs, return_exceptions=True):
		if isinstance(r, Exception):
			sys.stdout.write(f"failed: {str(r)[:500]}\n")
			continue
		results[r["label"]].append(r)
		sys.stdout.write(f"{r['label']} ep {r['episode']}: {r['outcome']} ({r['frames']} frames, {r['seconds']} s)\n")
	out = Path("artifacts/evals") / name
	summaries = [eval_summary.write_results(out, label, rs) for label, rs in results.items()]
	sys.stdout.write(json.dumps(summaries, indent=2) + f"\n{time.perf_counter() - t0:.0f} s; written to {out}\n")
