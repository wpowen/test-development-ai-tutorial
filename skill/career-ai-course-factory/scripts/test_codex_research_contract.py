#!/usr/bin/env python3
"""Offline RED/GREEN tests for the independent Codex research contract."""

from __future__ import annotations

import hashlib
import base64
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from codex_research_contract import compile_codex_trace, validate_codex_topic, validate_trace
from finalize_codex_research import finalize_codex_topic
from validate_career_package import validate_claim_deep_research


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


class CodexResearchContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.package = Path(self.temp.name)
        self.topic = self.package / "research/topics/topic-1"
        self.topic.mkdir(parents=True)
        self.private_key = self.package / "attestation-private.pem"
        self.public_key = self.package / "attestation-public.pem"
        subprocess.run(["openssl", "genrsa", "-out", str(self.private_key), "2048"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["openssl", "rsa", "-in", str(self.private_key), "-pubout", "-out", str(self.public_key)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.previous_attestation_key = os.environ.get("CODEX_RESEARCH_ATTESTATION_PUBLIC_KEY")
        os.environ["CODEX_RESEARCH_ATTESTATION_PUBLIC_KEY"] = str(self.public_key)
        (self.topic / "manuscript.md").write_text("# Manuscript\n\nBounded claim.\n", encoding="utf-8")
        dump(
            self.topic / "claim-inventory.json",
            {
                "schema_version": "claim-inventory.v1",
                "topic_id": "topic-1",
                "execution_contract": "codex-research.v1",
                "root_manifest": {"schema_version": "locator-root-manifest.v1", "package_relative_priority": True, "roots": {"topic": {"kind": "topic", "path": "research/topics/topic-1"}, "package": {"kind": "package", "path": "."}}},
                "extraction": {
                    "author_id": "author",
                    "independent_auditor_id": "auditor",
                    "source_files": ["manuscript.md"],
                    "source_hashes": {
                        "manuscript.md": digest_bytes((self.topic / "manuscript.md").read_bytes())
                    },
                    "locator_ledger": [{"locator": "topic:manuscript.md#md:Manuscript", "canonical_key": "topic:manuscript.md#md:Manuscript", "root_alias": "topic", "resolved_path": "manuscript.md", "sha256": digest_bytes((self.topic / "manuscript.md").read_bytes()), "selector": "md:Manuscript", "selector_kind": "md", "selector_value": "Manuscript", "line_start": None, "line_end": None, "line_count": 3, "claim_ids": ["C-01"]}],
                    "unmapped_propositions": 0,
                },
                "claims": [{
                    "claim_id": "C-01",
                    "statement": "A bounded claim.",
                    "claim_type": "mechanism",
                    "risk": "high",
                    "scope": "versioned environment",
                    "source_locations": ["topic:manuscript.md#md:Manuscript"],
                    "required_dimensions": ["terminology-boundary", "counterevidence"],
                    "proposed_disposition": "SCOPED",
                }],
            },
        )

    def tearDown(self) -> None:
        if self.previous_attestation_key is None:
            os.environ.pop("CODEX_RESEARCH_ATTESTATION_PUBLIC_KEY", None)
        else:
            os.environ["CODEX_RESEARCH_ATTESTATION_PUBLIC_KEY"] = self.previous_attestation_key
        self.temp.cleanup()

    def attest(self, trace: dict[str, object]) -> dict[str, object]:
        payload = json.dumps(trace, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        signature = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", str(self.private_key)],
            input=payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        ).stdout
        trace["runtime_attestation"] = {
            "schema_version": "codex-runtime-attestation.v1",
            "algorithm": "rsa-sha256",
            "key_id": "test-codex-runtime-key",
            "payload_sha256": digest_bytes(payload),
            "signature_base64": base64.b64encode(signature).decode("ascii"),
        }
        return trace

    def make_trace(self, run_id: str, phase: str, round_number: int) -> Path:
        run_dir = self.topic / "codex-research" / run_id
        run_dir.mkdir(parents=True)
        role = "researcher" if phase == "initial-research" else "counterevidence"
        agents = []
        events = []
        citations = []
        for index in range(2):
            agent_id = f"{run_id}-agent-{index + 1}"
            output = run_dir / f"{agent_id}.md"
            output.write_text(f"Finding from {agent_id}.\n", encoding="utf-8")
            agents.append({
                "runtime_observed_agent_id": agent_id,
                "role": role,
                "provider": "codex",
                "runtime": "codex-native-subagent",
                "session_id": f"session-{agent_id}",
                "parent_invocation_id": f"orchestrator-{run_id}",
                "independence_group": f"group-{agent_id}",
                "input_context_sha256": digest_bytes(f"context:{agent_id}".encode()),
                "prompt_sha256": digest_bytes(f"prompt:{agent_id}".encode()),
                "input_artifacts": [{
                    "path": "claim-inventory.json",
                    "sha256": digest_bytes((self.topic / "claim-inventory.json").read_bytes()),
                }],
                "output_path": str(output.relative_to(self.topic)),
                "output_sha256": digest_bytes(output.read_bytes()),
            })
            event_id = f"open-{agent_id}"
            url = f"https://example.test/{run_id}/{index + 1}"
            events.append({
                "event_id": event_id,
                "event_type": "source_open",
                "runtime_observed_agent_id": agent_id,
                "timestamp": f"2026-08-18T00:0{index}:00Z",
                "url": url,
                "result": "opened",
                "content_sha256": "sha256:" + str(index + 6) * 64,
            })
            citations.append({
                "citation_id": f"cite-{agent_id}",
                "runtime_observed_agent_id": agent_id,
                "url": url,
                "opening_event_id": event_id,
            })
        integrator_output = run_dir / "integrated-report.md"
        integrator_output.write_text("Integrated report.\n", encoding="utf-8")
        agents.append({
            "runtime_observed_agent_id": f"{run_id}-integrator",
            "role": "integrator",
            "provider": "codex",
            "runtime": "codex-orchestrator",
            "session_id": f"session-{run_id}-integrator",
            "parent_invocation_id": f"orchestrator-{run_id}",
            "independence_group": f"integration-{run_id}",
            "input_context_sha256": "sha256:" + "9" * 64,
            "prompt_sha256": "sha256:" + "8" * 64,
            "input_artifacts": [],
            "output_path": str(integrator_output.relative_to(self.topic)),
            "output_sha256": digest_bytes(integrator_output.read_bytes()),
        })
        trace = {
            "schema_version": "codex-runtime-trace.v1",
            "surface": "codex-research",
            "run_id": run_id,
            "topic_id": "topic-1",
            "claim_ids": ["C-01"],
            "phase": phase,
            "round": round_number,
            "status": "completed",
            "started_at": "2026-08-18T00:00:00Z",
            "completed_at": "2026-08-18T00:10:00Z",
            "orchestrator": {
                "runtime_observed_agent_id": f"orchestrator-{run_id}",
                "runtime": "codex",
                "session_id": f"orchestrator-session-{run_id}",
                "trace_id": f"trace-{run_id}",
            },
            "agents": agents,
            "events": events,
            "citations": citations,
            "limitations": [],
        }
        path = self.package / f"{run_id}-trace.json"
        dump(path, self.attest(trace))
        return path

    def test_rejects_agent_without_runtime_observed_identity(self) -> None:
        path = self.make_trace("r1", "initial-research", 1)
        trace = json.loads(path.read_text())
        del trace["agents"][0]["runtime_observed_agent_id"]
        trace.pop("runtime_attestation", None)
        self.attest(trace)
        with self.assertRaisesRegex(ValueError, "agent identity"):
            validate_trace(trace, self.topic)

    def test_rejects_shared_context_for_independent_agents(self) -> None:
        path = self.make_trace("r1", "initial-research", 1)
        trace = json.loads(path.read_text())
        trace["agents"][1]["input_context_sha256"] = trace["agents"][0]["input_context_sha256"]
        trace.pop("runtime_attestation", None)
        self.attest(trace)
        with self.assertRaisesRegex(ValueError, "shared context"):
            validate_trace(trace, self.topic)

    def test_integrator_does_not_count_as_independent_evidence(self) -> None:
        receipt = compile_codex_trace(
            package_root=self.package,
            topic_id="topic-1",
            claim_id="C-01",
            phase="initial-research",
            round_number=1,
            trace_file=self.make_trace("r1", "initial-research", 1),
            replace=False,
        )
        self.assertEqual(receipt["independent_agent_count"], 2)
        self.assertEqual(len(receipt["agent_invocation_ids"]), 2)

    def test_citation_without_matching_open_event_is_rejected(self) -> None:
        path = self.make_trace("r1", "initial-research", 1)
        trace = json.loads(path.read_text())
        trace["events"] = []
        trace.pop("runtime_attestation", None)
        self.attest(trace)
        with self.assertRaisesRegex(ValueError, "citation.*open"):
            validate_trace(trace, self.topic)

    def test_counterevidence_cannot_read_prior_synthesis(self) -> None:
        path = self.make_trace("r2", "counterevidence", 2)
        trace = json.loads(path.read_text())
        trace["events"].append({
            "event_id": "read-prior",
            "event_type": "artifact_read",
            "runtime_observed_agent_id": "r2-agent-1",
            "timestamp": "2026-08-18T00:02:00Z",
            "path": "evidence-synthesis.md",
            "sha256": "sha256:" + "7" * 64,
        })
        trace.pop("runtime_attestation", None)
        self.attest(trace)
        with self.assertRaisesRegex(ValueError, "counterevidence.*prior synthesis"):
            validate_trace(trace, self.topic)

    def test_counterevidence_cannot_read_any_prior_run_artifact(self) -> None:
        path = self.make_trace("r2", "counterevidence", 2)
        trace = json.loads(path.read_text())
        trace["events"].append({
            "event_id": "read-prior-run",
            "event_type": "artifact_read",
            "runtime_observed_agent_id": "r2-agent-1",
            "timestamp": "2026-08-18T00:02:00Z",
            "path": "codex-research/r1/raw-trace.json",
            "sha256": "sha256:" + "7" * 64,
        })
        trace.pop("runtime_attestation", None)
        self.attest(trace)
        with self.assertRaisesRegex(ValueError, "counterevidence.*prior research run"):
            validate_trace(trace, self.topic)

    def test_unattested_runtime_trace_cannot_compile_a_pass_receipt(self) -> None:
        path = self.make_trace("r1", "initial-research", 1)
        trace = json.loads(path.read_text())
        trace.pop("runtime_attestation")
        dump(path, trace)
        with self.assertRaisesRegex(ValueError, "runtime attestation"):
            compile_codex_trace(
                package_root=self.package,
                topic_id="topic-1",
                claim_id="C-01",
                phase="initial-research",
                round_number=1,
                trace_file=path,
                replace=False,
            )

    def test_topic_requires_fresh_counterevidence_agents_and_context(self) -> None:
        compile_codex_trace(
            package_root=self.package, topic_id="topic-1", claim_id="C-01",
            phase="initial-research", round_number=1,
            trace_file=self.make_trace("r1", "initial-research", 1), replace=False,
        )
        counter_path = self.make_trace("r2", "counterevidence", 2)
        counter = json.loads(counter_path.read_text())
        counter["agents"][0]["session_id"] = "session-r1-agent-1"
        counter["agents"][0]["input_context_sha256"] = digest_bytes(b"context:r1-agent-1")
        counter.pop("runtime_attestation", None)
        self.attest(counter)
        dump(counter_path, counter)
        compile_codex_trace(
            package_root=self.package, topic_id="topic-1", claim_id="C-01",
            phase="counterevidence", round_number=2,
            trace_file=counter_path, replace=False,
        )
        errors = validate_codex_topic(self.topic, require_saturation=False)
        self.assertTrue(any("fresh" in error or "reuses" in error for error in errors))

    def test_independent_adjudicator_compiles_codex_saturation(self) -> None:
        for run_id, phase, round_number in (
            ("r1", "initial-research", 1),
            ("r2", "counterevidence", 2),
            ("r3", "gap-fill", 3),
        ):
            compile_codex_trace(
                package_root=self.package, topic_id="topic-1", claim_id="C-01",
                phase=phase, round_number=round_number,
                trace_file=self.make_trace(run_id, phase, round_number), replace=False,
            )
        adjudications = self.package / "adjudications.json"
        dump(adjudications, {
            "schema_version": "codex-research-adjudications.v1",
            "topic_id": "topic-1",
            "auditor_id": "fresh-final-auditor",
            "claims": [{
                "claim_id": "C-01",
                "run_ids": ["r1", "r2", "r3"],
                "coverage_dimensions": [
                    {"dimension": "terminology-boundary", "status": "covered", "evidence_or_reason": "r1"},
                    {"dimension": "counterevidence", "status": "covered", "evidence_or_reason": "r2"},
                ],
                "contradiction_status": "resolved",
                "contradictions": [{
                    "issue": "Definitions vary by version.",
                    "run_ids": ["r1", "r2"],
                    "disposition": "scoped",
                    "rationale": "Use the declared version boundary.",
                }],
                "two_consecutive_rounds_without_material_change": True,
                "conclusive_primary_authority_exception": False,
                "round_assessments": [
                    {"run_id": "r1", "material_change": True, "assessment": "Initial evidence."},
                    {"run_id": "r2", "material_change": False, "assessment": "Counterevidence narrowed scope."},
                    {"run_id": "r3", "material_change": False, "assessment": "Gap fill confirmed scope."},
                ],
                "final_disposition": "SCOPED",
                "verdict": "SATURATED",
                "rationale": "Fresh independent rounds closed the bounded claim.",
            }],
        })
        result = finalize_codex_topic(
            package_root=self.package, topic_id="topic-1",
            adjudications_file=adjudications, replace=False,
        )
        self.assertEqual(result["overall_verdict"], "PASS-CODEX-RESEARCH")
        self.assertEqual(result["deep_research_status"], "BLOCKED-DEEP-RESEARCH")
        self.assertEqual(validate_codex_topic(self.topic), [])
        package_errors: list[str] = []
        validate_claim_deep_research(self.topic, "topic-1", package_errors)
        self.assertEqual(package_errors, [])


if __name__ == "__main__":
    unittest.main()
