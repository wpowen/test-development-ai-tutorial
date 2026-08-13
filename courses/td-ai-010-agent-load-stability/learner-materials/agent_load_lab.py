#!/usr/bin/env python3
"""Deterministic offline Agent load/stability teaching fixture."""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = (len(ordered) - 1) * p
    low, high = math.floor(rank), math.ceil(rank)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (rank - low)


def run(config: dict) -> tuple[dict, list[dict]]:
    rng = random.Random(config["seed"])
    workers = config["workers"]
    available_at = [0.0] * workers
    traces: list[dict] = []
    total_model_calls = total_tool_calls = total_attempts = first_attempts = 0
    total_cost = 0.0

    for index in range(config["tasks"]):
        task_id = f"task-{index + 1:04d}"
        admitted_at = index * config["arrival_interval_ms"]
        worker = min(range(workers), key=lambda item: available_at[item])
        started_at = max(admitted_at, available_at[worker])
        queue_ms = started_at - admitted_at
        now = started_at
        spans = []
        success = True
        attempts_for_task = 0
        model_calls = 0
        tool_calls = 0

        for step, kind in enumerate(("model", "order_lookup", "model", "refund_tool"), start=1):
            if not success:
                break
            max_attempts = 1 if kind == "model" else config["max_tool_attempts"]
            first_attempts += 1
            step_success = False
            for attempt in range(1, max_attempts + 1):
                attempts_for_task += 1
                total_attempts += 1
                if kind == "model":
                    model_calls += 1
                    total_model_calls += 1
                    duration = config["model_ms"] * rng.uniform(0.85, 1.2)
                    failed = rng.random() < config.get("model_failure_rate", 0.0)
                    total_cost += config["model_call_cost"]
                else:
                    tool_calls += 1
                    total_tool_calls += 1
                    duration = config["tool_ms"] * rng.uniform(0.8, 1.3)
                    failed = rng.random() < config["tool_failure_rate"]
                    total_cost += config["tool_call_cost"]
                span_start = now
                now += duration
                spans.append({
                    "step": step, "kind": kind, "attempt": attempt,
                    "start_ms": round(span_start, 2), "end_ms": round(now, 2),
                    "duration_ms": round(duration, 2), "status": "error" if failed else "ok",
                })
                if not failed:
                    step_success = True
                    break
                if attempt < max_attempts:
                    now += config["backoff_ms"] * attempt
            if not step_success:
                success = False

        completed_at = now
        available_at[worker] = completed_at
        e2e_ms = completed_at - admitted_at
        task_cost = model_calls * config["model_call_cost"] + tool_calls * config["tool_call_cost"]
        traces.append({
            "run_id": config["run_id"], "task_id": task_id, "worker": worker,
            "admitted_at_ms": round(admitted_at, 2), "started_at_ms": round(started_at, 2),
            "completed_at_ms": round(completed_at, 2), "queue_ms": round(queue_ms, 2),
            "e2e_ms": round(e2e_ms, 2), "success": success,
            "terminal_state": "completed" if success else "tool_failed",
            "model_calls": model_calls, "tool_calls": tool_calls,
            "attempts": attempts_for_task, "estimated_cost": round(task_cost, 5),
            "spans": spans,
        })

    successful = [trace for trace in traces if trace["success"]]
    duration_s = max(trace["completed_at_ms"] for trace in traces) / 1000
    metrics = {
        "task_success_rate": len(successful) / len(traces),
        "e2e_p95_ms": percentile([trace["e2e_ms"] for trace in traces], 0.95),
        "queue_p95_ms": percentile([trace["queue_ms"] for trace in traces], 0.95),
        "retry_amplification": total_attempts / first_attempts,
        "call_amplification": (total_model_calls + total_tool_calls) / len(traces),
        "cost_per_success": total_cost / len(successful) if successful else float("inf"),
        "total_cost": total_cost,
        "goodput_tasks_per_s": sum(
            1 for trace in successful
            if trace["e2e_ms"] <= config["thresholds"]["e2e_p95_ms"]
            and trace["estimated_cost"] <= config["thresholds"]["cost_per_success"]
        ) / duration_s,
    }
    checks = {
        "task_success_rate": metrics["task_success_rate"] >= config["thresholds"]["task_success_rate"],
        "e2e_p95_ms": metrics["e2e_p95_ms"] <= config["thresholds"]["e2e_p95_ms"],
        "queue_p95_ms": metrics["queue_p95_ms"] <= config["thresholds"]["queue_p95_ms"],
        "retry_amplification": metrics["retry_amplification"] <= config["thresholds"]["retry_amplification"],
        "cost_per_success": metrics["cost_per_success"] <= config["thresholds"]["cost_per_success"],
    }
    summary = {
        "schema_version": "1.0", "run_id": config["run_id"], "fixture": True,
        "workload": {key: config[key] for key in ("tasks", "workers", "arrival_interval_ms", "seed")},
        "metrics": {key: round(value, 5) for key, value in metrics.items()},
        "thresholds": config["thresholds"], "checks": checks, "gate_pass": all(checks.values()),
        "boundary": "Deterministic offline fixture; not a production capacity claim.",
    }
    return summary, traces


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    summary, traces = run(config)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output / "traces.jsonl").write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in traces), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
