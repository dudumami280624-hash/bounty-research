"""Fail-closed adapter: parse an explicitly supplied public bounty HTML snapshot.
No network calls, vulnerability scans, or automatic eligibility decisions.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from scrapling import Selector


def parse_snapshot(html: str, source_url: str) -> dict:
    if not source_url.startswith(("https://", "http://")):
        raise ValueError("Source must be an explicit HTTP(S) URL")
    page = Selector(text=html)
    title = (page.css("title::text").get() or "").strip()
    return {
        "schema_version": 1,
        "source_url": source_url,
        "page_title": title,
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "unverified_public_page_lead",
        "official_scope_verified": False,
        "vulnerability_verified": False,
        "ready_to_submit": False,
        "payout_verified_usd": 0,
        "note": "Human verification against official bounty scope required",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--html", required=True, type=Path)
    p.add_argument("--source-url", required=True)
    p.add_argument("--output", default="tools/scrapling/output/bounty_page_lead.json", type=Path)
    args = p.parse_args()
    data = parse_snapshot(args.html.read_text(encoding="utf-8"), args.source_url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote unverified lead: {args.output}")


if __name__ == "__main__":
    main()
