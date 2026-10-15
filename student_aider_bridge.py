"""Run upstream Aider against an isolated, authorized Solidity teaching fixture.

Uses Aider's real edit/test feedback engine, not a homegrown source patcher.
All LLM traffic must go to an explicit loopback llama.cpp server. No paid API.
"""
import argparse
import difflib
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
SOURCE = Path("student_lab/contracts/VulnerableVault.sol")
TEST = Path("student_lab/test/ReentrancyLesson.t.sol")
HELDOUT_SOURCE = Path("student_lab/held_out/contracts/GuardedSettings.sol")
HELDOUT_TEST = Path("student_lab/held_out/test/GuardedSettingsHidden.t.sol")


def local_endpoint(base_url):
    parsed = urlparse(base_url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise ValueError("Only a loopback HTTP inference endpoint is supported")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Invalid inference endpoint")
    return base_url.rstrip("/")


def checked_run(command, cwd, timeout, env=None):
    return subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=timeout)


def run(output, base_url="http://127.0.0.1:8091/v1", model="openai/local-coder", max_attempts=2, lesson="reentrancy-01", knowledge_index=None):
    """Try actual Aider edits; preserve attempts and independent Foundry results."""
    local_endpoint(base_url)
    if not 1 <= max_attempts <= 3:
        raise ValueError("max_attempts must be 1..3")
    if not model.startswith("openai/"):
        raise ValueError("Aider requires an OpenAI-compatible model name")
    if lesson not in {"reentrancy-01", "held-out-access-control-01"}:
        raise ValueError("Unknown local teaching assessment")
    blind = lesson == "held-out-access-control-01"
    source = HELDOUT_SOURCE if blind else SOURCE
    test_path = HELDOUT_TEST if blind else TEST
    test_contract = "GuardedSettingsHiddenTest" if blind else "ReentrancyLessonTest"
    from student_authorization import Scope, require_authorization
    scope = Scope("local-training", str((ROOT / "student_lab").resolve()), True)
    require_authorization(scope, str((ROOT / source).resolve()), "read")
    require_authorization(scope, str((ROOT / test_path).resolve()), "read")
    full_source = (ROOT / source).read_text(encoding="utf-8")
    if blind:
        vulnerable = full_source
        if "contract GuardedSettings" not in vulnerable or "onlyAdmin" in vulnerable:
            raise ValueError("Held-out exercise is missing or already corrected")
    else:
        marker = "contract FixedVault {"
        if marker not in full_source:
            raise ValueError("Missing verified reference fixture; cannot isolate challenge")
        vulnerable = full_source.split(marker, 1)[0]
        if "contract VulnerableVault" not in vulnerable:
            raise ValueError("Missing training contract")
    study_notes = []
    if knowledge_index and not blind:
        corpus = json.loads(Path(knowledge_index).read_text(encoding="utf-8"))
        study_notes = [str(x["training_note"])[:400] for x in corpus.get("samples", [])
                       if x.get("category") == "reentrancy" and x.get("validated_by") == "pinned-git-blob"][:2]
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    evidence = {"engine": "upstream-aider-cli", "model": model, "lesson": lesson, "unseen_fixture": blind,
                "authorization_verified": True, "model_generated_patch": False,
                "forge_passed": False, "deterministic_fixes": [], "endpoint_loopback": True,
                "reference_excluded_from_agent_workspace": True,
                "real_model_invoked": False, "independent_patch_test_passed": False,
                "attempts": [], "human_review_approved": False,
                "note": "Local training only; a passing known fixture is not an unseen assessment."}
    try:
        with tempfile.TemporaryDirectory(prefix="child-aider-training-") as temp:
            workspace = Path(temp) / ("student_lab/held_out" if blind else "student_lab")
            workspace.mkdir(parents=True, exist_ok=True)
            target = workspace / "contracts" / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(vulnerable, encoding="utf-8")
            test = workspace / "test" / test_path.name
            test.parent.mkdir(parents=True, exist_ok=True)
            test.write_text((ROOT / test_path).read_text(encoding="utf-8"), encoding="utf-8")
            if not shutil.which("aider"):
                raise FileNotFoundError("Official upstream aider CLI not installed")
            if not shutil.which("forge"):
                raise FileNotFoundError("Foundry forge not installed")
            init = checked_run(["git", "init", "-q"], str(workspace), 30)
            if init.returncode:
                raise RuntimeError(init.stderr[-1200:])
            # Prove the disposable fixture starts in a failing state, before any agent edit.
            baseline = checked_run(["forge", "test", "--root", str(workspace),
                                    "--match-contract", test_contract, "-vv"],
                                   str(workspace), 180)
            evidence["baseline_forge_exit_code"] = baseline.returncode
            evidence["baseline_test_failing"] = baseline.returncode != 0
            evidence["baseline_log_tail"] = (baseline.stdout + "\n" + baseline.stderr)[-3000:]
            if not evidence["baseline_test_failing"]:
                raise RuntimeError("Blind/training fixture must fail before model repair")
            env = dict(os.environ, OPENAI_API_BASE=local_endpoint(base_url),
                       OPENAI_API_KEY="local-no-paid-api", AIDER_ANALYTICS="false")
            feedback = ""
            for index in range(1, max_attempts + 1):
                if blind:
                    prompt = (
                        "This is an unseen, authorized local Solidity assessment. "
                        "Edit ONLY contracts/GuardedSettings.sol. "
                        "Keep the GuardedSettings API unchanged: admin(), limit(), updateLimit(uint256), "
                        "transferAdmin(address). Ensure only the current admin can change the limit "
                        "or transfer admin ownership, reject address(0), and preserve the new admin's "
                        "ability to update the limit. Do not change tests or claim tests ran."
                    )
                else:
                    prompt = (
                        "This is an authorized local Solidity teaching exercise. "
                        "Edit ONLY contracts/VulnerableVault.sol to ADD a secure "
                        "contract named FixedVault next to VulnerableVault without changing "
                        "VulnerableVault. FixedVault must expose balances, payable deposit(), "
                        "and withdraw(), preserve deposits and use checks-effects-interactions "
                        "to resist reentrancy. Do not change any tests. Do not claim tests ran."
                    )
                if study_notes and not blind:
                    prompt += "\nVerified historical learning note (legacy syntax; do not copy): " + " ".join(study_notes)
                prompt += "\nAider WHOLE edit format: write the existing filename contracts/" + source.name + " on its own line, followed by a triple-backtick solidity code block with the entire updated file. Do not create a different file or provide an explanation.\n"
                if not blind:
                    prompt += "\nIMPORTANT: FixedVault must be a STANDALONE contract. Never use `is VulnerableVault`, `override`, or `virtual`. The original functions are not virtual. Define a separate balances mapping and implement withdraw with balances[msg.sender] = 0 BEFORE the external call.\n"
                if feedback:
                    prompt += "\nThe previous attempt failed. Its code was reset, but its error must be remembered. Avoid repeating this failure. Real compiler or Foundry evidence:\n" + feedback[-2300:]
                cmd = ["aider", "--model", model, "--edit-format", "whole", "--yes-always",
                       "--no-auto-commits", "--no-auto-lint", "--no-stream", "--no-pretty",
                       "--message", prompt, str(Path("contracts") / source.name)]
                try:
                    attempt_run = checked_run(cmd, str(workspace), 480, env)
                    agent_log = (attempt_run.stdout + "\n" + attempt_run.stderr)[-6000:]
                    returncode = attempt_run.returncode
                except subprocess.TimeoutExpired as exc:
                    agent_log = str(exc)[-6000:]
                    returncode = 124
                candidate = target.read_text(encoding="utf-8")
                # Keep each retry independent: failed candidates are evidence, not a new baseline.
                # Aider may have changed protected source despite the instruction.
                # Restore the original challenge before the next model attempt.

                changed = candidate != vulnerable
                evidence["real_model_invoked"] = True
                rec = {"attempt": index, "aider_exit_code": returncode,
                       "agent_log_tail": agent_log, "edit_applied": changed,
                       "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
                       "diff_tail": "".join(list(difflib.unified_diff(vulnerable.splitlines(True),
                                      candidate.splitlines(True), fromfile="before", tofile="after")))[-6000:],
                       "deterministic_fixes": [], "forge_executed": False, "forge_passed": False}
                if changed:
                    if ((not blind and ("contract VulnerableVault" not in candidate or not candidate.startswith(vulnerable)))
                            or (blind and candidate.count("contract GuardedSettings") != 1)):
                        rec["invalid_edit"] = (
                            "Protected source was changed. Preserve the entire original file prefix "
                            "byte-for-byte and only append the requested standalone contract. "
                            "Do not inherit VulnerableVault: its functions are not virtual. "
                            "Your previous rejected diff follows:\\n" + rec["diff_tail"]
                        )
                    else:
                        forge = checked_run(["forge", "test", "--root", str(workspace),
                                             "--match-contract", test_contract, "-vv"],
                                            str(workspace), 180)
                        pass_count = forge.stdout.count("[PASS]")
                        verified = forge.returncode == 0 and pass_count >= (5 if blind else 2)
                        rec.update(forge_executed=True, forge_exit_code=forge.returncode,
                                   forge_passed=verified, passing_tests=pass_count,
                                   forge_log_tail=(forge.stdout + "\n" + forge.stderr)[-7000:])
                        if verified:
                            evidence["independent_patch_test_passed"] = True
                            evidence["forge_passed"] = True
                            evidence["model_generated_patch"] = True
                evidence["attempts"].append(rec)
                if evidence["independent_patch_test_passed"]:
                    break
                feedback = rec.get("forge_log_tail") or rec.get("invalid_edit") or agent_log
                rec["failure_lesson"] = feedback[-2300:] if not rec["forge_passed"] else ""
                evidence.setdefault("learning_history", []).append({"attempt": index, "failure_lesson": rec["failure_lesson"], "passed": rec["forge_passed"]})
                if index < max_attempts:
                    target.write_text(vulnerable, encoding="utf-8")
    finally:
        output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return evidence


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8091/v1")
    parser.add_argument("--model", default="openai/local-coder")
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--lesson", choices=["reentrancy-01", "held-out-access-control-01"], default="reentrancy-01")
    parser.add_argument("--knowledge-index")
    args = parser.parse_args()
    result = run(args.output, args.base_url, args.model, args.attempts, args.lesson, args.knowledge_index)
    print(json.dumps({"engine": result["engine"], "attempts": len(result["attempts"]),
                      "forge_passed": result["independent_patch_test_passed"]}))
