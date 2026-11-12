# [2025] Valio Aimo — Zero-Fail Logistics

## Metadata

- **Year**: 2025
- **Challenge Partner**: Valio Aimo
- **Original Historical Track**: AI & Data
- **2026 Target Track**: Data Track
- **Sub-theme**: II. Retail Supply Chain, Logistics Scheduling & Sustainable Consumption Data Mining (Retail Supply Chain, Logistics & Consumption Data)
- **Core Theme**: Per-line out-of-stock probability prediction model based on order history, picking timestamps, supplier on-time rates, and quality anomaly logs
- **Classification Rationale**: Provides real wholesale orders, picking流水, inventory availability, and supplier delivery history data, requiring the construction of a per-line out-of-stock risk prediction model and an intelligent substitute matching matrix.

---

## Full Original Challenge Name

Zero-Fail Logistics

## Challenge Description

Reinvent delivery reliability with predictive AI and multilingual, automated customer care—voice first, text second.

Valio Aimo® serves 20,000+ professional kitchens. Today, missing items are often discovered at delivery or via next-morning manual calls—too late. At Junction 2025, we seek a multimodal AI solution (voice + text + image/video) that turns disruptions into proactive customer experiences and materially reduces operational workload.
Currently, when an ordered product is unavailable, customers only discover it at delivery or via a manual call the next day—too late. The goal is to automate the incomplete delivery process end-to-end.

Your challenge:

1. Pre-picking prediction – Use order, stock, and supplier/quality data to forecast which items are likely to be missing.

2. Proactive notice during picking – If a shortage is detected, an AI agent contacts the customer (call/text) in their language, proposes replacements, and confirms changes instantly.

3. Post-delivery remediation – If a shortage still occurs, the AI triggers after-the-fact outreach and arranges corrective delivery (same-day add-on run or next-day).

4. Multimodal claims – Explore voice, text, images, and video for handling delivery discrepancies.

Impact: This is not only about reducing manual work, but about saving an entire operations team’s workload while improving customer satisfaction.

## Challenge Insights

Risk model: per-line Out-of-stock probability (features: supplier reliability, quality incidents, seasonality, pick time windows, freshness SLAs, substitution matrix).

Voice-first agent: two-way calling (outbound & inbound), call-reason classification, intents, confirmations, and auditable logs.

Substitution logic: “good-better-best” per SKU based on availability and recipe suitability.

Images/video: detect and score missing items from photos of opened crates; attach a confidence score.

## Judging Criteria

Judging:
Feasibility (production-ready architecture)
Completeness of problem coverage (end-to-end)
Quality of AI integration & customer experience
Demonstrated operational impact (FTE savings).

Path to production: strong demos will be considered for real development with Valio Aimo and partners.

Clear guidance to teams:
Show risk model + agent + notification flow + substitution in one demo.

Bonus: photo/video claims + two-way calling (customer calls back → agent resolves).

## Prizes

Prizes: Top three teams win €2000, €1500, and €500.

## Resources

Participants will have access to:

- Real-world order and picking data.

- “Mock data” extracts: order history, pick lines (timestamps), stock & availability, exception/quality logs, supplier delivery history.

- Test access to e-commerce / Minun Aimo for context (no separate sandbox).

- Multilingual APIs (ASR/TTS/NLU) and messaging channels (SMS/WhatsApp/email) for voice & text.

- Mentoring: AI, logistics, customer ops + partner coaching on which background data is essential.

Preferred tech: AI agents (voice & chat), predictive models, NLP/NLU, multimodal (image/video), optional routing/slot optimization.

## About the Partner

Valio Aimo® was created in 2021 as a bold leap forward by Valio—transforming traditional wholesale into a next-generation foodservice powerhouse. We are more than a distributor: Aimo is where the breadth and agility of wholesale meet the deep product expertise, R&D capability, and brand-building strength of a global food innovator.
20,000 professional customers across restaurants, foodservice operators, and industrial customers rely on us to keep their business running every single day.

- 25,000 product names sourced from 700 trusted suppliers, forming one of the most comprehensive foodservice assortments in Finland

- 350 specialists are committed to delivering excellence in logistics, service, and digital transformation.

- As part of Valio—Finland’s leading dairy and food company with €2.3B in revenue, operations in 50 export markets, and a pioneering sustainability mission (carbon-neutral milk by 2035)—Aimo represents the cutting edge of how foodservice can be reinvented for the AI-driven age.

Valio Aimo® is not just serving today’s kitchens; we are shaping the future of foodservice.
