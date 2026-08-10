"""Topic entry: Jira basis gate, signed intake, candidate provenance and human approval."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import quality_platform

state = quality_platform.state()
evidence = {"topic":"jira-basis-gate","webhook_verified":state["webhook"]["verified"],"candidate_approved":state["candidate"]["approved"],"ai_auto_approved":state["candidate"]["auto"],"human_gate":"AI质量负责人"}
print(json.dumps(evidence, ensure_ascii=False))
raise SystemExit(0 if evidence["webhook_verified"] and evidence["candidate_approved"] and not evidence["ai_auto_approved"] else 1)
