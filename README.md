# Synaptiq Inquiry Analysis CLI

Batch-scores IIA prospect inquiries for Synaptiq fit using the Claude API. Replaces the manual copy-paste-into-LLM workflow that broke at 523 rows.

## What It Does

1. **Loads** the input CSV and three reference docs (scoring prompt, company profile, IIA comparison)
2. **Partitions** rows into active, closed, and trivial buckets
3. **Pre-scores** trivial rows locally (cancelled/empty description) — no API call
4. **Batch-scores** active rows via Claude with full Fit/Urgency methodology
5. **Batch-scores** closed rows with Urgency fixed at 1 (lighter pass, larger batches)
6. **Caches** results in SQLite keyed by Case Number + description hash
7. **Outputs** a prioritized CSV and a summary markdown with Top Opportunities, Quick Wins, Distinct Capability Matches, and IIA Referral Candidates

### Cost Optimization

| Partition | Rows | Batch Size | API Calls | Notes |
|-----------|------|------------|-----------|-------|
| Trivial (cancelled/empty) | ~23 | — | 0 | Pre-scored locally |
| Active (Closed=0) | ~66 | 25 | ~3 | Full Fit + Urgency scoring |
| Closed (Closed=1) | ~434 | 50 | ~9 | Urgency fixed at 1 |
| **Total** | **523** | — | **~12** | ~$2 full run |

Use `--skip-closed` to score only active rows (~$0.33, ~3 API calls).

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

### Required Files

These must be in the same directory as `analyze.py`:

- `prospect-analysis-prompt-weighted.md` — scoring methodology (system prompt)
- `synaptiq-company-profile.md` — Synaptiq capabilities, industries, case studies
- `synaptiq-iia-comparison.md` — Synaptiq vs IIA distinct/overlap capabilities

## Usage

```bash
# Dry run — validates CSV parsing and partitioning, no API calls
python analyze.py --dry-run

# Score active rows only (fast, cheap)
python analyze.py --skip-closed

# Full run — all 523 rows
python analyze.py

# Custom input file and small batches
python analyze.py -i ~/Downloads/inquiry_input.csv --batch-size 5

# Force rescore everything (ignore cache)
python analyze.py --force-rescore

# Verbose logging
python analyze.py -v
```

### All Options

```
python analyze.py [OPTIONS]
  --input, -i           Input CSV (default: inquiry_input.csv)
  --output-dir, -o      Output directory (default: output/)
  --batch-size, -b      Active row batch size (default: 25)
  --closed-batch-size   Closed row batch size (default: 50)
  --model, -m           Claude model (default: claude-sonnet-4-20250514)
  --skip-closed         Skip LLM scoring for closed rows
  --force-rescore       Ignore cache, rescore everything
  --cache-file          SQLite cache path (default: cache.db)
  --dry-run             Preview without API calls
  --verbose, -v         Verbose logging
```

## Output

Each run creates two files in `output/`:

- **`inquiry_analysis_YYYYMMDD_HHMMSS.csv`** — All rows scored, sorted by Priority descending
- **`inquiry_analysis_YYYYMMDD_HHMMSS_summary.md`** — Auto-generated report sections:
  - Top Opportunities (Priority >= 16)
  - Quick Wins (Urgency = 5, Fit >= 3)
  - Distinct Capability Matches (Fit >= 4) with capability frequency
  - IIA Referral Candidates (Fit <= 2)

### CSV Columns

| Column | Description |
|--------|-------------|
| Case Number | From input CSV |
| Status | From input CSV |
| Age (Days) | From input CSV |
| Description | From input CSV |
| Summary | 1-2 sentence AI-generated summary |
| Distinct Capabilities Matched | Synaptiq capabilities that apply |
| Fit | 1-5, weighted toward Synaptiq distinct capabilities |
| Urgency | 1-5, based on status and age |
| Priority | Fit x Urgency (max 25) |

## Caching

Results are cached in `cache.db` (SQLite) keyed by Case Number + SHA-256 hash of the Description field. On re-run:

- **Same description** → cached result used (no API call)
- **Changed description** → re-scored via API
- **`--force-rescore`** → ignores cache entirely

## Scoring Methodology

See `prospect-analysis-prompt-weighted.md` for the full rubric. In summary:

- **Fit (1-5)**: Weighted toward Synaptiq's *distinct* capabilities (Machine Vision, ML Model Dev, LLM Implementation, DataLake, AI Agents, OCR, RPA, etc.) vs overlap capabilities shared with IIA (strategy, assessments, governance)
- **Urgency (1-5)**: Based on inquiry status (New/Scoping/Pending Expert = 5, Closed = 1) adjusted by age
- **Priority**: Fit x Urgency, max 25
