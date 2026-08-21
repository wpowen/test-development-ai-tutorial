#!/usr/bin/env python3
"""Fault-injection tests for canonical dimension migration."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from migrate_claim_dimensions import CANONICAL_DIMENSIONS, migrate
from validate_dimension_migration import validate_dimension_migration


def source_doc(*, legacy: str = "legacy-known") -> dict:
    return {
        "schema_version": "claim-list.v1",
        "topic_id": "TD-X",
        "claims": [{
            "claim_id": "TD-X-CLAIM-001",
            "statement": "A bounded claim about a local fixture.",
            "scope": "fixture only",
            "claim_type": "design",
            "risk": "medium",
            "source_locations": ["brief.md:L1"],
            "required_dimensions": [legacy, "terminology-and-system-boundary"],
            "proposed_disposition": "SCOPED",
        }],
    }


def registry_doc() -> dict:
    return {
        "schema_version": "dimension-alias-registry.v1",
        "registry_id": "test-registry",
        "entries": [{
            "legacy_dimension": "legacy-known",
            "canonical_dimensions": ["current-ai-model-application-behavior"],
            "mapping_status": "approved",
            "reason": "An explicit reviewed one-to-one legacy mapping for this fixture.",
        }],
    }


class DimensionMigrationTests(unittest.TestCase):
    def _files(self, root: Path, *, legacy: str = "legacy-known") -> tuple[Path, Path, Path]:
        source = root / "claim-list.json"
        registry = root / "aliases.json"
        sidecar = root / "sidecar.json"
        source.write_text(json.dumps(source_doc(legacy=legacy), ensure_ascii=False), encoding="utf-8")
        audit = root / "alias-audit.json"
        audit_doc = {"registry_id": "test-registry", "reviewed_by": "independent-auditor", "independent_review": True, "input_digest": "sha256:" + "1" * 64, "output_digest": "sha256:" + "2" * 64}
        audit.write_text(json.dumps(audit_doc), encoding="utf-8")
        doc = registry_doc()
        doc.update({"input_digest": audit_doc["input_digest"], "output_digest": audit_doc["output_digest"], "generated_by": "luna", "reviewed_by": "independent-auditor", "independent_review": True, "approved_at": "2026-08-20T00:00:00Z", "review_status": "approved", "audit_artifact": {"path": audit.name, "sha256": "sha256:" + __import__('hashlib').sha256(audit.read_bytes()).hexdigest()}})
        registry.write_text(json.dumps(doc), encoding="utf-8")
        return source, registry, sidecar

    def test_draft_is_exactly_fourteen_dimensions_and_pending(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, registry, sidecar = self._files(Path(directory))
            result = migrate(source, sidecar, alias_registry_path=registry, generated_by="luna")
            self.assertEqual(result["review_status"], "pending")
            self.assertEqual(len(result["claims"][0]["dimension_coverage"]), 14)
            self.assertEqual({row["dimension"] for row in result["claims"][0]["dimension_coverage"]}, set(CANONICAL_DIMENSIONS))
            self.assertEqual(result["claims"][0]["unmapped_legacy_dimensions"], [])
            self.assertEqual(validate_dimension_migration(sidecar, source, alias_registry_path=registry), [])

    def test_unknown_legacy_label_is_preserved_and_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, registry, sidecar = self._files(Path(directory), legacy="old-1432-label")
            result = migrate(source, sidecar, alias_registry_path=registry, generated_by="luna")
            row = result["claims"][0]
            self.assertEqual(row["unmapped_legacy_dimensions"], ["old-1432-label"])
            self.assertEqual(row["migration_status"], "BLOCKED-UNMAPPED-LEGACY")
            self.assertEqual(validate_dimension_migration(sidecar, source, alias_registry_path=registry), [])
            sidecar_doc = json.loads(sidecar.read_text(encoding="utf-8"))
            sidecar_doc["review_status"] = "approved"
            sidecar_doc["reviewed_by"] = "independent-reviewer"
            sidecar_doc["independent_review"] = True
            sidecar.write_text(json.dumps(sidecar_doc), encoding="utf-8")
            errors = validate_dimension_migration(sidecar, source, alias_registry_path=registry, require_ready=True)
            self.assertTrue(any("non-ready claim" in error or "unmapped" in error for error in errors))

    def test_stale_source_digest_and_identity_tamper_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, registry, sidecar = self._files(Path(directory))
            migrate(source, sidecar, alias_registry_path=registry, generated_by="luna")
            original = json.loads(source.read_text(encoding="utf-8"))
            original["claims"][0]["statement"] = "changed after migration"
            source.write_text(json.dumps(original), encoding="utf-8")
            errors = validate_dimension_migration(sidecar, source, alias_registry_path=registry)
            self.assertTrue(any("digest mismatch" in error for error in errors))

    def test_self_approval_and_duplicate_dimension_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, registry, sidecar = self._files(Path(directory))
            migrate(source, sidecar, alias_registry_path=registry, generated_by="same-person")
            doc = json.loads(sidecar.read_text(encoding="utf-8"))
            row = doc["claims"][0]
            # Simulate a reviewed, fully resolved sidecar, then inject two faults.
            for item in row["dimension_coverage"]:
                item["status"] = "applicable"
                item["reason"] = {"text": f"{row['claim_id']} independently reviewed applicability for {item['dimension']}.", "source_anchors": [{"locator": row['claim_id'], "sha256": "sha256:" + "3" * 64}]}
            row["migration_status"] = "READY"
            doc["review_status"] = "approved"
            doc["reviewed_by"] = "same-person"
            doc["independent_review"] = True
            doc["counts"] = {"claims": 1, "ready": 1, "pending": 0, "blocked_unmapped_legacy": 0, "unmapped_legacy_dimensions": 0}
            row["dimension_coverage"][1]["dimension"] = row["dimension_coverage"][0]["dimension"]
            sidecar.write_text(json.dumps(doc), encoding="utf-8")
            errors = validate_dimension_migration(sidecar, source, alias_registry_path=registry, require_ready=True)
            self.assertTrue(any("distinct" in error for error in errors))
            self.assertTrue(any("canonical 14" in error for error in errors))

    def test_forged_mapping_is_rejected_even_when_shape_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, registry, sidecar = self._files(Path(directory), legacy="old-1432-label")
            migrate(source, sidecar, alias_registry_path=registry, generated_by="luna")
            doc = json.loads(sidecar.read_text(encoding="utf-8"))
            row = doc["claims"][0]
            row["unmapped_legacy_dimensions"] = []
            row["mapped_dimensions"] = ["current-ai-model-application-behavior"]
            row["migration_status"] = "PENDING"
            doc["counts"]["blocked_unmapped_legacy"] = 0
            doc["counts"]["unmapped_legacy_dimensions"] = 0
            sidecar.write_text(json.dumps(doc), encoding="utf-8")
            errors = validate_dimension_migration(sidecar, source, alias_registry_path=registry)
            self.assertTrue(any("do not match explicit registry" in error for error in errors))

    def test_td_x101_legacy_ids_and_covered_status_are_not_reinterpreted(self) -> None:
        source = Path(__file__).resolve().parents[2] / "test-development-ai-v2/research/topics/TD-X101/claim-list.v1.json"
        if not source.is_file():
            self.skipTest("TD-X101 fixture is not present")
        with tempfile.TemporaryDirectory() as directory:
            sidecar = Path(directory) / "sidecar.json"
            migrate(source, sidecar, alias_registry_path=None, generated_by="luna")
            doc = json.loads(sidecar.read_text(encoding="utf-8"))
            row = doc["claims"][0]
            self.assertEqual(row["legacy_research_coverage"][0]["status"], "covered")
            self.assertEqual(row["dimension_coverage"][0]["status"], "pending")
            self.assertTrue(all(item["status"] == "pending" for item in row["dimension_coverage"]))
            self.assertEqual(validate_dimension_migration(sidecar, source), [])

    def test_alias_self_review_is_not_trusted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, registry, sidecar = self._files(Path(directory))
            registry_doc_value = json.loads(registry.read_text(encoding="utf-8"))
            registry_doc_value["reviewed_by"] = registry_doc_value["generated_by"]
            registry.write_text(json.dumps(registry_doc_value), encoding="utf-8")
            result = migrate(source, sidecar, alias_registry_path=registry, generated_by="luna")
            self.assertEqual(result["claims"][0]["unmapped_legacy_dimensions"], ["legacy-known"])
            errors = validate_dimension_migration(sidecar, source, alias_registry_path=registry)
            self.assertTrue(any("distinct" in error for error in errors))

    def test_fake_unstructured_reason_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, registry, sidecar = self._files(Path(directory))
            migrate(source, sidecar, alias_registry_path=registry, generated_by="luna")
            doc = json.loads(sidecar.read_text(encoding="utf-8"))
            doc["claims"][0]["dimension_coverage"][0]["reason"] = "looks applicable"
            sidecar.write_text(json.dumps(doc), encoding="utf-8")
            errors = validate_dimension_migration(sidecar, source, alias_registry_path=registry)
            self.assertTrue(any("structured reason" in error for error in errors))

    def test_required_dimension_without_coverage_is_not_recorded_not_covered(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, registry, sidecar = self._files(Path(directory))
            result = migrate(source, sidecar, alias_registry_path=registry, generated_by="luna")
            statuses = {item["dimension"]: item["status"] for item in result["claims"][0]["legacy_research_coverage"]}
            self.assertEqual(statuses["legacy-known"], "not-recorded")
            self.assertEqual(statuses["terminology-and-system-boundary"], "not-recorded")
            self.assertEqual(validate_dimension_migration(sidecar, source, alias_registry_path=registry), [])

    def test_applicable_status_is_preserved_and_anchor_digest_is_verified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, registry, sidecar = self._files(root)
            document = json.loads(source.read_text(encoding="utf-8"))
            document["claims"][0]["dimension_coverage"] = [{
                "dimension": "legacy-known", "status": "applicable", "reason": "Applicability only; no research coverage claim."
            }]
            source.write_text(json.dumps(document), encoding="utf-8")
            result = migrate(source, sidecar, alias_registry_path=registry, generated_by="luna")
            self.assertEqual(result["claims"][0]["legacy_research_coverage"][0]["status"], "applicable")
            tampered = json.loads(sidecar.read_text(encoding="utf-8"))
            tampered["claims"][0]["dimension_coverage"][0]["reason"]["source_anchors"][0]["sha256"] = "sha256:" + "f" * 64
            sidecar.write_text(json.dumps(tampered), encoding="utf-8")
            errors = validate_dimension_migration(sidecar, source, alias_registry_path=registry)
            self.assertTrue(any("anchor digest mismatch" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
