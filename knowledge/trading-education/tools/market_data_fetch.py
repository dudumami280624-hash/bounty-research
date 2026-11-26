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
    try:
        pointer=get(f"https://raw.githubusercontent.com/Pubmarks/datasets/main/{path}")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        # Raw and LFS media endpoints can differ in availability. Validate the
        # alternate response exactly as a normal CSV; never accept HTML.
        raw=get(f"https://media.githubusercontent.com/media/Pubmarks/datasets/main/{path}")
        validate(raw)
        return raw
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
    raw = b""
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

def fetch_open_archive(symbol):
    """CC BY 4.0: securities-js/market-data; historical research, not live quotes."""
    base = "https://securities-js.github.io/market-data"
    rows = []
    missing = []
    for year in range(2010, date.today().year + 1):
        try:
            obj = json.loads(get(f"{base}/us/symbol/{symbol}/prices/{year}.json"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                missing.append(year)
                continue
            raise
        if obj.get("symbol") != symbol or str(obj.get("year")) != str(year) or obj.get("period") != "day":
            raise ValueError("archive identity mismatch")
        for p in obj["prices"]:
            required = ("date","open","hi","lo","close","volume")
            missing_fields = [k for k in required if k not in p or p[k] is None]
            if missing_fields:
                raise ValueError(f"archive {symbol} {p.get('date', year)} missing OHLCV fields: {missing_fields}; cannot reconstruct candle")
            if not isinstance(p["date"], str) or not p["date"].startswith(str(year)+"-"):
                raise ValueError("archive date mismatch")
            rows.append([p[k] for k in required])
    if not rows:
        raise ValueError("open archive has no OHLCV for "+symbol)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Date","Open","High","Low","Close","Volume"])
    writer.writerows(sorted(rows))
    raw = buf.getvalue().encode()
    validate(raw)
    return raw, missing

def fetch(symbol, output):
    if not re.fullmatch(r"[A-Z0-9.-]+",symbol):
        raise ValueError("invalid symbol")
    missing_years = None
    # Use only verified local snapshot exports; no per-symbol HTTP request.
    local = os.environ.get("TMM_SNAPSHOT_DIR")
    if local:
        folder = Path(local)
        manifest = json.loads((folder / "snapshot-summary.json").read_text())
        if manifest.get("sha256") != "7b58eeafc855a502469fc5090eb703f76516172deebe13d51609fd6eb2c5f3f5":
            raise ValueError("Unrecognized snapshot")
        item = next((x for x in manifest["results"] if x["symbol"] == symbol and x["status"] == "structural_only"), None)
        if item:
            raw = (folder / (symbol+".csv")).read_bytes()
            count = validate(raw)
            digest = hashlib.sha256(raw).hexdigest()
            if count != item["rows"] or digest != item.get("sha256"):
                raise ValueError("Snapshot export integrity mismatch")
            output.mkdir(parents=True, exist_ok=True)
            (output / (symbol+".csv")).write_bytes(raw)
            return {"symbol":symbol,"rows":count,"sha256":digest,"adjustment":"unverified","source":manifest["url"],"snapshot_sha256":manifest["sha256"]}
        raise ValueError("Symbol unavailable in local snapshot; no HTTP retry")
    source = "Pubmarks/datasets"
    try:
        raw = fetch_pubmarks(symbol)
        count = validate(raw)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        try:
            raw, missing_years = fetch_open_archive(symbol)
            source = "securities-js/market-data (CC BY 4.0)"
            # Missing years must not silently bridge long-horizon research windows.
            if missing_years:
                raise ValueError("archive incomplete; missing years: " + ",".join(map(str, missing_years)))
        except Exception as archive_error:
            if os.environ.get("TMM_ALLOW_STOOQ_PERSONAL") != "1":
                raise ValueError("Pubmarks 404; open archive: "+str(archive_error)) from archive_error
            source = "Stooq (personal research only)"
            raw = fetch_stooq(symbol)
        count = validate(raw)
    output.mkdir(parents=True,exist_ok=True)
    (output/f"{symbol}.csv").write_bytes(raw)
    return {"symbol":symbol,"rows":count,"sha256":hashlib.sha256(raw).hexdigest(),"adjustment":"unverified","source":source,"missing_archive_years_since_2010":missing_years}

def run_batch(symbols, output):
    """Persist partial results and explicit retry queue, never certify missing data."""
    output.mkdir(parents=True, exist_ok=True)
    results, failures = [], []
    # Reuse only previously successful files with matching provenance and checksum.
    cached = {}
    try:
        previous = json.loads((output / "batch-summary.json").read_text(encoding="utf-8"))
        cached = {item["symbol"]: item for item in previous["results"] if isinstance(item, dict)}
    except (OSError, ValueError, KeyError, TypeError):
        pass
    for symbol in dict.fromkeys(symbols):
        try:
            result = None
            if re.fullmatch(r"[A-Z0-9.-]+", symbol) and symbol in cached:
                try:
                    item = cached[symbol]
                    raw = (output / f"{symbol}.csv").read_bytes()
                    if (item.get("source") and item.get("adjustment") and
                            hashlib.sha256(raw).hexdigest() == item.get("sha256") and
                            validate(raw) == item.get("rows")):
                        result = item
                except (OSError, ValueError, TypeError, KeyError):
                    pass
            if result is None:
                result = fetch(symbol, output)
            results.append(result)
            print(json.dumps(result), flush=True)
        except Exception as e:
            failure = {"symbol": symbol, "error": str(e),
                       "http_status": getattr(e, "code", None)}
            failures.append(failure)
            print(json.dumps(failure), flush=True)
    summary = {"requested": len(results)+len(failures),
               "successful": len(results), "failed": len(failures),
               "status": "complete" if not failures else ("partial" if results else "failed"),
               "results": results, "retry_queue": failures}
    tmp = output / "batch-summary.tmp"
    tmp.write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    tmp.replace(output / "batch-summary.json")
    return summary

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("symbols",nargs="+")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    summary=run_batch(args.symbols,args.output)
    print(json.dumps({k:summary[k] for k in ("requested","successful","failed","status")}),flush=True)
    # Keep strict CI acceptance: partial downloads are useful but not complete.
    raise SystemExit(int(summary["failed"] > 0))
