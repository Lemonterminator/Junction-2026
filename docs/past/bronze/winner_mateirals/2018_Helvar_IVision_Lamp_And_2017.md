# Helvar Smart Building Lighting Winners & Entries — Junction 2018 (`IVision Lamp`) & 2017 Context

- **Event / Years**:
  - **Junction 2018** (Espoo, November 23–25, 2018): *"The Brain of the Building"* (Intelligent Manufacturing / Smart Building Track)
  - **Junction 2017** (Espoo, November 24–26, 2017): *"Who needs a light switch?"*
- **Silver Challenge Specs**:
  - [2018_Helvar_The_Brain_Of_The_Building.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Helvar_The_Brain_Of_The_Building.md)
  - [2017_Helvar_Who_Needs_A_Light_Switch.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2017_Helvar_Who_Needs_A_Light_Switch.md)
- **Verification Tier**:
  - **2018**: **L2 Verified** (Official **Tsinghua University** newsroom + **SenseTime** official press release + **Helvar** Chief Future Illuminator blog + **Sultan Yerumbayev** public CV)
  - **2017**: **L2 Participant Record / No Verified L1 Challenge Winner Confirmed**
- **Primary URLs**:
  - Tsinghua Official News (Nov 26, 2018): https://www.tsinghua.edu.cn/info/1173/17718.htm
  - SenseTime Official Release: https://www.sensetime.com/cn/technology-new-detail/3606?categoryId=53
  - Helvar Blog Context (Henri Juslén): https://helvar.com/how-to-make-the-light-work-for-you/
  - 2nd Place Portfolio CV (Sultan Yerumbayev): https://sultan91.github.io/CV_Sultan_Yerumbayev.pdf
  - 2017 Participant Context (`Itis LIGHT`, `mbradio.ru`): https://mbradio.ru/publication/2403

---

## Junction 2018 Verified Results — *"The Brain of the Building"* (`Helvar`)

### 1st Place (Challenge Winner): **IVision Lamp**
- **Award**: **Challenge Winner (1st Place)** — Helvar *"The Brain of the Building"* (*Intelligent Manufacturing / Smart Building* track) — described by Tsinghua as the first time a Tsinghua team won a Junction Challenge Winner award.
- **Team Name & Members**: **Tsinghua–SenseTime Future Deep Learning and AI Student Interest Team** (清华大学未来深度学习与人工智能学生科技兴趣团队 / 清华-商汤未来深度学习人工智能兴趣团队):
  - **Xiulong Yuan (袁秀龙)** — Department of Electronic Engineering (Class 53)
  - **Yingxue Guo (郭映雪)** — Department of Electronic Engineering (Grad 171)
  - **Xin Li (李鑫)** — Department of Automation (Master's 162)
  - **Feng Liang (梁丰)** — Department of Microelectronics and Nanoelectronics (Master's 162)
- **Problem & Solution Summary**: Helvar challenged teams to combine AI algorithms with indoor sensor telemetry across a building to act as an autonomous intelligent building "brain" optimizing lighting comfort and energy efficiency. In **42 hours**, the team built **IVision Lamp**, fusing **computer vision** with **multi-sensor environmental fusion** (`视觉＋多传感器信息融合`) to dynamically adapt luminaire brightness and lighting behavior to real-time human context and ambient conditions.
- **Event Context**: Chosen from Tsinghua's 3 participating Junction 2018 teams (as the only mainland Chinese university competing among 1,300+ hackers across 105 countries/regions and 46 challenge tracks).

### 2nd Place (Challenge Runner-Up): **Occupancy & RL Building Optimization**
- **Award**: **2nd Place** — Helvar *"The Brain of the Building"* challenge (confirmed via personal academic CV)
- **Participant**: **Sultan Yerumbayev** (AI & Robotics MSc student, Innopolis University)
- **Solution Summary**: Developed an *"Occupancy model of a building using machine-learning techniques and reinforcement learning optimization of energy consumption"*, applying ML occupancy estimation and reinforcement-learning control to optimize building lighting/energy efficiency.

---

## Hardware / Edge AI Tech Stack Summary (2018)

- **1st Place (`IVision Lamp`)**: Smart luminaire / desk lamp hardware control + **computer vision perception** + **multi-sensor fusion** loop operating under live partner test evaluation.
- **2nd Place**: Building sensor occupancy inference (machine learning) + **reinforcement learning** energy-control policy.
- **Partner Domain Context (`Helvar` Chief Future Illuminator Henri Juslén)**: Human-centric lighting adjusting intensity and color temperature dynamically around circadian rhythm, occupancy, and DALI-2 intelligent lighting systems (`helvar.com`).

---

## Junction 2017 Status — *"Who needs a light switch?"* (`Helvar`)

- **Verified Challenge Submission [L2]**: **Itis LIGHT** by **Itis.Team** (Kazan / ITMO University participants — Mark, **Mikhail Kolchanov**, **Daniil Samoylov**, **Nikita Khilobok**, Ekaterina Vissarionova) developed an intelligent lighting controller designed to operate locally without continuous internet access (`mbradio.ru`, Dec 19, 2017).
- **Disambiguation (`ecoPets`)**: Devpost project `ecoPets` (`devpost.com/software/ecopets`) appeared in some keyword searches alongside 2017 smart-home sensors, but inspection confirms `ecoPets` competed in **Fortum**'s energy challenge rather than Helvar's lighting hardware challenge.
- **Official Winner Record**: **No verified public L1/L2 winner record found** naming the official 1st-place winner of Helvar's 2017 *"Who needs a light switch?"* challenge across Devpost, Helvar archives, or Junction Medium blogs.

---

## Transferable Lessons for Smart-Building & Edge-AI Teams

1. **Fuse Vision + Ambient Telemetry Rather Than Trusting One Modality**: `IVision Lamp` won over pure telemetry entries by combining computer-vision scene understanding with multi-sensor indoor signals.
2. **RL / Predictive Control Needs Occupancy Estimation First**: Modeling room occupancy patterns cleanly provides the state representation required for reinforcement learning energy optimization.
3. **Resilient Local Control**: Both 2017 (`Itis LIGHT`) and 2018 lighting architectures highlight keeping core lighting inference responsive on local building/luminaire nodes rather than stalling on cloud round-trips.

---

## Sources & Raw Excerpts

- **L2 University News — Tsinghua University (Nov 26, 2018)**: https://www.tsinghua.edu.cn/info/1173/17718.htm
  > Confirms award (*Challenge winner*, 欧华/Helvar *"现代建筑智能大脑"*), project name **IVision Lamp**, method (*"视觉＋多传感器信息融合的方法处理台灯智能设备的光线变化"*), and all 4 team members (**袁秀龙、郭映雪、李鑫、梁丰**) photographed with the Helvar judge.
- **L2 Corporate Press Release — SenseTime**: https://www.sensetime.com/cn/technology-new-detail/3606?categoryId=53
- **L2 Participant CV — Sultan Yerumbayev**: https://sultan91.github.io/CV_Sultan_Yerumbayev.pdf
- **L2 2017 Participant Interview — `mbradio.ru` (Dec 19, 2017)**: https://mbradio.ru/publication/2403
