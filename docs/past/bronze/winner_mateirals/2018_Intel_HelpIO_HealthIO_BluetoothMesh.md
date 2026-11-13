# Help.io / Team Health.io — Intel Bluetooth Mesh Winner, IoT Track Winner & 2nd Place Overall (Junction 2018)

- **Event / Year**: Junction 2018 (Aalto University, Espoo, November 23–25, 2018)
- **Track & Challenges**:
  - **Internet of Things (IoT) Track**
  - **Intel Challenge**: *"Innovative applications with Bluetooth mesh"*
  - **Movesense by Suunto**: *"Track Anything That Moves"* (patient biometric hardware layer)
  - *(Also cross-referenced: **Nokia / Intel IoT** 2nd Prize EV Bluetooth Mesh entry by **José Manuel García**, Univ. of Málaga)*
- **Silver Challenge Spec**: [2018_Intel_Innovative_Applications_With_Bluetooth_Mesh.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Intel_Innovative_Applications_With_Bluetooth_Mesh.md)
- **Verification Tier**: **L1 + L2** (Participant GitHub repo `mnimants/junction2018`, official Intel repos `intel/Junction2018` & `feri/Junction2018_Support`, Suunto Movesense official announcement, University of Latvia Faculty of Computing news, UMA press release, ITMO news)
- **Verified Awards (**Help.io** / **Health.io**)**:
  - **1st Prize — Intel Challenge**: *"Innovative applications with Bluetooth mesh"*
  - **1st Prize — Internet of Things (IoT) Track Overall**
  - **2nd Place Overall — Junction 2018 Main Competition** (among the top 11 track-winning finalist teams; also referenced in `mobiili.fi`'s finalist summary as an offline disaster communication system without internet)
- **Team Name & Members**: **Help.io** (in Swift UI / app code; referred to as **Team Health.io** in Movesense coverage) — University of Latvia Faculty of Computing students & alumni:
  - **Austris Cīrulnieks**
  - **Mārcis Nīmants** (`mnimants`)
  - **Elvijs Viļķels**
  - **Aigars Cibuļskis**
  - **Dāvis Mednis**
  *(Four of the five — Cīrulnieks, Nīmants, Viļķels, Mednis — previously won the 2017 Movesense Health Challenge with `ReCover`.)*
- **Primary URLs**:
  - Participant GitHub Repo: https://github.com/mnimants/junction2018
  - Official Intel BlueZ Mesh Stack (`meshd-ingas`): https://github.com/intel/Junction2018
  - Official Intel Support Kit & Sample Apps: https://github.com/feri/Junction2018_Support
  - Movesense Official 2018 Recap (Nov 28, 2018): https://www.movesense.com/news/2018/11/movesense-shined-in-junction-hackathon/
  - University of Latvia Official News (Nov 28, 2018): https://eztf.lu.lv/en/about-us/news/detail-view/t/98941/

---

## Problem & Solution Summary

In major natural disasters or mass-casualty incidents where cellular towers and power grids fail, first responders cannot rely on internet-backed triage software, yet medical personnel scattered across disaster zones urgently need to prioritize deteriorating patients.

**Help.io** builds a fully **offline, infrastructure-less emergency medical triage network**:
1. Patients wear **Suunto Movesense** BLE chest/skin sensors that stream real-time heart rate (`average` BPM) and R-R interval (`rrData`) telemetry.
2. Local iOS collector nodes run live biometric deterioration scoring directly on-device (`Swift` / iOS 12).
3. Whenever a patient crosses critical thresholds or experiences severe HR/RR volatility, the iOS gateway forwards an HTTP status event over a local Wi-Fi link to an **Intel NUC** running **BlueZ Mesh (`meshd`)**, which broadcasts triage alerts across **PHYTEC `reel_board`** smart badges worn by responders over a **Bluetooth Mesh** network requiring zero internet connectivity.

---

## Hardware / Sensors / MCU / Edge Tech Stack

### Official Intel Hackathon Kit (`feri/Junction2018_Support` & `intel/Junction2018`)

| Component | Exact Hardware / Software Observed | Role in Kit |
|---|---|---|
| **Edge Gateway** | **Intel NUC** (Linux) on local Wi-Fi `jnct-ble5-mesh` (capacity for **8 teams**) | Hosts experimental **BlueZ `meshd`** daemon (`intel/Junction2018` `meshd-ingas` branch; `ell 0.13`, D-Bus service `org.bluez.mesh1`) and Python 3 control gateway |
| **Mesh Wearable Badges** | **4x PHYTEC `reel_board`s** per team | Runs **Zephyr OS** (`samples/boards/reel_board/mesh_badge`) with e-ink/display readout, LED blink indicator, and on-board temperature sensor |
| **BLE HCI Dongle** | **nRF51 Dongle** (`nRF51_dongle` running Zephyr `hci_uart`) | Acts as the NUC's Bluetooth 5 / Mesh HCI controller |
| **Bluetooth Mesh Models** | BlueZ `example-models-console` (Python 3 / D-Bus) | `0x0000` Vendor Client (`0xfbf105` / `0xfdf105`), `0x1000` Generic OnOff (`0x8201` / `0x8202` / `0x8203`), `0x1102` Sensor Client (`0x8231`, temp `0x2a1f`) |

### Help.io Team Stack (`mnimants/junction2018`)

| Component | Exact Hardware / Software Observed | Role in Solution |
|---|---|---|
| **Biometric Wearables** | **Suunto Movesense** sensors | Verified device serials in Swift code: `175030001053` (Sector #1 -> mesh node `0x0001`) and `175030000988` (Sector #2 -> mesh node `0x0002`); streams `Movesense.HR_PATH` (`average` + `rrData`) |
| **Local Collector / Triage Engine** | **iOS 12 / Swift** app | Pods/libraries: `Movesense`, `AsyncDisplayKit` (`Texture`), `PromiseKit`, `Bond`, `SwiftyJSON`, `Alamofire`, `ScrollableGraphView` |
| **Gateway Bridge** | Local HTTP-to-Mesh endpoint | App POSTs via `Alamofire` to `http://10.100.5.16:3000/{bluetoothId}/{setup\|critical}` targeting Intel NUC mesh gateway |

---

## Architecture

```text
[Patient Sensor: Suunto Movesense BLE (175030001053 / 175030000988)]
   │ BLE HR_PATH (average HR + rrData R-R intervals)
   ▼
[iOS Collector App (Swift / AsyncDisplayKit / Movesense SDK)]
   │ Discard first 5 samples; evaluate last 5 after 15 readings
   │ Thresholds: HR < 60 or > 110, RR multiplier > 2.0, severity index
   │ Alamofire HTTP -> http://10.100.5.16:3000/{bluetoothId}/{setup|critical}
   ▼
[Intel NUC Gateway (BlueZ meshd-ingas D-Bus org.bluez.mesh1 + nRF51_dongle hci_uart)]
   │ Bluetooth Mesh (Zero internet / cellular dependency)
   ▼
[Responder Wearables: PHYTEC reel_board Mesh Badges (Zephyr mesh_badge)]
   └─► Displays patient sector alert & severity status directly on responder badge
```

---

## Key Engineering Decisions & Observed Logic (`ChooseDeviceTableNodeController.swift`)

1. **Warm-Up Filtering & Rolling Window Triage Scoring**:
   - Discards the initial `discardCount = 5` sensor packets so BLE skin-contact lock-in transients do not trigger false alarms.
   - Once `heartRateHistory.count >= 15`, computes a live triage severity metric over the last `historyItemsCount = 5` readings:
     - `severity = Int(avgHR + rrHighBound - rrLowerBound)`
   - Enforces physiological bounds (`lowestHRBound = 60.0`, `highestHRBound = 110.0` — inline code comments explicitly note higher production emergency thresholds like `140` / `240` were tightened for hackathon live-demo triggering) plus R-R variability checks (`highestRRMultiplier = 2.0`).
2. **Immediate Visual + Mesh Escalation**: On breach, the iOS dashboard flashes the patient cell red (`criticalState`) and dispatches `/critical` over local LAN directly to the Intel NUC mesh gateway (`10.100.5.16:3000`) to page doctors across the **Bluetooth Mesh** (`0x0001`, `0x0002`).
3. **Hardware Split Around BLE Stack Quirks**: Bridging **Movesense** sensors through an iOS collector before entering **Intel NUC + BlueZ `meshd`** avoided unreliable Linux-host simultaneous GATT + experimental BlueZ mesh multiplexing on a single `nRF51_dongle`.

---

## Metrics & Baseline

- **Kit Deployment Scale**: Intel supplied hardware kits for **8 teams** (1x NUC + 4x PHYTEC `reel_board`s + `nRF51_dongle` each); **26 teams** total submitted Movesense-based projects across Junction 2018.
- **Confirmed Triage Constants**: `discardCount = 5`, `heartRateHistory.count >= 15`, `historyItemsCount = 5`, `lowestHRBound = 60.0`, `highestHRBound = 110.0`, `highestRRMultiplier = 2.0`.
- **Competition Result**: Beats all other IoT track teams for **Intel 1st Prize** + **IoT Track Overall Winner**, placing **2nd Overall** out of 300+ projects and 11 track-winning finalists.

---

## Related Verified 2018 Intel / Nokia Bluetooth Mesh Entries [L2]

- **José Manuel García** (Industrial Organization Engineering, **Universidad de Málaga**): Won **2nd Prize** in the **Nokia & Intel IoT Bluetooth Mesh ("Bluetooth Mesh 5G") challenge** (`uma.es`, Nov 29, 2018) with an autonomous decentralized EV multi-point charging coordination system where vehicles connect over Bluetooth, build a local spatial map, and self-organize to charging stations by cost and user need. Source: https://www.uma.es/sala-de-prensa/noticias/tres-estudiantes-de-la-uma-se-alzan-con-los-tres-primeros-premios-de-junction-2018/
- **Itis.Team** (**Daniil Samoylov**, **Nikita Khilobok**, **Mikhail Kolchanov**, ITMO University): According to ITMO University press coverage (`https://news.itmo.ru/ru/news/9084/`), also claimed recognition at Junction 2018 for a solution combining **Intel NUC** and **Movesense** hardware (*exact challenge rank not independently confirmed in Intel/Movesense L1 releases*).

---

## Transferable Lessons for Embedded & Mesh IoT Teams

1. **Always Separate Sensor Acquisition From Mesh Transport During Hackathons**: Using iOS/BLE for mature sensor SDK acquisition (**Movesense**) and handing simple HTTP/JSON triggers (`/{id}/critical`) to the experimental **BlueZ Mesh** gateway let the team master two complex stacks in 42–48 hours without driver collisions.
2. **Expose Tunable Demo Thresholds Clearly**: Commenting hackathon-demo bounds (`60`–`110` BPM) vs. clinical bounds (`140`/`240`) lets judges both trigger live physical alerts reliably on stage and trust domain engineering judgment.
3. **Inspect Official Partner Support Kits First**: Intel's `heri` / `feri/Junction2018_Support` and `intel/Junction2018` (`meshd-ingas` commits by Inga Stotland & Brian Gix just days before Junction) show the exact BlueZ D-Bus APIs (`org.bluez.mesh1`, Vendor `0x0000`, OnOff `0x1000`, Sensor `0x1102`) teams built on.

---

## Sources & Raw Excerpts

- **L1 Participant GitHub**: https://github.com/mnimants/junction2018 (`ChooseDeviceTableNodeController.swift`, Movesense SDK integration, `10.100.5.16:3000`)
- **L1 Official Intel Mesh Repo & Support Kit**: https://github.com/intel/Junction2018 & https://github.com/feri/Junction2018_Support
- **L1 Official Partner Release — Movesense (Nov 28, 2018)**: https://www.movesense.com/news/2018/11/movesense-shined-in-junction-hackathon/
- **L2 Official University Release — Univ. of Latvia (Nov 28, 2018)**: https://eztf.lu.lv/en/about-us/news/detail-view/t/98941/
  > Lists all 5 members (**Austris Cīrulnieks, Mārcis Nīmants, Elvijs Viļķels, Aigars Cibuļskis, Dāvis Mednis**) and confirms they *"komanda uzvarēja Intel izaicinājumā 'Innovative applications with Bluetooth mesh'"*, won the IoT track overall, and took **2nd Place Overall** among the top 11 finalist teams.
