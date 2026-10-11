#!/usr/bin/env python3
"""Free global cash-bounty candidate directory. Read-only; no target probing."""
import json
import pathlib
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent
URL = "https://raw.githubusercontent.com/projectdiscovery/public-bugbounty-programs/main/dist/data.json"
OUTPUT = ROOT / "global_bounties.json"
KNOWN = {"hackerone.com": "HackerOne", "bugcrowd.com": "Bugcrowd",
         "intigriti.com": "Intigriti", "immunefi.com": "Immunefi",
         "yeswehack.com": "YesWeHack", "hackenproof.com": "HackenProof"}

def platform(url):
    host = (urlparse(url).hostname or "").lower()
    for domain, label in KNOWN.items():
        if host == domain or host.endswith("." + domain):
            return label
    return "Independent / other"

def extract(data):
    programs = data.get("programs") if isinstance(data, dict) else data
    if not isinstance(programs, list):
        raise ValueError("Unexpected program directory format")
    result = []
    seen = set()
    for row in programs:
        if not isinstance(row, dict) or row.get("bounty") is not True:
            continue
        url = row.get("url")
        if not isinstance(url, str) or urlparse(url).scheme != "https":
            continue
        name = str(row.get("name") or "").strip()
        if not name:
            continue
        key = url.lower().rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        result.append({
            "name": name, "platform": platform(url), "program_url": url,
            "catalog_marks_bounty": True,
            "cash_payment_verified": False,
            "open_and_authorized_verified": False,
            "rule": "Candidate only: read current program rules, cash payouts, and scope before any testing"
        })
    return sorted(result, key=lambda item: (item["platform"], item["name"].lower()))

def main():
    report = {"collected_at_utc": datetime.now(timezone.utc).isoformat(),
              "source": URL, "directory_is_third_party": True,
              "candidates": [], "error": None}
    try:
        req = urllib.request.Request(URL, headers={"User-Agent":"BountyCandidatesReadOnly/1.0"})
        with urllib.request.urlopen(req, timeout=25) as response:
            body = response.read(8_000_001)
        if len(body) > 8_000_000:
            raise ValueError("Input larger than 8MB")
        report["candidates"] = extract(json.loads(body))
        report["total_candidates"] = len(report["candidates"])
        counts = {}
        for row in report["candidates"]:
            counts[row["platform"]] = counts.get(row["platform"], 0) + 1
        report["by_platform"] = counts
    except Exception as exc:
        report["error"] = str(exc)[:300]
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("global bounty directory candidates:", report.get("total_candidates", 0))
    print("platform counts:", report.get("by_platform", {}))
    if report["error"]:
        print("error:", report["error"])
        raise SystemExit(1)

if __name__ == "__main__":
    main()
