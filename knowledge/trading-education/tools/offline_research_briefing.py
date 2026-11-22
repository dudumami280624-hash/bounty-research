#!/usr/bin/env python3
"""Horizon-inspired, offline source-linked research briefing.

Groups repeated source mentions across topics without claiming semantic
deduplication or fact verification. No source passages or images are emitted.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

def build(catalog):
    groups = defaultdict(lambda: {"name": "", "topics": set(), "locations": set(), "ocr": set()})
    for topic, record in catalog.get("topics", {}).items():
        for src in record.get("sources", []):
            sha = src.get("source_sha")
            if not sha:
                continue
            item = groups[sha]
            item["name"] = src.get("source_name", "Unknown")
            item["topics"].add(topic)
            for loc in src.get("locations", []):
                value = loc.get("location", "")
                if value:
                    item["locations"].add(value)
                    if "OCR-unverified" in value:
                        item["ocr"].add(value)
    rows = []
    for sha, item in groups.items():
        topics = sorted(item["topics"])
        # Editorial ranking only, NOT source reliability or truth scoring.
        priority = 10 * ("candlestick" in topics) + 3 * ("confirmation" in topics) + len(topics)
        rows.append((priority, sha, item, topics))
    return sorted(rows, key=lambda row: (-row[0], -len(row[2]["ocr"]), row[1]))

def render(catalog, limit=30):
    rows = build(catalog)
    output = [
        "# The Market Mind — offline evidence review briefing", "",
        "> Inspired by Horizon's profile-based ranking and grouping. This is a review queue, not a news feed, semantic deduplication, OCR validation, or independent fact checking.",
        "", f"- Unique source SHA groups: {len(rows)}",
        f"- Topic-source associations: {sum(len(v.get('sources', [])) for v in catalog.get('topics', {}).values())}",
        "- Ranking: candlestick +10, confirmation +3, one point per indexed topic; ties prefer more OCR-unverified locations.",
        "- Repeated SHA across topics is grouped once; separate sources with similar content are NOT automatically merged.",
        "", "## Highest-priority source reviews", ""
    ]
    for rank, (score, sha, item, topics) in enumerate(rows[:limit], 1):
        locs = sorted(item["ocr"])[:4] or sorted(item["locations"])[:4]
        output.extend([
            f"### {rank}. {item['name']}",
            f"- Source SHA: `{sha}`",
            f"- Editorial priority: {score}; topics: {', '.join(topics)}",
            f"- Indexed locations: {len(item['locations'])}; OCR-unverified locations: {len(item['ocr'])}",
            f"- Example locators (not validated): {', '.join(locs) if locs else 'none'}",
            "- Next: inspect original pages and compare independent sources before drafting any verified lesson.",
            ""
        ])
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(catalog, args.limit) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}; source groups: {len(build(catalog))}")

if __name__ == "__main__":
    main()
