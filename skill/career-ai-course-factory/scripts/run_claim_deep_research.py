#!/usr/bin/env python3
"""Run one claim-scoped OpenAI Responses API Deep Research job.

The runner is deliberately fail-closed: it writes the raw provider artifacts for
diagnosis, but appends a completed receipt only when the provider reports
completion and the output contains a report, citations, and a tool trajectory.
It uses only the Python standard library and never prints or persists the API key.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


TERMINAL_STATUSES = {"completed", "failed", "cancelled", "incomplete"}
PHASES = {
    "initial-deep-research",
    "primary-document-reconstruction",
    "counterevidence",
    "gap-fill",
    "verification",
}
TOOL_CALL_TYPES = {
    "web_search_call",
    "file_search_call",
    "mcp_call",
    "mcp_tool_call",
    "code_interpreter_call",
}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_path(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"required file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    )
    temporary_path = Path(handle.name)
    try:
        with handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def load_claim(topic_dir: Path, claim_id: str) -> dict[str, Any]:
    inventory = load_json(topic_dir / "claim-inventory.json")
    if not isinstance(inventory, dict) or inventory.get("schema_version") != "claim-inventory.v1":
        raise ValueError("claim-inventory.json must use claim-inventory.v1")
    # Import lazily to avoid the inventory preparation module importing this
    # runner for its atomic/hash helpers. A runner must never research against
    # a stale, ambiguous, or partially bound source locator.
    from prepare_claim_inventory import validate_inventory_locator_contract

    locator_errors = validate_inventory_locator_contract(
        inventory,
        package_root=topic_dir.parents[2],
        topic_dir=topic_dir,
    )
    if locator_errors:
        raise ValueError("claim-inventory locator contract is blocked: " + "; ".join(locator_errors[:5]))
    claims = inventory.get("claims")
    if not isinstance(claims, list):
        raise ValueError("claim-inventory.json claims must be an array")
    matches = [item for item in claims if isinstance(item, dict) and item.get("claim_id") == claim_id]
    if len(matches) != 1:
        raise ValueError(f"claim {claim_id!r} not found exactly once in claim-inventory.json")
    return matches[0]


def build_tools(
    *,
    web_enabled: bool,
    web_tool_type: str,
    vector_store_ids: list[str],
    mcp_server_url: str,
    mcp_server_label: str,
    allow_mixed_public_private: bool,
    code_interpreter: bool = False,
) -> tuple[list[dict[str, Any]], list[str]]:
    has_private = bool(vector_store_ids or mcp_server_url)
    if web_enabled and has_private and not allow_mixed_public_private:
        raise ValueError(
            "mixed public/private research is blocked; run public web and private sources in separate phases "
            "or pass --allow-mixed-public-private after reviewing exfiltration risk"
        )
    if bool(mcp_server_url) != bool(mcp_server_label):
        raise ValueError("--mcp-server-url and --mcp-server-label must be provided together")

    tools: list[dict[str, Any]] = []
    data_sources: list[str] = []
    if web_enabled:
        if web_tool_type not in {"web_search", "web_search_preview"}:
            raise ValueError("web tool type must be web_search or web_search_preview")
        tools.append({"type": web_tool_type})
        data_sources.append("web_search")
    if vector_store_ids:
        tools.append({"type": "file_search", "vector_store_ids": vector_store_ids})
        data_sources.append("file_search")
    if mcp_server_url:
        tools.append(
            {
                "type": "mcp",
                "server_label": mcp_server_label,
                "server_url": mcp_server_url,
                "require_approval": "never",
            }
        )
        data_sources.append("remote_mcp")
    if code_interpreter:
        tools.append({"type": "code_interpreter", "container": {"type": "auto"}})
        data_sources.append("code_interpreter")
    if not any(source in {"web_search", "file_search", "remote_mcp"} for source in data_sources):
        raise ValueError("at least one research data source is required: web, file search, or remote MCP")
    return tools, data_sources


def build_request_payload(
    *, model: str, prompt: str, tools: list[dict[str, Any]], metadata: dict[str, str]
) -> dict[str, Any]:
    if not model.strip():
        raise ValueError(
            "a current deep-research-capable model is required via --model or OPENAI_DEEP_RESEARCH_MODEL"
        )
    if not prompt.strip():
        raise ValueError("research prompt is empty")
    if not tools:
        raise ValueError("at least one research tool is required")
    include: list[str] = []
    if any(tool.get("type") in {"web_search", "web_search_preview"} for tool in tools):
        include.append("web_search_call.action.sources")
    if any(tool.get("type") == "file_search" for tool in tools):
        include.append("file_search_call.results")
    payload: dict[str, Any] = {
        "model": model.strip(),
        "background": True,
        "input": prompt,
        "tools": tools,
        "metadata": metadata,
    }
    if include:
        payload["include"] = include
    return payload


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def extract_response_artifacts(response: dict[str, Any]) -> dict[str, Any]:
    report_parts: list[str] = []
    citations: list[dict[str, Any]] = []
    tool_calls: list[dict[str, Any]] = []
    discovered_urls: set[str] = set()
    cited_urls: set[str] = set()
    opened_urls: set[str] = set()
    opening_events: list[dict[str, str]] = []
    citation_keys: set[tuple[str, str, int, int]] = set()

    output = response.get("output")
    if not isinstance(output, list):
        output = []
    for item in output:
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")
        if item_type in TOOL_CALL_TYPES:
            tool_calls.append(item)
            action = item.get("action")
            if isinstance(action, dict):
                sources = action.get("sources")
                if isinstance(sources, list):
                    for source in sources:
                        if isinstance(source, dict) and isinstance(source.get("url"), str) and source["url"]:
                            discovered_urls.add(source["url"])
                if action.get("type") in {"open_page", "open", "browse"}:
                    url = action.get("url")
                    if isinstance(url, str) and url:
                        opened_urls.add(url)
                        opening_events.append({
                            "event_id": str(item.get("id", "")),
                            "tool_call_id": str(item.get("id", "")),
                            "action_type": str(action.get("type", "")),
                            "timestamp": str(item.get("created_at") or action.get("timestamp") or ""),
                            "url": url,
                        })
        if item_type != "message":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if not isinstance(part, dict) or part.get("type") not in {"output_text", "text"}:
                continue
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                report_parts.append(text.strip())
            annotations = part.get("annotations")
            if not isinstance(annotations, list):
                continue
            for annotation in annotations:
                if not isinstance(annotation, dict) or annotation.get("type") != "url_citation":
                    continue
                url = annotation.get("url")
                if not isinstance(url, str) or not url:
                    continue
                cited_urls.add(url)
                title = annotation.get("title") if isinstance(annotation.get("title"), str) else ""
                start = annotation.get("start_index") if isinstance(annotation.get("start_index"), int) else -1
                end = annotation.get("end_index") if isinstance(annotation.get("end_index"), int) else -1
                key = (url, title, start, end)
                if key not in citation_keys:
                    citation_keys.add(key)
                    citations.append(
                        {"url": url, "title": title, "start_index": start, "end_index": end}
                    )

    # Preserve tool records found in nested provider output shapes without duplicating top-level calls.
    known_tool_fingerprints = {
        json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for item in tool_calls
    }
    for node in _walk(response):
        if node.get("type") in TOOL_CALL_TYPES:
            fingerprint = json.dumps(node, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            if fingerprint not in known_tool_fingerprints:
                tool_calls.append(node)
                known_tool_fingerprints.add(fingerprint)
            action = node.get("action")
            if isinstance(action, dict):
                sources = action.get("sources")
                if isinstance(sources, list):
                    for source in sources:
                        if isinstance(source, dict) and isinstance(source.get("url"), str) and source["url"]:
                            discovered_urls.add(source["url"])
            if isinstance(action, dict) and action.get("type") in {"open_page", "open", "browse"}:
                url = action.get("url")
                event = {
                    "event_id": str(node.get("id", "")),
                    "tool_call_id": str(node.get("id", "")),
                    "action_type": str(action.get("type", "")),
                    "timestamp": str(node.get("created_at") or action.get("timestamp") or ""),
                    "url": str(url or ""),
                }
                if isinstance(url, str) and url:
                    opened_urls.add(url)
                    if event not in opening_events:
                        opening_events.append(event)

    return {
        "report": "\n\n".join(report_parts).strip(),
        "citations": citations,
        "tool_calls": tool_calls,
        "discovered_urls": sorted(discovered_urls),
        "cited_urls": sorted(cited_urls),
        "opening_events": opening_events,
        "discovered_source_count": len(discovered_urls),
        "cited_source_count": len(cited_urls),
        "opened_source_count": len(opened_urls),
    }


def validate_completed_artifacts(response: dict[str, Any], artifacts: dict[str, Any]) -> None:
    if response.get("status") != "completed":
        raise ValueError(f"provider response is not completed: {response.get('status', 'unknown')}")
    response_id = response.get("id")
    if not isinstance(response_id, str) or not response_id:
        raise ValueError("completed response lacks a provider response id")
    if not isinstance(artifacts.get("report"), str) or not artifacts["report"].strip():
        raise ValueError("completed response lacks a non-empty report")
    if not isinstance(artifacts.get("citations"), list) or not artifacts["citations"]:
        raise ValueError("completed response lacks URL citations")
    if not isinstance(artifacts.get("tool_calls"), list) or not artifacts["tool_calls"]:
        raise ValueError("completed response lacks a research tool-call trajectory")
    if not isinstance(artifacts.get("opened_source_count"), int) or artifacts["opened_source_count"] < 1:
        raise ValueError("completed response does not prove any opened source")
    opening_events = artifacts.get("opening_events")
    if not isinstance(opening_events, list) or not opening_events:
        raise ValueError("completed response lacks an explicit source opening event")
    opened_event_urls: set[str] = set()
    for event in opening_events:
        if not isinstance(event, dict):
            raise ValueError("completed response has an invalid source opening event")
        if not event.get("event_id") or not event.get("tool_call_id"):
            raise ValueError("completed response source opening event lacks provider identity")
        if event.get("action_type") not in {"open_page", "open", "browse"}:
            raise ValueError("completed response source opening event has an invalid action type")
        if "timestamp" not in event or not isinstance(event.get("timestamp"), str):
            raise ValueError("completed response source opening event lacks an observed timestamp field")
        url = event.get("url")
        if not isinstance(url, str) or not url:
            raise ValueError("completed response source opening event lacks a URL")
        opened_event_urls.add(url)
    if artifacts["opened_source_count"] != len(opened_event_urls):
        raise ValueError("completed response opened source count does not match explicit opening events")


def append_completed_receipt(topic_dir: Path, topic_id: str, receipt: dict[str, Any]) -> None:
    receipt_path = topic_dir / "deep-research-receipts.json"
    if receipt_path.exists():
        document = load_json(receipt_path)
        if not isinstance(document, dict):
            raise ValueError("deep-research-receipts.json must be an object")
        if document.get("schema_version") != "deep-research-receipts.v1":
            raise ValueError("deep-research-receipts.json must use deep-research-receipts.v1")
        if document.get("topic_id") != topic_id:
            raise ValueError("deep-research-receipts.json topic_id does not match the requested topic")
    else:
        document = {"schema_version": "deep-research-receipts.v1", "topic_id": topic_id, "runs": []}
    runs = document.get("runs")
    if not isinstance(runs, list):
        raise ValueError("deep-research-receipts.json runs must be an array")
    document["runs"] = [item for item in runs if not isinstance(item, dict) or item.get("run_id") != receipt["run_id"]]
    document["runs"].append(receipt)
    atomic_write_json(receipt_path, document)


class OpenAIResponsesClient:
    def __init__(self, *, api_key: str, base_url: str, request_timeout: int) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.request_timeout = request_timeout

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.request_timeout) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"OpenAI API returned HTTP {exc.code} for {method} {path}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"OpenAI API request failed for {method} {path}: {exc.reason}") from exc
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError("OpenAI API returned invalid JSON") from exc
        if not isinstance(parsed, dict):
            raise RuntimeError("OpenAI API returned a non-object response")
        return parsed

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/responses", payload)

    def retrieve(self, response_id: str) -> dict[str, Any]:
        return self._request("GET", f"/responses/{response_id}")


def wait_for_terminal_response(
    client: OpenAIResponsesClient,
    initial: dict[str, Any],
    *,
    poll_interval: float,
    timeout_seconds: float,
    on_update: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    response_id = initial.get("id")
    if not isinstance(response_id, str) or not response_id:
        raise RuntimeError("OpenAI API create response did not include an id")
    current = initial
    deadline = time.monotonic() + timeout_seconds
    last_status = None
    while True:
        if on_update is not None:
            on_update(current)
        status = current.get("status")
        if status != last_status:
            print(f"response_id={response_id} status={status or 'unknown'}", file=sys.stderr)
            last_status = status
        if status in TERMINAL_STATUSES:
            return current
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(f"timed out waiting for response {response_id}")
        time.sleep(min(poll_interval, remaining))
        current = client.retrieve(response_id)


def compose_prompt(claim: dict[str, Any], phase: str, prompt_body: str) -> str:
    dimensions = claim.get("required_dimensions")
    dimension_text = ", ".join(str(item) for item in dimensions) if isinstance(dimensions, list) else ""
    return f"""# Claim-level Deep Research request

Research exactly one atomic claim. Do not broaden the request into other claims.

- Claim ID: {claim.get('claim_id', '')}
- Statement: {claim.get('statement', '')}
- Claim type: {claim.get('claim_type', '')}
- Risk: {claim.get('risk', '')}
- Scope: {claim.get('scope', '')}
- Phase: {phase}
- Required dimensions: {dimension_text}

Return an evidence-led report that distinguishes evidence, inference, uncertainty, contradiction, and cannot-prove boundaries. Open pivotal sources; prioritize primary and current technical documents; record versions, dates, population/environment, metrics and units where applicable; actively seek disconfirming evidence. Conclude with one proposed disposition: SUPPORTED, SCOPED, UNKNOWN-EXPLICIT, or REJECTED.

## Additional task instructions

{prompt_body.strip()}
""".strip() + "\n"


def safe_id(value: str, label: str) -> str:
    if not SAFE_ID.fullmatch(value):
        raise ValueError(f"{label} must contain only letters, digits, dot, underscore, or hyphen")
    return value


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--topic-id", required=True)
    parser.add_argument("--claim-id", required=True)
    parser.add_argument("--phase", required=True, choices=sorted(PHASES))
    parser.add_argument("--round", required=True, type=int)
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--model", default=os.environ.get("OPENAI_DEEP_RESEARCH_MODEL", ""))
    parser.add_argument(
        "--web-tool-type",
        default=os.environ.get("OPENAI_DEEP_RESEARCH_WEB_TOOL", "web_search_preview"),
    )
    parser.add_argument("--no-web", action="store_true")
    parser.add_argument("--vector-store-id", action="append", default=[])
    parser.add_argument("--mcp-server-url", default="")
    parser.add_argument("--mcp-server-label", default="")
    parser.add_argument("--allow-mixed-public-private", action="store_true")
    parser.add_argument("--code-interpreter", action="store_true")
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument("--timeout-seconds", type=float, default=3600.0)
    parser.add_argument("--request-timeout", type=int, default=120)
    parser.add_argument("--limitation", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        topic_id = safe_id(args.topic_id, "topic id")
        claim_id = safe_id(args.claim_id, "claim id")
        if args.round < 1:
            raise ValueError("--round must be at least 1")
        if args.poll_interval <= 0 or args.timeout_seconds <= 0 or args.request_timeout <= 0:
            raise ValueError("poll interval and timeout values must be positive")
        topic_dir = args.package_root.resolve() / "research" / "topics" / topic_id
        claim = load_claim(topic_dir, claim_id)
        prompt_body = args.prompt_file.read_text(encoding="utf-8")
        prompt = compose_prompt(claim, args.phase, prompt_body)
        tools, data_sources = build_tools(
            web_enabled=not args.no_web,
            web_tool_type=args.web_tool_type,
            vector_store_ids=args.vector_store_id,
            mcp_server_url=args.mcp_server_url,
            mcp_server_label=args.mcp_server_label,
            allow_mixed_public_private=args.allow_mixed_public_private,
            code_interpreter=args.code_interpreter,
        )
        payload = build_request_payload(
            model=args.model,
            prompt=prompt,
            tools=tools,
            metadata={"topic_id": topic_id, "claim_id": claim_id, "phase": args.phase},
        )
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "status": "DRY-RUN",
                        "topic_id": topic_id,
                        "claim_id": claim_id,
                        "phase": args.phase,
                        "round": args.round,
                        "model": args.model,
                        "data_sources": data_sources,
                        "prompt_chars": len(prompt),
                        "credential_read": False,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0

        run_id = safe_id(
            args.run_id or f"{claim_id.lower()}-r{args.round}-{args.phase}",
            "run id",
        )
        client = OpenAIResponsesClient(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            request_timeout=args.request_timeout,
        )
        run_dir = topic_dir / "deep-research" / run_id
        if run_dir.exists() and any(run_dir.iterdir()):
            raise ValueError(f"run directory already contains artifacts: {run_dir}")
        run_dir.mkdir(parents=True, exist_ok=True)
        request_path = run_dir / "request.md"
        request_path.write_text(prompt, encoding="utf-8")
        write_json(
            run_dir / "request.json",
            {
                "model": args.model,
                "background": True,
                "tools": tools,
                "metadata": payload["metadata"],
                "prompt_sha256": sha256_path(request_path),
                "note": "Prompt text is preserved in request.md; credentials are never persisted.",
            },
        )
        started_at = utc_now()
        raw_response_path = run_dir / "raw-response.json"
        initial = client.create(payload)
        response = wait_for_terminal_response(
            client,
            initial,
            poll_interval=args.poll_interval,
            timeout_seconds=args.timeout_seconds,
            on_update=lambda current: write_json(raw_response_path, current),
        )
        completed_at = utc_now()
        write_json(raw_response_path, response)
        artifacts = extract_response_artifacts(response)
        report_path = run_dir / "report.md"
        citations_path = run_dir / "citations.json"
        tool_calls_path = run_dir / "tool-calls.json"
        source_opening_ledger_path = run_dir / "source-opening-ledger.json"
        report_path.write_text(artifacts["report"].rstrip() + "\n", encoding="utf-8")
        write_json(citations_path, {"citations": artifacts["citations"]})
        write_json(tool_calls_path, {"calls": artifacts["tool_calls"]})
        validate_completed_artifacts(response, artifacts)

        response_id = str(response["id"])
        write_json(
            source_opening_ledger_path,
            {
                "schema_version": "source-opening-ledger.v1",
                "run_id": run_id,
                "response_or_export_id": response_id,
                "discovered_urls": artifacts["discovered_urls"],
                "cited_urls": artifacts["cited_urls"],
                "opening_events": artifacts["opening_events"],
                "discovered_source_count": artifacts["discovered_source_count"],
                "cited_source_count": artifacts["cited_source_count"],
                "opened_source_count": artifacts["opened_source_count"],
                "limitations": [
                    "Only explicit open_page/open/browse provider actions count as opened; search sources and citations remain separate."
                ],
            },
        )
        receipt = {
            "run_id": run_id,
            "claim_ids": [claim_id],
            "round": args.round,
            "phase": args.phase,
            "provider": "openai",
            "surface": "openai-responses-api",
            "model_or_feature": str(response.get("model") or args.model),
            "response_or_export_id": response_id,
            "started_at": started_at,
            "completed_at": completed_at,
            "request_path": str(request_path.relative_to(topic_dir)),
            "raw_response_path": str(raw_response_path.relative_to(topic_dir)),
            "report_path": str(report_path.relative_to(topic_dir)),
            "citations_path": str(citations_path.relative_to(topic_dir)),
            "tool_calls_path": str(tool_calls_path.relative_to(topic_dir)),
            "source_opening_ledger_path": str(source_opening_ledger_path.relative_to(topic_dir)),
            "input_sha256": sha256_path(request_path),
            "output_sha256": sha256_path(raw_response_path),
            "data_sources": data_sources,
            "tool_call_count": len(artifacts["tool_calls"]),
            "citation_count": len(artifacts["citations"]),
            "discovered_source_count": artifacts["discovered_source_count"],
            "cited_source_count": artifacts["cited_source_count"],
            "opened_source_count": artifacts["opened_source_count"],
            "status": "completed",
            "limitations": args.limitation,
        }
        append_completed_receipt(topic_dir, topic_id, receipt)
        print(f"PASS run_id={run_id} response_id={response_id} receipt={topic_dir / 'deep-research-receipts.json'}")
        return 0
    except (OSError, ValueError, RuntimeError, TimeoutError) as exc:
        print(f"BLOCKED-DEEP-RESEARCH: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
