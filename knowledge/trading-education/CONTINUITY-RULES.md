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

## 2026-11-22 21:54 Asia/Phnom_Penh — OCR window deadline mitigation
- Found concrete deterministic throughput risk: default visual window 12 pages * 12 seconds per-page OCR timeout = up to 144 seconds of OCR alone, while the scanner has a 65-second SIGALRM deadline. This can repeatedly abort before saving any page-level evidence.
- Research fix commit `884924b91cd5af8d64eb16df37a4af01575ebcf8`: bound window size by floor(55 / OCR page timeout), leaving ~10 seconds for rendering/metadata; default 12-second OCR now processes at most four pages per window. This is a conservative heuristic, not a guaranteed deadline for pathological rendering or downloads.
- Research synthetic wiring/arithmetic test commit `49bf06f50e55d44ac1ff4976314d98ec1ab8cd7c`. Main workflow commit `9672af18d1c465bc2b1a70ce2edd7a622522bbfb` adds the test and triggers push CI.
- Commit-run connector returned `workflow_runs: []`; its endpoint filters PR-triggered runs, so no new push run ID/result is verified. Historical run `44982683219` completed successfully but predates this fix.
- Latest actual report: 126/178 extraction-status records; 33 PDF text audits, 483 page metadata, 187 OCR-needed pages, 15 text-coverage-complete; zero independent semantic chart or fact verification. No new source completion verified this cycle.
- Next: inspect real post-commit Actions run/logs by run ID when available; measure whether bounded visual windows advance more page checkpoints, then address remaining OCR pages. If renderer itself exceeds the reserved 10 seconds, further adapt the budget based on measured per-page elapsed time. Do not claim synthetic tests prove live OCR success.

## 2026-11-22 22:55 Asia/Phnom_Penh — real OCR integration smoke
- Main unresolved verification gap: previous CI checks mostly used synthetic guards; no end-to-end installed Tesseract execution on an image-only PDF was enforced.
- Research commit `1ba89dadcb957ff0ea52bdbd9bcd0fbee1a65d18`: added `tools/test_real_ocr_smoke.py`, which rasterizes original large text into an image-only PDF, checks there is no embedded text, and calls the production `free_visual.inspect_pdf()` with installed Tesseract. It asserts OCR actually ran, returned nonempty text and SHA, and did not claim semantic verification.
- Main workflow commit `0d281d8520b71abafbe511a2e5f2e6f808659e71` runs this integration smoke after installing Tesseract and PyMuPDF. Push should trigger workflow; **run ID/result not yet independently confirmed**: connector `fetch_commit_workflow_runs` returned `workflow_runs: []` (PR-filtered). Historical run `44982683219` remains completed/success but predates this addition.
- Independent local live Tesseract check in current environment: PyMuPDF rasterized a text-only source into a new image-only PDF; embedded text was empty; actual `tesseract -l eng` returned exit code 0 and recognized `MARKET PRICE ACTION / OPEN HIGH LOW CLOSE`. This validates a free OCR executable path on a synthetic document, **not** the new repository test execution in CI, nor real textbook accuracy.
- Latest GitHub report read this cycle: 126/178 source extraction-status records; 33 PDFs / 483 page text metadata; 187 pages flagged OCR-needed; 15 PDF text audits complete; 51 incomplete OCR statuses; 0 independent chart semantics, facts, or course fusion.
- Next cycle: get actual GitHub Actions run/job result for main commit, fix any integration smoke failure. Then move actual 187-page OCR queue forward; keep priority 26 ahead of remaining 152. Do not get stuck on missing run lookup.

## 2026-11-22 23:56 Asia/Phnom_Penh — exhausted-source retry legacy UTC fix
- Inspected current main workflow and research branch extraction source, latest report, and real OCR smoke script.
- Actual bug: `main().eligible()` in `tools/run_extraction_batch.py` compared aware UTC `now` against legacy naive `last_attempt_utc`; `TypeError` is not caught, potentially aborting the entire extraction batch if an exhausted failed record exists. Fixed by interpreting legacy naive stamps as UTC.
- Research commit `d6bd5d005dfafd3533d5ede19b6eb7e6b3620825`; production-closure regression test `ca99d99196bb38a429347bedff97e8ad17602ee8`. This test executes the actual extracted eligibility function with mocked state, not real OCR or source extraction.
- Main workflow commit `5810bdf558236448a896abf35b2da39c70bb2797` adds the test and meets push path trigger conditions.
- CI lookup for this commit: `fetch_commit_workflow_runs` returned `workflow_runs: []` (connector is PR-run-filtered), combined commit statuses `[]`. **No run ID or successful CI conclusion verified.** Must verify actual Actions execution via a full run-list capability when available.
- Current latest extraction report: 126/178 text-extraction status records; 33 PDFs/483 page text metadata; 15 text-audit complete; 187 OCR-needed page flags; 51 partial OCR; 0 chart semantics, 0 independently fact checked, 0 fused courses. This cycle did not increase source coverage.
- Next: verify CI test actually runs, then prioritize page-level OCR progress and real source throughput; avoid further synthetic-only work if real OCR remains bottleneck.


## 2026-11-23 00:54 Asia/Phnom_Penh — exhausted retry metadata recovery
- Inspected current main workflow, production extraction and visual scanner, live OCR smoke script, latest report, and cross-session rules.
- Found a permanent-stall edge case in `run_extraction_batch.py`: exhausted `failed` records with missing or malformed `last_attempt_utc` returned `False` from `eligible()` forever, even after the six-hour retry period. This could strand a source with corrupt legacy metadata indefinitely. It is a preventative repair: the latest report has **0 failed sources**, so no current textbook completion increase is attributable to it.
- Research production fix commit `7ddf9e8c8c96bcebebfb668d52e60de3707c147e`: malformed/missing retry timestamps now permit a bounded retry, which writes a fresh valid timestamp. Existing valid timestamps retain six-hour cooldown. Research regression update `fa52ac1254186581d44eed21a554644dff5c875d` executes the actual extracted production eligibility function and tests malformed and missing fields (synthetic state, not OCR).
- Main workflow commit `4709f24b63a861a493320a8030f8bedecff3d9ef` touches the workflow push trigger and documents the new regression cases. **CI run ID and result not verified**: GitHub connector's commit-run lookup filters to PR runs; direct Actions URL failed with `DisabledError`. Do not infer success.
- Latest source report: 126/178 extracted status, 51 partial OCR, 1 needs visual review, 0 failed, 0 conversion; all 178 have status categories but none is independently fact-verified. PDF text audits 33 PDFs/483 page metadata, 187 OCR-needed flags, 15 text-audit coverage-complete. These are stage-specific metrics.
- Next run: first seek an accessible full Actions run listing/log for main commit `4709f24b`, repair any failing test; independently progress the **real OCR page queue**, especially first-26 candlestick sources. Avoid spending another cycle solely on retry guards. Do not claim regression fixture is textbook OCR.

## 2026-11-23 — Horizon offline grouping integration
- User explicitly authorized adapting Thysrael/Horizon, emphasizing tool usefulness depends on application. Read upstream README: profiles, ranking, grouped deduplication, RSS/financial sources, optional model-backed analysis. Do not require paid API.
- Added `tools/offline_research_briefing.py` to group repeated catalog source SHA across topics and rank candlestick/confirmation source reviews with traceable page locators; **this is not semantic duplicate detection, OCR completion, chart interpretation, or fact verification**. Research commit `abefce51b36f5430a49c73bcaa1f859b77d9e49d`.
- Main workflow commit `cb99d3ede9563852bd80dbc415b8e7d5f3667f80` invokes it after refreshing catalog; generated `integration/offline-research-briefing.md` is committed with other metadata if the job runs successfully.
- New CI run ID/result not yet verified. Next: verify execution and actual generated briefing; if broken fix immediately. Then use grouped priority queue to work on actual first-26 candlestick OCR/pages, not just tooling.
