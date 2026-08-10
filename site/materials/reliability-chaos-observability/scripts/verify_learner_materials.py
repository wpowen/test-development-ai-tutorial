#!/usr/bin/env python3
"""Verify learner-materials without PyYAML or other third-party packages."""
import ast
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    required = [
        "README.md", "fixtures/order-assistant-chaos.yaml", "fixtures/stability-gameday-report.yaml",
        "configs/agent-trace-schema.yaml", "configs/baseline.json", "configs/fault.json", "configs/repaired.json",
        "guides/chaos-experiment-sop.md", "guides/ai-observability-investigation.md", "guides/refund-agent-runbook.md",
        "scripts/reliability_lab.py",
    ]
    missing = [item for item in required if not (ROOT / item).is_file()]
    if missing:
        raise AssertionError(f"missing learner material: {missing}")
    for relative in required:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if len(text.strip()) < 40 or "\t" in text:
            raise AssertionError(f"incomplete text material: {relative}")
    for relative in ("fixtures/order-assistant-chaos.yaml", "fixtures/stability-gameday-report.yaml", "configs/agent-trace-schema.yaml"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        for marker in ("status", "production", "observ", "fault", "task"):
            if marker not in text.lower():
                raise AssertionError(f"{relative} missing YAML marker {marker}")
    for relative in ("configs/baseline.json", "configs/fault.json", "configs/repaired.json"):
        json.loads((ROOT / relative).read_text(encoding="utf-8"))
    tree = ast.parse((ROOT / "scripts/reliability_lab.py").read_text(encoding="utf-8"))
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    allowed = {"argparse", "json", "random", "sys", "pathlib"}
    if any(name.split(".")[0] not in allowed for name in imports):
        raise AssertionError(f"third-party import found: {imports}")
    commands = [
        ("baseline", "configs/baseline.json", "evidence/baseline", 0),
        ("fault", "configs/fault.json", "evidence/fault", 1),
        ("repaired", "configs/repaired.json", "evidence/repaired", 0),
    ]
    outcomes = []
    for name, config, output, expected in commands:
        result = subprocess.run([sys.executable, "scripts/reliability_lab.py", "--config", config, "--output", output], cwd=ROOT, capture_output=True, text=True)
        if result.returncode != expected:
            raise AssertionError(f"{name} exit {result.returncode}, expected {expected}: {result.stderr}")
        report = json.loads((ROOT / output / "summary.json").read_text(encoding="utf-8"))
        if report["gate_pass"] != (expected == 0):
            raise AssertionError(f"{name} gate/report mismatch")
        for field in ("task_success_rate", "e2e_p95_ms", "queue_p95_ms", "retry_amplification", "call_amplification", "cost_per_success"):
            if field not in report["metrics"]:
                raise AssertionError(f"{name} missing metric {field}")
        traces = (ROOT / output / "traces.jsonl").read_text(encoding="utf-8").splitlines()
        if len(traces) != report["metrics"]["admitted_tasks"]:
            raise AssertionError(f"{name} trace count mismatch")
        outcomes.append(f"{name}={result.returncode}")
    print("learner-materials verification PASS: " + ", ".join(outcomes) + "; JSON reports and YAML text complete")


if __name__ == "__main__":
    main()
