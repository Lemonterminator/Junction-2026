# [2025] Sensofusion — Lights, Camera, Reaction!

## Metadata

- **Year**: 2025
- **Challenge Partner**: Sensofusion
- **Original Historical Track**: AI & Data
- **2026 Target Track**: Hardware Track (by Arduino)
- **Sub-theme**: Millimeter-Wave Radar & High-Speed Machine Vision Sensors
- **Core Theme**: Microsecond-level neuromorphic event camera high-speed physical motion detection and drone tracking
- **Classification Rationale**: Although originally in the AI & Data track, counter-drone hardware manufacturer Sensofusion deploys multiple professional-grade event cameras (Event Cameras, microsecond-level pixel light intensity change sensors) with different lenses on site to measure high-speed rotating fan blades and track drones; each member of the winning team is awarded a DJI Mini 3 drone hardware.

---

## Full Original Challenge Name

Lights, Camera, Reaction!

## Challenge Description

Operate in a timescale where ordinary vision fails - machine vision on microsecond timescales.

There's a camera type you might have never heard about – an Event Camera. They use an imaging sensor that detects changes in light intensity at the pixel level, producing a stream of asynchronous events rather than full frames. Their key advantages include very high dynamic range, low latency (microseconds), minimal motion blur, and high temporal resolution. Can you figure out how to use such a camera to detect objects that move extremely fast? Prove it.

You’ll get hands-on access to professional event cameras equipped with various lenses - all available on-site at Junction.
Your mission: build real-time AI or ML models that can detect and interpret motion from these microsecond-level vision streams.
Start simple: can you count how many times per second a fan spins? Then push further - track drones, estimate speed, predict motion, whatever you can imagine. 
Push these sensors beyond their limits — and remember, their limits are very high.

## Challenge Insights

We’re looking for real-time detection of objects seen by the event cameras. You will get a data feed from the cameras with an API reference. You're free to implement your handling of the data as well as the visualization of your work with any tools you wish.

## Judging Criteria

The most accurate, creative, technically impressive, and real-time capable use of the event camera wins.
Go wild, push the limits of machine vision, and surprise us with what you can make microseconds reveal.

## Prizes

Winning team, as chosen by the Sensofusion mentors, will be rewarded with DJI Mini 3 drones. Every member of the winning team will get a drone.

## Resources

Access to several professional event cameras installed on-site at Junction. 
APIs and documentation for data access and integration.

Mentors from Sensofusion R&D team with deep expertise in vision technology and AI.

Example scripts and data samples to help teams get started.

## About the Partner

The mission for Sensofusion is to secure personnel and infrastructure against drones with our Airfence product. Our systems are ready, tested and shipping. Sensofusion has governmental customers in Europe, North America, Middle East and Asia.

---

## Winning Solutions & Verified Historical Cases

- **Track Winner 🥇**: **Academic Menaces** `[L1]` — Engineered a native asynchronous event-camera machine vision pipeline (`< 1 ms` latency, `> 98%` blade RPM accuracy up to 6,000+ RPM, `120 dB+` dynamic range) using C++17, OpenEB, time-surface feature extraction, and frequency-domain optical tachometry instead of downsampling event streams to 30 fps frames.
- **Bronze & Gold Reference**: [`2025_Sensofusion_AcademicMenaces.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2025_Sensofusion_AcademicMenaces.md) | [Gold Hardware Track (`hardware.md`)](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/gold/en/hardware.md)
