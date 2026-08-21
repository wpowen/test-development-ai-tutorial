#!/usr/bin/env python3
"""Offline tests for claim inventory and independent saturation workflow tooling."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from finalize_claim_research import finalize_topic_research, validate_adjudication_row
from prepare_claim_inventory import prepare_inventory, validate_inventory_locator_contract, verify_locator_ledger
from scan_locator_migration import scan


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


class ClaimResearchWorkflowTests(unittest.TestCase):
    def test_prepare_inventory_hashes_frozen_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            topic = package / "research/topics/topic-1"
            topic.mkdir(parents=True)
            (topic / "manuscript.md").write_text("# Manuscript\n\nBounded proposition.\n", encoding="utf-8")
            claims_file = package / "claims.json"
            dump(
                claims_file,
                {
                    "schema_version": "claim-list.v1", "topic_id": "topic-1",
                    "reviewed_by": "auditor", "unmapped_propositions": 0,
                    "claims": [{
                        "claim_id": "C-01",
                        "statement": "A bounded proposition.",
                        "claim_type": "mechanism",
                        "risk": "high",
                        "scope": "versioned environment",
                        "source_locations": ["topic:manuscript.md#md:Manuscript"],
                        "required_dimensions": ["terminology-boundary", "counterevidence"],
                        "proposed_disposition": "SCOPED",
                    }],
                },
            )

            result = prepare_inventory(
                package_root=package,
                topic_id="topic-1",
                claims_file=claims_file,
                source_files=["manuscript.md"],
                author_id="author",
                independent_auditor_id="auditor",
                replace=False,
            )
            self.assertEqual(result["extraction"]["unmapped_propositions"], 0)
            self.assertEqual(result["execution_contract"], "openai-deep-research.v1")
            self.assertRegex(result["extraction"]["source_hashes"]["manuscript.md"], r"^sha256:[0-9a-f]{64}$")
            self.assertTrue((topic / "claim-inventory.json").is_file())

    def test_prepare_inventory_rejects_duplicate_claims_and_self_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            topic = package / "research/topics/topic-1"
            topic.mkdir(parents=True)
            (topic / "manuscript.md").write_text("content", encoding="utf-8")
            claims_file = package / "claims.json"
            claim = {
                "claim_id": "C-01", "statement": "x", "claim_type": "definition", "risk": "low",
                "scope": "test", "source_locations": ["topic:manuscript.md"],
                "required_dimensions": ["terminology-boundary"], "proposed_disposition": "SCOPED",
            }
            dump(claims_file, {"schema_version":"claim-list.v1", "topic_id":"topic-1", "reviewed_by":"auditor", "unmapped_propositions":0, "claims":[claim, claim]})
            with self.assertRaisesRegex(ValueError, "duplicate claim_id"):
                prepare_inventory(
                    package_root=package, topic_id="topic-1", claims_file=claims_file,
                    source_files=["manuscript.md"], author_id="author",
                    independent_auditor_id="auditor", replace=False,
                )
            dump(claims_file, {"schema_version":"claim-list.v1", "topic_id":"topic-1", "reviewed_by":"author", "unmapped_propositions":0, "claims":[claim]})
            with self.assertRaisesRegex(ValueError, "independent"):
                prepare_inventory(
                    package_root=package, topic_id="topic-1", claims_file=claims_file,
                    source_files=["manuscript.md"], author_id="author",
                    independent_auditor_id="author", replace=False,
                )

    def _claim_doc(self, *, topic_id: str = "topic-1", locator: str = "topic:manuscript.md:L1-L1") -> dict:
        value = {
            "schema_version": "claim-list.v1", "topic_id": topic_id,
            "reviewed_by": "auditor", "unmapped_propositions": 0,
            "claims": [{
                "claim_id": "C-01", "statement": "x", "claim_type": "definition", "risk": "low",
                "scope": "test", "source_locations": [locator],
                "required_dimensions": ["terminology-boundary"], "proposed_disposition": "SCOPED",
            }],
        }
        if "#opaque:contract" in locator:
            value["selector_audits"] = {"contract": {"reviewed_by": "auditor", "rationale": "fixture selector audit"}}
        return value

    def _prepare_one(self, package: Path, locator: str, *, roots: dict[str, Path] | None = None) -> dict:
        topic = package / "research/topics/topic-1"
        topic.mkdir(parents=True, exist_ok=True)
        (topic / "manuscript.md").write_text("one\ntwo\nthree\n", encoding="utf-8")
        claims_file = package / "claims.json"
        dump(claims_file, self._claim_doc(locator=locator))
        return prepare_inventory(
            package_root=package, topic_id="topic-1", claims_file=claims_file,
            source_files=["manuscript.md"], author_id="author",
            independent_auditor_id="auditor", replace=False, locator_roots=roots,
        )

    def test_locator_ledger_freezes_lines_selector_and_explicit_package_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            result = self._prepare_one(package, "package:research/topics/topic-1/manuscript.md:L1-L2#opaque:contract")
            entry = result["extraction"]["locator_ledger"][0]
            self.assertEqual(entry["root_alias"], "package")
            self.assertEqual(entry["resolved_path"], "research/topics/topic-1/manuscript.md")
            self.assertEqual(entry["line_start"], 1)
            self.assertEqual(entry["line_end"], 2)
            self.assertEqual(entry["selector"], "opaque:contract")
            self.assertEqual(entry["selector_kind"], "opaque")
            self.assertRegex(entry["sha256"], r"^sha256:[0-9a-f]{64}$")

    def test_locator_rejects_external_without_allowlisted_alias_and_unknown_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            outside = package / "external"
            outside.mkdir()
            (outside / "source.md").write_text("external\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown locator root alias"):
                self._prepare_one(package, "ext:source.md:L1-L1")
            # The alias is explicit and therefore accepted; there is no implicit full-repo search.
            result = self._prepare_one(package, "ext:source.md:L1-L1", roots={"ext": outside})
            self.assertEqual(result["extraction"]["locator_ledger"][0]["root_alias"], "ext")

    def test_locator_rejects_missing_ambiguous_symlink_and_line_bounds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            outside = package / "external"
            outside.mkdir()
            (outside / "same.md").write_text("external\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "explicit root alias"):
                self._prepare_one(package, "manuscript.md", roots={"ext": package / "research/topics/topic-1"})
            with self.assertRaisesRegex(ValueError, "line range exceeds"):
                self._prepare_one(package, "topic:manuscript.md:L1-L4")
            with self.assertRaisesRegex(ValueError, "missing or empty"):
                self._prepare_one(package, "topic:missing.md")
            link = outside / "escape.md"
            link.symlink_to(package / "outside.md")
            (package / "outside.md").write_text("outside\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "escapes allowlisted root"):
                self._prepare_one(package, "ext:escape.md", roots={"ext": outside})

    def test_locator_rejects_parent_absolute_and_malformed_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            for locator, message in (("topic:../manuscript.md", "dot"), ("/tmp/manuscript.md", "relative"), ("manuscript.md:L2", "alias")):
                with self.assertRaisesRegex(ValueError, message):
                    self._prepare_one(package, locator)

    def test_locator_hash_freshness_is_rejected_after_source_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            result = self._prepare_one(package, "topic:manuscript.md:L1-L1")
            source = package / "research/topics/topic-1/manuscript.md"
            source.write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "stale"):
                verify_locator_ledger(
                    package_root=package, topic_id="topic-1",
                    ledger=result["extraction"]["locator_ledger"],
                    inventory=result,
                )

    def test_verify_locator_ledger_validates_the_supplied_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            result = self._prepare_one(package, "topic:manuscript.md:L1-L1")
            tampered = json.loads(json.dumps(result["extraction"]["locator_ledger"]))
            tampered[0]["sha256"] = "sha256:" + "f" * 64
            with self.assertRaisesRegex(ValueError, "stale"):
                verify_locator_ledger(
                    package_root=package, topic_id="topic-1", ledger=tampered, inventory=result
                )

    def test_historical_claim_list_scan_is_migration_needed_and_never_promotes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            topic = package / "research/topics/topic-legacy"
            topic.mkdir(parents=True)
            dump(topic / "claim-list.v1.json", {"schema_version": "claim-list.v1", "claims": [{"source_locations": ["manuscript.md:L1-L1", "../../../missing.md:L1-L1"]}]})
            report = scan(package)
            self.assertEqual(report["status"], "BLOCKED-MIGRATION-NEEDED")
            self.assertEqual(report["topics_scanned"], 1)
            self.assertGreaterEqual(report["parse_fail"], 2)
            self.assertGreaterEqual(report["missing"], 1)

    def test_public_contract_rejects_source_hash_key_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            inventory = self._prepare_one(package, "topic:manuscript.md:L1-L1")
            inventory["extraction"]["source_hashes"]["extra.md"] = inventory["extraction"]["source_hashes"]["manuscript.md"]
            errors = validate_inventory_locator_contract(
                inventory, package_root=package, topic_dir=package / "research/topics/topic-1"
            )
            self.assertTrue(any("exact matching keys" in error for error in errors))

    def test_selector_heading_must_be_unique(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            topic = package / "research/topics/topic-1"
            topic.mkdir(parents=True)
            (topic / "manuscript.md").write_text("# Duplicate\n\n# Duplicate\n", encoding="utf-8")
            claims_file = package / "claims.json"
            dump(claims_file, self._claim_doc(locator="topic:manuscript.md#md:Duplicate"))
            with self.assertRaisesRegex(ValueError, "not unique"):
                prepare_inventory(
                    package_root=package, topic_id="topic-1", claims_file=claims_file,
                    source_files=["manuscript.md"], author_id="author",
                    independent_auditor_id="auditor", replace=False,
                )

    def test_migration_scan_checks_explicit_missing_and_external_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            topic = package / "research/topics/topic-explicit"
            topic.mkdir(parents=True)
            dump(topic / "claim-list.v1.json", {"schema_version": "claim-list.v1", "claims": [{"source_locations": ["topic:missing.md:L1-L1", "factory:artifact.md:L1-L1"]}]})
            report = scan(package)
            self.assertEqual(report["parse_fail"], 0)
            self.assertEqual(report["missing"], 1)
            self.assertEqual(report["external_binding_needed"], 1)
            self.assertEqual(report["status"], "BLOCKED-MIGRATION-NEEDED")

    def test_finalize_builds_saturation_and_contradiction_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            topic = package / "research/topics/topic-1"
            topic.mkdir(parents=True)
            dump(
                topic / "claim-inventory.json",
                {
                    "schema_version": "claim-inventory.v1", "topic_id": "topic-1",
                    "extraction": {"author_id": "author", "independent_auditor_id": "auditor"},
                    "claims": [
                        {"claim_id": "C-01", "required_dimensions": ["terminology-boundary", "counterevidence"]}
                    ],
                },
            )
            dump(
                topic / "deep-research-receipts.json",
                {
                    "schema_version": "deep-research-receipts.v1", "topic_id": "topic-1",
                    "runs": [
                        {"run_id": "r1", "claim_ids": ["C-01"], "round": 1, "phase": "initial-deep-research", "status": "completed"},
                        {"run_id": "r2", "claim_ids": ["C-01"], "round": 2, "phase": "counterevidence", "status": "completed"},
                        {"run_id": "r3", "claim_ids": ["C-01"], "round": 3, "phase": "gap-fill", "status": "completed"},
                    ],
                },
            )
            decisions = package / "adjudications.json"
            dump(
                decisions,
                {
                    "schema_version": "claim-research-adjudications.v1", "topic_id": "topic-1",
                    "auditor_id": "auditor", "claims": [
                        {
                            "claim_id": "C-01", "run_ids": ["r1", "r2", "r3"],
                            "coverage_dimensions": [
                                {"dimension": "terminology-boundary", "status": "covered", "evidence_or_reason": "r1"},
                                {"dimension": "counterevidence", "status": "covered", "evidence_or_reason": "r2"},
                            ],
                            "contradiction_status": "resolved",
                            "contradictions": [
                                {"issue": "Definitions differed by version.", "run_ids": ["r1", "r2"], "disposition": "scoped", "rationale": "Use the current version only."}
                            ],
                            "two_consecutive_rounds_without_material_change": True,
                            "conclusive_primary_authority_exception": False,
                            "round_assessments": [
                                {"run_id": "r1", "material_change": True, "assessment": "Initial scoped finding."},
                                {"run_id": "r2", "material_change": False, "assessment": "Counterevidence narrowed wording only."},
                                {"run_id": "r3", "material_change": False, "assessment": "Gap fill confirmed the narrowed scope."},
                            ],
                            "final_disposition": "SCOPED", "verdict": "SATURATED",
                            "rationale": "Three rounds closed every required dimension without widening scope.",
                        }
                    ],
                },
            )

            saturation = finalize_topic_research(
                package_root=package, topic_id="topic-1", adjudications_file=decisions, replace=False
            )
            self.assertEqual(saturation["overall_verdict"], "PASS")
            self.assertEqual(saturation["independent_auditor_id"], "auditor")
            matrix = (topic / "contradiction-matrix.md").read_text(encoding="utf-8")
            self.assertIn("Definitions differed by version", matrix)

    def test_finalize_rejects_missing_phase_and_false_saturation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            topic = package / "research/topics/topic-1"
            topic.mkdir(parents=True)
            dump(
                topic / "claim-inventory.json",
                {
                    "schema_version": "claim-inventory.v1", "topic_id": "topic-1",
                    "extraction": {"author_id": "author", "independent_auditor_id": "auditor"},
                    "claims": [{"claim_id": "C-01", "required_dimensions": ["counterevidence"]}],
                },
            )
            dump(
                topic / "deep-research-receipts.json",
                {
                    "schema_version": "deep-research-receipts.v1", "topic_id": "topic-1",
                    "runs": [
                        {"run_id": "r1", "claim_ids": ["C-01"], "round": 1, "phase": "initial-deep-research", "status": "completed"},
                        {"run_id": "r2", "claim_ids": ["C-01"], "round": 2, "phase": "initial-deep-research", "status": "completed"},
                    ],
                },
            )
            decisions = package / "adjudications.json"
            dump(
                decisions,
                {
                    "schema_version": "claim-research-adjudications.v1", "topic_id": "topic-1",
                    "auditor_id": "auditor", "claims": [
                        {
                            "claim_id": "C-01", "run_ids": ["r1", "r2"],
                            "coverage_dimensions": [{"dimension": "counterevidence", "status": "covered", "evidence_or_reason": "r1"}],
                            "contradiction_status": "none-found", "contradictions": [],
                            "two_consecutive_rounds_without_material_change": False,
                            "conclusive_primary_authority_exception": False,
                            "round_assessments": [
                                {"run_id": "r1", "material_change": True, "assessment": "Initial finding only."},
                                {"run_id": "r2", "material_change": False, "assessment": "A repeated initial request is not counterevidence."},
                            ],
                            "final_disposition": "SUPPORTED", "verdict": "SATURATED", "rationale": "not enough",
                        }
                    ],
                },
            )
            with self.assertRaisesRegex(ValueError, "counterevidence"):
                finalize_topic_research(
                    package_root=package, topic_id="topic-1", adjudications_file=decisions, replace=False
                )
            self.assertFalse((topic / "research-saturation.json").exists())

    def test_stable_rounds_must_be_unique_and_consecutive(self) -> None:
        row = {
            "claim_id": "C-01", "run_ids": ["r1", "r3"],
            "coverage_dimensions": [{"dimension":"counterevidence", "status":"covered", "evidence_or_reason":"r3"}],
            "contradiction_status": "none-found", "contradictions": [],
            "two_consecutive_rounds_without_material_change": True,
            "conclusive_primary_authority_exception": False,
            "round_assessments": [
                {"run_id":"r1", "material_change":False, "assessment":"No material change."},
                {"run_id":"r3", "material_change":False, "assessment":"No material change."},
            ],
            "final_disposition":"SCOPED", "verdict":"SATURATED", "rationale":"Bounded result.",
        }
        runs = {
            "r1":{"run_id":"r1", "claim_ids":["C-01"], "round":1, "phase":"initial-deep-research", "status":"completed"},
            "r3":{"run_id":"r3", "claim_ids":["C-01"], "round":3, "phase":"counterevidence", "status":"completed"},
        }
        with self.assertRaisesRegex(ValueError, "consecutive"):
            validate_adjudication_row(row, required_dimensions={"counterevidence"}, valid_runs=runs)


if __name__ == "__main__":
    unittest.main()
