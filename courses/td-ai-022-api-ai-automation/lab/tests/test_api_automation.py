import json
import subprocess
import sys
import unittest
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
SCRIPT = LAB / "api_automation.py"

def cmd(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=LAB, text=True, capture_output=True)

class ApiAutomationProof(unittest.TestCase):
    def test_spec_candidates_include_runtime_surfaces(self):
        self.assertEqual(cmd("all", "--report", "unittest-baseline.json").returncode, 0)
        cases = json.loads((LAB / "state/candidate-cases.json").read_text())['cases']
        self.assertEqual({c['kind'] for c in cases}, {'contract','business','permission','idempotency','async','sse'})

    def test_mutation_is_red_and_repair_is_green(self):
        self.assertEqual(cmd("all", "--report", "unittest-baseline-2.json").returncode, 0)
        self.assertEqual(cmd("inject-defect").returncode, 0)
        mutation = cmd("run", "--report", "unittest-mutation.json")
        self.assertEqual(mutation.returncode, 1)
        report = json.loads((LAB / "reports/unittest-mutation.json").read_text())
        self.assertIn("BUS-SHIPPED-REJECT", [r['case_id'] for r in report['results'] if r['status']=='FAIL'])
        self.assertEqual(cmd("repair").returncode, 0)
        self.assertEqual(cmd("run", "--report", "unittest-repair.json").returncode, 0)

if __name__ == "__main__": unittest.main()
