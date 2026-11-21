#!/usr/bin/env python3
"""Synthetic regression: initial PDF extraction must record every deferred blank page."""
import os
import tempfile
from pathlib import Path
import fitz
from extract_source import pdf

def main():
    old=os.environ.get('TMM_INITIAL_OCR_MAX_PAGES')
    os.environ['TMM_INITIAL_OCR_MAX_PAGES']='0'
    try:
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'blank.pdf'
            doc=fitz.open()
            for _ in range(6):
                doc.new_page()
            doc.save(source)
            doc.close()
            blocks,images,details=pdf(source)
            assert details['pages']==6,details
            assert details['ocr_deferred_pages']==list(range(1,7)),details
            assert details['ocr_failed_pages']==list(range(1,7)),details
            assert not blocks,blocks
            assert details['initial_ocr_page_limit']==0,details
        print('PASS: six blank pages deferred with exact source page locators')
    finally:
        if old is None: os.environ.pop('TMM_INITIAL_OCR_MAX_PAGES',None)
        else: os.environ['TMM_INITIAL_OCR_MAX_PAGES']=old

if __name__=='__main__':main()
