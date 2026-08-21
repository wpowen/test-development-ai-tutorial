#!/usr/bin/env python3
"""Validate canonical-14 applicability migration sidecars fail-closed."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from migrate_claim_dimensions import (
    CANONICAL_DIMENSIONS,
    CANONICAL_SET,
    _coverage_map,
    _registry_entries,
    registry_approval_errors,
    _legacy_dimensions,
    _source_alias_registry,
    digest_file,
    identity_fingerprint,
    load_json,
)


def validate_dimension_migration(
    sidecar_path: Path,
    source_path: Path,
    *,
    alias_registry_path: Path | None = None,
    require_ready: bool = False,
) -> list[str]:
    errors: list[str] = []

    def _resolve_pointer(document: Any, pointer: str) -> Any:
        if pointer == "":
            return document
        if not pointer.startswith("/"):
            raise ValueError("JSON pointer must start with /")
        current = document
        for raw_part in pointer[1:].split("/"):
            part = raw_part.replace("~1", "/").replace("~0", "~")
            if isinstance(current, list):
                if not part.isdigit() or int(part) >= len(current):
                    raise ValueError("JSON pointer array index is invalid")
                current = current[int(part)]
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise ValueError("JSON pointer target does not exist")
        return current

    source_digest_for_anchors = digest_file(source_path)

    def _validate_reason(reason: Any, label: str) -> None:
        if not isinstance(reason, dict) or not isinstance(reason.get("text"), str) or not reason["text"].strip():
            errors.append(f"{label} needs structured reason text")
            return
        anchors = reason.get("source_anchors")
        if not isinstance(anchors, list) or not anchors:
            errors.append(f"{label} needs source anchors")
            return
        for anchor in anchors:
            if not isinstance(anchor, dict) or not str(anchor.get("locator", "")).strip() or not isinstance(anchor.get("sha256"), str) or not anchor["sha256"].startswith("sha256:"):
                errors.append(f"{label} has invalid source anchor")
                continue
            locator = str(anchor["locator"])
            if not locator.startswith("source:#"):
                errors.append(f"{label} source anchor must use source:# JSON pointer")
                continue
            if anchor["sha256"] != source_digest_for_anchors:
                errors.append(f"{label} source anchor digest mismatch")
            try:
                _resolve_pointer(source, locator[len("source:#"):])
            except ValueError as exc:
                errors.append(f"{label} source anchor cannot be resolved: {exc}")
    try:
        sidecar = load_json(sidecar_path)
    except Exception as exc:  # pragma: no cover - CLI boundary
        return [f"sidecar cannot be loaded: {exc}"]
    try:
        source = load_json(source_path)
    except Exception as exc:  # pragma: no cover - CLI boundary
        return [f"source inventory cannot be loaded: {exc}"]

    if sidecar.get("schema_version") != "claim-dimension-applicability.v1":
        errors.append("unsupported sidecar schema_version")
    if not str(sidecar.get("migration_id", "")).strip():
        errors.append("migration_id is required")
    generated_by = str(sidecar.get("generated_by", "")).strip()
    reviewed_by = str(sidecar.get("reviewed_by", "")).strip()
    review_status = sidecar.get("review_status")
    if not generated_by:
        errors.append("generated_by is required")
    if review_status not in {"pending", "approved", "rejected"}:
        errors.append("review_status must be pending, approved, or rejected")
    if review_status == "approved":
        if not reviewed_by:
            errors.append("approved sidecar needs reviewed_by")
        if reviewed_by == generated_by:
            errors.append("reviewer must be distinct from generator")
        if sidecar.get("independent_review") is not True:
            errors.append("approved sidecar needs independent_review=true")
    elif sidecar.get("independent_review") not in {None, False}:
        errors.append("independent_review can only be true on an approved sidecar")
    if require_ready and review_status != "approved":
        errors.append("sidecar is not approved")

    source_meta = sidecar.get("source_inventory")
    if not isinstance(source_meta, dict):
        errors.append("source_inventory metadata is required")
        source_meta = {}
    source_digest = digest_file(source_path)
    if source_meta.get("digest") != source_digest:
        errors.append("source inventory digest mismatch; sidecar is stale")
    if source_meta.get("schema_version") != source.get("schema_version"):
        errors.append("source inventory schema_version mismatch")
    if source_meta.get("topic_id") != str(source.get("topic_id", "unknown")):
        errors.append("source inventory topic_id mismatch")

    source_claims = source.get("claims")
    sidecar_claims = sidecar.get("claims")
    if not isinstance(source_claims, list) or not isinstance(sidecar_claims, list):
        errors.append("source and sidecar claims must be arrays")
        return errors
    source_map: dict[str, dict[str, Any]] = {}
    for claim in source_claims:
        if isinstance(claim, dict) and str(claim.get("claim_id", "")).strip():
            claim_id = str(claim["claim_id"])
            if claim_id in source_map:
                errors.append(f"source has duplicate claim_id: {claim_id}")
            source_map[claim_id] = claim
    side_map: dict[str, dict[str, Any]] = {}
    for claim in sidecar_claims:
        if not isinstance(claim, dict):
            errors.append("sidecar claims must be objects")
            continue
        claim_id = str(claim.get("claim_id", "")).strip()
        if not claim_id or claim_id in side_map:
            errors.append(f"sidecar has blank or duplicate claim_id: {claim_id}")
            continue
        side_map[claim_id] = claim
    if set(source_map) != set(side_map):
        errors.append(f"claim identity set mismatch: missing={sorted(set(source_map)-set(side_map))} extra={sorted(set(side_map)-set(source_map))}")
    if source_meta.get("claim_count") != len(source_claims):
        errors.append("source claim_count does not match source")
    if len(sidecar_claims) != len(source_claims):
        errors.append("sidecar claim count does not match source")

    registry_meta = sidecar.get("alias_registry")
    mapping_registry: dict[str, dict[str, Any]] = {}
    if not isinstance(registry_meta, dict):
        errors.append("alias_registry metadata is required")
    elif alias_registry_path is not None:
        if registry_meta.get("digest") != digest_file(alias_registry_path):
            errors.append("alias registry digest mismatch")
        try:
            registry_doc = load_json(alias_registry_path)
            mapping_registry = _registry_entries(registry_doc)
            approval_errors = registry_approval_errors(registry_doc, alias_registry_path)
            if any(entry.get("mapping_status") == "approved" for entry in mapping_registry.values()):
                errors.extend(approval_errors)
                if approval_errors:
                    mapping_registry = {label: {**entry, "mapping_status": "ambiguous"} for label, entry in mapping_registry.items()}
            for field in ("registry_id", "input_digest", "output_digest", "review_status", "generated_by", "reviewed_by", "independent_review", "approved_at", "audit_artifact"):
                if registry_meta.get(field) != registry_doc.get(field):
                    errors.append(f"sidecar alias_registry.{field} does not match registry")
        except Exception as exc:
            errors.append(f"alias registry invalid: {exc}")
    else:
        try:
            mapping_registry = _source_alias_registry(source)
        except Exception as exc:
            errors.append(f"source alias registry invalid: {exc}")

    for claim_id, source_claim in source_map.items():
        row = side_map.get(claim_id)
        if row is None:
            continue
        expected_fp = identity_fingerprint(source_claim)
        if row.get("identity_fingerprint") != expected_fp:
            errors.append(f"{claim_id} identity_fingerprint mismatch")
        legacy = row.get("legacy_dimensions")
        if not isinstance(legacy, list) or len(set(legacy)) != len(legacy) or any(not isinstance(x, str) or not x.strip() for x in legacy):
            errors.append(f"{claim_id} legacy_dimensions invalid")
        try:
            expected_legacy = _legacy_dimensions(source_claim, claim_id)
            if legacy != expected_legacy:
                errors.append(f"{claim_id} legacy_dimensions do not match source")
            expected_mapped: set[str] = set()
            expected_unmapped: list[str] = []
            for label in expected_legacy:
                if label in CANONICAL_SET:
                    expected_mapped.add(label)
                else:
                    entry = mapping_registry.get(label)
                    if entry and entry.get("mapping_status") == "approved" and entry.get("canonical_dimensions"):
                        expected_mapped.update(str(item) for item in entry["canonical_dimensions"])
                    else:
                        expected_unmapped.append(label)
            if row.get("mapped_dimensions") != sorted(expected_mapped):
                errors.append(f"{claim_id} mapped_dimensions do not match explicit registry")
            if row.get("unmapped_legacy_dimensions") != expected_unmapped:
                errors.append(f"{claim_id} unmapped_legacy_dimensions do not match explicit registry")
        except ValueError as exc:
            errors.append(str(exc))
        legacy_coverage = row.get("legacy_research_coverage")
        if not isinstance(legacy_coverage, list) or [item.get("dimension") for item in legacy_coverage if isinstance(item, dict)] != legacy:
            errors.append(f"{claim_id} legacy_research_coverage must preserve legacy order and labels")
        explicit_legacy = _coverage_map(source_claim, claim_id)
        for item in legacy_coverage if isinstance(legacy_coverage, list) else []:
            if not isinstance(item, dict) or item.get("status") not in {"covered", "applicable", "not-applicable", "not-recorded"}:
                errors.append(f"{claim_id} legacy research coverage status is invalid")
            elif isinstance(item, dict):
                dimension = str(item.get("dimension", ""))
                expected_status = explicit_legacy.get(dimension, ("not-recorded", ""))[0]
                if item.get("status") != expected_status:
                    errors.append(f"{claim_id} legacy research coverage status changed for {dimension}")
                _validate_reason(item.get("reason"), f"{claim_id} legacy research coverage")
        coverage = row.get("dimension_coverage")
        if not isinstance(coverage, list) or len(coverage) != 14:
            errors.append(f"{claim_id} must contain exactly 14 dimension rows")
            coverage = []
        dimension_ids: list[str] = []
        for item in coverage:
            if not isinstance(item, dict):
                errors.append(f"{claim_id} dimension row must be object")
                continue
            dimension = item.get("dimension")
            dimension_ids.append(str(dimension))
            if dimension not in CANONICAL_SET:
                errors.append(f"{claim_id} has non-canonical dimension: {dimension}")
            if item.get("status") not in {"pending", "applicable", "not-applicable"}:
                errors.append(f"{claim_id} {dimension} status must be pending, applicable, or not-applicable")
            reason = item.get("reason")
            _validate_reason(reason, f"{claim_id} {dimension}")
            if review_status == "approved" and item.get("status") == "pending":
                errors.append(f"{claim_id} {dimension} retains pending applicability on approved sidecar")
        if len(set(dimension_ids)) != 14 or set(dimension_ids) != CANONICAL_SET:
            errors.append(f"{claim_id} dimension rows must be the canonical 14 exactly once")
        for field in ("mapped_dimensions", "unmapped_legacy_dimensions"):
            value = row.get(field)
            if not isinstance(value, list) or len(set(value)) != len(value):
                errors.append(f"{claim_id} {field} must be a unique array")
        unmapped = row.get("unmapped_legacy_dimensions", [])
        if unmapped and row.get("migration_status") != "BLOCKED-UNMAPPED-LEGACY":
            errors.append(f"{claim_id} with unmapped legacy labels must be blocked")
        if not unmapped and row.get("migration_status") == "BLOCKED-UNMAPPED-LEGACY":
            errors.append(f"{claim_id} is blocked without unmapped legacy labels")
        if row.get("migration_status") not in {"PENDING", "BLOCKED-UNMAPPED-LEGACY", "READY"}:
            errors.append(f"{claim_id} migration_status is invalid")
        if review_status == "approved" and (unmapped or row.get("migration_status") != "READY"):
            errors.append(f"approved sidecar contains non-ready claim {claim_id}")

    counts = sidecar.get("counts")
    if not isinstance(counts, dict):
        errors.append("counts object is required")
    else:
        actual = {
            "claims": len(sidecar_claims),
            "ready": sum(row.get("migration_status") == "READY" for row in sidecar_claims if isinstance(row, dict)),
            "pending": sum(row.get("migration_status") == "PENDING" for row in sidecar_claims if isinstance(row, dict)),
            "blocked_unmapped_legacy": sum(row.get("migration_status") == "BLOCKED-UNMAPPED-LEGACY" for row in sidecar_claims if isinstance(row, dict)),
            "unmapped_legacy_dimensions": sum(len(row.get("unmapped_legacy_dimensions", [])) for row in sidecar_claims if isinstance(row, dict) and isinstance(row.get("unmapped_legacy_dimensions", []), list)),
        }
        for key, value in actual.items():
            if counts.get(key) != value:
                errors.append(f"counts.{key} mismatch: expected {value}, got {counts.get(key)}")
    if review_status == "approved" and any("unmapped" in error or "pending" in error.lower() for error in errors):
        errors.append("approved sidecar has unresolved migration findings")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sidecar", required=True, type=Path)
    parser.add_argument("--source-inventory", required=True, type=Path)
    parser.add_argument("--alias-registry", type=Path)
    parser.add_argument("--require-ready", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors = validate_dimension_migration(args.sidecar, args.source_inventory, alias_registry_path=args.alias_registry, require_ready=args.require_ready)
    if errors:
        for error in errors:
            print(f"BLOCKED-DIMENSION-MIGRATION: {error}", file=sys.stderr)
        return 2
    print("PASS dimension-migration sidecar is internally consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
