"""Deterministic fixture runner for the four quality-platform course pages.

This module never calls Jira, GitLab, Kubernetes, a model, or ChatOps.  It
creates reproducible offline evidence for the baseline -> fault -> repair
teaching loop and returns a non-zero exit code when an oracle fails.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

BASELINES: dict[str, dict[str, Any]] = {
    "TD-QP01": {
        "event": {"signature_valid": True, "event_id": "jira-evt-42", "duplicate_count": 1},
        "identity": {"actor": "jira-app:quality-gateway", "tenant": "acme-sandbox", "scopes": ["read:jira-work"]},
        "basis": {"issue": "PROJ-42", "revision": 7, "required_fields_present": True, "conflicts": []},
        "candidate": {"source_refs": ["jira://PROJ-42@7"], "approved_by": "reviewer:qa-lead", "auto_approved": False},
    },
    "TD-QP02": {
        "identity": {"actor": "gitlab-project-hook:17", "project_id": 17, "scopes": ["read_api", "status_check:write"]},
        "run": {"run_id": "run-42", "mr_iid": 9, "commit_sha": "a" * 40, "pipeline_id": 501},
        "gitlab": {"head_sha": "a" * 40, "pipeline_status": "success"},
        "junit": {"required_suites": ["unit", "contract"], "present_suites": ["unit", "contract"], "failed": 0, "artifact_hash_valid": True},
    },
    "TD-QP03": {
        "identity": {"provisioner": "sa:quality-provisioner", "runner": "sa:test-runner", "cleaner": "sa:quality-cleaner"},
        "environment": {"id": "env-run-42", "namespace": "quality-run-42", "owner_run": "run-42", "expires_in": 900},
        "permissions": {"cluster_admin": False, "secret_read": False, "cross_namespace": False},
        "controls": {"quota": True, "default_deny_network": True, "job_ttl": True},
        "cleanup": {"requested": True, "deleted_owned": 6, "residual_owned": 0, "audit_recorded": True},
    },
    "TD-QP04": {
        "event": {"specversion": "1.0", "source": "jira://acme/PROJ-42", "id": "evt-42", "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"},
        "delivery": {"inbox_accepts": 1, "duplicate_suppressed": 1, "outbox_attempts": 2, "dlq": 0},
        "effects": {"jira_defects": 1, "gitlab_statuses": 1, "k8s_cleanups": 1},
        "notice": {"sent": True, "contains_secret": False},
        "audit": {"reconciled": True, "rollback_ready": True},
    },
}

FAULTS = {
    "TD-QP01": ("basis.required_fields_present", False),
    "TD-QP02": ("gitlab.head_sha", "b" * 40),
    "TD-QP03": ("permissions.cluster_admin", True),
    "TD-QP04": ("effects.jira_defects", 2),
}


def _set_path(state: dict[str, Any], path: str, value: Any) -> None:
    cursor: dict[str, Any] = state
    parts = path.split(".")
    for part in parts[:-1]:
        cursor = cursor[part]
    cursor[parts[-1]] = value


def build_state(topic: str, mode: str) -> dict[str, Any]:
    state = copy.deepcopy(BASELINES[topic])
    if mode == "fault":
        _set_path(state, *FAULTS[topic])
    return state


def evaluate(topic: str, state: dict[str, Any]) -> list[dict[str, Any]]:
    if topic == "TD-QP01":
        checks = {
            "EVENT-SIGNATURE": state["event"]["signature_valid"],
            "EXACT-TENANT-IDENTITY": state["identity"]["tenant"] == "acme-sandbox",
            "LEAST-PRIVILEGE-SCOPE": state["identity"]["scopes"] == ["read:jira-work"],
            "BASIS-COMPLETE": state["basis"]["required_fields_present"] and not state["basis"]["conflicts"],
            "HUMAN-APPROVAL": bool(state["candidate"]["approved_by"]) and not state["candidate"]["auto_approved"],
        }
    elif topic == "TD-QP02":
        checks = {
            "PROJECT-IDENTITY": state["identity"]["project_id"] == 17,
            "CURRENT-SHA": state["run"]["commit_sha"] == state["gitlab"]["head_sha"],
            "PIPELINE-SUCCESS": state["gitlab"]["pipeline_status"] == "success",
            "JUNIT-COMPLETE": set(state["junit"]["required_suites"]) == set(state["junit"]["present_suites"]),
            "JUNIT-CLEAN": state["junit"]["failed"] == 0 and state["junit"]["artifact_hash_valid"],
        }
    elif topic == "TD-QP03":
        checks = {
            "IDENTITY-SEPARATION": len(set(state["identity"].values())) == 3,
            "NAMESPACE-OWNERSHIP": state["environment"]["namespace"] != "default" and bool(state["environment"]["owner_run"]),
            "LEAST-PRIVILEGE": not any(state["permissions"].values()),
            "RESOURCE-AND-NETWORK-CONTROLS": all(state["controls"].values()),
            "CLEANUP-CLOSED": state["cleanup"]["residual_owned"] == 0 and state["cleanup"]["audit_recorded"],
        }
    else:
        event = state["event"]
        checks = {
            "EVENT-IDENTITY": event["specversion"] == "1.0" and bool(event["source"]) and bool(event["id"]),
            "TRACE-CONTEXT": event["traceparent"].startswith("00-"),
            "IDEMPOTENT-INBOX": state["delivery"]["inbox_accepts"] == 1 and state["delivery"]["duplicate_suppressed"] == 1,
            "EXACTLY-ONCE-EFFECT": state["effects"] == {"jira_defects": 1, "gitlab_statuses": 1, "k8s_cleanups": 1},
            "AUDIT-ROLLBACK": state["audit"]["reconciled"] and state["audit"]["rollback_ready"] and not state["notice"]["contains_secret"],
        }
    return [{"oracle_id": key, "passed": bool(value)} for key, value in checks.items()]


def make_report(topic: str, mode: str) -> dict[str, Any]:
    state = build_state(topic, mode)
    checks = evaluate(topic, state)
    failures = [item["oracle_id"] for item in checks if not item["passed"]]
    canonical = json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "topic_id": topic,
        "mode": mode,
        "maturity": "fixture-tested",
        "verdict": "PASS" if not failures else "FAIL",
        "expected_exit_code": 0 if not failures else 1,
        "failed_oracle_ids": failures,
        "evidence_hash": hashlib.sha256(canonical.encode()).hexdigest(),
        "checks": checks,
        "state": state,
        "not_run": ["live Jira tenant", "live GitLab instance", "live Kubernetes cluster", "model provider", "ChatOps delivery"],
    }


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(topic: str) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["baseline", "fault", "repair", "cycle"])
    parser.add_argument("--report")
    parser.add_argument("--report-dir")
    args = parser.parse_args()
    if args.mode == "cycle":
        if not args.report_dir:
            parser.error("cycle requires --report-dir")
        target = ROOT / args.report_dir
        observed = []
        for mode in ("baseline", "fault", "repair"):
            report = make_report(topic, mode)
            write_report(target / f"{mode}.json", report)
            observed.append(report["expected_exit_code"])
        summary = {"topic_id": topic, "sequence": ["baseline", "fault", "repair"], "observed_exit_codes": observed, "expected_exit_codes": [0, 1, 0], "verdict": "PASS" if observed == [0, 1, 0] else "FAIL", "maturity": "fixture-tested"}
        write_report(target / "cycle-summary.json", summary)
        print(json.dumps(summary, ensure_ascii=False))
        return 0 if summary["verdict"] == "PASS" else 1
    if not args.report:
        parser.error("single mode requires --report")
    report = make_report(topic, args.mode)
    write_report(ROOT / args.report, report)
    print(json.dumps({"topic_id": topic, "mode": args.mode, "verdict": report["verdict"], "failed_oracle_ids": report["failed_oracle_ids"]}, ensure_ascii=False))
    return report["expected_exit_code"]
