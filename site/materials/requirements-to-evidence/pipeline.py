#!/usr/bin/env python3
"""Deterministic requirements-to-evidence teaching fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = ROOT / "seed"
STATE = ROOT / "state"
ARTIFACTS = ROOT / "artifacts"
REPORTS = ROOT / "reports"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reset() -> int:
    if STATE.exists():
        shutil.rmtree(STATE)
    if ARTIFACTS.exists():
        shutil.rmtree(ARTIFACTS)
    shutil.copytree(SEED, STATE)
    REPORTS.mkdir(exist_ok=True)
    print("PASS reset: approved document baseline and healthy implementation restored")
    return 0


def require_state():
    if not STATE.exists():
        reset()


def validate_basis(quiet: bool = False) -> tuple[int, dict]:
    require_state()
    basis = load(STATE / "basis.json")
    conflicts = basis.get("conflicts", [])
    missing = [key for key in ["baseline_id", "sources", "precedence_rule"] if not basis.get(key)]
    if conflicts or missing:
        result = {"status": "BLOCKED", "missing": missing, "conflicts": conflicts}
        if not quiet:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2, result
    result = {"status": "PASS", "baseline_id": basis["baseline_id"], "source_count": len(basis["sources"])}
    if not quiet:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0, result


def validate_contract(quiet: bool = False) -> tuple[int, dict]:
    require_state()
    contract = load(STATE / "requirement-contract.json")
    issues = []
    known_refs = {ref for source in load(STATE / "basis.json")["sources"] for ref in source["refs"]}
    for req in contract["requirements"]:
        if req["status"] not in {"ACCEPTED", "UNKNOWN", "BLOCKED"}:
            issues.append(f'{req["requirement_id"]}: invalid status')
        for ref in req.get("source_refs", []):
            if ref not in known_refs:
                issues.append(f'{req["requirement_id"]}: unknown source_ref {ref}')
        if req["status"] == "ACCEPTED" and not req.get("source_refs"):
            issues.append(f'{req["requirement_id"]}: accepted rule has no source_ref')
    for field in contract.get("unsupported_fields", []):
        issues.append(f'{field["requirement_id"]}: {field["field"]} has no source')
    status = "BLOCKED" if issues else "PASS"
    result = {"status": status, "issues": issues, "requirement_count": len(contract["requirements"])}
    if not quiet:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return (2 if issues else 0), result


def inject_doc_conflict() -> int:
    require_state()
    basis = load(STATE / "basis.json")
    basis["conflicts"] = [{
        "conflict_id": "CONFLICT-SHIPPED-CANCEL",
        "source_refs": ["PRD-v3#R17", "TECH-a13f#S04"],
        "question": "SHIPPED orders: reject or allow cancellation?",
        "owner_needed": "product-owner-order",
    }]
    save(STATE / "basis.json", basis)
    print("BLOCKED fixture injected: PRD and old technical design disagree")
    return 0


def inject_unsupported_rule() -> int:
    require_state()
    contract = load(STATE / "requirement-contract.json")
    contract["unsupported_fields"] = [{
        "requirement_id": "REQ-CANCEL-001",
        "field": "refund_timeout_hours",
        "value": 24,
    }]
    save(STATE / "requirement-contract.json", contract)
    print("Unsupported rule injected: refund_timeout_hours=24 has no source")
    return 0


def generate_tests() -> int:
    basis_code, _ = validate_basis(quiet=True)
    contract_code, _ = validate_contract(quiet=True)
    if basis_code or contract_code:
        print("BLOCKED: tests were not generated because upstream evidence failed")
        return 2
    tests = {
        "schema_version": "test-package.v1",
        "tests": [
            {
                "test_id": "T-CANCEL-SHIPPED-01",
                "requirement_ids": ["REQ-CANCEL-002"],
                "risk_ids": ["RISK-INVALID-STATE"],
                "fixture": {"owner": True, "state": "SHIPPED", "captured_amount": 10000},
                "expected": {"status_code": 409, "refund_count": 0, "state": "SHIPPED"},
                "source_refs": ["PRD-v3#R17", "OPENAPI-v7#/cancel/responses/409"],
            },
            {
                "test_id": "T-CANCEL-IDEMPOTENT-01",
                "requirement_ids": ["REQ-CANCEL-001"],
                "risk_ids": ["RISK-REFUND-DUPLICATE"],
                "fixture": {"owner": True, "state": "PAID_NOT_SHIPPED", "captured_amount": 10000, "repeat": 2},
                "expected": {"status_code": 202, "refund_count": 1, "state": "CANCEL_PENDING"},
                "source_refs": ["PRD-v3#R18", "OPENAPI-v7#/cancel"],
            },
            {
                "test_id": "T-CANCEL-AUTH-01",
                "requirement_ids": ["REQ-CANCEL-003"],
                "risk_ids": ["RISK-UNAUTHORIZED-CANCEL"],
                "fixture": {"owner": False, "state": "PAID_NOT_SHIPPED", "captured_amount": 10000},
                "expected": {"status_code": 403, "refund_count": 0, "state": "PAID_NOT_SHIPPED"},
                "source_refs": ["PRD-v3#R19", "OPENAPI-v7#/cancel/responses/403"],
            },
        ],
    }
    save(ARTIFACTS / "test-package.json", tests)
    print(f'PASS generated {len(tests["tests"])} evidence-bound tests')
    return 0


def service_cancel(fixture: dict, implementation: dict) -> dict:
    state = fixture["state"]
    if not fixture["owner"]:
        return {"status_code": 403, "refund_count": 0, "state": state}
    if state == "SHIPPED" and not implementation["allow_shipped_cancel"]:
        return {"status_code": 409, "refund_count": 0, "state": state}
    repeat = fixture.get("repeat", 1)
    refund_count = repeat if implementation["idempotency_broken"] else 1
    return {"status_code": 202, "refund_count": refund_count, "state": "CANCEL_PENDING"}


def execute(report_path: str | None = None) -> int:
    if not (ARTIFACTS / "test-package.json").exists():
        code = generate_tests()
        if code:
            return code
    implementation = load(STATE / "implementation.json")
    package = load(ARTIFACTS / "test-package.json")
    results = []
    for test in package["tests"]:
        actual = service_cancel(test["fixture"], implementation)
        mismatches = {key: {"expected": value, "actual": actual.get(key)} for key, value in test["expected"].items() if actual.get(key) != value}
        results.append({
            "test_id": test["test_id"],
            "requirement_ids": test["requirement_ids"],
            "risk_ids": test["risk_ids"],
            "status": "FAIL" if mismatches else "PASS",
            "mismatches": mismatches,
            "evidence": {"actual": actual, "source_refs": test["source_refs"], "mutation_id": implementation.get("mutation_id")},
        })
    failed = [item for item in results if item["status"] == "FAIL"]
    report = {
        "run_id": datetime.now(timezone.utc).strftime("RUN-%Y%m%dT%H%M%SZ"),
        "status": "FAIL" if failed else "PASS",
        "evidence_status": "fixture-tested",
        "baseline_id": load(STATE / "basis.json")["baseline_id"],
        "input_hashes": {
            "basis": digest(STATE / "basis.json"),
            "contract": digest(STATE / "requirement-contract.json"),
            "test_package": digest(ARTIFACTS / "test-package.json"),
            "implementation": digest(STATE / "implementation.json"),
        },
        "selected_test_ids": [item["test_id"] for item in results],
        "skipped": [],
        "retries": 0,
        "results": results,
        "boundary": "synthetic offline fixture; not production validated; human release decision required",
    }
    target = Path(report_path) if report_path else REPORTS / "latest.json"
    if not target.is_absolute():
        target = ROOT / target
    save(target, report)
    print(json.dumps({"status": report["status"], "failed": [item["test_id"] for item in failed], "report": str(target)}, ensure_ascii=False))
    return 1 if failed else 0


def inject_code_defect() -> int:
    require_state()
    implementation = load(STATE / "implementation.json")
    implementation.update({"allow_shipped_cancel": True, "mutation_id": "MUT-ALLOW-SHIPPED-CANCEL"})
    save(STATE / "implementation.json", implementation)
    print("Mutation injected: SHIPPED cancellation incorrectly returns 202")
    return 0


def repair() -> int:
    require_state()
    implementation = load(STATE / "implementation.json")
    implementation.update({"allow_shipped_cancel": False, "idempotency_broken": False, "mutation_id": None})
    save(STATE / "implementation.json", implementation)
    print("PASS repair: shipped cancellation and idempotency rules restored")
    return 0


def run_all(report_path: str | None) -> int:
    basis_code, basis = validate_basis(quiet=True)
    if basis_code:
        print(json.dumps(basis, ensure_ascii=False, indent=2))
        print("BLOCKED: no downstream artifacts were generated")
        return 2
    contract_code, contract = validate_contract(quiet=True)
    if contract_code:
        print(json.dumps(contract, ensure_ascii=False, indent=2))
        print("BLOCKED: no downstream artifacts were generated")
        return 2
    generated = generate_tests()
    return generated or execute(report_path)


def evidence() -> int:
    available = sorted(REPORTS.glob("*.json"))
    evidence_pack = {
        "status": "RELEASE_CANDIDATE" if available else "BLOCKED",
        "reports": [{"path": str(path.relative_to(ROOT)), "sha256": digest(path), "run_status": load(path)["status"]} for path in available],
        "decision_owner": "named release owner",
        "boundary": "synthetic offline fixture; not production validated; human release decision required",
    }
    save(ARTIFACTS / "evidence-pack.json", evidence_pack)
    print(json.dumps(evidence_pack, ensure_ascii=False, indent=2))
    return 0 if available else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["reset", "validate-basis", "inject-doc-conflict", "validate-contract", "inject-unsupported-rule", "generate-tests", "inject-code-defect", "execute", "repair", "all", "evidence"])
    parser.add_argument("--report")
    args = parser.parse_args()
    commands = {
        "reset": reset,
        "validate-basis": lambda: validate_basis()[0],
        "inject-doc-conflict": inject_doc_conflict,
        "validate-contract": lambda: validate_contract()[0],
        "inject-unsupported-rule": inject_unsupported_rule,
        "generate-tests": generate_tests,
        "inject-code-defect": inject_code_defect,
        "execute": lambda: execute(args.report),
        "repair": repair,
        "all": lambda: run_all(args.report),
        "evidence": evidence,
    }
    return commands[args.command]()


if __name__ == "__main__":
    sys.exit(main())
