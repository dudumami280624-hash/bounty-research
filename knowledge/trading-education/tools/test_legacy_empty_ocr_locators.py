#!/usr/bin/env python3
"""Scheduler regression only: not proof of real OCR or chart interpretation."""
from resume_visual_pages import interleave_visual_work, needs_legacy_reaudit

legacy={'coverage_complete':True,'scanner_revision':2,
        'ocr_failed_pages_total':3,'ocr_failed_page_numbers':[],
        'ocr_failures_without_page_locations':True}
assert needs_legacy_reaudit(legacy)
entries=[{'sha':'legacy','name':'old.pdf','category':'01-candles'}]
files={'legacy':{'visual_page_audit':legacy}}
assert [e['sha'] for e in interleave_visual_work(entries,files)]==['legacy']
assert not needs_legacy_reaudit({**legacy,'legacy_reaudit_started':True})
assert not needs_legacy_reaudit({**legacy,'ocr_failed_pages_total':0})
assert not needs_legacy_reaudit({**legacy,'ocr_failures_without_page_locations':False})
print('PASS: legacy empty OCR locator arrays reenter bounded audit queue')
