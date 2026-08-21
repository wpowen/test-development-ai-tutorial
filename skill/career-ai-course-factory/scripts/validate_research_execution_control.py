#!/usr/bin/env python3
"""Validate a bounded research batch before or after execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


TERMINAL = {"COMPLETED-RECEIPT", "BLOCKED-CAPABILITY", "BLOCKED-EVIDENCE", "TIMEOUT", "CANCELLED"}


def validate(document: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(document)]
    if errors:
        return errors
    batch = document["batch"]
    counters = document["counters"]
    claim_ids = batch["claim_ids"]
    if len(claim_ids) != len(set(claim_ids)):
        errors.append("batch claim_ids must be unique")
    if batch["index"] == 1 and len(claim_ids) != 1:
        errors.append("first batch must contain exactly one claim")
    if len(claim_ids) > batch["max_claims"]:
        errors.append("batch claim count exceeds max_claims")
    if counters["claims_started"] > batch["max_claims"]:
        errors.append("claims_started exceeds max_claims")
    if counters["provider_runs"] > batch["max_provider_runs"]:
        errors.append("provider_runs exceeds max_provider_runs")
    if counters["elapsed_minutes"] > batch["max_elapsed_minutes"]:
        errors.append("elapsed_minutes exceeds max_elapsed_minutes")
    budget = batch["max_total_tokens"]
    if budget != "UNKNOWN" and counters["total_tokens"] != "UNKNOWN" and counters["total_tokens"] > budget:
        errors.append("total_tokens exceeds max_total_tokens")
    if document["status"] == "ACTIVE":
        if counters["checkpoints_without_progress"] >= 2:
            errors.append("ACTIVE batch has two checkpoints without progress; stop it")
        if counters["provider_runs"] >= batch["max_provider_runs"]:
            errors.append("ACTIVE batch reached max_provider_runs; record a terminal stop")
        if counters["elapsed_minutes"] >= batch["max_elapsed_minutes"]:
            errors.append("ACTIVE batch reached max_elapsed_minutes; record TIMEOUT")
    else:
        if not document["stop_reason"].strip():
            errors.append("terminal batch needs stop_reason")
        if document["status"] == "COMPLETED-RECEIPT" and not document.get("output_artifact_hashes"):
            errors.append("COMPLETED-RECEIPT needs output_artifact_hashes")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("control", type=Path)
    parser.add_argument("--schema", type=Path, default=Path(__file__).resolve().parents[1] / "assets/schemas/research-execution-control.v1.schema.json")
    args = parser.parse_args()
    try:
        document = json.loads(args.control.read_text(encoding="utf-8"))
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
        errors = validate(document, schema)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"BLOCKED-CONTROL: {exc}")
        return 2
    if errors:
        print("BLOCKED-CONTROL")
        for error in errors:
            print(f"- {error}")
        return 2
    print(f"PASS-CONTROL {document['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
