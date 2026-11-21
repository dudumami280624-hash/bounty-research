#!/usr/bin/env python3
"""Synthetic retry scheduling regression; does not verify textbook OCR."""
from datetime import datetime, timezone, timedelta
from resume_visual_pages import next_retry_page

now=datetime(2026,11,21,8,0,tzinfo=timezone.utc)
cooldowns={"2":(now+timedelta(hours=6)).isoformat(),"4":(now-timedelta(seconds=1)).isoformat()}
assert next_retry_page([2,4,7],cooldowns,now)==4
assert next_retry_page([2,7],cooldowns,now)==7
assert next_retry_page([2],cooldowns,now) is None
assert next_retry_page([2],cooldowns,now+timedelta(hours=7))==2
assert next_retry_page([2,4],{"2":"invalid"},now)==2
print("PASS: failed PDF OCR pages independently rotate across cooldowns (synthetic)")
