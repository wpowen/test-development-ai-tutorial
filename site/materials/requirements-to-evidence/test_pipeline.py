#!/usr/bin/env python3
"""Regression tests for the eight-page deterministic teaching fixture."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PAGE_IDS = [f"TD-P0{index}" for index in range(1, 9)]


class LifecycleFixtureTests(unittest.TestCase):
    def run_pipeline(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "pipeline.py", *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_each_page_has_an_exact_owner_manifest_and_red_green_cycle(self) -> None:
        for page_id in PAGE_IDS:
            with self.subTest(page_id=page_id):
                manifest = json.loads((ROOT / "page-manifests" / f"{page_id}.json").read_text(encoding="utf-8"))
                prompt_manifest = json.loads((ROOT / "page-prompts" / page_id / "manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(manifest["owner_page_ids"], [page_id])
                self.assertEqual(prompt_manifest["owner_page_ids"], [page_id])
                self.assertEqual(prompt_manifest["provider"], "none")
                self.assertEqual(prompt_manifest["model_status"], "NOT_RUN")
                result = self.run_pipeline("page-cycle", "--page", page_id, "--report", f"reports/{page_id}-cycle.json")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                report = json.loads((ROOT / "reports" / f"{page_id}-cycle.json").read_text(encoding="utf-8"))
                self.assertEqual([phase["status"] for phase in report["phases"]], ["PASS", "FAIL", "PASS"])
                self.assertEqual(report["evidence_status"], "fixture-tested")
                self.assertEqual(report["model_status"], "NOT_RUN")

    def test_trace_result_is_not_a_model_pass_without_a_model_run(self) -> None:
        trace = json.loads((ROOT / "traceability.json").read_text(encoding="utf-8"))
        result = next(item for item in trace["links"] if item["id"] == "RESULT-SHIPPED")
        receipt = json.loads((ROOT / result["run_receipt"]).read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "PASS_FIXTURE")
        self.assertEqual(receipt["receipt_type"], "deterministic-fixture")
        self.assertEqual(receipt["model_status"], "NOT_RUN")
        self.assertEqual(receipt["provider"], "none")


if __name__ == "__main__":
    unittest.main()
