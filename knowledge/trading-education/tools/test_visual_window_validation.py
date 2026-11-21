#!/usr/bin/env python3
"""Synthetic validation only; does not assert textbook OCR or chart semantics."""
from resume_visual_pages import validate_visual_window

def fails(rows,start):
    try:
        validate_visual_window(rows,start)
    except RuntimeError:
        return
    raise AssertionError('invalid window accepted')

fails([],0)
fails([{'page':1,'document_total_pages':0}],0)
fails([{'page':2,'document_total_pages':3}],0)
fails([{'page':1,'document_total_pages':1},{'page':2,'document_total_pages':1}],0)
fails([{'page':2,'document_total_pages':2}],2)
assert validate_visual_window([{'page':1,'document_total_pages':2}],0)==2
assert validate_visual_window([{'page':2,'document_total_pages':2}],1)==2
print('PASS: invalid visual windows cannot falsely mark PDF page coverage complete (synthetic)')
