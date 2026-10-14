"""Two real model invocations, with persisted first-session learning evidence."""
import argparse
import json
from pathlib import Path
from student_learning_pipeline import run_once

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--model",required=True)
    p.add_argument("--knowledge",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    root=Path(a.out)
    root.mkdir(parents=True,exist_ok=True)
    records=[]
    for n in (1,2):
        records.append(run_once(a.model,a.knowledge,root/"memory.json",root/str(n),"reentrancy-01"))
    result={"sessions":len(records),"knowledge_used":records[0]["knowledge_context_sent"],
            "memory_reused":records[1]["prior_failure_context_sent"],
            "foundry_passed":[r["lab"]["passed"] for r in records],
            "graduated":bool(json.loads((root/"memory.json").read_text())["verified_courses"])}
    (root/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
    if not result["knowledge_used"] or not all(result["foundry_passed"]) or result["graduated"]:
        raise SystemExit("Real two-session evidence invalid")
if __name__=="__main__":
    main()
