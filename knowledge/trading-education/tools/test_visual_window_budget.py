#!/usr/bin/env python3
"""Static regression for the real scanner's bounded OCR window configuration.

This checks scheduling arithmetic, not live OCR quality or textbook coverage.
"""
from pathlib import Path
src=(Path(__file__).parent/'resume_visual_pages.py').read_text()
assert "ocr_timeout=max(1,min(120,int(os.environ.get('TMM_OCR_PAGE_TIMEOUT_SECONDS','12'))))" in src
assert "safe_pages=max(1,55//ocr_timeout)" in src
assert "min(safe_pages,adaptive_window_pages(" in src
for timeout, expected in [(1,55),(4,13),(12,4),(20,2),(55,1),(120,1)]:
    actual=max(1,55//timeout)
    assert actual==expected,(timeout,actual,expected)
    assert min(12,actual)*timeout<=max(55,timeout)
print('PASS: bounded OCR window arithmetic and scanner wiring (synthetic only)')
