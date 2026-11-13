# Team connection guide — pending server setup

The host is `intel-hp-omnibook-ultra-laptop-14t-kd000.taild8fece.ts.net`, Tailscale IPv4 `100.76.18.70`. Developer accounts dev1–dev4 exist. SSH on port 22 is listening on the Tailscale IPv4 and has been tested with the administrator account. Developer public keys and laptop connections are still pending. UFW is inactive; tailnet policies must permit access.

1. On macOS, Windows or Linux install Tailscale from https://tailscale.com/download if needed; sign in to the correct tailnet or accept the owner's invitation. A tailnet administrator must ensure policy grants access. Test `tailscale ping 100.76.18.70` in Terminal, PowerShell, or a Linux terminal.
2. Generate an individual key with `ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_junction` (PowerShell supports this syntax). Set a passphrase. Existing suitable keys may be reused. Send the administrator only the contents of `~/.ssh/id_ed25519_junction.pub`, labeled with your desired account; never share the private key. Windows users can run `Get-Content $HOME\.ssh\id_ed25519_junction.pub` in PowerShell; macOS/Linux can run `cat ~/.ssh/id_ed25519_junction.pub`.
3. After the administrator confirms your account and SSH port, edit `~/.ssh/config` (Windows: `%USERPROFILE%\.ssh\config`):

```sshconfig
Host junction-intel
    HostName 100.76.18.70
    User dev1
    IdentityFile ~/.ssh/id_ed25519_junction
    IdentitiesOnly yes
    ServerAliveInterval 30
    Port 22
```

Replace username, address, key path and port as appropriate. Verify the server host-key fingerprint independently with the administrator via a trusted channel before accepting the first connection. Run `ssh junction-intel`.
4. Install VS Code from https://code.visualstudio.com/ and Microsoft's Remote - SSH extension. Use “Remote-SSH: Connect to Host”, choose `junction-intel`, then open `/home/dev1/junction` using your own username once the repository exists. This requires an actual client test.
5. In the remote terminal run `hostname; uname -m; python3 -c 'import platform; print(platform.node(), platform.machine())'` to confirm execution is on the remote host. Once installed, run `cd ~/junction; tmux new -s development; claude`. Authenticate with your own Claude account following its prompts. Detach with Ctrl+B then D; reconnect with `tmux attach -t development`, or list sessions using `tmux ls`.
6. For an application bound to remote loopback on port 8000, run locally `ssh -L 8000:127.0.0.1:8000 junction-intel` and open http://127.0.0.1:8000. VS Code's Ports panel also forwards ports. Pick different ports for concurrent developers. Do not expose debug servers publicly.

Manual prerequisites: before connecting, obtain tailnet permission, create your own key, supply its public half, and verify the host fingerprint. For Claude, sign in individually on the remote machine; do not share tokens. For GitHub, configure your own Git identity and authenticate with an approved individual SSH key or credential method. Optional: use SSH agent and VS Code port forwarding. None of these steps has been completed for teammates.
