#!/usr/bin/env python3
"""Compile hash-bound research cost events without inventing token savings.

The compiler accepts JSONL (one event per line) and JSON event files containing
``{"events": [...]}``.  It is deliberately strict: an event is usable only
when its identity hash, token availability, status, retry/failure state and
artifact references are explicit and internally consistent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator

SCHEMA_VERSION = "research-cost-telemetry.v1"
UNKNOWN = "UNKNOWN"
HASH_PREFIX = "sha256:"
PROVIDER_SURFACES = {"openai-chatgpt", "openai-api", "codex-research"}
LOWER_COST_SURFACES = {"planner", "luna"}
VALID_PHASES = {"planning", "classification", "initial-research", "counterevidence", "gap-fill", "verification", "adjudication", "synthesis", "reuse", "invalidation", "other"}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return HASH_PREFIX + hashlib.sha256(value).hexdigest()


def sha256_value(value: Any) -> str:
    return sha256_bytes(canonical_json(value))


def file_digest(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _inside(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return path != root


def _hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.startswith(HASH_PREFIX) or len(value) != 71:
        raise ValueError(f"{label} must be a sha256 hash")
    try:
        int(value[len(HASH_PREFIX):], 16)
    except ValueError as exc:
        raise ValueError(f"{label} must be a sha256 hash") from exc
    return value


def _unknown_or_int(value: Any, label: str) -> int | str:
    if value == UNKNOWN:
        return UNKNOWN
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer or UNKNOWN")
    return value


def event_hash(event: dict[str, Any]) -> str:
    payload = {key: value for key, value in event.items() if key != "event_hash"}
    return sha256_value(payload)


def provider_model_is_valid(surface: str, model: str) -> bool:
    """Return whether a known provider/surface pair is eligible for savings.

    Unknown model names remain valid telemetry, but are deliberately ineligible
    for savings until the provider contract is explicit.  This keeps the
    compiler forward-compatible without silently treating a Luna/planner model
    as an OpenAI provider run.
    """
    if model == UNKNOWN:
        return False
    value = model.lower()
    if surface == "openai-chatgpt":
        return "deep-research" in value or "deepresearch" in value or value in {"o3", "o4-mini"}
    if surface == "openai-api":
        return "deep-research" in value or "deepresearch" in value or value.startswith(("o3", "o4"))
    if surface == "codex-research":
        return "deep-research" in value or "deepresearch" in value or value.startswith(("gpt-", "codex"))
    return False


def validate_event(event: Any, *, source: str = "event") -> dict[str, Any]:
    if not isinstance(event, dict):
        raise ValueError(f"{source} must be an object")
    required = {"event_id", "event_hash", "task_id", "run_id", "attempt_id", "phase", "model", "surface", "measurement_scope", "tokens", "latency_ms", "status", "retry", "failure", "canonical_unit_ids", "claim_ids", "input_artifact_hashes", "output_artifact_hashes", "reuse_decision", "invalidation_status"}
    missing = sorted(required - set(event))
    if missing:
        raise ValueError(f"{source} missing required fields: {', '.join(missing)}")
    if not isinstance(event["event_id"], str) or not event["event_id"].strip():
        raise ValueError(f"{source}.event_id must be non-empty")
    _hash(event["event_hash"], f"{source}.event_hash")
    expected = event_hash(event)
    if event["event_hash"] != expected:
        raise ValueError(f"{source}.event_hash does not match event contents")
    for key in ("task_id", "run_id", "attempt_id"):
        if not isinstance(event[key], str) or not event[key].strip():
            raise ValueError(f"{source}.{key} must be non-empty")
    if event["phase"] not in VALID_PHASES:
        raise ValueError(f"{source}.phase is unknown")
    if event["surface"] not in {"planner", "luna", "openai-chatgpt", "openai-api", "codex-research", "other"}:
        raise ValueError(f"{source}.surface is unknown")
    if event["measurement_scope"] not in {"baseline", "current", "neither"}:
        raise ValueError(f"{source}.measurement_scope is unknown")
    if not isinstance(event["model"], str) or not event["model"].strip():
        raise ValueError(f"{source}.model must be explicit, use UNKNOWN when unavailable")
    tokens = event["tokens"]
    if not isinstance(tokens, dict) or set(tokens) != {"input", "output", "total"}:
        raise ValueError(f"{source}.tokens must contain exactly input, output and total")
    for key in ("input", "output", "total"):
        tokens[key] = _unknown_or_int(tokens[key], f"{source}.tokens.{key}")
    if all(tokens[key] != UNKNOWN for key in ("input", "output", "total")) and tokens["total"] != tokens["input"] + tokens["output"]:
        raise ValueError(f"{source}.tokens.total must equal input + output when all are known")
    event["latency_ms"] = _unknown_or_int(event["latency_ms"], f"{source}.latency_ms")
    if event["status"] not in {"started", "completed", "failed", "cancelled", "blocked", "unknown"}:
        raise ValueError(f"{source}.status is unknown")
    retry = event["retry"]
    if not isinstance(retry, dict) or set(retry) != {"is_retry", "retry_index", "retry_of_attempt_id"}:
        raise ValueError(f"{source}.retry must explicitly record retry state")
    if not isinstance(retry["is_retry"], bool) or isinstance(retry["retry_index"], bool) or not isinstance(retry["retry_index"], int) or retry["retry_index"] < 0:
        raise ValueError(f"{source}.retry has invalid retry state")
    if retry["retry_of_attempt_id"] != UNKNOWN and (not isinstance(retry["retry_of_attempt_id"], str) or not retry["retry_of_attempt_id"].strip()):
        raise ValueError(f"{source}.retry.retry_of_attempt_id must be UNKNOWN or a non-empty ID")
    if retry["is_retry"] and retry["retry_index"] < 1:
        raise ValueError(f"{source}.retry retry_index must be >= 1 for retries")
    if not retry["is_retry"] and retry["retry_index"] != 0:
        raise ValueError(f"{source}.retry retry_index must be 0 for first attempts")
    failure = event["failure"]
    if not isinstance(failure, dict) or set(failure) != {"present", "category", "code", "message", "unknown_reason"} or not isinstance(failure["present"], bool):
        raise ValueError(f"{source}.failure must explicitly record failure state")
    for key in ("category", "code", "message", "unknown_reason"):
        if failure[key] != UNKNOWN and (not isinstance(failure[key], str) or not failure[key].strip()):
            raise ValueError(f"{source}.failure.{key} must be UNKNOWN or a non-empty string")
    if event["status"] == "failed" and not failure["present"]:
        raise ValueError(f"{source}.failed event must record failure.present=true")
    if event["status"] != "failed" and failure["present"]:
        raise ValueError(f"{source}.failure.present conflicts with status")
    if not failure["present"] and any(failure[key] != UNKNOWN for key in ("category", "code", "message", "unknown_reason")):
        raise ValueError(f"{source}.failure details must be UNKNOWN when failure.present=false")
    if failure["present"] and not ((failure["category"] != UNKNOWN and failure["code"] != UNKNOWN) or failure["unknown_reason"] != UNKNOWN):
        raise ValueError(f"{source}.failure requires category/code or an explicit unknown_reason")
    for key in ("canonical_unit_ids", "claim_ids", "input_artifact_hashes", "output_artifact_hashes"):
        if not isinstance(event[key], list):
            raise ValueError(f"{source}.{key} must be an array")
    for key in ("canonical_unit_ids", "claim_ids"):
        if any(not isinstance(item, str) or not item.strip() for item in event[key]) or len(event[key]) != len(set(event[key])):
            raise ValueError(f"{source}.{key} contains an invalid or duplicate ID")
    for key in ("input_artifact_hashes", "output_artifact_hashes"):
        if len(event[key]) != len(set(event[key])):
            raise ValueError(f"{source}.{key} contains duplicate hashes")
        for index, item in enumerate(event[key]):
            _hash(item, f"{source}.{key}[{index}]")
    if event["reuse_decision"] not in {"NOT-APPLICABLE", "DIRECT-REUSE", "SOURCE-REUSE-DELTA", "NO-REUSE", "UNDECIDED"}:
        raise ValueError(f"{source}.reuse_decision is invalid")
    if event["invalidation_status"] not in {"not-applicable", "current", "superseded", "invalid", "unknown"}:
        raise ValueError(f"{source}.invalidation_status is invalid")
    if event.get("delta_type") is not None and event["delta_type"] not in {"none", "scope", "source", "counterevidence", "invalidation", "other"}:
        raise ValueError(f"{source}.delta_type is invalid")
    return event


def load_events(path: Path) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        rows = []
        for line_number, line in enumerate(raw.splitlines(), 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number} invalid JSON: {exc.msg}") from exc
        return rows
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} invalid JSON: {exc.msg}") from exc
    if isinstance(data, dict) and isinstance(data.get("events"), list):
        return data["events"]
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    raise ValueError(f"{path} must contain an event object, array, or events array")


def _sum_known(events: Iterable[dict[str, Any]], scope: str) -> int | str:
    selected = [event for event in events if event["measurement_scope"] == scope]
    if not selected or any(event["tokens"]["total"] == UNKNOWN for event in selected):
        return UNKNOWN
    return sum(event["tokens"]["total"] for event in selected)


def _sum_provider_known(events: Iterable[dict[str, Any]], scope: str) -> int | str:
    selected = [event for event in events if event["measurement_scope"] == scope and event["surface"] in PROVIDER_SURFACES]
    if not selected:
        return UNKNOWN
    if any(not provider_model_is_valid(event["surface"], event["model"]) or event["tokens"]["total"] == UNKNOWN for event in selected):
        return UNKNOWN
    return sum(event["tokens"]["total"] for event in selected)


def _attempts(events: Iterable[dict[str, Any]], predicate) -> set[str]:
    return {event["attempt_id"] for event in events if predicate(event)}


def compile_telemetry(paths: list[Path], *, root: Path | None = None, output: Path | None = None, telemetry_id: str = "telemetry-compiled") -> dict[str, Any]:
    if not paths:
        raise ValueError("at least one event file is required")
    base = (root or Path.cwd()).resolve(strict=True)
    resolved: list[Path] = []
    for original in paths:
        path = (base / original if not original.is_absolute() else original).resolve(strict=True)
        if not _inside(base, path) or not path.is_file():
            raise ValueError(f"event path is outside root or not a regular file: {original}")
        resolved.append(path)
    if output is not None:
        out = (base / output if not output.is_absolute() else output).resolve()
        if not _inside(base, out):
            raise ValueError("output path is outside root")
        if out in resolved:
            raise ValueError("output must not overwrite an input event file")
    events: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in resolved:
        for index, raw_event in enumerate(load_events(path), 1):
            event = validate_event(raw_event, source=f"{path}:{index}")
            if event["event_id"] in seen:
                raise ValueError(f"duplicate event_id: {event['event_id']}")
            seen.add(event["event_id"])
            events.append(event)
    events.sort(key=lambda item: item["event_id"])
    by_attempt: dict[str, dict[str, Any]] = {}
    for event in events:
        prior = by_attempt.get(event["attempt_id"])
        if prior is not None and prior["task_id"] != event["task_id"]:
            raise ValueError(f"attempt_id cannot belong to multiple tasks: {event['attempt_id']}")
        by_attempt.setdefault(event["attempt_id"], event)
    for event in events:
        retry = event["retry"]
        if retry["is_retry"]:
            parent_id = retry["retry_of_attempt_id"]
            if parent_id == UNKNOWN or parent_id == event["attempt_id"] or parent_id not in by_attempt:
                raise ValueError(f"retry parent must exist and be a different attempt: {event['event_id']}")
            if by_attempt[parent_id]["task_id"] != event["task_id"]:
                raise ValueError(f"retry parent must belong to the same task: {event['event_id']}")
        elif retry["retry_of_attempt_id"] != UNKNOWN:
            raise ValueError(f"non-retry event must use UNKNOWN retry parent: {event['event_id']}")
    provider_events = [event for event in events if event["surface"] in PROVIDER_SURFACES]
    lower_cost_events = [event for event in events if event["surface"] in LOWER_COST_SURFACES]
    reuse_events = [event for event in events if event["reuse_decision"] != "NOT-APPLICABLE"]
    delta_events = [event for event in events if event.get("delta_type", "none") != "none" or event["reuse_decision"] == "SOURCE-REUSE-DELTA"]
    invalidation_events = [event for event in events if event["phase"] == "invalidation" or event["invalidation_status"] in {"superseded", "invalid"}]
    baseline = _sum_provider_known(events, "baseline")
    current = _sum_provider_known(events, "current")
    if baseline == UNKNOWN or current == UNKNOWN or baseline == 0:
        comparison = {"baseline_total_tokens": baseline, "current_total_tokens": current, "tokens_saved": UNKNOWN, "savings_percent": UNKNOWN, "status": "NOT-COMPUTABLE", "basis": "provider-reported-token-totals-only-and-valid-model-contract"}
    else:
        saved = baseline - current
        comparison = {"baseline_total_tokens": baseline, "current_total_tokens": current, "tokens_saved": saved, "savings_percent": (saved / baseline * 100 if baseline else 0), "status": "COMPUTED", "basis": "provider-reported-token-totals-only-and-valid-model-contract"}
    known_lower = _sum_known(lower_cost_events, "baseline") if lower_cost_events else UNKNOWN
    if lower_cost_events:
        known_lower = UNKNOWN if any(e["tokens"]["total"] == UNKNOWN for e in lower_cost_events) else sum(e["tokens"]["total"] for e in lower_cost_events)
    lower_cost = {"surfaces": ["planner", "luna"], "events_total": len(lower_cost_events), "known_total_tokens": known_lower, "unknown_token_events": sum(e["tokens"]["total"] == UNKNOWN for e in lower_cost_events), "status": "AVAILABLE" if known_lower != UNKNOWN else "NOT-COMPUTABLE"}
    provider_attempts = _attempts(provider_events, lambda _e: True)
    completed_provider_attempts = _attempts(provider_events, lambda e: e["status"] == "completed")
    counterevidence_attempts = _attempts(provider_events, lambda e: e["phase"] == "counterevidence")
    summary = {"events_total": len(events), "tasks_total": len({e["task_id"] for e in events}), "runs_total": len({e["run_id"] for e in events}), "attempts_total": len({e["attempt_id"] for e in events}), "actual_provider_runs": len(provider_attempts), "completed_provider_runs": len(completed_provider_attempts), "counterevidence_runs": len(counterevidence_attempts), "reuse_decisions": len(reuse_events), "direct_reuse": sum(e["reuse_decision"] == "DIRECT-REUSE" for e in events), "source_reuse_delta": sum(e["reuse_decision"] == "SOURCE-REUSE-DELTA" for e in events), "no_reuse": sum(e["reuse_decision"] == "NO-REUSE" for e in events), "invalidation_events": len(invalidation_events), "delta_events": len(delta_events), "lower_cost": lower_cost}
    result = {"schema_version": SCHEMA_VERSION, "telemetry_id": telemetry_id, "compiler_version": SCHEMA_VERSION, "source_event_file_digests": [file_digest(path) for path in resolved], "status": "READY", "events": events, "summary": summary, "cost_comparison": comparison}
    schema_path = Path(__file__).resolve().parents[1] / "assets/schemas/research-cost-telemetry.v1.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(result), key=lambda item: list(item.path))
    if errors:
        raise ValueError(f"compiled telemetry fails schema: {errors[0].message}")
    if output is not None:
        output_path = (base / output if not output.is_absolute() else output).resolve()
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--input", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--telemetry-id", default="telemetry-compiled")
    args = parser.parse_args(argv)
    try:
        result = compile_telemetry(args.input, root=args.root, output=args.output, telemetry_id=args.telemetry_id)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"BLOCKED-RESEARCH-COST-TELEMETRY: {exc}", file=sys.stderr)
        return 2
    if args.output is None:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
