import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "fixture" / "canonical_contract.json"
target = ROOT / "fixture" / "ui_contract.json"
target.write_text(json.dumps(json.loads(source.read_text()), indent=2) + "\n")
print("repaired: stable locator and business assertion restored")
