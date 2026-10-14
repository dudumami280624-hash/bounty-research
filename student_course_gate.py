"""Curriculum gate: only actual graded and tested evidence unlocks lessons."""
import argparse
import json
from pathlib import Path
from student_curriculum import curriculum

def evaluate(records):
    status={}
    for course in curriculum()["courses"]:
        ident=course["id"]
        deps=all(status.get(x,{}).get("passed") is True for x in course["prerequisites"])
        record=records.get(ident,{})
        assessment=record.get("assessment",{})
        lab=record.get("lab",{})
        has_fixture=bool(course["test_contract"])
        passed=bool(deps and has_fixture and assessment.get("independent_completion_verified") is True
                    and lab.get("executed") is True and lab.get("passed") is True
                    and record.get("human_review_approved") is True)
        status[ident]={"unlocked":deps,"has_lab_fixture":has_fixture,"passed":passed,
                       "needs":"real independent assessment, Forge evidence and review" if not passed else None}
    return status
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--evidence",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    evidence=json.loads(a.evidence.read_text(encoding="utf-8"))
    result=evaluate(evidence)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
