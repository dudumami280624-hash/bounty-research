#!/usr/bin/env python3
"""Synthetic fixture: fingerprints are reproducible, without persisting text."""
import hashlib
import tempfile
from pathlib import Path
import fitz
from free_visual import inspect_pdf
from resume_visual_pages import retain_page_evidence

with tempfile.TemporaryDirectory() as td:
    pdf=Path(td)/'fixture.pdf'
    doc=fitz.open()
    page=doc.new_page()
    for i in range(4):
        page.insert_text((72,72+i*20),'Evidence fingerprint regression sample with enough readable characters.')
    doc.save(pdf)
    doc.close()
    observed=inspect_pdf(pdf,Path(td)/'audit')
    assert len(observed)==1
    item=observed[0]
    assert item['text_origin']=='embedded_pdf_text',item
    assert item['ocr_performed'] is False
    assert len(item['text_sha256'])==64
    audit={}
    retain_page_evidence(audit,observed)
    evidence=audit['page_evidence']['1']
    assert evidence['text_sha256']==item['text_sha256']
    assert 'text' not in evidence
    assert evidence['ocr_actual_success'] is False
print('Page text fingerprint and copyright-safe checkpoint: PASS')
