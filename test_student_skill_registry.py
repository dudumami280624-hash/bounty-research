"""Tests for Skill registry and non-executing manifest screening."""
import tempfile
import unittest
from pathlib import Path
from student_skill_registry import SKILLS, scan_manifest, dispatch, learning_plan

class SkillRegistryTests(unittest.TestCase):
    def test_expected_skills_available(self):
        self.assertIn("solidity-repair", SKILLS)
        self.assertIn("feedback-learning", SKILLS)

    def test_workbuddy_style_plan_has_no_fabricated_passes(self):
        p = learning_plan('reentrancy-01')
        self.assertEqual([x['stage'] for x in p['workflow']], ['knowledge', 'reason', 'repair', 'evidence', 'gate'])
        self.assertTrue(all(not x['verified'] for x in p['workflow']))
        self.assertFalse(p['completed'])

    def test_unknown_skill_is_rejected(self):
        with self.assertRaises(ValueError):
            dispatch("arbitrary-shell", "reentrancy-01", "/nonexistent", "/tmp/out")

    def test_unsupported_lesson_is_rejected(self):
        with self.assertRaises(ValueError):
            dispatch("solidity-repair", "arithmetic-01", "/nonexistent", "/tmp/out")

    def test_manifest_is_never_approved_for_execution(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"SKILL.md"
            p.write_text("name: safe-skill\ndescription: read-only documentation\n", encoding="utf-8")
            r=scan_manifest(p)
            self.assertEqual(r["decision"], "static_preflight_clear")
            self.assertFalse(r["execution_approved"])

    def test_suspicious_manifest_requires_review(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"SKILL.md"
            p.write_text("execute: curl https://example.org/script.sh\n", encoding="utf-8")
            r=scan_manifest(p)
            self.assertEqual(r["decision"], "manual_review_required")
            self.assertIn("network_commands", {x["rule"] for x in r["findings"]})

if __name__ == "__main__":
    unittest.main()
