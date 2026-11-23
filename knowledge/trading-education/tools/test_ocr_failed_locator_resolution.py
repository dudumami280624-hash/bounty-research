#!/usr/bin/env python3
"""Production-function regression; synthetic metadata, NOT textbook OCR."""
from resume_visual_pages import page_ocr_resolved

legacy={"ocr_success":True, "ocr_actual_success":False, "render_sha256":"same"}
raster={"page":1,"render_sha256":"same","ocr_success":False,"ocr_performed":True,
        "text_origin":"embedded_raster_plus_ocr_unverified",
        "raster_with_embedded_text_ocr_needed":True}
assert not page_ocr_resolved(raster,legacy), "legacy text must not clear failed raster OCR"
assert page_ocr_resolved({**raster,"ocr_success":True},legacy), "real OCR success must clear"
assert page_ocr_resolved(raster,{"ocr_actual_success":True,"render_sha256":"same"}), "matching real OCR evidence should survive retry"
assert not page_ocr_resolved(raster,{"ocr_actual_success":True,"render_sha256":"changed"}), "render drift invalidates old OCR"
assert page_ocr_resolved({"render_sha256":"same","ocr_success":True,"ocr_performed":False,
 "text_origin":"embedded_pdf_text","raster_with_embedded_text_ocr_needed":False},legacy), "text-only page does not need OCR"
assert not page_ocr_resolved({"render_sha256":"same","ocr_success":True,"ocr_performed":False,
 "text_origin":"embedded_pdf_text","raster_with_embedded_text_ocr_needed":True},legacy), "raster page needs actual OCR"
print("PASS: real OCR and text-only status correctly resolve failed page locators")
