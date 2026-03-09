#!/usr/bin/env python3
"""
Read all_p1_hl.csv and write frequency CSVs (with marks stats) and pattern_summary.md:
high-frequency vs rare topics/subtopics/concepts, with marks analysis.
"""

import csv
import statistics
from pathlib import Path
from collections import Counter, defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent
MERGED_CSV = SCRIPT_DIR / "all_p1_hl.csv"
OUTPUT_MD = SCRIPT_DIR / "pattern_summary.md"

# Frequency CSV output paths
FREQ_TOPIC = SCRIPT_DIR / "frequency_by_topic.csv"
FREQ_SUBTOPIC = SCRIPT_DIR / "frequency_by_subtopic.csv"
FREQ_CONCEPT = SCRIPT_DIR / "frequency_by_concept.csv"
FREQ_COMMAND = SCRIPT_DIR / "frequency_by_command_term.csv"

# Topic numbers to names for readability (IB CS HL)
TOPIC_NAMES = {
    "1": "System fundamentals",
    "2": "Computer organization",
    "3": "Networks",
    "4": "Computational thinking, problem-solving and programming",
    "5": "Abstract data structures",
    "6": "Resource management",
    "7": "Control",
}
# All syllabus topics so Topic 6 (and any other with 0) appears in summaries
ALL_TOPICS = ["1", "2", "3", "4", "5", "6", "7"]
# All syllabus subtopics (IB CS HL) — 2.2 and 4.4 do not exist
ALL_SUBTOPICS = ["1.1", "1.2", "2.1", "3.1", "4.1", "4.2", "4.3", "5.1", "6.1", "7.1"]


def load_rows():
    rows = []
    with open(MERGED_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def parse_marks(marks_str: str) -> int:
    """Parse marks string to int; return 0 if invalid."""
    try:
        return int(marks_str.strip())
    except (ValueError, TypeError):
        return 0


def compute_frequency_with_marks(rows, key_fn, all_keys=None):
    """
    Compute count, total_marks, per-paper question counts, and per-paper marks.
    key_fn(row) -> key or list of keys (e.g. for concepts).
    Returns dict: key -> {count, total_marks, questions_per_paper, combined_per_paper}
    """
    count_by_key = Counter()
    total_marks_by_key = defaultdict(int)
    # questions_per_paper[key] = {paper_id: num_questions}
    questions_per_paper = defaultdict(lambda: defaultdict(int))
    # combined_per_paper[key] = {paper_id: sum_of_marks}
    combined_per_paper = defaultdict(lambda: defaultdict(int))

    for row in rows:
        marks = parse_marks(row.get("marks", ""))
        paper_id = (row["session"], row["paper"])
        keys = key_fn(row)
        if not isinstance(keys, list):
            keys = [keys] if keys else []
        for k in keys:
            if not k:
                continue
            count_by_key[k] += 1
            total_marks_by_key[k] += marks
            questions_per_paper[k][paper_id] += 1
            combined_per_paper[k][paper_id] += marks

    return {
        "count": count_by_key,
        "total_marks": dict(total_marks_by_key),
        "questions_per_paper": dict(questions_per_paper),
        "combined_per_paper": dict(combined_per_paper),
        "all_keys": all_keys,
    }


def get_question_stats(questions_per_paper, key, all_papers):
    """Return (min, median, max) of question count per paper for given key. Papers with no questions count as 0."""
    paper_qs = questions_per_paper.get(key, {})
    per_paper = [paper_qs.get(pid, 0) for pid in all_papers]
    if not per_paper:
        return 0, 0, 0
    return min(per_paper), statistics.median(per_paper), max(per_paper)


def get_marks_stats(combined_per_paper, key, all_papers):
    """Return (min, median, max) of combined marks per paper for given key. Papers with no questions count as 0."""
    paper_marks = combined_per_paper.get(key, {})
    per_paper = [paper_marks.get(pid, 0) for pid in all_papers]
    if not per_paper:
        return 0, 0, 0
    return min(per_paper), statistics.median(per_paper), max(per_paper)


def get_min_max_papers(combined_per_paper, key, all_papers):
    """Return (min_papers, max_papers) - session strings for papers with min/max combined marks (incl. 0)."""
    paper_marks = {pid: combined_per_paper.get(key, {}).get(pid, 0) for pid in all_papers}
    if not paper_marks:
        return "", ""
    mn_val = min(paper_marks.values())
    mx_val = max(paper_marks.values())
    min_papers = "; ".join(session for (session, _), v in paper_marks.items() if v == mn_val)
    max_papers = "; ".join(session for (session, _), v in paper_marks.items() if v == mx_val)
    return min_papers, max_papers


def write_frequency_csv(data, out_path, col_name, all_papers, all_keys=None):
    """Write CSV with col_name, count, total_marks, min/med/max Qs, min/med/max Marks, min_papers, max_papers."""
    count_by = data["count"]
    total_marks_by = data["total_marks"]
    questions_per_paper = data["questions_per_paper"]
    combined_per_paper = data["combined_per_paper"]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            col_name, "count", "total_marks",
            "min_qs", "median_qs", "max_qs",
            "min_marks", "median_marks", "max_marks",
            "min_marks_papers", "max_marks_papers",
        ])

        keys = all_keys if all_keys is not None else [k for k, _ in count_by.most_common()]
        for key in keys:
            count = count_by.get(key, 0)
            total = total_marks_by.get(key, 0)
            qs_mn, qs_med, qs_mx = get_question_stats(questions_per_paper, key, all_papers)
            mk_mn, mk_med, mk_mx = get_marks_stats(combined_per_paper, key, all_papers)
            min_ps, max_ps = get_min_max_papers(combined_per_paper, key, all_papers)
            qs_med_str = int(qs_med) if qs_med == int(qs_med) else round(qs_med, 1)
            mk_med_str = int(mk_med) if mk_med == int(mk_med) else round(mk_med, 1)
            w.writerow([key, count, total, qs_mn, qs_med_str, qs_mx, mk_mn, mk_med_str, mk_mx, min_ps, max_ps])


def main():
    if not MERGED_CSV.exists():
        print("Run aggregate_and_summarize.py first.")
        return

    rows = load_rows()
    n_questions = len(rows)
    all_papers = sorted({(r["session"], r["paper"]) for r in rows})
    n_papers = len(all_papers)

    # Topic: single key per row
    topic_data = compute_frequency_with_marks(
        rows,
        lambda r: r["topic"].strip(),
        all_keys=ALL_TOPICS,
    )
    write_frequency_csv(topic_data, FREQ_TOPIC, "topic", all_papers, ALL_TOPICS)

    # Subtopic: include all syllabus subtopics (exclude 2.2 and 4.4 — they do not exist)
    def subtopic_key(r):
        st = r["subtopic"].strip()
        return st if st and st not in ("2.2", "4.4") else None

    subtopic_data = compute_frequency_with_marks(rows, subtopic_key)
    write_frequency_csv(subtopic_data, FREQ_SUBTOPIC, "subtopic", all_papers, all_keys=ALL_SUBTOPICS)

    # Concept: multiple keys per row (semicolon-separated)
    def concept_keys(r):
        return [c.strip() for c in (r.get("concepts") or "").split(";") if c.strip()]

    concept_data = compute_frequency_with_marks(rows, concept_keys)
    write_frequency_csv(concept_data, FREQ_CONCEPT, "concept", all_papers)

    # Command term
    command_data = compute_frequency_with_marks(rows, lambda r: r["command_term"].strip())
    write_frequency_csv(command_data, FREQ_COMMAND, "command_term", all_papers)

    print("Frequency CSVs written to", SCRIPT_DIR)

    by_topic = topic_data["count"]
    by_subtopic = subtopic_data["count"]
    by_command = command_data["count"]
    by_concept = concept_data["count"]

    def fmt_med(med):
        return str(int(med)) if med == int(med) else f"{med:.1f}"

    lines = [
        "# Pattern analysis (Paper 1 HL)",
        "",
        f"Based on {n_questions} question parts from {n_papers} papers.",
        "",
        "**Column note:** Median # of Qs = median questions per paper; Median Marks = median marks per paper. Papers with no questions on that topic/subtopic/concept count as 0.",
        "",
        "---",
        "",
        "## Likely vs unlikely topics",
        "",
        "**All syllabus topics** (1-7) with question counts and marks:",
        "",
        "| Topic | Name | Count | % | Total marks | Median # of Qs | Median Marks |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for topic in ALL_TOPICS:
        count = by_topic.get(topic, 0)
        pct = 100 * count / n_questions if n_questions else 0
        name = TOPIC_NAMES.get(topic, f"Topic {topic}")
        total_m = topic_data["total_marks"].get(topic, 0)
        _, qs_med, _ = get_question_stats(topic_data["questions_per_paper"], topic, all_papers)
        _, mk_med, _ = get_marks_stats(topic_data["combined_per_paper"], topic, all_papers)
        lines.append(f"| {topic} | {name} | {count} | {pct:.1f}% | {total_m} | {fmt_med(qs_med)} | {fmt_med(mk_med)} |")
    lines.extend([
        "",
        "**High-frequency** (most tested): Topics 4, 1, 2, 5, 3. **Rare or absent in Paper 1 HL:** Topic 6 (Resource management), Topic 7 (Control).",
        "",
        "## Likely vs unlikely subtopics",
        "",
        "**All syllabus subtopics:**",
        "",
        "| Subtopic | Count | % | Total marks | Median # of Qs | Median Marks |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for st in ALL_SUBTOPICS:
        count = by_subtopic.get(st, 0)
        pct = 100 * count / n_questions if n_questions else 0
        total_m = subtopic_data["total_marks"].get(st, 0)
        _, qs_med, _ = get_question_stats(subtopic_data["questions_per_paper"], st, all_papers)
        _, mk_med, _ = get_marks_stats(subtopic_data["combined_per_paper"], st, all_papers)
        lines.append(f"| {st} | {count} | {pct:.1f}% | {total_m} | {fmt_med(qs_med)} | {fmt_med(mk_med)} |")
    lines.extend([
        "",
        "## Common concepts",
        "",
        "Concepts that appear in many questions (top 15):",
        "",
        "| Concept | Count | Total marks | Median # of Qs | Median Marks |",
        "| --- | --- | --- | --- | --- |",
    ])
    for concept, count in by_concept.most_common(15):
        total_m = concept_data["total_marks"].get(concept, 0)
        _, qs_med, _ = get_question_stats(concept_data["questions_per_paper"], concept, all_papers)
        _, mk_med, _ = get_marks_stats(concept_data["combined_per_paper"], concept, all_papers)
        lines.append(f"| {concept} | {count} | {total_m} | {fmt_med(qs_med)} | {fmt_med(mk_med)} |")
    lines.extend([
        "",
        "## Command terms",
        "",
        "Most used command terms:",
        "",
        "| Command term | Count | Total marks | Median # of Qs | Median Marks |",
        "| --- | --- | --- | --- | --- |",
    ])
    for ct, count in by_command.most_common(10):
        total_m = command_data["total_marks"].get(ct, 0)
        _, qs_med, _ = get_question_stats(command_data["questions_per_paper"], ct, all_papers)
        _, mk_med, _ = get_marks_stats(command_data["combined_per_paper"], ct, all_papers)
        lines.append(f"| {ct} | {count} | {total_m} | {fmt_med(qs_med)} | {fmt_med(mk_med)} |")

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("Pattern summary written to", OUTPUT_MD)


if __name__ == "__main__":
    main()
