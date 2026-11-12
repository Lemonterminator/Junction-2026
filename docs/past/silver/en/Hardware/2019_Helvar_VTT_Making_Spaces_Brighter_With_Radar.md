# [2019] Helvar & VTT — Making Spaces Brighter with Radar Technology

## Metadata

- **Year**: 2019
- **Challenge Partner**: Helvar & VTT
- **Original Historical Track**: AI & Data
- **2026 Target Track**: Hardware Track (by Arduino)
- **Sub-theme**: Millimeter-Wave Radar & High-Speed Machine Vision Sensors
- **Core Theme**: 60 GHz 2D millimeter-wave imaging radar and 24 GHz vital-sign radar sensors + real-time integration with smart luminaire hardware
- **Classification Rationale**: Although originally in the AI & Data track, the venue provides 60 GHz 2D millimeter-wave radar, 24 GHz millimeter-wave radar (capable of non-contact extraction of vital signs such as respiration and heart rate, as well as micro-motion), and physical smart luminaire hardware for teams to integrate and demonstrate in real time.

---

## Full Original Challenge Name

Making Spaces Brighter with Radar Technology

## Challenge Description

The ability to identify the human presence in a room has been around for a long time and is used to automatically and reliably control lights. But technological evolution demands innovation, and our goal is to create smarter and intelligent indoor spaces. By applying Machine Learning and AI algorithms on the data from Radar sensors, you can develop futuristic applications capable of delivering state-of-the-art lighting. This is the next step in creating truly smart indoor systems.

Imagine the possibilities when the entire building becomes alive and reacts to the behavior of its occupants. By utilizing advanced sensors such as Radars, can we calculate how many people are in the room and identify their location? Is it possible to identify if people are stationary or moving? If yes, what is their direction of movement?

Similarly, can we detect changes in the behavior of a person working at a desk, and deliver personalized lighting to boost their mood and productivity?

Moreover, it is not only limited to human presence. For example, is it possible to locate empty parking spaces in a garage? Can we identify the direction of the moving vehicle? Such insights have a multitude of applications, ranging from people flow in shopping malls, to building utilization measurements and advanced indoor occupancy sensing for lighting control.

## Resources

Helvar & VTT will provide: Demo Tools, Equipment and Datasets: We will provide a webpage containing luminaires locations on top of the layout of the environment. Participants can then simulate the behavior of the lights by sending commands through an API. Demo luminaires will also be provided, as well as Radar sensors. 

GARAGE: The participants are given a dataset from an indoor garage, collected using an RGB camera and a 60 GHz 2D Radar. The datasets are time-synchronized. People and vehicles are detected from the RGB frames which are represented by bounding boxes, provided in an image coordinate system. Radar data consist of 2D amplitude maps showing the targets in the floor plan coordinate system. 

MEETING ROOM: The participants are given a dataset from a meeting room consisting of 60 GHz 2D radar imaging data and corresponding RGB camera frames. The persons and their skeletons are detected from the RGB frames, and their bounding boxes and joint coordinates are provided in an image coordinate system. Radar data consist of 2D amplitude maps showing the targets in the floor plan coordinate system. The participants are given live access to the Radars for creating online demos. 

WORKPLACE: The participants are provided a dataset of a person that is working with their computer. The dataset includes raw 24 GHz radar data and corresponding RGB camera frames. The vital signs are extracted from the radar data, and person’s joint positions are detected and provided from the RGB frames. Raw radar data consist of amplitude and phase maps that can be used for detecting large and small scale movements. The participants are given live access to the sensors data, which can be used for creating online demos as well.
