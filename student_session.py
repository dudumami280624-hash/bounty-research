"""Supervised offline training session: assignment -> evidence -> Forge -> private record.
No external targets, wallet, server, or student personal data required.
"""
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from student_blind import allocate
from student_progress import assess

def load_lesson_knowledge(index_path, lesson):
    """Read curated teaching context; never treat advisory text as student evidence."""
    if index_path is None:
        return {"status": "not_configured", "entries": []}
    path = Path(index_path)
    if not path.is_file():
        return {"status": "missing", "entries": []}
    index = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(index, dict):
        raise ValueError("knowledge index must be an object")
    label = str(lesson).lower()
    topic = "reentrancy" if "cei" in label or "外部调用" in label or "reentr" in label else ("access" if "auth" in label else ("arithmetic" if "arithmetic" in label else label))
    entries = []
    for key, value in sorted(index.items()):
        if not isinstance(value, dict) or value.get("source") != "curated-case":
            continue
        content = " ".join(str(value.get(k) or "") for k in ("title", "category", "root_cause", "invariant"))
        if topic in content.lower():
            entries.append({"id": key, "title": value.get("title"), "invariant": value.get("invariant"), "verification": value.get("verification")})
    return {"status": "matched" if entries else "no_match", "entries": entries}

def run_session(seed, evidence, output, runner=subprocess.run, knowledge_index=None):
    assignment=allocate(seed)
    knowledge = load_lesson_knowledge(knowledge_index, assignment["id"] + " " + assignment["title"])\n    evidence=dict(evidence)
    evidence.setdefault("lesson",assignment["id"])
    evidence.setdefault("exercise",assignment["title"])
    # The learner must supply their own explanation and reproduction/repair evidence.
    review=assess(evidence)
    try:
        proc=runner(["forge","test","--root","student_lab","--match-contract","ReentrancyLessonTest","-vv"],
                    capture_output=True,text=True,timeout=180)
        test={"executed":True,"passed":proc.returncode==0,"returncode":proc.returncode,
              "log_tail":(proc.stdout+"\n"+proc.stderr)[-5000:]}
    except (FileNotFoundError,subprocess.TimeoutExpired) as exc:
        test={"executed":False,"passed":False,"error":type(exc).__name__}
    result={"assignment":assignment,"knowledge":knowledge,"assessment":review,"forge":test,
            "completed":bool(test["passed"] and review["verified"]),
            "recorded_at_utc":datetime.now(timezone.utc).isoformat(),
            "feedback":"请提交真实复现、修复及回归日志，交由监护人审核。" if not review["verified"] else
                       ("合约测试未通过，请根据测试日志修复并重试。" if not test["passed"] else "证据审核和本地测试均通过；仍需单独完成未知合约盲测。")}
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--seed",required=True,help="local session seed; no personal data")
    p.add_argument("--evidence",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--knowledge-index",type=Path)\n    a=p.parse_args()
    result=run_session(a.seed,json.loads(a.evidence.read_text(encoding="utf-8")),a.output,knowledge_index=a.knowledge_index)
    print(json.dumps({"completed":result["completed"],"forge":result["forge"]["passed"],
                      "assessment":result["assessment"]["status"],"feedback":result["feedback"]},ensure_ascii=False))
if __name__=="__main__":main()
