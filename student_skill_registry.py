"""Offline, fail-closed Skill registry for the AI child's existing learning runner.

Skills are *data*, not arbitrary shell plugins. Third-party manifests are never
executed. All executions dispatch to a finite set of audited local entry points.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS = {
    "solidity-repair": {
        "module": "student_independent_patch",
        "function": "run",
        "lessons": ["reentrancy-01"],
        "requires": ["local_gguf", "forge"],
        "provenance": "local first-party teaching fixture",
    },
    "feedback-learning": {
        "module": "student_revision_loop",
        "function": "revise",
        "lessons": ["reentrancy-01", "access-control-01"],
        "requires": ["local_gguf"],
        "provenance": "local first-party rubric feedback",
    },
}
SUSPICIOUS = {
    "network_commands": r"\b(?:curl|wget|Invoke-WebRequest|requests\.post)\b",
    "secret_access": r"(?i)(?:\.env|id_rsa|private.key|GITHUB_TOKEN|AWS_SECRET_ACCESS_KEY)",
    "dynamic_execution": r"\b(?:eval|exec|subprocess|os\.system)\s*\(",
    "destructive_commands": r"(?i)(?:rm\s+-rf|format\s+[a-z]:|shutil\.rmtree)",
    "prompt_override": r"(?i)(?:ignore\s+(?:all\s+)?previous\s+instructions|disable\s+(?:all\s+)?safety\s+checks)",
}
def scan_manifest(path):
    """Review a plain-text Skill file, without importing or running its contents."""
    path = Path(path)
    data = path.read_bytes()
    if len(data) > 256_000:
        raise ValueError("manifest too large")
    text = data.decode("utf-8")
    findings = [{"rule": name, "line": n, "excerpt": line[:180]}
                for n, line in enumerate(text.splitlines(), 1)
                for name, pattern in SUSPICIOUS.items()
                if re.search(pattern, line)]
    return {"file": str(path), "sha256": hashlib.sha256(data).hexdigest(),
            "mode": "static-preflight-only", "findings": findings,
            "decision": "manual_review_required" if findings else "static_preflight_clear",
            "execution_approved": False}

def dispatch(name, lesson, model, output):
    if name not in SKILLS: raise ValueError("skill not allowlisted")
    spec = SKILLS[name]
    if lesson not in spec["lessons"]: raise ValueError("lesson unsupported by skill")
    if name == "solidity-repair":
        from student_independent_patch import run
        return run(lesson, model, output)
    if name == "feedback-learning":
        from student_revision_loop import revise
        return revise(lesson, model, output)
    raise ValueError("skill not implemented")

def learning_plan(lesson):
    """Convert the WorkBuddy-style skill chain into a deterministic teaching plan."""
    from student_curriculum import curriculum
    courses = {course["id"]: course for course in curriculum()["courses"]}
    if lesson not in courses:
        raise ValueError("unknown course")
    course = courses[lesson]
    tasks = [
        {"stage": "knowledge", "action": "read_curated_sources",
         "references": course["reading"], "verified": False},
        {"stage": "reason", "action": "feedback-learning",
         "enabled": lesson in SKILLS["feedback-learning"]["lessons"],
         "verified": False},
        {"stage": "repair", "action": "solidity-repair",
         "enabled": lesson in SKILLS["solidity-repair"]["lessons"],
         "verified": False},
        {"stage": "evidence", "action": "foundry_test",
         "enabled": bool(course["lab"]), "verified": False},
        {"stage": "gate", "action": "human_review", "verified": False},
    ]
    return {"lesson": lesson, "source": "first-party curriculum",
            "workflow": tasks, "completed": False,
            "policy": "A plan is not execution evidence; do not mark any stage passed."}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--plan", metavar="LESSON")
    parser.add_argument("--scan", type=Path)
    parser.add_argument("--skill", choices=SKILLS)
    parser.add_argument("--lesson")
    parser.add_argument("--model")
    parser.add_argument("--output")
    a = parser.parse_args()
    if a.list:
        result = {"skills": SKILLS, "policy": "allowlist-only; never auto-execute imported skills"}
    elif a.plan:
        result = learning_plan(a.plan)
    elif a.scan:
        result = scan_manifest(a.scan)
    elif a.skill and a.lesson and a.model and a.output:
        result = dispatch(a.skill, a.lesson, a.model, a.output)
    else:
        parser.error("use --list, --plan LESSON, --scan FILE or --skill NAME --lesson ID --model PATH --output PATH")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
