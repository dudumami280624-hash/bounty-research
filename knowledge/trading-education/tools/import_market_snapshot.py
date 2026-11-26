"""Import a pinned public snapshot locally; never publish vendor rows.
Usage: python import_market_snapshot.py prices.parquet output SPY QQQ DAL NKE AAPL
Requires duckdb. Review upstream data rights before use.
"""
import argparse
import hashlib
import json
from pathlib import Path
from market_data_fetch import validate

SHA256 = "7b58eeafc855a502469fc5090eb703f76516172deebe13d51609fd6eb2c5f3f5"
URL = "https://github.com/Johnbrick123/sp500-data/releases/download/snapshot-2026-11/prices.parquet"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("file", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("symbols", nargs="+")
    a = p.parse_args()
    with a.file.open("rb") as f:
        digest = hashlib.file_digest(f, "sha256").hexdigest()
    if digest != SHA256:
        raise SystemExit("Snapshot digest mismatch")
    import duckdb
    db = duckdb.connect()
    a.output.mkdir(parents=True, exist_ok=True)
    report = []
    import csv, io, re
    for symbol in dict.fromkeys(a.symbols):
        if not re.fullmatch(r"[A-Z0-9.-]+", symbol):
            raise ValueError("Invalid symbol")
        try:
            rows = db.execute("""SELECT CAST(date AS DATE), open, high, low, close, volume, source
              FROM read_parquet(?) WHERE ticker = ? AND date >= DATE '1996-01-01'
              AND open IS NOT NULL AND high IS NOT NULL AND low IS NOT NULL
              AND close IS NOT NULL AND volume IS NOT NULL
              AND source <> 'carried-patch' ORDER BY date""", [str(a.file), symbol]).fetchall()
            sources = sorted({str(r[6]) for r in rows})
            if len(sources) != 1:
                raise ValueError("Absent or mixed source adjustment basis: "+str(sources))
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(["Date","Open","High","Low","Close","Volume"])
            w.writerows(r[:6] for r in rows)
            raw = buf.getvalue().encode()
            count = validate(raw)
            (a.output / (symbol+".csv")).write_bytes(raw)
            report.append(dict(symbol=symbol, rows=count, source=sources, adjustment="unverified", status="structural_only"))
        except Exception as e:
            report.append(dict(symbol=symbol, status="failed", error=str(e)))
    (a.output/"snapshot-summary.json").write_text(json.dumps(dict(url=URL,sha256=digest,results=report),indent=2))
    return int(any(r["status"]=="failed" for r in report))

if __name__ == "__main__":
    raise SystemExit(main())
