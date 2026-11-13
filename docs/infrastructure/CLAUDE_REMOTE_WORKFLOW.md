# Remote Claude workflow

tmux 3.6 is installed and a session was created and checked as intel; Claude Code is not yet installed. After installation and individual authentication: `ssh junction-intel`, `cd ~/junction`, `tmux new -s claude`, then `claude`. Commands executed in this terminal run on Ubuntu. Ctrl+B then D detaches; `tmux ls` and `tmux attach -t claude` reconnect. Separate Unix users own separate tmux sockets and home directories. Each developer uses their own checkout, account, credentials and session. No shared personal account or tokens in Git.

Claude Code worktree, subagent and tmux features depend on the installed version and have not been checked. Use separate checkout directories now; enable no experimental features without checking the installed version and team needs. Consult https://code.claude.com/docs/ for current official installation and login instructions; do not run a remote installer without reviewing it and obtaining required authorization.
