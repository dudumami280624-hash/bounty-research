"""Allocate an offline blind-learning prompt; no answers or labels disclosed."""
import argparse
import hashlib
import json
import secrets
from pathlib import Path
TASKS=(
 {"id":"blind-cei-01","title":"检查外部调用顺序","prompt":"阅读一份未标注的提款合约，记录余额变更和外部调用顺序；判断重入风险并设计修复测试。"},
 {"id":"blind-auth-02","title":"检查权限边界","prompt":"阅读一份未标注的管理员配置合约，设计授权与未授权账户的测试，解释可能的权限问题。"},
 {"id":"blind-arithmetic-03","title":"检查整数边界","prompt":"阅读一份未标注的奖励计算合约，设计边界和舍入测试，说明不变量。"},
)
def allocate(seed):
    digest=hashlib.sha256(seed.encode()).digest()
    return TASKS[int.from_bytes(digest[:8],"big")%len(TASKS)]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--seed")
    args=p.parse_args()
    assignment=allocate(args.seed or secrets.token_hex(16))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(assignment,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Assigned",assignment["id"],"to",args.output)
if __name__=="__main__":main()
