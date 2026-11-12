# [2025 Winner Case Study] Supercell — AI-First Fun: Prompt Me Maybe & LoreDash

## 1. 元数据概览 (Metadata)

- **对应赛题文件**: [`2025_Supercell_AI-First_Fun.md`](file:///C:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Agentic%20AI/2025_Supercell_AI-First_Fun.md)
- **赛道**: Agentic AI Track / AI & Data
- **出题方 (Partner)**: Supercell (赫尔辛基全球知名移动游戏公司，代表作《部落冲突》《皇室战争》《荒野乱斗》等)
- **赛题名称**: AI-First Fun
- **赛题核心挑战**: “打造一款必须依赖 AI 才能存在的原生游戏体验（Create a game that could not exist without AI）”，推动非确定性生成、实时自适应叙事、智能 NPC 与实时玩法创新。
- **奖金设置**: 1st Place €3,000 | 2nd Place €2,000 | 3rd Place €1,000
- **核心获奖项目与团队**:
  1. **【赛道总冠军 / Grand Prize Winner】: 《Prompt Me Maybe》** (由 Hive Helsinki / 42 Network 的 **Team Undefined** 构建，斩获 Supercell AI Hackathon 赛题总冠军与 1st Place)
  2. **【Junction 旗舰总决赛亚军 / Track Runner-Up】: 《LoreDash》** (由 Junction 传奇独行侠 **Frank Sandqvist** 单人构建，斩获 Supercell 赛道亚军及 **Junction 2025 全场总亚军 / Overall 2nd Place，斩获 €7,500 + €2,000 巨额奖金**)
  3. **【赛道季军 / Track 3rd Place】: 《Towercaster》** (由 Bocconi / 米兰理工学者 **Sueda Gül** 团队构建，LLM 隐式判决实时 PvP 对战游戏)

---

## 2. 获胜者与团队档案 (Winner Profiles & Social Links)

### 项目一：Prompt Me Maybe（赛题总冠军 / Grand Prize Winner）
- **开发团队**: Team Undefined (来自芬兰顶尖 Peer-to-Peer 编程学院 Hive Helsinki / 42 Network)
- **团队成员**:
  - **Aaron Padilla**: 软件工程师，前 Wolt 经历，Hive Helsinki 校友
    - **领英主页 (LinkedIn)**: [Aaron Padilla on LinkedIn](https://www.linkedin.com/in/aapadill/)
    - **GitHub**: [@aapadill](https://github.com/aapadill)
    - **个人主页 (Portfolio)**: [deblish.com](https://deblish.com/)
  - **Chi Lee (LeeRichi)**: 核心底层架构师，Junction 2024 获胜者，Supercell AI Hackathon 冠军
    - **GitHub**: [@LeeRichi](https://github.com/LeeRichi)
    - **开源代码仓库 (Repository)**: [GitHub - LeeRichi/PromptMeMaybe](https://github.com/LeeRichi/PromptMeMaybe)
  - **Martin Dahlström-Heuser**: 跨学科视觉艺术家与全栈开发者，阿尔托大学 (Aalto University) 及哥德堡大学校友
    - **GitHub**: [@mdheuser](https://github.com/mdheuser)
    - **艺术主页**: [Martin Dahlström-Heuser Official](https://www.mdheuser.com/)
  - **Helena Utzig**: Hive Helsinki 开发者与运营团队核心成员
  - **Yun-Chia Hsu**: 软件工程师与系统设计者
- **播客专访与公开分享**: 受邀参与知名 AI 游戏专访播客 *Playing with Inference* (Episode 18: "Building 'Prompt Me, Maybe' in 40 Hours at the Supercell AI Game Jam").

---

### 项目二：LoreDash（Junction 2025 全场总亚军 & Supercell 赛道亚军）
- **开发者**: **Frank Sandqvist** (以战队名 "to be Frank" 单人参赛)
- **个人简介 (Headline)**: Parallel entrepreneur | Founder at Smidyo & CNC Design | Operations Manager at Nykarleby Innovation Center | "Grandmaster of Junction"
- **领英主页 (Profile)**: [Frank Sandqvist on LinkedIn](https://www.linkedin.com/in/frank-sandqvist-9a096683/)
- **领英动态链接 (Post URL)**: [Post on LinkedIn](https://www.linkedin.com/feed/update/urn:li:activity:7445170584142970881/)
- **舞台路演回放 (YouTube Pitch)**: [Junction 2025 | Top 5 Finalist Pitch – LoreDash](https://www.youtube.com/@JunctionHackathon)

---

## 3. 获奖动态原文与深度转写 (Post Transcripts & Dialogue)

### 3.1 Frank Sandqvist 领英发帖回顾与感言 (Transcript)
> "I've only been grandmaster of a junction twice. Once with my STOP-sign at an actual street junction as a parade functionary, and second on the Junction newsletter. Great job Yankuan & Neea for somehow making my messy recalls into a coherent story!
> 
> One of the few constants in my professional life is once a year, and it's a highlight: attending Junction! I've been going since 2019, and it's a great outlet for the ideas and energy one gathers throughout the year. Keep it up guys.
> 
> [In Junction 2025], building LoreDash for the Supercell 'AI-First Fun' challenge proved that generative models can do far more than pre-rendered assets: they can synthesize interactive rulesets, audio, and gameplay on the fly. Thanks Junction!"

### 3.2 《Playing with Inference》专访播客 (Episode 18 转写要点)
在受邀与播客主持人 Ramon 和 Aaron 对话中，Team Undefined 拆解了《Prompt Me Maybe》夺得 Supercell 冠军的秘密：
- **评委真实反馈**: “Supercell 的评审明确表示，绝大多数团队只是拿商业引擎（Unity/Unreal）套一个 LLM 对话 NPC，但这类应用并非‘没有 AI 就活不下去的游戏’。而《Prompt Me Maybe》将生成模型直接接入了最底层的射击弹道与武器机制中，实现了‘语言即武器’的不可预测玩法。”
- **40 小时极限交付**: “我们选择用纯 C 语言编写光线投射（Ray-casting）引擎，而不是现成引擎。极高的运行帧率让哪怕是低算力设备也能瞬间完成图像处理与实时映射。”

---

## 4. 获奖项目技术方案与架构深度解析 (Technical Deep-Dive)

### 4.1 《Prompt Me Maybe》：语言即弹药的实时生成式 FPS
- **开发引擎**: 基于 C 语言及图形库 **MLX42**，从零手写 **Wolfenstein 3D 风格光线投射（Ray-casting）伪 3D 引擎**。
- **核心玩法机制**:
  1. **Prompt-to-Weapon（即时武器合成）**: 玩家在游戏过程中无需拾取常规枪械，在控制台输入任意自然语言提示词（如 `"a slice of pizza"`、`"screaming baby"`、`"cybernetic banana blaster"`）。
  2. **动态资产与机制注入流水线**: 
     - **视觉层**: 后端调用视觉生成模型与 Sprite 分割流水线，以秒级延迟返回贴合 90 年代像素风格的 HUD 持枪手部动画与第一视角攻击贴图。
     - **数值与弹道逻辑解析**: 后端 LLM 同步解析提示词的情感色彩、质量与属性，实时赋予伤害值、射程、射速及特殊粒子弹道（例如披萨武器发射热熔起司附着减速）。
  3. **地图与物理支持**: 基于 `.cub` 配置文件实现自定义地图布局、实时 2D 俯视小地图雷达（Minimap）、平滑的键鼠第一人称移动与射线碰撞判定。

---

### 4.2 《LoreDash》：维基百科兔子洞的微游戏瞬时生成器
- **开发者理念**: 将人类探索互联网随机知识（Wikipedia Rabbit Hole）的被动阅读行为，重构为高互动性的“即时游玩与通关”。
- **系统核心流水线**:
  1. **维基百科词条实时抓取**: 玩家点击“Dash”按钮，系统随机抓取一个维基百科真实词条文本。
  2. **Google Gemini Pro 规则与代码生成**: Gemini Pro 实时阅读词条长文本，提取核心冲突或知识考点，在数秒内自动编译生成一个微型 HTML5 / Canvas 交互游戏（谜题、反应挑战、知识问答跑酷）。
  3. **ElevenLabs 拟真音效生成**: 根据游戏背景主题（如中世纪战役 vs 量子物理）动态生成对应环境音效。
  4. **自适应音乐流**: 串联实时自适应音频流，使背景音乐伴随游戏节奏动态演化。

---

### 4.3 《Towercaster》：大模型隐式判决实时 PvP
- **核心机制**: 玩家输入任意概念进行“万物对战（Everything vs. Everything）”。
- **AI 裁判系统**: 每一回合的相克关系不依靠硬编码规则表，而是由 LLM 在幕后依照情境因果与物理/隐喻逻辑判定胜负（例如“火”克“木”，但“暴风雨”可能同时浇灭“火”并折断“木”），创造了极具悬念的对抗博弈。

---

## 5. Supercell 评审标准与黑客松获胜洞察 (Winning Methodology & Jury Insights)

根据 Supercell 评委在现场与 Medium 专访（*“Something unpredictable. Something shocking.”*）中的复盘，本赛题评分标准的关键分水岭在于：

1. **拒绝“贴皮 AI (AI as an afterthought)”**:
   - 常见失败做法：制作了一款常规的三消或塔防游戏，仅仅让 ChatGPT 生成关卡文案或扮演 NPC 聊天。
   - 获胜做法：AI 必须是**核心玩法循环（Core Gameplay Loop）的核心齿轮**。若拿掉 AI，游戏机制立即不复存在。
2. **极限反差的美学冲击**:
   - 《Prompt Me Maybe》将硬核低级 C 语言光线投射复古画面与前沿的 Diffusion / Multimodal API 结合，反差感拉满。
   - 《LoreDash》将严肃枯燥的百科知识库瞬间转变为无厘头可玩关卡，极度契合 Supercell “Fast, Fun, Accessible” 的设计基因。
3. **路演必须具备即时病毒传播力**:
   - Frank Sandqvist 与 Team Undefined 均在现场直接进行了 **Live Interactive Demo**（现场让观众或评委随机输入词条/武器词），用零失误的极速生成引爆全场掌声。