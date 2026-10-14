"""Bounded local-model revision loop. Feedback is rubric-only; no answer is leaked."""
import argparse
import json
import os
import subprocess
from pathlib import Path
from student_lab import LESSONS, grade
from student_practice import practice

def revise(lesson, model_path, output, runner=subprocess.run, max_attempts=3):
    if lesson not in LESSONS: raise ValueError("unknown lesson")
    if not Path(model_path).is_file(): raise FileNotFoundError(model_path)
    if not 1 <= max_attempts <= 5: raise ValueError("attempt limit")
    prompt=("你是离线智能合约安全学习者。请用简体中文回答，避免英文术语替代中文核心概念。"\n            "请严格分三部分：1.漏洞根因 2.修复方式 3.如何验证。每部分写具体技术步骤。"\n            "不得声称已运行测试。题目："+LESSONS[lesson]["prompt"])
    answers=[]
    for _ in range(max_attempts):
        cmd=[os.environ.get("LLAMA_CLI","llama-cli"),"-m",str(model_path),"-p",prompt,"-n","256","--temp","0"]
        p=runner(cmd,capture_output=True,text=True,timeout=240)
        if p.returncode!=0 or not p.stdout.strip(): raise RuntimeError("model inference failed")
        answer=p.stdout.strip()
        answers.append(answer)
        feedback=grade(lesson,answer)
        if not feedback["missing"]: break
        prompt=("请独立修改你的上一轮回答。上一轮回答：\n"+answer+
                "\n评分反馈：以下概念尚未充分解释："+", ".join(feedback["missing"])+
                "\n请给出更完整的漏洞原因、修复顺序和验证方式，不要照搬评分关键词。")
    record=practice(lesson,answers,output)
    record["agent"]={"type":"local_llama_cpp_feedback_loop","model_inference_executed":True,
                     "attempts_executed":len(answers),"independent_completion_verified":False,
                     "unknown_vulnerability_discovered":False}
    Path(output).write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return record

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--lesson",choices=LESSONS,required=True)
    parser.add_argument("--model",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=revise(args.lesson,args.model,args.output)
    print(json.dumps({"real_model_attempts":len(result["attempts"]),
                      "revision_observed":result["revision_observed"],
                      "improved_keyword_coverage":result["improved_keyword_coverage"],
                      "independent_completion_verified":False}))
