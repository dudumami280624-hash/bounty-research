#!/usr/bin/env python3
"""Publish allowlisted, credential-free connection status to private GitHub repository."""
import base64
import json
import os
import pathlib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
source = ROOT / "hackerone_connection.json"
if not source.exists():
    raise SystemExit("No status JSON to publish")

raw = json.loads(source.read_text(encoding="utf-8"))
allowed = ("time_utc", "service", "mode", "connected", "status", "http_status", "missing", "error_type")
safe = {key: raw[key] for key in allowed if key in raw}
safe["note"] = "Only status metadata. A successful check has connected=true and status=verified."
encoded = base64.b64encode((json.dumps(safe, indent=2, ensure_ascii=False) + "\n").encode()).decode()

token = os.getenv("GITHUB_TOKEN", "")
repo = os.getenv("GITHUB_REPOSITORY", "")
if not token or len(repo.split("/")) != 2:
    raise SystemExit("Missing GitHub token or repository identifier")
url = "https://api.github.com/repos/" + repo + "/contents/status/hackerone_connection.json"
headers = {"Authorization": "Bearer " + token,
           "Accept": "application/vnd.github+json",
           "X-GitHub-Api-Version": "2022-11-28",
           "Content-Type": "application/json",
           "User-Agent": "BountyResearchStatus/1.0"}
sha = None
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        sha = json.loads(resp.read(100000)).get("sha")
except urllib.error.HTTPError as error:
    if error.code != 404:
        print("Status lookup failed with HTTP", error.code)
        raise SystemExit(1)
body = {"message": "Update HackerOne connection verification status [skip ci]",
        "content": encoded, "branch": "main"}
if sha:
    body["sha"] = sha
req = urllib.request.Request(url, headers=headers, data=json.dumps(body).encode(), method="PUT")
try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        print("Published credential-free status; HTTP:", resp.status)
except urllib.error.HTTPError as error:
    print("Status publication failed with HTTP", error.code)
    raise SystemExit(1)

# Publish only IDs, basic states and coverage from the real provider report sync.
source_reports=ROOT/"hackerone_reports.json"
if source_reports.is_file():
    raw_reports=json.loads(source_reports.read_text(encoding="utf-8"))
    permitted_states={"new","triaged","needs-more-info","needs_more_info","resolved",
                      "informative","not-applicable","not_applicable","duplicate",
                      "spam","closed","pending","open","unknown"}
    safe_entries=[]
    for item in raw_reports.get("reports",[])[:100]:
        if (isinstance(item,dict) and
            isinstance(item.get("report_id"),str) and item["report_id"].isdigit() and
            item.get("state") in permitted_states):
            safe_entries.append({"report_id":item["report_id"],"state":item["state"]})
    safe_report={key:raw_reports.get(key) for key in (
        "time_utc","platform","mode","sync_status","coverage","reports_seen",
        "report_states","error_type","payout_tracking_status")}
    safe_report["reports"]=safe_entries
    safe_report["payouts_verified_usd"]=0
    target_url="https://api.github.com/repos/"+repo+"/contents/status/hackerone_reports.json"
    current_sha=None
    try:
        with urllib.request.urlopen(urllib.request.Request(target_url,headers=headers),timeout=15) as res:
            current_sha=json.loads(res.read(300000)).get("sha")
    except urllib.error.HTTPError as error:
        if error.code!=404:raise
    request_body={"message":"Update read-only HackerOne report states [skip ci]",
                  "content":base64.b64encode((json.dumps(safe_report,indent=2)+"\n").encode()).decode(),
                  "branch":"main"}
    if current_sha:request_body["sha"]=current_sha
    req=urllib.request.Request(target_url,headers=headers,
        data=json.dumps(request_body).encode(),method="PUT")
    with urllib.request.urlopen(req,timeout=20) as res:
        print("Published sanitized HackerOne report states:",res.status)
