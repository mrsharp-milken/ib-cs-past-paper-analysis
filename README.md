# Past Papers — Analysis (public)

Topic and frequency analysis for IB Computer Science Paper 1 HL past papers.

## Contents

- **`analysis/`** — Scripts, per-paper CSVs, merged data, and frequency summaries. Run `aggregate_and_summarize.py` then `pattern_analysis.py` from that directory.
- **`private_pdfs/`** — Symlink to `Past-Papers-Private/` (sibling folder containing the year folders). Used so paths in `analysis/PAPERS_TO_PROCESS.md` resolve locally. If you clone this repo alone, the link will be broken; the analysis does not depend on the PDFs.

## Repo split

- **This repo (public):** Analysis code and outputs only; no exam PDFs.
- **Private repo:** `Past-Papers-Private/` with folders like `Nov 2020/`, `May 2021/` containing the PDFs.

## Notes

I need to reprocess most of the PDFs with a more powerful model. On the initial pass the model I chose (Cursor's Composer) did a poor job of aligning questions to the appropriate Strands, even making up subtopics (2.2 and 4.4) that do not exist.

These are the CSVs that have already been reprocessed with Sonnet 4.6, I need to do the rest
- May_2014_P1_HL.csv
- May_2015_P1_HL.csv
- May_2016_P1_HL.csv
- May_2017_P1_HL.csv
- May_2018_P1_HL.csv
- Nov_2024_P1_HL.csv
