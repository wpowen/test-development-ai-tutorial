#!/usr/bin/env python3
"""独立、无第三方依赖的 AI 服务稳定性教学夹具。使用虚拟时间。"""
import argparse
import json
import random
import sys
from pathlib import Path


def percentile(values, p):
    ordered = sorted(values)
    if not ordered:
        return 0.0
    rank = (len(ordered) - 1) * p / 100
    low, high = int(rank), min(int(rank) + 1, len(ordered) - 1)
    return round(ordered[low] + (ordered[high] - ordered[low]) * (rank - low), 3)


def run(config):
    rng = random.Random(config["seed"])
    workers = [0.0] * config["workers"]
    traces, total_attempts, total_retries, total_calls, total_cost = [], 0, 0, 0, 0.0
    for task_no in range(config["tasks"]):
        arrival = task_no * config["arrival_interval_ms"]
        worker_index = min(range(len(workers)), key=workers.__getitem__)
        start = max(arrival, workers[worker_index])
        queue_wait = start - arrival
        model_attempts = tool_attempts = 0
        events, model_ok, tool_ok = [], False, False
        for attempt in range(config["model_max_attempts"]):
            model_attempts += 1; total_attempts += 1
            failed = rng.random() < config["model_failure_rate"]
            events.append({"kind": "model", "attempt": attempt + 1, "status": "error" if failed else "ok"})
            if not failed:
                model_ok = True; break
            if attempt + 1 < config["model_max_attempts"]:
                start += config["backoff_ms"] * (attempt + 1)
        if model_ok:
            for attempt in range(config["tool_max_attempts"]):
                tool_attempts += 1; total_attempts += 1
                failed = rng.random() < config["tool_failure_rate"]
                events.append({"kind": "tool", "attempt": attempt + 1, "status": "error" if failed else "ok"})
                if not failed:
                    tool_ok = True; break
                if attempt + 1 < config["tool_max_attempts"]:
                    start += config["backoff_ms"] * (attempt + 1)
        total_retries += max(0, model_attempts - 1) + (max(0, tool_attempts - 1) if model_ok else 0)
        latency = queue_wait + config["model_latency_ms"] + (config["tool_latency_ms"] if model_ok else 0) + config["backoff_ms"] * max(0, model_attempts + tool_attempts - 2)
        workers[worker_index] = start + config["model_latency_ms"] + (config["tool_latency_ms"] if model_ok else 0)
        success = model_ok and tool_ok and latency <= config["task_deadline_ms"]
        calls = model_attempts + tool_attempts + 1
        cost = model_attempts * config["model_call_cost"] + tool_attempts * config["tool_call_cost"] + config["retrieval_call_cost"]
        total_calls += calls; total_cost += cost
        traces.append({"task_id": f"task-{task_no + 1:04d}", "trace_id": f"trace-{task_no + 1:04d}", "arrival_ms": arrival, "queue_wait_ms": round(queue_wait, 3), "e2e_latency_ms": round(latency, 3), "success": success, "terminal_state": "completed" if success else ("timeout" if latency > config["task_deadline_ms"] else "dependency_failed"), "model_attempts": model_attempts, "tool_attempts": tool_attempts, "call_count": calls, "cost": round(cost, 5), "events": events})
    successes = sum(item["success"] for item in traces)
    metrics = {"admitted_tasks": len(traces), "task_success_rate": round(successes / len(traces), 5), "e2e_p95_ms": percentile([x["e2e_latency_ms"] for x in traces], 95), "queue_p95_ms": percentile([x["queue_wait_ms"] for x in traces], 95), "retry_attempts": total_retries, "retry_amplification": round(1 + total_retries / len(traces), 5), "call_amplification": round(total_calls / len(traces), 5), "total_cost": round(total_cost, 5), "cost_per_success": round(total_cost / successes, 5) if successes else None, "goodput_tasks_per_s": round(successes / (max(x["arrival_ms"] for x in traces) / 1000 + 0.001), 5)}
    thresholds = config["thresholds"]
    checks = {"task_success_rate": metrics["task_success_rate"] >= thresholds["task_success_rate"], "e2e_p95_ms": metrics["e2e_p95_ms"] <= thresholds["e2e_p95_ms"], "queue_p95_ms": metrics["queue_p95_ms"] <= thresholds["queue_p95_ms"], "retry_amplification": metrics["retry_amplification"] <= thresholds["retry_amplification"], "call_amplification": metrics["call_amplification"] <= thresholds["call_amplification"], "cost_per_success": metrics["cost_per_success"] is not None and metrics["cost_per_success"] <= thresholds["cost_per_success"]}
    return {"schema_version": "1.0", "run_id": config["run_id"], "fixture": True, "workload": {k: config[k] for k in ("tasks", "workers", "arrival_interval_ms", "seed")}, "metrics": metrics, "thresholds": thresholds, "checks": checks, "gate_pass": all(checks.values()), "boundary": "Deterministic offline fixture; no real model, tool, GPU, K8s or production traffic.", "fault": config.get("fault", "none")}, traces


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True); parser.add_argument("--output", required=True)
    args = parser.parse_args()
    summary, traces = run(json.loads(Path(args.config).read_text(encoding="utf-8")))
    output = Path(args.output); output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output / "traces.jsonl").open("w", encoding="utf-8") as stream:
        for trace in traces:
            stream.write(json.dumps(trace, ensure_ascii=False) + "\n")
    print(json.dumps({"run_id": summary["run_id"], "gate_pass": summary["gate_pass"], "metrics": summary["metrics"]}, ensure_ascii=False))
    return 0 if summary["gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
