#!/usr/bin/env python3
"""Regression tests for the eight-page deterministic teaching fixture."""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PAGE_IDS = [f"TD-P0{index}" for index in range(1, 9)]
PACKAGE_FILES = [
    "system-v1.md",
    "task-v1.md",
    "critic-v1.md",
    "input.json",
    "schema.json",
    "eval.json",
    "mutation.json",
    "manifest.json",
    "adaptation-card.md",
    "expected-output.json",
    "receipt.json",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
                self.assertTrue(prompt_manifest["direct_use"])
                self.assertEqual(prompt_manifest["copy_target"], "generic-ai-agent")
                prompt = (ROOT / "page-prompts" / page_id / "prompt-v1.md").read_text(encoding="utf-8")
                for marker in ("## 能做什么", "## 直接复制到 AI Agent", "## 修改这些字段就能复用", "## 结果自检", "## 停止条件与边界"):
                    self.assertIn(marker, prompt)
                result = self.run_pipeline("page-cycle", "--page", page_id, "--report", f"reports/{page_id}-cycle.json")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                report = json.loads((ROOT / "reports" / f"{page_id}-cycle.json").read_text(encoding="utf-8"))
                self.assertEqual([phase["status"] for phase in report["phases"]], ["PASS", "FAIL", "PASS"])
                self.assertEqual(report["evidence_status"], "fixture-tested")
                self.assertEqual(report["model_status"], "NOT_RUN")

    def test_each_page_has_a_complete_versioned_prompt_package(self) -> None:
        for page_id in PAGE_IDS:
            with self.subTest(page_id=page_id):
                directory = ROOT / "page-prompts" / page_id
                for filename in PACKAGE_FILES:
                    self.assertTrue((directory / filename).is_file(), f"{page_id} missing {filename}")

                manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
                schema = json.loads((directory / "schema.json").read_text(encoding="utf-8"))
                expected = json.loads((directory / "expected-output.json").read_text(encoding="utf-8"))
                evaluation = json.loads((directory / "eval.json").read_text(encoding="utf-8"))
                mutation = json.loads((directory / "mutation.json").read_text(encoding="utf-8"))
                receipt = json.loads((directory / "receipt.json").read_text(encoding="utf-8"))
                card = (directory / "adaptation-card.md").read_text(encoding="utf-8")

                self.assertEqual(manifest["owner_page_ids"], [page_id])
                self.assertEqual(manifest["provider"], "none")
                self.assertEqual(manifest["model_status"], "NOT_RUN")
                self.assertEqual(manifest["assembly_order"][0]["file"], "system-v1.md")
                self.assertEqual(manifest["assembly_order"][1]["file"], "task-v1.md")
                self.assertEqual(manifest["assembly_order"][2]["file"], "input.json")
                self.assertIn("critic-v1.md", [step["file"] for step in manifest["assembly_order"]])
                self.assertIn("prompt-v1.md", manifest["one_shot_copy_file"])
                for filename, digest in manifest["artifact_sha256"].items():
                    self.assertEqual(digest, sha256(directory / filename), f"{page_id} hash drift: {filename}")

                self.assertEqual(set(expected), set(schema["required"]))
                self.assertEqual(expected["page_id"], page_id)
                self.assertIn(expected["status"], schema["properties"]["status"]["enum"])
                self.assertEqual(
                    {case["case_type"] for case in evaluation["cases"]},
                    {"positive", "boundary", "conflict", "missing", "unauthorized", "refusal", "truncation", "locale"},
                )
                self.assertTrue(all(case["result"] == "NOT_RUN" for case in evaluation["cases"]))
                self.assertGreaterEqual(len(mutation["mutations"]), 6)
                self.assertTrue(all(case["result"] == "NOT_RUN" for case in mutation["mutations"]))
                self.assertEqual(receipt["receipt_type"], "static-package-build-receipt")
                self.assertEqual(receipt["model_status"], "NOT_RUN")
                self.assertEqual(receipt["raw_output_refs"], [])
                self.assertEqual(receipt["raw_output_sha256"], [])
                self.assertIn("没有调用模型", receipt["claim_boundary"])
                for marker in ("组合顺序", "system-v1.md", "task-v1.md", "critic-v1.md", "prompt-v1.md", "NOT_RUN"):
                    self.assertIn(marker, card)

                system_prompt = (directory / "system-v1.md").read_text(encoding="utf-8")
                task_prompt = (directory / "task-v1.md").read_text(encoding="utf-8")
                critic_prompt = (directory / "critic-v1.md").read_text(encoding="utf-8")
                self.assertEqual(len({system_prompt, task_prompt, critic_prompt}), 3)
                for prompt in (system_prompt, task_prompt, critic_prompt):
                    self.assertIn(page_id, prompt)
                    self.assertIn("BLOCKED", prompt)
                    self.assertIn("Unknown", prompt)

    def test_trace_result_is_not_a_model_pass_without_a_model_run(self) -> None:
        trace = json.loads((ROOT / "traceability.json").read_text(encoding="utf-8"))
        result = next(item for item in trace["links"] if item["id"] == "RESULT-SHIPPED")
        receipt = json.loads((ROOT / result["run_receipt"]).read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "PASS_FIXTURE")
        self.assertEqual(receipt["receipt_type"], "deterministic-fixture")
        self.assertEqual(receipt["model_status"], "NOT_RUN")
        self.assertEqual(receipt["provider"], "none")

    def test_direct_use_manifest_keeps_model_evidence_not_run(self) -> None:
        manifest = json.loads((ROOT / "DIRECT-USE-MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["page_ids"], PAGE_IDS)
        self.assertEqual(manifest["prompt_count"], 8)
        self.assertEqual(manifest["copy_target"], "generic-ai-agent")
        self.assertEqual(manifest["model_status"], "NOT_RUN")
        for package in manifest["packages"]:
            self.assertEqual(set(package["files"]), set(PACKAGE_FILES + ["prompt-v1.md"]))
            self.assertEqual(package["model_status"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
