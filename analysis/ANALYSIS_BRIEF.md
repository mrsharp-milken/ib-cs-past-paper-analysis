# Past Paper Topic Mapping — Instructions

Map each question part in an IB Computer Science Paper 1 HL exam to the syllabus (topic, subtopic, concepts). Output one CSV per paper. Session and paper identity come from the filename; the aggregation script will parse it.

## Workflow

1. **Claim (parallel-safe):** Pick the next row in `PAPERS_TO_PROCESS.md` that has status `pending` and for which `analysis/claims/{csv_filename}.claim` does **not** exist. Create that claim file only if it does not exist (atomic create). Example: `python3 -c "import os; p='analysis/claims/{csv_filename}.claim'; os.makedirs('analysis/claims', exist_ok=True); os.close(os.open(p, os.O_CREAT|os.O_EXCL|os.O_WRONLY))"` — use the actual `csv_filename` for that row. If the create fails because the file exists, another agent claimed it; re-read the list and try the next such pending row. If no unclaimed pending row remains, stop. Once you have created a claim file, you have exclusively claimed that paper.
2. In `analysis/PAPERS_TO_PROCESS.md`, set that paper's row to `in-progress`.
3. **Read the PDF directly** using your file-read capability (e.g. the Read tool) at the path given in that row — do not use scripts, `pdftotext`, or PDF extraction libraries. Map every question part to topic, subtopic, and concepts (IB CS syllabus). Write the CSV to `analysis/csv/{csv_filename}` for that row.
4. In `PAPERS_TO_PROCESS.md`, set that paper's row to `done`.
5. Delete the claim file `analysis/claims/{csv_filename}.claim`.

## CSV schema (per-paper)

No `session` or `paper` columns — those are inferred from the filename by the aggregator.

| Column       | Example                             | Notes |
| ------------ | ----------------------------------- | ----- |
| question     | 1, 2, 7, 11a, 12c                   | Question part identifier |
| marks        | 2, 4                                | From the paper |
| command_term | State, Outline, Describe, Determine | IB command term |
| topic        | 1, 2, 3, 4, 5, 6, 7                 | Syllabus topic number (1–7) |
| subtopic     | 1.1, 4.3, 5.1                       | e.g. 5.1 = Abstract data structures |
| concepts     | spreadsheets; recursion; stack       | Short keywords, semicolon-separated |

## Valid syllabus topics and subtopics

The only valid subtopic codes are listed below. **Do not invent subtopic numbers.** If a question does not fit neatly, use the closest valid subtopic and note the concepts column.

| Topic | Name | Valid subtopics |
|-------|------|-----------------|
| 1 | System fundamentals | 1.1 Systems in organisations · 1.2 System design basics · 1.3 Human interaction with the system · 1.4 Different types of system |
| 2 | Computer organisation | 2.1 Computer architecture (the only subtopic in Topic 2) |
| 3 | Networks | 3.1 Networks |
| 4 | Computational thinking, problem-solving and programming | 4.1 General principles · 4.2 Connecting computational thinking and program design · 4.3 Algorithm design (HL only) |
| 5 | Abstract data structures (HL only) | 5.1 Abstract data structures (the only subtopic in Topic 5) |
| 6 | Resource management (HL only) | 6.1 Resource management (the only subtopic in Topic 6) |
| 7 | Control (HL only) | 7.1 Control (the only subtopic in Topic 7) |

## Question coding

- Section A: questions 1–10 (no sub-parts unless the paper has (a)(b) etc.).
- Section B: 11, 11a, 11b, …, 12, 12a, 12b, 12c(i), 12c(ii), etc. Use the exact part labels from the paper.

## Filename rule

Each paper's CSV filename is in the `csv_filename` column of `PAPERS_TO_PROCESS.md` (e.g. `Nov_2024_P1_HL.csv`, `May_2013_P1_HL.csv`). Session and paper are encoded in the filename so the aggregation script can parse them.

## Reading the paper

Read the question paper PDF using your built-in file read tool (e.g. `Read` with the PDF path). Do **not** run scripts or install tools (e.g. `pdftotext`, `pypdf`) to extract text — reading the file directly is sufficient and preferred.

## Picking a paper

Process the **next pending** row in `PAPERS_TO_PROCESS.md` (workflow step 1 uses a claim file so only one agent takes each paper). If you are told to process a specific paper, use that row and skip the claim step: set in-progress → process → done (no claim file).
