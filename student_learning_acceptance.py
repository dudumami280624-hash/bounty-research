"""Evidence-based learning acceptance. Never conflate assisted patching with autonomy."""
import argparse
import json
from pathlib import Path

def evaluate(revision, patch):
    attempts = revision.get("attempts", [])
    patch_attempts = patch.get("attempts", [])
    model_only_pass = any(
        a.get("forge_passed") and not a.get("deterministic_fixes")
        for a in patch_attempts
    )
    feedback_improved = bool(revision.get("improved_keyword_coverage"))
    revision_observed = bool(revision.get("revision_observed"))
    assisted_pass = bool(patch.get("independent_patch_test_passed"))
    verified = bool(model_only_pass and feedback_improved and revision_observed)
    return {
        "model_invoked": bool(patch.get("real_model_invoked")),
        "feedback_revision_observed": revision_observed,
        "feedback_improved_coverage": feedback_improved,
        "assisted_foundry_passed": assisted_pass,
        "model_only_foundry_passed": model_only_pass,
        "autonomous_learning_accepted": verified,
        "unknown_vulnerability_discovered": False,
        "human_review_approved": False,
        "reason": ("Model-only repair and improved feedback coverage demonstrated"
                   if verified else "Assisted success is not independent learning; further evidence required"),
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--revision", type=Path, required=True)
    p.add_argument("--patch", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = evaluate(json.loads(args.revision.read_text()),
                      json.loads(args.patch.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
