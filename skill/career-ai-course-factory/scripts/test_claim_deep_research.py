#!/usr/bin/env python3
"""Offline regression tests for the claim-level OpenAI Deep Research runner."""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from run_claim_deep_research import (
    append_completed_receipt,
    build_request_payload,
    build_tools,
    extract_response_artifacts,
    load_claim,
    main,
    validate_completed_artifacts,
    wait_for_terminal_response,
    sha256_path,
)


class ClaimDeepResearchTests(unittest.TestCase):
    @staticmethod
    def write_minimal_topic(package_root: Path) -> tuple[Path, Path]:
        topic_dir = package_root / "research/topics/topic-1"
        topic_dir.mkdir(parents=True)
        manuscript = topic_dir / "manuscript.md"
        manuscript.write_text("# Fixture\n", encoding="utf-8")
        digest = sha256_path(manuscript)
        (topic_dir / "claim-inventory.json").write_text(
            json.dumps(
                {
                    "schema_version": "claim-inventory.v1",
                    "topic_id": "topic-1",
                    "root_manifest": {"schema_version": "locator-root-manifest.v1", "package_relative_priority": True, "roots": {"topic": {"kind": "topic", "path": "research/topics/topic-1"}, "package": {"kind": "package", "path": "."}}},
                    "extraction": {"author_id": "author", "independent_auditor_id": "auditor", "source_files": ["manuscript.md"], "source_hashes": {"manuscript.md": digest}, "locator_ledger": [{"locator": "topic:manuscript.md:L1-L1", "canonical_key": "topic:manuscript.md:L1-L1", "root_alias": "topic", "resolved_path": "manuscript.md", "sha256": digest, "selector": None, "selector_kind": None, "selector_value": None, "line_start": 1, "line_end": 1, "line_count": 1, "claim_ids": ["C-01"]}], "unmapped_propositions": 0},
                    "claims": [
                        {
                            "claim_id": "C-01",
                            "statement": "A bounded technical proposition.",
                            "claim_type": "mechanism",
                            "risk": "high",
                            "scope": "versioned environment",
                            "source_locations": ["topic:manuscript.md:L1-L1"],
                            "proposed_disposition": "SCOPED",
                            "required_dimensions": ["terminology-boundary"],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        prompt_path = package_root / "prompt.md"
        prompt_path.write_text("Inspect primary and disconfirming evidence.", encoding="utf-8")
        return topic_dir, prompt_path

    def test_load_claim_requires_exact_inventory_member(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package_root = Path(tmp)
            topic_dir = package_root / "research/topics/topic-1"
            topic_dir.mkdir(parents=True)
            manuscript = topic_dir / "manuscript.md"
            manuscript.write_text("# Fixture\n", encoding="utf-8")
            digest = sha256_path(manuscript)
            (topic_dir / "claim-inventory.json").write_text(
                json.dumps(
                    {
                        "schema_version": "claim-inventory.v1",
                        "topic_id": "topic-1",
                        "root_manifest": {"schema_version": "locator-root-manifest.v1", "package_relative_priority": True, "roots": {"topic": {"kind": "topic", "path": "research/topics/topic-1"}, "package": {"kind": "package", "path": "."}}},
                        "extraction": {"author_id": "author", "independent_auditor_id": "auditor", "source_files": ["manuscript.md"], "source_hashes": {"manuscript.md": digest}, "locator_ledger": [{"locator": "topic:manuscript.md:L1-L1", "canonical_key": "topic:manuscript.md:L1-L1", "root_alias": "topic", "resolved_path": "manuscript.md", "sha256": digest, "selector": None, "selector_kind": None, "selector_value": None, "line_start": 1, "line_end": 1, "line_count": 1, "claim_ids": ["C-01"]}], "unmapped_propositions": 0},
                        "claims": [
                            {
                                "claim_id": "C-01",
                                "statement": "A bounded technical proposition.",
                                "claim_type": "mechanism",
                                "risk": "high",
                                "scope": "versioned environment",
                                "source_locations": ["topic:manuscript.md:L1-L1"],
                                "proposed_disposition": "SCOPED",
                                "required_dimensions": ["terminology-boundary"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            claim = load_claim(topic_dir, "C-01")
            self.assertEqual(claim["claim_id"], "C-01")
            with self.assertRaisesRegex(ValueError, "not found"):
                load_claim(topic_dir, "C-99")

    def test_request_is_background_and_contains_one_atomic_claim(self) -> None:
        payload = build_request_payload(
            model="current-deep-research-model",
            prompt="Research only claim C-01.",
            tools=[{"type": "web_search_preview"}],
            metadata={"topic_id": "topic-1", "claim_id": "C-01", "phase": "initial-deep-research"},
        )
        self.assertTrue(payload["background"])
        self.assertEqual(payload["model"], "current-deep-research-model")
        self.assertEqual(payload["input"], "Research only claim C-01.")
        self.assertEqual(payload["metadata"]["claim_id"], "C-01")
        self.assertEqual(payload["include"], ["web_search_call.action.sources"])
        with self.assertRaisesRegex(ValueError, "model"):
            build_request_payload(model="", prompt="x", tools=[{"type": "web_search_preview"}], metadata={})

    def test_public_and_private_sources_cannot_mix_implicitly(self) -> None:
        with self.assertRaisesRegex(ValueError, "mixed public/private"):
            build_tools(
                web_enabled=True,
                web_tool_type="web_search_preview",
                vector_store_ids=[],
                mcp_server_url="https://mcp.example.test",
                mcp_server_label="private-docs",
                allow_mixed_public_private=False,
            )

        tools, data_sources = build_tools(
            web_enabled=False,
            web_tool_type="web_search_preview",
            vector_store_ids=["vs_123"],
            mcp_server_url="",
            mcp_server_label="",
            allow_mixed_public_private=False,
        )
        self.assertEqual(data_sources, ["file_search"])
        self.assertEqual(tools[0]["vector_store_ids"], ["vs_123"])

    def test_extracts_report_citations_and_tool_trajectory(self) -> None:
        response = {
            "id": "resp_123",
            "status": "completed",
            "model": "current-deep-research-model",
            "output": [
                {
                    "type": "web_search_call",
                    "id": "ws_1",
                    "status": "completed",
                    "action": {
                        "type": "open_page",
                        "url": "https://example.test/primary",
                        "sources": [
                            {"url": "https://example.test/primary"},
                            {"url": "https://example.test/corroborating"},
                        ],
                    },
                },
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "Bounded finding.",
                            "annotations": [
                                {
                                    "type": "url_citation",
                                    "url": "https://example.test/primary",
                                    "title": "Primary source",
                                    "start_index": 0,
                                    "end_index": 7,
                                }
                            ],
                        }
                    ],
                },
            ],
        }

        artifacts = extract_response_artifacts(response)
        self.assertEqual(artifacts["report"], "Bounded finding.")
        self.assertEqual(len(artifacts["citations"]), 1)
        self.assertEqual(len(artifacts["tool_calls"]), 1)
        self.assertEqual(artifacts["opened_source_count"], 1)
        validate_completed_artifacts(response, artifacts)

    def test_citations_and_search_sources_do_not_prove_opening(self) -> None:
        response = {
            "id": "resp_123",
            "status": "completed",
            "model": "current-deep-research-model",
            "output": [
                {
                    "type": "web_search_call",
                    "id": "ws_1",
                    "status": "completed",
                    "action": {
                        "type": "search",
                        "query": "bounded claim",
                        "sources": [{"url": "https://example.test/search-result"}],
                    },
                },
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{
                        "type": "output_text",
                        "text": "Bounded finding.",
                        "annotations": [{
                            "type": "url_citation",
                            "url": "https://example.test/search-result",
                            "title": "Search result",
                            "start_index": 0,
                            "end_index": 7,
                        }],
                    }],
                },
            ],
        }

        artifacts = extract_response_artifacts(response)
        self.assertEqual(artifacts["opened_source_count"], 0)
        with self.assertRaisesRegex(ValueError, "opened source"):
            validate_completed_artifacts(response, artifacts)

    def test_completed_artifacts_fail_closed_without_trace_or_citations(self) -> None:
        response = {"id": "resp_empty", "status": "completed", "output": []}
        artifacts = extract_response_artifacts(response)
        with self.assertRaisesRegex(ValueError, "report"):
            validate_completed_artifacts(response, artifacts)

    def test_receipt_append_is_idempotent_and_topic_bound(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            topic_dir = Path(tmp)
            receipt = {
                "run_id": "c-01-r1",
                "claim_ids": ["C-01"],
                "round": 1,
                "phase": "initial-deep-research",
                "provider": "openai",
                "surface": "openai-responses-api",
                "model_or_feature": "current-deep-research-model",
                "response_or_export_id": "resp_123",
                "started_at": "2026-08-18T00:00:00Z",
                "completed_at": "2026-08-18T00:01:00Z",
                "request_path": "deep-research/c-01-r1/request.md",
                "raw_response_path": "deep-research/c-01-r1/raw-response.json",
                "report_path": "deep-research/c-01-r1/report.md",
                "citations_path": "deep-research/c-01-r1/citations.json",
                "tool_calls_path": "deep-research/c-01-r1/tool-calls.json",
                "input_sha256": "sha256:" + "1" * 64,
                "output_sha256": "sha256:" + "2" * 64,
                "data_sources": ["web_search"],
                "tool_call_count": 1,
                "citation_count": 1,
                "opened_source_count": 1,
                "status": "completed",
                "limitations": [],
            }

            append_completed_receipt(topic_dir, "topic-1", receipt)
            append_completed_receipt(topic_dir, "topic-1", receipt)
            saved = json.loads((topic_dir / "deep-research-receipts.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["schema_version"], "deep-research-receipts.v1")
            self.assertEqual(saved["topic_id"], "topic-1")
            self.assertEqual(len(saved["runs"]), 1)

    def test_background_polling_persists_each_observed_state(self) -> None:
        class FakeClient:
            def __init__(self) -> None:
                self.responses = [
                    {"id": "resp_1", "status": "in_progress"},
                    {"id": "resp_1", "status": "completed"},
                ]

            def retrieve(self, response_id: str) -> dict[str, object]:
                self.asserted_response_id = response_id
                return self.responses.pop(0)

        observed: list[str] = []
        result = wait_for_terminal_response(
            FakeClient(),
            {"id": "resp_1", "status": "queued"},
            poll_interval=0.001,
            timeout_seconds=1,
            on_update=lambda value: observed.append(str(value["status"])),
        )
        self.assertEqual(result["status"], "completed")
        self.assertEqual(observed, ["queued", "in_progress", "completed"])

    def test_dry_run_needs_no_credential_and_writes_no_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package_root = Path(tmp)
            topic_dir, prompt_path = self.write_minimal_topic(package_root)
            output = io.StringIO()
            with mock.patch.dict(os.environ, {"OPENAI_API_KEY": ""}), contextlib.redirect_stdout(output):
                code = main(
                    [
                        "--package-root", str(package_root),
                        "--topic-id", "topic-1",
                        "--claim-id", "C-01",
                        "--phase", "initial-deep-research",
                        "--round", "1",
                        "--prompt-file", str(prompt_path),
                        "--model", "current-deep-research-model",
                        "--dry-run",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertIn('"credential_read": false', output.getvalue())
            self.assertFalse((topic_dir / "deep-research").exists())

    def test_missing_credential_fails_before_creating_run_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package_root = Path(tmp)
            topic_dir, prompt_path = self.write_minimal_topic(package_root)
            with mock.patch.dict(os.environ, {"OPENAI_API_KEY": ""}), contextlib.redirect_stderr(io.StringIO()):
                code = main(
                    [
                        "--package-root", str(package_root),
                        "--topic-id", "topic-1",
                        "--claim-id", "C-01",
                        "--phase", "initial-deep-research",
                        "--round", "1",
                        "--prompt-file", str(prompt_path),
                        "--model", "current-deep-research-model",
                    ]
                )
            self.assertEqual(code, 2)
            self.assertFalse((topic_dir / "deep-research").exists())


if __name__ == "__main__":
    unittest.main()
