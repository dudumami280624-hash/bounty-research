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
    elif name=="frontend_scope_results.json":
        out.update({k:value.get(k) for k in ("source_repo","source_commit","scope",
                   "execution","source_pinned","security_vulnerabilities_verified",
                   "bounty_reports_ready","dependency_advisory_counts")})
        out["checks"]={k:{"ok":v.get("ok"),"returncode":v.get("code")}
                       for k,v in value.get("checks",{}).items()}
    elif name=="official_scope_status.json":
        out.update({k:value.get(k) for k in (
            "verified_at_utc","program","scope_url","verified_count","status","reason",
            "live_testing_permitted","local_source_review_only")})
    elif name=="eligibility_status.json":
        out.update({k:value.get(k) for k in ("officially_verified_targets","official_scope_records","official_scope_record_only_not_live_eligibility","ready_for_live_testing","confirmed_eligible_reports","confirmed_payouts_usd","payout_status","specific_pocs_executed","conditional_poc_tests_executed","conditional_poc_execution","specific_real_world_exploits_verified")})
    elif name=="report_build_status.json":
        out["verified_reports_generated"]=value.get("verified_reports_generated",0)
        out["blocked_count"]=len(value.get("blocked",[]))
        out["report_ids"]=[x.get("id") for x in value.get("reports",[])][:20]
    elif name=="acceptance_status.json":
        out.update({k:value.get(k) for k in ("passed","total","full_acceptance","foundry_control_tests","business_outcomes")})
        out["stages"]=[{k:s.get(k) for k in ("stage","name","status","reason")} for s in value.get("stages",[])][:6]
    elif name=="lead_verification.json":
        out.update({k:value.get(k) for k in ("lead_count","related_sandbox_test_leads","finding_specific_pocs_executed","verified_vulnerabilities","ready_to_submit")})
        out["cases"]=[{k:r.get(k) for k in ("id","check","scope_relevance","poc_status","verified")} for r in value.get("cases",[])][:20]
    elif name=="submission_status.json":
        out.update({key:value.get(key) for key in ("mode","total_alerts","review_leads","approved_for_submission","actual_submissions","payout_confirmed_usd")})
    elif name=="deployment_fork_results.json":
        out.update({k:value.get(k) for k in ("execution","chain_id","source_commit",
            "tests_passed","tests_expected","real_deployment_state_checked",
            "real_world_exploit_verified","any_public_chain_transaction_broadcast",
            "returncode","error_type")})
        out["log_excerpt"]=str(value.get("log_excerpt") or "")[-1000:]
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
            "candidates.json","audit.json","slither_results.json","triage_results.json","validation_results.json","eligibility_status.json","specific_poc_results.json","submission_status.json","lead_verification.json","acceptance_status.json","official_scope_status.json","report_build_status.json","deployment_fork_results.json","frontend_scope_results.json")}}
token=os.environ["GITHUB_TOKEN"]
repo=os.environ["GITHUB_REPOSITORY"]
url=f"https://api.github.com/repos/{repo}/contents/status/audit_status.json"
headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json",
         "X-GitHub-Api-Version":"2022-11-28","User-Agent":"BountyResearch/1.0"}
sha=None
try:
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=12) as r:
        existing=json.loads(r.read(300000))
        sha=existing.get("sha")
        prior=json.loads(base64.b64decode(existing.get("content","")).decode("utf-8"))
        prior_run=int(prior.get("workflow_run_id") or 0)
        current_run=int(os.getenv("GITHUB_RUN_ID") or 0)
        if prior_run>current_run and current_run>0:
            print("Stale audit status skipped:",current_run,"<",prior_run)
            raise SystemExit(0)
except urllib.error.HTTPError as err:
    if err.code!=404: raise
content=base64.b64encode((json.dumps(report,indent=2)+"\n").encode()).decode()
body={"message":"Update audit status [skip ci]","content":content,"branch":"main"}
if sha:body["sha"]=sha
req=urllib.request.Request(url,headers=headers,data=json.dumps(body).encode(),method="PUT")
with urllib.request.urlopen(req,timeout=20) as resp:
    print("Audit status published:",resp.status)
