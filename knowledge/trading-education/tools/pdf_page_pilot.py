#!/usr/bin/env python3
"""Read-only PDF page/text/figure crop pilot. No AI claims or source modification."""
import argparse
import hashlib
import json
from pathlib import Path

def inspect(pdf_path: Path, output: Path, page_number: int, box):
    import pypdfium2 as pdfium
    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_path)
    if not 1 <= page_number:
        raise ValueError("page must be >= 1")
    if box is not None and (len(box) != 4 or not all(0 <= v <= 1 for v in box)
                            or box[0] >= box[2] or box[1] >= box[3]):
        raise ValueError("box must be normalized x0 y0 x1 y1")
    output.mkdir(parents=True, exist_ok=True)
    with pdfium.PdfDocument(str(pdf_path)) as doc:
        if page_number > len(doc):
            raise ValueError("page exceeds PDF page count")
        page = doc[page_number - 1]
        try:
            textpage = page.get_textpage()
            try:
                text = textpage.get_text_bounded()
            finally:
                textpage.close()
            text_path = output / f"page-{page_number:03d}.txt"
            text_path.write_text(text, encoding="utf-8")
            metadata = {"source_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
                        "page": page_number, "total_pages": len(doc),
                        "text_characters": len(text), "text_file": text_path.name,
                        "has_extractable_text": bool(text.strip()),
                        "visual_reviewed": False, "fact_verified": False}
            if box is not None:
                bitmap = page.render(scale=2)
                try:
                    image = bitmap.to_pil()
                    try:
                        w, h = image.size
                        coords = tuple(round(v * (w if i % 2 == 0 else h)) for i, v in enumerate(box))
                        crop_path = output / f"page-{page_number:03d}-crop.png"
                        image.crop(coords).save(crop_path)
                        metadata["crop_file"] = crop_path.name
                        metadata["crop_box_normalized"] = box
                    finally:
                        image.close()
                finally:
                    bitmap.close()
            (output / f"page-{page_number:03d}.json").write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return metadata
        finally:
            page.close()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pdf", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--box", type=float, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    args = p.parse_args()
    print(json.dumps(inspect(args.pdf, args.output, args.page, args.box), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
