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
INPUTS = ROOT / "inputs"
PROMPT_PACKAGE = ROOT / "prompt-package"
SCHEMAS = ROOT / "schemas"
RECEIPTS = ROOT / "receipts"
PAGE_PROMPTS = ROOT / "page-prompts"
PAGE_MANIFESTS = ROOT / "page-manifests"
DIRECT_USE_MANIFEST = ROOT / "DIRECT-USE-MANIFEST.json"
PAGE_IDS = tuple(f"TD-P0{index}" for index in range(1, 9))
PAGE_PROMPT_PACKAGE_FILES = (
    "prompt-v1.md",
    "system-v1.md",
    "task-v1.md",
    "critic-v1.md",
    "input.json",
    "schema.json",
    "eval.json",
    "mutation.json",
    "adaptation-card.md",
    "expected-output.json",
    "receipt.json",
    "manifest.json",
)

PAGE_FAILURES = {
    "TD-P01": ("SOURCE_CONFLICT", "Test Basis contains contradictory authorities"),
    "TD-P02": ("UNSUPPORTED_RULE", "Requirement Contract contains a value without source_refs"),
    "TD-P03": ("UNOWNED_BLOCKER", "Review question has no accountable owner or close_with evidence"),
    "TD-P04": ("METHOD_GAP", "Critical risk has no method, oracle, monitoring, or residual-risk owner"),
    "TD-P05": ("SELF_CONFIRMING_ORACLE", "Expected result was derived from the implementation under test"),
    "TD-P06": ("FAKE_GREEN_AUTOMATION", "Adapter swallowed an assertion or changed the approved oracle"),
    "TD-P07": ("UNATTRIBUTABLE_RUN", "Run is missing pinned input, selection, retry, or raw evidence"),
    "TD-P08": ("STALE_EVIDENCE", "Changed contract was allowed to inherit an obsolete PASS receipt"),
}


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


def validate_package(quiet: bool = False) -> tuple[int, dict]:
    required = [INPUTS / "authority-policy.json", PROMPT_PACKAGE / "manifest.json", PROMPT_PACKAGE / "system-v1.md", PROMPT_PACKAGE / "task-v1.md", PROMPT_PACKAGE / "critic-v1.md", PROMPT_PACKAGE / "eval.json", PROMPT_PACKAGE / "mutation.json", SCHEMAS / "requirement-contract.schema.json", ROOT / "DIRECT-USE-GUIDE.md", ROOT / "ADAPTATION-CARD.md", DIRECT_USE_MANIFEST]
    for page_id in PAGE_IDS:
        required.extend([
            PAGE_MANIFESTS / f"{page_id}.json",
            *(PAGE_PROMPTS / page_id / filename for filename in PAGE_PROMPT_PACKAGE_FILES),
        ])
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    result = {"status": "BLOCKED" if missing else "PASS", "missing": missing}
    if not quiet: print(json.dumps(result, ensure_ascii=False, indent=2))
    return (2 if missing else 0), result


def validate_page_package(page_id: str) -> tuple[int, dict]:
    if page_id not in PAGE_IDS:
        return 2, {"status": "BLOCKED", "issues": [f"unknown page_id {page_id}"]}
    manifest_path = PAGE_MANIFESTS / f"{page_id}.json"
    prompt_dir = PAGE_PROMPTS / page_id
    prompt_manifest_path = prompt_dir / "manifest.json"
    required = [manifest_path, *(prompt_dir / filename for filename in PAGE_PROMPT_PACKAGE_FILES)]
    issues = [f"missing {path.relative_to(ROOT)}" for path in required if not path.is_file() or path.stat().st_size == 0]
    if issues:
        return 2, {"status": "BLOCKED", "issues": issues}
    manifest = load(manifest_path)
    prompt_manifest = load(prompt_manifest_path)
    evaluation = load(prompt_dir / "eval.json")
    mutation = load(prompt_dir / "mutation.json")
    receipt = load(prompt_dir / "receipt.json")
    prompt_text = (prompt_dir / "prompt-v1.md").read_text(encoding="utf-8")
    if manifest.get("owner_page_ids") != [page_id]:
        issues.append("page manifest must declare exactly one owner_page_id")
    if prompt_manifest.get("owner_page_ids") != [page_id]:
        issues.append("prompt manifest must declare exactly one owner_page_id")
    if prompt_manifest.get("provider") != "none" or prompt_manifest.get("model_status") != "NOT_RUN":
        issues.append("offline prompt package must keep provider none and model_status NOT_RUN")
    if prompt_manifest.get("direct_use") is not True or prompt_manifest.get("copy_target") != "generic-ai-agent":
        issues.append("prompt package must declare generic AI Agent direct use")
    if len(prompt_manifest.get("editable_fields", [])) < 4:
        issues.append("direct-use prompt needs at least four editable fields")
    if len(prompt_manifest.get("expected_outputs", [])) < 3 or len(prompt_manifest.get("self_checks", [])) < 4:
        issues.append("direct-use prompt needs expected outputs and self checks")
    required_sections = (
        "## 能做什么",
        "## 使用前准备",
        "## 直接复制到 AI Agent",
        "## 修改这些字段就能复用",
        "## 预期输出",
        "## 结果自检",
        "## 停止条件与边界",
    )
    missing_sections = [section for section in required_sections if section not in prompt_text]
    if missing_sections:
        issues.append(f"direct-use prompt missing sections: {missing_sections}")
    for marker in ("[粘贴", "Evidence", "Inference", "Unknown", "BLOCKED", "source_ref", "不要编造"):
        if marker not in prompt_text:
            issues.append(f"direct-use prompt missing marker {marker}")
    assembly_files = [step.get("file") for step in prompt_manifest.get("assembly_order", [])]
    if assembly_files != ["system-v1.md", "task-v1.md", "input.json", "critic-v1.md"]:
        issues.append("prompt package assembly_order must preserve system, task, input, critic roles")
    if prompt_manifest.get("one_shot_copy_file") != "prompt-v1.md":
        issues.append("prompt package must retain prompt-v1.md as the one-shot beginner path")
    artifact_hashes = prompt_manifest.get("artifact_sha256", {})
    for filename in PAGE_PROMPT_PACKAGE_FILES:
        if filename == "manifest.json":
            continue
        expected_hash = artifact_hashes.get(filename)
        if expected_hash != digest(prompt_dir / filename):
            issues.append(f"prompt package hash drift: {filename}")
    eval_types = {item.get("case_type") for item in evaluation.get("cases", [])}
    required_eval_types = {"positive", "boundary", "conflict", "missing", "unauthorized", "refusal", "truncation", "locale"}
    if eval_types != required_eval_types or any(item.get("result") != "NOT_RUN" for item in evaluation.get("cases", [])):
        issues.append("page eval must define eight NOT_RUN case classes")
    if len(mutation.get("mutations", [])) < 6 or any(item.get("result") != "NOT_RUN" for item in mutation.get("mutations", [])):
        issues.append("page mutation set must define at least six NOT_RUN negative controls")
    if receipt.get("provider") != "none" or receipt.get("model_status") != "NOT_RUN" or receipt.get("raw_output_refs") or receipt.get("raw_output_sha256"):
        issues.append("static package receipt must preserve empty raw outputs and model NOT_RUN")
    step_ids = {step.get("step_id") for step in manifest.get("steps", [])}
    if not {"baseline", "fault", "repair", "cycle"}.issubset(step_ids):
        issues.append("page manifest must expose baseline, fault, repair, and cycle")
    return (2 if issues else 0), {"status": "BLOCKED" if issues else "PASS", "issues": issues, "page_id": page_id}


def page_phase(page_id: str, phase: str, report_path: str | None) -> int:
    package_code, package_result = validate_page_package(page_id)
    if package_code:
        print(json.dumps(package_result, ensure_ascii=False, indent=2))
        return package_code
    if phase not in {"baseline", "fault", "repair"}:
        print(json.dumps({"status": "BLOCKED", "issues": [f"unknown phase {phase}"]}, ensure_ascii=False))
        return 2
    failure_id, failure_message = PAGE_FAILURES[page_id]
    status = "FAIL" if phase == "fault" else "PASS"
    report = {
        "run_id": f"{page_id}-{phase}",
        "page_id": page_id,
        "phase": phase,
        "status": status,
        "finding_id": failure_id if phase == "fault" else None,
        "finding": failure_message if phase == "fault" else "approved fixture satisfies the page contract",
        "prompt_hash": digest(PAGE_PROMPTS / page_id / "prompt-v1.md"),
        "input_hash": digest(PAGE_PROMPTS / page_id / "input.json"),
        "evidence_status": "fixture-tested",
        "provider": "none",
        "model_status": "NOT_RUN",
        "boundary": "deterministic offline negative-control fixture; not model, practitioner, integration, live, publication, or production evidence",
    }
    target = ROOT / report_path if report_path else REPORTS / f"{page_id}-{phase}.json"
    save(target, report)
    print(json.dumps({"page_id": page_id, "phase": phase, "status": status, "report": str(target.relative_to(ROOT))}, ensure_ascii=False))
    return 1 if status == "FAIL" else 0


def page_cycle(page_id: str, report_path: str | None) -> int:
    phases = []
    for phase, expected_exit in (("baseline", 0), ("fault", 1), ("repair", 0)):
        phase_report = f"reports/{page_id}-{phase}.json"
        actual_exit = page_phase(page_id, phase, phase_report)
        report = load(ROOT / phase_report)
        phases.append({"phase": phase, "status": report["status"], "expected_exit_code": expected_exit, "actual_exit_code": actual_exit, "report": phase_report})
        if actual_exit != expected_exit:
            print(json.dumps({"status": "BLOCKED", "page_id": page_id, "phase": phase, "expected_exit": expected_exit, "actual_exit": actual_exit}, ensure_ascii=False))
            return 2
    cycle_report = {
        "run_id": f"{page_id}-cycle",
        "page_id": page_id,
        "status": "PASS",
        "phases": phases,
        "evidence_status": "fixture-tested",
        "provider": "none",
        "model_status": "NOT_RUN",
        "boundary": "0/1/0 deterministic teaching cycle only; no model/API, practitioner, integration, live, publication, or production claim",
    }
    target = ROOT / report_path if report_path else REPORTS / f"{page_id}-cycle.json"
    save(target, cycle_report)
    print(json.dumps({"status": "PASS", "page_id": page_id, "report": str(target.relative_to(ROOT))}, ensure_ascii=False))
    return 0


def validate_authority(quiet: bool = False) -> tuple[int, dict]:
    policy = load(INPUTS / "authority-policy.json")
    issues = []
    if not policy.get("owner") or not policy.get("evidence"): issues.append("authority owner/evidence missing")
    if policy.get("conflict_action") != "BLOCKED": issues.append("conflict action must be BLOCKED")
    result = {"status": "BLOCKED" if issues else "PASS", "issues": issues, "precedence": policy.get("precedence")}
    if not quiet: print(json.dumps(result, ensure_ascii=False, indent=2))
    return (2 if issues else 0), result


def validate_prompt_package(quiet: bool = False) -> tuple[int, dict]:
    manifest = load(PROMPT_PACKAGE / "manifest.json")
    evaluation = load(PROMPT_PACKAGE / "eval.json")
    mutation = load(PROMPT_PACKAGE / "mutation.json")
    issues = []
    if manifest.get("provider") != "none" or manifest.get("model") != "offline-deterministic" or manifest.get("status") != "NOT_RUN":
        issues.append("model manifest must remain explicit NOT_RUN offline")
    if len(evaluation.get("items", [])) < 8: issues.append("eval set must cover eight classes")
    if len(mutation.get("items", [])) < 3: issues.append("mutation set incomplete")
    result = {"status": "BLOCKED" if issues else "PASS", "issues": issues, "eval_cases": len(evaluation.get("items", []))}
    if not quiet: print(json.dumps(result, ensure_ascii=False, indent=2))
    return (2 if issues else 0), result


def validate_trace(quiet: bool = False) -> tuple[int, dict]:
    trace_path = ROOT / "traceability.json"
    if not trace_path.exists():
        result = {"status": "BLOCKED", "issues": ["traceability.json missing"]}
        if not quiet: print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2, result
    trace = load(trace_path)
    nodes = trace.get("links", [])
    ids = {node.get("id") for node in nodes}
    required = {"source", "claim", "risk", "method", "oracle", "case", "result"}
    issues = [f"missing {kind} node" for kind in required if not any(node.get("kind") == kind for node in nodes)]
    issues += [f"orphan {node.get('id')}" for node in nodes if node.get("kind") != "source" and any(ref not in ids for ref in node.get("refs", []))]
    result = {"status": "BLOCKED" if issues else "PASS", "issues": issues, "node_count": len(nodes)}
    if not quiet: print(json.dumps(result, ensure_ascii=False, indent=2))
    return (2 if issues else 0), result


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
    for gate in (validate_package, validate_authority, validate_prompt_package, validate_trace):
        code, result = gate(quiet=True)
        if code:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("BLOCKED: package/authority/prompt/trace gate failed")
            return 2
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
    parser.add_argument("command", choices=["reset", "validate-package", "validate-authority", "validate-prompt-package", "validate-trace", "validate-basis", "inject-doc-conflict", "validate-contract", "inject-unsupported-rule", "generate-tests", "inject-code-defect", "execute", "repair", "all", "evidence", "page-phase", "page-cycle"])
    parser.add_argument("--report")
    parser.add_argument("--page", choices=PAGE_IDS)
    parser.add_argument("--phase", choices=["baseline", "fault", "repair"])
    args = parser.parse_args()
    commands = {
        "reset": reset,
        "validate-package": lambda: validate_package()[0],
        "validate-authority": lambda: validate_authority()[0],
        "validate-prompt-package": lambda: validate_prompt_package()[0],
        "validate-trace": lambda: validate_trace()[0],
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
        "page-phase": lambda: page_phase(args.page or "", args.phase or "", args.report),
        "page-cycle": lambda: page_cycle(args.page or "", args.report),
    }
    return commands[args.command]()


if __name__ == "__main__":
    sys.exit(main())
