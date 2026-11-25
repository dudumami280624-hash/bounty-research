"""Free public market data fetcher. Run explicitly; no paid APIs."""
import argparse
import csv
import hashlib
import io
import json
import math
from datetime import date
import re
import urllib.request
import urllib.error
import time
import os
from pathlib import Path

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"TMM-research"}), timeout=30) as response:
        return response.read(20_000_001)

def validate(raw):
    if len(raw)>20_000_000:
        raise ValueError("file exceeds budget")
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if not rows:
        raise ValueError("empty CSV")
    cols={k.lower():k for k in rows[0]}
    for k in ("date","open","high","low","close","volume"):
        if k not in cols:
            raise ValueError("missing "+k)
    dates=set()
    for row in rows:
        d=row[cols["date"]]
        o,h,l,c,v=[float(row[cols[k]]) for k in ("open","high","low","close","volume")]
        if not all(math.isfinite(x) for x in (o,h,l,c,v)):
            raise ValueError("nonfinite OHLCV "+d)
        date.fromisoformat(d)
        if d in dates or not re.fullmatch(r"\d{4}-\d{2}-\d{2}",d) or not (0<l<=min(o,c)<=max(o,c)<=h and v>=0):
            raise ValueError("invalid or duplicate row "+d)
        dates.add(d)
    return len(rows)

def fetch_pubmarks(symbol):
    if not re.fullmatch(r"[A-Z0-9.-]+",symbol):
        raise ValueError("invalid symbol")
    path=f"data/stocks/{symbol}/ohlcv.csv"
    pointer=get(f"https://raw.githubusercontent.com/Pubmarks/datasets/main/{path}")
    match=re.search(rb"oid sha256:([0-9a-f]{64})\s+size (\d+)",pointer)
    if not match:
        raw=pointer
    else:
        raw=get(f"https://media.githubusercontent.com/media/Pubmarks/datasets/main/{path}")
        if len(raw)!=int(match[2]) or hashlib.sha256(raw).hexdigest()!=match[1].decode():
            raise ValueError("LFS integrity mismatch")
    return raw

_stooq_disabled = False
_last_stooq = 0.0

def fetch_stooq(symbol):
    global _stooq_disabled, _last_stooq
    if _stooq_disabled:
        raise ValueError("Stooq unavailable for this batch")
    if not re.fullmatch(r"[A-Z]+", symbol):
        raise ValueError("Stooq symbol mapping not verified")
    time.sleep(max(0, 2 - (time.monotonic() - _last_stooq)))
    _last_stooq = time.monotonic()
    try:
        raw = get(f"https://stooq.com/q/d/l/?s={symbol.lower()}.us&i=d")
        validate(raw)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 429):
            _stooq_disabled = True
        raise
    except ValueError:
        if not raw.lstrip().lower().startswith(b"date,"):
            _stooq_disabled = True
        raise
    return raw

def fetch(symbol, output):
    if not re.fullmatch(r"[A-Z0-9.-]+",symbol):
        raise ValueError("invalid symbol")
    source = "Pubmarks/datasets"
    try:
        raw = fetch_pubmarks(symbol)
        count = validate(raw)
    except urllib.error.HTTPError as e:
        if e.code != 404 or os.environ.get("TMM_ALLOW_STOOQ_PERSONAL") != "1":
            raise
        source = "Stooq (personal research only)"
        raw = fetch_stooq(symbol)
        count = validate(raw)
    output.mkdir(parents=True,exist_ok=True)
    (output/f"{symbol}.csv").write_bytes(raw)
    return {"symbol":symbol,"rows":count,"sha256":hashlib.sha256(raw).hexdigest(),"adjustment":"unverified","source":source}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("symbols",nargs="+")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    failed=False
    for symbol in dict.fromkeys(args.symbols):
        try:
            print(json.dumps(fetch(symbol,args.output)),flush=True)
        except Exception as e:
            failed=True
            print(json.dumps({"symbol":symbol,"error":str(e)}),flush=True)
    raise SystemExit(int(failed))
