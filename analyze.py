#!/usr/bin/env python3
"""Synaptiq Inquiry Analysis CLI — batch-scores prospect inquiries via Claude API."""

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

load_dotenv()

SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_BATCH_SIZE = 25
DEFAULT_CLOSED_BATCH_SIZE = 50

LOG = logging.getLogger("analyze")

# ---------------------------------------------------------------------------
# Reference docs
# ---------------------------------------------------------------------------

def load_reference_docs() -> dict[str, str]:
    """Load the three reference markdown files from the script directory."""
    files = {
        "scoring_prompt": SCRIPT_DIR / "prospect-analysis-prompt-weighted.md",
        "company_profile": SCRIPT_DIR / "synaptiq-company-profile.md",
        "iia_comparison": SCRIPT_DIR / "synaptiq-iia-comparison.md",
    }
    docs = {}
    for key, path in files.items():
        if not path.exists():
            LOG.error("Missing reference file: %s", path)
            sys.exit(1)
        docs[key] = path.read_text(encoding="utf-8")
    return docs


# ---------------------------------------------------------------------------
# CSV loading & partitioning
# ---------------------------------------------------------------------------

def load_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


def partition_rows(rows: list[dict]) -> dict[str, list[dict]]:
    """Split rows into active, closed, and trivial buckets."""
    active, closed, trivial = [], [], []
    for row in rows:
        desc = (row.get("Description") or "").strip()
        status = (row.get("Status") or "").strip()
        is_closed = str(row.get("Closed", "0")).strip() == "1"

        if not desc or status.lower() == "cancelled":
            trivial.append(row)
        elif is_closed:
            closed.append(row)
        else:
            active.append(row)
    return {"active": active, "closed": closed, "trivial": trivial}


# ---------------------------------------------------------------------------
# SQLite cache
# ---------------------------------------------------------------------------

def init_cache(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scored (
            case_number TEXT PRIMARY KEY,
            desc_hash   TEXT NOT NULL,
            result_json TEXT NOT NULL,
            scored_at   TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def desc_hash(description: str) -> str:
    return hashlib.sha256(description.encode("utf-8")).hexdigest()[:16]


def get_cached(conn: sqlite3.Connection, case_number: str, description: str):
    row = conn.execute(
        "SELECT desc_hash, result_json FROM scored WHERE case_number = ?",
        (case_number,),
    ).fetchone()
    if row and row[0] == desc_hash(description):
        return json.loads(row[1])
    return None


def save_cached(conn: sqlite3.Connection, case_number: str, description: str, result: dict):
    conn.execute(
        "INSERT OR REPLACE INTO scored (case_number, desc_hash, result_json, scored_at) VALUES (?, ?, ?, ?)",
        (case_number, desc_hash(description), json.dumps(result), datetime.utcnow().isoformat()),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Pre-score trivial rows locally (no API call)
# ---------------------------------------------------------------------------

def prescore_trivial(row: dict) -> dict:
    status = (row.get("Status") or "").strip()
    desc = (row.get("Description") or "").strip()
    if status.lower() == "cancelled":
        summary = "Inquiry was cancelled."
    else:
        summary = "No description provided."
    return {
        "Case Number": row["Case Number"],
        "Status": status,
        "Age (Days)": row.get("Age (Days)", ""),
        "Description": desc,
        "Summary": summary,
        "Distinct Capabilities Matched": "N/A",
        "Fit": 1,
        "Urgency": 1,
        "Priority": 1,
    }


# ---------------------------------------------------------------------------
# Build system prompt for Claude
# ---------------------------------------------------------------------------

def build_system_prompt(docs: dict[str, str], is_closed_batch: bool = False) -> str:
    parts = [
        docs["scoring_prompt"],
        "\n\n---\n\n## Service Provider Profile\n\n",
        docs["company_profile"],
        "\n\n---\n\n## Comparison Document\n\n",
        docs["iia_comparison"],
        "\n\n---\n\n## IMPORTANT OUTPUT INSTRUCTIONS\n\n",
        "You MUST return ONLY a valid JSON array. No markdown, no explanation, no code fences.\n",
        "Each element must be an object with exactly these keys:\n",
        '  "Case Number", "Status", "Age (Days)", "Description", "Summary",\n',
        '  "Distinct Capabilities Matched", "Fit", "Urgency", "Priority"\n',
        "Fit and Urgency must be integers 1-5. Priority = Fit * Urgency.\n",
        "Return one object per input row, in the same order as the input.\n",
    ]
    if is_closed_batch:
        parts.append(
            "\nThese rows are CLOSED inquiries. Set Urgency = 1 for all of them. "
            "Still score Fit (1-5) based on capability alignment.\n"
        )
    return "".join(parts)


def build_user_message(batch: list[dict]) -> str:
    """Serialize a batch of CSV rows into a text block for Claude."""
    lines = ["Score the following inquiries. Return JSON array only.\n"]
    for row in batch:
        lines.append(
            f"---\nCase Number: {row['Case Number']}\n"
            f"Subject: {row.get('Subject', '')}\n"
            f"Description: {row.get('Description', '')}\n"
            f"Status: {row.get('Status', '')}\n"
            f"Type: {row.get('Type', '')}\n"
            f"Date/Time Opened: {row.get('Date/Time Opened', '')}\n"
            f"Age (Days): {row.get('Age (Days)', '')}\n"
            f"Closed: {row.get('Closed', '')}\n"
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
                max_tokens=8192,
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
# Batch scoring
# ---------------------------------------------------------------------------

def score_batch(
    client: anthropic.Anthropic,
    batch: list[dict],
    docs: dict[str, str],
    model: str,
    is_closed: bool,
    conn: sqlite3.Connection,
    force_rescore: bool,
) -> list[dict]:
    """Score a batch via API, using cache where possible."""
    to_score = []
    cached_results = []

    for row in batch:
        cn = row["Case Number"]
        desc = row.get("Description", "")
        if not force_rescore:
            cached = get_cached(conn, cn, desc)
            if cached:
                LOG.debug("Cache hit: %s", cn)
                cached_results.append(cached)
                continue
        to_score.append(row)

    if not to_score:
        return cached_results

    system_prompt = build_system_prompt(docs, is_closed_batch=is_closed)
    user_msg = build_user_message(to_score)
    results = call_claude(client, system_prompt, user_msg, model)

    # Match results back to rows by position
    scored = []
    for i, result in enumerate(results):
        if i < len(to_score):
            cn = to_score[i]["Case Number"]
            # Ensure Case Number matches input (Claude might echo it differently)
            result["Case Number"] = cn
            if is_closed:
                result["Urgency"] = 1
                result["Priority"] = int(result.get("Fit", 1)) * 1
            save_cached(conn, cn, to_score[i].get("Description", ""), result)
            scored.append(result)

    return cached_results + scored


def score_rows(
    client: anthropic.Anthropic,
    rows: list[dict],
    docs: dict[str, str],
    model: str,
    batch_size: int,
    is_closed: bool,
    conn: sqlite3.Connection,
    force_rescore: bool,
    dry_run: bool,
) -> list[dict]:
    """Score a list of rows in batches."""
    all_results = []
    total_batches = (len(rows) + batch_size - 1) // batch_size
    label = "closed" if is_closed else "active"

    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        batch_num = i // batch_size + 1
        LOG.info(
            "Scoring %s batch %d/%d (%d rows)",
            label, batch_num, total_batches, len(batch),
        )

        if dry_run:
            for row in batch:
                all_results.append({
                    "Case Number": row["Case Number"],
                    "Status": row.get("Status", ""),
                    "Age (Days)": row.get("Age (Days)", ""),
                    "Description": row.get("Description", ""),
                    "Summary": "[DRY RUN — no API call]",
                    "Distinct Capabilities Matched": "N/A",
                    "Fit": 0,
                    "Urgency": 0,
                    "Priority": 0,
                })
            continue

        batch_results = score_batch(
            client, batch, docs, model, is_closed, conn, force_rescore
        )
        all_results.extend(batch_results)
        LOG.info("  -> Got %d results", len(batch_results))

    return all_results


# ---------------------------------------------------------------------------
# Output: CSV
# ---------------------------------------------------------------------------

CSV_COLUMNS = [
    "Case Number",
    "Status",
    "Age (Days)",
    "Description",
    "Summary",
    "Distinct Capabilities Matched",
    "Fit",
    "Urgency",
    "Priority",
]


def write_csv(results: list[dict], output_path: Path):
    sorted_results = sorted(results, key=lambda r: (-int(r.get("Priority", 0)), -int(r.get("Fit", 0))))
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sorted_results)
    LOG.info("Wrote CSV: %s (%d rows)", output_path, len(sorted_results))


# ---------------------------------------------------------------------------
# Output: Summary markdown
# ---------------------------------------------------------------------------

def write_summary(results: list[dict], output_path: Path):
    sorted_results = sorted(results, key=lambda r: (-int(r.get("Priority", 0)), -int(r.get("Fit", 0))))
    lines = [
        "# Synaptiq Inquiry Analysis Summary",
        f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
        f"**Total inquiries scored:** {len(sorted_results)}\n",
    ]

    # Stats
    fit_scores = [int(r.get("Fit", 0)) for r in sorted_results]
    priority_scores = [int(r.get("Priority", 0)) for r in sorted_results]
    if fit_scores:
        avg_fit = sum(fit_scores) / len(fit_scores)
        avg_priority = sum(priority_scores) / len(priority_scores)
        lines.append(f"**Average Fit:** {avg_fit:.1f} | **Average Priority:** {avg_priority:.1f}\n")

    # Top Opportunities (Priority >= 16)
    top = [r for r in sorted_results if int(r.get("Priority", 0)) >= 16]
    lines.append("---\n")
    lines.append("## Top Opportunities (Priority >= 16)\n")
    if top:
        for r in top:
            lines.append(
                f"- **{r['Case Number']}** (Fit={r['Fit']}, Urgency={r['Urgency']}, "
                f"Priority={r['Priority']}): {r.get('Summary', 'N/A')}"
            )
            caps = r.get("Distinct Capabilities Matched", "")
            if caps and caps != "N/A":
                lines.append(f"  - Capabilities: {caps}")
    else:
        lines.append("*No inquiries scored Priority >= 16.*\n")

    # Quick Wins (Urgency = 5, Fit >= 3)
    quick_wins = [r for r in sorted_results if int(r.get("Urgency", 0)) == 5 and int(r.get("Fit", 0)) >= 3]
    lines.append("\n---\n")
    lines.append("## Quick Wins (Urgency = 5, Fit >= 3)\n")
    if quick_wins:
        for r in quick_wins:
            lines.append(
                f"- **{r['Case Number']}** (Fit={r['Fit']}, Priority={r['Priority']}): "
                f"{r.get('Summary', 'N/A')}"
            )
    else:
        lines.append("*No quick wins identified.*\n")

    # Distinct Capability Matches (Fit >= 4)
    distinct = [r for r in sorted_results if int(r.get("Fit", 0)) >= 4]
    lines.append("\n---\n")
    lines.append("## Distinct Capability Matches (Fit >= 4)\n")
    if distinct:
        cap_counts: dict[str, int] = {}
        for r in distinct:
            caps = r.get("Distinct Capabilities Matched", "")
            if caps and caps not in ("N/A", "None", "Overlap only", "None - IIA better fit"):
                for cap in caps.split(","):
                    cap = cap.strip()
                    if cap:
                        cap_counts[cap] = cap_counts.get(cap, 0) + 1
        if cap_counts:
            lines.append("### Capability Frequency\n")
            for cap, count in sorted(cap_counts.items(), key=lambda x: -x[1]):
                lines.append(f"- **{cap}**: {count} inquiries")
            lines.append("")
        for r in distinct:
            lines.append(
                f"- **{r['Case Number']}** (Fit={r['Fit']}): {r.get('Summary', 'N/A')}"
            )
    else:
        lines.append("*No inquiries scored Fit >= 4.*\n")

    # IIA Referral Candidates (Fit <= 2)
    iia = [r for r in sorted_results if int(r.get("Fit", 0)) <= 2 and int(r.get("Fit", 0)) > 0]
    lines.append("\n---\n")
    lines.append("## IIA Referral Candidates (Fit <= 2)\n")
    if iia:
        lines.append(f"**{len(iia)} inquiries** better suited for IIA or other partners.\n")
        # Show top 20 by priority
        for r in iia[:20]:
            lines.append(
                f"- **{r['Case Number']}** (Fit={r['Fit']}, Priority={r['Priority']}): "
                f"{r.get('Summary', 'N/A')}"
            )
        if len(iia) > 20:
            lines.append(f"\n*... and {len(iia) - 20} more. See full CSV for details.*\n")
    else:
        lines.append("*No IIA referral candidates identified.*\n")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    LOG.info("Wrote summary: %s", output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Score Synaptiq prospect inquiries using Claude API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("-i", "--input", default=str(SCRIPT_DIR / "inquiry_input.csv"), help="Input CSV path")
    p.add_argument("-o", "--output-dir", default=str(SCRIPT_DIR / "output"), help="Output directory")
    p.add_argument("-b", "--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Active row batch size")
    p.add_argument("--closed-batch-size", type=int, default=DEFAULT_CLOSED_BATCH_SIZE, help="Closed row batch size")
    p.add_argument("-m", "--model", default=DEFAULT_MODEL, help="Claude model ID")
    p.add_argument("--skip-closed", action="store_true", help="Skip LLM scoring for closed rows")
    p.add_argument("--force-rescore", action="store_true", help="Ignore cache, rescore everything")
    p.add_argument("--cache-file", default=str(SCRIPT_DIR / "cache.db"), help="SQLite cache file path")
    p.add_argument("--dry-run", action="store_true", help="Preview partitioning without API calls")
    p.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    return p.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    # Validate input
    if not os.path.isfile(args.input):
        LOG.error("Input CSV not found: %s", args.input)
        sys.exit(1)

    # Load reference docs
    docs = load_reference_docs()
    LOG.info("Loaded reference documents")

    # Load and partition CSV
    rows = load_csv(args.input)
    LOG.info("Loaded %d rows from %s", len(rows), args.input)

    parts = partition_rows(rows)
    LOG.info(
        "Partitioned: %d active, %d closed, %d trivial",
        len(parts["active"]),
        len(parts["closed"]),
        len(parts["trivial"]),
    )

    # Init cache
    conn = init_cache(args.cache_file)

    # Init API client (not needed for dry-run, but validate key early)
    client = None
    if not args.dry_run:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            LOG.error("ANTHROPIC_API_KEY not set. Export it or add to .env file.")
            sys.exit(1)
        client = anthropic.Anthropic(api_key=api_key)

    all_results: list[dict] = []

    # 1. Pre-score trivial rows locally
    LOG.info("Pre-scoring %d trivial rows (no API call)", len(parts["trivial"]))
    for row in parts["trivial"]:
        all_results.append(prescore_trivial(row))

    # 2. Score active rows
    if parts["active"]:
        LOG.info("Scoring %d active rows (batch size %d)", len(parts["active"]), args.batch_size)
        active_results = score_rows(
            client,  # type: ignore[arg-type]
            parts["active"],
            docs,
            args.model,
            args.batch_size,
            is_closed=False,
            conn=conn,
            force_rescore=args.force_rescore,
            dry_run=args.dry_run,
        )
        all_results.extend(active_results)

    # 3. Score closed rows (or skip)
    if args.skip_closed:
        LOG.info("Skipping %d closed rows (--skip-closed)", len(parts["closed"]))
        for row in parts["closed"]:
            all_results.append(prescore_trivial(row))
    elif parts["closed"]:
        LOG.info(
            "Scoring %d closed rows (batch size %d, Urgency fixed at 1)",
            len(parts["closed"]),
            args.closed_batch_size,
        )
        closed_results = score_rows(
            client,  # type: ignore[arg-type]
            parts["closed"],
            docs,
            args.model,
            args.closed_batch_size,
            is_closed=True,
            conn=conn,
            force_rescore=args.force_rescore,
            dry_run=args.dry_run,
        )
        all_results.extend(closed_results)

    # 4. Write output
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = out_dir / f"inquiry_analysis_{ts}.csv"
    summary_path = out_dir / f"inquiry_analysis_{ts}_summary.md"

    write_csv(all_results, csv_path)
    write_summary(all_results, summary_path)

    # Final summary
    LOG.info("--- Done ---")
    LOG.info("Total scored: %d", len(all_results))
    scored_with_api = [r for r in all_results if r.get("Summary") != "[DRY RUN — no API call]" and r.get("Summary") != "Inquiry was cancelled." and r.get("Summary") != "No description provided."]
    LOG.info("API-scored: %d | Pre-scored: %d", len(scored_with_api), len(all_results) - len(scored_with_api))
    LOG.info("Output CSV: %s", csv_path)
    LOG.info("Summary: %s", summary_path)

    conn.close()


if __name__ == "__main__":
    main()
