# Inquiry Intake Analysis & Recommendations

*Analysis of 523 IIA member inquiries over 14 months*

---

## The Matching Problem

To make a great match, the person doing the matching needs to answer one question: **"Which expert has been where this member is, dealt with what they're dealing with, and can make the most of a single hour together?"**

That requires four things from the inquiry:

### 1. Domain Clarity — *What expertise is needed?* (Mostly OK)

The topic is usually identifiable from subject + description. **76%** of subjects are clear enough, and the rich descriptions (62% are 500+ chars) fill in the rest. **This is not the primary gap.** The 10% that are multi-topic are trickier — one expert may not cover both "data governance" and "GenAI adoption."

### 2. Depth/Stage — *Where are they in their journey?* (Major Gap)

This is **the single biggest matching problem.** 48% of inquiries give no signal about whether the member is exploring, executing, stuck, or validating. This matters enormously:

- An **explorer** needs someone who can lay out the landscape and help them prioritize
- Someone **actively executing** needs a practitioner who's done the specific thing
- Someone **stuck** needs a troubleshooter who's seen that failure mode
- Someone **seeking validation** needs a senior peer who can say "yes, you're on the right track"

Matching an explorer with a deep practitioner wastes the hour on details they're not ready for. Matching someone stuck with a strategist wastes it on theory they've already moved past.

### 3. "Been There" Context — *What makes an expert relatable?* (Significant Gap)

- **Only 12%** mention their industry — but a manufacturing CDO and a healthcare CDO have very different worlds
- **Only 14%** mention org type/size — advice for a Fortune 500 vs. a mid-market company is fundamentally different
- **35%** give team context, **35%** give the contact's role/level
- This matters because the member doesn't just want *correct* advice — they want it from someone who **understands their constraints** (regulatory, cultural, organizational)

### 4. What They Want From the Hour — *What should the expert prepare?* (Moderate Gap)

- 49% want frameworks/methodology
- 47% want direct advice
- 34% want examples from other organizations
- 18% want a peer exchange
- 17% want validation/review of their work
- **20% give no signal at all**

This is critical for **expert prep**. If the member wants case studies and the expert shows up with a framework deck, the hour underperforms.

### Other Notable Patterns

- **Authorship is fragmented**: Only 6% are written by the member themselves. 35% are 3rd-person summaries by IIA staff, 9% are forwarded emails. The rest are unclear. This means the intake is already an interpretation layer — signal is being lost.
- **46 inquiries are multi-part series** (numbered "1.", "2.", "3." for the same member) — suggesting the initial intake doesn't capture the full scope, so topics get split across multiple consults.
- **The gold-standard inquiries** (easy to match) all share: clear current state, specific challenge, stated desired outcome, team context, and an explicit ask. These represent maybe 10-15% of the data.

---

## Data Summary

| Metric | Value |
|--------|-------|
| Total inquiries analyzed | 523 |
| With descriptions | 513 |
| Rich descriptions (500+ chars) | 318 (62%) |
| Medium descriptions (150-500 chars) | 153 (30%) |
| Thin descriptions (< 150 chars) | 37 (7%) |
| Admin/placeholder (not real inquiries) | 5 (1%) |
| Average description length | 681 chars |
| Contains explicit questions | 290 (56%) |

### What's Systematically Missing

| Information Gap | % Missing | Matching Impact |
|---|---|---|
| Depth/maturity stage | 48% | Can't distinguish explorers from executors — wrong expert type |
| Industry | 88% | Can't match to someone who understands their constraints |
| Org type/size | 86% | Fortune 500 vs. mid-market need different experts |
| Current state ("where we are today") | 74% | Without this, the expert walks in blind |
| Team context (size/roles) | 65% | A solo analyst vs. 30-person org need different guidance |
| Contact's role/level | 65% | Directors and analysts need different things on the same topic |
| Consultation value type | 20% | Expert doesn't know whether to bring case studies or frameworks |

### Inquiry Depth Distribution

| Member's Stage | Count | % |
|---|---|---|
| Exploring/learning | 97 | 18% |
| Actively executing | 92 | 17% |
| Stuck/facing challenges | 149 | 29% |
| Seeking validation/review | 56 | 10% |
| No depth signal | 247 | 48% |

*Note: Some inquiries show signals for multiple stages; percentages do not sum to 100%.*

### Consultation Value Type Distribution

| What They Want | Count | % |
|---|---|---|
| Frameworks/methodology | 252 | 49% |
| Direct advice/guidance | 243 | 47% |
| Examples/benchmarks from others | 176 | 34% |
| Peer exchange | 93 | 18% |
| Review/validation of their work | 88 | 17% |
| Speaker/presentation | 50 | 9% |
| No clear value type | 105 | 20% |

### Domain Clusters

| Domain | Count | % |
|---|---|---|
| Analytics/BI | 197 | 38% |
| GenAI/LLM/Agentic | 130 | 25% |
| ML/Data Science Technical | 125 | 24% |
| Leadership/Coaching | 123 | 23% |
| Operating Model/Org Design | 63 | 12% |
| Data Governance | 56 | 10% |
| Cloud/Infrastructure | 50 | 9% |
| AI/ML Strategy | 48 | 9% |
| Data Strategy/Architecture | 37 | 7% |
| Talent/Workforce | 37 | 7% |

---

## Recommended Intake Questions

These are designed to be **quick for the member** (they're getting a free benefit, not filling out a form) while giving the matcher what they need. Framed as making their hour more productive, not as friction.

### Must-Have (3 questions that transform matching quality)

**1. "Where are you on this topic today?"** (structured)

- Just starting to explore this area
- Have a plan but haven't started executing
- Actively building/implementing
- Have something in place but it's not working well
- Looking to optimize or scale what's working

*Why: Fixes the 48% depth gap. This is the single highest-leverage question for matching.*

**2. "What would make this hour most valuable for you?"** (structured, multi-select)

- Hear how other organizations have approached this
- Get expert advice on a specific decision or challenge
- Validate or get feedback on an approach I'm already taking
- Learn a framework or methodology I can apply
- Connect with a peer who's dealt with something similar

*Why: Tells the expert what to prepare. Prevents the mismatch where a member wants peer stories and gets a lecture, or wants a framework and gets anecdotes.*

**3. "Briefly describe your specific situation — what are you working with and what's the challenge?"** (open text, 2-3 sentences)

> Example prompt: *"e.g., 'We're a 5-person analytics team in a manufacturing company. We just adopted Databricks but are struggling with getting business units to use our dashboards.'"*

*Why: The current descriptions are often written by IIA staff and lose the member's own framing. A short, member-authored statement captures industry, team size, tools, and the actual pain in natural language.*

### Nice-to-Have (improve matching further, but could be optional)

**4. "What's your role?"** (structured)

- Individual contributor / Analyst
- Team lead / Manager
- Director / Sr. Director
- VP / SVP / C-level

*Why: A director asking about "operating models" needs a different expert than an analyst asking the same thing.*

**5. "What industry are you in?"** (structured dropdown)

*Why: Only 12% mention it currently. Industry context determines which experts are relatable.*

**6. "Do you have specific questions you'd like to cover?"** (optional open text)

*Why: 56% already embed questions in their descriptions — formalizing this ensures the expert can prepare pointed answers rather than a generic overview.*

---

## Impact on Paid Conversion

These questions indirectly increase the likelihood a member asks to continue with paid work — not by qualifying them, but by ensuring the free hour is genuinely excellent. A well-matched expert who shows up prepared and speaks to the member's exact situation is the best sales tool there is. The current data suggests many hours are probably underperforming simply because the expert didn't know enough to prepare properly.
