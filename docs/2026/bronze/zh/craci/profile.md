# CRACI (Craci Corporation) — Junction 2026 技术合作方调研报告

> **调研分类**：Junction 2026 Bronze 级技术合作方（Tech Partner Profile）  
> **公司标签**：软件供应链安全 (Software Supply Chain Security) | 欧盟网络抗逆力法案合规 (EU Cyber Resilience Act / CRA) | CI/CD 自动化 SBOM (Automated SBOM in CI/CD)  
> **报告归档路径**：`bronze/craci/profile.md` & `docs/2026/bronze/craci/profile.md`  

---

## 1. 公司基本概况 (Company Overview)

| 项目 | 详细信息 |
| :--- | :--- |
| **公司全称** | Craci Corporation Oy (商业品牌：CRACI) |
| **公司官网** | [craci.com](https://craci.com) |
| **总部地址** | 芬兰 · 赫尔辛基 (Helsinki, Finland) |
| **创立年份** | 2025 年 |
| **核心创始人团队** | - **Juho Niemi** (Co-Founder & CEO)<br>- **Dennis Marttinen** (Co-Founder & CTO，曾活跃于北欧顶尖开源安全与系统级基础设施项目)<br>- **Jaakko Sirén** (Co-Founder & Head of Engineering/Product)<br>- **Petteri Pulkkinen** (Co-Founder & Operations/Growth) |
| **融资轮次与金额** | **种子前轮（Pre-Seed Round）已完成 €1.4M（约合 150 万美元）** |
| **主要投资机构** | **Lifeline Ventures** 领投（芬兰传奇早期风投，Supercell、Wolt、MariaDB 等欧洲独角兽的早期领投方），**First Fellow Partners**（由 Rovio 前 CEO Risto Siilasmaa 发起）与 **Wave Ventures** 联合参投 |
| **团队基因** | 专注于操作系统与容器运行时审计、CI/CD 管道虚拟化、自动化软件物料清单（SBOM）生成及欧盟最新网络安全监管合规技术 |

---

## 2. Vision（愿景）与 Mission（使命）(Vision & Mission)

### 🌟 愿景 (Vision)
> **"To build a world where digital supply chains are transparent, verifiable, and secure by design — transforming heavy regulatory mandates from operational burdens into structural engineering advantages."**  
> *(构建一个数字供应链天然透明、可被客观验证且出厂即安全的世界 — 将沉重的法规合规压力转化为结构性的工程竞争优势。)*

随着欧盟《网络抗逆力法案》（EU Cyber Resilience Act, CRA - Regulation (EU) 2024/2847）的出台，所有在欧盟境内销售的数字硬件与联网软件产品均被强制要求具备全生命周期的网络安全能力、物料透明度与漏洞汇报机制。CRACI 坚信未来的软件工程不应受困于繁复的法务审计与纸面合规，而应通过底层构建工具链的透明化实现**开箱即合规**。

### 🎯 使命 (Mission)
> **"To empower teams to ship software with confidence by providing full transparency into their software supply chain."**  
> *(通过赋予软件供应链百分之百的透视能力，让全球开发团队能够充满信心地发布每一行代码。)*

CRACI 确立了四项核心工程设计原则：
1. **Evidence over assertion（客观证据优于口头宣称）**：用构建运行时的真实网络与进程证据链替代静态扫描的不可靠推测。
2. **Secure by default（出厂默认安全）**：无需额外配置复杂的策略规则，流水线默认记录每一次依赖流转。
3. **Open standards - no lock-in（全面拥抱开放标准，拒绝厂商绑架）**：原生支持 SPDX 与 CycloneDX 等国际标准 SBOM 规范。
4. **Compliance without the tax（免除开发合规税）**：合规自动化发生在后台构建中，绝不拉低工程团队的代码交付速率与敏捷度。

---

## 3. 所属 Category（业务与技术分类）(Industry & Tech Category)

### 📌 核心分类 (Primary Category)
- **Software Supply Chain Security**（软件供应链安全平台）
- **EU Cyber Resilience Act (CRA) Automated Compliance**（欧盟网络抗逆力法案自动化合规）

### 🏷️ 细分技术标签 (Tech Tags & Taxonomies)
`SBOM (Software Bill of Materials)` `CycloneDX` `SPDX` `CI/CD Build Runner Security` `GitHub Actions Runner` `Vulnerability Tracking & KEV Mapping` `Transitive Dependency Audit` `DevSecOps` `EU CRA Regulation (EU) 2024/2847`

### 💡 行业生态位对比 (Ecosystem Positioning)
- **对比传统静态代码/依赖扫描器（如 Snyk / Dependabot / SonarQube）**：传统扫描器仅解析 `package-lock.json` 或静态 AST，极易被恶意后门、隐藏在构建脚本（如 `postinstall`、Makefile、Dockerfile）中动态下载拉取的恶意二进制所瞒骗；CRACI **直接在 CI/CD 构建 Runner 运行时内核层观察**所有被拉取的包与网络调用，捕获最真实的构建时依赖。
- **对比通用合规审计平台（如 Vanta / Drata）**：通用 GRC 平台聚焦于企业管理政策与 SOC2/ISO 流程，缺乏对二进制代码构建流、传递依赖及 EU CRA 严苛漏洞汇报时限（24 小时/72 小时）的技术级联动；CRACI 是专门为 CRA 开发者量身打造的技术实现层。

---

## 4. 核心产品与服务 (Core Products & Architecture)

### 4.1 主打平台：CRACI CI/CD Native Compliance Engine
CRACI 的核心创新在于将合规监控下沉至 CI/CD Runner 层。以 GitHub Actions 为例，开发者仅需一行配置即可将构建作业迁移至 CRACI 安全沙箱：

```yaml
# 开发者仅需修改一行配置即可启用
jobs:
  build-and-release:
    runs-on: craci    # 一键替换 ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install && npm run build
```

### 4.2 核心架构模型 (Architectural Workflow)

```
+─────────────────────────────────────────────────────────────────────────────+
|                             Developer Push / PR                             |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
+─────────────────────────────────────────────────────────────────────────────+
|                         CRACI Sandboxed Build Runner                        |
|   (Kernel eBPF & Process Tracking / Network Egress Interception)            |
|   - Real-time Transitive Dependencies Detection (NPM, PyPI, Cargo, Go, OCI) |
|   - Captures dynamic compilation artifacts, build scripts & system packages |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
+─────────────────────────────────────────────────────────────────────────────+
|                          Automated SBOM Generation                          |
|         Machine-Readable Spec Generation: CycloneDX 1.6 / SPDX 2.3/3.0      |
|         Cryptographic Attestation & Build Provenance Signing                |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
+─────────────────────────────────────────────────────────────────────────────+
|                   CRACI Continuous CRA Compliance Monitor                   |
|   - Dynamic Mapping: Known Exploited Vulnerabilities (CISA KEV / NVD CVE)    |
|   - 24h Active Exploit Early Warning & 72h Full Incident Dispatch to CSIRTs |
|   - Technical Documentation Dossier Generation for EU CE Conformity         |
+─────────────────────────────────────────────────────────────────────────────+
```

### 4.3 关键特性与竞争优势 (Key Features)
1. **真实构建时依赖追踪 (Runner-Level Dynamic Capture)**：
   - 彻底避免“静态锁文件脱节”漏洞，精准记录打包过程中容器内下载的真实依赖，哪怕依赖隐藏在嵌套压缩包或编译阶段也无所遁形。
2. **多标准机器可读 SBOM 原生导出 (Zero-Config SBOM)**：
   - 伴随每次 Release 自动生成并数字签名格式完备的 SBOM，完全匹配欧盟 CRA 附录 I 第 2 节法规硬性要求。
3. **精准到 Commit 的漏洞反向映射 (Commit-Level Blast Radius)**：
   - 一旦上游爆发新 0-day 或 CVE，CRACI 能秒级定位是哪一次 Git Commit、哪一个镜像版本受到波及，并自动向工程师推送精准补丁建议，告别无休止的“误报告警地狱”。
4. **内置欧盟 CRA 法律合规工作流 (CRA Article 14 Reporting Engine)**：
   - 内置针对 EU CRA 2026 年 9 月生效的漏洞通报时效（24 小时预警 / 72 小时详报）与 2027 年 12 月全面适用的合规文档包生成器。

---

## 5. 在 Junction 2026 黑客松中的角色与开发者赋能 (Junction 2026 Role & Hacker Enablement)

### 5.1 黑客松角色定位
- **定位**：Junction 2026 Bronze 级技术合作方（Tech Partner）。
- **黑客松主题联动**：紧扣本届 Junction **"European Tech Renaissance"（欧洲科技复兴）** 宏大主题，直击欧洲初创团队走向国际化最棘手的“合规与软件供应链主权”痛点。

### 5.2 推荐参赛赛道 (Recommended Tracks)
- **Security Track**：构建下一代自愈式软件供应链、AI Agent 依赖鉴权系统或自动化安全补丁机器人。
- **AI Infrastructure Track (by Verda)**：监控与审计分布式 AI 模型流水线中的第三方 Python/PyTorch/CUDA 轮子依赖，防止模型投毒与供应链木马。
- **Agentic AI Track**：针对调用复杂外部 API、下载第三方脚本的自主智能体（Autonomous Coding Agents），构建运行时的安全沙箱与行为证明。

### 5.3 参赛黑客典型落地场景 (Hackathon Ideas)
- **黑客松项目自带“欧盟 CRA 合规证书” (The Instant-CRA Verified Badge)**：
  - 参赛团队在提交任何 Web/Mobile/IoT 项目时，在 CI 流水线中加入 `runs-on: craci`，在 Demo 评审中展示生成的 CycloneDX SBOM 与实时漏洞风险为 0 的证明，作为技术成熟度的巨大加分项。
- **自主开源依赖修复 Agent (Autonomous CVE Remediation Bot)**：
  - 基于 CRACI 导出的细粒度漏洞上下文，结合大语言模型自动生成 Pull Request，不仅替换被污染的版本号，还能运行测试用例验证 API 兼容性。
- **硬件 IoT / 固件供应链透视看板 (Connected Device CRA Dashboard)**：
  - 针对嵌入式/Arduino 设备编译生成的固件镜像，利用 CRACI 解析底层 C 库与协议栈依赖，实现符合欧盟硬件上市规范的透视平台。

---

## 6. 官网与关键资源链接 (Official Links & Key Resources)

- **官方主页 (Website)**：[https://craci.com](https://craci.com)
- **融资与行业报道 (Funding Coverage)**：
  - ArcticStartup: 《Helsinki-based CRACI raises €1.4M to help software companies automate CRA compliance》
  - StartupReporter: 《Craci Corporation raises Pre-Seed round led by Lifeline Ventures》
- **核心法规与标准参考 (Standards & Regulations)**：
  - 欧盟委员会官方网络抗逆力法案条文 (EU CRA Regulation (EU) 2024/2847): [eur-lex.europa.eu](https://eur-lex.europa.eu)
  - CycloneDX 软件物料清单标准: [https://cyclonedx.org](https://cyclonedx.org)
  - SPDX (Software Package Data Exchange): [https://spdx.dev](https://spdx.dev)
- **Junction 2026 大赛官方主页**：[https://hackjunction.com](https://hackjunction.com) | [https://hackjunction.app](https://hackjunction.app)
