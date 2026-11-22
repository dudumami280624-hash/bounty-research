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
print('PASS: legacy naive UTC retry deadlines and eligible-page rotation (synthetic)')
