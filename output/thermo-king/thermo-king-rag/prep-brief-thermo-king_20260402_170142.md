# Consultant Prep Brief — Thermo King

*Generated: 2026-04-02 17:01:42*
*INTERNAL — NOT FOR DISTRIBUTION*

---

# Thermo King Prep Brief — Stephen Sklarew
**Contact:** Wendy (position TBD) | **Date:** TBD | **Duration:** 1 hour | **Type:** Introductory consult

---

## TL;DR
- **Who:** Thermo King — $5B transport refrigeration tech leader, subsidiary of Trane Technologies, ~2.5K employees globally
- **What they want:** Expert guidance on advanced RAG/document processing architecture — they're past basics, hitting complex multi-format challenges
- **Why now:** Successfully moved through "first phase" (PDF processing improvement), now scaling to Excel/PPT/Word with pipeline architecture decisions
- **The real ask:** Strategic consulting on generalized vs. specific processing, golden dataset structuring, and performance measurement frameworks
- **Key context:** They're technically sophisticated (billions of data points, embedded AI in telematics) with innovation-driven culture and performance obsession

---

## Company Snapshot

**Core Business:** Global leader in transport refrigeration (trucks, containers, rail) — they literally invented the industry in 1938. Think cold chain logistics backbone.

**Parent/Structure:** Trane Technologies subsidiary. Regional operations (Americas, EMEA, APAC). 900+ dealer locations across 85+ countries.

**Culture Codes:**
- **Innovation legacy:** "500+ U.S. patents," Frederick M. Jones Master Innovators club
- **Performance obsession:** Dealer awards based on "performance and leadership criteria"
- **Sustainability mission:** Reduce customer carbon footprint by 1 gigaton CO2 by 2030
- **Community focus:** Strong corporate social responsibility culture

**Key Players:**
- CEO: Erl Swierkowski (B- rating from employees — solid but not exceptional)
- VP Digital: Dominic Hand (your main counterpart likely)
- VP Connectivity: Declan McAndrew
- President Americas: Adam Wittwer

**Tech Sophistication Level:** HIGH. They're not AI beginners:
- AI embedded across 4 telematics levels
- Machine learning for predictive maintenance (>90% accuracy on failure prediction)
- Billions of weekly data points processed
- AWS Lambda, Azure SQL tech stack
- Remote Operating Center with 24/7 monitoring

---

## The Inquiry — What's Really Going On

**Surface level:** Need help with RAG architecture for multi-format documents (PDF/Excel/PPT/Word).

**What's actually happening:** They've proven RAG works (PDF success), but now facing the classic "scaling AI" inflection point. They're encountering architecture decisions that will define their next 2-3 years of AI capability.

**The underlying tension:** How do you balance flexibility vs. optimization when scaling AI systems? They're smart enough to know there's no universal answer — they need expert pattern matching from someone who's navigated this before.

**Wendy's likely hoping to hear:**
- "Yes, these are the right questions to be asking"
- Specific architectural patterns for their use cases
- Performance measurement frameworks that map to business value
- Confidence they're not missing something obvious

**Wendy's probably afraid of:**
- Building the wrong foundation and having to rebuild later
- Analysis paralysis on generalized vs. specific approaches
- Investing heavily in capabilities that don't translate to business impact

---

## Key Talking Points & Insights

### 1. **"Multi-Modal Document Architecture Patterns"**
**The insight:** Most orgs try to build one pipeline for all formats. Better approach is modular processing with unified retrieval layer.

**Why it lands:** Directly addresses their generalized vs. specific dilemma with a concrete architectural principle.

**How to introduce:** "When I see teams wrestling with Excel vs. PDF vs. PPT processing, the instinct is usually to build one unified pipeline. But what actually works better is..."

**Synaptiq reference:** Reference machine vision projects where we've handled diverse input types (images, documents, video) with modular processing architectures.

### 2. **"Golden Dataset Strategy for Production RAG"**
**The insight:** Golden datasets should mirror production data distribution, not just edge cases. Most teams over-index on outliers.

**Why it lands:** They specifically mentioned golden dataset structuring as a challenge — this gives them a framework.

**How to introduce:** "The golden dataset question is tricky because most teams build evaluation sets that don't reflect their actual query patterns..."

**Synaptiq reference:** Healthcare projects where we had to evaluate AI performance against real clinical workflows, not just textbook cases.

### 3. **"Performance Measurement Hierarchy for RAG"**
**The insight:** Layer metrics from technical (retrieval accuracy) to business (time saved, decision quality). Don't optimize technical metrics that don't predict business value.

**Why it lands:** Addresses their "what good looks like" concern with concrete measurement framework.

**How to introduce:** "When you're asking 'what does good performance look like,' there's usually a gap between what's easy to measure technically vs. what actually matters for business outcomes..."

**Synaptiq reference:** AIQ assessment methodology — we've developed frameworks for measuring AI business impact across organizations.

### 4. **"Context Window Strategy for Enterprise Documents"**
**The insight:** Enterprise docs (especially Excel/PPT) often have critical context in metadata, formatting, relationships between files. RAG architectures need to preserve this.

**Why it lands:** Shows deep understanding of enterprise document complexity beyond just text extraction.

**How to introduce:** "One thing we see with Excel and PowerPoint in particular is that the business context often lives in the structure and relationships, not just the content..."

**Synaptiq reference:** Legal document processing projects where relationships between documents were as important as individual content.

### 5. **"Scaling AI in Performance-Driven Cultures"**
**The insight:** Their dealer performance measurement culture is actually an asset for AI adoption — they already think in metrics and continuous improvement.

**Why it lands:** Connects their business culture to AI success patterns, shows you understand their organizational context.

**How to introduce:** "Looking at Thermo King's culture around performance measurement and dealer excellence — that's actually a huge advantage for scaling AI because..."

**Synaptiq reference:** Construction clients (Skanska, Ryan Companies) where performance measurement culture accelerated AI adoption.

### 6. **"Cold Chain Data Complexity Insight"**
**The insight:** Cold chain generates uniquely rich multimodal data (sensor, operational, regulatory, maintenance) — their document processing should connect to this broader data ecosystem.

**Why it lands:** Shows industry-specific understanding and suggests bigger strategic opportunities.

**How to introduce:** "Given the cold chain context, your document processing probably connects to sensor data, maintenance records, regulatory compliance... there's an opportunity to build RAG that bridges these data types..."

**Synaptiq reference:** IoT and operational data integration projects where document processing was part of larger data unification strategy.

---

## Landmines & Things to Avoid

### **Don't Position as "AI Beginners"**
- They're clearly sophisticated — avoid basic AI education
- Don't over-explain concepts like RAG or vector databases
- Jump straight to architectural and strategic questions

### **Avoid Generic Manufacturing Talk**
- Don't assume standard manufacturing pain points
- They're more tech company than traditional manufacturer
- Focus on their digital/connectivity sophistication

### **Don't Undersell Their Current Capabilities**
- They've already proven AI works at scale (telematics, predictive maintenance)
- Position as building on strength, not starting from scratch
- Respect their technical team's competence

### **Culture Sensitivities**
- Don't critique their innovation approach — they're proud of their patent history
- Acknowledge their market leadership position
- Performance culture means they want metrics and results, not just strategy

### **Avoid Parent Company Assumptions**
- Don't assume Trane Technologies corporate processes apply directly
- They operate with significant autonomy
- Focus on Thermo King specific context

---

## Recommended Meeting Flow (60 minutes)

### **Opening: Context & Positioning (5 min)**
- "Before we dive in, help me understand where you are in your RAG journey..."
- Listen for: current architecture, team composition, success metrics
- Position: "It sounds like you're exactly where we see most sophisticated teams at this stage..."

### **Deep Dive: Current State & Challenges (15 min)**
- Walk through their specific multi-format processing challenges
- Understand their architectural decisions so far
- Identify biggest friction points and scaling concerns
- Listen for: technical debt, performance bottlenecks, team capacity constraints

### **Strategic Discussion: Architecture Patterns (20 min)**
- Share modular processing insights (talking point #1)
- Discuss generalized vs. specific processing trade-offs
- Cover golden dataset strategy (talking point #2)
- Connect to their business context and performance culture

### **Performance & Measurement Framework (15 min)**
- Align on success criteria and measurement approaches (talking point #3)
- Discuss how to connect technical metrics to business value
- Reference their existing performance measurement culture
- Cover evaluation methodology evolution

### **Closing: Next Steps & Engagement Options (5 min)**
- Summarize key insights and alignment
- Propose specific next steps (likely AIQ assessment or architecture review)
- Exchange contact information and timeline expectations

---

## What Success Looks Like

### **For Wendy (this call):**
- Confidence they're asking the right questions and approaching challenges correctly
- Specific insights about architectural patterns they hadn't considered
- Clear sense that Synaptiq understands their level of sophistication
- Framework for thinking about performance measurement and business value alignment

### **For the broader engagement:**
- Scalable RAG architecture that handles diverse document types efficiently
- Performance measurement framework that connects AI capabilities to business outcomes
- Golden dataset methodology that supports continuous improvement
- Strategic clarity on generalized vs. specific processing approaches

### **For Stephen/Synaptiq:**
- Qualify as high-potential client with sophisticated AI needs and budget capacity
- Position for strategic engagement (not just tactical implementation)
- Next step: Propose AIQ assessment focused on RAG architecture maturity or direct architecture consulting engagement
- Timeline: Likely 2-3 month engagement starting with architecture review

---

## Power Moves

1. **Reference their telematics AI sophistication early** — shows you've done homework and respect their capabilities
2. **Connect document processing to their broader data ecosystem** — positions larger strategic opportunity
3. **Use their performance measurement culture** — frame everything in terms of measurable business outcomes
4. **Acknowledge their "second phase" maturity** — validate they're past basics and ready for sophisticated challenges
5. **Propose concrete next step** — AIQ assessment tailored to RAG architecture maturity, not basic AI readiness