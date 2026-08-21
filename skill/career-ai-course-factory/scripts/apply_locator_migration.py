#!/usr/bin/env python3
"""Apply only audited, unambiguous locator proposals to a claim inventory.

This helper deliberately refuses partial or guessed migrations.  It can
materialize a formal inventory only when every source location for the chosen
topic is an ``AUTO-CANDIDATE`` in the proposal and the existing claim list is
already independently reviewed with ``unmapped_propositions=0``.  Manual,
missing, or ambiguous rows remain proposal-only and must be resolved by an
auditor before this command can write an inventory.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from prepare_claim_inventory import prepare_inventory


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def migrate_topic(
    *,
    package_root: Path,
    proposal_path: Path,
    topic_id: str,
    source_files: list[str],
    author_id: str,
    independent_auditor_id: str,
    write: bool,
) -> dict[str, Any]:
    topic_dir = package_root.resolve() / "research" / "topics" / topic_id
    claims_path = topic_dir / "claim-list.v1.json"
    proposal = _load(proposal_path)
    claims = _load(claims_path)
    topic_proposal = next((item for item in proposal.get("topics", []) if item.get("topic_id") == topic_id), None)
    if not isinstance(topic_proposal, dict):
        raise ValueError(f"proposal has no topic {topic_id}")
    if claims.get("schema_version") != "claim-list.v1" or claims.get("unmapped_propositions") != 0:
        raise ValueError("claim list must be claim-list.v1 with unmapped_propositions=0")
    if claims.get("reviewed_by") != independent_auditor_id:
        raise ValueError("independent auditor id must match claim-list.v1 reviewed_by")

    by_claim: dict[str, list[dict[str, Any]]] = {}
    for row in topic_proposal.get("rows", []):
        by_claim.setdefault(str(row.get("claim_id")), []).append(row)
    transformed = copy.deepcopy(claims)
    pending: list[dict[str, Any]] = []
    for claim in transformed.get("claims", []):
        claim_id = str(claim.get("claim_id"))
        rows = by_claim.get(claim_id, [])
        raw_locations = list(claim.get("source_locations", []))
        if len(rows) != len(raw_locations):
            raise ValueError(f"proposal/claim locator count mismatch for {claim_id}")
        replacements: list[str] = []
        seen_replacements: set[str] = set()
        for raw, row in zip(raw_locations, rows):
            if row.get("raw") != raw or row.get("status") != "AUTO-CANDIDATE":
                pending.append({"claim_id": claim_id, "raw": raw, "status": row.get("status"), "row": row})
                replacements.append(str(raw))
            else:
                proposed_values = row.get("proposed_locators") or ([row["proposed"]] if isinstance(row.get("proposed"), str) else [])
                if not proposed_values or any(not isinstance(value, str) or not value for value in proposed_values):
                    pending.append({"claim_id": claim_id, "raw": raw, "status": "INVALID-PROPOSAL", "row": row})
                    replacements.append(str(raw))
                    continue
                if len(proposed_values) != len(set(proposed_values)):
                    pending.append({"claim_id": claim_id, "raw": raw, "status": "DUPLICATE-CANONICAL-LOCATOR", "row": row})
                    replacements.append(str(raw))
                    continue
                duplicate = next((value for value in proposed_values if value in seen_replacements), None)
                if duplicate is not None:
                    pending.append({"claim_id": claim_id, "raw": raw, "status": "DUPLICATE-CANONICAL-LOCATOR", "duplicate": duplicate, "row": row})
                    replacements.append(str(raw))
                    continue
                replacements.extend(proposed_values)
                seen_replacements.update(proposed_values)
        claim["source_locations"] = replacements

    result: dict[str, Any] = {
        "schema_version": "locator-migration-application.v1",
        "status": "READY-AUTO-ONLY" if not pending else "BLOCKED-MANUAL-REVIEW",
        "topic_id": topic_id,
        "proposal_sha256": _sha256(proposal_path),
        "claim_list_sha256": _sha256(claims_path),
        "locator_count": sum(len(item.get("source_locations", [])) for item in claims.get("claims", [])),
        "auto_candidate_count": sum(1 for claim in transformed.get("claims", []) for raw in claim.get("source_locations", []) if raw != ""),
        "pending": pending,
        "write": False,
    }
    if pending:
        return result
    if not write:
        result["write"] = False
        return result

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json") as handle:
        json.dump(transformed, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        try:
            inventory = prepare_inventory(
                package_root=package_root,
                topic_id=topic_id,
                claims_file=Path(handle.name),
                source_files=source_files,
                author_id=author_id,
                independent_auditor_id=independent_auditor_id,
                replace=True,
                execution_contract="openai-deep-research.v1",
                locator_roots={},
            )
        except (OSError, ValueError) as exc:
            result["status"] = "BLOCKED-LOCATOR-VALIDATION"
            result["error"] = str(exc)
            return result
    inventory["locator_migration"] = {
        "schema_version": "locator-migration-application.v1",
        "status": "APPLIED-AUTO-CANDIDATES",
        "proposal_sha256": result["proposal_sha256"],
        "claim_list_sha256": result["claim_list_sha256"],
        "manual_review_required": False,
    }
    (topic_dir / "claim-inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result["write"] = True
    result["inventory_claim_count"] = len(inventory.get("claims", []))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--proposal", required=True, type=Path)
    parser.add_argument("--topic-id", required=True)
    parser.add_argument("--source-file", action="append", required=True)
    parser.add_argument("--author-id", required=True)
    parser.add_argument("--independent-auditor-id", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        result = migrate_topic(
            package_root=args.package_root.resolve(),
            proposal_path=args.proposal.resolve(),
            topic_id=args.topic_id,
            source_files=args.source_file,
            author_id=args.author_id,
            independent_auditor_id=args.independent_auditor_id,
            write=args.write,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"BLOCKED-LOCATOR-MIGRATION: {exc}")
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "READY-AUTO-ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
