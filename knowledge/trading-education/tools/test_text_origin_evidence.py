#!/usr/bin/env python3
"""Synthetic PDF evidence test: embedded text must never be represented as OCR."""
import tempfile
from pathlib import Path
import fitz
from free_visual import inspect_pdf
from resume_visual_pages import retain_page_evidence

with tempfile.TemporaryDirectory() as td:
    source=Path(td)/'synthetic.pdf'
    doc=fitz.open()
    page=doc.new_page()
    page.insert_text((72,72),'Synthetic embedded text, not OCR')
    doc.save(source)
    doc.close()
    observations=inspect_pdf(source,Path(td)/'private',start_page=0)
    assert len(observations)==1
    assert observations[0]['text_origin']=='embedded_pdf_text'
    assert observations[0]['ocr_performed'] is False
    assert observations[0]['ocr_success'] is True
    audit={}
    retain_page_evidence(audit,observations)
    evidence=audit['page_evidence']['1']
    assert evidence['text_origin']=='embedded_pdf_text'
    assert evidence['ocr_performed'] is False
    assert 'Synthetic' not in str(evidence)
print('PASS synthetic embedded PDF text is not misattributed to OCR')
