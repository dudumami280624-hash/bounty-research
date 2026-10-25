#!/usr/bin/env python3
"""Reproduce core US market datasets for The Market Mind.

Usage:
  python scripts/reproduce_us_market_data.py --start 1970-01-01 --end 2025-12-31
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

SERIES = {
    "sp500": "SP500",
    "nasdaq": "NASDAQCOM",
    "fedfunds": "FEDFUNDS",
    "cpi": "CPIAUCSL",
    "unemployment": "UNRATE",
    "mortgage_delinquency": "DRSFRMACBS",
    "house_prices": "USSTHPI",
}

def fetch(series: str, start: str, end: str) -> bytes:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd={start}&coed={end}"
    with urlopen(url, timeout=60) as response:
        return response.read()

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="1920-01-01")
    parser.add_argument("--end", default="2025-12-31")
    parser.add_argument("--out", default="knowledge/market-psychology/data/us-fred")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"retrieved_at_utc": None, "start": args.start, "end": args.end, "series": {}}

    from datetime import datetime, timezone
    manifest["retrieved_at_utc"] = datetime.now(timezone.utc).isoformat()

    for name, series in SERIES.items():
        data = fetch(series, args.start, args.end)
        path = out / f"{name}_{series}.csv"
        path.write_bytes(data)
        manifest["series"][name] = {
            "fred_id": series,
            "file": str(path),
            "sha256": sha256(data),
            "bytes": len(data),
        }

    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
