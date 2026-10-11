#!/usr/bin/env python3
"""Conservative local-only first-stage source audit. No live target scanning."""

import json
import pathlib
import subprocess
import datetime
import shutil

ROOT = pathlib.Path(__file__).resolve().parent

config = json.loads(
    (ROOT / "config.json").read_text(encoding="utf-8")
)

report = {
    "time_utc": datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat(),
    "projects": []
}

for i, target in enumerate(config["repositories"]):
    entry = {
        "name": target["name"],
        "url": target["url"],
        "commit": target["commit"],
        "status": "not started"
    }

    report["projects"].append(entry)
    repo = ROOT / "_work" / str(i)

    try:
        repo.parent.mkdir(exist_ok=True)

        if repo.exists():
            shutil.rmtree(repo)

        subprocess.run(
            [
                "git", "clone", "--quiet", "--no-checkout",
                target["url"], str(repo)
            ],
            check=True,
            timeout=150
        )

        subprocess.run(
            [
                "git", "-C", str(repo),
                "checkout", "--quiet", target["commit"]
            ],
            check=True,
            timeout=90
        )

        files = [
            p for p in repo.rglob("*.sol")
            if p.is_file()
        ]

        entry["solidity_files"] = len(files)
        entry["status"] = "source retrieved; heuristic review only"
        entry["review_flags"] = []

        markers = (
            "delegatecall(",
            "tx.origin",
            "selfdestruct(",
            "call{value:"
        )

        for file in files:
            try:
                content = file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            for marker in markers:
                if marker in content:
                    entry["review_flags"].append({
                        "file": str(file.relative_to(repo)),
                        "marker": marker
                    })

        entry["flags_are_vulnerabilities"] = False

    except Exception as exc:
        entry["status"] = "error"
        entry["error"] = str(exc)[:500]

filename = ROOT / "audit.json"

filename.write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=False, indent=2))

# A successful GitHub job must mean every configured audit completed.
if any(project["status"] == "error" for project in report["projects"]):
    raise SystemExit(1)
