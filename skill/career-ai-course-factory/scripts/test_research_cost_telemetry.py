#!/usr/bin/env python3
"""Contract and fault tests for research-cost telemetry."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from compile_research_cost_telemetry import compile_telemetry, event_hash


def make_event(event_id: str, *, scope: str = "neither", total: int | str = "UNKNOWN", surface: str = "luna", phase: str = "classification", status: str = "completed", reuse: str = "NOT-APPLICABLE", invalidation: str = "not-applicable") -> dict:
    tokens = {"input": "UNKNOWN", "output": "UNKNOWN", "total": total}
    if isinstance(total, int):
        output = min(2, total)
        tokens = {"input": total - output, "output": output, "total": total}
    event = {"event_id": event_id, "task_id": "task-1", "run_id": f"run-{event_id}", "attempt_id": f"attempt-{event_id}", "phase": phase, "model": "gpt-5.6-luna" if surface == "luna" else "o3-deep-research", "surface": surface, "measurement_scope": scope, "tokens": tokens, "latency_ms": 25, "status": status, "retry": {"is_retry": False, "retry_index": 0, "retry_of_attempt_id": "UNKNOWN"}, "failure": {"present": False, "category": "UNKNOWN", "code": "UNKNOWN", "message": "UNKNOWN", "unknown_reason": "UNKNOWN"}, "canonical_unit_ids": ["CU-1"], "claim_ids": ["C-1"], "input_artifact_hashes": [], "output_artifact_hashes": [], "reuse_decision": reuse, "invalidation_status": invalidation, "delta_type": "none"}
    event["event_hash"] = event_hash(event)
    return event


class ResearchCostTelemetryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_jsonl(self, name: str, events: list[dict]) -> Path:
        path = self.root / name
        path.write_text("".join(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n" for event in events), encoding="utf-8")
        return path

    def test_compiles_jsonl_and_does_not_infer_savings_from_units(self) -> None:
        path = self.write_jsonl("events.jsonl", [make_event("a", scope="baseline", total=100), make_event("b", scope="current", total="UNKNOWN")])
        result = compile_telemetry([path], root=self.root)
        self.assertEqual(result["summary"]["events_total"], 2)
        self.assertEqual(result["cost_comparison"]["status"], "NOT-COMPUTABLE")
        self.assertEqual(result["cost_comparison"]["tokens_saved"], "UNKNOWN")

    def test_computes_actual_savings_only_from_known_baseline_and_current_totals(self) -> None:
        path = self.write_jsonl("events.jsonl", [make_event("a", scope="baseline", total=100, surface="openai-api"), make_event("b", scope="current", total=60, surface="openai-api")])
        result = compile_telemetry([path], root=self.root)
        self.assertEqual(result["cost_comparison"]["status"], "COMPUTED")
        self.assertEqual(result["cost_comparison"]["tokens_saved"], 40)
        self.assertEqual(result["cost_comparison"]["baseline_total_tokens"], 100)

    def test_provider_summary_distinguishes_surfaces_and_research_phases(self) -> None:
        events = [make_event("a", surface="planner"), make_event("b", surface="openai-api", phase="initial-research"), make_event("c", surface="codex-research", phase="counterevidence", reuse="SOURCE-REUSE-DELTA"), make_event("d", surface="openai-chatgpt", phase="invalidation", invalidation="invalid")]
        path = self.write_jsonl("events.jsonl", events)
        summary = compile_telemetry([path], root=self.root)["summary"]
        self.assertEqual(summary["actual_provider_runs"], 3)
        self.assertEqual(summary["counterevidence_runs"], 1)
        self.assertEqual(summary["source_reuse_delta"], 1)
        self.assertEqual(summary["invalidation_events"], 1)

    def test_tampered_event_hash_is_blocked(self) -> None:
        event = make_event("a")
        event["model"] = "tampered"
        path = self.write_jsonl("events.jsonl", [event])
        with self.assertRaisesRegex(ValueError, "event_hash"):
            compile_telemetry([path], root=self.root)

    def test_duplicate_event_id_is_blocked(self) -> None:
        path = self.write_jsonl("events.jsonl", [make_event("a"), make_event("a")])
        with self.assertRaisesRegex(ValueError, "duplicate event_id"):
            compile_telemetry([path], root=self.root)

    def test_token_total_mismatch_is_blocked(self) -> None:
        event = make_event("a")
        event["tokens"] = {"input": 2, "output": 3, "total": 99}
        event["event_hash"] = event_hash(event)
        path = self.write_jsonl("events.jsonl", [event])
        with self.assertRaisesRegex(ValueError, "total"):
            compile_telemetry([path], root=self.root)

    def test_failed_event_requires_explicit_failure(self) -> None:
        event = make_event("a", status="failed")
        event["event_hash"] = event_hash(event)
        path = self.write_jsonl("events.jsonl", [event])
        with self.assertRaisesRegex(ValueError, "failure"):
            compile_telemetry([path], root=self.root)

    def test_retry_parent_must_exist_in_same_task(self) -> None:
        event = make_event("retry")
        event["retry"] = {"is_retry": True, "retry_index": 1, "retry_of_attempt_id": "missing"}
        event["event_hash"] = event_hash(event)
        path = self.write_jsonl("events.jsonl", [event])
        with self.assertRaisesRegex(ValueError, "retry parent"):
            compile_telemetry([path], root=self.root)

    def test_non_retry_cannot_claim_retry_parent(self) -> None:
        event = make_event("first")
        event["retry"]["retry_of_attempt_id"] = "parent"
        event["event_hash"] = event_hash(event)
        path = self.write_jsonl("events.jsonl", [event])
        with self.assertRaisesRegex(ValueError, "non-retry"):
            compile_telemetry([path], root=self.root)

    def test_luna_tokens_are_lower_cost_and_cannot_compute_provider_savings(self) -> None:
        path = self.write_jsonl("events.jsonl", [make_event("a", scope="baseline", total=100), make_event("b", scope="current", total=60)])
        result = compile_telemetry([path], root=self.root)
        self.assertEqual(result["cost_comparison"]["status"], "NOT-COMPUTABLE")
        self.assertEqual(result["summary"]["lower_cost"]["known_total_tokens"], 160)

    def test_zero_provider_baseline_is_not_computable(self) -> None:
        path = self.write_jsonl("events.jsonl", [make_event("a", scope="baseline", total=0, surface="openai-api"), make_event("b", scope="current", total=60, surface="openai-api")])
        result = compile_telemetry([path], root=self.root)
        self.assertEqual(result["cost_comparison"]["status"], "NOT-COMPUTABLE")
        self.assertEqual(result["cost_comparison"]["tokens_saved"], "UNKNOWN")

    def test_provider_counts_are_unique_attempts_not_events(self) -> None:
        first = make_event("first", surface="openai-api")
        complete = make_event("complete", surface="openai-api")
        complete["attempt_id"] = first["attempt_id"]
        complete["event_hash"] = event_hash(complete)
        path = self.write_jsonl("events.jsonl", [first, complete])
        summary = compile_telemetry([path], root=self.root)["summary"]
        self.assertEqual(summary["actual_provider_runs"], 1)
        self.assertEqual(summary["completed_provider_runs"], 1)

    def test_failure_false_requires_all_details_unknown(self) -> None:
        event = make_event("a")
        event["failure"]["code"] = "E-1"
        event["event_hash"] = event_hash(event)
        path = self.write_jsonl("events.jsonl", [event])
        with self.assertRaisesRegex(ValueError, "details must be UNKNOWN"):
            compile_telemetry([path], root=self.root)

    def test_failure_can_use_explicit_unknown_reason(self) -> None:
        event = make_event("a", status="failed")
        event["failure"] = {"present": True, "category": "UNKNOWN", "code": "UNKNOWN", "message": "UNKNOWN", "unknown_reason": "provider returned no structured error"}
        event["event_hash"] = event_hash(event)
        path = self.write_jsonl("events.jsonl", [event])
        self.assertEqual(compile_telemetry([path], root=self.root)["events"][0]["failure"]["present"], True)

    def test_failure_partial_category_code_without_reason_is_blocked(self) -> None:
        event = make_event("a", status="failed")
        event["failure"] = {"present": True, "category": "provider", "code": "UNKNOWN", "message": "UNKNOWN", "unknown_reason": "UNKNOWN"}
        event["event_hash"] = event_hash(event)
        path = self.write_jsonl("events.jsonl", [event])
        with self.assertRaisesRegex(ValueError, "category/code"):
            compile_telemetry([path], root=self.root)

    def test_json_event_file_and_artifact_hashes_are_supported(self) -> None:
        event = make_event("a")
        digest = "sha256:" + "a" * 64
        event["input_artifact_hashes"] = [digest]
        event["output_artifact_hashes"] = [digest]
        event["event_hash"] = event_hash(event)
        path = self.root / "events.json"
        path.write_text(json.dumps({"events": [event]}), encoding="utf-8")
        result = compile_telemetry([path], root=self.root)
        self.assertEqual(result["events"][0]["input_artifact_hashes"], [digest])

    def test_path_escape_is_blocked(self) -> None:
        outside = self.root.parent / "outside.jsonl"
        outside.write_text(json.dumps(make_event("a")) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "outside root"):
            compile_telemetry([Path("..") / outside.name], root=self.root)


if __name__ == "__main__":
    unittest.main()
