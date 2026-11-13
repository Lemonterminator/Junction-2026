# Suunto / Movesense Challenge Winners — Junction 2017

- **Event / Year**: Junction 2017 (Dipoli, Aalto University, Espoo, November 24–26, 2017)
- **Track & Partner**: Health Technology / IoT — **Suunto / Movesense** (*"Track anything that moves!"*)
- **Silver Challenge Spec**: [2017_Suunto_Track_Anything_That_Moves.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2017_Suunto_Track_Anything_That_Moves.md)
- **Verification Tier**: **L1 + L2** (Official Movesense post-event report, Devpost project records, University of Latvia Faculty of Computing news)
- **Challenge Scale & Prizes**:
  - **24 projects** submitted using Movesense sensors at Junction 2017
  - Prizes awarded across three Movesense categories (**Health**, **Sports**, **General IoT**): **Suunto Spartan** sports watches + permanent Movesense developer sensor kits (e.g., team **DF LAB** received **6 Movesense sensors** + **4 Suunto Spartan watches**)
- **Primary URLs**:
  - Official Movesense 2017 Recap: https://www.movesense.com/news/2017/11/24-movesense-projects-at-junction-hackathon/
  - University of Latvia News (`DF LAB` / `ReCover`): https://eztf.lu.lv/par-mums/zinas/zina/t/29783/
  - Devpost — `ReCover`: https://devpost.com/software/recover-pfrq3g
  - Devpost — `Ne'e`: https://devpost.com/software/ne-e
  - Devpost — `Superman Navigation`: https://devpost.com/software/superman-navigation
  - Devpost — Notable Non-Winning Submission (`Spin Coach`): https://devpost.com/software/spin-coach

---

## Verified Winning Projects (Junction 2017)

### 1. ReCover (`DF LAB`) — Movesense Health Challenge Winner
- **Award**: **Movesense Health Challenge Winner** (received 6 Movesense sensors + 4 Suunto Spartan watches)
- **Team & Members**: **DF LAB** (University of Latvia Faculty of Computing) — **Austris Cīrulnieks**, **Elvijs Viļķels**, **Dāvis Mednis**, **Mārcis Nīmants** *(clinical rehabilitation concept initiated by **Emīls Sjundjukovs**, PhD researcher/mentor)*
- **Problem & Solution**: Post-operative knee rehabilitation patients struggle to gauge whether they are reaching prescribed joint flexion angles during unsupervised home exercises. **ReCover** mounts **two Movesense IMU sensors** above and below the knee joint and pairs them via BLE with an **iOS app** that calculates real-time knee flexion angles and renders live animated physiotherapy exercise guidance.
- **Significance**: Several core members (**Cīrulnieks, Nīmants, Viļķels, Mednis**) returned to Junction 2018 and combined Movesense sensors with Intel's Bluetooth Mesh hardware to win Intel 1st Prize, IoT Track 1st Prize, and **2nd Place Overall** as **Help.io / Health.io**.

### 2. Ne'e — Movesense Sports Award & Overall Health Track Winner
- **Award**: **Movesense Sports Award** + **Overall Health Track Winner** (selected as top project among **~40 Health track teams**)
- **Problem & Solution**: Team sports coaches lack an objective real-time measure of cumulative player fatigue across a full roster during matches or practice. **Ne'e** built a real-time multi-player coaching dashboard combining **Movesense** motion output and heart-rate data into a composite fatigue metric dubbed the **`"ne'e factor"`**.

### 3. Superman Navigation — Movesense General IoT Award Winner
- **Award**: **Movesense General IoT Award**
- **Problem & Solution**: Checking visual maps on a screen distracts pedestrians, cyclists, and visually impaired users while navigating. **Superman Navigation** reads continuous heading orientation from a **Movesense magnetometer / magnetic sensor**, compares body orientation against a target destination bearing, and modulates **smartphone haptic vibration frequency/intensity** — vibrating faster and stronger as the user points closer to the correct heading.

---

## Notable Verified Devpost Submission (Cross-Partner Sensor + ML)

- **Spin Coach** (https://devpost.com/software/spin-coach): Paired **Movesense / Suunto** sensor data with **Futurice** tooling and **TensorFlow** to analyze disc-golf throw acceleration kinematics.

---

## Hardware / Sensor Platform Overview (Movesense @ Junction 2017)

| Aspect | Observed Technical Spec |
|---|---|
| **Sensor Module** | Open-programmable **Suunto Movesense** BLE wearable sensor (IMU: accelerometer, gyro, magnetometer + ECG / heart rate) |
| **Dual-Sensor Kinematic Mode** | `ReCover` paired **two** synchronized Movesense sensors over BLE to compute differential joint angle across the knee |
| **Multi-User Broadcast Mode** | `Ne'e` aggregated concurrent athlete HR + motion streams onto a coach dashboard |
| **Magnetometer Haptic Mode** | `Superman Navigation` transformed magnetic heading delta into real-time smartphone vibration feedback |

---

## Transferable Lessons for Wearable & Embedded Teams

1. **Multi-Sensor Differential Kinematics Over Single-Node Guesswork**: Using two Movesense pods (`ReCover`) resolves relative joint angles robustly without requiring a fixed external camera or calibrated floor frame.
2. **Eyes-Free Output Channels Stand Out**: Converting sensor orientation deltas directly into **haptic pulse modulation** (`Superman Navigation`) creates an intuitive non-visual UX well suited for hardware demos.
3. **Domain-Grounded Composites Beat Raw Plots**: Naming and calibrating a single interpretable score like `Ne'e`'s `"ne'e factor"` or `ReCover`'s target flexion angle lets non-technical judges evaluate clinical/athletic value in seconds.

---

## Sources & Raw Excerpts

- **L1 Official Partner Report — Movesense**: https://www.movesense.com/news/2017/11/24-movesense-projects-at-junction-hackathon/
  - Confirms **24 Movesense projects**, awards across Health (**ReCover**), Sports (**Ne'e** — also overall Health Track Winner out of ~40 Health projects), and General IoT (**Superman Navigation**).
- **L2 University Release — Univ. of Latvia (`DF LAB`)**: https://eztf.lu.lv/par-mums/zinas/zina/t/29783/
  - Confirms team members (**Austris Cīrulnieks, Elvijs Viļķels, Dāvis Mednis, Mārcis Nīmants**, concept by **Emīls Sjundjukovs**) and hardware/watch prizes (6 Movesense sensors + 4 Suunto Spartan watches).
- **L1 Devpost Links**: `recover-pfrq3g`, `ne-e`, `superman-navigation`, `spin-coach`.
