"""Strict learning gates: model-only and held-out evidence are mandatory."""
def evaluate(revision, patch, held_out=None):
    held_out = held_out or {}
    attempts = patch.get("attempts", [])
    model_only = bool(patch.get("real_model_invoked") and any(
        a.get("forge_passed") is True and not a.get("deterministic_fixes")
        for a in attempts))
    feedback = bool(revision.get("revision_observed") and revision.get("improved_keyword_coverage"))
    unseen = bool(held_out.get("unseen_fixture") is True and
                  held_out.get("model_generated_patch") is True and
                  held_out.get("forge_passed") is True and
                  held_out.get("deterministic_fixes") == [] and
                  held_out.get("authorization_verified") is True)
    accepted = bool(model_only and feedback and unseen)
    return {
        "model_invoked": bool(patch.get("real_model_invoked")),
        "feedback_revision_observed": bool(revision.get("revision_observed")),
        "feedback_improved_coverage": bool(revision.get("improved_keyword_coverage")),
        "assisted_foundry_passed": bool(patch.get("independent_patch_test_passed")),
        "model_only_foundry_passed": model_only,
        "held_out_verified": unseen,
        "autonomous_learning_accepted": accepted,
        "unknown_vulnerability_discovered": False,
        "human_review_approved": False,
        "reason": "Independent model-only and held-out lab evidence verified" if accepted else "Missing model-only or unseen-task evidence"
    }

if __name__ == "__main__":
    import argparse, json
    from pathlib import Path
    p=argparse.ArgumentParser()
    p.add_argument("--revision",type=Path,required=True)
    p.add_argument("--patch",type=Path,required=True)
    p.add_argument("--held-out",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    unseen=json.loads(a.held_out.read_text()) if a.held_out else None
    result=evaluate(json.loads(a.revision.read_text()),json.loads(a.patch.read_text()),unseen)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))
