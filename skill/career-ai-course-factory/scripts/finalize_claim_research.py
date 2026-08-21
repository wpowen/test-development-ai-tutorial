#!/usr/bin/env python3
"""Compile independently authored adjudications into contradiction and saturation artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from run_claim_deep_research import atomic_write_json, load_json, safe_id


EXPANSION_PHASES = {"counterevidence", "gap-fill", "verification"}
DISPOSITIONS = {"SUPPORTED", "SCOPED", "UNKNOWN-EXPLICIT", "REJECTED"}
CONTRADICTION_STATUSES = {"resolved", "preserved-unresolved", "none-found"}


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
    )
    temporary_path = Path(handle.name)
    try:
        with handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def load_adjudications(path: Path) -> dict[str, Any]:
    value = load_json(path)
    if not isinstance(value, dict) or value.get("schema_version") != "claim-research-adjudications.v1":
        raise ValueError("adjudications must use claim-research-adjudications.v1")
    if not isinstance(value.get("claims"), list) or not value["claims"]:
        raise ValueError("adjudications claims must be a non-empty array")
    return value


def render_contradiction_matrix(topic_id: str, rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Contradiction matrix",
        "",
        f"Topic: `{topic_id}`",
        "",
        "## Claims",
        "",
        "This matrix is compiled from the independent adjudication input; it does not convert unresolved evidence into certainty.",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"### {row['claim_id']}",
                "",
                f"- Status: `{row['contradiction_status']}`",
                f"- Final disposition: `{row['final_disposition']}`",
                f"- Runs: {', '.join(f'`{run_id}`' for run_id in row['run_ids'])}",
                f"- Rationale: {row['rationale']}",
                "",
                "| Issue | Evidence runs | Disposition | Rationale |",
                "| --- | --- | --- | --- |",
            ]
        )
        contradictions = row.get("contradictions", [])
        if contradictions:
            for item in contradictions:
                issue = str(item["issue"]).replace("|", "\\|")
                run_ids = ", ".join(str(run_id) for run_id in item["run_ids"]).replace("|", "\\|")
                disposition = str(item["disposition"]).replace("|", "\\|")
                rationale = str(item["rationale"]).replace("|", "\\|")
                lines.append(f"| {issue} | {run_ids} | {disposition} | {rationale} |")
        else:
            lines.append("| No material contradiction recorded | — | none-found | The auditor found no conflicting claim that changes the bounded disposition. |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def validate_adjudication_row(
    row: dict[str, Any],
    *,
    required_dimensions: set[str],
    valid_runs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    claim_id = str(row.get("claim_id", ""))
    safe_id(claim_id, "adjudication claim id")
    run_ids = row.get("run_ids")
    if not isinstance(run_ids, list) or len(run_ids) < 2 or len(set(map(str, run_ids))) != len(run_ids):
        raise ValueError(f"claim {claim_id} must reference at least two distinct runs")
    run_ids = [str(item) for item in run_ids]
    linked_runs: list[dict[str, Any]] = []
    for run_id in run_ids:
        run = valid_runs.get(run_id)
        if run is None or claim_id not in {str(item) for item in run.get("claim_ids", [])}:
            raise ValueError(f"claim {claim_id} references an invalid or unrelated run: {run_id}")
        if run.get("status") != "completed":
            raise ValueError(f"claim {claim_id} references an incomplete run: {run_id}")
        linked_runs.append(run)
    phases = {str(item.get("phase", "")) for item in linked_runs}
    if "initial-deep-research" not in phases:
        raise ValueError(f"claim {claim_id} lacks an initial-deep-research run")
    if not phases.intersection(EXPANSION_PHASES):
        raise ValueError(f"claim {claim_id} lacks counterevidence, gap-fill, or verification research")

    coverage = row.get("coverage_dimensions")
    if not isinstance(coverage, list) or not coverage:
        raise ValueError(f"claim {claim_id} lacks coverage_dimensions")
    coverage_ids: set[str] = set()
    for item in coverage:
        if not isinstance(item, dict):
            raise ValueError(f"claim {claim_id} coverage rows must be objects")
        dimension = str(item.get("dimension", ""))
        if not dimension or dimension in coverage_ids:
            raise ValueError(f"claim {claim_id} has blank or duplicate coverage dimension")
        coverage_ids.add(dimension)
        if item.get("status") not in {"covered", "not-applicable"}:
            raise ValueError(f"claim {claim_id} coverage status is invalid for {dimension}")
        if not isinstance(item.get("evidence_or_reason"), str) or not item["evidence_or_reason"].strip():
            raise ValueError(f"claim {claim_id} coverage dimension {dimension} lacks evidence or reason")
    if coverage_ids != required_dimensions:
        missing = sorted(required_dimensions - coverage_ids)
        extra = sorted(coverage_ids - required_dimensions)
        raise ValueError(f"claim {claim_id} coverage mismatch; missing={missing} extra={extra}")

    contradiction_status = row.get("contradiction_status")
    if contradiction_status not in CONTRADICTION_STATUSES:
        raise ValueError(f"claim {claim_id} contradiction_status is invalid")
    contradictions = row.get("contradictions")
    if not isinstance(contradictions, list):
        raise ValueError(f"claim {claim_id} contradictions must be an array")
    if contradiction_status != "none-found" and not contradictions:
        raise ValueError(f"claim {claim_id} contradiction status requires at least one contradiction record")
    if contradiction_status == "none-found" and contradictions:
        raise ValueError(f"claim {claim_id} none-found status cannot contain contradiction records")
    for index, item in enumerate(contradictions):
        if not isinstance(item, dict):
            raise ValueError(f"claim {claim_id} contradiction {index} must be an object")
        for field in ("issue", "disposition", "rationale"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"claim {claim_id} contradiction {index} lacks {field}")
        evidence_runs = item.get("run_ids")
        if not isinstance(evidence_runs, list) or not evidence_runs or not set(map(str, evidence_runs)).issubset(set(run_ids)):
            raise ValueError(f"claim {claim_id} contradiction {index} references invalid runs")

    assessments = row.get("round_assessments")
    if not isinstance(assessments, list) or len(assessments) != len(run_ids):
        raise ValueError(f"claim {claim_id} needs one round assessment for every referenced run")
    assessment_by_run: dict[str, dict[str, Any]] = {}
    for item in assessments:
        if not isinstance(item, dict):
            raise ValueError(f"claim {claim_id} round assessment must be an object")
        run_id = str(item.get("run_id", ""))
        if run_id not in run_ids or run_id in assessment_by_run:
            raise ValueError(f"claim {claim_id} round assessment references an invalid or duplicate run")
        if not isinstance(item.get("material_change"), bool):
            raise ValueError(f"claim {claim_id} round assessment needs boolean material_change")
        if not isinstance(item.get("assessment"), str) or not item["assessment"].strip():
            raise ValueError(f"claim {claim_id} round assessment needs an explanation")
        assessment_by_run[run_id] = item

    ordered_runs = sorted(linked_runs, key=lambda item: int(item.get("round", 0)))
    ordered_ids = [str(item["run_id"]) for item in ordered_runs]
    if set(ordered_ids) != set(run_ids) or any(not isinstance(item.get("round"), int) or item["round"] < 1 for item in linked_runs):
        raise ValueError(f"claim {claim_id} run receipts need valid round numbers")
    round_numbers = [int(item["round"]) for item in ordered_runs]
    if len(set(round_numbers)) != len(round_numbers):
        raise ValueError(f"claim {claim_id} run round numbers must be unique")
    stable = row.get("two_consecutive_rounds_without_material_change") is True
    primary_exception = row.get("conclusive_primary_authority_exception") is True
    last_two_stable = len(ordered_ids) >= 2 and all(
        assessment_by_run[run_id]["material_change"] is False for run_id in ordered_ids[-2:]
    )
    if stable != last_two_stable:
        raise ValueError(f"claim {claim_id} stable-round assertion does not match the last two round assessments")
    if stable and round_numbers[-1] != round_numbers[-2] + 1:
        raise ValueError(f"claim {claim_id} stable rounds must be consecutive")
    if not stable and not primary_exception:
        raise ValueError(f"claim {claim_id} is not saturated: two stable rounds or a primary-authority exception is required")
    if primary_exception:
        rationale = row.get("primary_authority_exception_rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError(f"claim {claim_id} primary-authority exception lacks rationale")

    if row.get("verdict") != "SATURATED":
        raise ValueError(f"claim {claim_id} verdict must be SATURATED")
    if row.get("final_disposition") not in DISPOSITIONS:
        raise ValueError(f"claim {claim_id} final_disposition is invalid")
    if contradiction_status == "preserved-unresolved" and row.get("final_disposition") not in {"SCOPED", "UNKNOWN-EXPLICIT", "REJECTED"}:
        raise ValueError(f"claim {claim_id} unresolved contradiction cannot produce SUPPORTED")
    if not isinstance(row.get("rationale"), str) or not row["rationale"].strip():
        raise ValueError(f"claim {claim_id} saturation rationale is required")

    return {
        "claim_id": claim_id,
        "run_ids": ordered_ids,
        "coverage_dimensions": coverage,
        "contradiction_status": contradiction_status,
        "two_consecutive_rounds_without_material_change": stable,
        "conclusive_primary_authority_exception": primary_exception,
        "final_disposition": row["final_disposition"],
        "verdict": "SATURATED",
        "rationale": row["rationale"],
        "round_assessments": assessments,
    }


def finalize_topic_research(
    *, package_root: Path, topic_id: str, adjudications_file: Path, replace: bool
) -> dict[str, Any]:
    topic_id = safe_id(topic_id, "topic id")
    topic_dir = package_root.resolve() / "research" / "topics" / topic_id
    inventory = load_json(topic_dir / "claim-inventory.json")
    receipts = load_json(topic_dir / "deep-research-receipts.json")
    adjudications = load_adjudications(adjudications_file)
    if not isinstance(inventory, dict) or inventory.get("schema_version") != "claim-inventory.v1":
        raise ValueError("claim inventory is missing or invalid")
    if inventory.get("topic_id") != topic_id or adjudications.get("topic_id") != topic_id:
        raise ValueError("topic id mismatch across inventory or adjudications")
    if not isinstance(receipts, dict) or receipts.get("schema_version") != "deep-research-receipts.v1" or receipts.get("topic_id") != topic_id:
        raise ValueError("deep research receipts are missing, invalid, or topic-mismatched")

    extraction = inventory.get("extraction")
    if not isinstance(extraction, dict):
        raise ValueError("claim inventory extraction record is missing")
    author_id = str(extraction.get("author_id", ""))
    expected_auditor = str(extraction.get("independent_auditor_id", ""))
    auditor_id = str(adjudications.get("auditor_id", ""))
    if not auditor_id or auditor_id == author_id or auditor_id != expected_auditor:
        raise ValueError("adjudication auditor must match the independent auditor and differ from the author")

    claims = inventory.get("claims")
    runs = receipts.get("runs")
    if not isinstance(claims, list) or not claims or not isinstance(runs, list):
        raise ValueError("claim inventory or receipt runs are invalid")
    claim_map = {str(item.get("claim_id")): item for item in claims if isinstance(item, dict) and item.get("claim_id")}
    if len(claim_map) != len(claims):
        raise ValueError("claim inventory contains blank or duplicate ids")
    run_map = {str(item.get("run_id")): item for item in runs if isinstance(item, dict) and item.get("run_id")}
    if len(run_map) != len(runs):
        raise ValueError("deep research receipts contain blank or duplicate run ids")
    adjudication_rows = adjudications["claims"]
    row_map = {
        str(item.get("claim_id")): item
        for item in adjudication_rows
        if isinstance(item, dict) and item.get("claim_id")
    }
    if len(row_map) != len(adjudication_rows) or set(row_map) != set(claim_map):
        raise ValueError("adjudication claim set must exactly match the claim inventory")

    saturation_rows: list[dict[str, Any]] = []
    validated_rows: list[dict[str, Any]] = []
    for claim_id in claim_map:
        required = claim_map[claim_id].get("required_dimensions")
        if not isinstance(required, list) or not required:
            raise ValueError(f"claim {claim_id} required_dimensions are invalid")
        validated = validate_adjudication_row(
            row_map[claim_id], required_dimensions={str(item) for item in required}, valid_runs=run_map
        )
        saturation_rows.append(validated)
        validated_rows.append(row_map[claim_id])

    saturation = {
        "schema_version": "research-saturation.v1",
        "topic_id": topic_id,
        "independent_auditor_id": auditor_id,
        "claims": saturation_rows,
        "overall_verdict": "PASS",
    }
    saturation_path = topic_dir / "research-saturation.json"
    matrix_path = topic_dir / "contradiction-matrix.md"
    if not replace and (saturation_path.exists() or matrix_path.exists()):
        raise ValueError("saturation or contradiction artifact already exists; use --replace after independent review")
    matrix = render_contradiction_matrix(topic_id, validated_rows)
    atomic_write_text(matrix_path, matrix)
    atomic_write_json(saturation_path, saturation)
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
        saturation = finalize_topic_research(
            package_root=args.package_root,
            topic_id=args.topic_id,
            adjudications_file=args.adjudications_file,
            replace=args.replace,
        )
        print(f"PASS topic_id={saturation['topic_id']} claims={len(saturation['claims'])} verdict=PASS")
        return 0
    except (OSError, ValueError) as exc:
        print(f"BLOCKED-RESEARCH-SATURATION: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
