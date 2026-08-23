#!/usr/bin/env python3
"""In-memory regression tests for fail-closed model output validation."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from validate_model_output import validate


ROOT = Path(__file__).resolve().parent
BASE = json.loads((ROOT / "SAMPLE-MODEL-OUTPUT.json").read_text(encoding="utf-8"))


def expect_pass(name: str, data: dict) -> None:
    findings = validate(data)
    if findings:
        raise AssertionError(f"{name}: expected pass, got {findings}")
    print(f"PASS positive: {name}")


def expect_block(name: str, data: dict, expected: str) -> None:
    findings = validate(data)
    joined = "\n".join(findings)
    if expected not in joined:
        raise AssertionError(f"{name}: expected {expected!r}, got {joined!r}")
    print(f"PASS negative: {name}")


def main() -> int:
    expect_pass("sample output", BASE)

    no_f_confirmed = copy.deepcopy(BASE)
    no_f_confirmed["decision_state"] = "OFFICIAL-CHANNEL-CONFIRMED"
    no_f_confirmed["conflicts"] = []
    expect_block("F required for confirmation", no_f_confirmed, "requires provided F evidence")

    bad_privacy = copy.deepcopy(BASE)
    bad_privacy["privacy_gate"] = "FAIL-REDACTION"
    expect_block("redaction failure pauses", bad_privacy, "must force HIGH-RISK-PAUSE")

    conflict_but_consistent = copy.deepcopy(BASE)
    conflict_but_consistent["decision_state"] = "PROVISIONALLY-CONSISTENT-VERIFY-OUTSIDE-APP"
    expect_block("conflicts block consistent state", conflict_but_consistent, "unresolved conflicts")

    payment_advice = copy.deepcopy(BASE)
    payment_advice["next_actions"] = ["可以付款"]
    expect_block("payment advice rejected", payment_advice, "forbidden output phrase")

    missing_notice = copy.deepcopy(BASE)
    missing_notice["risk_notice"] = "结果仅供参考"
    expect_block("risk notice required", missing_notice, "risk_notice missing phrase")

    print("ALL OUTPUT CONTRACT TESTS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
