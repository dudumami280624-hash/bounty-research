# 2026-11-21 — failed OCR page retry fairness

Observed code defect: `resume_visual_pages.py` always selected `ocr_failed_page_numbers[0]` after full page coverage. A failed OCR page's global six-hour cooldown blocked every other failed page in the same PDF. The first repeatedly failing page could starve later failed pages indefinitely.

Fix on research branch: independent per-page retry cooldowns (`ocr_page_retry_after_utc` keyed by one-based page number), selecting the first eligible page, retaining failures as unresolved. Legacy `ocr_retry_after_utc` remains in older state but is removed when the next retry finishes; page locators are preserved. Synthetic regression `test_ocr_retry_rotation.py` tests rotation, expiry, and malformed cooldowns. No real chart interpretation or factual verification claimed.

Research commits: `9989964557d817de040cc65605b90187d07a820f`, `9559e34f6b55302257df6ee9f1dbd1f4f6b6a516`, `03442461f6a18118087d9b580cb4323057105341`. Main CI trigger: `c37d1d71a8e837e27bc4fe1e2e69aa21585eed97`.

Last confirmed live Actions run before this fix: `44886534254` succeeded (all jobs passed); it cannot validate the new test. Latest extraction report: 117/178 extracted, 38 partial OCR, 1 needs visual review, 0 verified chart semantics, 0 independent fact checks, 0 integrated lessons. Next run FIRST: locate new Actions run for main commit `c37d1d7`, inspect the OCR retry regression step and live audit logs, fix any failure. Then implement durable PDF text page-window continuation for repeatedly slow PDFs; current text extraction remains whole-document and private output is ephemeral. Do not publish source excerpts or charts.
