#!/usr/bin/env python3
"""Read-only bounty candidate discovery. NOT scope authorization."""
import json
import pathlib
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent
FEED = "https://raw.githubusercontent.com/infosec-us-team/Immunefi-Bug-Bounty-Programs-Unofficial/main/projects.json"
OUT = ROOT / "candidates.json"

def discover(data):
    if not isinstance(data, list):
        raise ValueError("Unexpected catalog structure")
    candidates = []
    seen = set()
    for program in data:
        if not isinstance(program, dict):
            continue
        slug = str(program.get("slug") or program.get("id") or program.get("name") or "").strip()
        if not slug:
            continue
        for asset in program.get("assets", []):
            if not isinstance(asset, dict):
                continue
            url = asset.get("url") or ""
            parsed = urlparse(url)
            parts = [p for p in parsed.path.split("/") if p]
            if parsed.hostname != "github.com" or len(parts) < 2:
                continue
            repository = "https://github.com/" + parts[0] + "/" + parts[1].removesuffix(".git")
            key = (slug, repository)
            if key in seen:
                continue
            seen.add(key)
            candidates.append({
                "program": slug,
                "repository": repository,
                "scope_asset_url": url,
                "program_page": "https://immunefi.com/bug-bounty/" + slug + "/scope/",
                "status": "UNVERIFIED: recheck official active status, scope, payouts and pinned commit before testing",
            })
    return candidates

def main():
    result = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "feed": FEED, "source_is_unofficial": True, "candidates": [], "error": None}
    try:
        request = urllib.request.Request(FEED, headers={"User-Agent": "BountyResearchReadOnly/1.0"})
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = response.read(12_000_001)
        if len(payload) > 12_000_000:
            raise ValueError("Catalog exceeds 12MB safety limit")
        result["candidates"] = discover(json.loads(payload))
        result["candidate_count"] = len(result["candidates"])
    except Exception as exc:
        result["error"] = str(exc)[:300]
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("candidate_count:", result.get("candidate_count", 0), "error:", result["error"])
    if result["error"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
