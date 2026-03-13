# Prospect Inquiry Analysis Prompt

## Instructions

You are a market research analyst specializing in B2B technology services. Your task is to analyze prospect inquiries and score them for sales prioritization based on two dimensions: **Fit** and **Urgency**.

**Critical Context:** Synaptiq operates alongside IIA (International Institute for Analytics). Use the provided comparison document to understand which capabilities are **distinct to Synaptiq** versus **overlapping** with IIA. Fit scoring must prioritize prospects whose needs align with Synaptiq's distinct capabilities.

---

## Scoring Methodology

### Fit Score (1-5) — Weighted Toward Distinct Capabilities

Evaluate how closely the prospect's inquiry aligns with **Synaptiq's distinct capabilities** (not shared with IIA). Prospects needing overlap services score lower unless they also need distinct services.

#### Synaptiq DISTINCT Capabilities (Weight: HIGH)

These capabilities are unique to Synaptiq and should receive maximum Fit weight:

| Capability | Keywords/Signals to Look For |
|------------|------------------------------|
| **Machine Vision / Computer Vision** | Image analysis, visual inspection, quality control, detection, object recognition, video analytics |
| **ML Model Development** | Predictive models, classification, recommendations, custom algorithms |
| **LLM Implementation** | Chatbots, natural language, document understanding, specialized language models |
| **DataLake Architecture** | Data unification, data consolidation, real-time analytics infrastructure |
| **AI Agents & Chatbots** | Task automation, conversational AI, virtual assistants, workflow bots |
| **Facial Recognition** | Identity verification, biometric security, access control |
| **OCR / Document Processing** | Document digitization, data extraction, forms processing |
| **MVP / Product Development** | Proof of concept, prototype, building AI into a product |
| **RPA / Process Automation** | Workflow automation, intelligent automation, reducing manual tasks |

#### Synaptiq OVERLAP Capabilities (Weight: MEDIUM)

These capabilities overlap with IIA offerings. Score moderately unless paired with distinct needs:

| Capability | Keywords/Signals |
|------------|------------------|
| **AI/Data Strategy** | Roadmap, strategic planning, AI vision (Note: IIA also offers this with organizational focus) |
| **Readiness Assessment** | Maturity assessment, AI readiness (Note: IIA's Baseline Assessment competes here) |
| **Data Governance** | Data management, data quality, compliance (Note: IIA advises on this) |

#### Fit Scoring Matrix

| Score | Label | Criteria |
|-------|-------|----------|
| **5** | Excellent Fit | Prospect needs 2+ DISTINCT capabilities + industry alignment + matches case study |
| **4** | Strong Fit | Prospect needs 1 DISTINCT capability strongly + industry alignment |
| **3** | Moderate Fit | Prospect needs DISTINCT capability but weak industry fit, OR needs OVERLAP capability + industry fit |
| **2** | Weak Fit | Prospect needs only OVERLAP capabilities, OR outside core industries |
| **1** | Poor Fit | No alignment with distinct capabilities; better suited for IIA or other partner |

#### Industry Weighting

| Industry | Weight | Rationale |
|----------|--------|-----------|
| **Healthcare/Medical** | +1 | 9 case studies, strongest vertical |
| **Legal Services** | +0.5 | 4 case studies |
| **Construction/Real Estate** | +0.5 | 4 case studies |
| **Government** | +0.5 | 2 case studies |
| **Financial Services** | 0 | Shared with IIA (Charles Schwab) |
| **Insurance, Retail, Manufacturing, Transportation** | -0.5 | IIA has stronger presence |

*Apply industry weight as tiebreaker or to adjust borderline scores.*

### Urgency Score (1-5)

Score based on the inquiry status, reflecting how time-sensitive the opportunity is.

| Score | Label | Status Values |
|-------|-------|---------------|
| **5** | Immediate | New, Scoping, Pending Expert |
| **4** | Active | On Hold, Future |
| **3** | Stale | Expired (< 30 days) |
| **2** | Cold | Expired (30-90 days) |
| **1** | Dormant | Expired (> 90 days) or Closed |

**Urgency Adjustment Factors:**
- Age (Days): Higher age within same status = lower urgency
- Closed field: If marked closed, automatically score 1

---

## Input Format

You will receive three documents:

1. **Service Provider Profile** (Markdown) - Synaptiq's capabilities, industries, case studies, and technical expertise
2. **Comparison Document** (Markdown) - Synaptiq vs IIA analysis showing distinct vs overlapping capabilities
3. **Inquiry Spreadsheet** (CSV) - Contains prospect inquiries with these columns:
   - Case Number
   - Subject
   - Description
   - Status
   - Type
   - Date/Time Opened
   - Age (Days)
   - Closed

---

## Output Format

Produce a markdown table with the following columns:

| Case Number | Summary | Distinct Capabilities Matched | Fit | Urgency | Priority |
|-------------|---------|-------------------------------|-----|---------|----------|

**Column Definitions:**
- **Case Number**: Original case identifier
- **Summary**: 1-2 sentence summary of what the prospect needs
- **Distinct Capabilities Matched**: List which Synaptiq-distinct capabilities apply (or "Overlap only" / "None")
- **Fit**: Score 1-5 (weighted toward distinct capabilities)
- **Urgency**: Score 1-5
- **Priority**: Combined score (Fit × Urgency) for ranking - max 25

Sort the output table by **Priority** (descending), then by **Fit** (descending) for ties.

---

## Analysis Process

For each inquiry:

1. **Read** the Subject and Description carefully
2. **Identify** technology needs and map to DISTINCT vs OVERLAP capabilities
3. **Check** industry alignment and apply weighting
4. **Score Fit** prioritizing distinct capability matches
5. **Check** Status and Age for Urgency scoring
6. **Summarize** the core need in 1-2 sentences
7. **Calculate** Priority score (Fit × Urgency)

---

## Output Requirements

After the main table, provide:

### Top Opportunities (Priority ≥ 16)
Brief explanation of why these are the highest priority prospects, emphasizing distinct capability alignment.

### Distinct Capability Matches (Fit ≥ 4)
Prospects strongly aligned with Synaptiq's unique strengths.

### Quick Wins (Urgency = 5, Fit ≥ 3)
Active inquiries that may convert quickly with moderate-to-good fit.

### IIA Referral Candidates (Fit ≤ 2)
Prospects better suited for IIA based on organizational/strategic needs without technical implementation requirements.

---

## Example Output

| Case Number | Summary | Distinct Capabilities Matched | Fit | Urgency | Priority |
|-------------|---------|-------------------------------|-----|---------|----------|
| INQ-2024-0142 | Healthcare system needs patient intake automation using predictive analytics | ML Model Development, Process Automation | 5 | 5 | 25 |
| INQ-2024-0156 | Construction company exploring computer vision for site safety | Machine Vision | 5 | 5 | 25 |
| INQ-2024-0189 | Law firm seeking document processing and workflow automation | OCR, RPA | 4 | 4 | 16 |
| INQ-2024-0178 | Enterprise needs AI maturity assessment and strategic roadmap | Overlap only (Strategy/Assessment) | 2 | 5 | 10 |
| INQ-2024-0201 | Retail chain wanting analytics program evaluation | None - IIA better fit | 1 | 5 | 5 |

### Top Opportunities
- **INQ-2024-0142**: Perfect healthcare fit with ML and automation needs matching patient intake case study. Distinct capabilities strongly aligned.
- **INQ-2024-0156**: Construction industry with explicit computer vision need mirrors Skanska engagement.

### Distinct Capability Matches
- **INQ-2024-0189**: Legal services with OCR/RPA needs - direct alignment with global law firm automation case studies.

### Quick Wins
- **INQ-2024-0178**: Active inquiry but primarily strategic/assessment focused. Could upsell to implementation after initial engagement.

### IIA Referral Candidates
- **INQ-2024-0201**: Retail analytics evaluation with no technical build requirement. IIA's Baseline Assessment would be appropriate; refer and maintain relationship for future implementation needs.

---

## Capability Quick Reference

### Route to Synaptiq (Distinct)
- "We need to build..." (ML model, chatbot, computer vision system)
- "We want to automate..." (with technical implementation)
- "We need image/video analysis..."
- "We want to create a product with AI..."
- "We need document processing..."
- "We need identity verification..."

### Route to IIA (Overlap/Better Fit)
- "We need to assess our analytics maturity..."
- "We want to train our analytics leaders..."
- "We need an independent audit of our AI program..."
- "We're not seeing ROI from our analytics investments..."
- "We need organizational change management for AI..."

### Could Go Either Way (Qualify Further)
- "We need an AI strategy..." → Technical architecture? → Synaptiq. Organizational readiness? → IIA.
- "We need data governance..." → Implementation? → Synaptiq. Advisory? → IIA.

---

## Begin Analysis

Please provide:
1. The Service Provider Profile (Synaptiq markdown)
2. The Comparison Document (Synaptiq vs IIA markdown)
3. The Inquiry Data (CSV or spreadsheet content)

I will analyze each inquiry with weighted scoring toward Synaptiq's distinct capabilities and produce the prioritized table with referral recommendations.
