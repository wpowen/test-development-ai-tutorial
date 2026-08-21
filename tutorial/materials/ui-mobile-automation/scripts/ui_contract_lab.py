"""Dependency-free learner lab. Run from learner-materials or with its script path."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "ui_contract.json"
CANONICAL = ROOT / "fixtures" / "canonical_ui_contract.json"
REPORTS = ROOT / "reports"
REQUIRED_FILES = {
    "fixtures/refund-approval.json": ("scenario_id", "business_oracle", "stable_locators"),
    "fixtures/android-receiving.yaml": ("scenario_id:", "business_oracle:", "stable_locator:"),
    "fixtures/ios-reschedule.json": ("scenario_id", "business_oracle", "stable_locator"),
    "fixtures/return-trajectory.json": ("scenario_id", "business_oracle", "stable_locators"),
    "configs/web-compatibility-matrix.yaml": ("schema:", "matrix:", "environment_contract:"),
    "configs/self-healing-policy.yaml": ("schema:", "allowed_mutations:", "human_gate:", "forbidden_actions:"),
    "guides/web-journey-sop.md": ("# Web 关键旅程 SOP", "业务 oracle", "NOT_RUN/static-reviewed"),
    "guides/a11y-visual-regression.md": ("# Accessibility 与视觉回归", "baseline", "NOT_RUN/static-reviewed"),
    "guides/android-device-matrix.md": ("# Android 设备矩阵", "Espresso", "NOT_RUN/static-reviewed"),
    "guides/ios-xcuitest-preflight.md": ("# iOS XCUITest Preflight", "xcodebuild -version", "NOT_RUN/static-reviewed"),
}

def write_report(path, status, missing=None):
    report = {"status": status, "oracle_pass": status == "PASS", "missing_contracts": missing or [], "execution": "offline-standard-library"}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if status == "PASS" else 1

def restore():
    FIXTURE.write_text(json.dumps(json.loads(CANONICAL.read_text()), ensure_ascii=False, indent=2) + "\n")

def validate_package():
    errors = []
    for relative, needles in REQUIRED_FILES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(relative)
            continue
        text = path.read_text()
        for needle in needles:
            if needle not in text:
                errors.append(f"{relative}:{needle}")
    for path in (FIXTURE, CANONICAL):
        try:
            json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}:{exc}")
    result = {"status": "PASS" if not errors else "FAIL", "checked_files": len(REQUIRED_FILES) + 2, "errors": errors}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not errors else 1

def evaluate(report):
    data = json.loads(FIXTURE.read_text())
    missing = [field for field in ("stable_locator", "business_assertion") if not data.get(field)]
    return write_report(report, "PASS" if not missing else "FAIL", missing)

def main():
    parser = argparse.ArgumentParser(description="offline UI contract learner lab")
    parser.add_argument("command", choices=("validate", "baseline", "mutation", "repair"))
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.command == "validate":
        return validate_package()
    if args.command in ("baseline", "repair"):
        restore()
        return evaluate(args.report or REPORTS / f"{args.command}.json")
    data = json.loads(FIXTURE.read_text())
    data.pop("stable_locator", None)
    data.pop("business_assertion", None)
    FIXTURE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return evaluate(args.report or REPORTS / "mutation.json")

if __name__ == "__main__":
    raise SystemExit(main())
