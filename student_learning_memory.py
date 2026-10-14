"""Durable, bounded, offline study memory with exact evidence links."""
import json
from pathlib import Path

def summarize_failure(lesson, feedback, forge_log=""):
    missing = feedback.get("missing", [])
    return {"lesson": lesson, "missing_concepts": [str(x)[:80] for x in missing][:10],
            "test_failure_excerpt": forge_log[-1200:], "resolved": False}

def load(path):
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"version": 1, "failures": [], "verified_courses": []}

def remember(path, item):
    path = Path(path)
    data = load(path)
    data["failures"].append(item)
    data["failures"] = data["failures"][-100:]
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return data

def context(path, lesson, limit=3):
    failures = [x for x in load(path)["failures"] if x.get("lesson") == lesson and not x.get("resolved")]
    return "\n".join("Previous gap: " + ", ".join(x.get("missing_concepts", [])) +
                     "\nPrior test failure: " + x.get("test_failure_excerpt", "")
                     for x in failures[-limit:])
