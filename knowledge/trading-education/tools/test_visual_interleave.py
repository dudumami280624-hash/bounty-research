#!/usr/bin/env python3
"""Synthetic scheduler fairness regression; not evidence of real OCR success."""
from datetime import datetime, timezone, timedelta
from resume_visual_pages import interleave_visual_work

past=(datetime.now(timezone.utc)-timedelta(hours=1)).isoformat()
entries=[]
files={}
for i in range(9):
    sha=f'u{i}'
    entries.append({'sha':sha,'name':sha+'.pdf','category':'01-price-action'})
    files[sha]={'visual_page_audit':{'coverage_complete':False,'next_page':i}}
for i in range(9):
    sha=f'r{i}'
    entries.append({'sha':sha,'name':sha+'.pdf','category':'01-price-action'})
    files[sha]={'visual_page_audit':{'coverage_complete':True,'next_page':20,'ocr_failed_page_numbers':[2],'ocr_page_retry_after_utc':{'2':past}}}
entries.append({'sha':'later','name':'later.pdf','category':'02-other'})
files['later']={'visual_page_audit':{'coverage_complete':False}}
order=[e['sha'] for e in interleave_visual_work(entries,files)]
assert len(order)==len(entries) and len(set(order))==len(entries)
assert sum(x.startswith('u') for x in order[:6])==4,order[:6]
assert sum(x.startswith('r') for x in order[:6])==2,order[:6]
assert order[-1]=='later',order
assert any(x.startswith('r') for x in order[:3]),order
assert any(x.startswith('u') for x in order[:3]),order
print('PASS: synthetic visual scheduler interleaves unfinished and due retries')
