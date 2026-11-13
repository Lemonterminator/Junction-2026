# [2018] Intel — Innovative Applications With Bluetooth Mesh

## Metadata

- **Year**: 2018
- **Challenge Partner**: Intel
- **Original Historical Track**: IoT & Hardware
- **2026 Target Track**: Hardware Track (by Arduino)
- **Sub-theme**: Embedded Systems, Edge Computing & Connectivity
- **Core Theme**: Smart space control based on IoT edge gateways and Bluetooth Mesh wireless sensor networks
- **Classification Rationale**: Originally in the IoT & Hardware track. Required building smart lighting, temperature control, security, or smart badge systems on IoT edge gateways that communicate with Bluetooth® Mesh wireless sensor network devices.

---

## Full Original Challenge Name

Innovative Applications With Bluetooth Mesh

## Challenge Description

Bluetooth® Mesh networking creates new opportunities for interacting with your environment, whether you’re making your home or office smarter using intelligent lighting, heating/cooling, and security systems, or wireless sensor networks.
The challenge includes creating an application, on IoT edge gateway, which is communicating and utilizing the capabilities of Bluetooth® Mesh network devices. Examples of such applications could be messaging boards, smart badge system or sensor data collection system.

---

## Winning Solutions & Verified Historical Cases

- **1st Prize Intel + 1st IoT Track + 2nd Place Overall (Main Competition)**: **Help.io / Team Health.io** (University of Latvia: Austris Cīrulnieks, Mārcis Nīmants, Elvijs Viļķels, Aigars Cibuļskis, Dāvis Mednis — returning core from 2017 Movesense winner `ReCover`) `[L1]`/`[L2]` — Built a zero-internet emergency triage mesh bridging Suunto Movesense BLE HR/R-R sensors (`Movesense.HR_PATH`) -> iOS 12 triage scorer (warm-up `discardCount = 5`, rolling window `5` after `15` readings, HR bounds `60..110`, RR ratio `> 2.0`) -> LAN HTTP (`10.100.5.16:3000/{id}/{setup|critical}`) -> **Intel NUC** BlueZ `meshd-ingas` + `nRF51_dongle` -> **4x PHYTEC `reel_board`s** running Zephyr `mesh_badge` smart responder badges (`0x0001`, `0x0002`).
- **Additional Verified Placer (`[L2]` Univ. of Málaga)**: **2nd Prize (Nokia / Intel EV Bluetooth Mesh)** — **José Manuel García** (UMA).
- **Hardware & Protocol Takeaways**: Offloading BLE peripheral telemetry through a mobile collector before entering the **Intel NUC BlueZ `meshd`** edge daemon avoided simultaneous Linux GATT + experimental Bluetooth Mesh HCI contention on a single `nRF51_dongle`; tightly gated live-demo thresholds guaranteed deterministic main-stage alerts.
- **Bronze Case Study**: [`2018_Intel_HelpIO_HealthIO_BluetoothMesh.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2018_Intel_HelpIO_HealthIO_BluetoothMesh.md)
- **Primary Sources**: [GitHub (`mnimants/junction2018`)](https://github.com/mnimants/junction2018) | [Intel BlueZ Mesh (`intel/Junction2018`)](https://github.com/intel/Junction2018) | [Intel Kit (`feri/Junction2018_Support`)](https://github.com/feri/Junction2018_Support) | [Movesense 2018 Recap](https://www.movesense.com/news/2018/11/movesense-shined-in-junction-hackathon/) | [Univ. of Latvia News](https://eztf.lu.lv/en/about-us/news/detail-view/t/98941/)
