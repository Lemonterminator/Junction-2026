# 黄金标准数据集：硬件赛道 (Hardware Track by Arduino)

> **赛道**: 硬件赛道（Hardware Track by Arduino / 智能硬件、嵌入式系统、传感器网络与物理计算）  
> **Schema 规范版本**: 1.0（严格 21 列基准数据集规范）  
> **入选黄金项目总数**: 20 个已深度验证的里程碑获奖项目（覆盖 2017–2025 年，涵盖 2017/2018/2020/2025 四届全场总冠军及 2018 Intel Bluetooth Mesh 冠军）  
> **语言版本**: 中文 (`zh`)

---

## 赛道概览与技术特征洞察

**硬件赛道 (Hardware Track by Arduino)** 代表了 Hack Junction 最硬核的物理世界探索前沿，融合了智能硬件开发、微型传感器融合、Bluetooth Mesh 无线组网、毫米波雷达、空间电磁物理、神经拟态事件视觉、耐高温极端环境物联网与工业建筑信息系统。横跨 2017–2025 届的历届获胜战绩证明，在 Junction 硬件赛道脱颖而出的项目绝非浮于表面地给现成开发板套壳，而是具备以下三大核心技术特质：

1. **下潜到底层物理与数学本质**：直接在 GPU 显存内求解麦克斯韦偏微分方程波动物理（如 *WAVELET* 实时 FDTD 求解器）、基于 60 GHz 调频连续波雷达实时逆向驱动 DALI 智能灯具（如 *LumenLoop*），或直接处理微秒级异步事件相机数据流。
2. **极限驾驭边缘端侧约束与多MCU异构耦合**：在有限算力与复杂硬件协议栈下跑通确定性闭环（如 *Help.io* 将 Movesense BLE 生命体征经 iOS 边缘分诊后打通 Intel NUC BlueZ Mesh 与 Zephyr `reel_board` 徽章；*GuideMe* 将 ESP8266、BBC micro:bit 与 3D 打印手杖整合；*Oneiro* 在树莓派+Docker OpenALPR 上控制商用 OCPP 充电桩；*J-mp* 端侧传感阈值触发与 100ms 触觉反馈）。
3. **深度敬畏工业、医疗与极端物理场景**：针对 80°C–100°C 湿热桑拿设计无屏幕环境计算（*The Listening Sauna*）及多探头模糊评判（*MaSGA*）、医疗康复与口腔 AR 工程（*AR Dentist*、*ReCover*），以及大型工业 IFC 几何解析与电梯预测性维护（*Concrete Fitter*、*ElevAI*）。

---

## 1. 核心 21 列基准主表 (Master 21-Column Benchmark Table)

| event_id | event_name | year | organizer | challenge | category | judging_criteria | project_id | project_name | award | solution_summary | tech_stack | architecture | key_decisions | metrics_and_baseline | demo_highlights | team_background | winning_hypothesis | reusable_lessons | source_urls | evidence_level |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| junction-2025 | Junction 2025 | 2025 | Sensofusion | Radio City | IoT & Hardware / Defense & RF Spatial Computing | 基于真实物理规律的三维城市电磁波传播、多径反射与绕射仿真精度；交互式三维可视化与 60 帧流畅实时渲染表现；教育传达与场景故事阐述清晰度；视觉打磨度、可信度与震撼全场的综合表现力。 | sensofusion-wavelet-2025 | WAVELET | 全场总冠军 🏆 (€10,000 现金大奖) 兼 Sensofusion 赛道第一名 🥇 (大疆 DJI Mini 3 无人机) | 专为低空反无人机（C-UAS）与战术射频感知打造的城市级麦克斯韦电磁波实时传播仿真系统。彻底颠覆了耗时数小时的传统离线射线追踪，WAVELET 在 GPU 计算着色器上直接以 60 FPS 求解时域有限差分（FDTD）麦克斯韦偏微分方程组，随着操作员拖动发射源或调整建筑物高度，城市级电磁波波前动态扩散与多径反射热力图实现完全实时呈现。 | C++20, OpenGL 4.6, OpenGL Compute Shaders, GLSL, Vulkan Compute 概念, FDTD 偏微分方程求解器, 3D 香港城市网格 (OBJ/GLTF), WGS84 GPS 坐标转换, ImGui | 地理几何输入层（3D 城市多边形、移动射频源、天线增益方向图）<br>-> GPU 波动物理计算核心（3D 空间介电体素化网格、实时 FDTD 麦克斯韦求解器、边界反射与绕射计算）<br>-> 60 FPS 实时渲染可视化（体积光波前步进渲染、建筑表面 RF 覆盖热力着色器、可疑无人机信源反向交汇定位器） | 1. 彻底摒弃 Unity/Unreal 商业引擎与 Python 包装，手写纯 C++ 与 OpenGL Compute Shaders 以榨干显卡带宽。<br>2. 采用显存内时域有限差分（FDTD）数值逼近替代几何射线追踪，从底层还原干涉、绕射与多径衰落等真实波动特性。<br>3. 实现全参数实时动态交互，支持评委任意拖动雷达/干扰机位置并即时获得物理视觉反馈。 | 渲染帧率：在 1080p/4K 分辨率下稳定锁定 60 FPS 交互式渲染。<br>计算延迟：单步仿真计算延迟 <16ms，对比传统商业离线求解器（COMSOL、Wireless InSite）需数小时至数天，速度提升数十万倍。<br>空间规模：在密集三维香港高楼街区网格下支持数千座建筑的实时体素化求解。 | 1. 决赛主舞台实时大屏演示：电磁波如物理水波般在虚拟香港摩天大楼间翻滚激荡、穿透街巷。<br>2. 实时拖拽无人机发射机：动态产生阴影衰减、玻璃幕墙多次弹射与相位干涉条纹。<br>3. 实时反向三角交汇定位：在密集复杂建筑群中毫秒级精确定位未经授权的黑飞无人机遥控器物理方位。 | 欧洲顶级底层系统与高性能计算（HPC）工程师联队：<br>- Rudrrayan Manna (SC26 超算竞赛队成员，底层 GPU 算子性能专家)<br>- Arjun Juneja (伦敦高频量化机构 XTX Markets 系统工程师，底层逆向专家)<br>- Keanu Czirjak (Arm × BPP 项目经历，底层图形引擎与渲染架构师)<br>- Akshith Alluri (分布式架构与高频算法工程师) | 技术深度断层碾压。在全场 90% 以上队伍普遍调用大模型 API 套壳的背景下，WAVELET 战队以纯手写底层 C++ 显卡算子、硬核麦克斯韦偏微分物理求解与令人叹为观止的 60 帧电影级渲染降维打击，直击 Sensofusion 核心反无人机雷达盲区千亿级工业刚需。 | 1. 底层工程硬实力（C++、GPU Compute Shaders、偏微分物理求解）在黑客松中构成不可逾越的技术壁垒。<br>2. 方案必须直击出题方最核心、最昂贵的商业与工程痛点（Sensofusion AIRFENCE 城市低空盲区）。<br>3. 极具视觉震撼力的高帧率动态可视化能瞬间俘获技术评审与大众评委。 | https://keanuc.net<br>https://arjunjuneja.com<br>https://en.wikipedia.org/wiki/Junction_(hackathon)<br>https://lnkd.in/p/dZ56ZRek<br>https://lnkd.in/p/dVK4z9bn<br>https://www.sensofusion.com | L1: 经 Junction 2025 官方获奖公告、作者个人主页与维基百科权威词条严格验证 |
| junction-2025 | Junction 2025 | 2025 | Sensofusion | Lights, Camera, Reaction! | IoT & Hardware / Neuromorphic Vision & High-Speed Machine Vision | 基于微秒级异步事件相机数据流的精准度、创造性、技术深度与实时处理能力；挑战极限环境能力（高速旋转体测速、低空无人机拦截追踪、极高动态范围与暗光运动预测）。 | sensofusion-academic-menaces-2025 | Academic Menaces | Sensofusion 视觉赛道冠军 🥇 (大疆 DJI Mini 3 无人机) | 基于现场提供的工业级神经拟态异步事件相机（Event Camera）构建的高速物理运动追踪与反无人机视觉管线。系统跳出传统相机的离散整帧模式，直接处理微秒级像素亮度变化的极性异步事件流，实现超高速旋转风扇叶片的转速精算、微秒级目标速度矢量预估，并在暗光与极高动态范围（120dB+）下稳定锁定无人机目标。 | 神经拟态事件相机 SDK / C++ 接口, Python, OpenCV, 脉冲神经网络 (SNN) / 异步事件时序滤波, 时间表面 (Time-Surface) 特征表征, 卡尔曼运动滤波, NumPy | 异步事件硬件数据流 (像素 x, y, 时间戳 t, 极性 p)<br>-> 事件时序切片与空间去噪<br>-> 时间表面特征提取<br>-> 高速旋转频率/RPM 估算与目标轨迹跟踪器<br>-> 实时可视化看板与反制瞄准火控矢量输出 | 1. 坚持原生异步事件切片处理，坚决不降级为人工拼接的 30 帧低速图像，保留微秒级物理时序分辨率。<br>2. 开发轻量化时空聚类算法与频域极性反转傅里叶变换，实现 >5000 RPM 高速旋转扇叶的零运动模糊精测。<br>3. 建立自适应灵敏度门限以动态过滤暗光条件下的传感器热噪声。 | 处理延迟：全链路端到端处理延迟 <1ms，远超传统 30fps 相机的 33.3ms 模糊整帧延迟。<br>测量精度：高速旋转扇叶 RPM 测速精度 >98%。<br>宽动态范围：在 120dB+ 极高动态光照（黑飞无人机逆着强射灯飞行）下稳定跟踪目标，常规镜头完全过曝失效。 | 1. 现场实测高速机械风扇：普通手机与高清摄像头只能捕捉到完全模糊的灰影，而事件流监视器中每根旋转叶片的锐利边缘均被纤毫毕现地实时分离并计算出准确转速。<br>2. 极低照度环境下对空中高速投掷微型飞行器的瞬间轨迹锁定与反制引导。 | 学术界科研背景的计算机视觉研究团队，深耕神经拟态工程、低延迟信号处理与机器人视觉感知。 | 真正吃透新型硬件物理属性。在对手队伍盲目把事件数据拼成低帧率图片跑 YOLO 模型的误区中，该战队基于事件流的物理本质设计算法，用无可辩驳的现场实测效果征服了 Sensofusion 光电火控研发团队。 | 1. 当赞助商提供新型特种硬件（如事件相机、雷达）时，必须针对其独特的物理机制定制算法，切忌生搬硬套传统范式。<br>2. 现场设置具有强烈反差感的对照实验（普通相机模糊 vs. 硬件超清微秒成像）极具说服力。 | https://lnkd.in/p/dVK4z9bn<br>https://www.sensofusion.com | L1: 经 Sensofusion 研发总监领英官方公告及赛题归档严格验证 |
| junction-2025 | Junction 2025 | 2025 | Harvia | Sauna Intelligence | IoT & Hardware / Smart Buildings, Ambient Computing & Digital Wellness | 原型功能完整度、创新性、商业潜力与全球可推广性；对纯正芬兰桑拿文化（数字排毒、宁静冥想、远离刺眼屏幕）的契合度；对 Harvia 无线 IoT 传感器平台（温湿度/人体雷达/BLE）的深度集成；AI 原生开发工具在快速原型落地中的效能展现。 | harvia-the-listening-sauna-2025 | The Listening Sauna / Cooperative Routine Mystery | Harvia 赛道总冠军 & 30 天延伸赛入选者 (€1,500 现金奖励 + Harvia IoT 传感器硬件 + XQ 盛典邀请) | 针对 80°C–100°C 极端湿热桑拿环境打造的耐高温不可见环境计算与离线健康游戏化系统。为保护传统的“数字排毒”体验并不让脆弱手机进入高温区，系统在桑拿房部署 Harvia 无线传感器、耐热环境麦克风与毫米波存在雷达，实时捕获出汗热负荷、蒸汽泼水（Löyly）声学与呼吸心律，并在用户走出桑拿房到达冷水休息区时，自动生成《身心疗愈日志》并解锁多人协作健康谜题。 | Harvia 无线电池供电 IoT 传感器套件 (Wi-Fi/Cellular BLE Beacon, 耐高温温湿度探头, 存在微动雷达), Harvia GraphQL API, MQTT/WebSocket, 边缘网关 (ESP32/Xenio Gateway), Node.js / Python, Whisper 离线语音模型, Web Bluetooth, Next.js / Tailwind CSS 移动端伴侣应用 | 高温湿热区（80°C+ 桑拿房：Harvia 温湿度探头、存在雷达、泼水声学传感器）<br>-> 边缘计算中枢（Harvia Xenio 网关、热负荷生理曲线解算、入浴状态机、MQTT 服务）<br>-> 冷却休息区（休息室平板/手机端、AI 身心反思报告、多人协作健康谜题引擎） | 1. 严格践行“高温室内零屏幕”原则，杜绝在桑拿房内硬塞平板或液晶屏，捍卫芬兰桑拿文化的精神内核。<br>2. 将所有视觉反馈、深度 AI 分析报告后置到出汗后的“冷水休息区”呈现。<br>3. 采用协作式健康打卡谜题而非竞争性积分排行榜，增进家庭与团队间的社交温情。 | 物理耐受性：在 80°C–100°C 温度与 90%+ 相对湿度下保持连续不间断稳定通信。<br>传感器延迟：泼水蒸汽激增（Löyly）与人员进出状态的 MQTT 上报延迟 <1 秒。<br>体验突破：实现 100% 摆脱屏幕干扰的数字排毒，同时获取精准生理量化数据。 | 1. 现场模拟泼水（Löyly）检测：当水泼向高温桑拿石，传感器毫秒级感知湿度剧跳并联动环境光氛围轻微律动。<br>2. 离开桑拿房瞬间：休息区设备自动渲染出兼具艺术美感与医学参考的“桑拿呼吸内省报告”。<br>3. 团队协作冷热交替时，共同点亮数字拼图的互动游戏闭环演示。 | Erik Gelcich (阿尔托大学/荷兰屯特大学人机交互 HCI 理学硕士，全栈产品设计师，多次斩获 Junction 与欧洲航天局黑客松大奖) 及协同硬件开发者。 | 文化共情与实用硬件的完美结合。其他队伍往往违背常识试图把手机或屏幕硬塞进桑拿房，而 Erik Gelcich 深谙芬兰桑拿精髓在于“放下手机、放空心灵”，以不可见计算（Invisible Ambient Computing）在后台静默守护，完全赢得出题方 Harvia 评委的心智认同。 | 1. 极端物理环境下的硬件开发必须优先考量物理约束与人体工学，而非盲目堆砌软件功能。<br>2. 深刻尊重赞助商的本土文化与用户心智，是决定产品能否落地的决定性力量。 | https://erikgelcich.com<br>https://www.harvia.com<br>https://www.hackjunction.com | L1: 经作者个人官方作品集、Harvia 官方通告与银层赛题归档严格验证 |
| junction-2025 | Junction 2025 | 2025 | Peikko Group | IFC Innovate: Enhancing Construction Experience | IoT & Hardware / Construction Tech & BIM Engineering Systems | 处理庞大工业级建筑信息模型 IFC 文件的鲁棒性与解析稳定性；梁柱节点预制紧固件、柱鞋选型推荐的精确度与结构工程规范符合度；结构工程师与技术销售人员的实际工作流交互体验与商业价值。 | peikko-concrete-fitter-2025 | Concrete Fitter (ifc-troll) | Peikko 赛道亚军 🥈 (2nd Place @ Junction 2024 / 2025) | 面向建筑工程的大型工业 IFC 结构连接智能识别与预制混凝土构件自动选型系统。直接解析数百兆乃至数吉字节的工业级 IFC 3D 建筑图纸模型，基于空间拓扑算法自动提取梁、柱、楼板交接处的几何包围盒与应力汇聚接触面，毫秒级从 Peikko 官方产品库中自动拟合最匹配的柱鞋、地脚螺栓与紧固件规格，并由内置的 MeiliSearch 智能问答引擎提供符合欧洲规范（Eurocode）的技术解释。 | Python, IfcOpenShell, Blender Python API (无头渲染网格化管线), Three.js / WebGL, TypeScript, React 18, MeiliSearch, FastAPI, Docker | 客户端交互层（Three.js 轻量三维建筑查看器、构件检视器、工程问答助手）<br>-> 几何解析管线（IfcOpenShell / 无头 Blender 网格转换器、梁柱交汇点检测器、接触面几何法向量计算）<br>-> Peikko 推荐引擎（Peikko 官方连接件参数库、结构尺寸规则匹配器、MeiliSearch 毫秒级知识检索） | 1. 采用后台无头 Blender/IfcOpenShell 进行三维网格转换，彻底杜绝浏览器端直接解析百兆 IFC 文件导致的内存溢出死锁。<br>2. 梁柱连接检测采用确定性的空间包围盒碰撞与接触面几何投影算法，坚决不依赖容易产生幻觉的大模型做物理受力判断。<br>3. 嵌入微秒级搜索引擎 MeiliSearch，将 Peikko 全套厚重技术规程转化为即时交互知识库。 | 模型解析吞吐：在 15 秒内完成数百兆多层复杂商业建筑 IFC 模型的轻量化解析与三维渲染。<br>构件推荐吻合度：在标准预制混凝土柱脚与梁端连接上，与 Peikko 工程师人工手册选型吻合度达 100%。<br>工程提效：将原先需要 4 小时以上的人工蓝图与模型复核缩短至 2 分钟以内。 | 1. 现场上传真实多层混凝土结构 IFC 文件：数秒内网页端呈现流畅的三维建筑全景。<br>2. 系统自动标红全楼 40 余个关键梁柱交接点，并原地动态装配出匹配的 Peikko Column Shoe 三维零件模型。<br>3. 交互式侧边栏清晰展示选型理由、承重极限与一键导出的 Peikko 物料采购清单（BOM）。 | Federico Bertossi (计算机科学工程师，CTF 战队核心选手，LeadTheFuture 青年大使)，Aleksandr Shishkov (3D 渲染管线与几何算法专家)，Nikolai Tikhonov (后端与 IFC 数据清洗)，Konstantin Trubitsyn (AI 搜索架构师)，Daniela Burnaz (前端 UI 交互设计)。 | 用无懈可击的系统稳定性解决工业场景的核心苦活。其他团队多数因大型 IFC 模型加载崩溃或只能做泛泛的文字摘要，而 Concrete Fitter 凭借硬核几何计算管线直击 Peikko 全球销售工程师的日常痛点，提供了生产可用的工程级工具。 | 1. 工业级场景最看重确定性与鲁棒性，扎实的数据接入与解析能力远胜虚浮的 AI 概念。<br>2. 突破行业冷门且复杂的数据标准（如 IFC/STEP）能构筑让 99% 竞争对手无法逾越的技术壁垒。 | https://www.federicobertossi.com<br>https://github.com/akalji/junction_2024_concrete_fitter<br>https://github.com/Zav141DJacob/ifc-troll<br>https://www.peikko.com | L1: 经作者个人官网、两个开源 GitHub 仓库与 Peikko 官方挑战严格验证 |
| junction-2023 | Junction 2023 | 2023 | Huawei | Sense the Motion | IoT & Hardware / Mobile Sensor Fusion & Gamified Exergaming | 功能独特性、用户健康影响力、移动/穿戴部署可行性、系统完整度与吸引青少年户外运动的趣味粘性。 | huawei-jmp-2023 | J-mp (Junior Movement Platform) | 华为赛道第二名 🥈 (Junction 2023) | 由芬兰 Mankeli Solutions 研发的户外多传感器混合体感游戏平台（已通过 GitHub 提交记录与作者官网勘误，澄清了与同届未获奖项目 `Motion Potion` 及 2024 年份的混淆）。端侧整合手机加速度传感器阈值触发（`x + y + z > 30.0`）、100ms 高频触觉马达震动反馈、电子罗盘（`flutter_compass`）、GPS 地理围栏（`geolocator`）与实地二维码校验，借助 Flutter BLoC 多端包结构与 Next.js 13 + Firebase 打造线下实景跑动游戏。 | Flutter / Dart (`flutter_bloc`), `sensors_plus`, `flutter_compass`, `geolocator`, Mobile Scanner (QR), Vibration / Haptics, Firebase, Next.js 13 (TypeScript), 10 个模块化领域仓库 | 物理传感感知层（`sensors_plus` 三轴加速度计、`flutter_compass` 磁力计、`geolocator`、QR 扫描）<br>-> BLoC Cubit 引擎层（`action_game_cubit.dart` 爆发动作检测 `x + y + z > 30.0` 与 `100ms` 触觉震动；`hide_and_seek_cubit.dart` 方位角寻路）<br>-> 多环境后端（Firebase + Next.js 13 + dev/staging/prod 多 Flavor 架构） | 1. 用极其稳健的向量幅值阈值（`x + y + z > 30.0`）叠加 `100ms` 节律震动实现零延迟爆发运动判定，避免复杂云端推理崩溃。<br>2. 在 48 小时内构建了包含 10 个独立领域包的 Domain-Driven 工程结构（`analytic_`, `authentication_`, `database_`, `storage_`, `notification_repository`）。<br>3. 利用罗盘与 GPS 将 Kaapelitehdas 电缆厂会场变为实景体感寻宝赛场。 | 爆发阈值：`x + y + z > 30.0` m/s^2 聚合加速度。<br>触觉反馈周期：`100 ms` 定时震动脉冲反馈。<br>工程完成度：48 小时内交付含 10 个领域仓库模块的生产级代码（末次提交 2023-11-12）。 | 1. 现场演示者手持设备奔跑与高频率甩臂冲刺，触发实时的罗盘寻路指引与 100ms 触觉节奏告警。<br>2. 会场实地扫描隐藏二维码校验点即时刷新多人积分榜。 | Mankeli Solutions Oy 团队：Jesse Lappalainen (`JareCoder`)、Juho Torkkeli (`JTorkk`)、Aku Paananen (`AkJkSenpai`)、Onnimanni Hannonen (`O-Hannonen`) 与 `Hylje5000`。 | 职业级跨端工程交付稳定性叠加真实离座体感玩法。项目在极高完成度下让评委与玩家真正离开座椅动起来，精准击中华为鼓励青少年减少久坐的核心命题。 | 1. 黑客松高频运动场景中，确定性的物理阈值（`x + y + z > 30.0`）配合 100ms 触觉震动往往比脆而不稳的黑盒模型更有现场感染力。<br>2. 务必交叉核对代码库提交年份与作者官方履历，杜绝年份与邻近非获奖项目的错误混编。 | https://github.com/Mankeli-Software/junction2023<br>https://www.jemlap.fi/projects | L1: 经获奖团队开源 GitHub 仓库 (`Mankeli-Software/junction2023`) 与作者个人作品集 (`jemlap.fi/projects`) 双重实证 |
| junction-2021 | Junction 2021 | 2021 | Helvar | Brighter Spaces: Intelligent Lighting | IoT & Hardware / Smart Building Sensor Networks & Floorplan Spatial AI | 基于楼宇红外（PIR）运动与音频时序日志自动还原未测绘传感器在建筑平面图上的安装坐标（"Where are all the devices?"）、人员动线追踪或地下车库行为识别。 | helvar-lumenloop3-2021 | Lumen Loop 3.0 | Helvar 赛道冠军 🥇 兼全场总决赛 Top-10（200+ 项目中脱颖而出） | 面向商业楼宇智慧照明的大规模传感器自动配准与空间拓扑匹配系统（覆盖 5 座 Helvar 真实楼宇数据集）。将异步传感器事件流按 `5s` 离散量化对齐到 `pd.date_range` 二值激活矩阵（`CombinedCorrelator`），基于与已知锚点设备的加权皮尔逊相关性（`scipy.stats.pearsonr`）预训练生成 `.pickle` 站点模型，并通过 Flask 提供 `64 px` 瓦片平面图点位推荐 Web 界面，将繁琐的现场人工调试工作流缩减大半。 | Python, `pandas`, `numpy`, `scipy` (`pearsonr`), `Pillow` (`ImageDraw`), Flask, Leaflet/Tile 瓦片地图前端 (`TILE_SIZE = 64`), 预训练 `.pickle` 模型 | 异步楼宇时序数据（`deviceid`, PIR 事件）<br>-> 离散时间桶量化（`df.timestamp.dt.floor` `5s` 切片）<br>-> 加权相关性推断引擎（`CombinedCorrelator` 生成 Top-K 锚点候选排序，`offload_tmp_data()`）<br>-> 人机协同配准端（Flask `/tiles/<z>/<x>/<y>` 与 `/recommendations/<id>`） | 1. 放弃花哨的数据看板，精准锁定电工安装千百盏智能灯具时最昂贵的“MAC ID 与平面图坐标人工测绘对照”痛点。<br>2. 将 5 座楼宇的全量矩阵计算离线预训练成 `.pickle` 并卸载临时张量（`offload_tmp_data()`），确保演示时毫秒级响应。<br>3. 采用 Top-K 推荐标注 + `64 px` 瓦片地图供工程师确认，巧妙规避对称走廊导致的绝对坐标回归误差。 | 时间对齐粒度：`5s` 二值激活时间桶（`time_buckets_config`）。<br>地图瓦片规格：`TILE_SIZE = 64` 像素金字塔瓦片（`site_1`..`site_5`）。<br>赛事战绩：全场 Top-10 决赛入围（200+ 项目；Helvar 赛道共 14 队立项、11 份完整提交）。 | 1. Web 前端点击任意未定位灯具 ID，平面图立即平移聚焦并高亮相关性最高的前几处物理走廊建议坐标。<br>2. 同屏展示 Pillow 渲染的绿色（`#50ff50`）锚点基准与预测目标坐标校验对比图。 | Elizaveta Lebedeva (`LizaLebedeva`, 数据科学/建模), Denys Kovalenko (`deniskovalenko`, 信号后端 — 2019 Helvar 卫冕冠军班底), Carlos Bentes (`cbentes`, 瓦片地图空间 Web 架构师)。 | 对工业部署成本的极致共情。两届元老在 2019 年跑通单节点 60GHz 雷达控制后，2021 年直击 Helvar 规模化部署中最耗人工的“Day-0 配准痛点”，用可解释皮尔逊共现算法交付了生产可用工具。 | 1. B2B 工业物联网赛题中，解决“现场部署配准与运维成本”的方案往往比纯前端监控面板更容易拿下高分。<br>2. 空间存在几何对称模糊时，采用“人机协同 Top-K 候选推荐 UI”远比强行输出单点坐标可信。 | https://github.com/LizaLebedeva/junction-2021<br>https://elizavetalebedeva.com/tag/junction/<br>https://www.youtube.com/watch?v=dX27x6s6wl4<br>https://hackjunction.medium.com/junction-2021-intelligent-lighting-as-the-engine-for-brighter-spaces-1926e69eed6b | L1: 经获奖团队开源仓库 (`LizaLebedeva/junction-2021`)、作者博客、演示视频与 Medium 官方报道严格验证 |
| junction-2021 | Junction 2021 | 2021 | CGI x KONE | Sky(scraper)-is-the-limit | IoT & Hardware / Industrial Predictive Maintenance & Smart Wearables | 双轨独立评审：(1) 面向通力电梯工单建议（SAR）的最高预测性能与最强可解释性模型（`F2` 重召回均衡误报）；(2) 面向高危现场维保的跳出框架（Out-of-the-Box）穿戴式硬件构想。 | cgi-kone-elevai-2021 | ElevAI (Team Glados) [同题硬件协同奖: S.H.I.E.L.D] | CGI x KONE “最佳性能与可解释模型”冠军 🥇 兼全场总决赛 Top-10 [同赛题颠覆构想奖: S.H.I.E.L.D] | 针对通力电梯全球预测维保误报问题的可解释工单过滤与 AR 远程预检系统（原始派单中含 13% 无需上门的无效工单）。团队运用 `ray.tune`、`HyperOptSearch` 与 `AsyncHyperBandScheduler` 对 XGBoost/LightGBM/CatBoost/RandomForest 进行自动化调参并严格锚定 `f2_score` 指标，结合分组误差边界分析（Groups 0–3）与低置信度 AR 复核闭环（同期穿戴获奖方案 *S.H.I.E.L.D* 在智能安全帽内集成照明、AR 相机、语音识别与手势交互）。 | Python, `ray.tune`, `HyperOptSearch`, `AsyncHyperBandScheduler`, `XGBoost` (`binary:logistic`), `LightGBM`, `CatBoost`, `RandomForest`, `f2_score`, PCA/t-SNE 分组误差诊断, AR 远程预检工作流 | 通力电梯工单数据集（87% 真实维修 vs 13% 无效上门）<br>-> 子群噪声审计（Groups 0–3 PCA/t-SNE 分布诊断）<br>-> Ray Tune HyperOpt 优化（`f2_score` 召回加权）<br>-> 低置信度 AR 现场预检与工程师全球回流标注 | 1. 对不同设备子群（Groups 0–3）做误差与特征极限审计，坦诚揭示数据不可约噪声上界而非刷高表面精度。<br>2. 将优化目标锚定为惩罚漏修风险的 `f2_score`，彻底避免“全部预测维修”的作弊高分模型。<br>3. 把模型低置信度样本无缝转接给 AR 远程协同复核，形成业务闭环。 | 朴素基线：`F2 = 0.92299`, `Accuracy = 0.70586`。<br>ElevAI 模型：**`F2 = 0.926601`**, **`Accuracy = 0.737212`**（精准过滤无效工单，准确率提升超 3.1 个百分点且未牺牲 F2 召回）。<br>数据占比：`87%` 有效 (`class 1`) vs `13%` 误报 (`class 0`)；CGI 两赛道共约 `30` 支队伍。 | 1. 大屏清晰对比过滤 13% 无效上门派单前后为一线电梯工程师释放的巨额高危工时。<br>2. 基于 PCA/t-SNE 与分组置信区间的诚实诊断图表，赢得 KONE 导师 Jaakko Uusitalo 高度赞赏。 | Team Glados：Ville Toiviainen (`Villux`) 与 Andreas Urbanski (`nardeas`) — 2017/2018 两届 Junction 全场总冠军核心成员。*(注：同题 Out-of-the-Box 智能头盔奖得主 `S.H.I.E.L.D` [L2] 具体队员名单未公开。)* | 工业工程诚实度与业务指标精确对齐。面对存在特征缺失的传感器子群，Team Glados 没有吹嘘虚假高分，而是用 `f2_score` + AR 人机 pre-check 将模型弱点转化为可靠的安全防线。 | 1. 工业维保赛题切忌盲目刷高 Accuracy，必须对齐防止安全漏报的 `f2_score` 等业务代价函数。<br>2. 用 PCA/t-SNE 诚实标出不可约数据噪声区间并用 AR 复核兜底，比盲目拟合更有高级工程质感。 | https://github.com/teamglados/elevai<br>https://vimeo.com/648187179<br>https://www.cgi.com/fi/fi/blogi/junction-2021-hackathon-highlights<br>https://en.wikipedia.org/wiki/Junction_(hackathon) | L1: 经获奖团队开源仓库 (`teamglados/elevai`)、Vimeo 演示与 CGI 官方赛后报告验证 |
| junction-2020 | Junction 2020 | 2020 | OP Financial Group | Finance Challenge (Junction 2020 Connected) | IoT & Hardware / Spatial Mobile Computing (ARKit) & Embedded UX | 技术创新性、物理-数字空间交互体验、原型完整度与远程赛制下的用户震撼度。 | op-saavi-2020 | Saavi – Healthy Finance | Junction 2020 Connected 全场总冠军 🏆 | 在疫情远程举办的 Junction 2020 Connected 中凭借“物理实物 × AR 空间交互”逆势夺得全场总冠军的智能财务伙伴。应用调用原生 iOS `ARKit` 空间视觉识别实体 OP 银行卡（`ist_card.arreferenceimage`），配合屏幕与空间轻弹手势速度判定（`abs(v) > 0.03`）实时在实体卡上方悬浮渲染多维订阅消费热图，并结合 Docker 化 `scikit-learn` `LogisticRegression` 微服务实时预测周期扣费风险。 | Swift (iOS), `ARKit` (`ARReferenceImage`), `Alamofire`, `SnapKit`, `Nuke`, `RxSwift`, `RxCocoa`, `AnimatedGradientView`, `FittedSheets`, Python `Flask`, `scikit-learn` (`OneHotEncoder`, `LogisticRegression`), Docker | 实体 OP 银行卡 (`ist_card.arreferenceimage`) -> 原生 iOS `ARKit` 位姿跟踪与轻弹速度触发（`abs(v) > 0.03`）<br>-> RxSwift 响应式三维面板<br>-> Docker化 Flask 服务 (`/user/subscription_prediction/<id>/`)<br>-> `scikit-learn` `LogisticRegression` | 1. 在线下焊板受限的疫情远程赛制下，巧妙借力物理赞助商实物（实体 OP 银行卡）作为 `ARKit` 视觉锚点。<br>2. 服务端使用容器化 `OneHotEncoder` + 逐服务平衡回归（`class_weight='balanced'`, `C=1e-2`），保障微服务毫秒级启动且绝不卡顿 AR 体验。<br>3. iOS 客户端与 Flask 推理后端彻底解耦并行开发。 | 手势触发阈值：`abs(v) > 0.03` 轻弹动作识别。<br>机器学习超参：`LogisticRegression(max_iter=1e7, class_weight='balanced', C=1e-2)`（基于 `new_sub.csv`）。<br>赛事最高荣誉：Junction 2020 Connected 全场总冠军。 | 1. 手机摄像头一扫桌面上的实体 OP 银行卡，卡面瞬间“生长”出随卡片视角旋转的立体财务健康浮动看板。<br>2. 手指轻弹即可消解冗余订阅并实时弹出下月周期扣费预测。 | Alexander Zimin (`azimin`, iOS/ARKit), Anton Lebedev (`antoleb`, Python Flask/ML), Andrey Krylov (`andreykr.com`, UX 设计), Andrey Volodin, Egor Petrov。 | 线上赛制中的“物理实物破壁效应”。当其余队伍都在提交纯网页表格与看板时，*Saavi* 利用每张桌面都有的实体银行卡和苹果 `ARKit` 打造了堪比物理外设的现场魔术交互。 | 1. 即使在纯软件或远程赛道，若能围绕赞助商实体物料构建 `ARKit`/计算机视觉锚定交互，依然能打出极具辨识度的空间硬件降维打击。<br>2. AR 演示端的后端推理模型务必保持轻量化容器设计。 | https://github.com/antoleb/saavi_back<br>https://github.com/azimin/MoneyMustBeFunnyAkaJunction2020Backup<br>https://www.andreykr.com/media<br>https://www.youtube.com/watch?v=Zc7ce9MxTNg<br>https://en.wikipedia.org/wiki/Junction_(hackathon) | L1: 经两大开源 GitHub 仓库 (`saavi_back` 与 iOS 客户端备份)、维基百科与作者官网严格验证 |
| junction-2019 | Junction 2019 | 2019 | Helvar & VTT | Making Spaces Brighter with Radar Technology | IoT & Hardware / Millimeter-Wave Radar & Closed-Loop Actuators | 基于 VTT 60 GHz 二维成像雷达与 24 GHz 生命体征雷达结合 RGB 真值估计空间占座率与状态，并实时逆向调控 Helvar DALI 智能灯具。 | helvar-vtt-lumenloop-2019 | LumenLoop | Helvar & VTT 赛道总冠军 🥇 | 两人战队打造的全球首个 60 GHz/24 GHz 毫米波雷达到商用 DALI 智能灯具闭环控制原型。直连现场以太网 RabbitMQ AMQP 总线（`10.84.110.2`）零拷贝消费 FlatBuffers 二进制流（`Vtt60Processed.Sample`），利用自适应去噪与在场人数阈值（`diff/max > 0.13`）分级换算照度，再经 `pyserial==3.4` 串口下发十六进制查找表指令直接点亮并调节物理灯具 `EC22`（`00`..`FE` 亮度与 `6500K`–`2700K` 色温），配合 React 看板与 Elasticsearch 存储。 | VTT 60 GHz FMCW 雷达, VTT 24 GHz 生命雷达, RabbitMQ AMQP (`10.84.110.2`), FlatBuffers (`Vtt60Processed.Sample`), Python, NumPy, `pyserial==3.4`, Helvar DALI BLE Mesh USB 网关 (`EC22`), React (`Demo.js`), Elasticsearch | VTT 60/24 GHz 毫米波雷达 -> 以太网 RabbitMQ (`radar60`/`radar24` FlatBuffers)<br>-> `live/Streamer60.py` 在场人数估测 (`diff/max > 0.13`)<br>-> `pyserial` DALI BLE Mesh 十六进制映射 (`EC22` 亮度/色温)<br>-> React 监控端 + Elasticsearch | 1. 拒做离线雷达绘图 Demo，打通了从底层射频流解析到真灯具 `EC22` 物理调光变色的全闭环控制。<br>2. 设计科学人体工学映射表（0 人待机 `5% / 6500K` -> 1 人 `20% / 5750K` -> 2 人 `30% / 4850K` -> 3+ 人 `60% / 3450K`）。<br>3. 使用 FlatBuffers Zero-Copy 对接 NumPy 数组以稳定接住 `100 Hz` 高频雷达帧率。 | 60 GHz 雷达参数：水平 `160°`、距离分辨率 `5 cm`、角分辨率 `3.5°`、微动精度 `<700 nm`（`180x110` @ `100 Hz`）。<br>24 GHz 雷达参数：水平 `80°`、距离分辨率 `60 cm`、微动 `1–5 um`。<br>控灯查表与触发：31 级调光 (`00`..`FE`)、39 级色温 (`6500K`–`2700K`)；检测阈值 `diff/max > 0.13`。 | 1. 评委走入 60 GHz 雷达探测锥范围的瞬间，桌台上的真实 Helvar 商用灯具 `EC22` 顺滑地从 6500K 极冷待机切换为温润明亮的会议照明。<br>2. 浏览器同步呈现实时雷达极坐标点云去噪热力图。 | Denys Kovalenko (`deniskovalenko`, 信号与串口控制) 与 Elizaveta Lebedeva (`elizavetalebedeva.com`, 建模与前端) — 2 人全栈硬件精锐，2021 年再次夺冠 Helvar。 | 彻底闭合物理控制回路的硬核实力。当多数队伍仅用公开 CSV 训练离线分类器时，两人战队现场吃透 AMQP+FlatBuffers+串口 DALI 协议，让雷达真实“指挥”了展台硬件。 | 1. 只要主办方展台摆有真物理执行器（灯具/充电桩/机械臂），务必亲手接通串口或 API 实现真机闭环控制。<br>2. 面对高帧率二进制射频/事件流，及早采用 FlatBuffers 零拷贝解包避免 Python 主线程阻塞。 | https://github.com/deniskovalenko/junction2019<br>https://elizavetalebedeva.com/tag/junction/<br>https://medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f | L1: 经获奖团队开源代码库 (`deniskovalenko/junction2019`)、作者博客与 Junction 官方 Medium 获奖名录验证 |
| junction-2019 | Junction 2019 | 2019 | Aalto University (AYY) | Smart Signage - For Students by Students | IoT & Hardware / Edge Embedded Kiosk, PIR & Touchless CV | 围绕 AYY 约 2,600 套学生公寓楼道场景设计智慧交互电子屏形态，并深度融合建筑暖通、水电及网络等物联网运行数据。 | aalto-ayyhello-2019 | AyyHello! (`ayyHello`) | 阿尔托大学学生会 AYY 赛道冠军 🥇 | 面向 AYY 2,600 套学生公寓（~3,500 住户）楼道打造的无接触防损智能引导屏原型。以树莓派为核心中枢，通过硬件级上升沿红外中断（`RPi.GPIO`, `PIR_PIN = 11`, `LED_PIN = 3`）感知行人靠近自动唤醒系统，随后调用 USB 摄像头与魔改版 `MobilePose-PyTorch`（`resnet18`, `224x224`）执行连续 10 帧防抖过滤的手势识别（`L`/`R`/`U`），经本地 Flask HTTP 接口（`http://10.42.0.157:5000/dir`）调控展示实时楼宇水电能耗、HSL 公交与互动小游戏的 React 终端。 | Raspberry Pi (Linux, `RPi.GPIO`), 热释电 PIR 传感器, USB 摄像头 (`--camera 0`), `PyTorch 1.0.0` (`MobilePose-PyTorch` `resnet18`), `OpenCV 3.4.2.17`, Python `Flask` + `flask_cors`, React `16.12.0`, Material-UI `4.6.1` | PIR 硬件中断 (`PIR_PIN = 11`, `LED_PIN = 3`) -> 唤醒摄像头 (`--camera 0`)<br>-> `MobilePose-PyTorch` (`resnet18`, `224x224`, 10 帧消抖)<br>-> `POST /dir` Flask 服务 (`analysis.py` 楼宇能耗 CSV)<br>-> React 看板 (`PublicTransport`, `Sustainability`, `Game`) | 1. 预判公共楼道触控屏易损坏/卫生隐患，坚定采用 PIR 自动唤醒 + 隔空姿态手势实现免触控操作。<br>2. 不盲目引入沉重的时序 3D-CNN，仅凭简洁有效的“连续 10 帧一致消抖”彻底消除现场杂乱人群引起的画面误翻页。<br>3. 将 GPIO 硬件、PyTorch CV 与前端解耦为本地 HTTP 微服务，保障 5 名成员零冲突并行联调。 | 模型输入尺度：`224x224` (`--inp_dim 224`) `resnet18` 骨架。<br>动作防抖窗口：连续 `10` 帧稳定判定输出 `L`/`R`/`U` 控制指令。<br>部署覆盖场景：针对 `2,600` 套学生公寓解析 `SMT8-12_*.csv`（`;` 分隔）真实楼宇水电热数据。 | 1. 评审走近原型展台瞬间触发树莓派硬件 `PIR_PIN = 11` 中断并点亮 `LED_PIN = 3` 唤醒大屏。<br>2. 隔空向左/向右/向上挥手平稳切换实用公交时刻表、楼宇节能图表及隔空体感小游戏。 | Mari Porko (`mariporko`), Harri Rahikainen (`HRahikainen`), Jesse Tolvanen (`JZNT`), Satria Sutisna (`satriasutisna`) 与 `smirq`（5 人团队）。 | 极高校园场景实用性与稳健的嵌入式消抖工艺。相比孤立枯燥的传感器后台曲线，把能耗警示包装进“起床看公交+顺手玩一局”的日常刚需并做到隔空稳控。 | 1. 现场人群密集的 CV 交互Demo中，简单的“N 帧一致消抖滤波”是保障零误触的最有效工程护城河。<br>2. 树莓派硬件 GPIO 脚位监控与重量级 PyTorch 模型拆进程 HTTP 通信可大幅加速联调。 | https://github.com/mariporko/junction2019<br>https://github.com/HRahikainen/junction2019<br>https://medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f<br>https://www.aalto.fi/en/news/student-union-looks-for-creative-ideas-for-their-information-channels-from-junction | L1: 经获奖团队 GitHub 开源仓库 (`mariporko/junction2019`)、阿尔托大学新闻与 Medium 官方名录验证 |
| junction-2018 | Junction 2018 | 2018 | Intel | Innovative Applications With Bluetooth Mesh | IoT & Hardware / Bluetooth Mesh Gateways, Edge Triage & Wearables | 在物联网边缘网关上构建充分利用 Bluetooth Mesh 无线传感器网络能力的智慧应急、照明、安全或智能徽章应用。 | intel-helpio-2018 | Help.io / Team Health.io | Intel 赛道第一名 🥇 + IoT 大赛道总冠军 🏆 + 全场总榜亚军 🥈（300+ 项目中列第 2） | 彻底断网可用的灾区多伤员生命体征分诊与 Bluetooth Mesh 自组网呼救系统。前端通过两枚 Suunto Movesense 胸带传感器以 BLE 采集心率与 R-R 间期并传入 iOS 12 客户端内置分诊状态机（`lowestHRBound = 60.0`、`highestHRBound = 110.0`、`highestRRMultiplier = 2.0`），一旦危急立刻向本地 Intel NUC 边缘网关发起触发请求（`10.100.5.16:3000/{bluetoothId}/critical`），经 NUC 上实验性 `BlueZ meshd-ingas` 与 `nRF51_dongle` 广播至 4 块基于 Zephyr OS 的 PHYTEC `reel_board` 救援电子墨水屏徽章，全程零互联网依赖。 | Suunto Movesense BLE, iOS 12 / Swift (`Movesense SDK`, `AsyncDisplayKit`, `PromiseKit`, `Bond`, `SwiftyJSON`, `Alamofire`, `ScrollableGraphView`), Intel NUC (Linux, `BlueZ meshd-ingas`, `ell 0.13`, `org.bluez.mesh1`), `nRF51_dongle` (`hci_uart`), 4x PHYTEC `reel_board` (`Zephyr OS mesh_badge`, 模型 `0x0000` / `0x1000` / `0x1102`) | 伤员 Movesense (`175030001053` / `175030000988`, `HR_PATH`)<br>-> iOS 12 本地危重分诊器 (`heartRateHistory >= 15`)<br>-> HTTP POST `10.100.5.16:3000/{id}/critical`<br>-> Intel NUC BlueZ `meshd` + `nRF51_dongle`<br>-> 4 块 PHYTEC `reel_board` Zephyr Mesh 电子徽章 | 1. 将成熟商业外设读取（iOS Movesense BLE SDK）与极早期实验性 `BlueZ meshd` 驱动拆解在轻量 HTTP 网关（`10.100.5.16:3000`）两侧，避免驱动死锁。<br>2. 明确隔离预热丢弃帧（`discardCount = 5`）并留出舞台现场可控触发心率窗口（`60`–`110` BPM）。<br>3. 严格复用 Intel 官方 `Junction2018_Support` 标准模型（`0x0000` Vendor、`0x1000` OnOff、`0x1102` 温度传感 `0x2a1f`）。 | 硬件配比：Intel 现场提供 8 套套件（每套 1x NUC + 1x `nRF51_dongle` + 4x `reel_board`）；Movesense 全场共 26 支队伍提交。<br>分诊代码常量：`discardCount = 5`、`heartRateHistory >= 15`、`lowestHRBound = 60.0`、`highestHRBound = 110.0`、`highestRRMultiplier = 2.0`。<br>赛事排名：Intel 第一 + IoT 赛道第一 + 全场总亚军（300+ 项目 / 11 强决赛圈）。 | 1. 在完全切断 Wi-Fi 外网的现场环境下，演示者心率脉冲跨越 threshold 瞬间通过 Bluetooth Mesh 点亮多块分布式 `reel_board` 墨水屏徽章并标注扇区患者编号（`0x0001` / `0x0002`）。<br>2. iOS 端基于 `ScrollableGraphView` 丝滑绘出双伤员实时心率与 R-R 波动曲线。 | 拉脱维亚大学计算机学院战队：Austris Cīrulnieks、Mārcis Nīmants (`mnimants`)、Elvijs Viļķels、Aigars Cibuļskis 与 Dāvis Mednis *(其中 4 人曾凭 ReCover 摘得 2017 Movesense 冠军)*。 | 极高工程成熟度的异构硬件隔离架构 + 震撼的无网救灾实测表现。团队将 iOS 稳健感知无缝切入 Intel 最前沿未定型的 `meshd-ingas` 协议栈，精准契合官方“真正用活蓝牙 Mesh 能力”核心期待。 | 1. 面对主办方极具实验性的底层通信套件（如初期 BlueZ Mesh），用极简 HTTP 桥接层把应用逻辑隔离出来是 48 小时零崩溃关键。<br>2. 赛前先啃透支持仓库里的 D-Bus 网关与标准 Mesh Model 操作码（`0x8202`, `0x8231`）。 | https://github.com/mnimants/junction2018<br>https://github.com/intel/Junction2018<br>https://github.com/feri/Junction2018_Support<br>https://www.movesense.com/news/2018/11/movesense-shined-in-junction-hackathon/<br>https://eztf.lu.lv/en/about-us/news/detail-view/t/98941/ | L1: 经冠军开源仓库 (`mnimants/junction2018`)、Intel 官方支持仓库、Movesense 官方战报与拉脱维亚大学公告证实 |
| junction-2018 | Junction 2018 | 2018 | Ensto | Teach EV Chargers New Tricks | IoT & Hardware / Edge Vision, Smart EV Chargers & Mobility | 基于现场真实商用电动车充电桩硬件开发板并深度集成 EnstoFlow IoT REST API 与 OCPP 控制协议，实现具商业闭环的创新出行功能。 | ensto-oneiro-2018 | Oneiro (Team Glados) | 全场总冠军 🏆 (€20,000 现金大奖) 兼 Ensto 出行赛道冠军 🥇（Ensto 共 14 支参赛队） | 将全芬兰私家电动充电桩共享化的“充电桩 Airbnb”与无感车牌识别硬件系统。树莓派 + PiCamera 在 `systemd` 守护下每隔 `0.5s` 抓拍 `640x480` 画面送入 Docker 化 `openalpr:16.04` 车牌识别服务（欧盟/芬兰 `eu`/`fi`，阈值 `confidence >= 75`），通过 Sanic 服务向 `EnstoFlow` REST/OCPP 下发 `spot_enable()` 指令直接驱动真实的 **Ensto Chago (`JunctionEVB1`)** 硬件充电桩上电亮灯，同时结合 React Native App 与 Telia 蜂窝基站 `Mapbox GL` 城市需求热力图形成完整商业闭环。 | 树莓派 + PiCamera (`systemd` `photographer.service`), Docker `openalpr:16.04`, Python 3 `Sanic` (`8000`), `EnstoFlow` REST API v1 (`JunctionEVB1` OCPP `A -> C`), React Native (`sdk-31.0.0`, Expo `^31.0.2`, Redux-Saga), `Mapbox GL JS v0.51.0` (Telia 移动人流), Terraform + AWS (`t2.nano`, ELB, ECR, S3, CloudFront, Route53) | 树莓派相机 (`0.5s` `640x480`, `2s` 超时)<br>-> Sanic 服务 + `openalpr:16.04` Docker (`conf >= 75`, `top_n=5`)<br>-> `EnstoFlow` OCPP `spot_enable()` 真实开关 `JunctionEVB1`<br>-> Expo 客户端 + Telia `Mapbox` 选址热力图 | 1. 通过边缘光学识别取代手机繁琐扫码，实现“驶入车位即无感鉴权开始供电”。<br>2. 不满足于单纯接通继电器，更以 Telia 电信蜂窝人流大数据热力图科学论证充电桩 P2P 选址与收益模型。<br>3. 为边缘节点设置 `systemd` 进程守护与 `2s` 强超时机制，保证无线会场丢包不死机。 | 抓取与识别阈值：`0.5s` (2 FPS) 采集、`640x480`、`2s` 请求超时、`top_n = 5` 且置信度 `>= 75` 自动开闸。<br>比赛战果：**全场总冠军 €20,000**（1,200–1,300 参赛者、300+ 项目）+ Ensto 赛道第一名（共 14 支参赛队）。 | 1. 上台演示将汽车牌照移至树莓派摄像头前，瞬间识别并用 OCPP 指令将现场 Ensto Chago 硬件（`JunctionEVB1`）状态灯转为充电中。<br>2. 大屏直观定位赫尔辛基大区电动车热力需求盲区。 | Team Glados（阿尔托大学校友与芬兰工程师）：Teemu Taskula (`Temzasse`)、Andreas Urbanski 与 Ville Toiviainen (`Villux`) — 实现罕见的 **2017 与 2018 连续两届 Junction 全场总冠军蝉联**。 | 真实工业设备控制 + 无可挑剔的商业闭环。Ensto 软件总监 Ville Parviainen 盛赞团队不仅极其流畅地打通了 Ensto 真实接口，更把共享经济定价与选址算得明明白白。 | 1. 面对工业硬件外设，用边缘视觉自动化消除用户的二次物理操作极具路演杀伤力。<br>2. 树莓派边缘采样脚本务必极简与强超时（`2s` + `systemd`），繁重 Docker OCR 放在稳健服务端。 | https://github.com/teamglados/oneiro<br>https://vimeo.com/302650304<br>https://talotekniikka-lehti.fi/oneiro-voitti-junction-2018-hackathonin/<br>https://mobiili.fi/2018/11/25/junction-hackathon-espoossa-paattyi-latauspisteiden-airbnbn-voittoon-sama-tiimi-voitti-kilpailun-viime-vuonnakin/ | L1: 经冠军开源仓库 (`teamglados/oneiro`)、演示视频与多家芬兰权威科技媒体确认 |
| junction-2018 | Junction 2018 | 2018 | Future Cities Track | Future Cities Challenge | IoT & Hardware / Assistive Dual-MCU Hardware & Custom CAD | 城市适老化无障碍出行痛点切合度、完整可穿戴硬件工程交付、现场易用性与可扩展潜力。 | futurecities-guideme-2018 | GuideMe | Future Cities 赛道总冠军 🥇 (€1,000) 兼全场总榜第 4 名（300+ 项目中列前 4） | 从零手工打造（含 3D 打印结构件、双单片机固件及看护人后台）的视障/长者智能导盲手杖手柄硬件。由 Wemos `ESP8266` 从 Google Maps Directions PHP 后端拉取路径导航方位角，经 `115200 baud` 串口（`pins 0/2`）送入 `BBC micro:bit`；后者结合片上地磁传感器实时比对行人朝向偏差，通过顶置 5x5 LED 矩阵箭标与 `pin 1` 触觉震动/蜂鸣提示零屏幕引导老人行走。 | `BBC micro:bit` (Cortex-M0, 磁力计, 5x5 LED, MicroPython `micro.py`), `Wemos ESP8266` (Arduino C++ `guideme_arduino_wifi_node.ino`), SolidWorks CAD (`guideme_handle.SLDPRT` / `.STL` 3D 打印件), PHP (`web/back.php`, `web/front.php`), Google Maps Directions API, HTML / jQuery / AJAX | 照护人网页端 (`web/front.php`, Google Maps)<br>-> `Wemos ESP8266` HTTP 拉取 (`guideme_arduino_wifi_node.ino`)<br>-> UART `115200` 串口 (`pin 0`/`2`)<br>-> `BBC micro:bit` 磁罗盘航向计算 (`micro.py`) -> 5x5 LED + `pin 1` 震动/蜂鸣 | 1. 践行严谨的硬件职责分工：`ESP8266` 专注无线 HTTP 网络通信，`micro:bit` 专注地磁姿态解算、LED 箭头与 `pin 1` 触觉执行，避免单颗芯片协议栈冲突。<br>2. 在赛场直接完成 SolidWorks 参数建模（`guideme_handle.SLDPRT`）与 3D 打印壳体装配，交付真正握持感良好的实体手杖配件。<br>3. 为照护家人配置实时 GPS 位置跟踪与远程目的地设置网页端。 | 串行接口指标：`115200 baud` UART（`pin 0` / `pin 2`），触觉执行输出（`pin 1`）。<br>结构工艺：开源仓内含完整 SolidWorks 与 `.STL` 3D 打印把手设计文件。<br>赛事排名：**全场第 4 名**（300+ 项目、~1,300 参赛者）+ Future Cities 赛道第 1 名 (€1,000)。 | 1. 现场转动 3D 打印智能手杖手柄时，顶部嵌装的 `micro:bit` 5x5 LED 箭头随地磁方位平滑偏转，并在偏离方向时发出清晰触觉脉冲预警。<br>2. 看护端网页实时重规划步行转弯节点并下发新航向。 | 西班牙瓦伦西亚理工大学精锐五人战队（Makers UPV）：Jaime Laborda Macario、Iván Torres Játiva、Enrique Miralles Dolz、Joaquín Montesinos Muñoz 与 Matías Fernández Patón。 | 令人惊叹的机械 CAD × 双控硬件 × Web 端到端完整度。五位跨专业工程师（电子、核聚变、通信、生物医学）48 小时内连外壳带底层串口驱动一气呵成，征服了芬兰全场评委。 | 1. Wi-Fi 联网由 `ESP8266` 专职承担、传感器与执行器交给另一颗主控经 `115200` 串口联动，可大幅减低黑客松现场调参崩溃率。<br>2. 现场 3D 打印一款严丝合缝的实体结构外壳，产品说服力比裸露杜邦线面包板翻十倍。 | https://github.com/makers-upv/GuideMe<br>https://www.upv.es/noticias-upv/noticia-10627-junction-2018-es.html<br>https://mobiili.fi/2018/11/25/junction-hackathon-espoossa-paattyi-latauspisteiden-airbnbn-voittoon-sama-tiimi-voitti-kilpailun-viime-vuonnakin/ | L1: 经冠军开源仓库 (`makers-upv/GuideMe`)、UPV 官方新闻稿与芬兰科技媒体决赛报道证实 |
| junction-2018 | Junction 2018 | 2018 | Vaisala | Hack the Sauna | IoT & Hardware / Extreme-Environment Multi-Sensor Analytics | 在极端高温高湿桑拿环境下替代传统机械表盘，把维萨拉多维精密传感器遥测转化为直观体感指导与运营调控洞察。 | vaisala-masga-2018 | Make Sauna Great Again (MaSGA) | Vaisala “Hack the Sauna” 赛道第一名 🥇（后续论文发表于 IEEE IECON 2020） | 依托维萨拉工业级多点桑拿传感探头（`Stove1`、`Bench1–3`、`Floor1`）构建的实证模糊评价与双角色温湿舒适度决策引擎。后端通过 Python Google Cloud Functions（`Addono/masga-backend`）拉取 `apigtw.vaisala.com` 温度、相对湿度、比焓（Enthalpy）、二氧化碳及氧气浓度，运用基于现场 22 份真人桑拿调研校准的梯形模糊相似算法（`quadro()`），每 `10s` 向客户端及管理员输出“泼水/开窗通风”或功率调控指令。 | 维萨拉工业传感探头组 (温度/RH/比焓/CO2/O2: `Stove1`, `Bench1–3`, `Floor1`), 维萨拉 API 网关, Python (Google Cloud Functions `main.py`), 梯形模糊相似函数 (`quadro()`), Bootstrap 4.1.3, jQuery 3.3.1 | 5 点维萨拉工业探头 (`Stove1`, `Bench1–3`, `Floor1`)<br>-> 维萨拉 REST API 网关<br>-> GCF Python 评分核心（22 份真人调查校准 `quadro()`）<br>-> 双角色前端面板（每 `10s` 刷新 User / Manager 视图） | 1. 拒绝拍脑袋定温度阈值，直接在真实桑拿房收集了 22 位入浴 10–15 分钟以上用户的舒适度真值样本进行标定。<br>2. 设计梯形模糊相似匹配函数 `quadro()` 量化复杂多物理量偏差（后续扩展发表至 IEEE IECON 2020 论文）。<br>3. 将枯燥传感器指标切分为“浴客直观操作提示（加湿/通风）”与“店长热泵机组边界报警”。 | 真值校准集：`22` 份真人现场桑拿体验调研（每份 `>= 10–15 min`）。<br>遥测刷新：`10s` (`10000 ms`) 轮询 GCF。<br>评分红绿灯阈值：`> 88%` 绿（完美）、`> 75%` 橙（下降）、`<= 75%` 红（较差）；衍生学术论文收录 IEEE IECON 2020。 | 1. 同屏对比晦涩的 CO2 ppm / 比焓数字曲线与简洁直白的“体验 89% 🟢 / 建议开窗”行动指令。<br>2. 一键切换“普通桑拿游客模式”与“桑拿商业运营维护视角”。 | 阿尔托大学等联合科研精锐团队：Siavash H. Khajavi (Aalto 博士后)、Alireza Jaribion (Aalto 研究员)、Adriaan Knapen (`Addono`)、Leila Abiedat 与 Arnab Banik。 | 真实现场实证数据 + 可发表级多传感器融合算法。当一般黑客松队伍在编造“舒适指数”时，该队用现场 22 份真人采样校准模糊数学方程，兼具学术严谨与工业可用性。 | 1. 哪怕在黑客松现场，收集 20+ 份真实人群测试真值也能让传感器融合模型的参数调优立于不败之地。<br>2. 把多探头工业参数直接映射为终端用户的一句话可执行动作。 | https://github.com/Addono/masga-backend<br>https://github.com/Addono/masga<br>https://www.vaisala.com/en/blog/2018-11/winners-vaisalas-challenges-junction-2018-hacked-weather-and-sauna<br>https://www.aalto.fi/en/news/winning-team-hack-the-sauna-experience-to-a-new-level-at-junction<br>https://aaltodoc.aalto.fi/items/44b6d03b-0849-4381-a9e4-300de579f7d3<br>https://youtu.be/rNtnsDjz0vM | L1: 经冠军前后端仓库、Vaisala 官方战报、Aalto 新闻稿与 IEEE IECON 2020 学术归档验证 |
| junction-2018 | Junction 2018 | 2018 | Movesense by Suunto & Stara | Track Anything That Moves / Stara StreetReboot2 | IoT & Hardware / Crowdsourced Infrastructure IMU & Smart City | 基于可编程 Movesense IMU 传感器的实用增值、系统就绪度、交互体验与赫尔辛基城市道路运维（Stara）实际影响。 | movesense-terrainsense-2018 | TerrainSense | Movesense 多赛道联合第一名 🥇 兼赫尔辛基市政 Stara StreetReboot2 亚军 🥈 (€1,000) | 低成本自行车道路面平整度众包巡检硬件方案。团队把一枚 Suunto Movesense 惯性加速度计直接固定在自行车后轴车架（`taka-akseli`）上，骑行时经 BLE 向 Android 手机上传颠簸振动波并捆绑 GPS 生成 GPX 轨迹及 AWS 路面破损热力图，助市政养护精准排雷。赛后成功落地为赫尔辛基市、Forum Virium、HAMK 应用科技大学与 InnoTrafik 等三项多年度市政试点并拓展 AWS Rekognition 视觉识别。 | Suunto Movesense IMU 传感器 (BLE), Android App (GPS + BLE 采集), GPX 空间轨迹, AWS S3 / EC2 路面热力平台 *(赛后试点拓展 AWS Rekognition 视觉识别)* | 自行车后轴 (`taka-akseli`) Movesense IMU -> BLE 传输<br>-> Android GPS 颠簸对齐<br>-> AWS S3 / EC2 城市自行车道破损热力图与 GPX<br>-> 市政养护调度 | 1. 跳出传统“戴在手腕/胸口测人体运动”思维，将 IMU 直接安装到自行车后轴测量高频路面微振。<br>2. 精明绑定双赛道战略（Movesense 硬件 + 赫尔辛基城市养路 Stara 数据），同时赢得硬件厂商与市政机关双重奖金。<br>3. 输出标准 GPX 地理轨迹便于城市 GIS 工程师直接导入地图系统。 | 赛题漏斗：Movesense 共获 26 项最终提交（来自 35 队周六领套件）。<br>市政授奖记录 (`HEL 2019-003563`)：获 Stara StreetReboot2 亚军 €1,000 + Movesense 多赛道组合第一名。<br>商业转化：赛后签署 `3` 项赫尔辛基与 HAMK 真实路测试点项目。 | 1. 自行车骑行路测原始高频震动曲线实时同步渲染出赫尔辛基自行车道红绿破损等级热力图。<br>2. 赫尔辛基市政正式公文与官方复盘演讲 PPT 证实其赛后长期落地价值。 | Ville Saramaa (`vill.dev`) 及北欧联合开发成员 *(后续携手 HAMK 与 InnoTrafik 推动市政试点落地)*。 | 极富商业想象力的硬件跨界打法。一枚几十欧元的体育 IMU 传感器，绑定在共享单车或通勤自行车后轴上便成了低成本高频城市市政道路巡检车队。 | 1. 将赛事通用传感套件与城市级市政基础设施（Stara、交通局）挑战赛题耦合，最容易拿下跨赛道复合大奖。<br>2. 别把 IMU 局限于人类四肢：贴合载具车轴、阀门或机械臂能瞬间摆脱同质化竞争。 | https://www.movesense.com/news/2018/11/movesense-shined-in-junction-hackathon/<br>https://www.movesense.com/wp-content/uploads/2018/12/TerrainSense_Junction_presentation.pdf<br>https://paatokset.hel.fi/fi/asia/hel-2019-003563<br>https://vill.dev/projects/<br>https://unlimited.hamk.fi/teknologia-ja-liikenne/pyoravaylien-kunnon-tutkiminen-sensoriteknologian-keinoin/ | L1: 经 Movesense 官方演讲 PDF、赫尔辛基市政公文 (`HEL 2019-003563`) 与 HAMK 试点文献证实 |
| junction-2018 | Junction 2018 | 2018 | Helvar | The Brain of the Building | IoT & Hardware / Smart Luminaires & Multi-Sensor Vision Fusion | 构建连接楼宇照明传感器网络与环境控制端的中枢“建筑大脑”，优化空间舒适度与异常自动感知能力。 | helvar-ivision-lamp-2018 | IVision Lamp | Helvar “现代建筑智能大脑”赛道冠军 🥇 | 由清华大学与商汤科技联合学生兴趣团队在 42 小时内从零打造的视觉与多传感器融合智能台灯系统。针对智能灯具单纯依赖单点阈值不够聪明的痛点，融合光学视觉感知与多传感器环境信息流以闭环调控实体台灯设备的实时光线输出，击败众多纯算法队为清华大学斩获历史上首个 Junction 挑战赛道冠军（因闭源竞赛性质，公开仓库与量化毫秒/精度指标 `[Not publicly documented]`）。 | 智能台灯实体硬件, 计算机视觉感知管线, 多传感器信息融合中枢, 实时自适应光学调控逻辑 *(详细内部代码与开源仓库未公开)* | 光学视觉摄像头 + 多传感器环境感知信号<br>-> 多传感器信息融合推理算法<br>-> 智能台灯实体灯具光线动态自适应控制 | 1. 用“视觉感知 + 多传感器数据融合”取代孤立被动环境光感应，提升建筑端照明控制的场景理解力。<br>2. 聚焦台灯硬件实物联调，用 42 小时直观物理光线交互验证击败纯 PPT/离线图表方案。 | 开发冲刺时长：`42` 小时（全会场 1,300+ 黑客、46 个赛题竞争）。<br>数据证据边界：官方通稿未公开源代码仓库及定量延迟/精度实测数值 `[L2]`。 | 1. 在 Helvar 展台实测验证环境中，根据多传感器与视觉状态变化动态调控台灯真实照明亮度，获 Helvar 评委现场直接授冠。 | 清华–商汤未来深度学习与人工智能学生科技兴趣团队：袁秀龙（电子系）、郭映雪（电子系）、李鑫（自动化系）与梁丰（微电子与纳电子学系）。 | 跨院系硬核学术底蕴叠加物理实体调光呈现。电子、自动化与微电子跨专业精锐结合深度学习视觉，42 小时内呈现稳定真实的硬件调光效果。 | 1. 面对智能照明/楼宇老牌企业时，“视觉 + 环境传感融合驱动真机灯光响应”往往胜过单纯分析历史建筑能耗 CSV。<br>2. 针对 `[L2]` 媒体报道型获奖项目严格声明开源与数值边界，绝不编造未公开延时指标。 | https://www.tsinghua.edu.cn/info/1173/17718.htm<br>https://www.sensetime.com/cn/technology-new-detail/3606?categoryId=53<br>https://helvar.com/how-to-make-the-light-work-for-you/ | L2: 经清华大学官方新闻网与商汤科技新闻通稿交叉证实 |
| junction-2018 | Junction 2018 | 2018 | Fleetboard (Daimler / Mercedes-Benz) | Trucks X Code | IoT & Hardware / Connected Heavy Vehicle SDK & Fleet Telemetry | 基于戴姆勒 Fleetboard 重卡车载硬件 SDK 读取梅赛德斯-奔驰商用车实时总线与传感器遥测，开发具商用价值的高级监测与车载应用。 | fleetboard-trucksense-2018 | TruckSense | Fleetboard 重卡赛道冠军 🥇（赢取赴德国斯图加特戴姆勒/奔驰总部 3 天全公费技术考察研习） | 在 ~40 小时内基于梅赛德斯-奔驰重卡车载终端与 Fleetboard SDK 打造的实时车队状态监测与机器学习前瞻预测系统。接入卡车真实行驶与总线传感流，通过后端 ML 预测模型研判未来运行工况与潜在异常，并在可视化网页端直观呈现；凭极强商用可执行性击败全场竞争对手获赴德奔驰总部考察奖励（团队开源仓库及定量误差 RMSE/MAE 未在高校公报中公开 `[L2]`）。 | Fleetboard SDK (梅赛德斯-奔驰卡车车载计算机平台), 实时总线遥测流接入, 机器学习预测后台, 图形化 Web 监控端 *(详细模型与仓库未公开)* | 奔驰商用重卡车载终端 / Fleetboard SDK<br>-> 实时车辆传感遥测接入后台<br>-> ML 未来工况趋势预测 -> 车队图形监控看板 | 1. 直面商用货运行业的高昂抛锚代价，不止展示当前状态读数，而是增加基于机器学习的未来运行参数预测。<br>2. 严格遵照 Fleetboard 商业车规 SDK 数据规范开发跨端监控逻辑。 | 开发窗口：约 `40` 小时（自约 10,000 名报名者筛选出的千人规模赛场）。<br>数据证据边界：高校及区域新闻公报未披露源码仓库与具体机器学习误差指标 `[L2]`。 | 1. 流畅展现梅赛德斯重卡实时车载总线健康指标与前瞻运行趋势可视化看板，获邀请赴德国斯图加特与车载终端研发工程师深度共创。 | 西班牙卡塔赫纳理工大学 (UPCT) 与伏林航空 (Vueling) 工程师联队：Pablo Moyano（UPCT 远程信息处理工程）、Enrique Fernández（UPCT）及 2 名 Vueling 软件工程师。 | 车联网专业背景（Telematics）+ 航空高可靠性开发经验精准契合商用卡车需求。以预测性指标抢在故障发生前预警直中物流车队刚需。 | 1. 在车载硬件 SDK 挑战中，叠加“异常/工况前瞻预测”功能往往比纯静态仪表盘更打动主机厂评委。<br>2. 对无公开源码的 `[L2]` 报道案例明确注明证据缺失边界。 | https://www.upct.es/noticias/2018-11-30-premiados-dos-alumnos-de-la-upct-por-resolver-un-reto-tecnologico-para-monitorizar-los-camiones-mercedes<br>https://www.laverdad.es/murcia/cartagena/estudiantes-upct-resuelven-20181202005210-ntvo.html | L2: 经西班牙卡塔赫纳理工大学官方公报与 La Verdad 新闻报道证实 |
| junction-2017 | Junction 2017 | 2017 | STARA / Junction Main Competition | Main Competition & STARA Urban Challenge | IoT & Hardware / Mobile Edge Vision & Smart Infrastructure | 在 Junction 2017 全场 1,500 名选手、13 个大类赛道中角逐技术深度、工程鲁棒性与城市基建落地价值。 | stara-signvision-2017 | Signvision (Team Glados) | 全场总冠军 🏆 (€20,000 现金大奖) 兼 STARA 市政赛道亚军 🥈 | 利用众包手机视觉与 GPS 自动测绘城市交通路标资产的端云协同计算机视觉系统（奠定了 Team Glados 2017/2018 连续卫冕总冠军的技术底座）。手机端 React Native 实时采集影像与经纬度，经高频 `uWs` WebSocket（3000 端口，5000ms 去重冷却）传至后端；先由 OpenCV HSV 红色掩膜与 `scikit-image` 连通域 ROI 滤出有效候选框（`numPixels > 1000`, `30%` 扩边），再送入 CUDA 8.0 Docker + AWS ECS 部署的 `TensorFlow 1.4.0` `32x32x3` CNN（基于 GTSRB `00014` 停车标志训练），即时上云标注城市地图。 | React Native (相机 + GPS), Node.js `uWs` WebSockets (`3000`), `Koa` (`8000`), Python `Flask` (`8080`), `OpenCV` + `scikit-image` (`label`), `TensorFlow 1.4.0` CNN, CUDA 8.0 Docker, Terraform + AWS ECS | 手机摄像头 + GPS (React Native)<br>-> `uWs` WebSocket 与 `Koa` (`5000ms` 去重冷却)<br>-> OpenCV HSV 红域分割 + `scikit-image` ROI (`numPixels > 1000`)<br>-> TensorFlow `1.4.0` `32x32x3` CNN (`Dense(2)`) AWS ECS GPU 部署 | 1. 采用“经典几何色彩分割 (HSV + 连通域) + 极轻量 `32x32x3` CNN”混合架构，避免了直接跑大型检测网络带来的高误报与算力爆炸。<br>2. 在 `uWs` 网关中加入 `5000ms` 同址上报冷却窗，彻底杜绝车辆等红灯时刷爆地图数据库的工程漏洞。<br>3. 全套基础设施采用 Terraform (`aws/*.tf`) 与 CUDA 8.0 Docker 实现一键云端拉起。 | 模型输入与步数：`32x32x3` (`Conv2D(16)` -> `Conv2D(32)` -> `Dense(2)`), GTSRB `00014` 训练 `2,000`/`18,000` steps。<br>候选过滤阈值：`numPixels > 1000` (`30%` bbox 扩边), WebSocket `5000 ms` 冷却去重。<br>赛事体量：夺得 €20,000 全场总冠（1,500 名选手 / 4,000 报名）兼 STARA 第 2 名。 | 1. 现场拿着运行移动端应用的手机扫过测试交通标志，市政道路大屏几乎无卡顿地在对应经纬度落下准确标牌资产点。<br>2. 极快吞吐的 WebSocket 推流配合平稳抗抖动弹窗体验惊艳全场投票。 | Team Glados：Andreas Urbanski、Teemu Taskula 与 Ville Toiviainen — 芬兰阿尔托大学传奇三人组，包揽 2017 与 2018 两届全场总冠军及 2021 KONE 冠军。 | 经典视觉滤波护航轻量深度学习 + 超前 DevOps 工程化意识。用简单稳健的 HSV ROI 提取护航小模型，48 小时交付零宕机的“车载边端感知+地图自动化基建”闭环。 | 1. 在户外强光干扰复杂的移动视觉赛题中，“传统 HSV/形态学过滤 + 轻量级裁剪分类器”比直接拿通用大模型更稳、更省流。<br>2. 移动采图网关务必设置空间/时间去重冷却窗口（如 `5000ms`）。 | https://github.com/teamglados/signvision<br>https://devpost.com/software/glados<br>https://vimeo.com/244507554<br>https://www.uusiteknologia.fi/2017/11/28/junction2017-voittaja-yhdisti-big-datan-mobiiliin/ | L1: 经冠军开源 GitHub 仓库 (`teamglados/signvision`)、Devpost 项目页、视频与芬兰科技媒体报道证实 |
| junction-2017 | Junction 2017 | 2017 | Suunto (Movesense) | Track anything that moves! | IoT & Hardware / Dual-IMU Biomechanics & Rehab Wearables | 围绕可编程 Suunto Movesense BLE 传感器考核场景增值度、功能完备度与用户体验（覆盖健康、运动与通用物联网三大子项）。 | suunto-recover-2017 | ReCover (`DF LAB`) | Movesense 健康赛道总冠军 🥇（赢得 6 枚 Movesense 传感器 + 4 块 Suunto Spartan 腕表） | 面向术后膝关节居家康复患者的双传感 IMU 角度精准测量系统。团队创造性地在患者膝关节上下侧同时固定**两枚同步运行的 Suunto Movesense BLE 传感器**，通过蓝牙低功耗接入 iOS 应用，实时解算胫股关节相对弯曲差分角度并对照康复师目标区间即时提醒，解决居家复健“练不到位或过度屈伸伤骨”核心难题（该原班团队于次年升级融合 Intel 蓝牙 Mesh 夺得 2018 全场总亚军 `Help.io`）。 | 2x Suunto Movesense 可编程传感器 (加速度计/陀螺仪/磁力计), BLE (`movesense-mobile-lib`), iOS 原生应用, 双传感相对关节角差分算法 | 膝上 Movesense + 膝下 Movesense<br>-> 双路 BLE 同步采集 (`movesense-mobile-lib`)<br>-> 实时相对关节屈伸角度差分解算<br>-> iOS 康复训练指导与依从性反馈界面 | 1. 摒弃容易受站姿前倾干扰的单传感做法，跨关节布设**成对双 IMU** 做坐标系差分，得出纯粹的关节夹角变化。<br>2. 由医学博士/导师 Emīls Sjundjukovs 提供真实临床术后角度康复需求背书，拒绝伪健康场景。<br>3. 在 24 支同使用 Movesense 套件的赛道队伍中选准复健刚需切口。 | 赛道竞争度：Movesense 2017 共吸引 `24` 个项目提交（会场共 1,500 名选手）。<br>硬件配置：双传感 IMU 肢体差分方案；获奖奖品 `6` 枚传感器 + `4` 块 Suunto Spartan 智能表。 | 1. 演示人员现场屈伸膝盖，iOS 屏幕上同步绘制高精度关节实时角度弧度变化与康复达标安全绿区提示。<br>2. 用极低成本家用可穿戴套件复刻医院精密测角仪能力。 | 拉脱维亚大学计算机学院 DF LAB 战队：Austris Cīrulnieks、Elvijs Viļķels、Dāvis Mednis 与 Mārcis Nīmants *(医学创意指导 Emīls Sjundjukovs)*。 | 极简巧妙的生物力学参考系差分思路 + 清晰临床路径。用两枚开源惯性模组相减获得稳定关节弯曲角，以物理对称巧思瞬间折服 Suunto 硬件评审团。 | 1. 测量人体关节角度或相对形变时，“跨节点双传感器差分参考”可一键消除身体整体倾斜噪声。<br>2. 硬件选手连续参赛能产生惊人复利：该战队正是凭 2017 双传感打下的 BLE 功底，次年一举攻克 Intel Bluetooth Mesh。 | https://devpost.com/software/recover-pfrq3g<br>https://www.movesense.com/news/2017/11/24-movesense-projects-at-junction-hackathon/<br>https://eztf.lu.lv/par-mums/zinas/zina/t/29783/ | L1: 经 Suunto 官方战报、Devpost 项目库与拉脱维亚大学官方通告严格证实 |
| junction-2017 | Junction 2017 | 2017 | Planmeca Oy | Reshaping the future of dentistry | IoT & Hardware / 3D Dental Imaging & Mobile AR Overlay | 围绕数字化 3D 口腔锥形束 CT 与口扫硬件数据流拓展“虚拟无打扰口腔诊疗”和治疗前置模拟互动体验。 | planmeca-ar-dentist-2017 | AR Dentist | Planmeca 赛道第一名 🥇（13 支专业参赛队中胜出） | 面向未来口腔诊所的实时椅子旁增强现实 (AR) 疗程预览双屏系统（基于 Planmeca 现场 3D 口腔影像数据包开发）。由移动工程+工业三维设计双人精锐打造：牙医可在笔记本端即时微调三维牙齿矫正与治疗参数，受试者面部叠加的移动端实时 AR 面部识别三维口腔效果同步瞬间更新，大幅减缓患者术前焦虑与沟通成本（官方通稿未公开源码仓库及具体 FPS 帧率指标 `[L1]`）。 | Planmeca 3D 口腔三维影像数据包, 笔记本三维参数控制工作站, 移动端实时面部识别 AR 渲染客户端 *(源码仓库未对外公开)* | Planmeca 3D 口腔扫面数据 + 笔记本调参控制器<br>-> 实时参数同步桥<br>-> 移动端人脸跟踪与 3D 口腔 AR 叠加引擎 | 1. 采用“医生端笔记本调参 + 患者端手机沉浸式 AR 照镜预览”双屏协作构型，既保证医学参数精密修改又兼顾患者低门槛感知。<br>2. 跨国 2 人超级配对（计算机物理移动研发 + 工业 3D 造型设计），48 小时内不涉冗杂沟通快速闭环模型精度与手机推流。<br>3. 紧扣“无打扰口腔初诊预览”直击 13 支赛道竞争者核心区隔。 | 赛道竞争规模：健康赛道共 `13` 支参赛队正面挑战 Planmeca 赛题（评委含研发经理 Sakari Kettunen 等高管）。<br>数据证据边界：官方战报未公开 GitHub 代码库及具体 AR 渲染帧率读数 `[L1]`。 | 1. 双端实时演示：在笔记本端拉动三维口腔修复模型滑块，一旁对准人脸的手机屏幕中 3D 齿列叠加特效立刻跟着无延迟重塑变形。 | 跨学科两人精锐战队 AR Dentist：Samuel Laska（斯洛伐克，物理与计算机背景移动开发）与 Linda Ukkonen（芬兰，工业设计 3D 造型硕士）。 | 极致紧密的“3D 工业建模 × 移动实时 AR”二人黄金组合。用令人直观理解的实时照镜口腔变化解决了牙医与患者间百年不变的沟通盲区。 | 1. 医疗/消费类硬件与 AR 赛道中，“工业 3D 美术/CAD 设计师 + 移动研发工程师”的极简二人组往往效率远超臃肿的大队伍。<br>2. “后台精密调控端 + 前台傻瓜 AR 展示端”双机联动路演极其讨喜。 | https://www.planmeca.com/news-and-events/newsroom/2018/planmeca-challenged-hackers-to-reshape-the-future-of-dentistry/ | L1: 经全球口腔巨头 Planmeca 官网 2018 年 1 月官方新闻公告严格证实 |

---

## 2. 深度剖析项目卡片 (21 个字段完整版)

---

### 项目卡片 1: WAVELET (Sensofusion — Radio City)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2025`
- **赛事名称 (event_name)**: `Junction 2025`
- **举办年份 (year)**: `2025`
- **出题机构 (organizer)**: `Sensofusion` (芬兰国防低空反无人机军工独角兽，AIRFENCE 研发商)
- **挑战赛题 (challenge)**: `Radio City` (无线电之城：城市级空间射频电磁波实时传播仿真)
- **赛题类别 (category)**: `IoT & Hardware / Defense & RF Spatial Computing` (物联网与硬件 / 国防与射频空间计算)
- **评审标准 (judging_criteria)**:
  - 基于真实物理规律的三维城市电磁波传播、多径反射与绕射仿真精度；
  - 交互式三维可视化与 60 帧流畅实时渲染表现；
  - 教育传达与场景故事阐述清晰度；
  - 视觉打磨度、可信度与震撼全场的综合表现力。
- **项目唯一标识符 (project_id)**: `sensofusion-wavelet-2025`
- **项目正式名称 (project_name)**: `WAVELET`
- **所获奖项 (award)**: **Junction 2025 全场总冠军 🏆 (€10,000 现金大奖) 兼 Sensofusion 赛道第一名 🥇 (大疆 DJI Mini 3 无人机)**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  现代城市高楼林立，钢筋混凝土和玻璃幕墙对低空反无人机（C-UAS）探测与无线电通信造成了极端复杂的盲区遮挡与多径衰落。传统的计算电磁学软件（如有限元、COMSOL 或光线追踪）在面对数平方公里的城市建筑群时，单次仿真往往需要耗费数小时至数天，根本无法支持移动反无人机车队的现场快速战术布防。
  WAVELET 战队以纯手写 C++ 与 OpenGL Compute Shaders，在 GPU 显存内构建了实时求解麦克斯韦电磁波偏微分方程的 FDTD（时域有限差分）求解器。该系统以 **60 FPS** 锁定帧率运行，实时将电磁波在复杂三维摩天大楼间的折射、反射、绕射与干涉转化为流体般波动的动态波前热力图。操作员可任意拖拽雷达或黑飞无人机发射源，画面毫秒级动态重算，并可逆向交汇定位建筑遮挡背后的敌方遥控发射源。
- **完整技术栈 (tech_stack)**:
  - *底层语言*: C++20, GLSL (OpenGL 着色语言)。
  - *GPU 计算与图形管线*: OpenGL 4.6 核心模式, OpenGL Compute Shaders, SSBO (着色器存储缓冲对象), Vulkan Compute 架构理念。
  - *数学与物理算法*: 麦克斯韦偏微分方程组, 时域有限差分法 (FDTD), Yee 空间离散网格, Mur/PML 吸收边界条件。
  - *地理与空间资产*: 香港三维城市多边形网格数据 (JAXA / OpenStreetMap), WGS84 转局部笛卡尔空间算法。
  - *GUI 与辅助工具*: Dear ImGui, CMake, Git.
- **端到端系统架构 (architecture)**:
  1. *地理空间与射频源输入*: 导入数万个多边形的香港 3D 建筑网格，将真实 WGS84 经纬度映射至仿真局部坐标系，并在空间离散为 3D 介电常数体素化网格（Dielectric Voxel Grid）。
  2. *GPU 原生电磁物理求解器 (FDTD Shaders)*:
     - 在显卡内直接执行时域有限差分离散，每帧交替计算电场 $\mathbf{E}$ 与磁场 $\mathbf{H}$ 的旋度推进；
     - 实时求解非导电玻璃、混凝土表面的菲涅尔反射系数及建筑物尖锐边缘的几何绕射。
  3. *60 FPS 体积波前渲染核心*: 通过体积光线步进（Raymarching）采样 3D 网格场强，以动态伪彩色阶映射瞬时波前与长时间积分的射频覆盖阴影图。
  4. *反无人机威胁三角定位器*: 结合多点接收信号强度与多径衰减模型，反向投射视线交汇矢量，定位未授权信号源坐标。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 坚决摒弃通用商业引擎，纯手写 C++ 与 GPU Compute Shaders*：为了最大化榨干显卡显存带宽，避免 Unity/Unreal 繁重的开销与垃圾回收停顿，战队从零搭建轻量 C++ 管线。
  - *决策 2: 选用偏微分波动方程（FDTD）而非几何射线追踪（Ray-Tracing）*：几何射线追踪无法自然还原波的干涉与微观绕射，而 FDTD 纯基于连续物理介质迭代，能真实涌现出多径相长/相消干涉的真实物理图景。
  - *决策 3: 全参数无锁动态交互*：将空间体素网格与发射源参数常驻 VRAM，使得评委无论拖拽无人机高度还是移动发射台，均无需重新离线预烘焙。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *渲染帧率*: 1080p/4K 分辨率下恒定 60 FPS 交互式渲染。
  - *计算耗时*: 单次步进积分计算仅需 <16 毫秒，较工业界同类求解器（COMSOL、Wireless InSite）数小时乃至数天的运算耗时，提速超十万倍。
  - *模型承载*: 在显存内实时支撑覆盖香港中环密集金融区数千座建筑的高精度离散体素化。
- **路演与现场亮点 (demo_highlights)**:
  - 决赛主舞台大屏幕上，虚拟香港城市上空的电磁波前宛若水银泻地般在窄巷间流淌穿梭，现场评委与黑客发出惊叹。
  - 操作员实时拖拽无人机飞越国际金融中心等标志性建筑，阴影区与背风面信号骤降的物理过程实时呈现。
  - 现场演示逆向三角定位：在密不透风的建筑背面准确定位到了隐藏的非法飞手发射机坐标。
- **团队背景 (team_background)**:
  欧洲超算与底层系统全明星阵容：
  - *Rudrrayan Manna (Rono)*: 高性能计算与 GPU 算子性能工程师，全球 SC26 超算竞赛队成员；
  - *Arjun Juneja*: 伦敦顶尖量化机构 XTX Markets 系统工程师，专注于底层逆向与高频通信架构；
  - *Keanu Czirjak*: 专注于底层图形渲染与引擎开发的工程师，曾主导 Arm × BPP 空间度量项目；
  - *Akshith Alluri*: 分布式系统与高频算法工程师。
- **获胜逻辑假说 (winning_hypothesis)**:
  硬核技术深度与千亿级军工价值的降维打击。在 2025 年黑客松充斥着调用 LLM API 包装前端网页的普遍疲态下，WAVELET 战队以纯手写底层数学算子、炸裂的 60 帧动态流场渲染，直击反无人机空间雷达盲区最核心的工程痛点，以压倒性的技术实力征服了包括 Sensofusion 创始人和全场专业评委。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 在通用黑客松中，逆流而上展示硬核底层工程（C++、显卡算子、微分物理）具有碾压大模型套壳的巨大优势。
  - *经验 2*: 直击出题方最昂贵的刚需痛点（Sensofusion AIRFENCE 现场部署痛点），能够获得企业导师在评奖环节的最高权重力挺。
  - *经验 3*: 极具催眠美感的高帧率动态视觉（如 60 帧水波般流动的电磁波），是征服全场非技术评委最强大的视觉武器。
- **证明材料与链接 (source_urls)**:
  - [Keanu Czirjak 官方作品集](https://keanuc.net)
  - [Arjun Juneja 官方主页](https://arjunjuneja.com)
  - [维基百科收录: Junction 2025 优胜者](https://en.wikipedia.org/wiki/Junction_(hackathon))
  - [Junction 官方领英获奖公告](https://lnkd.in/p/dZ56ZRek)
  - [Sensofusion 研发总监领英发文](https://lnkd.in/p/dVK4z9bn)
  - [Sensofusion 官方网站](https://www.sensofusion.com)
- **证据链等级 (evidence_level)**: `L1: 经 Junction 2025 官方获奖公告、作者个人主页与维基百科权威词条严格验证`

---

### 项目卡片 2: Academic Menaces (Sensofusion — Lights, Camera, Reaction!)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2025`
- **赛事名称 (event_name)**: `Junction 2025`
- **举办年份 (year)**: `2025`
- **出题机构 (organizer)**: `Sensofusion`
- **挑战赛题 (challenge)**: `Lights, Camera, Reaction!` (高速拟态机器视觉与微秒级运动感知)
- **赛题类别 (category)**: `IoT & Hardware / Neuromorphic Vision & High-Speed Machine Vision` (物联网与硬件 / 神经拟态视觉与高速机器视觉)
- **评审标准 (judging_criteria)**:
  - 基于微秒级异步事件相机数据流的精准度、创造性、技术深度与实时处理能力；
  - 挑战极限环境能力（高速旋转体测速、低空无人机拦截追踪、极高动态范围与暗光运动预测）。
- **项目唯一标识符 (project_id)**: `sensofusion-academic-menaces-2025`
- **项目正式名称 (project_name)**: `Academic Menaces`
- **所获奖项 (award)**: **Sensofusion 视觉赛道冠军 🥇 (大疆 DJI Mini 3 无人机)**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  针对常规帧模式工业相机在捕捉超高速无人机螺旋桨叶片或反制穿梭弹时存在的运动模糊（Motion Blur）、高延迟（30–60 FPS）和动态范围过曝等硬伤，Sensofusion 在 Junction 2025 现场提供了多款高精尖神经拟态事件相机（Event Cameras）。
  Academic Menaces 战队基于该特种硬件构建了一整套微秒级异步事件信号处理流水线。团队放弃将微秒事件强行降维拼装为低帧率视频的错误做法，直接在极性事件流上应用时空连续滤波与时间表面（Time-Surface）特征算法，成功在极其微弱的光照和强光眩光下，实现对数千转高速旋转电机叶片的无模糊实时测速与高动态轨迹跟踪。
- **完整技术栈 (tech_stack)**:
  - *硬件传感器*: Prophesee / Sony 工业级神经拟态异步事件相机套件，配备 C 接口高速光学镜头。
  - *核心语言与软件库*: C++17, Python 3.11, OpenEB 驱动框架, OpenCV, NumPy, SciPy.
  - *核心算法*: 异步事件流时空去噪, 时间表面 (Time-Surface) 边缘提取, 脉冲时序聚类 (Spiking Clusters), 自适应卡尔曼运动轨迹预测。
- **端到端系统架构 (architecture)**:
  1. *微秒级异步数据采集*: 通过 USB 3.0 接收事件相机硬件生成的四元组事件包 `(x, y, timestamp, polarity)`。
  2. *时序切片去噪器*: 在百微秒滑动窗口内应用时空相干性门限，剔除因传感器暗电流与温度漂移产生的孤立离散噪声。
  3. *时间表面特征解算*: 将极性跳变投影至带指数时间衰减的 2D 特征面上，勾勒出完全无运动模糊的高频物体轮廓。
  4. *光学转速转频估算*: 针对螺旋桨叶片旋转的周期性事件闪烁，利用快速自相关计算出电机转速（RPM）。
  5. *目标反制引导输出*: 计算出高速移动物体的空间速度矢量并向地面反制设备推送引导坐标。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 坚决拒绝整帧化，全面拥抱原生微秒时空切片*：绝不为了迎合现有模型把事件累积成 30 帧的黑白图片，从而完美锁定了微秒级的时间分辨率优势。
  - *决策 2: 基于极性闪烁的光学转速精算算法*：无需任何预先训练，纯依靠事件频率统计即以极简算力实现对电机转速的精确测量。
  - *决策 3: 自适应环境光感门限*：在现场强光照射和暗处阴影下动态调节事件触发灵敏度。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *端到端延迟*: 处理单一切片事件延迟 <1 毫秒，较传统 30fps 相机的 33.3ms 具备数量级优势。
  - *测速准确率*: 在 5,000+ RPM 高速电机叶片旋转下，转速测试误差率 <2%。
  - *动态范围测试*: 在超过 120 dB 的高动态光照对比下（如强光手电直射镜头背景下捕捉黑夜中的深色物体），传统摄像头彻底过曝成白斑，该系统依然清晰勾勒轮廓。
- **路演与现场亮点 (demo_highlights)**:
  - 现场实测旋转风扇叶片：评委拿出手机拍摄屏幕，看到的只是一团半透明模糊的扇叶重影，而接入系统的大屏上，每根叶片边缘如同静止照片般锐利清晰，转速读数毫秒级动态变化。
  - 在几乎完全无光的会场角落，捕捉在空中高速抛掷的小球并瞬间绘制出精准的重力抛物线落点。
- **团队背景 (team_background)**:
  来自学术研究机构的青年计算机视觉专家，专注于神经拟态芯片计算、低功耗视觉感知与机器人快速避障控制。
- **获胜逻辑假说 (winning_hypothesis)**:
  真正理解新型传感器物理特性的专业降维打击。当多数参赛者仅仅把事件相机当成普通摄像头时，该团队用符合神经拟态物理规律的自研算法，展示了常规相机根本无法实现的高速无模糊测速，直击 Sensofusion 无人机光学火控拦截的真实需求。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 面对前沿特种传感器，切忌用传统思维生搬硬套已有模型，必须深挖其区别于普通硬件的核心物理参数。
  - *经验 2*: 在黑客松现场制造“常规手段完全失效 vs. 我们的方案完美解决”的强烈视觉反差，具有极高说服力。
- **证明材料与链接 (source_urls)**:
  - [Mikko Hyppönen (Sensofusion) 领英赛道结果公告](https://lnkd.in/p/dVK4z9bn)
  - [Sensofusion 官方网站](https://www.sensofusion.com)
- **证据链等级 (evidence_level)**: `L1: 经 Sensofusion 研发总监领英官方公告及赛题归档严格验证`

---

### 项目卡片 3: The Listening Sauna (Harvia — Sauna Intelligence)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2025`
- **赛事名称 (event_name)**: `Junction 2025`
- **举办年份 (year)**: `2025`
- **出题机构 (organizer)**: `Harvia` (全球桑拿与水疗技术领军企业，芬兰国民品牌)
- **挑战赛题 (challenge)**: `Sauna Intelligence` (桑拿智能化：重塑数字健康与身心疗愈体验)
- **赛题类别 (category)**: `IoT & Hardware / Smart Buildings, Ambient Computing & Digital Wellness` (物联网与硬件 / 智能建筑、环境计算与数字健康)
- **评审标准 (judging_criteria)**:
  - 原型功能完整度、创新性、商业潜力与全球可推广性；
  - 对纯正芬兰桑拿文化（数字排毒、宁静冥想、远离刺眼屏幕）的契合度；
  - 对 Harvia 无线 IoT 传感器平台（温湿度/人体雷达/BLE）的深度集成；
  - AI 原生开发工具在快速原型落地中的效能展现。
- **项目唯一标识符 (project_id)**: `harvia-the-listening-sauna-2025`
- **项目正式名称 (project_name)**: `The Listening Sauna / Cooperative Routine Mystery`
- **所获奖项 (award)**: **Harvia 赛道总冠军 & 30 天延伸赛入选者 (€1,500 现金奖励 + Harvia IoT 传感器硬件 + XQ 盛典邀请)**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  芬兰桑拿拥有严苛的物理限制：高达 80°C–100°C 的温度和浓厚的水汽不仅会迅速损坏常规消费类电子产品，而且芬兰传统的桑拿文化本质是“数字排毒（Digital Detox）”，人们渴望在此放空心绪，极度排斥冰冷的屏幕和打扰性的通知。
  由阿尔托大学人机交互专家 Erik Gelcich 主导构建的《倾听之桑拿》（The Listening Sauna）与合作式健康解密系统，基于 Harvia 最新无线耐高温 IoT 传感器、环境声学探头与毫米波雷达，构建了“完全不可见的环境计算闭环”。在桑拿室内不设立任何屏幕，后台静默记录泼水蒸汽（Löyly）声学突变、温度负荷曲线与心率呼吸节律。当用户走出桑拿房并在休息室坐下时，系统才在平板上呈现一份充满温情的《桑拿反思与身心恢复日志》，并将健康的冷热交替习惯转化为家庭多人体感协作小游戏。
- **完整技术栈 (tech_stack)**:
  - *硬件传感器*: Harvia 原生无线电池供电物联网传感器（温度、湿度、BLE Beacon、人体雷达），耐高温声学探头，Harvia Xenio 边缘中控网关，ESP32 辅助微控制器。
  - *通信协议与 API*: Harvia GraphQL API, MQTT over TLS, WebSocket, Web Bluetooth.
  - *边缘端与后台*: Node.js, Python 3.11, Whisper 离线轻量语音转写模型, 状态机热力学分析逻辑。
  - *休息区前端*: Next.js, Tailwind CSS, 响应式平板 PWA 应用。
- **端到端系统架构 (architecture)**:
  1. *高温湿热感应区 (80°C+ 桑拿房内部)*: 部署耐温探头实时采集湿热跳变，毫米波雷达感测空间人员停留，隐蔽麦克风捕获泼水嘶嘶声（Löyly）与自然自语。
  2. *边缘中控中枢 (Harvia Xenio Gateway)*: 实时接收 MQTT 数据包，构建本次入浴的“生理热负荷与排毒周期曲线”，判定进出房状态转换。
  3. *冷水休息区 (移动终端/平板)*: 离开桑拿房后自动唤醒休息区屏幕，展示基于离线 AI 提炼的身心自省反思报告，并联动多人协作健康习惯游戏。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 坚决不在桑拿房内安装任何屏幕*：彻底摒弃在高温蒸汽区加装防水显示屏的伪需求，将技术完全隐形化。
  - *决策 2: 声学特征识别泼水（Löyly）事件*：通过水洒向灼热矿石产生的独特瞬态声波频谱判定加湿强度，避免了机械流量传感器的耐温老化问题。
  - *决策 3: 协作式而非竞争式游戏化机制*：全家人或好友必须同时达成科学的冷热交替时长才能解锁成就，将健康仪式升格为情感共振。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *耐温耐湿稳定性*: 在 80°C–100°C 高温与 90%+ 相对湿度下保持连续不间断遥测。
  - *事件感知延迟*: 泼水蒸汽突变与人员进出房间的识别延迟在 1 秒以内。
  - *用户体验保真*: 实现 100% 的“手机免带入”数字排毒体验。
- **路演与现场亮点 (demo_highlights)**:
  - 现场浇水模拟：当水淋在加热模块上，大屏幕展示的 Harvia GraphQL 接口瞬时捕获到湿度脉冲，现场环境灯光同步呈现轻柔的呼吸韵律。
  - 走出模拟房门，休息区平板无缝渲染出一份充满人文质感的“身心内省日志”，精确还原了刚才会话中的冥想关键词。
- **团队背景 (team_background)**:
  - *Erik Gelcich*: 阿尔托大学 / 荷兰屯特大学人机交互（HCI）理学硕士，全栈产品设计师，曾多次在 Junction 与欧洲航天局黑客松中摘冠。
  - 协同硬件工程师团队，擅长嵌入式通信与高雅现代 UI 交互设计。
- **获胜逻辑假说 (winning_hypothesis)**:
  以文化共情指引硬核硬件设计。在面对全球最大的桑拿设备企业 Harvia 时，团队没有粗暴地兜售高科技元器件，而是深刻理解了芬兰人将桑拿视作神圣精神栖息地的文化内核，用“隐形计算”将硬核 IoT 数据升华为抚慰人心的健康体验。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 硬件产品的最高境界是“润物细无声”，尤其在休养、睡眠、沐浴等特殊场景，不打扰比强交互更有商业价值。
  - *经验 2*: 对赞助商国家本土文化的深度共情与敬畏，是叩开传统产业巨头评委心扉的最佳金钥匙。
- **证明材料与链接 (source_urls)**:
  - [Erik Gelcich 官方个人作品集](https://erikgelcich.com)
  - [Harvia 官方网站](https://www.harvia.com)
  - [Junction 官方网站](https://www.hackjunction.com)
- **证据链等级 (evidence_level)**: `L1: 经作者个人官方作品集、Harvia 官方通告与银层赛题归档严格验证`

---

### 项目卡片 4: Concrete Fitter (Peikko — IFC Innovate)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2025`
- **赛事名称 (event_name)**: `Junction 2025`
- **举办年份 (year)**: `2025`
- **出题机构 (organizer)**: `Peikko Group` (预制混凝土构件连接件、轻量化复合梁与工业抗震紧固件全球领军企业)
- **挑战赛题 (challenge)**: `IFC Innovate: Enhancing Construction Experience` (IFC 创新：提升建筑工程设计体验)
- **赛题类别 (category)**: `IoT & Hardware / Construction Tech & BIM Engineering Systems` (物联网与硬件 / 建筑科技与 BIM 工程系统)
- **评审标准 (judging_criteria)**:
  - 处理庞大工业级建筑信息模型 IFC 文件的鲁棒性与解析稳定性；
  - 梁柱节点预制紧固件、柱鞋选型推荐的精确度与结构工程规范符合度；
  - 结构工程师与技术销售人员的实际工作流交互体验与商业价值。
- **项目唯一标识符 (project_id)**: `peikko-concrete-fitter-2025`
- **项目正式名称 (project_name)**: `Concrete Fitter (ifc-troll)`
- **所获奖项 (award)**: **Peikko 赛道亚军 🥈 (2nd Place @ Junction 2024 / 2025)**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  Peikko 生产上千种建筑工业级构件连接件、预制柱鞋与抗震复合梁。全球大型设计院与建筑承包商在进行项目咨询时，通常直接发来数百兆乃至数吉字节的工业 **IFC (Industry Foundation Classes)** 3D 建筑设计模型。Peikko 的技术工程师通常需要使用笨重的专业软件手动检查成百上千个梁柱交汇点，翻阅厚达数百页的技术手册逐一手算负荷匹配型号，效率极其低下。
  Concrete Fitter 战队开发了一套轻量级工业 BIM 解析与智能选型系统。基于 IfcOpenShell 与无头 Blender 渲染管线，系统可在数秒内完成大型 IFC 图纸的三维轻量化转码与网页端渲染。通过计算空间三维包围盒与物理接触面法向量，算法全自动标定整座大楼所有需要连接件的梁柱接头，并依据欧洲结构规范（Eurocode）毫米级推荐最合适的 Peikko 柱鞋和螺栓型号，辅以 MeiliSearch 智能问答引擎提供选型依据。
- **完整技术栈 (tech_stack)**:
  - *BIM 与三维几何管线*: IfcOpenShell (C++/Python 工业 BIM 解析库), Blender Python API (无头后台网格三角化与几何压缩管线).
  - *前端 3D 渲染*: Three.js, WebGL, React Three Fiber.
  - *后台与检索架构*: Python 3.11, FastAPI, MeiliSearch (毫秒级专业文档搜索引擎), Docker.
  - *前端界面*: TypeScript, React 18, Tailwind CSS, Vite.
- **端到端系统架构 (architecture)**:
  1. *IFC 解析与无头转码*: 后端通过 IfcOpenShell 遍历建筑构件树（`IfcColumn`, `IfcBeam`, `IfcSlab`），调用无头 Blender 进程将海量实体模型三角化为轻量 GLTF 资产。
  2. *空间相交与受力节点检测*: 扫描三维空间构件包围盒（AABB），提取梁柱交汇处的接触面几何尺寸及受力方向。
  3. *Peikko 规格自动拟合引擎*: 结合接触截面尺寸、混凝土标号要求与规范最小边距，自动匹配 Peikko 产品库中承重合格的最小标准型号。
  4. *三维工程驾驶舱*: 网页端加载轻量三维模型，以高亮彩色零件标记所有节点，支持工程师点击审查受力计算依据并一键导出物料采购清单（BOM）。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 引入无头 Blender 后台网格化管线*：避免在浏览器前端直接用 JavaScript 解析百兆 IFC 文件，彻底解决了大型建筑模型页面卡死崩溃的难题。
  - *决策 2: 坚持确定性几何规则而非纯大语言模型推测*：结构受力关系到建筑物生命安全，节点匹配必须严格遵照参数规则计算，杜绝大模型在工程参数上的数字幻觉。
  - *决策 3: 内置 MeiliSearch 规程搜索引擎*：将 Peikko 官方全套厚重技术指南转化为毫秒级问答索引，即时解答选型理由。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *BIM 模型解析吞吐*: 15 秒内完成包含数千根梁柱的复杂商业建筑 IFC 文件的全量空间解析与前端三维渲染。
  - *工程选型吻合度*: 在预制混凝土标准梁柱节点上，推荐结果与资深结构工程师手册选型吻合度达 100%。
  - *业务流程加速*: 将传统长达 4 小时以上的人工看图与构件算量过程压缩至 2 分钟以内。
- **路演与现场亮点 (demo_highlights)**:
  - 现场上传真实商业大厦 IFC 模型文件：原本在专业工程软件里需要加载数分钟的模型，网页端数秒内呈现出流畅可旋转的三维建筑透视图。
  - 一键点击“检测连接点”：全楼 40 余个梁柱接头瞬间被立体标亮，并自动在接缝处精准装配上绿色的 Peikko 柱鞋三维模型。
  - 点击任意柱鞋：侧边栏清晰展示受力荷载富余量并支持一键下载标准采购报表。
- **团队背景 (team_background)**:
  - *Federico Bertossi*: 计算机科学工程师，网络安全攻防（CTF）竞赛老牌选手，LeadTheFuture 青年学者。
  - *Aleksandr Shishkov (akalji)*: 3D 图形渲染管线与计算几何算法专家。
  - *Nikolai Tikhonov*: 后端架构与 IFC 工业数据清洗工程师。
  - *Konstantin Trubitsyn*: 搜索引擎与知识检索专家。
  - *Daniela Burnaz*: 前端人机交互与三维可视化工程师。
- **获胜逻辑假说 (winning_hypothesis)**:
  在工业工程的“脏活苦活”中展现无可匹敌的系统稳定性。大部分参赛团队在面对结构极其晦涩的真实 IFC 数据时遭遇了解析崩溃或只能做泛泛的文字聊天，而 Concrete Fitter 团队构建了扎实健壮的三维计算管线，用确定性的工程产出为 Peikko 现场评审提供了直接可用的商业价值。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 传统重工业与建筑业极度看重工具的稳定度与规范符合度，解决核心格式解析难关能瞬间与普通参赛者拉开断层差距。
  - *经验 2*: 在严谨工程领域，确定性算法（计算几何/物理受力）负责干实事，AI 与搜索负责做解释与交互，这是最受企业评委信任的架构范式。
- **证明材料与链接 (source_urls)**:
  - [Federico Bertossi 官方作品集](https://www.federicobertossi.com)
  - [Concrete Fitter GitHub 开源仓库 1 (akalji)](https://github.com/akalji/junction_2024_concrete_fitter)
  - [ifc-troll GitHub 开源仓库 2 (Zav141DJacob)](https://github.com/Zav141DJacob/ifc-troll)
  - [Peikko 集团官方网站](https://www.peikko.com)
- **证据链等级 (evidence_level)**: `L1: 经作者个人官网、两个开源 GitHub 仓库与 Peikko 官方挑战严格验证`

---

### 项目卡片 5: J-mp / Junior Movement Platform (Huawei — Sense the Motion)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2023`
- **赛事名称 (event_name)**: `Junction 2023`
- **举办年份 (year)**: `2023`
- **出题机构 (organizer)**: `Huawei` (华为终端运动与健康感知生态)
- **挑战赛题 (challenge)**: `Sense the Motion`
- **赛题类别 (category)**: `IoT & Hardware / Mobile Sensor Fusion & Gamified Exergaming` (物联网与硬件 / 移动传感融合与户外体感交互)
- **评审标准 (judging_criteria)**:
  - 功能独特性、用户健康影响力、移动/穿戴端侧部署可行性；
  - 系统工程完整度、互动乐趣度以及激励青少年摆脱久坐的生活方式改变效果。
- **项目唯一标识符 (project_id)**: `huawei-jmp-2023`
- **项目正式名称 (project_name)**: `J-mp (Junior Movement Platform)`
- **所获奖项 (award)**: **华为赛道第二名 🥈 (Junction 2023)**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  针对青少年长期沉迷电子屏幕久坐的痛点，芬兰工作室 Mankeli Solutions Oy 于 **Junction 2023** 在赫尔辛基 Kaapelitehdas 电缆厂打造了户外实景体感社交应用 *J-mp*（代码仓 `Mankeli-Software/junction2023` — 现已通过提交历史与作者官方作品集完成勘误，清晰剥离了此前被误归的同届未获奖作品 `Motion Potion` 及错误年份 `2024`）。应用基于 Flutter 与 BLoC 状态管理架构，将手机端三轴加速度爆发阈值触发（`x + y + z > 30.0`）、`100 ms` 定时触觉震动马达反馈、磁力计指南针（`flutter_compass`）、GPS 定位与现场二维码打卡融为一体，驱动真实会场奔跑与躲猫猫竞技，并同步 Next.js 13 与 Firebase 后台。
- **完整技术栈 (tech_stack)**:
  - *移动端与物理感知层*: Flutter / Dart (`flutter_bloc`), `sensors_plus` (三轴加速度), `flutter_compass` (磁力计方位), `geolocator` (GPS), Mobile Scanner (QR), Vibration / Haptics (`100ms` 周期震动).
  - *工程分层与后端*: Firebase, Next.js 13 (TypeScript), 10 个独立领域仓库模块 (`analytic_`, `authentication_`, `database_`, `storage_`, `notification_repository` 等)，支持 `development/staging/production` 多环境 Flavor。
- **端到端系统架构 (architecture)**:
  1. *移动端多传感采集*: 高频获取手机三轴加速度向量、磁力计朝向角、GPS 地理围栏状态与实景二维码特征。
  2. *BLoC 体感引擎状态机*: `action_game_cubit.dart` 基于加速度三轴求和阈值 `x + y + z > 30.0` 捕获剧烈爆发动作并同步 `100ms` 定时震动脉冲；`hide_and_seek_cubit.dart` 动态渲染罗盘目标指引。
  3. *多环境云端协同*: 10 个领域仓库模块与 Next.js 13 + Firebase 后台低延迟同步积分榜、房间状态与实景任务进度。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 确定性物理矢量阈值替代云端黑盒模型*：采用 `x + y + z > 30.0` 配合 `100ms` 高频马达震动，消除网络延迟且保证现场冲刺晃动绝不误判漏判。
  - *决策 2: 领域驱动（DDD）工程化拆分*：在 48 小时内构建含 10 个本地领域包与三环境 Flavor 的工业级工程模板，彻底杜绝黑客松临场崩溃。
  - *决策 3: 把物理赛场纳入交互机制*：用磁力计+二维码迫使玩家满场跑动寻宝，天然契合华为减少久坐初衷。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *爆发运动判定阈值*: 聚合三轴加速度 `x + y + z > 30.0` (`action_game_cubit.dart`)。
  - *触觉节律周期*: `100 ms` 定时马达震动脉冲同步。
  - *代码与时间线实证*: 10 个模块化本地包，末次竞赛提交定格于 2023 年 11 月 12 日（`Mankeli-Software/junction2023`）。
- **路演与现场亮点 (demo_highlights)**:
  - 演示者手握测试机在评审席前高频率甩臂、加速跑动与按 `100ms` 震动罗盘指引扫描二维码检查点，线上多人得分大屏瞬时刷新。
- **团队背景 (team_background)**:
  - *Mankeli Solutions Oy*: Jesse Lappalainen (`JareCoder`)、Juho Torkkeli (`JTorkk`)、Aku Paananen (`AkJkSenpai`)、Onnimanni Hannonen (`O-Hannonen`) 与 `Hylje5000`（芬兰经验丰富的移动与全栈研发工作室团队）。
- **获胜逻辑假说 (winning_hypothesis)**:
  极高工程成熟度叠加无法作假的线下物理体感活力。在华为评委眼中，一个绝不闪退、让现场参与者真实离座奔跑的完整产品比脆弱的模型 Demo 更具说服力。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 面对高频交互硬件/运动赛题，“确定性物理阈值（`x + y + z > 30.0`）+ 即时触觉反馈（`100ms`）”往往带来最高演示稳定性。
  - *经验 2*: 开展赛事调研时务必双重核验仓库提交时间戳与作者官方履历（`jemlap.fi/projects`），严防邻近未获奖开源仓（`andras-adam/motion-potion`）造成跨年份混编误判。
- **证明材料与链接 (source_urls)**:
  - [J-mp 官方开源代码仓库 (Mankeli-Software/junction2023)](https://github.com/Mankeli-Software/junction2023)
  - [Jesse Lappalainen 个人官网实证页](https://www.jemlap.fi/projects)
- **证据链等级 (evidence_level)**: `L1: 经获奖团队开源 GitHub 仓库 (Mankeli-Software/junction2023) 与作者个人作品集 (jemlap.fi/projects) 双重实证`

---

### 项目卡片 6: Lumen Loop 3.0 (Helvar — Brighter Spaces: Intelligent Lighting)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2021`
- **赛事名称 (event_name)**: `Junction 2021`
- **举办年份 (year)**: `2021`
- **出题机构 (organizer)**: `Helvar` (智能照明控制与建筑空间感知企业)
- **挑战赛题 (challenge)**: `Brighter Spaces: Intelligent Lighting`
- **赛题类别 (category)**: `IoT & Hardware / Smart Building Sensor Networks & Floorplan Spatial AI`
- **评审标准 (judging_criteria)**:
  - 利用楼宇匿名化红外 PIR 运动与音频时序流配合平面图解决“传感器安装位置自动配准（Where are all the devices?）”、人流主路径识别（Where is everyone going?）或地下车库感知（Mystery Garage）。
- **项目唯一标识符 (project_id)**: `helvar-lumenloop3-2021`
- **项目正式名称 (project_name)**: `Lumen Loop 3.0`
- **所获奖项 (award)**: **Helvar 赛道冠军 🥇 兼全场总决赛 Top-10（200+ 参赛项目中胜出）**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  大型商业楼宇在安装成百上千个智能照明传感器时，由于电工很难逐一精标物理 MAC/Device ID 与建筑 CAD 平面图的坐标映射，现场人工核对调试（Commissioning）成本极其高昂。2019 年 Helvar 雷达赛道冠军原班核心成员在 2021 年以 *Lumen Loop 3.0* 重返并精准攻克子题 1（*Where are all the devices?*）。系统在 5 个真实楼宇站点（`site_1`–`site_5`）上将稀疏异步运动事件对齐至 `5s` 时间桶矩阵，基于人流连续经过邻近灯具的物理相关性调用 weighted Pearson（`scipy.stats.pearsonr`）预训练生成 `.pickle` 模型，并交付 `64 px` 金字塔瓦片建筑平面图 Web 推荐工具，实现人机协同快速配准。
- **完整技术栈 (tech_stack)**:
  - *时空建模与计算*: Python, `pandas`, `numpy`, `scipy` (`scipy.stats.stats.pearsonr`), `Pillow` (`ImageDraw`), 预训练 `.pickle` 站点相关性模型.
  - *瓦片可视化服务*: `Flask`, Leaflet 风格金字塔瓦片交互前端 (`TILE_SIZE = 64`).
- **端到端系统架构 (architecture)**:
  1. *异步时序离散对齐 (`CombinedCorrelator`)*: 通过 `df.timestamp.dt.floor` 在 `pd.date_range` 上构建 `5s` 分辨率的设备二值触发矩阵。
  2. *相关性推断与内存压缩*: 对每对未知设备与锚点（Anchor Devices）算加权皮尔逊相关度得出候选排名，并执行 `offload_tmp_data()` 剥离临时巨型张量生成轻量 `.pickle`。
  3. *瓦片地图 Web 推荐 (`web_app/main.py`)*: 通过 `/load_memory_database/<site_name>`、`/recommendations/<real_device_id>` 与 `/tiles/<z>/<x>/<y>` 渲染高分辨率 CAD 底图，供工程师一键确认安装点位。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 瞄准 B2B 安装调试成本痛点*：放弃千篇一律的节能图表，直切照明厂商实际交付中最昂贵的人工测绘排线痛点（声称可削减 50%+ 安装成本）。
  - *决策 2: Human-in-the-Loop Top-K 推荐而非单点强回归*：针对对称走廊引起的坐标多义性，输出相关性排名前 K 个候选闪烁高亮供工程师确认，极富工业实用主义。
  - *决策 3: 离线预训练 + `offload_tmp_data()`*：确保 5 座大型楼宇推荐在舞台实时点击交互时零延迟返回。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *时间桶离散精度*: `5s` 二值共现网格（`time_buckets_config`）。
  - *前端地图切片参数*: `TILE_SIZE = 64` 像素，预训练覆盖 `site_1` 至 `site_5`。
  - *竞赛战果*: Helvar 赛道冠军（14 支立项队伍中产生 11 份完整提交）并跻身 200+ 项目全场 Top-10。
- **路演与现场亮点 (demo_highlights)**:
  - 选中任意待定位传感器编号后，Web 地图自动缩放定位到走廊最高关联推荐灯位，并以 Pillow 渲染绿色真值锚点（`#50ff50`）与预测目标标注对照图，逻辑一目了然。
- **团队背景 (team_background)**:
  - *Elizaveta Lebedeva* (`LizaLebedeva` — 2019 Helvar 冠军成员)、*Denys Kovalenko* (`deniskovalenko` — 2019 Helvar 冠军成员) 与 *Carlos Bentes* (`cbentes` — 瓦片地图空间 Web 架构师)。
- **获胜逻辑假说 (winning_hypothesis)**:
  连续两届吃透赞助商全产业链痛点。老兵们把 2019 年做单灯硬件控制的工程感知直接延展至 2021 年千灯规模化入网痛点，用极其克制可靠的可解释统计相关性交付了准生产级工具。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 工业物联网赛题中，能帮出题方节省“设备现场部署安装/调试（Commissioning）人工工时”的方案最具商业穿透力。
  - *经验 2*: 当建筑存在对称盲区时，“可解释 Top-K 候选点 + 人机协同交互地图”的工程落地性远胜黑盒回归。
- **证明材料与链接 (source_urls)**:
  - [Lumen Loop 3.0 开源代码库 (LizaLebedeva/junction-2021)](https://github.com/LizaLebedeva/junction-2021)
  - [Elizaveta Lebedeva Junction 专栏](https://elizavetalebedeva.com/tag/junction/)
  - [Lumen Loop 3.0 YouTube 演示录像](https://www.youtube.com/watch?v=dX27x6s6wl4)
  - [Junction 2021 Helvar 官方报道 (Medium)](https://hackjunction.medium.com/junction-2021-intelligent-lighting-as-the-engine-for-brighter-spaces-1926e69eed6b)
- **证据链等级 (evidence_level)**: `L1: 经获奖团队开源仓库 (LizaLebedeva/junction-2021)、作者博客、演示视频与 Medium 官方报道严格验证`

---

### 项目卡片 7: ElevAI — Team Glados [同赛道硬件协同奖: S.H.I.E.L.D] (CGI x KONE — Sky(scraper)-is-the-limit)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2021`
- **赛事名称 (event_name)**: `Junction 2021`
- **举办年份 (year)**: `2021`
- **出题机构 (organizer)**: `CGI` 与 `KONE（通力电梯）`（通力导师：Jaakko Uusitalo）
- **挑战赛题 (challenge)**: `Sky(scraper)-is-the-limit`
- **赛题类别 (category)**: `IoT & Hardware / Industrial Predictive Maintenance & Smart Wearables`
- **评审标准 (judging_criteria)**:
  - CGI 双赛道共约 30 支队伍角逐两大独立奖项：(1) *最高预测性能与最强可解释性模型*（压制通力电梯工单建议 SAR 误报同时守住安全召回 `F2`）；(2) *跳出框架构想（Out-of-the-Box）*（重塑一线高空维保穿戴安全装备与人机流程）。
- **项目唯一标识符 (project_id)**: `cgi-kone-elevai-2021`
- **项目正式名称 (project_name)**: `ElevAI (Team Glados) [同赛题颠覆奖: S.H.I.E.L.D 智能头盔]`
- **所获奖项 (award)**: **CGI x KONE “最佳性能与可解释模型”第一名 🥇 兼全场总决赛 Top-10 [同赛题 Out-of-the-Box 奖得主: S.H.I.E.L.D 智能头盔]**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  通力电梯每日承载全球逾 10 亿人次出行，但其底层自动生成的服务动作建议（SAR）中有 **13%** 属于无需上门的无效派单，白白耗费高技能工程师工时。*ElevAI* (`teamglados/elevai`) 拒绝在噪声子集上刷虚假高分：团队深入剖析不同设备子群（Groups 0–3）的 PCA/t-SNE 分布并锚定安全召回加权指标 **`f2_score`**，运用 `ray.tune` + `HyperOptSearch` 与 `AsyncHyperBandScheduler` 优化 XGBoost/LightGBM/CatBoost/RF，并将低置信度工单引入移动端 AR 远程预检；同赛题另一获奖方案 *S.H.I.E.L.D* (`[L2]`) 则打造集成了嵌入式照明、AR 相机、语音转文字及手势识别的井道作业智能头盔，实现全程免脱绝缘手套交互。
- **完整技术栈 (tech_stack)**:
  - *AutoML 与误差诊断*: Python, `ray.tune`, `HyperOptSearch`, `AsyncHyperBandScheduler`, `XGBoost` (`binary:logistic`), `LightGBM`, `CatBoost`, `RandomForest`, `f2_score`, PCA/t-SNE 分群诊断.
  - *维保穿戴协同构型*: AR 远程预检闭环 (`ElevAI`), 同赛题 *S.H.I.E.L.D* 穿戴安全帽构想（嵌入式照明 + AR 镜头 + 语音识别 + 手势控制）.
- **端到端系统架构 (architecture)**:
  1. *不均衡工单与子群边界审计*: 针对 `87%` 真实需求（`class 1`）vs `13%` 无效上门（`class 0`）建立 `Groups 0–3` 特征极限诊断，严防“全预测 1”伪高分。
  2. *召回优先自动化超参搜索*: `ray.tune` + `HyperOptSearch` 搜索最平衡的 GBT 模型树结构并锁定 `f2_score`。
  3. *低置信度 AR 复核闭环*: 对存疑派单唤醒工程师远程 AR 核验与全球零件磨损数据回流机制。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 严格锚定安全加权 `f2_score`*：工业维保漏修风险代价远高于误派单，锁定 `f2_score` 后在守住召回底线前提下额外剔除大量无效上门。
  - *决策 2: 坦诚展示不可约噪声子群上限*：利用 PCA/t-SNE 论证 `Groups 0–3` 的理论准确率极限，博得通力资深工程师的绝对信任。
  - *决策 3: 将模型弱点包装为 AR 人机协作产品线*：与同赛题智能安全帽 *S.H.I.E.L.D* 共同指向“井道免手动 AR 远程诊断”真实刚需。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *朴素基线*: `F2 = 0.92299`, `Accuracy = 0.70586`。
  - *ElevAI 模型实测*: **`F2 = 0.926601`**, **`Accuracy = 0.737212`**（精准清除无效上门误报，准确率抬升超 3.1 个百分点且 `F2` 同步走高）。
  - *样本分布与规模*: 87% 真实维保 vs 13% 无效上门；CGI 双赛道合计约 30 支队伍，ElevAI 挺进全场 Top-10。
- **路演与现场亮点 (demo_highlights)**:
  - 大屏直算过滤 13% 无效派单后可为电梯团队节约的巨额高危一线工时，并用直观的 `Groups 0–3` 信心热图赢得导师 Jaakko Uusitalo 认可。
- **团队背景 (team_background)**:
  - *Team Glados*: Ville Toiviainen (`Villux`) 与 Andreas Urbanski (`nardeas`) — Junction 2017 & 2018 两届全场总冠军传奇成员。*(注：同题 Out-of-the-Box 奖 `S.H.I.E.L.D` [L2] 具体成员及代码库未公开。)*
- **获胜逻辑假说 (winning_hypothesis)**:
  高级工业工程诚实度配合商业代价函数精准对齐。敢于在老牌制造业评委面前用数学证明数据噪声上界，再用 AR 人机协同补足边界。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 工业预测性维护赛题务必选对安全代价函数（如 `f2_score`），切勿刷毫无业务意义的 Accuracy。
  - *经验 2*: 把模型的低置信度区间自然嫁接为 AR/穿戴终端的人工预检工位，往往能升华整个工业产品叙事。
- **证明材料与链接 (source_urls)**:
  - [ElevAI 开源仓库 (teamglados/elevai)](https://github.com/teamglados/elevai)
  - [ElevAI 演示视频 (Vimeo)](https://vimeo.com/648187179)
  - [CGI Finland Junction 2021 官方复盘](https://www.cgi.com/fi/fi/blogi/junction-2021-hackathon-highlights)
  - [Wikipedia Junction 历届总冠军条目](https://en.wikipedia.org/wiki/Junction_(hackathon))
- **证据链等级 (evidence_level)**: `L1: 经获奖团队开源仓库 (teamglados/elevai)、Vimeo 演示与 CGI 官方赛后报告验证`

---

### 项目卡片 8: Saavi – Healthy Finance (OP / Finance — Junction 2020 Connected 全场总冠军)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2020`
- **赛事名称 (event_name)**: `Junction 2020 Connected`
- **举办年份 (year)**: `2020`
- **出题机构 (organizer)**: `OP Financial Group` (芬兰金融集团)
- **挑战赛题 (challenge)**: `Finance Challenge (Junction 2020 Connected)`
- **赛题类别 (category)**: `IoT & Hardware / Spatial Mobile Computing (ARKit) & Embedded UX`
- **评审标准 (judging_criteria)**:
  - 疫情线上混合赛制下的技术创新性、实体与数字融合空间体验、系统完整度与全场综合感染力。
- **项目唯一标识符 (project_id)**: `op-saavi-2020`
- **项目正式名称 (project_name)**: `Saavi – Healthy Finance`
- **所获奖项 (award)**: **Junction 2020 Connected 全场总冠军 🏆（主竞赛总大奖）**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  2020 年受新冠疫情影响 Junction 改为远程举办，纯物理硬件实验室供给骤减。*Saavi – Healthy Finance* 凭借“实体物理物件 × 移动 AR 空间计算 × 端云轻量 ML”打破线上视觉疲劳一举夺魁。iOS 原生 `ARKit` 将赞助商实体 OP 银行卡设为空间视觉识别锚点（`ist_card.arreferenceimage`），配合空间轻弹手势速度感知（`abs(v) > 0.03`）让立体账单与订阅消耗悬浮在物理卡片正上方随手转动，并衔接 Docker 容器化的 Flask + `scikit-learn` 预测引擎实时演算下次扣费周期。
- **完整技术栈 (tech_stack)**:
  - *移动端空间 AR 栈*: Swift (iOS), `ARKit` (`ARReferenceImage`), `Alamofire`, `SnapKit`, `Nuke`, `RxSwift`, `RxCocoa`, `AnimatedGradientView`, `FittedSheets`.
  - *后端容器预测引擎*: Docker 化 Python `Flask`, `markupsafe`, `scikit-learn` (`OneHotEncoder`, `LogisticRegression`).
- **端到端系统架构 (architecture)**:
  1. *实体银行卡空间锚定*: 通过 `ARKit` 识别物理卡片视觉纹样（`ist_card.arreferenceimage`），锁定 6-DoF 相对摄像机三维坐标系。
  2. *物理动量手势反馈*: 识别 `abs(v) > 0.03` 的卡片轻弹动作与 `RxSwift` 响应式卡片层切换（`FittedSheets`）。
  3. *Docker 微服务预测 (`antoleb/saavi_back`)*: 对外暴露 `/user/<user_id>`、`/user/subscription_prediction/<user_id>/` 与 `/user/next_two_subscriptions/<user_id>/`，由轻量平衡逻辑回归给出高准确率的周期订阅风险预测。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 借赞助商实体卡打造低门槛硬件交互感*：无需焊接传感器，利用桌面现成 OP 银行卡即实现媲美智能眼镜的 AR 空间交互。
  - *决策 2: 容器化轻量线性模型保障实时响应*：采用 `OneHotEncoder` + 逐服务 `LogisticRegression(max_iter=1e7, class_weight='balanced', C=1e-2)` 杜绝推理阻塞 AR 画面帧率。
  - *决策 3: iOS AR 客户端与预测 Flask 彻底解耦*：双端仓库独立演进并用 Docker 一键拉起调试。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *物理手势阈值*: 轻弹操作触发门限 `abs(v) > 0.03`。
  - *预测模型超参*: `LogisticRegression(max_iter=1e7, class_weight='balanced', C=1e-2)`，训练于 `new_sub.csv`（`service_name`, `service_category`, `number_of_payments`）。
  - *比赛成绩*: Junction 2020 Connected 全场总冠军。
- **路演与现场亮点 (demo_highlights)**:
  - 摄像头扫过实拍 OP 银行卡的瞬间，卡面精准“立”起炫目可旋转的三维健康消费图谱，手指一弹即可预判与划除隐形扣费订阅，在全网录屏评审中拥有极强沉浸辨识度。
- **团队背景 (team_background)**:
  - *Alexander Zimin* (`azimin` — iOS/ARKit 研发), *Anton Lebedev* (`antoleb` — Python Flask/ML 研发), *Andrey Krylov* (`andreykr.com` — 体验 UI/UX 设计), *Andrey Volodin* 与 *Egor Petrov*。
- **获胜逻辑假说 (winning_hypothesis)**:
  全远程赛制中的极强“实物触感破壁”。当全场 95% 参赛者沦为千篇一律的网页 PPT 和静态 Dashboard 时，*Saavi* 用银行卡实体 AR 成功还原了硬件魔术般的体感体验。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 即使赛场缺少传感器开发板，围绕赞助商官方物理实物做 `ARKit`/空间视觉交互，也能打出媲美硬核硬件的视觉护城河。
  - *经验 2*: AR 前台旁搭配 Docker 化的轻快线性模型微服务（`scikit-learn`），比臃肿沉重的大模型稳妥十倍。
- **证明材料与链接 (source_urls)**:
  - [Saavi ML 后端 GitHub 仓库 (antoleb/saavi_back)](https://github.com/antoleb/saavi_back)
  - [Saavi iOS ARKit 客户端仓库 (azimin)](https://github.com/azimin/MoneyMustBeFunnyAkaJunction2020Backup)
  - [Andrey Krylov 设计官网证实](https://www.andreykr.com/media)
  - [YouTube 演示录像](https://www.youtube.com/watch?v=Zc7ce9MxTNg)
  - [Wikipedia Junction 历届总冠军条目](https://en.wikipedia.org/wiki/Junction_(hackathon))
- **证据链等级 (evidence_level)**: `L1: 经两大开源 GitHub 仓库 (saavi_back 与 iOS 客户端备份)、维基百科与作者官网严格验证`

---

### 项目卡片 9: LumenLoop (Helvar & VTT — Making Spaces Brighter with Radar Technology)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2019`
- **赛事名称 (event_name)**: `Junction 2019`
- **举办年份 (year)**: `2019`
- **出题机构 (organizer)**: `Helvar` & `VTT 芬兰国家技术研究中心`
- **挑战赛题 (challenge)**: `Making Spaces Brighter with Radar Technology`
- **赛题类别 (category)**: `IoT & Hardware / Millimeter-Wave Radar & Closed-Loop Actuators`
- **评审标准 (judging_criteria)**:
  - 利用现场 VTT 60 GHz 2D 成像雷达、24 GHz 生命体征雷达与同步 RGB 标注集推断房内/车库人员数量及工作状态，并驱动智能照明调控。
- **项目唯一标识符 (project_id)**: `helvar-vtt-lumenloop-2019`
- **项目正式名称 (project_name)**: `LumenLoop`
- **所获奖项 (award)**: **Helvar & VTT 赛道冠军 🥇**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  绝大多数队伍只基于主办方发布的脱敏离线 CSV 做静态数据分析，而仅两人的 *LumenLoop* 战队在 48 小时内硬核打通了从“现场 VTT 实时 60/24 GHz 毫米波射频流”到“Helvar 物理 BLE Mesh 智能灯具 `EC22`”的全闭环控制。程序从以太网 RabbitMQ 消息队列（`10.84.110.2`）零拷贝读取 FlatBuffers 雷达帧，经差分去噪（`diff/max > 0.13`）换算出精确人数与场景状态，然后调用 `pyserial` 向实体 DALI 网关下发十六进制亮度/色温查找表指令，让展台上的物理灯具实时随着人数变温调光，并同步将数据写入 Elasticsearch 与 React 前端看板。
- **完整技术栈 (tech_stack)**:
  - *射频硬件与消息传输*: VTT 60 GHz FMCW 二维成像雷达 (`160°` 视场, `5 cm` 距离分辨率, `<700 nm` 微动探测, `180x110` @ `100 Hz`), VTT 24 GHz 生命体征雷达 (`1–5 um`), RabbitMQ AMQP (`10.84.110.2`), FlatBuffers (`Vtt60Processed.Sample`, `RadarRawInt.Sample`).
  - *控制与显示栈*: Python, NumPy, `pyserial==3.4`, Helvar DALI BLE Mesh USB 网关 (`EC22`), React (`Demo.js`), Elasticsearch.
- **端到端系统架构 (architecture)**:
  1. *AMQP 零拷贝解包*: 直连 `radar60`/`radar24` 队列并用 FlatBuffers 原生 `AmplitudeAsNumpy()` / `AngleAsNumpy()` 解包百赫兹三维极坐标矩阵。
  2. *动态去噪与人数分类 (`live/Streamer60.py`)*: 剔除环境静止杂波并采用 `diff/max > 0.13` 动态分割室内活跃人数等级。
  3. *DALI 串口物理闭环*: 按照 31 级调光 (`00`..`FE`) 与 39 级色温 (`6500K`–`2700K` / `1964`..`0A8C`) 查表下发串口 hex 报文，直接指挥真机灯具 `EC22`。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 拒停留在仿真界面，亲手点亮真灯 `EC22`*：直面复杂的 AMQP + FlatBuffers + USB 串口 hex 协议，将雷达信号真正变成了物理空间的光影变化。
  - *决策 2: 符合人因工程学的色温照度梯度*: 严密标定 0 人节电极冷待机（`5% / 6500K`）、1 人专注办公（`20% / 5750K`）、2 人双人讨论（`30% / 4850K`）至 3+ 人热烈协同（`60% / 3450K`）四档舒适曲线。
  - *决策 3: Native FlatBuffers 转 NumPy*：省去中间 JSON 序列化消耗，保证 100Hz 实时流绝不积压丢帧。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *60 GHz 雷达指标*: 水平 `160°` / 俯仰 `25°`、距离分辨率 `5 cm`、角分辨率 `3.5°`、微动 `<700 nm`（`180x110` 帧率 `100 Hz`）。
  - *24 GHz 雷达指标*: 水平 `80°`、距离分辨率 `60 cm`、微动 `1–5 um`（`497` 原始信道）。
  - *控灯分辨率与阈值*: 31 级亮度 hex 查表 (`00`–`FE`) x 39 级 Kelvin 色温查表 (`6500K`–`2700K`)；触发门槛 `diff/max > 0.13`。
- **路演与现场亮点 (demo_highlights)**:
  - 评委亲身迈入 VTT 60GHz 雷达扇面的一刻，展位上的实体 Helvar 商用灯具 `EC22` 立马柔和拉升亮度并过渡为温暖会议色温，旁侧 React 大屏实时刷新极坐标点云图。
- **团队背景 (team_background)**:
  - *Denys Kovalenko* (`deniskovalenko` — 后端信号建模与串口控制) 与 *Elizaveta Lebedeva* (`elizavetalebedeva.com` — 数据科学与前端交互)，仅 2 人出战并于 2021 年再夺 Helvar 冠军。
- **获胜逻辑假说 (winning_hypothesis)**:
  完整硬件传感-决策-执行闭环的降维打击。在只剩十几个小时还要手搓二进制 FlatBuffers 和串口 16 进制报文的高压下，用真实物理光变征服了研发方 VTT 与 Helvar 评委。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 主办方桌台只要摆放了真实的物理执行器件，不惜一切代价跑通“真机闭环控制”就是夺冠最优解。
  - *经验 2*: 周五夜里第一时间测试 RabbitMQ / FlatBuffers 等底层协议栈吞吐，避免后期数据格式转化拖垮演示。
- **证明材料与链接 (source_urls)**:
  - [LumenLoop GitHub 开源代码仓库 (deniskovalenko/junction2019)](https://github.com/deniskovalenko/junction2019)
  - [Elizaveta Lebedeva 个人专栏确认](https://elizavetalebedeva.com/tag/junction/)
  - [Junction 2019 官方获奖名单 (Medium)](https://medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f)
- **证据链等级 (evidence_level)**: `L1: 经获奖团队开源代码库 (deniskovalenko/junction2019)、作者博客与 Junction 官方 Medium 获奖名录验证`

---

### 项目卡片 10: AyyHello! (Aalto University AYY — Smart Signage - For Students by Students)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2019`
- **赛事名称 (event_name)**: `Junction 2019`
- **举办年份 (year)**: `2019`
- **出题机构 (organizer)**: `阿尔托大学 & 阿尔托大学学生会 (AYY)`
- **挑战赛题 (challenge)**: `Smart Signage - For Students by Students`
- **赛题类别 (category)**: `IoT & Hardware / Edge Embedded Kiosk, PIR & Touchless CV`
- **评审标准 (judging_criteria)**:
  - 面向 AYY 旗下约 2,600 套公寓楼道（~3,500 租户）打造既具备楼宇热/水/电与网络传感融合深度，又能真正留住学生驻足阅读互动的智慧电子标牌方案。
- **项目唯一标识符 (project_id)**: `aalto-ayyhello-2019`
- **项目正式名称 (project_name)**: `AyyHello! (ayyHello)`
- **所获奖项 (award)**: **阿尔托大学学生会 AYY 赛道第一名 🥇**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  公寓走廊安装触摸屏面临损坏率高、清洁卫生差与日常无人理睬的顽疾。*AyyHello!* 打造了一套极低成本树莓派免触控楼道智能引导终端：平时进入省电息屏模式，一旦走廊行人触发硬件热释电红外上升沿中断（`RPi.GPIO`, `PIR_PIN = 11`, `LED_PIN = 3`）立即唤醒系统与 USB 摄像头，由本地修改版 `MobilePose-PyTorch`（`resnet18`, `224x224`）执行连续 10 帧消抖过滤后输出左/右/上（`L`/`R`/`U`）隔空手势指令，通过 Flask 接口控制 React 终端切换楼宇真实水电能耗数据、HSL 公交发车时刻与体感小游戏。
- **完整技术栈 (tech_stack)**:
  - *树莓派与传感硬件*: Raspberry Pi SBC (`Linux`), PIR 红外热释电传感器 + 提示 LED (`RPi.GPIO`, `GPIO.BOARD` 引脚 `PIR_PIN = 11` / `LED_PIN = 3`), USB 摄像头 (`--camera 0`).
  - *边缘视觉与前后端*: `PyTorch 1.0.0` (`MobilePose-PyTorch` `ResEstimator`, `resnet18` / `mobilenetv2`), `OpenCV 3.4.2.17`, Python `Flask` + `flask_cors`, React `16.12.0`, Material-UI `4.6.1`, `nuka-carousel`, `victory`, `react-google-charts`.
- **端到端系统架构 (architecture)**:
  1. *硬件中断级接近唤醒*: `ayy-lmao/pir.py` 注册 `GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=pir_isr_cb)`，有人走近瞬时点亮状态灯 `LED_PIN = 3`。
  2. *连续 10 帧防抖视觉手势 (`run_webcam.py`)*: 基于 `--model resnet18 --inp_dim 224` 提取上身骨骼关键点并做 10 帧一致稳定性锁定后触发 `L`/`R`/`U`。
  3. *微服务状态看板 (`app.py`, `analysis.py`)*: `POST http://10.42.0.157:5000/dir` 驱动 React 轮播页，后端自动跳过 52 行元数据头解析 `SMT8-12_*.csv`（分号 `;` 分隔）提供 `/el`, `/heat`, `/water` 柱状趋势。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 坚持公共楼道纯隔空交互*：用“PIR + 隔空姿态”替代成本昂贵且易遭磕碰划伤的电容触摸屏。
  - *决策 2: 10 帧简单确定性防抖胜过复杂 3D-CNN*：在展厅过道背影干扰极大的状态下，连续 10 帧投票锁定彻底消除手势抖动。
  - *决策 3: GPIO、CV 与 Web 前端分进程本地 HTTP 解耦*：确保负责焊接引脚、调参 PyTorch 与画 React 图表的 5 位队友开发互不卡脖子。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *姿态推理网输入*: `--model resnet18 --inp_dim 224` (`224x224`)。
  - *稳定抗干扰周期*: 连续 `10` 帧同手势一致方下发控制 (`L`/`R`/`U`)。
  - *覆盖资产基线*: 对标 AYY 全盘约 `2,600` 套学生公寓与 `3,500` 名住户，实盘清洗 `SMT8-12_*.csv` 时序能耗档案。
- **路演与现场亮点 (demo_highlights)**:
  - 评审走近瞬间点亮 LED 与唤醒屏幕，隔空向左/右挥手即可切屏浏览刚出炉的公交时刻表、宿管水电碳排排名与减压小游戏，毫无卡顿误触。
- **团队背景 (team_background)**:
  - 五人阿尔托与芬兰技术联队：*Mari Porko* (`mariporko`), *Harri Rahikainen* (`HRahikainen`), *Jesse Tolvanen* (`JZNT`), *Satria Sutisna* (`satriasutisna`) 及 `smirq`。
- **获胜逻辑假说 (winning_hypothesis)**:
  “高频生活实用信息包裹楼宇物联网指标 + 无故障嵌入式交互设计”。学生会深知没人愿意看干瘪的暖通报表，加上刚需公交发车时刻与防手抖体感控制自然全票通过。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 凡在喧嚣黑客松现场做摄像头手势 Demo，必须设计至少 8–10 帧的时间消抖状态机（Temporal Debounce）过滤路人干扰。
  - *经验 2*: 将 `RPi.GPIO` 硬件监控脚本、深度学习推理和 Web 屏端分别封成独立本地进程 HTTP 协同，联调极稳。
- **证明材料与链接 (source_urls)**:
  - [AyyHello! GitHub 仓库 (mariporko/junction2019)](https://github.com/mariporko/junction2019)
  - [协同仓库分枝 (HRahikainen/junction2019)](https://github.com/HRahikainen/junction2019)
  - [Junction 2019 官方获奖名单 (Medium)](https://medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f)
  - [阿尔托大学 AYY 赛题官方报道](https://www.aalto.fi/en/news/student-union-looks-for-creative-ideas-for-their-information-channels-from-junction)
- **证据链等级 (evidence_level)**: `L1: 经获奖团队 GitHub 开源仓库 (mariporko/junction2019)、阿尔托大学新闻与 Medium 官方名录验证`

---

### 项目卡片 11: Help.io / Team Health.io (Intel — Innovative Applications With Bluetooth Mesh)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2018`
- **赛事名称 (event_name)**: `Junction 2018`
- **举办年份 (year)**: `2018`
- **出题机构 (organizer)**: `Intel`（现场提供 8 套硬件套件，协同 `Movesense by Suunto` 生理传感硬件）
- **挑战赛题 (challenge)**: `Innovative Applications With Bluetooth Mesh`
- **赛题类别 (category)**: `IoT & Hardware / Bluetooth Mesh Gateways, Edge Triage & Wearables`
- **评审标准 (judging_criteria)**:
  - 构建运行于边缘物联网网关上的突破性应用，深度调用 Bluetooth Mesh 无线网状传感节点能力（智能电子徽章、离线通信与照明告警，不依赖外网/云端连接）。
- **项目唯一标识符 (project_id)**: `intel-helpio-2018`
- **项目正式名称 (project_name)**: `Help.io / Team Health.io`
- **所获奖项 (award)**: **Intel 赛道第一名 🥇 + 物联网 IoT 大赛道总冠军 🏆 + Junction 2018 全场总亚军 🥈（300+ 项目中排名第 2）**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  灾难现场基站毁坏断网后，一线急救队员亟需零蜂窝、自组网的多伤员生命体征跨区通报系统。曾在 2017 年夺得 Movesense 冠军的拉脱维亚大学原班骨干，于 2018 年将两枚 Suunto Movesense 胸带传感器与 Intel 前沿的 **Bluetooth Mesh** 实验开发套件（`intel/Junction2018`, `feri/Junction2018_Support`）强强耦合：患者端 Movesense 传感器经蓝牙读取心率及 R-R 间期并传入 iOS 12 端侧实时分诊引擎；一旦危急（超越 `60`–`110` BPM 或 R-R 突变倍率 `2.0`），iOS 直接向本地局域网内的 **Intel NUC 网关**（`10.100.5.16:3000/{bluetoothId}/critical`）发出触发请求，推动 NUC 内的 `BlueZ meshd-ingas` 与 `nRF51_dongle` 经蓝牙 Mesh 泛洪点亮分布式 4 块 Zephyr OS **PHYTEC `reel_board`** 救援电子墨水屏徽章，全链无需任何外网支持。
- **完整技术栈 (tech_stack)**:
  - *生理穿戴端*: Suunto Movesense BLE 传感器（实码序列号 `175030001053`->节点 `0x0001`, `175030000988`->`0x0002`, 订阅 `Movesense.HR_PATH`）.
  - *移动端边缘分诊*: iOS 12 / Swift (`Movesense SDK`, `AsyncDisplayKit`/`Texture`, `PromiseKit`, `Bond`, `SwiftyJSON`, `Alamofire`, `ScrollableGraphView`).
  - *蓝牙 Mesh 基础设施*: Intel NUC (Linux, 无线子网 `jnct-ble5-mesh`), 实验版 `BlueZ` (`meshd-ingas` 分支, `ell 0.13`, D-Bus 服务 `org.bluez.mesh1`), `nRF51_dongle` (`hci_uart`), 4 块 PHYTEC `reel_board` (`Zephyr OS` `mesh_badge`, 模型 `0x0000` Vendor / `0x1000` Generic OnOff / `0x1102` Sensor 温度 `0x2a1f`).
- **端到端系统架构 (architecture)**:
  1. *穿戴传感采集*: Movesense 蓝牙传输平均心率与毫秒级 R-R 间期至靠近伤员侧的 iOS 端。
  2. *端侧容错分诊状态机*: 先行丢弃 `discardCount = 5` 初始化噪点并要求缓冲队列 `heartRateHistory.count >= 15`，再按可控阈值触发告警状态。
  3. *HTTP-to-BlueZ Mesh 异构网关*: iOS 客户端借助 `Alamofire` 向 Intel NUC 网关发送本地 REST 请求（`10.100.5.16:3000/{bluetoothId}/{setup / critical}`），驱动 `nRF51_dongle` 将报警指令与病人区位分发至 4 块 Zephyr Mesh 电子徽章。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 用极简 HTTP 桥隔离早期不稳定的 `BlueZ meshd`*：Intel 的 `meshd-ingas` 分支在赛前几天刚合并提交，将其严格封在 NUC HTTP 网关后方，使 iOS SDK 团队零阻塞高效联调。
  - *决策 2: 在代码中预留清晰可调的临床/演示两套阈值*：设定现场演练安全门限（`60`–`110` BPM），确保上台高强度活动立刻稳健亮起 Mesh 徽章告警。
  - *决策 3: 遵循标准 Mesh Model 操作码（`0x8202`, `0x8231`）*：吃透 Intel 官方 `Junction2018_Support` 工具，借力蓝牙标准化模型实现多硬件协同而非私有轮询。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *套件配比与生态*: Intel 全场仅向 8 支队配发套件（每套 `1x NUC + 1x nRF51_dongle + 4x reel_board`）；Movesense 共 26 支队伍参赛。
  - *代码实证分诊常数*: `discardCount = 5`、`heartRateHistory >= 15`、`lowestHRBound = 60.0`、`highestHRBound = 110.0`、`highestRRMultiplier = 2.0`。
  - *名次突破*: **Intel 冠军 + IoT 赛道总冠军 + 全场 300+ 项目第 2 名**（进入 11 强决赛圈）。
- **路演与现场亮点 (demo_highlights)**:
  - 在彻底断开互联网路由的演示现场，演示者剧烈运动跨越阈值瞬间，分布式 `reel_board` 救护员电子墨水屏徽章全部同步亮灯并发出精确扇区呼救（`0x0001` / `0x0002`），旁侧 iOS 用 `ScrollableGraphView` 实时描画心电节拍。
- **团队背景 (team_background)**:
  - 拉脱维亚大学计算机学院战队：*Austris Cīrulnieks*、*Mārcis Nīmants* (`mnimants`)、*Elvijs Viļķels*、*Aigars Cibuļskis* 与 *Dāvis Mednis* *(团队中 4 人在 2017 年曾夺得 Movesense 健康赛冠军 ReCover)*。
- **获胜逻辑假说 (winning_hypothesis)**:
  老练的异构系统解耦与不可辩驳的“无网自组 Mesh 实物触发”。团队没有盲目在实验版 Linux 蓝牙栈上硬写 UI，而用简洁网关层无缝黏合工业开发板与商用穿戴，堪称 Junction 硬件双栈工程范本。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 主办方发到手的极早期芯片固件/协议栈（如 BlueZ Mesh、新型 SDK）最怕与上层生态冲突——尽快用标准本地 HTTP/MQTT 网关隔离出清晰职责边界。
  - *经验 2*: 开赛第一晚把官方支持仓（`Junction2018_Support`）翻透，直接沿用原厂预设 UUID / Model Opcode 能省掉一天踩坑时间。
- **证明材料与链接 (source_urls)**:
  - [Help.io 官方 GitHub 代码库 (mnimants/junction2018)](https://github.com/mnimants/junction2018)
  - [Intel 官方 Mesh 源码库 (intel/Junction2018)](https://github.com/intel/Junction2018)
  - [Intel 支持配置工具箱 (feri/Junction2018_Support)](https://github.com/feri/Junction2018_Support)
  - [Movesense 官方 2018 战报](https://www.movesense.com/news/2018/11/movesense-shined-in-junction-hackathon/)
  - [拉脱维亚大学官方新闻通告](https://eztf.lu.lv/en/about-us/news/detail-view/t/98941/)
- **证据链等级 (evidence_level)**: `L1: 经冠军开源仓库 (mnimants/junction2018)、Intel 官方支持仓库、Movesense 官方战报与拉脱维亚大学公告证实`

---

### 项目卡片 12: Oneiro — Team Glados (Ensto — Teach EV Chargers New Tricks)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2018`
- **赛事名称 (event_name)**: `Junction 2018`
- **举办年份 (year)**: `2018`
- **出题机构 (organizer)**: `Ensto` (Ensto Flow 智能电动车充电 — 评审负责人：软件总监 Ville Parviainen)
- **挑战赛题 (challenge)**: `Teach EV Chargers New Tricks`
- **赛题类别 (category)**: `IoT & Hardware / Edge Vision, Smart EV Chargers & Mobility`
- **评审标准 (judging_criteria)**:
  - 结合现场 Ensto 商用充电桩硬件开发板及 EnstoFlow IoT REST API (`RealDevice` OCPP 控制)，从 14 支参赛队中遴选最具技术深度、商业闭环可行性与交互体验的创意方案。
- **项目唯一标识符 (project_id)**: `ensto-oneiro-2018`
- **项目正式名称 (project_name)**: `Oneiro (Team Glados)`
- **所获奖项 (award)**: **Junction 2018 全场总冠军 🏆 (€20,000 现金大奖) 兼 Ensto 赛道第一名 🥇（Ensto 双挑战共 14 支参赛队）**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  针对城市电动充电桩分布不足与闲置率高的结构错配，Team Glados 打造了由树莓派边缘视觉驱动的私家充电桩共享平台（被芬媒誉为“充电桩 Airbnb”）。核心硬件环采用树莓派 + PiCamera 在 `systemd` 服务监护下每 `0.5s` 抓拍 `640x480` 画面发送至 Python `Sanic` 后端与 Docker 化 `openalpr:16.04` 车牌识别引擎；凡识别欧盟/芬兰号牌置信度超过 `75` 立即通过 `EnstoFlow` REST API 下发 `spot_enable()` 与 OCPP 启动交易指令，**物理控制真实 Ensto Chago 商用充电桩（`JunctionEVB1`）状态灯转蓝并正式上电供电**，更以 Telia 电信蜂窝人流大数据在 Mapbox GL 绘制商业选址热力图。
- **完整技术栈 (tech_stack)**:
  - *边缘采集与商用电桩硬件*: 树莓派 Raspberry Pi + PiCamera (`systemd` `photographer.service`), **Ensto Chago 商用电动车充电桩** (`JunctionEVB1` `RealDevice` OCPP `A -> C` 模式).
  - *视觉识牌与控制中台*: Docker 化 `openalpr:16.04` (`country="eu"`, `default_region="fi"`), Python 3 + `Sanic` (`8000` 端口), `EnstoFlow` REST API v1 (HTTP Basic Auth).
  - *客户端、选址地理与云运维*: React Native (`sdk-31.0.0`, Expo `^31.0.2`, Redux-Saga, Axios), `Mapbox GL JS v0.51.0` (Telia Uusimaa 蜂窝基站人流), Terraform + AWS (`t2.nano`, ELB, ECR, S3, CloudFront, Route53).
- **端到端系统架构 (architecture)**:
  1. *自愈式边缘采样 (`raspberry/photographer.py`)*: 每 `0.5s` (2 FPS) 抓拍 `640x480` JPEG 并以 `2s` 强超时向 `/postimage` 推送图像帧。
  2. *容器化车牌推理 (`server/licence_plate.py`)*: 调用 `openalpr:16.04` 计算 `top_n = 5` 候选项，匹配车主数据库且 `confidence >= 75` 时瞬间放行。
  3. *OCPP 真实充电桩控制 (`server/enstoflow.py`)*: 查询 `chargingPointGroup` 并下发 `{connector}/starttransaction/{tag}`，真实开启 `JunctionEVB1` 物理硬件充电过程并同步在 `Mapbox GL` 揭示城区供电缺口。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 用汽车牌照无感视觉鉴权取代扫码充电*：严寒雨雪场景下车主无需下车掏手机扫码，驶入即被 PiCamera 无感放行充电。
  - *决策 2: 跨赛题引入 Telia 移动基站热力数据论证商模*：不止步于控制继电器通断，用 `Uusimaa_activity_data` 精确测算私人共享充电桩的潜在租金回报热区。
  - *决策 3: 为无人值守 Pi 节点加满保护锁*：`systemd` 崩溃自动拉起配合严格 `2s` 请求超时，彻底防止弱网环境堵死边缘推流。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *边缘视频采样频率*: `0.5 s`（2 FPS）`640x480` 画面捕获，强超时 `2 s`。
  - *车牌鉴权准确门槛*: `top_n = 5` 识别列表匹配且阈值 `confidence >= 75` 自动开桩。
  - *竞赛战绩*: **全场总冠军 €20,000**（1,200–1,300 参赛者、300+ 项目）+ Ensto 赛道第一名（14 支竞争队）。
- **路演与现场亮点 (demo_highlights)**:
  - 在主办方展位前手持测试车牌靠近树莓派镜头，大屏幕上车牌识别毫秒级命中并通过 OCPP 真机点亮 Ensto Chago（`JunctionEVB1`）状态灯，同时 Mapbox GL 大屏热图锁定赫尔辛基热门供需差区。
- **团队背景 (team_background)**:
  - *Team Glados*: *Teemu Taskula* (`Temzasse`)、*Andreas Urbanski* 与 *Ville Toiviainen* (`Villux`) — **极罕见地蝉联 Junction 2017 (*Signvision*) 与 Junction 2018 (*Oneiro*) 两届全场总冠军**。
- **获胜逻辑假说 (winning_hypothesis)**:
  真硬件控制能力与顶格商业完整度完美交汇。Ensto 软件总监 Ville Parviainen 赛后公开盛赞该项目实现了“极佳的 Ensto 真实接口整合 × 无懈可击的商业盈利测算 × 一流的用户界面”。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 使用光学识别/无线无感认证替换用户端多余点击交互，能让笨重工业外设呈现惊艳未来感。
  - *经验 2*: 边缘单片机/树莓派采样代码务必小巧带强超时并交由 `systemd` 托管，识别计算重担卸载至容器后端。
- **证明材料与链接 (source_urls)**:
  - [Oneiro GitHub 官方代码仓库 (teamglados/oneiro)](https://github.com/teamglados/oneiro)
  - [Oneiro Vimeo 官方路演录像](https://vimeo.com/302650304)
  - [Talotekniikka-lehti 芬兰行业报道](https://talotekniikka-lehti.fi/oneiro-voitti-junction-2018-hackathonin/)
  - [Mobiili.fi 冠军专访](https://mobiili.fi/2018/11/25/junction-hackathon-espoossa-paattyi-latauspisteiden-airbnbn-voittoon-sama-tiimi-voitti-kilpailun-viime-vuonnakin/)
- **证据链等级 (evidence_level)**: `L1: 经冠军开源仓库 (teamglados/oneiro)、演示视频与多家芬兰权威科技媒体确认`

---

### 项目卡片 13: GuideMe — Makers UPV (Future Cities 赛道 — 全场第 4 名)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2018`
- **赛事名称 (event_name)**: `Junction 2018`
- **举办年份 (year)**: `2018`
- **出题机构 (organizer)**: `Future Cities Track` (Junction 2018 主竞赛前五强赛道)
- **挑战赛题 (challenge)**: `Future Cities Challenge`
- **赛题类别 (category)**: `IoT & Hardware / Assistive Dual-MCU Hardware & Custom CAD`
- **评审标准 (judging_criteria)**:
  - 软硬件一体化工程完整度、城市弱势群体适老化与无障碍影响、实体穿戴/手持可用性与城市规模化价值。
- **项目唯一标识符 (project_id)**: `futurecities-guideme-2018`
- **项目正式名称 (project_name)**: `GuideMe`
- **所获奖项 (award)**: **Future Cities 赛道总冠军 🥇 (€1,000) 兼 Junction 2018 全场总第 4 名（300+ 项目中列第 4）**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  长者和视障人士步行时边看手机地图极易绊倒发生危险。西班牙瓦伦西亚理工大学精锐战队 Makers UPV 在 48 小时内从零完成机械结构、双控电路与导航软件全栈工程 *GuideMe*：团队在现场通过 SolidWorks 建模并 3D 打印出人体工学拐杖手柄外壳（`guideme_handle.SLDPRT` / `.STL`），内部嵌入两颗分工明晰的单片机——由 Wemos `ESP8266` 从 Google Maps Directions PHP 后台拉取步行节点方位，再经 `115200 baud` UART（`pins 0/2`）交由 `BBC micro:bit`；后者凭借内置磁力计实时对齐行人面朝方向，使用 5x5 LED 矢标并配合 `pin 1` 触觉震动/蜂鸣零手机屏幕引路，并支持家人网页端实时看护追踪。
- **完整技术栈 (tech_stack)**:
  - *双单片机嵌入式架构*: `BBC micro:bit` (ARM Cortex-M0, 磁力计, 5x5 LED 点阵, MicroPython `micro.py`), `Wemos ESP8266` (Arduino C++ `guideme_arduino_wifi_node.ino`).
  - *三维外壳与导航后端*: SolidWorks CAD (`guideme_handle.SLDPRT`) 与 `.STL` 3D 打印模型, `PHP` (`web/back.php`, `web/front.php`), Google Maps Directions API, HTML / jQuery / AJAX.
- **端到端系统架构 (architecture)**:
  1. *照护家人 Web 端 (`web/front.php`, `back.php`)*: 远端输入出行目的地并基于 AJAX 实时监测长者步行动态点位。
  2. *Wi-Fi 串口通信节点 (`guideme_arduino_wifi_node.ino`)*: `ESP8266` 专注轮询路径节点并通过 `115200` 波特率串口下发目标方位角。
  3. *地磁罗盘与触觉执行器 (`micro.py`)*: `BBC micro:bit` 读取磁力计比对航向偏差，即时驱动手柄顶部 5x5 LED 转向图标并经 `pin 1` 输出震动与蜂鸣引导。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 双 MCU 职责彻底解耦*：把耗资源容易阻塞的 Wi-Fi HTTP 请求全扔给 `ESP8266`，保留轻快的 `micro:bit` 实时跑地磁滤波与 `pin 1` 触觉震动，开发稳定零冲突。
  - *决策 2: 现场 SolidWorks 建模并 3D 打印成品握把*：开源仓保留完整 `.SLDPRT`/`.STL`，把所有跳线和电池干净封印入可单手握持的手杖外壳。
  - *决策 3: 视觉LED与纯触觉多模态互补*：既照顾低视力长者的余光箭头阅读，也为全盲人士保留盲操震动方向提示。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *底层总线通信*: `115200 baud` UART 跨板通信 (`pin 0` / `pin 2`)，触觉/蜂鸣执行端绑定 `pin 1`。
  - *实体工程文件*: 仓库实证含完整 SolidWorks 零件设计及 `.STL` 打印结构件。
  - *赛事战果*: **全场总榜第 4 名**（300+ 提交项目中紧随 Oneiro、Help.io 之后）+ Future Cities 赛道冠军 (€1,000)。
- **路演与现场亮点 (demo_highlights)**:
  - 手持 3D 打印智能手杖手柄原地转向，顶置 `micro:bit` LED 箭头随空间方位实时补偿指向并在偏差时刻发出规律震动脉冲，大屏幕同步刷新长者定位轨迹。
- **团队背景 (team_background)**:
  - 西班牙瓦伦西亚理工大学（UPV）跨学科精锐五人战队 *Makers UPV*：*Jaime Laborda Macario*、*Iván Torres Játiva*（电子工程）、*Enrique Miralles Dolz*（核聚变工程）、*Joaquín Montesinos Muñoz*（电信工程）与 *Matías Fernández Patón*（生物医学工程）。
- **获胜逻辑假说 (winning_hypothesis)**:
  令人惊叹的机械 CAD × 双单片机 × Web 看护全链成品完成度。五名不同学科工程师 48 小时协同作战直接拿出像商业预研样机一样的实体手杖，高居全场第四。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 使用 `ESP8266` 专门管无线联网 + 伴生微控制器专注实时传感和舵机/震动输出（`115200` 串口对接），比单芯片死扛一切稳定十倍。
  - *经验 2*: 一款现场 3D 打印出来的合身工业结构件外壳，能让硬件作品在评审桌上呈现压倒性的产品完成感。
- **证明材料与链接 (source_urls)**:
  - [GuideMe 官方开源代码仓库 (makers-upv/GuideMe)](https://github.com/makers-upv/GuideMe)
  - [瓦伦西亚理工大学 UPV 官方报道](https://www.upv.es/noticias-upv/noticia-10627-junction-2018-es.html)
  - [Mobiili.fi 芬兰决赛报道](https://mobiili.fi/2018/11/25/junction-hackathon-espoossa-paattyi-latauspisteiden-airbnbn-voittoon-sama-tiimi-voitti-kilpailun-viime-vuonnakin/)
- **证据链等级 (evidence_level)**: `L1: 经冠军开源仓库 (makers-upv/GuideMe)、UPV 官方新闻稿与芬兰科技媒体决赛报道证实`

---

### 项目卡片 14: Make Sauna Great Again / MaSGA (Vaisala — Hack the Sauna)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2018`
- **赛事名称 (event_name)**: `Junction 2018`
- **举办年份 (year)**: `2018`
- **出题机构 (organizer)**: `Vaisala（维萨拉）`（评审官：Sampsa Lahtinen, Ari Alanko, Riku Hakala）
- **挑战赛题 (challenge)**: `Hack the Sauna`
- **赛题类别 (category)**: `IoT & Hardware / Extreme-Environment Multi-Sensor Analytics`
- **评审标准 (judging_criteria)**:
  - 将维萨拉工业精密多物理量传感器探头（温度、相对湿度、比焓 Enthalpy、CO2 与 O2）接入桑拿严酷高湿热场景，输出具商业与体感价值的新一代智能监测应用。
- **项目唯一标识符 (project_id)**: `vaisala-masga-2018`
- **项目正式名称 (project_name)**: `Make Sauna Great Again (MaSGA)`
- **所获奖项 (award)**: **Vaisala “Hack the Sauna” 赛道冠军 🥇（赛后学术论文入选 IEEE IECON 2020）**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  传统双金属桑拿机械温度计只看单一位置温度，忽略空间分层热梯度、二氧化碳憋闷与湿热比焓失衡。*MaSGA* 团队实时接入现场五路分布式维萨拉工业探头（`Stove1`、`Bench1–3`、`Floor1`）在 `apigtw.vaisala.com` 释放的多维物理遥测，但团队没有主观臆造舒适公式，而是**直接在 instrumented 桑拿房内采集了 22 份浴客真实 10–15 分钟以上的体感调研问卷作为真值**，在 Google Cloud Functions Python 引擎（`Addono/masga-backend`）中构建梯形模糊相似度模型（`quadro()`），每 `10s` 向客户端给出清晰直观的绿/橙/红状态与人话指令（“立刻泼水加湿 / 开门通风”或运营端功率调优）。
- **完整技术栈 (tech_stack)**:
  - *多点工业探头与接口*: 维萨拉多点高温高湿传感系统（测量温度、RH、比焓、CO2 与 O2，部署于 `Stove1` / `Bench1–3` / `Floor1`），Vaisala REST API 网关 (`/saunameasurements/latest`).
  - *模糊计算云端与看板*: Python on Google Cloud Functions (`main.py`), 梯形模糊相似匹配函数 (`quadro()`), Bootstrap 4.1.3, jQuery 3.3.1 (`10s` 周期轮询).
- **端到端系统架构 (architecture)**:
  1. *空间立体传感输入*: 五组工业探头连续监测炉石、长凳及地面微环境物理梯度。
  2. *真值校准模糊求解器 (`quadro()`)*: 云函数基于 22 位真人桑拿体验调研标定理想区间，输出区分 *浴客 (user)* 与 *运营主管 (manager)* 的标准化健康得分。
  3. *双角色行动指引前端*: 每 `10s` 刷新并按 `>88%` 绿 / `>75%` 橙 / `<=75%` 红阈值弹出精确行动建议。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 现场采集 22 份真人体验样本建立真值基准*：让 `70 °C`、`800 ppm` CO2、`17%` O2 等目标区间站住科学脚跟。
  - *决策 2: 梯形模糊相似方程 `quadro()` 替代脆性硬切阈值*：科学处理多个热力学变量间的耦合偏离（后续正式发表 IEEE IECON 2020 论文）。
  - *决策 3: Bather 与 Operator 双角色界面隔离*：避免向普通用户塞入艰深比焓数据，直接翻译为可执行的物理改善提示。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *真人标定数据集*: `22` 份进入监控桑拿房持续 `>= 10–15 min` 的真实用户体验调查。
  - *遥测同步周期与等级*: `10 s` 轮询刷屏；UI 阈值分级 `> 88%` 绿（完美）、`> 75%` 橙（下降）、`<= 75%` 红（较差）。
  - *学术衍生成果*: 赛后方法扩展发表于 IEEE IECON 2020（收录于 `aaltodoc.aalto.fi`）。
- **路演与现场亮点 (demo_highlights)**:
  - 录像（`https://youtu.be/rNtnsDjz0vM`）现场切换普通浴客提示（提醒 CO2 过高请开门透气）与桑拿运营店长工程功率调校视图。
- **团队背景 (team_background)**:
  - 阿尔托大学等联合科研团队：*Siavash H. Khajavi*（Aalto DIEM 博士后）、*Alireza Jaribion*（Aalto 研究员）、*Adriaan Knapen*（`Addono`, Aalto EIT）、*Leila Abiedat* 与 *Arnab Banik*。
- **获胜逻辑假说 (winning_hypothesis)**:
  黑客松罕见的“现场人类真值标定科学严谨度 × 清晰的动作引导产品设计”。维萨拉评审团一眼看出算法不仅在黑客松跑通，甚至具备直接进入学术论文和商业仪表盘的高水准。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 哪怕只有短短两晚，在现场亲自抓 20 来位体验者收集真值样本（Ground-Truth Survey），传感器算法瞬间与“瞎调参组”拉开质的区别。
  - *经验 2*: 不要只把传感数字画成折线图丢给用户——帮不同角色直接译出一句动作指示。
- **证明材料与链接 (source_urls)**:
  - [MaSGA 云函数后端 GitHub (Addono/masga-backend)](https://github.com/Addono/masga-backend)
  - [MaSGA 前端仪表盘 GitHub (Addono/masga)](https://github.com/Addono/masga)
  - [Vaisala 官方赛后获奖通告](https://www.vaisala.com/en/blog/2018-11/winners-vaisalas-challenges-junction-2018-hacked-weather-and-sauna)
  - [阿尔托大学官网专访报道](https://www.aalto.fi/en/news/winning-team-hack-the-sauna-experience-to-a-new-level-at-junction)
  - [IEEE IECON 2020 论文归档 (Aaltodoc)](https://aaltodoc.aalto.fi/items/44b6d03b-0849-4381-a9e4-300de579f7d3)
  - [MaSGA 现场路演视频 (YouTube)](https://youtu.be/rNtnsDjz0vM)
- **证据链等级 (evidence_level)**: `L1: 经冠军前后端仓库、Vaisala 官方战报、Aalto 新闻稿与 IEEE IECON 2020 学术归档验证`

---

### 项目卡片 15: TerrainSense (Movesense & Stara — Track Anything That Moves / StreetReboot2)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2018`
- **赛事名称 (event_name)**: `Junction 2018`
- **举办年份 (year)**: `2018`
- **出题机构 (organizer)**: `Movesense by Suunto` & `赫尔辛基市政工程局 Stara`
- **挑战赛题 (challenge)**: `Track Anything That Moves / Stara StreetReboot2`
- **赛题类别 (category)**: `IoT & Hardware / Crowdsourced Infrastructure IMU & Smart City`
- **评审标准 (judging_criteria)**:
  - 基于可编程 Movesense IMU 传感器的真实应用价值与原型就绪度，叠加城市基础设施巡检落地效用（Stara StreetReboot2）。
- **项目唯一标识符 (project_id)**: `movesense-terrainsense-2018`
- **项目正式名称 (project_name)**: `TerrainSense`
- **所获奖项 (award)**: **Movesense 赛道多挑战联合第一名 🥇 & 赫尔辛基市政 Stara StreetReboot2 亚军 🥈 (€1,000)**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  城市非机动车道里程动辄数千公里，市政专车路面普查频次低且费用极其高昂。*TerrainSense* 打破“运动传感器只能戴手腕/胸口测人体心率”的思维定式，创造性地将轻量编程式 **Suunto Movesense** IMU 直接卡装在通勤自行车的后轮车轴/后叉上（`taka-akseli`）。骑行过程中产生的路面坑洼、树根顶拱高频振动经 BLE 实时传入 Android 手机对齐 GPS 坐标，并导出标准 GPX 路径至 AWS S3/EC2 云端生成城市非机动车道破损严重度热力图——赛后顺利转化为**赫尔辛基市、Forum Virium、HAMK 与 InnoTrafik 三项多年度真实试点项目**并扩展 AWS Rekognition 道路视觉识别。
- **完整技术栈 (tech_stack)**:
  - *端侧感测与移动端*: Suunto Movesense 可编程 IMU 传感器 (BLE), Android App (GPS + BLE 同步记录), 标准 GPX 空间导出.
  - *云端与后续试点视觉*: AWS S3 / AWS EC2 市政道路破损热力网 *(赛后试点新增 AWS Rekognition 道路视频识别)*.
- **端到端系统架构 (architecture)**:
  1. *物理载具刚性安装*: 在自行车后轮轴（`taka-akseli`）刚性固定 IMU，不受骑行者手臂屈伸阻尼衰减干扰。
  2. *边缘时空融合*: Android App 持续融合 BLE 高频颠簸脉冲与 GPS 坐标流封装为标准 GPX 文件。
  3. *市政热力巡检台*: AWS 云端汇聚多位骑手轨迹渲染全城自行车道待维修热力排期表（`TerrainSense_Junction_presentation.pdf`）。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 把传感器戴到交通工具轴心上而非人身*：规避手臂悬架缓冲，直接捕获最真实的路面高频凹凸冲击。
  - *决策 2: 精准双赛题叠加攻略*：同步切入 Movesense 硬件赛题与赫尔辛基市 Stara 城市道路数据赛题，通吃两个金主奖金。
  - *决策 3: 输出行业通用 GPX 轨迹*：保障市政 GIS 工程师无需二次洗数据即可直接叠加市政地图巡检维修。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *硬件赛道规模*: Movesense 周五领出 `18` 套、周六升至 `35` 队、共 `26` 个完赛作品（`movesense.com`）。
  - *市政官方奖金 (`HEL 2019-003563`)*: Stara StreetReboot2 **€1,000 亚军** + **Movesense 最佳多赛题组合一等奖**。
  - *商业试点延续*: 赛后真实推进了 **3 项**联合赫尔辛基市、Forum Virium 及 HAMK 参与的实地工程试点。*(源码仓未公开 `[L1/L2]`。)*
- **路演与现场亮点 (demo_highlights)**:
  - 展示实测骑行原始颠簸信号如何精准定位赫尔辛基市具体哪几段自行车道需要优先铺路修补（并留存官方 Movesense 汇报 PPT 佐证）。
- **团队背景 (team_background)**:
  - *Ville Saramaa*（`vill.dev`）及北欧跨界研发成员 *(赛后与 HAMK 应用科技大学、InnoTrafik 持续合作落地试点)*。
- **获胜逻辑假说 (winning_hypothesis)**:
  绝妙的硬件载具跨界位置选择叠加精确双赛题商业捆绑。区区数十欧元的蓝牙穿戴 IMU，贴到单车后轴瞬间变身为市政基建大数据采集车队，自然进入城市采购试点名录。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 将通用硬件开发套件与一个行业/市政端业务赛题联动，最容易触发 1+1>2 的复利获奖效应。
  - *经验 2*: 多思考传感器还能贴到哪些“非人类肢体”载体（车轴、水管、电梯导轨），往往秒杀全场同质穿戴队。
- **证明材料与链接 (source_urls)**:
  - [Movesense 官方 2018 战报](https://www.movesense.com/news/2018/11/movesense-shined-in-junction-hackathon/)
  - [TerrainSense 官方介绍 PPT (PDF)](https://www.movesense.com/wp-content/uploads/2018/12/TerrainSense_Junction_presentation.pdf)
  - [赫尔辛基市政府正式授奖公文 HEL 2019-003563](https://paatokset.hel.fi/fi/asia/hel-2019-003563)
  - [Ville Saramaa 个人作品集](https://vill.dev/projects/)
  - [HAMK 自行车道传感器研究试点报告](https://unlimited.hamk.fi/teknologia-ja-liikenne/pyoravaylien-kunnon-tutkiminen-sensoriteknologian-keinoin/)
- **证据链等级 (evidence_level)**: `L1: 经 Movesense 官方演讲 PDF、赫尔辛基市政公文 (HEL 2019-003563) 与 HAMK 试点文献证实`

---

### 项目卡片 16: IVision Lamp — 清华-商汤未来深度学习战队 (Helvar — The Brain of the Building)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2018`
- **赛事名称 (event_name)**: `Junction 2018`
- **举办年份 (year)**: `2018`
- **出题机构 (organizer)**: `Helvar` (智能照明与建筑环境系统)
- **挑战赛题 (challenge)**: `The Brain of the Building`
- **赛题类别 (category)**: `IoT & Hardware / Smart Luminaires & Multi-Sensor Vision Fusion`
- **评审标准 (judging_criteria)**:
  - 将照明传感器数据与建筑环境控制中枢融合，打造自主调节环境舒适度、激发生产力并自动发现异常的智慧“建筑大脑”。
- **项目唯一标识符 (project_id)**: `helvar-ivision-lamp-2018`
- **项目正式名称 (project_name)**: `IVision Lamp`
- **所获奖项 (award)**: **Helvar “现代建筑智能大脑”赛道冠军 🥇（清华大学队伍历史上首次荣获 Junction 挑战赛道第一名）**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  针对传统照明灯具仅凭单一亮暗或红外简单触发、缺乏空间语义理解的问题，清华大学 × 商汤科技未来深度学习学生兴趣团队 4 名研究生与本科生在 42 小时内联手打造智能台灯原型 *IVision Lamp*。系统采用“视觉感知 + 多传感器信息融合”技术路线实时跟踪空间环境与光照变化，并在实体智能台灯硬件上实现自适应闭环光效控制，赢得 Helvar 现场评审团高度认可摘冠（依据清华大学官方新闻网与商汤科技官方报道核验；详细源码仓库与具体延迟毫秒指标未对外公开发布 `[L2]`）。
- **完整技术栈 (tech_stack)**:
  - *实物硬件与融合感知*: 智能台灯实体控制硬件、视觉图像感知管线、多传感器环境信息融合中枢 *(完整工程代码仓库未公开)*。
- **端到端系统架构 (architecture)**:
  1. *多模态感知摄入*: 实时同步采集光学相机视觉帧与多路环境传感信号。
  2. *端侧/近端多传感器信息融合*: 过滤单一传感误判并研判合理照明强度调节量。
  3. *实体台灯闭环调光*: 直接调节实体台灯硬件物理光线输出响应现场环境测试。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 视觉感知 + 多传感器联合融合*：借视觉场景理解弥补环境照度探头单薄缺陷。
  - *决策 2: 42 小时直出实体台灯物理验证*：紧扣真实设备动态调光演示而非停留在纯历史能耗数据分析。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *实战冲刺时长*: `42` 小时现场从零研发完成（会场覆盖 105 个国家/地区 1,300+ 极客及 46 个赛题）。
  - *证据链透明边界*: 官方高校与企业报道明确证实奖项、团队成员及技术方法，但闭源项目未公开发布源码仓与量化性能指标 `[L2]`。
- **路演与现场亮点 (demo_highlights)**:
  - 于 Helvar 现场评估测试台架上顺滑展现视觉融合驱动下的实时台灯光线自适应调节能力。
- **团队背景 (team_background)**:
  - *清华大学–商汤未来深度学习与人工智能学生科技兴趣团队*: *袁秀龙*（电子系 53 班）、*郭映雪*（电子系研 171）、*李鑫*（自动化系硕 162）与 *梁丰*（微纳电子系硕 162）。
- **获胜逻辑假说 (winning_hypothesis)**:
  扎实跨电子、微纳电子与自动化院系的硬科技班底，将商汤深度学习视觉与真实多传感硬件调光稳稳融合进一台可触摸验证的智能台灯之中。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 智能家居与楼宇照明赛题里，引入视觉感知与多传感器互校的实体调光 Demo 最容易抢占评委第一视觉焦点。
  - *经验 2*: 对未开源的 `[L2]` 媒体报道型获奖案例严守诚实原则，绝不杜撰未披露指标。
- **证明材料与链接 (source_urls)**:
  - [清华大学官方新闻网报道 (2018-11-26)](https://www.tsinghua.edu.cn/info/1173/17718.htm)
  - [商汤科技官方新闻稿](https://www.sensetime.com/cn/technology-new-detail/3606?categoryId=53)
  - [Helvar 智能照明域专业博客参照](https://helvar.com/how-to-make-the-light-work-for-you/)
- **证据链等级 (evidence_level)**: `L2: 经清华大学官方新闻网与商汤科技新闻通稿交叉证实`

---

### 项目卡片 17: TruckSense — UPCT & Vueling (Fleetboard — Trucks X Code)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2018`
- **赛事名称 (event_name)**: `Junction 2018`
- **举办年份 (year)**: `2018`
- **出题机构 (organizer)**: `Fleetboard` (戴姆勒 / 梅赛德斯-奔驰商用重卡车联网事业部)
- **挑战赛题 (challenge)**: `Trucks X Code`
- **赛题类别 (category)**: `IoT & Hardware / Connected Heavy Vehicle SDK & Fleet Telemetry`
- **评审标准 (judging_criteria)**:
  - 基于 Fleetboard 官方 SDK 读取梅赛德斯-奔驰重型卡车车载计算机实时车辆总线数据与传感器遥测，开发极具商用落地价值的车载/管理端应用。
- **项目唯一标识符 (project_id)**: `fleetboard-trucksense-2018`
- **项目正式名称 (project_name)**: `TruckSense`
- **所获奖项 (award)**: **Fleetboard 重卡赛道冠军 🥇（赢取赴德国斯图加特戴姆勒总部 3 天全公费技术共创考察研习）**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  重型商用货运卡车一旦路上意外故障，拖车与货损代价动辄数万欧元。西班牙卡塔赫纳理工大学（UPCT）两名远程信息处理工程学生与两名西班牙伏林航空（Vueling）工程师组成 *TruckSense*，在约 40 小时内直接接入梅赛德斯-奔驰卡车车载计算机与 **Fleetboard SDK** 暴露的实时车队总线流，结合机器学习对车辆未来关键运行参数进行前瞻预测，并通过图形化 Web 监控端直观展现——力克同场对手直接受邀前往德国斯图加特戴姆勒总部与车载工程师闭门深化（依据 UPCT 与 La Verdad 报道核验；代码仓与定量误差未公开 `[L2]`）。
- **完整技术栈 (tech_stack)**:
  - *车载总线接口与分析*: 梅赛德斯-奔驰卡车车载终端 / Fleetboard SDK, 实时总线遥测收集后台, 机器学习状态前瞻预测管道, 图形化 Web 监测终端 *(详细内部架构与源码未开源)*。
- **端到端系统架构 (architecture)**:
  1. *真实重卡巴士总线上云*: 对接 Fleetboard 暴露的商用重卡在线实时行车数据。
  2. *前瞻工况预测后台*: 对原始工况做时序预测提前捕捉异常苗头。
  3. *图形化车队驾驶舱*: 清晰投射当下健康指标及未来数小时演化曲线。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 从“被动看现在”升级为“ML 预测未来”*：为商用车队抢出预防性入站检修窗口。
  - *决策 2: 严丝合缝贴合戴姆勒 Fleetboard 商用载体约束*：让德国主机厂评委直观看到极低的商业集成转化门槛。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *现场开发耗时*: 约 `40` 小时连续工程推进（约 10,000 报名者选拔约 1,000+ 现场参赛）。
  - *证据链边界说明*: UPCT 高校新闻网与区域报刊充分实锤冠军身份与斯图加特奖励，未公开 GitHub 代码及模型预测误差值 `[L2]`。
- **路演与现场亮点 (demo_highlights)**:
  - 清爽直观展现真实商用重卡实时行驶遥测与未来运行趋势推演面板，赢得前往斯图加特戴姆勒总部共创的顶格通道奖励。
- **团队背景 (team_background)**:
  - *TruckSense*：西班牙卡塔赫纳理工大学（UPCT）FOSC 开源俱乐部学生 *Pablo Moyano*（三次黑客松获奖老将）与 *Enrique Fernández*（远程信息处理工程），携手 *两名 Vueling 航空资深软件工程师*。
- **获胜逻辑假说 (winning_hypothesis)**:
  车联网专业深度（Telematics Engineering）遇上航空级严谨工业实践，没有搞花哨酷炫概念，反而直击主机厂最在乎的“在途故障预判与高可用架构”。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 对接车企/工程机械开放总线 SDK 时，“未来趋势前瞻预警”永远比静态历史轨迹回放更容易锁定胜局。
  - *经验 2*: 针对未公开代码的 `[L2]` 报道案例务必诚实声明边界。
- **证明材料与链接 (source_urls)**:
  - [西班牙 UPCT 大学官方获奖通告 (2018-11-30)](https://www.upct.es/noticias/2018-11-30-premiados-dos-alumnos-de-la-upct-por-resolver-un-reto-tecnologico-para-monitorizar-los-camiones-mercedes)
  - [La Verdad 西班牙新闻报道](https://www.laverdad.es/murcia/cartagena/estudiantes-upct-resuelven-20181202005210-ntvo.html)
- **证据链等级 (evidence_level)**: `L2: 经西班牙卡塔赫纳理工大学官方公报与 La Verdad 新闻报道证实`

---

### 项目卡片 18: Signvision — Team Glados (Junction 2017 全场总冠军 & STARA 亚军)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2017`
- **赛事名称 (event_name)**: `Junction 2017`
- **举办年份 (year)**: `2017`
- **出题机构 (organizer)**: `STARA` & `Junction 主竞赛组委会`（Espoo Dipoli，CEO Ville Leppälä）
- **挑战赛题 (challenge)**: `Main Competition & STARA Urban Infrastructure Challenge`
- **赛题类别 (category)**: `IoT & Hardware / Mobile Edge Vision & Smart Infrastructure`
- **评审标准 (judging_criteria)**:
  - 从 Junction 2017 横跨 13 个大赛道、1,500 名国际选手中综合评定工程实现深度、实时计算机视觉稳定性、云架构可扩展性与市政基建实用价值。
- **项目唯一标识符 (project_id)**: `stara-signvision-2017`
- **项目正式名称 (project_name)**: `Signvision (Team Glados)`
- **所获奖项 (award)**: **Junction 2017 全场总冠军 🏆 (€20,000 现金大奖) 兼 STARA 市政赛道亚军 🥈**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  市政部门核查城区成千上万块损毁、遮挡交通路牌耗时极巨。在 2017 年铸就 Team Glados 连续两届总冠王朝的奠基之作 *Signvision* (`teamglados/signvision`) 中，团队让日常行驶车辆上的手机充当众包城市视觉巡检节点：React Native 客户端实时抓取路边画面与 GPS 坐标并经高吞吐 `uWs` WebSocket（3000 端口，设立 `5000 ms` 同址去重冷却）推送至后端；先经 OpenCV HSV 红域颜色分割与 `scikit-image` 连通域过滤（`numPixels > 1000`, `30%` 边框扩充），再交由部署于 CUDA 8.0 Docker + AWS ECS Terraform 的 `TensorFlow 1.4.0` `32x32x3` 轻量 CNN（基于 GTSRB 停车标志 `00014` 训练）精判分类并瞬间上云点亮城市基础设施资产地图。
- **完整技术栈 (tech_stack)**:
  - *移动端与低延迟网关*: React Native (相机帧与 GPS 采集), Node.js `uWs` WebSocket (`3000`), `Koa` HTTP API (`8000`).
  - *混合视觉与全自动云编排*: Python `Flask` (`8080`), `OpenCV` HSV 色彩掩膜与形态学处理, `scikit-image` (`skimage.measure.label`), `TensorFlow 1.4.0` (`Conv2D(16)` -> `Conv2D(32)` -> `Dense(2)`), CUDA 8.0 Docker, Terraform + AWS ECS (`aws/*.tf`).
- **端到端系统架构 (architecture)**:
  1. *移动端实景推流 (`MARK_SEND`)*: 持续打包摄像头路拍画面与精确经纬度直连后端 WebSocket 网关。
  2. *经典视觉粗筛 + 防洪峰冷却 (`server/server.js`)*: 在 `5000 ms` 冷却窗口内屏蔽冗余重复上报；再用传统 HSV 红色分割 + 连通区域抠图保证只把干净路牌 ROI 送入深度学习网络。
  3. *GPU 云端推理与标注分发 (`cnn_model/app.py`)*: `32x32x3` CNN 在 Dockerized GPU 上迅速落锤并下发 `MARK_RECEIVE` 标点点亮市政看板。
- **关键技术决策 (key_decisions)**:
  - *决策 1: “传统 HSV 连通域分割 + 超轻 `32x32x3` CNN”混合流水线*：48 小时内不死磕庞重全图检测网，而是先用快速稳定的传统色域抠图护航小模型，又准又省算力。
  - *决策 2: 严防死堵工程陷阱的 `5000 ms` WebSocket 去重锁*：彻底防止演示车载手机等红灯时朝同一块路牌连刷上百条假记录。
  - *决策 3: Terraform + React Native 武器库沿用沉淀*：次年（2018）团队原班人马直接复用该整套全栈流水线打造 *Oneiro* 再捧走 €20,000！

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *网络规模与训练步数*: `32x32x3` 输入 -> `Conv2D(16, 3x3, stride=2, ELU)` -> `Conv2D(32, 3x3, stride=2, ELU)` -> `Flatten` -> `Dense(2)`；基于 GTSRB `00014` 训练 `2,000` / `18,000` 步。
  - *关键滤除与去重阈值*: 最小面积 `numPixels > 1000` 伴 `30%` 包围盒外扩；WebSocket `5000 ms` 冷却时间。
  - *竞赛体量*: 从 `4,000` 名申请者筛选的 `1,500` 名现场选手、`13` 个大赛道中夺下 **€20,000 全场总冠军** 兼 STARA 第 2 名。
- **路演与现场亮点 (demo_highlights)**:
  - 现场走近或驾车经过测试路牌时，大屏幕实时弹出零错位的交通资产坐标钉点，全栈 GPU 容器吞吐顺滑毫无丢帧。
- **团队背景 (team_background)**:
  - *Team Glados*：*Andreas Urbanski*、*Teemu Taskula*（`teemu.taskula@aalto.fi`）与 *Ville Toiviainen*（`Villux`）— 后来蝉联 2018 全场冠军（*Oneiro*）并摘得 2021 KONE 冠军（*ElevAI*）。
- **获胜逻辑假说 (winning_hypothesis)**:
  用极具老到工业经验的混合视觉方案避开暴力端到端拟合坑位，再加上无懈可击的基础设施编排能力，让看似平平无奇的路标检测跑出了金融交易级的工程稳健度。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 面对户外复杂强光动态背景下的边缘视觉赛题，“HSV/形态学几何裁剪 ROI + 极轻量分类网”是最防翻车的黄金公式。
  - *经验 2*: 凡涉及持续移动摄影采集的网关层，必加时间/地理空间去重冷却窗口（如 `5000ms`）。
- **证明材料与链接 (source_urls)**:
  - [Signvision 官方 GitHub 仓库 (teamglados/signvision)](https://github.com/teamglados/signvision)
  - [Devpost 历史存档页](https://devpost.com/software/glados)
  - [Vimeo 路演录像](https://vimeo.com/244507554)
  - [Uusi Teknologia 芬兰权威科技报道](https://www.uusiteknologia.fi/2017/11/28/junction2017-voittaja-yhdisti-big-datan-mobiiliin/)
- **证据链等级 (evidence_level)**: `L1: 经冠军开源 GitHub 仓库 (teamglados/signvision)、Devpost 项目页、视频与芬兰科技媒体报道证实`

---

### 项目卡片 19: ReCover — DF LAB (Suunto / Movesense — Track Anything That Moves)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2017`
- **赛事名称 (event_name)**: `Junction 2017`
- **举办年份 (year)**: `2017`
- **出题机构 (organizer)**: `Suunto（颂拓）` (Movesense 开源可编程运动传感器平台)
- **挑战赛题 (challenge)**: `Track anything that moves!`
- **赛题类别 (category)**: `IoT & Hardware / Dual-IMU Biomechanics & Rehab Wearables`
- **评审标准 (judging_criteria)**:
  - 考核基于可编程 Suunto Movesense BLE 传感器开发出对运动、健康或物联网具高附加值、功能高度完备且交互顺畅的真实原型。
- **项目唯一标识符 (project_id)**: `suunto-recover-2017`
- **项目正式名称 (project_name)**: `ReCover (DF LAB)`
- **所获奖项 (award)**: **Movesense 健康赛道冠军 🥇（赢得 6 枚 Movesense 传感器 + 4 块 Suunto Spartan 腕表）**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  膝关节术后居家康复患者在脱离医院量角器后，仅凭感觉练习屈伸动作极易因屈曲不到位导致僵硬、或过度用力二次拉伤韧带。在 Junction 2017 同台竞争的 `24` 支 Movesense 参赛作品中，拉脱维亚大学 *DF LAB* 战队创造性地将**两枚同步运行的 Suunto Movesense IMU 传感器分别佩戴在患者膝关节上方大腿与下方小腿处**，利用双路 BLE 采集传入 iOS 客户端做相对坐标差分计算，精准还原纯粹的膝关节弯曲角度并提供安全目标区间实时提醒——正是这批骨干次年跨界携手 Intel 网关勇夺 2018 全场亚军（*Help.io*）。
- **完整技术栈 (tech_stack)**:
  - *双传感微分可穿戴系统*: `2x` 可编程 **Suunto Movesense** BLE 模组 (加速度计/陀螺仪/磁力计, `movesense-mobile-lib`).
  - *移动端复健应用*: iOS 原生康复训练视觉反馈界面，实时对照康复医嘱目标角度拱形进度提示。
- **端到端系统架构 (architecture)**:
  1. *上下肢端双节点采样*: 膝上大腿模组与膝下小腿模组同步发射多轴惯性姿态报文至手机端。
  2. *参考系相对差分解算*: 计算两个传感器坐标系之间的纯相对夹角差，彻底抵消人躺坐姿势偏移干扰。
  3. *患者复健安全区指导*: 界面实时标识“当前屈膝度数”及医生规定的上下安全门槛区间。
- **关键技术决策 (key_decisions)**:
  - *决策 1: 独具匠心的“跨关节双传感器差分”*：绕开单传感器靠重力斜率估算会随坐姿弯腰彻底失效的物理死穴。
  - *决策 2: 医学临床痛点真实背书*：核心康复需求直接由医学博士研究员 Emīls Sjundjukovs 发起输入，告别伪健康计步器。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *竞争规模*: 从 Junction 2017 现场共 `24` 支提交的 Movesense 团队中力夺**健康类头名**（全赛场 1,500 人）。
  - *实体配比与激励*: 跨关节双传感方案；获奖 `6` 枚传感器及 `4` 块 Suunto Spartan 旗舰腕表。*(代码库未公开存档 `[L1/L2]`。)*
- **路演与现场亮点 (demo_highlights)**:
  - 选手当众做屈膝复健演示时，iOS 画面精确如医院精密角度仪般实时跟踪并反馈“刚好达标 / 超出保护角”的体感区间变化。
- **团队背景 (team_background)**:
  - 拉脱维亚大学计算机学院 *DF LAB* 战队：*Austris Cīrulnieks*、*Elvijs Viļķels*、*Dāvis Mednis* 与 *Mārcis Nīmants* *(临床理念发起与指导 Emīls Sjundjukovs)* — 2018 年全员进化成为 Intel 冠军 *Help.io* 班底。
- **获胜逻辑假说 (winning_hypothesis)**:
  教科书般的“两传感器坐标系相对差分”物理直觉结合真实临床术后痛点，直接让 Suunto 硬件工程师眼前一亮。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 人体关节弯曲或器械形变类测量，“跨关节两枚传感器做相对矢量差”可秒杀单传感器漂移。
  - *经验 2*: 连续多届打磨同一套 BLE 底层传感技能树会产生滚雪球式战果（`ReCover` 2017 -> `Help.io` 2018）。
- **证明材料与链接 (source_urls)**:
  - [ReCover Devpost 历史存档](https://devpost.com/software/recover-pfrq3g)
  - [Movesense 官方 2017 赛季获奖战报](https://www.movesense.com/news/2017/11/24-movesense-projects-at-junction-hackathon/)
  - [拉脱维亚大学官方新闻公告](https://eztf.lu.lv/par-mums/zinas/zina/t/29783/)
- **证据链等级 (evidence_level)**: `L1: 经 Suunto 官方战报、Devpost 项目库与拉脱维亚大学官方通告严格证实`

---

### 项目卡片 20: AR Dentist (Planmeca Oy — Reshaping the Future of Dentistry)

#### 1. 基础元数据
- **赛事标识符 (event_id)**: `junction-2017`
- **赛事名称 (event_name)**: `Junction 2017`
- **举办年份 (year)**: `2017`
- **出题机构 (organizer)**: `Planmeca Oy`（评审专家：产品开发经理 Sakari Kettunen & 数字业务方案经理 Antti Haanpää）
- **挑战赛题 (challenge)**: `Reshaping the future of dentistry`
- **赛题类别 (category)**: `IoT & Hardware / 3D Dental Imaging & Mobile AR Overlay`
- **评审标准 (judging_criteria)**:
  - 结合现场 Planmeca 3D 口腔成像与数字化诊疗设备数据流，打造令患者倍感轻松无压、兼顾牙医远程前置规划的“未来虚拟牙科诊室”方案。
- **项目唯一标识符 (project_id)**: `planmeca-ar-dentist-2017`
- **项目正式名称 (project_name)**: `AR Dentist`
- **所获奖项 (award)**: **Planmeca 挑战赛道第一名 🥇（13 支正面角逐队伍中夺魁）**

#### 2. 技术架构与核心工程
- **方案概要 (solution_summary)**:
  口腔诊患者常常对冰冷电脑屏幕上的 CBCT 锥形束 CT 切片毫无画面感，引发治疗沟通障碍与术前紧张。在健康赛道 13 支强劲队伍正面角逐中，临时组队的二人梦幻小组 *AR Dentist* 直接调用 **Planmeca 现场 3D 口腔成像数据集** 构建双屏同步 AR 预演：医生只需在伴侣笔记本端平滑修改 3D 牙齿参数，对准受试者面部的手机屏幕即可毫秒级同步追踪人脸并将改版后的三维口腔修复模型自然贴合到“AR 魔镜”之中（依据 Planmeca 官方新闻公告核验；源码仓库与具体帧率数据未对外公开 `[L1]`）。
- **完整技术栈 (tech_stack)**:
  - *医学影像与双屏 AR*: Planmeca 3D 口腔影像数据集 (`Planmeca Romexis` 生态背景), 伴侣笔记本 3D 参数调节终端, 移动端实时人脸识别跟踪与 3D 口腔 AR 渲染引擎 *(闭源未公开代码仓)*。
- **端到端系统架构 (architecture)**:
  1. *医用参数控制端 (笔记本)*: 载入 Planmeca 3D 口腔影像模型并提供流畅的疗程形态控制面板。
  2. *低延迟参数广播同步*: 将参数变动实时注入移动渲染管线，保障无卡顿交互感。
  3. *患者级实景 AR 魔镜*: 跟踪人脸动态旋转并在嘴部位置无缝映射立体口腔预期效果。
- **关键技术决策 (key_decisions)**:
  - *决策 1: “医生精细操控台 + 患者直观手机魔镜”双端分流*：绝不在拥挤手机小屏硬塞复杂 CAD 菜单，大幅抬高诊室落地优雅度。
  - *决策 2: 工业 3D 设计 + 移动软件物理开发“黄金二人组”*：剔除冗杂沟通，直接确保高精度 3D 模型美术与实时移动端跟踪完美契合。

#### 3. 验证指标与实战启示
- **量化指标与基线对比 (metrics_and_baseline)**:
  - *竞赛淘汰率*: 面对同赛道 `13` 支挑战 Planmeca 的专业战队摘下头名（全景赛场 Dipoli 共 1,500 名国际选手）。
  - *数据透明边界*: 全球牙科设备巨头 Planmeca 官方通稿详实披露成员、评委、方案构型与排名，未附带公开 GitHub 链接及 FPS 实测数字 `[L1]`。
- **路演与现场亮点 (demo_highlights)**:
  - 演示现场一侧电脑调整牙齿三维矫正滑块，另一侧照着模特面部的手机画面立即精准跟着变换虚拟微笑，治愈感满分。
- **团队背景 (team_background)**:
  - 跨学科跨国两人黄金小组 *AR Dentist*：*Samuel Laska*（斯洛伐克，物理与计算机背景移动开发者）与 *Linda Ukkonen*（芬兰，工业设计与 3D 建模专业）。
- **获胜逻辑假说 (winning_hypothesis)**:
  极其精准的专业互补配比与极暖心的诊室交互同理心。比起单纯堆叠算法指标，他们用一台手机加一台电脑让高冷的三维牙科影像真正服务到了患者眼前心理安全感。
- **可复用黑客松经验 (reusable_lessons)**:
  - *经验 1*: 医疗健康或消费硬件/AR 赛道，**“3D 工业设计师 + 移动工程师”的精悍 2 人班底**开发产出比极高。
  - *经验 2*: 善用“专业侧笔记本调控 -> 受试者侧手机 AR 实时映射”的双屏舞台演示阵型，产品定位瞬间传神。
- **证明材料与链接 (source_urls)**:
  - [Planmeca 全球官网 2018 年官方赛后揭晓报道](https://www.planmeca.com/news-and-events/newsroom/2018/planmeca-challenged-hackers-to-reshape-the-future-of-dentistry/)
- **证据链等级 (evidence_level)**: `L1: 经全球口腔巨头 Planmeca 官网 2018 年 1 月官方新闻公告严格证实`
