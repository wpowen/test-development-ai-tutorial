#!/usr/bin/env python3
"""Cross-artifact, fail-closed checks for clustered evidence contracts.

JSON Schema validates individual documents; this module validates identity,
reuse, route arithmetic, and bundle provenance across documents.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any


PAGE_ID = re.compile(r"(?:^|[\s/#:_-])(?:page[_-]?id|page[-_]\d+)(?:$|[\s/#:_-])", re.I)

CANONICAL_FIELDS = ("normalized_statement", "normalized_scope", "normalized_version", "normalized_time_boundary", "normalized_vendor", "normalized_environment", "normalized_region", "normalized_risk", "normalized_claim_type", "normalized_population", "normalized_predicate", "normalized_required_dimensions", "normalized_execution_contract", "normalized_cluster", "normalized_evidence_class", "normalized_route", "normalized_source_family_policy")


def component_digest(value: Any) -> str:
    normalized = re.sub(r"\s+", " ", str(value if value is not None else "").strip().lower())
    return "sha256:" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def canonical_key_digest(key: dict[str, Any]) -> str:
    payload = "\0".join(str(key.get(field, "")) for field in CANONICAL_FIELDS)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def page_set_digest(coverage: dict[str, Any]) -> str:
    payload = {
        "expected": coverage.get("expected_page_ids", []),
        "covered": coverage.get("covered_page_ids", []),
        "missing": coverage.get("missing_page_ids", []),
        "unexpected": coverage.get("unexpected_page_ids", []),
    }
    return "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def validate_page_coverage(cluster_map: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    """Ensure the exact catalog/page-set binding is identical across artifacts."""
    errors: list[str] = []
    map_coverage = cluster_map.get("page_coverage")
    manifest_coverage = manifest.get("page_coverage")
    if map_coverage is None and manifest_coverage is None:
        if manifest.get("status") == "READY":
            errors.append("READY research route must include page_coverage")
        return errors
    if not isinstance(map_coverage, dict) or not isinstance(manifest_coverage, dict):
        errors.append("page_coverage must be present as an object on both map and manifest")
        return errors
    if map_coverage != manifest_coverage:
        errors.append("page_coverage must be identical on map and manifest")
    expected = list(map_coverage.get("expected_page_ids", []))
    covered = list(map_coverage.get("covered_page_ids", []))
    missing = list(map_coverage.get("missing_page_ids", []))
    unexpected = list(map_coverage.get("unexpected_page_ids", []))
    if expected != sorted(set(expected)) or covered != sorted(set(covered)) or missing != sorted(set(missing)) or unexpected != sorted(set(unexpected)):
        errors.append("page_coverage page IDs must be sorted and unique")
    if map_coverage.get("page_set_digest") != page_set_digest(map_coverage):
        errors.append("page_coverage page_set_digest is stale")
    if set(expected) != set(covered) | set(missing) or set(covered) & set(missing):
        errors.append("page_coverage expected/covered/missing sets do not reconcile")
    if set(covered) & set(unexpected) or set(expected) & set(unexpected):
        errors.append("page_coverage unexpected IDs overlap expected or covered IDs")
    counts = manifest.get("counts", {})
    for field, value in (("pages_expected", len(expected)), ("pages_with_claim_inventory", len(covered)), ("missing_page_count", len(missing)), ("unexpected_page_count", len(unexpected))):
        if field in counts and counts.get(field) != value:
            errors.append(f"page coverage {field} does not match page_coverage")
    if map_coverage.get("coverage_source") == "catalog-manifest" and not map_coverage.get("catalog_manifest_digest"):
        errors.append("catalog-manifest page coverage requires catalog_manifest_digest")
    if manifest.get("status") == "READY" and (map_coverage.get("coverage_source") != "catalog-manifest" or missing or unexpected):
        errors.append("READY research route requires exact catalog-manifest page coverage")
    return errors


def validate_classification_overlay(overlay: dict[str, Any], source_claims: list[dict[str, Any]], source_inventory_digests: list[str]) -> list[str]:
    """Validate overlay approval and exact source inventory coverage."""
    errors: list[str] = []
    source_ids = [str(item.get("claim_id", "")) for item in source_claims]
    overlay_claims = overlay.get("claims", [])
    overlay_ids = [str(item.get("claim_id", "")) for item in overlay_claims]
    if overlay.get("source_inventory_digests") != source_inventory_digests:
        errors.append("classification overlay source inventory digest is stale or incomplete")
    if len(source_ids) != len(set(source_ids)):
        errors.append("source inventory has duplicate claim IDs")
    if len(overlay_ids) != len(set(overlay_ids)):
        errors.append("classification overlay has duplicate claim IDs")
    if set(overlay_ids) != set(source_ids):
        errors.append("classification overlay claim IDs must exactly match source inventory")
    if overlay.get("claim_count") != len(overlay_claims) or overlay.get("claim_count") != len(source_ids):
        errors.append("classification overlay claim_count does not match exact coverage")
    if overlay.get("review_status") == "approved":
        if overlay.get("independent_review") is not True:
            errors.append("approved classification overlay requires independent_review=true")
        if not overlay.get("generated_by") or not overlay.get("reviewed_by") or overlay.get("generated_by") == overlay.get("reviewed_by"):
            errors.append("approved classification overlay requires distinct generator and reviewer")
        if any(item.get("evidence_class") == "UNCLASSIFIED" or item.get("risk") == "unknown" for item in overlay_claims):
            errors.append("approved classification overlay cannot contain UNCLASSIFIED or unknown risk")
        structured = ("subject", "predicate", "object", "claim_type_family", "scope", "version", "time_boundary", "vendor_or_tool", "environment", "population", "region_language", "authority_risk", "required_dimensions", "execution_contract", "local_validation_locators", "target_evidence_required")
        for item in overlay_claims:
            for field in structured:
                value = item.get(field)
                if value is None or (isinstance(value, str) and value.strip().lower() in {"", "unknown", "not-specified", "not_specified"}):
                    errors.append(f"approved overlay has unknown required field {field}: {item.get('claim_id')}")
                expected = component_digest(json.dumps(value, sort_keys=True, ensure_ascii=False) if isinstance(value, (list, dict)) else value)
                if item.get("field_digests", {}).get(field) != expected:
                    errors.append(f"approved overlay field digest mismatch ({field}): {item.get('claim_id')}")
            target = item.get("target_evidence_required") is True
            if (item.get("evidence_class") == "TARGET-EMPIRICAL") != target or (target and item.get("route") != "TARGET-EVIDENCE"):
                errors.append(f"target evidence/class/route mismatch: {item.get('claim_id')}")
    for item in overlay_claims:
        if item.get("primary_cluster_id") in set(item.get("related_cluster_ids", [])):
            errors.append(f"related clusters repeat primary cluster: {item.get('claim_id')}")
    return errors


def validate_cluster_evidence(cluster_map: dict[str, Any], bundle: dict[str, Any], reuse: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_page_coverage(cluster_map, manifest))
    map_overlay = cluster_map.get("classification_overlay_digest")
    manifest_overlay = manifest.get("classification_overlay_digest")
    if bool(map_overlay) != bool(manifest_overlay) or (map_overlay and map_overlay != manifest_overlay):
        errors.append("classification overlay digest must be present and identical on map and manifest")
    claims = cluster_map.get("claims", [])
    keys: dict[str, str] = {}
    for claim in claims:
        if claim.get("primary_cluster_id") == "K00" and not (claim.get("evidence_class") == "UNCLASSIFIED" and claim.get("route") == "BLOCKED-UNCLASSIFIED" and claim.get("status") == "BLOCKED"):
            errors.append(f"K00 is reserved for blocked UNCLASSIFIED claims: {claim.get('claim_id')}")
        key = claim.get("canonical_claim_key", {})
        digest = key.get("key_digest")
        if digest != canonical_key_digest(key):
            errors.append(f"canonical key digest mismatch: {claim.get('claim_id')}")
        expected_components = dict(zip(("statement", "scope", "version", "time_boundary", "vendor", "environment", "region", "risk", "claim_type", "population", "predicate", "required_dimensions", "execution_contract", "cluster", "evidence_class", "route", "source_family_policy"), (key.get(field) for field in CANONICAL_FIELDS)))
        for name, value in expected_components.items():
            if key.get("component_digests", {}).get(name) != component_digest(value):
                errors.append(f"canonical component digest mismatch ({name}): {claim.get('claim_id')}")
        if digest in keys:
            previous = keys[digest]
            same_unit = claim.get("canonical_unit_id") and claim.get("canonical_unit_id") == previous.get("canonical_unit_id")
            if not same_unit:
                errors.append(f"duplicate canonical_claim_key without shared unit: {digest}: {previous.get('claim_id')} and {claim.get('claim_id')}")
        elif digest:
            keys[digest] = claim
        for field in ("normalized_statement", "normalized_scope", "normalized_version", "normalized_environment", "normalized_region", "normalized_risk"):
            if PAGE_ID.search(str(key.get(field, ""))):
                errors.append(f"canonical claim key contains page identifier in {field}: {claim.get('claim_id')}")
        if claim.get("evidence_class") == "TARGET-EMPIRICAL":
            evidence = claim.get("target_evidence", {})
            if evidence.get("status") in {"PASS", "FAIL"} and not evidence.get("evidence_refs"):
                errors.append(f"target {evidence.get('status')} requires evidence locators: {claim.get('claim_id')}")
            if any(ref.get("kind") != "target" for ref in evidence.get("evidence_refs", [])):
                errors.append(f"target evidence has non-target locator: {claim.get('claim_id')}")

    units: dict[str, list[dict[str, Any]]] = {}
    for claim in claims:
        unit_id = claim.get("canonical_unit_id")
        if unit_id:
            units.setdefault(str(unit_id), []).append(claim)
    for unit_id, members in units.items():
        anchors = [claim for claim in members if claim.get("canonical_unit_role") == "anchor"]
        if len(anchors) != 1:
            errors.append(f"canonical unit {unit_id} must have exactly one anchor")
        if any(claim.get("canonical_unit_role") not in {"anchor", "member"} for claim in members):
            errors.append(f"canonical unit {unit_id} has missing or invalid member role")
    bundle_present = bool(bundle.get("bundle_id") and bundle.get("anchor_claim_id") and bundle.get("member_claim_ids"))
    if units and bundle_present:
        anchor_ids = {str(claim.get("claim_id")): unit_id for unit_id, members in units.items() for claim in members if claim.get("canonical_unit_role") == "anchor"}
        bundle_anchor = str(bundle.get("anchor_claim_id", ""))
        if bundle_anchor not in anchor_ids:
            errors.append("bundle.anchor_claim_id must identify a canonical unit anchor")
        else:
            unit_id = anchor_ids[bundle_anchor]
            unit_claim_ids = {str(claim.get("claim_id")) for claim in units[unit_id]}
            bundle_members = set(map(str, bundle.get("member_claim_ids", [])))
            if not bundle_members or not bundle_members.issubset(unit_claim_ids):
                errors.append("bundle members must belong to the anchor canonical unit")

    bundle_id = bundle.get("bundle_id")
    bundle_members = set(bundle.get("member_claim_ids", []))
    predicate_ids = set(bundle.get("predicate_ids", []))
    for decision in reuse.get("decisions", []):
        equivalence = decision.get("equivalence", {})
        dimensions = [equivalence.get(name) for name in ("identity", "scope", "version", "environment", "region", "risk", "population", "predicate")]
        verdict = equivalence.get("verdict")
        kind = decision.get("decision")
        if kind == "DIRECT-REUSE" and (verdict != "exact" or any(value != "equal" for value in dimensions)):
            errors.append(f"DIRECT-REUSE is not exact across all equivalence dimensions: {decision.get('decision_id')}")
        if kind == "SOURCE-REUSE-DELTA" and (verdict != "delta-required" or all(value == "equal" for value in dimensions)):
            errors.append(f"SOURCE-REUSE-DELTA lacks an actual delta: {decision.get('decision_id')}")
        if kind == "NO-REUSE" and verdict not in {"incompatible", "unknown"}:
            errors.append(f"NO-REUSE must be incompatible or unknown: {decision.get('decision_id')}")
        if verdict == "unknown" and kind != "NO-REUSE":
            errors.append(f"unknown equivalence cannot be reused: {decision.get('decision_id')}")
        if decision.get("bundle_id") != bundle_id:
            errors.append(f"reuse decision references wrong bundle: {decision.get('decision_id')}")
        if decision.get("bundle_revision") != bundle.get("bundle_revision") or decision.get("bundle_digest") != bundle.get("bundle_digest"):
            errors.append(f"reuse decision references stale bundle revision/digest: {decision.get('decision_id')}")
        if decision.get("member_claim_id") not in bundle_members:
            errors.append(f"reuse decision references disallowed bundle member: {decision.get('decision_id')}")
        if decision.get("predicate_id") not in predicate_ids:
            errors.append(f"reuse decision references unsupported predicate: {decision.get('decision_id')}")
        if decision.get("predicate_scope_digest") != bundle.get("digests", {}).get("scope_digest"):
            errors.append(f"reuse decision predicate scope is not bundle-bound: {decision.get('decision_id')}")

    counts = manifest.get("counts", {})
    routes = manifest.get("routes", {})
    if sum(routes.get(route, 0) for route in ("LOCAL-VERIFY", "EXTERNAL-RESEARCH", "TARGET-EVIDENCE", "TEACHING-VALIDATION", "BLOCKED-UNCLASSIFIED")) != counts.get("claims_total"):
        errors.append("route totals must equal counts.claims_total")
    for unit, route in (("local_units", "LOCAL-VERIFY"), ("target_units", "TARGET-EVIDENCE"), ("teaching_units", "TEACHING-VALIDATION"), ("blocked_units", "BLOCKED-UNCLASSIFIED")):
        if counts.get(unit) != routes.get(route):
            errors.append(f"{unit} must equal {route} route count")
    if counts.get("canonical_external_units_after", 0) > counts.get("eligible_external_units_before", 0):
        errors.append("canonical external units cannot exceed eligible external baseline")
    pages_expected = counts.get("pages_expected")
    pages_covered = counts.get("pages_with_claim_inventory")
    missing_pages = counts.get("missing_page_count")
    if pages_expected is not None and pages_covered is not None and missing_pages is not None and pages_expected != pages_covered + missing_pages:
        errors.append("page coverage counts must reconcile")
    if manifest.get("status") == "READY" and pages_expected is not None and pages_covered is not None and pages_expected != pages_covered:
        errors.append("READY dry run requires every expected page to have claim inventory")
    no_reuse = manifest.get("reuse", {}).get("NO-REUSE", 0)
    audited = manifest.get("reuse", {}).get("audited_decision_count")
    if no_reuse > counts.get("claims_total", 0) - counts.get("blocked_units", 0):
        errors.append("NO-REUSE cannot count blocked claims")
    if audited is not None and no_reuse > audited:
        errors.append("NO-REUSE cannot exceed audited decision count")
    if manifest.get("status") == "READY" and (manifest.get("unclassified_count", 0) or counts.get("blocked_units", 0) or routes.get("BLOCKED-UNCLASSIFIED", 0) or manifest.get("invalidation", {}).get("invalid", 0)):
        errors.append("READY dry run cannot contain blocked, unclassified, or invalid units")
    return errors
