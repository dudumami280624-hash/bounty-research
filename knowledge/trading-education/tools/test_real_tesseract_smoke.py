#!/usr/bin/env python3
"""Real Tesseract OCR smoke test on generated scanned PDF; NOT textbook validation."""
import os
import shutil
import tempfile
import unittest
from pathlib import Path

class RealOcrSmoke(unittest.TestCase):
    def test_scanned_pdf_uses_real_tesseract(self):
        if not shutil.which("tesseract"):
            self.skipTest("Tesseract not installed")
        import fitz
        from PIL import Image, ImageDraw, ImageFont
        from free_visual import inspect_pdf
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            image = Image.new("RGB", (1400, 400), "white")
            draw = ImageDraw.Draw(image)
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            font = ImageFont.truetype(font_path, 82) if Path(font_path).exists() else ImageFont.load_default()
            draw.text((55, 105), "CANDLESTICK 2026", fill="black", font=font)
            image_path = root / "scan.png"
            image.save(image_path)
            doc = fitz.open()
            page = doc.new_page(width=700, height=200)
            page.insert_image(page.rect, filename=str(image_path))
            pdf_path = root / "scanned.pdf"
            doc.save(str(pdf_path))
            doc.close()
            old = os.environ.get("TMM_OCR_PAGE_TIMEOUT_SECONDS")
            os.environ["TMM_OCR_PAGE_TIMEOUT_SECONDS"] = "20"
            try:
                rows = inspect_pdf(pdf_path, root / "out")
            finally:
                if old is None:
                    os.environ.pop("TMM_OCR_PAGE_TIMEOUT_SECONDS", None)
                else:
                    os.environ["TMM_OCR_PAGE_TIMEOUT_SECONDS"] = old
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertTrue(row["ocr_performed"], row)
            self.assertTrue(row["ocr_success"], row)
            self.assertEqual(row["text_origin"], "ocr_unverified")
            self.assertGreater(row["ocr_text_characters"], 8)
            self.assertTrue(row.get("text_sha256"))
            self.assertFalse(row["chart_semantics_verified"])

if __name__ == "__main__":
    unittest.main()
