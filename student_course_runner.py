"""Run an offline course session with real model, feedback, and existing Foundry lab."""
import argparse
import json
import subprocess
from pathlib import Path
from student_curriculum import curriculum
from student_revision_loop import revise
from student_course_gate import evaluate

def run(lesson,model,output,knowledge_index=None):
    courses={x["id"]:x for x in curriculum()["courses"]}
    if lesson not in courses:raise ValueError("unknown course")
    course=courses[lesson]
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    reasoning=revise(lesson,model,output.with_suffix(".attempts.json"))
    lab={"executed":False,"passed":False,"reason":"no dedicated lab fixture"}
    if course["test_contract"]:
        try:
            p=subprocess.run(["forge","test","--root","student_lab","--match-contract",
               course["test_contract"],"-vv"],capture_output=True,text=True,timeout=180)
            lab={"executed":True,"passed":p.returncode==0,"returncode":p.returncode,
                 "log_tail":(p.stdout+"\n"+p.stderr)[-4000:]}
        except (FileNotFoundError,subprocess.TimeoutExpired) as exc:
            lab={"executed":False,"passed":False,"reason":type(exc).__name__}
    record={lesson:{"assessment":{"independent_completion_verified":False,
                "attempts":len(reasoning["attempts"]),
                "improved_keyword_coverage":reasoning["improved_keyword_coverage"]},
                "lab":lab,"human_review_approved":False}}
    result={"lesson":lesson,"reading":course["reading"],"objectives":course["objectives"],
            "attempts_file":str(output.with_suffix(".attempts.json")),
            "evidence":record,"course_gate":evaluate(record),
            "note":"Teaching attempt and existing lab evidence only; not an independent blind solution."}
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--lesson",required=True)
    p.add_argument("--model",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();r=run(a.lesson,a.model,a.output)
    print(json.dumps({"lesson":r["lesson"],"attempts":r["evidence"][a.lesson]["assessment"]["attempts"],
       "forge_passed":r["evidence"][a.lesson]["lab"]["passed"],
       "course_passed":r["course_gate"][a.lesson]["passed"]}))
