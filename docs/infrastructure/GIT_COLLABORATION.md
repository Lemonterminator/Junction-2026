# Git collaboration

Intended remote: `git@github.com:Lemonterminator/Junction-2026.git`. The repository has an existing main branch. Ubuntu developer accounts still need their own GitHub access.

Each developer configures their own `git config --global user.name 'Name'` and `git config --global user.email 'email'`, then authenticates individually to GitHub. Once access is granted, clone into their own `~/junction`: `git clone git@github.com:Lemonterminator/Junction-2026.git ~/junction`. If the remote is empty, coordinate initialization and default branch before pushing.

Fetch with `git fetch origin`, create a feature branch from the agreed up-to-date base with `git switch -c feature/my-task origin/main` (substitute the actual default branch), commit with `git add ...` and `git commit`, and push your own branch with `git push -u origin feature/my-task` after confirming the remote. Open a GitHub pull request; review, resolve conflicts in the feature branch, run tests, and merge under the team's agreed policy. Git worktrees can isolate parallel branches for one user, but separate accounts and clones remain the team boundary.

A separate integration checkout and its owner have not been established. Agree on an owner and deployment procedure; never edit or restart the live demo without coordination.
