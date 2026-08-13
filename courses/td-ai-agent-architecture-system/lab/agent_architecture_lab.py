#!/usr/bin/env python3
"""Deterministic D0-D7 Agent architecture fixture; no model or network calls."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOPICS = tuple(f"TD-AG-{i:02d}" for i in range(11))

BASE: dict[str, dict[str, Any]] = {
    "TD-AG-00": {"boundary": {"inputs": True, "domains": 8, "rings": 4, "guards": True, "owners": True, "oracles": True}},
    "TD-AG-01": {"judge": {"gold": True, "human_labels": True, "order_ab": "A", "order_ba": "A", "fact_blocker": True, "card": True}},
    "TD-AG-02": {"trace": {"outcome": True, "prohibited_calls": 0, "authorized": True, "complete": True, "first_error": None}},
    "TD-AG-03": {"orchestration": {"handoff_schema": True, "facts_survive": 5, "isolation": True, "step_limit": 5, "time_limit": True, "cost_limit": True, "stop_reason": "downstream_error"}},
    "TD-AG-04": {"human": {"interrupt_step": 2, "dirty_state": False, "rollback": True, "takeover": True, "approval": True, "owner": True}},
    "TD-AG-05": {"reliability": {"tasks": 12, "runs": 5, "pass_at_k": 0.83, "pass_all_k": 0.75, "clustered_ci": True, "horizon_buckets": True, "sample_reason": True}},
    "TD-AG-06": {"security": {"attack_cases": 8, "manifest_hash": True, "tenant_isolation": True, "min_scope": True, "sandbox": True, "no_side_effect": True, "blast_radius": True, "owner": True}},
    "TD-AG-07": {"economics": {"task_trace": True, "p95": True, "p99": True, "goodput": True, "cost_tail": True, "hard_budget": True, "resource_isolation": True}},
    "TD-AG-08": {"governance": {"business_rules": True, "audit_chain": True, "model_version": True, "prompt_version": True, "tool_version": True, "memory_version": True, "human_owner": True, "rollback": True}},
    "TD-AG-09": {"rings": {"offline": True, "sandbox": True, "shadow": "NOT_RUN", "online": "NOT_RUN", "hard_redline": True, "statistical_gate": True, "risk_acceptance": True, "receipt_maturity": True}},
    "TD-AG-10": {"high_risk": {"timestamp": True, "advice_execution_split": True, "capability_sandbox": True, "hard_limit": True, "dual_approval": True, "kill_switch": True, "no_real_funds": True}},
}


def state(topic: str, phase: str) -> dict[str, Any]:
    value = copy.deepcopy(BASE[topic])
    if phase != "fault":
        return value
    fault_map = {
        "TD-AG-00": ("boundary", "oracles", False),
        "TD-AG-01": ("judge", "order_ba", "B"),
        "TD-AG-02": ("trace", "prohibited_calls", 1),
        "TD-AG-03": ("orchestration", "stop_reason", None),
        "TD-AG-04": ("human", "rollback", False),
        "TD-AG-05": ("reliability", "clustered_ci", False),
        "TD-AG-06": ("security", "tenant_isolation", False),
        "TD-AG-07": ("economics", "hard_budget", False),
        "TD-AG-08": ("governance", "tool_version", False),
        "TD-AG-09": ("rings", "hard_redline", False),
        "TD-AG-10": ("high_risk", "hard_limit", False),
    }
    section, key, bad = fault_map[topic]
    value[section][key] = bad
    return value


def checks(topic: str, value: dict[str, Any]) -> dict[str, bool]:
    if topic == "TD-AG-00":
        x = value["boundary"]; return {"INPUTS": x["inputs"], "D0-D7": x["domains"] == 8, "FOUR-RINGS": x["rings"] == 4, "GUARDS": x["guards"], "OWNER-ORACLE": x["owners"] and x["oracles"]}
    if topic == "TD-AG-01":
        x = value["judge"]; return {"GOLD": x["gold"], "HUMAN-LABELS": x["human_labels"], "ORDER-STABLE": x["order_ab"] == x["order_ba"], "FACT-BLOCKER": x["fact_blocker"], "JUDGE-CARD": x["card"]}
    if topic == "TD-AG-02":
        x = value["trace"]; return {"OUTCOME": x["outcome"], "STEP-SAFETY": x["prohibited_calls"] == 0 and x["authorized"], "TRACE-COMPLETE": x["complete"], "FIRST-ERROR": x["first_error"] is None}
    if topic == "TD-AG-03":
        x = value["orchestration"]; return {"HANDOFF": x["handoff_schema"], "FACT-SURVIVAL": x["facts_survive"] >= 5, "ISOLATION": x["isolation"], "TRIPLE-BUDGET": x["step_limit"] > 0 and x["time_limit"] and x["cost_limit"], "STOP-REASON": bool(x["stop_reason"])}
    if topic == "TD-AG-04":
        x = value["human"]; return {"INTERRUPT": x["interrupt_step"] > 0, "NO-DIRTY-STATE": not x["dirty_state"], "ROLLBACK": x["rollback"], "TAKEOVER": x["takeover"], "APPROVAL-OWNER": x["approval"] and x["owner"]}
    if topic == "TD-AG-05":
        x = value["reliability"]; return {"TASKS": x["tasks"] > 0, "REPEATS": x["runs"] >= 3, "PASS-K-SEPARATE": x["pass_at_k"] >= x["pass_all_k"], "CLUSTERED-CI": x["clustered_ci"], "HORIZON": x["horizon_buckets"], "SAMPLE-REASON": x["sample_reason"]}
    if topic == "TD-AG-06":
        x = value["security"]; return {"ATTACK-CASES": x["attack_cases"] > 0, "MANIFEST": x["manifest_hash"], "TENANT": x["tenant_isolation"], "SCOPE": x["min_scope"], "SANDBOX": x["sandbox"], "NO-SIDE-EFFECT": x["no_side_effect"], "BLAST-RADIUS": x["blast_radius"] and x["owner"]}
    if topic == "TD-AG-07":
        x = value["economics"]; return {"TASK-TRACE": x["task_trace"], "TAILS": x["p95"] and x["p99"], "GOODPUT": x["goodput"], "COST-TAIL": x["cost_tail"], "HARD-BUDGET": x["hard_budget"], "RESOURCE-ISOLATION": x["resource_isolation"]}
    if topic == "TD-AG-08":
        x = value["governance"]; return {"BUSINESS-RULES": x["business_rules"], "AUDIT": x["audit_chain"], "FOUR-VERSION": x["model_version"] and x["prompt_version"] and x["tool_version"] and x["memory_version"], "OWNER": x["human_owner"], "ROLLBACK": x["rollback"]}
    if topic == "TD-AG-09":
        x = value["rings"]; return {"OFFLINE": x["offline"], "SANDBOX": x["sandbox"], "UNRUN-BOUNDARY": x["shadow"] == "NOT_RUN" and x["online"] == "NOT_RUN", "HARD-REDLINE": x["hard_redline"], "STATISTICAL": x["statistical_gate"], "RISK-ACCEPTANCE": x["risk_acceptance"], "RECEIPT": x["receipt_maturity"]}
    x = value["high_risk"]; return {"TIMESTAMP": x["timestamp"], "ADVICE-EXECUTION": x["advice_execution_split"], "SANDBOX": x["capability_sandbox"], "HARD-LIMIT": x["hard_limit"], "DUAL-APPROVAL": x["dual_approval"], "KILL-SWITCH": x["kill_switch"], "NO-REAL-FUNDS": x["no_real_funds"]}


def report(topic: str, phase: str) -> dict[str, Any]:
    value = state(topic, phase)
    checks_result = [{"oracle_id": key, "passed": bool(passed)} for key, passed in checks(topic, value).items()]
    failed = [item["oracle_id"] for item in checks_result if not item["passed"]]
    return {"topic_id": topic, "phase": phase, "maturity": "fixture-tested", "verdict": "PASS" if not failed else "FAIL", "expected_exit_code": 0 if not failed else 1, "failed_oracle_ids": failed, "state_hash": hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest(), "checks": checks_result, "state": value, "not_run": ["live model", "live agent", "live tools", "live shadow", "online monitoring", "practitioner review", "learner transfer"]}


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", choices=TOPICS, required=True)
    parser.add_argument("--phase", choices=["baseline", "fault", "repair", "cycle"], required=True)
    parser.add_argument("--report")
    parser.add_argument("--report-dir")
    args = parser.parse_args()
    if args.phase == "cycle":
        if not args.report_dir:
            parser.error("cycle requires --report-dir")
        target = ROOT / args.report_dir
        observed = []
        for phase in ("baseline", "fault", "repair"):
            item = report(args.topic, phase)
            write(target / f"{phase}.json", item)
            observed.append(item["expected_exit_code"])
        summary = {"topic_id": args.topic, "observed_exit_codes": observed, "expected_exit_codes": [0, 1, 0], "verdict": "PASS" if observed == [0, 1, 0] else "FAIL", "maturity": "fixture-tested", "model_evidence": "NOT_RUN"}
        write(target / "cycle-summary.json", summary)
        print(json.dumps(summary, ensure_ascii=False))
        return 0 if summary["verdict"] == "PASS" else 1
    if not args.report:
        parser.error("single phase requires --report")
    item = report(args.topic, args.phase)
    write(ROOT / args.report, item)
    print(json.dumps({"topic_id": args.topic, "phase": args.phase, "verdict": item["verdict"], "failed": item["failed_oracle_ids"]}, ensure_ascii=False))
    return item["expected_exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
