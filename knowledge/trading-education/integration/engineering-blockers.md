# The Market Mind — engineering blockers (metadata only)

## 2026-11-21: hard PDF/OCR extraction hang

- Evidence: Actions run 44863231422, job 136721082930, step "Extract next indexed source" timed out after 15 minutes.
- The last BEGIN without matching END was `《金融炼金术》乔治·索罗斯.pdf` (Git blob `5726836b66f424f3c8e90f80486d871b9f53cdf7`). Four preceding sources finished, but the job-level timeout prevented a normal batch report.
- Root cause hypothesis: Python SIGALRM is not a reliable hard deadline for native PDF parsing / OCR subprocesses. This is an observed hang, not proof of the exact blocking library.
- Fix: run each source in an isolated process group and terminate the group after the configured 90 seconds; checkpoint completed sources individually. Synthetic regression checks hard deadline and success path, **not** real textbook OCR or semantic verification.
- Verification pending: obtain a new Actions run ID, inspect the new hard-timeout test and extraction logs, confirm the problematic PDF becomes a recorded failed attempt within 90 seconds and subsequent sources progress.
- If the source still stalls, instrument separate download / parse / OCR phase timings and inspect process exit statuses. Avoid committing copyrighted source text/images.
- Last confirmed extraction report: 89/178 extracted, 5 partial OCR, 1 needs visual review, 0 independently fact checked, 0 chart-semantic verified, 0 integrated lessons.

## 2026-11-21 — First-pass OCR retry scheduling
- Found: first-pass failed OCR pages were recorded but lacked per-page six-hour retry deadlines; completed-coverage books could repeatedly reattempt the same failed page ahead of other pending work.
- Fixed: resume_visual_pages.py now assigns individual cooldowns for every failed observation, and clears only the corresponding page after successful recognition. Research commits a708e6a, ccc34d4; synthetic regression f7ea3e4; main CI workflow 2ad2fdc.
- Real CI: 44921935959 queued when checked; previous run 44920462245 succeeded, but predates this fix. Do not treat the synthetic test as OCR quality validation.
- Last confirmed progress: 126/178 text-extracted, 51 partial OCR, 1 visual review; 32 PDF audits, 11 page-coverage complete; zero semantic/fact/lesson verification.
- Next blocker: page-level OCR text is transient and cannot be combined into a complete cross-run private text extraction. Design secure/private checkpointing and provenance-preserving partial extraction without publishing copyrighted textbook text or figures. First verify 44921935959 and fix failures.
