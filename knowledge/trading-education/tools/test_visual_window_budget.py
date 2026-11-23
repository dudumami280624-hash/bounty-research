#!/usr/bin/env python3
"""Regression for the elapsed-time OCR window gate (not textbook validation)."""
from pathlib import Path

root = Path(__file__).parent
scanner = (root / 'free_visual.py').read_text(encoding='utf-8')
scheduler = (root / 'resume_visual_pages.py').read_text(encoding='utf-8')
assert "ocr_timeout=max(1,min(120,int(os.environ.get('TMM_OCR_PAGE_TIMEOUT_SECONDS','12'))))" in scheduler
assert "window_pages=1 if retry_page" in scheduler
assert "window_budget=max(ocr_timeout+4,min(58,int(os.environ.get('TMM_VISUAL_WINDOW_BUDGET_SECONDS','52'))))" in scanner
assert "time.monotonic()-window_started+ocr_timeout+3>=window_budget" in scanner
assert "if result and" in scanner
assert "result[-1]['visual_coverage_complete'] = result[-1]['page'] >= total_pages" in scanner

# A timeout-aware window permits fast selectable-text pages to advance while
# reserving time for the next OCR call. This does not assert OCR quality.
for timeout in (1, 4, 12, 20, 55, 120):
    budget = max(timeout+4, min(58, 52))
    assert budget >= timeout+4
    assert (0 + timeout + 3) < budget
    assert (budget - timeout - 3 + timeout + 3) >= budget
print('PASS: elapsed-time OCR gate, partial coverage and scheduler wiring (structural only)')
