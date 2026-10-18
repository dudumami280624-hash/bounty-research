"""Blind Shannon diagnosis with a free local model and auditable evidence."""
import argparse,json,os,subprocess
from pathlib import Path

CASE = """请对比两次不同的 Shannon 3.4.0 失败，不能把它们混为一谈。
A：一次扫描的 pre-recon 运行约14分钟，recon 运行约8分钟后 AGENT_EXECUTION_FAILED；
stopReason=error，没有可用的具体 provider 错误信息。
B：另一次独立扫描在 runPreflightValidation 阶段约1.5秒就失败，提示 openai-codex
凭证验证时 provider 拒绝请求。随后直接运行 Pi 最小请求，明确返回
“The usage limit has been reached”。
请用中文简洁回答：A 的失败阶段与已知/未知原因；B 的失败阶段与证据支持的原因；
各自下一步最小安全诊断；应保存哪些脱敏证据。不要只说继续重跑。
不要调用付费 API，不要扫描任何目标。"""

def evaluate(answer):
    low=answer.lower()
    checks={
      "incident_a_recon_and_agent_failure":("recon" in low or "侦察" in answer) and ("agent_execution_failed" in low or "执行失败" in answer),
      "incident_a_root_cause_left_unknown":any(x in answer for x in ("根因未知","原因未知","无法确定","尚不清楚","未能确定","不能确定","尚未证实","证据不足")),
      "incident_b_preflight_identified":("preflight" in low or "预检" in answer),
      "incident_b_usage_limit_identified":any(x in low for x in ("usage limit","额度限制","使用额度","配额限制","额度已达","用量限制","达到使用上限")),
      "incidents_not_conflated":any(x in answer for x in ("不能据此断言","不能推断","不能认为","两次独立","不同根因","不能认定两者相同")),
      "safe_evidence_or_diagnostic_step":any(x in answer for x in ("脱敏","日志","auth.json","最小请求","最小化测试","保存证据","保存日志")),
      "causal_separation_explicit":any(x in answer for x in ("不能证明a","不能证明 A","不能说明a","不能说明 A","不能直接推断","不能据此认为","不能据此判断","不代表a","不代表 A","两者不能混为一谈","不能归因于a","不能归因于 A","不同运行不能","不能据此断言","不能推断","不能认为")) ,
    }
    # Lexical checks are screening only; false negatives require reviewing raw answers.\n    return checks

def run(model,output,binary="llama-cli",runner=subprocess.run,case=CASE):
    if not Path(model).is_file(): raise FileNotFoundError("GGUF model not found")
    instruction=("请按四段回答：1.A的观察事实与失败阶段；2.B的观察事实与失败阶段；"
                 "3.分别标明哪些结论有证据、哪些原因尚不能确定，避免跨事件归因；"
                 "4.最小安全验证动作与脱敏证据。只根据日志，不补造细节。")
    prompt=case+"\\n"+instruction
    proc=runner([binary,"-m",str(model),"-p",prompt,"-n","450","--temp","0","--no-display-prompt"],
                capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=300)
    if proc.returncode or not proc.stdout.strip():
        raise RuntimeError("local inference failed: "+proc.stderr[-400:])
    answer=proc.stdout.strip()
    # Defend against prompt echo even if the CLI flag is ignored by a version/build.
    if prompt in answer:
        answer=answer.replace(prompt,"").strip()
    elif case in answer:
        answer=answer.replace(case,"").strip()
    if not answer or answer==case:
        raise RuntimeError("model produced no independent answer")
    checks=evaluate(answer)
    passed=all(checks.values())
    payload={"case":"shannon-two-failures-01","inference_executed":True,"answer":answer,
             "rubric_checks":checks,"rubric_passed":passed,
             "human_review_required":True,"independent_completion_verified":False}
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return payload

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--model",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--case-file",type=Path)
    a=p.parse_args();case=a.case_file.read_text(encoding="utf-8") if a.case_file else CASE;result=run(a.model,a.output,os.environ.get("LLAMA_CLI","llama-cli"),case=case)
    print(json.dumps({"rubric_passed":result["rubric_passed"],"rubric_checks":result["rubric_checks"],
                      "independent_completion_verified":False},ensure_ascii=False))
    if not result["rubric_passed"]: raise SystemExit(1)
