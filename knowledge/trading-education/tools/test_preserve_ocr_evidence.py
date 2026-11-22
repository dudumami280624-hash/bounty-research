#!/usr/bin/env python3
"""Synthetic regression: retries must not erase successful OCR page evidence."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from resume_visual_pages import retain_page_evidence

def observation(success, digest):
    return {'page': 1, 'render_sha256': digest, 'ocr_success': success,
            'ocr_performed': True, 'ocr_text_characters': 45 if success else 0,
            'text_sha256': 'a'*64 if success else None,
            'text_origin': 'ocr_unverified', 'chart_candidate': False}

audit={}
retain_page_evidence(audit,[observation(True,'render-A')])
first=dict(audit['page_evidence']['1'])
retain_page_evidence(audit,[observation(False,'render-A')])
assert audit['page_evidence']['1']==first, 'transient OCR failure erased successful evidence'
retain_page_evidence(audit,[observation(False,'render-B')])
assert not audit['page_evidence']['1']['ocr_success'], 'changed page must not inherit old evidence'
print('PASS: same-render retry preserves OCR; changed render invalidates it')
