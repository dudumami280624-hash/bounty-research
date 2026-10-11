#!/usr/bin/env python3
"""Fail-closed bounty eligibility and payout tracking; no external target testing."""
import json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def policy(global_data,bugcrowd_data,triage_data,validation_data):
    candidates=global_data.get("candidates",[])
    bc=bugcrowd_data.get("candidates",[])
    findings=triage_data.get("findings",[])
    return {
      "checked_at_utc":datetime.now(timezone.utc).isoformat(),
      "source":"unofficial directory; not official permission",
      "candidate_count":len(candidates),"bugcrowd_candidates":len(bc),
      "officially_verified_targets":sum(x.get("open_and_authorized_verified") is True and x.get("cash_payment_verified") is True for x in candidates),
      "ready_for_live_testing":0,
      "confirmed_eligible_reports":0,
      "confirmed_payouts_usd":0,
      "payout_status":"unknown_no_verified_payment_records",
      "platform_tracking":{"HackerOne":"API connectivity only; no report or payment synchronization",
                           "Bugcrowd":"public directory only; no account API",
                           "Immunefi":"public candidate discovery only; no account API"},
      "gates":{"official_rules_and_assets":"not_verified","specific_reproduction":"not_verified",
               "impact_evidence":"not_verified","eligible_for_submission":False},
      "security_leads":sum(x.get("priority")=="review" for x in findings),
      "specific_pocs_executed":validation_data.get("specific_pocs_executed",0),
      "note":"No live target tests, submissions, or money transfers. Never infer authorization from repository or directory."
    }
def main():
    def read(name):
        try:return json.loads((ROOT/name).read_text(encoding="utf-8"))
        except (OSError,ValueError):return {}
    report=policy(read("global_bounties.json"),read("bugcrowd_bounties.json"),read("triage_results.json"),read("validation_results.json"))
    (ROOT/"eligibility_status.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print("Eligibility:",report["officially_verified_targets"],"officially verified; payout:",report["payout_status"])
if __name__=="__main__":main()
