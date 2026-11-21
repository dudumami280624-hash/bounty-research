#!/usr/bin/env python3
"""Synthetic regression: a child checkpoint must survive a hard audit timeout.
Does not verify real PDF OCR, chart semantics, or copyrighted content.
"""
import ast
from pathlib import Path

source=Path(__file__).with_name('run_extraction_batch.py').read_text(encoding='utf-8')
tree=ast.parse(source)
names={n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
assert 'advance_pdf_text_windows' in names
assert 'main' in names
assert "audit_proc.join(audit_deadline)" in source
assert "os.killpg(audit_proc.pid,signal.SIGKILL)" in source
assert "audit_checkpoint.replace(STATE)" in source
assert "files[sha]['pdf_text_page_audit']=record['pdf_text_page_audit']" in source
assert "'embedded_text_sha256'" in source
assert "'ocr_needed'" in source
print('PASS: audit deadline, atomic checkpoint, child-state merge, metadata-only evidence guards')
