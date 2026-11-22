# The Market Mind — automation blockers and next actions

> **历史检查点提示（2026-11-22）**：下文的126/178、60份视觉审计及16份覆盖完成等数字是对应时间的历史记录，不能当作实时总进度。请分别查看 [latest-extraction-report.md](latest-extraction-report.md) 和 [visual-page-coverage-progress.md](visual-page-coverage-progress.md) 获取各自最近生成的状态；两份报告统计口径不同，不能互相替代，也都不代表逐页语义审核、图表判断或事实核验完成。

## 2026-11-22 11:50 Asia/Phnom_Penh — checkpoint regression
- Verified failed Actions run: 44982683219, job 137086419986. Failure in test_pdf_text_checkpoint.py line 38: page 1 `ocr_needed` was true despite fixture expectation false. CI did run subsequent visual scan (six windows), generated 10 unverified outlines, and committed page metadata (a63ae02). This is a test failure, not evidence that real OCR or factual validation succeeded.
- Root cause: test fixture passed literal escaped newline sequences to a single `insert_text` call, so long text could be clipped beyond the PDF page. Changed to three separate, in-bounds text draws; locally verified with PyMuPDF that 111 non-whitespace characters are extractable, above the 80-character production gate.
- Research commit: 3971b0b196a823c238d2ca784123b3d12818d68e. Main workflow trigger commit: dc8f7be155b5672bddfd3499bf5c195b47a8a8ad. New CI run ID not yet visible at first query; **must check result first next run**, fix any failing step.
- Current metadata: 126/178 extracted; 51 partial OCR; visual audits 60 PDFs, 16 coverage-complete; text audit 10 PDFs/189 pages, 5 complete, 68 OCR-needed. Independent chart semantics and fact checks remain zero. The source text is not persisted in the public repository.
- Next substantive blocker: recover verified page-level OCR output across runs without publishing copyrighted text or images; prefer private transient artifacts with explicit retention controls or deterministic re-extraction and source SHA checks. Do not equate OCR hashes with factual validation.

## 2026-11-23 03:43 ICT — confirmed current CI checkpoint
- Rechecked real GitHub Actions run [45057886406](https://github.com/dudumami280624-hash/bounty-research/actions/runs/45057886406): attempt 2 is **completed / success**. Earlier attempt failed in the synthetic PDF audit cooldown guard; the research-branch correction was committed as `d7fd4b013a3272d8905c22aa72730e73ddab8ea1`. The detailed failure and rerun evidence is recorded in [ci-blocker-2026-11-22.md](ci-blocker-2026-11-22.md).
- Latest [extraction report](latest-extraction-report.md) still records 126/178 extraction statuses, 35 PDF page-text metadata files / 507 pages, 198 OCR-needed page flags, 51 incomplete OCR sources, and **zero** verified full OCR sources, chart reviews, fact checks or curriculum integrations. This is metadata progress, not page-by-page reading.
- Historical failures and historical `must check next run` instructions above are preserved as dated records; they no longer describe the present CI state. The remaining work is actual OCR/content verification, not this synthetic guard.
