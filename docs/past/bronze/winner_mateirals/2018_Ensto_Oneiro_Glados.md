# Oneiro — Team Glados (Junction 2018 Overall Grand Winner & Ensto Mobility Winner)

- **Event / Year**: Junction 2018 (Espoo / Aalto University Campus, Dipoli, November 23–25, 2018)
- **Track & Challenge**: Mobility — *"Teach EV chargers new tricks"* (**Ensto** / Ensto Flow)
- **Silver Challenge Spec**: [2018_Ensto_Teach_EV_Chargers_New_Tricks.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Ensto_Teach_EV_Chargers_New_Tricks.md)
- **Verification Tier**: **L1 + L2** (Winning team GitHub repository + Finnish technology press + Mobiili.fi coverage with Ensto Head of Software quote)
- **Award(s)**:
  - **1st Prize — Junction 2018 Main Competition (Overall Grand Winner, €20,000)** (selected via participant peer-review voting across ~1,200–1,300 participants and 300+ solutions)
  - **1st Prize — Ensto Challenge** (*"Teach EV chargers new tricks"*, out of **14 teams** participating across Ensto's two Junction 2018 challenges; **Ensto challenge judge**: **Ville Parviainen**, Head of Software, Ensto)
- **Team Name & Members**: **Team Glados** (**Oneiro** project) — **Teemu Taskula** (`Temzasse`), **Andreas Urbanski**, **Ville Toiviainen** (`Villux`) (Finnish software developers & Aalto University students; repeat Junction Main Competition champions after winning Junction 2017 with *Signvision*)
- **Primary URLs**:
  - GitHub Repository: https://github.com/teamglados/oneiro (5 stars, 1 fork; created 2018-11-23, last updated 2019-11-18)
  - Demo Video: https://vimeo.com/302650304
  - Historical Team Deployment Endpoints (recorded in repo): `https://api.teamglados.com`, `https://heatmap.teamglados.com`
  - Talotekniikka-lehti Article: https://talotekniikka-lehti.fi/oneiro-voitti-junction-2018-hackathonin/
  - Mobiili.fi Coverage (Nov 25, 2018): https://mobiili.fi/2018/11/25/junction-hackathon-espoossa-paattyi-latauspisteiden-airbnbn-voittoon-sama-tiimi-voitti-kilpailun-viime-vuonnakin/

---

## Problem & Solution Summary

Many densely populated urban areas and private residential parking spots lack public EV charging infrastructure, leaving private or semi-private chargers idle for much of the day while visiting EV drivers struggle to find convenient charging.

**Oneiro** ("Airbnb for EV charging stations") turns private **Ensto Chago** charging stations into a peer-to-peer shared charging network with zero physical RFID keycards or manual owner handoffs:
1. A charger owner registers their Ensto Chago charging point and earns revenue when drivers rent it.
2. An EV driver reserves an available charger via the **Oneiro** mobile app and simply drives up to the spot.
3. A **Raspberry Pi + PiCamera** mounted at the charging bay continuously captures frames and streams them to the backend, where **OpenALPR** automatically recognizes the incoming vehicle's European/Finnish license plate.
4. Once license plate confidence passes threshold (`>= 75`), the backend automatically unlocks and starts an OCPP transaction on the Ensto Chago hardware via the **EnstoFlow REST API**, shifting charger state from green (`Available` / `Pending`) to blue (`Charging`).
5. A companion **City Planner / Operator Heatmap** overlays **Telia** mobile network activity density with existing EV charger footprints across Uusimaa to identify under-served high-demand areas.

---

## Hardware / Sensors / MCU / Edge Tech Stack

| Layer | Observed Component / Technology | Exact Details from `teamglados/oneiro` & Sources |
|---|---|---|
| **EV Charger Hardware** | **Ensto Chago** EV charger | Controlled via Ensto Flow `RealDevice` group (`JunctionEVB1` when `LIVE_MODE=true`; simulated IDs `oneiro` / `junction-6` for test mode); controller placed in `A -> C` mode with status LEDs (`Unavailable` = red, `Available` = green, `Pending` = green, `Charging` = blue) |
| **Edge Vision Node** | **Raspberry Pi + PiCamera** | `raspberry/photographer.py` managed via `systemd` (`photographer.service`), capturing `640x480` `pi_image.jpg` frames every `0.5 s` and posting multipart `media` with a `2 s` HTTP timeout to `/postimage` |
| **ALPR Engine** | **OpenALPR** (`openalpr:16.04` Docker image) | `server/licence_plate.py` (`country="eu"`, `default_region="fi"`, `detect_region=False`, `top_n=5`) triggering `spot_enable()` at `confidence >= 75` |
| **Backend Server** | Python 3 + **Sanic** (`port 8000`) | `server/server.py`, `server/api.py`, `server/enstoflow.py`, `server/apiwrapper.py`, `server/evobjects.py` |
| **Charger Control API** | **EnstoFlow REST API v1** + OCPP polling | `https://junctionev.enstoflow.com/api/v1/` (HTTP Basic Auth); endpoints `chargingPointGroup`, `chargingPoint/{id}/configuration`, `resetsoft`, `resethard`, `{connector}/starttransaction/{tag}`, `stoptransaction`, `unlockconnector`, `statusoperative`, `statusinoperative`, plus OCPP polling (`BootNotification`, `DiagnosticsStatusNotification`, `FirmwareStatusNotification`, `Heartbeat`, `MeterValues`, `StatusNotification`) |
| **Mobile Client** | **React Native (`sdk-31.0.0`) + Expo (`^31.0.2`)** | `client/` using Redux, Redux-Saga, and Axios |
| **Urban Heatmap** | **Mapbox GL JS `v0.51.0`** | `heatmap/` combining Telia cellular activity (`11.1.2018 2pm - 4pm`, `Uusimaa_activity_data_hourly_20_min_break_MTC_201801.txt`, `FI_MTC_WGS84_update.shp`) with charger coordinates bounded to `22 <= long <= 26`, `59 <= lat <= 64` |
| **Cloud / IaC** | **Terraform + AWS** | `cloud/*.tf` provisioning EC2 `t2.nano`, ELB (`443 -> 8000`), ECR (`glados`), S3, CloudFront, and Route53 |

---

## Architecture

```text
[Raspberry Pi + PiCamera]
   │ 640x480 JPEG every 0.5s (systemd photographer.service, POST /postimage, 2s timeout)
   ▼
[AWS EC2 t2.nano / ELB :443 -> Sanic Backend :8000 (openalpr:16.04)]
   │ OpenALPR (EU / region=fi, confidence >= 75) -> match plate to reservation
   ▼
[EnstoFlow REST API v1 (junctionev.enstoflow.com/api/v1/)]
   │ Basic Auth -> unlockconnector / starttransaction/{tag} / status & OCPP polling
   ▼
[Ensto Chago Charger (JunctionEVB1)]
   │ State LED transitions: Available (green) -> Charging (blue) -> Stop & Billing
   ├──► [React Native Expo Client] (Driver reservation / Owner income view)
   └──► [Mapbox GL JS Heatmap] (Telia Uusimaa activity + existing charger coverage)
```

---

## Key Engineering Decisions

1. **Physical-World Zero-Friction Authentication via Edge ALPR**: Instead of requiring new RFID cards or QR scanning in winter conditions, mounting a low-cost Raspberry Pi camera to automate plate recognition eliminated manual authentication steps while still gating physical power delivery cleanly on `confidence >= 75`.
2. **Dual Live / Demo Mode Abstraction**: `enstoflow.py` explicitly isolates hardware integration (`LIVE_MODE=true` targeting `JunctionEVB1` inside `RealDevice`) from simulated IDs (`oneiro` / `junction-6`). `server/README.md` documents the physical charger controller sequence (`A->C` mode and LED colors) so judges and teammates could verify hardware state transitions reliably.
3. **Resilient Edge Polling Loop**: The edge capture script (`photographer.py`) runs under `systemd` with an explicit `2 s` HTTP timeout and `0.5 s` cadence, preventing transient Wi-Fi stalls at the hackathon venue from freezing the Pi camera pipeline.
4. **Full-Stack + Business Model Execution**: Ensto Head of Software **Ville Parviainen** specifically praised the combination of deep Ensto API integration, user-friendly UI, and complete business model calculation (`owners_cut = total_cost * 0.70`, pairing electricity & parking fee components).

---

## Metrics & Baseline

- **Hackathon Competition Scale**: ~1,200–1,300 participants (selected from 7,000+ applicants across 100+ nationalities), 300+ submitted solutions; **14 teams** across Ensto's two Junction 2018 challenges.
- **Vision & Latency Parameters**: `640x480` capture interval `0.5 s` (2 FPS capture cadence), `2 s` request timeout, `top_n=5` ALPR candidates, auto-unlock threshold `confidence >= 75`.
- **Mock Pricing / Owner Economics (from `spot_stop_charging` & `README.md`)**:
  - Mock session duration in demo: `random.uniform(60, 120)` minutes
  - Tariff model in code: charging `0.25 €/h` + parking `0.6 €/h`; `owners_cut = total_cost * 0.70`
  - Documented theoretical charger owner revenue: `500€ to 3000€ per year` assuming `2–3h/day` shared utilization
- **Prizes Won**: **€20,000** Main Competition Grand Prize + Ensto Mobility Challenge 1st Prize.

---

## Demo Highlights

- Live end-to-end physical hardware integration against **Ensto Chago** charger unit `JunctionEVB1` triggered from a live camera stream on Raspberry Pi + React Native mobile interface + live Vimeo demo (`vimeo.com/302650304`).
- Added an operator planning view (**Mapbox GL JS** + **Telia** Uusimaa activity shapefile) showing spatial gaps between human density and public EV chargers.

---

## Transferable Lessons for Hardware / Embedded / Edge Teams

1. **Wrap Partner Hardware Behind Live + Mock Flags**: Supporting both physical device control (`LIVE_MODE=true`) and deterministic mock devices (`oneiro` / `junction-6`) lets frontend, backend, and ML work proceed in parallel without blocking on limited physical test units.
2. **Treat Physical State Observability as First-Class**: Documenting hardware LED states and OCPP lifecycle calls (`BootNotification`, `Heartbeat`, `MeterValues`, `StatusNotification`) makes live hardware demos debuggable under 48-hour pressure.
3. **Close the Loop From Sensor to Economics**: Pairing embedded/IoT automation with both consumer UX (mobile app) and macro operator value (Telia demand heatmap + revenue split math) directly aligns with judge scoring on business viability.
4. **Make Edge Networking Bounded**: Short HTTP timeouts (`2 s`) and `systemd` service supervision keep headless edge nodes self-healing on crowded hackathon networks.

---

## Sources & Raw Excerpts

- **L1 Primary Source — GitHub Repo**: https://github.com/teamglados/oneiro
  - Directory/file evidence verified: `raspberry/photographer.py`, `raspberry/photographer.service`, `Dockerfile` (`openalpr:16.04`), `server/licence_plate.py`, `server/enstoflow.py`, `server/apiwrapper.py`, `server/evobjects.py`, `server/server.py`, `server/api.py`, `server/README.md`, `client/` (Expo `^31.0.2`), `heatmap/` (`Mapbox GL JS v0.51.0`, Telia `Uusimaa_activity_data_hourly_20_min_break_MTC_201801.txt`), `cloud/*.tf`.
- **L2 Primary News — Talotekniikka-lehti**: https://talotekniikka-lehti.fi/oneiro-voitti-junction-2018-hackathonin/
  > *"Ensto asetti tapahtumaan kaksi haastetta, joihin osallistui kaikkiaan 14 tiimiä. Oneiron suomalaiset ohjelmistokehittäjät Teemu Taskula, Andreas Urbanski ja Ville Toiviainen suunnittelivat voittoprojektissaan sovelluksen sähköautojen latauspisteiden vuokraamiseen suoraan omistajan toimesta."*
- **L2 Primary News — Mobiili.fi (Nov 25, 2018)**: https://mobiili.fi/2018/11/25/junction-hackathon-espoossa-paattyi-latauspisteiden-airbnbn-voittoon-sama-tiimi-voitti-kilpailun-viime-vuonnakin/
  > *"“Olimme mukana kahdella sähkön käyttöön liittyvällä haasteella. Voittajatiimi yhdisti projektissaan huikean teknisen toteutuksen Enston rajapintoihin, minkä lisäksi tuotteen bisnesmahdollisuudet oli mietitty loppuun asti. Toteutuksen kruunasi käyttäjäystävällinen käyttöliittymä”, sanoo voittajahaasteen asettaneen Enston Head of Software, Ville Parviainen."*
