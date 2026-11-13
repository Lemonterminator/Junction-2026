# 2017–2018 Hardware & IoT Verification Gap Report (Alepa, Nokia, ABB, Trimble, Qt, Rightware, Cisco Meraki, TrueFace, Ensto Heating, Espoo)

- **Scope**: Exhaustive audit of Junction 2017 and Junction 2018 Silver Hardware challenge files where **no complete verified 1st-place public winner roster** was confirmed across Devpost, GitHub, Medium, corporate partner blogs, municipal portals, or university press releases — plus verified partial findings discovered along the way.
- **Verification Tier**: **Verified Negative Public Record / Partial Partner Evidence**

---

## Why 2017–2018 Sub-Challenge Coverage Has Structural Archive Gaps

1. **Judging Platform Migration (`2018`)**: Unlike 2017 (which used `junction-2017.devpost.com` alongside corporate blogs), Junction 2018 migrated project submissions to an internal custom submission platform (`http://project-plat.herokuapp.com/dashboard` — observed verbatim in `teamglados/oneiro/HELP.md`) and archived sub-track pages under `2018.hackjunction.com`. Both portals were later decommissioned, leaving only projects mirrored to personal GitHub repos, Devpost mirrors, university newsrooms, municipal procurement records, or partner blogs.
2. **Scraping & Indexation Limits**: Direct HTTP access to `devpost.com` project pages returns `HTTP 403`, and Junction Medium winner posts (e.g., `medium.com/hack-junction/...`) also return `HTTP 403` to automated `urllib` clients; therefore Devpost/Medium items were checked via search indexing and archived secondary sources, with every unconfirmed gap stated transparently below.

---

## Track-by-Track Findings & Confirmed Gaps (2018)

### 1. Alepa — *"Munchies Robot Hack"* (2018)
- **Silver Spec**: [2018_Alepa_Munchies_Robot_Hack.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Alepa_Munchies_Robot_Hack.md)
- **Status**: **No verified public winner record found** after searching Devpost, Medium, GitHub, and Finnish press (`SOK` / `Alepa` / `Starship`).
- **False-Positive Disambiguation**: GitHub repo `kvld/junction2018` turned up under Finnish grocery/retail Junction 2018 keyword searches, but inspection confirmed it is an **iOS K-Group personalized diet plan app** (`K Group Challenge.xcodeproj`), unrelated to Alepa's delivery-robot challenge.

### 2. Nokia — *"Living on the Edge"* (2018)
- **Silver Spec**: [2018_Nokia_Living_On_The_Edge.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Nokia_Living_On_The_Edge.md)
- **Status**: **1st-place winner not publicly identified; L2 2nd-Place Nokia/Intel Cross-Challenge Co-Winner Verified**:
  - Official **Universidad de Málaga (UMA)** press news (Nov 29, 2018, https://www.uma.es/sala-de-prensa/noticias/tres-estudiantes-de-la-uma-se-alzan-con-los-tres-primeros-premios-de-junction-2018/) confirms **José Manuel García** (Industrial Organization Engineering) won **2nd Prize** recognized by **Nokia** in a joint **Nokia & Intel IoT Bluetooth Mesh ("Bluetooth Mesh 5G") challenge**, where electric vehicles connect via Bluetooth to build a spatial map and autonomously organize multi-point charging schedules based on price and user constraints.
  - No public winner record found specifically citing Nokia's *"Living on the Edge"* challenge title.

### 3. ABB — *"Do Captains Dream of Electric Ships?"* (2018)
- **Silver Spec**: [2018_ABB_Do_Captains_Dream_Of_Electric_Ships.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_ABB_Do_Captains_Dream_Of_Electric_Ships.md)
- **Status**: **No verified public winner record found** after searching Devpost, GitHub, Medium, and ABB Marine blogs (confirmed ABB's presence at Junction 2018 via `uma.es` sponsor list).

### 4. Rightware — *"Connected Car UX Challenge"* (2018)
- **Silver Spec**: [2018_Rightware_Connected_Car_UX.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Rightware_Connected_Car_UX.md)
- **Status**: **No verified public winner record found** across Devpost, GitHub (`Kanzi` + `Junction 2018`), Medium, or Rightware press releases.

### 5. Cisco — *"Meraki - Capture the Creature"* (2018)
- **Silver Spec**: [2018_Cisco_Meraki_Capture_The_Creature.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Cisco_Meraki_Capture_The_Creature.md)
- **Status**: **No verified public winner record found** after searching Devpost, GitHub (`Meraki` + `Junction 2018`), and Cisco blogs (confirmed Cisco's sponsor presence via `uma.es`).

### 6. Ensto — *"Adaptive Smart Electric Heating"* (2018)
- **Silver Spec**: [2018_Ensto_Adaptive_Smart_Electric_Heating.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Ensto_Adaptive_Smart_Electric_Heating.md)
- **Status**: **No verified public winner record found** for the electric heating challenge. However, L2 source `talotekniikka-lehti.fi` confirms Ensto ran **two challenges** at Junction 2018 attracting **14 participating teams in total** (with *Teach EV Chargers New Tricks* won by Team Glados's **Oneiro**; see [2018_Ensto_Oneiro_Glados.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2018_Ensto_Oneiro_Glados.md)).

### 7. Espoo — *"Analyzed Information at your Fingertips"* (2018)
- **Silver Spec**: [2018_Espoo_Analyzed_Information_At_Your_Fingertips.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Espoo_Analyzed_Information_At_Your_Fingertips.md)
- **Status**: **No verified public winner record found** for Espoo's challenge.
- **Adjacent Verified Smart-City Track Records (2018)**:
  - **Future Cities Track 1st (€1,000) / 4th Overall**: **GuideMe** by Makers UPV (see [2018_FutureCities_GuideMe_MakersUPV.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2018_FutureCities_GuideMe_MakersUPV.md)).
  - **City of Helsinki Stara `StreetReboot2` (`HEL 2019-003563`)**: 1st Place **€2,000** = **Make Meclu Great Again**; 2nd Place **€1,000** = **TerrainSense** (cross-linked in [2018_Movesense_Winners.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2018_Movesense_Winners.md)).

---

## Track-by-Track Findings & Confirmed Gaps (2017)

### 8. Trimble — *"Transform the way the world builds!"* (HoloLens / Intelligent Building, 2017)
- **Silver Spec**: [2017_Trimble_Transform_The_Way_The_World_Builds.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2017_Trimble_Transform_The_Way_The_World_Builds.md)
- **Status**: **L1 Challenge Participation Recap Found; Specific Winning Team Name Unverified**:
  - Trimble's Junction 2017 post-event article (`Trimble at Junction 2017 – Hacking the Way the World Works`, https://middleeast-business.com/Article?id=323) verifies that Trimble ran its challenge in the **Intelligent Building track**, where **4 teams** submitted 48-hour projects using Trimble technologies (AR/VR/HoloLens context), while web-search Devpost summaries indicate two winning slots / €1,000 prize pool. Specific team names/repos were not publicly extracted.

### 9. The Qt Company — *"Cross Platform for Desktop and Embedded"* (2017)
- **Silver Spec**: [2017_The_Qt_Company_Cross_Platform_Embedded.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2017_The_Qt_Company_Cross_Platform_Embedded.md)
- **Status**: **No verified public winner record found** across Devpost, GitHub, Qt blog, or Medium.

### 10. TrueFace.ai — *"Facial Recognition for Everyone"* (2017)
- **Silver Spec**: [2017_TrueFace_Facial_Recognition_For_Everyone.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2017_TrueFace_Facial_Recognition_For_Everyone.md)
- **Status**: **No verified public winner record found** across Devpost, GitHub, or Medium.

### 11. Helvar (2017) — *"Who needs a light switch?"*
- **Silver Spec**: [2017_Helvar_Who_Needs_A_Light_Switch.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2017_Helvar_Who_Needs_A_Light_Switch.md)
- **Status**: **L2 Participant Verified (`Itis LIGHT`), Official 2017 Winner Unverified** — see dedicated coverage in [2018_Helvar_IVision_Lamp_And_2017.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2018_Helvar_IVision_Lamp_And_2017.md).

---

## Sources Used in Verification Audit

- UMA Junction 2018 Release: https://www.uma.es/sala-de-prensa/noticias/tres-estudiantes-de-la-uma-se-alzan-con-los-tres-primeros-premios-de-junction-2018/
- Trimble Junction 2017 Article Mirror: https://middleeast-business.com/Article?id=323
- Helsinki Stara `StreetReboot2` Decision: https://paatokset.hel.fi/fi/asia/hel-2019-003563
- Talotekniikka-lehti (Ensto 14 teams across 2 challenges): https://talotekniikka-lehti.fi/oneiro-voitti-junction-2018-hackathonin/
- `teamglados/oneiro` (`HELP.md` referencing `http://project-plat.herokuapp.com/dashboard`): https://github.com/teamglados/oneiro
- `kvld/junction2018` (disambiguated as K-Group iOS app): https://github.com/kvld/junction2018
