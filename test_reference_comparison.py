"""Regression checks for the known-good local teaching reference.

These checks only verify the existing reference; they do not grant model credit.
"""
import unittest
from pathlib import Path


class ReferenceComparisonTest(unittest.TestCase):
    def test_reference_and_vulnerable_are_distinct(self):
        source = Path("student_lab/contracts/VulnerableVault.sol").read_text()
        self.assertIn("contract VulnerableVault", source)
        self.assertIn("contract FixedVault", source)
        vulnerable, reference = source.split("contract FixedVault", 1)
        self.assertLess(vulnerable.index("msg.sender.call"), vulnerable.index("balances[msg.sender] = 0"))
        self.assertLess(reference.index("balances[msg.sender] = 0"), reference.index("msg.sender.call"))

    def test_reference_behavior_has_foundry_regression(self):
        test = Path("student_lab/test/ReentrancyLesson.t.sol").read_text()
        self.assertIn("testVulnerableVaultCanBeDrained", test)
        self.assertIn("testFixedVaultResistsReentrancy", test)


if __name__ == "__main__":
    unittest.main()
