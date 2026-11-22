#!/usr/bin/env python3
"""Static regression for PDF text-audit failure cooldown; not real OCR."""
import ast
from pathlib import Path

source = Path(__file__).with_name('run_extraction_batch.py').read_text(encoding='utf-8')
tree = ast.parse(source)
assert "retry_after=audit.get('retry_after_utc')" in source
assert "deadline=datetime.fromisoformat(retry_after)" in source
assert "if deadline.tzinfo is None:" in source
assert "deadline=deadline.replace(tzinfo=timezone.utc)" in source
assert "if datetime.now(timezone.utc)<deadline:" in source
assert "audit['retry_after_utc']=(datetime.now(timezone.utc)+timedelta(hours=6)).isoformat()" in source
assert "audit.pop('retry_after_utc',None)" in source
print('PASS: audit cooldown UTC normalization guards and syntax')
