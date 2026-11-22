#!/usr/bin/env python3
"""Execute the production retry eligibility closure with legacy timestamps.

No source downloads, OCR, or fact verification are implied.
"""
import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

path = Path(__file__).with_name("run_extraction_batch.py")
tree = ast.parse(path.read_text(encoding="utf-8"))
main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
fn = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == "eligible")
# Compile the real production function, rather than duplicating its logic.
namespace = {"datetime": datetime, "timedelta": timedelta, "timezone": timezone,
             "Path": Path, "MAX_ATTEMPTS": 3}
exec(compile(ast.Module(body=[fn], type_ignores=[]), str(path), "exec"), namespace)
sha = "a" * 40
entry = {"sha": sha, "name": "priority.pdf"}
namespace["terminal"] = {"extracted", "needs_visual_review", "partial_ocr_failure"}
namespace["converter_available"] = False
now = datetime.now(timezone.utc)
cases = [
    ({"extraction_status": "failed", "attempts": 3,
      "last_attempt_utc": (now - timedelta(hours=7)).replace(tzinfo=None).isoformat()}, True),
    ({"extraction_status": "failed", "attempts": 3,
      "last_attempt_utc": (now - timedelta(hours=1)).replace(tzinfo=None).isoformat()}, False),
    ({"extraction_status": "failed", "attempts": 3,
      "last_attempt_utc": (now - timedelta(hours=7)).isoformat()}, True),
    ({"extraction_status": "extracted", "attempts": 3}, False),
    ({"extraction_status": "failed", "attempts": 3, "last_attempt_utc": "invalid"}, False),
]
for record, expected in cases:
    namespace["files"] = {sha: record}
    actual = namespace["eligible"](entry)
    assert actual is expected, (record, actual, expected)
print("PASS: production retry eligibility with naive/aware UTC, cooldown, and invalid records; no live source processing")
