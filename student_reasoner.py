"""Offline local model adapter. No paid API, network target, or false inference claims."""
import argparse
import json
import os
import subprocess
from pathlib import Path
from student_lab import LESSONS
from student_practice import practice

def local_inference(lesson, model_path, output, runner=subprocess.run):
    if lesson not in LESSONS:
        raise ValueError("unknown lesson")
    model=Path(model_path)
    if not model.is_file():
        raise FileNotFoundError("local model file not found")
    binary=os.environ.get("LLAMA_CLI","llama-cli")
    prompt=("你是一名离线 Solidity 安全学习者。请只分析给定的教学问题，"
            "解释漏洞根因与修复方案，不访问真实目标。\n题目："+LESSONS[lesson]["prompt"])
    cmd=[binary,"-m",str(model),"-p",prompt,"-n","256","--temp","0"]
    result=runner(cmd,capture_output=True,text=True,timeout=240)
    if result.returncode!=0 or not result.stdout.strip():
        raise RuntimeError("local model inference failed")
    first=result.stdout.strip()
    feedback=practice(lesson,[first],output)
    feedback["agent"]={"type":"local_llama_cpp","model_inference_executed":True,
                       "model_path":model.name,"independent_completion_verified":False}
    Path(output).write_text(json.dumps(feedback,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return feedback

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--lesson",choices=LESSONS,required=True)
    p.add_argument("--model",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    r=local_inference(a.lesson,a.model,a.output)
    print(json.dumps({"inference_executed":True,"review_required":r["review_required"]}))
if __name__=="__main__":
    main()
