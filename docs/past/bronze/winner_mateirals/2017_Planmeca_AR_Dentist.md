# AR Dentist — Planmeca "Reshaping the Future of Dentistry" Winner (Junction 2017)

- **Event / Year**: Junction 2017 (Dipoli, Aalto University, Espoo, November 24–26, 2017)
- **Track & Challenge**: **Health Technology** (Planmeca Chief Partner) — *"Reshaping the future of dentistry"*
- **Silver Challenge Spec**: [2017_Planmeca_Reshaping_Dental_Care.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2017_Planmeca_Reshaping_Dental_Care.md)
- **Verification Tier**: **L1 Verified** (Official Planmeca newsroom post-event report naming winning team, members, judges, challenge participant count, and technical architecture)
- **Award**: **1st Place — Planmeca Challenge Winner** (out of **13 competing hacker teams**; jury included **Sakari Kettunen**, Product Development Manager, and **Antti Haanpää**, Digital Business Solution Manager)
- **Team Name & Members**: **AR Dentist**
  - **Samuel Laska** (Slovakia — physics & computer science background; mobile application developer)
  - **Linda Ukkonen** (Finland — industrial design graduate specializing in 3D modeling & design; teamed up solo/paired after originally signing up with others interested in a different track)
- **Primary URL**:
  - Official Planmeca Newsroom Article (Jan 12, 2018): https://www.planmeca.com/news-and-events/newsroom/2018/planmeca-challenged-hackers-to-reshape-the-future-of-dentistry/ *(historical redirect from `/news/2018/ar-app-wins-planmecas-junction-hackathon-challenge/`)*

---

## Problem & Solution Summary

Clinical dental CBCT scans and 3D surgical/orthodontic treatment plans live on workstation software (e.g., Planmeca Romexis), making it difficult for dentists to explain spatial procedures intuitively to patients—either chairside or remotely.

**AR Dentist** built a real-time **mobile augmented-reality dental visualization app**:
1. Ingests **Planmeca 3D imaging data** (patient CBCT / dental geometry).
2. Tracks the patient's face live through a **mobile camera** and fits the 3D dental anatomy onto the patient's face in real time.
3. Streams live adjustments triggered from a companion **laptop workstation**, allowing clinicians to demonstrate treatment options and projected outcomes interactively both in-clinic and remotely.

---

## Observed Technical Stack & Pairing

| Component | Observed Details | Source Evidence |
|---|---|---|
| **Imaging Data Input** | **Planmeca 3D dental imaging datasets** | Supplied by Planmeca challenge kit (`Planmeca Romexis` / 3D imaging export) |
| **AR Frontend** | Real-time **mobile AR application** | Live facial tracking & 3D dental overlay fitting to patient face |
| **Control Workstation** | Companion **laptop control interface** | Real-time modification of 3D parameters streamed immediately to the mobile overlay |
| **Skill Pairing** | Mobile CS/Physics (`Laska`) + Industrial 3D Design (`Ukkonen`) | 2-person cross-disciplinary team built complete live AR prototype in 48 hours |

---

## Metrics & Event Context

- **Challenge Adoption**: **13 hacker teams** attempted Planmeca's Junction 2017 challenge inside the Health Technology track (1,500 total event attendees from 70+ countries at Dipoli).
- **Public Code Gap**: No public GitHub or Devpost repository link was published alongside Planmeca's official winner announcement.

---

## Transferable Lessons for Medical Imaging & AR Teams

1. **Two-Device Split (Workstation Control + Mobile AR Lens)**: Letting the clinician manipulate complex 3D CAD/CBCT parameters on a laptop while projecting simplified overlays onto a mobile screen creates an immediately understandable doctor-patient demo.
2. **Design + Mobile Engineering Dyads Punch Above Team Size**: A focused two-person team combining industrial 3D modeling with mobile engineering outperformed larger squads among 13 teams.

---

## Sources & Raw Excerpts

- **L1 Official Partner Report — Planmeca (Jan 12, 2018)**: https://www.planmeca.com/news-and-events/newsroom/2018/planmeca-challenged-hackers-to-reshape-the-future-of-dentistry/
  > *"The winning team was called AR Dentist and it consisted of Samuel Laska from Slovakia and Linda Ukkonen from Finland. Their solution was a creative mobile application which uses Planmeca’s 3D imaging data in real-time fitting it on a patient’s face according to changes made from a laptop."*
  > *"Planmeca’s challenge was the ambitious choice of 13 brave hacker teams."*
