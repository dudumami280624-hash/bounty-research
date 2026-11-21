#!/usr/bin/env python3
"""Synthetic scheduling regression only; not OCR quality or textbook validation."""
from resume_visual_pages import adaptive_window_pages

assert [adaptive_window_pages(12,n) for n in range(6)] == [12,6,3,1,1,1]
assert adaptive_window_pages(1,0)==1
assert adaptive_window_pages(12,-1)==12
assert adaptive_window_pages(12,100)==1
print('adaptive OCR visual window regression passed')
