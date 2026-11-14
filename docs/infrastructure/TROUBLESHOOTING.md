# Troubleshooting

- Tailscale ping fails: confirm both devices are connected to the correct tailnet, check invitation and tailnet policy with its administrator, and check network restrictions. The observed direct path is point-in-time only.
- SSH connection refused: server may not be listening on that address/port; an administrator should inspect `ss -tlnp` and service status. Port 22 refused during preflight.
- SSH authentication fails: verify username, installed public key, permissions (`~/.ssh` 700, `authorized_keys` 600), and chosen identity. Never send private keys or passwords to teammates.
- Fingerprint mismatch: stop and independently verify with the administrator before accepting a new key.
- VS Code fails: first verify terminal SSH, remote disk space, and supported server dependencies; inspect Remote - SSH logs. No VS Code client test has occurred.
- Camera busy: coordinate with its owner; never kill unknown processes. Port busy: choose a unique local and remote port, and inspect your own processes.
- tmux session missing: use the same Unix account and `tmux ls`; tmux cannot survive a reboot unless separately restored.

## Studio, arms and cameras on the workstation

- Re-plugged camera or arm not seen by Studio: Docker only exposes devices present when the container started.
  Restart Studio: `cd ~/junction/external/physical-ai-studio/application/docker && docker compose -p docker restart`.
- Device numbers (`/dev/ttyACM*`, `/dev/video*`) change after re-plugging. Identify arms by serial
  (`ls -l /dev/serial/by-id/`) and re-select or re-sync cameras in Studio.
- Teleoperation stops about 1 s after enabling with "Sync read failed with comm result -6": put the leader in the
  follower's pose before enabling, check the follower's power connector and adapter, then check its voltage and
  motor protection registers (see the 2026-11-14 hardware handoff).
- Camera fails with "Failed to allocate required memory" or a Studio camera worker fails: USB 2 bandwidth is
  exhausted. Spread cameras across separate laptop ports; put the D415 on a USB 3 port and cable.
- Wrist looks rotated in the setup wizard's 3D preview: the wizard draws normalized values as degrees, so the wrist
  roll shows only part of the real rotation. Compare in the regular robot viewer instead.
- Scripts cannot open an arm's serial port: a Studio browser tab on an environment or robot page holds the arms and
  reconnects after restarts. Close the tab first. After Studio disconnects, the follower keeps holding position (torque on).
