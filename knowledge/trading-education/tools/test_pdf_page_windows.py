#!/usr/bin/env python3
"""Synthetic PDF window regression; no textbook excerpts or model-verification claims."""
import tempfile
from pathlib import Path
import fitz
from extract_source import pdf

def main():
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/"fixture.pdf"
        doc=fitz.open()
        for i in range(5):
            page=doc.new_page()
            page.insert_text((72,72),f"Synthetic page {i+1}")
        doc.save(path)
        blocks, images, details=pdf(path,start_page=2,max_pages=2)
        assert [b["location"] for b in blocks]==["page-3","page-4"],blocks
        assert details["pages"]==5
        assert details["window_start_page"]==3
        assert details["window_end_page"]==4
        assert details["window_complete"] is False
        blocks, _, details=pdf(path,start_page=4,max_pages=2)
        assert [b["location"] for b in blocks]==["page-5"]
        assert details["window_complete"] is True
    print("PASS synthetic bounded PDF page windows and one-based source locators")

if __name__=="__main__": main()
