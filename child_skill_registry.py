"""Read-only, allowlisted local security skills. No arbitrary shell execution."""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS = {
    "solidity-tests": {
        "description": "Run Foundry tests in the authorized local teaching lab",
        "command": ["forge", "test", "--root", str(ROOT / "student_lab"), "-vv"],
        "cwd": ROOT / "student_lab",
    },
    "solidity-static": {
        "description": "Check the local Solidity teaching contract with Slither",
        "command": ["slither", str(ROOT / "student_lab" / "contracts" / "VulnerableVault.sol"), "--json", "-"],
        "cwd": ROOT / "student_lab",
    },
}

def run_skill(name, timeout=120):
    if name not in SKILLS:
        raise ValueError("Unknown skill")
    spec = SKILLS[name]
    if not spec["cwd"].is_dir():
        raise FileNotFoundError("Local training lab missing")
    try:
        result = subprocess.run(spec["command"], cwd=spec["cwd"], timeout=timeout,
                                capture_output=True, text=True, errors="replace")
        return {"skill": name, "executed": True, "exit_code": result.returncode,
                "passed": result.returncode == 0, "stdout_tail": result.stdout[-4000:],
                "stderr_tail": result.stderr[-2000:]}
    except FileNotFoundError as exc:
        return {"skill": name, "executed": False, "passed": False,
                "error": "Tool not installed: " + str(exc.filename)}
    except subprocess.TimeoutExpired:
        return {"skill": name, "executed": True, "passed": False, "error": "Timeout"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--skill", choices=sorted(SKILLS))
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.list:
        print(json.dumps({k: v["description"] for k, v in SKILLS.items()}, indent=2))
    else:
        if not args.skill:
            parser.error("--skill required unless --list")
        evidence = run_skill(args.skill)
        report = json.dumps(evidence, indent=2)
        if args.output:
            Path(args.output).write_text(report + "\n", encoding="utf-8")
        print(report)
        raise SystemExit(0 if evidence["passed"] else 1)
