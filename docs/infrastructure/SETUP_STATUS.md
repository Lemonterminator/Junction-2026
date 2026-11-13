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
