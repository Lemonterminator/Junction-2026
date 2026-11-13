# [2019] Aalto University — Smart Signage - For Student by Students

## Metadata

- **Year**: 2019
- **Challenge Partner**: Aalto University
- **Original Historical Track**: IoT & Hardware
- **2026 Target Track**: Hardware Track (by Arduino)
- **Sub-theme**: Smart Buildings, Industrial IoT & Digital Twins
- **Core Theme**: Hardware form factor design for apartment building smart signage and integration of HVAC/water-electricity/network IoT data
- **Classification Rationale**: Originally in the IoT & Hardware track. Hardware and software design for corridor smart interactive displays across 2,600 apartments in AYY student housing, integrating real sensor data such as building HVAC, water/electricity consumption, and network load.

---

## Full Original Challenge Name

Smart Signage - For Student by Students

## Challenge Description

The Aalto University Student Union (AYY) owns about 2600 apartments, which house around 3500 tenants. AYY has been planning to install information screens (smart signage) to the stairwells and hallways of its apartment buildings. This challenge is about finding solutions and ideas on what these “smart signage” screens could be like in terms of their hardware, but most importantly in terms of their software. What information could they show and what kind of functionality could they include?

AYY would like to see different kinds of ideas and concepts about what kinds of relevant data and functionality could be incorporated into these screens. These can include, for example, data about the building’s heat, water, and electricity consumption, network usage data, AYY’s news and advertising, tenant listings that update automatically, and all kinds of fun functionality that could also work between the screens in different hallways and buildings. At their best, the solutions to this challenge could also improve the experience of communality between the students living in AYY’s housing.

## Resources

AYY will provide: AYY’s IT-team will be on promises during the weekend to help you out with the challenge. We will bring an anonymized package of network usage data and HVAC-data from one of our buildings for you to use.

---

## Winning Solutions & Verified Historical Cases

- **1st Place (Winner)**: **AyyHello!** (Jesse Tolvanen, Satria Sutisna, Harri Rahikainen, Mari Porko, `smirq`) `[L1]` — Transformed passive stairwell signage into a touchless Raspberry Pi interactive kiosk: a hardware PIR sensor (`GPIO.BOARD Pin 11` rising-edge ISR + `Pin 3` status LED) wakes the display, a USB webcam running modified `MobilePose-PyTorch` (`ResNet-18 @ 224x224`) translates debounced 10-frame upper-body gestures (`L`/`R`/`U`) via local `POST /dir` to Flask (`:5000`), and a React `16.12.0` (`nuka-carousel` + `victory`) UI displays real AYY building CSV utility analytics (`/el`, `/heat`, `/water`), transit/weather cards, and a touchless minigame.
- **Hardware & Integration Takeaways**: Decoupling Raspberry Pi GPIO (`pir.py`), PyTorch pose inference (`run_webcam.py`), Flask telemetry parsing (`analysis.py`), and React kiosk (`junction-ayy`) over local HTTP allowed parallel team velocity, while 10-frame majority-vote debouncing prevented raw keypoint jitter without heavy temporal neural networks.
- **Bronze Case Study**: [`2019_Aalto_AYY_SmartSignage_AyyHello.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2019_Aalto_AYY_SmartSignage_AyyHello.md)
- **Primary Sources**: [Junction 2019 Winners (Medium)](https://medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f) | [AyyHello! GitHub Repo (`mariporko/junction2019`)](https://github.com/mariporko/junction2019) | [Aalto News](https://www.aalto.fi/en/news/student-union-looks-for-creative-ideas-for-their-information-channels-from-junction)
