# Make Sauna Great Again (MaSGA) — Vaisala Challenge Winners (Junction 2018)

- **Event / Year**: Junction 2018 (Aalto University, Espoo, November 23–25, 2018)
- **Track & Challenges**: **Vaisala** Challenges:
  1. *"Hack the Sauna"* (**Smart Everyday / IoT hardware**)
  2. *"Actually Useful Weather"* (Data / Weather API)
- **Silver Challenge Specs**:
  - [2018_Vaisala_Hack_The_Sauna.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Vaisala_Hack_The_Sauna.md)
  - [2018_Vaisala_Actually_Useful_Weather.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Vaisala_Actually_Useful_Weather.md)
- **Verification Tier**: **L1 + L2** (Official Vaisala blog + Aalto University news + Winner GitHub frontend/backend repos + Aalto IECON 2020 academic paper)
- **Verified Winners & Runners-Up**:
  - **Hack the Sauna Winner (1st Prize)**: **Make Sauna Great Again (MaSGA)**
    - **Members**: **Siavash H. Khajavi** (Aalto DIEM postdoc), **Alireza Jaribion** (Aalto DIEM researcher), **Adriaan Knapen** (`Addono`, Aalto EIT), **Leila Abiedat** (St Petersburg State University), **Arnab Banik** (Clark University)
  - **Hack the Sauna Runners-Up**: **Talking Sauna** & **BMC – Blazing Measurements and Controls**
  - **Actually Useful Weather Winner (1st Prize)**: **Should I Go** (**Arturs Znotins, Siiri Talvistu, Mathias Luick, Roberts Dargis**); Runners-up: **Weather Player**, **rairAI.biz**
  - **Vaisala Jury**: **Sampsa Lahtinen**, **Ari Alanko**, **Riku Hakala**
- **Primary URLs**:
  - GitHub Frontend: https://github.com/Addono/masga
  - GitHub Backend: https://github.com/Addono/masga-backend
  - Official Vaisala Blog: https://www.vaisala.com/en/blog/2018-11/winners-vaisalas-challenges-junction-2018-hacked-weather-and-sauna
  - Official Aalto News: https://www.aalto.fi/en/news/winning-team-hack-the-sauna-experience-to-a-new-level-at-junction
  - Demo Video: https://youtu.be/rNtnsDjz0vM
  - IECON 2020 Paper Record (Aaltodoc, DOI `10.1109/IECON43393.2020.9254270`): https://aaltodoc.aalto.fi/items/44b6d03b-0849-4381-a9e4-300de579f7d3

---

## Problem & Solution Summary (`MaSGA` — Hack the Sauna)

Sauna quality depends on coupled physical variables — oxygen concentration, CO2 buildup, bench-level vs. stove temperature, enthalpy, and humidity — yet most bathers and sauna managers rely solely on a single analog thermometer and guesswork for ventilation and adding water (*löyly*).

**Make Sauna Great Again (MaSGA)** pairs Vaisala's live multi-point industrial sauna sensor telemetry with empirical user-preference calibration and **trapezoidal fuzzy similarity scoring**:
1. Polls Vaisala's real-time sauna measurement API covering bench, stove, and floor probes (`O2`, `CO2`, `Temperature`, `Enthalpy`, `Relative humidity`).
2. Computes separate domain-specific comfort/efficiency scores (`0–100%`) for **Sauna Users** vs. **Sauna Facility Managers**, calibrated from **22 real sauna-bather survey responses** collected from bathers spending at least `10–15` minutes in the test sauna.
3. Outputs real-time traffic-light experience tiers (`> 88%` green, `> 75%` orange, `<= 75%` red) and concrete operational actions (e.g., *"Add water to stove"*, *"High CO2 levels, open the door"*, *"Power up the stove"*, *"Turn on air ventilation"*).

---

## Hardware / Sensors / Edge / Cloud Stack

| Layer | Observed Component / Technology | Exact Details from `Addono/masga-backend` & `Addono/masga` |
|---|---|---|
| **Physical Sensor Network** | **Vaisala Multi-Sensor Sauna Telemetry** | Multi-position probes (`Stove1`, `Bench1`, `Bench2`, `Bench3`, `Floor1`) measuring Temperature, Relative Humidity, Enthalpy, CO2, and Oxygen |
| **Partner Data Gateway** | **Vaisala API Gateway REST Endpoint** | `https://apigtw.vaisala.com/hackjunction2018/saunameasurements/latest?SensorID=...&limit=1` |
| **Cloud Scoring Engine** | **Google Cloud Functions** (`Python`) | Deployed endpoint `us-central1-junction-2018.cloudfunctions.net/get-percentage?user={user\|manager}` running `Addono/masga-backend/main.py` |
| **Frontend Web Dashboard** | **Bootstrap 4.1.3 + jQuery 3.3.1** | `Addono/masga/js/main.js` polling Cloud Function every **`10 s`** (`10000 ms`) with user/manager mode switching |

---

## Architecture

```text
[Vaisala Sauna Probes: Stove1, Bench1, Bench2, Bench3, Floor1]
   │ O2, CO2, Temp, RH, Enthalpy
   ▼
[Vaisala API Gateway] (apigtw.vaisala.com/hackjunction2018/saunameasurements/latest)
   │ Polled by Cloud Function on demand
   ▼
[Google Cloud Functions: get-percentage?user={user|manager} (main.py)]
   ├─► Trapezoidal fuzzy similarity engine quadro(): S21 = (s2 ^ v) * s4
   ├─► Empirically calibrated from 22 sauna-bather surveys (>=10-15 min sessions)
   └─► Generates percentage score + targeted action alert strings
   ▼
[Web Dashboard (Bootstrap 4.1.3 / jQuery 3.3.1, 10s poll)]
   ├─► > 88%: Green ("Perfect sauna experience")
   ├─► > 75%: Orange ("Degraded sauna experience")
   └─► <= 75%: Red ("Poor sauna experience")
```

---

## Key Engineering Decisions & Observed Sensor Targets (`main.py`)

### 1. User Mode vs. Manager Mode Sensor Targets `[SensorID, metric, norm, optimal]`

**User Mode** (`?user=user` — bather comfort & air quality):
- `Bench3 Oxygen`: norm `/1`, optimal `17.0`
- `Bench2 Temperature`: norm `/5`, optimal `70.0`
- `Bench1 CO2`: norm `/100`, optimal `800.0`
- `Floor1 Temperature`: norm `/5`, optimal `35.0`
- **Actionable User Alerts**:
  - `Bench2 Relative humidity < 10` -> `"Add water to stove"`
  - `Bench1 CO2 > 1000` -> `"High CO2 levels, open the door"`

**Manager Mode** (`?user=manager` — energy, thermal capacity & ventilation control):
- `Stove1 Temperature`: norm `/10`, optimal `290`
- `Bench2 Enthalpy`: norm `/10`, optimal `280`
- `Bench2 Relative humidity`: norm `/1`, optimal `18`
- `Bench1 CO2`: norm `/100`, optimal `800`
- **Actionable Manager Alerts**:
  - `Stove1 Temp < 280 or Bench2 Enthalpy < 180` -> `"Power up the stove"`
  - `Stove1 Temp > 400` -> `"Power down the stove"`
  - `Bench2 Enthalpy > 400` -> `"Cool down the stove"`
  - `Bench2 RH < 12` -> `"Add more water"` / `Bench2 RH > 28` -> `"Don't add water"`
  - `Bench1 CO2 > 1000` -> `"Turn on air ventilation or open the door"`

### 2. Fuzzy Similarity Math (`quadro()`)
Rather than brittle linear averaging or single-threshold pass/fail checks, **Alireza Jaribion** and **Siavash H. Khajavi** implemented a **trapezoidal fuzzy number similarity index** `quadro()` computing `S21 = (s2 ^ v) * s4` (falling back to `exp(tz) * s4` when intervals collapse). The team later formalized this hackathon methodology into a peer-reviewed **IEEE IECON 2020** publication (`DOI: 10.1109/IECON43393.2020.9254270`).

---

## Metrics & Baseline

- **Ground-Truth Calibration Dataset**: **22 sauna user surveys** collected from bathers spending **>= 10–15 minutes** inside the monitored sauna.
- **Dashboard Refresh Interval**: `10 s` (`jQuery` polling to Google Cloud Functions).
- **UI Score Thresholds**: `> 88%` Green (*"Perfect sauna experience"*), `> 75%` Orange (*"Degraded sauna experience"*), `<= 75%` Red (*"Poor sauna experience"*).

---

## Demo Highlights

- Dual persona UX switching seamlessly between **Bather** comfort guidance (e.g., open door at high CO2, add *löyly* when dry) and **Sauna Operator** plant tuning (stove power / enthalpy bounds).
- Video demonstration archived at `https://youtu.be/rNtnsDjz0vM`.

---

## Transferable Lessons for IoT & Sensor-Analytics Teams

1. **Collect Real Ground Truth On-Site**: Gathering 22 human comfort surveys inside the actual instrumented sauna gave *MaSGA* defensible optimal targets (`70 °C` bench, `800 ppm` CO2, `17%` O2) instead of arbitrary guesswork.
2. **Translate Raw Telemetry into Role-Specific Actions**: Raw sensor graphs force users to interpret numbers; mapping multi-sensor deviations directly to *"Add water"* or *"Turn on ventilation"* turns telemetry into an interactive product.
3. **Publishable Sensor Fusion**: Multi-sensor fuzzy similarity (`quadro()`) was robust enough both for a 48-hour demo and for subsequent IEEE IECON peer review (`2020`).

---

## Sources & Raw Excerpts

- **L1 Winner Backend & Frontend**: https://github.com/Addono/masga-backend (`main.py`) & https://github.com/Addono/masga (`js/main.js`)
- **L1 Official Partner Blog — Vaisala**: https://www.vaisala.com/en/blog/2018-11/winners-vaisalas-challenges-junction-2018-hacked-weather-and-sauna
  - Confirms winners & runners-up for both Vaisala challenges (**MaSGA**, **Talking Sauna**, **BMC – Blazing Measurements and Controls**; **Should I Go**, **Weather Player**, **rairAI.biz**) and judges (**Sampsa Lahtinen, Ari Alanko, Riku Hakala**).
- **L2 Official University News — Aalto University**: https://www.aalto.fi/en/news/winning-team-hack-the-sauna-experience-to-a-new-level-at-junction
- **L2 Academic Follow-Up — Aaltodoc (IECON 2020)**: https://aaltodoc.aalto.fi/items/44b6d03b-0849-4381-a9e4-300de579f7d3
