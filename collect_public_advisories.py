"""Collect public GitHub-reviewed security advisories with deduplication and provenance.

The resulting records are reference knowledge, not validated exploit findings.
"""
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

URL = "https://api.github.com/advisories"

def collect(pages=3):
    records = {}
    for page in range(1, pages + 1):
        req = Request(f"{URL}?per_page=100&page={page}&type=reviewed", headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "bounty-research-knowledge-collector",
            **({"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"} if os.environ.get("GITHUB_TOKEN") else {})
        })
        with urlopen(req, timeout=35) as response:
            entries = json.load(response)
        if not isinstance(entries, list):
            raise RuntimeError("unexpected advisories API response")
        for entry in entries:
            key = entry.get("ghsa_id")
            if not key:
                continue
            records[key] = {
                "id": key,
                "title": entry.get("summary"),
                "description": entry.get("description"),
                "category": [c.get("cwe_id") for c in entry.get("cwes", []) if c.get("cwe_id")],
                "source_url": entry.get("html_url"),
                "published_at": entry.get("published_at"),
                "updated_at": entry.get("updated_at"),
                "identifiers": entry.get("identifiers", []),
                "affected": entry.get("vulnerabilities", []),
                "verification": "public-advisory-unverified-locally",
            }
        if len(entries) < 100:
            break
    return records

def summarize(records):
    by_month = {}
    for record in records.values():
        date = record.get("published_at")
        if isinstance(date, str) and len(date) >= 7:
            month = date[:7]
            by_month[month] = by_month.get(month, 0) + 1
    return {
        "sample_size": len(records),
        "monthly_in_sample": dict(sorted(by_month.items())),
        "quarterly_in_sample": {
            f"{y}-Q{(int(m)-1)//3+1}": sum(count for key, count in by_month.items() if key[:4] == y and (int(key[5:7])-1)//3+1 == (int(m)-1)//3+1)
            for y,m in {(k[:4],k[5:7]) for k in by_month}
        },
        "coverage": "latest paginated reviewed GitHub advisories only; NOT global totals",
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pages", type=int, default=3)
    p.add_argument("--output", default="advisory-knowledge.json")
    p.add_argument("--summary", default="advisory-summary.json")
    a = p.parse_args()
    if not 1 <= a.pages <= 20:
        p.error("pages must be 1..20")
    records = collect(a.pages)
    Path(a.output).write_text(json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True)+"\n")
    Path(a.summary).write_text(json.dumps(summarize(records), ensure_ascii=False, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"unique_advisories":len(records),"output":a.output}))

if __name__ == "__main__":
    main()
