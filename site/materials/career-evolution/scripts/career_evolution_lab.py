#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def get_path(data, dotted):
    value = data
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def set_path(data, dotted, value):
    parts = dotted.split(".")
    current = data
    for part in parts[:-1]:
        current = current.setdefault(part, {})
    current[parts[-1]] = value


def evaluate(manifest_path: Path, mode: str):
    manifest = load(manifest_path)
    root = manifest_path.parents[1]
    fixture_path = root / manifest["input_fixture"]
    actual = copy.deepcopy(load(fixture_path)["observation"])
    if mode == "fault":
        for key, value in manifest["fault_patch"].items():
            set_path(actual, key, value)
    checks = []
    for key, expected in manifest["expected"].items():
        observed = get_path(actual, key)
        checks.append({"field": key, "expected": expected, "actual": observed, "pass": observed == expected})
    passed = all(check["pass"] for check in checks)
    report = {
        "schema_version": "1.0.0",
        "page_id": manifest["page_id"],
        "phase": mode,
        "verdict": "PASS" if passed else "FAIL",
        "exit_code": 0 if passed else 1,
        "evidence_level": "PASS-FIXTURE" if passed else "FAIL-FIXTURE",
        "model_execution": "NOT_RUN",
        "input_sha256": digest(fixture_path),
        "manifest_sha256": digest(manifest_path),
        "checks": checks,
        "unknowns": manifest["unknowns"],
        "boundary": manifest["evidence_boundary"],
    }
    out = root / "evidence" / manifest["page_id"] / f"{mode}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report["exit_code"], out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--mode", choices=["baseline", "fault", "repair", "cycle"], required=True)
    args = parser.parse_args()
    manifest_path = Path(args.manifest).resolve()
    if args.mode != "cycle":
        phase = "baseline" if args.mode == "repair" else args.mode
        code, out = evaluate(manifest_path, phase)
        if args.mode == "repair":
            target = out.with_name("repair.json")
            out.replace(target)
            out = target
        print(json.dumps({"phase": args.mode, "exit_code": code, "report": str(out)}, ensure_ascii=False))
        raise SystemExit(code)
    codes = []
    reports = {}
    for phase in ("baseline", "fault", "repair"):
        source = "baseline" if phase == "repair" else phase
        code, out = evaluate(manifest_path, source)
        if phase == "repair":
            target = out.with_name("repair.json")
            out.replace(target)
            out = target
        codes.append(code)
        reports[phase] = str(out)
    manifest = load(manifest_path)
    root = manifest_path.parents[1]
    ok = codes == [0, 1, 0]
    out = root / "evidence" / manifest["page_id"] / "cycle.json"
    out.write_text(json.dumps({"page_id": manifest["page_id"], "actual_exit_codes": codes, "expected_exit_codes": [0, 1, 0], "verdict": "PASS" if ok else "FAIL", "reports": reports, "evidence_level": "PASS-FIXTURE" if ok else "FAIL-FIXTURE", "model_execution": "NOT_RUN"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"phase": "cycle", "actual_exit_codes": codes, "report": str(out)}, ensure_ascii=False))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
