import json
import subprocess
import sys
import unittest
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
LEARNER = LAB.parent / "learner-materials"

class ContractValidatorTests(unittest.TestCase):
    def run_script(self, name, *args):
        return subprocess.run([PYTHON, str(LAB / "scripts" / name), *args], cwd=LAB, text=True, capture_output=True)

    def setUp(self):
        self.run_script("reset_candidate.py")

    def test_baseline_mutation_repair_is_0_1_0(self):
        baseline = self.run_script("evaluate.py", "--report", "reports/unittest-baseline.json")
        self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)
        mutation = self.run_script("inject_regression.py")
        self.assertEqual(mutation.returncode, 0)
        failed = self.run_script("evaluate.py", "--report", "reports/unittest-mutation.json")
        self.assertEqual(failed.returncode, 1)
        report = json.loads((LAB / "reports/unittest-mutation.json").read_text())
        self.assertEqual(set(report["missing_contracts"]), {"stable_locator", "business_assertion"})
        repair = self.run_script("reset_candidate.py")
        self.assertEqual(repair.returncode, 0)
        green = self.run_script("evaluate.py", "--report", "reports/unittest-repair.json")
        self.assertEqual(green.returncode, 0, green.stdout + green.stderr)

    def test_canonical_contract_contains_the_two_gate_fields(self):
        data = json.loads((LAB / "fixture/canonical_contract.json").read_text())
        self.assertTrue(data["stable_locator"])
        self.assertTrue(data["business_assertion"])

    def test_package_validator_covers_required_samples_and_contract(self):
        result = self.run_script("validate_package.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"status": "PASS"', result.stdout)

    def test_copied_learner_materials_runs_independent_0_1_0(self):
        def run(*args):
            return subprocess.run([PYTHON, str(LEARNER / "scripts/ui_contract_lab.py"), *args], cwd=LEARNER, text=True, capture_output=True)
        valid = run("validate")
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
        baseline = run("baseline", "--report", "reports/test-baseline.json")
        self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)
        mutation = run("mutation", "--report", "reports/test-mutation.json")
        self.assertEqual(mutation.returncode, 1, mutation.stdout + mutation.stderr)
        repair = run("repair", "--report", "reports/test-repair.json")
        self.assertEqual(repair.returncode, 0, repair.stdout + repair.stderr)

if __name__ == "__main__":
    unittest.main()
