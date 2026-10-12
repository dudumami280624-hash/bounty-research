#!/usr/bin/env python3
"""Fail-closed bounty eligibility and payout tracking; no external target testing."""
import json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def policy(global_data,bugcrowd_data,triage_data,validation_data,poc_data=None,official_scope=None):
    official_scope=official_scope if isinstance(official_scope,dict) else {}
    poc_data = poc_data if isinstance(poc_data,dict) else {}
    candidates=global_data.get("candidates",[])
    bc=bugcrowd_data.get("candidates",[])
    findings=triage_data.get("findings",[])
    # Unofficial directory records cannot self-certify program permission.
    candidates = candidates if isinstance(candidates, list) else []
    bc = bc if isinstance(bc, list) else []
    findings = findings if isinstance(findings, list) else []
    ignored_claims = sum(isinstance(x, dict) and (
        x.get("open_and_authorized_verified") is True or
        x.get("cash_payment_verified") is True) for x in candidates)
    return {
      "checked_at_utc":datetime.now(timezone.utc).isoformat(),
      "source":"unofficial directory; not official permission",
      "candidate_count":len(candidates),"bugcrowd_candidates":len(bc),
      "officially_verified_targets":0,
      "official_scope_records":1 if official_scope.get("official_scope_url") and official_scope.get("pinned_commit")== "ab92502e9da98784dfe3bd3ef933d4e9345ff628" else 0,
      "official_scope_record_only_not_live_eligibility":True,
      "candidate_verification_claims_ignored":ignored_claims,
      "official_verification_basis":"none: independent official-source verification records not implemented",
      "official_program_scope":{"Horizen":"official scope checked; only listed assets and demonstrated in-scope impact qualify",
          "pinned_commit":"ab92502e9da98784dfe3bd3ef933d4e9345ff628",
          "direct_source_files":["src/ZenStaker.sol","src/RewardAccumulator.sol"],
          "source_url":"https://immunefi.com/bug-bounty/horizen/scope/",
          "local_only_poc":True,"public_chain_attack":False},
      "ready_for_live_testing":0,
      "confirmed_eligible_reports":0,
      "confirmed_payouts_usd":0,
      "payout_status":"unknown_no_verified_payment_records",
      "platform_tracking":{"HackerOne":"API connectivity only; no report or payment synchronization",
                           "Bugcrowd":"public directory only; no account API",
                           "Immunefi":"public candidate discovery only; no account API"},
      "gates":{"official_rules_and_assets":"Horizen selected pinned source verified; every specific finding still requires impact and known-issue checks","specific_reproduction":"not_verified",
               "impact_evidence":"not_verified","eligible_for_submission":False},
      "security_leads":sum(isinstance(x,dict) and x.get("priority")=="review" for x in findings),
      "conditional_poc_tests_executed":poc_data.get("tests_passed",0) if poc_data.get("execution")=="passed" else 0,
      "conditional_poc_execution":poc_data.get("execution","not_run"),
      "specific_real_world_exploits_verified":0,
      "specific_pocs_executed":0,
      "note":"Third-party directory flags cannot authorize testing. No live target tests, submissions, or money transfers."
    }
def main():
    def read(name):
        try:return json.loads((ROOT/name).read_text(encoding="utf-8"))
        except (OSError,ValueError):return {}
    report=policy(read("global_bounties.json"),read("bugcrowd_bounties.json"),read("triage_results.json"),read("validation_results.json"),read("specific_poc_results.json"),read("scope_horizen.json"))
    (ROOT/"eligibility_status.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print("Eligibility:",report["officially_verified_targets"],"officially verified; payout:",report["payout_status"])
if __name__=="__main__":main()
