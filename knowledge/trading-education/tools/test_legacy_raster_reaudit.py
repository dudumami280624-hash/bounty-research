#!/usr/bin/env python3
"""Check production scheduler requeues completed pre-raster-OCR audits."""
import ast
from pathlib import Path

path=Path(__file__).with_name("resume_visual_pages.py")
tree=ast.parse(path.read_text(encoding="utf-8"))
names={n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
assert {"interleave_visual_work","visual_priority","main"} <= names
src=path.read_text(encoding="utf-8")
assert "scanner_revision',0)<2" in src
assert "scanner_reaudit_in_progress" in src
assert "audit['scanner_revision']=2" in src
assert "audit['next_page']=0" in src
print("PASS: production scanner re-audit path is present (structural only; not textbook OCR)")
