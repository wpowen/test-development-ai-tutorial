#!/usr/bin/env python3
"""Evaluate recorded RAG/LLM outputs with fail-closed teaching gates."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_FIELDS = {"id", "answer", "retrieved_ids", "citations", "refusal", "tool_call", "latency_ms", "cost_usd"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{line_no} must be a JSON object")
        rows.append(value)
    return rows


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[max(0, math.ceil(fraction * len(ordered)) - 1)]


def compare(value: float, rule: dict[str, Any]) -> bool:
    return value >= rule["value"] if rule["op"] == ">=" else value <= rule["value"]


def number(value: Any, field: str, failures: list[str]) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        failures.append(f"invalid telemetry type: {field}")
        return 0.0
    result = float(value)
    if not math.isfinite(result) or result < 0:
        failures.append(f"invalid telemetry value: {field}={value}")
        return 0.0
    return result


def string_list(value: Any, field: str, failures: list[str]) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        failures.append(f"invalid string list: {field}")
        return []
    return value


def evaluate(
    cases: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    thresholds: dict[str, dict[str, Any]],
    knowledge_ids: set[str] | None = None,
) -> dict[str, Any]:
    knowledge_ids = knowledge_ids or {doc_id for case in cases for doc_id in case.get("allowed_citations", [])}
    candidate_id_values = [item.get("id") for item in candidates]
    string_candidate_ids = [item_id for item_id in candidate_id_values if isinstance(item_id, str)]
    by_id = {item["id"]: item for item in candidates if isinstance(item.get("id"), str)}
    expected_ids = {case["id"] for case in cases}
    actual_ids = set(string_candidate_ids)
    duplicate_ids = sorted({item_id for item_id in string_candidate_ids if string_candidate_ids.count(item_id) > 1})
    unexpected_ids = sorted(actual_ids - expected_ids)
    missing_ids = sorted(expected_ids - actual_ids)

    details = []
    citation_checks: list[bool] = []
    refusal_checks: list[bool] = []
    tool_checks: list[bool] = []
    schema_checks: list[bool] = []
    forbidden_hits = 0
    latencies: list[float] = []
    costs: list[float] = []
    retrieval_expected_total = 0
    retrieval_hit_total = 0
    retrieval_actual_total = 0
    retrieval_relevant_total = 0

    for case in cases:
        candidate = by_id.get(case["id"])
        if candidate is None:
            details.append({"id": case["id"], "slice": case.get("slice"), "pass": False, "failures": ["missing candidate"]})
            schema_checks.append(False)
            continue

        failures: list[str] = []
        missing_fields = sorted(CANDIDATE_FIELDS - set(candidate))
        unknown_fields = sorted(set(candidate) - CANDIDATE_FIELDS)
        if missing_fields:
            failures.append(f"missing fields: {missing_fields}")
        if unknown_fields:
            failures.append(f"unknown fields: {unknown_fields}")

        answer = candidate.get("answer")
        if not isinstance(answer, str):
            failures.append("answer must be a string")
            answer = ""
        answer_lower = answer.lower()
        citations = string_list(candidate.get("citations"), "citations", failures)
        retrieved_ids = string_list(candidate.get("retrieved_ids"), "retrieved_ids", failures)
        refusal = candidate.get("refusal")
        if not isinstance(refusal, bool):
            failures.append("refusal must be boolean")

        invalid_retrieved = sorted(set(retrieved_ids) - knowledge_ids)
        invalid_citations = sorted(set(citations) - knowledge_ids)
        if invalid_retrieved:
            failures.append(f"unknown retrieved ids: {invalid_retrieved}")
        if invalid_citations:
            failures.append(f"unknown citation ids: {invalid_citations}")
        if not set(citations) <= set(retrieved_ids):
            failures.append("citations must be present in retrieved_ids")

        expected_retrieved = set(case.get("expected_retrieved_ids", []))
        actual_retrieved = set(retrieved_ids)
        retrieval_expected_total += len(expected_retrieved)
        retrieval_hit_total += len(expected_retrieved & actual_retrieved)
        retrieval_actual_total += len(actual_retrieved)
        retrieval_relevant_total += len(expected_retrieved & actual_retrieved)
        if expected_retrieved != actual_retrieved:
            failures.append(f"retrieval mismatch: expected {sorted(expected_retrieved)}, got {sorted(actual_retrieved)}")

        missing_terms = [term for term in case["expected_terms"] if term.lower() not in answer_lower]
        if missing_terms:
            failures.append(f"missing expected terms: {missing_terms}")
        found_forbidden = [term for term in case["forbidden_terms"] if term.lower() in answer_lower]
        if found_forbidden:
            forbidden_hits += 1
            failures.append(f"forbidden claims: {found_forbidden}")

        if case["require_citation"]:
            actual_citations = set(citations)
            allowed_citations = set(case["allowed_citations"])
            citation_ok = bool(actual_citations) and actual_citations <= allowed_citations
            citation_checks.append(citation_ok)
            if not citation_ok:
                failures.append(f"missing or disallowed citation: {sorted(actual_citations)}")

        refusal_ok = refusal is case["expected_refusal"]
        refusal_checks.append(refusal_ok)
        if not refusal_ok:
            failures.append(f"refusal mismatch: expected {case['expected_refusal']}")

        expected_tool = case.get("expected_tool")
        actual_tool = candidate.get("tool_call")
        if actual_tool is not None and (not isinstance(actual_tool, dict) or set(actual_tool) != {"name", "args"} or not isinstance(actual_tool.get("name"), str) or not isinstance(actual_tool.get("args"), dict)):
            failures.append("tool_call must be null or {name: string, args: object}")
            actual_tool = None
        if expected_tool:
            tool_ok = bool(actual_tool) and actual_tool.get("name") == expected_tool["name"] and actual_tool.get("args") == expected_tool["args"]
        else:
            tool_ok = actual_tool is None
        tool_checks.append(tool_ok)
        if not tool_ok:
            failures.append(f"wrong or unexpected tool call: {actual_tool}")

        latency = number(candidate.get("latency_ms"), "latency_ms", failures)
        cost = number(candidate.get("cost_usd"), "cost_usd", failures)
        latencies.append(latency)
        costs.append(cost)
        schema_ok = not any(message.startswith(("missing fields", "unknown fields", "answer must", "invalid ", "refusal must", "tool_call must", "unknown retrieved", "unknown citation", "citations must")) for message in failures)
        schema_checks.append(schema_ok)
        details.append({"id": case["id"], "slice": case["slice"], "pass": not failures, "failures": failures})

    metrics = {
        "coverage": len(expected_ids & actual_ids) / len(cases),
        "candidate_set_exact": 1.0 if not duplicate_ids and not unexpected_ids and not missing_ids and len(string_candidate_ids) == len(candidate_id_values) else 0.0,
        "task_pass_rate": sum(item["pass"] for item in details) / len(cases),
        "schema_pass_rate": sum(schema_checks) / len(cases),
        "retrieval_recall": retrieval_hit_total / retrieval_expected_total if retrieval_expected_total else 1.0,
        "retrieval_precision": retrieval_relevant_total / retrieval_actual_total if retrieval_actual_total else 1.0,
        "citation_pass_rate": sum(citation_checks) / len(citation_checks) if citation_checks else 1.0,
        "forbidden_claim_rate": forbidden_hits / len(cases),
        "refusal_pass_rate": sum(refusal_checks) / len(refusal_checks) if refusal_checks else 1.0,
        "tool_pass_rate": sum(tool_checks) / len(tool_checks) if tool_checks else 1.0,
        "p95_latency_ms": percentile(latencies, 0.95),
        "avg_cost_usd": sum(costs) / len(costs) if costs else 0.0,
        "max_cost_usd": max(costs) if costs else 0.0,
    }
    gates = {name: {"value": metrics[name], **rule, "pass": compare(metrics[name], rule)} for name, rule in thresholds.items()}
    verdict = "PASS" if all(gate["pass"] for gate in gates.values()) else "FAIL"
    return {
        "verdict": verdict,
        "candidate_set": {"missing": missing_ids, "unexpected": unexpected_ids, "duplicates": duplicate_ids},
        "metrics": metrics,
        "gates": gates,
        "details": details,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, default=ROOT / "data/candidate-current.jsonl")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/latest.json")
    args = parser.parse_args()
    try:
        cases = read_jsonl(ROOT / "data/eval_cases.jsonl")
        candidates = read_jsonl(args.candidate)
        thresholds = json.loads((ROOT / "data/thresholds.json").read_text(encoding="utf-8"))
        knowledge = json.loads((ROOT / "data/knowledge_base.json").read_text(encoding="utf-8"))
        knowledge_ids = {item["id"] for item in knowledge["documents"]}
        result = evaluate(cases, candidates, thresholds, knowledge_ids)
        exit_code = 0 if result["verdict"] == "PASS" else 1
    except Exception as exc:
        result = {"verdict": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
        exit_code = 2
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("verdict", "metrics", "error") if key in result}, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
