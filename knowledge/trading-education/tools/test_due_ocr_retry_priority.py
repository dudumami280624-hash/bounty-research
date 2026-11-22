#!/usr/bin/env python3
"""Synthetic scheduler regression; not real OCR or semantic verification."""
from datetime import datetime, timezone, timedelta
from resume_visual_pages import visual_priority

now=datetime.now(timezone.utc)
future=(now+timedelta(hours=6)).isoformat()
past=(now-timedelta(hours=1)).isoformat()
entries=[{'sha':x,'name':x+'.pdf','category':'01-price-action'} for x in ('due','unfinished','cooling')]
files={
 'due':{'visual_page_audit':{'coverage_complete':True,'next_page':20,'ocr_failed_page_numbers':[3],'ocr_page_retry_after_utc':{'3':past}}},
 'unfinished':{'visual_page_audit':{'coverage_complete':False,'next_page':12}},
 'cooling':{'visual_page_audit':{'coverage_complete':True,'next_page':20,'ocr_failed_page_numbers':[3],'ocr_page_retry_after_utc':{'3':future}}},
}
assert [x['sha'] for x in sorted(entries,key=lambda e:visual_priority(e,files))]==['due','unfinished','cooling']
print('PASS due OCR retry priority; synthetic scheduler only')
