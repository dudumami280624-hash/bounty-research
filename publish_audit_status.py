#!/usr/bin/env python3
"""Publish bounded audit-status metadata only, not private source or secrets."""
import base64
import json
import os
from pathlib import Path
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parent
def read_report(name):
    try:
        value=json.loads((ROOT/name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"present":False}
    out={"present":True}
    if name=="audit.json":
        out["projects"]=[{"name":x.get("name"),"status":x.get("status"),
                          "solidity_files":x.get("solidity_files"),
                          "flags":len(x.get("review_flags",[]))}
                         for x in value.get("projects",[])][:25]
    elif name=="eligibility_status.json":
        out.update({k:value.get(k) for k in ("officially_verified_targets","ready_for_live_testing","confirmed_eligible_reports","confirmed_payouts_usd","payout_status","specific_pocs_executed","conditional_poc_tests_executed","conditional_poc_execution","specific_real_world_exploits_verified")})
    elif name=="submission_status.json":
        out.update({key:value.get(key) for key in ("mode","total","approved_for_submission","actual_submissions","payout_confirmed_usd")})
    elif name=="specific_poc_results.json":
        out.update({key:value.get(key) for key in ("execution","test_suite","tests_passed","tests_failed","conditional_simulation_only","real_world_exploit_verified","official_reward_token_callback_verified","ready_to_submit","returncode")})
    elif name=="validation_results.json":
        out["leads_recorded"]=value.get("leads_recorded")
        out["specific_pocs_executed"]=value.get("specific_pocs_executed")
        out["verified_vulnerabilities"]=value.get("verified_vulnerabilities")
        out["test_runs"]=[{"project":r.get("project"),"test_status":r.get("test_status"),"returncode":r.get("returncode")} for r in value.get("test_runs",[])][:25]
    elif name=="triage_results.json":
        out.update({key:value.get(key) for key in ("total_alerts","unique_alerts","needs_review","verified_vulnerabilities","ready_to_submit","payout_verified_usd")})
        out["severity_counts"]=value.get("severity_counts",{})
        out["review_queue"]=[{"id":x.get("id"),"check":x.get("check"),"impact":x.get("impact"),"scope_relevance":x.get("scope_relevance"),"reproduction":x.get("reproduction")} for x in value.get("findings",[]) if x.get("priority")=="review"][:30]
    elif name=="slither_results.json":
        out["projects"]=[{"name":x.get("name"),"status":x.get("status"),
                          "triage_flags":len(x.get("findings",[])),
                          "error_type":x.get("error_type"),
                          "error_excerpt":str(x.get("error_excerpt") or "")[-900:]}
                         for x in value.get("projects",[])][:25]
    else:
        out["error"]=str(value.get("error") or "")[:120]
        out["candidate_count"]=value.get("candidate_count",value.get("total_candidates"))
    return out

report={"time_utc":datetime.now(timezone.utc).isoformat(),
        "workflow_run_id":os.getenv("GITHUB_RUN_ID",""),
        "workflow_sha":os.getenv("GITHUB_SHA",""),
        "note":"Static triage flags are NOT verified vulnerabilities.",
        "reports":{name:read_report(name) for name in (
            "global_bounties.json","bugcrowd_bounties.json",
            "candidates.json","audit.json","slither_results.json","triage_results.json","validation_results.json","eligibility_status.json","specific_poc_results.json","submission_status.json")}}
token=os.environ["GITHUB_TOKEN"]
repo=os.environ["GITHUB_REPOSITORY"]
url=f"https://api.github.com/repos/{repo}/contents/status/audit_status.json"
headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json",
         "X-GitHub-Api-Version":"2022-11-28","User-Agent":"BountyResearch/1.0"}
sha=None
try:
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=12) as r:
        sha=json.loads(r.read(50000)).get("sha")
except urllib.error.HTTPError as err:
    if err.code!=404: raise
content=base64.b64encode((json.dumps(report,indent=2)+"\n").encode()).decode()
body={"message":"Update audit status [skip ci]","content":content,"branch":"main"}
if sha:body["sha"]=sha
req=urllib.request.Request(url,headers=headers,data=json.dumps(body).encode(),method="PUT")
with urllib.request.urlopen(req,timeout=20) as resp:
    print("Audit status published:",resp.status)
