# Engineering checkpoint — 2026-11-21 12:52 Asia/Phnom_Penh

## Verified state
- Inventory: 178; first 26 candlestick/price-action sources all have extraction_status=extracted (text only, not visual semantics).
- Source extraction state: 99 extracted, 6 partial_ocr_failure, 1 needs_visual_review, 1 failed; 71 not yet recorded. This is the snapshot read before the next CI run.
- Failed source: 《金融炼金术》乔治·索罗斯.pdf, attempt 1, hard worker timeout after 90 seconds. Source is NOT successfully extracted.
- Last inspected run 44863231422: extraction step failed, later visual-audit and metadata-commit steps succeeded. This run predates isolated hard-timeout fix.
- The legacy OCR audit field ocr_failures_without_page_locations is currently present in 0 tracked records; the code fix handles historical/next migration cases rather than claiming a real source recovered.

## This checkpoint's change
- Research commit 5591a47724f493d19699aaa6cf88c7a4e91911e2: a completed historical page audit with unresolved OCR failures but no page numbers now rewinds to page 1, and only clears the unknown-location flag after all pages are re-audited. Page coverage alone never counts as semantic or factual verification.
- Main workflow commit 49a0f9e46f7ea2483b33404a9e2099be30bcd1ac adds Python syntax check and triggers the extraction workflow.
- CI run ID for this new commit was not returned by the connector: commit workflow-run lookup returned an empty list (endpoint filters PR-triggered runs). Do not claim new CI success.

## Next action
1. Retrieve the new workflow run from the GitHub Actions UI/API, inspect syntax step and extraction step logs.
2. If source timeout persists, split PDF extraction/OCR into independently checkpointed page ranges rather than retrying whole book. Preserve page locations, source hashes and incomplete flags.
3. Continue the remaining 71 unrecorded sources; run OCR page-specific retries for 6 partial cases.
4. Establish independent chart semantic analysis and external evidence verification, neither of which has been completed. Never publish copyrighted original pages/text or claim OCR is fact checking.
