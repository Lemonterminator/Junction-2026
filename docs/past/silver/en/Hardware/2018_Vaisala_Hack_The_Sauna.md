# [2018] Vaisala — Hack the Sauna

## Metadata

- **Year**: 2018
- **Challenge Partner**: Vaisala
- **Original Historical Track**: Sustainability
- **2026 Target Track**: Hardware Track (by Arduino)
- **Sub-theme**: Smart Buildings, Industrial IoT & Digital Twins
- **Core Theme**: Industrial-grade sauna sensing and measurement instruments (replacing traditional mechanical thermometers) and digital experience in extreme high-temperature and high-humidity environments
- **Classification Rationale**: Although originally in the Sustainability track, it focuses on the application and digital transformation of precision temperature and humidity measurement sensor hardware in extreme high-temperature and high-humidity physical environments (sauna rooms).

---

## Full Original Challenge Name

Hack the Sauna

## Challenge Description

Sauna is a traditional place for bathing and relaxation. It can also be a harsh environment for both people and measurement instruments. The sauna experience has not changed much in centuries: for example, the conditions in sauna are still today measured using mechanical temperature gauges. We feel like it is time to modernise the sauna experience!

---

## Winning Solutions & Verified Historical Cases

- **1st Prize Winner**: **Make Sauna Great Again (MaSGA)** (Siavash H. Khajavi, Alireza Jaribion, Adriaan Knapen, Leila Abiedat, Arnab Banik) `[L1]`/`[L2]` — Polled Vaisala's live multi-point sauna probes (`Stove1`, `Bench1–3`, `Floor1` tracking O2, CO2, Temperature, Relative Humidity, Enthalpy) via Google Cloud Functions running a trapezoidal fuzzy similarity model (`quadro()`) empirically calibrated from **22 real sauna-bather surveys** (`10–15 min` sessions). Delivered separate **User Mode** (`Bench2 Temp 70°C`, `Bench3 O2 17%`, `Bench1 CO2 800 ppm`) and **Manager Mode** (`Stove1 Temp 290°C`, `Enthalpy 280`, `RH 18%`) actionable alerts (`> 88%` green / `> 75%` orange / `<= 75%` red) over a `10 s` dashboard poll, later published at IEEE IECON 2020.
- **Verified Runners-Up**: **Talking Sauna** & **BMC – Blazing Measurements and Controls** `[L1]`.
- **Hardware & IoT Takeaways**: Grounding multi-probe thermodynamics in real empirical survey calibration and role-split alerts (bather comfort vs. facility stove/ventilation control) avoids arbitrary sensor thresholds.
- **Bronze Case Study**: [`2018_Vaisala_MaSGA.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2018_Vaisala_MaSGA.md)
- **Primary Sources**: [Frontend Repo (`Addono/masga`)](https://github.com/Addono/masga) | [Backend Repo (`Addono/masga-backend`)](https://github.com/Addono/masga-backend) | [Vaisala Official Blog](https://www.vaisala.com/en/blog/2018-11/winners-vaisalas-challenges-junction-2018-hacked-weather-and-sauna) | [Aalto News](https://www.aalto.fi/en/news/winning-team-hack-the-sauna-experience-to-a-new-level-at-junction) | [IEEE IECON 2020 (Aaltodoc)](https://aaltodoc.aalto.fi/items/44b6d03b-0849-4381-a9e4-300de579f7d3)
