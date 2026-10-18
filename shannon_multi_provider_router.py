"""Deterministic, fail-closed Shannon model candidate routing; no paid calls."""
import argparse
import json
import os
import subprocess
from pathlib import Path
from shannon_provider_preflight import inspect

RETRYABLE = ("usage limit", "rate limit", "429", "quota", "timeout", "timed out", "temporarily unavailable", "503", "502")
NON_RETRYABLE = ("permission denied", "invalid api key", "unauthorized", "invalid credentials", "out of scope")

def candidates(config):
    items = config.get("candidates", [])
    if not isinstance(items, list) or not items:
        raise ValueError("nonempty candidates list required")
    seen = set()
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("model"), str):
            raise ValueError("each candidate needs a model")
        name = item["model"]
        if name in seen:
            raise ValueError("duplicate candidate")
        seen.add(name)
        yield item

def route(config, attempt, evidence_path):
    history = []
    selected = None
    for candidate in candidates(config):
        model = candidate["model"]
        result = inspect(model, use_pi_auth=bool(candidate.get("pi_auth")),
                         models_config=candidate.get("models_config"),
                         api_key=os.getenv(candidate.get("api_key_env", "SHANNON_AI_API_KEY")))
        if not result["ready_for_remote_validation"]:
            history.append({"model": model, "status": "skipped_preflight", "problems": result["problems"]})
            continue
        status, reason = attempt(candidate)
        # Never persist raw stderr or credentials.
        reason_lower = str(reason).lower()
        if status == 0:
            selected = model
            history.append({"model": model, "status": "passed_validation_only"})
            break
        if any(term in reason_lower for term in NON_RETRYABLE):
            history.append({"model": model, "status": "blocked_nonretryable"})
            break
        if any(term in reason_lower for term in RETRYABLE):
            history.append({"model": model, "status": "retryable_provider_failure"})
            continue
        history.append({"model": model, "status": "unknown_failure_stop"})
        break
    report = {"selected_model": selected, "remote_model_verified": selected is not None,
              "full_shannon_scan_verified": False, "unlimited_free_verified": False, "attempts": history}
    target = Path(evidence_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--evidence", default="child-evidence/shannon-provider-routing.json")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    def attempt(candidate):
        if args.dry_run:
            return 1, "not validated in dry run"
        command = candidate.get("validation_command")
        if not isinstance(command, list) or not command or not all(isinstance(x, str) for x in command):
            return 1, "validation command missing"
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=90,
                                  env={**os.environ, "SHANNON_AI_MODEL": candidate["model"]})
            return proc.returncode, (proc.stderr + "\n" + proc.stdout)[-1500:]
        except subprocess.TimeoutExpired:
            return 1, "timeout"
    result = route(config, attempt, args.evidence)
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["selected_model"] else 1)

if __name__ == "__main__":
    main()
