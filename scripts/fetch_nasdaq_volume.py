#!/usr/bin/env python3
"""Fetch Nasdaq Data Link daily OHLCV bars.

Set NASDAQ_API_KEY when the selected Nasdaq Data Link product requires it.
"""
from __future__ import annotations
import argparse, hashlib, json, os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--symbol", default="SPY")
    p.add_argument("--start", default="2022-01-01")
    p.add_argument("--end", default="2023-01-31")
    p.add_argument("--out", default="knowledge/market-psychology/data/nasdaq")
    a=p.parse_args()
    key=os.environ.get("NASDAQ_API_KEY")
    params={"symbol":a.symbol,"startDate":a.start,"endDate":a.end,"limit":10000}
    if key: params["apiKey"]=key
    url="https://api.nasdaq.com/api/quote/"+a.symbol+"/historical?"+urlencode(params)
    req=Request(url,headers={"User-Agent":"The-Market-Mind-research/0.1","Accept":"application/json"})
    try:
        raw=urlopen(req,timeout=60).read()
    except Exception as e:
        raise SystemExit("Nasdaq access failed: "+str(e))
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    f=out/(a.symbol+"_"+a.start+"_"+a.end+".json"); f.write_bytes(raw)
    m={"source":"Nasdaq Historical Data API","url":url,"symbol":a.symbol,"start":a.start,"end":a.end,"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"status":"DOWNLOADED"}
    (out/"manifest.json").write_text(json.dumps(m,indent=2),encoding="utf-8")
    print(json.dumps(m,indent=2))
if __name__=="__main__": main()
