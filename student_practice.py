"""Offline iterative practice; preserves learner attempts without inventing independence."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from student_lab import LESSONS, grade

def practice(lesson, attempts, output):
    if lesson not in LESSONS:
        raise ValueError("unknown lesson")
    if not isinstance(attempts, list) or not attempts:
        raise ValueError("actual learner attempts required")
    history=[]
    for i, answer in enumerate(attempts, 1):
        if not isinstance(answer, str):
            raise ValueError("attempt must be text")
        feedback=grade(lesson, answer)
        history.append({"attempt":i,"answer":answer,"feedback":feedback,"needs_revision":bool(feedback["missing"])})
    result={"lesson":lesson,"prompt":LESSONS[lesson]["prompt"],"attempts":history,
            "revision_observed":len(history)>1,
            "improved_keyword_coverage":len(history)>1 and len(history[-1]["feedback"]["matched"])>len(history[0]["feedback"]["matched"]),
            "independent_completion_verified":False,"review_required":True,
            "recorded_at_utc":datetime.now(timezone.utc).isoformat()}
    path=Path(output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--lesson",required=True,choices=LESSONS)
    p.add_argument("--attempts",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    result=practice(a.lesson,json.loads(a.attempts.read_text(encoding="utf-8")),a.output)
    print(json.dumps({"attempts":len(result["attempts"]),"improved_keyword_coverage":result["improved_keyword_coverage"],"independent_completion_verified":False},ensure_ascii=False))
if __name__=="__main__":
    main()
