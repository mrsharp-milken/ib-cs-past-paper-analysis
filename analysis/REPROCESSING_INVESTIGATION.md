# Past Paper Analysis — Reprocessing Investigation

This document summarizes findings on subtopic inconsistencies (4.4, 2.2), multi-subtopic handling, and other improvements.

---

## 1. Subtopic 4.4 — "0 in most papers, 33 in one"

### What the data shows

- **frequency_by_subtopic.csv**: 4.4 has `min_combined_marks=0`, `median=0`, `max_combined_marks=33`, with max only in **May 2015**.
- Papers with **0** marks for 4.4 include: May 2019, 2021, 2022, 2023, 2024, Nov 2014–2023 (many sessions).
- Papers with **non-zero** 4.4 marks: May 2014, 2015, 2016, 2017, 2018, Nov 2024.

### Root cause: inconsistent coding, not syllabus

- The syllabus reference file **Computer Science Strands Topics1-7.csv** lists Topic 4 as **4.1, 4.2, 4.3** only. There is **no 4.4** in that syllabus.
- In the CSVs, **4.4** is used for algorithm construction/tracing (e.g. "Construct algorithm", "Trace", pseudocode). That content in the official syllabus sits under **4.2** (e.g. 4.2.4–4.2.9: analyse/construct pseudocode, algorithms) and **4.3** (e.g. 4.3.9, 4.3.13: construct algorithms using loops, arrays, collections).
- So **4.4** is an extra code used only in some papers. Where it is used (e.g. May 2014–2018, Nov 2024), algorithm-heavy questions are tagged 4.4; where it is not (e.g. Nov 2023, May 2022), the same type of question is tagged **4.2** or **4.3** (or even **5.1** when focused on data structures).

**Examples:**

| Paper    | Question type              | Coded as |
|----------|----------------------------|----------|
| May 2015 | Construct algorithm; trace | 4.4      |
| May 2022 | Construct algorithm; pseudocode; array | 4.3      |
| Nov 2023 | Construct algorithm; 2D array; pseudocode | 5.1  |

### Recommendation

- **Option A (align to syllabus):** Treat 4.4 as invalid and **re-map all 4.4** to **4.2** (algorithm/pseudocode design) or **4.3** (constructing code) using a simple rule (e.g. "Construct/Trace algorithm" → 4.2, "Construct using loops/arrays" → 4.3). Then regenerate frequency tables.
- **Option B (keep 4.4):** Add 4.4 to the analysis as an explicit "HL algorithm focus" code, document the mapping rule in ANALYSIS_BRIEF.md, and **reprocess papers that currently use only 4.2/4.3** for algorithm construction so that algorithm-heavy parts are also tagged 4.4 where appropriate. That would make 4.4 stats comparable across papers.

---

## 2. Subtopic 2.2 — "0 in most papers, 7 in one"

### What the data shows

- **2.2** has `min_combined_marks=0`, `median=0`, `max_combined_marks=7` (Nov 2024).
- Only a few papers have any 2.2: May 2014, 2016, 2017, 2018, Nov 2024 (and pre-2014 May 2013).

### Root cause

- The syllabus file only has **2.1** for Topic 2 (Computer organization). There is **no 2.2** in the Strands file.
- In the CSVs, **2.2** is used for CPU/architecture/memory (e.g. RAM/ROM, control unit, ALU, MDR, cache, interrupts). In the official syllabus that content is under **2.1** (e.g. 2.1.1–2.1.4: CPU, ALU, CU, registers, primary memory, cache, machine instruction cycle).
- So 2.2 is again an extra code. Most papers code these questions as **2.1**; a few (and Nov 2024 in particular) use **2.2**, hence 0 in most papers and 7 in one.

### Recommendation

- **Option A:** Re-map all **2.2** → **2.1** so Topic 2 is consistent with the syllabus and combined marks for "Computer organization" are comparable.
- **Option B:** If you want to keep 2.2 (e.g. for "low-level architecture" vs "general organization"), document it and optionally reprocess so that CPU/registers/memory questions are coded consistently (either all 2.1 or split 2.1/2.2 by a clear rule).

---

## 3. Questions that connect to multiple subtopics

### Current behaviour

- The CSV schema has **one row per question part** and **one subtopic per row** (single `subtopic` column).
- So a question that clearly spans two subtopics (e.g. "construct an algorithm using a 2D array" → 4.2/4.4 and 5.1) is forced into a **single** subtopic. Different coders (or the same coder at different times) may choose different "primary" subtopics.
- That leads to:
  - **Under-counting** for one of the subtopics.
  - **Inconsistent totals** when the "primary" choice varies (e.g. 4.4 vs 4.3 vs 5.1 for algorithm+data-structure questions).

### Possible improvements

1. **Allow multiple subtopics per row (recommended)**  
   - Add a second column, e.g. `subtopic_secondary`, or allow `subtopic` to contain semicolon-separated values (e.g. `4.4; 5.1`).  
   - Update ANALYSIS_BRIEF.md: "If a question part clearly maps to two subtopics, list the primary in `subtopic` and the other in `subtopic_secondary`, or use semicolon-separated subtopics."  
   - In aggregation:
     - For **counts and total_marks**: either count the row under each listed subtopic (with a rule to avoid double-counting marks, e.g. count full marks once per subtopic for "combined marks per paper").
     - Or define "primary subtopic gets full marks; secondary gets 0" for combined marks, and use secondary only for concept coverage.

2. **Keep single subtopic but add guidance**  
   - In ANALYSIS_BRIEF.md, add a rule: "When a question spans two subtopics, choose the one that carries the **majority of the marks** or the **main skill** (e.g. 'construct algorithm' → 4.2/4.4 over 5.1 if the focus is algorithm design)."  
   - Then reprocess papers where multi-subtopic questions were coded inconsistently.

3. **Support multiple rows per question part**  
   - Allow duplicate rows with same `question` but different `subtopic`, and split `marks` (e.g. 6 marks → 4 for 4.4, 2 for 5.1). This is more accurate but heavier to maintain and requires clear rules for splitting.

Recommendation: **Option 1** (semicolon-separated or secondary subtopic) plus a clear rule in the brief, and aggregation that counts each subtopic for frequency but attributes full marks only to the primary subtopic for "combined marks per paper" to keep totals correct.

---

## 4. Other improvements

### 4.1 Pre-2014 papers excluded by design

- **aggregate_and_summarize.py** uses `CSV_DIR.glob("*.csv")`, so only CSVs **directly** in `analysis/csv/` are loaded. CSVs in `analysis/csv/pre-2014/` are **intentionally** excluded (different syllabus).

### 4.2 Syllabus alignment

- **pattern_analysis.py** uses a hardcoded `ALL_SUBTOPICS` that includes **4.4** and **2.2**. The syllabus file does not. Consider:
  - Either removing 4.4 and 2.2 from the canonical list and re-mapping them in the data, or
  - Adding 4.4 and 2.2 to a "HL/extension" syllabus reference and using them consistently (see sections 1 and 2).

### 4.3 Verification

- Add a small check (e.g. in **aggregate_and_summarize.py** or a separate script): for each subtopic code present in the CSVs, verify it appears in the official syllabus (or in an allowed extension list). That would have caught 4.4 and 2.2 as non-standard.

### 4.4 Total marks consistency

- **verify_total_marks** already checks that all papers have the same total marks. Keep this; if you split marks across subtopics (option 3 in section 3), ensure the sum of marks per paper is still correct.

---

## 5. Summary of suggested actions

| Priority | Action |
|----------|--------|
| 1 | Decide policy for 4.4 and 2.2: either re-map to 4.2/4.3 and 2.1, or document and use them consistently and optionally reprocess. |
| 2 | Extend schema and brief for multi-subtopic (e.g. secondary subtopic or semicolon-separated), and define how aggregation counts marks. |
| 3 | Add syllabus validation so only defined (or explicitly allowed) subtopics are used. |

If you tell me which options you prefer (4.4/2.2: A or B; multi-subtopic: 1, 2, or 3), I can outline concrete CSV and script changes next.
