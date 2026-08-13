#!/usr/bin/env python3
"""Manifest-driven specialty fixture runner. Business rules live in page manifests."""
import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def execute(manifest_path, mode, report_path):
    manifest = load(manifest_path)
    required = [ROOT / item for item in manifest["required_files"]]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file() or path.stat().st_size == 0]
    rules = manifest["oracle_rules"]
    target = manifest["fault_injection"]["target_oracle"]
    results = []
    for rule in rules:
        passed = not (mode == "fault" and rule["oracle_id"] == target)
        results.append({"oracle_id": rule["oracle_id"], "passed": passed, "evidence": rule["evidence"], "owner": rule["owner"]})
    passed = not missing and all(item["passed"] for item in results)
    report = {
        "schema_version": "1.0", "page_id": manifest["page_id"], "mode": mode,
        "status": "PASS" if passed else "FAIL", "exit_code": 0 if passed else 1,
        "manifest_sha256": digest(manifest_path), "missing_files": missing,
        "fault_id": manifest["fault_injection"]["fault_id"] if mode == "fault" else None,
        "oracle_results": results, "owners": manifest["owners"],
        "evidence_level": "deterministic-offline-fixture",
        "boundary": manifest["evidence_boundary"],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--mode", choices=("baseline", "fault", "repair", "cycle"), required=True)
    parser.add_argument("--report")
    args = parser.parse_args()
    manifest_path = ROOT / args.manifest
    manifest = load(manifest_path)
    base = ROOT / "evidence" / manifest["page_id"]
    if args.mode == "cycle":
        receipts = [execute(manifest_path, mode, base / f"{mode}.json") for mode in ("baseline", "fault", "repair")]
        ok = [item["exit_code"] for item in receipts] == [0, 1, 0]
        cycle = {"page_id": manifest["page_id"], "expected_exit_codes": [0,1,0], "actual_exit_codes": [item["exit_code"] for item in receipts], "status": "PASS" if ok else "FAIL", "boundary": manifest["evidence_boundary"]}
        (base / "cycle.json").write_text(json.dumps(cycle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(cycle, ensure_ascii=False))
        return 0 if ok else 1
    report_path = ROOT / args.report if args.report else base / f"{args.mode}.json"
    report = execute(manifest_path, args.mode, report_path)
    print(json.dumps({"page_id": report["page_id"], "mode": report["mode"], "status": report["status"], "report": str(report_path)}, ensure_ascii=False))
    return report["exit_code"]

if __name__ == "__main__":
    sys.exit(main())
