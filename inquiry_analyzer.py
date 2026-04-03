#!/usr/bin/env python3
"""IIA Inquiry Matchability Analyzer — assesses how ready member inquiries are
to be matched to the right expert for a 1-hour consultation.

Modes:
  Single — analyze one inquiry from --subject / --description flags
  Batch  — analyze a CSV of inquiries and produce enriched CSV + summary

Outputs (batch mode):
  1. Enriched CSV with matchability scores and follow-up questions
  2. Summary markdown report with score distribution and gap analysis
"""

import argparse
import csv
import hashlib
import json
import logging
import os
import random
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / ".env")

DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_BATCH_SIZE = 10
LOG = logging.getLogger("inquiry_analyzer")

ANALYSIS_COLUMNS = [
    "matchability_score",
    "domain_tags",
    "depth_stage",
    "value_type",
    "missing_info",
    "follow_up_questions",
    "match_ready",
]


# ---------------------------------------------------------------------------
# SQLite cache
# ---------------------------------------------------------------------------

def inquiry_hash(subject: str, description: str) -> str:
    combined = f"{subject.strip()}|{description.strip()}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()[:16]


def init_cache(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analyzed (
            inquiry_hash TEXT PRIMARY KEY,
            result_json  TEXT NOT NULL,
            analyzed_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def get_cached(conn: sqlite3.Connection, subject: str, description: str):
    h = inquiry_hash(subject, description)
    row = conn.execute(
        "SELECT result_json FROM analyzed WHERE inquiry_hash = ?", (h,)
    ).fetchone()
    if row:
        return json.loads(row[0])
    return None


def save_cached(conn: sqlite3.Connection, subject: str, description: str, result: dict):
    h = inquiry_hash(subject, description)
    conn.execute(
        "INSERT OR REPLACE INTO analyzed (inquiry_hash, result_json, analyzed_at) VALUES (?, ?, ?)",
        (h, json.dumps(result), datetime.now(tz=None).isoformat()),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# CSV loading
# ---------------------------------------------------------------------------

def load_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


# ---------------------------------------------------------------------------
# Claude prompt construction
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert at assessing the matchability of IIA (International Institute for Analytics) member inquiries. Members receive a free 1-hour consultation with an expert as part of their paid membership. Your job is to evaluate how ready each inquiry is to be matched to the right expert so that hour is maximally productive.

## Analysis Framework

The matching problem: to make a great match, the matcher needs to answer "Which expert has been where this member is, dealt with what they're dealing with, and can make the most of a single hour together?"

That requires four things from the inquiry:

### 1. Domain Clarity — What expertise is needed?
Can you identify the specific topic area(s) well enough to find the right expert? Multi-topic inquiries are harder — one expert may not cover both "data governance" and "GenAI adoption."

### 2. Depth/Stage — Where are they in their journey?
This is the single biggest matching factor. The stages:
- EXPLORING: Just starting to learn about this area, need landscape/orientation
- PLANNING: Have identified the area, developing a plan or strategy
- EXECUTING: Actively building/implementing, need practitioner guidance
- STUCK: Have something in place but hitting specific challenges
- VALIDATING: Have an approach, want confirmation or refinement from someone experienced

Matching an explorer with a deep practitioner wastes the hour on details they're not ready for. Matching someone stuck with a strategist wastes it on theory they've already moved past.

### 3. "Been There" Context — What makes an expert relatable?
- Industry context (manufacturing CDO vs healthcare CDO have different worlds)
- Org type/size (Fortune 500 vs mid-market need different advice)
- Team context — size, roles, reporting structure
- Contact's role/level (director vs analyst need different things on same topic)

The member doesn't just want correct advice — they want it from someone who understands their constraints.

### 4. What They Want From the Hour — What should the expert prepare?
- Frameworks/methodology — want a structured approach to apply
- Advice — want direct guidance on a specific decision or challenge
- Examples — want to hear how other organizations have approached this
- Peer exchange — want to compare notes with someone in a similar role
- Validation — want feedback/review on their existing approach
- Presentation — want a speaker or facilitator for a team session

If the member wants case studies and the expert shows up with a framework deck, the hour underperforms.

## Important Context
- These are NOT sales opportunities. This is a free membership benefit. The goal is matching the member to the best expert for a productive hour.
- Many descriptions are written by IIA staff in 3rd person, not by the member. Some are forwarded emails. Some are admin notes. Account for this.
- Some inquiries are follow-ups or multi-part series — note this if evident.

## Your Task

For each inquiry, assess ALL of the following:

1. **matchability_score (integer 1-5)**:
   - 5 = Match-ready: clear domain, depth, context, and desired outcome
   - 4 = Minor gap: one piece of context missing but inferable
   - 3 = Moderate gaps: domain is clear but 2+ contextual gaps
   - 2 = Significant gaps: hard to match without follow-up
   - 1 = Unmatchable as-is: too vague, admin note, or no clear ask

2. **domain_tags**: Classify into one or more of (comma-separated):
   analytics_bi, genai_llm_agentic, ml_data_science, leadership_coaching,
   operating_model_org_design, data_governance, cloud_infrastructure,
   ai_ml_strategy, data_strategy_architecture, talent_workforce

3. **depth_stage**: One of: exploring, planning, executing, stuck, validating, unknown

4. **value_type**: One of: frameworks, advice, examples, peer_exchange, validation, presentation, unknown

5. **missing_info**: Which of these gaps are present (comma-separated, or empty string if none):
   depth_stage, industry, org_context, team_context, role_level, consultation_value_type

6. **follow_up_questions**: For inquiries scoring 1-3, generate 1-2 specific questions the IIA staff should ask the member BEFORE matching. Questions must be:
   - Specific to THIS inquiry (not generic intake questions)
   - Quick for the member to answer
   - Framed as making their consultation hour more productive
   If matchability is 4 or 5, return an empty string.

7. **match_ready**: "yes" if matchability_score >= 4, "no" otherwise

## OUTPUT FORMAT

Return ONLY a valid JSON array. No markdown, no explanation, no code fences.
Each element must be an object with exactly these keys:
  "subject", "description_excerpt", "matchability_score", "domain_tags", "depth_stage",
  "value_type", "missing_info", "follow_up_questions", "match_ready"

- subject: echo back the subject as given
- description_excerpt: first 100 characters of the description (for verification)
- matchability_score: integer 1-5
- domain_tags: comma-separated string
- depth_stage: single string from the allowed values
- value_type: single string from the allowed values
- missing_info: comma-separated string of gap names, or empty string
- follow_up_questions: string with the questions, or empty string
- match_ready: "yes" or "no"

Return one object per input inquiry, in the same order as the input."""


def build_user_message(batch: list[dict]) -> str:
    """Serialize a batch of inquiries into a text block for Claude."""
    lines = ["Analyze the following IIA member inquiries. Return JSON array only.\n"]
    for row in batch:
        lines.append(
            f"---\n"
            f"Subject: {row.get('Subject', '')}\n"
            f"Description: {row.get('Description', '')}\n"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# API call with retry
# ---------------------------------------------------------------------------

def call_claude(
    client: anthropic.Anthropic,
    system_prompt: str,
    user_message: str,
    model: str,
    max_retries: int = 5,
) -> list[dict]:
    """Call Claude and parse JSON array response, with exponential backoff."""
    last_exc = None
    for attempt in range(max_retries):
        try:
            LOG.debug("API call attempt %d/%d (%d chars user msg)", attempt + 1, max_retries, len(user_message))
            response = client.messages.create(
                model=model,
                max_tokens=16384,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            text = response.content[0].text.strip()
            # Strip markdown code fences if Claude adds them despite instructions
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3].strip()
            results = json.loads(text)
            if not isinstance(results, list):
                raise ValueError(f"Expected JSON array, got {type(results).__name__}")
            return results
        except anthropic.RateLimitError as e:
            last_exc = e
            retry_after = int(e.response.headers.get("retry-after", "30")) if e.response else 30
            delay = max(retry_after, 2 ** attempt) + random.uniform(0, 2)
            LOG.warning("Rate limited. Retrying in %.1fs (attempt %d/%d)", delay, attempt + 1, max_retries)
            time.sleep(delay)
        except anthropic.APIStatusError as e:
            if e.status_code >= 500:
                last_exc = e
                delay = 2 ** attempt + random.uniform(0, 2)
                LOG.warning("Server error %d. Retrying in %.1fs", e.status_code, delay)
                time.sleep(delay)
            else:
                raise
        except (json.JSONDecodeError, ValueError) as e:
            LOG.error("Failed to parse Claude response: %s", e)
            LOG.debug("Raw response text:\n%s", text[:500])
            raise

    raise last_exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Analysis logic
# ---------------------------------------------------------------------------

def analyze_batch(
    client: anthropic.Anthropic,
    batch: list[dict],
    model: str,
    conn: sqlite3.Connection,
    force_rescore: bool,
) -> list[dict]:
    """Analyze a batch of inquiries, using cache where possible."""
    to_analyze = []
    results_map = {}  # index -> result (preserves order)

    for i, row in enumerate(batch):
        subj = row.get("Subject", "").strip()
        desc = row.get("Description", "").strip()
        if not force_rescore:
            cached = get_cached(conn, subj, desc)
            if cached:
                results_map[i] = cached
                LOG.debug("Cache hit: %s", subj[:60])
                continue
        to_analyze.append((i, row))

    if to_analyze:
        user_msg = build_user_message([row for _, row in to_analyze])
        api_results = call_claude(client, SYSTEM_PROMPT, user_msg, model)

        for j, (orig_idx, row) in enumerate(to_analyze):
            if j < len(api_results):
                result = api_results[j]
                # Normalize keys
                result["subject"] = row.get("Subject", "")
                subj = row.get("Subject", "").strip()
                desc = row.get("Description", "").strip()
                save_cached(conn, subj, desc, result)
                results_map[orig_idx] = result
            else:
                LOG.warning("Claude returned fewer results than expected for: %s", row.get("Subject", "")[:60])

    # Return in original order
    return [results_map[i] for i in sorted(results_map)]


def analyze_single(
    client: anthropic.Anthropic,
    subject: str,
    description: str,
    model: str,
    conn: sqlite3.Connection,
    force_rescore: bool,
) -> dict:
    """Analyze a single inquiry."""
    if not force_rescore:
        cached = get_cached(conn, subject, description)
        if cached:
            LOG.info("Using cached analysis")
            return cached

    row = {"Subject": subject, "Description": description}
    user_msg = build_user_message([row])
    results = call_claude(client, SYSTEM_PROMPT, user_msg, model)
    result = results[0]
    result["subject"] = subject
    save_cached(conn, subject, description, result)
    return result


# ---------------------------------------------------------------------------
# Output: single mode (stdout)
# ---------------------------------------------------------------------------

def print_formatted_result(result: dict, subject: str, description: str):
    """Print a human-readable analysis to stdout."""
    score = result.get("matchability_score", "?")
    ready = result.get("match_ready", "?")
    domains = result.get("domain_tags", "?")
    stage = result.get("depth_stage", "?")
    vtype = result.get("value_type", "?")
    missing = result.get("missing_info", "")
    questions = result.get("follow_up_questions", "")

    print()
    print("=" * 60)
    print("  INQUIRY MATCHABILITY ANALYSIS")
    print("=" * 60)
    print()
    print(f"  Subject:     {subject}")
    desc_display = description[:200] + "..." if len(description) > 200 else description
    print(f"  Description: {desc_display}")
    print()
    print(f"  Matchability Score:  {score}/5  {'MATCH READY' if ready == 'yes' else 'NEEDS FOLLOW-UP'}")
    print(f"  Domain:              {domains}")
    print(f"  Depth/Stage:         {stage}")
    print(f"  Value Type:          {vtype}")
    if missing:
        print(f"  Missing Info:        {missing}")
    else:
        print(f"  Missing Info:        (none)")
    print()

    if questions:
        print("  FOLLOW-UP QUESTIONS:")
        print("  " + "-" * 40)
        for line in questions.strip().split("\n"):
            print(f"  {line}")
        print()
    print("=" * 60)
    print()


# ---------------------------------------------------------------------------
# Output: batch mode (CSV + summary)
# ---------------------------------------------------------------------------

def write_enriched_csv(
    original_rows: list[dict],
    analysis_results: list[dict],
    output_path: Path,
):
    """Write CSV with original columns plus analysis columns, sorted by matchability (worst first)."""
    # Merge original rows with analysis
    merged = []
    for orig, analysis in zip(original_rows, analysis_results):
        row = dict(orig)
        for col in ANALYSIS_COLUMNS:
            row[col] = analysis.get(col, "")
        merged.append(row)

    # Sort by matchability_score ascending (needs-attention first)
    merged.sort(key=lambda r: int(r.get("matchability_score", 0)))

    fieldnames = list(original_rows[0].keys()) + ANALYSIS_COLUMNS
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(merged)

    LOG.info("Wrote enriched CSV: %s", output_path)


def write_summary_md(
    analysis_results: list[dict],
    output_path: Path,
    total_rows: int,
):
    """Write a summary markdown report."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    scores = [int(r.get("matchability_score", 0)) for r in analysis_results]
    match_ready = sum(1 for r in analysis_results if r.get("match_ready") == "yes")
    needs_followup = total_rows - match_ready
    avg_score = sum(scores) / len(scores) if scores else 0

    # Score distribution
    score_dist = {s: scores.count(s) for s in range(1, 6)}

    # Gap frequency
    from collections import Counter
    all_gaps = []
    for r in analysis_results:
        gaps = r.get("missing_info", "")
        if gaps:
            all_gaps.extend(g.strip() for g in gaps.split(",") if g.strip())
    gap_counts = Counter(all_gaps).most_common()

    # Domain frequency
    all_domains = []
    for r in analysis_results:
        tags = r.get("domain_tags", "")
        if tags:
            all_domains.extend(d.strip() for d in tags.split(",") if d.strip())
    domain_counts = Counter(all_domains).most_common()

    # Stage frequency
    stage_counts = Counter(r.get("depth_stage", "unknown") for r in analysis_results).most_common()

    # Value type frequency
    value_counts = Counter(r.get("value_type", "unknown") for r in analysis_results).most_common()

    lines = [
        f"# IIA Inquiry Matchability Analysis\n",
        f"*Generated: {ts}*\n",
        f"**Total inquiries analyzed:** {total_rows}\n",
        f"## Overview\n",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Match-ready (score 4-5) | {match_ready} ({match_ready * 100 // total_rows}%) |",
        f"| Needs follow-up (score 1-3) | {needs_followup} ({needs_followup * 100 // total_rows}%) |",
        f"| Average matchability score | {avg_score:.1f} |",
        f"",
        f"## Score Distribution\n",
        f"| Score | Description | Count | % |",
        f"|-------|-------------|-------|---|",
    ]
    score_labels = {
        5: "Match-ready",
        4: "Minor gap",
        3: "Moderate gaps",
        2: "Significant gaps",
        1: "Unmatchable as-is",
    }
    for s in range(5, 0, -1):
        c = score_dist.get(s, 0)
        pct = c * 100 // total_rows if total_rows else 0
        lines.append(f"| {s} | {score_labels[s]} | {c} | {pct}% |")

    lines += [
        f"",
        f"## Most Common Information Gaps\n",
        f"| Gap | Count | % of inquiries |",
        f"|-----|-------|----------------|",
    ]
    gap_labels = {
        "depth_stage": "Depth/maturity stage",
        "industry": "Industry",
        "org_context": "Org type/size",
        "team_context": "Team context",
        "role_level": "Contact's role/level",
        "consultation_value_type": "Consultation value type",
    }
    for gap, count in gap_counts:
        label = gap_labels.get(gap, gap)
        pct = count * 100 // total_rows if total_rows else 0
        lines.append(f"| {label} | {count} | {pct}% |")

    lines += [
        f"",
        f"## Domain Distribution\n",
        f"| Domain | Count | % |",
        f"|--------|-------|---|",
    ]
    for domain, count in domain_counts:
        pct = count * 100 // total_rows if total_rows else 0
        lines.append(f"| {domain} | {count} | {pct}% |")

    lines += [
        f"",
        f"## Depth/Stage Distribution\n",
        f"| Stage | Count | % |",
        f"|-------|-------|---|",
    ]
    for stage, count in stage_counts:
        pct = count * 100 // total_rows if total_rows else 0
        lines.append(f"| {stage} | {count} | {pct}% |")

    lines += [
        f"",
        f"## Consultation Value Type Distribution\n",
        f"| Value Type | Count | % |",
        f"|------------|-------|---|",
    ]
    for vt, count in value_counts:
        pct = count * 100 // total_rows if total_rows else 0
        lines.append(f"| {vt} | {count} | {pct}% |")

    # Inquiries needing follow-up (score <= 2)
    critical = [r for r in analysis_results if int(r.get("matchability_score", 0)) <= 2]
    if critical:
        lines += [
            f"",
            f"## Critical Follow-ups Needed (Score 1-2)\n",
        ]
        for r in sorted(critical, key=lambda x: int(x.get("matchability_score", 0))):
            subj = r.get("subject", "N/A")[:80]
            score = r.get("matchability_score", "?")
            qs = r.get("follow_up_questions", "").strip()
            lines.append(f"### [{score}/5] {subj}\n")
            if qs:
                lines.append(f"{qs}\n")
            else:
                lines.append(f"*No follow-up questions generated.*\n")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    LOG.info("Wrote summary: %s", output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Assess IIA member inquiry matchability for expert matching.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single inquiry
  %(prog)s --subject "AI Readiness Support" --description "We are looking for..."

  # Batch CSV
  %(prog)s -i inquiry_export.csv

  # Batch with custom options
  %(prog)s -i inquiry_export.csv -b 5 -o output/matchability -v
        """,
    )
    p.add_argument(
        "-i", "--input",
        help="Input CSV path (batch mode). Must have Subject and Description columns.",
    )
    p.add_argument(
        "--subject",
        help="Single inquiry subject (optional, used with --description)",
    )
    p.add_argument(
        "--description",
        help="Single inquiry description (single mode). Can be used alone or with --subject.",
    )
    p.add_argument(
        "-o", "--output-dir",
        default=str(SCRIPT_DIR / "output"),
        help="Output directory for batch mode (default: output/)",
    )
    p.add_argument(
        "-b", "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Batch size for CSV processing (default: {DEFAULT_BATCH_SIZE})",
    )
    p.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL,
        help=f"Claude model (default: {DEFAULT_MODEL})",
    )
    p.add_argument(
        "--force-rescore",
        action="store_true",
        help="Ignore cache, rescore everything",
    )
    p.add_argument(
        "--cache-file",
        default=str(SCRIPT_DIR / "inquiry_analyzer_cache.db"),
        help="SQLite cache path (default: inquiry_analyzer_cache.db)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without API calls",
    )
    p.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose logging",
    )
    return p.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    # Validate args — need either --input or --description (or both --subject and --description)
    if not args.input and not args.description:
        LOG.error("Either --input (batch mode) or --description (single mode) is required.")
        sys.exit(1)

    # Init cache
    conn = init_cache(args.cache_file)

    # --- Single mode ---
    if args.description and not args.input:
        subject = args.subject or ""
        if args.dry_run:
            print("\n[DRY RUN] Would analyze:")
            if subject:
                print(f"  Subject: {subject}")
            print(f"  Description: {args.description[:200]}...")
            return

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            LOG.error("ANTHROPIC_API_KEY not set. Export it or add to .env file.")
            sys.exit(1)
        client = anthropic.Anthropic(api_key=api_key)

        result = analyze_single(
            client, subject, args.description,
            args.model, conn, args.force_rescore,
        )
        print_formatted_result(result, subject, args.description)
        return

    # --- Batch mode ---
    input_path = Path(args.input)
    if not input_path.is_file():
        LOG.error("Input file not found: %s", input_path)
        sys.exit(1)

    rows = load_csv(str(input_path))
    LOG.info("Loaded %d rows from %s", len(rows), input_path.name)

    # Filter out rows with no description
    valid_rows = [r for r in rows if (r.get("Description") or "").strip()]
    skipped = len(rows) - len(valid_rows)
    if skipped:
        LOG.info("Skipping %d rows with empty descriptions", skipped)

    # Batch count
    num_batches = (len(valid_rows) + args.batch_size - 1) // args.batch_size
    LOG.info("Processing %d inquiries in %d batches of %d", len(valid_rows), num_batches, args.batch_size)

    if args.dry_run:
        print(f"\n[DRY RUN] Would analyze {len(valid_rows)} inquiries in {num_batches} batches.")
        print(f"  Input: {input_path}")
        print(f"  Model: {args.model}")
        print(f"  Batch size: {args.batch_size}")
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        LOG.error("ANTHROPIC_API_KEY not set. Export it or add to .env file.")
        sys.exit(1)
    client = anthropic.Anthropic(api_key=api_key)

    # Process batches
    all_results = []
    for batch_idx in range(num_batches):
        start = batch_idx * args.batch_size
        end = min(start + args.batch_size, len(valid_rows))
        batch = valid_rows[start:end]
        LOG.info("Batch %d/%d (%d inquiries)...", batch_idx + 1, num_batches, len(batch))

        results = analyze_batch(client, batch, args.model, conn, args.force_rescore)
        all_results.extend(results)
        LOG.info("  Batch %d done. %d results so far.", batch_idx + 1, len(all_results))

    # Write outputs
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_path = out_dir / f"inquiry_matchability_{ts}.csv"
    write_enriched_csv(valid_rows, all_results, csv_path)

    summary_path = out_dir / f"inquiry_matchability_{ts}_summary.md"
    write_summary_md(all_results, summary_path, len(valid_rows))

    # Final summary
    match_ready = sum(1 for r in all_results if r.get("match_ready") == "yes")
    LOG.info("--- Done ---")
    LOG.info("Analyzed: %d inquiries", len(all_results))
    LOG.info("Match-ready: %d (%d%%)", match_ready, match_ready * 100 // len(all_results) if all_results else 0)
    LOG.info("Needs follow-up: %d", len(all_results) - match_ready)
    LOG.info("Outputs:")
    LOG.info("  1. CSV:     %s", csv_path.name)
    LOG.info("  2. Summary: %s", summary_path.name)


if __name__ == "__main__":
    main()
