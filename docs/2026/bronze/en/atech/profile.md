# Atech (atech.dev) — Junction 2026 Partner Research Profile

> **Research Category**: Junction 2026 Bronze Hardware & Physical Computing Partner  
> **Core Tags**: Modular Hardware Ecosystem | Prompt-to-Product | "LEGO for Real Electronics" | ESP32-S3 Vibe-Engineering  
> **Archive Path**: `bronze/en/atech/profile.md` & `docs/2026/bronze/en/atech/profile.md`  

---

## 1. Company Overview

- **Company Legal Name**: Atech (commonly referenced as Atech / primary web domain `atech.dev`)
- **Headquarters**: Nordic Region (co-founding leadership operating across Copenhagen, Denmark and Stockholm, Sweden).
- **Founding Background & Genesis**:
  - Founded by three Nordic entrepreneurs uniting backgrounds in industrial product design, embedded engineering, and modern full-stack software development:
    - **Tomas Erik Harmer** (Co-founder & CEO)
    - **Vladimir Baran** (Co-founder & CCO)
    - **David Stålmarck** (Co-founder & CTO)
  - **The Genesis Story**: The concept emerged from a frustrating personal experience when the founders attempted to construct a simple "automated smart plant watering system". They realized that even an elementary physical prototype demanded weeks of wrestling with tangled breadboard jumper wires, hazardous soldering irons, dense microcontroller datasheets, manual pinout mappings, and low-level C/C++ embedded drivers.
  - **The Core Epiphany**: While the modern software ecosystem achieved "prompt-to-app deployment in minutes" through LLMs and web frameworks, **physical hardware engineering remained chained to workflows from twenty years ago**. To dismantle this friction and eliminate months of prototyping latency, they founded Atech to pioneer **"Vibe-engineering for hardware"**.
- **Industry Standing & Venture Backing**:
  - Atech is one of the most prominent hardware and IoT pioneers in the European startup ecosystem, widely celebrated as **"LEGO for real electronics"**.
  - Closed an $800,000 Pre-seed funding round with a premier roster of institutional backers, including Nordic super-angel syndicate **Nordic Makers**, European VC **Emblem**, viral AI software builder **Lovable**, alongside the **Sequoia Scout Fund** and **Andreessen Horowitz (a16z) Scout Fund**.

---

## 2. Core Products & Technical Architecture

Atech engineers a unified physical computing ecosystem, fusing standardized modular hardware components with an LLM-driven prompt-to-firmware synthesis web platform.

### 2.1 Flagship Hardware Portfolio & Modular Ecosystem
- **Modular Electronics Hardware Kits**:
  - **Core Motherboard**: Powered by an **Espressif ESP32-S3** dual-core microcontroller (integrating high-speed 2.4 GHz Wi-Fi 4 and Bluetooth 5.0 LE, equipped with ample SRAM and Flash storage capable of executing lightweight on-device edge ML inference).
  - **Plug-and-Play Standardized Ports**: Numbered, polarized snap-in sockets that eradicate breadboards, loose jumper cables, and soldering irons.
  - **Hot-Swappable Snap-on Sensor & Peripheral Modules**:
    - **Environmental & Sensory Perception**: Industrial-grade temperature and humidity sensors, CO2/air quality gas sensors, capacitive soil moisture probes, precision Time-of-Flight (ToF)/infrared distance and gesture sensors, ambient light detectors, and high-sensitivity MEMS microphones.
    - **Display & Vision Modules**: High-resolution full-color TFT LCDs, micro OLED screens, and ESP32 camera modules.
    - **Human-Machine Input**: Continuous rotary encoders, tactile push buttons, multi-directional micro joysticks, and capacitive touch sliders.
    - **Actuators & Feedback**: Micro audio speakers with integrated amplifiers, passive/active buzzers, addressable RGB LED pixel matrices, and dedicated micro DC motor/servo driver headers.

### 2.2 Core Software Platform & Developer Tooling
- **AI-Driven "Prompt-to-Product" Web Studio**:
  - Developers describe physical device behaviors in natural language (e.g., *"Build a desktop environmental monitor: if CO2 exceeds 1000 ppm or temperature is too high, display a red alert on screen and pulse the buzzer; the rotary knob toggles between Celsius and Fahrenheit"*).
  - The AI compiler parses physical device semantics, selects required peripheral modules, instructs exactly which numbered motherboard port to snap each module into, and automatically compiles and flashes embedded firmware over WebSerial.
- **Open-Source Python SDK (`pip install atech`)**:
  - Built specifically for software engineers and AI coding assistants (**Claude Code**, **Cursor**, **Lovable**). Developers orchestrate physical hardware behaviors directly within Python scripts, supporting CLI compilation, real-time telemetry streaming, and automated serial flashing.
- **Virtual Hardware Simulation Engine (`esp32sim`)**:
  - Enables developers without physical hardware on hand to execute software emulation, testing sensor telemetry streams and state machine logic directly on a laptop.

---

## 3. Vision and Mission

### 3.1 Official Statements
- **Mission**:
  > *"To drastically lower the barrier to entry for building in the physical world and democratize hardware innovation for every creator, engineer, and student."*

- **Vision**:
  > *"To bring 'vibe-engineering' to hardware — making physical computing as fluid, rapid, and prompt-driven as generative software development, turning ideas into tangible smart devices in minutes instead of months."*

---

## 4. Category & Classification

- **Primary Category**: **Modular Hardware & Physical Prototyping Platform**
- **Secondary Categories**:
  - **AI-Driven Firmware Generation (Prompt-to-Firmware)**
  - **IoT & Edge Computing Platform**
  - **EdTech & Maker Infrastructure**

---

## 5. Role at Junction 2026 & Challenge Tracks Prediction

### 5.1 Hackathon Partner Positioning
Atech serves as the **Ultimate Game Changer for the Hardware Track and Physical Computing** at Junction 2026.

Historically, hardware projects represent the highest attrition rate at 48-hour hackathons:
- Software engineers often possess exceptional product vision but lack low-level embedded C/C++ knowledge or circuit debugging experience.
- Even veteran electrical engineering teams frequently suffer from loose breadboard wires, burned GPIO pins, or memory leaks deep into the competition night.

**Atech enables pure software developers and design students to assemble functional physical hardware and deploy working firmware within 10 minutes, dedicating the remaining 47 hours to high-value AI workflows, application logic, and user experience.**

### 5.2 Target Tracks & Challenge Proposals
1. **Hardware & Physical Computing Track**:
   - The primary development platform for assembling aesthetically refined, functionally complete smart hardware prototypes on site.
2. **Smart Living, Environment & Health Track**:
   - Rapidly engineer intelligent home environmental monitors, non-contact gestural health interfaces, or carbon footprint indicators using ambient sensor modules.
3. **Hardware-Meets-AI / Ambient Intelligence**:
   - The classic edge-to-cloud architecture: Atech hardware ingests physical telemetry (temperature, acoustic events, camera frames), streams data over Wi-Fi to **Aiven** Kafka/PostgreSQL, triggers inference on **Featherless** or **Modal** foundation models, and executes reactive physical responses (lighting, audio alerts, or servo kinetics).

---

### 5.3 Quickstart Guide for Hackers

```bash
# 1. Install official Atech Python SDK
pip install atech

# 2. Inspect module registry and hardware manifest via CLI or AI coding assistants
atech modules list
```

**Python Hardware Control & Cloud Integration Example**:
```python
# firmware_logic.py (or generated via Atech Web Studio)
from atech import Device, Screen, Sensor, Knob

# Initialize Atech ESP32-S3 core unit
device = Device()

# Declare modular port assignments (solderless snap-in ports)
screen = Screen(port=1)
temp_sensor = Sensor.temperature(port=2)
co2_sensor = Sensor.co2(port=3)
knob = Knob(port=4)

@device.on_loop(interval_ms=1000)
def check_environment():
    temp = temp_sensor.read()
    co2 = co2_sensor.read()
    
    # Real-time local display rendering
    screen.display_text(f"Temp: {temp}°C\nCO2: {co2} ppm")
    
    # If telemetry exceeds threshold, dispatch alert to cloud backend
    if co2 > 1000:
        device.wifi.post("https://your-modal-backend.modal.run/alert", json={"co2": co2})

device.run()
```

---

## 6. Official Links & Key Resources

- **Official Website**: [https://atech.dev](https://atech.dev)
- **Web Studio & Firmware Generator**: [https://atech.dev](https://atech.dev)
- **Atech Open-Source Firmware Repository**: [https://github.com/joakimeriksson/atech-firmware](https://github.com/joakimeriksson/atech-firmware)
- **Atech Python SDK on PyPI**: [https://pypi.org/project/atech/](https://pypi.org/project/atech/) (`pip install atech`)
- **AI Coding Assistant Workflows**: Native compatibility with Cursor, Claude Code, and Lovable for prompt-assisted embedded development.
