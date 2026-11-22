#!/usr/bin/env python3
"""Real PyMuPDF regression: raster chart with long selectable caption needs OCR.

Synthetic fixture tests the production PDF text-audit function, NOT a textbook
or actual Tesseract transcription, semantic chart interpretation, or fact-check.
"""
import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import fitz
from PIL import Image, ImageDraw
import run_extraction_batch as runner


def make_pdf():
    im = Image.new("RGB", (420, 220), "white")
    draw = ImageDraw.Draw(im)
    draw.line([(20, 180), (80, 100), (140, 160), (200, 40), (260, 90), (350, 30)], fill="black", width=4)
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    doc = fitz.open()
    page = doc.new_page(width=600, height=800)
    # >80 meaningful characters, enough to bypass the old sparse-only rule.
    caption = "This selectable caption describes general trading terminology. " * 5
    page.insert_textbox(fitz.Rect(30, 30, 560, 180), caption, fontsize=12)
    page.insert_image(fitz.Rect(30, 220, 450, 440), stream=buf.getvalue())
    raw = doc.tobytes()
    doc.close()
    return raw


def main():
    blob = make_pdf()
    sha = "a" * 40
    entry = {"sha": sha, "name": "priority-candlestick.pdf", "category": "01-candlestick"}
    files = {sha: {"extraction_status": "extracted"}}
    with tempfile.TemporaryDirectory() as td:
        with patch.object(runner, "STATE", Path(td) / "state.json"), patch.object(
            runner, "download_blob", lambda *_args, **_kw: blob
        ):
            advanced = runner.advance_pdf_text_windows([entry], files, budget_seconds=30)
        assert len(advanced) == 1, advanced
        evidence = files[sha]["pdf_text_page_audit"]["page_evidence"]["1"]
        assert evidence["embedded_meaningful_chars"] >= 80, evidence
        assert evidence["raster_image_objects"] >= 1, evidence
        assert evidence["ocr_needed"] is True, evidence
        assert evidence["verified"] is False, evidence
        assert files[sha]["pdf_text_page_audit"]["coverage_complete"] is True
        print(json.dumps({"result": "PASS", "real_parser": "PyMuPDF",
                          "fixture": "generated_pdf_not_textbook",
                          "ocr_needed": evidence["ocr_needed"],
                          "independently_verified": False}))


if __name__ == "__main__":
    main()
