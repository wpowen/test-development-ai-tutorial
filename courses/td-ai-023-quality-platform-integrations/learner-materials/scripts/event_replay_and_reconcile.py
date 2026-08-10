"""Topic entry: replay suppression, reconciliation and audit evidence."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import quality_platform

state = quality_platform.state()
checks = quality_platform.check(state)
evidence = {"topic":"event-replay-reconcile","accepted":state["inbox"]["accepted"],"duplicates_suppressed":state["inbox"]["duplicates"],"writeback":state["writeback"],"audit_hash":state["audit"]["hash"],"reconciliation":"re-read external facts before writeback","gate_oracles":len(checks)}
print(json.dumps(evidence, ensure_ascii=False))
raise SystemExit(0 if evidence["accepted"] == 1 and evidence["duplicates_suppressed"] == 1 and evidence["gate_oracles"] >= 9 else 1)
