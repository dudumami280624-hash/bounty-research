#!/usr/bin/env python3
"""Synthetic scheduling test only; does not validate real OCR or source facts."""
from datetime import datetime, timezone, timedelta
from resume_visual_pages import next_retry_page, update_page_retry_cooldowns

now=datetime(2026,11,21,15,0,tzinfo=timezone.utc)
audit={}
observations=[{'page':1},{'page':2},{'page':3}]
update_page_retry_cooldowns(audit,observations,{1,3},now)
cooldowns=audit['ocr_page_retry_after_utc']
assert set(cooldowns)=={'1','3'},cooldowns
assert next_retry_page([1,3],cooldowns,now) is None
assert next_retry_page([1,3],cooldowns,now+timedelta(hours=6,seconds=1))==1
update_page_retry_cooldowns(audit,[{'page':1}],{3},now+timedelta(hours=7))
assert '1' not in cooldowns and '3' in cooldowns
assert next_retry_page([3],cooldowns,now+timedelta(hours=7))==3
print('PASS synthetic first-pass per-page OCR retry cooldown and clearing')
