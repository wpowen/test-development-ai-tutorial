#!/usr/bin/env python3
"""Fail-closed validator for the user-facing model output contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOWED_STATES = {
    "INSUFFICIENT-EVIDENCE",
    "HIGH-RISK-PAUSE",
    "INCONSISTENCY-DETECTED",
    "PROVISIONALLY-CONSISTENT-VERIFY-OUTSIDE-APP",
    "OFFICIAL-CHANNEL-CONFIRMED",
}
REQUIRED = {
    "schema_version",
    "case_id",
    "privacy_gate",
    "input_completeness",
    "observations",
    "identity_continuity",
    "group_history",
    "payment_consistency",
    "missing_evidence",
    "conflicts",
    "decision_state",
    "next_actions",
    "risk_notice",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    missing = sorted(REQUIRED - set(data))
    if missing:
        findings.append(f"missing top-level fields: {missing}")
    state = data.get("decision_state")
    if state not in ALLOWED_STATES:
        findings.append("decision_state is not allowed")
    provided = set(data.get("input_completeness", {}).get("provided", []))
    if state == "OFFICIAL-CHANNEL-CONFIRMED" and "F" not in provided:
        findings.append("OFFICIAL-CHANNEL-CONFIRMED requires provided F evidence")
    conflicts = data.get("conflicts", [])
    if conflicts and state in {"PROVISIONALLY-CONSISTENT-VERIFY-OUTSIDE-APP", "OFFICIAL-CHANNEL-CONFIRMED"}:
        findings.append("unresolved conflicts cannot produce a consistent or confirmed state")
    if data.get("privacy_gate") == "FAIL-REDACTION" and state != "HIGH-RISK-PAUSE":
        findings.append("failed redaction must force HIGH-RISK-PAUSE")
    if not isinstance(data.get("next_actions"), list) or not data.get("next_actions"):
        findings.append("next_actions must be non-empty")
    notice = str(data.get("risk_notice", ""))
    for phrase in ("不能访问微信后台", "学校群外官方确认前不要付款"):
        if phrase not in notice:
            findings.append(f"risk_notice missing phrase: {phrase}")
    serialized = json.dumps(data, ensure_ascii=False)
    for forbidden in ("身份置信度", "诈骗概率", "可以付款", "确认此人就是老师"):
        if forbidden in serialized:
            findings.append(f"forbidden output phrase: {forbidden}")
    group = data.get("group_history", {})
    if group.get("status") == "UNKNOWN" and not group.get("boundary"):
        findings.append("UNKNOWN group history requires a boundary")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    data = json.loads(args.output.read_text(encoding="utf-8"))
    findings = validate(data)
    status = "PASS-CONTRACT" if not findings else "FAIL-CONTRACT"
    receipt = {
        "schema_version": "parent-group-fee-output-validation.v2",
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "input_path": str(args.output),
        "input_sha256": sha256(args.output),
        "status": status,
        "findings": findings,
        "limitations": [
            "Validates structure and fail-closed invariants only",
            "Does not prove OCR accuracy, identity, fraud status, learner success, or loss prevention",
        ],
    }
    if args.receipt:
        args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
