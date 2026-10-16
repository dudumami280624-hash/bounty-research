#!/usr/bin/env python3
"""Fetch real published audit PDFs for the pinned target, extract searchable evidence.
No LLM, paid API, or invented vulnerability labels.
"""
import hashlib
import json
import urllib.request
from pathlib import Path
from pypdf import PdfReader

COMMIT = "ab92502e9da98784dfe3bd3ef933d4e9345ff628"
BASE = f"https://raw.githubusercontent.com/HorizenOfficial/staker/{COMMIT}/audits/"
NAMES = [
    "2024_12_Staker_Sherlock_Audit_Report.pdf",
    "2025_01_Reward_Notifiers_Offbeat_Security_Audit_Report.pdf",
    "2025_01_Staker_Sherlock_Public_Audit_Contest_Report.pdf",
]
OUT = Path("horizen-audit-knowledge")
OUT.mkdir(exist_ok=True)
manifest = []
for name in NAMES:
    url = BASE + name
    req = urllib.request.Request(url, headers={"User-Agent": "authorized-audit-research/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        data = response.read()
    pdf = OUT / name
    pdf.write_bytes(data)
    reader = PdfReader(str(pdf))
    pages = []
    for number, page in enumerate(reader.pages, 1):
        content = page.extract_text() or ""
        pages.append({"page": number, "text": content})
    extracted = OUT / (name + ".pages.json")
    extracted.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest.append({"source_url": url, "sha256": hashlib.sha256(data).hexdigest(),
                     "page_count": len(pages), "nonempty_pages": sum(bool(p["text"].strip()) for p in pages),
                     "extracted_file": str(extracted)})
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(manifest, indent=2))
