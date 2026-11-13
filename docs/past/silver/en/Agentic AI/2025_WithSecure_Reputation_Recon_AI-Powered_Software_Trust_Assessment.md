# [2025] WithSecure — Reputation Recon: AI-Powered Software Trust Assessment

## Metadata

- **Year**: 2025
- **Challenge Partner**: WithSecure
- **Original Historical Track**: Security
- **2026 Target Track**: Agentic AI Track
- **Sub-theme**: II. Compliance Auditing, Security Recon & Enterprise Knowledge Agents
- **Core Theme**: Autonomous software security posture recon Agent for CISOs (entity disambiguation, CVE/CISA traceability, and MCP assessment)
- **Classification Rationale**: Originating from the Security track, given minimal input (product name or URL), a GenAI assessment agent automatically retrieves high signal-to-noise security signals across the web (PSIRT, CVE, CISA KEV, compliance certifications), completes entity resolution, evidence mapping, and 0–100 risk scoring, with special mention of assessing emerging MCP services.

---

## Full Original Challenge Name

Reputation Recon: AI-Powered Software Trust Assessment

## Challenge Description

Build an AI assessor that turns a product name or URL into a CISO-ready trust brief with sources in minutes.

Security teams and CISOs (Chief Information Security Officer) are constantly asked to approve new tools they’ve never seen before. They need accurate, concise, and source-grounded snapshots of a product’s security posture, fast. This challenge asks participants to build a GenAI-powered assessor that fetches reliable signals from the web and synthesizes them into a decision-ready brief. Help us move security from reactive firefighting to proactive enablement.

Note: Teams may optionally evaluate emerging integration frameworks (e.g., MCP services) as targets of assessment, but MCP is not required.

Given minimal input (product name, vendor, or URL), build a system that:
- Resolves the entity and vendor identity.
- Classifies the software into a clear taxonomy (e.g., File sharing, GenAI tool, SaaS CRM, Endpoint agent).
- Produces a concise security posture summary with citations.
- Covers: description, usage, vendor reputation, CVE trend summaries (Common Vulnerabilities and Exposures), incidents/abuse signals, data handling/compliance, deployment/admin controls, and transparent 0–100 trust/risk score with rationale and confidence.
- Suggests 1–2 safer alternatives with short rationale.

Deliverables can be a CLI (Command Line Interface), service, or bonus web UI with compare-view. A lightweight local cache with timestamps and reproducibility is required.

## Challenge Insights

Focus on high-signal sources: vendor security/PSIRT pages (Product Security Incident Response Team), Terms of Service/Data Processing Agreement, (System and Organization Controls Type II), ISO attestations, reputable advisories/CERTs (Notices from Computer Emergency Response Teams or vendors), and CISA KEV (CISA Known Exploited Vulnerabilities catalog). Guard against hallucinations by labeling vendor-stated vs. independent claims. When data is scarce, return “Insufficient public evidence.”

## Judging Criteria

Evaluation criteria: 

Problem-fit and readability; correct entity resolution and categorization; evidence quality; security posture synthesis (trends, incidents, compliance); technical execution and resilience; transparent scoring logic; relevant alternatives with mini-compare.

Functional Requirements
- Minimal Input: Accept product name, vendor, or URL; resolve to canonical product.
- Categorization: Assign at least one category from taxonomy with justification.
- Security Posture: Summarize CVE trends (12–24mo), incidents/abuse, compliance posture, admin controls.
- Trust/Risk Rating: Transparent 0–100 with rationale and confidence.
- Alternatives: Suggest safer tools with short rationale.
- Citations: ≤8 URLs, each mapped to claims.
- Interface: CLI (Command Line Interface) or service; bonus simple compare UI.
- Local Cache: Required with timestamps and reproducibility.

Non-Functional Requirements
- GenAI use: entity resolution, classification, summarization; guard against hallucinations.
- Privacy: no customer PII; label vendor vs independent claims.
- Reproducibility: deterministic prompts, snapshot mode, cached raw fetches.
- Resilience: handle missing data, API rate limits, partial failures gracefully.

Evaluation Rubric (100 pts)
- Problem fit & clarity (15)
- Entity resolution & categorization (20)
- Evidence & citation quality (24)
- Security posture synthesis (12)
- Technical execution & resilience (15)
- Trust/risk score transparency (8)
- Alternatives & quick compare (6)

Winning projects will emphasize clarity: a brief readable in under 2 minutes, ≤8 links, transparent scoring logic, and explicit evidence labeling.

## Prizes

Prizes: €2,000 / €1,500 / €500 (Top-3 teams)

## Resources

Withsecure will provide:

Pre-prepared list of applications (names, optional binary hashes).

Guidance on source prioritization and claim–evidence mapping.

Public references: CVE/CVSS (Common Vulnerability Scoring System) databases, CISA KEV, vendor security pages, disclosure/bug bounty sites.

Example prompts for entity resolution and categorization.

Mentors on-site during the weekend (technical + domain expertise).

Bonus theme: assessing MCP-style integrations.

Required: lightweight local cache (JSON/SQLite), snapshot mode, deterministic parameters.

## About the Partner

At WithSecure™, we believe cyber security should empower, not overwhelm. That’s why our Elements Cloud blends AI, expertise, and co-security to deliver results that matter. We’ve got your back — and we’ll make it easy.

At Junction 2025, we bring cutting-edge cyber expertise straight to the builders shaping tomorrow.

---

**Verified award update:** Aegis won first place in the WithSecure challenge, according to its team; its research agent searches general sources and malware databases. Reputation Recon is the challenge title, not the winning project name. [Winner’s post](https://lnkd.in/p/dDKVFCKi).
