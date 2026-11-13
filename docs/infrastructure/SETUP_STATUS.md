# Setup status

## Local project integration — 13 November 2026

The Windows checkout now includes the pinned Physical AI Studio submodule, shared
AI memory, and CPU/Intel/robot Compose configurations. Compose configuration parsing
was checked; images have not been built or started. Docker Desktop's Linux engine
is unavailable and `wsl --status` reports WSL is not installed. Nothing was deployed
to the Ubuntu workstation. Current evidence: [shared status](../../memory/STATUS.md).

## Ubuntu workstation — historical 13 November 2026 audit

- **Working:** Tailscale connection from one Mac; key-based administrator SSH to port 22; verified host fingerprint; four isolated Unix home directories and accounts without sudo; Git, Python venv with pip, and a tmux session as intel.
- **Configured, not reboot-tested:** `junction-ssh.service`, bound to 100.76.18.70:22 and enabled at boot. Default SSH service/socket were runtime masked during installation. A temporary listener on 2222 also exists until reboot or explicitly stopped.
- **Pending:** each developer's public key and actual SSH/VS Code connection, individual GitHub and Claude authentication, independent repository clones, Claude Code installation, and integration checkout.
- **Untested:** camera capture, GPU/NPU inference, multi-user tmux isolation, four simultaneous clients, and restart behavior. No shared camera service has been built.
- **Manual:** each developer joins the authorized tailnet, supplies a labeled public SSH key, verifies the host fingerprint, and authenticates their own GitHub and Claude accounts. Never share private keys or passwords.

## Update 13 November 2026 (evening)

- **Physical AI Studio:** running in Docker (`~/Downloads/physical-ai-studio-main/application/docker`, profile `xpu`, privileged) at http://100.76.18.70:7860. Devices are only visible to the container if plugged in before it starts; after re-plugging arms or cameras run `docker compose restart` in that directory.
- **Studio project** "Defect Sorting (Intel Challenge)" with cameras `wrist` (USB2.0_CAM1), `front` (Webcam Audio), `top` (RealSense D415 serial 243722064948, colour), all 640×480@30. Arms not yet added: serials `5AAF262737` (ttyACM0) and `5AE7045026` (ttyACM1), leader/follower unassigned, uncalibrated.
- **Host Intel runtimes:** apt `intel-opencl-icd libze1 libze-intel-gpu1 clinfo`; NPU user-space `intel-level-zero-npu` + `intel-driver-compiler-npu` v1.38.0 (ubuntu2604 debs in `~/installers/npu-1.38.0`). `intel-fw-npu` deliberately not installed (kernel firmware left as shipped).
- **intel account:** groups docker, video, render added. Access and admin workarounds are kept in the untracked `.local/` folder.
- **Anomalib env:** `~/workspace/.venv-anomalib` (uv, Python 3.12): anomalib[openvino] 2.7.0, OpenVINO 2026.4.1, torch 2.15 CPU, NNCF, pyrealsense2, opencv-headless. Smoke test `~/workspace/smoke_anomalib.py` (Padim, synthetic data) trains, exports to OpenVINO, and runs on all devices.
- **Measured (Padim resnet18, static 1×3×256×256, LATENCY hint):** CPU 5.0 ms, GPU 1.5 ms, NPU 8.5 ms per inference. NPU requires a static input shape (`model.reshape(...)`); the dynamic export fails to compile on NPU.
