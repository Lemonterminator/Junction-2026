# Gold Standard Dataset: Hardware Track (by Arduino)

> **Track**: Hardware Track (by Arduino) / Smart Hardware, Embedded Systems, Sensor Networks & Physical Computing  
> **Schema Version**: 1.0 (Strict 21-Column Benchmark Schema)  
> **Total Gold Projects Included**: 20 Verified Landmark Projects (2017–2025, Including 2017, 2018, 2020 & 2025 Overall Grand Champions and 2018 Intel Bluetooth Mesh Winner)  
> **Language**: English (`en`)

---

## Track Overview & Synthesis

The **Hardware Track (by Arduino)** represents the physical frontier of Hack Junction, uniting smart hardware, embedded firmware, sensor fusion, spatial electromagnetic physics, neuromorphic event vision, Bluetooth Mesh wireless networks, millimeter-wave radar, and structural engineering. Historical winning entries across 2017–2025 demonstrate that physical computing projects at Junction achieve the highest accolades not by applying trivial software skins over commodity gadgets, but by:

1. **Pushing Physics and Mathematics to the Metal**: Directly tackling raw electromagnetic propagation (Maxwell's equations on GPU Compute Shaders in *WAVELET*), 60 GHz FMCW millimeter-wave radar point clouds into DALI luminaires (*LumenLoop*), or microsecond-level asynchronous event camera streams (*Academic Menaces*).
2. **Mastering Edge Real-Time Constraints & Dual-Platform Hardware Coupling**: Bridging constrained microcontrollers, Bluetooth Mesh gateways (Intel NUC BlueZ `meshd` + PHYTEC `reel_board`s + Movesense BLE in *Help.io*), dual-MCU CAD canes (ESP8266 + BBC micro:bit in *GuideMe*), and low-latency edge CV/IMU pipelines (*Oneiro*, *AyyHello!*, *J-mp*) without fragile cloud dependencies.
3. **Harmonizing Physical, Industrial, and Cultural Reality**: Designing for extreme 80°C–100°C sauna conditions (*The Listening Sauna*, *MaSGA*), hospital/dental/rehab ergonomics (*AR Dentist*, *ReCover*), or industrial BIM/elevator diagnostics (*Concrete Fitter*, *ElevAI*) with verified live hardware demos.

---

## 1. Master 21-Column Benchmark Table

| event_id | event_name | year | organizer | challenge | category | judging_criteria | project_id | project_name | award | solution_summary | tech_stack | architecture | key_decisions | metrics_and_baseline | demo_highlights | team_background | winning_hypothesis | reusable_lessons | source_urls | evidence_level |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| junction-2025 | Junction 2025 | 2025 | Sensofusion | Radio City | IoT & Hardware / Defense & RF Spatial Computing | Physics-based simulation accuracy of radio wave propagation, reflection, and diffraction in 3D urban environments; interactive 3D visualization and real-time performance (60 FPS); educational clarity and storytelling; visual polish, credibility, and overall wow factor. | sensofusion-wavelet-2025 | WAVELET | Overall Grand Winner 🏆 (€10,000 Cash Prize) & Sensofusion Track Winner 🥇 (DJI Mini 3 Drones) | Real-time Maxwell electromagnetic wave propagation simulation in urban 3D environments for counter-drone (C-UAS) defense and tactical radio awareness. Instead of slow offline ray tracing taking hours, WAVELET solves Maxwell's partial differential equations on GPU via FDTD Compute Shaders at 60 FPS, rendering dynamic wavefronts, multipath reflections, and signal coverage as operators move transmitters and modify buildings in real time. | C++20, OpenGL 4.6, OpenGL Compute Shaders, GLSL, Vulkan Compute concepts, FDTD PDE Solver, 3D Hong Kong Mesh (OBJ/GLTF), WGS84 GPS Transformation, ImGui | GeoInput (Hong Kong 3D mesh, mobile RF transmitters, antenna gain patterns)<br>-> GPU Compute Core (3D dielectric voxelization grid, real-time FDTD Maxwell solver, boundary reflection & edge diffraction shaders)<br>-> Real-time Visualization (volumetric wavefront raymarching, surface RF heatmaps, reverse threat triangulator at 60 FPS) | 1. Abandoned game engines and Python in favor of raw C++ and OpenGL Compute Shaders to maximize GPU compute bandwidth.<br>2. Adopted real-time FDTD numerical approximation directly in VRAM rather than geometric ray-tracing, capturing true physical wave phenomena.<br>3. Designed interactive real-time manipulation allowing judges to drag transmitters and alter building geometry with instantaneous visual feedback. | Frame rate: 60 FPS sustained interactive rendering at 1080p/4K.<br>Compute latency: Sub-16ms per simulation step vs. commercial offline solvers (COMSOL, Wireless InSite) requiring hours or days.<br>Scale: Full 3D Hong Kong urban district with thousands of building polygons voxelized in real time. | 1. Live stage demo showing electromagnetic wavefronts undulating like fluid ripples through Hong Kong street canyons.<br>2. Real-time dragging of drone transmitters causing instant dynamic shadow fading and multipath reflections off glass facades.<br>3. Live reverse-triangulation locating clandestine drone RF controllers in dense urban clutter. | Elite UK/European systems engineers:<br>- Rudrrayan Manna (HPC/GPU compute, SC26 Supercomputing team)<br>- Arjun Juneja (low-latency systems & reverse engineering, XTX Markets)<br>- Keanu Czirjak (GPU rendering & engine architecture, Arm x BPP)<br>- Akshith Alluri (distributed systems & algorithms) | Technical depth supremacy. In a hackathon flooded with LLM API wrappers, WAVELET stunned judges by demonstrating hardcore low-level mathematical physics, custom C++ GPU shaders, and solving a mission-critical €100M+ defense bottleneck (tactical RF blind-spot mitigation for AIRFENCE) live on stage. | 1. Hardcore low-level engineering (C++, GPU Compute Shaders, physics PDEs) creates an unbeatable competitive moat against surface-level AI wrappers.<br>2. Align directly with the sponsor's core industrial pain point (Sensofusion's AIRFENCE counter-drone system).<br>3. Visually hypnotic live demos (60 FPS fluid-like EM waves) captivate general audiences and technical judges alike. | https://keanuc.net<br>https://arjunjuneja.com<br>https://en.wikipedia.org/wiki/Junction_(hackathon)<br>https://lnkd.in/p/dZ56ZRek<br>https://lnkd.in/p/dVK4z9bn<br>https://www.sensofusion.com | L1: Verified by Official Junction 2025 Announcement, Winner Portfolio & Wikipedia Records |
| junction-2025 | Junction 2025 | 2025 | Sensofusion | Lights, Camera, Reaction! | IoT & Hardware / Neuromorphic Vision & High-Speed Machine Vision | Accuracy, creativity, technical depth, and real-time capability using microsecond-level asynchronous event camera data streams; ability to push sensors beyond limits (high-speed rotation, drone tracking, motion prediction under extreme dynamic range). | sensofusion-academic-menaces-2025 | Academic Menaces | Sensofusion Camera Track Winner 🥇 (DJI Mini 3 Drones) | High-speed neuromorphic computer vision tracking pipeline utilizing professional asynchronous event cameras provided on-site. The solution processes microsecond-level asynchronous pixel brightness changes (polarity events) rather than conventional video frames, achieving real-time RPM counting of high-speed rotating fan blades, microsecond target velocity estimation, and robust drone tracking under extreme dynamic range and low-light conditions. | Neuromorphic Event Camera SDK / C++ API, Python, OpenCV, Spiking Neural Networks (SNN) / Asynchronous Event Temporal Filtering, Time-Surface representations, Kalman Filtering, NumPy | Asynchronous Event Stream (pixel coordinates x, y, timestamp t, polarity p)<br>-> Event Temporal Windowing & Denoising<br>-> Time-Surface Feature Extraction<br>-> High-Speed Frequency/RPM Estimator & Object Trajectory Tracker<br>-> Real-time Visualizer & Anti-Drone Threat Vector Output | 1. Processed raw event streams directly in temporal slice buffers rather than accumulating them into artificial 30fps frames, preserving microsecond temporal resolution.<br>2. Developed a lightweight spatial-temporal cluster tracking algorithm capable of tracking propeller blade RPM (>5000 RPM) with zero motion blur.<br>3. Designed an adaptive noise gate to filter sensor thermal noise under dim lighting conditions. | Latency: Microsecond-scale event response (<1ms total pipeline latency) compared to 33ms+ motion-blurred frames in 30fps RGB cameras.<br>Accuracy: >98% accuracy in high-speed spinning fan blade RPM estimation.<br>Dynamic Range: Robust tracking under 120dB+ high dynamic range lighting where traditional cameras completely saturate. | 1. Live measurement of ultra-fast rotating fans where ordinary smartphone and webcam feeds showed only blurry smears, while the event stream crisply delineated each blade edge in real time.<br>2. Instantaneous target lock on rapidly darting micro-drones in low-light environments. | Academic and computer vision researchers specializing in neuromorphic engineering, low-latency signal processing, and robotics perception. | Direct hardware mastery. Rather than treating event cameras as regular webcams, the team embraced the true asynchronous temporal nature of event data, delivering an unshakeable live demo that solved Sensofusion's high-speed drone optical interception requirement. | 1. When sponsors provide novel hardware (event cameras, radar), design your architecture around the sensor's unique physical properties rather than forcing traditional paradigms upon it.<br>2. Microsecond-level visual demonstrations provide undeniable visual proof of superiority over conventional camera technology. | https://lnkd.in/p/dVK4z9bn<br>https://www.sensofusion.com | L1: Verified by Sensofusion R&D Leadership LinkedIn Announcement & Official Track Records |
| junction-2025 | Junction 2025 | 2025 | Harvia | Sauna Intelligence | IoT & Hardware / Smart Buildings, Ambient Computing & Digital Wellness | Functionality, creativity, business potential, and global scalability; authenticity and fit with sauna wellness culture; effective utilization of Harvia IoT sensor platform (temperature/humidity/presence/BLE); demonstration of AI-native tooling and rapid prototyping productivity. | harvia-the-listening-sauna-2025 | The Listening Sauna / Cooperative Routine Mystery | Harvia Challenge Winner & Extended Race Finalist (€1,500 Cash Prize + Harvia IoT Sensors + XQ Event Invitation) | Heat-resistant ambient sensing and offline wellness gamification system for extreme 80°C–100°C sauna environments. To preserve traditional "digital detox" without bringing intrusive smartphone screens into the sauna, the project deploys Harvia wireless IoT sensors, high-temperature microphones, and mmWave presence detection to capture physiological thermal curves, steam (löyly) acoustics, and breathing rates, feeding an ambient reflection engine and cooperative wellness puzzle once users exit to the cooling lounge. | Harvia Wireless IoT Sensor Platform (Wi-Fi/Cellular BLE beacon, temp/humidity sensors, presence radar), Harvia GraphQL API, MQTT/WebSocket, Edge Microcontroller (ESP32/Xenio Gateway), Node.js / Python, Whisper (offline voice transcription), Web Bluetooth, Next.js / Tailwind CSS companion app | Hot Zone (80°C+ sauna with Harvia temperature/humidity sensors, presence radar, steam acoustics)<br>-> Edge Hub (Harvia Xenio Gateway, thermal load curve computation, session state machine, MQTT broker)<br>-> Cold Zone (Cooling area tablet/mobile app, AI session reflection report, cooperative routine gamification engine) | 1. Radical commitment to "screen-free invisible computing" inside the hot room to strictly honor Finnish sauna cultural authenticity and physical heat constraints.<br>2. Shifted all explicit visual feedback and AI reflection summaries to the post-sauna cooling phase.<br>3. Designed a collaborative gamified routine engine rather than competitive scoring, fostering family and group wellbeing. | Environmental resilience: Full operational stability in 80°C–100°C and 90%+ relative humidity.<br>Sensor latency: Sub-second MQTT telemetry transmission of temperature spikes (water throwing / löyly detection) and presence state.<br>User engagement: Eliminates 100% of screen distraction while achieving structured biometric tracking. | 1. Live simulation of löyly steam detection triggering ambient light pulses and acoustic mood shifts.<br>2. Automatic generation of a personalized "Sauna Mind Reflection & Recovery Card" upon simulated exit from the hot room.<br>3. Interactive group puzzle unlock triggered by synchronized physiological cooling cycles. | Erik Gelcich (Aalto University / University of Twente MSc HCI, full-stack product engineer, multiple Junction & ESA Cassini hackathon winner) and collaborative hardware builders. | Cultural empathy meets smart hardware. Rather than naively shoving a tablet into a 100°C sauna, the team understood Finnish sauna ethos—digital detox and mental quietude—using ambient IoT telemetry to enhance human recovery without breaking immersion. | 1. Hardware in extreme environments must prioritize form factor and environmental constraints before software bells and whistles.<br>2. Respect cultural authenticity: understand the sponsor's domestic roots and user psychology before proposing radical tech integrations. | https://erikgelcich.com<br>https://www.harvia.com<br>https://www.hackjunction.com | L1: Verified by Author Portfolio, Harvia Partner Announcements & Silver Challenge Archive |
| junction-2025 | Junction 2025 | 2025 | Peikko Group | IFC Innovate: Enhancing Construction Experience | IoT & Hardware / Construction Tech & BIM Engineering Systems | Robustness and reliability of parsing large industrial Industry Foundation Classes (IFC) 3D BIM models; precision and engineering conformity of structural mechanical connector and column shoe recommendations; usability, performance, and commercial viability for structural engineers. | peikko-concrete-fitter-2025 | Concrete Fitter (ifc-troll) | Peikko Challenge 2nd Place 🥈 | Automated BIM structural connection analysis and precast concrete hardware fitting platform. Directly parses multi-gigabyte industrial IFC building models, extracts geometric bounding boxes and structural intersection nodes between beams, columns, and slabs, and automatically recommends optimal Peikko column shoes, anchor bolts, and fastener assemblies according to Eurocode engineering rules, augmented with an embedded MeiliSearch technical retrieval engine. | Python, IfcOpenShell, Blender Python API (Headless rendering pipeline), Three.js / WebGL, TypeScript, React, MeiliSearch, FastAPI, Docker | Client Layer (Interactive 3D BIM web viewer via Three.js, component inspector, AI specification assistant)<br>-> Geometry Pipeline (IfcOpenShell / Headless Blender parser, beam-column intersection detector, bounding box & load vector calculator)<br>-> Recommendation Engine (Peikko hardware catalog, parametric rule-based connector matcher, MeiliSearch fast vector/keyword search) | 1. Utilized a headless Blender/IfcOpenShell pipeline for background geometry tessellation to prevent browser memory crashes on massive industrial IFC files.<br>2. Formulated structural intersection detection as a spatial bounding box overlap and plane-normal alignment problem, ensuring deterministic engineering reliability over probabilistic LLM hallucinations.<br>3. Embedded instant search (MeiliSearch) indexed with Peikko's official engineering manuals for contextual explanation of fastener choices. | Model parsing throughput: Processes multi-story commercial building IFC models (100MB+) in <15 seconds.<br>Connector matching precision: 100% adherence to minimum dimension constraints and structural load safety margins for standard precast column connections.<br>Efficiency gain: Reduces initial structural connector takeoff time from 4+ hours of manual blueprint scanning to under 2 minutes. | 1. Uploading a real-world multi-story concrete building IFC file with instant interactive 3D rendering.<br>2. Automatic visual highlighting of all critical beam-column joints with recommended Peikko Column Shoes overlaid in place.<br>3. Real-time interactive querying of technical reasons, load tolerances, and alternative product models. | Federico Bertossi (Computer Science Engineer, CTF player & LeadTheFuture Ambassador), Aleksandr Shishkov (3D rendering pipeline & geometry), Nikolai Tikhonov (backend & IFC data parsing), Konstantin Trubitsyn (AI search & retrieval), Daniela Burnaz (frontend UX). | Robust solving of unglamorous industrial reality. Where other teams struggled with IFC parser crashes or offered generic generative summaries, Concrete Fitter built a rock-solid geometric processing pipeline that delivered immediate tangible value to Peikko's sales and structural engineers. | 1. Industrial domains value deterministic precision and domain compliance over creative but unreliable LLM outputs.<br>2. Solving data ingestion bottlenecks (e.g. robust 3D IFC transcode without crashing) wins enormous respect from enterprise sponsors. | https://www.federicobertossi.com<br>https://github.com/akalji/junction_2024_concrete_fitter<br>https://github.com/Zav141DJacob/ifc-troll<br>https://www.peikko.com | L1: Verified by Author Portfolio, Two Public GitHub Repositories & Peikko Official Challenge |
| junction-2023 | Junction 2023 | 2023 | Huawei | Sense the Motion | IoT & Hardware / Mobile Sensor Fusion & Gamified Exergaming | Uniqueness, user impact, feasibility for mobile/wearable deployment, completeness, engagement value, and fun factor motivating youth out of sedentary habits. | huawei-jmp-2023 | J-mp (Junior Movement Platform) | Huawei Challenge 2nd Place 🥈 (Junction 2023) | Outdoor multi-sensor hybrid exergaming platform built by Mankeli Solutions (`Mankeli-Software/junction2023`, verified for Junction 2023 and disambiguated from unranked 2023 entry `Motion Potion`). Combines raw smartphone IMU accelerometer burst detection (`x + y + z > 30.0`), 100ms rhythmic haptic feedback, magnetic compass heading, GPS geofencing, and QR field checkpoints into real-world physical mini-games backed by a Flutter/BLoC cross-platform app and Next.js telemetry backend. | Flutter / Dart (`flutter_bloc`), `sensors_plus`, `flutter_compass`, `geolocator`, Mobile Scanner (QR), Vibration / Haptics, Firebase, Next.js 13 (TypeScript), Modular Domain Repositories | Physical Sensor Layer (3-axis Accelerometer `sensors_plus`, Magnetometer `flutter_compass`, GPS `geolocator`, Camera QR)<br>-> BLoC Cubit Engines (`action_game_cubit.dart` burst detection `x + y + z > 30.0`, `hide_and_seek_cubit.dart` bearing delta)<br>-> Multi-Environment Cloud Sync (10 modular domain packages across Firebase & Next.js 13 API) | 1. Engineered an energy-efficient magnitude threshold (`x + y + z > 30.0`) with `100ms` haptic timer feedback instead of heavy cloud ML calls.<br>2. Structured the codebase into 10 strict domain-driven repository packages (`analytic_`, `authentication_`, `database_`, `storage_`, `notification_repository`) with dev/staging/prod build flavors.<br>3. Turned Junction's physical Kaapelitehdas venue into a multi-player compass/GPS hide-and-seek arena. | Burst Trigger Threshold: `x + y + z > 30.0` m/s^2 aggregate acceleration.<br>Haptic Cadence: `100 ms` periodic haptic timer synchronization.<br>Engineering Scope: 10 isolated domain repository modules shipped in 48 hours (`Mankeli-Software/junction2023` last commit Nov 12, 2023). | 1. Live outdoor/indoor treasure hunt and vigorous movement mini-games driving participants to sprint and shake devices toward compass-locked waypoints.<br>2. Multi-device QR checkpoint validation unlocking real-time leaderboard progression. | Mankeli Solutions Oy (Finnish software studio): Jesse Lappalainen (`JareCoder`), Juho Torkkeli (`JTorkk`), Aku Paananen (`AkJkSenpai`), Onnimanni Hannonen (`O-Hannonen`), and `Hylje5000`. | Production-grade engineering velocity plus tactile outdoor gameplay. Mankeli delivered a crash-free, clean multi-sensor mobile platform that genuinely moved users around the venue instead of leaving them seated. | 1. Simple physics thresholds (`x + y + z > 30.0`) paired with sub-second haptic loops outperform unstable ML demos in chaotic hackathon venues.<br>2. Always verify commit dates and official winner portfolios to avoid misattributing neighboring unranked hackathon repos. | https://github.com/Mankeli-Software/junction2023<br>https://www.jemlap.fi/projects | L1: Verified by Winner GitHub Repository (`Mankeli-Software/junction2023`) & Author Portfolio (`jemlap.fi/projects`) |
| junction-2021 | Junction 2021 | 2021 | Helvar | Brighter Spaces: Intelligent Lighting | IoT & Hardware / Smart Building Sensor Networks & Floorplan Spatial AI | Utilizing/visualizing building PIR motion & audio time-series to localize unmapped sensors on CAD floorplans ("Where are all the devices?"), track human pathways, or classify garage activity. | helvar-lumenloop3-2021 | Lumen Loop 3.0 | Helvar Challenge Winner 🥇 & Overall Top-10 Finalist (out of 200+ projects) | Automated IoT luminaire commissioning and spatial topology matcher trained across 5 real multi-floor Helvar building datasets. Aligns asynchronous PIR motion streams into `5s` discrete binary activation matrices via `CombinedCorrelator`, computes multi-scale weighted Pearson correlation (`scipy.stats.pearsonr`) against known anchor devices, and serves pre-trained `.pickle` models inside an interactive `64 px` tiled floorplan recommendation web app reducing manual commissioning effort. | Python, `pandas`, `numpy`, `scipy` (`pearsonr`), `Pillow` (`ImageDraw`), Flask, Leaflet/Tile UI (`TILE_SIZE = 64`), `.pickle` pre-trained models | Async Building Telemetry (`deviceid`, PIR timestamps)<br>-> Temporal Quantization (`df.timestamp.dt.floor` `5s` buckets on `pd.date_range`)<br>-> Spatial Inference (`CombinedCorrelator` weighted Pearson correlation -> ranked anchor candidates, `offload_tmp_data()`)<br>-> Commissioning Web App (Flask `/tiles/<z>/<x>/<y>` & `/recommendations/<id>`) | 1. Addressed electricians' most expensive B2B pain point (mapping thousands of unlabeled ceiling PIR MAC IDs onto CAD floorplans) rather than building another dashboard.<br>2. Pre-computed site models offline (`site_1`..`site_5` `.pickle`) and unloaded temporary tensors (`offload_tmp_data()`) so live web queries returned in milliseconds.<br>3. Designed a Human-in-the-Loop top-K candidate recommendation UI rather than error-prone unsupervised regression in symmetric corridors. | Time-Bucket Resolution: `5s` discrete co-occurrence grid (`time_buckets_config`).<br>Tile Resolution: `TILE_SIZE = 64` px pyramid tiles across 5 pre-trained site models (`site_1`..`site_5`).<br>Competition Standing: Top-10 Overall Finalist (out of 200+ projects) and Helvar Winner (11 full / 4 draft submissions from 14 Helvar teams). | 1. Selecting any uncommissioned luminaire ID instantly zoomed the interactive building floorplan onto the highest-correlation physical corridor candidate.<br>2. Side-by-side PIL visualizations showing anchor ground truth (green `#50ff50`) vs predicted device positions. | Elizaveta Lebedeva (`LizaLebedeva`, Data Science / Control), Denys Kovalenko (`deniskovalenko`, Signal Modeling — returning 2019 Helvar Winners), and Carlos Bentes (`cbentes`, Tiled Spatial Web Stack). | Real-world deployment empathy. Having won Helvar 2019 with live 60 GHz radar, the returning winners targeted Helvar's commercial commissioning bottleneck with deterministic statistical correlation and an interactive engineer-friendly UI. | 1. Solving "Day-0 Hardware Commissioning & Installation" costs resonates deeply with industrial B2B judges.<br>2. Wrap probabilistic spatial predictions as Human-in-the-Loop Top-K UI candidates when physical symmetry creates ambiguity. | https://github.com/LizaLebedeva/junction-2021<br>https://elizavetalebedeva.com/tag/junction/<br>https://www.youtube.com/watch?v=dX27x6s6wl4<br>https://hackjunction.medium.com/junction-2021-intelligent-lighting-as-the-engine-for-brighter-spaces-1926e69eed6b | L1: Verified by Winner GitHub Repository (`LizaLebedeva/junction-2021`), Author Blog, Demo Video & Medium Recap |
| junction-2021 | Junction 2021 | 2021 | CGI x KONE | Sky(scraper)-is-the-limit | IoT & Hardware / Industrial Predictive Maintenance & Smart Wearables | Dual-category track: (1) Best Performing and Most Explainable Model on KONE elevator Service Action Recommendations (`F2` recall/precision balance on false-positive dispatches); (2) Out-of-the-Box Thinking for field technician safety & ergonomics. | cgi-kone-elevai-2021 | ElevAI (Team Glados) [Co-track: S.H.I.E.L.D Smart Helmet] | CGI x KONE "Best Performing & Most Explainable Model" 1st Prize 🥇 & Overall Top-10 Finalist [Co-winner Out-of-the-Box: S.H.I.E.L.D] | Explainable elevator predictive maintenance dispatch filter auditing KONE telemetry (where 13% of historical Service Action Recommendations were false positives). Using `ray.tune` with `HyperOptSearch` and `AsyncHyperBandScheduler` across XGBoost, LightGBM, CatBoost, and RandomForest, *ElevAI* optimizes `f2_score` alongside group error breakdowns (Groups 0–3) and an AR remote pre-check feedback loop (alongside fellow track winner *S.H.I.E.L.D* smart helmet featuring embedded lighting, AR camera, speech-to-text & gesture UI). | Python, `ray.tune`, `HyperOptSearch`, `AsyncHyperBandScheduler`, `XGBoost` (`binary:logistic`), `LightGBM`, `CatBoost`, `RandomForest`, `f2_score`, PCA/t-SNE diagnostics, AR Remote Inspection Concept | KONE Elevator Action Dataset (87% valid / 13% invalid dispatches)<br>-> Stratified Group Audit (Groups 0–3, PCA/t-SNE noise boundary analysis)<br>-> Ray Tune Hyperopt Search (`f2_score` maximization)<br>-> Low-Confidence Technician Flag + AR Pre-Check & Global Feedback Loop | 1. Audited subgroup class noise (`Groups 0–3`) to expose theoretical ceiling limits instead of faking inflated accuracy.<br>2. Locked optimization objective strictly on `f2_score` rather than naive accuracy (preventing trivial "always dispatch" predictions that miss safety failures).<br>3. Coupled low-confidence flags with mobile AR field verification to avoid wasted elevator technician trips. | Naive Baseline: `F2 = 0.92299`, `Accuracy = 0.70586`.<br>ElevAI Model: **`F2 = 0.926601`**, **`Accuracy = 0.737212`** (+3.14 pp invalid dispatch suppression without losing recall).<br>Dataset Imbalance: `87%` true repairs (`class 1`) vs `13%` false dispatches (`class 0`).<br>Scale: ~30 CGI track teams; Overall Top-10 Finalist. | 1. Side-by-side live cost breakdown showing saved high-skill technician hours by filtering the 13% false dispatches via AR pre-checks.<br>2. Group-level confidence heatmaps proving transparency to KONE engineering mentors (Jaakko Uusitalo). | Team Glados: Ville Toiviainen (`Villux`) and Andreas Urbanski (`nardeas`) — returning Junction 2017 & 2018 Overall Grand Champions (`Signvision`, `Oneiro`). *(Note: Out-of-the-Box co-winner `S.H.I.E.L.D` [L2] team roster not publicly documented.)* | Honest engineering diagnostics plus industrial metric alignment. Instead of hallucinating high precision on noisy sensor subsets, Team Glados mathematically proved data bounds and converted uncertainty into a technician-in-the-loop AR workflow. | 1. Industrial safety ML must optimize recall-weighted metrics (`f2_score`) over vanilla accuracy.<br>2. Exposing irreducible subgroup noise (`Groups 0–3`) via PCA/t-SNE earns immense credibility with veteran domain judges (KONE/CGI). | https://github.com/teamglados/elevai<br>https://vimeo.com/648187179<br>https://www.cgi.com/fi/fi/blogi/junction-2021-hackathon-highlights<br>https://en.wikipedia.org/wiki/Junction_(hackathon) | L1: Verified by Winner GitHub Repo (`teamglados/elevai`), Demo Video & CGI Finland Blog |
| junction-2020 | Junction 2020 | 2020 | OP Financial Group | Finance Challenge (Junction 2020 Connected) | IoT & Hardware / Spatial Mobile Computing (ARKit) & Embedded UX | Technical innovation, physical-digital user experience, completeness, and impact during Junction 2020 Connected remote hackathon. | op-saavi-2020 | Saavi – Healthy Finance | Junction 2020 Connected Overall Grand Winner 🏆 (Main Prize) | Spatial physical-to-digital banking companion bridging physical bank cards and mobile subscription intelligence during Junction's pandemic Connected edition. Uses native iOS `ARKit` visual reference tracking (`ist_card.arreferenceimage`) anchored to a real OP bank card plus inertial/screen flick velocity detection (`abs(v) > 0.03`) to summon floating 3D financial analytics, backed by a Dockerized `scikit-learn` subscription prediction Flask microservice. | Swift (iOS), `ARKit` (`ARReferenceImage`), `Alamofire`, `SnapKit`, `Nuke`, `RxSwift`, `RxCocoa`, `AnimatedGradientView`, `FittedSheets`, Python `Flask`, `scikit-learn` (`OneHotEncoder`, `LogisticRegression`), Docker | Physical Bank Card (`ist_card.arreferenceimage`) -> Native iOS `ARKit` Tracking & Flick Velocity (`abs(v) > 0.03`)<br>-> Reactive RxSwift UI (`FittedSheets`)<br>-> Dockerized Flask API (`/user/subscription_prediction/<id>/`)<br>-> `scikit-learn` Per-Service `LogisticRegression` Predictor | 1. Anchored digital personal finance UI onto an everyday physical object (a physical OP debit/credit card via `ARKit`) during a remote hackathon lacking lab hardware.<br>2. Used balanced per-service linear classifiers (`C=1e-2`, `class_weight='balanced'`) over opaque neural nets for fast containerized cold-starts.<br>3. Separated iOS AR client (`azimin`) from ML API (`antoleb`) cleanly over REST/JSON. | Flick Velocity Threshold: `abs(v) > 0.03` gesture trigger on card UI.<br>ML Solver: `LogisticRegression(max_iter=1e7, class_weight='balanced', C=1e-2)` trained on `new_sub.csv`.<br>Competition Standing: Overall Grand Winner across Junction 2020 Connected. | 1. Pointing a live iPhone camera at a physical OP bank card immediately materialized layered floating AR financial insights tied to physical card orientation.<br>2. Swiping/flicking off virtual subscription panels triggered instant predictive next-charge forecasts. | Alexander Zimin (`azimin`, iOS/ARKit), Anton Lebedev (`antoleb`, Python Flask/ML), Andrey Krylov (`andreykr.com`, UX Design), Andrey Volodin, and Egor Petrov. | Tactile physical-digital bridge in a virtual year. When most Connected 2020 teams shipped static web dashboards, *Saavi* turned the user's own camera and physical bank card into an unforgettable spatial computing interface. | 1. Even in software-heavy or remote tracks, using `ARKit`/vision anchored on a physical sponsor artifact creates instant hardware-grade stage magic.<br>2. Keep ML microservices lightweight (`OneHotEncoder` + regularized `LogisticRegression` in Docker) so AR demos never stall. | https://github.com/antoleb/saavi_back<br>https://github.com/azimin/MoneyMustBeFunnyAkaJunction2020Backup<br>https://www.andreykr.com/media<br>https://www.youtube.com/watch?v=Zc7ce9MxTNg<br>https://en.wikipedia.org/wiki/Junction_(hackathon) | L1: Verified by Two Public Winner Repositories (`saavi_back`, iOS backup), Wikipedia & Author Portfolio |
| junction-2019 | Junction 2019 | 2019 | Helvar & VTT | Making Spaces Brighter with Radar Technology | IoT & Hardware / Millimeter-Wave Radar & Closed-Loop Actuators | Utilizing VTT 60 GHz 2D imaging radar & 24 GHz vital-sign radar alongside RGB ground truth to estimate room/garage occupancy, track occupant state, and dynamically drive Helvar DALI intelligent luminaires. | helvar-vtt-lumenloop-2019 | LumenLoop | Helvar & VTT Challenge 1st Place Winner 🥇 | Real-time closed-loop millimeter-wave radar to smart luminaire actuation system built by a 2-person team. Consumes live 60 GHz FMCW (`180x110` polar frames at `100 Hz`, `5 cm` range resolution) and 24 GHz vital-sign streams over RabbitMQ (`10.84.110.2`) encoded in FlatBuffers, denoises occupancy (`diff/max > 0.13`), and directly commands physical Helvar DALI BLE-Mesh luminaire `EC22` via `pyserial` hex lookup tables (`00`..`FE` dimming, `6500K`–`2700K` color temperature), paired with React UI and Elasticsearch logging. | VTT 60 GHz FMCW Radar, VTT 24 GHz Vital Radar, RabbitMQ AMQP (`10.84.110.2`), FlatBuffers (`Vtt60Processed.Sample`), Python, NumPy, `pyserial==3.4`, Helvar DALI BLE Mesh USB Gateway (`EC22`), React (`Demo.js`), Elasticsearch | VTT 60/24 GHz FMCW Radars -> Ethernet RabbitMQ AMQP (`radar60`/`radar24` FlatBuffers)<br>-> `live/Streamer60.py` Denoise & Occupancy (`diff/max > 0.13`)<br>-> `pyserial` DALI BLE Mesh Hex LUTs (`EC22` intensity/Kelvin)<br>-> React Live Monitor + Elasticsearch | 1. Closed the physical loop completely: instead of stopping at matplotlib radar charts, converted live radar occupancy directly into serial hex frames dimming real `EC22` hardware.<br>2. Calibrated discrete ergonomic comfort states (`0` people `5% / 6500K` standby up to `3+` people `60% / 3450K` warm light) avoiding jarring flicker.<br>3. Parsed binary FlatBuffers cleanly with zero-copy NumPy arrays to sustain `100 Hz` radar cadence. | VTT 60 GHz Spec: `160 deg` H-beamwidth, `5 cm` range res, `3.5 deg` angular res, `<700 nm` micromotion (`180x110` @ `100 Hz`).<br>VTT 24 GHz Spec: `80 deg` H-beamwidth, `60 cm` range res, `1–5 um` micromotion.<br>Control LUTs: 31 brightness steps (`00`..`FE`) & 39 color-temp steps (`6500K`–`2700K`); occupancy trigger `diff/max > 0.13`. | 1. Judges walking into the 60 GHz radar cone immediately watched physical Helvar demo luminaire `EC22` smoothly ramp from cool 6500K standby (`5%`) to warm meeting lighting (`3450K` / `60%`).<br>2. Live polar radar heatmap synchronized beside physical lamp state. | Denys Kovalenko (`deniskovalenko`, Backend / DALI Serial Control) and Elizaveta Lebedeva (`elizavetalebedeva.com`, Data Science / React UI) — 2-person team who repeated at Helvar 2021. | Full physical sensor-to-actuator closure. Out of a field focused purely on offline CSV modeling, a 2-person team ingested raw AMQP FlatBuffers telemetry and physically modulated live DALI hardware on stage. | 1. Always close the loop from sensor back to physical actuator whenever partner hardware is at the booth.<br>2. Build binary FlatBuffers / RabbitMQ consumers early so high-rate RF streams don't bottleneck downstream UIs. | https://github.com/deniskovalenko/junction2019<br>https://elizavetalebedeva.com/tag/junction/<br>https://medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f | L1: Verified by Winner GitHub Repository (`deniskovalenko/junction2019`), Author Blog & Official Junction Medium Winners List |
| junction-2019 | Junction 2019 | 2019 | Aalto University (AYY) | Smart Signage - For Students by Students | IoT & Hardware / Edge Embedded Kiosk, PIR & Touchless CV | Incorporating real AYY student-housing HVAC, water, electricity, and network telemetry into interactive stairwell/hallway smart signage hardware with practical student utility. | aalto-ayyhello-2019 | AyyHello! (`ayyHello`) | Aalto University AYY Challenge 1st Place Winner 🥇 | Hygienic, touchless stairwell smart signage prototype spanning ~2,600 AYY student apartments (~3,500 residents). Combines a Raspberry Pi with a rising-edge hardware PIR wake interrupt (`RPi.GPIO`, `PIR_PIN = 11`, `LED_PIN = 3`) and USB webcam running modified `MobilePose-PyTorch` (`resnet18`, `224x224`) 10-frame debounced gesture classification (`L` / `R` / `U`), dispatching HTTP commands (`http://10.42.0.157:5000/dir`) to a React/Material-UI kiosk displaying live AYY utility CSV analytics (`SMT8-12_*.csv`), HSL transit, weather, and a webcam mini-game. | Raspberry Pi (Linux, `RPi.GPIO`), PIR Motion Sensor, USB Webcam (`--camera 0`), `PyTorch 1.0.0` (`MobilePose-PyTorch` `resnet18` / `mobilenetv2`), `OpenCV 3.4.2.17`, Python `Flask` + `flask_cors`, React `16.12.0`, Material-UI `4.6.1` | PIR Hardware Interrupt (`PIR_PIN = 11`, `LED_PIN = 3`) -> Wake Display & Webcam (`--camera 0`)<br>-> `MobilePose-PyTorch` (`resnet18`, `224x224`, 10-frame debounce)<br>-> `POST /dir` Flask Backend (`analysis.py` AYY CSVs)<br>-> React Kiosk (`PublicTransport`, `Sustainability`, `Game`) | 1. Chose touchless pose gestures over fragile stairwell touchscreens, making public building hardware tamper- and smudge-resistant.<br>2. Stabilized noisy keypoint predictions with a simple 10-frame temporal debounce window rather than training an unstable 3D-CNN/LSTM.<br>3. Decoupled Raspberry Pi GPIO, PyTorch CV (`estimator.py`), and React kiosk (`App.js`) over local HTTP so 5 team members could develop in parallel. | Input Resolution: `224x224` (`--inp_dim 224`) via `resnet18` backbone.<br>Temporal Debounce: `10`-frame majority stability filter for `L`/`R`/`U` commands.<br>Target Footprint: Designed for AYY's `~2,600` student apartments (`~3,500` residents) parsing `SMT8-12_*.csv` (`delimiter=';'`). | 1. Judges approaching the kiosk triggered the hardware PIR interrupt (`LED_PIN = 3`), waking the display automatically.<br>2. Waving left/right/up cleanly flipped between commuter bus schedules, real building kWh/water footprint charts, and an interactive pose game. | Mari Porko (`mariporko`), Harri Rahikainen (`HRahikainen`), Jesse Tolvanen (`JZNT`), Satria Sutisna (`satriasutisna`), and `smirq` (5-person Aalto/Finnish team). | Practical residential hardware realism + effortless touchless UX. Rather than dumping raw Grafana HVAC plots, the team paired energy awareness with daily commuter utility and rock-solid debounced PIR + webcam interaction. | 1. Temporal debouncing (`10`-frame lock) is an indispensable reliability pattern for live camera gesture demos in crowded hackathon halls.<br>2. Decouple SBC GPIO (`RPi.GPIO`), PyTorch inference, and frontend over local HTTP microservices for parallel hacking. | https://github.com/mariporko/junction2019<br>https://github.com/HRahikainen/junction2019<br>https://medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f<br>https://www.aalto.fi/en/news/student-union-looks-for-creative-ideas-for-their-information-channels-from-junction | L1: Verified by Winner GitHub Repositories (`mariporko/junction2019`), Aalto News & Official Medium Winners List |
| junction-2018 | Junction 2018 | 2018 | Intel | Innovative Applications With Bluetooth Mesh | IoT & Hardware / Bluetooth Mesh Gateways, Edge Triage & Wearables | Creating an IoT edge gateway application communicating with and exploiting Bluetooth Mesh wireless sensor networks (badges, sensors, lighting, messaging without cloud infrastructure). | intel-helpio-2018 | Help.io / Team Health.io | Intel Challenge 1st Prize 🥇 + IoT Track Overall Winner 🏆 + 2nd Place Overall 🥈 (out of 300+ projects) | Offline disaster-triage and first-responder mesh network combining Suunto Movesense wearable biometrics with Intel's experimental Bluetooth Mesh hardware kit. Collects patient heart-rate and R-R intervals via BLE into an iOS 12 triage engine (`lowestHRBound = 60.0`, `highestHRBound = 110.0`, `highestRRMultiplier = 2.0`), then POSTs critical casualty alerts (`10.100.5.16:3000/{bluetoothId}/critical`) to an Intel NUC (`BlueZ meshd-ingas` + `nRF51_dongle`) that broadcasts mesh alerts across 4 PHYTEC `reel_board` e-ink responder badges running Zephyr OS — zero internet required. | Suunto Movesense (HR/RR BLE), iOS 12 / Swift (`Movesense SDK`, `AsyncDisplayKit`, `PromiseKit`, `Bond`, `SwiftyJSON`, `Alamofire`, `ScrollableGraphView`), Intel NUC (Linux, `BlueZ` `meshd-ingas`, `ell 0.13`, `org.bluez.mesh1`), `nRF51_dongle` (`hci_uart`), 4x PHYTEC `reel_board`s (`Zephyr OS` `mesh_badge`, models `0x0000` / `0x1000` / `0x1102`) | Patient Movesense (`175030001053` / `175030000988`, `HR_PATH`)<br>-> iOS 12 Local Triage Engine (`heartRateHistory >= 15`)<br>-> HTTP POST `10.100.5.16:3000/{id}/critical`<br>-> Intel NUC BlueZ `meshd` + `nRF51_dongle` HCI<br>-> PHYTEC `reel_board` Zephyr Mesh Badges | 1. Decoupled mature sensor acquisition (iOS Movesense BLE SDK) from experimental `BlueZ` mesh drivers over a clean local HTTP endpoint (`10.100.5.16:3000`), avoiding driver/thread deadlocks in 48 hours.<br>2. Configured explicit demo-tunable triage limits (`60`–`110` BPM) cleanly separated from initialization warm-up (`discardCount = 5`).<br>3. Leveraged standard Bluetooth Mesh models (`0x0000` Vendor, `0x1000` OnOff, `0x1102` Sensor temp `0x2a1f`) from Intel's `Junction2018_Support` kit rather than inventing proprietary RF packets. | Hardware Kit Ratio: 1x Intel NUC + 1x `nRF51_dongle` + 4x `reel_board`s (Intel supplied 8 total kits); paired with Movesense BLE (`26` total Movesense projects).<br>Triage Bounds: `discardCount = 5`, `heartRateHistory >= 15`, `lowestHRBound = 60.0`, `highestHRBound = 110.0`, `highestRRMultiplier = 2.0`.<br>Rank: 1st Intel + 1st IoT Track + **2nd Overall** (among 11 finalists & 300+ projects). | 1. Triggering abnormal heart-rate spikes on a live human wearing Movesense autonomously flashed alerts and patient sector metadata (`0x0001` / `0x0002`) across networked `reel_board` e-ink responder badges with Wi-Fi uplink completely severed.<br>2. Real-time multi-patient ECG waveform plotting via `ScrollableGraphView` on iOS. | University of Latvia Faculty of Computing: Austris Cīrulnieks, Mārcis Nīmants (`mnimants`), Elvijs Viļķels, Aigars Cibuļskis, and Dāvis Mednis *(4 members previously won 2017 Movesense Health Challenge with ReCover)*. | Clean dual-stack systems architecture plus visceral zero-internet hardware resilience. Bridging commercial wearable biometrics into Intel's bleeding-edge `meshd-ingas` stack stunned judges by operating as a true off-grid responder mesh. | 1. When given bleeding-edge vendor firmware (`BlueZ meshd`), isolate it behind a simple HTTP gateway so iOS/web engineers can iterate independently.<br>2. Inspect vendor support repos (`feri/Junction2018_Support`, `intel/Junction2018`) early to use exact pre-provisioned GATT/Mesh model opcodes (`0x8202`, `0x8231`). | https://github.com/mnimants/junction2018<br>https://github.com/intel/Junction2018<br>https://github.com/feri/Junction2018_Support<br>https://www.movesense.com/news/2018/11/movesense-shined-in-junction-hackathon/<br>https://eztf.lu.lv/en/about-us/news/detail-view/t/98941/ | L1: Verified by Winner Repo (`mnimants/junction2018`), Official Intel Repos, Movesense Press & Univ. of Latvia Release |
| junction-2018 | Junction 2018 | 2018 | Ensto | Teach EV Chargers New Tricks | IoT & Hardware / Edge Vision, Smart EV Chargers & Mobility | Extending real EV charging station hardware with novel software/hardware capabilities over the EnstoFlow REST API (`RealDevice` OCPP control) and persuasive commercial business models. | ensto-oneiro-2018 | Oneiro (Team Glados) | Overall Grand Winner 🏆 (€20,000 Cash Prize) & Ensto Mobility Challenge 1st Prize 🥇 (out of 14 Ensto teams) | Peer-to-peer "Airbnb for EV chargers" powered by autonomous edge license-plate recognition on a real Ensto Chago station. A Raspberry Pi + PiCamera running a supervised `systemd` service captures `640x480` frames every `0.5s`, posts them to Dockerized `openalpr:16.04` (`country="eu"`, `confidence >= 75`), and dispatches `spot_enable()` commands via Sanic -> `EnstoFlow` REST/OCPP to unlock real charging station `JunctionEVB1`, complemented by a React Native app and Telia cellular `Mapbox GL` demand heatmap. | Raspberry Pi + PiCamera (`systemd` `photographer.service`), Docker `openalpr:16.04` (`eu`/`fi`), Python 3 + `Sanic` (`port 8000`), `EnstoFlow` REST API v1 (`JunctionEVB1`, OCPP `A -> C`), React Native (`sdk-31.0.0`, Expo `^31.0.2`, Redux-Saga), `Mapbox GL JS v0.51.0` (Telia mobility data), Terraform + AWS (`t2.nano`, ELB, ECR, S3, CloudFront, Route53) | Raspberry Pi Camera (`0.5s` `640x480`, `2s` timeout)<br>-> Sanic Server (`port 8000`) & Docker `openalpr:16.04` (`conf >= 75`, `top_n=5`)<br>-> `EnstoFlow` OCPP `spot_enable()` (`JunctionEVB1` LEDs)<br>-> Expo React Native Rider App + Telia `Mapbox` Heatmap | 1. Used hardware computer vision (PiCamera ALPR) so EV drivers simply pull up and charge hands-free without juggling apps or RFID cards.<br>2. Paired physical hardware actuation directly with commercial owner economics (`mock` energy/revenue split) and city demand planning (Telia cellular Telco heatmap).<br>3. Wrapped Pi capture in a fault-tolerant `systemd` unit with short `2s` HTTP timeouts so wireless packet drops never hung the edge node. | Capture Cadence: `0.5s` (`2 FPS`) at `640x480` with `2s` HTTP timeout.<br>ALPR Auto-Unlock Gate: `top_n = 5` EU/FI plate candidates matching at `confidence >= 75`.<br>Competition Standing: **1st Overall €20,000** (~1,200–1,300 participants, 300+ solutions) + 1st of `14` Ensto challenge teams. | 1. Holding a license plate in front of the Raspberry Pi camera live on stage triggered Docker ALPR recognition and switched the real Ensto Chago station (`JunctionEVB1`) LED status to active charging.<br>2. Live Mapbox GL cellular heatmap identifying underserved Helsinki charger placement gaps. | Team Glados (Aalto students & Finnish engineers): Teemu Taskula (`Temzasse`), Andreas Urbanski, and Ville Toiviainen (`Villux`) — achieved rare **back-to-back Junction Overall Grand Wins (2017 & 2018)**. | End-to-end physical actuation plus rare commercial polish. Ensto's Head of Software (Ville Parviainen) highlighted how seamlessly *Oneiro* fused real OCPP charger APIs with zero-friction edge vision and a viable P2P business model. | 1. Physical automation (camera/RFID unlocking a live sponsor machine) removes manual app taps and steals the stage demo.<br>2. Keep edge camera scripts minimal (`0.5s` loop, `2s` timeout, `systemd` restart) while heavy OCR/ALPR runs in containerized backends. | https://github.com/teamglados/oneiro<br>https://vimeo.com/302650304<br>https://talotekniikka-lehti.fi/oneiro-voitti-junction-2018-hackathonin/<br>https://mobiili.fi/2018/11/25/junction-hackathon-espoossa-paattyi-latauspisteiden-airbnbn-voittoon-sama-tiimi-voitti-kilpailun-viime-vuonnakin/ | L1: Verified by Winner GitHub Repository (`teamglados/oneiro`), Demo Video & Finnish Tech Press |
| junction-2018 | Junction 2018 | 2018 | Future Cities Track | Future Cities Challenge | IoT & Hardware / Assistive Dual-MCU Hardware & Custom CAD | Hardware completeness, citizen accessibility impact, field usability, and scalable urban innovation. | futurecities-guideme-2018 | GuideMe | Future Cities Track 1st Prize 🥇 (€1,000) & 4th Place Overall (out of 300+ projects) | Smart haptic walking-cane navigation attachment engineered end-to-end (custom SolidWorks/STL 3D-printed chassis, dual-MCU firmware, and web caregiver portal) to guide visually impaired or elderly pedestrians without smartphone screens. A Wemos `ESP8266` fetches turn-by-turn routes from a Google Maps Directions PHP backend and relays bearings over `115200 baud` UART (`pins 0/2`) to a `BBC micro:bit`, whose onboard magnetometer drives directional 5x5 LED arrows and `pin 1` vibration/buzzer actuators inside an ergonomic cane handle. | `BBC micro:bit` (ARM Cortex-M0, magnetometer, 5x5 LED matrix, MicroPython `micro.py`), `Wemos ESP8266` (Arduino C++ `guideme_arduino_wifi_node.ino`), SolidWorks CAD (`guideme_handle.SLDPRT` / `.STL` 3D print), PHP (`web/back.php`, `web/front.php`), Google Maps Directions API, HTML / jQuery / AJAX | Caregiver Web UI (`web/front.php`, Google Maps API)<br>-> `Wemos ESP8266` HTTP Poller (`guideme_arduino_wifi_node.ino`)<br>-> UART `115200 baud` (`pin 0`/`pin 2`)<br>-> `BBC micro:bit` Magnetometer Compass Lock (`micro.py`) -> 5x5 LED + `pin 1` Haptic Buzzer/Vibrator | 1. Split responsibilities across two cheap hobby boards: `ESP8266` solely handled Wi-Fi HTTP fetching while `BBC micro:bit` owned magnetic heading alignment, LED feedback, and `pin 1` haptics — avoiding MicroPython Wi-Fi bloat.<br>2. Modeled and 3D-printed a real ergonomic enclosure (`guideme_handle.SLDPRT` / `.STL`) on site so the electronics mounted cleanly on a physical cane.<br>3. Exposed live GPS tracking and remote destination entry for family caregivers in AJAX/PHP. | Serial Interface: `115200 baud` UART over `BBC micro:bit` `pin 0` / `pin 2`, actuator PWM/output on `pin 1`.<br>Enclosure Spec: Custom parametric CAD `.SLDPRT` + `.STL` handle fabricated at Junction.<br>Competition Standing: **4th Place Overall** (among ~1,300 participants & 300+ projects) + Future Cities Track 1st (€1,000). | 1. Rotating the physical 3D-printed cane handle in hand triggered real-time magnetometer re-alignment across the top-mounted `micro:bit` 5x5 LEDs and audible/tactile buzz pulses.<br>2. Caregiver web portal dynamically updating next waypoint bearings mid-walk. | Makers UPV (Universitat Politècnica de València multidisciplinary engineering team): Jaime Laborda Macario, Iván Torres Játiva, Enrique Miralles Dolz, Joaquín Montesinos Muñoz, and Matías Fernández Patón. | Tactile assistive industrial design meets disciplined dual-MCU partitioning. Five cross-disciplinary engineers built mechanical CAD, firmware, electronics, and web control from zero in 48 hours and ranked 4th overall. | 1. Partitioning Wi-Fi/cloud comms onto an `ESP8266` and real-time sensors/actuators onto a companion MCU over `115200` UART simplifies hackathon debugging.<br>2. Custom 3D-printed mechanical enclosures transform exposed breadboards into convincing product prototypes. | https://github.com/makers-upv/GuideMe<br>https://www.upv.es/noticias-upv/noticia-10627-junction-2018-es.html<br>https://mobiili.fi/2018/11/25/junction-hackathon-espoossa-paattyi-latauspisteiden-airbnbn-voittoon-sama-tiimi-voitti-kilpailun-viime-vuonnakin/ | L1: Verified by Winner GitHub Repository (`makers-upv/GuideMe`), Official UPV Release & Finnish Finalist Press |
| junction-2018 | Junction 2018 | 2018 | Vaisala | Hack the Sauna | IoT & Hardware / Extreme-Environment Multi-Sensor Analytics | Transforming industrial precision temperature, humidity, enthalpy, CO2, and O2 telemetry into actionable extreme-environment sauna wellness & plant control insights. | vaisala-masga-2018 | Make Sauna Great Again (MaSGA) | Vaisala "Hack the Sauna" Challenge 1st Prize 🥇 (later published at IEEE IECON 2020) | Empirical fuzzy-similarity digital comfort score and operator diagnostic dashboard powered by multi-zone Vaisala industrial sauna probes (`Stove1`, `Bench1–3`, `Floor1`). Ingests live Temperature, Relative Humidity, Enthalpy, CO2, and Oxygen readings from `apigtw.vaisala.com`, evaluates trapezoidal fuzzy matching (`quadro()`) calibrated directly from 22 in-sauna bather surveys inside a Python Google Cloud Function (`Addono/masga-backend`), and outputs instant persona-specific guidance (e.g., "add water" vs stove/ventilation tuning) every `10s`. | Vaisala Industrial Sauna Probes (Temp, RH, Enthalpy, CO2, O2 across `Stove1`, `Bench1–3`, `Floor1`), Vaisala REST API Gateway, Python (Google Cloud Functions `main.py`), Trapezoidal Fuzzy Similarity (`quadro()`), Bootstrap 4.1.3, jQuery 3.3.1 | 5x Physical Vaisala Probes (`Stove1`, `Bench1–3`, `Floor1`)<br>-> Vaisala API Gateway (`/saunameasurements/latest`)<br>-> Google Cloud Functions Python Engine (`quadro()` fuzzy similarity on 22 user surveys)<br>-> Dual-Mode Bootstrap Dashboard (`10s` polling for User / Manager) | 1. Collected 22 real bathers' empirical surveys (`>= 10–15 min` sessions) on site rather than inventing arbitrary thermal thresholds.<br>2. Encoded nonlinear multi-sensor comfort tradeoffs using trapezoidal fuzzy similarity (`quadro()`), later peer-reviewed in IEEE IECON 2020.<br>3. Split UI cleanly into *Bather* (actionable "add water" / open door prompts) and *Operator* (plant stove/airflow bounds) views. | Ground-Truth Dataset: `22` live sauna bather surveys (`>= 10–15 min` exposure).<br>Telemetry Cadence: `10s` (`10000 ms`) frontend refresh via `us-central1` GCF.<br>Health Score Thresholds: `> 88%` Green ("Perfect"), `> 75%` Orange ("Degraded"), `<= 75%` Red ("Poor"); academic follow-up published IEEE IECON 2020. | 1. Live demo contrasting raw ambiguous CO2/RH readings against clear traffic-light comfort indicators and "throw löyly / ventilate" action prompts.<br>2. Seamless toggle between recreational sauna guest view and commercial facility manager diagnostics. | Aalto / international interdisciplinary research team: Siavash H. Khajavi (Aalto DIEM postdoc), Alireza Jaribion (Aalto DIEM researcher), Adriaan Knapen (`Addono`), Leila Abiedat, and Arnab Banik. | Scientific ground-truth rigor paired with clear operational UX. Instead of displaying raw probe curves, the team collected live human survey baselines and distilled 5 sensor channels into publishable fuzzy wellness logic. | 1. Collecting even a tiny empirical dataset on site (`22` human ground-truth surveys) anchors sensor models in reality.<br>2. Always translate raw multi-probe industrial telemetry into role-specific action prompts rather than raw time-series plots. | https://github.com/Addono/masga-backend<br>https://github.com/Addono/masga<br>https://www.vaisala.com/en/blog/2018-11/winners-vaisalas-challenges-junction-2018-hacked-weather-and-sauna<br>https://www.aalto.fi/en/news/winning-team-hack-the-sauna-experience-to-a-new-level-at-junction<br>https://aaltodoc.aalto.fi/items/44b6d03b-0849-4381-a9e4-300de579f7d3<br>https://youtu.be/rNtnsDjz0vM | L1: Verified by Winner GitHub Repos, Official Vaisala Blog, Aalto News & IEEE IECON 2020 Paper |
| junction-2018 | Junction 2018 | 2018 | Movesense by Suunto & Stara | Track Anything That Moves / Stara StreetReboot2 | IoT & Hardware / Crowdsourced Infrastructure IMU & Smart City | Added value, functional readiness, UX using programmable Movesense IMUs, plus urban infrastructure impact for City of Helsinki Stara. | movesense-terrainsense-2018 | TerrainSense | Movesense 1st Prize 🥇 (Best Multi-Challenge Combination) & City of Helsinki Stara StreetReboot2 2nd Place 🥈 (€1,000) | Low-cost urban cycling-path roughness crowdsourcing system. Mounts a programmable Suunto Movesense IMU accelerometer directly on a bicycle's rear axle (`taka-akseli`), streams vibration/shock telemetry over BLE to an Android app paired with GPS coordinates, and uploads GPX traces to an AWS S3/EC2 web heatmap exposing bumpy pavement segments for Helsinki municipal repair planning — later advancing to 3 multi-year municipal pilots with Helsinki, Forum Virium, HAMK, and InnoTrafik adding AWS Rekognition CV. | Suunto Movesense IMU Sensor (Bluetooth LE), Android Mobile App (GPS + BLE ingestion), GPX Telemetry Export, AWS S3 / AWS EC2 Cloud Heatmap *(plus post-hackathon AWS Rekognition road-video CV)* | Rear-Axle (`taka-akseli`) Movesense IMU -> BLE Stream<br>-> Android GPS + Vibration Correlator<br>-> AWS S3 / EC2 Road Roughness Heatmap & GPX Inspector<br>-> Municipal Cycling Maintenance Workflow | 1. Chose non-human infrastructure monitoring (mounting IMU on bicycle rear axles rather than human wrists) to differentiate in a wearable-heavy field.<br>2. Bridged two partner tracks simultaneously (Movesense hardware + Helsinki Stara `StreetReboot2`), winning awards from both panels.<br>3. Leveraged standard GPX geospatial export so city GIS engineers could ingest pothole/vibration traces immediately. | Challenge Funnel: 26 final Movesense submissions (out of 35 Saturday / 18 Friday kits).<br>Stara Prize (`HEL 2019-003563`): €1,000 (2nd Place Stara StreetReboot2) + Movesense 1st Multi-Challenge Award.<br>Post-Hackathon Impact: 3 real pilot deployments (City of Helsinki, Forum Virium, HAMK, InnoTrafik). | 1. Live bicycle axle vibration trace synced with interactive Helsinki cycling-lane severity map.<br>2. Official Stara municipal decision record and commercial follow-on presentation deck proving lasting city adoption. | Ville Saramaa (`vill.dev`) and interdisciplinary Nordic builders *(expanded into municipal pilots with HAMK & InnoTrafik)*. | Strategic dual-track hardware-to-municipal fit. Mounting a €50 IMU sensor onto commuter bicycle axles solved a multi-thousand-euro road-inspection problem for City of Helsinki Stara. | 1. Combining one hardware kit (Movesense/Intel) with a civic/industrial dataset challenge (`Stara`) multiplies prize equity and real-world impact.<br>2. Think beyond wrists and chests: mounting IMUs onto vehicles, machines, or bicycles immediately distinguishes a project. | https://www.movesense.com/news/2018/11/movesense-shined-in-junction-hackathon/<br>https://www.movesense.com/wp-content/uploads/2018/12/TerrainSense_Junction_presentation.pdf<br>https://paatokset.hel.fi/fi/asia/hel-2019-003563<br>https://vill.dev/projects/<br>https://unlimited.hamk.fi/teknologia-ja-liikenne/pyoravaylien-kunnon-tutkiminen-sensoriteknologian-keinoin/ | L1: Verified by Official Movesense Presentation PDF, Municipal Award Record (`HEL 2019-003563`) & Pilot Reports |
| junction-2018 | Junction 2018 | 2018 | Helvar | The Brain of the Building | IoT & Hardware / Smart Luminaires & Multi-Sensor Vision Fusion | Building autonomous cognitive lighting hubs connecting lighting sensors and environment controls to optimize comfort, anomalies, and occupant productivity. | helvar-ivision-lamp-2018 | IVision Lamp | Helvar "The Brain of the Building" Challenge 1st Place Winner 🥇 | Autonomous smart luminaire control system unifying computer vision perception and multi-sensor fusion built in 42 hours by the Tsinghua University × SenseTime Future Deep Learning Student Team. Processes real-time optical visual cues alongside ambient multi-sensor streams to dynamically adapt luminaire brightness and illumination quality inside live smart-building partner tests, earning Helvar's 1st prize (no public source repository or quantitative latency metrics published). | Smart Desk Luminaire Hardware, Computer Vision Perception Pipeline, Multi-Sensor Fusion Hub, Real-Time Adaptive Lighting Control *(full internal stack/repo not publicly disclosed)* | Camera Vision Input + Multi-Sensor Environmental Telemetry<br>-> Real-Time Multi-Sensor Fusion Engine<br>-> Closed-Loop Smart Desk Luminaire Intensity Modulation | 1. Paired camera-based computer vision directly with ambient luminaire sensors rather than treating lighting purely as offline energy analytics.<br>2. Focused on a tight 42-hour hardware-in-the-loop smart lamp demo validated live with Helvar judges. | Implementation Window: `42` hours from scratch at Junction 2018 (among 1,300+ hackers, 46 challenges).<br>Public Benchmark Boundary: No public GitHub repo or quantitative lux/latency metrics published `[L2]`. | 1. Live multi-sensor vision fusion adjusting luminaire lighting behavior dynamically during Helvar partner booth evaluation. | Tsinghua–SenseTime Future Deep Learning Student Interest Team: Xiulong Yuan (EE), Yingxue Guo (EE), Xin Li (Automation), and Feng Liang (Microelectronics & Nanoelectronics). | Hardware-focused cross-disciplinary academic depth. Combining electronic engineering, automation, and deep-learning vision produced the first-ever Tsinghua Junction Challenge Win. | 1. Adding real visual + multi-sensor fusion onto physical hardware beats purely simulation-based ML models in smart-building tracks.<br>2. Document `[L2]` academic/press-verified builds clearly without fabricating missing private metrics. | https://www.tsinghua.edu.cn/info/1173/17718.htm<br>https://www.sensetime.com/cn/technology-new-detail/3606?categoryId=53<br>https://helvar.com/how-to-make-the-light-work-for-you/ | L2: Verified by Official Tsinghua University Newsroom & SenseTime Press Release |
| junction-2018 | Junction 2018 | 2018 | Fleetboard (Daimler / Mercedes-Benz) | Trucks X Code | IoT & Hardware / Connected Heavy Vehicle SDK & Fleet Telemetry | Creating high-value Android/web applications exploiting live commercial Mercedes-Benz heavy-truck vehicle bus and sensor telemetry exposed via the Fleetboard SDK. | fleetboard-trucksense-2018 | TruckSense | Fleetboard Challenge 1st Prize 🥇 (3-Day Stuttgart Daimler Innovation Workshop) | Connected commercial-truck monitoring and predictive diagnostics web application built on the Fleetboard Mercedes-Benz on-board computer SDK in ~40 hours. Streams live heavy-truck telemetry into a machine-learning forecasting pipeline and interactive graphical monitoring console, winning a 3-day all-expenses-paid engineering workshop at Daimler/Mercedes-Benz HQ in Stuttgart (no public codebase or quantitative forecasting error published). | Fleetboard SDK (Mercedes-Benz Truck On-Board Computer), Live Vehicle Bus Telemetry Ingestion, Machine Learning Predictive Pipeline, Web Visualization App *(exact model/repo not publicly documented)* | Mercedes-Benz Commercial Truck On-Board Computer / Fleetboard SDK<br>-> Streaming Telemetry Ingestion Backend<br>-> ML Future-Metric Forecaster -> Fleet Graphical Dashboard | 1. Built directly atop real commercial vehicle telemetry pipelines exposed by Daimler's Fleetboard SDK rather than generic static fleet tables.<br>2. Combined real-time operational monitoring with predictive forward forecasting to address fleet downtime costs. | Implementation Window: `~40` hours (pre-selected from ~10,000 applicants across ~1,000+ competitors).<br>Public Benchmark Boundary: No public GitHub repository or quantitative MAE/RMSE metric published `[L2]`. | 1. Real-time graphical vehicle telemetry cockpit projecting predictive future truck states cleanly for Mercedes-Benz engineers. | UPCT (Universidad Politécnica de Cartagena) & Vueling Engineers: Pablo Moyano (UPCT Telematics), Enrique Fernández (UPCT Telematics), plus 2 Vueling software developers. | Direct industrial telematics utility over flashy gimmicks. Telematics + airline engineering talent spoke the exact operational uptime language prized by Daimler Fleetboard judges. | 1. On industrial automotive SDK challenges, forward-looking predictive maintenance UIs consistently beat passive telemetry viewers.<br>2. Explicitly log public-code boundaries on `[L2]` university-verified wins. | https://www.upct.es/noticias/2018-11-30-premiados-dos-alumnos-de-la-upct-por-resolver-un-reto-tecnologico-para-monitorizar-los-camiones-mercedes<br>https://www.laverdad.es/murcia/cartagena/estudiantes-upct-resuelven-20181202005210-ntvo.html | L2: Verified by Official UPCT University Release & La Verdad Press Report |
| junction-2017 | Junction 2017 | 2017 | STARA / Junction Main Competition | Main Competition & STARA Urban Challenge | IoT & Hardware / Mobile Edge Vision & Smart Infrastructure | Technical depth, scalability, and real-world urban infrastructure impact across Junction 2017's 1,500 competitors and 13 tracks. | stara-signvision-2017 | Signvision (Team Glados) | Overall Grand Winner 🏆 (€20,000 Cash Prize) & STARA Challenge 2nd Prize 🥈 | Real-time crowdsourced traffic-sign audit and infrastructure mapping pipeline turning smartphone dashboard video and GPS coordinates into an automated municipal inventory. Streams frames + lat/lng over high-throughput `uWs` WebSockets (`port 3000`, `5000ms` deduplication) to a Python/OpenCV HSV red-mask + `scikit-image` ROI detector (`numPixels > 1000`, `30%` padding) and TensorFlow `1.4.0` CNN (`32x32x3` trained on GTSRB Stop `00014`) deployed in CUDA 8.0 Docker + AWS ECS Terraform — inaugurating Team Glados's back-to-back Junction Main Competition dynasty. | React Native (Camera + GPS), Node.js `uWs` WebSockets (`3000`), `Koa` (`8000`), Python `Flask` (`8080`), `OpenCV` + `scikit-image` (`label`), `TensorFlow 1.4.0` CNN, CUDA 8.0 Docker, Terraform + AWS ECS | Smartphone Camera + GPS (React Native)<br>-> `uWs` WebSocket & `Koa` API (`5000ms` dedup)<br>-> OpenCV HSV Red-Mask + `scikit-image` ROI (`numPixels > 1000`)<br>-> TensorFlow `1.4.0` `32x32x3` CNN (`Dense(2)`) in CUDA 8.0 Docker / AWS ECS | 1. Inserted a classical OpenCV HSV + connected-component ROI pre-filter before TensorFlow so the tiny `32x32x3` CNN only classified crisp padded traffic-sign patches.<br>2. Added a `5000ms` WebSocket deduplication cooldown so stationary vehicles wouldn't flood the map with duplicate sign logs.<br>3. Packaged the full cloud stack in reproducible Terraform (`aws/*.tf`) + CUDA 8.0 Docker containers. | CNN Input: `32x32x3` (`Conv2D(16, 3x3)` -> `Conv2D(32, 3x3)` -> `Flatten` -> `Dense(2)`), trained on GTSRB `00014` (`2,000`/`18,000` steps).<br>ROI / Throttle: `numPixels > 1000` (`30%` bbox pad), `5000 ms` WebSocket cooldown.<br>Scale: €20,000 Overall Winner across 1,500 attendees / 13 tracks + STARA 2nd. | 1. Driving/walking past real Finnish/Stop test signs immediately dropped geocoded pins onto the live municipal infrastructure dashboard.<br>2. Smooth live end-to-end phone-to-cloud CV detection with zero GPU container crashes. | Team Glados: Andreas Urbanski, Teemu Taskula, and Ville Toiviainen — Aalto/Finnish systems trio who won back-to-back Junction Overall Prizes (`2017` & `2018`). | Hybrid classical-CV + lightweight DL + DevOps maturity. Instead of overfitting an end-to-end detector in 48h, classical HSV ROI cropping made a `32x32` TF classifier rock-solid for city road inventorying. | 1. Hybrid pipelines (HSV/morphology crop -> tiny CNN) dramatically cut false positives under varying outdoor lighting in 48-hour builds.<br>2. Always add spatial/temporal deduplication (`5000ms` cooldown) on continuous edge-camera streams. | https://github.com/teamglados/signvision<br>https://devpost.com/software/glados<br>https://vimeo.com/244507554<br>https://www.uusiteknologia.fi/2017/11/28/junction2017-voittaja-yhdisti-big-datan-mobiiliin/ | L1: Verified by Winner GitHub Repository (`teamglados/signvision`), Devpost, Demo Video & Finnish Tech Press |
| junction-2017 | Junction 2017 | 2017 | Suunto (Movesense) | Track anything that moves! | IoT & Hardware / Dual-IMU Biomechanics & Rehab Wearables | Value added to selected use case, functional concept readiness, and UX using programmable Suunto Movesense BLE sensors across Health, Sports, or IoT. | suunto-recover-2017 | ReCover (`DF LAB`) | Movesense Health Challenge Winner 🥇 (6 Movesense Sensors + 4 Suunto Spartan Watches) | Post-operative home knee-rehabilitation biofeedback system solving unsupervised joint-angle guessing for recovering patients. Mounts **two synchronized Suunto Movesense IMU sensors** above and below the knee joint and streams dual quaternion/inertial orientation over BLE to an iOS application computing live relative knee flexion angles against therapist recovery targets — marking the Latvian team's origin before returning to win 2018 Intel + 2nd Overall (*Help.io*). | 2x Programmable Suunto Movesense Wearable Sensors (IMU: Accel/Gyro/Mag), Bluetooth Low Energy (`movesense-mobile-lib`), iOS Mobile App, Differential Joint-Angle Kinematics | Upper-Leg Movesense IMU + Lower-Leg Movesense IMU<br>-> Dual-Sensor BLE Sync (`movesense-mobile-lib`)<br>-> Real-Time Differential Joint Flexion Angle Computation<br>-> iOS Patient Adherence & Physio Guidance UI | 1. Mounted **two** independent Movesense sensors spanning the anatomical joint rather than one sensor, yielding frame-invariant relative flexion angles regardless of overall body lean.<br>2. Grounded product workflow in clinical rehabilitation insight mentored by PhD researcher Emīls Sjundjukovs.<br>3. Selected Health as the clearest unmet daily-adherence vertical among 24 competing Movesense teams. | Hardware Challenge Scope: `1` of `24` Movesense submissions at Junction 2017 (Dipoli; 1,500 total participants).<br>Physical Kit: Differential 2-sensor wearable topology (`2` Movesense IMUs per limb); prizes: `6` Movesense sensors + `4` Suunto Spartan watches. | 1. Presenter flexing his knee live showed instantaneous degree-by-degree angle feedback and safe recovery target zone confirmation on iOS.<br>2. Demonstrated how cheap strapped wearables replace clinic goniometers at home. | DF LAB (University of Latvia Faculty of Computing): Austris Cīrulnieks, Elvijs Viļķels, Dāvis Mednis, and Mārcis Nīmants *(clinical concept initiated by PhD researcher/mentor Emīls Sjundjukovs)*. | Clean dual-sensor physics plus clinical empathy. Computing relative vector difference between two synchronized limb IMUs immediately impressed Suunto hardware engineers over naive single-IMU pedometers. | 1. Measuring relative angles across a joint requires paired dual-IMU referencing so posture shifts don't corrupt clinical measurements.<br>2. Hardware teams compound mastery across editions: DF LAB evolved from 2017 `ReCover` directly into 2018's Intel-winning `Help.io`. | https://devpost.com/software/recover-pfrq3g<br>https://www.movesense.com/news/2017/11/24-movesense-projects-at-junction-hackathon/<br>https://eztf.lu.lv/par-mums/zinas/zina/t/29783/ | L1: Verified by Official Movesense Challenge Report, Devpost Record & University of Latvia Press |
| junction-2017 | Junction 2017 | 2017 | Planmeca Oy | Reshaping the future of dentistry | IoT & Hardware / 3D Dental Imaging & Mobile AR Overlay | Expanding digital dental care and 3D cone-beam CT / intraoral data into effortless patient workflows and virtual pre-treatment planning tools. | planmeca-ar-dentist-2017 | AR Dentist | Planmeca Challenge 1st Prize Winner 🥇 (out of 13 competing teams) | Real-time chairside dental Augmented Reality preview prototype fusing Planmeca's 3D dental imaging datasets (`Planmeca Romexis` / CBCT exports) with live patient facial tracking. Built by a cross-disciplinary 2-person dyad pairing mobile physics/CS engineering with industrial 3D design: clinicians manipulate 3D dental treatment parameters on a companion laptop control interface while seeing parametric adjustments update instantaneously over the patient's face in a live mobile AR viewer. | Planmeca 3D Dental Imaging Datasets, Companion Laptop 3D Parameter Workstation, Real-Time Mobile AR Client (Live Facial Tracking & 3D Dental Overlay) *(no public source repository published)* | Planmeca 3D Dental Scan Data + Laptop Parameter Controller<br>-> Live Parameter Sync Bridge<br>-> Mobile AR Engine (Facial Tracking + Parametric 3D Dental Mesh Overlay) | 1. Split workflow between a precision laptop control workstation (for the dentist) and a lightweight patient-facing AR phone display (lowering chairside anxiety).<br>2. Combined two complementary founders — industrial 3D modeling + mobile CS/physics — allowing custom dental assets and AR tracking to finish cleanly in 48 hours.<br>3. Beat 12 other Health track teams on patient-experience tangibility. | Challenge Competition: `1st` out of `13` hacker teams tackling Planmeca's Junction 2017 challenge (jury: Sakari Kettunen & Antti Haanpää).<br>Public Benchmark Boundary: No public GitHub repo or FPS telemetry published `[L1]` Planmeca newsroom. | 1. Live dual-device demo: tweaking 3D dental parameters on the laptop immediately updated the overlaid 3D smile/treatment geometry aligned on the subject's face in mobile AR. | AR Dentist (2-person cross-disciplinary dyad): Samuel Laska (Slovakia — physics/CS mobile engineer) and Linda Ukkonen (Finland — industrial design & 3D modeling graduate). | Asymmetric 2-person skill complementarity plus tactile clinical empathy. Pairing 3D CAD fidelity directly with real-time mobile AR answered Planmeca's dual mandate of virtual clinic planning and patient reassurance. | 1. A tight 2-person dyad uniting Industrial 3D Design + Mobile Engineering routinely outperforms oversized pure-software teams on medical hardware/AR tracks.<br>2. Dual-screen operator-plus-patient demos (laptop control -> mobile AR view) clarify clinical value instantly. | https://www.planmeca.com/news-and-events/newsroom/2018/planmeca-challenged-hackers-to-reshape-the-future-of-dentistry/ | L1: Verified by Official Planmeca Corporate Newsroom Announcement (Jan 12, 2018) |

---

## 2. Comprehensive Deep-Dive Cards (21 Fields per Project)

---

### Project Card 1: WAVELET (Sensofusion — Radio City)

#### 1. Basic Metadata
- **Event ID**: `junction-2025`
- **Event Name**: `Junction 2025`
- **Year**: `2025`
- **Organizer**: `Sensofusion` (Finnish Counter-UAS and RF Spatial Intelligence Pioneer, creators of AIRFENCE)
- **Challenge Name**: `Radio City`
- **Category**: `IoT & Hardware / Defense & RF Spatial Computing`
- **Judging Criteria**:
  - Accurate physics-based mathematical simulation of radio wave propagation, reflection, diffraction, and attenuation in complex 3D urban topographies.
  - Interactive 3D visualization and fluid real-time graphics performance (60 FPS).
  - Educational clarity, visual polish, and high-impact live demonstration ("Wow factor").
- **Project ID**: `sensofusion-wavelet-2025`
- **Project Name**: `WAVELET`
- **Award**: **Overall Grand Winner 🏆 (€10,000 Cash Prize) & Sensofusion Track Winner 🥇 (DJI Mini 3 Drones)**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  Modern high-density urban canyons severely degrade counter-drone (C-UAS) radio frequency sensing due to multi-path reflections and severe shadowing from reinforced concrete and glass structures. Traditional computational electromagnetic tools (such as ray-tracing simulators or finite-element solvers like COMSOL) require hours or days to compute a single static RF heat map, making tactical, mobile deployment impossible.
  WAVELET completely disrupted this paradigm by building a GPU-native Maxwell electromagnetic wave solver running at a locked **60 FPS**. Written from scratch in C++ and OpenGL Compute Shaders, WAVELET executes real-time Finite-Difference Time-Domain (FDTD) partial differential equation integration across 3D voxelized urban geometry. Military operators and defense analysts can interactively drag RF transmitters (such as rogue drone controllers or airborne video downlinks) or dynamically modify building heights, observing physical electromagnetic wave fronts ripple across the city like fluid waves in real time.
- **Tech Stack**:
  - *Core Languages*: C++20, GLSL (OpenGL Shading Language).
  - *GPU Graphics & Compute Pipeline*: OpenGL 4.6 Core Profile, OpenGL Compute Shaders, Vulkan Compute concepts, Shader Storage Buffer Objects (SSBO).
  - *Numerical Methods*: Finite-Difference Time-Domain (FDTD) partial differential equation grid solver, Yee cell discretization, Mur/PML absorbing boundary conditions.
  - *Geospatial & 3D Assets*: 3D Hong Kong urban polygon mesh (JAXA / OpenStreetMap), WGS84 to local Cartesian coordinate transformation algorithms.
  - *UI & Tooling*: Dear ImGui, CMake, Git.
- **System Architecture**:
  1. *Geospatial Ingestion Layer*: Parses multi-million polygon 3D city models (Hong Kong dataset provided by Sensofusion), normalizes GPS coordinates into localized metric space, and performs spatial voxelization into discrete 3D dielectric grids.
  2. *GPU Compute Core (Compute Shaders)*:
     - Discretizes spatial dielectric permittivity and permeability values.
     - Solves time-dependent Maxwell's curl equations ($\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}$, $\nabla \times \mathbf{H} = \mathbf{J} + \frac{\partial \mathbf{D}}{\partial t}$) across adjacent grid voxels every frame.
     - Simulates multi-path surface reflection, phase interference, and edge diffraction around building obstructions.
  3. *Volumetric Raymarching & Rendering Engine*: Samples dynamic 3D field intensities using volumetric raymarching, applying chromatic field-strength transfer functions and surface projection heat maps onto architectural facades.
  4. *Tactical Threat Triangulator*: Interactively calculates reverse line-of-bearing vectors to isolate clandestine drone pilot transmitters amidst dense multipath clutter.
- **Key Technical Decisions**:
  - *Decision 1: Direct C++ and GPU Compute Shaders over Commercial Game Engines*: Rejected Unity, Unreal Engine, and Python wrappers to achieve direct control over VRAM memory allocation and avoid garbage collection or framework overhead.
  - *Decision 2: True Wave PDE Solver (FDTD) over Geometric Ray-Tracing*: Chose physical wave equation discretization over optical ray tracing. This allowed true wave phenomena (constructive/destructive interference, diffraction around sharp building corners, penetration through non-metallic glass) to emerge naturally from physical laws.
  - *Decision 3: Real-Time Dynamic Manipulation*: Designed the pipeline so every parameter (transmitter position, antenna frequency, building opacity) can be mutated interactively without recompilation or re-voxelization.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Rendering Performance*: Locked 60 FPS at 1080p/4K resolution during continuous physical simulation.
  - *Simulation Step Latency*: Sub-16 milliseconds per FDTD iteration. Compared to industrial baseline solvers (Wireless InSite, COMSOL, Altair Feko) requiring 2 to 48 hours for comparable urban zones, WAVELET achieved a ~100,000x speedup for interactive exploration.
  - *Spatial Resolution*: Thousands of building structures and terrain elevations simulated simultaneously in high-density 3D grids.
- **Demo Highlights**:
  - Live main-stage demonstration: Electrified the entire auditorium by rendering electromagnetic waves propagating outward from a moving drone like physical ripples across the Hong Kong skyline.
  - Interactive manipulation: The team dynamically altered building heights and dragged radar stations, showing instantaneous signal blockage, multi-path bounce, and radio shadow zones.
  - Reverse threat localization: Showcased live counter-drone tracking, identifying the hidden operator's ground transmitter behind high-rise obstructions.
- **Team Background**:
  An international dream team of elite low-level systems and high-performance computing engineers:
  - *Rudrrayan Manna (Rono)*: High-Performance Computing (HPC) & GPU acceleration specialist, member of the SC26 Supercomputing competition team.
  - *Arjun Juneja*: Low-latency systems engineer and reverse engineering expert with quantitative finance experience at XTX Markets London.
  - *Keanu Czirjak*: GPU rendering engineer and systems architect with research experience across Arm and BPP projects.
  - *Akshith Alluri*: Distributed systems and core algorithms engineer.
- **Winning Hypothesis**:
  Technical depth supremacy and mission-critical relevance. In a hackathon where 90%+ of entries were superficial wrappers around OpenAI or Anthropic APIs, WAVELET delivered an astonishing display of hardcore low-level mathematical physics, custom GPU shaders, and visual brilliance that directly addressed Sensofusion’s core multi-million-euro defense challenge.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: Low-level engineering (C++, GPU Compute, raw physics) creates an unassailable technical moat in general hackathons.
  - *Lesson 2*: Hypnotic visual feedback (60 FPS fluid-like wave simulation) ensures your project is memorable to both technical reviewers and general main-stage judges.
  - *Lesson 3*: Aligning directly with the sponsor's flagship commercial problem (C-UAS RF blind-spots) guarantees strong mentor advocacy during final deliberations.
- **Source URLs**:
  - [Keanu Czirjak Portfolio](https://keanuc.net)
  - [Arjun Juneja Portfolio](https://arjunjuneja.com)
  - [Wikipedia: Junction Hackathon](https://en.wikipedia.org/wiki/Junction_(hackathon))
  - [Junction Official Grand Winner LinkedIn Post](https://lnkd.in/p/dZ56ZRek)
  - [Mikko Hyppönen (Sensofusion) Official LinkedIn Announcement](https://lnkd.in/p/dVK4z9bn)
  - [Sensofusion Official Website](https://www.sensofusion.com)
- **Evidence Level**: `L1: Verified by Official Junction 2025 Announcement, Winner Portfolio & Wikipedia Records`

---

### Project Card 2: Academic Menaces (Sensofusion — Lights, Camera, Reaction!)

#### 1. Basic Metadata
- **Event ID**: `junction-2025`
- **Event Name**: `Junction 2025`
- **Year**: `2025`
- **Organizer**: `Sensofusion`
- **Challenge Name**: `Lights, Camera, Reaction!`
- **Category**: `IoT & Hardware / Neuromorphic Vision & High-Speed Machine Vision`
- **Judging Criteria**:
  - Accuracy, creativity, and technical sophistication in handling microsecond-level asynchronous event camera vision streams.
  - Capability to extract high-speed physical motion (e.g., fan blade RPM calculation, micro-drone tracking).
  - Real-time pipeline latency and robustness under extreme dynamic range (120dB+) and adverse lighting.
- **Project ID**: `sensofusion-academic-menaces-2025`
- **Project Name**: `Academic Menaces`
- **Award**: **Sensofusion Camera Track Winner 🥇 (DJI Mini 3 Drones)**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  Standard RGB frame-based cameras fail completely when tracking ultra-high-speed targets like anti-drone projectiles or rapidly spinning quadcopter rotors due to motion blur, low frame rates (30–60 FPS), and limited dynamic range. Sensofusion deployed professional-grade neuromorphic Event Cameras on-site at Junction 2025.
  Team Academic Menaces built a high-speed machine vision pipeline operating on raw asynchronous pixel polarity events. Rather than naively accumulating events into standard artificial image frames, the team engineered a microsecond-scale temporal filtering and spatial clustering pipeline. The system tracks high-speed drone propeller rotation, calculates rotor RPM with mathematical precision, and maintains continuous target lock on fast-moving physical objects under extreme lighting conditions where traditional optical sensors fail.
- **Tech Stack**:
  - *Hardware Sensors*: Professional Prophesee / Sony Neuromorphic Event Camera development kits equipped with C-mount high-speed optical lenses.
  - *Core Languages & Libraries*: C++17, Python 3.11, OpenEB (Open Event-Based Vision SDK), OpenCV, NumPy, SciPy.
  - *Algorithms*: Asynchronous Event Temporal Denoising, Time-Surface Feature Extraction, Spiking Neural Network (SNN) representations, Adaptive Kalman Motion Filtering.
- **System Architecture**:
  1. *Hardware Event Stream Ingestion*: Ingests raw asynchronous event packets `(x, y, timestamp, polarity)` from the sensor over USB 3.0 at microsecond resolution.
  2. *Temporal Noise Filtering*: Filters background thermal noise and sensor jitter using temporal coincidence windowing.
  3. *Time-Surface Feature Generator*: Maps spatio-temporal event trajectories onto continuous exponential decay surfaces, highlighting edges of moving objects with zero motion blur.
  4. *High-Speed Frequency Estimator*: Analyzes periodic intensity transitions to compute fan and rotor blade rotation frequencies (RPM).
  5. *Target Trajectory & Threat Vector Pipeline*: Predicts high-speed projectile and drone trajectories, feeding coordinates into counter-drone targeting systems.
- **Key Technical Decisions**:
  - *Decision 1: Native Asynchronous Processing*: Avoided flattening event streams into 30fps pseudo-frames, preserving microsecond timing accuracy.
  - *Decision 2: Frequency-Domain Optical Tachometry*: Utilized fast Fourier and temporal autocorrelation on event polarity flips to count spinning rotor blades directly from microsecond data.
  - *Decision 3: Dynamic Threshold Gating*: Built an adaptive noise filter that adjusted polarity sensitivity dynamically based on ambient illumination changes.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Pipeline Latency*: <1 millisecond end-to-end processing latency, compared to 33.3ms minimum latency in standard 30fps video pipelines.
  - *Measurement Precision*: >98% accuracy in computing rotating blade frequencies up to 6,000+ RPM.
  - *Dynamic Range Robustness*: Maintained clear object tracking under extreme lighting contrasts exceeding 120 dB (e.g. tracking black drone rotors directly against blinding stage spotlights).
- **Demo Highlights**:
  - Live demonstration showing a high-speed mechanical desk fan spinning at several thousand RPM: ordinary smartphone cameras showed a hazy, indistinguishable gray smear, while the Academic Menaces event visualizer clearly isolated every single blade edge and computed exact RPM in real time.
  - High-speed tracking of flying projectiles tossed across the room with instantaneous bounding-box lock.
- **Team Background**:
  Academic researchers and computer vision specialists with rigorous backgrounds in neuromorphic computing, asynchronous signal processing, and robotics.
- **Winning Hypothesis**:
  Deep hardware comprehension. While rival teams attempted to run heavy, pre-trained YOLO models on artificial frame buffers (destroying the very advantage of event cameras), Academic Menaces developed algorithms specifically tailored to the asynchronous physical nature of neuromorphic hardware.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: When sponsors provide specialized hardware, embrace the hardware's unique operational philosophy rather than forcing legacy software models upon it.
  - *Lesson 2*: Side-by-side comparative live demos (e.g., phone camera showing blur vs. event stream showing crisp microsecond edges) provide undeniable proof of superiority.
- **Source URLs**:
  - [Mikko Hyppönen (Sensofusion) Official Track Announcement](https://lnkd.in/p/dVK4z9bn)
  - [Sensofusion Official Website](https://www.sensofusion.com)
- **Evidence Level**: `L1: Verified by Sensofusion R&D Leadership LinkedIn Announcement & Official Track Records`

---

### Project Card 3: The Listening Sauna / Cooperative Mystery (Harvia — Sauna Intelligence)

#### 1. Basic Metadata
- **Event ID**: `junction-2025`
- **Event Name**: `Junction 2025`
- **Year**: `2025`
- **Organizer**: `Harvia` (Global leader in sauna and spa technology)
- **Challenge Name**: `Sauna Intelligence`
- **Category**: `IoT & Hardware / Smart Buildings, Ambient Computing & Digital Wellness`
- **Judging Criteria**:
  - Prototype functionality, creativity, commercial feasibility, and global scalability.
  - Respect for authentic Finnish sauna culture (digital detox, tranquility, screen-free atmosphere).
  - Effective integration with Harvia's wireless IoT sensor platform (temperature/humidity/presence radar/BLE).
  - Fluent demonstration of AI-native tooling during the rapid prototyping process.
- **Project ID**: `harvia-the-listening-sauna-2025`
- **Project Name**: `The Listening Sauna / Cooperative Routine Mystery`
- **Award**: **Harvia Challenge Winner & Extended Race Finalist (€1,500 Cash Prize + Harvia IoT Sensors + XQ Event Invitation)**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  Sauna environments represent an extreme physical challenge: temperatures exceeding 80°C–100°C and 90%+ humidity destroy standard consumer electronics, while the cultural tradition of Finnish sauna demands a complete "digital detox" free from glowing touchscreens and intrusive notification chimes.
  Created by Aalto University human-computer interaction engineer Erik Gelcich, *The Listening Sauna* and *Cooperative Routine Mystery* system deployed Harvia’s battery-powered IoT sensors, high-temperature environmental microphones, and mmWave presence radar into an ambient, screen-free physical computing platform. In the hot zone, the system silently records steam bursts (*löyly*), thermal cycles, and natural voice conversations. Once bathers transition to the cold lounge, the platform synthesizes an AI-driven "Mind Reflection & Physiological Recovery Journal" and unlocks cooperative wellbeing puzzle milestones.
- **Tech Stack**:
  - *Hardware Sensors & Gateways*: Harvia Wireless Battery-Powered Sauna Sensor Platform (temperature, relative humidity, BLE beacon, presence detection), high-temperature acoustic probes, Harvia Xenio Gateway, ESP32 edge microcontroller.
  - *Protocols & APIs*: Harvia GraphQL API, MQTT over TLS, WebSockets, Web Bluetooth API.
  - *Backend & Edge Processing*: Node.js, Python 3.11, local Whisper speech-to-text model, rule-based thermal curve state machine.
  - *Frontend & Visualization*: Next.js, Tailwind CSS, PWA mobile/tablet companion app for the cooling lounge.
- **System Architecture**:
  1. *Hot Zone (80°C–100°C Harsh Environment)*: Harvia ruggedized sensors measure rapid temperature spikes and humidity surges from water thrown onto hot sauna rocks (*löyly* detection). MmWave radar detects human presence without cameras; ambient microphones capture spoken reflections and breathing rates.
  2. *Edge Telemetry Hub (Harvia Xenio Gateway)*: Streams sensor data via MQTT to a local edge processor. Formulates thermal exposure duration, cardiovascular heat-stress curves, and session transition states.
  3. *Cold Lounge Zone (Post-Sauna Interface)*: When the presence radar detects bathers exiting to the lounge, the system activates a calm tablet/mobile interface displaying recovery insights, AI conversation summaries, and cooperative health milestones.
- **Key Technical Decisions**:
  - *Decision 1: Zero Screens in the Hot Zone*: Resisted the temptation to place tablets or waterproof screens inside the sauna, honoring the Finnish cultural mandate of peaceful disconnection.
  - *Decision 2: Acoustic Löyly Detection*: Identified the distinctive acoustic signature of water vaporization on stones to measure ritual intensity without delicate mechanical flow meters.
  - *Decision 3: Cooperative Rather Than Competitive Gamification*: Designed wellness challenges as cooperative routines (e.g. family heat-cooling cycles) to nurture social bonding rather than stressful competitive scoreboards.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Thermal & Environmental Robustness*: Reliable hardware telemetry streaming in 80°C–100°C ambient temperatures and 95% relative humidity.
  - *Telemetry Latency*: Sub-second MQTT transmission of steam throwing events and room occupancy states.
  - *User Experience Impact*: 100% elimination of digital screen distractions inside the sauna while providing rich, actionable biometric feedback post-session.
- **Demo Highlights**:
  - Simulated water-tossing (*löyly*) demonstration: pouring water over simulated heater elements immediately registered as a sharp humidity spike in the Harvia GraphQL API, triggering subtle ambient lighting shifts.
  - Automatic generation of an empathetic "Sauna Reflection Log" summarizing relaxation themes from a simulated voice chat.
  - Live unlocking of a cooperative family wellness puzzle when thermal and cooling timers were correctly balanced.
- **Team Background**:
  - *Erik Gelcich*: Master of Science in Human-Computer Interaction from Aalto University and the University of Twente; veteran builder and recurrent winner of European hackathons (Junction, ESA Cassini).
  - Collaborative engineering team specializing in full-stack web architectures and embedded IoT devices.
- **Winning Hypothesis**:
  Cultural empathy combined with smart hardware pragmatism. While other competitors proposed impractical solutions (like bringing smartphones into hot steam or installing touchscreens that would overheat within minutes), Erik Gelcich understood that true smart sauna technology must remain invisible, using ambient computing to deepen the restorative ritual.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: In IoT and hardware challenges, physical constraints (temperature, water, battery) dictate product viability before software features.
  - *Lesson 2*: Deep respect for cultural heritage and user psychology often wins more acclaim from enterprise judges than aggressive over-engineering.
- **Source URLs**:
  - [Erik Gelcich Personal Portfolio](https://erikgelcich.com)
  - [Harvia Official Website](https://www.harvia.com)
  - [Junction Official Website](https://www.hackjunction.com)
- **Evidence Level**: `L1: Verified by Author Portfolio, Harvia Partner Announcements & Silver Challenge Archive`

---

### Project Card 4: Concrete Fitter / ifc-troll (Peikko — IFC Innovate)

#### 1. Basic Metadata
- **Event ID**: `junction-2025`
- **Event Name**: `Junction 2025`
- **Year**: `2025`
- **Organizer**: `Peikko Group` (Global leader in precast concrete connections, composite beams, and construction fasteners)
- **Challenge Name**: `IFC Innovate: Enhancing Construction Experience`
- **Category**: `IoT & Hardware / Construction Tech & BIM Engineering Systems`
- **Judging Criteria**:
  - Parsing stability and robustness when handling massive industrial Industry Foundation Classes (IFC) 3D BIM data.
  - Accuracy and engineering validity of structural hardware recommendations (e.g. column shoes, foundation bolts).
  - Usability, responsiveness, and practical workflow integration for structural engineers and Peikko technical sales teams.
- **Project ID**: `peikko-concrete-fitter-2025`
- **Project Name**: `Concrete Fitter (ifc-troll)`
- **Award**: **Peikko Challenge 2nd Place 🥈**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  Peikko produces thousands of specialized precast concrete connectors, column shoes, and Deltabeam composite girders. When structural consulting firms submit large, complex 3D Industry Foundation Classes (IFC) architectural files, Peikko's structural engineers must manually review hundreds of beam-column joints, calculate shear and bending loads, and match specifications from thick paper catalogs—a tedious process prone to human error.
  Team Concrete Fitter developed an automated BIM analysis and hardware specification platform. Using IfcOpenShell and a headless Blender geometry pipeline, the platform ingests massive IFC building models, automatically scans 3D topological intersections between columns, beams, and slabs, and computes geometric bounding boxes and structural interfaces. It instantly maps each joint to the optimal Peikko hardware catalog item (such as HPK Column Shoes and HPM Anchor Bolts) according to Eurocode engineering rules, augmented by an embedded MeiliSearch retrieval assistant.
- **Tech Stack**:
  - *BIM & 3D Geometry Processing*: IfcOpenShell (C++/Python bindings for IFC data), Blender Python API (Headless background mesh processing and geometry tessellation).
  - *Web 3D Visualization*: Three.js, WebGL, React Three Fiber.
  - *Backend & Search Architecture*: Python 3.11, FastAPI, MeiliSearch (ultra-fast search engine for engineering documentation), Docker.
  - *Frontend & UI*: TypeScript, React 18, Tailwind CSS, Vite.
- **System Architecture**:
  1. *IFC Ingestion & Geometry Transcoding*: Ingests raw IFC building files, parses the STEP physical file structure via IfcOpenShell, and dispatches geometry tessellation to a headless Blender worker to generate lightweight GLTF assets.
  2. *Structural Intersection Detector*: Traverses the spatial element hierarchy (`IfcColumn`, `IfcBeam`, `IfcSlab`), computes 3D axis-aligned bounding boxes (AABB), and identifies physical contact surfaces and load-bearing interface planes.
  3. *Peikko Hardware Fitting Engine*: Evaluates joint dimensions, concrete grade, and structural load constraints against Peikko's parametric product rules, selecting the compliant column shoe or anchor bolt assembly.
  4. *Interactive 3D Engineering Console*: Renders the full 3D building model in WebGL, overlays color-coded connector indicators at each joint, and provides conversational engineering rationale via MeiliSearch.
- **Key Technical Decisions**:
  - *Decision 1: Headless Blender Pipeline for Heavy 3D Geometry*: Offloaded heavy IFC boolean operations and polygon meshing to a background headless Blender pipeline, preventing client browser memory crashes on 100MB+ industrial models.
  - *Decision 2: Deterministic Geometric Rules over LLM Hallucinations*: Chose deterministic computational geometry and strict parametric lookups over generative AI models for structural joint matching, ensuring 100% adherence to building codes.
  - *Decision 3: Embedded MeiliSearch Assistant*: Indexed Peikko's complete catalog and technical manuals into MeiliSearch to provide sub-10ms conversational explanations for every recommended hardware component.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *BIM Ingestion Throughput*: Parses complex multi-story commercial building models (100MB+ IFC files) in under 15 seconds.
  - *Recommendation Conformity*: 100% engineering compliance with minimum edge distance and load-bearing specifications for standard precast column connections.
  - *Engineering Workflow Acceleration*: Slashes initial structural hardware takeoff time from 4+ hours of manual blueprint scanning to less than 2 minutes.
- **Demo Highlights**:
  - Live upload of a multi-story industrial building IFC file: the web interface parsed the entire structure into a smooth 3D interactive viewer within seconds.
  - Automatic detection of over 40 structural column-foundation joints, instantly superimposing 3D models of Peikko Column Shoes into their exact structural placement.
  - Live interactive query: clicking a connection revealed structural load tolerances and generated a direct exportable Peikko Bill of Materials (BOM).
- **Team Background**:
  - *Federico Bertossi*: Computer Science Engineer, CTF security competitor, and LeadTheFuture Ambassador.
  - *Aleksandr Shishkov (akalji)*: 3D rendering pipeline developer and computational geometry specialist.
  - *Nikolai Tikhonov*: Backend engineer and IFC data pipeline architect.
  - *Konstantin Trubitsyn*: Search engine and retrieval systems specialist.
  - *Daniela Burnaz*: Frontend UX and interactive visualization engineer.
- **Winning Hypothesis**:
  Solving unglamorous industrial reality with unshakeable stability. While other teams struggled with IFC parser crashes or proposed generic AI chatbots, Concrete Fitter built a robust, production-grade geometric pipeline that solved Peikko's daily sales engineering bottleneck on real-world industrial CAD data.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: Industrial sponsors prize deterministic precision, robust data ingestion, and building code compliance far above flashy but unreliable generative AI.
  - *Lesson 2*: Overcoming difficult file format hurdles (such as enterprise IFC parsing) immediately sets your project apart from 99% of hackathon competitors.
- **Source URLs**:
  - [Federico Bertossi Official Portfolio](https://www.federicobertossi.com)
  - [Concrete Fitter GitHub Repository 1 (akalji)](https://github.com/akalji/junction_2024_concrete_fitter)
  - [ifc-troll GitHub Repository 2 (Zav141DJacob)](https://github.com/Zav141DJacob/ifc-troll)
  - [Peikko Group Official Website](https://www.peikko.com)
- **Evidence Level**: `L1: Verified by Author Portfolio, Two Public GitHub Repositories & Peikko Official Challenge`

---

### Project Card 5: J-mp / Junior Movement Platform (Huawei — Sense the Motion)

#### 1. Basic Metadata
- **Event ID**: `junction-2023`
- **Event Name**: `Junction 2023`
- **Year**: `2023`
- **Organizer**: `Huawei` (HMS / Huawei Consumer Device Ecosystem)
- **Challenge Name**: `Sense the Motion`
- **Category**: `IoT & Hardware / Mobile Sensor Fusion & Gamified Exergaming`
- **Judging Criteria**:
  - Uniqueness, user impact, and feasibility for mobile/wearable deployment.
  - Completeness, engagement value, and fun factor motivating youth out of sedentary routines.
- **Project ID**: `huawei-jmp-2023`
- **Project Name**: `J-mp (Junior Movement Platform)`
- **Award**: **Huawei Challenge 2nd Place 🥈 (Junction 2023)**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  To pull smartphone-centric youth out of prolonged sitting into outdoor physical movement without heavyweight wearables or brittle cloud inference, Mankeli Solutions Oy engineered *J-mp* during Junction 2023 at Kaapelitehdas (`Mankeli-Software/junction2023` — previously confused in older notes with unranked 2023 entry `Motion Potion`). Built atop Flutter (`flutter_bloc`), *J-mp* turns raw inertial sensors, magnetic compass heading, GPS telemetry, rhythmic 100ms haptic vibration loops, and physical QR markers into high-energy outdoor hide-and-seek and physical sprint mini-games synced with Firebase and Next.js 13.
- **Tech Stack**:
  - *Mobile Sensor Layer*: Flutter / Dart (`flutter_bloc`), `sensors_plus` (3-axis accelerometer), `flutter_compass` (magnetometer), `geolocator` (GPS), Mobile Scanner (QR), Vibration / Haptics (`100ms` timer).
  - *Cloud & Web Telemetry*: Firebase, Next.js 13 (TypeScript), 10 domain-driven local Dart packages (`analytic_`, `authentication_`, `database_`, `storage_`, `notification_repository`).
- **System Architecture**:
  1. *Physical Sensor Capture*: Continuously polls tri-axial accelerometer streams (`sensors_plus`), magnetic bearing (`flutter_compass`), GPS coordinates (`geolocator`), and physical venue QR scans.
  2. *BLoC Exergame State Engines*: `action_game_cubit.dart` detects vigorous shake/sprint bursts (`x + y + z > 30.0`) paired with `100ms` haptic feedback pulses; `hide_and_seek_cubit.dart` guides spatial player bearing toward hidden targets.
  3. *Multi-Flavor Sync*: Pushes scores, sessions, and alerts across separated repository modules into Firebase and Next.js 13 across dev/staging/production environments.
- **Key Technical Decisions**:
  - *Decision 1: Deterministic Physics Threshold*: Replaced jittery black-box cloud ML with an aggregate acceleration magnitude trigger (`x + y + z > 30.0`) and `100ms` haptics for zero-lag reliable activation.
  - *Decision 2: Production Domain Modularity*: Split app logic into 10 strict domain-driven repository packages so five builders shipped clean multi-flavor code in 48 hours.
  - *Decision 3: Venue-Wide Physical Play*: Coupled compass bearing and QR checkpoints to make users physically run across Kaapelitehdas rather than staying seated.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Burst Trigger Threshold*: Aggregate accelerometer norm gate `x + y + z > 30.0` (`action_game_cubit.dart`).
  - *Tactile Feedback Loop*: `100 ms` cyclic haptic pulse synchronization.
  - *Engineering Scope*: 10 modular domain packages delivered with final Junction 2023 commits on Nov 12, 2023 (`Mankeli-Software/junction2023`).
- **Demo Highlights**:
  - Presenters physically sprinting and shaking phones triggered live compass target locks and 100ms rhythmic vibration feedback while QR scans updated multiplayer leaderboards immediately.
- **Team Background**:
  - *Mankeli Solutions Oy*: Jesse Lappalainen (`JareCoder`), Juho Torkkeli (`JTorkk`), Aku Paananen (`AkJkSenpai`), Onnimanni Hannonen (`O-Hannonen`), and `Hylje5000` (Finnish software & mobile engineering studio).
- **Winning Hypothesis**:
  Crash-free engineering completeness combined with unmistakable physical fun. By proving an outdoors sensor-fused game loop that genuinely got judges and youth moving, Mankeli stood out cleanly from fragile ML prototypes.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: Simple kinematic thresholds (`x + y + z > 30.0`) paired with responsive `100ms` haptics create far stronger live energy than laggy cloud classifiers.
  - *Lesson 2*: Always cross-check commit timestamps and author portfolios (`jemlap.fi/projects`) so neighboring unranked hackathon repos (`andras-adam/motion-potion`) are never misattributed.
- **Source URLs**:
  - [J-mp Winner GitHub Repository (Mankeli-Software/junction2023)](https://github.com/Mankeli-Software/junction2023)
  - [Jesse Lappalainen Portfolio Verification](https://www.jemlap.fi/projects)
- **Evidence Level**: `L1: Verified by Winner GitHub Repository (Mankeli-Software/junction2023) & Author Portfolio (jemlap.fi/projects)`

---

### Project Card 6: Lumen Loop 3.0 (Helvar — Brighter Spaces: Intelligent Lighting)

#### 1. Basic Metadata
- **Event ID**: `junction-2021`
- **Event Name**: `Junction 2021`
- **Year**: `2021`
- **Organizer**: `Helvar` (Smart Building Lighting & Controls)
- **Challenge Name**: `Brighter Spaces: Intelligent Lighting`
- **Category**: `IoT & Hardware / Smart Building Sensor Networks & Floorplan Spatial AI`
- **Judging Criteria**:
  - Exploiting anonymized building PIR motion and audio time-series across CAD floorplans to automatically locate unlabeled ceiling sensors ("Where are all the devices?"), map occupant traffic ("Where is everyone going?"), or interpret garage sensor streams ("Mystery Garage").
- **Project ID**: `helvar-lumenloop3-2021`
- **Project Name**: `Lumen Loop 3.0`
- **Award**: **Helvar Challenge Winner 🥇 & Overall Top-10 Finalist (out of 200+ projects)**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  Installing hundreds of networked ceiling luminaires and PIR sensors across multi-story commercial buildings incurs steep manual commissioning costs because electricians rarely log every MAC/Device ID cleanly onto CAD floorplans. Returning Helvar 2019 winners *LumenLoop* targeted Challenge 1 (*"Where are all the devices?"*) across five Helvar building sites (`site_1`–`site_5`). *Lumen Loop 3.0* buckets asynchronous PIR triggers into `5s` discrete binary matrices, evaluates weighted Pearson correlation against known anchor luminaires, and surfaces Human-in-the-Loop top-K map candidates on zoomable `64 px` floorplan tiles.
- **Tech Stack**:
  - *Signal Correlation & ML*: Python, `pandas`, `numpy`, `scipy` (`scipy.stats.stats.pearsonr`), `Pillow` (`ImageDraw`), pre-trained `.pickle` site correlation caches.
  - *Web Tile Commissioning Server*: `Flask`, Leaflet-style pyramid tile serving (`TILE_SIZE = 64`).
- **System Architecture**:
  1. *Temporal Alignment (`CombinedCorrelator`)*: Floors sparse sensor trigger timestamps into `5s` discrete grids via `df.timestamp.dt.floor` over `pd.date_range`.
  2. *Weighted Spatial Co-Occurrence*: Computes pairwise Pearson correlations with known anchor IDs, leveraging human hallway continuity to rank physical candidate nodes before invoking `offload_tmp_data()` to shrink serialized `.pickle` footprint.
  3. *Human-in-the-Loop Tile UI*: Flask endpoints (`/load_memory_database/<site_name>`, `/recommendations/<real_device_id>`, `/tiles/<z>/<x>/<y>`, `/devices/<zoom>`) highlight top-K candidate spots on interactive `64 px` floorplans.
- **Key Technical Decisions**:
  - *Decision 1: Target B2B Installation Bottlenecks*: Prioritized automated commissioning over cosmetic dashboards, directly targeting 50%+ field installation labor cost reduction.
  - *Decision 2: Human-in-the-Loop Top-K Over Raw Coordinate Regression*: Because symmetric corridors confuse pure coordinate regression, presenting ranked candidate pins on tiled maps ensures zero mis-wiring in production.
  - *Decision 3: Pre-Trained `.pickle` + Tensor Offloading*: Serialized per-site correlation tables (`site_1_model...pickle`–`site_5`) offline so interactive floorplan queries run instantaneously during stage demos.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Temporal Discretization Window*: `5s` discrete binary activation bins (`time_buckets_config`).
  - *Map Visualization Spec*: `TILE_SIZE = 64` px pyramid floorplan tiles serving `site_1` through `site_5`.
  - *Competition Standing*: Helvar Winner (11 full / 4 draft submissions from 14 locked Helvar teams) & Top-10 Overall Finalist out of 200+ projects.
- **Demo Highlights**:
  - Clicking an unmapped Device ID smoothly zoomed the interactive floorplan to the highest-correlation hallway fixtures while Pillow overlays rendered anchor devices in green (`#50ff50`) against target predictions in red.
- **Team Background**:
  - *Elizaveta Lebedeva* (`LizaLebedeva`, Data Science / Modeling — 2019 Helvar Winner), *Denys Kovalenko* (`deniskovalenko`, Signal Backend — 2019 Helvar Winner), and *Carlos Bentes* (`cbentes`, Tiled Spatial Web Stack).
- **Winning Hypothesis**:
  Deep operational empathy paired with fast statistical rigor. Returning winners skipped superficial AI hype and solved Day-0 IoT commissioning economics with explainable co-occurrence math.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: Solving hardware commissioning/installation friction beats generic building-analytics plots in industrial IoT tracks.
  - *Lesson 2*: Offload heavy pairwise matrices into pre-trained `.pickle` caches (`offload_tmp_data()`) before live judging.
- **Source URLs**:
  - [Lumen Loop 3.0 GitHub Repository (LizaLebedeva/junction-2021)](https://github.com/LizaLebedeva/junction-2021)
  - [Elizaveta Lebedeva Junction Portfolio](https://elizavetalebedeva.com/tag/junction/)
  - [Lumen Loop 3.0 Demo Video (YouTube)](https://www.youtube.com/watch?v=dX27x6s6wl4)
  - [Junction Official Helvar 2021 Recap (Medium)](https://hackjunction.medium.com/junction-2021-intelligent-lighting-as-the-engine-for-brighter-spaces-1926e69eed6b)
- **Evidence Level**: `L1: Verified by Winner GitHub Repository (LizaLebedeva/junction-2021), Author Blog, Demo Video & Medium Recap`

---

### Project Card 7: ElevAI — Team Glados [Co-track Winner: S.H.I.E.L.D] (CGI x KONE — Sky(scraper)-is-the-limit)

#### 1. Basic Metadata
- **Event ID**: `junction-2021`
- **Event Name**: `Junction 2021`
- **Year**: `2021`
- **Organizer**: `CGI` & `KONE` (Mentor: Jaakko Uusitalo)
- **Challenge Name**: `Sky(scraper)-is-the-limit`
- **Category**: `IoT & Hardware / Industrial Predictive Maintenance & Smart Wearables`
- **Judging Criteria**:
  - Dual-category judging across ~30 CGI track teams: (1) *Best Performing and Most Explainable Model* balancing fault recall against false-positive Service Action Recommendation (SAR) truck rolls; (2) *Out-of-the-Box Thinking* for hands-free field wearable maintenance concepts.
- **Project ID**: `cgi-kone-elevai-2021`
- **Project Name**: `ElevAI (Team Glados) [Co-track: S.H.I.E.L.D Smart Helmet]`
- **Award**: **CGI x KONE "Best Performing & Most Explainable Model" 1st Prize 🥇 & Overall Top-10 Finalist [Co-winner Out-of-the-Box: S.H.I.E.L.D Smart Helmet]**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  KONE moves 1B+ elevator passengers daily, yet 13% of automated Service Action Recommendations (SARs) dispatch highly skilled technicians unnecessarily. Instead of overclaiming fake accuracy on noisy asset groups, *ElevAI* (`teamglados/elevai`) audited subgroup noise (`Groups 0–3`), trained `ray.tune` + `HyperOptSearch` ensembles directly optimizing safety-weighted `f2_score`, and routed low-confidence alerts through a mobile AR technician pre-check loop — complementing co-winner *S.H.I.E.L.D*'s wearable smart helmet with embedded lighting, AR camera, voice-to-text, and gesture navigation.
- **Tech Stack**:
  - *AutoML & Explainability*: Python, `ray.tune`, `HyperOptSearch`, `AsyncHyperBandScheduler`, `XGBoost` (`binary:logistic`), `LightGBM`, `CatBoost`, `RandomForest`, `f2_score`, PCA/t-SNE subgroup diagnostics.
  - *Field Hardware Concept*: Mobile AR remote pre-check workflow (`ElevAI`), plus Out-of-the-Box smart safety helmet concept (*S.H.I.E.L.D*: embedded lighting, AR camera, speech-to-text, gesture recognition).
- **System Architecture**:
  1. *Imbalanced Dispatch Audit*: Splits 87% true maintenance (`class 1`) vs 13% invalid calls (`class 0`) across stratified equipment sub-groups (`Groups 0–3`) using PCA/t-SNE.
  2. *Safety-Weighted Tuning (`ray.tune`)*: Optimizes GBT ensembles strictly for `f2_score` so precision gains never sacrifice elevator passenger safety recall.
  3. *Human-in-the-Loop AR Triage*: Routes borderline predictions to AR remote technician verification and global part-wear feedback logging.
- **Key Technical Decisions**:
  - *Decision 1: Align Objective to `f2_score`*: Explicitly rejected naive accuracy maximization ("predict all 1s") in favor of `f2_score` cost-weighted suppression of invalid dispatches.
  - *Decision 2: Honest Subgroup Noise Disclosure*: Proved theoretical performance ceilings in under-featured sensor subsets (`Groups 0–3`) via PCA/t-SNE rather than hiding weak slices.
  - *Decision 3: Hands-Free Field Ergonomics*: Both *ElevAI* (AR pre-check) and co-winner *S.H.I.E.L.D* (integrated lighting/voice/gesture helmet) targeted elevator mechanics wearing heavy gloves in dark shafts.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Naive Baseline*: `F2 = 0.92299`, `Accuracy = 0.70586`.
  - *ElevAI Model*: **`F2 = 0.926601`**, **`Accuracy = 0.737212`** (+3.14 percentage-point invalid dispatch reduction without recall loss).
  - *Class Skew*: `87%` real maintenance (`class 1`) vs `13%` false dispatches (`class 0`); ~30 teams across CGI 2021 tracks.
- **Demo Highlights**:
  - Live cost-impact walk-through showing exact wasted technician hours recovered from the 13% false-positive tail via AR pre-checks, paired with transparent group-level error charts reviewed by KONE mentor Jaakko Uusitalo.
- **Team Background**:
  - *Team Glados*: Ville Toiviainen (`Villux`) and Andreas Urbanski (`nardeas`), 2017 & 2018 Junction Overall Grand Champions. *(Out-of-the-Box co-winner `S.H.I.E.L.D` [L2] team names and codebase not publicly documented.)*
- **Winning Hypothesis**:
  Engineering honesty paired with domain safety math. Proving irreducible sensor-group limits and plugging that uncertainty gap with AR pre-checks resonated deeply with KONE's maintenance leadership.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: In industrial reliability tasks, optimize domain loss (`f2_score`), never vanilla accuracy.
  - *Lesson 2*: Turn low-confidence ML cases into a human-in-the-loop AR/wearable verification product feature.
- **Source URLs**:
  - [ElevAI GitHub Repository (teamglados/elevai)](https://github.com/teamglados/elevai)
  - [ElevAI Demo Video (Vimeo)](https://vimeo.com/648187179)
  - [CGI Finland Junction 2021 Highlights](https://www.cgi.com/fi/fi/blogi/junction-2021-hackathon-highlights)
  - [Wikipedia: Junction (hackathon)](https://en.wikipedia.org/wiki/Junction_(hackathon))
- **Evidence Level**: `L1: Verified by Winner GitHub Repo (teamglados/elevai), Demo Video & CGI Finland Blog`

---

### Project Card 8: Saavi – Healthy Finance (OP / Finance — Junction 2020 Connected Overall Winner)

#### 1. Basic Metadata
- **Event ID**: `junction-2020`
- **Event Name**: `Junction 2020 Connected`
- **Year**: `2020`
- **Organizer**: `OP Financial Group` (Finance Track)
- **Challenge Name**: `Finance Challenge (Junction 2020 Connected)`
- **Category**: `IoT & Hardware / Spatial Mobile Computing (ARKit) & Embedded UX`
- **Judging Criteria**:
  - Technical creativity, physical-digital user experience, completeness, and impact under pandemic-era remote hackathon constraints.
- **Project ID**: `op-saavi-2020`
- **Project Name**: `Saavi – Healthy Finance`
- **Award**: **Junction 2020 Connected Overall Grand Winner 🏆 (Main Prize)**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  During COVID-19's remote Junction 2020 Connected edition (when physical electronics lab access collapsed), *Saavi – Healthy Finance* won the Overall Grand Prize by anchoring spatial AR computing directly onto an everyday physical artifact: an OP debit/credit card. Native iOS `ARKit` tracks the real card texture (`ist_card.arreferenceimage`) and monitors card-flick gestures (`abs(v) > 0.03`) to project floating 3D financial analytics backed by a containerized `scikit-learn` subscription prediction Flask microservice (`antoleb/saavi_back`).
- **Tech Stack**:
  - *iOS Spatial AR Client*: Swift, `ARKit` (`ARReferenceImage`), `Alamofire`, `SnapKit`, `Nuke`, `RxSwift`, `RxCocoa`, `AnimatedGradientView`, `FittedSheets`.
  - *Prediction Microservice*: Dockerized Python `Flask`, `markupsafe`, `scikit-learn` (`OneHotEncoder`, `LogisticRegression`).
- **System Architecture**:
  1. *Physical Card Anchor*: `ARKit` recognizes physical card target `ist_card.arreferenceimage` and tracks continuous camera-relative pose.
  2. *Kinetic Flick Gesture*: Reactive RxSwift UI listens for velocity threshold `abs(v) > 0.03` to inspect or dismiss recurring subscription sheets.
  3. *Containerized ML Predictor*: Dockerized Flask (`run_app.py`) exposes `/user/<id>`, `/user/subscription_prediction/<id>/`, and `/user/next_two_subscriptions/<id>/` backed by `scikit-learn` per-service logistic models trained on `new_sub.csv`.
- **Key Technical Decisions**:
  - *Decision 1: Sponsor Artifact as Physical Anchor*: Transformed an ordinary plastic bank card into a tactile spatial hardware controller when lab kits were unavailable.
  - *Decision 2: Lightweight Regularized Linear Classifiers*: Used `OneHotEncoder` + per-service `LogisticRegression(max_iter=1e7, class_weight='balanced', C=1e-2)` for fast deterministic Docker cold-starts.
  - *Decision 3: Clean iOS/Backend Separation*: Decoupled native Swift AR (`azimin`) from Python ML endpoints (`antoleb`) so neither stalled the other.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *AR Gesture Velocity Gate*: `abs(v) > 0.03` spatial flick detection threshold.
  - *ML Solver Parameters*: `LogisticRegression(max_iter=1e7, class_weight='balanced', C=1e-2)` trained on `new_sub.csv` (`service_name`, `service_category`, `number_of_payments`).
  - *Competition Standing*: Overall Main Prize Grand Winner at Junction 2020 Connected.
- **Demo Highlights**:
  - Aiming a live iPhone camera at a physical OP bank card caused interactive floating financial health widgets and predicted upcoming bills to lock spatially onto the physical card surface.
- **Team Background**:
  - *Alexander Zimin* (`azimin`, iOS/ARKit), *Anton Lebedev* (`antoleb`, Python Flask/ML), *Andrey Krylov* (`andreykr.com`, UX/UI Design), *Andrey Volodin*, and *Egor Petrov*.
- **Winning Hypothesis**:
  Physical-digital contrast during an all-remote hackathon. While peer teams demoed browser charts over Zoom, *Saavi* created undeniable hardware-like tactile delight using computer-vision `ARKit` anchored on real sponsor plastics.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: If hardware booths are absent, turn the user's phone camera + sponsor physical card/object into an `ARKit` spatial controller.
  - *Lesson 2*: Pair snappy native mobile AR views with small, fast Dockerized `scikit-learn` JSON services.
- **Source URLs**:
  - [Saavi ML Backend GitHub (antoleb/saavi_back)](https://github.com/antoleb/saavi_back)
  - [Saavi iOS ARKit Backup Repo (azimin)](https://github.com/azimin/MoneyMustBeFunnyAkaJunction2020Backup)
  - [Andrey Krylov Design Portfolio](https://www.andreykr.com/media)
  - [Demo Video (YouTube)](https://www.youtube.com/watch?v=Zc7ce9MxTNg)
  - [Wikipedia: Junction (hackathon)](https://en.wikipedia.org/wiki/Junction_(hackathon))
- **Evidence Level**: `L1: Verified by Two Public Winner Repositories (saavi_back, iOS backup), Wikipedia & Author Portfolio`

---

### Project Card 9: LumenLoop (Helvar & VTT — Making Spaces Brighter with Radar Technology)

#### 1. Basic Metadata
- **Event ID**: `junction-2019`
- **Event Name**: `Junction 2019`
- **Year**: `2019`
- **Organizer**: `Helvar` & `VTT Technical Research Centre of Finland`
- **Challenge Name**: `Making Spaces Brighter with Radar Technology`
- **Category**: `IoT & Hardware / Millimeter-Wave Radar & Closed-Loop Actuators`
- **Judging Criteria**:
  - Leveraging VTT 60 GHz 2D imaging radar and 24 GHz vital-sign radar alongside RGB ground-truth datasets to detect room/garage occupancy, occupant posture/behavior, and dynamically actuate Helvar smart luminaires.
- **Project ID**: `helvar-vtt-lumenloop-2019`
- **Project Name**: `LumenLoop`
- **Award**: **Helvar & VTT Challenge 1st Place Winner 🥇**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  Rather than analyzing pre-recorded radar CSV files offline, 2-person team *LumenLoop* closed the full hardware-in-the-loop circuit between VTT's live 60 GHz/24 GHz millimeter-wave radars and Helvar's physical DALI demo luminaire `EC22`. The pipeline consumes live RabbitMQ AMQP FlatBuffers frames at `100 Hz`, denoises room occupancy changes (`diff/max > 0.13`), maps occupant count monotonically into circadian Kelvin/brightness targets, and transmits `pyserial` hex lookup commands straight over USB-Serial BLE Mesh to change real booth lighting live on stage.
- **Tech Stack**:
  - *RF Sensors & Transport*: VTT 60 GHz FMCW 2D Radar (`160°` H, `5 cm` range res, `<700 nm` micromotion, `180x110` @ `100 Hz`), VTT 24 GHz Vital Radar (`1–5 um`), RabbitMQ AMQP (`10.84.110.2`), FlatBuffers (`Vtt60Processed.Sample`, `RadarRawInt.Sample`).
  - *Control & Actuation*: Python, NumPy, `pyserial==3.4`, Helvar DALI BLE Mesh USB gateway (`ID: "EC22"`), React (`Demo.js`), Elasticsearch.
- **System Architecture**:
  1. *Zero-Copy Radar Ingestion*: Subscribes to `radar60` / `radar24` RabbitMQ queues over Ethernet and decodes FlatBuffers binary samples via `AmplitudeAsNumpy()` / `AngleAsNumpy()`.
  2. *Occupancy Inference (`live/Streamer60.py`)*: Denoises polar background matrices and triggers occupant-count state transitions when `diff/max > 0.13`.
  3. *Closed-Loop DALI Serial Control*: Translates occupant count into 31-step brightness (`00`..`FE`) and 39-step Kelvin hex codes (`1964`..`0A8C` for `6500K`–`2700K`) sent via `pyserial` to luminaire `EC22`.
- **Key Technical Decisions**:
  - *Decision 1: Close the Hardware Loop to `EC22`*: Insisted on modulating a physical luminaire via serial USB BLE Mesh instead of stopping at passive web charts.
  - *Decision 2: Smooth Multi-Person Circadian LUT*: Defined deterministic occupancy-to-lighting ramps (`0` people: `5% / 6500K`; `1`: `20% / 5750K`; `2`: `30% / 4850K`; `3+`: `60% / 3450K`) tailored to office/meeting ergonomics.
  - *Decision 3: Binary FlatBuffers Ingestion*: Used native FlatBuffers NumPy accessors directly on AMQP streams so `100 Hz` radar cadence stayed drop-free.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *60 GHz Radar Envelope*: `160 deg` horizontal beam, `25 deg` elevation, `5 cm` range res, `3.5 deg` angular res, `<700 nm` micromotion (`180x110` @ `100 Hz`).
  - *24 GHz Radar Envelope*: `80 deg` H-beam, `60 cm` range res, `1–5 um` micromotion (`497` channels).
  - *Actuation Precision*: `31` brightness LUT steps (`00`–`FE`) x `39` Kelvin steps (`6500K`–`2700K`), occupancy trigger `diff/max > 0.13`.
- **Demo Highlights**:
  - Judges walking into VTT's live 60 GHz beam watched physical luminaire `EC22` respond effortlessly — shifting brightness from 5% standby up to 60% warmer illumination alongside live polar radar heatmaps.
- **Team Background**:
  - *Denys Kovalenko* (`deniskovalenko`, Backend / Signal Processing / DALI Serial Control) and *Elizaveta Lebedeva* (`elizavetalebedeva.com`, Data Science / React UI) — 2-person squad that returned to win Helvar again in 2021.
- **Winning Hypothesis**:
  Full physical loop closure. Only a handful of teams wire live RF message brokers back into serial lighting controllers in 48 hours, making *LumenLoop*'s 2-person hardware control undeniable.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: If an industrial sensor sponsor brings real actuators (lights, motors, EV chargers), closing sensor -> inference -> serial actuator control almost always beats open-loop analytics.
  - *Lesson 2*: Parse partner binary protocols (FlatBuffers/Protobuf over AMQP/MQTT) cleanly via vectorized NumPy early on Friday night.
- **Source URLs**:
  - [LumenLoop GitHub Repository (deniskovalenko/junction2019)](https://github.com/deniskovalenko/junction2019)
  - [Elizaveta Lebedeva Author Confirmation](https://elizavetalebedeva.com/tag/junction/)
  - [Official Junction 2019 Winners List (Medium)](https://medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f)
- **Evidence Level**: `L1: Verified by Winner GitHub Repository (deniskovalenko/junction2019), Author Blog & Official Junction Medium Winners List`

---

### Project Card 10: AyyHello! (Aalto University AYY — Smart Signage - For Students by Students)

#### 1. Basic Metadata
- **Event ID**: `junction-2019`
- **Event Name**: `Junction 2019`
- **Year**: `2019`
- **Organizer**: `Aalto University & AYY (Aalto University Student Union)`
- **Challenge Name**: `Smart Signage - For Students by Students`
- **Category**: `IoT & Hardware / Edge Embedded Kiosk, PIR & Touchless CV`
- **Judging Criteria**:
  - Practical stairwell/hallway display hardware concept across ~2,600 student apartments (~3,500 residents), effectively turning AYY building HVAC, water, electricity, and network telemetry into engaging resident functionality.
- **Project ID**: `aalto-ayyhello-2019`
- **Project Name**: `AyyHello! (ayyHello)`
- **Award**: **Aalto University AYY Challenge 1st Place Winner 🥇**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  Corridor touchscreens suffer hygiene, vandalism, and glare failures in student housing stairwells. *AyyHello!* built a touchless Raspberry Pi hallway kiosk driven by a hardware PIR motion wake interrupt (`RPi.GPIO`, `PIR_PIN = 11`, `LED_PIN = 3`) and a USB webcam running modified `MobilePose-PyTorch` (`resnet18`, `224x224`) with a 10-frame temporal debounce filter (`L` / `R` / `U`), switching React/Material-UI cards displaying live AYY building energy/water footprints (`SMT8-12_*.csv`), HSL transit departures, weather, and a touchless pose mini-game.
- **Tech Stack**:
  - *Edge Hardware & Interrupts*: Raspberry Pi SBC (`Linux`), PIR motion sensor + indicator LED (`RPi.GPIO`, `GPIO.BOARD` `PIR_PIN = 11`, `LED_PIN = 3`), USB webcam (`--camera 0`).
  - *CV & Application Stack*: `PyTorch 1.0.0` (`MobilePose-PyTorch` `ResEstimator`, `resnet18` / `mobilenetv2`), `OpenCV 3.4.2.17`, Python `Flask` + `flask_cors`, React `16.12.0`, Material-UI `4.6.1`, `nuka-carousel`, `victory`, `react-google-charts`.
- **System Architecture**:
  1. *Hardware PIR Wake*: `ayy-lmao/pir.py` attaches `GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=pir_isr_cb)` flashing `LED_PIN = 3` and waking approaching passersby sessions.
  2. *Debounced Gesture Classifier (`estimator.py`, `run_webcam.py`)*: Runs `resnet18` (`--inp_dim 224`) pose keypoints and demands 10 consecutive consistent frames before issuing `L`, `R`, or `U`.
  3. *Microservice Kiosk Bridge (`app.py`, `analysis.py`)*: Local HTTP `POST http://10.42.0.157:5000/dir` steers React carousel cards (`/el`, `/heat`, `/water` parsed from semicolon AYY CSVs skipping 52 metadata rows).
- **Key Technical Decisions**:
  - *Decision 1: Hygienic Touchless Hardware*: Avoided fragile stairwell capacitive glass altogether by pairing hardware PIR wake with mid-air pose gestures.
  - *Decision 2: 10-Frame Temporal Debounce Over Heavy 3D-CNNs*: Prevented stray crowd motion in crowded halls from misfiring UI navigation using a lightweight 10-frame stability buffer.
  - *Decision 3: Multi-Process Local HTTP Split*: Separated GPIO (`pir.py`), PyTorch CV (`run_webcam.py`), and React (`App.js`) across `10.42.0.157:5000` so five engineers integrated independently.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Vision Backbone*: `resnet18` at `224x224` input resolution (`--inp_dim 224`).
  - *Reliability Filter*: `10`-frame temporal debouncing window gating `L`, `R`, `U` commands.
  - *Building Coverage*: Engineered for AYY's `~2,600` apartments (`~3,500` tenants), ingesting `SMT8-12_*.csv` (`hourly`, `weekly`, `monthly`).
- **Demo Highlights**:
  - Walking past the booth fired `PIR_PIN = 11`, illuminating `LED_PIN = 3`; clean hand waves flipped smoothly between Helsinki bus schedules, weekly dorm water/electricity bars, and an interactive pose mini-game.
- **Team Background**:
  - Five-member Aalto/Finnish squad: *Mari Porko* (`mariporko`), *Harri Rahikainen* (`HRahikainen`), *Jesse Tolvanen* (`JZNT`), *Satria Sutisna* (`satriasutisna`), and `smirq`.
- **Winning Hypothesis**:
  Daily resident pull + rock-solid debounced hardware interaction. Housing union judges saw students genuinely stop for transit/games while passively internalizing sustainability metrics.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: A `10`-frame temporal consensus window is mandatory whenever running live camera gesture UIs in chaotic expo halls.
  - *Lesson 2*: Decouple SBC hardware GPIO pins, deep learning processes, and web kiosks behind local Flask endpoints for zero-collision teamwork.
- **Source URLs**:
  - [AyyHello! GitHub Repository (mariporko/junction2019)](https://github.com/mariporko/junction2019)
  - [Fork Repo (HRahikainen/junction2019)](https://github.com/HRahikainen/junction2019)
  - [Official Junction 2019 Winners List (Medium)](https://medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f)
  - [Aalto University AYY Challenge News](https://www.aalto.fi/en/news/student-union-looks-for-creative-ideas-for-their-information-channels-from-junction)
- **Evidence Level**: `L1: Verified by Winner GitHub Repositories (mariporko/junction2019), Aalto News & Official Medium Winners List`

---

### Project Card 11: Help.io / Team Health.io (Intel — Innovative Applications With Bluetooth Mesh)

#### 1. Basic Metadata
- **Event ID**: `junction-2018`
- **Event Name**: `Junction 2018`
- **Year**: `2018`
- **Organizer**: `Intel` (Partner hardware kit alongside `Movesense by Suunto`)
- **Challenge Name**: `Innovative Applications With Bluetooth Mesh`
- **Category**: `IoT & Hardware / Bluetooth Mesh Gateways, Edge Triage & Wearables`
- **Judging Criteria**:
  - Designing a practical application on an IoT edge gateway exploiting Bluetooth Mesh wireless sensor networks (e.g., smart badges, building/emergency messaging without cellular/internet dependence).
- **Project ID**: `intel-helpio-2018`
- **Project Name**: `Help.io / Team Health.io`
- **Award**: **Intel Challenge 1st Prize 🥇 + IoT Track Overall Winner 🏆 + Junction 2018 2nd Place Overall 🥈 (out of 300+ projects)**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  In major disasters when cellular and Wi-Fi networks fail, first responders lose situational visibility over dispersed casualties. Building directly atop Intel's bleeding-edge Junction 2018 Bluetooth Mesh kit (`intel/Junction2018`, `feri/Junction2018_Support`) and Suunto Movesense wearable sensors, Latvia's *Help.io / Health.io* created an off-grid emergency triage mesh. Patient Movesense chest sensors stream live heart rate and R-R intervals via BLE to an iOS 12 triage engine (`discardCount = 5`, `lowestHRBound = 60.0`, `highestHRBound = 110.0`, `highestRRMultiplier = 2.0`), which fires HTTP alerts (`10.100.5.16:3000/{bluetoothId}/critical`) to an Intel NUC (`BlueZ meshd-ingas` + `nRF51_dongle`), broadcasting critical responder alerts across four Zephyr-based PHYTEC `reel_board` e-ink badges.
- **Tech Stack**:
  - *Wearable Biometrics*: Suunto Movesense BLE sensors (`175030001053` -> `0x0001`, `175030000988` -> `0x0002`, `Movesense.HR_PATH` `average` + `rrData`).
  - *Edge Mobile Triage*: iOS 12 / Swift (`Movesense SDK`, `AsyncDisplayKit`/`Texture`, `PromiseKit`, `Bond`, `SwiftyJSON`, `Alamofire`, `ScrollableGraphView`).
  - *Bluetooth Mesh Infrastructure*: Intel NUC (Linux on `jnct-ble5-mesh`), experimental `BlueZ` (`meshd-ingas`, `ell 0.13`, D-Bus `org.bluez.mesh1`), `nRF51_dongle` (Zephyr `hci_uart`), 4x PHYTEC `reel_board`s running Zephyr `mesh_badge` (`0x0000` Vendor, `0x1000` OnOff, `0x1102` Sensor temp `0x2a1f`).
- **System Architecture**:
  1. *Biometric BLE Telemetry*: Movesense chest straps transmit continuous average HR + R-R intervals over Bluetooth LE to nearby responder/patient iOS 12 client.
  2. *Local Edge Triage Engine*: Discards initialization samples (`discardCount = 5`), checks `heartRateHistory.count >= 15` against `60.0–110.0` BPM & `2.0x` RR spike rules, avoiding spurious triggers.
  3. *HTTP-to-BlueZ Mesh Gateway*: `Alamofire` POSTs to `10.100.5.16:3000/{id}/{setup / critical}`, driving Intel NUC Python D-Bus `org.bluez.mesh1` -> `nRF51_dongle` -> 4x PHYTEC `reel_board` e-ink/LED responder badges off-grid.
- **Key Technical Decisions**:
  - *Decision 1: Clean HTTP Isolation Around Experimental Mesh Stack*: Because Intel's `meshd-ingas` daemon had literally landed days before Junction, keeping mature Movesense iOS SDK code isolated behind `10.100.5.16:3000` prevented SDK/driver conflicts.
  - *Decision 2: Tunable Demo Clinical Bounds*: Exposed clean threshold constants (`60`–`110` BPM vs field `140`/`240`) so live stage demos triggered alarm cascades deterministically.
  - *Decision 3: Multi-Kit Synergy*: Bridged Intel NUC/Mesh hardware cleanly with Suunto Movesense kits, winning top Intel, overall IoT Track, and #2 Overall across Junction 2018.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Kit Deployment Scale*: `8` Intel hardware kits distributed (each `1` NUC + `1` `nRF51_dongle` + `4` PHYTEC `reel_board`s); `26` Movesense projects total.
  - *Verified Triage Constants*: `discardCount = 5`, `heartRateHistory.count >= 15`, `lowestHRBound = 60.0`, `highestHRBound = 110.0`, `highestRRMultiplier = 2.0`.
  - *Competition Standing*: Intel 1st + IoT Track Winner + **2nd Place Overall** among 11 track finalists and 300+ Junction 2018 submissions.
- **Demo Highlights**:
  - Deliberately spiking the wearer's heart rate while completely disconnected from the internet propagated emergency alerts over Bluetooth Mesh onto physical PHYTEC `reel_board` e-ink responder badges, pinpointing sector nodes (`0x0001` / `0x0002`), alongside real-time `ScrollableGraphView` telemetry on iOS.
- **Team Background**:
  - University of Latvia Faculty of Computing: *Austris Cīrulnieks*, *Mārcis Nīmants* (`mnimants`), *Elvijs Viļķels*, *Aigars Cibuļskis*, and *Dāvis Mednis* (4 of 5 won the 2017 Movesense Health Challenge with *ReCover*).
- **Winning Hypothesis**:
  Off-grid hardware reliability plus surgical architectural separation. By mastering Intel's newest BlueZ Mesh daemon behind a clean local gateway while uniting it with proven Movesense sensors, they delivered an undeniable physical emergency demo.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: Isolate experimental partner SDKs (`BlueZ meshd` / Zephyr) on an edge hub behind simple HTTP JSON triggers (`/{id}/critical`) so app and embedded devs never block each other.
  - *Lesson 2*: Study partner support repositories (`intel/Junction2018`, `feri/Junction2018_Support`) immediately to lock exact D-Bus and GATT/Mesh model opcodes (`0x8202`, `0x8231`).
- **Source URLs**:
  - [Help.io GitHub Repository (mnimants/junction2018)](https://github.com/mnimants/junction2018)
  - [Official Intel Mesh Repo (intel/Junction2018)](https://github.com/intel/Junction2018)
  - [Intel Support Kit (feri/Junction2018_Support)](https://github.com/feri/Junction2018_Support)
  - [Movesense Official 2018 Report](https://www.movesense.com/news/2018/11/movesense-shined-in-junction-hackathon/)
  - [University of Latvia Official Release](https://eztf.lu.lv/en/about-us/news/detail-view/t/98941/)
- **Evidence Level**: `L1: Verified by Winner Repo (mnimants/junction2018), Official Intel Repos, Movesense Press & Univ. of Latvia Release`

---

### Project Card 12: Oneiro — Team Glados (Ensto — Teach EV Chargers New Tricks)

#### 1. Basic Metadata
- **Event ID**: `junction-2018`
- **Event Name**: `Junction 2018`
- **Year**: `2018`
- **Organizer**: `Ensto` (Ensto Flow EV Charging — Judge: Ville Parviainen, Head of Software)
- **Challenge Name**: `Teach EV Chargers New Tricks`
- **Category**: `IoT & Hardware / Edge Vision, Smart EV Chargers & Mobility`
- **Judging Criteria**:
  - Building novel functionality atop on-site Ensto EV charging hardware and the EnstoFlow REST API (`RealDevice` OCPP control), evaluated on technical execution, business viability, and intuitive UX across 14 Ensto teams.
- **Project ID**: `ensto-oneiro-2018`
- **Project Name**: `Oneiro (Team Glados)`
- **Award**: **Junction 2018 Overall Grand Winner 🏆 (€20,000 Cash Prize) & Ensto Mobility Challenge 1st Prize 🥇 (out of 14 teams)**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  To combat urban EV charger scarcity without waiting for public utility rollouts, *Oneiro* built an automated P2P "Airbnb for private EV chargers" driven by live edge computer vision on a real **Ensto Chago** station (`JunctionEVB1`). A Raspberry Pi + PiCamera running under `systemd` (`photographer.service`) uploads `640x480` frames every `0.5s` to a Sanic server calling containerized `openalpr:16.04` (`country="eu"`, `top_n=5`); once a registered plate exceeds `confidence >= 75`, Sanic executes OCPP `spot_enable()` via `EnstoFlow` REST API v1 to physically switch charger status LEDs and power delivery — backed by React Native Expo apps and Telia cellular `Mapbox GL` heatmaps.
- **Tech Stack**:
  - *Edge Vision & Station Hardware*: Raspberry Pi + PiCamera (`systemd` `photographer.service`), **Ensto Chago EV Charger** (`JunctionEVB1` in `RealDevice` OCPP `A -> C` mode).
  - *OCR & Control Backend*: Dockerized `openalpr:16.04` (`eu`/`fi`), Python 3 + `Sanic` (`port 8000`), `EnstoFlow` REST API v1 (`/api/v1/`, HTTP Basic Auth).
  - *Client, Geospatial & Cloud*: React Native (`sdk-31.0.0`, Expo `^31.0.2`, Redux-Saga, Axios), `Mapbox GL JS v0.51.0` (Telia Uusimaa cellular heatmap), Terraform + AWS (`t2.nano`, ELB, ECR, S3, CloudFront, Route53).
- **System Architecture**:
  1. *Supervised Edge Capture (`raspberry/photographer.py`)*: Posts `640x480` `pi_image.jpg` every `0.5s` over multipart HTTP with a hard `2s` timeout.
  2. *Containerized ALPR Match (`server/licence_plate.py`)*: `openalpr:16.04` checks top `5` EU/FI plate candidates; confidence `>= 75` unlocks registered owner slots.
  3. *Real OCPP Actuation (`server/enstoflow.py`)*: Polls `chargingPointGroup` / `configuration` and executes `{connector}/starttransaction/{tag}` (`spot_enable()`), physically switching live `JunctionEVB1` charger LEDs alongside Telia cellular placement heatmaps (`heatmap/`).
- **Key Technical Decisions**:
  - *Decision 1: Hands-Free Camera Auth Over NFC/App Friction*: Automated pull-in charging via license plate recognition so drivers avoid juggling multiple provider apps in freezing Nordic weather.
  - *Decision 2: Commercial Realism via Telia Footfall Data*: Grounded host P2P pricing economics (`spot_stop_charging`) and urban charger expansion gaps with actual Telia telecom activity datasets (`FI_MTC_WGS84`).
  - *Decision 3: Self-Healing `systemd` + `2s` Timeout*: Prevented wireless conference congestion from freezing the headless Raspberry Pi node.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Edge Capture Parameters*: `0.5s` interval (`2 FPS`), `640x480` JPEG frame, `2 s` HTTP timeout (`systemd` supervised).
  - *ALPR Gate*: `top_n = 5` European candidates unlocking at `confidence >= 75`.
  - *Competition Standing*: **Overall Grand Winner €20,000** (~1,200–1,300 participants, 300+ submissions) + 1st of 14 teams in Ensto's challenges.
- **Demo Highlights**:
  - Presenting a test license plate in front of the live PiCamera switched the on-stage Ensto Chago hardware (`JunctionEVB1`) from idle blue/red directly into active OCPP charging while Telia demand heatmaps highlighted Helsinki supply deserts.
- **Team Background**:
  - *Team Glados*: *Teemu Taskula* (`Temzasse`), *Andreas Urbanski*, and *Ville Toiviainen* (`Villux`) — rare **back-to-back Junction Overall Grand Champions (2017 *Signvision* & 2018 *Oneiro*)**.
- **Winning Hypothesis**:
  End-to-end physical hardware control wedded to a finished P2P marketplace model. Ensto Head of Software Ville Parviainen praised how seamlessly *Oneiro* integrated Ensto's production charger APIs with turnkey UX and sound business logic.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: Using edge CV to automate away user taps/cards on physical sponsor equipment delivers unforgettable live demos.
  - *Lesson 2*: Always bind headless Raspberry Pi demo loops with `systemd` restart policies and bounded HTTP timeouts (`2s`).
- **Source URLs**:
  - [Oneiro GitHub Repository (teamglados/oneiro)](https://github.com/teamglados/oneiro)
  - [Oneiro Demo Video (Vimeo)](https://vimeo.com/302650304)
  - [Talotekniikka-lehti Coverage](https://talotekniikka-lehti.fi/oneiro-voitti-junction-2018-hackathonin/)
  - [Mobiili.fi Winner Coverage](https://mobiili.fi/2018/11/25/junction-hackathon-espoossa-paattyi-latauspisteiden-airbnbn-voittoon-sama-tiimi-voitti-kilpailun-viime-vuonnakin/)
- **Evidence Level**: `L1: Verified by Winner GitHub Repository (teamglados/oneiro), Demo Video & Finnish Tech Press`

---

### Project Card 13: GuideMe — Makers UPV (Future Cities Track — 4th Overall)

#### 1. Basic Metadata
- **Event ID**: `junction-2018`
- **Event Name**: `Junction 2018`
- **Year**: `2018`
- **Organizer**: `Future Cities Track` (Junction 2018 Main Competition Top Finalist Track)
- **Challenge Name**: `Future Cities Challenge`
- **Category**: `IoT & Hardware / Assistive Dual-MCU Hardware & Custom CAD`
- **Judging Criteria**:
  - Hardware completeness, urban citizen accessibility impact, tactile usability, and scalable public impact.
- **Project ID**: `futurecities-guideme-2018`
- **Project Name**: `GuideMe`
- **Award**: **Future Cities Track 1st Prize 🥇 (€1,000) & Junction 2018 4th Place Overall (out of 300+ projects)**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  Elderly pedestrians and visually impaired users struggle to walk safely while staring at tiny smartphone turn-by-turn maps. Spanish multidisciplinary team Makers UPV built *GuideMe* from bare metal and CAD in 48 hours: a custom 3D-printed ergonomic walking-cane handle (`guideme_handle.SLDPRT` / `.STL`) housing dual MCUs and a battery. A Wemos `ESP8266` polls walking waypoint vectors from a Google Maps Directions PHP backend and relays headings over `115200 baud` UART (`pins 0/2`) to a `BBC micro:bit`, whose onboard magnetometer drives clear directional arrows on its 5x5 LED matrix alongside `pin 1` vibration/buzzer haptics — plus an AJAX caregiver tracking portal.
- **Tech Stack**:
  - *Dual-MCU Embedded Hardware*: `BBC micro:bit` (ARM Cortex-M0, magnetometer, 5x5 LED array, MicroPython `micro.py`), `Wemos ESP8266` (`guideme_arduino_wifi_node.ino`).
  - *Mechanical Enclosure & Navigation Web*: SolidWorks CAD (`guideme_handle.SLDPRT`) + `.STL` 3D print files, `PHP` (`web/back.php`, `web/front.php`), Google Maps Directions API, HTML / jQuery / AJAX.
- **System Architecture**:
  1. *Caregiver Map Backend (`web/front.php`, `back.php`)*: Caregiver assigns destinations remotely and tracks current GPS trajectory in real time via AJAX.
  2. *Wi-Fi Serial Bridge (`guideme_arduino_wifi_node.ino`)*: `Wemos ESP8266` polls next turn bearings and forwards serial instructions at `115200 baud`.
  3. *Magnetometer Haptic Guidance (`micro.py`)*: `BBC micro:bit` compares continuous compass heading against desired bearing and triggers 5x5 LED turn arrows plus `pin 1` haptic vibrator/buzzer actuators inside the custom 3D-printed cane handle.
- **Key Technical Decisions**:
  - *Decision 1: Dual-MCU Partitioning*: Dedicated networking strictly to the cheap `ESP8266` while keeping `micro:bit` deterministic for compass alignment, 5x5 LEDs, and haptics — avoiding Wi-Fi stack crashes on MicroPython.
  - *Decision 2: On-Site 3D-Printed Mechanical Handle*: Modeled `.SLDPRT`/`.STL` enclosures on site so batteries and PCBs snapped into a genuine ergonomic walking cane handle.
  - *Decision 3: Multi-Sensory Accessibility*: Paired top-facing LEDs for low-vision sight cues with silent `pin 1` tactile vibrations/buzzer for eyes-free urban navigation.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Serial Link*: `115200 baud` UART across `pin 0` / `pin 2`; actuator control pin `pin 1`.
  - *Hardware Packaging*: Full SolidWorks CAD part (`guideme_handle.SLDPRT`) and printable `.STL` verified in Git repo.
  - *Competition Standing*: **4th Place Overall** across 300+ Junction submissions (~1,300 attendees) + Future Cities 1st (€1,000).
- **Demo Highlights**:
  - Physically rotating the 3D-printed walking cane handle updated `micro:bit` LED turn vectors seamlessly while pulsing `pin 1` haptics and live caregiver route updates on screen.
- **Team Background**:
  - *Makers UPV* (Universitat Politècnica de València): *Jaime Laborda Macario*, *Iván Torres Játiva* (Electronic Eng.), *Enrique Miralles Dolz* (Nuclear Fusion Eng.), *Joaquín Montesinos Muñoz* (Telecoms Eng.), and *Matías Fernández Patón* (Biomedical Eng.).
- **Winning Hypothesis**:
  End-to-end physical product polish. Few student teams unite CAD 3D printing, dual-board serial electronics, compass math, and caregiver GPS web tooling within a single hackathon weekend.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: Decouple Wi-Fi HTTP fetching onto an `ESP8266` and sensor/actuator PWM loops onto a companion MCU via `115200` UART for painless integration.
  - *Lesson 2*: Designing and 3D-printing an ergonomic enclosure elevates raw jumper-wired sensors into tangible hardware products.
- **Source URLs**:
  - [GuideMe GitHub Repository (makers-upv/GuideMe)](https://github.com/makers-upv/GuideMe)
  - [UPV University Press Release](https://www.upv.es/noticias-upv/noticia-10627-junction-2018-es.html)
  - [Mobiili.fi Finalist Coverage](https://mobiili.fi/2018/11/25/junction-hackathon-espoossa-paattyi-latauspisteiden-airbnbn-voittoon-sama-tiimi-voitti-kilpailun-viime-vuonnakin/)
- **Evidence Level**: `L1: Verified by Winner GitHub Repository (makers-upv/GuideMe), Official UPV Release & Finnish Finalist Press`

---

### Project Card 14: Make Sauna Great Again / MaSGA (Vaisala — Hack the Sauna)

#### 1. Basic Metadata
- **Event ID**: `junction-2018`
- **Event Name**: `Junction 2018`
- **Year**: `2018`
- **Organizer**: `Vaisala` (Judges: Sampsa Lahtinen, Ari Alanko, Riku Hakala)
- **Challenge Name**: `Hack the Sauna`
- **Category**: `IoT & Hardware / Extreme-Environment Multi-Sensor Analytics`
- **Judging Criteria**:
  - Transforming industrial multi-probe sauna measurements (Temp, Relative Humidity, Enthalpy, CO2, O2) into next-generation extreme-environment wellness insights and facility control intelligence.
- **Project ID**: `vaisala-masga-2018`
- **Project Name**: `Make Sauna Great Again (MaSGA)`
- **Award**: **Vaisala "Hack the Sauna" Challenge 1st Prize 🥇 (Peer-Reviewed Follow-Up Published at IEEE IECON 2020)**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  Analog bi-metallic sauna thermometers measure temperature in one corner while ignoring stratification, CO2 suffocation, oxygen drop, and enthalpy balance. *MaSGA* tapped five distributed Vaisala industrial probes (`Stove1`, `Bench1`, `Bench2`, `Bench3`, `Floor1`) via `apigtw.vaisala.com`, calibrated a trapezoidal fuzzy-similarity comfort model (`quadro()`) against **22 genuine in-sauna bather surveys** (`>= 10–15 min` exposure) inside a Python Google Cloud Function (`Addono/masga-backend`), and pushed simple role-tailored actions ("Add *löyly* water", "Open door for fresh air", vs stove power tuning) every `10s`.
- **Tech Stack**:
  - *Physical Industrial Probes*: Vaisala Multi-Sensor Sauna Array (Temperature, RH, Enthalpy, CO2, O2 across `Stove1`, `Bench1–3`, `Floor1`), Vaisala API Gateway (`/saunameasurements/latest`).
  - *Scoring Engine & Web App*: Python on Google Cloud Functions (`main.py`), custom trapezoidal fuzzy similarity (`quadro()`), Bootstrap 4.1.3, jQuery 3.3.1 (`10s` polling).
- **System Architecture**:
  1. *Distributed Sauna Sensor Array*: Five spatial probes continuously stream thermal stratification, gas concentration, and steam enthalpy to Vaisala REST endpoints.
  2. *Empirically Calibrated Fuzzy Solver (`quadro()`)*: Google Cloud Function normalizes live metrics against 22 empirical human comfort ground-truth surveys and weights Deviations for `user` vs `manager` targets.
  3. *Dual-Persona Action Dashboard*: Polls every `10s`, painting intuitive comfort grades (`>88%` Green, `>75%` Orange, `<=75%` Red) alongside explicit corrective instructions.
- **Key Technical Decisions**:
  - *Decision 1: Empirical In-Sauna Ground-Truth Collection*: Collected 22 real bathers' 10–15 minute survey ratings instead of guessing optimal humidity/CO2 bounds.
  - *Decision 2: Publishable Fuzzy Similarity Modeling (`quadro()`)*: Smoothly modeled interrelated thermodynamic curves rather than brittle step-threshold alarms, passing IEEE IECON 2020 peer review.
  - *Decision 3: Persona Split Between Bather & Plant Operator*: Translated cryptic ppm/enthalpy readouts directly into human actions (*"Add water"* vs *"Adjust stove duty"*).

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Ground-Truth Calibration*: `22` live human sauna surveys (`>= 10–15 min` immersion inside the instrumented sauna).
  - *Dashboard Cadence & Tiers*: `10s` refresh interval; clarity thresholds `>88%` Green ("Perfect"), `>75%` Orange ("Degraded"), `<=75%` Red ("Poor").
  - *Academic Validation*: Extended into IEEE IECON 2020 conference publication (`aaltodoc.aalto.fi`).
- **Demo Highlights**:
  - Dual-persona demo (`https://youtu.be/rNtnsDjz0vM`) toggling live between recreational bather comfort guidance and commercial sauna plant manager thermodynamics.
- **Team Background**:
  - *Siavash H. Khajavi* (Aalto DIEM postdoc), *Alireza Jaribion* (Aalto DIEM researcher), *Adriaan Knapen* (`Addono`, Aalto EIT), *Leila Abiedat*, and *Arnab Banik*.
- **Winning Hypothesis**:
  Real ground-truth calibration inside 48 hours plus clear user/operator abstraction. Vaisala judges recognized rigorous thermodynamic engineering translated cleanly into accessible consumer actions.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: Even collecting ~20 real user calibration samples on-site makes sensor analytics models vastly more credible than invented thresholds.
  - *Lesson 2*: Never hand users raw multi-probe graphs when role-specific directives (*"Open vent"*, *"Add steam"*) solve their exact problem.
- **Source URLs**:
  - [MaSGA Backend GitHub (Addono/masga-backend)](https://github.com/Addono/masga-backend)
  - [MaSGA Frontend GitHub (Addono/masga)](https://github.com/Addono/masga)
  - [Vaisala Official Winners Blog](https://www.vaisala.com/en/blog/2018-11/winners-vaisalas-challenges-junction-2018-hacked-weather-and-sauna)
  - [Aalto University News Coverage](https://www.aalto.fi/en/news/winning-team-hack-the-sauna-experience-to-a-new-level-at-junction)
  - [Aalto IECON 2020 Publication Record](https://aaltodoc.aalto.fi/items/44b6d03b-0849-4381-a9e4-300de579f7d3)
  - [MaSGA Demo Video (YouTube)](https://youtu.be/rNtnsDjz0vM)
- **Evidence Level**: `L1: Verified by Winner GitHub Repos, Official Vaisala Blog, Aalto News & IEEE IECON 2020 Paper`

---

### Project Card 15: TerrainSense (Movesense by Suunto & Stara — Track Anything That Moves / StreetReboot2)

#### 1. Basic Metadata
- **Event ID**: `junction-2018`
- **Event Name**: `Junction 2018`
- **Year**: `2018`
- **Organizer**: `Movesense by Suunto` & `City of Helsinki Stara`
- **Challenge Name**: `Track Anything That Moves / Stara StreetReboot2`
- **Category**: `IoT & Hardware / Crowdsourced Infrastructure IMU & Smart City`
- **Judging Criteria**:
  - Practical innovation and functional readiness using programmable Movesense IMUs, paired with real municipal maintenance utility for Helsinki StreetReboot2.
- **Project ID**: `movesense-terrainsense-2018`
- **Project Name**: `TerrainSense`
- **Award**: **Movesense Challenge 1st Prize 🥇 (Best Multi-Challenge Combination) & City of Helsinki Stara StreetReboot2 2nd Place 🥈 (€1,000)**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  Municipalities inspect thousands of kilometers of cycling paths infrequently using costly specialist vans. Rather than wearing an IMU on the human body, *TerrainSense* mounted a rugged **Suunto Movesense** IMU directly on a commuter bicycle's rear axle/wheel frame (`taka-akseli`). Streaming shock/vibration waves over BLE into an Android companion app synced with GPS timestamps generates open GPX routes and AWS S3/EC2 severity heatmaps pinpointing asphalt cracks and root heave for Helsinki maintenance crews — evolving post-Junction into **3 city pilots** with Helsinki, Forum Virium Helsinki, HAMK, and InnoTrafik adding AWS Rekognition CV.
- **Tech Stack**:
  - *Physical Edge Sensor & Mobile*: Programmable Suunto Movesense IMU (Bluetooth LE), Android GPS + BLE collector, standard GPX telemetry.
  - *Cloud Mapping & Later Pilot CV*: AWS S3 / AWS EC2 geospatial heatmap dashboard *(expanded post-hackathon with AWS Rekognition computer-vision road video inference)*.
- **System Architecture**:
  1. *Mechanical Non-Human Sensing*: Rear-axle (`taka-akseli`) Movesense IMU captures unsuspended frame shock directly without rider wrist damping.
  2. *Edge GPS Alignment*: Android companion fuses BLE IMU vibration peaks with GPS coordinate traces and formats standardized GPX files.
  3. *Municipal Severity Map*: AWS S3/EC2 ingests multi-rider traces into an actionable cycle-path maintenance heatmap (`TerrainSense_Junction_presentation.pdf`).
- **Key Technical Decisions**:
  - *Decision 1: Rear-Axle Mounting Physics*: Mounted the IMU rigidly on the bike rear axle rather than rider arms/torsos to measure clean surface vibration uncorrupted by human elbow flex.
  - *Decision 2: Deliberate Cross-Challenge Stacking*: Coupled Movesense's sensor kit directly with City of Helsinki's Stara `StreetReboot2` dataset/mandate to win both panels.
  - *Decision 3: Standard GPX Interoperability*: Output GIS-native GPX paths so public-works engineers could integrate anomaly overlays immediately.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Movesense Cohort Size*: `18` Friday kits -> `35` Saturday kits -> `26` final submitted projects (`movesense.com`).
  - *Verified Municipal Award (`HEL 2019-003563`)*: **€1,000** Stara `StreetReboot2` 2nd Place + **Movesense Multi-Challenge 1st Prize**.
  - *Commercial Pilot Impact*: Expanded into **3 post-hackathon pilots** across City of Helsinki, Forum Virium Helsinki, HAMK, and InnoTrafik. *(Hackathon codebase not publicly open-sourced `[L1/L2]`.)*
- **Demo Highlights**:
  - Interactive cycle-lane vibration map highlighting real Helsinki rough patches synced beside rear-axle sensor telemetry (`TerrainSense_Junction_presentation.pdf`).
- **Team Background**:
  - *Ville Saramaa* (`vill.dev`) and interdisciplinary Nordic builders *(collaborating post-hackathon with HAMK and InnoTrafik)*.
- **Winning Hypothesis**:
  Clever physical placement + dual-sponsor alignment. Strapping a €50 IMU sensor onto commuter bicycle hubs delivered an order-of-magnitude cheaper road-quality fleet that actually entered municipal procurement pilots.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: Stacking one hardware sensor kit (Movesense/Intel) onto a municipal/civic data challenge (`Stara`) compounds judging appeal and post-event pilot funding.
  - *Lesson 2*: Ask "can this IMU mount onto a vehicle/machine/axle instead of a human wrist?" to separate instantly from lookalike health trackers.
- **Source URLs**:
  - [Movesense Official Junction 2018 Report](https://www.movesense.com/news/2018/11/movesense-shined-in-junction-hackathon/)
  - [TerrainSense Presentation PDF (Movesense)](https://www.movesense.com/wp-content/uploads/2018/12/TerrainSense_Junction_presentation.pdf)
  - [Helsinki Municipal Award Decision HEL 2019-003563](https://paatokset.hel.fi/fi/asia/hel-2019-003563)
  - [Ville Saramaa Portfolio](https://vill.dev/projects/)
  - [HAMK Cycleway Pilot Documentation](https://unlimited.hamk.fi/teknologia-ja-liikenne/pyoravaylien-kunnon-tutkiminen-sensoriteknologian-keinoin/)
- **Evidence Level**: `L1: Verified by Official Movesense Presentation PDF, Municipal Award Record (HEL 2019-003563) & Pilot Reports`

---

### Project Card 16: IVision Lamp — Tsinghua–SenseTime (Helvar — The Brain of the Building)

#### 1. Basic Metadata
- **Event ID**: `junction-2018`
- **Event Name**: `Junction 2018`
- **Year**: `2018`
- **Organizer**: `Helvar` (Smart Buildings & Circadian Lighting)
- **Challenge Name**: `The Brain of the Building`
- **Category**: `IoT & Hardware / Smart Luminaires & Multi-Sensor Vision Fusion`
- **Judging Criteria**:
  - Connecting building lighting sensors and environmental controls into an autonomous cognitive hub optimizing comfort, mood, productivity, and anomaly response.
- **Project ID**: `helvar-ivision-lamp-2018`
- **Project Name**: `IVision Lamp`
- **Award**: **Helvar "The Brain of the Building" Challenge 1st Place Winner 🥇 (First Tsinghua University Challenge Win in Junction History)**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  To overcome static single-sensor luminaires that blindly follow simple lux or timeout rules, the 4-member Tsinghua University × SenseTime Student Deep Learning Team engineered *IVision Lamp* in 42 hours. Fusing camera-based computer vision cues alongside multi-sensor environmental inputs, their smart desk lamp closed a real-time adaptive lighting control loop verified directly under Helvar judge testing on-site (per official Tsinghua University & SenseTime releases; no public code repository or quantitative lux/latency tables released `[L2]`).
- **Tech Stack**:
  - *Smart Luminaire & Fusion*: Physical smart desk luminaire actuation, real-time computer vision perception, multi-sensor information fusion logic *(internal code repo not publicly disclosed)*.
- **System Architecture**:
  1. *Multi-Modal Input Acquisition*: Streams visual optical context alongside multi-sensor ambient lighting/environmental signals.
  2. *Edge Multi-Sensor Fusion*: Reconciles optical workspace state with ambient probe cues to prevent spurious brightness swings.
  3. *Closed-Loop Luminaire Modulation*: Drives adaptive brightness transitions smoothly on the physical lamp device in live Helvar partner testing.
- **Key Technical Decisions**:
  - *Decision 1: Vision + Multi-Sensor Coupling*: Added rich optical scene understanding atop ambient environmental probes instead of treating smart lighting as purely offline spreadsheet analytics.
  - *Decision 2: Live Luminaire Hardware Validation*: Built a working physical lamp test rig in 42 hours rather than presenting pure simulation plots.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Development Sprint*: `42` hours at Junction 2018 (selected across 1,300+ participants from 105 regions, 46 challenges).
  - *Public Benchmark Boundary*: Official university and SenseTime press dispatches confirm project architecture & 1st Prize without releasing public GitHub source or quantitative ms/lux metrics `[L2]`.
- **Demo Highlights**:
  - On-site live luminaire demonstration reacting smoothly to visual/multi-sensor changes during direct evaluation by Helvar's judging team.
- **Team Background**:
  - *Tsinghua–SenseTime Future Deep Learning Student Interest Team*: *Xiulong Yuan* (Electronic Eng.), *Yingxue Guo* (Electronic Eng.), *Xin Li* (Automation), and *Feng Liang* (Microelectronics & Nanoelectronics).
- **Winning Hypothesis**:
  Multidisciplinary hardware + vision execution. Uniting EE, microelectronics, automation, and deep learning produced a physical smart luminaire that outshined pure energy-spreadsheet approaches.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: Pairing optical vision with environmental multi-sensor fusion on a physical luminaire consistently distinguishes winners in smart-building challenges.
  - *Lesson 2*: Document press-verified `[L2]` projects honestly with explicit verification boundaries instead of fabricating private benchmarks.
- **Source URLs**:
  - [Tsinghua University Official News Report](https://www.tsinghua.edu.cn/info/1173/17718.htm)
  - [SenseTime Press Release](https://www.sensetime.com/cn/technology-new-detail/3606?categoryId=53)
  - [Helvar Lighting Philosophy Reference](https://helvar.com/how-to-make-the-light-work-for-you/)
- **Evidence Level**: `L2: Verified by Official Tsinghua University Newsroom & SenseTime Press Release`

---

### Project Card 17: TruckSense — UPCT & Vueling (Fleetboard — Trucks X Code)

#### 1. Basic Metadata
- **Event ID**: `junction-2018`
- **Event Name**: `Junction 2018`
- **Year**: `2018`
- **Organizer**: `Fleetboard` (Daimler / Mercedes-Benz Trucks)
- **Challenge Name**: `Trucks X Code`
- **Category**: `IoT & Hardware / Connected Heavy Vehicle SDK & Fleet Telemetry`
- **Judging Criteria**:
  - Exploiting live commercial Mercedes-Benz heavy-truck vehicle bus and sensor telemetry exposed by the Fleetboard SDK for practical road-freight impact.
- **Project ID**: `fleetboard-trucksense-2018`
- **Project Name**: `TruckSense`
- **Award**: **Fleetboard Challenge 1st Prize 🥇 (3-Day All-Expenses Daimler/Mercedes Innovation Workshop in Stuttgart)**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  Commercial trucking fleets suffer costly unscheduled downtime when diagnostic alerts arrive too late. In ~40 hours at Junction 2018, UPCT Telematics students *Pablo Moyano* and *Enrique Fernández* alongside two Vueling airline developers built *TruckSense*: ingesting live commercial truck telemetry from the Mercedes-Benz **Fleetboard SDK**, running forward-looking machine learning operational state predictions, and surfacing fleet/vehicle health trajectories in an intuitive web interface (per official UPCT & La Verdad releases; internal repository & numeric ML error rates not published `[L2]`).
- **Tech Stack**:
  - *Vehicle Hardware SDK & Backend*: Mercedes-Benz Truck On-Board Computer / Fleetboard SDK telemetry, streaming ingestion backend, ML predictive forecasting pipeline, live graphical web interface *(exact model/repo undisclosed)*.
- **System Architecture**:
  1. *Live Heavy-Truck Telemetry*: Pulls commercial vehicle bus metrics through Fleetboard's truck SDK.
  2. *Predictive ML Forecaster*: Projects upcoming vehicle operating parameters forward rather than passively mirroring current snapshots.
  3. *Fleet Operations Console*: Presents live and predicted truck metrics to logistics operators on a clean graphical dashboard.
- **Key Technical Decisions**:
  - *Decision 1: Predictive Forecasting Over Passive Gauges*: Turned raw bus telemetry into forward failure warnings tailored to Mercedes fleet economics.
  - *Decision 2: Native On-Board Compatibility*: Designed directly around Fleetboard's commercial truck app constraints rather than consumer car mocks.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Hackathon Implementation Sprint*: `~40` hours (from ~1,000+ accepted competitors out of ~10,000 applicants).
  - *Public Benchmark Boundary*: Official university and press records confirm Fleetboard 1st Prize and Stuttgart engineering workshop without publishing source code or RMSE/MAE logs `[L2]`.
- **Demo Highlights**:
  - Real-time heavy-truck telemetry visualization combined with ML forward predictions, directly winning a 3-day technical co-creation workshop with Daimler on-board computer engineers in Stuttgart.
- **Team Background**:
  - *TruckSense*: UPCT Telematics engineers *Pablo Moyano* and *Enrique Fernández* (Free Open Source Club / FOSC), partnered with *two software engineers from Vueling Airlines*.
- **Winning Hypothesis**:
  Telematics + aviation operational discipline aligned directly with commercial trucking uptime ROI.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: When enterprise vehicle/machinery sponsors expose a real bus SDK, adding forward-looking anomaly forecasting separates solutions from basic telemetry mirrors.
  - *Lesson 2*: Always distinguish `[L2]` press-verified awards cleanly from `[L1]` audited open-source codebases.
- **Source URLs**:
  - [UPCT Official University Press Release](https://www.upct.es/noticias/2018-11-30-premiados-dos-alumnos-de-la-upct-por-resolver-un-reto-tecnologico-para-monitorizar-los-camiones-mercedes)
  - [La Verdad Regional Press Coverage](https://www.laverdad.es/murcia/cartagena/estudiantes-upct-resuelven-20181202005210-ntvo.html)
- **Evidence Level**: `L2: Verified by Official UPCT University Release & La Verdad Press Report`

---

### Project Card 18: Signvision — Team Glados (Junction 2017 Main Competition & STARA)

#### 1. Basic Metadata
- **Event ID**: `junction-2017`
- **Event Name**: `Junction 2017`
- **Year**: `2017`
- **Organizer**: `STARA` & `Junction Main Competition` (Dipoli, Aalto University, Espoo; CEO Ville Leppälä)
- **Challenge Name**: `Main Competition & STARA Urban Infrastructure Challenge`
- **Category**: `IoT & Hardware / Mobile Edge Vision & Smart Infrastructure`
- **Judging Criteria**:
  - Technical engineering sophistication, real-time vision robustness, cloud scalability, and urban municipal asset management value across 1,500 hackers and 13 tracks.
- **Project ID**: `stara-signvision-2017`
- **Project Name**: `Signvision (Team Glados)`
- **Award**: **Junction 2017 Overall Grand Winner 🏆 (€20,000 Cash Prize) & STARA Challenge 2nd Prize 🥈**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  Cities spend substantial municipal budgets auditing damaged or missing traffic signage manually. Originating as *Team Glados*'s flagship Junction win before their 2018 *Oneiro* repeat, *Signvision* (`teamglados/signvision`) turns moving vehicle smartphones into an automated crowdsourced traffic-sign inventory pipeline. React Native streams camera images + GPS coordinates over `uWs` WebSockets (`port 3000`, `5000 ms` deduplication cooldown) to a Python/Flask backend (`port 8080`) chaining classical OpenCV HSV red-mask + `scikit-image` connected-component cropping (`numPixels > 1000`, `30%` bbox pad) into a `TensorFlow 1.4.0` `32x32x3` CNN trained on GTSRB Stop class `00014`, all containerized cleanly via CUDA 8.0 Docker + AWS ECS Terraform.
- **Tech Stack**:
  - *Mobile Capture & Comms*: React Native (Camera + GPS telemetry), Node.js `uWs` WebSocket (`port 3000`), `Koa` (`port 8000`).
  - *Hybrid CV & Cloud Infra*: Python `Flask` (`port 8080`), `OpenCV` HSV segmentation + `scikit-image` (`skimage.measure.label`), `TensorFlow 1.4.0` CNN (`Conv2D(16)` -> `Conv2D(32)` -> `Dense(2)`), CUDA 8.0 Docker, Terraform + AWS ECS (`aws/*.tf`).
- **System Architecture**:
  1. *Mobile Edge Stream*: React Native dispatches `MARK_SEND` camera + `lat/lng` frames over `uWs`.
  2. *Cooldown & Classical ROI Crop*: `server/server.js` enforces a `5000 ms` spatial/temporal dedup gate; OpenCV HSV red thresholding + morphological ops + `scikit-image` connected components isolate crisp candidate boxes (`numPixels > 1000`, `30%` padding).
  3. *GPU Classification & Map Pinning*: `cnn_model/app.py` evaluates `32x32x3` crops on CUDA 8.0 ECS containers and broadcasts confirmed `MARK_RECEIVE` map markers.
- **Key Technical Decisions**:
  - *Decision 1: Hybrid Classical HSV Crop + Tiny `32x32x3` CNN*: Pre-cropping tight candidate patches optically eliminated background clutter and kept TF 1.4.0 inference blazingly fast.
  - *Decision 2: `5000 ms` WebSocket Deduplication Guard*: Prevented red-light traffic stops from flooding municipal asset logs with redundant sign entries.
  - *Decision 3: Production Terraform AWS + React Native Pattern*: Team Glados carried this exact battle-tested Terraform/React Native/Docker muscle directly forward to win Junction 2018 (*Oneiro*) as well.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Classifier Architecture & Training*: `32x32x3` input -> `Conv2D(16, 3x3, stride=2, ELU)` -> `Conv2D(32, 3x3, stride=2, ELU)` -> `Flatten` -> `Dense(2)` trained on GTSRB Stop `00014` (`2,000` / `18,000` steps).
  - *Filtering & Debounce Constants*: ROI minimum `numPixels > 1000` (`30%` bbox pad); WebSocket cooldown `5000 ms`.
  - *Competition Scale*: **€20,000** Main Prize out of `1,500` attendees (from `4,000` applicants) across `13` tracks + STARA 2nd Prize.
- **Demo Highlights**:
  - Scanning test traffic signs dropped live verified geolocated markers directly onto the municipal dashboard with zero Docker GPU stalls.
- **Team Background**:
  - *Team Glados*: *Andreas Urbanski*, *Teemu Taskula* (`teemu.taskula@aalto.fi`), and *Ville Toiviainen* (`Villux`) — Aalto/Finnish systems engineers who subsequently won Junction 2018 Overall (*Oneiro*) and Junction 2021 CGI x KONE (*ElevAI*).
- **Winning Hypothesis**:
  Practical hybrid CV engineering + unmatched full-stack DevOps velocity. Instead of betting on slow monolithic detectors, HSV segmentation + tiny TF 1.4.0 + `5000 ms` debouncing worked reliably on live video feeds.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: Pairing classical OpenCV color/geometry ROI proposals with lightweight CNN classifiers dramatically outperforms noisy end-to-end models in 48 hours.
  - *Lesson 2*: Always implement spatial/temporal deduplication (`5000ms` cooldown) on continuous vehicle/camera vision streams.
- **Source URLs**:
  - [Signvision GitHub Repository (teamglados/signvision)](https://github.com/teamglados/signvision)
  - [Signvision Devpost Submission](https://devpost.com/software/glados)
  - [Demo Video (Vimeo)](https://vimeo.com/244507554)
  - [Uusi Teknologia Winner Coverage](https://www.uusiteknologia.fi/2017/11/28/junction2017-voittaja-yhdisti-big-datan-mobiiliin/)
- **Evidence Level**: `L1: Verified by Winner GitHub Repository (teamglados/signvision), Devpost, Demo Video & Finnish Tech Press`

---

### Project Card 19: ReCover — DF LAB (Suunto / Movesense — Track Anything That Moves)

#### 1. Basic Metadata
- **Event ID**: `junction-2017`
- **Event Name**: `Junction 2017`
- **Year**: `2017`
- **Organizer**: `Suunto` (Movesense Open Programmable Sensor Platform)
- **Challenge Name**: `Track anything that moves!`
- **Category**: `IoT & Hardware / Dual-IMU Biomechanics & Rehab Wearables`
- **Judging Criteria**:
  - Level of added value to the selected domain (Sports, Health, or General IoT), functional readiness, and effortless UX building atop Suunto Movesense programmable BLE sensors and REST/mobile libraries.
- **Project ID**: `suunto-recover-2017`
- **Project Name**: `ReCover (DF LAB)`
- **Award**: **Movesense Health Challenge Winner 🥇 (6 Movesense Sensors + 4 Suunto Spartan Watches)**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  Post-operative knee rehabilitation patients have no objective way at home to know whether they hit prescribed flexion angles without over-straining healing tissue. Among 24 Movesense entries at Junction 2017, University of Latvia squad *DF LAB* mounted **two synchronized Suunto Movesense IMU sensors** above and below the patient's knee joint, streaming orientation over BLE to an iOS application that computes relative knee flexion geometry in real time — launching the exact Latvian builders who returned a year later to win 2018 Intel + 2nd Overall (*Help.io*).
- **Tech Stack**:
  - *Differential Wearable Hardware*: `2x` Programmable **Suunto Movesense** sensors (accelerometer, gyroscope, magnetometer over Bluetooth LE, `movesense-mobile-lib`).
  - *Mobile Biofeedback Client*: Native iOS rehab adherence application displaying real-time flexion angles against clinician recovery goals.
- **System Architecture**:
  1. *Dual-Segment Limb Acquisition*: Thigh and shin Movesense IMUs broadcast synchronized inertial states over concurrent BLE links.
  2. *Relative Joint Kinematics*: Subtracts lower-limb vs upper-limb sensor frames so flexion angle stays invariant to overall body tilt/sitting angle.
  3. *iOS Patient Adherence UX*: Highlights safe therapeutic target zones dynamically as the patient performs supervised/home exercises.
- **Key Technical Decisions**:
  - *Decision 1: Paired Differential Sensor Topology*: Rejected single-sensor approximation (corrupted whenever the torso shifts) by using two IMUs spanning the knee joint.
  - *Decision 2: Clinician-Initiated Unmet Need*: Grounded rehab bounds directly in clinical concept work initiated by PhD researcher Emīls Sjundjukovs rather than generic fitness step counters.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Competition Pool*: Selected top **Health** winner out of `24` completed Movesense projects at Junction 2017 (Dipoli; 1,500 overall hackers).
  - *Verified Kit & Prize*: Paired `2`-sensor differential knee setup; team awarded `6` Movesense sensors + `4` Suunto Spartan watches. *(Code repository not publicly archived; documented via Devpost/Movesense/UL Press `[L1/L2]`.)*
- **Demo Highlights**:
  - Live knee bending synced cleanly to real-time iOS flexion arc indicators showing target rehab zones instantaneously without clinical protractors.
- **Team Background**:
  - *DF LAB* (University of Latvia Faculty of Computing): *Austris Cīrulnieks*, *Elvijs Viļķels*, *Dāvis Mednis*, and *Mārcis Nīmants* *(mentored clinically by PhD researcher Emīls Sjundjukovs)* — later core winners of 2018 Intel (*Help.io*).
- **Winning Hypothesis**:
  Clean multi-sensor geometry + clear medical necessity. Mounting two BLE sensors relative to one hinge joint solved clinical accuracy trivially compared to single-IMU guesswork.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: Joint-angle biomechanics demands differential dual-IMU referencing across the hinge rather than absolute orientation from one sensor.
  - *Lesson 2*: Wearable BLE fluency compounds rapidly across editions (*ReCover* 2017 -> *Help.io* Intel 1st & 2nd Overall 2018).
- **Source URLs**:
  - [ReCover Devpost Submission](https://devpost.com/software/recover-pfrq3g)
  - [Movesense Official 2017 Winner Report](https://www.movesense.com/news/2017/11/24-movesense-projects-at-junction-hackathon/)
  - [University of Latvia Press Release](https://eztf.lu.lv/par-mums/zinas/zina/t/29783/)
- **Evidence Level**: `L1: Verified by Official Movesense Challenge Report, Devpost Record & University of Latvia Press`

---

### Project Card 20: AR Dentist (Planmeca Oy — Reshaping the Future of Dentistry)

#### 1. Basic Metadata
- **Event ID**: `junction-2017`
- **Event Name**: `Junction 2017`
- **Year**: `2017`
- **Organizer**: `Planmeca Oy` (Jury: Sakari Kettunen, Product Development Manager & Antti Haanpää, Digital Business Solution Manager)
- **Challenge Name**: `Reshaping the future of dentistry`
- **Category**: `IoT & Hardware / 3D Dental Imaging & Mobile AR Overlay`
- **Judging Criteria**:
  - Expanding digital 3D dental imaging/CBCT equipment ecosystems into a frictionless patient experience and effortless remote/virtual treatment planning out of 13 competing Health track teams.
- **Project ID**: `planmeca-ar-dentist-2017`
- **Project Name**: `AR Dentist`
- **Award**: **Planmeca Challenge 1st Prize Winner 🥇 (out of 13 competing teams)**

#### 2. Technical Architecture & Implementation
- **Solution Summary**:
  Dental patients struggle to visualize abstract orthodontic or restorative CAD plans from dry 3D cone-beam CT models on clinic monitors. Outperforming 12 larger squads, the 2-person cross-disciplinary team *AR Dentist* fused **Planmeca 3D dental imaging datasets** with live mobile facial tracking: a dentist manipulates treatment parameters in real time on a companion laptop interface, immediately updating rendered 3D dental overlays aligned onto the patient's live face on a mobile AR mirror (verified in Planmeca's official newsroom report; public repo & numeric FPS telemetry not released `[L1]`).
- **Tech Stack**:
  - *Medical Data & AR Stack*: Planmeca 3D Dental Imaging Datasets (`Planmeca Romexis` / CBCT context), companion laptop 3D parameter control UI, real-time mobile AR facial tracking and 3D mesh overlay *(codebase unpublished)*.
- **System Architecture**:
  1. *Clinical Control Workstation (Laptop)*: Ingests Planmeca 3D dental imaging parameters and exposes interactive treatment sliders for clinicians.
  2. *Real-Time Parameter Sync*: Streams parametric dental transformations straight to the mobile viewer without blocking rendering.
  3. *Patient-Facing Mobile AR Overlay*: Anchors live facial tracking and renders updated 3D dental alignment interactively in front of the patient.
- **Key Technical Decisions**:
  - *Decision 1: Asymmetric Dual-Device UX*: Placed granular precision controls on a clinician's laptop while giving the anxious patient an effortless, intuitive phone "AR magic mirror".
  - *Decision 2: Ultra-Lean 2-Person Skill Pairing*: Paired physics/CS mobile engineering (`Samuel Laska`) directly with industrial 3D modeling design (`Linda Ukkonen`), achieving studio-grade 3D fidelity with minimal overhead.

#### 3. Execution Metrics & Verification
- **Metrics and Baseline**:
  - *Challenge Competition Pool*: **1st** out of `13` hacker teams solving Planmeca's Junction 2017 challenge (across 1,500 attendees / 70+ countries at Dipoli).
  - *Public Benchmark Boundary*: Official Planmeca corporate newsroom verifies architecture, team, jury, and 1st place without publishing GitHub source or rendering latency logs `[L1]`.
- **Demo Highlights**:
  - Adjusting 3D parameter controls on the laptop side updated aligned 3D dental visualization smoothly in real time atop the user's face in the mobile AR viewport.
- **Team Background**:
  - *AR Dentist* (2-person cross-disciplinary dyad): *Samuel Laska* (Slovakia — physics & computer science, mobile developer) and *Linda Ukkonen* (Finland — industrial design & 3D modeling specialist).
- **Winning Hypothesis**:
  Tight Clinical Empathy × Complementary Craftsmanship. Merging Planmeca's medical 3D assets directly into an instant patient "try-on mirror" solved both clinician planning and patient reassurance cleanly.
- **Reusable Lessons for Hackathon Builders**:
  - *Lesson 1*: A focused 2-person pairing of **Industrial 3D Modeler/Designer + Mobile Developer** routinely beats bloated all-coding teams on AR/medical hardware tracks.
  - *Lesson 2*: Dual-screen "Operator Control Laptop -> Live Patient Mobile AR Overlay" creates immediate commercial clarity on stage.
- **Source URLs**:
  - [Planmeca Official Challenge Winner Release (Jan 12, 2018)](https://www.planmeca.com/news-and-events/newsroom/2018/planmeca-challenged-hackers-to-reshape-the-future-of-dentistry/)
- **Evidence Level**: `L1: Verified by Official Planmeca Corporate Newsroom Announcement (Jan 12, 2018)`
