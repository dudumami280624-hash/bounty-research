# OCR text continuity and evidence — 2026-11-22

## Verified state
- Latest completed GitHub Actions run 44998057812: success.
- Latest extraction report: 126/178 sources with extracted status, 51 partial OCR failures; PDF text audit 13 files / 264 pages, 106 pages flagged for OCR. This is NOT full-text OCR verification.
- Visual audit: 94 PDF files tracked, 25 complete page traversals, 186 recorded actual OCR-success pages, 63 embedded-text pages. Independent semantic verification remains zero.

## Work completed this run
- Research commits c8ae2c0 and 8eca3e6: SHA-256 fingerprint of actual OCR or embedded PDF text at page level; only hash/character counts and source-linked page locators are persisted. No textbook excerpts, images, or raw OCR output in public Git.
- Regression test 5a4d7a1 verifies the embedded-text fingerprint is preserved in metadata, and that embedded text is not misrepresented as actual OCR.
- Main workflow ae7bd635 runs this test. New Actions run 45000264456 queued at last check; not yet accepted.

## Remaining blocker — highest priority next run
- The current scanner discards the full Tesseract output after each window; only hashes/metadata survive between runners. Therefore it cannot yet combine OCR pages into a complete private book transcript. Hashes are evidence, not source text.
- Do NOT place copyrighted OCR output in this public repository or public Actions artifacts. Investigate private storage with explicitly restricted access and retention, or a runner-local end-to-end per-book analysis in one run with only original derived notes/hashes committed. If no secure free storage exists, document exact limitations and implement the runner-local alternative.
- First inspect run 45000264456 for failure; fix any regression before new features. Continue prioritizing 26 price-action sources, then 152 others. Do not claim chart semantics or independent fact checking from OCR.
