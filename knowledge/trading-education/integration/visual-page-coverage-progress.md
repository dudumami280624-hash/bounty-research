# PDF page-level visual coverage (not semantic verification)

- PDF files with tracked visual audit: 26
- Page coverage complete: 10
- Windows attempted this run: 6
- Repeated failures cooling down for automatic retry: 0
- Page coverage finished but OCR incomplete: 2
- Chart semantics independently verified: 0 (not performed by this scanner)
- Source page hashes and positions only; no copyrighted pages or OCR excerpts.

## 2026-11-21 audit correctness fix

- Empty scanner windows previously could set `coverage_complete=true` because `next_page=0` and `total_pages=0`; corrected in `resume_visual_pages.py`.
- Reject noncontiguous page locators, zero page count and out-of-range windows; retain source checkpoint and retry on error.
- Added `test_visual_window_validation.py` with synthetic invalid/valid windows; main workflow commit `e0bb7cfb1bd45fab5e75d5f64bd31bc546880322` invokes it.
- **Validation status:** workflow run for this commit not yet observed; prior successful run `44891806169` did not contain this regression test. No real chart semantics or independent factual checks claimed.
- **Next:** verify new run and repair any CI failures; then implement persistent bounded text extraction for large PDFs (current page windows only cover visual scanning).
