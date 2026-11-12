# CRACI (Craci Corporation) — Junction 2026 Tech Partner Research Report

> **Research Classification**: Junction 2026 Bronze Tech Partner Profile  
> **Company Tags**: Software Supply Chain Security | EU Cyber Resilience Act (CRA) Compliance | Automated SBOM in CI/CD  
> **Archive Paths**: `bronze/en/craci/profile.md` & `docs/2026/bronze/en/craci/profile.md`  

---

## 1. Company Overview

| Attribute | Detailed Information |
| :--- | :--- |
| **Company Legal Name** | Craci Corporation Oy (Commercial Brand: CRACI) |
| **Official Website** | [https://craci.com](https://craci.com) |
| **Headquarters** | Helsinki, Finland |
| **Year Founded** | 2025 |
| **Founding Team** | - **Juho Niemi** (Co-Founder & CEO)<br>- **Dennis Marttinen** (Co-Founder & CTO, prominent contributor to Nordic open-source security and systems infrastructure)<br>- **Jaakko Sirén** (Co-Founder & Head of Engineering/Product)<br>- **Petteri Pulkkinen** (Co-Founder & Operations/Growth) |
| **Funding & Capital Raised** | **Pre-Seed Round: €1.4M (approx. $1.5M USD) completed** |
| **Lead Investors** | Led by **Lifeline Ventures** (legendary Finnish early-stage venture firm, early backers of European unicorns including Supercell, Wolt, and MariaDB), with participation from **First Fellow Partners** (founded by former Nokia Chairman / Rovio CEO Risto Siilasmaa) and **Wave Ventures** |
| **Team DNA** | Deep expertise in OS and container runtime auditing, CI/CD pipeline virtualization, automated Software Bill of Materials (SBOM) generation, and EU regulatory cybersecurity compliance engineering |

---

## 2. Core Products & Technical Architecture

### 2.1 Flagship Platform: CRACI CI/CD Native Compliance Engine
CRACI's breakthrough innovation shifts compliance monitoring down to the bare metal of the CI/CD runner layer. Taking GitHub Actions as a prime example, developers migrate build jobs into CRACI's verified sandbox with a single line change:

```yaml
# Developers enable full compliance instrumentation with a single line
jobs:
  build-and-release:
    runs-on: craci    # Direct drop-in replacement for ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install && npm run build
```

### 2.2 Core Architectural Workflow

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

### 2.3 Key Features & Competitive Advantages
1. **Runner-Level Dynamic Capture**:
   - Permanently eliminates the blind spots of "stale static lockfiles." Accurately records actual runtime artifacts and binary packages pulled inside containers during builds, capturing dependencies hidden within nested tarballs or build-time compilation stages.
2. **Zero-Config Machine-Readable SBOM Export**:
   - Automatically generates and cryptographically signs standardized SBOMs alongside every production release, strictly adhering to Annex I, Section 2 of the EU Cyber Resilience Act.
3. **Commit-Level Blast Radius Mapping**:
   - When a new 0-day or CVE emerges upstream, CRACI identifies the exact Git commit and image tag impacted within seconds, delivering precise surgical remediation advisories directly to engineers and eliminating false-positive alert fatigue.
4. **Built-In CRA Article 14 Compliance Workflows**:
   - Out-of-the-box workflows for the mandatory early warning notification within 24 hours and comprehensive incident reporting within 72 hours (effective September 2026), alongside audit-ready technical documentation dossiers required for EU CE conformity (December 2027).

---

## 3. Vision and Mission

### 3.1 Vision
> **"To build a world where digital supply chains are transparent, verifiable, and secure by design — transforming heavy regulatory mandates from operational burdens into structural engineering advantages."**

With the passage of the EU Cyber Resilience Act (Regulation (EU) 2024/2847), all connected hardware and software products marketed across the European Union must mandate full-lifecycle cybersecurity, software bill-of-materials transparency, and rapid vulnerability reporting. CRACI believes that modern software engineering should not be crippled by manual legal audits and checkbox compliance, but should instead achieve **compliance-by-default** through automated transparency in the core toolchain.

### 3.2 Mission
> **"To empower teams to ship software with confidence by providing full transparency into their software supply chain."**

CRACI executes this mission across four core architectural principles:
1. **Evidence over assertion**: Substituting the brittle guesswork of static scanners with cryptographic runtime execution and network egress evidence.
2. **Secure by default**: Tracking every dependency transition silently and automatically without requiring intricate rule configuration.
3. **Open standards - no lock-in**: Native, uncompromising adherence to global open specifications such as SPDX and CycloneDX.
4. **Compliance without the tax**: Running compliance automation seamlessly in the background without degrading developer velocity or deployment agility.

---

## 4. Category & Classification

### 4.1 Primary Category
- **Software Supply Chain Security**
- **EU Cyber Resilience Act (CRA) Automated Compliance**

### 4.2 Tech Tags & Taxonomies
`SBOM (Software Bill of Materials)` `CycloneDX` `SPDX` `CI/CD Build Runner Security` `GitHub Actions Runner` `Vulnerability Tracking & KEV Mapping` `Transitive Dependency Audit` `DevSecOps` `EU CRA Regulation (EU) 2024/2847`

### 4.3 Ecosystem Positioning
- **Versus Traditional Static Scanners (e.g., Snyk, Dependabot, SonarQube)**: Legacy tools parse static `package-lock.json` manifests or ASTs, remaining vulnerable to malicious payloads or binaries fetched dynamically in build scripts (e.g., `postinstall` hooks, Makefiles, Dockerfiles). CRACI **monitors directly at the OS kernel layer inside the CI/CD runner**, capturing true ephemeral build-time dependencies.
- **Versus General GRC Platforms (e.g., Vanta, Drata)**: General compliance platforms focus on HR policies and high-level SOC 2 / ISO questionnaires, lacking direct integration with binary compiler streams, transitive build graphs, or strict EU CRA incident reporting clocks (24h / 72h). CRACI is purpose-built as an engineering execution engine for the CRA.

---

## 5. Role at Junction 2026 & Challenge Tracks Prediction

### 5.1 Hackathon Role & Positioning
- **Role**: Junction 2026 Bronze Tech Partner.
- **Theme Alignment**: Directly anchors the overarching **"European Tech Renaissance"** theme of Junction 2026, tackling the most formidable barrier European startups encounter when scaling globally: software supply chain sovereignty and regulatory compliance.

### 5.2 Recommended Tracks
- **Security Track**: Building next-generation self-healing software supply chains, dependency attestation protocols for AI agents, or automated security patch bots.
- **AI Infrastructure Track (by Verda)**: Auditing and monitoring third-party Python, PyTorch, and CUDA wheel dependencies in distributed model training pipelines to prevent model poisoning and supply chain trojans.
- **Agentic AI Track**: Designing runtime sandboxes and verifiable behavioral attestation for autonomous coding agents executing external packages and shell commands.

### 5.3 Typical Hackathon Implementation Scenarios
- **The Instant-CRA Verified Badge**:
  - Hackathon teams append `runs-on: craci` to their CI pipelines across Web, Mobile, or IoT repositories. In their final project demo, teams showcase an automatically generated CycloneDX SBOM and verified zero-CVE attestation as decisive proof of production readiness.
- **Autonomous CVE Remediation Bot**:
  - Combining CRACI's granular vulnerability context with LLMs to automatically generate verified pull requests that not only increment compromised dependencies, but also run regression test suites to guarantee API compatibility.
- **Connected Device CRA Dashboard**:
  - Parsing low-level C libraries and RTOS protocol stack dependencies from compiled embedded/Arduino firmware images, delivering a regulatory transparency portal satisfying EU CE hardware conformity.

---

## 6. Official Links & Key Resources

- **Official Website**: [https://craci.com](https://craci.com)
- **Funding & Industry Coverage**:
  - ArcticStartup: *"Helsinki-based CRACI raises €1.4M to help software companies automate CRA compliance"*
  - StartupReporter: *"Craci Corporation raises Pre-Seed round led by Lifeline Ventures"*
- **Core Regulations & Technical Standards**:
  - Official European Commission Text (EU CRA Regulation (EU) 2024/2847): [eur-lex.europa.eu](https://eur-lex.europa.eu)
  - CycloneDX SBOM Specification: [https://cyclonedx.org](https://cyclonedx.org)
  - SPDX (Software Package Data Exchange): [https://spdx.dev](https://spdx.dev)
- **Junction 2026 Official Links**: [https://hackjunction.com](https://hackjunction.com) | [https://hackjunction.app](https://hackjunction.app)
