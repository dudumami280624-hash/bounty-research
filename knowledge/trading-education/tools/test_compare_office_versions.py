#!/usr/bin/env python3
"""Synthetic regression for compare_office_versions.py; no textbook content."""
import tempfile
import zipfile
from pathlib import Path
from compare_office_versions import analyze, extract

def make(path, member, xml):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(member, xml)

def main():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        a, b, c = (root / x for x in ("a.docx", "b.docx", "c.pptx"))
        word = ('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                '<w:body><w:p><w:r><w:t>十字星 ABC</w:t></w:r></w:p></w:body></w:document>')
        slide = ('<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                 '<a:t>十字星 ABC</a:t></p:sld>')
        make(a, "word/document.xml", word)
        make(b, "word/document.xml", word)
        make(c, "ppt/slides/slide1.xml", slide)
        assert extract(a) == ["十字星 ABC"]
        assert extract(c) == ["十字星 ABC"]
        report = analyze([a, b, c])
        assert len(report["sources"]) == 3
        assert len(report["pairs"]) == 3
        assert all(pair["normalized_text_identical"] for pair in report["pairs"])
        assert all(pair["token_coverage_a"] == 1 for pair in report["pairs"])
        assert report["visual_reviewed"] is False
        assert report["fact_verified"] is False
    print("Synthetic Office comparison checks passed")

if __name__ == "__main__":
    main()
