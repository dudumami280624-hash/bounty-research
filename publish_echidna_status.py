#!/usr/bin/env python3
"""Publish upstream Echidna's actual run verdict; never invent security findings."""
import base64,json,os,urllib.request,urllib.error
from datetime import datetime,timezone
from pathlib import Path

path=Path("echidna-results.json")
raw={}
if path.exists():
    try:
        raw=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError):
        pass
tests=raw.get("tests",[]) if isinstance(raw,dict) else []
tests=tests if isinstance(tests,list) else []
outcome=os.getenv("FUZZ_STEP_OUTCOME","unknown")
record={
 "time_utc":datetime.now(timezone.utc).isoformat(),
 "workflow_run_id":os.getenv("GITHUB_RUN_ID",""),
 "workflow_sha":os.getenv("GITHUB_SHA",""),
 "upstream_engine":"crytic/echidna-action@v2",
 "upstream_step_outcome":outcome,
 "raw_campaign_present":bool(raw),
 "raw_campaign_success":raw.get("success") if isinstance(raw,dict) else None,
 "properties_seen":len(tests),
 "property_statuses":[{"name":str(t.get("name",""))[:100],"status":str(t.get("status",""))[:30]} for t in tests if isinstance(t,dict)][:30],
 "source_commit":"ab92502e9da98784dfe3bd3ef933d4e9345ff628",
 "real_world_exploit_verified":False,
 "ready_to_submit":False,
}
# A successful step without an inspectable result is not a verified campaign.
record["campaign_verified_passed"]=(outcome=="success" and
    record["raw_campaign_present"] and record["raw_campaign_success"] is True and
    record["properties_seen"]>=3 and
    all(t["status"]=="passed" for t in record["property_statuses"]))
print("Echidna:",{k:v for k,v in record.items() if k not in ("property_statuses",)})
token=os.environ["GITHUB_TOKEN"]
repo=os.environ["GITHUB_REPOSITORY"]
url=f"https://api.github.com/repos/{repo}/contents/status/echidna_status.json"
headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json",
         "X-GitHub-Api-Version":"2022-11-28","User-Agent":"BountyResearch-Echidna/1.0"}
sha=None
try:
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=12) as response:
        sha=json.loads(response.read(40000)).get("sha")
except urllib.error.HTTPError as exc:
    if exc.code!=404:raise
body={"message":"Record upstream Echidna fuzz outcome [skip ci]",
      "content":base64.b64encode((json.dumps(record,indent=2)+"\n").encode("utf-8")).decode("ascii"),
      "branch":"main"}
if sha:body["sha"]=sha
request=urllib.request.Request(url,headers=headers,data=json.dumps(body).encode("utf-8"),method="PUT")
with urllib.request.urlopen(request,timeout=20) as result:
    print("Echidna status saved:",result.status)
