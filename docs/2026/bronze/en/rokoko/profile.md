# Rokoko (Rokoko Electronics ApS) — Junction 2026 Partner In-Depth Research Report

## 1. Company Overview

- **Full Company Name**: Rokoko Electronics ApS
- **Global Headquarters**: Copenhagen, Denmark, with engineering hubs and regional operations in San Francisco, Los Angeles, and Athens, Greece.
- **Founding Background**:
  - Founded in 2014 by **Jakob Balslev** (CEO), **Matias Søndergaard**, and **Anders Klok**.
  - The company originated from ideas conceived at the National Film School of Denmark. At the time, Hollywood-grade optical motion capture systems were prohibitively expensive (easily hundreds of thousands to millions of dollars), requiring dozens of specialized high-speed infrared cameras, reflective retro-markers, and dedicated light-controlled stages spanning hundreds of square meters. This made professional motion capture entirely out of reach for indie filmmakers, boutique game studios, and small-to-midsize animation teams.
  - The founding team set out to engineer a solution leveraging Micro-Electro-Mechanical Systems (MEMS) Inertial Measurement Units (IMUs) and precision sensor fusion filtering algorithms—effectively turning the entire motion capture studio into wearable apparel. This pioneered portable, wireless, markerless-ambient inertial motion capture accessible to both indie creators and enterprise studios.
- **Industry & Technical Standing**:
  - **Global Pioneer in Inertial Motion Capture and Creator Tools**: Rokoko fundamentally democratized motion capture technology. Over 50,000+ creators, game developers, VFX artists, indie animators, and AAA studios (including Netflix, Sony, Marvel, Warner Bros, CD Projekt Red, and Ubisoft), as well as world-renowned academic and research institutions, rely heavily on Rokoko systems.
  - **From MoCap Hardware to Full-Stack Spatial Computing & Physical AI**: Today, Rokoko has expanded far beyond its flagship Smartsuit Pro, establishing a comprehensive spatial computing ecosystem that spans micro-gesture Smartgloves, facial performance tracking (Face Capture), AI-driven browser-based markerless video tracking (Rokoko Vision), seamless real-time integration into major 3D engines (Unreal Engine, Unity, Blender), and biomimetic robotics teleoperation pipelines.

---

## 2. Core Products & Technical Architecture

Rokoko provides an end-to-end closed-loop toolchain encompassing hardware sensor acquisition, real-time data filtering and retargeting, and low-latency streaming to multi-platform software and 3D game engines.

### 2.1 Core Hardware Product Matrix
- **Smartsuit Pro II (Flagship Inertial Motion Capture Suit)**:
  - Houses 17 to 19 industrial-grade 9-DoF IMU sensors (integrating gyroscopes, accelerometers, and magnetometers) strategically mapped across critical human skeletal landmarks.
  - **Total Wireless Freedom**: Powered by standard USB power banks for multi-hour operational endurance; supports dual-band 2.4GHz / 5GHz Wi-Fi real-time wireless streaming as well as on-hub standalone offline storage (allowing actors to sprint, vault, or tumble outdoors untethered from a PC, syncing data with one click post-shoot).
  - **Rapid Calibration**: Requires only seconds in a standard "T-Pose" or "Straight Pose" to establish full-body biomechanical skeletal calibration.
- **Smartgloves (Biomechanical MoCap Gloves)**:
  - Purpose-built for intricate human hand and finger kinematics, integrating micro-magnetic and inertial sensor arrays across wrists, palms, and individual finger phalanges. Accurately tracks piano playing, fist clenching, subtle gesturing, and fine articulation, completely eliminating the labor-intensive process of frame-by-frame finger rigging.
- **Rokoko Coil Pro (High-Precision Global Positioning Base Station)**:
  - A revolutionary electromagnetic tracking anchor designed to counteract global positional drift inherent to pure inertial dead reckoning over extended, high-intensity locomotion, providing centimeter-level absolute world coordinates.
- **Face Capture (Real-Time Facial Performance Tracking)**:
  - Leverages iOS TrueDepth camera sensor arrays and ARKit's 52 standard facial blendshapes. Synchronizes seamlessly with body and glove capture to deliver unified "Body + Expression + Lip Sync" full-performance capture in real time.

### 2.2 Core Software & Algorithm Ecosystem
- **Rokoko Studio (Desktop Motion Capture Command Center)**:
  - Cross-platform workstation suite featuring multi-actor live capture, real-time 3D skeletal retargeting visualization, sensor diagnostics, advanced foot-locking contact detection algorithms (mitigating sliding/foot-slip), and multi-format export pipelines (FBX, BVH, CSV).
- **Rokoko Vision (Browser-Based AI Markerless Motion Capture)**:
  - Requires zero wearable hardware: using a standard monocular webcam or uploading an MP4 video clip recorded on a smartphone, advanced computer vision neural networks extract high-fidelity 3D human skeletal kinematics directly in the cloud/browser.
- **Motion Library (Curated MoCap Asset Marketplace)**:
  - Deeply integrated into Studio and Unreal/Unity, offering a commercial marketplace of tens of thousands of motion assets performed by Hollywood-grade stunt actors, covering combat, parkour, dance, and everyday locomotion.

### 2.3 Developer Integration & Real-Time Streaming Toolchain (SDK & Protocols)
- **Real-Time Game Engine Plugins (Live Link Integrations)**:
  - **Unreal Engine Plugin**: Native support for Unreal Live Link, instantly streaming and retargeting live motion frames onto Epic Games **MetaHuman** high-fidelity digital humans, supporting instant virtual production recording via Take Recorder.
  - **Unity Plugin**: Powered by the open-source `rokoko-studio-live-unity` package and `StudioManager` scripts, listening on local network UDP sockets to dynamically drive Unity Animator rigs and humanoid avatars.
  - **Blender / Maya / Houdini / Cinema 4D Plugins**: Streamlines workflow for 3D animators with one-click retargeting, baking, and timeline keyframe editing.
- **Rokoko Command API (Remote Automation Protocol)**:
  - TCP/IP JSON command interface enabling third-party applications or custom game logic to remotely orchestrate Rokoko Studio:
    ```json
    { "command": "StartRecording", "filename": "Scene_01_Take_03" }
    ```
- **Rokoko Device SDK (Low-Level Hardware Interfacing)**:
  - Empowers engineers to bypass Rokoko Studio entirely and interface directly with Smartsuit Pro hardware over USB or raw wireless sockets:
    - **RCSP (Rokoko Command Server Protocol)**: Manages device discovery, battery state, pairing, and hardware button triggers.
    - **RGMP (Rokoko General Motion Protocol)**: Ultra-low-latency binary protocol delivering raw, uncompressed sensor quaternions, angular velocities, and linear accelerations. Widely adopted across robotics labs, reinforcement learning research, and human-in-the-loop teleoperation systems.

---

## 3. Vision and Mission

### 3.1 Official Mission
> *"To make professional motion capture and character animation accessible, intuitive, and affordable for all creators — from indie visionaries to world-class studios."*

### 3.2 Official Vision
> *"To democratize human motion data and spatial computing — transforming how humans interact with digital worlds, virtual characters, robotics, and physical AI."*

### 3.3 Core Design Philosophy
- **Invisible Tech**: Technology must stay out of the creator's way. No tangled umbilical cables or complex optical darkroom setups—put on the suit and perform naturally.
- **Real-Time Synchronicity**: Sub-millisecond latency data transport ensures that every nuance of physical movement translates immediately into digital worlds and virtual engines.
- **Bridging the Physical & Virtual**: Transforming biological kinetic energy from the physical world into the primary input modality for spatial computing, digital twins, and embodied robotics.

---

## 4. Category & Classification

- **Primary Category**: Motion Capture & Spatial Computing Platform
- **Secondary Categories**:
  - 3D Character Animation & Virtual Production
  - XR & Interactive Game Development
  - Physical AI, Robotics & Human Teleoperation
  - Biomechanics & Human Movement Analytics

---

## 5. Role at Junction 2026 & Challenge Tracks Prediction

### 5.1 Hackathon Partner Positioning
Rokoko serves as the challenge partner and specialized motion capture hardware provider for the **Spatial Computing, Gaming & Interactive 3D / Creative Tech** track at Junction 2026.
On-site, Rokoko typically supplies multiple **Smartsuit Pro II suits, Smartgloves, and facial capture mounts**, hosting an interactive MoCap Demo Arena. Participating teams can wear the suits, capture bespoke animation data, or subscribe to live UDP stream broadcasts over the local network to drive games, AR/VR experiences, or embodied AI control loops.

### 5.2 Challenge Tracks Prediction & Potential Prompts
1. **Real-Time Spatial Interactions & Full-Body XR Gaming**:
   - *Challenge Concept*: Moving beyond traditional keyboards, mice, or handheld VR controllers—how can full-body motion capture and nuanced finger gestures enable physics-based combat, spellcasting, parkour, or martial arts gaming experiences?
   - *Solution Approach*: Integrate Rokoko Studio Live Link in Unity/Unreal, binding live skeletal tracking to rigid-body physics characters for authentic impact physics, dodging, and spatial mechanics.
2. **Physical AI, Imitation Learning & Robot Teleoperation**:
   - *Challenge Concept*: Humanoid robots and dexterous manipulators require massive amounts of high-fidelity human kinematic demonstrations. How can Smartsuit Pro and Smartgloves be leveraged for low-latency teleoperation of simulated robots (e.g., in Isaac Gym or MuJoCo) and the generation of imitation learning datasets?
   - *Solution Approach*: Use the Rokoko Device SDK or UDP data feed to stream joint quaternions, mapping them to inverse kinematics (IK) targets on humanoid bipeds or robotic end-effectors for real-time mirroring and training data collection.
3. **VTubers, Digital Humans & Live Generative Entertainment**:
   - *Challenge Concept*: Combine generative AI voice synthesis, LLM-driven behavioral intelligence, and human-in-the-loop performance capture to create next-generation interactive live performances or immersive interactive theater.
   - *Solution Approach*: Drive Unreal MetaHumans with Rokoko MoCap, pairing local speech-to-text (Whisper) with real-time LLM narrative steering for dynamic live audience interactions.
4. **Digital Health, Sports Biomechanics & Ergonomics**:
   - *Challenge Concept*: Utilize high-frequency joint angular velocity and acceleration telemetry to assess patient rehabilitation progress, athletic technique standardization, or ergonomic injury risks in industrial workplace environments.
   - *Solution Approach*: Quantify spinal curvature, knee joint loading, and gait symmetry, feeding real-time 3D health dashboards and automated injury warning alerts.

### 5.3 Quickstart Guide for Hackathon Teams
- **Step 1 (Enable Live Stream)**: In Rokoko Studio, navigate to **Live Stream** settings, specify the target IP (e.g., `127.0.0.1`) and port (default `14043`), selecting JSON or Rokoko Studio Data protocol.
- **Step 2 (Rapid Python Stream Ingestion)**:
  ```python
  import socket
  import json

  # Listen to UDP broadcast packets from Rokoko Studio
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(("0.0.0.0", 14043))

  print("Listening for Rokoko motion frames...")
  while True:
      data, addr = sock.recvfrom(65535)
      mocap_frame = json.loads(data.decode("utf-8"))
      # Extract skeletal coordinates and joint orientation quaternions
      for body in mocap_frame.get("scene", {}).get("actors", []):
          head_pos = body["body"]["head"]["position"]
          print(f"Actor [{body['name']}] Head Position: {head_pos}")
  ```
- **Step 3 (Rapid Unity Integration)**:
  - Import the `rokoko-studio-live-unity` package.
  - Drop the `StudioManager` prefab into your scene and enable "Auto Create Actors".
  - Move in the suit on-site, and the 3D humanoid avatar in Unity will mirror the movement 1:1 in real time!

---

## 6. Official Links & Key Resources

- **Rokoko Official Website**: [https://rokoko.com](https://rokoko.com)
- **Rokoko Knowledge Base & Support Center**: [https://support.rokoko.com](https://support.rokoko.com)
- **Rokoko Studio Download**: [https://rokoko.com/products/studio](https://rokoko.com/products/studio)
- **Rokoko Vision (Web AI Video MoCap)**: [https://rokoko.com/products/vision](https://rokoko.com/products/vision)
- **Unity Plugin GitHub Repository**: [https://github.com/rokoko/rokoko-studio-live-unity](https://github.com/rokoko/rokoko-studio-live-unity)
- **Unreal Engine Plugin GitHub Repository**: [https://github.com/rokoko/rokoko-studio-live-unreal-engine](https://github.com/rokoko/rokoko-studio-live-unreal-engine)
- **Rokoko Developer Command API & SDK Documentation**: [https://support.rokoko.com/hc/en-us/articles/4410427618577-Rokoko-Studio-Command-API](https://support.rokoko.com/hc/en-us/articles/4410427618577-Rokoko-Studio-Command-API)
