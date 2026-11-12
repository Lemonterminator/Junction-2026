# 2026 Hardware Track (by Arduino) — Historical Challenge Archive (2017–2025)

> **Source**: `docs/past/bronze/challenges_full.json` (Hack Junction Historical Challenges 2017–2025)
> **Total Challenges Included**: **43 challenges**
> **Target Track (2026)**: `Hardware Track (by Arduino)`

---

## 1. Track Definition & Reorganization Criteria

# 2026 Hardware Track (by Arduino) — Historical Challenge Reorganization Archive (Silver Layer)

## Track Definition & Reorganization Criteria

**Corresponding 2026 Track**: **Hardware Track (by Arduino)**

This directory systematically reorganizes and curates all challenges from Hack Junction 2017–2025 (all 147 challenges in the Bronze layer) that relate to **smart hardware, sensor networks, embedded systems, robotics and automation control, wearable devices, mmWave radar/event cameras, and digitization of the physical world (IoT & Physical Computing)**:

1. **Complete retention of all 11 challenges from the historical `IoT & Hardware` track**: Covering wearable motion sensors (Suunto Movesense), cross-platform embedded development (The Qt Company / Raspberry Pi), RFID indoor/outdoor positioning (Finn-ID), narrowband IoT emergency communication (Ericsson NB-IoT), smart charging station development boards (Ensto), Bluetooth Mesh edge gateways (Intel), apartment building smart interactive displays (Aalto University), indoor sensor network positioning (Helvar), elevator and building digital twins (KONE), and wireless sauna IoT sensors (Harvia).
2. **Deep mining and aggregation of 32 hardware/sensor/robotics challenges from 9 other historical tracks**:
   - **mmWave Radar and High-Speed Machine Vision Sensors**: Sensofusion microsecond-level neuromorphic event camera (Event Camera) high-speed object and drone tracking, Sensofusion urban radio wave propagation simulation, Helvar & VTT 60GHz/24GHz mmWave radar indoor sensing and contactless vital sign extraction.
   - **Wearable Devices, Smart Glasses, and Biosensing Hardware**: Snap fifth-generation Spectacles AR smart glasses, Pixieray 12-channel infrared eye-tracking smart glasses, Huawei STMicroelectronics (STM SensorTile) embedded wearable development kit, Movesense motion sensors.
   - **Robotics, Heavy Machinery, and Specialized Hardware Equipment**: Alepa candy-picking robot mobile control, CGI & KONE & Meyer Turku luxury cruise ship autonomous service robot, ABB electrified connected vessel, Valmet paper machine roller micron-level grinding sensors and XR maintenance, Valmet x HSY industrial OPC UA protocol-based autonomous control of wastewater pumping stations, Planmeca 3D intraoral scanners and digital dental treatment unit hardware.
   - **Smart Buildings, Smart Water, and Environmental Sensing Hardware**: Helvar smart lighting sensor room (PIR/thermal imaging camera/emotion ring), Vaisala meteorological instruments and high-temperature high-humidity sauna sensing instruments, Oras Bluetooth smart faucets and digital showerheads, Ensto smart electric heating hardware, KONE x Granlund building MEP (Mechanical, Electrical, and Plumbing) hardware asset inventory.
   - **Edge Computing Clusters, In-Vehicle Hardware, and RF Terminals**: SUSE Raspberry Pi (Raspberry Pi 3B+/4B+) uMEC edge computing cluster, Ericsson / Nokia 5G low-latency edge hardware control, Fleetboard Mercedes-Benz heavy truck real-time telemetry SDK, Rightware smart vehicle digital instrument cluster, DENSO vehicle-to-charger interconnection hardware, Stora Enso smart packaging/wooden structure RFID sensors, Nexi NFC card reader hardware protocol parsing, TrueFace Chui smart access control hardware, Trimble HoloLens mixed reality building measurement.

---

## 2. Challenge Directory & Summary Table

| # | Year | Partner | Challenge Name | Historical Track | Core Theme | Details |
| :---: | :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | **2017** | **Suunto** | Track anything that moves - Build a Movesense based tracking concept for sports, health or something else | `IoT & Hardware` | Movesense programmable motion sensors and C++ embedded firmware development | [📄 View Details](./2017_Suunto_Track_Anything_That_Moves.md) |
| 2 | **2017** | **The Qt Company** | Cross Platform for Desktop and Embedded - Create the User Experience of a lifetime on multiple platforms. | `IoT & Hardware` | Cross-platform embedded device UI and interaction development based on Raspberry Pi and Qt | [📄 View Details](./2017_The_Qt_Company_Cross_Platform_Embedded.md) |
| 3 | **2017** | **Finn-ID Oy** | Where the #?! is it? – RFID Helps. - Create a navigation app.  by using RFID tags. | `IoT & Hardware` | Indoor/outdoor item positioning and navigation using RFID readers, electronic tags, and Vuzix M300 smart glasses | [📄 View Details](./2017_Finn_ID_RFID_Navigation.md) |
| 4 | **2018** | **Espoo** | Analyzed Information at your Fingertips | `IoT & Hardware` | Automated collection, fusion analysis, and embedded visualization components for multi-source open data in cities and regions | [📄 View Details](./2018_Espoo_Analyzed_Information_At_Your_Fingertips.md) |
| 5 | **2018** | **Ericsson** | Saved by IoT | `IoT & Hardware` | Distributed NB-IoT deployment and wearable sensor gateways in disaster-area network-disconnected environments | [📄 View Details](./2018_Ericsson_Saved_By_IoT.md) |
| 6 | **2018** | **Ensto** | Teach EV Chargers New Tricks | `IoT & Hardware` | Feature extension for smart EV charging stations based on hardware development boards and the Ensto IoT platform | [📄 View Details](./2018_Ensto_Teach_EV_Chargers_New_Tricks.md) |
| 7 | **2018** | **Intel** | Innovative Applications With Bluetooth Mesh | `IoT & Hardware` | Smart space control based on IoT edge gateways and Bluetooth Mesh wireless sensor networks | [📄 View Details](./2018_Intel_Innovative_Applications_With_Bluetooth_Mesh.md) |
| 8 | **2019** | **Aalto University** | Smart Signage - For Student by Students | `IoT & Hardware` | Hardware form factor design for apartment building smart signage and integration of HVAC/water-electricity/network IoT data | [📄 View Details](./2019_Aalto_University_Smart_Signage.md) |
| 9 | **2021** | **Helvar** | Brighter Spaces: Intelligent Lighting | `IoT & Hardware` | Self-calibration of indoor motion and audio sensor networks, high-frequency pedestrian trajectory recognition, and multimodal perception in underground garages | [📄 View Details](./2021_Helvar_Brighter_Spaces_Intelligent_Lighting.md) |
| 10 | **2024** | **KONE** | BIM for any building, by anyone. | `IoT & Hardware` | Rapid 3D BIM modeling of existing buildings and elevator electromechanical equipment, IoT remote operations, and digital twins | [📄 View Details](./2024_KONE_BIM_For_Any_Building.md) |
| 11 | **2025** | **Harvia** | Sauna Intelligence | `IoT & Hardware` | Harvia wireless battery-powered sauna IoT sensors (temperature/humidity/presence detection/BLE beacon) and smart home integration | [📄 View Details](./2025_Harvia_Sauna_Intelligence.md) |
| 12 | **2017** | **Helvar** | Who needs a light switch? - Automate the whole process of controlling light. | `AI & Data` | Automated lighting hardware control based on passive infrared (PIR), FLIR thermal cameras, light sensors, and Moodmetric emotion rings | [📄 View Details](./2017_Helvar_Who_Needs_A_Light_Switch.md) |
| 13 | **2017** | **Planmeca Oy** | Reshaping the future of dental care. - Dive into the world of technology and use it to revolutionize dental care. | `Health` | Hardware digitization of digital dental treatment units, 3D oral imaging equipment, and intraoral scanners | [📄 View Details](./2017_Planmeca_Reshaping_Dental_Care.md) |
| 14 | **2017** | **Trimble** | Transform the way the world builds! - Create the next big thing in digitalizing the building industry. | `AI & Data` | 3D measurement sensing of physical building spaces and Microsoft HoloLens mixed reality hardware interaction | [📄 View Details](./2017_Trimble_Transform_The_Way_The_World_Builds.md) |
| 15 | **2017** | **TrueFace.ai** | Facial Recognition for Everyone - Create an app using one or multiple of TrueFace.ai facial recognition APIs | `AI & Data` | Facial recognition and anti-spoofing detection system based on Chui smart doorbell and access control terminal hardware | [📄 View Details](./2017_TrueFace_Facial_Recognition_For_Everyone.md) |
| 16 | **2017** | **Stora Enso's challenge in cooperation with Siili Solutions** | Store smarter - Is there intelligent life in your space? | `Sustainability` | RFID reader/antenna arrays and CLT/LVL smart timber building components with built-in temperature and humidity sensors | [📄 View Details](./2017_Stora_Enso_Siili_Store_Smarter.md) |
| 17 | **2018** | **Outotec** | I hear voices in my factory | `Sustainability` | Acoustic (Audio) and Motion sensor fault diagnosis and early warning for high-temperature heavy equipment in metallurgical plants | [📄 View Details](./2018_Outotec_I_Hear_Voices_In_My_Factory.md) |
| 18 | **2018** | **Helvar** | The Brain of the Building | `AI & Data` | Building-level intelligent control hub integrating lighting control sensors and ventilation/HVAC hardware | [📄 View Details](./2018_Helvar_The_Brain_Of_The_Building.md) |
| 19 | **2018** | **Alepa** | Munchies Robot Hack | `Entertainment` | Remote control of a physical pick-and-pay candy robot via mobile devices (Pick 'n' Pay Candy Robot) | [📄 View Details](./2018_Alepa_Munchies_Robot_Hack.md) |
| 20 | **2018** | **Fleetboard** | Trucks X Code | `Urban & Mobility` | In-vehicle application development based on Mercedes-Benz heavy truck onboard sensors and live vehicle telemetry data | [📄 View Details](./2018_Fleetboard_Trucks_X_Code.md) |
| 21 | **2018** | **Rightware** | Connected Car UX Challenge | `Sustainability` | Smart connected vehicle digital instrument clusters, in-vehicle multi-screen cockpits, and adaptive interaction with interior/exterior environmental perception | [📄 View Details](./2018_Rightware_Connected_Car_UX.md) |
| 22 | **2018** | **Ensto** | Adaptive Smart Electric Heating | `Sustainability` | Adaptive temperature control and energy consumption optimization for programmable smart electric heating hardware devices | [📄 View Details](./2018_Ensto_Adaptive_Smart_Electric_Heating.md) |
| 23 | **2018** | **ABB** | Do Captains Dream of Electric Ships? | `Other` | ABB electrified, digitalized, and connected future ships (Electric & Connected Ships) hardware and control system innovation | [📄 View Details](./2018_ABB_Do_Captains_Dream_Of_Electric_Ships.md) |
| 24 | **2018** | **Nokia** | Living on the Edge | `Entertainment` | Real-time hardware interaction applications based on Nokia 5G ultra-low latency radio access network and edge computing (MEC) | [📄 View Details](./2018_Nokia_Living_On_The_Edge.md) |
| 25 | **2018** | **Movesense By Suunto** | Track Anything that Moves | `Entertainment` | Monitoring of sports equipment, human body, production lines, and bridges based on Movesense inertial measurement unit (IMU) sensors | [📄 View Details](./2018_Movesense_By_Suunto_Track_Anything_That_Moves.md) |
| 26 | **2018** | **Vaisala** | Actually Useful Weather | `Sustainability` | Fusion applications of Vaisala high-precision meteorological and environmental measurement instrument data in maritime, agricultural, aviation, and building scenarios | [📄 View Details](./2018_Vaisala_Actually_Useful_Weather.md) |
| 27 | **2018** | **Vaisala** | Hack the Sauna | `Sustainability` | Industrial-grade sauna sensing and measurement instruments (replacing traditional mechanical thermometers) and digital experience in extreme high-temperature and high-humidity environments | [📄 View Details](./2018_Vaisala_Hack_The_Sauna.md) |
| 28 | **2018** | **Cisco** | Meraki - Capture the Creature | `Entertainment` | Indoor spatial awareness based on Cisco Meraki Bluetooth beacons (BLE Beacon) and Wi-Fi wireless positioning hardware | [📄 View Details](./2018_Cisco_Meraki_Capture_The_Creature.md) |
| 29 | **2019** | **Ericsson** | Greener City Transport with 5G | `Urban & Mobility` | Centralized real-time control of vehicle fleets and coordinated scheduling of multi-source sensors based on 5G low-latency communication networks | [📄 View Details](./2019_Ericsson_Greener_City_Transport_With_5G.md) |
| 30 | **2019** | **Valmet** | Service Workshop of the Future | `AI & Data` | Micron-level grinding sensor measurement data for giant paper machine rollers, Node-RED hardware simulation, and XR headset interaction | [📄 View Details](./2019_Valmet_Service_Workshop_Of_The_Future.md) |
| 31 | **2019** | **Helvar & VTT** | Making Spaces Brighter with Radar Technology | `AI & Data` | 60 GHz 2D millimeter-wave imaging radar and 24 GHz vital-sign radar sensors + real-time integration with smart luminaire hardware | [📄 View Details](./2019_Helvar_VTT_Making_Spaces_Brighter_With_Radar.md) |
| 32 | **2019** | **SUSE** | Open Open City | `Urban & Mobility` | Edge computing platform based on a Raspberry Pi 3B+/4B+ hardware cluster (uMEC edge nodes) and a dedicated Wi-Fi network | [📄 View Details](./2019_SUSE_Open_Open_City.md) |
| 33 | **2022** | **Oras** | The Smartest Water Experience | `Sustainability` | Oras Hydractiva digital showerhead and touchless Bluetooth smart faucets (SMART Faucets) water sensing and leak localization | [📄 View Details](./2022_Oras_The_Smartest_Water_Experience.md) |
| 34 | **2022** | **CGI & KONE & Meyer Turku** | Cruising with Robots | `Other` | Design of autonomous service robots and automated passenger/cargo flow hardware systems on large luxury cruise ships | [📄 View Details](./2022_CGI_KONE_Meyer_Turku_Cruising_With_Robots.md) |
| 35 | **2022** | **Nexi** | Crack the Payments | `Finance` | Low-level communication protocol analysis of financial IC cards based on external NFC reader hardware and mobile NFC modules | [📄 View Details](./2022_Nexi_Crack_The_Payments.md) |
| 36 | **2024** | **Pixieray** | Peek Behind the Eyes | `Entertainment` | Data analysis of smart glasses hardware integrating 6 infrared eye-tracking sensors per eye, accelerometer, and ambient light/UV sensors | [📄 View Details](./2024_Pixieray_Peek_Behind_The_Eyes.md) |
| 37 | **2024** | **Huawei** | Sense the motion | `AI & Data` | Real-time motion/emotion sensing algorithms based on STMicroelectronics SensorTile development kits and smartwatches | [📄 View Details](./2024_Huawei_Sense_The_Motion.md) |
| 38 | **2025** | **KONE x Granlund** | Modernizing a trillion-euro inventory | `AI & Data` | Automated inspection and collection of physical building MEP (mechanical, electrical, plumbing) equipment assets and ultimate digital twin construction | [📄 View Details](./2025_KONE_Granlund_Modernizing_Trillion_Euro_Inventory.md) |
| 39 | **2025** | **Denso** | ChargeID: Trusted EV Services | `Urban & Mobility` | Secure interconnection of automotive tier-one supplier DENSO vehicle-side hardware, smart charging piles, and decentralized identity (DID) | [📄 View Details](./2025_Denso_ChargeID_Trusted_EV_Services.md) |
| 40 | **2025** | **Sensofusion** | Lights, Camera, Reaction! | `AI & Data` | Microsecond-level neuromorphic event camera high-speed physical motion detection and drone tracking | [📄 View Details](./2025_Sensofusion_Lights_Camera_Reaction.md) |
| 41 | **2025** | **Sensofusion** | Radio City | `Entertainment` | Physical propagation and multipath reflection simulation of radio waves from mobile radios, vehicles, and drones in 3D urban environments | [📄 View Details](./2025_Sensofusion_Radio_City.md) |
| 42 | **2025** | **Valmet x HSY** | Intelligent Flow Optimization | `Sustainability` | Autonomous collaborative control of urban sewage pump station hardware clusters based on industrial automation protocol OPC UA and digital twins | [📄 View Details](./2025_Valmet_HSY_Intelligent_Flow_Optimization.md) |
| 43 | **2025** | **Snap Inc.** | Your Real-World AI Companion | `AI & Data` | Spatial perception and all-day personal AI companion based on fifth-generation Snap Spectacles AR smart glasses hardware | [📄 View Details](./2025_Snap_Your_Real_World_AI_Companion.md) |

---

## 3. Structured Breakdown & Consolidated Listing

### 1. [2017] Suunto — Track anything that moves - Build a Movesense based tracking concept for sports, health or something else

- **File**: [2017_Suunto_Track_Anything_That_Moves.md](./2017_Suunto_Track_Anything_That_Moves.md)
- **Original Track**: `IoT & Hardware` | **Sub-theme**: Wearables, Motion & Biometric Sensors
- **Core Theme**: Movesense programmable motion sensors and C++ embedded firmware development
- **Classification Rationale**: Originally in the IoT & Hardware track. Centered on Suunto Movesense programmable motion sensor hardware, programming jigs, and embedded C++ firmware with mobile REST/BLE interface development, representing a typical micro-sensor and wearable hardware development challenge.

#### Description

The world is full of things that move – whether it’s an athlete’s body or sports equipment, a machine on a production line, a bridge under traffic, any of us in our daily life, or anything else that we can imagine. Often it would be highly valuable to know how and when these things move – or don’t move. Movesense offers a programmable motion sensor, API’s and software libraries that enable you to quickly build your own sensor functions and mobile applications to track anything that moves. Help the world to stay on the move!

#### Resources

Find out more at www.movesense.com.
https://bitbucket.org/suunto/movesense-device-lib (public from early September)
https://bitbucket.org/suunto/movesense-mobile-lib (will be made public soon)

#### Prizes

All teams that submit a Movesense based project can keep the Movesense sensors used in development. As winner prizes, we will hand out the latest Suunto Spartan watch for each team member of the best solutions in three categories: 1. Sports 2. Health and Wellbeing 3. General IoT In addition, teams with commercially viable solutions for sports and daily wellbeing will have an opportunity to talk with Suunto about partnering options.

---

### 2. [2017] The Qt Company — Cross Platform for Desktop and Embedded - Create the User Experience of a lifetime on multiple platforms.

- **File**: [2017_The_Qt_Company_Cross_Platform_Embedded.md](./2017_The_Qt_Company_Cross_Platform_Embedded.md)
- **Original Track**: `IoT & Hardware` | **Sub-theme**: Embedded Systems, Edge Computing & Connectivity
- **Core Theme**: Cross-platform embedded device UI and interaction development based on Raspberry Pi and Qt
- **Classification Rationale**: Originally in the IoT & Hardware track. The organizers provided multiple Raspberry Pi embedded development boards and peripheral kits on-site, requiring the use of C++/Qt to build high-performance interactive systems spanning desktop and embedded smart hardware terminals.

#### Description

Create fluid, high-performance and intuitive UIs, applications, and embedded devices – with the same code base for all platforms. In our homes, our cars, our workplaces and our pockets smart devices are everywhere. Qt makes sure you can create unique & modern connected devices that stand out from the crowd.

#### Resources

You can find a lot of resources and help to Qt at for instance:
- http://doc.qt.io
- http://forum.qt.io
and other qt.io sites

#### Prizes

The prize for this challenge is a license to the full Qt developer licenese. Other prizes will be revealed at a later date, follow this space!

---

### 3. [2017] Finn-ID Oy — Where the #?! is it? – RFID Helps. - Create a navigation app.  by using RFID tags.

- **File**: [2017_Finn_ID_RFID_Navigation.md](./2017_Finn_ID_RFID_Navigation.md)
- **Original Track**: `IoT & Hardware` | **Sub-theme**: RFID, Indoor Positioning & Smart Terminals
- **Core Theme**: Indoor/outdoor item positioning and navigation using RFID readers, electronic tags, and Vuzix M300 smart glasses
- **Classification Rationale**: Originally in the IoT & Hardware track. On-site provision of RFID readers, RFID tags, Vuzix M300 smart glasses, Honeywell industrial mobile terminals, and Toshiba printers, focusing on RFID hardware and augmented reality navigation integration.

#### Description

Nowadays, technology makes possible to locate the locations of the items. By using this technology, we can facilitate and enhance the everyday lives of the people and businesses. We can create a clear view of the data.

#### Resources

You will get all the necessary details during the event.

#### Prizes

Team member prizes (our assumption 4-6-person team)
First prize: Each member of the team gets a $ 100 gift voucher to the Amazon
Second prize: Each member of the team gets a $ 50 gift voucher to the Amazon Team member prizes (our assumption 4-6-person team)
First prize: Each member of the team gets a $ 100 gift voucher to the Amazon
Second prize: Each member of the team gets a $ 50 gift voucher to the Amazon

---

### 4. [2018] Espoo — Analyzed Information at your Fingertips

- **File**: [2018_Espoo_Analyzed_Information_At_Your_Fingertips.md](./2018_Espoo_Analyzed_Information_At_Your_Fingertips.md)
- **Original Track**: `IoT & Hardware` | **Sub-theme**: Smart Buildings, Industrial IoT & Digital Twins
- **Core Theme**: Automated collection, fusion analysis, and embedded visualization components for multi-source open data in cities and regions
- **Classification Rationale**: Originally an official challenge in the 2018 IoT & Hardware track. Focused on automated aggregation, real-time updates, and enterprise-oriented embedded information dashboards for city-level multi-source sensor and public open data in Espoo.

#### Description

Develop a solution or solutions that generate information by joining, analyzing and visualizing open data sets. This solution should able to be embedded in websites, update information automatically and generate information that interests especially enterprises.
National, regional and local governments generate uncounted amounts of various open data sets. These open data sets can be transformed into useful regional information by using data analyzing tools which the city of Espoo has already done to some extent.
However, this already analyzed regional information is often scattered or otherwise difficult to find. Also, due to limited financial resources much of this regional data has not been analyzed. As a result, various private actors experience difficulties in acquiring all the relevant and necessary information.
The city of Espoo is looking for cost-effective ways to transform data sets into useful regional information and distribute it to various private actors already located in Espoo area or aiming to relocate/expand into Espoo area.
The challenge is to develop a solution or solutions that generate information by joining, analyzing and visualizing open data sets. This solution should generate information that interests especially enterprises. Also, this solution should be able to be embedded in different type of websites and update information automatically.

---

### 5. [2018] Ericsson — Saved by IoT

- **File**: [2018_Ericsson_Saved_By_IoT.md](./2018_Ericsson_Saved_By_IoT.md)
- **Original Track**: `IoT & Hardware` | **Sub-theme**: Embedded Systems, Edge Computing & Connectivity
- **Core Theme**: Distributed NB-IoT deployment and wearable sensor gateways in disaster-area network-disconnected environments
- **Classification Rationale**: Originally in the IoT & Hardware track. Combines distributed Narrowband IoT (NB-IoT) deployment solutions for scenarios with damaged communication infrastructure, with wearable device sensors for real-time vital sign collection acting as IoT cloud gateways.

#### Description

Imagine a situation where a natural disaster hits your neighborhood, and local communication infrastructure is knocked out. In the middle of the havoc, how can you reach out and tell your family and loved ones that you are still here, alive and kicking? Or indicate that you are hurt, in danger, needing help?
Smartphones and wearable devices collect lots of data, which can be made available to indicate the wearer’s whereabouts and condition. The sensor data streams can be analyzed and interpreted for example by machine learning solutions in cloud (or any other suitable place), to produce and make available indication of danger, aliveness, etc.
This challenge is twofold:
- Provide (at least) a conceptual plan with evidence of technical feasibility on how to create and deploy distributed narrow band IoT connectivity when local infra is down.
- Build an application which demonstrates the capability of applicable wearable device to provide sensor data and acting as a gateway towards IoT cloud. Note that the same solution may be used for smaller scale incidents (like car accidents) when the local communication infrastructure is intact.

---

### 6. [2018] Ensto — Teach EV Chargers New Tricks

- **File**: [2018_Ensto_Teach_EV_Chargers_New_Tricks.md](./2018_Ensto_Teach_EV_Chargers_New_Tricks.md)
- **Original Track**: `IoT & Hardware` | **Sub-theme**: Smart Energy, EV Charging & Mobility Hardware
- **Core Theme**: Feature extension for smart EV charging stations based on hardware development boards and the Ensto IoT platform
- **Classification Rationale**: Originally in the IoT & Hardware track. Required developing new features on on-site provided hardware development boards and deeply integrating with the Ensto smart charging station IoT backend REST API.

#### Description

Car charging can be much more than just plugging a car and filling the battery. Cars are charged in homes, workplaces, hotels, shopping malls, car parks and airports, to just mention a few, and in all these places the user may have different needs. Create the best possible car charging experience for the electric car driver on one or more segments. Implement/demo this solution utilizing Ensto’s platform offered REST API and additional functionality developed on top of the provided development boards. You can also utilize the already collected IoT data from our backend service for your solution.

---

### 7. [2018] Intel — Innovative Applications With Bluetooth Mesh

- **File**: [2018_Intel_Innovative_Applications_With_Bluetooth_Mesh.md](./2018_Intel_Innovative_Applications_With_Bluetooth_Mesh.md)
- **Original Track**: `IoT & Hardware` | **Sub-theme**: Embedded Systems, Edge Computing & Connectivity
- **Core Theme**: Smart space control based on IoT edge gateways and Bluetooth Mesh wireless sensor networks
- **Classification Rationale**: Originally in the IoT & Hardware track. Required building smart lighting, temperature control, security, or smart badge systems on IoT edge gateways that communicate with Bluetooth® Mesh wireless sensor network devices.

#### Description

Bluetooth® Mesh networking creates new opportunities for interacting with your environment, whether you’re making your home or office smarter using intelligent lighting, heating/cooling, and security systems, or wireless sensor networks.
The challenge includes creating an application, on IoT edge gateway, which is communicating and utilizing the capabilities of Bluetooth® Mesh network devices. Examples of such applications could be messaging boards, smart badge system or sensor data collection system.

---

### 8. [2019] Aalto University — Smart Signage - For Student by Students

- **File**: [2019_Aalto_University_Smart_Signage.md](./2019_Aalto_University_Smart_Signage.md)
- **Original Track**: `IoT & Hardware` | **Sub-theme**: Smart Buildings, Industrial IoT & Digital Twins
- **Core Theme**: Hardware form factor design for apartment building smart signage and integration of HVAC/water-electricity/network IoT data
- **Classification Rationale**: Originally in the IoT & Hardware track. Hardware and software design for corridor smart interactive displays across 2,600 apartments in AYY student housing, integrating real sensor data such as building HVAC, water/electricity consumption, and network load.

#### Description

The Aalto University Student Union (AYY) owns about 2600 apartments, which house around 3500 tenants. AYY has been planning to install information screens (smart signage) to the stairwells and hallways of its apartment buildings. This challenge is about finding solutions and ideas on what these “smart signage” screens could be like in terms of their hardware, but most importantly in terms of their software. What information could they show and what kind of functionality could they include?

AYY would like to see different kinds of ideas and concepts about what kinds of relevant data and functionality could be incorporated into these screens. These can include, for example, data about the building’s heat, water, and electricity consumption, network usage data, AYY’s news and advertising, tenant listings that update automatically, and all kinds of fun functionality that could also work between the screens in different hallways and buildings. At their best, the solutions to this challenge could also improve the experience of communality between the students living in AYY’s housing.

#### Resources

AYY will provide: AYY’s IT-team will be on promises during the weekend to help you out with the challenge. We will bring an anonymized package of network usage data and HVAC-data from one of our buildings for you to use.

---

### 9. [2021] Helvar — Brighter Spaces: Intelligent Lighting

- **File**: [2021_Helvar_Brighter_Spaces_Intelligent_Lighting.md](./2021_Helvar_Brighter_Spaces_Intelligent_Lighting.md)
- **Original Track**: `IoT & Hardware` | **Sub-theme**: Smart Buildings, Industrial IoT & Digital Twins
- **Core Theme**: Self-calibration of indoor motion and audio sensor networks, high-frequency pedestrian trajectory recognition, and multimodal perception in underground garages
- **Classification Rationale**: Originally in the IoT & Hardware track. Based on time-series data from motion sensors in indoor lighting systems and audio/motion sensors in garages, solving automatic localization of large-scale sensor networks on building floor plans and human/vehicle behavior recognition.

#### Description

In this challenge, we ask you to utilise, apply and visualise the sensor data to understand the use of the building and to improve applying the sensor network optimally in the building in the first place. You can select one or all three of the parts of the challenge to work on.

Where are all the devices?
We typically spend a lot of effort on identifying and positioning a large number of sensors on a floorplan. Can we simplify the process, and use the data from a subset of the sensors to automatically place the rest on a floorplan?

Where is everyone going?
Motion sensors are useful in determining the amount of activity in a space. We also know what kind of space it is, for example, a hallway or a corridor. Can we identify what are the most used pathways in a building, given the hundreds of thousands of motion events the sensors are generating?

Mystery Garage
There are moving vehicles and pedestrians in a garage. We have motion and audio sensors. Can we identify what is happening in the garage? Are there vehicles coming in or going out? Are pedestrians walking towards the elevators, or getting in their cars?

#### Resources

We will provide layouts of the different floorplans containing device locations and time-series of motion and audio events.

Datasets:
BUILDINGS The participants are given datasets from indoor premises. The data will be completely anonymised. The floorplans will contain devices and their locations. The dataset will be a time series of motion events from all the sensors on the floorplan.

GARAGE The participants are given a training dataset from an indoor garage, collected using motion and audio sensors. 

You are encouraged to use other data sources and feel free to use data from/combine your ideas with other Junction challenges if you see a fit.

---

### 10. [2024] KONE — BIM for any building, by anyone.

- **File**: [2024_KONE_BIM_For_Any_Building.md](./2024_KONE_BIM_For_Any_Building.md)
- **Original Track**: `IoT & Hardware` | **Sub-theme**: Smart Buildings, Industrial IoT & Digital Twins
- **Core Theme**: Rapid 3D BIM modeling of existing buildings and elevator electromechanical equipment, IoT remote operations, and digital twins
- **Classification Rationale**: Originally in the IoT & Hardware track. Focused on IoT smart maintenance and rapid 3D digital twin (BIM) construction for building electromechanical hardware such as elevators and escalators, enabling real-time remote visualization of physical building equipment status.

#### Description

Transform sales: Gamify building 3D modeling and exporting with just a few click.

Our industry is moving towards smarter maintenance with IoT and digital twins, allowing remote operations and real-time 3D visualizations of buildings, equipment, and people. But there’s a big challenge: many older buildings don’t have 3D models or BIMs, which limits the ability to improve maintenance and modernization. This gap slows us down and prevents us from making operations as efficient as they could be. Help us create a 3D BIM and digital twin of any building and its equipment to solve a massive industry-wide problem, drive smarter, faster maintenance and modernization, and open the door to fully connected, future-ready operations.

---

### 11. [2025] Harvia — Sauna Intelligence

- **File**: [2025_Harvia_Sauna_Intelligence.md](./2025_Harvia_Sauna_Intelligence.md)
- **Original Track**: `IoT & Hardware` | **Sub-theme**: Smart Buildings, Industrial IoT & Digital Twins
- **Core Theme**: Harvia wireless battery-powered sauna IoT sensors (temperature/humidity/presence detection/BLE beacon) and smart home integration
- **Classification Rationale**: Originally in the IoT & Hardware track. On-site provision of Harvia's newly developed Wi-Fi/cellular wireless battery-powered sauna sensors (including temperature, humidity measurement, human presence detection, and Bluetooth beacons) and Matter/smart home and wearable device integration interfaces.

#### Description

Reimagine the sauna experience using AI tools – show how AI-native coding accelerates your solution.

Harvia is the world leader in sauna and spa solutions, now evolving from a hardware manufacturer into a digital wellness pioneer. With new IoT sauna sensors and APIs, we invite developers to create next-generation sauna and wellbeing applications. At Junction and Harvia, we are especially interested in seeing AI-native and fluent use of AI tools in your solutions – from ideation to prototyping – showing how modern development accelerates better outcomes. Whether your concept makes saunas smarter, more social, or globally accessible, the key is demonstrating true AI-native building.

Your task is to build an innovative solution for Harvia to lift the sauna experience to a new level. Possibly using Harvia’s new sauna sensor platform (Wi-Fi or cellular connected wireless battery-powered sauna sensor including temperature and humidity measurement, presence detection, Bluetooth beacon). The challenge is open-ended: you might create predictive models for smoother use of sauna, personalised wellness recommendations, integrations to other relevant devices (e.g. wearables), social and gamified experiences, or entirely new digital business models. At the same time, it is crucial to demonstrate the use of AI tools fluently and natively in your development process – from coding to testing and iteration. Think globally – the fastest growing market is the United States, where sauna culture is still emerging. We want you to design something that hits the spot with a specific but relevant user group or can potentially scale across cultures, from Finnish homes to luxury spas in Los Angeles.

#### Resources

List of technologies we are bringing:
Sauna sensor devices (demo units installed in Junction venue saunas)
Harvia GraphQL API (pre-release access)
Example datasets of historical sauna sessions
Bluetooth beacon features for presence detection and gamification
On-site technical mentors from Harvia and SÄDE Innovations

#### Prizes

Cash prize pool of €1,500 for Junction winners and an additional €1,500 for the 30-day follow-up race. Harvia sauna sensor devices for winners, plus the opportunity to join a month-long challenge with extended prizes. Top performers may also be recruited directly into Harvia’s new digital team.

---

### 12. [2017] Helvar — Who needs a light switch? - Automate the whole process of controlling light.

- **File**: [2017_Helvar_Who_Needs_A_Light_Switch.md](./2017_Helvar_Who_Needs_A_Light_Switch.md)
- **Original Track**: `AI & Data` | **Sub-theme**: Smart Buildings, Industrial IoT & Digital Twins
- **Core Theme**: Automated lighting hardware control based on passive infrared (PIR), FLIR thermal cameras, light sensors, and Moodmetric emotion rings
- **Classification Rationale**: Although originally in the AI & Data track, a real Smart Room hardware environment was set up on-site, providing passive infrared sensors (PIR), illuminance sensors, FLIR Lepton thermal cameras, Moodmetric electrodermal rings, physical buttons, and professional lighting control APIs, representing a typical multi-sensor fusion and smart hardware control challenge.

#### Description

People are too lazy to control the lights manually! Help us to either automate the whole process or at least by giving the user a really frictionless control. Test your innovativeness by finding new ways to increase people well-being with intelligent algorithms and/or the newest sensors…

#### Prizes

1st price: Hubsan H501S quadcopters (or equivalent) for the winning team. Honorable mention: Amazon Echo Dot devices for selected teams.

---

### 13. [2017] Planmeca Oy — Reshaping the future of dental care. - Dive into the world of technology and use it to revolutionize dental care.

- **File**: [2017_Planmeca_Reshaping_Dental_Care.md](./2017_Planmeca_Reshaping_Dental_Care.md)
- **Original Track**: `Health` | **Sub-theme**: Robotics, Heavy Machinery & Specialized Medical Hardware
- **Core Theme**: Hardware digitization of digital dental treatment units, 3D oral imaging equipment, and intraoral scanners
- **Classification Rationale**: Although originally in the Health track, partner Planmeca brought digital dental treatment units, 3D cone-beam CT imaging equipment, and high-precision intraoral optical scanners to the venue for participants to test, combining medical precision instrument hardware with 3D digital twins.

#### Description

Digital revolution is transforming the entire field of health care and patient care is no longer just taking care of the sick but preventing them from getting sick in the first place. For health care professionals new technology is a way to more efficient, more accurate and more comfortable care. Digital solutions can move the boundaries of health and dental care – the care pathway can start long before the visit to the clinic and go on long after. With advanced 3D imaging technology we can already create a precise digital twin of the patient, which raises a question whether we even need a visit to the dentist any longer?

#### Resources

More details and sample data will be provided on Planmeca’s Junction website soon: www.planmeca.com/junction.

#### Prizes

Prizes to be announced.

---

### 14. [2017] Trimble — Transform the way the world builds! - Create the next big thing in digitalizing the building industry.

- **File**: [2017_Trimble_Transform_The_Way_The_World_Builds.md](./2017_Trimble_Transform_The_Way_The_World_Builds.md)
- **Original Track**: `AI & Data` | **Sub-theme**: RFID, Indoor Positioning & Smart Terminals
- **Core Theme**: 3D measurement sensing of physical building spaces and Microsoft HoloLens mixed reality hardware interaction
- **Classification Rationale**: Although originally in the AI & Data track, it focused on sensor measurement conversion from the physical 3D world to digital models, with Microsoft HoloLens mixed reality headsets and AR/VR hardware provided on-site.

#### Description

We live in a 3D world, and we need to handle lots of 3D data in our business. The challenge is the journey from reality to digital and back to existing world. Have you ever measured your house or organized the furniture virtually using your phone? Now is the chance to put your fire into creating groundbreaking applications using 3D modelling, images, machine learning, sensors, augmented/virtual reality, voice recognition or whatever that makes things magical. Beam me up, Scotty!

#### Resources

https://connect.trimble.com/developer.html

#### Prizes

TBATBA

---

### 15. [2017] TrueFace.ai — Facial Recognition for Everyone - Create an app using one or multiple of TrueFace.ai facial recognition APIs

- **File**: [2017_TrueFace_Facial_Recognition_For_Everyone.md](./2017_TrueFace_Facial_Recognition_For_Everyone.md)
- **Original Track**: `AI & Data` | **Sub-theme**: RFID, Indoor Positioning & Smart Terminals
- **Core Theme**: Facial recognition and anti-spoofing detection system based on Chui smart doorbell and access control terminal hardware
- **Classification Rationale**: Although originally in the AI & Data track, its core hardware carrier and winning prizes were the Chui smart facial recognition doorbell and physical access control hardware (Facial Recognition Security & Access Control Hardware).

#### Description

Facial recognition is taking over. Even Apple is part of it now! From paying with your face, authenticating with your face, detecting emotions, detecting face characteristics, surveillance, automatic check-in and much more, the use cases are endless.

Take part in this and apply your own application of our deep learning powered facial recognition.

#### Resources

API Documentation: https://getchui.github.io/chuiaidocs/#introduction

For any questions join our Slack channel - https://join.slack.com/t/truefaceaicommunity/shared_invite/MjM4MTE3NDgxMTg2LTE1MDQ4NjM0NzEtNzQ4ZTczZTNjNQ

#### Prizes

A Chui device for each member of the winning team. It is a facial recognition security system (can be used as a smart doorbell or access control system) that is managed from the application.A Chui device for each member of the winning team. It is a facial recognition security system (can be used as a smart doorbell or access control system) that is managed from the application.

---

### 16. [2017] Stora Enso's challenge in cooperation with Siili Solutions — Store smarter - Is there intelligent life in your space?

- **File**: [2017_Stora_Enso_Siili_Store_Smarter.md](./2017_Stora_Enso_Siili_Store_Smarter.md)
- **Original Track**: `Sustainability` | **Sub-theme**: Spatial Positioning, RFID & Smart Terminal Hardware (RFID, Indoor Positioning & Smart Terminals)
- **Core Theme**: RFID reader/antenna arrays and CLT/LVL smart timber building components with built-in temperature and humidity sensors
- **Classification Rationale**: Although originally in the Sustainability track, the challenge provides a full set of RFID tags, reader, antenna hardware, and physical storage objects on-site, and involves IoT development combined with Stora Enso's smart timber building components featuring built-in humidity and positioning sensors.

#### Description

Do you have a storage space in your basement or in the attic? Do you remember what is in there? Nowadays we own so many things, and for many of us the experience of trying to organize our private or work stuff is challenging. The problem is that many times we don’t remember what we have, or we don’t know where those things are, or if it is still even usable. 

Sound familiar? Then why not help us come up with a smart storage space!
You can think of solving these problems, either for a
1)    Residential building (private storage space) or
2)    School, hospital, library or other public building (public storage spaces)

What would your smart storage space look like? Would it help reduce waste (like recycling or reuse)? Or keep track of and optimize the value of your items? Help in optimizing general warehouse management?

#### Prizes

The winning team will be awarded with a journey to a European capital, including some Smart City experience and a visit to a Stora Enso manufacturing unit of smart building components. The second team will get to attend a free-of-choice course at Siili Adacemy.The winning team will be awarded with a journey to a European capital, including some Smart City experience and a visit to a Stora Enso manufacturing unit of smart building components. The second team will get to attend a free-of-choice course at Siili Adacemy.

---

### 17. [2018] Outotec — I hear voices in my factory

- **File**: [2018_Outotec_I_Hear_Voices_In_My_Factory.md](./2018_Outotec_I_Hear_Voices_In_My_Factory.md)
- **Original Track**: `Sustainability` | **Sub-theme**: Smart Buildings, Industrial IoT & Digital Twins
- **Core Theme**: Acoustic (Audio) and Motion sensor fault diagnosis and early warning for high-temperature heavy equipment in metallurgical plants
- **Classification Rationale**: Although originally in the Sustainability track, the core is predictive maintenance and fault diagnosis of heavy machinery in metallurgical plants based on physical signals collected by industrial acoustic sensors and motion vibration sensors.

#### Description

There is a factory, far far away from Junction, producing valuable metals to meet our everyday needs. This is a complex process requiring tremendous amounts of energy and blistering temperatures in which things can go wrong with the potential of damage to people and equipment. Based on the provided audio and motion data and failure events, can you diagnose how the factory operates and predict future failures, or prevent them? Can you visualise the data so that it speaks to the operators to help guide them safely? We do not know if there is even any correlation between the data and failures (in theory there should be), so we value a good try and clever new ways for digesting and visualising the data. Make the factory a safer place to work!

---

### 18. [2018] Helvar — The Brain of the Building

- **File**: [2018_Helvar_The_Brain_Of_The_Building.md](./2018_Helvar_The_Brain_Of_The_Building.md)
- **Original Track**: `AI & Data` | **Sub-theme**: Smart Buildings, Industrial IoT & Digital Twins
- **Core Theme**: Building-level intelligent control hub integrating lighting control sensors and ventilation/HVAC hardware
- **Classification Rationale**: Although originally in the AI & Data track, it focuses on hardware data interoperability between lighting control sensor networks and ventilation systems in public buildings, automatic environmental adjustment, and hardware fault anomaly detection.

#### Description

How smart can your building be? How can you control the lighting in a building to boost mood and productivity? Can this brain-driven building  optimise the indoor environment automatically, detect possible defects and abnormalities and compensate for them? How can machine learning and AI be used to do this? What can you tell about building usage and status using the power of data.
Many of the public buildings are equipped with a wide variety of systems controlling the environment of the building such as ventilation, lighting etc. These systems are working individually without exchanging information outside its system but they are collecting data that can be utilized more broadly and can be used as basis for totally new data driven services. Especially the lighting control systems are collecting data of the people’s movement in the building. By applying suitable AI algorithms you can create a totally new BRAIN of the building which combines data from different sources beyond lighting control purposes.

---

### 19. [2018] Alepa — Munchies Robot Hack

- **File**: [2018_Alepa_Munchies_Robot_Hack.md](./2018_Alepa_Munchies_Robot_Hack.md)
- **Original Track**: `Entertainment` | **Sub-theme**: Robotics, Heavy Machinery & Specialized Medical Hardware
- **Core Theme**: Remote control of a physical pick-and-pay candy robot via mobile devices (Pick 'n' Pay Candy Robot)
- **Classification Rationale**: Although originally in the Entertainment track, the core task is to write a mobile control program to directly operate the on-site physical pick-and-pay candy robot hardware (Pick 'n' Pay Candy Robot), which is a typical robotics motion control and human-machine interaction challenge.

#### Description

You just found the best spot on the sofa and you’re in the middle of a video game or just minding your own business, when the desire of sweet and yummy hits you like a hammer. You’re not in the mood to move your ass, though. The question is: how mobile are your munchies?
We’re looking for an entertaining solution in the spirit of street science to solve a tricky problem: how to control a pick’ n’ pay candy robot with a mobile device.

---

### 20. [2018] Fleetboard — Trucks X Code

- **File**: [2018_Fleetboard_Trucks_X_Code.md](./2018_Fleetboard_Trucks_X_Code.md)
- **Original Track**: `Urban & Mobility` | **Sub-theme**: Smart Energy, EV Charging & Mobility Hardware
- **Core Theme**: In-vehicle application development based on Mercedes-Benz heavy truck onboard sensors and live vehicle telemetry data
- **Classification Rationale**: Although originally in the Urban & Mobility track, it provides the Fleetboard commercial vehicle onboard hardware SDK to directly read real-time vehicle bus and sensor telemetry data from heavy trucks.

#### Description

Do you know what almost all roads worldwide have in common? A truck has been there. And now your code can be there too! Now, real-time truck data is readily available for developers to build applications.
It’s just you and our SDK. Will you choose to brave your destiny and go, where no code has gone before? Then create an Android application leveraging the live vehicle data exposed by our SDK for the Mercedes-Benz Truck App Portal and help the logistics industry maximize its efficiency.

---

### 21. [2018] Rightware — Connected Car UX Challenge

- **File**: [2018_Rightware_Connected_Car_UX.md](./2018_Rightware_Connected_Car_UX.md)
- **Original Track**: `Sustainability` | **Sub-theme**: Smart Energy, EV Charging & Mobility Hardware
- **Core Theme**: Smart connected vehicle digital instrument clusters, in-vehicle multi-screen cockpits, and adaptive interaction with interior/exterior environmental perception
- **Classification Rationale**: Although originally in the Sustainability track, it is initiated by Rightware (Kanzi), a leading automotive digital cockpit software company, and focuses on in-vehicle digital instrument hardware display and cockpit HMI design that integrates interior and exterior sensor states.

#### Description

Cars are steadily becoming more connected, and digital displays and user interfaces are beginning to take over from analog ones. The user experience will become more personalized, and outside intelligence will be integrated into the in-car environment. With the right tools, automotive user interfaces will become context-sensitive, adapting to conditions inside or outside the vehicle. These trends introduce exciting new possibilities for the automotive user experience!
Look into the future! What services do you think should be integrated into the connected car of tomorrow? How should these services interact with each other? What should they enable, how should they be implemented, and what should they look like? Show innovation and let your creativity shine!

---

### 22. [2018] Ensto — Adaptive Smart Electric Heating

- **File**: [2018_Ensto_Adaptive_Smart_Electric_Heating.md](./2018_Ensto_Adaptive_Smart_Electric_Heating.md)
- **Original Track**: `Sustainability` | **Sub-theme**: Smart Energy, EV Charging & Mobility Hardware
- **Core Theme**: Adaptive temperature control and energy consumption optimization for programmable smart electric heating hardware devices
- **Classification Rationale**: Although originally in the Sustainability track, it revolves around Ensto smart electric heater hardware and IoT thermostat backend, exploring self-learning building smart heating hardware control.

#### Description

Controllable smart heating can cut down unnecessary energy consumption. Heating management can be utilized through third party data and a backend service data that is open and scalable. It can learn and remember. But most of all, what else could it do?

---

### 23. [2018] ABB — Do Captains Dream of Electric Ships?

- **File**: [2018_ABB_Do_Captains_Dream_Of_Electric_Ships.md](./2018_ABB_Do_Captains_Dream_Of_Electric_Ships.md)
- **Original Track**: `Other` | **Sub-theme**: Robotics, Heavy Machinery & Specialized Medical Hardware
- **Core Theme**: ABB electrified, digitalized, and connected future ships (Electric & Connected Ships) hardware and control system innovation
- **Classification Rationale**: Although originally in the Other track, it is initiated by ABB, an industrial electrical and automation giant, and focuses on electric ship propulsion systems, onboard IoT sensing, and intelligent maritime hardware automation.

#### Description

At ABB we have a vision that ships should be electric, digital and connected. Help us build upon that vision by creating an innovation for the ship of the future.

---

### 24. [2018] Nokia — Living on the Edge

- **File**: [2018_Nokia_Living_On_The_Edge.md](./2018_Nokia_Living_On_The_Edge.md)
- **Original Track**: `Entertainment` | **Sub-theme**: Embedded Systems, Edge Computing & Connectivity
- **Core Theme**: Real-time hardware interaction applications based on Nokia 5G ultra-low latency radio access network and edge computing (MEC)
- **Classification Rationale**: Although originally in the Entertainment track, it focuses on 5G communication infrastructure and validation of ultra-low latency edge hardware capabilities.

#### Description

5G networks will enable high-speed and low-latency mobile connectivity at an unprecedented level. We want you to innovate applications that use 5G to showcase and visualize the difference 5G networks will bring compared to 4G. Zero-ping gaming? Instantaneous downloads? Perfect streaming of 4K videos? Or how about combining them all? Go outside-the-box to summon the future of 5G.

---

### 25. [2018] Movesense By Suunto — Track Anything that Moves

- **File**: [2018_Movesense_By_Suunto_Track_Anything_That_Moves.md](./2018_Movesense_By_Suunto_Track_Anything_That_Moves.md)
- **Original Track**: `Entertainment` | **Sub-theme**: Wearables, Motion & Biometric Sensors
- **Core Theme**: Monitoring of sports equipment, human body, production lines, and bridges based on Movesense inertial measurement unit (IMU) sensors
- **Classification Rationale**: Although categorized in the Entertainment track in 2018, it shares the same origin as the 2017 Suunto challenge, with the core being the use of Movesense programmable motion sensor hardware to track athletes, sports equipment, industrial assembly line equipment, or bridge vibrations.

#### Description

The world is full of things that move: an athlete’s body or sports equipment, a machine on a production line, a bridge under traffic, any of us in our daily life, or anything else that we can imagine. Often it would be highly valuable to know how and when these things move – or don’t move. What is the tracking solution that you think the world clearly needs but is still lacking? Build your demo and win great Suunto watches.

---

### 26. [2018] Vaisala — Actually Useful Weather

- **File**: [2018_Vaisala_Actually_Useful_Weather.md](./2018_Vaisala_Actually_Useful_Weather.md)
- **Original Track**: `Sustainability` | **Sub-theme**: Smart Buildings, Industrial IoT & Digital Twins
- **Core Theme**: Fusion applications of Vaisala high-precision meteorological and environmental measurement instrument data in maritime, agricultural, aviation, and building scenarios
- **Classification Rationale**: Although originally in the Sustainability track, it is initiated by Vaisala, a world-leading manufacturer of meteorological and industrial environmental measurement instruments, and the core is applying high-precision meteorological and environmental sensor data to specific physical operation scenarios.

#### Description

There are a ton of general all-purpose weather apps and services out there – mainly concentrating on forecasts. We want you to show us how weather data can be used and visualized in a meaningful and useful way for some specific real life context. The context could be anything, like sports, different hobbies (e.g. sailing, golf, gardening, mountain biking, storm chasing etc. )  or even businesses (agriculture, construction, freight, aviation etc.)
We are interested in new ways of combining weather and environmental data with modern technologies and also how these can be applied in daily life.

---

### 27. [2018] Vaisala — Hack the Sauna

- **File**: [2018_Vaisala_Hack_The_Sauna.md](./2018_Vaisala_Hack_The_Sauna.md)
- **Original Track**: `Sustainability` | **Sub-theme**: Smart Buildings, Industrial IoT & Digital Twins
- **Core Theme**: Industrial-grade sauna sensing and measurement instruments (replacing traditional mechanical thermometers) and digital experience in extreme high-temperature and high-humidity environments
- **Classification Rationale**: Although originally in the Sustainability track, it focuses on the application and digital transformation of precision temperature and humidity measurement sensor hardware in extreme high-temperature and high-humidity physical environments (sauna rooms).

#### Description

Sauna is a traditional place for bathing and relaxation. It can also be a harsh environment for both people and measurement instruments. The sauna experience has not changed much in centuries: for example, the conditions in sauna are still today measured using mechanical temperature gauges. We feel like it is time to modernise the sauna experience!

---

### 28. [2018] Cisco — Meraki - Capture the Creature

- **File**: [2018_Cisco_Meraki_Capture_The_Creature.md](./2018_Cisco_Meraki_Capture_The_Creature.md)
- **Original Track**: `Entertainment` | **Sub-theme**: Spatial Positioning, RFID & Smart Terminal Hardware (RFID, Indoor Positioning & Smart Terminals)
- **Core Theme**: Indoor spatial awareness based on Cisco Meraki Bluetooth beacons (BLE Beacon) and Wi-Fi wireless positioning hardware
- **Classification Rationale**: Although originally in the Entertainment track, the underlying technology is entirely based on real-time physical location tracking using Cisco Meraki wireless network hardware devices (BLE Beacons and Wi-Fi indoor positioning base stations).

#### Description

Today’s retail companies look for new ways to drive customer loyalty and increase number of visits to their physical stores. In this challenge, you will develop an indoor, location-aware creature hunting game for smartphones, based on the BLE beacon or Wi-Fi location technologies in the Cisco Meraki solution. The aim of the game is to entertain young visitors and get their parents to visit store sections with offers that might interest them.

---

### 29. [2019] Ericsson — Greener City Transport with 5G

- **File**: [2019_Ericsson_Greener_City_Transport_With_5G.md](./2019_Ericsson_Greener_City_Transport_With_5G.md)
- **Original Track**: `Urban & Mobility` | **Sub-theme**: Embedded Systems, Edge Computing & Connectivity
- **Core Theme**: Centralized real-time control of vehicle fleets and coordinated scheduling of multi-source sensors based on 5G low-latency communication networks
- **Classification Rationale**: Although originally in the Urban & Mobility track, it focuses on the application of 5G ultra-low latency wireless communication technology in intelligent fleet control and vehicle-road cooperative hardware scheduling.

#### Description

Current trends show global population is moving to urban areas. With bigger and denser cities, transport of people and goods is getting more complicated. With such volume, if we continue with the same methodologies for city transportation, air pollution and organization will become critical problems.

The introduction of 5G technologies will enable different transportation models by centralizing the transport decision making without suffering much from latency and aggregate information from several sources. You as a team find ways to optimize city wide transportation challenge between different actors.

The goal is to transport as many customers as possible to their destinations. At the end of the hackathon we are going to put all participants on the same simulation and you will compete for the customers. Whoever gets more points wins. We will probably have several rounds.

This challenge is a great place to show your development skills with any modern software technology you prefer!

#### Resources

Ericsson will provide: A server with a simple API where you can control your fleet of cars and see the world status. In addition to this, we will also provide amazing mentors.

---

### 30. [2019] Valmet — Service Workshop of the Future

- **File**: [2019_Valmet_Service_Workshop_Of_The_Future.md](./2019_Valmet_Service_Workshop_Of_The_Future.md)
- **Original Track**: `AI & Data` | **Sub-theme**: Robotics, Heavy Machinery & Specialized Medical Hardware
- **Core Theme**: Micron-level grinding sensor measurement data for giant paper machine rollers, Node-RED hardware simulation, and XR headset interaction
- **Classification Rationale**: Although originally in the AI & Data track, it involves development for micron-level roundness measurement sensor hardware (Sensor ware) for large paper machinery rollers, Node-RED IoT data flows, and VR/MR hardware headsets.

#### Description

We all remember those woodwork classes when we were sweating like never before while smoothening the awesome spoon-to-be with too small piece of sandpaper. Now, imagine a machine that would have 1 000 000 times the surface of a spoon to smoothen at accuracy in micrometers. Doesn’t sound tempting? Paper, board and pulp drying machines need this smoothening grinding service hundreds of hours per year for their rolls. A non-smooth roll will cause losses at speed of 50€ per minute.

This challenge is excellent for hackers interested in recent developments in the fields of sensor ware, visualisation tools and machine learning, not forgetting to mention that these are real and really big machines in question. Your task is to find ways to make grinding these rolls more effective and in a way, more tempting. So, how do you visualise something so minuscule that can’t be seen with bare eyes?

#### Resources

Valmet will provide: Participants are offered a chance to develop on ValmetXR platform. ValmetXR platform provides efficient tools to build customized user-interfaces for documentation and training, by replacing typical manuals with immersive learning environment. ValmetXR incorporates virtual reality, mixed reality and interactive augmented reality experiences via smartphones, tablets and VR/MR headsets in a virtual platform. Platform is based on Unity Engine. All 3D models, 360/2D videos, documents and links can be configured and embedded into the platform. With Node-RED one can wire simulations into ValmetXR.

In addition, Aalto and Valmet provide mentoring for roll grinding, roll behavior and services business. Example datasets demonstrating roll geometry and running paper machines are also provided.

Valmet will provide:
3D Models and XR platform 
Datasets of the paper web from real paper machines
Datasets from paper machine roll roundness measurements

---

### 31. [2019] Helvar & VTT — Making Spaces Brighter with Radar Technology

- **File**: [2019_Helvar_VTT_Making_Spaces_Brighter_With_Radar.md](./2019_Helvar_VTT_Making_Spaces_Brighter_With_Radar.md)
- **Original Track**: `AI & Data` | **Sub-theme**: Millimeter-Wave Radar & High-Speed Machine Vision Sensors
- **Core Theme**: 60 GHz 2D millimeter-wave imaging radar and 24 GHz vital-sign radar sensors + real-time integration with smart luminaire hardware
- **Classification Rationale**: Although originally in the AI & Data track, the venue provides 60 GHz 2D millimeter-wave radar, 24 GHz millimeter-wave radar (capable of non-contact extraction of vital signs such as respiration and heart rate, as well as micro-motion), and physical smart luminaire hardware for teams to integrate and demonstrate in real time.

#### Description

The ability to identify the human presence in a room has been around for a long time and is used to automatically and reliably control lights. But technological evolution demands innovation, and our goal is to create smarter and intelligent indoor spaces. By applying Machine Learning and AI algorithms on the data from Radar sensors, you can develop futuristic applications capable of delivering state-of-the-art lighting. This is the next step in creating truly smart indoor systems.

Imagine the possibilities when the entire building becomes alive and reacts to the behavior of its occupants. By utilizing advanced sensors such as Radars, can we calculate how many people are in the room and identify their location? Is it possible to identify if people are stationary or moving? If yes, what is their direction of movement?

Similarly, can we detect changes in the behavior of a person working at a desk, and deliver personalized lighting to boost their mood and productivity?

Moreover, it is not only limited to human presence. For example, is it possible to locate empty parking spaces in a garage? Can we identify the direction of the moving vehicle? Such insights have a multitude of applications, ranging from people flow in shopping malls, to building utilization measurements and advanced indoor occupancy sensing for lighting control.

#### Resources

Helvar & VTT will provide: Demo Tools, Equipment and Datasets: We will provide a webpage containing luminaires locations on top of the layout of the environment. Participants can then simulate the behavior of the lights by sending commands through an API. Demo luminaires will also be provided, as well as Radar sensors. 

GARAGE: The participants are given a dataset from an indoor garage, collected using an RGB camera and a 60 GHz 2D Radar. The datasets are time-synchronized. People and vehicles are detected from the RGB frames which are represented by bounding boxes, provided in an image coordinate system. Radar data consist of 2D amplitude maps showing the targets in the floor plan coordinate system. 

MEETING ROOM: The participants are given a dataset from a meeting room consisting of 60 GHz 2D radar imaging data and corresponding RGB camera frames. The persons and their skeletons are detected from the RGB frames, and their bounding boxes and joint coordinates are provided in an image coordinate system. Radar data consist of 2D amplitude maps showing the targets in the floor plan coordinate system. The participants are given live access to the Radars for creating online demos. 

WORKPLACE: The participants are provided a dataset of a person that is working with their computer. The dataset includes raw 24 GHz radar data and corresponding RGB camera frames. The vital signs are extracted from the radar data, and person’s joint positions are detected and provided from the RGB frames. Raw radar data consist of amplitude and phase maps that can be used for detecting large and small scale movements. The participants are given live access to the sensors data, which can be used for creating online demos as well.

---

### 32. [2019] SUSE — Open Open City

- **File**: [2019_SUSE_Open_Open_City.md](./2019_SUSE_Open_Open_City.md)
- **Original Track**: `Urban & Mobility` | **Sub-theme**: Embedded Systems, Edge Computing & Connectivity
- **Core Theme**: Edge computing platform based on a Raspberry Pi 3B+/4B+ hardware cluster (uMEC edge nodes) and a dedicated Wi-Fi network
- **Classification Rationale**: Although originally in the Urban & Mobility track, the venue has set up a physical uMEC edge computing cluster composed of Raspberry Pi 3B+ and 4B+ development boards and a dedicated Wi-Fi network, running k3s and ETSI MEC edge hardware interfaces.

#### Description

Cities of the future will improve the quality of life of citizens by integrating technologies and infrastructure via innovative open platforms.

Edge computing plays an increasing role in the telecom industry all over the world. One of the focus areas of edge development is "smart cities". SUSE is participating in the Akraino / uMEC project that aims to define and deliver a compute platform for network edge devices. The challengers are asked to demonstrate use cases and create a prototype of an open data platform which can collect, analyze and share weather, traffic, emergency information with citizens.

Participants of the challenge will get access to a dedicated WiFi network and a k3s cluster that runs on our uMEC nodes (Raspberry Pi 3B+ and 4B+ boards). This base platform will also include a set of MEC APIs that should be used for solving the challenge. The participants will develop applications on top of these APIs and deploy them into our cluster. More demanding applications can be implemented and deployed using SUSE CAP. In the later case we are interested to see smart integrations between powerful cloud native app deployments and our uMEC network.

#### Resources

Suse will provide: We will provide a cluster of edge computing nodes including hardware and software. This cluster will serve as the deployment platform for the containerized applications built by the challenge participants. We will provide open implementation of a subset of certain ETSI MEC APIs. 

More demanding solutions can utilize SUSE CAP which enables easy cloud native application development. These solutions must interact with the devices and APIs on uMEC edge network.

---

### 33. [2022] Oras — The Smartest Water Experience

- **File**: [2022_Oras_The_Smartest_Water_Experience.md](./2022_Oras_The_Smartest_Water_Experience.md)
- **Original Track**: `Sustainability` | **Sub-theme**: Smart Buildings, Industrial IoT & Digital Twins
- **Core Theme**: Oras Hydractiva digital showerhead and touchless Bluetooth smart faucets (SMART Faucets) water sensing and leak localization
- **Classification Rationale**: Although originally in the Sustainability track, the venue showcases Oras digital handheld showerhead and touchless Bluetooth smart faucet hardware, and provides real data from smart water meters/faucet sensors across 20 households in an entire apartment building.

#### Description

All of us use water every day for many purposes. Yet, we might not know where the water is used the most, and more importantly, how it should be used: People should know the amount of water they use in shower or what is a reasonable amount
Building owners could predict the need of hot water and optimize the heating process
In hand washing, a long soaping time (up to 20 sec) is crucial to get all the microbes away
In big buildings it´s important for plumbers to quickly identify the location of the leaking faucet
What data and insights could be visualized and how should it need to be displayed? How can we make every user more conscious about their water usage and encourage them to do better? Information could be transformed into targets or even positive competition via gamification, resulting in doing good for the users and our environment.

#### Resources

During the event, we will provide proprietary water usage data in JSON-format from one building including 20 apartments for the contenders. Our experts are supporting and mentoring throughout the event. Also the latest developments of our product offering such as digital hand shower and touchless Bluetooth faucets are presented at our booth and online at Oras Hydractiva Digital - Save water and energy in the shower and SMART faucets (oras.com)

---

### 34. [2022] CGI & KONE & Meyer Turku — Cruising with Robots

- **File**: [2022_CGI_KONE_Meyer_Turku_Cruising_With_Robots.md](./2022_CGI_KONE_Meyer_Turku_Cruising_With_Robots.md)
- **Original Track**: `Other` | **Sub-theme**: Robotics, Heavy Machinery & Specialized Medical Hardware
- **Core Theme**: Design of autonomous service robots and automated passenger/cargo flow hardware systems on large luxury cruise ships
- **Classification Rationale**: Although originally in the Other track, it is jointly initiated by shipbuilding giant Meyer Turku, elevator and people-flow giant KONE, and CGI, with the core being the design of physical service robots and automated logistics hardware workflows in cruise ship scenarios.

#### Description

People flow is the way how people move in and between place A to place B. Good people flow means people moving smoothly, safely, comfortably, and without waiting. In cruises people flow can be discovered from the passengers’ and crew’s points of view.\
\
Think about the service that is visible and non-visible for cruise passengers. In conclusion, we wish to have a visual presentation (mock-ups, animation etc.) of the service path and people flow. You may use your imagination not only with robots but with automation systems, as well.\
\
We encourage you to be creative with your conclusion. Remember to put effort into the user interface in your solution via mock-ups.

#### Resources

- Useful information about cruises from Meyer (pdf. to download)\
- People flow and robotics expert from KONE\
- Mentoring at Junction Hackathon\

---

### 35. [2022] Nexi — Crack the Payments

- **File**: [2022_Nexi_Crack_The_Payments.md](./2022_Nexi_Crack_The_Payments.md)
- **Original Track**: `Finance` | **Sub-theme**: RFID, Indoor Positioning & Smart Terminals
- **Core Theme**: Low-level communication protocol analysis of financial IC cards based on external NFC reader hardware and mobile NFC modules
- **Classification Rationale**: Although originally in the Finance track, the organizers provide physical NFC reader hardware (NFC Readers) on site, requiring direct reading and parsing of the wireless radio frequency communication messages between chip cards and POS terminal hardware.

#### Description

Behind the scenes, there are different communication protocols, cryptographic standards, financial sector requirements, country regulations, etc. However, the end-user of the payment system sees and holds only the top of the iceberg: The Card.\
Cards operate by striping, tapping, and inserting. Are these methods of payment equally secure? Does it matter which type of card (Maestro, Visa, MasterCard) you use? Dig into the communication between the card and terminal and investigate how secure the payments truly are!\
Build the solution which reads the card data using NFC protocol. Ideally, it should show the parsed content and identify the security level of your card. The solution should be easy to use and explain what was found in detail!

#### Resources

We will bring NFC readers, but you could also use your mobile phones for that.

#### Prizes

The winning team will be awarded 1500€

---

### 36. [2024] Pixieray — Peek Behind the Eyes

- **File**: [2024_Pixieray_Peek_Behind_The_Eyes.md](./2024_Pixieray_Peek_Behind_The_Eyes.md)
- **Original Track**: `Entertainment` | **Sub-theme**: Wearables, Motion & Biometric Sensors
- **Core Theme**: Data analysis of smart glasses hardware integrating 6 infrared eye-tracking sensors per eye, accelerometer, and ambient light/UV sensors
- **Classification Rationale**: Although originally in the Entertainment track, the core data source comes from Pixieray smart glasses hardware (6 infrared sensors per eye for eye tracking, a three-axis accelerometer for head pose tracking, and ambient light and UV sensors).

#### Description

Can you tell if someone is reading, driving, or tired by looking at their eyes? Can your eyes reveal if you're feeling stressed? Can you identify if someone is being dishonest? When we read, drive, or watch a movie, our eyes are active. Pixieray uses premium eyeglasses with invisible technology that can track eye movements, head movements, and lighting conditions.\
\
Your job is to dive head first into the data and find interesting insights on human behavior and how it correlates with eye movement. Analyze the data and find out what eyes can tell you.\
\
We challenge you to use this novel data source to create meaningful, beautiful and impactful ideas that have practical effect on everyday life.

#### Resources

We provide data sourced from spesialized eyewear that tracks eye movement, coupled with video data capturing user behaviour while wearing these glasses. Your task is to analyze, interpret, and draw meaningful insights from this rich dataset. The datasets are provided in JSON format, ensuring easy parsing and integration with most data analysis tools and platforms. - eye movements from 6 IR-sensors on each eye, - accelerometer data, - ambient light and UV levels / To participate in this challenge and get access to the data please visit our booth (NDA must been signed)

#### Prizes

The winning team will receive 500 €, the runner-up will get 300 € and the third place will be rewarded with 100 €. \
\
The prizes are delivered as Amazon gift cards.

---

### 37. [2024] Huawei — Sense the motion

- **File**: [2024_Huawei_Sense_The_Motion.md](./2024_Huawei_Sense_The_Motion.md)
- **Original Track**: `AI & Data` | **Sub-theme**: Wearables, Motion & Biometric Sensors
- **Core Theme**: Real-time motion/emotion sensing algorithms based on STMicroelectronics SensorTile development kits and smartwatches
- **Classification Rationale**: Although originally in the AI & Data track, the organizers provide STMicroelectronics SensorTile embedded sensor development kits (STM Sensor Tile Dev Kits) and smart wearable devices on site, requiring the implementation of motion and emotion perception models that can run in real time on the wearable end.

#### Description

Create innovative and captivating features for mobile and wearable devices that resonate with the youth, encouraging them to reduce sedentary behaviors and embrace more physical active lifestyle. In addition, for people suffering from mental health issues, emotion recognition could help improve self-awareness and mental health professionals could integrate the technology into treatment plans to monitor patient’s emotional response and well-being.

#### Resources

During the event, participating teams will be creating novel sports and health features targeted to wearable or mobile devices. Feature, algorithm, or model can be created using some existing datasets or using real-time sensor data. Sensor data can be obtained from (but not limited to):\
\
- Android sensor framework\
- iOS Core Motion\
- STMicroelectronics sensor tile development kit\
- Free online datasets i.e. from Kaggle\
\
We are going to provide some STM sensor tile development kits to participants for development but otherwise, teams should use their own laptops, mobile phones, or smartwatches.\

#### Prizes

1st place: 8000€ / 2nd place: 5000€ / 3rd place: 3000€

---

### 38. [2025] KONE x Granlund — Modernizing a trillion-euro inventory

- **File**: [2025_KONE_Granlund_Modernizing_Trillion_Euro_Inventory.md](./2025_KONE_Granlund_Modernizing_Trillion_Euro_Inventory.md)
- **Original Track**: `AI & Data` | **Sub-theme**: Smart Buildings, Industrial IoT & Digital Twins
- **Core Theme**: Automated inspection and collection of physical building MEP (mechanical, electrical, plumbing) equipment assets and ultimate digital twin construction
- **Classification Rationale**: Although originally in the AI & Data track, it focuses on automated inventory and digital twinning of nameplates, status, and locations of mechanical, electrical, and plumbing (MEP) hardware equipment in physical buildings.

#### Description

Empower the Built World with AI and Create the Ultimate Digital Twin

Buildings are the world’s largest asset class with a total value of about 350 trillion euros. Despite the great value, the number, condition and location of all the equipment in the buildings are not always known. However, up-to-date equipment information is an important starting point for maintenance services and planning of repairs. Collecting this information is currently laborious and requires an equipment inventory survey, where an expert manually collects device data on site. With this challenge, we are looking for solutions that can automate equipment inventory surveys. Can you develop a solution for gathering data from mechanical, electrical and plumbing equipment in buildings that is user-friendly for non-experts and doesn’t rely on specialized hardware?

---

### 39. [2025] Denso — ChargeID: Trusted EV Services

- **File**: [2025_Denso_ChargeID_Trusted_EV_Services.md](./2025_Denso_ChargeID_Trusted_EV_Services.md)
- **Original Track**: `Urban & Mobility` | **Sub-theme**: Smart Energy, EV Charging & Mobility Hardware
- **Core Theme**: Secure interconnection of automotive tier-one supplier DENSO vehicle-side hardware, smart charging piles, and decentralized identity (DID)
- **Classification Rationale**: Although originally in the Urban & Mobility track, it is initiated by DENSO, a global top-tier automotive components hardware giant, and revolves around smart connected vehicle hardware, charging pile terminals, and trusted vehicle-pile communication.

#### Description

Reimagine semi-public EV charging with AI and decentralized identity, where drivers, vehicles, and charge points interact seamlessly with businesses.

EV charging in workplaces, fleets, and semi-public facilities is growing fast, yet most infrastructure is still “dumb.” Businesses can’t easily create differentiated services, while drivers expect transparency and control. With AI and decentralized identity across drivers, vehicles, and charge points, charging journey & experience can evolve into secure, personalized, and productive services that benefit everyone from drivers to charger point operators to business who own vehicles and chargers. 

Today, companies such as fleet operators, employers, or retail chains have limited ways to innovate around charging, since infrastructure is basic and data flows are restricted and controlled by individual parties. Drivers, vehicles, and charge points all need trusted ways to authenticate, share, and interact with services without relying on central intermediaries. How can AI and decentralized identity enable businesses to deliver services like demand forecasting, cost optimization, or personalized charging experiences, while keeping ownership close to the user and the assets involved?

#### Resources

Mentors from DID project R&D and innovation team.

During the event, participants will develop innovative semi-public B2B2C EV charging solutions that combine AI and decentralized identity. The challenge centers around the Denso DID Agent, a leading identity-as-a-service platform enabling secure and privacy-preserving connectivity for vehicles and related assets. This technology allows trusted, anonymous interactions between drivers, vehicles, and charge points within Mobility-as-a-Service (MaaS) scenarios.

Participants will have access to the Denso DID Agent, its API documentation, and sample datasets representing vehicles and charging stations. These resources provide a foundation for exploring authentication, data exchange, and service creation using decentralized identity principles.

Expert mentors from our product development and R&D teams, actively involved in DID initiatives across the automotive sector, will support teams throughout the event.

#### Prizes

We will reward the top three teams with a total of €1000 in cash prizes, recognizing the most creative and impactful solutions. In addition to the prize, winners will gain visibility among industry experts and receive mentoring opportunities with our product and R&D teams working on decentralized identity in mobility services.

---

### 40. [2025] Sensofusion — Lights, Camera, Reaction!

- **File**: [2025_Sensofusion_Lights_Camera_Reaction.md](./2025_Sensofusion_Lights_Camera_Reaction.md)
- **Original Track**: `AI & Data` | **Sub-theme**: Millimeter-Wave Radar & High-Speed Machine Vision Sensors
- **Core Theme**: Microsecond-level neuromorphic event camera high-speed physical motion detection and drone tracking
- **Classification Rationale**: Although originally in the AI & Data track, counter-drone hardware manufacturer Sensofusion deploys multiple professional-grade event cameras (Event Cameras, microsecond-level pixel light intensity change sensors) with different lenses on site to measure high-speed rotating fan blades and track drones; each member of the winning team is awarded a DJI Mini 3 drone hardware.

#### Description

Operate in a timescale where ordinary vision fails - machine vision on microsecond timescales.

There's a camera type you might have never heard about – an Event Camera. They use an imaging sensor that detects changes in light intensity at the pixel level, producing a stream of asynchronous events rather than full frames. Their key advantages include very high dynamic range, low latency (microseconds), minimal motion blur, and high temporal resolution. Can you figure out how to use such a camera to detect objects that move extremely fast? Prove it.

You’ll get hands-on access to professional event cameras equipped with various lenses - all available on-site at Junction.
Your mission: build real-time AI or ML models that can detect and interpret motion from these microsecond-level vision streams.
Start simple: can you count how many times per second a fan spins? Then push further - track drones, estimate speed, predict motion, whatever you can imagine. 
Push these sensors beyond their limits — and remember, their limits are very high.

#### Resources

Access to several professional event cameras installed on-site at Junction. 
APIs and documentation for data access and integration.

Mentors from Sensofusion R&D team with deep expertise in vision technology and AI.

Example scripts and data samples to help teams get started.

#### Prizes

Winning team, as chosen by the Sensofusion mentors, will be rewarded with DJI Mini 3 drones. Every member of the winning team will get a drone.

---

### 41. [2025] Sensofusion — Radio City

- **File**: [2025_Sensofusion_Radio_City.md](./2025_Sensofusion_Radio_City.md)
- **Original Track**: `Entertainment` | **Sub-theme**: Millimeter-Wave Radar & High-Speed Machine Vision Sensors
- **Core Theme**: Physical propagation and multipath reflection simulation of radio waves from mobile radios, vehicles, and drones in 3D urban environments
- **Classification Rationale**: Although originally in the Entertainment track, it is initiated by counter-drone RF detection hardware manufacturer Sensofusion, focusing on physical modeling of propagation loss, reflection, and occlusion of radio waves among real physical urban buildings.

#### Description

Radio waves: They surround us and penetrate us; they bind the galaxy together. Show them to us.

Radio quietly powers much of what we do every day. This challenge offers an approachable way to grasp the basics. Take a 3D city model and make the invisible radio world visible. Show when and where radio transmitters can be heard — and when they fade away.

Using the provided 3D model of Hong Kong, demonstrate how radio waves travel. Place imaginary moving radio sources on the map: for example, people walking on the streets with mobile phones, cars driving on the streets or drones flying in the air – or come up with other sources. Then visualize how the radio transmission sent from these sources travel. You'll demonstrate how radio waves bounce from walls and how geographic obstacles will block radio. We’ll be looking for a physics-based simulation with creative visuals. You need a grasp of how radio behaves. Ideally, your visualization helps others learn too. Feel free to add interactivity and bring in other data, if they add to the story. There are several different ways to visualize radio waves. There is no single correct solution for this challenge; there are multiple creative ways of showing your results.

#### Resources

City 3D Model: Hong Kong (tall buildings, interesting geography)
Unit: meters
Licenses:
JAXA https://earth.jaxa.jp/en/data/policy/
OpenStreetMap contributors https://www.openstreetmap.org/copyright

Extra details:
A python3 function to map a GPS coordinate to the model space:

def lat_lon_to_model_space(lat_lon):
    import math
    hong_kong_center_lat_lon = (22.268385798683745, 114.2578125)
    EARTH_RADIUS_METERS = 6371000
    delta_lat_deg = float(lat_lon[0]) - float(hong_kong_center_lat_lon[0])
    delta_lon_deg = float(lat_lon[1]) - float(hong_kong_center_lat_lon[1])

    meters_north = math.radians(delta_lat_deg) * EARTH_RADIUS_METERS

    cos_latitude = math.cos(math.radians(hong_kong_center_lat_lon[0]))
    radius_at_latitude = EARTH_RADIUS_METERS * cos_latitude
    meters_east = math.radians(delta_lon_deg) * radius_at_latitude

    # Flip signs to match your coordinate system
    return [meters_north, -meters_east]

Area bounds WGS84: {'north_lat': 22.59372606392931, 'south_lat': 21.943045533438177, 'west_lon': 113.90625, 'east_lon': 114.609375}

#### Prizes

The winning team, as chosen by the Sensofusion mentors, will be rewarded with DJI Mini 3 drones. Every member of the winning team will get a drone.

---

### 42. [2025] Valmet x HSY — Intelligent Flow Optimization

- **File**: [2025_Valmet_HSY_Intelligent_Flow_Optimization.md](./2025_Valmet_HSY_Intelligent_Flow_Optimization.md)
- **Original Track**: `Sustainability` | **Sub-theme**: Robotics, Heavy Machinery & Specialized Medical Hardware
- **Core Theme**: Autonomous collaborative control of urban sewage pump station hardware clusters based on industrial automation protocol OPC UA and digital twins
- **Classification Rationale**: Although originally in the Sustainability track, it requires direct interaction with the sewage pump station control system and digital twin simulation environment through the industrial automation standard hardware communication protocol OPC UA, to achieve real-time safe control of physical pump clusters.

#### Description

Build a multi-agent AI that autonomously minimizes wastewater pumping energy—one of the most critical processes in modern infrastructure—by forecasting inflow, power prices, and flow dynamics in real time.

Every city relies on invisible systems that keep life running—and wastewater management is one of the most critical. Pumps operate nonstop, consuming massive amounts of energy while facing the chaos of inflow, storms, and fluctuating electricity prices. What if these networks could think for themselves? With multi-agent AI, Valmet and HSY invite you to transform static infrastructure into a living system that predicts, adapts, and optimizes wastewater flow in real time.

Wastewater networks operate 24/7 and cannot stop — yet they hide untapped potential for intelligent optimization. Each pumping station must balance constant flow, limited storage, and fluctuating electricity prices while staying resilient to stormwater surges. Traditional automation follows fixed rules and ignores real-time changes and forecasts. Your task is to build a multi-agent AI system where autonomous agents plan pumping according to daily energy prices, coordinate flow between stations, and find the most energy-efficient pumping strategy without violating safety or process constraints. The goal: make one of society’s most critical infrastructure systems self-optimizing.

#### Resources

Participants will have access to HSY’s historical wastewater and inflow datasets—real operational data spanning years of environmental variation. System communication and control will be implemented through the OPC UA protocol, the industrial standard for secure, real-time data exchange. Mentors from Valmet, HSY, and Aalto University will provide hands-on guidance in areas such as process automation, multi-agent architectures, and in future solutions can be tested with digital twin simulation. Teams are free to use any AI framework of their choice—from reinforcement learning environments to optimization libraries or custom-built agent systems.

#### Prizes

1# 2000€, 2# 1500€, 3# 500€

---

### 43. [2025] Snap Inc. — Your Real-World AI Companion

- **File**: [2025_Snap_Your_Real_World_AI_Companion.md](./2025_Snap_Your_Real_World_AI_Companion.md)
- **Original Track**: `AI & Data` | **Sub-theme**: Wearables, Motion & Biometric Sensors
- **Core Theme**: Spatial perception and all-day personal AI companion based on fifth-generation Snap Spectacles AR smart glasses hardware
- **Classification Rationale**: Although originally in the AI & Data track, each participating team is issued a pair of fifth-generation Snap Spectacles AR glasses hardware on site (each member of the winning team wins a pair of Spectacles), requiring the use of the glasses' cameras and spatial sensors to develop real-time AR/AI applications.

#### Description

Design an AIxAR experience for Spectacles that transforms AR glasses into an intelligent companion aware of your world, context, and needs.

AR glasses like Spectacles represent the next frontier of personal technology. They see what you see, hear what you hear, and understand the world around you—unlocking new ways for humans and AI to work together in real-time. At Europe’s largest AI hackathon, we invite you to design and build a Spectacles Lens that delivers an AI-first experience, transforming Spectacles into an intelligent companion for a specific, real-world scenario. Move beyond simple commands and create an assistant that is deeply integrated with the user's environment and intentions. Exceptional projects will move beyond simply responding to direct user questions. We challenge you to build an AI that anticipates user needs, provides spatial support, and helps users stay more engaged and present in their environment.

Build a Lens for Spectacles that demonstrates a compelling, AI-first experience. Your project should showcase how a real-world AI companion can provide genuine value and enhance a user's life. Our encouragement is for you to think about the moments in your daily life where glasses that can see and AI that can understand your patterns, routines, and interactions could simplify things.

#### Resources

Members of Snap’s Engineering team, with expertise in Spectacles developer experience and design.

Participants will build using Snap’s Lens Studio tool and 5th generation Spectacles. Lens Studio is free and available online to download, offering a full suite of features for creating immersive, real-time AR experiences powered by computer vision, scene understanding, and ML integration. Throughout the hackathon, Snap mentors will provide hands-on guidance on Lens Studio workflows and best practices for designing intuitive, human-centered AR experiences.We’ll provide documentation, sample projects, and live mentorship support to help you bring your AI companion to life.

List of technologies that we are bringing:
- Spectacles (1 pair per team)

We’ll be bringing mentors from our Snap Lab team with engineering and design backgrounds who work directly with the development of Spectacles.

#### Prizes

The Prizes:
🥇 1st Place: Each team member wins a pair of Spectacles
🥈 2nd Place: Each team member wins a Soundview Speaker
🥉 3rd Place: Each team member wins an Elexa Power Bank

---
