# Model releases

Trained policies are shared as assets of **private GitHub releases** on
`Lemonterminator/Junction-2026`, never committed to Git (`models/`, `artifacts/`
and `checkpoints/` are Git-ignored). Each release carries a `release.json`
manifest written by `defect_sorter.model_release`: every file with its size and
SHA-256, the training run it came from (recipe, data source, episode counts,
steps, final losses), the code commit and a status.

| Status | Meaning |
| --- | --- |
| `smoke-test` | Proves the export and download path. Not for the arm. |
| `baseline` | First model on real recordings with known data limits (see the manifest's `inspection` block). Not validated for the arm. |
| `candidate` | Trained on real recordings, under evaluation. |
| `demo` | Frozen for the judged run. |

Releases other than `demo` are published as GitHub pre-releases.

## Current releases

| Tag | Status | Contents |
| --- | --- | --- |
| [`anomaly-patchcore-baseline-1`](https://github.com/Lemonterminator/Junction-2026/releases/tag/anomaly-patchcore-baseline-1) | `baseline` | PatchCore 10 % (wide_resnet50, fold 0 of the real baseline), OpenVINO `model.xml/.bin`, 267 MB. |
| [`anomaly-padim-baseline-1`](https://github.com/Lemonterminator/Junction-2026/releases/tag/anomaly-padim-baseline-1) | `baseline` | Padim (resnet18, fold 0 of the real baseline), OpenVINO `model.xml/.bin`, 168 MB. |
| [`model-smolvla-studio-smoke-1`](https://github.com/Lemonterminator/Junction-2026/releases/tag/model-smolvla-studio-smoke-1) | `smoke-test` | SmolVLA, 50 steps on the first Studio recording (2 episodes, green-bowl task only), OpenVINO IR (`smolvla.xml/.bin`, `tokenizer.xml/.bin`, `manifest.json`), ~0.8 GB. Train loss 0.16, held-out val loss 0.81. Runs on CPU: 50×6 action chunk in ~295 ms with synthetic input. |

## Download and verify

Any repository collaborator with `gh auth login` done can download; the release
is private, so an unauthenticated URL returns 404.

```bash
gh release download model-smolvla-studio-smoke-1 --repo Lemonterminator/Junction-2026 --dir models/model-smolvla-studio-smoke-1
uv run python -m defect_sorter.model_release verify models/model-smolvla-studio-smoke-1
```

`verify` prints `ok` and exits 0 when every file in `release.json` is present
with the right size and hash; otherwise it lists each missing or corrupt file
and exits 1. Re-run the download with `--clobber` to replace bad files.

The exported `manifest.json` (from `physicalai export`) describes the policy's
inputs and outputs; load it with the Physical AI Studio runtime in the backend
environment. The state vector uses Studio's normalised units (body joints
−100…100, gripper 0…100), not twin degrees.

## Publish a new release

From the training PC, in the Studio backend environment (on Windows the
launcher avoids the POSIX-only robot CLI; on Linux `physicalai export` works the
same way):

```bash
<studio-venv>/python scripts/offline_pipeline/physicalai_without_robot_cli.py export --policy physicalai.policies.SmolVLA --ckpt_path artifacts/training/<run>/checkpoints/best.ckpt --backend openvino --output_dir artifacts/export/<run>
uv run python -m defect_sorter.model_release manifest artifacts/export/<run> artifacts/training/<run> --status candidate --out artifacts/export/<run>/release.json
gh release create model-smolvla-<run> artifacts/export/<run>/* --repo Lemonterminator/Junction-2026 --target main --prerelease --title "SmolVLA <run> (candidate)"
```

Use `best.ckpt` when validation produced one, otherwise `last.ckpt`. Commit the
code first, so `code_commit` in the manifest points at pushed history. Assets
are limited to 2 GiB each.

## Training curves (MLflow)

Each released run is also logged to the MLflow server on the training PC (see
[TRAINING.md](TRAINING.md#experiment-tracking-with-mlflow)). The server listens on
loopback. Teammates reach it with an SSH tunnel to the training PC, or over
Tailscale Serve (tailnet-only HTTPS) once Serve is enabled for the tailnet:

```bash
tailscale serve --bg 5000
```

The server is started with `--allowed-hosts` that includes the machine's
`*.ts.net` name so MLflow accepts proxied requests.

## Anomaly baselines (PatchCore, Padim)

`anomaly-manifest` packages one fold model of `scripts/anomaly/real_baseline.py` (default fold 0) with the threshold
chosen on that fold's validation episodes, the cross-fold episode results, frame AUROC per fold and the measured
latency. It refuses a staged `model.xml`/`model.bin` that differs from the fold export. The manifest records the
**CPU** threshold only:

- Scores differ by device (the NPU scores about 16 % lower than the CPU), so calibrate the threshold on each device
  before using that device's scores.
- On Intel integrated GPUs compile with `INFERENCE_PRECISION_HINT=f32`; the default FP16 output is wrong
  (`OpenVinoScorer` sets it).
- The PatchCore export has a fixed batch of 2; `OpenVinoScorer` keeps it.
- Good-brick training data are mostly orange and from one session, so these are baselines, not final models.

```bash
uv run --extra tracking python -m defect_sorter.tracking anomaly artifacts/anomaly/real-baseline-v2 --fold 0 --uri https://monsterai.tail8cc5dd.ts.net --param backbone=resnet18
mkdir -p artifacts/release/anomaly-padim-baseline-1 && cp artifacts/anomaly/real-baseline-v2/fold0/padim/export/weights/openvino/model.* artifacts/release/anomaly-padim-baseline-1/
uv run python -m defect_sorter.model_release anomaly-manifest artifacts/release/anomaly-padim-baseline-1 artifacts/anomaly/real-baseline-v2 --fold 0 --status baseline --out artifacts/release/anomaly-padim-baseline-1/release.json
gh release create anomaly-padim-baseline-1 artifacts/release/anomaly-padim-baseline-1/* --repo Lemonterminator/Junction-2026 --target main --prerelease --title "Padim baseline 1"
```

On Windows set `PYTHONIOENCODING=utf-8` for the tracking command: MLflow prints an emoji run link that cp1252 cannot
encode, which leaves the run in status RUNNING (the files are uploaded; mark it FINISHED).

### On the Intel workstation

The two baselines were copied with SSH keys (no password) from a verified download into `~/models/anomaly/` of the
`intel` account, outside Docker. `~/models/studio-anomaly-models.override.yaml` mounts that folder read-only at
`/app/models/anomaly`; add it as one more `-f` to the four files the Studio project already uses, then
`docker compose ... up -d --force-recreate --no-deps physical-ai-studio-xpu` (the live preview drops for a moment).

### Per-device thresholds

`scripts/anomaly/calibrate_devices.py` picks a threshold per OpenVINO device on the fold's validation episodes and
judges the test episodes with it. On the workstation (OpenVINO 2026.4, fold 0, 7 test episodes):

| Model | Device | Threshold | Score vs CPU | Latency median / p90 |
| --- | --- | ---: | --- | --- |
| Padim | CPU | 0.5238 | reference | 9.1 / 10.1 ms |
| Padim | iGPU, FP32 | 0.5238 | same | 36.3 / 50.8 ms |
| Padim | NPU | 0.5238 | up to 0.23 % lower | 9.2 / 9.5 ms |
| PatchCore | CPU | 0.4030 | reference | 861 / 1006 ms |
| PatchCore | iGPU, FP32 | 0.4030 | same | 215 / 264 ms |
| PatchCore | NPU | none | graph compilation fails | none |

The earlier note that NPU scores are about 16 % lower did not reproduce with these exports and this runtime, so keep
one threshold per device anyway. The test fold is tiny, so treat the confusion counts as a smoke check, and the
latencies were taken while Studio was running.
