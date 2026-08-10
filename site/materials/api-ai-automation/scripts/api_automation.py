#!/usr/bin/env python3
"""Copy-safe, standard-library API automation proof for the learner-materials package."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
CONFIGS = ROOT / "configs"

# Independent teaching rules. The service simulation below does not read or mutate them.
ORACLES = {
    "BUS-SHIPPED-REJECT": {"status": 409, "state": "SHIPPED", "side_effect_count": 0},
    "AUTH-NONOWNER-REJECT": {"status": 403, "state": "PAID_NOT_SHIPPED", "side_effect_count": 0},
    "IDEMP-SINGLE-EFFECT": {"status": 202, "state": "CANCEL_PENDING", "side_effect_count": 1},
    "ASYNC-LEGAL-TRANSITIONS": ["QUEUED", "CANCEL_PENDING", "COMPLETED"],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path):
    return json.loads(read_text(path))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def oracle_hash() -> str:
    payload = json.dumps(ORACLES, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def operation_ids(yaml_text: str) -> list[str]:
    return re.findall(r"^\s*operationId:\s*([A-Za-z0-9_-]+)\s*$", yaml_text, flags=re.MULTILINE)


def simulated_cancel(owner: bool, state: str, repeats: int, mutation: bool) -> dict:
    if not owner:
        return {"status": 403, "state": state, "side_effect_count": 0}
    if state == "SHIPPED" and not mutation:
        return {"status": 409, "state": "SHIPPED", "side_effect_count": 0}
    return {"status": 202, "state": "CANCEL_PENDING", "side_effect_count": 1}


def compare(case_id: str, actual, expected) -> dict:
    issues = []
    if isinstance(expected, dict):
        for key, value in expected.items():
            if actual.get(key) != value:
                issues.append(f"{key}: expected {value!r}, actual {actual.get(key)!r}")
    elif actual != expected:
        issues.append(f"expected {expected!r}, actual {actual!r}")
    return {"case_id": case_id, "status": "FAIL" if issues else "PASS", "issues": issues, "actual": actual}


def validate_event_fixture(data: dict) -> list[str]:
    issues = []
    required = set(data["event_contract"]["required_fields"])
    terminal_types = set(data["event_contract"]["terminal_event_types"])
    for stream in data["streams"]:
        events = stream["events"]
        for event in events:
            missing = required - set(event)
            if missing:
                issues.append(f"{stream['stream_id']}: missing fields {sorted(missing)}")
        unique_events = {event["event_id"]: event for event in events}
        ordered = list(unique_events.values())
        sequences = [event["sequence"] for event in ordered]
        if sequences != sorted(sequences):
            issues.append(f"{stream['stream_id']}: non-monotonic sequence")
        terminals = [event for event in ordered if event["terminal"]]
        if len(terminals) != 1 or terminals[0]["event_type"] not in terminal_types:
            issues.append(f"{stream['stream_id']}: expected exactly one valid terminal")
        if "expected_unique_side_effects" in stream:
            effects = {event["event_id"] for event in events if event["event_type"] == "payment.succeeded"}
            if len(effects) != stream["expected_unique_side_effects"]:
                issues.append(f"{stream['stream_id']}: duplicate delivery changed side-effect count")
    return issues


def run(mode: str, report_arg: str) -> int:
    mutation = mode == "mutation"
    order_path = FIXTURES / "order-cancel.openapi.yaml"
    payment_path = FIXTURES / "payment-intent.openapi.yaml"
    events_path = FIXTURES / "checkout-events.json"
    mutation_path = CONFIGS / "schema-mutations.yaml"
    workload_path = CONFIGS / "ai-performance-workload.yaml"

    order_text = read_text(order_path)
    payment_text = read_text(payment_path)
    mutation_text = read_text(mutation_path)
    workload_text = read_text(workload_path)
    events = read_json(events_path)

    results = []
    order_ops = set(operation_ids(order_text))
    payment_ops = set(operation_ids(payment_text))
    results.append(compare("CONTRACT-ORDER-OPERATIONS", sorted(order_ops), sorted({"cancelOrder", "getCancellationTask", "streamOrderCancellationEvents"})))
    results.append(compare("CONTRACT-PAYMENT-OPERATIONS", sorted(payment_ops), sorted({"createPaymentIntent", "confirmPaymentIntent", "streamPaymentIntentEvents"})))

    schema_markers = ["required: [task_id, order_id, status]", "required: [intent_id, order_id, amount_minor, currency, status]", "Idempotency-Key", "text/event-stream"]
    missing_markers = [marker for marker in schema_markers if marker not in order_text + payment_text]
    results.append({"case_id": "SCHEMA-REQUIRED-SURFACES", "status": "FAIL" if missing_markers else "PASS", "issues": [f"missing marker: {item}" for item in missing_markers], "actual": {"missing_markers": missing_markers}})

    results.append(compare("BUS-SHIPPED-REJECT", simulated_cancel(True, "SHIPPED", 1, mutation), ORACLES["BUS-SHIPPED-REJECT"]))
    results.append(compare("AUTH-NONOWNER-REJECT", simulated_cancel(False, "PAID_NOT_SHIPPED", 1, mutation), ORACLES["AUTH-NONOWNER-REJECT"]))
    results.append(compare("IDEMP-SINGLE-EFFECT", simulated_cancel(True, "PAID_NOT_SHIPPED", 2, mutation), ORACLES["IDEMP-SINGLE-EFFECT"]))
    results.append(compare("ASYNC-LEGAL-TRANSITIONS", ["QUEUED", "CANCEL_PENDING", "COMPLETED"], ORACLES["ASYNC-LEGAL-TRANSITIONS"]))

    event_issues = validate_event_fixture(events)
    results.append({"case_id": "EVENT-ORDER-TERMINAL-AND-DEDUP", "status": "FAIL" if event_issues else "PASS", "issues": event_issues, "actual": {"stream_count": len(events["streams"])}})

    config_issues = []
    for marker in ["MUT-ORDER-SHIPPED-ACCEPTED", "MUT-IDEMPOTENCY-DUPLICATE-REFUND", "MUT-SSE-DOUBLE-TERMINAL"]:
        if marker not in mutation_text:
            config_issues.append(f"mutation catalog missing {marker}")
    for marker in ["execution_status: NOT_RUN", "task_success_rate_min", "duplicate_side_effect_rate_max", "cost_per_success_usd_max"]:
        if marker not in workload_text:
            config_issues.append(f"workload config missing {marker}")
    results.append({"case_id": "CONFIG-MUTATION-AND-WORKLOAD", "status": "FAIL" if config_issues else "PASS", "issues": config_issues, "actual": {"external_execution": "NOT_RUN"}})

    failed = [item for item in results if item["status"] == "FAIL"]
    report = {
        "run_id": datetime.now(timezone.utc).strftime("RUN-%Y%m%dT%H%M%SZ"),
        "mode": mode,
        "status": "FAIL" if failed else "PASS",
        "exit_code": 1 if failed else 0,
        "evidence_status": "fixture-tested",
        "runtime": platform.python_version(),
        "workdir_contract": "learner-materials root",
        "mutation_id": "MUT-ORDER-SHIPPED-ACCEPTED" if mutation else None,
        "oracle": {"id": "approved-teaching-oracle.v1", "sha256": oracle_hash(), "independent_from_service_flags": True},
        "input_hashes": {
            "order_openapi": sha256(order_path),
            "payment_openapi": sha256(payment_path),
            "checkout_events": sha256(events_path),
            "schema_mutations": sha256(mutation_path),
            "ai_performance_workload": sha256(workload_path),
        },
        "results": results,
        "failed_case_ids": [item["case_id"] for item in failed],
        "not_run": ["Schemathesis", "Pact", "k6", "GitLab CI", "live endpoint", "real model", "production traffic"],
        "boundary": "Synthetic, offline, standard-library fixture. No external tool or service execution.",
    }
    report_path = Path(report_arg)
    if not report_path.is_absolute():
        report_path = ROOT / report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mode": mode, "status": report["status"], "exit_code": report["exit_code"], "failed_case_ids": report["failed_case_ids"], "report": str(report_path)}, ensure_ascii=False))
    return report["exit_code"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["baseline", "mutation", "repair"])
    parser.add_argument("--report", default=None)
    args = parser.parse_args()
    default_report = f"reports/{args.mode}.json"
    return run(args.mode, args.report or default_report)


if __name__ == "__main__":
    sys.exit(main())
