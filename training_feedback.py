"""Generate evidence-grounded next lessons from real lab reports.

Lessons are proposals for offline testing, never verified discoveries.
"""
import json,sys
from pathlib import Path

def lessons(metrics, capabilities):
    m=json.loads(Path(metrics).read_text())
    c=json.loads(Path(capabilities).read_text())
    items=[]
    if m.get("fn",0)>0:
        items.append({"priority":1,"lesson":"Investigate missed positives","evidence":{"fn":m["fn"]},"experiment":"Add an independent positive fixture and compare scanner detector traces","acceptance":"False negatives decrease without increased false positives"})
    if m.get("fp",0)>0:
        items.append({"priority":1,"lesson":"Investigate false positives","evidence":{"fp":m["fp"]},"experiment":"Compare safe state-update ordering and detector source locations","acceptance":"False positives decrease without decreased recall"})
    t=c.get("transfer",{})
    if not t.get("transfer_verified"):
        items.append({"priority":2,"lesson":"Expand independent transfer evaluation","evidence":{"families":t.get("independent_families",0)},"experiment":"Add unseen positive and negative fixtures from distinct public lab families","acceptance":"At least two independent positive and two negative families, with reported precision and recall"})
    u=c.get("understanding",{})
    if not u.get("independently_verified"):
        items.append({"priority":2,"lesson":"Verify causal explanation","evidence":{"curated_cases":u.get("cases",0)},"experiment":"Check invariant violations and patch behavior with isolated EVM assertions","acceptance":"Recorded vulnerable-versus-fixed execution evidence"})
    if not items:
        items.append({"priority":3,"lesson":"Holdout regression","experiment":"Test new unseen fixtures without changing labels or thresholds","acceptance":"No metric regression"})
    return {"status":"lesson_proposals_not_auto_learned","lessons":items}

if __name__=="__main__":
    result=lessons(sys.argv[1],sys.argv[2])
    Path(sys.argv[3]).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False))
