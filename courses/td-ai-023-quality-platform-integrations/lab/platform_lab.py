"""Offline Jira -> GitLab -> K8s -> evidence -> notification simulator."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
from pathlib import Path

import oracle

ROOT = Path(__file__).resolve().parent
SECRET = b"fixture-webhook-secret"
GOOD_SHA = "a" * 40
OLD_SHA = "b" * 40


def signed(body: bytes) -> str:
    return hmac.new(SECRET, body, hashlib.sha256).hexdigest()


def build_state(mutation: str | None = None) -> dict:
    event = {"id": "jira-evt-42", "type": "quality.requirement.changed", "issue": "PROJ-42", "sha": GOOD_SHA}
    body = json.dumps(event, sort_keys=True).encode()
    state = {
        "webhook": {"verified": hmac.compare_digest(signed(body), signed(body)), "event_id": event["id"]},
        "inbox": {"accepted": 1, "duplicates": 1, "keys": ["jira:PROJ-42:jira-evt-42"]},
        "candidate": {"status": "approved", "auto_approved": False, "model": "offline-rule-candidate-v1", "prompt_hash": "sha256:fixture"},
        "run": {"run_id": "run-42", "commit_sha": GOOD_SHA, "pipeline_id": 9001},
        "gitlab": {"head_sha": GOOD_SHA, "pipeline_status": "success"},
        "junit": {"present": True, "total": 3, "passed": 3, "failed": 0, "artifact_sha256": "junit-sha-42"},
        "k8s": {"namespace": "quality-run-42", "roles": ["namespace-job-runner"], "ttl_seconds": 900, "owner_run_id": "run-42"},
        "writeback": {"jira_updates": 1, "gitlab_statuses": 1, "fingerprint": "fp-42"},
        "notification": {"body": "PROJ-42 MR !7 sha aaaaaaaa result PASS failures=0 artifact=artifact://junit/run-42"},
        "audit": {"previous_hash": "genesis", "event": "gate:PASS:run-42", "append_only": True},
    }
    state["audit"]["hash"] = hashlib.sha256((state["audit"]["previous_hash"] + state["audit"]["event"]).encode()).hexdigest()
    if mutation == "stale_sha":
        state["run"]["commit_sha"] = OLD_SHA
    elif mutation == "replay":
        state["inbox"]["accepted"] = 2
    elif mutation == "rbac":
        state["k8s"]["roles"].append("cluster-admin")
    elif mutation == "missing_report":
        state["junit"]["present"] = False
    return state


def run(mode: str, report_name: str) -> int:
    mutation = None if mode in {"baseline", "repair", "all"} else mode
    state = build_state(mutation)
    result = oracle.report(state, mutation_id=f"MUT-{mutation}" if mutation else None)
    result.update({"course_id": "td-ai-023-quality-platform-integrations", "mode": mode, "state": state})
    path = ROOT / "reports" / report_name
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(path), "verdict": result["verdict"], "failed_oracle_ids": result["failed_oracle_ids"]}, ensure_ascii=False))
    return result["exit_code"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["baseline", "stale_sha", "replay", "rbac", "missing_report", "repair", "all"])
    parser.add_argument("--report", default=None)
    args = parser.parse_args()
    name = args.report or {"baseline": "baseline.json", "repair": "repair.json", "all": "baseline.json"}.get(args.mode, "mutation.json")
    return run(args.mode, name)


if __name__ == "__main__":
    raise SystemExit(main())
