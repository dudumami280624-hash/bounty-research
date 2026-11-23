#!/usr/bin/env python3
"""Synthetic regression for malformed persisted page locators; not real OCR."""
from datetime import datetime, timezone
from resume_visual_pages import next_retry_page, bounded_failed_pages

now=datetime.now(timezone.utc)
assert next_retry_page(['999', '2'], {}, now, 4)==2
assert next_retry_page(['999'], {}, now, 4) is None
assert next_retry_page(['3'], {}, now, 3)==3
assert next_retry_page(['2'], {}, now, None)==2
print('PASS: out-of-range OCR page IDs are ignored without blocking valid retries')

assert bounded_failed_pages(['999', '2', 3, '0', '-1', 'bad', None, True], 4)=={2,3}
assert bounded_failed_pages(['999'], 4)==set()
print('PASS: persisted OCR failures are bounded to actual document pages')
