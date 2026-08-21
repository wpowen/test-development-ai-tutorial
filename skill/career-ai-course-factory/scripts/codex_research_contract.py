#!/usr/bin/env python3
"""Compile and validate fail-closed Codex-native claim research receipts."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from run_claim_deep_research import atomic_write_json, safe_id, sha256_path
from prepare_claim_inventory import validate_inventory_locator_contract


HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
PHASES = {"initial-research", "counterevidence", "gap-fill", "verification"}
EVIDENCE_ROLES = {"researcher", "counterevidence"}
FORBIDDEN_COUNTEREVIDENCE_INPUTS = {
    "evidence-synthesis.md",
    "contradiction-matrix.md",
    "research-saturation.json",
    "codex-research-saturation.json",
    "integrated-report.md",
    "adjudication",
}


def _attestation_payload(trace: dict[str, Any]) -> bytes:
    payload = {key: value for key, value in trace.items() if key != "runtime_attestation"}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _validate_runtime_attestation(trace: dict[str, Any], public_key: Path | None) -> dict[str, str]:
    attestation = trace.get("runtime_attestation")
    if not isinstance(attestation, dict):
        raise ValueError("runtime attestation is required; caller-authored identity fields are not sufficient")
    required = {"schema_version", "algorithm", "key_id", "payload_sha256", "signature_base64"}
    if not required.issubset(attestation):
        raise ValueError("runtime attestation is incomplete")
    if attestation.get("schema_version") != "codex-runtime-attestation.v1" or attestation.get("algorithm") != "rsa-sha256":
        raise ValueError("runtime attestation uses an unsupported contract")
    configured = public_key or (Path(os.environ["CODEX_RESEARCH_ATTESTATION_PUBLIC_KEY"]) if os.environ.get("CODEX_RESEARCH_ATTESTATION_PUBLIC_KEY") else None)
    if configured is None or not configured.is_file():
        raise ValueError("runtime attestation cannot be verified without a trusted public key")
    payload = _attestation_payload(trace)
    payload_sha256 = "sha256:" + hashlib.sha256(payload).hexdigest()
    if attestation.get("payload_sha256") != payload_sha256:
        raise ValueError("runtime attestation payload hash mismatch")
    try:
        signature = base64.b64decode(str(attestation.get("signature_base64", "")), validate=True)
    except ValueError as exc:
        raise ValueError("runtime attestation signature is not valid base64") from exc
    with tempfile.NamedTemporaryFile() as signature_file:
        signature_file.write(signature)
        signature_file.flush()
        completed = subprocess.run(
            ["openssl", "dgst", "-sha256", "-verify", str(configured), "-signature", signature_file.name],
            input=payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    if completed.returncode != 0:
        raise ValueError("runtime attestation signature verification failed")
    return {
        "key_id": str(attestation.get("key_id")),
        "public_key_sha256": sha256_path(configured),
        "payload_sha256": payload_sha256,
    }


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"required file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def _require_hash(value: object, label: str) -> str:
    text = str(value or "")
    if not HASH_RE.fullmatch(text):
        raise ValueError(f"{label} must be a sha256 digest")
    return text


def _resolve_topic_path(topic_dir: Path, relative: object, label: str) -> Path:
    text = str(relative or "")
    root = topic_dir.resolve()
    candidate = (topic_dir / text).resolve()
    if not text or (candidate != root and root not in candidate.parents):
        raise ValueError(f"unsafe or empty {label}: {text}")
    if not candidate.is_file() or candidate.stat().st_size == 0:
        raise ValueError(f"missing or empty {label}: {text}")
    return candidate


def _validate_agent(agent: dict[str, Any], topic_dir: Path, orchestrator_id: str) -> dict[str, Any]:
    agent_id = str(agent.get("runtime_observed_agent_id", ""))
    if not agent_id:
        raise ValueError("agent identity requires runtime_observed_agent_id")
    required = [
        "role", "provider", "runtime", "session_id", "parent_invocation_id",
        "independence_group", "input_context_sha256", "prompt_sha256",
        "input_artifacts", "output_path", "output_sha256",
    ]
    missing = [field for field in required if agent.get(field) is None or agent.get(field) == ""]
    if missing:
        raise ValueError(f"agent identity {agent_id} missing: {', '.join(missing)}")
    if agent.get("provider") != "codex":
        raise ValueError(f"agent identity {agent_id} provider must be codex")
    if str(agent.get("parent_invocation_id")) != orchestrator_id:
        raise ValueError(f"agent identity {agent_id} parent invocation mismatch")
    _require_hash(agent.get("input_context_sha256"), f"agent {agent_id} input context")
    _require_hash(agent.get("prompt_sha256"), f"agent {agent_id} prompt")
    output_path = _resolve_topic_path(topic_dir, agent.get("output_path"), f"agent {agent_id} output")
    if sha256_path(output_path) != _require_hash(agent.get("output_sha256"), f"agent {agent_id} output"):
        raise ValueError(f"agent {agent_id} output hash mismatch")
    inputs = agent.get("input_artifacts")
    if not isinstance(inputs, list):
        raise ValueError(f"agent {agent_id} input_artifacts must be an array")
    for index, artifact in enumerate(inputs):
        if not isinstance(artifact, dict):
            raise ValueError(f"agent {agent_id} input artifact {index} must be an object")
        artifact_path = _resolve_topic_path(topic_dir, artifact.get("path"), f"agent {agent_id} input artifact")
        if sha256_path(artifact_path) != _require_hash(artifact.get("sha256"), f"agent {agent_id} input artifact"):
            raise ValueError(f"agent {agent_id} input artifact hash mismatch: {artifact.get('path', '')}")
    return agent


def validate_trace(trace: dict[str, Any], topic_dir: Path, *, attestation_public_key: Path | None = None) -> dict[str, Any]:
    if not isinstance(trace, dict) or trace.get("schema_version") != "codex-runtime-trace.v1":
        raise ValueError("trace must use codex-runtime-trace.v1")
    if trace.get("surface") != "codex-research":
        raise ValueError("trace surface must be codex-research")
    if trace.get("status") != "completed":
        raise ValueError("trace status must be completed")
    if trace.get("phase") not in PHASES:
        raise ValueError("trace phase is invalid")
    attestation = _validate_runtime_attestation(trace, attestation_public_key)
    claim_ids = trace.get("claim_ids")
    if not isinstance(claim_ids, list) or len(claim_ids) != 1:
        raise ValueError("Codex research trace must contain exactly one claim")
    orchestrator = trace.get("orchestrator")
    if not isinstance(orchestrator, dict):
        raise ValueError("trace requires a runtime-observed orchestrator")
    orchestrator_id = str(orchestrator.get("runtime_observed_agent_id", ""))
    for field in ("runtime_observed_agent_id", "runtime", "session_id", "trace_id"):
        if not str(orchestrator.get(field, "")):
            raise ValueError(f"orchestrator identity missing {field}")

    raw_agents = trace.get("agents")
    if not isinstance(raw_agents, list) or not raw_agents:
        raise ValueError("trace requires agent identities")
    agents = [_validate_agent(agent, topic_dir, orchestrator_id) for agent in raw_agents if isinstance(agent, dict)]
    if len(agents) != len(raw_agents):
        raise ValueError("every trace agent must be an object")
    ids = [str(agent["runtime_observed_agent_id"]) for agent in agents]
    if len(set(ids)) != len(ids):
        raise ValueError("agent identities must be unique within a run")

    evidence_agents = [agent for agent in agents if agent.get("role") in EVIDENCE_ROLES]
    minimum = 2 if trace.get("phase") == "initial-research" else 1
    if len(evidence_agents) < minimum:
        raise ValueError(f"{trace.get('phase')} requires at least {minimum} independent evidence agent(s)")
    contexts = [str(agent["input_context_sha256"]) for agent in evidence_agents]
    groups = [str(agent["independence_group"]) for agent in evidence_agents]
    sessions = [str(agent["session_id"]) for agent in evidence_agents]
    if len(set(contexts)) != len(contexts):
        raise ValueError("independent agents use a shared context")
    if len(set(groups)) != len(groups):
        raise ValueError("independent agents share independence group")
    if len(set(sessions)) != len(sessions):
        raise ValueError("independent agents share runtime session")
    integrators = [agent for agent in agents if agent.get("role") == "integrator"]
    if len(integrators) != 1:
        raise ValueError("each Codex research run requires exactly one integrator")

    events = trace.get("events")
    if not isinstance(events, list):
        raise ValueError("trace events must be an array")
    event_ids: set[str] = set()
    openings: dict[str, dict[str, Any]] = {}
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("trace event must be an object")
        event_id = str(event.get("event_id", ""))
        if not event_id or event_id in event_ids:
            raise ValueError("trace event ids must be unique and non-empty")
        event_ids.add(event_id)
        agent_id = str(event.get("runtime_observed_agent_id", ""))
        if agent_id not in ids:
            raise ValueError(f"trace event {event_id} references an unknown agent")
        if event.get("event_type") == "source_open":
            if event.get("result") != "opened" or not str(event.get("url", "")):
                raise ValueError(f"source opening event {event_id} is incomplete")
            _require_hash(event.get("content_sha256"), f"source opening event {event_id} content")
            openings[event_id] = event
        if trace.get("phase") == "counterevidence" and event.get("event_type") == "artifact_read":
            path = str(event.get("path", "")).lower()
            if "codex-research/" in path or "codex-research\\" in path:
                raise ValueError("counterevidence agent read a prior research run artifact")
            if any(token in path for token in FORBIDDEN_COUNTEREVIDENCE_INPUTS):
                raise ValueError("counterevidence agent read prior synthesis or adjudication")

    citations = trace.get("citations")
    if not isinstance(citations, list) or not citations:
        raise ValueError("trace requires citations mapped to source opening events")
    for citation in citations:
        if not isinstance(citation, dict):
            raise ValueError("citation must be an object")
        opening_id = str(citation.get("opening_event_id", ""))
        opening = openings.get(opening_id)
        if opening is None:
            raise ValueError("citation lacks a matching source open event")
        if str(citation.get("url", "")) != str(opening.get("url", "")):
            raise ValueError("citation URL does not match its source open event")
        if str(citation.get("runtime_observed_agent_id", "")) != str(opening.get("runtime_observed_agent_id", "")):
            raise ValueError("citation agent does not match its source open event")

    return {
        "evidence_agents": evidence_agents,
        "integrator": integrators[0],
        "openings": list(openings.values()),
        "citations": citations,
        "events": events,
        "attestation": attestation,
    }


def _load_codex_inventory(topic_dir: Path, topic_id: str, claim_id: str) -> dict[str, Any]:
    inventory = load_json(topic_dir / "claim-inventory.json")
    if not isinstance(inventory, dict) or inventory.get("schema_version") != "claim-inventory.v1":
        raise ValueError("claim inventory must use claim-inventory.v1")
    if inventory.get("topic_id") != topic_id:
        raise ValueError("claim inventory topic mismatch")
    if inventory.get("execution_contract") != "codex-research.v1":
        raise ValueError("claim inventory must select codex-research.v1")
    locator_errors = validate_inventory_locator_contract(
        inventory, package_root=topic_dir.parents[2], topic_dir=topic_dir
    )
    if locator_errors:
        raise ValueError("claim inventory locator contract is blocked: " + "; ".join(locator_errors[:5]))
    claims = inventory.get("claims")
    matches = [row for row in claims if isinstance(row, dict) and row.get("claim_id") == claim_id] if isinstance(claims, list) else []
    if len(matches) != 1:
        raise ValueError(f"claim {claim_id} not found exactly once")
    return inventory


def compile_codex_trace(
    *, package_root: Path, topic_id: str, claim_id: str, phase: str,
    round_number: int, trace_file: Path, replace: bool, attestation_public_key: Path | None = None,
) -> dict[str, Any]:
    topic_id = safe_id(topic_id, "topic id")
    claim_id = safe_id(claim_id, "claim id")
    if phase not in PHASES or round_number < 1:
        raise ValueError("invalid phase or round")
    topic_dir = package_root.resolve() / "research" / "topics" / topic_id
    _load_codex_inventory(topic_dir, topic_id, claim_id)
    trace = load_json(trace_file)
    if not isinstance(trace, dict):
        raise ValueError("runtime trace must be an object")
    if trace.get("topic_id") != topic_id or trace.get("claim_ids") != [claim_id]:
        raise ValueError("runtime trace topic or claim mismatch")
    if trace.get("phase") != phase or trace.get("round") != round_number:
        raise ValueError("runtime trace phase or round mismatch")
    run_id = safe_id(str(trace.get("run_id", "")), "run id")
    normalized = validate_trace(trace, topic_dir, attestation_public_key=attestation_public_key)
    run_dir = topic_dir / "codex-research" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_trace_path = run_dir / "raw-trace.json"
    if raw_trace_path.exists() and not replace:
        raise ValueError(f"Codex run already exists: {run_id}; use replace after review")
    atomic_write_json(raw_trace_path, trace)
    agent_trace_path = run_dir / "agent-trace.json"
    opening_path = run_dir / "source-openings.json"
    citation_path = run_dir / "citations.json"
    atomic_write_json(agent_trace_path, {"schema_version": "codex-agent-trace.v1", "agents": trace["agents"], "events": trace["events"]})
    atomic_write_json(opening_path, {"schema_version": "codex-source-openings.v1", "openings": normalized["openings"]})
    atomic_write_json(citation_path, {"schema_version": "codex-citations.v1", "citations": normalized["citations"]})
    evidence_agents = normalized["evidence_agents"]
    receipt = {
        "run_id": run_id,
        "claim_ids": [claim_id],
        "round": round_number,
        "phase": phase,
        "provider": "codex",
        "surface": "codex-research",
        "started_at": str(trace.get("started_at", "")),
        "completed_at": str(trace.get("completed_at", "")),
        "orchestrator_invocation_id": str(trace["orchestrator"]["runtime_observed_agent_id"]),
        "orchestrator_session_id": str(trace["orchestrator"]["session_id"]),
        "trace_id": str(trace["orchestrator"]["trace_id"]),
        "runtime_attestation_key_id": normalized["attestation"]["key_id"],
        "runtime_attestation_public_key_sha256": normalized["attestation"]["public_key_sha256"],
        "runtime_attestation_payload_sha256": normalized["attestation"]["payload_sha256"],
        "raw_trace_path": str(raw_trace_path.relative_to(topic_dir)),
        "raw_trace_sha256": sha256_path(raw_trace_path),
        "agent_trace_path": str(agent_trace_path.relative_to(topic_dir)),
        "agent_trace_sha256": sha256_path(agent_trace_path),
        "source_openings_path": str(opening_path.relative_to(topic_dir)),
        "source_openings_sha256": sha256_path(opening_path),
        "citations_path": str(citation_path.relative_to(topic_dir)),
        "citations_sha256": sha256_path(citation_path),
        "agent_invocation_ids": [str(agent["runtime_observed_agent_id"]) for agent in evidence_agents],
        "agent_session_ids": [str(agent["session_id"]) for agent in evidence_agents],
        "independence_groups": [str(agent["independence_group"]) for agent in evidence_agents],
        "agent_context_sha256s": [str(agent["input_context_sha256"]) for agent in evidence_agents],
        "agent_output_sha256s": [str(agent["output_sha256"]) for agent in evidence_agents],
        "input_artifact_sha256s": sorted({
            str(artifact["sha256"])
            for agent in evidence_agents
            for artifact in agent.get("input_artifacts", [])
            if isinstance(artifact, dict) and artifact.get("sha256")
        }),
        "integrator_invocation_id": str(normalized["integrator"]["runtime_observed_agent_id"]),
        "independent_agent_count": len(evidence_agents),
        "source_opening_count": len(normalized["openings"]),
        "citation_count": len(normalized["citations"]),
        "status": "completed",
        "limitations": list(trace.get("limitations", [])) if isinstance(trace.get("limitations"), list) else [],
    }
    receipt_path = topic_dir / "codex-research-receipts.json"
    if receipt_path.exists():
        document = load_json(receipt_path)
        if not isinstance(document, dict) or document.get("schema_version") != "codex-research-receipts.v1":
            raise ValueError("codex-research-receipts.json has an invalid schema")
        if document.get("topic_id") != topic_id:
            raise ValueError("Codex receipt topic mismatch")
    else:
        document = {"schema_version": "codex-research-receipts.v1", "topic_id": topic_id, "runs": []}
    runs = document.get("runs")
    if not isinstance(runs, list):
        raise ValueError("Codex receipt runs must be an array")
    document["runs"] = [row for row in runs if not isinstance(row, dict) or row.get("run_id") != run_id] + [receipt]
    atomic_write_json(receipt_path, document)
    return receipt


def validate_codex_topic(topic_dir: Path, *, require_saturation: bool = True, attestation_public_key: Path | None = None) -> list[str]:
    errors: list[str] = []
    try:
        inventory = load_json(topic_dir / "claim-inventory.json")
        if not isinstance(inventory, dict) or inventory.get("execution_contract") != "codex-research.v1":
            return ["claim inventory does not select codex-research.v1"]
        errors.extend(validate_inventory_locator_contract(
            inventory, package_root=topic_dir.parents[2], topic_dir=topic_dir
        ))
        claim_ids = {str(row.get("claim_id")) for row in inventory.get("claims", []) if isinstance(row, dict)}
        extraction = inventory.get("extraction", {})
        for relative in extraction.get("source_files", []) if isinstance(extraction, dict) else []:
            source = _resolve_topic_path(topic_dir, relative, "claim inventory source")
            if extraction.get("source_hashes", {}).get(relative) != sha256_path(source):
                errors.append(f"claim inventory source hash mismatch: {relative}")
        receipts = load_json(topic_dir / "codex-research-receipts.json")
        if not isinstance(receipts, dict) or receipts.get("schema_version") != "codex-research-receipts.v1":
            return errors + ["invalid codex-research-receipts.json"]
        runs = receipts.get("runs")
        if not isinstance(runs, list) or not runs:
            return errors + ["Codex research needs completed runs"]
        initial_by_claim: dict[str, list[dict[str, Any]]] = {claim: [] for claim in claim_ids}
        expansion_by_claim: dict[str, list[dict[str, Any]]] = {claim: [] for claim in claim_ids}
        for run in runs:
            if not isinstance(run, dict):
                errors.append("Codex receipt run must be an object")
                continue
            run_id = str(run.get("run_id", ""))
            try:
                raw_path = _resolve_topic_path(topic_dir, run.get("raw_trace_path"), f"run {run_id} raw trace")
                if sha256_path(raw_path) != run.get("raw_trace_sha256"):
                    raise ValueError(f"run {run_id} raw trace hash mismatch")
                trace = load_json(raw_path)
                normalized = validate_trace(trace, topic_dir, attestation_public_key=attestation_public_key)
                if normalized["attestation"]["key_id"] != run.get("runtime_attestation_key_id"):
                    raise ValueError(f"run {run_id} runtime attestation key mismatch")
                if normalized["attestation"]["public_key_sha256"] != run.get("runtime_attestation_public_key_sha256"):
                    raise ValueError(f"run {run_id} runtime attestation trust root mismatch")
                if len(normalized["evidence_agents"]) != run.get("independent_agent_count"):
                    raise ValueError(f"run {run_id} independent agent count mismatch")
                if len(normalized["openings"]) != run.get("source_opening_count"):
                    raise ValueError(f"run {run_id} source opening count mismatch")
                if len(normalized["citations"]) != run.get("citation_count"):
                    raise ValueError(f"run {run_id} citation count mismatch")
            except ValueError as exc:
                errors.append(str(exc))
                continue
            for claim_id in run.get("claim_ids", []) if isinstance(run.get("claim_ids"), list) else []:
                if claim_id not in claim_ids:
                    errors.append(f"run {run_id} references unknown claim {claim_id}")
                elif run.get("phase") == "initial-research":
                    initial_by_claim[claim_id].append(run)
                elif run.get("phase") in {"counterevidence", "gap-fill", "verification"}:
                    expansion_by_claim[claim_id].append(run)
        for claim_id in claim_ids:
            initials = initial_by_claim[claim_id]
            expansions = expansion_by_claim[claim_id]
            if not initials:
                errors.append(f"claim {claim_id} lacks initial Codex research")
                continue
            if not expansions:
                errors.append(f"claim {claim_id} lacks Codex counterevidence or gap-fill")
                continue
            initial_ids = {value for run in initials for value in run.get("agent_invocation_ids", [])}
            initial_sessions = {value for run in initials for value in run.get("agent_session_ids", [])}
            initial_contexts = {value for run in initials for value in run.get("agent_context_sha256s", [])}
            initial_outputs = {value for run in initials for value in run.get("agent_output_sha256s", [])}
            for run in expansions:
                if initial_ids.intersection(run.get("agent_invocation_ids", [])):
                    errors.append(f"claim {claim_id} counterevidence reuses an initial agent; fresh agent required")
                if initial_sessions.intersection(run.get("agent_session_ids", [])):
                    errors.append(f"claim {claim_id} counterevidence reuses an initial session; fresh context required")
                if initial_contexts.intersection(run.get("agent_context_sha256s", [])):
                    errors.append(f"claim {claim_id} counterevidence reuses initial context; fresh context required")
                if initial_outputs.intersection(run.get("input_artifact_sha256s", [])):
                    errors.append(f"claim {claim_id} counterevidence consumed prior research output")
        if require_saturation:
            saturation = load_json(topic_dir / "codex-research-saturation.json")
            if not isinstance(saturation, dict) or saturation.get("schema_version") != "codex-research-saturation.v1" or saturation.get("overall_verdict") != "PASS-CODEX-RESEARCH":
                errors.append("Codex research saturation is missing or not PASS-CODEX-RESEARCH")
    except ValueError as exc:
        errors.append(str(exc))
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    compile_parser = subparsers.add_parser("compile")
    compile_parser.add_argument("--package-root", required=True, type=Path)
    compile_parser.add_argument("--topic-id", required=True)
    compile_parser.add_argument("--claim-id", required=True)
    compile_parser.add_argument("--phase", required=True, choices=sorted(PHASES))
    compile_parser.add_argument("--round", required=True, type=int)
    compile_parser.add_argument("--trace-file", required=True, type=Path)
    compile_parser.add_argument("--attestation-public-key", type=Path)
    compile_parser.add_argument("--replace", action="store_true")
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--package-root", required=True, type=Path)
    validate_parser.add_argument("--topic-id", required=True)
    validate_parser.add_argument("--allow-missing-saturation", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "compile":
            receipt = compile_codex_trace(
                package_root=args.package_root, topic_id=args.topic_id, claim_id=args.claim_id,
                phase=args.phase, round_number=args.round, trace_file=args.trace_file, replace=args.replace,
                attestation_public_key=args.attestation_public_key,
            )
            print(f"PASS-CODEX-TRACE run_id={receipt['run_id']} agents={receipt['independent_agent_count']}")
            return 0
        topic_dir = args.package_root.resolve() / "research" / "topics" / safe_id(args.topic_id, "topic id")
        errors = validate_codex_topic(topic_dir, require_saturation=not args.allow_missing_saturation)
        if errors:
            raise ValueError("; ".join(errors))
        print(f"PASS-CODEX-RESEARCH topic_id={args.topic_id}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"BLOCKED-CODEX-RESEARCH: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
