import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import oracle
import platform_lab


class PlatformLabTests(unittest.TestCase):
    def test_baseline_is_green(self):
        self.assertEqual(oracle.report(platform_lab.build_state())["verdict"], "PASS")

    def test_each_fault_is_red(self):
        for mutation in ("stale_sha", "replay", "rbac", "missing_report"):
            with self.subTest(mutation=mutation):
                result = oracle.report(platform_lab.build_state(mutation), "MUT-" + mutation)
                self.assertEqual(result["verdict"], "FAIL")
                self.assertTrue(result["failed_oracle_ids"])

    def test_ai_candidate_cannot_self_approve(self):
        state = platform_lab.build_state()
        state["candidate"]["auto_approved"] = True
        self.assertIn("AI-HUMAN-BOUNDARY", oracle.report(state)["failed_oracle_ids"])


if __name__ == "__main__":
    unittest.main()
