# The Market Mind — cross-session execution rules

Updated: 2026-11-22. This is a project handoff document, not a claim that any task ran.

## User authorization and priorities
- Work proactively on the authorized GitHub repository `dudumami280624-hash/bounty-research`.
- Research branch: `memory/the-market-mind-daily`; workflow changes on `main` in `.github/workflows/the-market-mind-extraction.yml`.
- 178 source materials; prioritize the first 26 candlestick/price-action sources, then remaining 152.
- Aim for usable, original, evidence-grounded English lessons in beginner → intermediate → advanced order.
- User wants **real progress every hour**, not an hourly repeat of the same blocker or an hourly status-only report.

## Non-blocking execution loop
1. Inspect current GitHub state, latest real Actions runs/logs, extraction state, catalog, and outstanding queues.
2. Select a concrete, feasible improvement; actually implement it, run available tests, and commit to the appropriate branch.
3. If blocked, identify the exact failing step, try a reasonable free alternative, preserve checkpoints, and move to another independent workstream in the same cycle. Never let one PDF, OCR page, API, or CI failure stall all 178 sources.
4. Rotate among source extraction, legacy Office conversion, PDF OCR/page coverage, candlestick chart observations, provenance and cross-source disagreement review, and original lesson preparation.
5. Return to deferred blockers in subsequent cycles using saved failure evidence, not by restarting completed work.
6. Each report must distinguish: actual change, commit SHA, real CI run ID/result if available, measured source/page/chart/lesson progress, unresolved blocker, and next action. Explicitly say when CI has not been confirmed.
7. Avoid asking the user to approve routine, already-authorized repository maintenance or trivial next steps. Do not confuse more tests/commits with completed教材.

## Accuracy, cost, copyright, publication
- Free/open-source methods first; do not require paid APIs or assume keys.
- Never treat OCR text, keyword hits, synthetic fixtures, or AI chart descriptions as independent fact verification.
- Keep exact source IDs, page locators, uncertainty, contradiction status, and review evidence. Separate extraction completeness from visual interpretation and factual validation.
- Do not commit copyrighted textbook passages or chart screenshots publicly. Use hashes and metadata; original public examples must be independently sourced/licensed.
- Do not publish to X/YouTube or other public channels without separate explicit user permission.
- Chinese for user reports; natural American English for public lesson drafts.

## Known verified state at handoff
- 2026-11-22: catalog `integration/research-catalog.json` contained 10 topics, 640 topic-to-source entries, and `verified_claims: 0`; these counts are not completion percentages.
- Historical extraction-status report: 126/178 had text-extraction status records, not full text verification. Recheck before citing as current.
- Prior successful GitHub Actions run: `44982683219`; do not claim this validates later workflow changes.
- Offline provenance audit `tools/audit_provenance.py` and synthetic regression `tools/test_audit_provenance.py` were added; latest workflow changes require independent real-run confirmation.
- User specifically instructed: **每小时都有进展，不是每小时卡死在同一个问题上**.

## 2026-11-22 hourly execution handoff — visual scheduler fairness
- Actual fix: `tools/resume_visual_pages.py` now interleaves two unfinished PDF page-audit windows with one completed-PDF due OCR retry inside each inventory tier, instead of sorting all due retries before every unfinished source. This prevents a large due-retry backlog from monopolizing a bounded hourly window while still servicing retries.
- Research commits: `6e9027316aae33df19df0f73f40ef734e53f8c20` (scheduler), `7cdca891f11d6c37a7a2687e4fe44ba4f1ed5ea6` (synthetic regression).
- Main workflow commit: `fe497d994ec25896eb0bc0f545cfcf5a917f8929` adds `test_visual_interleave.py`. A push to main should trigger CI, but the connector's commit-to-run endpoint only exposes PR-triggered runs and returned `workflow_runs: []`; public GitHub API URL was inaccessible through web. **New run ID/result not verified.** Previous known run `44982683219` succeeded, but predates this change.
- Latest report observed: 126/178 extraction-status records; 31 PDFs with page-text metadata (459 pages), 175 pages flagged for OCR; 16 of those 31 PDF text audits incomplete. Separate visual coverage report: 127 PDFs tracked, 38 visual audits coverage-complete, 352 OCR-success page evidence, 333 embedded-text page evidence. These metrics measure different stages and must not be added together or called factual/semantic verification.
- Next run: verify new workflow step and actual run outcome; if failed, inspect job log and repair. Then advance the 175 page-level OCR queue and 26 priority sources. If no run ID available, keep doing independent code/research work and record exact verification gap; do not block on CI lookup.

## 2026-11-22 19:54 Asia/Phnom_Penh — PDF text-audit legacy cooldown repair
- Actual defect: `advance_pdf_text_windows()` in `tools/run_extraction_batch.py` compared aware `datetime.now(timezone.utc)` with potentially naive `datetime.fromisoformat(retry_after)`. Historical naive checkpoint timestamps can raise `TypeError` and interrupt the whole extraction batch instead of skipping/retrying one PDF.
- Research fix commit `ea7067236d5ba2a36de0f8179d9e1a2a4c8f5f2c`: interpret legacy naive retry timestamps as UTC before comparison. Regression commit `2c0a9de6b4b52a847d1bfc2e883e24c4eeb12f78`: synthetic/AST guard only, **not** a real PDF extraction test.
- Main workflow commit `d2c79f76640d20f743e60f126b0f7fce4ccd9754` adds the test. Commit-to-run lookup returned `workflow_runs: []` because the connector exposes PR-triggered runs only; **no new run ID/result confirmed**. Historical run `44982683219` had completed-success extract job, but predates this fix.
- Observed latest metadata: 126/178 extraction-status records; 33 PDF text audits with 483 page metadata, 187 pages marked OCR-needed, 15 PDF text-audit coverage-complete. Separate visual scanner: 127 tracked PDF audits, 38 page-coverage-complete, 364 actual OCR-success page evidence, 429 embedded-text page evidence, zero independent chart-semantic checks. These categories overlap or represent different stages; do not add them.
- Next cycle: verify CI from a newly discoverable run ID or Actions page; if unavailable, continue actual page/OCR progress and inspect the text-audit cooldown and worker timeout path. Do not claim synthetic tests validate live OCR or factual correctness.

## 2026-11-22 20:56 Asia/Phnom_Penh — legacy OCR page-ID repair
- Defect: persisted `ocr_failed_page_numbers` may contain string page locators such as `"2"`. `next_retry_page()` previously returned the string unchanged; the real visual scanner then computed `retry_page-1`, raising `TypeError`. A repeated failed retry could strand the page indefinitely. Invalid zero/negative/nonnumeric locators also needed filtering.
- Fix commits on research branch: `ee0daf53c062076af270a1850f2b9781cc99f09b` normalizes page IDs to positive integers; `18e14447f3e0f18dfcfaea4010139b9c9fd26f32` normalizes the stored failed-page set before reconciling newly scanned numeric pages; `3f991dfdfd6aafe4974caffc3cef0799ec8921fa` adds synthetic cases for string and invalid IDs.
- Main workflow commit `14946f872c3a26e57c3c61bb3e1d1dcdb3ef9656` updates the existing test step comment and triggers push workflow. Commit-to-run connector returned `workflow_runs: []`; it filters PR runs and cannot prove push run status. Latest independently retrieved historical run `44982683219` succeeded but predates all new commits. **New run ID and CI result remain unverified.**
- Latest `latest-extraction-report.md`: 126/178 have extraction-status records; 33 PDFs / 483 pages have text-audit metadata; 187 pages flagged OCR-needed; 15 PDFs text-coverage-complete; 51 OCR-incomplete source statuses; zero chart semantic and independent fact verification. No additional real textbook processing was verified during this repair.
- Next: inspect real workflow execution and page evidence; if CI fails, fix exact failing step. Continue priority-26 PDFs, OCR, and independent source review without waiting on inaccessible run lookup.
