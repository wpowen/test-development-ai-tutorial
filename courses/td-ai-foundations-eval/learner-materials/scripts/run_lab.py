#!/usr/bin/env python3
"""Deterministic AI-quality contract lab; it never calls a model or network."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "configs" / "topic-contracts.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--phase", choices=("baseline", "fault", "repair"), required=True)
    args = parser.parse_args()

    contracts = json.loads(CONTRACTS.read_text(encoding="utf-8"))
    if args.topic not in contracts:
        raise SystemExit(f"unknown topic: {args.topic}")
    contract = contracts[args.topic]
    observations = dict(contract["baseline_observations"])
    injected = None
    if args.phase == "fault":
        injected = contract["mutation"]
        observations[injected["field"]] = injected["fault_value"]

    checks = []
    for field, expected in contract["expected"].items():
        actual = observations.get(field)
        checks.append({
            "field": field,
            "expected": expected,
            "actual": actual,
            "status": "PASS" if actual == expected else "FAIL",
        })
    verdict = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    report = {
        "schema_version": "1.0.0",
        "topic_id": args.topic,
        "phase": args.phase,
        "evidence_level": "offline-deterministic-fixture",
        "model_execution": "NOT_RUN",
        "verdict": verdict,
        "decision": contract["decision"],
        "checks": checks,
        "injected_mutation": injected,
        "remaining_unknowns": contract["remaining_unknowns"],
    }
    target = ROOT / "reports" / args.topic / f"{args.phase}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"topic_id": args.topic, "phase": args.phase, "verdict": verdict, "report": str(target.relative_to(ROOT))}, ensure_ascii=False))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
