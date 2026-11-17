"""Offline Shannon provider preflight: no credentials or network requests required."""
import argparse
import json
import os
from pathlib import Path

def inspect(model, use_pi_auth=False, models_config=None, api_key=None):
    provider, sep, model_id = model.partition(":")
    problems = []
    if not sep or not provider or not model_id:
        problems.append("SHANNON_AI_MODEL must be provider:model-id")
    if provider == "openai-codex":
        problems.append("Codex subscription has usage limits; not an unlimited-free backend")
    if use_pi_auth and provider == "openai-codex":
        problems.append("PI auth cannot bypass exhausted Codex quota")
    if not api_key and not use_pi_auth:
        problems.append("No provider credential configured (local compatible servers can use a placeholder)")
    if models_config:
        try:
            cfg = json.loads(Path(models_config).read_text(encoding="utf-8"))
            spec = cfg["providers"][provider]
            if not isinstance(spec.get("models"), list) or not any(m.get("id") == model_id for m in spec["models"]):
                problems.append("Model ID not declared in models-config")
            if not spec.get("baseUrl") or not spec.get("api"):
                problems.append("Provider needs baseUrl and api in models-config")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            problems.append("Invalid models-config: " + type(exc).__name__)
    return {"provider": provider, "model": model_id, "offline_check": True,
            "remote_model_verified": False, "unlimited_free_verified": False,
            "ready_for_remote_validation": not problems, "problems": problems}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=os.getenv("SHANNON_AI_MODEL", ""))
    p.add_argument("--models-config")
    p.add_argument("--pi-auth", action="store_true")
    a = p.parse_args()
    result = inspect(a.model, a.pi_auth or os.getenv("SHANNON_USE_PI_AUTH") == "1",
                     a.models_config, os.getenv("SHANNON_AI_API_KEY"))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["ready_for_remote_validation"] else 1)

if __name__ == "__main__":
    main()
