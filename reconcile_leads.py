#!/usr/bin/env python3
"""Reconcile scoped leads with real executed sandbox evidence, fail closed."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(name):
    try:return json.loads((ROOT/name).read_text(encoding="utf-8"))
    except (OSError,ValueError):return {}
def reconcile(triage,poc):
    cases=[]
    for case in triage.get("findings",[]):
        if case.get("priority")!="review":continue
        row={k:case.get(k) for k in ("id","check","impact","scope_relevance")}
        row.update({"verified":False,"ready_to_submit":False,"poc_status":"not_executed",
                    "reason":"No finding-specific proof of real in-scope impact"})
        if (case.get("check")=="reentrancy-no-eth"
            and case.get("scope_relevance")=="direct_in_scope_source"
            and poc.get("execution")=="passed"):
            row["poc_status"]="conditional_synthetic_callback_reproduced"
            row["reason"]="Synthetic callback ERC20 only; production ZEN callback and exploitability not established"
        elif case.get("scope_relevance")=="not_established":
            row["reason"]="No confirmed relation to an official in-scope asset"
        elif case.get("scope_relevance")=="inherited_impact_must_be_proven":
            row["reason"]="Inherited implementation; impact on in-scope deployment not established"
        cases.append(row)
    return {"cases":cases,"lead_count":len(cases),
            "conditional_evidence_leads":sum(c["poc_status"]=="conditional_synthetic_callback_reproduced" for c in cases),
            "verified_vulnerabilities":0,"ready_to_submit":0}
def main():
    result=reconcile(load("triage_results.json"),load("specific_poc_results.json"))
    (ROOT/"lead_verification.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Per-lead evidence:",result["lead_count"],"conditional:",result["conditional_evidence_leads"],"verified:",result["verified_vulnerabilities"])
if __name__=="__main__":main()
