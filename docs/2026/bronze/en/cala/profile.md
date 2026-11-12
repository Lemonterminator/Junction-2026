# Cala (cala.ai) — Junction 2026 Challenge Partner In-Depth Research Profile

> **Research Category**: Junction 2026 Bronze Challenge Partner Profile  
> **Core Tags**: AI Agent Data Infrastructure | Structured Knowledge Graph & Truth Engine | Native Model Context Protocol (MCP) Provider | Financial & Regulatory Due Diligence  
> **Archive Path**: `bronze/en/cala/profile.md` & `docs/2026/bronze/en/cala/profile.md`  

---

## 1. Company Overview

- **Company Entity Name**: Cala (Cala AI)
- **Official Portal**: [https://cala.ai](https://cala.ai)
- **Headquarters**: European / US Distributed
- **Industry Standing**: The dedicated structured knowledge layer and verified data infrastructure engineered for autonomous AI agents and large language models (LLMs).
- **Core Value Proposition**: *"The preferred data layer for agents. At Cala we process data so you don't have to. Skip the data and start building."*
- **Critical Entity Disambiguation**:
  > [!IMPORTANT]
  > **Key Entity Resolution Audit (Ground Truth Verified)**:
  > The official hackathon challenge partner is **Cala AI (`https://cala.ai`)**, an enterprise data infrastructure provider for AI agents. It is **NOT** the identically named apparel supply chain SaaS `ca.la` (which rebranded to Mercer). The official Junction 2026 Partners showcase links directly to `https://cala.ai`.

---

## 2. Core Products & Technical Architecture

Cala directly resolves the primary bottleneck confronting modern autonomous agents during internet information retrieval: traditional web scrapers return noisy, ad-cluttered, unformatted HTML prose with fluctuating temporal validity. This induces prompt context bloat, schema parsing failures, and hallucinated reasoning leaps in agent workflows.

### 2.1 Structured World Knowledge Foundation (The World's Knowledge, Structured)
- **Verified Facts vs. Web Chaos**: Cala pre-ingests, disambiguates, cleans, and semantically aligns global authoritative sources, enabling AI agents to query deterministic, strongly typed entities rather than navigating messy unstructured web pages.
- **Maximum Token Efficiency**: Strongly typed schema responses reduce useless token consumption by 70% to 85% compared to raw web prose, slashing LLM API inference costs.
- **Full Data Provenance & Lineage**: Every property and field is timestamped, bounded by valid effective dates, and linked directly to immutable authoritative source citations, completely eliminating factual hallucinations in agent decision loops.

### 2.2 Core Verticals & Authoritative Data Ingestion (One Endpoint, Any Industry)
- **Finance, Risk Management & Regulatory Compliance (KYC / AML)**:
  - **SEC / EDGAR Filings**: 10-K (Annual Reports), 10-Q (Quarterly Reports), 8-K (Material Events), Proxy Statements, and Form 4 Insider Transactions.
  - **Capital Markets & Liquidity Telemetry**: Major exchange quotes, CBOE, FINRA TRACE fixed-income trade reporting, and Federal Reserve Economic Data (FRED).
  - **Credit & Sovereign Ratings**: Issuer credit ratings from Moody's, S&P, and Fitch, alongside FDIC bank health classifications and Federal Reserve stress test matrices.
  - **Global Sanctions & Watchlists**: OFAC Specially Designated Nationals (SDN), EU Consolidated Financial Sanctions List, UN Security Council Sanctions, and FinCEN anti-money laundering alerts.
  - **Corporate Registries & Ultimate Beneficial Ownership (UBO)**: UK Companies House, US Secretary of State filings, and cross-jurisdictional ultimate corporate ownership trees.
  - **Litigation & Case Law**: US Federal Court PACER filings, CourtListener, and cross-border judicial judgments.
  - **Central Banking & Monetary Policy**: Federal Reserve H-series releases, European Central Bank (ECB) statistical data warehouses, and Bank for International Settlements (BIS) metrics.
  - **Politically Exposed Persons (PEP)**: Official UN, EU, and global national government gazette directories.
- **Healthcare & Life Sciences**: Pharmaceutical registries, clinical practice guidelines, public health mandates, and biomedical literature metadata.
- **Legal & Governance**: Statutory revisions, regulatory frameworks, model contract benchmarks, and compliance clause comparisons.
- **Horizontal Expansion**: Extending structured schemas into Human Resources (HR) and AgTech.

### 2.3 AI-Native Developer Integration
- **Native Model Context Protocol (MCP) Endpoint**:
  - Delivers a production-grade remote MCP server (`https://api.cala.ai/mcp/`), connecting out-of-the-box via standard `mcp.json` to Cursor, Claude Code, Antigravity, Claude Desktop, n8n, LangChain, or custom autonomous runtime environments.
  ```json
  {
    "mcpServers": {
      "cala": {
        "url": "https://api.cala.ai/mcp/",
        "headers": {
          "X-API-KEY": "YOUR_CALA_API_KEY"
        }
      }
    }
  }
  ```
- **Fine-Grained Property Chaining API**:
  - Deterministic property chaining across entities, temporal windows, and financial statements (e.g., `Acme.Financials.NetIncomeLoss.From=2016.To=2026`).

---

## 3. Vision and Mission

### Vision
> *"To build the global knowledge layer for the agentic era — where every AI agent queries verified truth instead of digital noise."*  
> 
> Cala envisions an ecosystem where foundation models transcend web hallucination, collaborating across a deterministic, verifiable, and semantically linked global knowledge graph.

### Mission
> *"At Cala we process data so you don't have to. Skip the data and start building."*  
> 
> Eliminating the fragile scraping, parsing, and pipeline maintenance burdens for AI engineers, providing an instant, authoritative knowledge foundation with cryptographic data lineage.

---

## 4. Category & Classification

- **Primary Category**: **AI Agent Data Infrastructure**
- **Secondary Categories**:
  - **Structured Knowledge Graph & Truth Engine**
  - **Model Context Protocol (MCP) Fact Provider**
  - **Regulatory, Financial & Firmographics Intelligence**

---

## 5. Role at Junction 2026 & Challenge Tracks Prediction

### Target Challenge Tracks
- **Agentic AI Track**
- **FinTech & Corporate Due-Diligence Track**
- **Data & Real-Time Intelligence Track**

### Hackathon Friction Eliminated
Hackers designing autonomous agents routinely lose 10+ hours wrangling BeautifulSoup, Playwright scripts, and flaky regexes that inevitably trigger IP blocks and CAPTCHAs during live judging. By configuring the Cala MCP endpoint, **teams endow their agents with a decade of verified SEC balance sheets, global sanctions records, and corporate ownership graphs within 60 seconds.**

### Challenge Problem Statements

1. **Autonomous KYC & Deep Due-Diligence Agent**:
   - Given a target corporation name, an autonomous agent orchestrates Cala MCP tools to trace UBO ownership structures, cross-examine OFAC/EU sanctions registries, evaluate recent 8-K disclosures, and compile an institutional-grade compliance audit memorandum.
2. **Macro Supply-Chain Shock Navigator**:
   - Ingesting central bank releases, FRED macro indicators, and trade flow data via Cala, the agent performs instant causal impact modeling following geopolitical conflicts, interest rate pivots, or energy supply disruptions.
3. **Swarm Equity Research Desk via MCP**:
   - Deploy a collaborative agent swarm comprising an Industry Sector Analyst, a Legal Compliance Auditor, and a Financial Modeler. All agents share the Cala MCP pipeline to execute multi-year cross-company balance sheet audits and flag abnormal valuation anomalies in real time.

---

## 6. Official Links & Key Resources

- **Official Website**: [https://cala.ai](https://cala.ai)
- **Developer Documentation**: [https://cala.ai/docs](https://cala.ai/docs)
- **Production MCP Endpoint**: `https://api.cala.ai/mcp/`
- **Online Playground & Interactive Console**: [https://cala.ai/try](https://cala.ai/try)
