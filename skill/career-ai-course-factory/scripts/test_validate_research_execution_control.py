import json
import tempfile
import unittest
from pathlib import Path

from validate_research_execution_control import validate


class ResearchExecutionControlTests(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads((Path(__file__).resolve().parents[1] / "assets/schemas/research-execution-control.v1.schema.json").read_text())

    def base(self):
        return {
            "schema_version": "research-execution-control.v1",
            "control_id": "control-canary",
            "goal_id": "goal-103-pages",
            "status": "ACTIVE",
            "scope": {"pages_expected": 103, "claims_expected": 40557, "release_targets": ["github-pages", "chatgpt-site"]},
            "batch": {"index": 1, "claim_ids": ["C-1"], "canonical_unit_ids": ["U-1"], "phase": "initial-research", "surface": "openai-chatgpt", "max_claims": 1, "max_provider_runs": 1, "max_elapsed_minutes": 5, "max_total_tokens": "UNKNOWN"},
            "counters": {"claims_started": 1, "provider_runs": 0, "elapsed_minutes": 1, "total_tokens": "UNKNOWN", "checkpoints_without_progress": 0},
            "checkpoint": {"interval_minutes": 1, "last_progress": "started", "progress_artifact_hashes": []},
            "stop_reason": "UNKNOWN",
            "next_action": "wait",
        }

    def test_first_batch_is_bounded(self):
        self.assertEqual(validate(self.base(), self.schema), [])

    def test_active_timeout_is_blocked(self):
        doc = self.base(); doc["counters"]["elapsed_minutes"] = 5
        self.assertTrue(any("max_elapsed_minutes" in error for error in validate(doc, self.schema)))

    def test_no_progress_requires_stop(self):
        doc = self.base(); doc["counters"]["checkpoints_without_progress"] = 2
        self.assertTrue(any("checkpoints" in error for error in validate(doc, self.schema)))

    def test_completion_needs_artifact(self):
        doc = self.base(); doc["status"] = "COMPLETED-RECEIPT"; doc["stop_reason"] = "receipt"; doc["counters"]["provider_runs"] = 1
        self.assertTrue(any("output_artifact_hashes" in error for error in validate(doc, self.schema)))

    def test_timeout_is_terminal(self):
        doc = self.base(); doc["status"] = "TIMEOUT"; doc["stop_reason"] = "elapsed cap"; doc["next_action"] = "record blocked"
        self.assertEqual(validate(doc, self.schema), [])


if __name__ == "__main__":
    unittest.main()
