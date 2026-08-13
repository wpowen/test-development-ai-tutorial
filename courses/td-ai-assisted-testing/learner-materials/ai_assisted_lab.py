#!/usr/bin/env python3
"""Deterministic fixture lab for TD-T05..TD-T08.

The runner validates candidate artifacts against frozen, independent rules. It
does not call a model and never treats its own candidate text as an Oracle.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
TOPICS = ("TD-T05", "TD-T06", "TD-T07", "TD-T08")


def load_json(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(relative: str) -> str:
    return "sha256:" + hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def write_report(relative: str, report: dict[str, Any]) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify_prompt_package(topic: str) -> list[str]:
    folder = f"page-prompts/{topic}"
    manifest = load_json(f"{folder}/manifest.json")
    required = ("prompt-v1.md", "critic-v1.md", "input.json", "schema.json", "eval.json", "mutation.json", "model-config.json")
    errors = [f"missing {name}" for name in required if not (ROOT / folder / name).is_file()]
    if manifest.get("topic_id") != topic or manifest.get("version") != "1.0.0":
        errors.append("manifest identity/version mismatch")
    if manifest.get("model_evidence") != "NOT_RUN":
        errors.append("offline package must keep model_evidence=NOT_RUN")
    if manifest.get("independent_oracle") != "../../fixtures/oracles.json":
        errors.append("independent oracle must be outside the generator package")
    eval_cases = load_json(f"{folder}/eval.json").get("cases", [])
    required_kinds = {"positive", "boundary", "conflict", "missing", "unauthorized", "refusal", "truncation", "paraphrase"}
    if {case.get("kind") for case in eval_cases} != required_kinds:
        errors.append("eval set must cover eight stop/variation kinds")
    mutations = load_json(f"{folder}/mutation.json").get("mutations", [])
    if not mutations or any(not item.get("expected_status") for item in mutations):
        errors.append("mutation package is incomplete")
    return errors


def common_report(topic: str, phase: str) -> dict[str, Any]:
    manifest = load_json(f"page-prompts/{topic}/manifest.json")
    return {
        "schema_version": "1.0",
        "topic_id": topic,
        "phase": phase,
        "evidence_scope": "deterministic-offline-fixture",
        "model_evidence": "NOT_RUN",
        "prompt_package": {"version": manifest["version"], "manifest_hash": sha256(f"page-prompts/{topic}/manifest.json")},
        "basis_hash": sha256("fixtures/basis.json"),
        "oracle_hash": sha256("fixtures/oracles.json"),
        "oracle_authority": "frozen approved basis; independent from candidate generator",
        "human_decision_required": True,
    }


def run_t05(phase: str) -> tuple[int, dict[str, Any]]:
    report = common_report("TD-T05", phase)
    basis = load_json("fixtures/basis.json")
    risks = [
        {"risk_id": "R-ACTIVATED", "requirement_ref": "PRD-v4#R12", "diff_ref": "refund.py#L18-L24", "oracle_id": "O-ACTIVATED-BLOCK", "owner": "qa-refund", "status": "CANDIDATE"},
        {"risk_id": "R-AUDIT", "requirement_ref": "PRD-v4#R13", "diff_ref": "events.py#L9-L16", "oracle_id": "O-AUDIT-ONCE", "owner": "qa-refund", "status": "CANDIDATE"},
    ]
    if phase == "fault":
        risks[1].pop("diff_ref")
        risks.append({"risk_id": "R-INVENTED-SLA", "requirement_ref": "UNKNOWN", "diff_ref": "refund.py#L1-L4", "oracle_id": "MODEL-GUESSED", "owner": "UNKNOWN", "status": "CANDIDATE"})
    missing = [item["risk_id"] for item in risks if any(not item.get(key) or item.get(key) == "UNKNOWN" for key in ("requirement_ref", "diff_ref", "oracle_id", "owner"))]
    invalid_oracle = [item["risk_id"] for item in risks if item.get("oracle_id") not in basis["accepted_oracle_ids"]]
    status = "BLOCKED" if missing or invalid_oracle else "PASS"
    report.update({"status": status, "risk_candidates": risks, "missing_evidence": missing, "invalid_oracle_refs": invalid_oracle, "decision": "STOP_AND_REVIEW" if status == "BLOCKED" else "ACCEPT_CANDIDATES_FOR_HUMAN_REVIEW"})
    return (2 if status == "BLOCKED" else 0), report


def refund_result(case: dict[str, Any], mutated: bool) -> dict[str, Any]:
    blocked = case["activated"] and case["product_type"] == "DIGITAL"
    if mutated:
        blocked = not blocked
    return {"decision": "MANUAL_REVIEW" if blocked else "AUTO_REFUND", "audit_events": 1}


def run_t06(phase: str) -> tuple[int, dict[str, Any]]:
    report = common_report("TD-T06", phase)
    oracles = load_json("fixtures/oracles.json")["test_cases"]
    mutated = phase == "fault"
    results = []
    for case in oracles:
        actual = refund_result(case["input"], mutated)
        passed = actual == case["expected"]
        results.append({"case_id": case["case_id"], "oracle_source": case["oracle_source"], "actual": actual, "expected": case["expected"], "status": "PASS" if passed else "FAIL"})
    failed = [item["case_id"] for item in results if item["status"] == "FAIL"]
    status = "FAIL" if failed else "PASS"
    report.update({"status": status, "mutation_id": "M-INVERT-ACTIVATED-GUARD" if mutated else None, "mutation_outcome": "KILLED" if mutated and failed else "NOT_APPLIED" if not mutated else "SURVIVED", "results": results, "failed_cases": failed, "decision": "REJECT_MUTATED_IMPLEMENTATION" if failed else "BASELINE_ACCEPTED"})
    return (1 if failed else 0), report


def generated_cases(seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    amounts = [1, 100, 9999]
    states = ["PAID", "ACTIVATED"]
    keys = ["idem-a", "idem-b"]
    cases = []
    for _ in range(24):
        cases.append({"amount_cents": rng.choice(amounts), "state": rng.choice(states), "idempotency_key": rng.choice(keys), "repeat": rng.choice([1, 2])})
    cases.append({"amount_cents": 1, "state": "PAID", "idempotency_key": "idem-min", "repeat": 2})
    return cases


def run_t07(phase: str) -> tuple[int, dict[str, Any]]:
    report = common_report("TD-T07", phase)
    seed = 20260811
    idempotency_broken = phase == "fault"
    failures = []
    for case in generated_cases(seed):
        refund_count = case["repeat"] if idempotency_broken else 1
        if refund_count > 1:
            failures.append({"input": case, "invariant": "refund_count<=1", "actual_refund_count": refund_count})
    minimal = None
    if failures:
        original = failures[0]["input"]
        minimal = {"idempotency_key": original["idempotency_key"], "repeat": original["repeat"]}
    status = "FAIL" if failures else "PASS"
    report.update({"status": status, "seed": seed, "method_selection": ["boundary-value", "decision-table", "property-based"], "rejected_method": {"method": "unconstrained-random-fuzz", "reason": "cannot preserve business-valid states or a stable Oracle"}, "generated_count": 25, "failure_count": len(failures), "minimal_counterexample": minimal, "replay": {"seed": seed, "system_version": "refund-fixture-v1", "reproduced": bool(failures)}, "decision": "ADD_MINIMAL_REGRESSION_AND_REJECT" if failures else "PROPERTY_HOLDS_FOR_FIXTURE"})
    return (1 if failures else 0), report


def run_t08(phase: str) -> tuple[int, dict[str, Any]]:
    report = common_report("TD-T08", phase)
    events = load_json("fixtures/failure-events.json")["events"]
    if phase == "fault":
        events = [dict(item, trace_id="", commit="mixed") for item in events]
    clusters: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        key = event["trace_id"] or "missing-trace"
        clusters.setdefault(key, []).append(event)
    output = []
    unknown = False
    for key, members in clusters.items():
        refs = [item["event_id"] for item in members]
        commits = {item["commit"] for item in members}
        environments = {item["environment"] for item in members}
        evidence_closed = key != "missing-trace" and len(refs) >= 2 and len(commits) == 1 and len(environments) == 1
        experiment = "pool-size-only-replay" if evidence_closed else "NOT_RUN"
        cause_status = "VERIFIED_CAUSE" if evidence_closed else "UNKNOWN"
        unknown = unknown or not evidence_closed
        output.append({"cluster_id": key, "raw_event_refs": refs, "symptom": "refund dependency timeout", "hypothesis": "connection pool exhaustion", "cause_status": cause_status, "next_experiment": experiment, "commit_set": sorted(commits), "environment_set": sorted(environments)})
    status = "UNKNOWN" if unknown else "PASS"
    report.update({"status": status, "clusters": output, "raw_evidence_preserved": not unknown, "decision": "ESCALATE_WITHOUT_ROOT_CAUSE" if unknown else "HAND_OFF_VERIFIED_FIXTURE_CAUSE"})
    return (2 if unknown else 0), report


RUNNERS = {"TD-T05": run_t05, "TD-T06": run_t06, "TD-T07": run_t07, "TD-T08": run_t08}


def run_topic(topic: str, phase: str, report_path: str) -> int:
    errors = verify_prompt_package(topic)
    if errors:
        report = common_report(topic, phase)
        report.update({"status": "BLOCKED", "package_errors": errors})
        write_report(report_path, report)
        print(json.dumps({"topic": topic, "phase": phase, "status": "BLOCKED", "errors": errors}, ensure_ascii=False))
        return 2
    code, report = RUNNERS[topic](phase)
    write_report(report_path, report)
    print(json.dumps({"topic": topic, "phase": phase, "status": report["status"], "report": report_path}, ensure_ascii=False))
    return code


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("verify-packages")
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--topic", choices=TOPICS, required=True)
    run_parser.add_argument("--phase", choices=("baseline", "fault", "repair"), required=True)
    run_parser.add_argument("--report", required=True)
    suite_parser = sub.add_parser("suite")
    suite_parser.add_argument("--phase", choices=("baseline", "fault", "repair"), required=True)
    args = parser.parse_args()
    if args.command == "verify-packages":
        errors = {topic: verify_prompt_package(topic) for topic in TOPICS}
        errors = {topic: items for topic, items in errors.items() if items}
        print(json.dumps({"status": "PASS" if not errors else "BLOCKED", "model_evidence": "NOT_RUN", "errors": errors}, ensure_ascii=False))
        return 0 if not errors else 2
    if args.command == "run":
        return run_topic(args.topic, args.phase, args.report)
    codes = []
    for topic in TOPICS:
        codes.append(run_topic(topic, args.phase, f"reports/{topic.lower()}-{args.phase}.json"))
    if args.phase == "fault":
        return 1 if all(code in (1, 2) for code in codes) else 2
    return 0 if all(code == 0 for code in codes) else 2


if __name__ == "__main__":
    raise SystemExit(main())
