#!/usr/bin/env python3
"""Read-only HackerOne report-state sync. No disclosure text or credentials saved."""
import base64
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT=Path(__file__).resolve().parent
URL="https://api.hackerone.com/v1/hackers/me/reports?page%5Bsize%5D=25"
MAX_PAGES=4
ALLOWED_STATES={"new","triaged","needs-more-info","needs_more_info",
                "resolved","informative","not-applicable","not_applicable",
                "duplicate","spam","closed","pending","open","unknown"}

def sanitize_report(item):
    if not isinstance(item,dict):
        return None
    ident=item.get("id")
    attrs=item.get("attributes")
    if not isinstance(ident,(int,str)) or not str(ident).isdigit():
        return None
    attrs=attrs if isinstance(attrs,dict) else {}
    raw=attrs.get("state")
    # Unknown states remain unknown; no speculative acceptance or payout.
    state=raw.strip().lower() if isinstance(raw,str) else "unknown"
    if state not in ALLOWED_STATES:
        state="unknown"
    return {"report_id":str(ident),"state":state}

def parse_page(data):
    if not isinstance(data,dict) or not isinstance(data.get("data"),list):
        raise ValueError("Invalid HackerOne reports API response")
    records=[sanitize_report(x) for x in data["data"]]
    records=[x for x in records if x is not None]
    # Fail closed if the provider changed its schema, not a false 0-report.
    if len(records)!=len(data["data"]):
        raise ValueError("Unexpected HackerOne report shape")
    links=data.get("links") or {}
    next_url=links.get("next") if isinstance(links,dict) else None
    if next_url and (not isinstance(next_url,str) or urlparse(next_url).hostname!="api.hackerone.com" or urlparse(next_url).scheme!="https"):
        raise ValueError("Untrusted pagination URL")
    return records,next_url

def summarize(pages):
    items={}
    for page in pages:
        records,_=parse_page(page)
        for r in records:items[r["report_id"]]=r
    entries=sorted(items.values(),key=lambda x:int(x["report_id"]))
    states={}
    for r in entries:states[r["state"]]=states.get(r["state"],0)+1
    return {"reports_seen":len(entries),"report_states":states,
            "reports":entries,"payouts_verified_usd":0,
            "payout_tracking_status":"not_verified_by_reports_endpoint"}

def main():
    status={"time_utc":datetime.now(timezone.utc).isoformat(),
            "platform":"HackerOne","mode":"READ_ONLY","sync_status":"not_run",
            "reports_seen":0,"report_states":{},"reports":[],
            "payouts_verified_usd":0,
            "payout_tracking_status":"no_payment_records"}
    user=os.getenv("HACKERONE_USERNAME","").strip()
    token=os.getenv("HACKERONE_API_TOKEN","").strip()
    try:
        if not user or not token:
            raise ValueError("Credentials unavailable")
        auth=base64.b64encode((user+":"+token).encode()).decode()
        url=URL
        pages=[]
        for page_number in range(MAX_PAGES):
            request=urllib.request.Request(url,headers={
                "Authorization":"Basic "+auth,
                "Accept":"application/json",
                "User-Agent":"BountyResearchReadOnly/1.0"
            },method="GET")
            with urllib.request.urlopen(request,timeout=20) as response:
                if response.status!=200:raise ValueError("Unexpected provider status")
                page=json.loads(response.read(3_000_000))
            _,next_url=parse_page(page)
            pages.append(page)
            if not next_url:break
            url=next_url
        result=summarize(pages)
        status.update(result)
        status["sync_status"]="success"
        status["coverage"]="complete" if not next_url else "partial_first_100_reports"
    except Exception as e:
        status["sync_status"]="failed"
        status["error_type"]=type(e).__name__
        status["coverage"]="unknown"
    (ROOT/"hackerone_reports.json").write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n")
    print("HackerOne report sync:",status["sync_status"],"reports:",status["reports_seen"],
          "coverage:",status["coverage"])
    if status["sync_status"]!="success":raise SystemExit(1)
if __name__=="__main__":main()
