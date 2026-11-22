#!/usr/bin/env python3
"""Safe opt-in manifest gate for cobalt-assisted video research.

No downloads occur here. cobalt must be separately deployed/configured and
source rights verified by a human. No textbook/media bytes are committed.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

ALLOWED = {"youtube.com", "www.youtube.com", "youtu.be", "x.com", "twitter.com", "www.tiktok.com", "tiktok.com"}
def assess(record):
    url = record.get("url", "")
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or host not in ALLOWED:
        return "blocked_invalid_or_unapproved_host"
    if record.get("permission") != "explicit_authorization":
        return "blocked_no_documented_permission"
    if not record.get("permission_reference"):
        return "blocked_missing_permission_evidence"
    if record.get("media_kind") not in ("financial_education", "market_chart"):
        return "blocked_unrelated_content"
    return "eligible_for_manual_download_review"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        ap.error("manifest must be a JSON array")
    lines = ["# Cobalt media acquisition — permission-gated queue", "",
             "> Metadata only. No media downloaded. Eligibility is NOT proof of permission or technical downloadability.",
             "> Review platform terms and copyright before any external download.", ""]
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            ap.error(f"item {i} must be an object")
        status = assess(item)
        lines.extend([f"## Item {i}", f"- URL: {item.get('url', '')}",
                      f"- Gate: `{status}`",
                      f"- Evidence reference: {item.get('permission_reference', 'none')}", ""])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Reviewed {len(data)} media candidates; no downloads performed")

if __name__ == "__main__":
    main()
