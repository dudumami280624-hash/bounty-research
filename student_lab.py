"""Offline learner lab: no wallet, credentials, network, or live targets required."""
import argparse
import json
from pathlib import Path

LESSONS = {
    "reentrancy-01": {
        "title": "重入漏洞：检查-效果-交互",
        "prompt": "某提款函数先向用户发送 ETH，再把余额设为零。漏洞根因是什么？应先做哪一步？",
        "answer": "状态更新必须先于外部调用；否则外部调用可在余额清零前重入。",
        "keywords": ("状态", "外部调用", "先"),
    },
    "access-control-01": {
        "title": "访问控制：敏感操作权限",
        "prompt": "一个任何人都能调用的 setOwner 函数有什么问题？如何修复？",
        "answer": "缺少访问控制；仅授权所有者或角色能更改所有者，并测试未授权调用失败。",
        "keywords": ("权限", "授权"),
    },
}
def grade(lesson, response):
    if lesson not in LESSONS:
        raise ValueError("unknown lesson")
    answer = response.strip()
    if not answer:
        return {"lesson": lesson, "status": "incomplete", "matched": [], "missing": list(LESSONS[lesson]["keywords"]), "human_review_required": True}
    keywords = LESSONS[lesson]["keywords"]
    matched = [word for word in keywords if word in answer]
    return {"lesson": lesson, "status": "review_required", "matched": matched, "missing": [word for word in keywords if word not in answer], "human_review_required": True, "note": "关键词仅辅助反馈，不代表独立实战通过"}
def main():
    parser=argparse.ArgumentParser(description="Offline student lab entrypoint")
    parser.add_argument("--list",action="store_true")
    parser.add_argument("--lesson",choices=LESSONS)
    parser.add_argument("--answer-file",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    if args.list:
        print(json.dumps({k:{"title":v["title"],"prompt":v["prompt"]} for k,v in LESSONS.items()},ensure_ascii=False,indent=2))
        return
    if not args.lesson:
        parser.error("choose --list or --lesson")
    if not args.answer_file:
        print(LESSONS[args.lesson]["prompt"])
        return
    result=grade(args.lesson,args.answer_file.read_text(encoding="utf-8"))
    payload=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload+"\n",encoding="utf-8")
    print(payload)
if __name__=="__main__":
    main()
