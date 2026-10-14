"""Evidence-preserving offline learning pipeline. No live targets or automatic promotion."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from student_curriculum import curriculum
from student_lab import LESSONS
from student_revision_loop import revise
from student_authorization import Scope, require_authorization
from student_learning_memory import context as previous_failures, remember, summarize_failure

def retrieve(question, knowledge_root, limit=3):
    root = Path(knowledge_root).resolve()
    if not root.is_dir():
        return []
    words = set(question.lower().split())
    # Chinese prompts have no whitespace: match domain terms as substrings.
    words.update(term for term in ("重入", "提款", "状态", "外部调用", "权限", "整数", "余额", "验证") if term in question)
    hits = []
    for path in sorted(root.rglob("*.md")):
        if not path.is_file() or not path.resolve().is_relative_to(root):
            continue
        content = path.read_text(encoding="utf-8")[:20000]
        score = sum(token in content.lower() for token in words if len(token) > 2)
        if score:
            hits.append((score, str(path.relative_to(root)), hashlib.sha256(content.encode()).hexdigest()))
    return [{"file": name, "sha256": digest} for _, name, digest in sorted(hits, reverse=True)[:limit]]

def choose_course(memory):
    courses = curriculum()["courses"]
    completed = set(memory.get("verified_courses", []))
    for course in courses:
        if course["id"] not in completed and all(x in completed for x in course["prerequisites"]):
            return course
    return None

def run_once(model, knowledge_root, memory_path, evidence_dir, lesson=None, forge_runner=None):
    memory_path = Path(memory_path)
    evidence_dir = Path(evidence_dir)
    memory = json.loads(memory_path.read_text(encoding="utf-8")) if memory_path.exists() else {"version": 1, "sessions": [], "verified_courses": []}
    courses = {c["id"]: c for c in curriculum()["courses"]}
    course = courses[lesson] if lesson else choose_course(memory)
    if course is None:
        return {"status": "no_unlocked_course"}
    lesson_id = course["id"]
    if lesson_id not in LESSONS:
        return {"status": "blocked", "reason": "no assessment", "lesson": lesson_id}
    evidence_dir.mkdir(parents=True, exist_ok=True)
    retrieval = retrieve(LESSONS[lesson_id]["prompt"], knowledge_root)
    assessment_path = evidence_dir / (lesson_id + "-attempts.json")
    retrieved_text = []
    root = Path(knowledge_root).resolve()
    for hit in retrieval:
        path = (root / hit["file"]).resolve()
        if path.is_file() and path.is_relative_to(root):
            retrieved_text.append(path.read_text(encoding="utf-8")[:1200])
    learning_context = "\n".join(retrieved_text)[:3000] + "\n" + previous_failures(memory_path.with_suffix(".failures.json"), lesson_id)
    reasoning = revise(lesson_id, model, assessment_path, learning_context=learning_context)
    lab = {"executed": False, "passed": False, "reason": "dedicated lab not configured"}
    if course.get("test_contract") and course.get("lab"):
        from subprocess import run
        test_file = Path(course["lab"])
        scope = Scope("local-training", str(Path.cwd() / "student_lab"), True)
        require_authorization(scope, str(test_file), "test")
        runner = forge_runner or run
        result = runner(["forge", "test", "--root", "student_lab", "--match-contract", course["test_contract"], "-vv"], capture_output=True, text=True, timeout=180)
        lab = {"executed": True, "passed": result.returncode == 0, "returncode": result.returncode, "log_tail": (result.stdout + "\n" + result.stderr)[-3000:]}
    record = {"knowledge_context_sent": bool(retrieved_text), "prior_failure_context_sent": bool(previous_failures(memory_path.with_suffix(".failures.json"), lesson_id)), "timestamp": datetime.now(timezone.utc).isoformat(), "lesson": lesson_id, "retrieval": retrieval,
              "reasoning_attempts": len(reasoning["attempts"]), "feedback_improved": reasoning["improved_keyword_coverage"],
              "lab": lab, "model_independent_solution_verified": False,
              "held_out_problem_passed": False, "human_review_approved": False}
    memory["sessions"].append(record)
    if not reasoning["improved_keyword_coverage"] or not lab["passed"]:
        attempts = reasoning.get("attempts", [])
        last = attempts[-1] if attempts and isinstance(attempts[-1], dict) else {}
        feedback = last.get("feedback", {})
        remember(memory_path.with_suffix(".failures.json"), summarize_failure(lesson_id, feedback, lab.get("log_tail", lab.get("reason", ""))))
    # Graduation is never inferred from keyword feedback or an existing fixture.\n    # Only a separate signed-off independent assessment may update verified_courses.
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.write_text(json.dumps(memory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (evidence_dir / (lesson_id + "-session.json")).write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--knowledge-root", default="knowledge")
    p.add_argument("--memory", default="child-evidence/learning-memory.json")
    p.add_argument("--evidence-dir", default="child-evidence")
    p.add_argument("--lesson", choices=[c["id"] for c in curriculum()["courses"]])
    a = p.parse_args()
    print(json.dumps(run_once(a.model, a.knowledge_root, a.memory, a.evidence_dir, a.lesson), ensure_ascii=False, indent=2))
