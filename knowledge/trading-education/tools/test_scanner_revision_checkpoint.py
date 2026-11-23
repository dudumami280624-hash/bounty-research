#!/usr/bin/env python3
"""Regression: newly completed PDF audits must not be rescanned forever."""
import ast
from pathlib import Path

source = Path(__file__).with_name("resume_visual_pages.py").read_text(encoding="utf-8")
module = ast.parse(source)
fn = next(n for n in module.body if isinstance(n, ast.FunctionDef)
          and n.name == "mark_scanner_revision_if_covered")
namespace = {}
exec(compile(ast.Module(body=[fn], type_ignores=[]), "<isolated production function>", "exec"), namespace)
mark = namespace["mark_scanner_revision_if_covered"]

fresh = {"coverage_complete": True, "next_page": 12, "ocr_complete": False,
         "ocr_failed_page_numbers": [4]}
mark(fresh)
assert fresh["scanner_revision"] == 2
assert fresh["ocr_complete"] is False
assert fresh["ocr_failed_page_numbers"] == [4]
legacy = {"coverage_complete": True, "scanner_reaudit_in_progress": True}
mark(legacy)
assert legacy["scanner_revision"] == 2
assert "scanner_reaudit_in_progress" not in legacy
partial = {"coverage_complete": False, "scanner_reaudit_in_progress": True}
mark(partial)
assert "scanner_revision" not in partial
assert partial["scanner_reaudit_in_progress"]
# Ensure the production main path calls the function, not only this fixture.
main = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == "main")
assert any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
           and n.func.id == "mark_scanner_revision_if_covered"
           for n in ast.walk(main))
print("PASS: completed first-pass scans stamped; OCR failures preserved")
