#!/usr/bin/env python3
"""Deterministic scheduler regression, not real OCR or semantic verification."""
import ast
from pathlib import Path
src=Path(__file__).with_name('resume_visual_pages.py').read_text(encoding='utf-8')
tree=ast.parse(src)
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='visual_priority')
ns={}
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<visual_priority>','exec'),ns)
priority=ns['visual_priority']
entries=[{'sha':str(i),'name':f'{i}.pdf','category':'01-price-action'} for i in range(3)]
files={str(i):{'visual_page_audit':{'next_page':12,'coverage_complete':False,'last_advanced_utc':''}} for i in range(3)}
served=[]
for _ in range(3):
    e=min(entries,key=lambda e:priority(e,files))
    served.append(e['sha'])
    files[e['sha']]['visual_page_audit']['last_advanced_utc']=f'2026-11-22T0{len(served)}:00:00+00:00'
assert len(set(served))==3,served
outside={'sha':'other','name':'other.pdf','category':'02-other'}
files['other']={'visual_page_audit':{'next_page':0,'coverage_complete':False,'last_advanced_utc':''}}
assert priority(entries[0],files)<priority(outside,files)
assert "checkpoint.replace(STATE)" in src
print('PASS: three consecutive windows rotate all three priority PDFs; priority category preserved; atomic checkpoint guard')
