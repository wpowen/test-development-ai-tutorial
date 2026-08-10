import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/api_automation.py"


def run_mode(mode, report_path):
    return subprocess.run(
        [sys.executable, "scripts/api_automation.py", mode, "--report", str(report_path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


class LearnerMaterialsContract(unittest.TestCase):
    def test_baseline_mutation_repair_from_package_root_is_0_1_0(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report_dir = Path(temp_dir)
            runs = {mode: run_mode(mode, report_dir / f"{mode}.json") for mode in ("baseline", "mutation", "repair")}
            self.assertEqual([runs[m].returncode for m in ("baseline", "mutation", "repair")], [0, 1, 0])
            reports = {mode: json.loads((report_dir / f"{mode}.json").read_text(encoding="utf-8")) for mode in runs}
            self.assertEqual([reports[m]["status"] for m in ("baseline", "mutation", "repair")], ["PASS", "FAIL", "PASS"])
            self.assertEqual(reports["mutation"]["failed_case_ids"], ["BUS-SHIPPED-REJECT"])
            for report in reports.values():
                self.assertEqual(report["workdir_contract"], "learner-materials root")
                self.assertEqual(report["not_run"][:4], ["Schemathesis", "Pact", "k6", "GitLab CI"])

    def test_json_and_yaml_text_are_readable_without_third_party_packages(self):
        checkout = json.loads((ROOT / "fixtures/checkout-events.json").read_text(encoding="utf-8"))
        self.assertTrue(checkout["synthetic_data"])
        yaml_paths = [
            ROOT / "fixtures/order-cancel.openapi.yaml",
            ROOT / "fixtures/payment-intent.openapi.yaml",
            ROOT / "configs/schema-mutations.yaml",
            ROOT / "configs/ai-performance-workload.yaml",
        ]
        for path in yaml_paths:
            text = path.read_text(encoding="utf-8")
            self.assertGreater(len(text), 200, path)
            self.assertNotIn("TODO", text, path)
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("import yaml", script)
        self.assertNotIn("from yaml", script)

    def test_copied_package_runs_without_course_lab(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            copied = Path(temp_dir) / "learner-materials"
            shutil.copytree(ROOT, copied)
            result = subprocess.run(
                [sys.executable, "scripts/api_automation.py", "baseline", "--report", "reports/copied-baseline.json"],
                cwd=copied,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((copied / "reports/copied-baseline.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["workdir_contract"], "learner-materials root")


if __name__ == "__main__":
    unittest.main()
