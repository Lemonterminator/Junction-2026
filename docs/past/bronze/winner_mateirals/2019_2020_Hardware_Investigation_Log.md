# [Investigation Log] Junction 2019–2020 Hardware, Radar, Edge, Robotics & IoT Audit

## 1. Purpose & Methodology

This log documents the exhaustive source verification conducted across **Junction 2019** (Nov 15–17, 2019, Otaniemi, Espoo) and **Junction 2020 Connected** (Nov 6–8, 2020, hybrid/online during COVID-19) for the Bronze archive (`docs/past/bronze/winner_mateirals/`).

**Evidence Grading Standard**:
- **`[L1]` Primary Evidence**: Official Junction winner announcements (`medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f`), primary source code repositories & commit histories (`github.com`), official Silver challenge specifications (`docs/past/silver/en/Hardware/`).
- **`[L2]` Secondary Evidence**: Partner engineering blogs & press releases (`vttresearch.com`, `aalto.fi`, `lfedge.org`, `sttinfo.fi`, `hkfoods.com`), university achievement announcements (`hse.ru`, `sutd.edu.sg`), Wikipedia (`Junction (hackathon)`), and verified author blogs/articles/resumes (`elizavetalebedeva.com`, `habr.com`, `alenev.ru`, `andreykr.com`, `aaltoidbm.hatenablog.com`, `sireesh.io`, `startupadventures.org`).
- **Epistemic Discipline**: Cloudflare/403-protected pages (`medium.com`, `startupadventures.org`, `vk.ru`, `chatbotslife.com`) were never bypassed; verification relied strictly on search-grounded snippets + redirect resolution + direct fetching of open primary repos and readable technical blogs. Unverified fields are explicitly marked `[Not publicly documented]`.

---

## 2. Overall Grand Winners Verification (2019 & 2020)

| Year | Event Edition | Overall Grand Winner | Track / Partner | Hardware / CV / Edge Involvement? | Verification Sources |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2019** | **Junction 2019** | **TassuPassu** *(Runners-up: `Crowds Against Humanity`, `Vault. Secure the Future`)* | Ericsson — *Security Awareness for Kids* | **No (Pure Software)** — gamified visual/story password manager for kids (Team: Tulika Ganoo, Yevhenii Kalashnyk, Reinis Skorovs, Ronalds Sovas) | `[L1]` Medium winners post + `[L2]` Wikipedia |
| **2020** | **Junction 2020 Connected** | **Saavi – Healthy Finance** | OP / Finance Track | **Yes (Mobile Spatial Computing / ARKit)** — native iOS `ARKit` tracking physical credit card (`ist_card.arreferenceimage`) + card-tilt angular-velocity UI switching + `scikit-learn` ML backend | `[L1]` `azimin/MoneyMustBeFunnyAkaJunction2020Backup` & `antoleb/saavi_back` + `[L2]` Wikipedia & `andreykr.com` |

---

## 3. Master Audit of All 2019–2020 Challenges & Outcomes

### 3.1 Silver Hardware Track (`docs/past/silver/en/Hardware/`, 5 Challenges in 2019, 0 in 2020)

| Year | Partner & Challenge | Original Track | Verified Winners (`[L1]` Medium) | Hardware / Code Proof Found | Bronze Case Study |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2019** | **Aalto University (AYY)** — *Smart Signage - For Student by Students* | `IoT & Hardware` | **Winner**: `AyyHello!` | Full `[L1]` repo `mariporko/junction2019`: RPi `RPi.GPIO` PIR (`PIN 11`)/LED (`PIN 3`), PyTorch `MobilePose` webcam CV -> `POST /dir`, React kiosk + AYY building CSVs | [`2019_Aalto_AYY_SmartSignage_AyyHello.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2019_Aalto_AYY_SmartSignage_AyyHello.md) |
| **2019** | **Helvar & VTT** — *Making Spaces Brighter with Radar Technology* | `AI & Data` | **Winner**: `LumenLoop`<br/>**1st RU**: `Brighten your way`<br/>**2nd RU**: `figvam` | Full `[L1]` repo `deniskovalenko/junction2019` (Denys Kovalenko & Elizaveta Lebedeva) + 11-page `README.pdf` (60/24 GHz specs, RabbitMQ FlatBuffers, DALI `pyserial` Helvar luminaire `EC22`, React UI, Elasticsearch). `[L2]` `hse.ru` confirms `figvam` roster & WiFi FingerPrinting/sleep-light modes | [`2019_Helvar_VTT_Radar_LumenLoop.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2019_Helvar_VTT_Radar_LumenLoop.md) |
| **2019** | **Valmet & Aalto** — *Service Workshop of the Future* | `AI & Data` | **Winner**: `PaperCut Inc.`<br/>**1st RU**: `Smooth Grindr` | `[L2]` Ucha Vekua (`startupadventures.org`) confirms VR 3D roller-data visualization; `[L2]` `aalto.fi` confirms micron roll-grinding telemetry (€50/min downtime) + `ValmetXR` (Unity) + `Node-RED` | [`2019_Valmet_ServiceWorkshop_PaperCut_Inc.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2019_Valmet_ServiceWorkshop_PaperCut_Inc.md) |
| **2019** | **SUSE** — *Open Open City* | `Urban & Mobility` | **Winner**: `Flowify`<br/>**1st RU**: `suseXcity`<br/>**2nd RU**: `Ravenholm` | Team code `[Not publicly documented]`; full `[L2]` LF Edge Akraino MicroMEC blog details SUSE's on-site Raspberry Pi `3B+`/`4B` (`k3s` + OpenFaaS Cloud + ETSI MEC) cluster | [`2019_SUSE_OpenOpenCity_Flowify.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2019_SUSE_OpenOpenCity_Flowify.md) |
| **2019** | **Ericsson** — *Greener City Transport with 5G* | `Urban & Mobility` | **Winner**: `League of Agents`<br/>**1st RU**: `5G`<br/>**2nd RU**: `FastCity` | `[L2]` Adithya Sireesh resume confirms 1st place via RL transport agents; `[L1]` Silver spec confirms server fleet-control API simulation | [`2019_Ericsson_5GTransport_LeagueOfAgents.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2019_Ericsson_5GTransport_LeagueOfAgents.md) |

### 3.2 Remaining `challenges_full.json` 2019–2020 Tracks & Junction 2020 Connected Partners

| Year (True vs JSON) | Partner & Challenge | Outcome / Trace Found | Hardware Track Relevant? |
| :--- | :--- | :--- | :--- |
| **2019** *(JSON: 2020 Error)* | **QOCO Systems** — *Smooth Travels* | `[L1]` Medium: Winner `Luggage Love`, Runner-up `Skylock`, HMs `Trags` & `QOCO Realtime Assistant`. `[L2]` `ryojimatsuzaki` won 1st/19 with **Smartphone + NFC chip** Finnair prototype. Contrast unranked QR repo `dani2819/baggage-handling-app` | **Yes (NFC-adjacent)** — Case study written ([`2019_QOCO_SmoothTravels_NFC_Baggage.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2019_QOCO_SmoothTravels_NFC_Baggage.md)) |
| **2019** *(JSON: 2020 Error)* | **Stara & Helsingin kaupunki** — *Reboot Building Repairs* | `[L2]` `sttinfo.fi` (20.11.2019) confirms 2019 winner **Xiple** (`Staraoke` software repair workflow) | No (Software) |
| **2019** | **Ericsson** — *Security Awareness for Kids* | `[L1]` Medium: `TassuPassu` (1st & Grand Winner), `teamglados/blackmirror` (2nd) | No (Pure Software) |
| **2019** | **Columbia Road** — *Bring Mispurchases to an End* | `[L1]` Medium: Winner `Road to Spare`; `[L2]` `sutd.edu.sg`: 2nd place **Team SK5** (CV skin-condition recommender) | Software / Cloud CV only |
| **2019** | **Aalto University & CityScienceLab** — *Urban Events Under Hack* | `[L1]` Medium: Winner `Team Discover`; no public hardware/IoT repo found | No public hardware trace |
| **2019** | **VK, Microsoft, Business Finland, D-Fence (x2), CGI & Sitra, Varian, CGI & Kesko, Visit Finland** | Verified challenge presence in `challenges_full.json`; non-hardware tracks | Excluded (Software/Data/Health) |
| **2020 Connected** | **OP** *(Finance)* | Overall Grand Winner **Saavi – Healthy Finance** (native `ARKit` physical card + ML) | **Yes (ARKit/IMU)** — Case study written ([`2020_OverallWinner_Saavi_HealthyFinance_ARKit.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2020_OverallWinner_Saavi_HealthyFinance_ARKit.md)) |
| **2020 Connected** | **HKScan** — *Agrofood Ecosystem* | `[L2]` `hkfoods.com`: Winner **Social Meat** (event food-impact web app; Linnéa Hammarberg, Nguyen Le Khanh Ngoc, Deepjyoti Paul, Tulika Ganoo) | No (Software) |
| **2020 Connected** | **Paulig** | `[L1]` GitHub `thekirsila/Junction2020-Paulig`: Winner (Django + Snowflake coffee sustainability) | No (Software) |
| **2020 Connected** | **Genelec, Aito, Supercell, Brella, Rovio** | Sparse public 2020 sub-challenge winner archives; no public hardware/robotics winners surfaced for Genelec (audio hardware) or other 2020 partners despite targeted searches | `[No public winner trace found]` |
| **2020 Connected** | **Top 10 Finalist (`teamglados/hivemind`)** | Verified web peer-learning platform on GitHub | No (Software) |

---

## 4. Unranked / Community Hardware Prototypes Recovered (Not Confirmed Winners)

During repository forensics, several authentic **non-winning / unranked** Junction 2019–2020 hardware & CV/VR builds surfaced. They are archived here rather than as winner case studies so competition placements remain strictly accurate:

1. **OwlEye (`m0rg0t/OwlEye`, Junction 2020 Connected)** `[L1]` Repo + `[L2]` Author (`habr.com/ru/articles/754234/`, `alenev.ru/en/it/`):
   - **Author**: Anton Lenev (`m0rg0t`), built Nov 6–8, 2020 during Junction 2020 Connected.
   - **Hardware Stack**: `Arduino Nano`, `HC-SR04` ultrasonic rangefinder (`HC_TRIG_PIN = 12`, `HC_ECHO_PIN = 13`), vibration motor (`VIBRO_PIN = 2`), status LED (`LED_PIN = 3`), piezo buzzer (`BUZZER_PIN = 4`), `HW-131` power board, EVA foam cosplay-style housing + Autodesk Fusion 360 3D CAD (`owl/Owl.stl`, `https://a360.co/3eIkNEf`).
   - **Firmware Logic (`arduino/owl_main/owl_main.ino`)**: Computes distance-proportional interval (`signalTimeout = 10 * distance`), pulsing haptic vibration 10 ms before buzzer beep (`tone(BUZZER_PIN, distance * 5)`) + LED flash to act as an assistive wearable necklace ("parking sensor for humans") & COVID-19 distancing aid. No prize or Top-10 placement is claimed in Habr or `alenev.ru`.
2. **Pain-Relief WebVR (`LizaLebedeva/junction-2020-vr` / `deniskovalenko/junction-2020-vr`, Junction 2020 Connected)** `[L1]`:
   - Built by the 2019 Helvar winners (Elizaveta Lebedeva & Denys Kovalenko) using WebVR tested on a budget €13 `iBOX` Google Cardboard mobile headset; no documented 2020 prize.
3. **Find My Bag (`dani2819/baggage-handling-app`, Junction 2019 QOCO)** `[L1]`:
   - Built Nov 16–17, 2019 (`Abdullah Danyal Saeed`, `Azeem Akhter`, `kamalmemon`); React `16.12.0` + Firebase + `react-qr-code` + `react-qr-reader`; unranked participant entry in the 19-team QOCO challenge.
4. **STACC Team (`stacc.ee/junction/`, Junction 2019 Helvar & VTT)** `[L2]`:
   - 5-person Estonian data science team (`Maksym, Raul, Christian, Carlos, Eerik`); documented their weekend on Helvar/VTT's radar challenge without placing top-3.

---

## 5. Metadata Anomalies & False-Positive Disambiguations Resolved

1. **`AyyHello!` vs `LumenLoop` Medium Snippet Conflation**: Because both `Smart Signage` (`Aalto / AYY`) and `Making Spaces Brighter with Radar` (`Helvar & VTT`) sat consecutively under Junction 2019's `Intelligent Infrastructure` showcase, naive search summaries sometimes mixed them. Separate `site:medium.com` queries plus primary `README` inspection in `mariporko/junction2019` and `deniskovalenko/junction2019` cleanly proved **AyyHello! won Aalto AYY Smart Signage** and **LumenLoop won Helvar & VTT Radar**.
2. **`challenges_full.json` Year=2020 Error**: `Stara` and `QOCO` are tagged `Year: 2020` in `challenges_full.json` despite occurring in November **2019**.
3. **Commercial & Cross-Event False Positives Rejected**:
   - UK LED brand `lumenloop.co.uk` and print-management vendor `PaperCut` (unrelated to 2019 teams);
   - Finnish *5G Cyber Security Hackathon* (`traficom.fi` PDF, separate event);
   - Mid-2019 online hackathon winners `Smart Piggy` & `Askpro.online` (Reddit online Junction community event, distinct from November Helsinki 2019/2020 flagship editions);
   - `Lumen Loop 3.0` (`LizaLebedeva/junction-2021`, 2021 follow-up with AirTag/graph maintenance, properly separated from Denys & Elizaveta's 2019 `LumenLoop` Helvar win).

---

## 6. Representative Search Queries Executed

- `"The winners of Junction 2019" site:medium.com/hack-junction`
- `"Making Spaces Brighter with Radar" site:medium.com/hack-junction`
- `"Smart Signage" site:medium.com/hack-junction/the-winners-of-junction-2019`
- `"Smart Signage" "First runner-up" OR "Second runner-up" "Junction 2019"`
- `"Service Workshop of the Future" site:medium.com/hack-junction/the-winners-of-junction-2019`
- `"Open Open City" site:medium.com/hack-junction/the-winners-of-junction-2019`
- `"Greener City Transport" site:medium.com/hack-junction/the-winners-of-junction-2019`
- `"Smooth Travels" site:medium.com/hack-junction/the-winners-of-junction-2019`
- `"Urban Events Under Hack" "Junction 2019" winner OR "Bring Mispurchases to an End" "Junction 2019" winner`
- `site:elizavetalebedeva.com "Junction" OR "Helvar"` & `"LumenLoop" "Elizaveta" OR "Denys Kovalenko"`
- `"Ucha Vekua" "Junction" OR "PaperCut Inc" "Junction 2019" OR "startupadventures.org" "Valmet"`
- `"ryojimatsuzaki" "QOCO" OR "Smooth Travels" "Junction 2019" winner`
- `"The Winners of Junction 2020 Connected" site:medium.com/hack-junction OR site:hackjunction.com`
- `"Junction 2020" "Genelec" winner OR "Aito" winner OR "Brella" winner OR "Supercell" OR "Rovio" OR "HKScan"`
- `"OwlEye" "Junction" OR "m0rg0t" "Junction 2020"`
- `"Smart Piggy" "Askpro.online" OR "Smart Piggy" "Junction" "2020"`
