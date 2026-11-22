# 2026-11-22 PDF checkpoint regression repair

- Confirmed failed Actions run: 44973660915 (failed step 21, `Verify PDF text checkpoint resumes across CI runs`).
- Root cause: the synthetic checkpoint test inserted only ~25 meaningful characters on its nonblank pages, while production now intentionally labels pages with fewer than 80 meaningful characters `embedded_sparse_unverified`. The legacy test expected `embedded_pdf_text`.
- Fix commits on research branch: `36ed5ec` (substantive synthetic page fixture), `d502ae9` (assert both sparse and substantive cases).
- Workflow trigger on main: `134eff1`. New run ID pending GitHub scheduling at time of note; no claim of passing test.
- Real source extraction: last report 126/178 with text extraction records; 51 partial OCR; 10 PDF text audits / 189 pages / 5 page audits complete / 68 pages flagged OCR; visual page audits 48 tracked, 13 complete; semantic and independent fact checks 0.
- Important: page audits and synthetic regressions are not source OCR completion, factual verification, or chart semantic verification.
- Next run: inspect new Actions job result and logs; if the checkpoint test still fails, reproduce the exact fixture assertion and repair it. Then address durable private OCR text across CI runs without committing copyrighted text or images publicly.
