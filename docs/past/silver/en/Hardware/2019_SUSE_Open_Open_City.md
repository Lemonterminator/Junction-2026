# [2019] SUSE — Open Open City

## Metadata

- **Year**: 2019
- **Challenge Partner**: SUSE
- **Original Historical Track**: Urban & Mobility
- **2026 Target Track**: Hardware Track (by Arduino)
- **Sub-theme**: Embedded Systems, Edge Computing & Connectivity
- **Core Theme**: Edge computing platform based on a Raspberry Pi 3B+/4B+ hardware cluster (uMEC edge nodes) and a dedicated Wi-Fi network
- **Classification Rationale**: Although originally in the Urban & Mobility track, the venue has set up a physical uMEC edge computing cluster composed of Raspberry Pi 3B+ and 4B+ development boards and a dedicated Wi-Fi network, running k3s and ETSI MEC edge hardware interfaces.

---

## Full Original Challenge Name

Open Open City

## Challenge Description

Cities of the future will improve the quality of life of citizens by integrating technologies and infrastructure via innovative open platforms.

Edge computing plays an increasing role in the telecom industry all over the world. One of the focus areas of edge development is "smart cities". SUSE is participating in the Akraino / uMEC project that aims to define and deliver a compute platform for network edge devices. The challengers are asked to demonstrate use cases and create a prototype of an open data platform which can collect, analyze and share weather, traffic, emergency information with citizens.

Participants of the challenge will get access to a dedicated WiFi network and a k3s cluster that runs on our uMEC nodes (Raspberry Pi 3B+ and 4B+ boards). This base platform will also include a set of MEC APIs that should be used for solving the challenge. The participants will develop applications on top of these APIs and deploy them into our cluster. More demanding applications can be implemented and deployed using SUSE CAP. In the later case we are interested to see smart integrations between powerful cloud native app deployments and our uMEC network.

## Resources

Suse will provide: We will provide a cluster of edge computing nodes including hardware and software. This cluster will serve as the deployment platform for the containerized applications built by the challenge participants. We will provide open implementation of a subset of certain ETSI MEC APIs. 

More demanding solutions can utilize SUSE CAP which enables easy cloud native application development. These solutions must interact with the devices and APIs on uMEC edge network.

---

## Winning Solutions & Verified Historical Cases

- **1st Place (Winner)**: **Flowify** `[L1]` *(team roster and source repo not publicly archived)*
- **1st Runner-up (2nd Place)**: **suseXcity** `[L1]`
- **2nd Runner-up (3rd Place)**: **Ravenholm** `[L1]`
- **On-Site Edge Hardware Testbed Architecture (`[L2]` LF Edge / Akraino MicroMEC)**: SUSE, Nokia, and Arm deployed physical tabletop clusters of **Raspberry Pi 3B+ / 4B (`<= 4 GB RAM`)** running lightweight **k3s**, **OpenFaaS Cloud**, and an **ETSI MEC API** subset over dedicated local Wi-Fi.
- **Hardware & Engineering Takeaways**: Multi-team stateful containers on Pi SD cards exposed severe I/O bottlenecks and corruption risks during Junction 2019—directly driving LF Edge Akraino R3 to migrate to **PXE network boot + shared iSCSI storage**; multi-arch `arm64`/`armhf` builds must also be prepared before arriving at an Arm edge table.
- **Bronze Case Study**: [`2019_SUSE_OpenOpenCity_Flowify.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2019_SUSE_OpenOpenCity_Flowify.md)
- **Primary Sources**: [Junction 2019 Winners (Medium)](https://medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f) | [LF Edge Akraino MicroMEC Blog](https://www.lfedge.org/2020/08/13/micromec-now-available-with-the-akraino-r3-release/)
