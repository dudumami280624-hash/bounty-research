#!/usr/bin/env python3
"""Real PyMuPDF blank-page regression; synthetic PDF, not textbook validation."""
import tempfile
from pathlib import Path
import fitz
from free_visual import inspect_pdf
from resume_visual_pages import page_ocr_resolved

with tempfile.TemporaryDirectory() as td:
    pdf=Path(td)/'pages.pdf'
    doc=fitz.open()
    doc.new_page()
    page=doc.new_page()
    page.draw_rect(fitz.Rect(30,30,120,90),color=(0,0,0))
    doc.save(pdf)
    doc.close()
    observations=inspect_pdf(pdf,Path(td)/'out')
    assert len(observations)==2
    blank, graphic=observations
    assert blank['visually_blank_no_ocr_needed'] is True, blank
    assert blank['ocr_performed'] is False, blank
    assert page_ocr_resolved(blank,{}) is True
    assert graphic['visually_blank_no_ocr_needed'] is False, graphic
    assert graphic['vector_drawings']>0, graphic
    # A chart-like page with no OCR text must never be marked resolved.
    unresolved={**graphic,'ocr_performed':True,'ocr_success':False}
    assert page_ocr_resolved(unresolved,{}) is False
    assert page_ocr_resolved({**blank,'image_objects':1},{}) is False
print('PASS: actual PyMuPDF blank page is not an OCR failure; drawn page remains unresolved')
