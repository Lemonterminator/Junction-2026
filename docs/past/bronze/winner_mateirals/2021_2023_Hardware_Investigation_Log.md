# Junction 2021–2023 Hardware, Robotics, IoT & Edge-AI Winner Investigation Log

> **文档性质**: Bronze 级历史调查总账（Investigation Log）。严格遵循 **零幻觉、可验证证据分级** 原则：仅记录本次检索会话中通过工具直接读取与交叉验证的团队、项目、技术栈、奖池金额及权威 URL；任何在公开档案中未出现的技术细节或缺失奖项均明确标注为 `[Not publicly documented]` 或 `[No public winner record verified]`。

## 1. 证据分级标准与检索边界 (Methodology & Evidence Levels)

- **`[L1]` 一级实证证据**：获奖团队公开源代码仓库（含 Git 提交者、依赖、核心算法实现）、个人作品集/技术博客确认页、或项目直接关联的一手视频/部署记录。
- **`[L2]` 二级权威证据**：出题企业官方技术博客（如 CGI Finland 官网）、Junction 官方 Medium 赛后复盘文章、Wikipedia 历届主奖总表、场地主办方（Kaapelitehdas）/ 芬兰科技媒体新闻通稿（Uusiteknologia.fi / STT Info / Mynewsdesk）。
- **核心档案缺口发现**：通过逆向比对 `docs/past/bronze/challenges_full.json` 与 `hackjunction.com` 官方前端 JS Bundle (`index-48h8IPvx.js`) 发现，官方新站归档在 2021–2023 年仅分别保留了 **5 个 (2021)**、**15 个 (2022)** 与 **6 个 (2023)** 赛题，漏录了 **CGI x KONE 2021**、**Huawei 2021/2023**、**Outokumpu 2023**、**Oras 2021** 等多项关键工业与硬件/传感器赛道；且 `docs/past/silver/en/Hardware/` 仅收录 4 个 2021–2022 赛题（2023 年在 `Hardware/` 目录下为 0 个）。

---

## 2. Junction 2021–2023 全场总冠军台账 (Overall Grand Winners)

根据 Wikipedia `Junction_(hackathon)` 历届主奖总表 `[L2]`、芬兰媒体与活动场馆公告 `[L2]` 核查结果：

| 年份 | 举办时间与地点 | 主奖池 (`[L2]`) | 全场总冠军项目与团队 (`[L2]`) | 领域与硬件/边缘属性判定 | 公开核验状态与来源 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2021** | 2021.11.19–21<br/>混合赛制（Otaniemi Aalto Hub + 全球 8 Hub + Gather） | **€10,000** (`[L2]` 2021–2022 常规主奖池) | **Nice-ify**<br/>成员：**Bryce Cronin**（单人队，澳大利亚开发者） | **纯软件 / 语音 NLP**：实时过滤语音聊天环境中的仇恨言论并替换为友善表达（非硬件/IoT）。 | `[L2]` Wikipedia + Medium 报道。 |
| **2022** | 2022.11.04–06<br/>Espoo Dipoli 线下回归（1,300+ 参赛者） | **€10,000** (`[L2]` Uusiteknologia.fi & LYY) | **Bitter Sweet**（项目名亦作 *Haru*）<br/>成员：**Donghoon Jang, Sunghun Kim, Junseong Kim, Chansu Park** | **纯软件 / 生成式 AI**：基于 GPT-3 与 Stable Diffusion 的 AI 情绪图画日记（非硬件/IoT）。 | `[L2]` Wikipedia 主奖总表 + LYY / Uusiteknologia.fi。 |
| **2023** | 2023.11.10–12<br/>Helsinki Kaapelitehdas 电缆厂（1,500+ 参赛者） | **€20,000 主奖池** (`[L2]` Kaapelitehdas) | **Driving Change – In the Blink for Safety**<br/>成员：**Markus Andersson, David Enberg, Alex Granlund, Johannes Peltola** | **未确认技术实现（疑似道路安全/驾驶辅助方向）**：Wikipedia 表中仅记录项目名与 4 名队员姓名，**未附带具体赛题归属、是否使用车载摄像头/边缘 CV 或纯 App 的任何技术说明**。 | `[L2]` Wikipedia 主奖总表 + Kaapelitehdas；闭幕式录像 [`gInQIghJOTY`](https://www.youtube.com/watch?v=gInQIghJOTY) 存在但无公开检索字幕，技术仓库 `[Not publicly documented]`。 |

> **严格实证说明**：虽然 `"In the Blink for Safety"` 字面常与驾驶疲劳眨眼检测（DMS/Edge-CV）产生联想，但在所有直接工具读取的原始页面（含 Wikipedia 原文）中均无该项目技术栈的直接文字描述。依据严格核查规则，本档案不将“边缘 CV 摄像头”当作已证实事实归因于该项目，仅将其作为全场总冠军条目完整留档并标记缺口。

---

## 3. 2021–2023 硬件、机器人、嵌入式、海事/工业 IoT 与传感器赛道全量调查表

### 3.1 已核验获奖者 (`L1` / `L2`)

| 年份 | 合作伙伴与赛题 | 原赛题分类 / Silver 归档 | 已证实获奖团队与名次 | 核验核心技术栈与方案 | 证据等级与核验链接 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2021** | **Helvar** — `Brighter Spaces: Intelligent Lighting` | `IoT & Hardware` / [`Hardware/2021_Helvar...`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2021_Helvar_Brighter_Spaces_Intelligent_Lighting.md) | **Lumen Loop 3.0**（Helvar 赛题获胜 + 全场 Top-10，200+ 项目中入围）<br/>成员：Elizaveta Lebedeva, Denys Kovalenko, Carlos Bentes | 5s 等桶离散化 `CombinedCorrelator` + 加权 Pearson `scipy` 相关性定位传感器坐标 + `.pickle` 序列化模型 + Flask 64px 建筑平面瓦片地图与 Top-K 推荐交互 UI（`"AirTag meets intelligent lighting"`）。 | `[L1]` [`LizaLebedeva/junction-2021`](https://github.com/LizaLebedeva/junction-2021)<br/>`[L1]` [`elizavetalebedeva.com/tag/junction/`](https://elizavetalebedeva.com/tag/junction/)<br/>`[L1]` YouTube [`dX27x6s6wl4`](https://www.youtube.com/watch?v=dX27x6s6wl4)<br/>`[L2]` [`hackjunction.medium.com (1926e69eed6b)`](https://hackjunction.medium.com/junction-2021-intelligent-lighting-as-the-engine-for-brighter-spaces-1926e69eed6b) |
| **2021** | **Helvar** — `Brighter Spaces: Intelligent Lighting` | 同上（Helvar 含 3 个子赛题） | **FloorMagic (Healthy Mind Tech)**（公司履历标注 `Junction 2021 - Helvar Challenge Winner`）<br/>成员：Paula Petcu, Troels Nielsen, Martin Basterrechea, Kim Ng | 基于楼宇运动传感器人流数据反推未标注传感器位置；源码仓库 `[Not publicly documented]`。 | `[L1]` [`healthymindtech.com`](https://healthymindtech.com/)<br/>`[L2]` [`hackjunction.medium.com (2ee963c6c0e8)`](https://hackjunction.medium.com/junction-2021-intelligent-lighting-as-the-engine-for-brighter-spaces-2ee963c6c0e8) |
| **2021** | **CGI x KONE** — `Sky(scraper)-is-the-limit` | *缺省未入 `challenges_full.json`* | **Team Glados — `ElevAI`**（*"Best Performing and Most Explainable Model"* 第一名 + 全场 Top-10）<br/>核心作者：Ville Toiviainen (`Villux`), Andreas Urbanski (`nardeas`) | Ray Tune + Hyperopt (`500` trials, 5-fold) 优化 `XGBoost` / LightGBM / CatBoost / RF + `SMOTEENN` / `RandomUnderSampler`；`f2_score ≈ 0.9722`；单树轨迹 + SHAP 可解释 + AR 远程设备预检 + 工程师现场部件故障反哺闭环。 | `[L2]` [`CGI 2021 博客`](https://www.cgi.com/fi/fi/blogi/junction-2021-hackathon-highlights)<br/>`[L1]` [`teamglados/elevai`](https://github.com/teamglados/elevai)<br/>`[L1]` [`vimeo.com/648187179`](https://vimeo.com/648187179) |
| **2021** | **CGI x KONE** — `Sky(scraper)-is-the-limit` | 同上 | **S.H.I.E.L.D** (*Safety Helmet with Intelligent Embedded Lighting Device* — *"Out-of-the-Box Thinking"* 奖项得主) | 智能安全帽集成嵌入式照明、AR 摄像头、语音转文本（STT）与手势识别，用于免手触电梯井道维保；队员与源码 `[Not publicly documented]`。 | `[L2]` [`CGI 2021 博客`](https://www.cgi.com/fi/fi/blogi/junction-2021-hackathon-highlights) |
| **2022** | **CGI x KONE x Meyer Turku** — `Cruising with Robots` | `Other` / [`Hardware/2022_CGI_KONE...`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2022_CGI_KONE_Meyer_Turku_Cruising_With_Robots.md) | **1st Place**: **C-HAL 9000**<br/>**2nd Place**: **Laundry day is everyday** | 邮轮“人流 × 机器人流”协同与显/隐性船上自动化服务；CGI 提及赛道涌现屋顶攀爬机器人与服务路径追踪智能手表原型；队内成员与代码仓库 `[Not publicly documented]`。 | `[L2]` [`CGI 2022 博客 (10.11.2022)`](https://www.cgi.com/fi/fi/blogi/cginside/out-box-thinking-more-valuable-ever)<br/>`[L2]` YouTube [`Ph5deOWpGh4`](https://www.youtube.com/watch?v=Ph5deOWpGh4) |
| **2022** | **Huawei** — `Work Remotely with Huawei` | `Health`（移动健康与 ML 姿态识别） | **Pause-Fit**（Winner） | 面向远程办公人员的多人社交健身游戏，集成华为机器学习 SDK（Huawei ML SDK）姿态识别。 | `[L2]` [Huawei Developer Forum (`0203103393061865053`)](https://forums.developer.huawei.com/forumPortal/en/topic/0203103393061865053) |
| **2023** | **Huawei** — `Sense the Motion` | *缺省未入 `challenges_full.json`* | **2nd Place**: **J-mp**（Jesse Lappalainen, Juho Torkkeli, Aku Paananen, Onnimanni Hannonen, `Hylje5000`）<br/>*1st Place*: `[Not publicly documented]` | Flutter App + `sensors_plus` 加速度三轴阈值（`x+y+z > 30.0`）+ `vibration` 触觉反馈 + `flutter_compass` 磁力计 + GPS + QR 扫码户外游戏；Firebase + Next.js 13。 | `[L1]` [`Mankeli-Software/junction2023`](https://github.com/Mankeli-Software/junction2023)<br/>`[L1]` [`jemlap.fi/projects`](https://www.jemlap.fi/projects) |

---

### 3.2 已核验开源参赛项目（非冠军或名次未公开）与非硬件高可见度同届获奖者

| 年份 | 赛题 / 赛道 | 项目 / 团队 | 属性与关键技术事实 | 证据与状态 |
| :--- | :--- | :--- | :--- | :--- |
| **2021** | **Oras** — `The Smartest Water Experience` *(早于 2022 版)* | `penny-five/hanaverse` (`2021-11-19T16:00:06Z`) | Kotlin Spring Boot + Gradle + PostgreSQL 13.4 (`docker-compose`) 后端原型，针对 Oras 智能水体验节水赛题。 | `[L1]` 仓库存在；获奖名次 `[Not publicly documented]`。 |
| **2021** | **Huawei** — `Innovate With Huawei` | *Mynewsdesk 报道提及获奖者* | 聚焦 AR 与 3D 建模移动应用/游戏开发（HMS 生态）。 | `[L2]` Mynewsdesk 芬兰报道（未深入硬件外设）。 |
| **2021** | **CGI x City of Turku** — `Preventing loneliness and social isolation` | **1st**: `The Chain of Support` (5人)；**2nd**: `Finnish Fast` | 基于 ML 活动推荐与链接协调员匹配的社会服务/软件方案（非硬件）。 | `[L2]` CGI 2021 官方博客。 |
| **2022** | **Healthy Mind Tech (多赛道自述)** | **Healthy Mind Tech** (Paula Petcu 等) | 团队官网获奖列表载明 **`Junction 2022 - Winner in 3 categories`**，但未指明这 3 个具体赛题名称。 | `[L1]` [`healthymindtech.com`](https://healthymindtech.com/)；具体赛道 `[Not publicly documented]`。 |
| **2022** | **CGI** — `Now Green Code you must` | **1st**: `Carbon: Green Audio Service`；**2nd**: `0x00ff00` | 绿色低能耗媒体站点后端与前端软件挑战（非硬件）。 | `[L2]` CGI 2022 官方博客。 |
| **2022** | **Smartly.io** — `Produce More Content With Less!` | **Team Glados (`mishmash`)** | 1st Prize 创意数字内容生成平台（软件/GenAI）。 | `[L1]` [`teamglados/mishmash`](https://github.com/teamglados/mishmash) |
| **2022** | **BNB Chain** — `The Road Towards Society 2.0` | **3rd**: `SilentBerry` | Web3/区块链轨道（非硬件）。 | `[L2]` STT Info 新闻稿。 |
| **2023** | **Huawei** — `Sense the Motion` | **Motion Potion** (`andras-adam/motion-potion`) | Expo/RN Android 原生 IMU（1ms `DeviceMotion` 500 帧滑窗 + `lpf` 低通滤波 + 几何画圆/X/Y 直线手势识别 + GPS 地图）。 | `[L1]` [`andras-adam/motion-potion`](https://github.com/andras-adam/motion-potion)；名次 `[Not publicly documented]`。 |
| **2023** | **Huawei** — `Sense the Motion` | **Vital** (`MiroKeimioniemi/vital-app`) | 华为穿戴步数/心率区/睡眠遥测 -> Azure Functions Python -> React + Roblox 游戏属性联动。 | `[L1]` [`MiroKeimioniemi/vital-app`](https://github.com/MiroKeimioniemi/vital-app)；名次 `[Not publicly documented]`。 |
| **2023** | **Outokumpu** — `Sustainable AI-Generated Insights` | **PR🌍MPTERRA** (`ecognize`) & **Stainless Hill** | 针对钢铁生产可持续性的 Custom-GPT / Streamlit AI 助手（软件/LLM，无工业传感硬件）；该赛题官方获奖名单 `[Not publicly documented]`。 | `[L1]` [`nathanyaqueby/ecognize`](https://github.com/nathanyaqueby/ecognize) & [`oussamabatouche.com`](https://oussamabatouche.com/projects/hck_junction_23/) |
| **2023** | **Veikkaus** — `Next Level of Interactive Gaming Experiences` | **VeikkAS**（Top finalist tier） | 互动游戏体验赛道（非硬件）。 | `[L1]` `vinski.fi` & `iqiz.dev` |

---

## 4. 无公开获奖记录赛道与重点企业缺席核查清单 (No-Winner-Record & Negative Audit)

经全网（中英文及芬兰语搜索、GitHub、`hackjunction.com`、`hackjunction.medium.com`、Devpost、企业新闻室及 YouTube 闭幕式页面）交叉排查，确认以下结果：

### 4.1 明确存在赛题但 **无公开可验证获奖名单 (`[No public winner record verified]`)**
1. **Oras (2022)** — `The Smartest Water Experience` ([`docs/past/silver/en/Hardware/2022_Oras_The_Smartest_Water_Experience.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2022_Oras_The_Smartest_Water_Experience.md))
   - **赛题硬件与数据**: Oras Hydractiva 数字花洒与 BLE 无触控智能水龙头、20 套公寓真实水流与漏水定位 JSON 数据、20 秒洗手肥皂提醒算法需求。
   - **核查结果**: Oras 官网仅留存产品获奖与设计报道，未公开 Junction 2021 或 2022 黑客松获奖队伍名单。
2. **Nexi (2022)** — `Crack the Payments` ([`docs/past/silver/en/Hardware/2022_Nexi_Crack_The_Payments.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2022_Nexi_Crack_The_Payments.md))
   - **赛题硬件与数据**: 外接 NFC 读卡器与手机 NFC 底层协议解析（Visa / MasterCard / Maestro 支付终端通信协议，€1,500 奖金）。
   - **核查结果**: 以 `Nexi` 及前身品牌 `Nets` 进行跨语言检索，均未发现公开的获奖队伍或源码仓库。
3. **Cronvall (2023)** — `Making industrial purchase decisions more transparent & sustainable`
   - **核查结果**: 在 `challenges_full.json` 及 `hackjunction.com` 存在 2023 工业采购可持续赛题条目，但无任何公开获奖队伍或仓库记录。

### 4.2 重点硬件/工业伙伴 2021–2023 缺席核实清单 (Negative Audit)
针对重点关注的硬件、仪器、能源与工业物联网伙伴，核实其在 **2021–2023 年主会场 Junction 旗舰赛** 的出题状态如下：

| 目标企业 | 2021–2023 主赛是否出题 / 是否有公开获奖记录 | 真实历史分布年份（已在档案/官方记录中核验） |
| :--- | :--- | :--- |
| **Trimble** | **无 2021–2023 记录** | 早期届次（如 2017–2018 档案记录） |
| **Vaisala** | **无 2021–2023 记录** | 早期届次（如 2017–2018 档案记录） |
| **Suunto (Movesense)** | **无 2021–2023 主赛获奖记录** | 历史硬件合作生态伙伴（2017–2019 Movesense 系列），未在 2021–2023 主赛赛道榜出现 |
| **Valmet** | **无 2021–2023 主赛记录** | **2019**（联合 Aalto AIIC 出题 `Service Workshop of the Future`，`PaperCut Inc.` 获胜）与 **2025**（联合 HSY 出题 `Intelligent Flow Optimization`，`IWPO` 获胜） |
| **Nokia** | **无 2021–2023 具体硬件赛题/获奖记录** | `hackjunction.com` 历史合作伙伴列表常驻品牌，但 2021–2023 年主挑战列表中未现专属硬件/通信赛题 |
| **Murata / Kempower / Danfoss** | **无 2021–2023 Junction 旗舰赛记录** | 属芬兰/北欧更广泛工业生态或区域活动讨论对象，未担任 Junction 2021–2023 主赛挑战出题方 |

---

## 5. 新建 Bronze 案例档案总索引

1. [`2021_Helvar_BrighterSpaces_LumenLoop3_FloorMagic.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2021_Helvar_BrighterSpaces_LumenLoop3_FloorMagic.md) — **Helvar 2021 (`L1`/`L2`)**: `Lumen Loop 3.0` + `FloorMagic`
2. [`2021_CGI_KONE_SkyScraper_ElevAI_SHIELD.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2021_CGI_KONE_SkyScraper_ElevAI_SHIELD.md) — **CGI x KONE 2021 (`L1`/`L2`)**: `ElevAI` (`Team Glados`) + `S.H.I.E.L.D` 智能维保安全帽
3. [`2022_CGI_KONE_MeyerTurku_CruisingWithRobots_CHAL9000.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2022_CGI_KONE_MeyerTurku_CruisingWithRobots_CHAL9000.md) — **CGI x KONE x Meyer Turku 2022 (`L2`)**: `C-HAL 9000` (1st) + `Laundry day is everyday` (2nd)
4. [`2023_Huawei_SenseTheMotion_Jmp_MotionPotion_Vital.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2023_Huawei_SenseTheMotion_Jmp_MotionPotion_Vital.md) — **Huawei 2023 (`L1`)**: `J-mp` (2nd Place) + 同赛道开源硬件感知对照 (`Motion Potion`, `Vital`)
5. [`2021_2023_Hardware_Investigation_Log.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2021_2023_Hardware_Investigation_Log.md) — **2021–2023 调查总账与缺口核实报告**
