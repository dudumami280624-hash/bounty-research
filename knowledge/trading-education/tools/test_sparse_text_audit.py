#!/usr/bin/env python3
"""Execute the production PDF sparse-page character-count expression on fixtures.
This is a synthetic regression, not real source OCR or semantic verification.
"""
import ast
import re
from pathlib import Path

source=Path(__file__).with_name('run_extraction_batch.py').read_text(encoding='utf-8')
tree=ast.parse(source)
audit=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='advance_pdf_text_windows')
assignments=[n for n in ast.walk(audit) if isinstance(n,ast.Assign)]
count=next(n.value for n in assignments if any(isinstance(t,ast.Name) and t.id=='meaningful_chars' for t in n.targets))
gate=next(n.value for n in assignments if any(isinstance(t,ast.Name) and t.id=='needs_ocr' for t in n.targets))
def evaluate(raw):
    chars=eval(compile(ast.Expression(count),'<production-character-count>','eval'),{'len':len,'re':re,'raw':raw})
    needed=eval(compile(ast.Expression(gate),'<production-ocr-gate>','eval'),{'meaningful_chars':chars})
    return chars,needed

assert evaluate('12'+' '*500)==(2,True)
assert evaluate('12\n\t'+' '*500)==(2,True)
assert evaluate('X'*79)==(79,True)
assert evaluate('X'*80)==(80,False)
assert evaluate('X '*80)==(80,False)
assert "'embedded_meaningful_chars':meaningful_chars" in source
assert "'ocr_needed':needs_ocr" in source
assert "'verified':False" in source
print('PASS: production sparse PDF page audit gate executes correctly on synthetic inputs; no real OCR claim')
