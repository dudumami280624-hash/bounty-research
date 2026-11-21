# 2026-11-21 — bounded initial OCR / large PDF follow-up

Evidence: GitHub Actions run 44872898838 succeeded overall, but source `《金融炼金术》乔治·索罗斯.pdf` (Git blob `5726836b66f424f3c8e90f80486d871b9f53cdf7`) failed its 90-second worker deadline, after BEGIN at 05:53:14Z and END at 05:54:44Z. Other sources continued; the run reported 103/178 extracted, 9 partial OCR, 1 visual review and 1 failed. A successful workflow is **not** proof that every source succeeded.

Change: initial PDF text extraction now OCRs at most four image-only pages, and records the exact 1-based deferred pages as `ocr_deferred_pages` and `ocr_failed_pages`. Deferred pages remain `partial_ocr_failure`, never verified. The existing separate visual page auditor is responsible for follow-up. This bounds OCR subprocess count but **does not** make giant PDFs resumable at the text-extraction stage, nor does it independently verify charts.

Commits: research `285072556943e56883fe739c0cd351c4c1ea3ce2`, regression `b070d7600063f8fa78d3bfab2ba949b15b2618f7`; main workflow `eeeedf6dbea963463e8bca0ce7488269db5907c7`. Live test run `44877897788` was queued when inspected, not yet verified.

NEXT RUN FIRST: inspect run 44877897788, especially the synthetic OCR deferral test and the real failed Soros PDF. If the Soros source still times out, implement a durable page-chunk text extraction state machine (source SHA, page cursor, completed-page hashes and pending OCR pages), without committing copyrighted text; avoid just increasing timeout. Validate a real multi-run continuation on that source. Continue the remaining source queue. The synthetic test does not establish real OCR or visual/semantic verification.

No copyrighted excerpts or images stored here. No paid APIs or external publication.

## Follow-up: empty OCR output incorrectly counted as success

Observed in `tools/free_visual.py`: Tesseract return code 0 was treated as `ocr_success=True` even if stdout was empty. This could remove pages from the failed-page retry queue and overstate OCR completion. Research commit `520450b17fee847c821b5ae6fcadcaca3bcd0a76` now requires both exit code 0 and non-empty recognized text; otherwise the page remains pending review. Main workflow trigger commit `d4a44a78d366b2d0f35e1bab9e1c228c0088ffc5`. Latest previously completed live Actions run `44881780193` succeeded; this predates the fix and cannot validate it. The latest report records 104/178 extracted and 24 partial OCR; no independently verified chart semantics or factual claims. NEXT: inspect new run ID and logs, confirm real extraction and visual-page audit, then implement durable large-PDF page chunking; a successful workflow does not prove every source is fully processed. No original textbook text or images committed.
