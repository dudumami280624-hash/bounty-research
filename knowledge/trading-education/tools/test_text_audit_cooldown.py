#!/usr/bin/env python3
"""Static regression for audit failure cooldown, not real OCR verification."""
import ast
from pathlib import Path
s=Path(__file__).with_name('run_extraction_batch.py').read_text(encoding='utf-8')
ast.parse(s)
assert "retry_after=audit.get('retry_after_utc')" in s
assert "datetime.now(timezone.utc)<datetime.fromisoformat(retry_after)" in s
assert "audit['retry_after_utc']=(datetime.now(timezone.utc)+timedelta(hours=6)).isoformat()" in s
assert "audit.pop('retry_after_utc',None)" in s
print('PASS: audit cooldown guards and syntax')
