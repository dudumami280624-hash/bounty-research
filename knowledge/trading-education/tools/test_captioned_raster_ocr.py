#!/usr/bin/env python3
"""Real production-scanner regression on a generated captioned raster PDF."""
import os
import shutil
import tempfile
import unittest
from pathlib import Path

class HybridRasterOcr(unittest.TestCase):
    def test_captioned_raster_is_not_treated_as_full_text(self):
        if not shutil.which("tesseract"):
            self.skipTest("Tesseract unavailable")
        import fitz
        from PIL import Image, ImageDraw, ImageFont
        from free_visual import inspect_pdf
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            img=Image.new("RGB",(1400,450),"white")
            d=ImageDraw.Draw(img)
            font_file="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            font=ImageFont.truetype(font_file,75) if Path(font_file).exists() else ImageFont.load_default()
            d.text((60,130),"CANDLESTICK 2026",fill="black",font=font)
            image_path=root/"chart.png";img.save(image_path)
            pdf=fitz.open();page=pdf.new_page(width=700,height=330)
            page.insert_text((35,35),"This chart has a lengthy explanatory caption with embedded text. "*3)
            page.insert_image(fitz.Rect(0,85,700,310),filename=str(image_path))
            path=root/"fixture.pdf";pdf.save(path);pdf.close()
            old=os.environ.get("TMM_OCR_PAGE_TIMEOUT_SECONDS")
            os.environ["TMM_OCR_PAGE_TIMEOUT_SECONDS"]="20"
            try: rows=inspect_pdf(path,root/"audit")
            finally:
                if old is None: os.environ.pop("TMM_OCR_PAGE_TIMEOUT_SECONDS",None)
                else: os.environ["TMM_OCR_PAGE_TIMEOUT_SECONDS"]=old
            self.assertEqual(len(rows),1)
            row=rows[0]
            self.assertTrue(row["raster_with_embedded_text_ocr_needed"])
            self.assertTrue(row["ocr_performed"])
            self.assertEqual(row["text_origin"],"embedded_raster_plus_ocr_unverified")
            self.assertTrue(row["ocr_success"],row)
            self.assertFalse(row["chart_semantics_verified"])

if __name__=="__main__": unittest.main()
