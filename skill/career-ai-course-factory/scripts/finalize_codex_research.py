#!/usr/bin/env python3
"""Compile independent Codex-research adjudications into a terminal saturation record."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from codex_research_contract import load_json, validate_codex_topic
from finalize_claim_research import atomic_write_text, render_contradiction_matrix, validate_adjudication_row
from run_claim_deep_research import atomic_write_json, safe_id


def finalize_codex_topic(
    *, package_root: Path, topic_id: str, adjudications_file: Path, replace: bool,
) -> dict[str, Any]:
    topic_id = safe_id(topic_id, "topic id")
    topic_dir = package_root.resolve() / "research" / "topics" / topic_id
    validation_errors = validate_codex_topic(topic_dir, require_saturation=False)
    if validation_errors:
        raise ValueError("Codex research receipts are invalid: " + "; ".join(validation_errors))
    inventory = load_json(topic_dir / "claim-inventory.json")
    receipts = load_json(topic_dir / "codex-research-receipts.json")
    adjudications = load_json(adjudications_file)
    if not isinstance(adjudications, dict) or adjudications.get("schema_version") != "codex-research-adjudications.v1":
        raise ValueError("adjudications must use codex-research-adjudications.v1")
    if adjudications.get("topic_id") != topic_id:
        raise ValueError("adjudication topic mismatch")
    extraction = inventory.get("extraction", {})
    author_id = str(extraction.get("author_id", ""))
    auditor_id = str(adjudications.get("auditor_id", ""))
    if not auditor_id or auditor_id in {author_id, str(extraction.get("independent_auditor_id", ""))}:
        raise ValueError("Codex saturation requires a fresh auditor distinct from author and claim extractor")
    runs = receipts.get("runs", [])
    runtime_identities = {
        str(value)
        for run in runs if isinstance(run, dict)
        for field in ("agent_invocation_ids",)
        for value in (run.get(field, []) if isinstance(run.get(field), list) else [])
    }
    runtime_identities.update(
        str(run.get(field, ""))
        for run in runs if isinstance(run, dict)
        for field in ("integrator_invocation_id", "orchestrator_invocation_id")
    )
    if auditor_id in runtime_identities:
        raise ValueError("Codex saturation auditor cannot be an evidence agent, integrator, or orchestrator")
    run_map: dict[str, dict[str, Any]] = {}
    for run in runs:
        if not isinstance(run, dict):
            continue
        mapped = dict(run)
        if mapped.get("phase") == "initial-research":
            mapped["phase"] = "initial-deep-research"
        run_map[str(mapped.get("run_id", ""))] = mapped
    claim_map = {
        str(row.get("claim_id")): row
        for row in inventory.get("claims", []) if isinstance(row, dict)
    }
    rows = adjudications.get("claims")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Codex adjudications claims must be a non-empty array")
    compiled: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Codex adjudication row must be an object")
        claim_id = str(row.get("claim_id", ""))
        claim = claim_map.get(claim_id)
        if claim is None or claim_id in seen:
            raise ValueError(f"Codex adjudication has unknown or duplicate claim: {claim_id}")
        seen.add(claim_id)
        compiled.append(validate_adjudication_row(
            row,
            required_dimensions={str(value) for value in claim.get("required_dimensions", [])},
            valid_runs=run_map,
        ))
    if seen != set(claim_map):
        raise ValueError("Codex adjudications do not cover every claim")
    saturation = {
        "schema_version": "codex-research-saturation.v1",
        "topic_id": topic_id,
        "author_id": author_id,
        "independent_auditor_id": auditor_id,
        "claims": compiled,
        "overall_verdict": "PASS-CODEX-RESEARCH",
        "deep_research_status": "BLOCKED-DEEP-RESEARCH",
    }
    saturation_path = topic_dir / "codex-research-saturation.json"
    matrix_path = topic_dir / "codex-contradiction-matrix.md"
    if not replace and (saturation_path.exists() or matrix_path.exists()):
        raise ValueError("Codex terminal artifacts already exist; use --replace after independent review")
    atomic_write_json(saturation_path, saturation)
    atomic_write_text(matrix_path, render_contradiction_matrix(topic_id, rows))
    return saturation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--topic-id", required=True)
    parser.add_argument("--adjudications-file", required=True, type=Path)
    parser.add_argument("--replace", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = finalize_codex_topic(
            package_root=args.package_root, topic_id=args.topic_id,
            adjudications_file=args.adjudications_file, replace=args.replace,
        )
        print(f"PASS-CODEX-RESEARCH topic_id={result['topic_id']} claims={len(result['claims'])}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"BLOCKED-CODEX-RESEARCH: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
