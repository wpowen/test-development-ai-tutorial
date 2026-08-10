import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from reliability_lab import run


ROOT = Path(__file__).parent / "configs"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class ReliabilityLabTests(unittest.TestCase):
    def test_three_stage_gate_is_0_1_0(self):
        baseline, _ = run(load("baseline.json"))
        fault, _ = run(load("latency-retry-fault.json"))
        repaired, _ = run(load("repaired.json"))
        self.assertTrue(baseline["gate_pass"])
        self.assertFalse(fault["gate_pass"])
        self.assertTrue(repaired["gate_pass"])
        self.assertGreater(fault["metrics"]["queue_p95_ms"], baseline["metrics"]["queue_p95_ms"])
        self.assertGreater(fault["metrics"]["retry_amplification"], baseline["metrics"]["retry_amplification"])

    def test_machine_readable_trace_has_task_and_attempt_fields(self):
        summary, traces = run(load("baseline.json"))
        self.assertEqual(summary["metrics"]["admitted_tasks"], len(traces))
        for trace in traces[:5]:
            self.assertIn("task_id", trace)
            self.assertIn("trace_id", trace)
            self.assertIn("terminal_state", trace)
            self.assertIsInstance(trace["events"], list)

    def test_percentiles_are_deterministic_and_cost_is_reported(self):
        first, _ = run(load("baseline.json"))
        second, _ = run(load("baseline.json"))
        self.assertEqual(first, second)
        self.assertGreater(first["metrics"]["cost_per_success"], 0)


if __name__ == "__main__":
    unittest.main()
