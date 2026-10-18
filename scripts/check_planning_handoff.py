#!/usr/bin/env python3
"""Dependency-free, fail-closed planning/handoff repository gate."""
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "AGENTS.md": ("HANDOFF.md", "task_plan.md"),
    "HANDOFF.md": ("# ",),
    "task_plan.md": ("# ",),
    "findings.md": ("# ",),
    "progress.md": ("# ",),
    ".agents/skills/planning-with-files/SKILL.md": ("name: planning-with-files",),
    ".agents/skills/handoff/SKILL.md": ("name: handoff",),
}
def check(root=ROOT):
    failures = []
    for path, markers in REQUIRED.items():
        target = root / path
        if not target.is_file():
            failures.append(f"MISSING: {path}")
            continue
        content = target.read_text(encoding="utf-8")
        if not content.strip():
            failures.append(f"EMPTY: {path}")
        for marker in markers:
            if marker not in content:
                failures.append(f"INVALID: {path}: missing {marker!r}")
    return failures

if __name__ == "__main__":
    problems = check()
    print(json.dumps({"result": "PASS" if not problems else "BLOCKED", "checks": len(REQUIRED), "problems": problems}, ensure_ascii=False, indent=2))
    sys.exit(1 if problems else 0)
