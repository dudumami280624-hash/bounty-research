"""Blind Shannon diagnosis with a free local model and auditable evidence."""
import argparse
import json
import os
import subprocess
from pathlib import Path

CASE = """You are diagnosing two separate Shannon runs. Do not assume they have the same cause.
A: pre-recon ran ~14 minutes, recon ran ~8 minutes, then AGENT_EXECUTION_FAILED;
stopReason=error, no useful provider error snippet.
B: separate run failed during runPreflightValidation after ~1.5 seconds.
Provider said: credentials from pi auth.json validation failed; non-retryable request error.
A separate direct Pi call returned: Codex error: The usage limit has been reached.
For EACH incident identify stage, what cause is proven vs unknown, a minimal safe next
step, and redacted evidence to preserve. Answer in Chinese. Do not call external APIs."""

def evaluate(answer):
    """Advisory rubric only. Never equate keyword hits with independent success."""
    low = answer.lower()
    checks = {
        "recon_identified": "recon" in low or "侦察" in answer,
        "preflight_identified": "preflight" in low or "预检" in answer,
        "quota_identified": any(x in low for x in ("usage limit", "quota", "额度", "配额", "使用限制")),
        "uncertainty_expressed": any(x in answer for x in ("未知", "未证实", "无法确定", "不能确定", "无法证明", "尚未")),
    }
    return checks

def run(model, output, binary="llama-cli", runner=subprocess.run):
    if not Path(model).is_file():
        raise FileNotFoundError("GGUF model not found")
    proc = runner([binary, "-m", str(model), "-p", CASE, "-n", "400", "--temp", "0"],
                  capture_output=True, text=True, timeout=240)
    if proc.returncode or not proc.stdout.strip():
        raise RuntimeError("local inference failed: " + proc.stderr[-400:])
    raw = proc.stdout.strip()
    # llama-cli can echo its prompt; NEVER grade the question as if it were an answer.
    answer = raw.replace(CASE, "").strip()
    if not answer:
        raise RuntimeError("model produced no independent answer after prompt removal")
    checks = evaluate(answer)
    payload = {
        "case": "shannon-two-failures-01",
        "inference_executed": True,
        "answer": answer,
        "keyword_checks": checks,
        "keyword_coverage": sum(checks.values()),
        "human_review_required": True,
        "independent_completion_verified": False,
    }
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.model, args.output, os.environ.get("LLAMA_CLI", "llama-cli"))
    print(json.dumps({"keyword_coverage": result["keyword_coverage"],
                      "independent_completion_verified": False}))
