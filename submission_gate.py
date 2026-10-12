#!/usr/bin/env python3
"""Local-only submission eligibility check. Never posts anything to external platforms."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
GATES=("verified","bounty_scope_verified","known_issue_checked","impact_verified","poc_passed","explicit_submission_approved")
def ready(case):
    return isinstance(case,dict) and all(case.get(k) is True for k in GATES) and isinstance(case.get("evidence_path"),str) and case["evidence_path"].startswith("evidence/") and ".." not in case["evidence_path"]
def main():
    try:cases=json.loads((ROOT/"triage_results.json").read_text(encoding="utf-8")).get("findings",[])
    except (ValueError,OSError):cases=[]
    review_cases=[x for x in cases if isinstance(x,dict) and x.get("priority")=="review"]
    result={"mode":"drafts_only","total_alerts":len(cases),"review_leads":len(review_cases),
            "approved_for_submission":sum(ready(x) for x in review_cases),
            "actual_submissions":0,"payout_confirmed_usd":0,
            "note":"Requires evidence and explicit submission approval; this script never sends network requests."}
    (ROOT/"submission_status.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print("Submission eligibility:",result["approved_for_submission"],"of",result["review_leads"])
if __name__=="__main__":main()
