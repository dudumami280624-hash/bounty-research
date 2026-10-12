#!/usr/bin/env python3
"""Deterministic, auditable scope-first classification of pinned Horizen alerts."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
# Manually inspected source paths; scope exclusion is not a proof of false positive.
EXCLUDED={
 "df03bce1714d":("src/notifiers/TransferFromRewardNotifier.sol","auxiliary notifier, not listed in pinned scope"),
 "972ce92ec305":("src/script/DeployBase.sol","deployment script, not an onchain affected contract"),
 "00f846e1adf2":("src/notifiers/TransferRewardNotifier.sol","auxiliary notifier, not listed in pinned scope"),
 "016430194a14":("src/extensions/StakerDelegateSurrogateVotes.sol","different surrogate extension, not used by ZenStaker"),
}
DIRECT={
 "12ec614578dc":"src/RewardAccumulator.sol",
 "1429588799f6":"src/ZenStaker.sol",
 "8e48c2a2804a":"src/RewardAccumulator.sol",
}
INHERITED={"be1c1609e7b5","20f0b85eac0b","98fdd9e27146","b241ec50cd2c","d51386d2891a","9d74cbad990c"}
def classify(findings):
    out=[]
    for row in findings:
        if row.get("priority")!="review":continue
        ident=row["id"];desc=row.get("description","")
        if ident in EXCLUDED:
            path,reason=EXCLUDED[ident]
            verdict="not_in_direct_scope";condition=path in desc
        elif ident in DIRECT:
            path=DIRECT[ident];reason="direct in-scope Solidity file, exploitability not established"
            verdict="in_scope_requires_poc";condition=path in desc
        elif ident in INHERITED:
            path="src/Staker.sol" if ident!="9d74cbad990c" else "src/DelegationSurrogate.sol"
            reason="inherited or used-by-in-scope pathway; impact requires proof"
            verdict="inherited_requires_impact_proof";condition=path in desc
        else:
            path="";reason="unreviewed id";verdict="unclassified";condition=False
        if not condition:verdict="classification_blocked_source_mismatch"
        out.append({"id":ident,"check":row.get("check"),"location":path,
                    "scope_verdict":verdict,"reason":reason,"verified_vulnerability":False,
                    "eligible_report":False})
    summary={"total_leads":len(out),"excluded_from_direct_scope":sum(x["scope_verdict"]=="not_in_direct_scope" for x in out),
             "direct_requires_poc":sum(x["scope_verdict"]=="in_scope_requires_poc" for x in out),
             "inherited_requires_proof":sum(x["scope_verdict"]=="inherited_requires_impact_proof" for x in out),
             "classification_errors":sum(x["scope_verdict"] in ("unclassified","classification_blocked_source_mismatch") for x in out),
             "verified_vulnerabilities":0,"findings":out}
    return summary
def main():
    raw=json.loads((ROOT/"triage_results.json").read_text())
    result=classify(raw.get("findings",[]))
    (ROOT/"scope_review.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("Scope review:",{k:v for k,v in result.items() if k!="findings"})
    if result["classification_errors"] or result["total_leads"]!=13:raise SystemExit(1)
if __name__=="__main__":main()
