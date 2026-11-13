# Signvision — Team Glados (Junction 2017 Overall Grand Winner & STARA 2nd Prize)

- **Event / Year**: Junction 2017 (Dipoli, Aalto University, Espoo, November 24–26, 2017; 1,500 participants from 80+ countries selected from 4,000 applicants across 13 tracks; Junction CEO Ville Leppälä)
- **Track & Challenge**: Main Competition Winner & **STARA** Urban Infrastructure Challenge (*Note: Signvision won the Overall Main Competition after competing in the STARA challenge; listed alongside 2017 Hardware/Embedded winners as Team Glados's computer-vision/mobile-edge predecessor to Oneiro*)
- **Silver Hardware Context**: [Hardware/README.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/README.md)
- **Verification Tier**: **L1 + L2** (GitHub repository + Devpost submission + Uusi Teknologia article)
- **Award(s)**:
  - **1st Prize — Junction 2017 Main Competition (Overall Grand Winner, €20,000)**
  - **2nd Prize — STARA Challenge** @ Junction 2017 *(and later **2nd Prize** @ Reboot Hacks x Slush 2017)*
- **Team Name & Members**: **Team Glados** — **Andreas Urbanski**, **Teemu Taskula** (`teemu.taskula@aalto.fi`), **Ville Toiviainen** (`Villux`)
- **Primary URLs**:
  - GitHub Repository: https://github.com/teamglados/signvision
  - Devpost Submission: https://devpost.com/software/glados
  - Demo Video: https://vimeo.com/244507554
  - Uusi Teknologia News (Nov 28, 2017): https://www.uusiteknologia.fi/2017/11/28/junction2017-voittaja-yhdisti-big-datan-mobiiliin/

---

## Problem & Solution Summary

Municipal road maintenance agencies (such as Helsinki's **Stara**) need up-to-date visibility into missing, damaged, or obstructed traffic signs without dispatching dedicated survey fleets on every street.

**Signvision** crowdsources automated traffic sign detection from smartphones mounted in everyday vehicles:
1. A React Native mobile app continuously streams live camera frames + GPS coordinates (`lat`, `lng`) over a low-latency WebSocket connection.
2. On the backend, an **OpenCV** color-segmentation & connected-component pipeline isolates candidate red traffic-sign ROIs from raw frames.
3. Candidate crops are classified by a custom **TensorFlow** convolutional neural network trained on the German Traffic Sign Recognition Benchmark (GTSRB) Stop sign class (`00014`), logging verified GPS detections while rate-limiting duplicates so municipal maintenance teams can map sign inventory in real time.

---

## Hardware / Sensors / Edge / ML Stack

| Layer | Observed Component / Technology | Exact Details from `teamglados/signvision` |
|---|---|---|
| **Mobile Edge Sensor** | Smartphone Camera + GPS (React Native client) | Captures live video frames paired with `lat` / `lng` telemetry and transmits to WebSocket backend (`MARK_SEND` -> `MARK_RECEIVE`) |
| **Realtime Ingestion** | Node.js **`uWs`** WebSocket + **`Koa`** HTTP server | `server/server.js` WebSocket on port `3000` with `5000 ms` deduplication cooldown; Koa API on port `8000` |
| **CV Preprocessing** | **OpenCV** + **`scikit-image`** (`skimage.measure.label`) | HSV red-mask segmentation -> morphological erode/dilate -> connected-component ROI extraction (`numPixels > 1000`, `30%` bounding-box padding) |
| **Classification Model** | **TensorFlow `1.4.0`** CNN (`cnn_model/app.py`, **Flask** port `8080`) | `32x32x3` input -> `Conv2D(16, 3x3, stride=2, ELU)` -> `Conv2D(32, 3x3, stride=2, ELU)` -> `Flatten` -> `Dense(2)` trained on GTSRB Stop sign class `00014` (2,000 / 18,000 steps) |
| **Deployment / Infra** | **CUDA 8.0 Docker + AWS ECS Terraform** | `aws/*.tf` Terraform configuration deploying GPU-ready containers on AWS ECS |

---

## Architecture

```text
[Smartphone (React Native: Camera + GPS)]
   │ Live frame + {lat, lng} via WebSocket
   ▼
[Node.js uWs (:3000) + Koa (:8000) Server]
   │ 5000ms spatial/temporal cooldown -> forward frame
   ▼
[Python Flask ML Microservice (cnn_model/app.py :8080)]
   ├─► 1. OpenCV HSV red mask + erode/dilate + skimage.measure.label (>1000 px ROI + 30% pad)
   └─► 2. TensorFlow 1.4.0 CNN (32x32x3 -> Conv16 -> Conv32 -> Dense(2), GTSRB Stop class 00014)
   │ Classification event {lat, lng, sign}
   ▼
[Crowdsourced Municipal Traffic-Sign Map / Dashboard]
```

---

## Key Engineering Decisions & Observed Quirks

1. **Two-Stage Classical CV Proposal + Tiny CNN**: Rather than running slow sliding-window or heavy object-detection networks across entire HD camera frames during a 48-hour hackathon, the team used fast HSV red thresholding + connected-component filtering (`numPixels > 1000`) to generate cropped proposals for a compact `32x32` CNN.
2. **Real-Time Transport Split**: Decoupled raw WebSocket frame ingestion (`uWs` on port `3000`) from REST endpoints (`Koa` on port `8000`) and Python ML inference (`Flask` on port `8080`).
3. **Observed Hackathon Hardcoding (`app.py`)**: Inspection of `cnn_model/app.py` shows `'probability': 0.0` was hardcoded in the JSON return payload alongside the classification result — a classic hackathon shortcut focused on getting end-to-end live detection working cleanly for the demo.

---

## Metrics & Baseline

- **Event Scale**: 1,500 attendees (80+ countries, selected from 4,000 applicants) across 13 tracks (`uusiteknologia.fi`).
- **Model Training & Inference Specs**: Input shape `32x32x3`; ROI pixel floor `numPixels > 1000` with `30%` padding; deduplication cooldown `5000 ms`; GTSRB Stop sign class `00014` trained for `2000` / `18000` steps.
- **Prize**: **€20,000** Main Competition 1st Prize (Junction 2017 Overall Winner) + **2nd Prize** STARA Challenge.

---

## Demo Highlights

- Demonstrated live camera stream -> real-time cloud CV/ML detection -> mapped sign alerts in the Vimeo submission video (`https://vimeo.com/244507554`).
- Positioned specifically around real-world urban maintenance utility for Helsinki's **Stara** infrastructure fleet.

---

## Transferable Lessons for Edge & Vision Teams

1. **ROI Proposal Filtering Cuts Inference Latency**: Classical HSV/morphological region proposals feeding a tiny `32x32` classifier remain an effective low-compute architecture for mobile/edge dashcam pipelines when targets have strong color/shape priors.
2. **Deduplicate Streams Early**: Adding a `5000 ms` server cooldown stops stationary vehicles from spamming duplicate map markers against municipal databases.
3. **Reusable Full-Stack Muscle**: Team Glados carried their React Native + Python/Docker + Terraform AWS pipeline directly from Junction 2017 (*Signvision*) to win Junction 2018 (*Oneiro*) back-to-back.

---

## Sources & Raw Excerpts

- **L1 GitHub Repo**: https://github.com/teamglados/signvision (`server/server.js`, `cnn_model/app.py`, `aws/*.tf`, React Native client)
- **L1 Devpost**: https://devpost.com/software/glados
- **L2 Finnish Tech Press — Uusi Teknologia (Nov 28, 2017)**: https://www.uusiteknologia.fi/2017/11/28/junction2017-voittaja-yhdisti-big-datan-mobiiliin/
  - Documents Junction 2017's 1,500 participants from 80+ countries (out of 4,000 applicants), 13 tracks, Junction CEO Ville Leppälä, and Team Glados's €20,000 win with *Signvision*.
