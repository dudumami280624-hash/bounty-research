#!/usr/bin/env python3
"""Read-only DOCX/PPTX text comparison for candlestick version candidates.

Uses Python standard library only. Does not inspect images or establish semantic
equivalence. Outputs hashes and counts, not copyrighted source passages.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

def extract(path):
    suffix = path.suffix.lower()
    if suffix not in (".docx", ".pptx"):
        raise ValueError("Only DOCX/PPTX supported: " + str(path))
    units = []
    with zipfile.ZipFile(path) as z:
        if suffix == ".docx":
            names = ["word/document.xml"]
        else:
            names = sorted(
                (n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide[0-9]+\.xml", n)),
                key=lambda n: int(re.search(r"slide([0-9]+)", n).group(1)))
        for name in names:
            if name not in z.namelist():
                continue
            root = ET.fromstring(z.read(name))
            tag = "{http://schemas.openxmlformats.org/drawingml/2006/main}t" if suffix == ".pptx" else "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
            parts = [e.text or "" for e in root.iter(tag)]
            units.append(" ".join(parts))
    return units

def normalized(text):
    return re.sub(r"\s+", "", text).casefold()

def analyze(paths):
    records = []
    for path in paths:
        units = extract(path)
        norm = normalized(" ".join(units))
        tokens = set(re.findall(r"[\u4e00-\u9fff]|[a-z0-9]+", norm))
        records.append({"name": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "units": len(units), "characters": len(norm),
                        "normalized_sha256": hashlib.sha256(norm.encode()).hexdigest(),
                        "_tokens": tokens})
    pairs = []
    for i, a in enumerate(records):
        for b in records[i+1:]:
            common = len(a["_tokens"] & b["_tokens"])
            pairs.append({"a": a["name"], "b": b["name"],
                          "token_coverage_a": round(common / len(a["_tokens"]), 4) if a["_tokens"] else None,
                          "token_coverage_b": round(common / len(b["_tokens"]), 4) if b["_tokens"] else None,
                          "normalized_text_identical": (a["characters"] > 0 and b["characters"] > 0\n                                                        and a["normalized_sha256"] == b["normalized_sha256"])})
    for r in records:
        del r["_tokens"]
    return {"sources": records, "pairs": pairs, "visual_reviewed": False, "fact_verified": False,
            "note": "Token coverage is a coarse screening metric, not paragraph overlap or proof of duplication."}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.files)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sources": len(result["sources"]), "pairs": len(result["pairs"]),
                      "output": str(args.output)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
