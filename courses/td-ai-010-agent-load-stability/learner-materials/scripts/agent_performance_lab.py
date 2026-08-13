#!/usr/bin/env python3
"""Deterministic Agent performance and stability teaching lab.

The lab models synthetic tasks and deliberately separates task success from
request completion. It proves the eight local gates and their red/green
behavior; it never estimates production capacity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path


def percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * quantile
    low, high = math.floor(position), math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def compare(actual: float, operator: str, target: float) -> bool:
    if operator == "min":
        return actual >= target
    if operator == "max":
        return actual <= target
    if operator == "eq":
        return actual == target
    raise ValueError(f"unsupported gate operator: {operator}")


def simulate(page_id: str, phase: str, profile: dict) -> tuple[dict, list[dict]]:
    params = profile["phases"][phase]
    rng = random.Random(profile["seed"] + {"baseline": 0, "fault": 100, "repair": 200}[phase])
    workers = int(params["workers"])
    available_at = [0.0] * workers
    traces: list[dict] = []
    scheduled_at = 0.0

    for index in range(int(profile["tasks"])):
        task_type = profile["task_mix"][index % len(profile["task_mix"])]
        if params["load_model"] == "open":
            admitted_at = index * float(params["arrival_interval_ms"])
        else:
            admitted_at = scheduled_at
        worker = min(range(workers), key=lambda item: available_at[item])
        started_at = max(admitted_at, available_at[worker])
        queue_ms = started_at - admitted_at
        input_tokens = int(params["input_tokens"] * (0.75 + 0.5 * rng.random()))
        output_tokens = int(params["output_tokens"] * (0.8 + 0.4 * rng.random()))
        retry_count = int(params["retry_count"] if index % 3 else params.get("retry_peak", params["retry_count"]))
        step_count = int(params["step_count"] + retry_count)
        ttft_ms = float(params["ttft_ms"]) + input_tokens * float(params["prefill_ms_per_token"]) + queue_ms
        tpot_ms = float(params["tpot_ms"]) * (0.9 + 0.2 * rng.random())
        tool_ms = float(params["tool_ms"]) * (0.85 + 0.3 * rng.random())
        service_ms = ttft_ms + output_tokens * tpot_ms + tool_ms + retry_count * float(params["retry_penalty_ms"])
        e2e_ms = service_ms + float(params.get("orchestration_ms", 20))
        completed_at = started_at + service_ms
        available_at[worker] = completed_at
        if params["load_model"] == "closed":
            scheduled_at = min(available_at)

        business_success = rng.random() >= float(params["failure_rate"])
        trace_complete = rng.random() >= float(params["trace_gap_rate"])
        cleanup_ok = rng.random() >= float(params["cleanup_failure_rate"])
        degraded = bool(params.get("degrade_on_pressure", False) and (queue_ms > profile["pressure_queue_ms"] or retry_count > 1))
        traces.append({
            "task_id": f"{page_id.lower()}-{phase}-{index + 1:03d}",
            "task_type": task_type,
            "load_model": params["load_model"],
            "admitted_at_ms": round(admitted_at, 3),
            "started_at_ms": round(started_at, 3),
            "completed_at_ms": round(completed_at, 3),
            "queue_ms": round(queue_ms, 3),
            "ttft_ms": round(ttft_ms, 3),
            "tpot_ms": round(tpot_ms, 3),
            "e2e_ms": round(e2e_ms, 3),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "retry_count": retry_count,
            "step_count": step_count,
            "business_success": business_success,
            "terminal_state": "degraded_read_only" if degraded else ("completed" if business_success else "failed"),
            "trace_complete": trace_complete,
            "cleanup_ok": cleanup_ok,
            "memory_mb": round(float(params["memory_base_mb"]) + index * float(params["memory_growth_mb_per_task"]), 3),
            "spans": [
                {"span_id": f"root-{index}", "parent_span_id": None, "kind": "invoke_agent", "attempt": 1},
                {"span_id": f"model-{index}", "parent_span_id": f"root-{index}" if trace_complete else None, "kind": "gen_ai.chat", "attempt": 1},
                {"span_id": f"tool-{index}", "parent_span_id": f"root-{index}" if trace_complete else None, "kind": "execute_tool", "attempt": retry_count + 1},
            ],
        })

    completed = max(item["completed_at_ms"] for item in traces)
    first_admission = min(item["admitted_at_ms"] for item in traces)
    duration_s = max((completed - first_admission) / 1000, 0.001)
    successful = [item for item in traces if item["business_success"]]
    good = [item for item in successful if item["e2e_ms"] <= profile["good_task_latency_ms"] and item["retry_count"] <= profile["good_task_retry_limit"]]
    observed_rate = len(traces) / duration_s
    target_rate = 1000 / float(params["arrival_interval_ms"])
    memory_slope = (traces[-1]["memory_mb"] - traces[0]["memory_mb"]) / max(len(traces) - 1, 1)
    metrics = {
        "workload_slice_coverage": float(params.get("represented_slice_rate", 1.0)),
        "business_oracle_rate": float(params.get("business_oracle_rate", 1.0)),
        "ttft_p95_ms": percentile([item["ttft_ms"] for item in traces], 0.95),
        "tpot_p95_ms": percentile([item["tpot_ms"] for item in traces], 0.95),
        "queue_p95_ms": percentile([item["queue_ms"] for item in traces], 0.95),
        "retry_p95": percentile([item["retry_count"] for item in traces], 0.95),
        "step_p95": percentile([item["step_count"] for item in traces], 0.95),
        "trace_complete_rate": sum(item["trace_complete"] for item in traces) / len(traces),
        "arrival_rate_fidelity": min(observed_rate, target_rate) / max(observed_rate, target_rate),
        "coordinated_omission_detected": 1.0 if params["load_model"] == "open" else 0.0,
        "goodput_tasks_per_s": len(good) / duration_s,
        "bottleneck_attributed": 1.0 if params.get("bottleneck") in {"queue", "prefill", "decode", "tool", "retry"} else 0.0,
        "timeout_budget_valid": 1.0 if params["retry_penalty_ms"] * max(params["retry_peak"], 1) < profile["good_task_latency_ms"] else 0.0,
        "degrade_safe_rate": sum(item["terminal_state"] == "degraded_read_only" for item in traces) / max(1, sum(item["queue_ms"] > profile["pressure_queue_ms"] or item["retry_count"] > 1 for item in traces)),
        "memory_growth_mb_per_task": memory_slope,
        "cleanup_success_rate": sum(item["cleanup_ok"] for item in traces) / len(traces),
        "good_task_rate": len(good) / len(traces),
        "alert_actionability": float(params["alert_actionability"]),
        "incident_evidence_complete": float(params["incident_evidence_complete"]),
        "task_success_rate": len(successful) / len(traces),
        "e2e_p95_ms": percentile([item["e2e_ms"] for item in traces], 0.95),
        "observed_rate_tasks_per_s": observed_rate,
    }
    gates = profile["gates"]
    checks = {name: compare(float(metrics[name]), rule["operator"], float(rule["value"])) for name, rule in gates.items()}
    summary = {
        "schema_version": "agent-performance-run.v2",
        "page_id": page_id,
        "phase": phase,
        "fixture": True,
        "workload_version": profile["workload_version"],
        "prompt_package_version": "1.0.0",
        "metrics": {key: round(value, 5) for key, value in metrics.items()},
        "gates": gates,
        "checks": checks,
        "gate_pass": all(checks.values()),
        "configuration_hash": hashlib.sha256(json.dumps(profile, sort_keys=True).encode()).hexdigest(),
        "evidence_boundary": "Deterministic synthetic load fixture; this is not a production capacity claim.",
    }
    return summary, traces


def load_manifest(path: Path) -> tuple[dict, dict, Path]:
    path = path.resolve()
    manifest = json.loads(path.read_text(encoding="utf-8"))
    root = path.parent.parent
    profile_path = root / manifest["profile"]
    return manifest, json.loads(profile_path.read_text(encoding="utf-8")), root


def write_run(output: Path, summary: dict, traces: list[dict]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "traces.jsonl").write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in traces), encoding="utf-8")


def execute(manifest_path: Path, phase: str, report_dir: Path | None) -> tuple[int, dict]:
    manifest, profile, root = load_manifest(manifest_path)
    report_root = root.parent / "evidence" if root.name == "lab" else root / "reports"
    output = report_dir or report_root / manifest["page_id"] / phase
    summary, traces = simulate(manifest["page_id"], phase, profile)
    write_run(output, summary, traces)
    return (0 if summary["gate_pass"] else 1), summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("baseline", "fault", "repair", "cycle"))
    parser.add_argument("--report-dir", type=Path)
    args = parser.parse_args()
    if args.mode != "cycle":
        code, summary = execute(args.manifest, args.mode, args.report_dir)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return code

    manifest, _, root = load_manifest(args.manifest)
    report_root = root.parent / "evidence" if root.name == "lab" else root / "reports"
    base = args.report_dir or report_root / manifest["page_id"]
    observed: dict[str, int] = {}
    summaries: dict[str, dict] = {}
    for phase in ("baseline", "fault", "repair"):
        code, summary = execute(args.manifest, phase, base / phase)
        observed[phase] = code
        summaries[phase] = summary
    cycle_pass = observed == {"baseline": 0, "fault": 1, "repair": 0}
    cycle = {
        "schema_version": "agent-performance-cycle.v2",
        "page_id": manifest["page_id"],
        "observed_exit_codes": observed,
        "expected_exit_codes": {"baseline": 0, "fault": 1, "repair": 0},
        "cycle_pass": cycle_pass,
        "fault_detected_by": [name for name, ok in summaries["fault"]["checks"].items() if not ok],
        "repair_comparison": {
            key: {"fault": summaries["fault"]["metrics"][key], "repair": summaries["repair"]["metrics"][key]}
            for key in summaries["fault"]["gates"]
        },
        "evidence_boundary": "Fixture-tested only; no live model, practitioner review, or production capacity evidence.",
    }
    base.mkdir(parents=True, exist_ok=True)
    (base / "cycle-summary.json").write_text(json.dumps(cycle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(cycle, ensure_ascii=False, indent=2))
    return 0 if cycle_pass else 2


if __name__ == "__main__":
    sys.exit(main())
