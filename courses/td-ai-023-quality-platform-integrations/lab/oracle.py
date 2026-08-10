"""Independent, deterministic Oracle for the quality control-plane fixture."""
from __future__ import annotations

import hashlib


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def evaluate(state: dict) -> list[dict]:
    checks = []
    checks.append(("WEBHOOK-SIGNATURE", state["webhook"]["verified"], "signed webhook accepted"))
    checks.append(("INBOX-DEDUPE", state["inbox"]["accepted"] == 1 and state["inbox"]["duplicates"] == 1, "one side effect for replay"))
    checks.append(("AI-HUMAN-BOUNDARY", state["candidate"]["status"] == "approved" and not state["candidate"]["auto_approved"], "candidate has human approval"))
    checks.append(("SHA-BINDING", state["run"]["commit_sha"] == state["gitlab"]["head_sha"], "evidence belongs to current HEAD"))
    checks.append(("JUNIT-COMPLETE", state["junit"]["present"] and state["junit"]["failed"] == 0, "required report is present and green"))
    checks.append(("K8S-BOUNDARY", state["k8s"]["namespace"] != "default" and "cluster-admin" not in state["k8s"]["roles"] and state["k8s"]["ttl_seconds"] > 0, "isolated namespace and least privilege"))
    checks.append(("WRITEBACK-IDEMPOTENCY", state["writeback"]["jira_updates"] == 1 and state["writeback"]["gitlab_statuses"] == 1, "one Jira and one current-SHA status write"))
    checks.append(("NOTIFICATION-REDACTION", "token" not in state["notification"]["body"].lower() and "secret" not in state["notification"]["body"].lower(), "notification contains no credentials"))
    expected_ledger = _sha(state["audit"]["previous_hash"] + state["audit"]["event"])
    checks.append(("AUDIT-CHAIN", state["audit"]["hash"] == expected_ledger and state["audit"]["append_only"], "audit hash is chained"))
    return [{"oracle_id": oid, "passed": bool(ok), "reason": reason} for oid, ok, reason in checks]


def report(state: dict, mutation_id: str | None = None) -> dict:
    checks = evaluate(state)
    failed = [item["oracle_id"] for item in checks if not item["passed"]]
    return {"verdict": "PASS" if not failed else "FAIL", "exit_code": 0 if not failed else 1,
            "mutation_id": mutation_id, "failed_oracle_ids": failed, "checks": checks,
            "input_hash": _sha(str(sorted(state.items()))), "oracle_version": "oracle-v1"}
