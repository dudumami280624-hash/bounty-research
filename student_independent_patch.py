"""Real-model Solidity patch attempts against an isolated, disposable teaching fixture."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

SOURCE = Path("student_lab/contracts/VulnerableVault.sol")
TEST = Path("student_lab/test/ReentrancyLesson.t.sol")
MARKER = "contract FixedVault {"
SYSTEM = """You are fixing a local Solidity teaching contract. Return ONLY a complete
Solidity contract named FixedVault, with a balances mapping, deposit() and withdraw().
Use pragma solidity ^0.8.20. Protect against reentrancy using checks-effects-interactions.
Do not include markdown, explanations, or VulnerableVault. Do not claim tests ran."""

def extract(text):
    # Require an actual model-generated contract rather than accepting a prewritten fixture.
    match = re.search(r"contract\s+FixedVault\s*\{", text)
    if not match:
        return None
    start = match.start()
    depth = 0
    for i in range(match.end()-1, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                contract = text[start:i+1]
                if len(contract) > 12000 or len(contract) < 90:
                    return None
                return contract + "\n"
    return None

def run(lesson, model, output, attempts=3):
    if lesson != "reentrancy-01":
        raise ValueError("only reentrancy-01 has a verified isolated code fixture")
    if not 1 <= attempts <= 3:
        raise ValueError("attempts must be 1..3")
    model = Path(model)
    if not model.is_file():
        raise FileNotFoundError(model)
    original = SOURCE.read_text(encoding="utf-8")
    vulnerable = original.split(MARKER, 1)[0]
    if "contract VulnerableVault" not in vulnerable:
        raise RuntimeError("missing vulnerable teaching fixture")
    prompt = SYSTEM + "\nExisting vulnerable example (DO NOT CHANGE):\n" + vulnerable + "\nThe contract must have exactly deposit() and withdraw() and mapping balances."
    records = []
    success = False
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="child-solidity-") as td:
            root = Path(td)
            (root / "contracts").mkdir()
            (root / "test").mkdir()
            (root / "test" / TEST.name).write_text(TEST.read_text(encoding="utf-8"), encoding="utf-8")
            for index in range(1, attempts+1):
                cmd = [os.environ.get("LLAMA_CLI", "llama-cli"), "-m", str(model.resolve()),
                       "-p", prompt, "-n", "700", "--temp", "0"]
                inference = subprocess.run(cmd, capture_output=True, encoding="utf-8",
                                           errors="replace", timeout=240)
                record = {"attempt": index, "model_exit_code": inference.returncode,
                          "raw_model_output": inference.stdout[-20000:],
                          "model_stderr_tail": inference.stderr[-2000:],
                          "patch_extracted": False, "forge_executed": False, "forge_passed": False}
                if inference.returncode != 0:
                    record["error"] = "model execution failed"
                    records.append(record)
                    break
                candidate = extract(inference.stdout)
                if candidate is None:
                    feedback = "Your answer did not contain a complete FixedVault Solidity contract."
                else:
                    record["patch_extracted"] = True
                    record["candidate_sha256"] = hashlib.sha256(candidate.encode()).hexdigest()
                    record["candidate_code"] = candidate
                    (root / "contracts" / SOURCE.name).write_text(vulnerable + candidate, encoding="utf-8")
                    forge = subprocess.run(["forge", "test", "--root", str(root),
                                            "--match-contract", "ReentrancyLessonTest", "-vv"],
                                           capture_output=True, encoding="utf-8",
                                           errors="replace", timeout=180)
                    record["forge_executed"] = True
                    record["forge_exit_code"] = forge.returncode
                    record["forge_log_tail"] = (forge.stdout + "\n" + forge.stderr)[-9000:]
                    record["forge_passed"] = forge.returncode == 0
                    feedback = record["forge_log_tail"][-2500:]
                    if record["forge_passed"]:
                        success = True
                records.append(record)
                if success:
                    break
                prompt = SYSTEM + "\nPrevious answer:\n" + inference.stdout[-6000:] + (
                    "\nThe isolated Foundry test did not pass. Correct the Solidity contract. "
                    "Return a complete FixedVault contract only. Feedback:\n" + feedback)
    finally:
        result = {"lesson": lesson, "real_model_invoked": len(records) > 0,
                  "independent_patch_test_passed": success, "attempts": records,
                  "human_review_approved": False,
                  "note": "Passing a teaching fixture is not an unknown-vulnerability discovery or human-approved course completion."}
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lesson", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = run(args.lesson, args.model, args.output)
    print(json.dumps({"attempts": len(result["attempts"]),
                      "independent_patch_test_passed": result["independent_patch_test_passed"]}))
