#!/usr/bin/env python3
"""Synthetic regression: legacy naive UTC retry checkpoints must not stall PDF work."""
from datetime import datetime, timezone, timedelta
from resume_visual_pages import next_retry_page

now=datetime(2026,11,22,10,0,tzinfo=timezone.utc)
assert next_retry_page([1],{'1':'2026-11-22T09:00:00'},now)==1
assert next_retry_page([1],{'1':'2026-11-22T11:00:00'},now) is None
assert next_retry_page([1,2],{'1':'2026-11-22T11:00:00','2':'2026-11-22T09:00:00+00:00'},now)==2
assert next_retry_page([1],{'1':'invalid'},now)==1
assert next_retry_page([1],{},now)==1
# Persisted JSON can contain string page numbers; retry arithmetic requires ints.
assert next_retry_page(['2'], {'2':'2026-11-22T09:00:00'}, now)==2
assert next_retry_page(['0','not-a-page','3'], {'3':'2026-11-22T09:00:00'}, now)==3
assert next_retry_page(['-1','0','bad'], {}, now) is None
assert next_retry_page([True, 4], {'4':'2026-11-22T09:00:00'}, now)==4
# Invalid JSON deadline values must not strand otherwise valid page locators.
for malformed in (None, 123, [], {}, True):
    assert next_retry_page([1], {'1': malformed}, now)==1
# Out-of-range locators must not mask an eligible page in the same document.
assert next_retry_page([99, 2], {}, now, total_pages=3)==2
assert next_retry_page([99], {}, now, total_pages=3) is None
print('PASS: legacy UTC deadlines and numeric/string OCR page retry locators (synthetic)')
