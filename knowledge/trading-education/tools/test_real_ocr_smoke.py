#!/usr/bin/env python3
"""Run the installed free OCR engine on a generated image-only PDF.

This tests real Tesseract execution and PyMuPDF rendering, NOT textbook OCR
accuracy, chart semantics, or independent fact verification.
"""
import os
import shutil
import tempfile
from pathlib import Path

from free_visual import inspect_pdf


def main():
    import fitz
    if not shutil.which("tesseract"):
        raise RuntimeError("Tesseract missing: real OCR smoke test cannot run")
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        # Draw large, high-contrast original text, then rasterize it into a
        # separate image-only PDF so embedded PDF text cannot pass the test.
        source = fitz.open()
        page = source.new_page(width=612, height=792)
        page.insert_text((65, 160), "MARKET PRICE ACTION", fontsize=32)
        page.insert_text((65, 240), "OPEN HIGH LOW CLOSE", fontsize=27)
        raster = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        source.close()
        scanned = fitz.open()
        dest = scanned.new_page(width=612, height=792)
        dest.insert_image(dest.rect, stream=raster.tobytes("png"))
        path = root / "generated-image-only.pdf"
        scanned.save(path)
        scanned.close()
        previous = os.environ.get("TMM_VISUAL_MAX_PAGES")
        os.environ["TMM_VISUAL_MAX_PAGES"] = "1"
        try:
            observations = inspect_pdf(path, root / "audit")
        finally:
            if previous is None:
                os.environ.pop("TMM_VISUAL_MAX_PAGES", None)
            else:
                os.environ["TMM_VISUAL_MAX_PAGES"] = previous
        assert len(observations) == 1, observations
        result = observations[0]
        assert result["embedded_text_characters"] == 0, result
        assert result["ocr_performed"] is True, result
        assert result["ocr_success"] is True, result
        assert result["ocr_text_characters"] >= 10, result
        assert result["text_origin"] == "ocr_unverified", result
        assert result["chart_semantics_verified"] is False, result
        assert result["text_sha256"], result
        print("PASS: real Tesseract OCR on generated image-only PDF; no textbook or semantic verification")


if __name__ == "__main__":
    main()
