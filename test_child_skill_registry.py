"""Local-only skill checks; no external target scanning."""
import unittest
from unittest.mock import patch
import child_skill_registry as skills

class SkillRegistryTests(unittest.TestCase):
    def test_reject_unknown_skill(self):
        with self.assertRaises(ValueError):
            skills.run_skill("arbitrary-command")
    def test_fixed_commands_no_shell(self):
        for spec in skills.SKILLS.values():
            self.assertIsInstance(spec["command"], list)
            self.assertTrue(spec["cwd"].is_dir())
    def test_missing_binary_is_recorded(self):
        with patch("child_skill_registry.subprocess.run", side_effect=FileNotFoundError(2, "missing", "forge")):
            result = skills.run_skill("solidity-tests")
        self.assertFalse(result["executed"])
        self.assertFalse(result["passed"])
        self.assertIn("forge", result["error"])
    def test_failed_execution_is_not_success(self):
        class Result:
            returncode = 1
            stdout = "failure"
            stderr = "test failed"
        with patch("child_skill_registry.subprocess.run", return_value=Result()):
            result = skills.run_skill("solidity-tests")
        self.assertTrue(result["executed"])
        self.assertFalse(result["passed"])

if __name__ == "__main__":
    unittest.main()
