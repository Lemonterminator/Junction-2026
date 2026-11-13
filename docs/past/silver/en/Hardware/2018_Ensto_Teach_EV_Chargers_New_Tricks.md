# [2018] Ensto — Teach EV Chargers New Tricks

## Metadata

- **Year**: 2018
- **Challenge Partner**: Ensto
- **Original Historical Track**: IoT & Hardware
- **2026 Target Track**: Hardware Track (by Arduino)
- **Sub-theme**: Smart Energy, EV Charging & Mobility Hardware
- **Core Theme**: Feature extension for smart EV charging stations based on hardware development boards and the Ensto IoT platform
- **Classification Rationale**: Originally in the IoT & Hardware track. Required developing new features on on-site provided hardware development boards and deeply integrating with the Ensto smart charging station IoT backend REST API.

---

## Full Original Challenge Name

Teach EV Chargers New Tricks

## Challenge Description

Car charging can be much more than just plugging a car and filling the battery. Cars are charged in homes, workplaces, hotels, shopping malls, car parks and airports, to just mention a few, and in all these places the user may have different needs. Create the best possible car charging experience for the electric car driver on one or more segments. Implement/demo this solution utilizing Ensto’s platform offered REST API and additional functionality developed on top of the provided development boards. You can also utilize the already collected IoT data from our backend service for your solution.

---

## Winning Solutions & Verified Historical Cases

- **1st Prize Ensto & Junction 2018 Overall Grand Winner 🏆 (€20,000)**: **Oneiro (Team Glados)** (Teemu Taskula, Andreas Urbanski, Ville Toiviainen — back-to-back Junction Grand Champions after 2017 *Signvision*) `[L1]`/`[L2]` — "Airbnb for EV chargers" eliminating winter RFID/keycard handoffs: a **Raspberry Pi + PiCamera** (`systemd photographer.service`) streams `640x480` frames every `0.5 s` (`2 s` timeout) to an AWS Sanic backend running Dockerized **`openalpr:16.04`** (`country="eu"`, `region="fi"`, threshold `confidence >= 75`), automatically unlocking and billing physical **Ensto Chago** hardware (`JunctionEVB1`) via the EnstoFlow OCPP/REST v1 API alongside a React Native Expo app and a Mapbox GL Uusimaa demand heatmap powered by Telia cellular activity data.
- **Hardware & Integration Takeaways**: Wrapping real physical charger endpoints behind a `LIVE_MODE=true` toggle vs. deterministic mock charger IDs (`oneiro` / `junction-6`), exposing physical charger LED state machines (`Green` -> `Blue` Charging), and closing the loop from edge vision to owner revenue split (`0.25 €/h` + `0.6 €/h`, `owners_cut = 0.70`) anchored both peer votes and Ensto jury scoring.
- **Bronze Case Study**: [`2018_Ensto_Oneiro_Glados.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2018_Ensto_Oneiro_Glados.md)
- **Primary Sources**: [GitHub (`teamglados/oneiro`)](https://github.com/teamglados/oneiro) | [Vimeo Demo](https://vimeo.com/302650304) | [Mobiili.fi Coverage](https://mobiili.fi/2018/11/25/junction-hackathon-espoossa-paattyi-latauspisteiden-airbnbn-voittoon-sama-tiimi-voitti-kilpailun-viime-vuonnakin/) | [Talotekniikka-lehti](https://talotekniikka-lehti.fi/oneiro-voitti-junction-2018-hackathonin/)
