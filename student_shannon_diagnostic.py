"""Blind Shannon diagnostic with a local llama.cpp model; records uncoached answer."""
import argparse, json, os, subprocess
from pathlib import Path
CASE = """Incident A: Shannon 3.4.0 pre-recon ran approximately 14 minutes and recon
approximately 8 minutes, then AGENT_EXECUTION_FAILED. Provider stopReason=error;
no explanatory error snippet is available.
Incident B: a separate run failed at runPreflightValidation in about 1.5 seconds:
openai-codex credentials from pi auth.json validation failed: The provider rejected
the model request with a non-retryable error.
A separate minimal Pi call returned: Codex error: The usage limit has been reached.
For each incident state the failure phase, what root cause is and is not proven,
the next minimal diagnostic step, and how to preserve redacted evidence.
Do not use a paid API or scan any target. Answer in Chinese."""
def run(model, output, binary="llama-cli"):
    if not Path(model).is_file():
        raise FileNotFoundError("GGUF model not found")
    proc=subprocess.run([binary,"-m",str(model),"-p",CASE,"-n","400","--temp","0"],
                        capture_output=True,text=True,timeout=240)
    if proc.returncode or not proc.stdout.strip():
        raise RuntimeError("local inference failed: "+proc.stderr[-400:])
    answer=proc.stdout.strip()
    # Keyword checks are feedback, NOT proof of independent reasoning.
    checks={
      "incident_a_recon":any(w in answer.lower() for w in ("recon","侦察")),
      "incident_b_preflight":any(w in answer.lower() for w in ("preflight","预检")),
      "quota_limit":any(w in answer.lower() for w in ("额度","配额","usage limit","使用限制")),
      "uncertainty":any(w in answer for w in ("未知","无法确定","不能确定","未证实","无法证明","尚未")),
    }
    payload={"case":"shannon-two-failures-01","inference_executed":True,
             "answer":answer,"keyword_checks":checks,
             "keyword_coverage":sum(checks.values()),"human_review_required":True,
             "independent_completion_verified":False}
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return payload
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--model",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps({"keyword_coverage":run(a.model,a.output,os.environ.get("LLAMA_CLI","llama-cli"))["keyword_coverage"]}))
