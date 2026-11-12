# Context.dev (Context Data Inc.) — Junction 2026 Partner In-Depth Research Report

> **Partner Tags**: Tech & Challenge Partner | Next-Generation Web Data & Context Extraction API Platform for AI Agents & LLMs  
> **Official Website**: [https://context.dev](https://context.dev)  
> **Core Positioning**: Agentic Data Infrastructure & LLM-Ready Web Extraction (One-stop web data, crawling, and brand intelligence infrastructure enabling autonomous agents to seamlessly navigate and comprehend the World Wide Web)

---

## 1. Company Overview

- **Company Legal Name**: Context Data Inc. (branded as **Context.dev**, formerly **Brand.dev**)
- **Official Domain**: [https://context.dev](https://context.dev)
- **Headquarters**: San Francisco, California, USA
- **Founding Background & Core Team**:
  - **Yahia Bakour (Founder & CEO)**: Seasoned systems and platform engineering expert and serial entrepreneur. Formerly Principal Software Engineer / Engineering Manager at Sunrun, the leading global residential solar provider; prior to that, served as SDE2 and Tech Lead at Amazon, spearheading mission-critical retail checkout infrastructure processing hundreds of billions in annual gross merchandise volume; previously founded quantitative crypto monitoring tool StockAlarm.io, orchestrating a successful commercial acquisition.
  - **Ryan MacArthur (Co-Founder & Ecosystem Lead)**: Researcher in frontier security and distributed computing with deep expertise in zero-trust architectures, Trusted Execution Environments (TEEs), and agentic system infrastructure; long-standing active contributor to European and North American hackathon ecosystems (including multiple tenures as core mentor and judge at Junction), passionately championing the adoption of real-time web perception technologies among frontier builders.
  - **Incubation Background**: Context.dev (initially incubated under the Brand.dev moniker before expanding into a generalized agentic web data fabric) was backed by premier startup accelerator **Y Combinator (YC S26)**, securing robust backing from top-tier Silicon Valley angel investors and prominent AI venture firms from its inception.
- **Pain Points & Founding Thesis**:
  - The contemporary World Wide Web was architected over the past three decades **explicitly for human visual browsing**: saturated with bloated DOM hierarchies, dynamic JavaScript Single-Page Application (SPA) hydration, modal popups, cookie consent overlays, and aggressive bot mitigation systems (e.g., Cloudflare, DataDome).
  - Modern autonomous agents and Retrieval-Augmented Generation (RAG) pipelines demand real-time, high-fidelity, pristine web context. However, engineering teams routinely squander weeks spinning up and maintaining brittle headless Chromium browser clusters, procuring costly residential proxy pools, solving CAPTCHAs, and maintaining fragile HTML regex parsers.
  - Context.dev was created to abstract the grueling complexities of web scraping, anti-bot circumvention, and semantic cleaning behind a single modern API, **transforming the live web into machine-ready high-density Markdown and strictly typed JSON with one call**.
- **Industry & Technological Standing**:
  - Positioned squarely in the top tier of Silicon Valley's surging "Agentic Data Infrastructure" sector.
  - Outperforms legacy scraping toolchains in developer experience, joining pioneers like Firecrawl, Tavily, and Jina Reader in establishing the "Gold Standard for Web Extraction in the LLM Era".
  - Its specialized **Brand & Firmographics Intelligence** engine is broadly deployed across fintech, competitive intelligence, B2B sales enablement, and marketing automation—widely recognized as an AI-native, intelligent "Clearbit alternative".

---

## 2. Core Products & Technical Architecture

Context.dev delivers a modern, lightning-fast, high-availability RESTful API and plug-and-play multi-language SDKs, liberating developers from underlying web scraping intricacies with a single API key.

### 2.1 Feature Breakdown & Core Endpoint Architecture

#### 1. Web Scraping & Markdown Transformation (`/web/*`)
- **LLM-Ready Clean Markdown (`GET /web/scrape/markdown`)**:
  - Accepts any target URL, automatically spins up headless browsers to render dynamic JavaScript, and bypasses complex anti-bot bot mitigation systems.
  - Semantically detects and strips away navigation bars, footers, ad banners, sidebars, and superfluous scripts, outputting clean, highly structured Markdown with hierarchical headings and hyperlinks. This content can be injected directly into LLM context windows, slashing token consumption.
- **Raw HTML Extraction (`GET /web/scrape/html`)**:
  - Delivers pristine, fully hydrated DOM trees post-JS execution for advanced developers requiring custom AST parsing.
- **Visual Web Perception & Full-Page Screenshots (`GET /web/screenshot`)**:
  - Captures high-resolution PNG viewports or full-page scrolling captures, supplying direct visual ground truth for Vision-Language Models (VLM Agents, e.g., GPT-4o, Claude 3.5 Sonnet).
- **Design Asset Extraction (`GET /web/styleguide` & `GET /web/fonts`)**:
  - Extracts full site color palettes (Hex values), typography scales, and font families in seconds, enabling frontend agents to replicate and align UI aesthetics automatically.

#### 2. Full-Site Crawling & Sitemap Ingestion (`POST /web/crawl`)
- **Recursive Web Crawling (`POST /web/crawl`)**:
  - Given a seed domain (e.g., `https://docs.example.com`), the engine concurrently discovers and crawls pages according to specified depth and path filters, packaging clean Markdown across all pages to rapidly assemble corpus data for proprietary RAG pipelines.
- **Intelligent Sitemap Parser (`GET /web/scrape/sitemap`)**:
  - Detects, parses, and resolves remote `sitemap.xml` feeds into structured URL index inventories.

#### 3. Structured Data Extraction & AI Querying (`/brand/ai/*` & `/web/extract`)
- **Schema-Guided Strongly Typed Extraction**:
  - Developers pass a target URL alongside an arbitrary JSON Schema; the underlying neural extraction engine interprets page semantics and extracts conforming, type-safe JSON payloads.
- **E-Commerce Catalog & Product Parsing (`POST /brand/ai/product` & `POST /brand/ai/products`)**:
  - Programmatically extracts product titles, active prices, list prices, SKUs, multi-angle imagery, and variant attributes across diverse platforms (Shopify, Amazon, custom storefronts).
- **Natural Language Web Inquiries (`POST /brand/ai/query`)**:
  - Formulates direct natural language questions against web pages at the API layer, eliminating the need to ingest entire bodies of text into secondary prompt templates.

#### 4. Enterprise & Brand Firmographic Intelligence (`/brand/*`)
- **Comprehensive Brand Profile Retrieval (`GET /brand/retrieve`)**:
  - Ingests a company domain and returns rich corporate identity assets including high-resolution vector logos, primary/secondary brand hex codes, social media profiles (Twitter/X, LinkedIn, GitHub), company bios, founding years, and standard industry codes (NAICS / SIC).
- **Multi-Vector Entity Resolution**:
  - Supports reverse entity lookup via legal names (`retrieve-by-name`), stock tickers (`retrieve-by-ticker`), corporate email domains (`retrieve-by-email`), and more.
- **Transaction Descriptor Normalization (`GET /brand/transaction_identifier`)**:
  - Instantly resolves obscure, truncated bank/credit card transaction descriptors (e.g., `AMZN MKTPLACE WA*2A1...`) into normalized corporate entities and verified domains.

### 2.2 Developer Ecosystem & Architectural Highlights
- **Base URL**: `https://api.context.dev/v1`
- **Minimalist Authentication**: Standard HTTP Bearer Token authentication (`Authorization: Bearer <API_KEY>`).
- **SDK Support**: First-party and community libraries spanning **Python, TypeScript / Node.js, Go, Ruby, and PHP**.
- **AI Framework Integrations**: Native connectors for LangChain, LlamaIndex, CrewAI, alongside first-class support for the Model Context Protocol (MCP), enabling direct mounting as external tools within Claude Desktop, Cursor, or custom agent runtimes.

---

## 3. Vision and Mission

### 3.1 Mission Statement
> **"To give agents the internet."**  
> Context.dev's foundational mission is to permanently eradicate the heavy engineering drag of web scraping, bot mitigation countermeasures, and data cleaning. It empowers global AI developers to connect their autonomous agents to the pulse of real-world digital information without having to build and babysit specialized crawler infrastructure.

### 3.2 Vision Statement
> **"To build the unified real-time context layer for the autonomous agent era."**  
> Context.dev believes the future internet will be predominantly consumed and driven by autonomous, collaborative AI agents. Context.dev strives to be the ubiquitous sensory cortex of this new paradigm, making live web data as effortless, rapid, structured, and dependable to query as local memory.

---

## 4. Category & Classification

- **Primary Category**:
  - **Agentic Data Infrastructure**
- **Secondary Categories**:
  - **LLM-Ready Web Extraction & Crawling API**
  - **Brand Intelligence & Firmographics Enrichment**
  - **RAG Context Ingestion Pipeline**
  - **Multi-Modal Web Perception for AI**

---

## 5. Role at Junction 2026 & Challenge Tracks Prediction

### 5.1 Hackathon Role & Positioning
At Junction 2026, Context.dev serves as the premier unfair advantage for hackathon teams constructing **agents endowed with live real-world web perception**.

Hackathon projects often fall flat when agents remain trapped within static training data or pricey closed APIs. The moment an idea requires "evaluating competitor pricing live," "investigating startup updates across the web," or "scraping municipal policy updates," teams stumble into brittle crawler scripts or 403 Forbidden roadblocks. With Context.dev, hackers need merely **three lines of code** to feed any URL, comprehensive documentation hub, or corporate brand intelligence directly into their agents, elevating demo polish and technical execution.

### 5.2 Anticipated Challenge Tracks & Themes

1. **Autonomous Deep Research & Due Diligence Agent**:
   - **Challenge Prompt**: Build an autonomous AI agent capable of conducting end-to-end investment or competitive due diligence on specified companies or niche markets.
   - **Technical Implementation**: The agent leverages Context.dev `/web/crawl` to ingest whole corporate sites and technical whitepapers, coupled with `/brand/retrieve` to pull firmographic profiles and competitor ecosystems, synthesizing comprehensive multi-page market reports detailing business models, competitive moats, and technical architectures.

2. **Real-Time Competitive Intelligence & Brand Radar**:
   - **Challenge Prompt**: Design a 24/7 automated reconnaissance radar across cross-border e-commerce, developer tooling, or consumer electronics.
   - **Technical Implementation**: Utilizes Context.dev `/brand/ai/products` and schema extraction to monitor rival catalog drops, discounting patterns, UI color changes, and positioning shifts, firing automated tactical alerts and analysis via webhooks.

3. **Multimodal Agentic Browser & UI Replicator**:
   - **Challenge Prompt**: Push the frontier of vision-language models interacting with the live visual web.
   - **Technical Implementation**: Combines Context.dev `/web/screenshot`, `/web/styleguide`, and clean Markdown to empower agents that not only read page copy, but also interpret visual aesthetics, generating clean, production-grade frontend component code mirroring the target interface ("Vibe-to-Code").

### 5.3 Quickstart Code Example

```python
"""
Junction 2026: Build a real-time web extraction agent in 3 minutes with Context.dev
Install dependencies: pip install requests
"""
import os
import requests

CONTEXT_API_KEY = os.environ.get("CONTEXT_API_KEY", "your_context_api_key_here")
BASE_URL = "https://api.context.dev/v1"
HEADERS = {
    "Authorization": f"Bearer {CONTEXT_API_KEY}",
    "Content-Type": "application/json"
}

def scrape_url_to_markdown(target_url: str) -> str:
    """Scrape a target URL and transform it into clean, LLM-ready Markdown."""
    endpoint = f"{BASE_URL}/web/scrape/markdown"
    params = {"url": target_url}
    
    response = requests.get(endpoint, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("markdown", "")

def get_brand_intelligence(domain: str) -> dict:
    """Extract corporate brand metadata (logos, palette, social links, industry classification)."""
    endpoint = f"{BASE_URL}/brand/retrieve"
    params = {"domain": domain}
    
    response = requests.get(endpoint, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    test_domain = "anthropic.com"
    print(f"[*] Retrieving brand intelligence for {test_domain}...")
    brand_info = get_brand_intelligence(test_domain)
    print(f"Brand Name: {brand_info.get('name')}")
    print(f"Brand Logo: {brand_info.get('logo')}")
    print(f"Primary Color: {brand_info.get('colors', {}).get('primary')}")
    print(f"Social Links: {brand_info.get('socials')}")
    
    print("\n[*] Extracting high-density Markdown context from web page...")
    markdown_content = scrape_url_to_markdown(f"https://{test_domain}")
    print(f"Extracted Content Preview (First 300 characters):\n{markdown_content[:300]}...")
```

---

## 6. Official Links & Key Resources

- **Official Website**: [https://context.dev](https://context.dev)
- **Developer Documentation**: [https://docs.context.dev](https://docs.context.dev)
- **API Reference Specification**: [https://context.dev/docs/api-reference](https://context.dev/docs/api-reference)
- **Official GitHub Organization**: [https://github.com/context-dev](https://github.com/context-dev)
- **Official Blog & Changelog**: [https://context.dev/blog](https://context.dev/blog)
