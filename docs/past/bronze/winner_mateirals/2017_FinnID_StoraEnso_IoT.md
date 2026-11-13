# Finn-ID & Stora Enso / Siili RFID + Packaging IoT — Hardware Stack, Entries & Win Record (Junction 2017)

- **Event / Year**: Junction 2017 (Dipoli, Aalto University, Espoo, November 24–26, 2017)
- **Challenges Covered**:
  1. **Finn-ID** — *"RFID Navigation"*
  2. **Stora Enso & Siili Solutions** — *"Store Smarter"* (Intelligent Packaging / Smart Warehouse IoT)
- **Silver Challenge Specs**:
  - [2017_Finn_ID_RFID_Navigation.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2017_Finn_ID_RFID_Navigation.md)
  - [2017_Stora_Enso_Siili_Store_Smarter.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2017_Stora_Enso_Siili_Store_Smarter.md)
- **Verification Tier**:
  - **Hardware / API Infrastructure**: **L1 Verified** (`serge-sedelnikov/junction2017` official Stora Enso starter pack & `Konkko/junction2017-finnid` participant repo exposing Finn-ID endpoint)
  - **Finn-ID / Stora Enso Winner Record**: **L2 Partial Win Claim (`Itis.Team` — ITMO University / `mbradio.ru`), Partner-Specific Winner Unverified in L1 Archives**
- **Primary URLs**:
  - Stora Enso Official IoT Architecture & Starter Repo: https://github.com/serge-sedelnikov/junction2017
  - Finn-ID Participant Repo (`Konkko/junction2017-finnid`): https://github.com/Konkko/junction2017-finnid
  - ITMO University News (`Itis.Team` 2017 IoT Smart Warehouse Win): https://news.itmo.ru/ru/news/9084/
  - Interview on Itis.Team's 3 Junction 2017 Hardware Projects (`mbradio.ru`, Dec 19, 2017): https://mbradio.ru/publication/2403

---

## 1. Stora Enso & Siili Official Hardware / Telemetry Architecture (`serge-sedelnikov/junction2017`) [L1]

The official **Stora Enso / Wood City / Intelligent Packaging** starter repository documents exact physical warehouse IoT hardware deployed inside Dipoli at Junction 2017:

| Subsystem | Observed Hardware / Protocol | Exact Endpoint / Parameters |
|---|---|---|
| **UHF RFID Gate** | **Impinj** 4-antenna UHF RFID reader (`MAC 00:16:25:12:16:4F`) | `20 ms` continuous scan rate; raw **`Socket.IO`** stream at `balabanovo.westeurope.cloudapp.azure.com` reporting `antenna_port`, `epc`, `peak_rssi`, and `scan_count` |
| **Filtered Zone Events** | **MQTT** broker (`mqtt.intelligentpackaging.online`) | TCP port **`1883`** and WebSocket port **`9001`** emitting stateful zone topics `location/:id/tagEntered` and `location/:id/tagLeft` |
| **NFC Interaction** | NFC smart packaging tags | MQTT topic `nfc/scan` supporting custom per-tag redirect URLs |
| **Environmental LoRa Nodes** | Autonomous **LoRa** air-quality & motion sensors | Reported **temperature, relative humidity, CO2, luminosity, and movement** every **`15 minutes`**, exposed via **GraphQL** API at `woodcityapiqa.azurewebsites.net/api/v1/GraphQL` (`building: "Junction2017"`) |

---

## 2. Finn-ID Hardware API & Verified Submission (`Konkko/junction2017-finnid`) [L1]

- **Authors**: **Niko Autio**, **Kimmo Sairanen**, `jatu`
- **Architecture Observed**:
  - **Backend (`Node.js` / `Express`)**: Polled Finn-ID's live Azure EPC inventory service (`http://finnidhackjunctionrfidwebapi.azurewebsites.net/api/Epc/GetAll`) on a **`1 s` interval** to track real-time tagged asset locations across RFID reader zones.
  - **Frontend**: **`Vue.js 2.5.2`** reactive browser UI visualizing live tagged item state.

---

## 3. Verified Participant / Win Claim Record (`Itis.Team`) [L2]

- **Team**: **Itis.Team** (Kazan / ITMO University — **Mikhail Kolchanov**, **Daniil Samoylov**, **Nikita Khilobok**, Mark, Ekaterina Vissarionova).
- **Projects Built at Junction 2017** (`https://mbradio.ru/publication/2403`):
  1. **`It is alive`**: Real-time parcel condition monitoring (temperature, humidity, shock/acceleration, illumination) inside smart boxes.
  2. **`Finn-id-universal security`**: Physical-document anti-loss/anti-theft monitoring utilizing **Finn-ID** RFID readers to alert on missing/unauthorized document movement.
  3. **`Itis LIGHT`**: Offline intelligent lighting assistant (submitted in Helvar's smart lighting context).
- **Win Claim (`https://news.itmo.ru/ru/news/9084/`)**: ITMO University's official news article states that at Junction 2017 the team built *"три проекта, одна победа (Обработка и визуализация данных с IoT устройств на умном складе)"* (1 victory in *"Processing and visualization of data from IoT devices in a smart warehouse"*).
- **Attribution Gap**: While `news.itmo.ru` explicitly records a Junction 2017 IoT Smart Warehouse victory, neither ITMO nor `mbradio.ru` nor public Stora Enso / Finn-ID announcements publish the exact partner challenge title (whether *Stora Enso*, *Finn-ID*, or an internal sub-prize), and no independent L1 Devpost/partner blog post confirms the complete winner rosters of either **Finn-ID** or **Stora Enso** at Junction 2017.

---

## Transferable Lessons for Industrial RFID & Warehouse IoT Teams

1. **Dual Raw + Stateful Event Streams (`Socket.IO` + `MQTT`)**: Stora Enso's starter kit paired noisy `20 ms` raw RSSI packets (`Socket.IO`) with clean server-debounced `tagEntered`/`tagLeft` state transitions (`MQTT`) — letting advanced teams build localization ML on raw RSSI while UI teams consumed clean entry/exit events immediately.
2. **Match Polling Frequency to Sensor Physics**: High-speed RFID portals ran at `20 ms` (`1 s` HTTP polling in `Konkko`), whereas autonomous battery-powered **LoRa** environmental sensors reported every `15 minutes` via GraphQL.

---

## Sources & Raw Excerpts

- **L1 Official Starter Kit**: https://github.com/serge-sedelnikov/junction2017 (Impinj `00:16:25:12:16:4F`, MQTT `1883`/`9001`, LoRa GraphQL `woodcityapiqa.azurewebsites.net/api/v1/GraphQL`)
- **L1 Participant Repo (`Finn-ID`)**: https://github.com/Konkko/junction2017-finnid (`http://finnidhackjunctionrfidwebapi.azurewebsites.net/api/Epc/GetAll`, Vue `2.5.2`)
- **L2 University News (`ITMO`)**: https://news.itmo.ru/ru/news/9084/
- **L2 Interview (`mbradio.ru`)**: https://mbradio.ru/publication/2403
