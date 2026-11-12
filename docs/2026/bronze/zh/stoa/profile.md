# Stoa (Stoa Technologies Oy / Stoa Build) — Junction 2026 课题提供方深度调研报告

## 1. 公司基本概况

- **公司全名**: Stoa Technologies Oy (商用品牌名: Stoa / Stoa Build)
- **官方主页**: [https://stoabuild.com/](https://stoabuild.com/)
- **公司总部**: 芬兰赫尔辛基 (Kampinkuja 2, 00100 Helsinki, Finland)
- **创立背景**:
  - Stoa 创立于芬兰赫尔辛基，核心团队来自知名工程软件、建筑信息模型（BIM）及前沿人工智能实验室。
  - 面对全球最古老、最庞大却数字化最碎片化的万亿美元级建筑工程行业（Construction Industry），创始团队深刻指出：**建筑工地上绝大多数返工、延期与安全事故所必需的预防性信息其实早已存在，但却被割裂在图纸、CAD、BIM 模型、施工日报、变更单（RFI）和邮件等数十个互不相通的独立系统中**。现场工程师与工人往往因为无法在关键决策点实时触达正确信息而导致巨额损失。
  - Stoa 致力于打造专为建筑施工现场量身定制的 AI 原生操作系统（The AI-Native Operating System for Construction Projects），将工地现场的所有离散信息汇聚为一个统一、动态自适应的“活体项目大脑（Living Project Brain）”。
- **行业地位与落地规模**:
  - **已赋能欧洲超 40 亿欧元（€4B+）规模的大型工程项目**，涵盖商业综合体、大型能源基建、工业厂房与住宅开发。
  - 实测数据表现卓越：
    - **每周为每名现场工长与项目工程师节约 2~8 小时**无意义的信息查找与沟通时间；
    - **现场决策响应速度提升 8 倍**；
    - **平均为整个工程施工周期缩短约 6%** 的总工期。
- **与易混淆实体的辨析说明**:
  > [!IMPORTANT]
  > **实体对齐关键勘误 (Ground Truth Verified)**:
  > 本课题提供方为芬兰建筑科技独角兽初创 **Stoa Technologies Oy (`https://stoabuild.com/`)**；**绝非**赫尔辛基东区的伊塔克斯市立文化中心（Cultural Centre Stoa / `stoa.fi`）。官方在 Junction 2026 官网 Partners 展区明确外链为 `https://stoabuild.com/`。

---

## 2. 核心产品与业务体系

Stoa 构建了“统一集成信息层 + 建筑领域专用知识图谱 + 三大交互行动中枢”的技术架构：

### 2.1 集成与信息层 (Integrations & Information Layer)
- **零摩擦无感对接**: 无需现场推倒重来或进行痛苦的数据迁移，Stoa 开箱即用集成工地现有的数十种专业工程软件系统（Procore、Autodesk Construction Cloud / Revit、Dalux、BIM 360、SharePoint 等），2 个工作日内自动将零散文件解析并抽取至统一底座。
- **欧盟数据主权与严苛隐私保护**: 数据严格存储并处理在欧盟境内（EU Data Residency），绝对不使用客户工程专有图纸训练公共基座模型，支持企业申请 30 天内彻底硬删除。

### 2.2 建筑专用知识图谱与动态关联 (Construction-Focused Knowledge Graph)
- **图纸与规范的深度语义对齐**: 传统通用 LLM 无法理解建筑工程图纸中微小的符号、层级与几何约束。Stoa 建立了建筑领域的语义实体图谱，将 2D 施工图纸、3D BIM 构件、技术规格书（Specs）与规范条文深度双向锚定。
- **图纸沉浸式导航**: 工程师在平面施工图中点击某一墙体类型（Wall Type），系统右侧自动联动展开定义该墙体耐火等级、龙骨间距与隔音阻尼的对应细部详图与设计变更，彻底消除来回翻阅厚重图纸的痛苦。

### 2.3 AI 原生工程问答与动态变更雷达 (AI-Native Chat & Change Feed)
- **严格溯源的问答机制**: 任何工长在平板电脑上向项目提问（例如：“3 层空调水管吊架间距规范是多少？”、“昨晚修改的剪力墙钢筋配比文件在哪里？”），Stoa 返回的每一句话都附带可点击核验的原始图纸版次、设计院 RFI 批复编号及具体页码锚点。
- **动态变更雷达 (Change Feed)**: 不依赖人工邮件通知，Stoa 主动在后台比对新旧图纸图层，精准指出“设计师实际改动了哪根梁柱、这一改动波及了下属哪些管道与机电标高”，防患于未然。

### 2.4 自动化闭环与 AI 智控日程 (Automation & Document Bank)
- 当现场发现偏差，Stoa 可自动串联相关证据链一键生成工业级工作汇报单；针对高频重复问题，可直接委派自主 Agent 在新版图纸上传时自动执行合规性前置扫描。

---

## 3. Vision（愿景）与 Mission（使命）

### Vision (愿景)
*"To become the AI-native operating system and living project brain for the global construction industry — transforming how the physical world is built through transparent, unified, and real-time intelligence."*  
（成为全球建筑与工程施工事实上的 AI 操作系统与智能大脑，用透明、统一与实时的空间数字智能彻底重塑人类物理世界的营造方式。）

### Mission (使命)
*"The information that would prevent most problems on a construction site already exists. It's just scattered across systems that never talk to each other, so no one reaches it in time. Stoa is here to change this — connecting every piece of project data into a unified, living brain so teams build faster and with complete certainty."*  
（消除建筑工地严重的信息孤岛与沟通延迟，让工地的每一次浇筑、吊装与施工交底都基于绝对精准的实时全量数据，让建筑人告别扯皮与返工，从容掌控工程质量。）

---

## 4. 所属 Category

- **ConTech** (Construction Technology / 建筑科技与智慧工地)
- **AI-Native Enterprise Knowledge Graphs** (企业级工程图纸与多模态知识图谱)
- **Industrial Multi-Modal AI Operating Systems** (工业级多模态 AI 操作系统)
- **Smart Infrastructure & Urban Engineering** (智慧基础设施与城市工程)

---

## 5. 在 Junction 黑客松中的角色与赛道挑战预测

### 对应赛道
- **Agentic AI Track** (自主工程智能体)
- **Urban & Mobility / Smart Infrastructure Track** (智慧城市与大型基建)
- **AI Infrastructure & Multi-Modal Engineering Track** (多模态工业工程)

### 挑战课题预测
1. **多模态图纸与施工规范合规性自主审计 Agent (Automated BIM/CAD Compliance Checker)**:
   - 结合 Stoa 的建筑工程知识图谱，开发一个自动审查现场拍照或 3D 点云与设计图纸是否一致的 Agent，自动标出消防通道净宽违规、管道冲突等现场隐患。
2. **工地多语种劳工语音智能调度与安全警报向导 (Multilingual Voice Safety Copilot on Site)**:
   - 针对欧洲大型跨国工地多语种（芬兰语、英语、波兰语、爱沙尼亚语等）工人现场沟通难点，利用 Stoa 知识库打造语音驱动的即时安全技术交底助手。
3. **基于图纸变更的工程成本与进度波及效应自主推演引擎 (Change Impact & Schedule Ripple Engine)**:
   - 当设计院上传图纸变更时，Agent 自动推演该变更对材料采购、人员排班与后续关键路径工序的连锁影响，输出最优纠偏建议。

---

## 6. 官网与关键资源链接

- **官方主页**: [https://stoabuild.com/](https://stoabuild.com/)
- **公司联系与演示预约**: `info@stoabuild.com` / [Book a Demo](https://stoabuild.com/)
- **总部地址**: Kampinkuja 2, 00100 Helsinki, Finland
