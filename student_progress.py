"""Local-only evidence-based lab progress. No identity or network required."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = ("lesson", "exercise", "reproduction", "repair", "regression", "explanation")
def assess(entry):
    missing=[k for k in REQUIRED if not isinstance(entry.get(k),str) or not entry[k].strip()]
    if missing:
        return {"status":"incomplete","missing":missing,"verified":False}
    if entry.get("independent") is not True:
        return {"status":"assisted_or_unknown","missing":[],"verified":False}
    if entry.get("reviewer_approved") is not True:
        return {"status":"awaiting_review","missing":[],"verified":False}
    return {"status":"reviewed_evidence","missing":[],"verified":True,
            "note":"Evidence reviewed; not proof of independent discovery without an unseen blind task."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--submission",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    raw=json.loads(a.submission.read_text(encoding="utf-8"))
    if not isinstance(raw,dict):
        raise ValueError("submission must be a JSON object")
    result=assess(raw)
    result["checked_at_utc"]=datetime.now(timezone.utc).isoformat()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__":
    main()
