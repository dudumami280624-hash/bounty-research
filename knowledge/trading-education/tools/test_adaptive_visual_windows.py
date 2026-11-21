#!/usr/bin/env python3
"""Synthetic scheduling regression only; not OCR quality or textbook validation."""
from resume_visual_pages import adaptive_window_pages, visual_priority

assert [adaptive_window_pages(12,n) for n in range(6)] == [12,6,3,1,1,1]
assert adaptive_window_pages(1,0)==1
assert adaptive_window_pages(12,-1)==12
assert adaptive_window_pages(12,100)==1
print('adaptive OCR visual window regression passed')

# Synthetic queue regression: started PDFs must not be perpetually displaced by
# newly discovered page-zero PDFs; priority category 01 still comes first.
entries=[
 {'sha':'new','name':'new.pdf','category':'02-rest'},
 {'sha':'started','name':'started.pdf','category':'02-rest'},
 {'sha':'priority','name':'priority.pdf','category':'01-candlestick'},
 {'sha':'done','name':'done.pdf','category':'02-rest'},
]
records={
 'new':{'visual_page_audit':{'next_page':0}},
 'started':{'visual_page_audit':{'next_page':24}},
 'priority':{'visual_page_audit':{'next_page':0}},
 'done':{'visual_page_audit':{'next_page':50,'coverage_complete':True}},
}
assert [e['sha'] for e in sorted(entries,key=lambda e:visual_priority(e,records))]==[
 'priority','started','new','done']
print('visual queue starvation and priority regression passed')
