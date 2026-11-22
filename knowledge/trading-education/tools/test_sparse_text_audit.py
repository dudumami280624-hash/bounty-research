#!/usr/bin/env python3
"""Synthetic regression for page-audit sparse text; no real OCR verification."""
import ast
from pathlib import Path
source=Path(__file__).with_name('run_extraction_batch.py').read_text(encoding='utf-8')
ast.parse(source)
assert "meaningful_chars=len(re.sub(r'\\s+', '', raw))" in source
assert "needs_ocr=meaningful_chars<80" in source
assert "'embedded_meaningful_chars':meaningful_chars" in source
assert "'ocr_needed':needs_ocr" in source
assert "'verified':False" in source
print('PASS: sparse embedded text marked OCR-needed; metadata remains unverified')
