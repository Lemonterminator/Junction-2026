# Ericsson — "Saved by IoT" Smart Cloud Winner (Junction 2018)

- **Event / Year**: Junction 2018 (Aalto University, Espoo, November 23–25, 2018)
- **Track & Challenge**: **Smart Cloud** Track — *"Saved by IoT"* (**Ericsson**) *(Ericsson sponsored three Smart Cloud challenges: `Signaling Heroes`, `Threat Intelligence FTW`, and `Saved by IoT`)*
- **Silver Challenge Spec**: [2018_Ericsson_Saved_By_IoT.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Ericsson_Saved_By_IoT.md)
- **Verification Tier**: **L1 Partial Winner Description** (Official EU Horizon 2020 **SOFIE** IoT consortium report covering Junction 2018; winning team name, member roster, and repository were not published)
- **Verified Winning Concept Summary**:
  - Per the official EU **SOFIE Project** Junction 2018 event report (Dec 11, 2018): *"the winners of the Ericsson Smart Cloud track developed a Bluetooth enabled device with long battery life deployed with drones, using mesh network for crisis communication for the Saved by IoT challenge."*
- **Primary URL**:
  - SOFIE H2020 Post-Event Report (Dec 11, 2018): https://www.sofie-iot.eu/news/junction-2018-europe-s-biggest-hackathon.html

---

## Problem & Solution Summary

When cellular towers and grid power collapse during earthquakes, floods, or remote wilderness emergencies, rescue teams lack low-power local communication relays capable of reaching survivors across obstructed terrain.

According to the SOFIE post-event summary, the winning team of Ericsson's Smart Cloud track (**Saved by IoT**) designed a **long-battery-life Bluetooth-enabled mesh node deployed via drones** to establish an airborne/dropped ad-hoc crisis communications mesh network without fixed infrastructure.

---

## Observed Technical Stack (from L1 SOFIE Source)

- **Radio & Networking**: **Bluetooth** low-energy / **mesh networking** for decentralized off-grid crisis communication.
- **Power Envelope**: Designed explicitly around **long battery life** for emergency endurance.
- **Deployment Platform**: **Drone-deployed** physical relay/beacon nodes bridging unreachable crisis zones.

---

## Archive Status & Disambiguation Notes

- **Team Name / Roster Gap**: Neither the SOFIE report nor indexed Devpost, GitHub, Medium, or Ericsson corporate blog archives list the winning team's name, individual members, or public source code repository.
- **Disambiguation vs. Help.io / Health.io**: While **Help.io / Health.io** (University of Latvia) also built an offline disaster Bluetooth Mesh solution at Junction 2018 (using **Suunto Movesense** wearables + **Intel NUC / PHYTEC `reel_board`s** to win the Intel challenge, IoT track, and 2nd Overall), `Help.io`'s public code (`mnimants/junction2018`) and University of Latvia release document **patient vital-sign triage**, not **drone-deployed long-battery Bluetooth beacons**. Therefore, SOFIE's description confirms a distinct **Ericsson Smart Cloud Track** winner implementing **drone-dropped Bluetooth mesh crisis nodes**.

---

## Sources & Raw Excerpts

- **L1 Primary Source — SOFIE H2020 Blog (Dec 11, 2018)**: https://www.sofie-iot.eu/news/junction-2018-europe-s-biggest-hackathon.html
  > Verbatim finding: Ericsson sponsored three Smart Cloud challenges (`Signaling Heroes`, `Threat Intelligence FTW`, `Saved by IoT`), and *"the winners of the Ericsson Smart Cloud track developed a Bluetooth enabled device with long battery life deployed with drones, using mesh network for crisis communication for the Saved by IoT challenge."*
- **Searched Without Additional Winner Identification**: Devpost (`junction-2018.devpost.com` & `site:devpost.com/software`), GitHub (`Junction 2018` + `Saved by IoT` / `Ericsson`), Ericsson newsroom, and Medium (`hack-junction`).
