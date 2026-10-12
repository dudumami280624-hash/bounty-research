#!/usr/bin/env python3
"""Scope-first review using Slither source mappings; no fixed IDs or fixed lead count."""
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DIRECT={"src/ZenStaker.sol","src/RewardAccumulator.sol"}
INHERITED={"src/Staker.sol","src/DelegationSurrogate.sol"}
# These are not listed as independent assets in the source-pinned Horizen scope.
AUXILIARY={
    "src/notifiers/TransferFromRewardNotifier.sol",
    "src/notifiers/TransferRewardNotifier.sol",
    "src/script/DeployBase.sol",
    "src/extensions/StakerDelegateSurrogateVotes.sol",
}
PATTERN=re.compile(r"(?:src|script|test|lib|node_modules)/[\w./-]+\.sol")

def source_paths(row):
    mapped=row.get("locations",[])
    if isinstance(mapped,list):
        result={x["path"] for x in mapped if isinstance(x,dict) and isinstance(x.get("path"),str)}
        if result:return result
    # Compatibility with archived detections without structured source mapping.
    return set(PATTERN.findall(row.get("description","")))

def classify(findings):
    rows=[]
    for case in findings:
        if case.get("priority")!="review":continue
        paths=source_paths(case)
        if paths & DIRECT:
            verdict="in_scope_requires_poc"
            reason="Direct scoped source. Still requires finding-specific proof of exploitable impact."
        elif paths & INHERITED:
            verdict="inherited_requires_impact_proof"
            reason="Prove actual inherited impact on deployed ZenStaker before treating as eligible."
        elif paths and paths <= AUXILIARY:
            verdict="not_in_direct_scope"
            reason="Standalone auxiliary or deployment source is not a separately listed scoped target."
        else:
            verdict="scope_not_established"
            reason="No confirmed matching asset. Not a verified vulnerability or submission candidate."
        rows.append({"id":case.get("id"),"check":case.get("check"),
                     "locations":sorted(paths),"scope_verdict":verdict,"reason":reason,
                     "verified_vulnerability":False,"eligible_report":False})
    counts={key:sum(x["scope_verdict"]==key for x in rows) for key in (
        "not_in_direct_scope","in_scope_requires_poc",
        "inherited_requires_impact_proof","scope_not_established")}
    return {"total_leads":len(rows),"excluded_from_direct_scope":counts["not_in_direct_scope"],
            "direct_requires_poc":counts["in_scope_requires_poc"],
            "inherited_requires_proof":counts["inherited_requires_impact_proof"],
            "scope_not_established":counts["scope_not_established"],
            "classification_errors":0,"verified_vulnerabilities":0,"findings":rows}

def main():
    raw=json.loads((ROOT/"triage_results.json").read_text(encoding="utf-8"))
    result=classify(raw.get("findings",[]))
    (ROOT/"scope_review.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("Scope review:",{k:v for k,v in result.items() if k!="findings"})

if __name__=="__main__":main()
