# Synaptiq IIA Inquiry Analysis Tools

Four CLI tools for processing IIA prospect inquiries: assessing inquiry matchability for expert matching, batch scoring inquiries at scale, generating tailored consultant engagement packages, and creating base bio documents from raw content.

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Tool 1: Inquiry Matchability Analyzer (`inquiry_analyzer.py`)

Assesses how ready IIA member inquiries are to be matched to the right expert for a free 1-hour consultation. Identifies information gaps and generates specific follow-up questions to ask before matching.

### What It Does

For each inquiry, uses Claude to:

1. **Score matchability** (1-5) — how ready the inquiry is to be matched
2. **Classify** — domain cluster, depth/stage, and consultation value type
3. **Identify gaps** — which of 6 key information dimensions are missing
4. **Generate follow-up questions** — specific to the inquiry, for low-scoring entries

### Modes

**Single mode** — analyze one inquiry and print results to terminal:

```bash
# Description only
python inquiry_analyzer.py --description "We are exploring how to build a RAG pipeline..."

# With subject
python inquiry_analyzer.py --subject "RAG Support" --description "We are exploring..."
```

**Batch mode** — analyze a CSV and produce enriched outputs:

```bash
python inquiry_analyzer.py -i inquiry_export.csv
python inquiry_analyzer.py -i inquiry_export.csv -b 20 -o output/matchability -v
```

### Analysis Dimensions

| Dimension | Values |
|-----------|--------|
| **Matchability Score** | 1 (unmatchable) to 5 (match-ready) |
| **Domain Tags** | `analytics_bi`, `genai_llm_agentic`, `ml_data_science`, `leadership_coaching`, `operating_model_org_design`, `data_governance`, `cloud_infrastructure`, `ai_ml_strategy`, `data_strategy_architecture`, `talent_workforce` |
| **Depth/Stage** | `exploring`, `planning`, `executing`, `stuck`, `validating`, `unknown` |
| **Value Type** | `frameworks`, `advice`, `examples`, `peer_exchange`, `validation`, `presentation`, `unknown` |
| **Missing Info** | `depth_stage`, `industry`, `org_context`, `team_context`, `role_level`, `consultation_value_type` |

### All Options

```
python inquiry_analyzer.py [OPTIONS]
  -i, --input           Input CSV path (batch mode)
  --subject             Single inquiry subject (optional)
  --description         Single inquiry description (single mode)
  -o, --output-dir      Output directory (default: output/)
  -b, --batch-size      Batch size for CSV processing (default: 10)
  -m, --model           Claude model (default: claude-sonnet-4-20250514)
  --force-rescore       Ignore cache, rescore everything
  --cache-file          SQLite cache path (default: inquiry_analyzer_cache.db)
  --dry-run             Preview without API calls
  -v, --verbose         Verbose logging
```

### Outputs (Batch Mode)

| # | File | Description |
|---|------|-------------|
| 1 | `inquiry_matchability_<ts>.csv` | Enriched CSV with all original columns plus analysis columns, sorted by matchability score (worst first) |
| 2 | `inquiry_matchability_<ts>_summary.md` | Summary report — score distribution, gap frequency, domain breakdown, and critical follow-ups needed |

### Caching

Results are cached in `inquiry_analyzer_cache.db` (SQLite) keyed by SHA-256 hash of subject + description. On re-run, identical inquiries are served from cache without an API call. Use `--force-rescore` to bypass.

---

## Tool 2: Bio Tailoring CLI (`tailor_bio.py`)

Researches a prospect company via web search, tailors a consultant bio, and generates a full pre-engagement package — all from two inputs.

### What It Does

1. **Researches** the prospect company using Claude with web search (culture, structure, AI posture, industry context)
2. **Generates** a tailored consultant bio reframed for the prospect's inquiry and values
3. **Produces** 5 outputs as a complete engagement prep package

### Inputs

| Argument | Required | Description |
|----------|----------|-------------|
| `--company`, `-c` | Yes | Name of the prospect company |
| `--inquiry`, `-q` | Yes | Inquiry description text, or path to a `.txt`/`.md` file |
| `--bio`, `-b` | No | Path to original bio `.docx` (default: `2026 Sklarew Bio - IIA.docx`) |
| `--company-profile`, `-p` | No | Path to Synaptiq profile `.md` (default: `synaptiq-company-profile.md`) |
| `--company-research`, `-r` | No | Path to existing company research `.md` (skips web research step) |
| `--output-dir`, `-o` | No | Output directory (default: `output/<company-slug>/`) |
| `--model`, `-m` | No | Claude model for content generation (default: `claude-sonnet-4-20250514`) |
| `--research-model` | No | Claude model for web research (default: `claude-sonnet-4-20250514`) |
| `--verbose`, `-v` | No | Verbose logging |

### Outputs

Each run creates 5 files in the output directory:

| # | File | Format | Description |
|---|------|--------|-------------|
| 1 | `<Consultant> Bio - <Company>.docx` | `.docx` | Tailored bio with headshot and logo from original |
| 2 | `tailoring-specifics-<slug>_<ts>.md` | `.md` | What was tailored and why — emphasis shifts, language alignment, de-emphasized elements |
| 3 | `company-profile-<slug>_<ts>.md` | `.md` | Company research profile — overview, culture, workforce, AI posture, industry context |
| 4 | `discovery-questions-<slug>_<ts>.md` | `.md` | 3-5 recommended questions for the initial consult with rationale |
| 5 | `prep-brief-<slug>_<ts>.md` | `.md` | Internal consultant prep brief — TL;DR, talking points, landmines, meeting flow, success criteria |

### Research Caching

Company research is automatically cached. On subsequent runs targeting the same output directory, the tool detects existing `company-profile-*.md` files and reuses the most recent one instead of running a new web search. You can also provide a specific research file:

```bash
python tailor_bio.py -c "Acme Corp" -q "..." -r output/acme/company-profile-acme_20260401_120000.md
```

### Usage

```bash
# Basic usage — just company name and inquiry text
python tailor_bio.py -c "Acme Corp" -q "Seeking AI workforce planning guidance..."

# Use a different consultant's bio
python tailor_bio.py -c "Acme Corp" -q "..." -b "2026 Oates Bio - IIA.docx"

# Inquiry from a file
python tailor_bio.py -c "Acme Corp" -q inquiry.txt

# Custom output directory
python tailor_bio.py -c "Acme Corp" -q "..." -o output/custom-folder

# Reuse existing company research (skip web search)
python tailor_bio.py -c "Acme Corp" -q "..." -r path/to/company-profile.md

# Verbose logging
python tailor_bio.py -c "Acme Corp" -q "..." -v
```

---

## Tool 3: Base Bio Generator (`generate_tailored_bio.py`)

Standalone script that builds a formatted `.docx` bio document from scratch using `python-docx`. Unlike `tailor_bio.py` which tailors an existing bio for a specific prospect, this script generates a complete bio document with custom layout, headshot, logo, and structured content sections.

### What It Does

Builds a polished Word document with:

1. **Company logo** (centered header)
2. **Headshot + name/title block** (side-by-side table layout)
3. **Overview** section (succinct bio paragraph)
4. **Background & Expertise** (multi-paragraph extended bio)
5. **Relevant Experience** (bulleted highlights with bold titles)

### Usage

This is a template script — edit the content variables directly in the file for each new bio, then run:

```bash
python generate_tailored_bio.py
```

Images are expected at `/tmp/bio_images/word/media/` (extracted from a source `.docx` via zipfile). The output path is configured at the bottom of the script.

---

## Tool 4: Batch Inquiry Scoring CLI (`analyze.py`)

Batch-scores IIA prospect inquiries for Synaptiq fit using the Claude API. Replaces the manual copy-paste-into-LLM workflow that broke at 523 rows.

### What It Does

1. **Loads** the input CSV and three reference docs (scoring prompt, company profile, IIA comparison)
2. **Partitions** rows into active, closed, and trivial buckets
3. **Pre-scores** trivial rows locally (cancelled/empty description) — no API call
4. **Batch-scores** active rows via Claude with full Fit/Urgency methodology
5. **Batch-scores** closed rows with Urgency fixed at 1 (lighter pass, larger batches)
6. **Caches** results in SQLite keyed by Case Number + description hash
7. **Outputs** a prioritized CSV and a summary markdown

### Required Files

These must be in the same directory as `analyze.py`:

- `prospect-analysis-prompt-weighted.md` — scoring methodology (system prompt)
- `synaptiq-company-profile.md` — Synaptiq capabilities, industries, case studies
- `synaptiq-iia-comparison.md` — Synaptiq vs IIA distinct/overlap capabilities

### Usage

```bash
# Dry run — validates CSV parsing and partitioning, no API calls
python analyze.py --dry-run

# Score active rows only (fast, cheap)
python analyze.py --skip-closed

# Full run — all rows
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

### Output

Each run creates two files in `output/`:

- **`inquiry_analysis_<ts>.csv`** — All rows scored, sorted by Priority descending
- **`inquiry_analysis_<ts>_summary.md`** — Top Opportunities, Quick Wins, Distinct Capability Matches, IIA Referral Candidates

### Caching

Results are cached in `cache.db` (SQLite) keyed by Case Number + SHA-256 hash of the Description field. On re-run:

- **Same description** → cached result used (no API call)
- **Changed description** → re-scored via API
- **`--force-rescore`** → ignores cache entirely

### Scoring Methodology

See `prospect-analysis-prompt-weighted.md` for the full rubric. In summary:

- **Fit (1-5)**: Weighted toward Synaptiq's *distinct* capabilities (Machine Vision, ML Model Dev, LLM Implementation, DataLake, AI Agents, OCR, RPA, etc.)
- **Urgency (1-5)**: Based on inquiry status and age
- **Priority**: Fit × Urgency, max 25
