#!/usr/bin/env python3
"""Create a fail-closed canonical-14-dimension applicability sidecar.

This command never edits the source inventory.  It copies stable claim identity,
records every legacy label, and only applies exact mappings from an explicit
alias registry.  Missing/ambiguous labels remain visible and block approval.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CANONICAL_DIMENSIONS = (
    "terminology-and-system-boundary",
    "conventional-or-non-ai-baseline",
    "professional-actor-workflow-artifact-decision-failure-cost",
    "current-ai-model-application-behavior",
    "architecture-interfaces-state-data-versioning",
    "metrics-statistics-population-slices-uncertainty-threshold-method",
    "implementation-repository-commands-configuration-reproducibility",
    "failure-incidents-issues-counterexamples-disconfirming-evidence",
    "security-privacy-permissions-abuse-compliance-human-authority",
    "performance-latency-capacity-reliability-cost",
    "operations-observability-rollback-waiver-feedback",
    "tool-vendor-alternatives-and-non-ai-alternatives",
    "regional-language-organization-environment-variation",
    "learner-prerequisite-action-diagnosis-reuse-transfer",
)
CANONICAL_SET = set(CANONICAL_DIMENSIONS)


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def identity_fingerprint(claim: dict[str, Any]) -> str:
    parts = (str(claim.get("claim_id", "")), str(claim.get("statement", "")), str(claim.get("scope", "")))
    return digest_bytes("\0".join(parts).encode("utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _clean_labels(value: Any, field: str, claim_id: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"claim {claim_id} {field} must be a string array")
    return list(dict.fromkeys(item.strip() for item in value))


def _coverage_map(claim: dict[str, Any], claim_id: str) -> dict[str, tuple[str, str]]:
    raw = claim.get("dimension_coverage")
    if raw is None:
        return {}
    if isinstance(raw, dict):
        rows = [{"dimension": key, **(value if isinstance(value, dict) else {})} for key, value in raw.items()]
    elif isinstance(raw, list):
        rows = raw
    else:
        raise ValueError(f"claim {claim_id} dimension_coverage must be an object or array")
    result: dict[str, tuple[str, str]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f"claim {claim_id} dimension_coverage rows must be objects")
        dimension = str(row.get("dimension", "")).strip()
        status = str(row.get("status", "")).strip()
        reason = str(row.get("reason", row.get("evidence_or_reason", ""))).strip()
        if not dimension or dimension in result:
            raise ValueError(f"claim {claim_id} dimension_coverage has blank or duplicate dimension")
        if status not in {"covered", "applicable", "not-applicable"}:
            raise ValueError(f"claim {claim_id} dimension_coverage has unsupported status for {dimension}")
        if not reason:
            raise ValueError(f"claim {claim_id} dimension_coverage {dimension} lacks reason")
        # Preserve the legacy status exactly. Applicability and research
        # coverage are different concepts and must never be converted here.
        result[dimension] = (status, reason)
    return result


def _registry_entries(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if registry.get("schema_version") != "dimension-alias-registry.v1":
        raise ValueError("alias registry must use dimension-alias-registry.v1")
    entries = registry.get("entries")
    if not isinstance(entries, list):
        raise ValueError("alias registry entries must be an array")
    result: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("alias registry entries must be objects")
        label = str(entry.get("legacy_dimension", "")).strip()
        targets = entry.get("canonical_dimensions")
        status = entry.get("mapping_status")
        if not label or label in result:
            raise ValueError(f"alias registry has blank or duplicate legacy_dimension: {label}")
        if not isinstance(targets, list) or not targets or len(set(targets)) != len(targets):
            raise ValueError(f"alias registry {label} must have unique canonical_dimensions")
        if any(item not in CANONICAL_SET for item in targets):
            raise ValueError(f"alias registry {label} contains a non-canonical target")
        if status not in {"approved", "rejected", "ambiguous"}:
            raise ValueError(f"alias registry {label} has invalid mapping_status")
        result[label] = entry
    return result


def registry_approval_errors(registry: dict[str, Any], registry_path: Path | None = None) -> list[str]:
    """Verify approval using an external audit artifact, not a self-attested flag."""
    errors: list[str] = []
    for field in ("registry_id", "input_digest", "output_digest", "generated_by", "reviewed_by", "approved_at", "review_status", "independent_review", "audit_artifact"):
        if field not in registry:
            errors.append(f"alias registry missing {field}")
    if registry.get("review_status") != "approved":
        errors.append("alias registry is not approved")
    if not str(registry.get("reviewed_by", "")).strip() or registry.get("reviewed_by") == registry.get("generated_by"):
        errors.append("alias registry reviewer must be distinct from generator")
    if registry.get("independent_review") is not True:
        errors.append("alias registry needs independent_review=true")
    artifact = registry.get("audit_artifact")
    if not isinstance(artifact, dict) or not artifact.get("path") or not artifact.get("sha256"):
        errors.append("alias registry needs audit_artifact path and sha256")
        return errors
    artifact_path = Path(str(artifact["path"]))
    if not artifact_path.is_absolute() and registry_path is not None:
        artifact_path = registry_path.parent / artifact_path
    try:
        if digest_file(artifact_path) != artifact["sha256"]:
            errors.append("alias registry audit artifact digest mismatch")
        audit = load_json(artifact_path)
        if audit.get("registry_id") != registry.get("registry_id"):
            errors.append("alias audit artifact registry_id mismatch")
        if audit.get("reviewed_by") != registry.get("reviewed_by") or audit.get("independent_review") is not True:
            errors.append("alias audit artifact does not prove independent review")
        if audit.get("input_digest") != registry.get("input_digest") or audit.get("output_digest") != registry.get("output_digest"):
            errors.append("alias audit artifact input/output digest mismatch")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"alias audit artifact unavailable: {exc}")
    return errors


def _source_alias_registry(source: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Read explicit legacy mappings embedded in a source claim list.

    These are deliberately treated as pending mappings; an independent reviewer
    must approve the generated sidecar before it can be consumed downstream.
    """
    aliases = source.get("dimension_aliases", {})
    if aliases is None:
        return {}
    if not isinstance(aliases, dict):
        raise ValueError("source dimension_aliases must be an object")
    result: dict[str, dict[str, Any]] = {}
    for label, raw in aliases.items():
        if not isinstance(label, str) or not label.strip() or not isinstance(raw, dict):
            raise ValueError("source dimension_aliases entries must be named objects")
        targets = raw.get("canonical_dimensions")
        if not isinstance(targets, list) or not targets or any(item not in CANONICAL_SET for item in targets):
            # Preserve it as unresolved instead of guessing.
            targets = []
        result[label.strip()] = {
            "legacy_dimension": label.strip(),
            "canonical_dimensions": list(dict.fromkeys(targets)),
            "mapping_status": "ambiguous",
            "reason": str(raw.get("reason", "source-declared mapping requires independent review")),
        }
    return result


def _legacy_dimensions(claim: dict[str, Any], claim_id: str) -> list[str]:
    required = _clean_labels(claim.get("required_dimensions"), "required_dimensions", claim_id)
    coverage = _coverage_map(claim, claim_id)
    labels = list(dict.fromkeys(required + list(coverage)))
    if not labels:
        raise ValueError(f"claim {claim_id} has no legacy dimensions to migrate")
    return labels


def migrate(source_path: Path, output_path: Path, *, alias_registry_path: Path | None, generated_by: str, migration_id: str = "claim-dimension-migration-v1") -> dict[str, Any]:
    source = load_json(source_path)
    if source.get("schema_version") not in {"claim-list.v1", "claim-inventory.v1"}:
        raise ValueError("source must be claim-list.v1 or claim-inventory.v1")
    claims = source.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ValueError("source claims must be a non-empty array")

    registry: dict[str, dict[str, Any]] = {}
    registry_meta: dict[str, Any]
    if alias_registry_path is not None:
        registry_doc = load_json(alias_registry_path)
        registry = _registry_entries(registry_doc)
        approval_errors = registry_approval_errors(registry_doc, alias_registry_path)
        if approval_errors:
            registry = {label: {**entry, "mapping_status": "ambiguous"} for label, entry in registry.items()}
        registry_meta = {
            "path": str(alias_registry_path.resolve()),
            "digest": digest_file(alias_registry_path),
            "schema_version": str(registry_doc["schema_version"]),
            "registry_id": str(registry_doc.get("registry_id", "unknown")),
            "input_digest": str(registry_doc.get("input_digest", digest_bytes(b"untrusted-registry-input"))),
            "output_digest": str(registry_doc.get("output_digest", digest_bytes(b"untrusted-registry-output"))),
            "review_status": str(registry_doc.get("review_status", "pending")),
            "generated_by": str(registry_doc.get("generated_by", "unknown")),
            "reviewed_by": str(registry_doc.get("reviewed_by", "")),
            "independent_review": bool(registry_doc.get("independent_review", False)),
            "approved_at": str(registry_doc.get("approved_at", "")),
            "audit_artifact": registry_doc.get("audit_artifact", {"path": "", "sha256": digest_bytes(b"missing-audit")}),
        }
    else:
        registry = _source_alias_registry(source)
        pending_digest = digest_bytes(b"source.dimension_aliases")
        registry_meta = {"path": "<source.dimension_aliases>", "digest": pending_digest, "schema_version": "embedded-pending", "registry_id": "embedded-pending", "input_digest": pending_digest, "output_digest": pending_digest, "review_status": "pending", "generated_by": generated_by, "reviewed_by": "", "independent_review": False, "approved_at": "", "audit_artifact": {"path": "<none>", "sha256": pending_digest}}

    out_claims: list[dict[str, Any]] = []
    seen: set[str] = set()
    source_digest = digest_file(source_path)
    for claim_index, raw_claim in enumerate(claims):
        if not isinstance(raw_claim, dict):
            raise ValueError("source claims must contain objects")
        claim_id = str(raw_claim.get("claim_id", "")).strip()
        if not claim_id or claim_id in seen:
            raise ValueError(f"source claims have blank or duplicate claim_id: {claim_id}")
        seen.add(claim_id)
        legacy = _legacy_dimensions(raw_claim, claim_id)
        explicit = _coverage_map(raw_claim, claim_id)
        mapped: set[str] = set()
        unmapped: list[str] = []
        for label in legacy:
            if label in CANONICAL_SET:
                mapped.add(label)
                continue
            entry = registry.get(label)
            if entry and entry.get("mapping_status") == "approved" and entry.get("canonical_dimensions"):
                mapped.update(str(item) for item in entry["canonical_dimensions"])
            else:
                unmapped.append(label)

        legacy_coverage: list[dict[str, Any]] = []
        for legacy_dimension in legacy:
            if legacy_dimension in explicit:
                legacy_status, legacy_reason = explicit[legacy_dimension]
                anchor_locator = f"source:#/claims/{claim_index}/dimension_coverage"
            else:
                legacy_status = "not-recorded"
                legacy_reason = f"{claim_id}: required_dimensions declares applicability need only; no legacy research coverage record exists."
                anchor_locator = f"source:#/claims/{claim_index}/required_dimensions"
            legacy_coverage.append({
                "dimension": legacy_dimension,
                "status": legacy_status,
                "reason": {
                    "text": legacy_reason,
                    "source_anchors": [{"locator": anchor_locator, "sha256": source_digest}],
                },
            })

        coverage: list[dict[str, Any]] = []
        for dimension in CANONICAL_DIMENSIONS:
            coverage.append({
                "dimension": dimension,
                "status": "pending",
                "reason": {
                    "text": f"{claim_id}: applicability requires manual independent judgement; legacy research coverage is not applicability.",
                    "source_anchors": [{"locator": f"source:#/claims/{claim_index}", "sha256": source_digest}],
                },
            })

        status = "BLOCKED-UNMAPPED-LEGACY" if unmapped else "PENDING"
        out_claims.append({
            "claim_id": claim_id,
            "identity_fingerprint": identity_fingerprint(raw_claim),
            "legacy_dimensions": legacy,
            "legacy_research_coverage": legacy_coverage,
            "mapped_dimensions": sorted(mapped),
            "unmapped_legacy_dimensions": unmapped,
            "dimension_coverage": coverage,
            "migration_status": status,
        })

    counts = {
        "claims": len(out_claims),
        "ready": 0,
        "pending": sum(item["migration_status"] == "PENDING" for item in out_claims),
        "blocked_unmapped_legacy": sum(item["migration_status"] == "BLOCKED-UNMAPPED-LEGACY" for item in out_claims),
        "unmapped_legacy_dimensions": sum(len(item["unmapped_legacy_dimensions"]) for item in out_claims),
    }
    result = {
        "schema_version": "claim-dimension-applicability.v1",
        "migration_id": migration_id,
        "source_inventory": {
            "path": str(source_path.resolve()),
            "digest": digest_file(source_path),
            "schema_version": str(source["schema_version"]),
            "topic_id": str(source.get("topic_id", "unknown")),
            "claim_count": len(claims),
        },
        "alias_registry": registry_meta,
        "generated_by": generated_by,
        "reviewed_by": "",
        "independent_review": False,
        "review_status": "pending",
        "claims": out_claims,
        "counts": counts,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    # generated_at is intentionally not required by the schema but useful for audit.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-inventory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--alias-registry", type=Path)
    parser.add_argument("--generated-by", default="dimension-migration")
    parser.add_argument("--migration-id", default="claim-dimension-migration-v1")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = migrate(args.source_inventory, args.output, alias_registry_path=args.alias_registry, generated_by=args.generated_by, migration_id=args.migration_id)
        print(f"PASS-DRAFT claims={result['counts']['claims']} blocked_unmapped_legacy={result['counts']['blocked_unmapped_legacy']} review_status=pending")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"BLOCKED-DIMENSION-MIGRATION: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
