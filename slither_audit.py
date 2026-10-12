#!/usr/bin/env python3
"""Run free Slither on a configured, pinned, local Solidity source tree.
Reports are triage candidates, never proof of an exploitable issue.
"""
import json
import pathlib
import shutil
import subprocess
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
OUT = ROOT / "slither_results.json"
records = []
def detector_locations(item, folder):
    """Capture Slither's structured source locations; description text is not authoritative."""
    locations = []
    seen = set()
    for element in item.get("elements", [])[:80]:
        mapping = element.get("source_mapping") or {}
        path = None
        absolute = mapping.get("filename_absolute")
        if isinstance(absolute, str):
            try:
                path = pathlib.Path(absolute).resolve().relative_to(folder.resolve()).as_posix()
            except ValueError:
                pass
        if path is None:
            relative = mapping.get("filename_relative")
            if isinstance(relative, str):
                relative = relative.replace("\\", "/").lstrip("./")
                if relative.startswith(("src/", "lib/", "test/", "script/")):
                    path = relative
                elif "/_work/" in relative:
                    # This is a workspace path, not a repository-relative location.
                    path = None
        if not path or path in seen:
            continue
        seen.add(path)
        lines = mapping.get("lines", [])
        if not isinstance(lines, list):
            lines = []
        locations.append({"path":path,"lines":[v for v in lines[:12] if type(v) is int and v > 0],
                          "element_type":str(element.get("type") or "")[:60]})
        if len(locations) >= 30:
            break
    return locations
binary = shutil.which("slither")
for idx, target in enumerate(CONFIG["repositories"]):
    folder = ROOT / "_work" / str(idx)
    row = {"name": target["name"], "commit": target["commit"],
           "status": "not_started", "findings": [],
           "findings_verified_as_vulnerabilities": False}
    records.append(row)
    if not binary:
        row["status"] = "scanner_unavailable"
        continue
    if not folder.is_dir():
        row["status"] = "source_unavailable"
        continue
    report_path = ROOT / ("slither_raw_" + str(idx) + ".json")
    try:
        process = subprocess.run(
            [binary, str(folder), "--json", str(report_path), "--disable-color",
             "--exclude-low", "--exclude-informational",
             "--filter-paths", r"(^|/)(lib|node_modules|test|script)/"],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            text=True, timeout=180, check=False)
        if report_path.exists():
            data = json.loads(report_path.read_text(encoding="utf-8"))
            for item in data.get("results", {}).get("detectors", []):
                row["findings"].append({
                    "check": item.get("check"), "impact": item.get("impact"),
                    "confidence": item.get("confidence"),
                    "description": str(item.get("description", ""))[:1200],
                    "locations": detector_locations(item, folder)
                })
            row["status"] = "analyzed" if process.returncode in (0, 255) else "scanner_error"
        else:
            row["status"] = "scan_failed_no_json"
            row["scanner_returncode"] = process.returncode
            row["error_excerpt"] = process.stderr[-1600:]
        if row["status"] != "analyzed":
            row["scanner_returncode"] = process.returncode
            row["error_excerpt"] = process.stderr[-1500:]
    except Exception as exc:
        row["status"] = "scanner_exception"
        row["error_type"] = type(exc).__name__
    finally:
        report_path.unlink(missing_ok=True)
result = {"time_utc": datetime.now(timezone.utc).isoformat(),
          "analysis_type": "automated_static_triage_not_poc",
          "projects": records}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print("Slither source triage:", [(r["name"], r["status"], len(r["findings"])) for r in records])
if any(r["status"] != "analyzed" for r in records):
    raise SystemExit(1)
