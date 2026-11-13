# GuideMe — Makers UPV (Future Cities Track Winner & 4th Place Overall, Junction 2018)

- **Event / Year**: Junction 2018 (Aalto University, Espoo, November 23–25, 2018)
- **Track**: **Future Cities** *(Smart Physical / Assistive IoT Hardware prototype adjacent to Espoo/Urban Hardware challenges; cited alongside Oneiro & Help.io in `mobiili.fi` as a Main Competition top finalist — `"vanhuksia suunnistamaan avustava älykävelykeppi"`)*
- **Silver Context**: [Hardware/README.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/README.md) & [2018_Espoo_Analyzed_Information_At_Your_Fingertips.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Espoo_Analyzed_Information_At_Your_Fingertips.md)
- **Verification Tier**: **L1 + L2** (Complete hardware/firmware/CAD/backend GitHub repository `makers-upv/GuideMe` + official Universitat Politècnica de València press release + `mobiili.fi` Junction finalist report)
- **Award(s)**:
  - **1st Prize — Future Cities Track (€1,000)**
  - **4th Place Overall — Junction 2018 Main Competition** (finishing behind **Oneiro** `#1` and **Help.io** `#2` among top track-winning finalists)
- **Team Name & Members**: **Makers UPV** (Universitat Politècnica de València):
  - **Jaime Laborda Macario**
  - **Iván Torres Játiva** (Electronic Engineering)
  - **Enrique Miralles Dolz** (Nuclear Fusion Engineering)
  - **Joaquín Montesinos Muñoz** (Telecommunications Engineering)
  - **Matías Fernández Patón** (Biomedical Engineering)
- **Primary URLs**:
  - GitHub Repository: https://github.com/makers-upv/GuideMe
  - UPV Official News Release: https://www.upv.es/noticias-upv/noticia-10627-junction-2018-es.html
  - Mobiili.fi Finalist Coverage: https://mobiili.fi/2018/11/25/junction-hackathon-espoossa-paattyi-latauspisteiden-airbnbn-voittoon-sama-tiimi-voitti-kilpailun-viime-vuonnakin/

---

## Problem & Solution Summary

Older adults experiencing mild cognitive impairment, disorientation, or Alzheimer's disease often get lost walking in unfamiliar areas, and small smartphone screens are difficult to read while walking outdoors.

**GuideMe** embeds an autonomous turn-by-turn **smart walking-cane handle** + remote caregiver dashboard:
1. A family member or caregiver opens the **GuideMe** web map interface and sets the elderly user's desired destination.
2. The **PHP backend** queries the **Google Maps Directions API**, calculates exact walking bearings between sequential waypoints, and serves live target azimuth instructions.
3. A **Wemos ESP8266** Wi-Fi MCU housed inside the custom **3D-printed ergonomic cane handle** polls navigation commands over HTTP and relays waypoint bearings via UART (`115200 baud`) to a **BBC micro:bit**.
4. Using the **micro:bit's onboard magnetometer compass**, the cane calculates real-time heading error and lights up bold directional arrows on the **5x5 LED matrix** while triggering a **vibration/buzzer actuator** (pin 1) for turns, all while reporting live GPS/route state back to the caregiver web interface.

---

## Hardware / Firmware / CAD / Web Stack (`makers-upv/GuideMe`)

| Layer | Observed Hardware / Tech | Exact File / Spec Details |
|---|---|---|
| **Display & Compass MCU** | **BBC micro:bit** (ARM Cortex-M0 + magnetometer + 5x5 LED array) | MicroPython firmware `micro.py`; reads UART (`115200 baud` on pins `0` / `2`), drives `pin 1` vibration/buzzer haptic feedback, compares magnetometer heading to target bearing, and displays directional arrows on 5x5 LED grid |
| **Wi-Fi Connectivity Node** | **Wemos ESP8266** | Arduino C++ sketch `guideme_arduino_wifi_node.ino` polling HTTP backend routes and forwarding target headings over serial to micro:bit |
| **Mechanical Enclosure** | Custom **3D-Printed Walking-Cane Handle** | CAD & print files committed in repo (`guideme_handle.SLDPRT` SolidWorks part + `.STL` mesh), engineered on-site to house MCU + battery + top-facing 5x5 LEDs |
| **Cloud / Navigation Backend** | **PHP + Google Maps Directions API** | `web/back.php` + `web/front.php` calculating turn-by-turn walking route vectors |
| **Caregiver Tracking UI** | **HTML / jQuery / AJAX Map UI** | Caregiver enters destination and monitors user position and route status in real time |

---

## Architecture

```text
[Caregiver Web UI (web/front.php: jQuery / AJAX)]
   │ Sets destination on map; monitors live user location
   ▼
[PHP Server (web/back.php + Google Maps Directions API)]
   │ Resolves walking waypoints & target compass bearings
   ▼ HTTP Polling over Wi-Fi
[Wemos ESP8266 (guideme_arduino_wifi_node.ino)]
   │ UART Serial (115200 baud, pins 0/2)
   ▼
[BBC micro:bit (MicroPython: micro.py) + 3D-Printed Cane Handle (STL)]
   ├─► Magnetometer compares cane orientation vs. target bearing
   ├─► 5x5 LED Matrix displays high-contrast directional arrow
   └─► Pin 1 triggers tactile vibration / buzzer guidance
```

---

## Key Engineering Decisions

1. **Decoupling Wi-Fi (ESP8266) from UX & Compass (BBC micro:bit)**: Rather than fighting tiny I2C OLED displays or building custom compass-calibration libraries on a bare Wi-Fi microcontroller under 48-hour pressure, the team leveraged the **BBC micro:bit**'s built-in magnetometer + 5x5 LED matrix + simple MicroPython runtime alongside an **ESP8266** strictly as a serial Wi-Fi modem (`115200` UART).
2. **Physical CAD Delivery During Hackathon**: Including both parametric CAD (`guideme_handle.SLDPRT`) and printable `.STL` geometry produced a tangible, holdable ergonomic smart cane handle on stage — critical for winning Future Cities and reaching 4th Place Overall.
3. **Glanceable Low-Cognitive-Load Interface**: High-contrast 5x5 arrows + haptic vibration on a walking aid eliminates smartphone handling for elderly users.

---

## Metrics & Competition Standing

- **Prizes**: **€1,000** (1st Place Future Cities Track) + **4th Place Overall** out of 300+ projects (`upv.es`).
- **UART Interface Spec**: `115200` baud over `pin 0` / `pin 2`, with actuator output on `pin 1` (`micro.py`).

---

## Transferable Lessons for Embedded & Assistive-Hardware Teams

1. **Use Dual-MCU Division of Labor for Speed**: Pairing a connectivity-first board (**ESP8266**) over plain UART with a sensor/display-rich board (**micro:bit**) eliminates driver conflicts and speeds up firmware iteration.
2. **Always Bring Custom 3D-Printed Form Factor to Demo Stage**: Turning loose breadboards into a functional, ergonomic handle (`guideme_handle.STL`) directly elevated an IoT prototype into an overall top-4 finalist.
3. **Design Around Two Stakeholders**: Balancing ultra-simple hardware UX for the senior user with a full web tracking map for the caregiver tells a complete adoption story.

---

## Sources & Raw Excerpts

- **L1 GitHub Repository**: https://github.com/makers-upv/GuideMe (`micro.py`, `guideme_arduino_wifi_node.ino`, `guideme_handle.SLDPRT`, `.STL`, `web/back.php`, `web/front.php`)
- **L2 University Press Release — UPV**: https://www.upv.es/noticias-upv/noticia-10627-junction-2018-es.html
  - Confirms **Future Cities 1st Place (€1,000)**, **4th Place Overall**, and all 5 team members (**Jaime Laborda Macario, Iván Torres Játiva, Enrique Miralles Dolz, Joaquín Montesinos Muñoz, Matías Fernández Patón**).
- **L2 Finnish Press — Mobiili.fi (Nov 25, 2018)**: https://mobiili.fi/2018/11/25/junction-hackathon-espoossa-paattyi-latauspisteiden-airbnbn-voittoon-sama-tiimi-voitti-kilpailun-viime-vuonnakin/
