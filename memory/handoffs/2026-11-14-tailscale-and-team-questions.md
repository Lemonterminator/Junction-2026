# 2026-11-14 — Tailscale remote operation plan and open questions for the team

- Author: linan
- Branch and commit: `docs/tailscale-remote-operation` (this PR)
- Scope: remote-access plan for the workstation, kickoff answers, questions the team has to answer

## Changes

- [Tailscale remote operation plan](../../docs/infrastructure/TAILSCALE_REMOTE_OPERATION.md): proposal only.
  Teleoperation stays on the workstation; the tailnet carries Studio (7860), SSH, the alignment/live pages and
  the Studio → 5090 trainer link. Nothing in it has been applied.
- [DECISIONS](../DECISIONS.md): records the kickoff answers below.
- [Execution plan](../../docs/plans/PHYSICAL_AI_EXECUTION_PLAN.md): §1.1 and W0.1 note the answers and that the
  evidence table still follows the old (PDF) split.

## Kickoff answers (relayed by linan from the organizers, not independently verified)

| Question | Answer |
| --- | --- |
| Which scoring table is final? | The GitHub one (`JUNCTION2026.md`): Task Success Rate 25, Intel Tech Integration 25, Dataset & Pipeline Quality 20, System Efficiency 20, Creativity 10. Not the PDF table. |
| Does a 5090 as remote trainer count? | Yes. |
| What is a defect? | A cross drawn with a marker pen on a Lego brick. |

If you heard something different, say so in the PR; do not silently edit the table.

## Evidence

- From an operator laptop on the tailnet (2026-11-14, Helsinki is its nearest DERP region): `tailscale ping` to
  `100.76.18.70` went through DERP for the first packets and then direct (8 ms); netcheck reports UDP, IPv4 and
  IPv6 working. TCP 22 and 7860 are reachable, 443 is not (no `tailscale serve` yet). One point-in-time test.
- The tailnet shows two devices only; there is no 5090 node.
- The Studio compose in the submodule (`application/docker/docker-compose.yaml`) publishes `7860:7860` with
  `HOST=0.0.0.0`, so Studio is reachable on every interface and has no login. Read from the file; the running
  container was not inspected.
- No SSH login, no Studio action and no arm motion happened. No tailnet setting was changed.

## Open questions — please answer (edit the Answer column in a PR, or tell linan)

Agents: read this table before starting related work, and do not guess the answers.

| # | Ask | Who | Why it matters | Answer |
| --- | --- | --- | --- | --- |
| Q1 | Who owns W1 (contracts, object tracking, action state machine, outcome records — plan §5 W1)? Is anyone already writing it? | Whoever works in `src/defect_sorter` | Two people editing the same modules. linan can start the first failing test (single-object state machine) once nobody else has. | |
| Q2 | Is the first `Sorting cell` episode recorded? Are the camera and bowl positions frozen? Have leader/follower wrist neutrals been compared? | Hardware / field lead | Critical path (plan §3.1). The last record says none of these is done. | |
| Q3 | Before recording: change the follower power supply or add a slew limit? The teleop dropouts are unexplained (leading guess: supply dip on the first large move, no slew limit in the driver). | Hardware / field lead | A dropout during a recording wastes the episode and may trip servo protection. linan has no access to change it. | |
| Q4 | Are the ArUco markers printed and stuck on? Has the alignment page seen a real marker yet? | Whoever owns markers | Real-marker detection is unverified (PR #4). | |
| Q5 | Who administers the tailnet? Real emails for `group:operators` (may drive Studio) and `group:devs` (SSH only). | Tailnet admin | The ACL draft still has placeholders. Studio has no login, so the operators list decides who can move the arm. | |
| Q6 | What is the 5090: Windows + WSL2 or native Linux? Who owns it? Can it join the tailnet as `junction-5090`? | 5090 owner | The Studio trainer registration and the tiny training run (W0.3) are blocked until it is reachable. | |
| Q7 | When is there a window with no recording in which the on-site lead can recreate the Studio container so 7860 binds to `127.0.0.1` (then `tailscale serve`)? | Field lead | Today anyone on the venue Wi-Fi can open Studio and move the arm. Docker published ports bypass UFW, so enabling UFW alone does not fix it. | |
| Q8 | Defect details: pen colour and thickness, which face carries the cross (top, so the D415/top camera sees it?), size, and which brick colours/shapes are used. How many marked and unmarked bricks do we have? | Perception owner + field lead | Anomalib has to find a small hand-drawn mark; resolution and lighting decide whether 640×480 crops are enough, and the normal/defect split must be by physical brick. | |
| Q9 | Remaining kickoff items: bowl/sorting rules, allowed evaluation scenes, what the Robotics AI Suite has to show, submission contents and deadline. | Whoever talks to the organizers | Plan W0.1 still lists them as assumptions. | |

## Next steps

- Merge this PR, then the admin applies the ACL after Preview (plan §3), keeping a monitor and keyboard at the
  workstation in case of lock-out.
- linan: first failing test for the single-object state machine, once Q1 is answered.
- Re-run `tailscale ping` and `netcheck` from the venue network before relying on direct connections.

Never include credentials, private chat transcripts, or model/dataset contents.
