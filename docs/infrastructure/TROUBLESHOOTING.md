# Troubleshooting

- Tailscale ping fails: confirm both devices are connected to the correct tailnet, check invitation and tailnet policy with its administrator, and check network restrictions. The observed direct path is point-in-time only.
- SSH connection refused: server may not be listening on that address/port; an administrator should inspect `ss -tlnp` and service status. Port 22 refused during preflight.
- SSH authentication fails: verify username, installed public key, permissions (`~/.ssh` 700, `authorized_keys` 600), and chosen identity. Never send private keys or passwords to teammates.
- Fingerprint mismatch: stop and independently verify with the administrator before accepting a new key.
- VS Code fails: first verify terminal SSH, remote disk space, and supported server dependencies; inspect Remote - SSH logs. No VS Code client test has occurred.
- Camera busy: coordinate with its owner; never kill unknown processes. Port busy: choose a unique local and remote port, and inspect your own processes.
- tmux session missing: use the same Unix account and `tmux ls`; tmux cannot survive a reboot unless separately restored.
