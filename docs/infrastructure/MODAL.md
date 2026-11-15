# Training on Modal

Modal is the overflow GPU when the RTX 5090 on the training PC is busy, and the
planned place for SmolVLA pretraining on synthetic LeRobot v3 data. The entry
point `scripts/modal/train.py` runs the same `defect_sorter.training` plan as a
local run, in an image built from the pinned Studio submodule with
`uv sync --frozen --extra cuda`, so torch, `physicalai` and the trainer config
match the 5090. Only the paths move onto a Modal Volume.

Upstream Studio also ships a Modal trainer (`external/physical-ai-studio/application/modal`)
that Studio's UI deploys and drives through its batch job contract with the
`physicalai-trainer-cuda:main` image. Ours exists because we train from the CLI
with our own recipes and dataset contracts, and want the pinned lock, not
upstream `main`.

## Setup

The Modal CLI authenticates with `modal token set` (or `MODAL_TOKEN_ID` /
`MODAL_TOKEN_SECRET`), which stores the token in `~/.modal.toml`. Never put the
token in the repository, recipes, MLflow or logs. Install the CLI outside the
project environment (`pip install --user modal` or `uvx modal`); the project
does not depend on it.

The workspace needs a payment method and a spend limit above zero. With a zero
limit every function call fails with `workspace has exceeded its spend limit`,
even at $0 spent. Set the limit in the Modal dashboard under workspace settings;
it is the hard budget cap for everything below.

Check that a GPU can be allocated (a few seconds of T4 time):

```bash
modal run scripts/modal/gpu_check.py --gpu T4
```

## Prices

From `modal billing rates` on 2026-11-15, USD per hour; CPU ($0.047/core/h) and
memory ($0.008/GiB/h) are billed on top, the Volume at $0.09/GiB/month.

| GPU | VRAM | $/h |
| --- | --- | --- |
| T4 | 16 GB | 0.59 |
| L4 | 24 GB | 0.80 |
| A10G | 24 GB | 1.10 |
| L40S | 48 GB | 1.95 |
| A100 | 40 / 80 GB | 2.10 / 2.50 |
| H100 | 80 GB | 3.95 |

`L40S` is the default: enough memory for the SmolVLA expert recipe without
measuring VRAM first. No Modal run has been measured yet, so steps per hour and
the cost of a 10k-step run are unknown; run a short smoke recipe first.

## Train

The Volume `junction-training` holds `datasets/<name>` (uploaded recordings),
`runs/<run-name>` (one directory per run, never overwritten) and `hf-cache/`
(downloaded base weights, reused across runs).

1. Local dry run. Validates recipe and dataset contract, prints the upload and
   download commands and the GPU cost ceiling. Calls nothing remote.

   ```bash
   python scripts/modal/train.py --recipe configs/training/smolvla_sort_depth_v2.toml --dataset configs/training/dataset.sort_depth_v2.toml --dataset-name sort-depth-v2 --run-name modal-smoke-01 --gpu L40S --max-hours 1
   ```

2. Upload the recording once (the `upload` line printed above):

   ```bash
   modal volume put junction-training data/studio/af9b173a-ee59-4e24-97c8-be71dba701ce /datasets/sort-depth-v2
   ```

3. Remote plan. Builds the image (first time only, several minutes of CPU) and
   builds the plan inside the container against the uploaded recording. No GPU.

   ```bash
   modal run scripts/modal/train.py --recipe configs/training/smolvla_sort_depth_v2.toml --dataset configs/training/dataset.sort_depth_v2.toml --dataset-name sort-depth-v2 --run-name modal-smoke-01
   ```

4. Train. `--max-hours` becomes the call timeout, so the GPU charge is at most
   rate × hours; the dry run prints that ceiling. Use a short recipe copy under
   `.local/` (small `max_steps`) before a full run.

   ```bash
   modal run scripts/modal/train.py --recipe .local/smolvla-smoke.toml --dataset configs/training/dataset.sort_depth_v2.toml --dataset-name sort-depth-v2 --run-name modal-smoke-01 --gpu L40S --max-hours 1 --go
   ```

   The local `modal run` stays attached and streams the trainer log. Add
   `--detach` after `modal run` to keep the call running if the terminal closes.
   The container commits the run directory to the Volume every 10 minutes, so
   `metrics/` and `last.ckpt` can be fetched while it runs.

   The simulated batch dataset uses the same steps with
   `--recipe configs/training/smolvla_sim_batch_v1.toml --dataset configs/training/dataset.sim_batch_v1.toml --dataset-name sim-batch-v1`.

   Warm start. A SmolVLA recipe may name `warm_start = "<name>"`: the run then
   loads the weights of an earlier run instead of `lerobot/smolvla_base`
   (normalisation statistics still come from the new training data). Convert the
   earlier checkpoint once in the Studio backend environment and upload it; the
   dry run prints the upload line and the remote run refuses to start without it:

   ```bash
   uv run --project external/physical-ai-studio/application/backend --extra cuda --frozen python scripts/training/ckpt_to_warm_start.py artifacts/training/sort-depth-v2-10k/checkpoints/best.ckpt artifacts/warm-start/sort-depth-v2-10k
   ```

   ```bash
   modal volume put junction-training artifacts/warm-start/sort-depth-v2-10k /warm-start/sort-depth-v2-10k
   ```

   Local runs read the same directory from `artifacts/warm-start/` (`--warm-start-root`).

   Several GPUs. `devices = N` in a recipe runs Lightning DDP on N GPUs of one
   container (`--gpu L40S` with `devices = 8` asks Modal for `L40S:8`; at most 8
   per container), `num_workers` sets data loader processes per GPU, and the cost
   ceiling counts all N GPUs. The effective batch grows N times: shorten
   `max_steps` and scale the learning rate with it. Every run writes
   `checkpoints/periodic.ckpt` every 500 steps as a restart point between epochs.

5. Download and log to MLflow:

   ```bash
   modal volume get junction-training /runs/modal-smoke-01 artifacts/training
   uv run --extra tracking python -m defect_sorter.tracking training artifacts/training/modal-smoke-01
   ```

   `plan.json` inside the run keeps the container paths (`/vol/...`); the
   logger reads parameters and metrics from it, not paths. Export and release
   then follow [MODEL_RELEASES.md](MODEL_RELEASES.md).

## MLflow from Modal

The MLflow server runs on the training PC and is reachable only inside the
tailnet; Modal containers are not in it. Logging after download (step 5) is the
supported path: it needs no credential in the cloud, reuses
`defect_sorter.tracking` unchanged and gives the same records as local runs.
The cost is that curves appear only after a download; for a running job,
download `runs/<run>/metrics` and log it again under a new MLflow run, or read
the CSV directly.

Live logging would need the container to join the tailnet: an ephemeral,
pre-approved, tagged Tailscale auth key stored as a Modal Secret, `tailscaled`
in userspace networking mode inside the image, and a tailnet ACL that lets that
tag reach only the MLflow port on the training PC. That puts a tailnet
credential in the cloud and adds an MLflow client to the trainer environment,
so it is not set up.

## Limits

- One GPU per call, no automatic retry, no resume across calls; a timeout stops
  training and keeps the last committed `last.ckpt` and metrics.
- Uploading a recording copies it to Modal's storage. Recordings with people in
  frame need the team's agreement before upload.
- The image is built from the local submodule checkout; after bumping the
  submodule the next `modal run` rebuilds it.
- Neither a remote plan nor a GPU run has been executed yet: the workspace spend
  limit blocked the first GPU check.
