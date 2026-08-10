#!/usr/bin/env python3
"""Offline API automation course lab: spec candidates, independent Oracle, and mutation proof."""
from __future__ import annotations
import argparse, hashlib, json, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
from oracle import check_case

ROOT = Path(__file__).resolve().parent
SEED, STATE, REPORTS = ROOT / "seed", ROOT / "state", ROOT / "reports"

def load(p): return json.loads(p.read_text(encoding="utf-8"))
def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def reset():
    if STATE.exists(): shutil.rmtree(STATE)
    if REPORTS.exists():
        for p in REPORTS.glob("*.json"): p.unlink()
    STATE.mkdir(parents=True)
    save(STATE / "implementation.json", {"allow_shipped_cancel": False, "duplicate_side_effect": False, "mutation_id": None})
    print("PASS reset: healthy order API fixture restored")
    return 0

def ensure_state():
    if not STATE.exists(): reset()

def generate_candidates():
    spec = load(SEED / "openapi.json")
    cases = []
    for path, methods in spec["paths"].items():
        for method, operation in methods.items():
            cases.append({"case_id": f"SPEC-{operation['operationId']}-shape", "operation_id": operation["operationId"], "method": method.upper(), "path": path, "kind": "contract"})
    cases += [
      {"case_id":"BUS-SHIPPED-REJECT", "operation_id":"cancelOrder", "kind":"business", "fixture":{"owner":True,"state":"SHIPPED","repeat":1}, "expected":{"status":409,"refund_count":0,"state":"SHIPPED"}},
      {"case_id":"AUTH-NONOWNER-REJECT", "operation_id":"cancelOrder", "kind":"permission", "fixture":{"owner":False,"state":"PAID_NOT_SHIPPED","repeat":1}, "expected":{"status":403,"refund_count":0,"state":"PAID_NOT_SHIPPED"}},
      {"case_id":"IDEMP-SINGLE-EFFECT", "operation_id":"cancelOrder", "kind":"idempotency", "fixture":{"owner":True,"state":"PAID_NOT_SHIPPED","repeat":2}, "expected":{"status":202,"refund_count":1,"state":"CANCEL_PENDING"}},
      {"case_id":"ASYNC-LEGAL-TRANSITIONS", "operation_id":"getTask", "kind":"async", "expected":{"states":["QUEUED","CANCEL_PENDING","COMPLETED"]}},
      {"case_id":"SSE-ONE-TERMINAL", "operation_id":"orderEvents", "kind":"sse", "expected":{"events":["task.accepted","order.cancelled"],"terminal_count":1}}
    ]
    save(STATE / "candidate-cases.json", {"generated_from": "lab/seed/openapi.json", "generator": "deterministic-spec-candidate-v1", "cases": cases})
    print(f"PASS generated {len(cases)} candidates; business Oracles remain independent")
    return 0

def service(fixture, impl):
    if not fixture["owner"]: return {"status":403,"refund_count":0,"state":fixture["state"]}
    if fixture["state"] == "SHIPPED" and not impl["allow_shipped_cancel"]: return {"status":409,"refund_count":0,"state":"SHIPPED"}
    count = fixture["repeat"] if impl["duplicate_side_effect"] else 1
    return {"status":202,"refund_count":count,"state":"CANCEL_PENDING"}

def run(report_name):
    ensure_state()
    if not (STATE / "candidate-cases.json").exists(): generate_candidates()
    impl, package = load(STATE / "implementation.json"), load(STATE / "candidate-cases.json")
    results = []
    for case in package["cases"]:
        actual = None
        if case["kind"] == "contract":
            actual = {"operation_id": case["operation_id"]}
        elif case["kind"] in {"business","permission","idempotency"}:
            actual = service(case["fixture"], impl)
        elif case["kind"] == "async":
            actual = ["QUEUED", "CANCEL_PENDING", "COMPLETED"]
        elif case["kind"] == "sse":
            actual = [{"id":"e1","type":"task.accepted","terminal":False},{"id":"e2","type":"order.cancelled","terminal":True}]
        issues = check_case(case, actual)
        results.append({"case_id":case["case_id"],"kind":case["kind"],"status":"FAIL" if issues else "PASS","issues":issues,"oracle":"independent-oracle-v1"})
    failed = [r for r in results if r["status"] == "FAIL"]
    report = {"run_id":datetime.now(timezone.utc).strftime("RUN-%Y%m%dT%H%M%SZ"),"status":"FAIL" if failed else "PASS","evidence_status":"fixture-tested","generator":"deterministic-spec-candidate-v1","oracle":"independent-oracle-v1","oracle_path":"lab/oracle.py","input_hashes":{"openapi":digest(SEED/"openapi.json"),"candidates":digest(STATE/"candidate-cases.json"),"implementation":digest(STATE/"implementation.json"),"oracle":digest(ROOT/"oracle.py")},"selected_case_ids":[r["case_id"] for r in results],"results":results,"boundary":"synthetic offline service; no live endpoint, credentials, external queue, or production data"}
    target = REPORTS / report_name
    save(target, report)
    print(json.dumps({"status":report["status"],"failed_case_ids":[r["case_id"] for r in failed],"report":str(target)}, ensure_ascii=False))
    return 1 if failed else 0

def inject():
    ensure_state(); impl = load(STATE / "implementation.json"); impl.update({"allow_shipped_cancel":True,"mutation_id":"MUT-SHIPPED-CANCEL-2026-08-10"}); save(STATE/"implementation.json",impl); print("Mutation injected: SHIPPED cancellation incorrectly accepted"); return 0
def repair():
    ensure_state(); impl = load(STATE / "implementation.json"); impl.update({"allow_shipped_cancel":False,"duplicate_side_effect":False,"mutation_id":None}); save(STATE/"implementation.json",impl); print("PASS repair: state and side-effect rules restored"); return 0

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("command", choices=["reset","generate","run","inject-defect","repair","all"]); parser.add_argument("--report", default=None); args=parser.parse_args()
    if args.command=="reset": return reset()
    if args.command=="generate": ensure_state(); return generate_candidates()
    if args.command=="inject-defect": return inject()
    if args.command=="repair": return repair()
    if args.command=="run": return run(args.report or "latest.json")
    if args.command=="all":
        reset(); generate_candidates(); return run(args.report or "latest.json")
    return reset()
if __name__ == "__main__": sys.exit(main())
