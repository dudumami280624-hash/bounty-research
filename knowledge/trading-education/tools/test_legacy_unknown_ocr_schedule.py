#!/usr/bin/env python3
"""Scheduling regression only; no textbook OCR or semantic verification."""
from resume_visual_pages import interleave_visual_work

def entry(sha, name):
    return {'sha':sha,'name':name,'category':'01-candlestick'}

entries=[entry('legacy','legacy.pdf'),entry('fresh','fresh.pdf')]
files={
    'legacy': {'visual_page_audit': {'coverage_complete':True,'scanner_revision':2,
        'ocr_failures_without_page_locations':True,'ocr_failed_pages_total':1,'next_page':10,
        'ocr_failed_page_numbers':[]}},
    'fresh': {'visual_page_audit': {'coverage_complete':False,'scanner_revision':2,'next_page':2}},
}
order=[x['sha'] for x in interleave_visual_work(entries,files)]
# A legacy unknown-page flag without a positive failure count is not enough
# to force a full re-audit; model the actual persisted legacy failure state.
assert 'legacy' in order and 'fresh' in order, order
files['legacy']['visual_page_audit']['legacy_reaudit_started']=True
files['legacy']['visual_page_audit']['coverage_complete']=False
assert 'legacy' in [x['sha'] for x in interleave_visual_work(entries,files)]
print('PASS: legacy OCR failures lacking page locators receive a real re-audit scheduling slot (synthetic)')
