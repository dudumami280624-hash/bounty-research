"""Offline safety and invocation tests for the upstream Aider bridge."""
import tempfile
import unittest
from pathlib import Path

from student_aider_bridge import local_endpoint, run


class UpstreamAiderBridgeTests(unittest.TestCase):
    def test_accepts_loopback_only(self):
        self.assertEqual(local_endpoint("http://127.0.0.1:8091/v1"), "http://127.0.0.1:8091/v1")
        self.assertEqual(local_endpoint("http://localhost:8091/v1/"), "http://localhost:8091/v1")

    def test_rejects_remote_paid_api(self):
        for value in ["https://api.openai.com/v1", "http://example.com/v1",
                      "https://127.0.0.1:8091/v1", "http://127.0.0.1:8091/v1?token=x"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                local_endpoint(value)

    def test_bounded_attempts(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                run(Path(temp) / "result.json", max_attempts=0)
            with self.assertRaises(ValueError):
                run(Path(temp) / "result.json", max_attempts=4)

    def test_model_name_is_local_compatible(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                run(Path(temp) / "result.json", model="remote-provider/model")


if __name__ == "__main__":
    unittest.main()
