# [2019 Hardware-Adjacent Case Study] QOCO Systems — Smooth Travels (`NFC & QR Baggage Tracking`)

## 1. Metadata & Verification Ledger

- **Dataset Correction Alert**: Marked `"Year": 2020` in `docs/past/bronze/challenges_full.json`, **actually occurred at Junction 2019 (November 15–17, 2019)** — independently proven by the official `"The winners of Junction 2019"` Medium post `[L1]`, winner blog dated `2019-11-19` `[L2]`, and participant GitHub commits dated Nov 16–17, 2019 `[L1]`.
- **Event & Dates**: Junction 2019 (November 15–17, 2019, Väre, Otaniemi, Espoo)
- **Partner**: **QOCO Systems** (aviation & maintenance operations SaaS)
- **Challenge Name**: `Smooth Travels` (19 participating teams `[L2]`)
- **Verified Official Placements** (`[L1]` Junction Medium):
  - **Winner (1st Place)**: **Luggage Love**
  - **Runner-up (2nd Place)**: **Skylock** *(details `[Not publicly documented]`)*
  - **Honorable Mentions**: **Trags** & **QOCO Realtime Assistant** *(details `[Not publicly documented]`)*
- **Verified Winning Prototype Narrative** (`[L2]` Author Blog):
  - **Ryoji Matsuzaki** (`ryojimatsuzaki`, Aalto University IDBM UI/UX designer) + **3 programmers + 1 business member** (5-person team) won 1st place in QOCO Systems' `Smooth Travels` track out of 19 teams with a working **Smartphone + NFC chip** baggage-pairing Finnair mobile add-on prototype `[L2]`. *(Note: `[L1]` lists the 1st-place winner name as `Luggage Love` and `[L2]` records Matsuzaki's team winning 1st place in this exact track; because Matsuzaki's blog did not explicitly print the string "Luggage Love", both labels are recorded transparently without conjecture.)*
- **Unranked Participant Codebase Found (Disambiguated)**:
  - [`dani2819/baggage-handling-app`](https://github.com/dani2819/baggage-handling-app) (**"Find My Bag"**, commits Nov 16–17, 2019 by `Abdullah Danyal Saeed`, `Azeem Akhter` / `azmaktr`, `kamalmemon`) — QR-code PWA alternative (`react-qr-code` + `react-qr-reader` + Firebase), documented below as a direct NFC-vs-QR architectural comparison `[L1]`.
- **Evidence Sources**:
  - `[L1]` Official Winners Announcement: Junction Medium, *"The winners of Junction 2019"* (`https://medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f`)
  - `[L2]` Winner Blog: Ryoji Matsuzaki, *"JUNCTION 2019でカテゴリー優勝🎉"* (`https://aaltoidbm.hatenablog.com/entry/2019/11/19/071856`, published 2019-11-19)
  - `[L1]` Participant QR Implementation: [`dani2819/baggage-handling-app`](https://github.com/dani2819/baggage-handling-app) (`package.json`, `presentation/` PDF & `.drawio` diagrams)

---

## 2. Physical-Digital Pain Point & Hardware Trade-Off (NFC vs QR)

Checked airport luggage creates passenger anxiety during transfers and baggage claim because travelers often only learn a bag went missing *after* every suitcase has cleared the carousel `[L2]`.

```mermaid
flowchart LR
    subgraph NFCWinner["1st Place Winner Prototype (ryojimatsuzaki Team, L2)"]
        TAG["Passive NFC Tag / Chip<br/>on Checked Baggage"] -->|Tap to Read & Pair| PHONE["Smartphone Finnair Add-On<br/>(Mobile NFC Reader)"]
        PHONE -->|Event Stream| STATUS["Near-Real-Time Baggage Status<br/>& Airline Loading Efficiency"]
    end

    subgraph QRPeer["Unranked Peer Architecture (dani2819 / Find My Bag, L1)"]
        QR["Printed / Digital QR Bag Tag<br/>(react-qr-code)"] -->|Camera Scan| PWA["React 16.12 + Ant Design PWA<br/>(react-qr-reader + Firebase)"]
    end
```

### Engineering Trade-Offs Observed Across the Challenge
1. **NFC Chip Pairing (`ryojimatsuzaki` winning prototype, `[L2]`)**:
   - **Mechanism**: Uses physical near-field communication (`NFC` chip embedded/attached to luggage) scanned directly by the passenger's smartphone to bind traveler identity with bag telemetry inside an airline add-on (conceptualized for Finnair) `[L2]`.
   - **Strength**: Fast tap pairing, survives dark cargo holds/tarmac weather better than paper barcodes once read by ground-crew RFID/NFC gates, and impressed judges enough with a working physical chip-pairing demo to beat 18 competing teams (winning a follow-up company presentation at QOCO Systems) `[L2]`.
   - **Trade-off**: Requires airline-side NFC/RFID reader infrastructure rollout across hubs before achieving network-effect reliability `[L2]`.
2. **QR Camera Scanning (`dani2819/baggage-handling-app`, `[L1]`)**:
   - **Stack**: `react` `^16.12.0`, `antd`, `antd-mobile`, `firebase` `^7.4.0`, `react-qr-code` `^0.1.3`, `react-qr-reader` `^2.2.1`, `netlify-cli` `[L1]`.
   - **Trade-off**: Zero physical hardware dependencies beyond existing paper tags and phone cameras, making deployment universal, but visually less tactile than physical NFC tap pairing during a live hackathon pitch.

---

## 3. Transferable Hardware Hackathon Lesson

- **Even a Single Cheap Physical Tag Elevates an Enterprise SaaS Pitch**: In an aviation API challenge where most of the 19 teams built web dashboards (`Find My Bag`), bringing an actual **physical NFC chip** and demonstrating live smartphone-to-tag pairing in under 30 seconds made the passenger experience tangible and secured 1st place `[L2]`.
