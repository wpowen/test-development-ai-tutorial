import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
target = ROOT / "fixture" / "ui_contract.json"
data = json.loads(target.read_text())
data.pop("stable_locator", None)
data.pop("business_assertion", None)
target.write_text(json.dumps(data, indent=2) + "\n")
print("mutation: deleted stable_locator and business_assertion")
