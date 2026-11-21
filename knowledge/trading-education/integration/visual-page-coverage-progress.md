# PDF page-level visual coverage (not semantic verification)

- PDF files with tracked visual audit: 32
- Page coverage complete: 10
- Windows attempted this run: 6
- Repeated failures cooling down for automatic retry: 0
- Page coverage finished but OCR incomplete: 2
- Chart semantics independently verified: 0 (not performed by this scanner)
- Source page hashes and positions only; no copyrighted pages or OCR excerpts.

## 2026-11-21 text provenance correction
- Previously `ocr_success=true` could mean merely that a PDF already contained embedded selectable text; it did **not** prove OCR was performed.
- New page evidence records `text_origin` (`embedded_pdf_text`, `ocr_unverified`, `none`, or `legacy_unknown`) and `ocr_performed`; existing historical evidence remains explicitly unknown, not retroactively certified.
- `ocr_success` remains for backward compatibility and must be read as **text availability**, not independent OCR verification.
- Synthetic regression `test_text_origin_evidence.py` is wired into main CI; a successful CI run is required before claiming regression passed.
- Outstanding: full private PDF text/OCR page-window persistence and actual independent chart/claim verification. No textbook excerpts/images are published.
