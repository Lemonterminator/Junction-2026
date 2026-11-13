# Suunto / Movesense Challenge & Track Winners — Junction 2018

- **Event / Year**: Junction 2018 (Aalto University, Espoo, November 23–25, 2018)
- **Track & Partner**: **Movesense by Suunto** (*"Track Anything That Moves"*), spanning HealthTech, IoT, and Future Cities / StreetReboot2 cross-challenge tracks
- **Silver Challenge Spec**: [2018_Movesense_By_Suunto_Track_Anything_That_Moves.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Movesense_By_Suunto_Track_Anything_That_Moves.md)
- **Verification Tier**: **L1 + L2** (Official Movesense post-event announcements, official Movesense presentation PDF, Helsinki Stara municipal award decision `HEL 2019-003563`, HAMK pilot documentation, developer portfolio `vill.dev`, University of Latvia news)
- **Challenge Scale**: **18 teams** picked up Movesense hardware kits by Friday opening, rising to **35 teams** by Saturday, resulting in **26 submitted projects** (`movesense.com`).
- **Primary URLs**:
  - Official Movesense 2018 Recap (Nov 28, 2018): https://www.movesense.com/news/2018/11/movesense-shined-in-junction-hackathon/
  - Movesense Progress Report PDF (Jan 3, 2019): https://www.movesense.com/wp-content/uploads/2019/01/Movesense_Progress2018_PR_final_Jan3_2019.pdf
  - TerrainSense Junction Pitch PDF: https://www.movesense.com/wp-content/uploads/2018/12/TerrainSense_Junction_presentation.pdf
  - Developer Project Archive (`Ville Saramaa`): https://vill.dev/projects/
  - Helsinki Stara Municipal Decision (`HEL 2019-003563`): https://paatokset.hel.fi/fi/asia/hel-2019-003563
  - HAMK Cycling Infrastructure Pilot Report: https://unlimited.hamk.fi/teknologia-ja-liikenne/pyoravaylien-kunnon-tutkiminen-sensoriteknologian-keinoin/

---

## Verified Winners & Track Champions (Junction 2018)

### 1. Smart Labour Assistant — Movesense Challenge 1st Prize (Single-Challenge Winner)
- **Award**: **1st Prize — Movesense Challenge**
- **Team Members**: **Brian Irvine**, **Ahnaf Ahmad** (University of Oulu)
- **Problem & Solution**: Expectant mothers in labor often struggle to maintain rhythmic, calming breathing under intense stress. **Smart Labour Assistant** attaches a **Movesense** motion/breathing sensor to track chest/respiratory excursions in real time and streams telemetry into a **Unity 3D AR** experience where a virtual bird follows a ball rising on inhale and descending on exhale, providing visual biofeedback for breathing-based pain management.

### 2. TerrainSense — Movesense 1st Prize (Best Multi-Challenge Combination) & Stara StreetReboot2 2nd Place (€1,000)
- **Award(s)**:
  - **1st Prize — Movesense** (Best combination with other hackathon challenges)
  - **2nd Place (€1,000 prize)** — City of Helsinki Construction Services (**Stara**) **StreetReboot2** challenge *(where 1st Place €2,000 went to **Make Meclu Great Again** per official Helsinki record `HEL 2019-003563`)*
- **Identified Team Member**: **Ville Saramaa** (`vill.dev`)
- **Problem & Solution**: Municipalities need continuous, low-cost pavement-roughness monitoring on urban bicycle paths rather than rare manual inspections. **TerrainSense** mounts a **Movesense** IMU accelerometer directly on a bicycle's rear axle/wheel frame (`taka-akseli`), pairs it via Bluetooth to an Android smartphone mounted on the handlebar (for clean GPS lock), and uploads vibration + GPS tracks to **AWS S3 / EC2** to render interactive surface-quality web heatmaps and export **GPX** routes.
- **Post-Hackathon Commercialization**: Expanded beyond Junction into **three pilot projects** with the **City of Helsinki**, **Forum Virium Helsinki**, **HAMK** (Häme University of Applied Sciences), and **InnoTrafik**, adding an **AWS Rekognition** computer-vision video pipeline for automated pothole and crack detection through **January 2023**.

### 3. Take the Guessing Out of Coaching — Movesense 3rd Highlight
- **Award**: **3rd Highlight — Movesense Challenge**
- **Problem & Solution**: Basketball coaches lack automated statistics distinguishing ball handling events like passes and catches without expensive multi-camera gyms. Wearing a **Movesense** sensor on the wrist, the team collected a labeled dataset of **1,000 basketball passes** directly during the hackathon weekend and trained a **neural network** classifier achieving **96.5% accuracy** classifying passes and catches.

### 4. Team GaitSense — Health Tech Track Overall Winner
- **Award**: **Health Tech Track Overall Winner** (incorporating Movesense hardware)
- **Problem & Solution**: Analyzed live **Movesense** gait kinematics using an **AI classifier** to categorize human gait styles automatically for sports performance analysis and rehabilitation workflows.

### 5. Team Health.io / Help.io — IoT Track Overall Winner & 2nd Place Overall
- **Award**: **IoT Track Overall Winner**, **Intel Bluetooth Mesh 1st Prize**, and **2nd Place Overall (Main Competition)**
- **Integration**: Used **Suunto Movesense** BLE heart-rate & R-R interval chest sensors feeding an iOS triage engine bridged to an Intel NUC Bluetooth Mesh disaster-response network. See dedicated dossier: [2018_Intel_HelpIO_HealthIO_BluetoothMesh.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2018_Intel_HelpIO_HealthIO_BluetoothMesh.md).

---

## Architecture & Hardware Patterns Observed Across Winners

| Project | Sensor Placement | Edge / Compute Platform | Output / Pipeline |
|---|---|---|---|
| **Smart Labour Assistant** | Chest / respiratory motion | Movesense BLE -> Mobile / AR | **Unity 3D AR** biofeedback bird animation |
| **TerrainSense** | Bicycle rear axle (`taka-akseli`) | Movesense BLE -> Android + GPS | **AWS S3 / EC2**, web heatmap, GPX export, later **AWS Rekognition** |
| **Take the Guessing Out...** | Athlete wrist | Movesense IMU -> Neural Network | Pass/catch classifier (**96.5%** on **1,000** collected passes) |
| **Team GaitSense** | Gait / body sensor | Movesense IMU -> AI Classifier | Automated clinical/sports gait style categorization |
| **Help.io / Health.io** | Patient HR + RR chest strap | Movesense BLE -> iOS 12 -> Intel NUC | **BlueZ Mesh** responder `reel_board` e-ink badge alerts |

---

## Metrics & Baseline

- **Challenge Funnel**: `18` Friday kits -> `35` Saturday kits -> `26` final submitted projects (`movesense.com`).
- **Observed Hackathon Dataset & Accuracy**: **1,000** hand-collected basketball passes yielding **96.5%** neural-network classification accuracy (*Take the guessing out of coaching*).
- **City Prize Verification (`HEL 2019-003563`)**: Stara StreetReboot2 awarded **€2,000** (1st: *Make Meclu Great Again*) and **€1,000** (2nd: *TerrainSense*).

---

## Transferable Lessons for Wearable & Edge-ML Hardware Teams

1. **Collect Small, Clean Task-Specific Datasets On-Site**: Collecting 1,000 clean basketball pass samples during the hackathon yielded a convincing `96.5%` neural-network demo where generic public datasets do not exist.
2. **Place the Sensor Where Signal-to-Noise Peaks**: Mounting Movesense directly on the **bicycle rear axle** while keeping the phone on the **handlebar** (`TerrainSense`) cleanly separated road-vibration physics from GPS reception.
3. **Cross-Challenge Stacking Multiplies Impact**: Pairing a physical sensor kit (**Movesense**) with an infrastructure or mesh challenge (**Stara StreetReboot2**, **Intel Bluetooth Mesh**) consistently unlocked both track victories and overall finalist podiums.

---

## Sources & Raw Excerpts

- **L1 Official Partner Report — Movesense (Nov 28, 2018)**: https://www.movesense.com/news/2018/11/movesense-shined-in-junction-hackathon/
- **L1 Presentation Deck — TerrainSense**: https://www.movesense.com/wp-content/uploads/2018/12/TerrainSense_Junction_presentation.pdf
- **L1 Municipal Award Record — Helsinki Stara (`HEL 2019-003563`)**: https://paatokset.hel.fi/fi/asia/hel-2019-003563
- **L2 Portfolio & Pilot Reports**: https://vill.dev/projects/ & https://unlimited.hamk.fi/teknologia-ja-liikenne/pyoravaylien-kunnon-tutkiminen-sensoriteknologian-keinoin/
