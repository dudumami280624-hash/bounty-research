# 2026-11-22 08:54 ICT — CI blocker and repair

- Failing real GitHub Actions runs: 44968867623 and 44972697057, both failed in `Verify sparse PDF text audit flags OCR-needed pages`. The latter job log reports `AssertionError` in `test_sparse_text_audit.py`, line 7.
- Root cause confirmed in the production source: `advance_pdf_text_windows` used the regex literal with **two** backslashes before `s`, which matches a literal backslash followed by s, not whitespace. As a result, whitespace-heavy PDF pages could be misclassified as having enough meaningful text.
- Repair: research commit `3174a4495a80ad0d53e02da9b8c33d3fc573537a` uses the correct `r'\\s+'` regex (one backslash in Python source). Research commit `43174aab881baa33ad1550955040360ff523f53f` replaces brittle source-string matching with execution of the actual production AST expression on synthetic whitespace/threshold fixtures.
- Main workflow trigger commit: `2cb7c1a3c169361cd75a4256a53470c5cb1d66a6`. Inspect the resulting run and its job logs before claiming validation.
- Last published counts before new run: 126/178 extraction-status records; 51 partial OCR; 10 PDF text audits / 189 audited pages / 5 fully traversed / 68 OCR-needed page markers; 13 visual page audits complete. No new source extraction or independent chart/fact verification confirmed in this repair.
- **Next run first:** verify latest CI test and actual PDF page-audit progress; if successful, prioritize durable, private, non-public OCR text storage and complete first-26 source audits. Do not treat metadata-only audits, synthetic tests, or OCR as independent verification.
- Copyright safety: do not publish source PDF pages, original images, or extracted/OCR full text. No paid APIs, X or YouTube publication.
