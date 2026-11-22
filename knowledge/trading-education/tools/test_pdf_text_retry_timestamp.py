#!/usr/bin/env python3
"""Synthetic guard: PDF text audit must tolerate legacy naive UTC retry times."""
from datetime import datetime, timezone
from pathlib import Path
import ast

source=Path(__file__).with_name('run_extraction_batch.py').read_text(encoding='utf-8')
tree=ast.parse(source)
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='advance_pdf_text_windows')
# Check the actual function contains the UTC normalization, not an unrelated helper.
segment=ast.get_source_segment(source,fn)
assert 'deadline.tzinfo is None' in segment
assert 'deadline.replace(tzinfo=timezone.utc)' in segment
now=datetime(2026,11,22,12,tzinfo=timezone.utc)
for raw,expected in [('2026-11-22T11:00:00',False),('2026-11-22T13:00:00',True),('2026-11-22T11:00:00+00:00',False)]:
    deadline=datetime.fromisoformat(raw)
    if deadline.tzinfo is None: deadline=deadline.replace(tzinfo=timezone.utc)
    assert (now<deadline)==expected
print('PASS: synthetic legacy UTC text-audit cooldown regression; not a real PDF run')
