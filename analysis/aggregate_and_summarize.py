#!/usr/bin/env python3
"""
Aggregate per-paper topic-mapping CSVs into one merged file and produce
frequency tables. Session and paper are parsed from each CSV filename.
"""

import csv
import re
from pathlib import Path
from collections import Counter, defaultdict

# Paths relative to script location
SCRIPT_DIR = Path(__file__).resolve().parent
CSV_DIR = SCRIPT_DIR / "csv"
OUTPUT_DIR = SCRIPT_DIR

# All IB CS HL syllabus topics (1-7); include all in topic frequency so Topic 6 etc. appear even with 0
ALL_TOPICS = ["1", "2", "3", "4", "5", "6", "7"]


def parse_filename(filename: str) -> tuple[str, str]:
    """Parse csv_filename (e.g. Nov_2024_P1_HL.csv) into (session, paper)."""
    stem = Path(filename).stem  # e.g. Nov_2024_P1_HL
    # Pattern: {Month}_{Year}_P1_HL
    match = re.match(r"^(May|Nov)_(\d{4})_P1_HL$", stem, re.IGNORECASE)
    if match:
        month, year = match.groups()
        session = f"{month} {year}"
        paper = "P1 HL"
        return session, paper
    # Fallback: use stem as session, P1 HL as paper
    session = stem.replace("_", " ")
    return session, "P1 HL"


def load_all_papers() -> list[dict]:
    """Load per-paper CSVs from csv/ only (excludes subfolders e.g. pre-2014/ — different syllabus)."""
    rows = []
    for path in sorted(CSV_DIR.glob("*.csv")):
        session, paper = parse_filename(path.name)
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["session"] = session
                row["paper"] = paper
                rows.append(row)
    return rows


def sort_key(row: dict) -> tuple:
    """Sort by session (Nov before May within year for consistency), then question."""
    s = row["session"]
    # "May 2013" -> (2013, 0), "Nov 2013" -> (2013, 1) so May then Nov
    parts = s.split()
    if len(parts) == 2:
        year = int(parts[1])
        month_order = 0 if parts[0].lower() == "may" else 1
        return (year, month_order, row.get("question", ""))
    return (0, 0, row.get("question", ""))


def merge_csv(rows: list[dict], out_path: Path) -> None:
    """Write merged CSV with columns: session, paper, question, marks, command_term, topic, subtopic, concepts."""
    fieldnames = ["session", "paper", "question", "marks", "command_term", "topic", "subtopic", "concepts"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in sorted(rows, key=sort_key):
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def frequency_tables(rows: list[dict]) -> dict:
    """Compute counts by topic, subtopic, concept, command_term."""
    by_topic = Counter()
    by_subtopic = Counter()
    by_concept = Counter()
    by_command = Counter()
    for row in rows:
        by_topic[row.get("topic", "").strip()] += 1
        by_subtopic[row.get("subtopic", "").strip()] += 1
        by_command[row.get("command_term", "").strip()] += 1
        concepts = row.get("concepts", "") or ""
        for c in (x.strip() for x in concepts.split(";") if x.strip()):
            by_concept[c] += 1
    return {
        "topic": by_topic,
        "subtopic": by_subtopic,
        "concept": by_concept,
        "command_term": by_command,
    }


def write_frequency_csv(freq: Counter, out_path: Path, col_name: str, all_keys: list[str] | None = None) -> None:
    """Write a two-column CSV: col_name, count. If all_keys given (e.g. ALL_TOPICS), list all with 0 for missing."""
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([col_name, "count"])
        if all_keys is not None:
            for key in all_keys:
                w.writerow([key, freq.get(key, 0)])
        else:
            for key, count in freq.most_common():
                w.writerow([key, count])


def write_frequency_md(tables: dict, out_path: Path) -> None:
    """Write frequency_summary.md with all tables. Topic table includes all 1-7."""
    lines = ["# Frequency summary (Paper 1 HL)\n"]
    for name, freq in tables.items():
        lines.append(f"## By {name.replace('_', ' ')}\n")
        lines.append("| " + name.replace("_", " ") + " | count |")
        lines.append("| --- | --- |")
        if name == "topic":
            for key in ALL_TOPICS:
                count = freq.get(key, 0)
                lines.append(f"| {key} | {count} |")
        else:
            for key, count in freq.most_common():
                lines.append(f"| {key} | {count} |")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def verify_total_marks(rows: list[dict]) -> None:
    """Verify each paper has the same total marks; print result."""
    totals: dict[str, int] = defaultdict(int)
    for row in rows:
        session = row.get("session", "")
        try:
            marks = int(row.get("marks", 0) or 0)
        except (ValueError, TypeError):
            marks = 0
        totals[session] += marks

    if not totals:
        return

    values = list(totals.values())
    if len(set(values)) == 1:
        print(f"All papers had a total of {values[0]} marks")
    else:
        print("Papers with different totals:")
        for session in sorted(totals.keys()):
            print(f"  {session}: {totals[session]} marks")


def main() -> None:
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_all_papers()
    if not rows:
        print("No CSV files found in", CSV_DIR)
        return

    merge_path = OUTPUT_DIR / "all_p1_hl.csv"
    merge_csv(rows, merge_path)
    print("Merged CSV written to", merge_path)

    tables = frequency_tables(rows)
    write_frequency_csv(tables["topic"], OUTPUT_DIR / "frequency_by_topic.csv", "topic", all_keys=ALL_TOPICS)
    write_frequency_csv(tables["subtopic"], OUTPUT_DIR / "frequency_by_subtopic.csv", "subtopic")
    write_frequency_csv(tables["concept"], OUTPUT_DIR / "frequency_by_concept.csv", "concept")
    write_frequency_csv(tables["command_term"], OUTPUT_DIR / "frequency_by_command_term.csv", "command_term")
    write_frequency_md(tables, OUTPUT_DIR / "frequency_summary.md")
    print("Frequency tables written to", OUTPUT_DIR)

    verify_total_marks(rows)


if __name__ == "__main__":
    main()
