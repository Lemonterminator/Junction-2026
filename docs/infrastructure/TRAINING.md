# Local policy training on RTX 5090

Updated: 2026-11-14. This is an executable preparation path for the pinned Studio
revision `17714488fa9c7d098a056da83f7c220cf983957d`. The default project environment
does not import PyTorch or download weights. Real data and CUDA execution are not
validated by the offline test suite.

For the challenge delivery, prefer the [execution plan](../plans/PHYSICAL_AI_EXECUTION_PLAN.md)
section 4.4: register the 5090 host as a Studio remote trainer so dataset snapshots,
jobs, logs and returned model artifacts remain traceable in Studio. Upstream supports
local and remote trainers; this host's registration and training are not validated.
The CLI below invokes the same pinned training library, but does not automatically
create a Studio UI job or register its output model. Keep it for environment checks
and controlled experiments; do not present CLI completion as verified UI integration.

The [Gold challenge analysis](../2026/gold/en/intel_physical_ai_challenge.md) and
[execution recommendations](../2026/gold/en/intel_physical_ai_creativity_options.md)
prioritize a physical closed loop: camera -> Anomalib -> decision -> policy ->
SO-101 -> observe the outcome. These recipes train alternative policies for that
loop. They do not integrate Anomalib decisions into instructions or execute an arm.
The PDF and GitHub judging rubrics remain different; these are engineering choices,
not additional contest requirements.

## Available lines

| Recipe | Purpose | Initial settings | Status |
| --- | --- | --- | --- |
| `configs/training/act_baseline.toml` | ACT imitation-learning baseline; not a language-conditioned VLA and not pretrained robot-policy fine-tuning | batch 8, fp32, 10k steps | Plan/schema tests only |
| `configs/training/smolvla_expert.toml` | Fine-tune `lerobot/smolvla_base`, freeze vision/VLM and train action expert/state projection | batch 4, gradient accumulation 2, bf16 mixed, 10k steps | Recommended first VLA experiment; no measured fit/time/quality yet |
| `configs/training/pi05_lora.toml` | Fine-tune `lerobot/pi05_base` using LoRA rank 16 with fp32 adapters | batch 1, accumulation 8, bf16 mixed, gradient checkpointing, compile disabled | Experimental; no guarantee it fits 32GB or exports successfully |

Pi0.5 LoRA cannot combine with `train_expert_only=true` or
`freeze_vision_encoder=true` in this revision. The recipe keeps both false;
adapter injection performs the base-parameter freezing. Its base optimizer rate is
not pre-scaled: upstream applies `lora_lr_scale=10` during optimizer construction.
ACT's image backbone can still download pretrained ImageNet weights when training.

All budgets are starting configurations, not claims about required training time
or convergence. Run a short experiment before the full budget, inspect held-out
loss, then evaluate task success on hardware through the team's separate process.

## 1. Prepare the recording contract

The input is a **local LeRobot v3.0 recording**, exported/copied with all its files.
Studio's pinned import tools also require v3.0. v2 layouts are rejected rather than
silently interpreted as v3. Do not record and train against the same changing folder.

Copy `configs/training/dataset.example.toml` into `.local/dataset.toml` and edit it.
The root path is relative to that TOML file: after copying, use
`root = "../data/sorting"` for this checkout's `data/sorting` directory, rather
than retaining the example's `../../data/sorting`. Declare:

- The exact camera feature keys present in `meta/info.json`, in intended policy
  order. The example uses `top` then `wrist`; add `front` only if recorded and wanted.
- The exact ordered joint names for **both** `observation.state` and `action`.
- One unit convention per joint: `degrees`, `radians`, `normalized_-100_100`, or
  `normalized_0_100`. This is an operator declaration, not a value inferred from
  dimension or proven by LeRobot metadata. SO-101 body joints can use degrees or
  normalized values; the gripper often uses 0..100. Verify the recorder/runtime
  settings before using the example's degree declaration.
- The actual recording fps and a dataset repo ID used by LeRobot with the local root.

Do not change joint units/order or camera mounting between demonstrations and
deployment without recalibration and an explicit dataset/model migration.

The light metadata check verifies version, fps, joint dimensions/order, matching
camera keys and image/video features. Missing data is allowed only while planning.
`run` additionally requires nonempty data Parquet shards, `meta/tasks.parquet`,
`meta/stats.json`, episode shards, and each declared video camera's MP4 payload.
These presence checks do not prove full recording integrity or valid numerical
state/action values.

Before loading policy weights, a separate preflight in the CUDA environment reads
the actual task Parquet table with pandas/pyarrow and streams frame `task_index`
columns. It rejects empty instructions, noncontiguous task metadata indices and
missing/out-of-range frame references. The policy's real dataloader still owns full
payload decoding, normalization statistics, video synchronization and training-data
compatibility. Labels must describe the demonstrated task; the code cannot verify
their meaning from text alone.

## 2. Inspect plans without data

Run at the repository root; this works in the light Python 3.12 environment:

```bash
uv sync --locked
uv run python -m defect_sorter.training plan \
  --recipe configs/training/smolvla_expert.toml \
  --dataset configs/training/dataset.example.toml --run-name smolvla-first
```

Replace the recipe with `act_baseline.toml` or `pi05_lora.toml` for the other lines.
PowerShell users can put the command on one line. If uv is outside PATH, invoke
its executable by full path and pass `--uv` with the same full path for child jobs.

The JSON contains the real CLI argument vector, generated training configuration,
camera layout, dataset status, and a `metrics: null` field. No files, GPU work or
model weights are created by planning. When metadata exists, it also reports the
same seeded episode split used by upstream. Whole episodes, rather than random
frames from the same trajectory, are held out. This does not guarantee separation
by recording session or object instance; split those deliberately for evaluation.

## 3. Prepare the independent CUDA environment

Use Linux or WSL2 for the CUDA environment. Keep the checkout and recording on the
Linux filesystem for that run, generate the plan there, and use Linux paths;
a Windows-generated plan is not a portable WSL launch script.

The root perception/test package stays on Python 3.12. Studio backend requires
Python 3.13 and selects a CUDA 12.8 PyTorch build through its own `cuda` extra:

```bash
git submodule update --init --recursive
uv sync --project external/physical-ai-studio/application/backend --extra cuda --frozen
uv run --project external/physical-ai-studio/application/backend --extra cuda --frozen python -c "import torch; assert torch.cuda.is_available(); print(torch.__version__, torch.cuda.get_device_name(0))"
```

The CUDA environment and optional model dependencies are substantial downloads.
Do not install them into the root `.venv` or mix them with the root's CPU Anomalib
environment. Check current GPU usage and leave enough VRAM for the chosen run.
Configure required Hugging Face access in the training environment using your own
account; credentials must not go in recipes, dataset contracts or Git. Gated model
access and network downloads can still fail even after metadata checks pass.

## 4. Run after real data arrives

Copy the recipe under `.local/` for a short experiment and set `max_steps` to a small
positive number. Check the printed plan, then replace `plan` with `run`:

```bash
uv run python -m defect_sorter.training run \
  --recipe .local/smolvla-smoke.toml \
  --dataset .local/dataset.toml --run-name smolvla-smoke-01
```

`run` first executes the real task-data preflight in the backend environment. On
success it creates a new run directory and calls:

```text
uv run --project <pinned-backend> --extra cuda --frozen physicalai fit --config <run>/config.json
```

Outputs stay under ignored `artifacts/training/<run-name>/`: plan/config, Lightning
CSV logs and checkpoints. Existing run directories are never replaced. A failed
training run remains available for diagnosis; choose a new run name for a retry.
`last.ckpt` is the continuation artifact; `best.ckpt` depends on completing a
validation pass. A run shorter than one training epoch may not produce held-out
metrics or a best checkpoint. Full optimizer resume is not wired into this wrapper.

Model export is deliberately separate so a successful training checkpoint survives
an unsupported export backend or device. After selecting and validating a checkpoint:

```bash
uv run --project external/physical-ai-studio/application/backend --extra cuda --frozen physicalai export \
  --policy physicalai.policies.SmolVLA --ckpt_path <checkpoint.ckpt> \
  --backend openvino --output_dir artifacts/exports/smolvla
```

Change policy class to `ACT` or `Pi05` as appropriate. Export support does not prove
CPU/GPU/NPU compilation, latency, numerical parity or physical task success. Run
those checks on the Intel deployment host with the selected model and preserve its
joint/camera/instruction contract. This wrapper never connects to a camera or arm.

## Verification scope and sources

`tests/test_training.py` uses synthetic metadata and task arrays to cover three
plans, missing/invalid data, disjoint seeded splits, exact joint/camera schema,
nonfinite learning rates, output traversal/non-overwrite, CLI JSON, task language
validation and generated kwargs against pinned upstream constructor signatures.
It also executes the upstream **pure camera-slot layout method** in isolation,
catching the distinction between LeRobot `observation.images.top` and SmolVLA's
`images.top`: the generated policy remap uses the camera suffix `top`.

These tests do not import models, execute gradients, decode a complete recorded
dataset, run the heavy parser, benchmark a GPU, or export a policy. Real CUDA
installation, a first fit/export and measured VRAM remain required validation.

A separate Windows synthetic-Parquet smoke was attempted in an isolated temporary
environment with pandas/pyarrow. It stalled while importing a pandas extension and
was stopped; a bounded diagnostic retry exited after 30 seconds in the same import.
No task table was decoded and this check did not pass. The cause was not established;
this does not change the offline test results above or establish Linux/WSL readiness.

Source contracts: [training CLI parser](../../external/physical-ai-studio/library/src/physicalai/cli/_dispatch.py),
[LeRobot datamodule](../../external/physical-ai-studio/library/src/physicalai/data/lerobot/datamodule.py),
[SmolVLA policy](../../external/physical-ai-studio/library/src/physicalai/policies/smolvla/policy.py),
[Pi0.5 LoRA example](../../external/physical-ai-studio/library/configs/physicalai/pi05/aloha/lora.yaml),
[v3 import checks](../../external/physical-ai-studio/application/backend/src/cli/hf/inspection.py),
[task metadata semantics](../../external/physical-ai-studio/application/backend/src/internal_datasets/lerobot/episode_task.py).

## Experiment tracking with MLflow

Finished runs are logged to a local MLflow server on the training PC
(`defect_sorter.tracking`, `tracking` extra). The trainer's environment needs no
MLflow: the logger reads the run directory afterwards (`plan.json`, Lightning's
`metrics.csv`, and `best.ckpt` or else `last.ckpt`). Every run carries a `source`
tag (`twin` or `real`) and a `kind` tag (`training` or `evaluation`).

```bash
uv run --extra tracking mlflow server --host 127.0.0.1 --port 5000 \
  --backend-store-uri sqlite:///artifacts/mlflow/mlflow.db --artifacts-destination artifacts/mlflow/artifacts
uv run --extra tracking python -m defect_sorter.tracking training artifacts/training/<run>
uv run --extra tracking python -m defect_sorter.tracking evaluation artifacts/twin/<eval>
```

On Windows set `PYTHONUTF8=1`; MLflow prints an emoji when a run finishes and a
cp1252 console crashes on it. The server listens on loopback only. Teammates can
reach it with `ssh -L 5000:127.0.0.1:5000`, or over `tailscale serve` once Serve
is enabled for the tailnet (see [MODEL_RELEASES.md](MODEL_RELEASES.md#training-curves-mlflow)). Store and artifacts live in the Git-ignored
`artifacts/mlflow/`. Each checkpoint is about 1.7 GB, so use `--no-artifacts` for
runs whose weights are not worth keeping.
