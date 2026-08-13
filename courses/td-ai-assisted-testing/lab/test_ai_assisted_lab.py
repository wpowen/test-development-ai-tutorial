import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class LabTests(unittest.TestCase):
    def run_case(self, topic: str, phase: str, expected: int):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.json"
            result = subprocess.run([sys.executable, "ai_assisted_lab.py", "run", "--topic", topic, "--phase", phase, "--report", str(report)], cwd=ROOT, check=False, capture_output=True, text=True)
            self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual("NOT_RUN", payload["model_evidence"])
            self.assertIn(payload["status"], {"PASS", "FAIL", "BLOCKED", "UNKNOWN"})

    def test_all_cycles(self):
        expected_fault = {"TD-T05": 2, "TD-T06": 1, "TD-T07": 1, "TD-T08": 2}
        for topic in expected_fault:
            with self.subTest(topic=topic, phase="baseline"):
                self.run_case(topic, "baseline", 0)
            with self.subTest(topic=topic, phase="fault"):
                self.run_case(topic, "fault", expected_fault[topic])
            with self.subTest(topic=topic, phase="repair"):
                self.run_case(topic, "repair", 0)


if __name__ == "__main__":
    unittest.main()
