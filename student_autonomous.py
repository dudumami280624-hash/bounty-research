"""Offline autonomous *baseline* learner for the curated exercises.

This is a deterministic reasoning baseline, NOT an LLM and NOT independent
discovery of an unknown vulnerability. Its output is explicitly attributed.
"""
import argparse
import json
from pathlib import Path
from student_lab import LESSONS
from student_practice import practice

CONCEPTS={
 "reentrancy-01":{
  "initial":"提款函数执行外部调用后才清零余额，可能发生重入。",
  "revision":"先更新状态，再执行外部调用；用恶意回调测试修复前后余额不变量。"},
 "access-control-01":{
  "initial":"setOwner 缺少权限检查，任意调用者可更改所有者。",
  "revision":"添加权限检查，仅授权账户可调用；测试未授权账户交易回退。"},
}
def run_autonomous_baseline(lesson, output):
    if lesson not in LESSONS or lesson not in CONCEPTS:
        raise ValueError("no autonomous baseline for this lesson")
    concept=CONCEPTS[lesson]
    record=practice(lesson,[concept["initial"],concept["revision"]],output)
    record["agent"]={"type":"deterministic_curated_baseline",
                     "discovered_unknown_vulnerability":False,
                     "model_inference_executed":False,
                     "self_generated_from_curated_rules":True}
    Path(output).write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return record

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--lesson",choices=CONCEPTS,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=run_autonomous_baseline(a.lesson,a.output)
    print(json.dumps({"attempts":len(result["attempts"]),
                      "improved":result["improved_keyword_coverage"],
                      "independent_completion_verified":False},ensure_ascii=False))
if __name__=="__main__":
    main()
