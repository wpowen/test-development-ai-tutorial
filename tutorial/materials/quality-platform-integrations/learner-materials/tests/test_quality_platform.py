import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import quality_platform
import subprocess
import json
import tempfile

class LearnerMaterialTests(unittest.TestCase):
    def test_baseline_and_repair_green(self):
        self.assertFalse([x for x in quality_platform.check(quality_platform.state()) if not x["passed"]])
    def test_mutations_red(self):
        for name in ("stale_sha", "replay", "rbac", "missing-report"):
                self.assertTrue([x for x in quality_platform.check(quality_platform.state(name)) if not x["passed"]])

    def test_topic_cycles_prove_green_red_green(self):
        root = Path(__file__).resolve().parents[1]
        names = ("basis_gate_and_candidate_review.py", "gitlab_sha_junit_gate.py", "ephemeral_namespace_cleanup.py", "event_replay_and_reconcile.py")
        for name in names:
            path = root / "scripts" / name
            self.assertTrue(path.is_file() and path.stat().st_size > 100, name)
            with tempfile.TemporaryDirectory(dir=root) as temp:
                relative = str(Path(temp).relative_to(root))
                result = subprocess.run([sys.executable, str(path), "cycle", "--report-dir", relative], capture_output=True, text=True)
                summary = json.loads((Path(temp) / "cycle-summary.json").read_text())
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(summary["observed_exit_codes"], [0, 1, 0])

    def test_each_fault_has_a_named_failed_oracle(self):
        from topic_cycle import make_report
        for topic in ("TD-QP01", "TD-QP02", "TD-QP03", "TD-QP04"):
            report = make_report(topic, "fault")
            self.assertEqual(report["verdict"], "FAIL")
            self.assertTrue(report["failed_oracle_ids"])
            self.assertEqual(report["not_run"][0], "live Jira tenant")
