#!/usr/bin/env python3
"""Fetch SEC 8-K filing dates as a free earnings-disclosure control."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
from urllib.request import Request,urlopen

CIKS={"AAPL":"0000320193","MSFT":"0000789019","AMZN":"0001018724","GOOGL":"0001652044","META":"0001326801","NVDA":"0001045810"}

def main():
 p=argparse.ArgumentParser(); p.add_argument("--start",default="2021-01-01"); p.add_argument("--end",default="2025-12-31"); p.add_argument("--out",default="knowledge/market-psychology/data/sec-edgar/MAJOR_CONSTITUENT_8K_DATES.csv"); a=p.parse_args()
 Path(a.out).parent.mkdir(parents=True,exist_ok=True); rows=[]
 for ticker,cik in CIKS.items():
  req=Request(f"https://data.sec.gov/submissions/CIK{cik}.json",headers={"User-Agent":"The Market Mind research contact@example.com"})
  data=json.loads(urlopen(req,timeout=90).read()); r=data["filings"]["recent"]
  for form,date,acc in zip(r["form"],r["filingDate"],r["accessionNumber"]):
   if form=="8-K" and a.start<=date<=a.end: rows.append((ticker,date,acc))
 with open(a.out,"w",newline="") as f:
  w=csv.writer(f); w.writerow(["ticker","filing_date","accession_number"]); w.writerows(rows)
 print("rows",len(rows),"output",a.out)
if __name__=="__main__": main()
