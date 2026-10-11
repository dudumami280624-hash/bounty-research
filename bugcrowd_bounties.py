#!/usr/bin/env python3
"""Extract Bugcrowd cash-bounty *candidates* from the downloaded public directory.
No login, scraping behind authentication, or target testing.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "global_bounties.json"
DEST = ROOT / "bugcrowd_bounties.json"

def select_bugcrowd_candidates(global_report):
    if global_report.get("error"):
        raise ValueError("Global directory download failed")
    candidates = global_report.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("Global directory is missing candidates")
    found = {}
    for item in candidates:
        if not isinstance(item, dict):
            continue
        url = item.get("program_url", "")
        if not isinstance(url, str):
            continue
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in ("bugcrowd.com", "www.bugcrowd.com"):
            continue
        if not item.get("catalog_marks_bounty"):
            continue
        normalized_url = "https://bugcrowd.com" + parsed.path.rstrip("/")
        found[normalized_url.lower()] = {
            "name": item.get("name", ""),
            "program_url": normalized_url,
            "platform": "Bugcrowd",
            "candidate_cash_bounty": True,
            "cash_amount_verified": False,
            "official_scope_verified": False,
            "live_status_verified": False,
            "requires_official_rule_review": True,
        }
    return sorted(found.values(), key=lambda x: x["name"].lower())

def main():
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "platform": "Bugcrowd", "source": "ProjectDiscovery public-bugbounty-programs directory",
              "official_bugcrowd_api": False, "error": None, "candidates": [], "candidate_count": 0}
    try:
        global_report = json.loads(SOURCE.read_text(encoding="utf-8"))
        report["candidates"] = select_bugcrowd_candidates(global_report)
        report["candidate_count"] = len(report["candidates"])
        report["source_collected_at_utc"] = global_report.get("collected_at_utc")
    except Exception as exc:
        report["error"] = type(exc).__name__ + ": " + str(exc)[:150]
    DEST.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Bugcrowd public bounty candidates:", report["candidate_count"], "error:", report["error"])
    if report["error"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
