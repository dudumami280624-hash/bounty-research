#!/usr/bin/env python3
"""Offline MediaCrawler export importer: metadata-only, no scraping or login.

Public reports contain no post text, user names, cookies, or source media.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

PLATFORMS = {"xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu"}
ID_KEYS = ("note_id", "aweme_id", "video_id", "id", "post_id", "article_id")
URL_KEYS = ("note_url", "video_url", "url", "post_url", "article_url")
TEXT_KEYS = ("title", "desc", "content", "text")
KEYWORDS = ("k线", "蜡烛图", "技术分析", "成交量", "price action", "candlestick", "volume")

def load_records(path):
    if path.suffix.lower() == ".jsonl":
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                yield json.loads(line)
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("data", data.get("items", []))
        if not isinstance(data, list):
            raise ValueError("Expected list, or object with data/items array")
        yield from data

def summarize(records, platform):
    if platform not in PLATFORMS:
        raise ValueError("Unsupported platform")
    unique = set()
    counts = Counter()
    total = 0
    skipped = 0
    for obj in records:
        total += 1
        if not isinstance(obj, dict):
            skipped += 1
            continue
        ident = next((str(obj[k]) for k in ID_KEYS if obj.get(k) is not None), "")
        url = next((str(obj[k]) for k in URL_KEYS if obj.get(k)), "")
        # Never include original IDs or URLs in a public report.
        if url and urlparse(url).scheme not in ("http", "https"):
            skipped += 1
            continue
        if not ident and not url:
            skipped += 1
            continue
        digest = hashlib.sha256((platform + "\0" + (ident or url)).encode()).hexdigest()
        if digest in unique:
            counts["duplicate_records"] += 1
            continue
        unique.add(digest)
        body = " ".join(str(obj.get(k, "")) for k in TEXT_KEYS).lower()
        matched = [word for word in KEYWORDS if word in body]
        counts["topic_candidates"] += bool(matched)
        counts["unmatched"] += not bool(matched)
    return {"platform": platform, "total_records": total, "unique_records": len(unique),
            "skipped_records": skipped, "duplicate_records": counts["duplicate_records"],
            "keyword_topic_candidates_unverified": counts["topic_candidates"],
            "unmatched_records": counts["unmatched"],
            "independently_verified_claims": 0}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path, help="Local MediaCrawler JSON or JSONL export; never commit raw data")
    ap.add_argument("--platform", required=True, choices=sorted(PLATFORMS))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    summary = summarize(load_records(args.input), args.platform)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))

if __name__ == "__main__":
    main()
