# The Market Mind — engineering blockers (metadata only)

## 2026-11-21: hard PDF/OCR extraction hang

- Evidence: Actions run 44863231422, job 136721082930, step "Extract next indexed source" timed out after 15 minutes.
- The last BEGIN without matching END was `《金融炼金术》乔治·索罗斯.pdf` (Git blob `5726836b66f424f3c8e90f80486d871b9f53cdf7`). Four preceding sources finished, but the job-level timeout prevented a normal batch report.
- Root cause hypothesis: Python SIGALRM is not a reliable hard deadline for native PDF parsing / OCR subprocesses. This is an observed hang, not proof of the exact blocking library.
- Fix: run each source in an isolated process group and terminate the group after the configured 90 seconds; checkpoint completed sources individually. Synthetic regression checks hard deadline and success path, **not** real textbook OCR or semantic verification.
- Verification pending: obtain a new Actions run ID, inspect the new hard-timeout test and extraction logs, confirm the problematic PDF becomes a recorded failed attempt within 90 seconds and subsequent sources progress.
- If the source still stalls, instrument separate download / parse / OCR phase timings and inspect process exit statuses. Avoid committing copyrighted source text/images.
- Last confirmed extraction report: 89/178 extracted, 5 partial OCR, 1 needs visual review, 0 independently fact checked, 0 chart-semantic verified, 0 integrated lessons.
