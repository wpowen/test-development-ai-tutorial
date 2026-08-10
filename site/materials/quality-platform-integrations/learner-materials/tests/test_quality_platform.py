import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import quality_platform
import subprocess

class LearnerMaterialTests(unittest.TestCase):
    def test_baseline_and_repair_green(self):
        self.assertFalse([x for x in quality_platform.check(quality_platform.state()) if not x["passed"]])
    def test_mutations_red(self):
        for name in ("stale_sha", "replay", "rbac", "missing-report"):
                self.assertTrue([x for x in quality_platform.check(quality_platform.state(name)) if not x["passed"]])

    def test_fixed_topic_entrypoints_are_live(self):
        root = Path(__file__).resolve().parents[1]
        names = ("basis_gate_and_candidate_review.py", "gitlab_sha_junit_gate.py", "ephemeral_namespace_cleanup.py", "event_replay_and_reconcile.py")
        for name in names:
            path = root / "scripts" / name
            self.assertTrue(path.is_file() and path.stat().st_size > 100, name)
            result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"topic"', result.stdout)
