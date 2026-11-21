#!/usr/bin/env python3
"""Real local PyMuPDF fixture: a page-number-only PDF must invoke Tesseract.
Synthetic PDF only: does not claim source OCR or semantic verification.
"""
import tempfile
from pathlib import Path
from unittest.mock import patch
import fitz
from free_visual import inspect_pdf

with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'fixture.pdf'
    d=fitz.open()
    page=d.new_page()
    page.insert_text((72,72),'12')
    d.save(p);d.close()
    class OCR:
        returncode=0
        stdout='sample extracted page content'
        stderr=''
    real_run=__import__('subprocess').run
    def fake_run(cmd,*args,**kwargs):
        if '--list-langs' in cmd: return type('Languages',(),{'stdout':'eng'})()
        if cmd[0]=='tesseract': return OCR()
        return real_run(cmd,*args,**kwargs)
    with patch('free_visual.shutil.which',return_value='/usr/bin/tesseract'),patch('free_visual.subprocess.run',side_effect=fake_run) as runner:
        records=inspect_pdf(p,Path(td)/'out')
    x=records[0]
    assert x['embedded_text_sparse'] is True
    assert x['ocr_performed'] is True
    assert x['text_origin']=='embedded_sparse_plus_ocr_unverified'
    assert x['chart_semantics_verified'] is False
    assert any(c.args[0][0]=='tesseract' and 'stdout' in c.args[0] for c in runner.call_args_list)
print('PASS: sparse embedded text does not suppress OCR (synthetic PDF)')
