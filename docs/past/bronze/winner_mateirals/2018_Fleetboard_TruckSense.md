# TruckSense — Fleetboard (Daimler / Mercedes-Benz) Challenge Winner (Junction 2018)

- **Event / Year**: Junction 2018 (Aalto University / Espoo, November 23–25, 2018)
- **Track & Challenge**: **Mobility** Track — *"Trucks X Code"* (**Fleetboard**, Daimler / Mercedes-Benz Trucks)
- **Silver Challenge Spec**: [2018_Fleetboard_Trucks_X_Code.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Fleetboard_Trucks_X_Code.md)
- **Verification Tier**: **L2 Verified** (Official **Universidad Politécnica de Cartagena (UPCT)** press release + **La Verdad** Spanish regional newspaper report)
- **Award(s)**: **1st Place / Challenge Winner** — Fleetboard *"Trucks X Code"* Mobility Challenge (prize: **3-day all-expenses-paid trip & technical innovation workshop in Stuttgart**, Germany, at Daimler/Mercedes-Benz HQ collaborating with Mercedes truck on-board computer engineers)
- **Team & Members**: **TruckSense**
  - **Pablo Moyano** (Telematics Engineering student, UPCT; Free Open Source Club / FOSC; 3x hackathon award winner)
  - **Enrique Fernández** (Telematics Engineering student, UPCT; Free Open Source Club / FOSC)
  - **+ 2 software developers working at Vueling** *(full names not stated in the UPCT / La Verdad articles)*
- **Primary URLs**:
  - Official UPCT Press Release (Nov 30, 2018): https://www.upct.es/noticias/2018-11-30-premiados-dos-alumnos-de-la-upct-por-resolver-un-reto-tecnologico-para-monitorizar-los-camiones-mercedes
  - La Verdad Article (Dec 2, 2018): https://www.laverdad.es/murcia/cartagena/estudiantes-upct-resuelven-20181202005210-ntvo.html

---

## Problem & Solution Summary

Heavy commercial truck fleets generate rich real-time vehicle bus and operational telemetry through Mercedes-Benz on-board truck computers, but drivers and fleet operators need predictive foresight rather than post-hoc fault logs.

**TruckSense** built a real-time vehicle-to-cloud predictive telemetry application targeted directly at **Mercedes-Benz truck on-board computing environments (Fleetboard)**:
1. Captures live truck operational data streams from the on-board truck interface/SDK.
2. Streams vehicle telemetry to a cloud backend applying **machine learning** models to forecast upcoming vehicle metrics/states.
3. Visualizes real-time telemetry alongside predicted future truck conditions in an intuitive graphical web dashboard for drivers and fleet dispatchers.

---

## Observed Hardware / Edge / ML Stack

| Layer | Observed Component / Technology | Details from UPCT & La Verdad Sources |
|---|---|---|
| **Target Vehicle Platform** | **Mercedes-Benz Truck On-Board Computer / Fleetboard SDK** | Challenge required building applications deployable on Mercedes-Benz commercial truck on-board computers |
| **Telemetry & Predictive Backend** | Streaming ingestion server + **Machine Learning** forecasting | Predicts future truck operating metrics from live vehicle telemetry |
| **Visualization** | Real-time graphical web application | Live fleet/vehicle health and predictive trend interface |

---

## Key Engineering Decisions

1. **Closing the Loop From On-Board Capture to Forecast**: Rather than building a static dashboard showing current CAN/SDK snapshots, *TruckSense* added an ML forecasting step so fleet operators see predicted future values alongside live truck telemetry.
2. **Real-Time Browser Delivery**: Delivering the visual layer as a responsive graphical web app made the solution deployable both inside cabin displays and at fleet management desks during the Stuttgart workshop follow-up.

---

## Metrics & Event Context

- **Event Scale Noted**: Pre-selected from roughly 10,000 applicants (~1,000+ competitors accepted across Junction 2018) with ~40 hours of core hackathon implementation time.
- **Public Code Gap**: No public GitHub repository URL or quantitative ML error metric (e.g., RMSE/MAE) was published in the UPCT or La Verdad articles.

---

## Transferable Lessons for Automotive & Fleet-Telematics Teams

1. **Shift Telematics from "What Happened" to "What Happens Next"**: Adding even lightweight forward time-series prediction on top of live vehicle bus/SDK streams differentiates an industrial winner from generic monitoring UIs.
2. **Leverage Open-Source Hardware/Telematics Communities**: UPCT highlighted that experience from its student **Free Open Source Club (FOSC)** directly prepared both students for rapid 40-hour on-board SDK integration.

---

## Sources & Raw Excerpts

- **L2 Official University Release — UPCT (Nov 30, 2018)**: https://www.upct.es/noticias/2018-11-30-premiados-dos-alumnos-de-la-upct-por-resolver-un-reto-tecnologico-para-monitorizar-los-camiones-mercedes
  > *"El equipo formado por estudiantes de la Politécnica desarrolló el proyecto ‘TruckSense’, una aplicación que capta la información en tiempo real del camión y que a su vez la manda a un servidor para poder aplicar técnicas de aprendizaje máquina para predecir datos futuros y transmitir y mostrar toda esta información en forma gráfica en tiempo real a través de una aplicación web."*
- **L2 Regional Press — La Verdad (Dec 2, 2018)**: https://www.laverdad.es/murcia/cartagena/estudiantes-upct-resuelven-20181202005210-ntvo.html
