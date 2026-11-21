#!/usr/bin/env python3
"""Synthetic checkpoint regression; no claim of real OCR/semantic validation."""
from resume_visual_pages import retain_page_evidence
audit={}
retain_page_evidence(audit,[{'page':1,'render_sha256':'a'*64,'ocr_success':True,'ocr_text_characters':42,'chart_candidate':False}])
retain_page_evidence(audit,[{'page':2,'render_sha256':'b'*64,'ocr_success':False,'ocr_text_characters':0,'chart_candidate':True}])
assert set(audit['page_evidence'])=={'1','2'}
assert audit['page_evidence']['1']['ocr_text_characters']==42
assert audit['page_evidence']['2']['chart_candidate_unverified'] is True
retain_page_evidence(audit,[{'page':2,'render_sha256':'c'*64,'ocr_success':True,'ocr_text_characters':5,'chart_candidate':True}])
assert audit['page_evidence']['1']['render_sha256']=='a'*64
assert audit['page_evidence']['2']['render_sha256']=='c'*64
assert audit['page_evidence']['2']['ocr_success'] is True
assert 'text' not in audit['page_evidence']['2']
print('PASS: per-page provenance survives multiple windows and updates retries (synthetic)')
