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
| `candidate` | Trained on real recordings, under evaluation. |
| `demo` | Frozen for the judged run. |

Releases other than `demo` are published as GitHub pre-releases.

## Current releases

| Tag | Status | Contents |
| --- | --- | --- |
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
