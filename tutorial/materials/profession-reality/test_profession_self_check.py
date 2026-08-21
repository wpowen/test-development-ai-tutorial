import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parent


class ProfessionSelfCheckTests(unittest.TestCase):
    def run_phase(self, phase: str):
        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / f"{phase}.json"
            completed = subprocess.run(
                ["python3", "profession_self_check.py", "phase", "--phase", phase, "--report", str(report)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            return completed, json.loads(report.read_text())

    def test_baseline_fault_repair_cycle_is_observable(self):
        baseline, baseline_report = self.run_phase("baseline")
        fault, fault_report = self.run_phase("fault")
        repair, repair_report = self.run_phase("repair")

        self.assertEqual(0, baseline.returncode)
        self.assertEqual("PASS_FIXTURE", baseline_report["status"])
        self.assertEqual(1, fault.returncode)
        self.assertEqual("FAIL_EXPECTED", fault_report["status"])
        self.assertEqual(0, repair.returncode)
        self.assertEqual("PASS_FIXTURE", repair_report["status"])
        self.assertIn("independent_oracle", fault_report["failed_checks"])
        self.assertIn("human_release_owner", fault_report["failed_checks"])

    def test_prompt_contract_is_versioned_and_offline(self):
        manifest = json.loads((ROOT / "prompts/TD-F01/manifest.json").read_text())
        evaluation = json.loads((ROOT / "prompts/TD-F01/eval.json").read_text())

        self.assertEqual(["TD-F01"], manifest["owner_page_ids"])
        self.assertEqual("1.0.0", manifest["version"])
        self.assertEqual("none", manifest["provider"])
        self.assertEqual("NOT_RUN", manifest["model_status"])
        self.assertGreaterEqual(len(evaluation["cases"]), 5)
        self.assertGreaterEqual(len(evaluation["mutations"]), 3)

    def test_manifest_declares_exact_failure_cycle(self):
        manifest = json.loads((ROOT / "manifest.json").read_text())
        self.assertEqual(["TD-F01"], manifest["owner_page_ids"])
        self.assertEqual("materials/profession-reality", manifest["working_directory"])
        steps = {step["step_id"]: step for step in manifest["steps"]}
        self.assertEqual(0, steps["baseline"]["expected_exit_code"])
        self.assertEqual(1, steps["fault"]["expected_exit_code"])
        self.assertEqual(0, steps["repair"]["expected_exit_code"])
        self.assertEqual("cycle", manifest["page_command_step_id"])


if __name__ == "__main__":
    unittest.main()
