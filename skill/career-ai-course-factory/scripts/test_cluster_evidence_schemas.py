#!/usr/bin/env python3
"""Positive and fault-injection tests for clustered research evidence contracts."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
try:
    from validate_cluster_evidence import canonical_key_digest, component_digest, page_set_digest, validate_classification_overlay, validate_cluster_evidence
except ImportError:  # unittest module mode
    from .validate_cluster_evidence import canonical_key_digest, component_digest, page_set_digest, validate_classification_overlay, validate_cluster_evidence


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "assets" / "schemas"
DIGEST = "sha256:" + "a" * 64


def validator(name: str) -> Draft202012Validator:
    schema = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def assert_valid(test: unittest.TestCase, name: str, document: dict) -> None:
    errors = sorted(validator(name).iter_errors(document), key=lambda error: list(error.path))
    test.assertEqual(errors, [], [error.message for error in errors])


def assert_invalid(test: unittest.TestCase, name: str, document: dict) -> None:
    test.assertTrue(list(validator(name).iter_errors(document)))


def digests() -> dict:
    return {
        "scope_digest": DIGEST,
        "version_digest": DIGEST,
        "environment_digest": DIGEST,
        "region_digest": DIGEST,
        "risk_digest": DIGEST,
    }


def locator(kind: str = "local") -> dict:
    return {"locator_id": "loc-1", "kind": kind, "uri_or_path": "fixtures/example.json", "digest": DIGEST}


def origin(kind: str = "claim-inventory") -> dict:
    return {"origin_kind": kind, "origin_id": "origin-1", "origin_path": "research/claim-inventory.json", "origin_digest": DIGEST}


def canonical_key(statement: str = "bounded claim") -> dict:
    key = {
        "normalized_statement": statement,
        "normalized_scope": "documented scope",
        "normalized_version": "v1",
        "normalized_time_boundary": "current",
        "normalized_vendor": "acme",
        "normalized_environment": "fixture",
        "normalized_region": "global",
        "normalized_risk": "medium", "normalized_claim_type": "mechanism", "normalized_population": "bounded fixture", "normalized_predicate": "supports scoped claim", "normalized_required_dimensions": "terminology-and-system-boundary", "normalized_execution_contract": "openai-deep-research.v1", "normalized_cluster": "K03", "normalized_evidence_class": "SHARED-MECHANISM", "normalized_route": "EXTERNAL-RESEARCH", "normalized_source_family_policy": "primary",
        "component_digests": {},
    }
    for name, field in {"statement": "normalized_statement", "scope": "normalized_scope", "version": "normalized_version", "time_boundary": "normalized_time_boundary", "vendor": "normalized_vendor", "environment": "normalized_environment", "region": "normalized_region", "risk": "normalized_risk", "claim_type": "normalized_claim_type", "population": "normalized_population", "predicate": "normalized_predicate", "required_dimensions": "normalized_required_dimensions", "execution_contract": "normalized_execution_contract", "cluster": "normalized_cluster", "evidence_class": "normalized_evidence_class", "route": "normalized_route", "source_family_policy": "normalized_source_family_policy"}.items():
        key["component_digests"][name] = component_digest(key[field])
    key["key_digest"] = canonical_key_digest(key)
    return key


def invalidation() -> dict:
    return {"status": "current", "triggers": ["scope-change"], "invalidates_node_ids": ["N2-1", "N4-1"]}


def claim_contract_fields() -> dict:
    return {"execution_contract": "openai-deep-research.v1", "required_dimensions": ["terminology-and-system-boundary"], "time_boundary": "current", "vendor_or_tool": "acme"}


class ClusterEvidenceSchemaTests(unittest.TestCase):
    def test_claim_map_accepts_all_nine_classes_and_explicit_routes(self) -> None:
        classes = [
            ("LOCAL-DETERMINISTIC", "LOCAL-VERIFY"),
            ("STABLE-DEFINITION", "EXTERNAL-RESEARCH"),
            ("SHARED-MECHANISM", "EXTERNAL-RESEARCH"),
            ("VENDOR-VERSION", "EXTERNAL-RESEARCH"),
            ("NUMERIC-STATISTICAL", "EXTERNAL-RESEARCH"),
            ("SECURITY-AUTHORITY", "EXTERNAL-RESEARCH"),
            ("FAILURE-OPERATIONS", "EXTERNAL-RESEARCH"),
            ("TEACHING-PROFESSIONAL", "TEACHING-VALIDATION"),
            ("TARGET-EMPIRICAL", "TARGET-EVIDENCE"),
        ]
        claims = []
        for index, (evidence_class, route) in enumerate(classes):
            claim = {
                **claim_contract_fields(),
                "claim_id": f"C-{index + 1:02d}", "statement": f"Bounded claim {index + 1}.", "status": "MAPPED",
                "claim_type": "mechanism", "risk": "medium", "primary_cluster_id": "K03",
                "evidence_class": evidence_class, "route": route,
                "identity_fingerprint": DIGEST, "request_fingerprint": DIGEST, "digests": digests(),
                "canonical_claim_key": canonical_key(),
                "source_locators": [locator("target" if route == "TARGET-EVIDENCE" else "local")],
                "origin": origin(), "cannot_prove": ["Production efficacy is not established."], "invalidation": invalidation(),
            }
            if route == "TARGET-EVIDENCE":
                claim["target_evidence"] = {"required": True, "status": "UNKNOWN", "evidence_refs": [], "cannot_substitute_with": ["fixture", "external-web"]}
            claims.append(claim)
        document = {
            "schema_version": "claim-cluster-map.v1", "map_id": "map-2026-08-20", "generated_at": "2026-08-20T00:00:00Z",
            "inventory_digest": DIGEST, "cluster_registry_version": "clusters.v1", "claims": claims,
        }
        assert_valid(self, "claim-cluster-map.v1.schema.json", document)

    def test_claim_map_rejects_target_without_target_evidence_and_wrong_local_route(self) -> None:
        base = {
            "schema_version": "claim-cluster-map.v1", "map_id": "m", "generated_at": "now", "inventory_digest": DIGEST,
            "cluster_registry_version": "v1", "claims": [{
                **claim_contract_fields(),
                "claim_id": "C-1", "statement": "A target fact", "claim_type": "behavior", "risk": "high", "primary_cluster_id": "K03", "status": "MAPPED",
                "evidence_class": "TARGET-EMPIRICAL", "route": "EXTERNAL-RESEARCH", "identity_fingerprint": DIGEST,
                "request_fingerprint": DIGEST, "digests": digests(), "source_locators": [locator("external")], "origin": origin(),
                "canonical_claim_key": canonical_key(), "cannot_prove": ["Current target state"], "invalidation": invalidation(),
            }],
        }
        assert_invalid(self, "claim-cluster-map.v1.schema.json", base)
        base["claims"][0]["evidence_class"] = "LOCAL-DETERMINISTIC"
        base["claims"][0]["route"] = "EXTERNAL-RESEARCH"
        assert_invalid(self, "claim-cluster-map.v1.schema.json", base)

    def test_unclassified_is_only_a_blocked_route(self) -> None:
        claim = {
            **claim_contract_fields(),
            "claim_id": "C-U", "statement": "unclassified", "claim_type": "unknown", "risk": "unknown", "primary_cluster_id": "K00", "evidence_class": "UNCLASSIFIED", "route": "BLOCKED-UNCLASSIFIED", "status": "BLOCKED", "identity_fingerprint": DIGEST, "request_fingerprint": DIGEST, "canonical_claim_key": canonical_key(), "digests": digests(), "source_locators": [locator()], "origin": origin(), "cannot_prove": ["Classification is not complete."], "invalidation": invalidation(),
        }
        document = {"schema_version": "claim-cluster-map.v1", "map_id": "m", "generated_at": "now", "inventory_digest": DIGEST, "cluster_registry_version": "v1", "claims": [claim]}
        assert_valid(self, "claim-cluster-map.v1.schema.json", document)
        claim["status"] = "MAPPED"
        assert_invalid(self, "claim-cluster-map.v1.schema.json", document)
        claim["status"] = "BLOCKED"
        claim["evidence_class"] = "STABLE-DEFINITION"
        assert_invalid(self, "claim-cluster-map.v1.schema.json", document)

    def test_bundle_is_explicitly_not_a_completed_provider_receipt(self) -> None:
        bundle = {
            "schema_version": "evidence-bundle.v1", "artifact_kind": "evidence-bundle", "bundle_id": "B-1", "bundle_revision": 1,
            "anchor_claim_id": "C-1", "evidence_class": "STABLE-DEFINITION", "route": "EXTERNAL-RESEARCH", "digests": digests(),
            "bundle_digest": DIGEST, "member_claim_ids": ["C-1"], "predicate_ids": ["P-1"],
            "origin_receipts": [{"receipt_id": "R-1", "receipt_schema_version": "deep-research-receipts.v1", "receipt_path": "deep-research-receipts.json", "receipt_digest": DIGEST, "provider": "openai", "surface": "openai-responses-api", "status": "completed"}],
            "source_locators": [locator("external")], "supports_predicates": ["Supports the versioned definition only."],
            "cannot_prove": ["Does not prove this repository's implementation or production behavior."], "invalidation": invalidation(),
            "provider_receipt_status": "referenced-only-not-a-receipt", "receipt_status": "bundle-ready",
        }
        assert_valid(self, "evidence-bundle.v1.schema.json", bundle)
        forged = copy.deepcopy(bundle)
        forged["artifact_kind"] = "deep-research-receipt"
        assert_invalid(self, "evidence-bundle.v1.schema.json", forged)
        forged = copy.deepcopy(bundle)
        forged["provider_receipt_status"] = "completed"
        assert_invalid(self, "evidence-bundle.v1.schema.json", forged)
        forged = copy.deepcopy(bundle)
        forged["invalidation"] = {"status": "superseded", "triggers": ["version-change"], "invalidates_node_ids": []}
        assert_invalid(self, "evidence-bundle.v1.schema.json", forged)

    def test_reuse_decisions_are_three_state_and_unknown_is_fail_closed(self) -> None:
        decision = {
            "schema_version": "claim-evidence-reuse-decisions.v1", "decision_set_id": "d-1", "map_digest": DIGEST,
            "decisions": [{
                "decision_id": "D-1", "claim_id": "C-1", "bundle_id": "B-1", "decision": "DIRECT-REUSE",
                "bundle_revision": 1, "bundle_digest": DIGEST, "member_claim_id": "C-1", "predicate_id": "P-1", "predicate_scope_digest": DIGEST,
                "equivalence": {key: "equal" for key in ["identity", "scope", "version", "environment", "region", "risk", "population", "predicate"]} | {"verdict": "exact"},
                "digests": digests(), "target_evidence": {"required": False, "status": "NOT_RUN", "evidence_refs": []},
                "local_transfer_locator": "research/claim-map.json#C-1", "cannot_prove": ["Target behavior."], "invalidation": invalidation(), "rationale": "All transfer dimensions are exact.",
            }],
        }
        assert_valid(self, "claim-evidence-reuse-decisions.v1.schema.json", decision)
        unknown = copy.deepcopy(decision)
        unknown["decisions"][0]["equivalence"]["scope"] = "unknown"
        unknown["decisions"][0]["equivalence"]["verdict"] = "unknown"
        assert_invalid(self, "claim-evidence-reuse-decisions.v1.schema.json", unknown)
        target = copy.deepcopy(decision)
        target["decisions"][0]["target_evidence"] = {"required": True, "status": "UNKNOWN", "evidence_refs": []}
        assert_invalid(self, "claim-evidence-reuse-decisions.v1.schema.json", target)

    def test_dry_run_ready_requires_zero_unclassified_and_bundle_invalidation_is_explicit(self) -> None:
        manifest = {
            "schema_version": "research-route-dry-run-manifest.v1", "dry_run_id": "dry-1", "generated_at": "now",
            "input_inventory_digests": [DIGEST], "map_digest": DIGEST, "status": "READY", "unclassified_count": 0,
            "counts": {"pages_expected": 103, "pages_with_claim_inventory": 103, "missing_page_count": 0, "unexpected_page_count": 0, "pages_total": 103, "claims_total": 3328, "eligible_external_units_before": 100, "canonical_external_units_after": 70, "local_units": 20, "target_units": 10, "teaching_units": 8, "blocked_units": 0},
            "routes": {"LOCAL-VERIFY": 20, "EXTERNAL-RESEARCH": 70, "TARGET-EVIDENCE": 10, "TEACHING-VALIDATION": 8, "BLOCKED-UNCLASSIFIED": 0},
            "reuse": {"DIRECT-REUSE": 20, "SOURCE-REUSE-DELTA": 10, "NO-REUSE": 5},
            "invalidation": {"current": 90, "superseded": 2, "invalid": 1, "invalidation_count": 3},
        }
        assert_valid(self, "research-route-dry-run-manifest.v1.schema.json", manifest)
        blocked = copy.deepcopy(manifest)
        blocked["unclassified_count"] = 1
        blocked["routes"]["BLOCKED-UNCLASSIFIED"] = 1
        assert_invalid(self, "research-route-dry-run-manifest.v1.schema.json", blocked)
        missing_invalidation = copy.deepcopy(manifest)
        missing_invalidation["invalidation"].pop("invalidation_count")
        assert_invalid(self, "research-route-dry-run-manifest.v1.schema.json", missing_invalidation)

    def test_page_coverage_is_hash_bound_and_shared_by_map_and_manifest(self) -> None:
        coverage = {
            "coverage_source": "catalog-manifest", "catalog_manifest_digest": DIGEST,
            "expected_page_ids": ["TD-F01", "TD-P01"], "covered_page_ids": ["TD-F01", "TD-P01"],
            "missing_page_ids": [], "unexpected_page_ids": [],
        }
        coverage["page_set_digest"] = page_set_digest(coverage)
        cluster_map = {"page_coverage": coverage}
        manifest = {"status": "READY", "page_coverage": copy.deepcopy(coverage), "counts": {
            "pages_expected": 2, "pages_with_claim_inventory": 2, "missing_page_count": 0,
            "unexpected_page_count": 0, "claims_total": 0, "local_units": 0, "target_units": 0, "teaching_units": 0, "blocked_units": 0,
        }, "routes": {"LOCAL-VERIFY": 0, "EXTERNAL-RESEARCH": 0, "TARGET-EVIDENCE": 0, "TEACHING-VALIDATION": 0, "BLOCKED-UNCLASSIFIED": 0}}
        self.assertEqual(validate_cluster_evidence(cluster_map, {}, {"decisions": []}, manifest), [])
        forged = copy.deepcopy(manifest)
        forged["page_coverage"]["expected_page_ids"] = ["TD-F01"]
        self.assertTrue(any("page_coverage" in error for error in validate_cluster_evidence(cluster_map, {}, {"decisions": []}, forged)))

    def test_pending_classification_overlay_can_preserve_k00_blocked_claims(self) -> None:
        overlay = {
            "schema_version": "classification-overlay.v1", "overlay_id": "o-blocked",
            "source_inventory_digests": [DIGEST], "generated_by": "luna", "reviewed_by": "pending-auditor",
            "independent_review": False, "review_status": "pending", "claim_count": 1,
            "claims": [{"claim_id": "C-U", "evidence_class": "UNCLASSIFIED", "risk": "unknown",
                         "primary_cluster_id": "K00", "related_cluster_ids": [], "source_family_policy": "unknown",
                         "classification_reason": "insufficient subject/predicate", "target_evidence_required": False}],
        }
        assert_valid(self, "classification-overlay.v1.schema.json", overlay)

    def test_cross_artifact_validator_rejects_duplicates_page_ids_and_bad_routes(self) -> None:
        claim = {"claim_id": "C-1", "canonical_claim_key": canonical_key()}
        cluster_map = {"claims": [claim, {"claim_id": "C-2", "canonical_claim_key": canonical_key()}]}
        bundle = {"bundle_id": "B-1", "bundle_revision": 1, "bundle_digest": DIGEST, "member_claim_ids": ["C-1"], "predicate_ids": ["P-1"], "digests": digests()}
        reuse = {"decisions": []}
        manifest = {"status": "READY", "unclassified_count": 0, "counts": {"claims_total": 2, "eligible_external_units_before": 1, "canonical_external_units_after": 2, "blocked_units": 0}, "routes": {"LOCAL-VERIFY": 1, "EXTERNAL-RESEARCH": 0, "TARGET-EVIDENCE": 0, "TEACHING-VALIDATION": 0, "BLOCKED-UNCLASSIFIED": 0}, "invalidation": {"invalid": 0}}
        errors = validate_cluster_evidence(cluster_map, bundle, reuse, manifest)
        self.assertTrue(any("duplicate canonical" in error for error in errors))
        self.assertTrue(any("route totals" in error for error in errors))
        self.assertTrue(any("cannot exceed" in error for error in errors))
        page_key = copy.deepcopy(canonical_key())
        page_key["normalized_scope"] = "page-12 only"
        self.assertTrue(any("page identifier" in error for error in validate_cluster_evidence({"claims": [{"claim_id": "C-1", "canonical_claim_key": page_key}]}, bundle, reuse, manifest)))
        tampered = copy.deepcopy(canonical_key())
        tampered["normalized_predicate"] = "different predicate"
        self.assertTrue(any("digest mismatch" in error for error in validate_cluster_evidence({"claims": [{"claim_id": "C-1", "canonical_claim_key": tampered}]}, bundle, reuse, manifest)))
        tampered_component = copy.deepcopy(canonical_key())
        tampered_component["component_digests"]["population"] = DIGEST
        self.assertTrue(any("component digest mismatch (population)" in error for error in validate_cluster_evidence({"claims": [{"claim_id": "C-1", "canonical_claim_key": tampered_component}]}, bundle, reuse, manifest)))
        map_with_overlay = {"claims": [], "classification_overlay_digest": DIGEST}
        manifest_with_other_overlay = {**manifest, "classification_overlay_digest": "sha256:" + "b" * 64}
        self.assertTrue(any("classification overlay digest" in error for error in validate_cluster_evidence(map_with_overlay, bundle, reuse, manifest_with_other_overlay)))

    def test_identical_thirteen_vector_is_valid_only_with_explicit_shared_unit(self) -> None:
        shared = {"claims": [{"claim_id": "C-1", "canonical_claim_key": canonical_key(), "canonical_unit_id": "U-1", "canonical_unit_role": "anchor"}, {"claim_id": "C-2", "canonical_claim_key": canonical_key(), "canonical_unit_id": "U-1", "canonical_unit_role": "member"}]}
        manifest = {"status": "BLOCKED", "unclassified_count": 0, "counts": {"claims_total": 2, "eligible_external_units_before": 2, "canonical_external_units_after": 1, "blocked_units": 0}, "routes": {"LOCAL-VERIFY": 0, "EXTERNAL-RESEARCH": 2, "TARGET-EVIDENCE": 0, "TEACHING-VALIDATION": 0, "BLOCKED-UNCLASSIFIED": 0}, "invalidation": {"invalid": 0}}
        errors = validate_cluster_evidence(shared, {"bundle_id": "B", "anchor_claim_id": "C-1", "bundle_revision": 1, "bundle_digest": DIGEST, "member_claim_ids": ["C-1", "C-2"], "predicate_ids": [], "digests": digests()}, {"decisions": []}, manifest)
        self.assertFalse(any("duplicate canonical" in error for error in errors), errors)

    def test_canonical_unit_requires_one_anchor_and_bundle_same_unit_members(self) -> None:
        claims = [{"claim_id": "C-1", "canonical_claim_key": canonical_key(), "canonical_unit_id": "U-1", "canonical_unit_role": "member"}, {"claim_id": "C-2", "canonical_claim_key": canonical_key(), "canonical_unit_id": "U-1", "canonical_unit_role": "member"}]
        manifest = {"status": "BLOCKED", "unclassified_count": 0, "counts": {"claims_total": 2, "eligible_external_units_before": 2, "canonical_external_units_after": 1, "blocked_units": 0}, "routes": {"LOCAL-VERIFY": 0, "EXTERNAL-RESEARCH": 2, "TARGET-EVIDENCE": 0, "TEACHING-VALIDATION": 0, "BLOCKED-UNCLASSIFIED": 0}, "invalidation": {"invalid": 0}}
        bundle = {"anchor_claim_id": "C-1", "bundle_id": "B", "bundle_revision": 1, "bundle_digest": DIGEST, "member_claim_ids": ["C-1", "C-2"], "predicate_ids": [], "digests": digests()}
        errors = validate_cluster_evidence({"claims": claims}, bundle, {"decisions": []}, manifest)
        self.assertTrue(any("exactly one anchor" in error for error in errors))
        claims[0]["canonical_unit_role"] = "anchor"
        claims[1]["canonical_unit_id"] = "U-2"
        errors = validate_cluster_evidence({"claims": claims}, bundle, {"decisions": []}, manifest)
        self.assertTrue(any("anchor canonical unit" in error for error in errors))
        claims[1].pop("canonical_unit_role")
        errors = validate_cluster_evidence({"claims": claims}, bundle, {"decisions": []}, manifest)
        self.assertTrue(any("missing or invalid member role" in error for error in errors))

    def test_classification_dry_run_without_bundle_is_valid_but_wrong_bundle_anchor_fails(self) -> None:
        claims = [{"claim_id": "C-1", "canonical_claim_key": canonical_key(), "canonical_unit_id": "U-1", "canonical_unit_role": "anchor"}]
        manifest = {"status": "BLOCKED", "unclassified_count": 0, "counts": {"claims_total": 1, "eligible_external_units_before": 1, "canonical_external_units_after": 1, "local_units": 0, "target_units": 0, "teaching_units": 0, "blocked_units": 0}, "routes": {"LOCAL-VERIFY": 0, "EXTERNAL-RESEARCH": 1, "TARGET-EVIDENCE": 0, "TEACHING-VALIDATION": 0, "BLOCKED-UNCLASSIFIED": 0}, "invalidation": {"invalid": 0}}
        self.assertFalse(validate_cluster_evidence({"claims": claims}, {}, {"decisions": []}, manifest))
        wrong_anchor = {"bundle_id": "B", "anchor_claim_id": "C-2", "member_claim_ids": ["C-1"]}
        self.assertTrue(any("anchor" in error for error in validate_cluster_evidence({"claims": claims}, wrong_anchor, {"decisions": []}, manifest)))

    def test_cross_artifact_validator_rejects_stale_bundle_unsupported_predicate_and_bundle_receipt(self) -> None:
        bundle = {"artifact_kind": "evidence-bundle", "bundle_id": "B-1", "bundle_revision": 2, "bundle_digest": DIGEST, "member_claim_ids": ["C-1"], "predicate_ids": ["P-1"], "digests": digests()}
        decision = {"decision_id": "D-1", "claim_id": "C-1", "bundle_id": "B-1", "bundle_revision": 1, "bundle_digest": "sha256:" + "b" * 64, "member_claim_id": "C-2", "predicate_id": "P-2", "predicate_scope_digest": "sha256:" + "b" * 64, "decision": "NO-REUSE", "equivalence": {"identity": "unknown", "scope": "unknown", "version": "unknown", "environment": "unknown", "region": "unknown", "risk": "unknown", "population": "unknown", "predicate": "unknown", "verdict": "unknown"}}
        manifest = {"status": "BLOCKED", "unclassified_count": 0, "counts": {"claims_total": 0, "eligible_external_units_before": 0, "canonical_external_units_after": 0, "blocked_units": 1}, "routes": {"LOCAL-VERIFY": 0, "EXTERNAL-RESEARCH": 0, "TARGET-EVIDENCE": 0, "TEACHING-VALIDATION": 0, "BLOCKED-UNCLASSIFIED": 0}, "invalidation": {"invalid": 0}}
        errors = validate_cluster_evidence({"claims": []}, bundle, {"decisions": [decision]}, manifest)
        self.assertTrue(any("stale bundle" in error for error in errors))
        self.assertTrue(any("disallowed bundle member" in error for error in errors))
        self.assertTrue(any("unsupported predicate" in error for error in errors))
        forged = copy.deepcopy(bundle)
        forged["artifact_kind"] = "deep-research-receipt"
        assert_invalid(self, "evidence-bundle.v1.schema.json", forged)

    def test_classification_overlay_requires_exact_independent_approval(self) -> None:
        structured = {"subject": "retrieval", "predicate": "supports", "object": "bounded claim", "claim_type_family": "mechanism", "scope": "fixture", "version": "v1", "time_boundary": "2026-08-20", "vendor_or_tool": "none", "environment": "offline", "population": "bounded", "region_language": "global-en", "authority_risk": "low", "required_dimensions": ["boundary"], "execution_contract": "openai-deep-research.v1", "local_validation_locators": ["fixtures/x.json"], "target_evidence_required": False}
        field_digests = {field: component_digest(json.dumps(value, sort_keys=True, ensure_ascii=False) if isinstance(value, (list, dict)) else value) for field, value in structured.items()}
        overlay = {"schema_version": "classification-overlay.v1", "overlay_id": "o-1", "source_inventory_digests": [DIGEST], "generated_by": "factory", "reviewed_by": "auditor", "independent_review": True, "review_status": "approved", "claim_count": 1, "claims": [{"claim_id": "C-1", "evidence_class": "STABLE-DEFINITION", "risk": "low", "primary_cluster_id": "K01", "related_cluster_ids": ["K02"], "source_family_policy": "primary", "classification_reason": "definition", "route": "EXTERNAL-RESEARCH", **structured, "field_digests": field_digests}]}
        assert_valid(self, "classification-overlay.v1.schema.json", overlay)
        self.assertEqual(validate_classification_overlay(overlay, [{"claim_id": "C-1"}], [DIGEST]), [])
        self.assertTrue(validate_classification_overlay({**overlay, "generated_by": "same", "reviewed_by": "same"}, [{"claim_id": "C-1"}], [DIGEST]))
        self.assertTrue(validate_classification_overlay({**overlay, "source_inventory_digests": ["sha256:" + "b" * 64]}, [{"claim_id": "C-1"}], [DIGEST]))
        self.assertTrue(validate_classification_overlay({**overlay, "claims": [*overlay["claims"], {**overlay["claims"][0], "claim_id": "C-2"}], "claim_count": 2}, [{"claim_id": "C-1"}], [DIGEST]))
        unknown = {**overlay, "claims": [{**overlay["claims"][0], "evidence_class": "UNCLASSIFIED", "risk": "unknown"}]}
        self.assertTrue(validate_classification_overlay(unknown, [{"claim_id": "C-1"}], [DIGEST]))

    def test_target_pass_fail_requires_real_target_locators_and_exact_reuse_requires_all_equal(self) -> None:
        base = {
            "schema_version": "claim-cluster-map.v1", "map_id": "m", "generated_at": "now", "inventory_digest": DIGEST, "cluster_registry_version": "v1",
            "claims": [{"claim_id": "C-1", "statement": "target", "claim_type": "behavior", "risk": "high", "primary_cluster_id": "K03", "status": "MAPPED", "evidence_class": "TARGET-EMPIRICAL", "route": "TARGET-EVIDENCE", "identity_fingerprint": DIGEST, "request_fingerprint": DIGEST, "canonical_claim_key": canonical_key(), "digests": digests(), "source_locators": [locator("target")], "origin": origin(), "cannot_prove": ["production"], "invalidation": invalidation(), "target_evidence": {"required": True, "status": "PASS", "evidence_refs": [], "cannot_substitute_with": ["fixture"]}}],
        }
        assert_invalid(self, "claim-cluster-map.v1.schema.json", base)
        base["claims"][0]["target_evidence"]["evidence_refs"] = [{"locator_id": "t-1", "kind": "local", "uri_or_path": "fixture.json", "digest": DIGEST}]
        assert_invalid(self, "claim-cluster-map.v1.schema.json", base)

        decision = {"decision_id": "D-1", "claim_id": "C-1", "bundle_id": "B-1", "bundle_revision": 1, "bundle_digest": DIGEST, "member_claim_id": "C-1", "predicate_id": "P-1", "predicate_scope_digest": DIGEST, "decision": "DIRECT-REUSE", "equivalence": {"identity": "equal", "scope": "unknown", "version": "equal", "environment": "equal", "region": "equal", "risk": "equal", "population": "equal", "predicate": "equal", "verdict": "exact"}}
        errors = validate_cluster_evidence({"claims": []}, {"bundle_id": "B-1", "bundle_revision": 1, "bundle_digest": DIGEST, "member_claim_ids": ["C-1"], "predicate_ids": ["P-1"], "digests": digests()}, {"decisions": [decision]}, {"status": "BLOCKED", "unclassified_count": 0, "counts": {"claims_total": 0, "eligible_external_units_before": 0, "canonical_external_units_after": 0, "blocked_units": 0}, "routes": {"LOCAL-VERIFY": 0, "EXTERNAL-RESEARCH": 0, "TARGET-EVIDENCE": 0, "TEACHING-VALIDATION": 0, "BLOCKED-UNCLASSIFIED": 0}, "invalidation": {"invalid": 0}})
        self.assertTrue(any("DIRECT-REUSE is not exact" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
