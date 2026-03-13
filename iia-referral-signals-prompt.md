# IIA Referral Signal Extraction Prompt

## Purpose

Analyze prospect inquiries to identify patterns and signals that indicate a strong fit for **Synaptiq's distinct capabilities**. The output is a practical reference guide IIA staff can use to recognize Synaptiq referral opportunities in future inquiries and customer conversations.

**Note:** This analysis ignores inquiry status, age, and urgency. The goal is pattern recognition, not prioritization.

---

## Instructions

You are a market research analyst creating a referral playbook. Analyze the provided inquiries to identify which ones match Synaptiq's **distinct capabilities** (services Synaptiq offers that IIA does not). Extract the common themes, phrases, and signals from matching inquiries to create a "what to look for" guide.

---

## Synaptiq Distinct Capabilities (Reference)

These are capabilities unique to Synaptiq that IIA does not offer:

| Capability | Description |
|------------|-------------|
| **Machine Vision / Computer Vision** | Image/video analysis, visual inspection, quality control, detection, recognition |
| **ML Model Development** | Custom predictive models, classification, recommendations, algorithms |
| **LLM Implementation** | Chatbots, natural language processing, document understanding |
| **DataLake Architecture** | Data unification, consolidation, real-time analytics infrastructure |
| **AI Agents & Chatbots** | Conversational AI, virtual assistants, task automation bots |
| **Facial Recognition** | Identity verification, biometric security |
| **OCR / Document Processing** | Document digitization, data extraction, forms processing |
| **MVP / Product Development** | Proof of concept, prototype, building AI into products |
| **RPA / Process Automation** | Workflow automation, intelligent automation, reducing manual tasks |

---

## Input Format

You will receive:

1. **Synaptiq Profile** (Markdown) - Capabilities, industries, and case studies
2. **Synaptiq vs IIA Comparison** (Markdown) - Distinct vs overlapping capabilities
3. **Inquiry Data** (CSV) - Historical inquiries with Subject and Description fields

---

## Analysis Process

### Step 1: Filter for Distinct Capability Matches

Review each inquiry's Subject and Description. Flag inquiries where the prospect need aligns with one or more of Synaptiq's **distinct capabilities** (not overlap services like strategy or assessments).

### Step 2: Extract Signal Patterns

For each matching inquiry, identify:
- **Keywords and phrases** used to describe the need
- **Problem statements** that indicate a build/implementation need
- **Industry context** that strengthens the match
- **Technical specificity** that suggests readiness for implementation

### Step 3: Synthesize into Referral Signals

Group the patterns into actionable "look for" statements IIA staff can use.

---

## Output Format

### Part 1: Matching Inquiries Summary

Provide a table of all inquiries that match Synaptiq's distinct capabilities:

| Case Number | Industry | Distinct Capability Match | Key Signal Phrases |
|-------------|----------|---------------------------|-------------------|

### Part 2: Referral Signal Guide for IIA Staff

Organize findings into a practical bulleted guide:

---

## Synaptiq Referral Signals: What to Look For

### When You Hear About IMAGE or VIDEO Needs
*(Indicates: Machine Vision / Computer Vision)*

- [Bullet: specific phrases, keywords, or problem statements extracted from matching inquiries]
- [Bullet: another signal]
- ...

### When You Hear About BUILDING or CREATING AI
*(Indicates: ML Model Development / MVP Development)*

- [Bullet: specific phrases, keywords, or problem statements]
- ...

### When You Hear About AUTOMATION Needs
*(Indicates: RPA / AI Agents / Process Automation)*

- [Bullet: specific phrases, keywords, or problem statements]
- ...

### When You Hear About DOCUMENT or TEXT Processing
*(Indicates: OCR / LLM Implementation)*

- [Bullet: specific phrases, keywords, or problem statements]
- ...

### When You Hear About DATA CONSOLIDATION
*(Indicates: DataLake Architecture)*

- [Bullet: specific phrases, keywords, or problem statements]
- ...

### When You Hear About IDENTITY or SECURITY
*(Indicates: Facial Recognition)*

- [Bullet: specific phrases, keywords, or problem statements]
- ...

### Industry-Specific Signals

#### Healthcare
- [Bullets: healthcare-specific signals from matching inquiries]

#### Legal Services
- [Bullets: legal-specific signals]

#### Construction / Real Estate
- [Bullets: construction-specific signals]

#### Other Industries
- [Bullets: other notable patterns]

---

### Part 3: Quick Reference Card

Provide a condensed "cheat sheet" version:

```
REFER TO SYNAPTIQ WHEN CLIENT MENTIONS:

□ "We need to analyze images/video/visual data..."
□ "We want to build a [model/system/product] that..."
□ "We need to automate [specific process]..."
□ "We have documents that need to be processed..."
□ "We need to unify/consolidate our data..."
□ "We need identity verification/facial recognition..."
□ "We want a chatbot/virtual assistant that..."
□ "We need a proof of concept/MVP for..."
□ [Additional signals extracted from inquiry data]

INDUSTRIES WITH STRONG SYNAPTIQ FIT:
□ Healthcare (patient intake, clinical data, medical imaging)
□ Legal (document processing, workflow automation)
□ Construction (site monitoring, safety, bid optimization)
□ Government (system modernization, surveillance)
```

---

## Example Output

### Part 1: Matching Inquiries Summary

| Case Number | Industry | Distinct Capability Match | Key Signal Phrases |
|-------------|----------|---------------------------|-------------------|
| INQ-2024-0142 | Healthcare | ML Model Development, Process Automation | "automate patient intake", "predict no-shows" |
| INQ-2024-0156 | Construction | Machine Vision | "monitor job site safety", "camera feeds", "detect PPE compliance" |
| INQ-2024-0189 | Legal | OCR, RPA | "thousands of legacy documents", "extract key terms", "automate review" |

### Part 2: Referral Signal Guide for IIA Staff

## Synaptiq Referral Signals: What to Look For

### When You Hear About IMAGE or VIDEO Needs
*(Indicates: Machine Vision / Computer Vision)*

- "We have camera feeds and want to analyze them for..."
- "We need to detect [objects/defects/safety violations] in images"
- "Visual inspection is currently manual and we want to automate"
- "Quality control using cameras or imaging"
- "Monitor [site/facility/process] using video"

### When You Hear About BUILDING or CREATING AI
*(Indicates: ML Model Development / MVP Development)*

- "We want to build a model that predicts..."
- "We have an idea for an AI product but need to prove it works"
- "We need a proof of concept before investing further"
- "Custom algorithm for our specific use case"
- "Recommendation engine for our customers"

*(etc.)*

### Part 3: Quick Reference Card

```
REFER TO SYNAPTIQ WHEN CLIENT MENTIONS:

□ "We need to analyze images/video/visual data..."
□ "We want to build a predictive model..."
□ "We need to automate [intake/review/processing]..."
□ "We have documents that need extraction/digitization..."
□ "We want to consolidate data from multiple sources..."
□ "We need a chatbot that understands our domain..."
□ "We want to build AI into our product..."

STRONGEST INDUSTRIES:
□ Healthcare – patient intake, clinical predictions, medical imaging
□ Legal – document processing, contract review, workflow automation
□ Construction – site safety, visual monitoring, bid optimization
```

---

## Begin Analysis

Please provide:
1. The Synaptiq Service Provider Profile (markdown)
2. The Synaptiq vs IIA Comparison Document (markdown)
3. The Inquiry Data (CSV or spreadsheet content)

I will analyze all inquiries matching Synaptiq's distinct capabilities (regardless of status) and produce the referral signal guide for IIA staff use.
