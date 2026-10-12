#!/usr/bin/env python3
"""Reconcile scoped leads with real executed sandbox evidence, fail closed."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(name):
    try:return json.loads((ROOT/name).read_text(encoding="utf-8"))
    except (OSError,ValueError):return {}
def reconcile(triage,poc,fork=None):
    fork=fork if isinstance(fork,dict) else {}
    fork_tests=set(fork.get("tests_confirmed") or [])
    cases=[]
    for case in triage.get("findings",[]):
        if case.get("priority")!="review":continue
        row={k:case.get(k) for k in ("id","check","impact","scope_relevance")}
        row.update({"verified":False,"ready_to_submit":False,"poc_status":"not_executed",
                    "reason":"No finding-specific proof of real in-scope impact"})
        if (case.get("id")=="12ec614578dc"
            and case.get("check")=="divide-before-multiply"
            and "src/RewardAccumulator.sol" in case.get("description","")
            and poc.get("execution")=="passed"
            and poc.get("tests_passed",0)>=6
            and poc.get("named_tests_confirmed") is True
            and poc.get("source_commit")=="ab92502e9da98784dfe3bd3ef933d4e9345ff628"):
            row["poc_status"]="finding_specific_arithmetic_property_passed"
            row["reason"]="Foundry fuzz confirmed time-window grid in pinned source; no exploitable deviation demonstrated"
        elif (case.get("check")=="reentrancy-no-eth"
            and "RewardAccumulator.sendRewardsToStaker()" in case.get("description","")
            and "src/RewardAccumulator.sol" in case.get("description","")
            and fork.get("execution")=="passed"
            and "test_RealFork_ActualTokenTransferDoesNotCallbackReceiver" in fork_tests):
            row["poc_status"]="finding_specific_real_token_condition_excluded"
            row["reason"]="Actual deployed tZEN transfer on Horizen local fork did not callback receiver; synthetic malicious-token reentry prerequisite is absent"
        elif ("ZenStaker._fetchOrDeploySurrogate" in case.get("description","")
              and case.get("check")=="reentrancy-no-eth"
              and fork.get("execution")=="passed"
              and "test_RealFork_ActualTokenApproveDoesNotCallbackSpender" in fork_tests):
            row["poc_status"]="finding_specific_real_token_condition_excluded"
            row["reason"]="Actual deployed tZEN approve on Horizen local fork did not callback spender; token-callback prerequisite for surrogate-path reentry is absent"
        elif (case.get("check")=="reentrancy-no-eth"
            and "RewardAccumulator.sendRewardsToStaker()" in case.get("description","")
            and "src/RewardAccumulator.sol" in case.get("description","")
            and poc.get("execution")=="passed"):
            row["poc_status"]="related_sandbox_test_not_finding_specific"
            row["reason"]="Related synthetic callback test passed, but production tZEN callback condition has not yet been checked"
        elif ("ZenStaker._fetchOrDeploySurrogate" in case.get("description","")
              and case.get("check")=="reentrancy-no-eth"):
            row["reason"]="Surrogate constructor path requires actual-token callback validation on the authorized local fork"
        elif case.get("scope_relevance")=="not_established":
            row["reason"]="No confirmed relation to an official in-scope asset"
        elif case.get("scope_relevance")=="inherited_impact_must_be_proven":
            row["reason"]="Inherited implementation; impact on in-scope deployment not established"
        cases.append(row)
    return {"cases":cases,"lead_count":len(cases),
            "related_sandbox_test_leads":sum(c["poc_status"]=="related_sandbox_test_not_finding_specific" for c in cases),
            "finding_specific_pocs_executed":sum(c["poc_status"]=="finding_specific_arithmetic_property_passed" for c in cases),
            "verified_vulnerabilities":0,"ready_to_submit":0}
def main():
    result=reconcile(load("triage_results.json"),load("specific_poc_results.json"),load("deployment_fork_results.json"))
    (ROOT/"lead_verification.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Per-lead evidence:",result["lead_count"],"conditional:",result["related_sandbox_test_leads"],"verified:",result["verified_vulnerabilities"])
if __name__=="__main__":main()
