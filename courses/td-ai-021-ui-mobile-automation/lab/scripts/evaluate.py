import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "fixture" / "ui_contract.json"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    data = json.loads(CONTRACT.read_text())
    required = ("stable_locator", "business_assertion")
    missing = [key for key in required if not data.get(key)]
    result = {"contract": str(CONTRACT.relative_to(ROOT)), "missing_contracts": missing,
              "oracle_pass": not missing, "status": "PASS" if not missing else "FAIL",
              "execution": "offline-standard-library"}
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not missing else 1

if __name__ == "__main__":
    raise SystemExit(main())
