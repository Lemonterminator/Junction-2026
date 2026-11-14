# Project context

Updated: 2026-11-13 (Europe/Helsinki).

## Goal and sources

Build the Intel Junction 2026 Physical AI Challenge prototype: inspect objects,
detect defects with Anomalib, select an action, and physically sort with SO-101;
optimize supported inference on Intel Core Ultra hardware.

- [PDF transcript](../docs/2026/silver/intel_physical_ai_hackathon.md) and original PDF:
  archived event brief, including its six-category rubric.
- [Upstream event guide](../external/physical-ai-studio/JUNCTION2026.md): operational
  guide on the `junction2026` branch, including a different five-category rubric.
- [Source manifest](../docs/2026/bronze/intel_open_edge_platform/manifest.json): pinned
  source revisions and hashes; organizational repo inventory is a dated snapshot.
- [Challenge analysis](../docs/2026/gold/zh/intel_physical_ai_challenge.md).
- [Repository opportunities](../docs/2026/gold/zh/intel_physical_ai_creativity_options.md).

The user supplied the organizer message: "Check out the interesting repos here;
Feel free to use any of them for an extra bit of creativity" and the Open Edge
Platform organization link. This is attributed user-provided context, not an
independently retrieved official rule or a requirement to use additional repos.

## Known constraints

- The upstream Studio backend requires Python >=3.13,<3.14; the older workstation
  audit lists system Python 3.14.4. Containers isolate the required interpreter.
- Studio handles configuration, demonstrations, policy training, export, and running
  models. Anomalib detection and its connection to action selection remain our work.
- The GitHub guide states $100 Modal training credit per participant, redeemed as
  organizers instruct. Redemption and personal credentials have not been verified.
- CPU/GPU UI support and OpenVINO export do not imply every model runs on NPU.
- Exact objects, defects, sorting rules, and final judging rubric require organizer
  confirmation. Preserve conflicting sources; do not choose by file date alone.

## Workstation: historical audit, not a live check

[Audit](../docs/infrastructure/SYSTEM_AUDIT.md): Ubuntu 26.04.1, Core Ultra X9 388H,
Arc B390, Panther Lake NPU, about 61 GiB RAM; render/NPU device nodes were present.
Camera capture, GPU/NPU inference, and arm operation were not established. Read
[access guidance](../docs/infrastructure/HARDWARE_ACCESS.md) before device use.
Current work is on the user's Windows checkout, not that Ubuntu host.

## Current direction

Baseline: camera -> Anomalib -> action selection -> trained policy -> SO-101 ->
observe the result. Proposed extension: one/few-shot object segmentation using
Instant Learn; it does not by itself generalize the robot's grasping policy.
Measure success rate, inference latency, sorting-cycle time, and hardware resource
use before making efficiency claims. No robot integration has been implemented yet.

## Event rules (Participant Guidebook)

Source: [Participant Guidebook PDF](../docs/2026/silver/Junction_2026_Participant_Guidebook.pdf),
24 pages, provided by the user on 2026-11-14.

- Final submission: Sunday 15 November 10:00, strict; set the project from DRAFT to FINAL.
  Required: name, punchline, description, challenge, technologies, a public pitch video of at most
  2 minutes, demo and source code links, pitch deck PDF, team phone numbers and Discord usernames.
- Peer review: Sunday 10:30–14:00 at the venue; teams absent from it are not eligible for the main
  prize. Top 5 pitch for 3 minutes plus 3 minutes of questions. Challenge winners are chosen by partners.
- Source code must be accessible to organizers; submissions are MIT-licensed; code outside open-source
  libraries must be written at the event. This repository is private as of 2026-11-14, so access or
  visibility must be settled before the deadline.
- Intel workshop: Saturday 14 November 12:00–12:30, Hardware Lab, 5th floor. Team size 1–4.

Live hardware status is in [STATUS.md](STATUS.md); the audit above is historical.
