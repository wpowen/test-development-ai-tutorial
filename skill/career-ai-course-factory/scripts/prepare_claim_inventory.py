#!/usr/bin/env python3
"""Create a hash-bound claim inventory from an independently reviewed claim list."""

from __future__ import annotations

import argparse
import copy
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

from run_claim_deep_research import atomic_write_json, safe_id, sha256_path


REQUIRED_CLAIM_FIELDS = {
    "claim_id",
    "statement",
    "claim_type",
    "risk",
    "scope",
    "source_locations",
    "required_dimensions",
    "proposed_disposition",
}
RISKS = {"low", "medium", "high", "critical"}
DISPOSITIONS = {"SUPPORTED", "SCOPED", "UNKNOWN-EXPLICIT", "REJECTED"}
EXECUTION_CONTRACTS = {"openai-deep-research.v1", "codex-research.v1"}
LOCATOR_LINE_RE = re.compile(r"^L(?P<start>[1-9][0-9]*)-L(?P<end>[1-9][0-9]*)$")
LOCATOR_PATH_RE = re.compile(r"^(?P<path>.+?)(?::(?P<lines>L[1-9][0-9]*-L[1-9][0-9]*))?$")
ALIAS_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
SAFE_RELATIVE_RE = re.compile(r"^[^/][^\\]*$")


def load_claim_document(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"claims file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in claims file: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema_version") != "claim-list.v1":
        raise ValueError("claims file must be an independently reviewed claim-list.v1 object")
    rows_value = value.get("claims")
    if not isinstance(rows_value, list) or not rows_value:
        raise ValueError("claims file must contain a non-empty claims array")
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(rows_value):
        if not isinstance(item, dict):
            raise ValueError(f"claim row {index} must be an object")
        rows.append(item)
    value["claims"] = rows
    return value


def validate_claim_rows(rows: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    for index, claim in enumerate(rows):
        missing = sorted(REQUIRED_CLAIM_FIELDS - set(claim))
        if missing:
            raise ValueError(f"claim row {index} missing fields: {', '.join(missing)}")
        claim_id = str(claim.get("claim_id", ""))
        safe_id(claim_id, f"claim row {index} id")
        if claim_id in seen:
            raise ValueError(f"duplicate claim_id: {claim_id}")
        seen.add(claim_id)
        for field in ("statement", "claim_type", "scope"):
            if not isinstance(claim.get(field), str) or not claim[field].strip():
                raise ValueError(f"claim {claim_id} {field} must be non-empty")
        if claim.get("risk") not in RISKS:
            raise ValueError(f"claim {claim_id} risk must be one of {sorted(RISKS)}")
        if claim.get("proposed_disposition") not in DISPOSITIONS:
            raise ValueError(f"claim {claim_id} proposed_disposition is invalid")
        for field in ("source_locations", "required_dimensions"):
            value = claim.get(field)
            if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item.strip() for item in value):
                raise ValueError(f"claim {claim_id} {field} must be a non-empty string array")
        dimensions = claim["required_dimensions"]
        if len(set(dimensions)) != len(dimensions):
            raise ValueError(f"claim {claim_id} required_dimensions contains duplicates")


def _root_relative(root: Path, candidate: Path, label: str) -> str:
    try:
        return candidate.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(f"locator escapes allowlisted root {label}: {candidate}") from exc


def _parse_locator(raw: str) -> tuple[str, str, int | None, int | None, str | None, str]:
    """Parse the explicit ``alias:path[:Lstart-Lend][#kind:value]`` grammar."""
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("locator must be a non-empty string")
    value = raw.strip()
    if value.startswith("/") or value.startswith("~") or "\\" in value:
        raise ValueError(f"locator must be a relative POSIX path: {raw}")
    path_and_selector, separator, selector = value.partition("#")
    if separator and (not selector or selector.startswith("#")):
        raise ValueError(f"locator selector is invalid: {raw}")
    match = LOCATOR_PATH_RE.fullmatch(path_and_selector)
    if not match:
        raise ValueError(f"locator grammar is invalid: {raw}")
    path = match.group("path")
    line_spec = match.group("lines")
    if path.startswith("/") or path in {".", ".."}:
        raise ValueError(f"locator path is invalid: {raw}")
    parts = path.split("/")
    if any(not part or part == ".." or part == "." for part in parts):
        raise ValueError(f"locator path cannot contain dot or empty segments: {raw}")
    if ":" not in path:
        raise ValueError(f"locator requires an explicit root alias: {raw}")
    alias, path = path.split(":", 1)
    if not ALIAS_RE.fullmatch(alias) or not path:
        raise ValueError(f"locator alias is invalid: {raw}")
    relative_parts = path.split("/")
    if any(not part or part in {".", ".."} for part in relative_parts):
        raise ValueError(f"locator path cannot contain dot or empty segments: {raw}")
    start = end = None
    if line_spec:
        line_match = LOCATOR_LINE_RE.fullmatch(line_spec)
        if not line_match:
            raise ValueError(f"locator line range is invalid: {raw}")
        start, end = int(line_match.group("start")), int(line_match.group("end"))
        if start > end:
            raise ValueError(f"locator line range is reversed: {raw}")
    canonical_alias = "package" if alias == "package-root" else alias
    canonical = f"{canonical_alias}:{path}"
    if start is not None:
        canonical += f":L{start}-L{end}"
    if separator:
        canonical += f"#{selector}"
    return canonical_alias, path, start, end, selector if separator else None, canonical


def _selector_audit(selector: str | None, candidate: Path, audits: dict[str, Any]) -> tuple[str | None, str | None]:
    if selector is None:
        return None, None
    if ":" not in selector:
        raise ValueError(f"selector requires explicit kind (md/json/csv/opaque): #{selector}")
    kind, value = selector.split(":", 1)
    if kind == "md":
        if candidate.suffix.lower() not in {".md", ".markdown"} or not value.strip():
            raise ValueError(f"md selector requires a Markdown heading: #{selector}")
        headings = [
            match.group(1).strip()
            for match in re.finditer(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", candidate.read_text(encoding="utf-8"), re.MULTILINE)
        ]
        occurrences = headings.count(value.strip())
        if occurrences == 0:
            raise ValueError(f"Markdown heading selector not found: #{selector}")
        if occurrences != 1:
            raise ValueError(f"Markdown heading selector is not unique ({occurrences} matches): #{selector}")
        return kind, value
    if kind == "json":
        if candidate.suffix.lower() != ".json":
            raise ValueError(f"json selector requires a JSON file: #{selector}")
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"JSON selector source is invalid: #{selector}") from exc
        pointer = value
        if pointer and not pointer.startswith("/"):
            raise ValueError(f"JSON selector must use a JSON Pointer: #{selector}")
        current: Any = data
        if pointer:
            for token in pointer[1:].split("/"):
                token = token.replace("~1", "/").replace("~0", "~")
                try:
                    current = current[int(token)] if isinstance(current, list) else current[token]
                except (KeyError, IndexError, TypeError, ValueError) as exc:
                    raise ValueError(f"JSON Pointer selector not found: #{selector}") from exc
        return kind, value
    if kind == "csv":
        if candidate.suffix.lower() != ".csv":
            raise ValueError(f"csv selector requires a CSV file: #{selector}")
        with candidate.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        if value.startswith("line="):
            try:
                line = int(value[5:])
            except ValueError as exc:
                raise ValueError(f"CSV line selector is invalid: #{selector}") from exc
            if line < 2 or line > len(rows) + 1:
                raise ValueError(f"CSV line selector not found: #{selector}")
        elif value.startswith("key="):
            if "=" not in value[4:]:
                raise ValueError(f"CSV key selector is invalid: #{selector}")
            column, expected = value[4:].split("=", 1)
            matches = sum(row.get(column) == expected for row in rows)
            if matches == 0:
                raise ValueError(f"CSV key selector not found: #{selector}")
            if matches != 1:
                raise ValueError(f"CSV key selector is not unique ({matches} matches): #{selector}")
        else:
            raise ValueError(f"CSV selector must use line=N or key=COLUMN=VALUE: #{selector}")
        return kind, value
    if kind == "opaque":
        audit = audits.get(value)
        if not isinstance(audit, dict) or not audit.get("reviewed_by") or not audit.get("rationale"):
            raise ValueError(f"opaque selector requires an explicit audited selector record: #{selector}")
        return kind, value
    raise ValueError(f"unknown selector kind {kind!r}: #{selector}")


def _resolve_locator(
    *,
    raw: str,
    topic_dir: Path,
    package_root: Path,
    locator_roots: dict[str, Path],
    selector_audits: dict[str, Any] | None = None,
) -> dict[str, Any]:
    alias, relative, line_start, line_end, selector, canonical_key = _parse_locator(raw)
    roots = {"topic": topic_dir.resolve(), "package": package_root.resolve(), "package-root": package_root.resolve()}
    roots.update({name: path.resolve() for name, path in locator_roots.items()})
    if alias not in roots:
        raise ValueError(f"unknown locator root alias {alias!r} in {raw}")
    root = roots[alias]
    candidate = (root / relative).resolve()
    resolved_relative = _root_relative(root, candidate, alias)
    if not candidate.is_file() or candidate.stat().st_size == 0:
        raise ValueError(f"locator is missing or empty: {raw}")
    try:
        line_count = len(candidate.read_text(encoding="utf-8").splitlines())
    except UnicodeError as exc:
        raise ValueError(f"locator file is not valid UTF-8 text: {raw}") from exc
    if line_start is not None and (line_end is None or line_start < 1 or line_end > line_count):
        raise ValueError(f"locator line range exceeds file ({line_count} lines): {raw}")
    selector_kind, selector_value = _selector_audit(selector, candidate, selector_audits or {})
    digest = sha256_path(candidate)
    return {
        "locator": raw,
        "canonical_key": canonical_key,
        "root_alias": alias,
        "resolved_path": resolved_relative,
        "sha256": digest,
        "selector": selector,
        "selector_kind": selector_kind,
        "selector_value": selector_value,
        "line_start": line_start,
        "line_end": line_end,
        "line_count": line_count,
    }


def resolve_topic_file(topic_dir: Path, relative: str) -> Path:
    """Compatibility resolver for the existing frozen source_files contract."""
    topic_root = topic_dir.resolve()
    candidate = (topic_dir / relative).resolve()
    _root_relative(topic_root, candidate, "topic")
    if not candidate.is_file() or candidate.stat().st_size == 0:
        raise ValueError(f"topic source is missing or empty: {relative}")
    return candidate


def _validate_safe_relative(relative: str, field: str) -> None:
    if not isinstance(relative, str) or not relative or relative.startswith(("/", "~")) or "\\" in relative:
        raise ValueError(f"{field} must be a safe relative POSIX path: {relative}")
    parts = relative.split("/")
    if any(not part or part in {".", ".."} for part in parts):
        raise ValueError(f"{field} must not contain dot or empty path segments: {relative}")


def _build_root_manifest(package_root: Path, topic_dir: Path, locator_roots: dict[str, Path]) -> dict[str, Any]:
    package = package_root.resolve()
    roots: dict[str, dict[str, Any]] = {
        "topic": {"kind": "topic", "path": _root_relative(package, topic_dir.resolve(), "package")},
        "package": {"kind": "package", "path": "."},
    }
    for alias, supplied in sorted(locator_roots.items()):
        resolved = supplied.resolve()
        try:
            relative = resolved.relative_to(package).as_posix()
        except ValueError:
            roots[alias] = {
                "kind": "external",
                "path": resolved.as_posix(),
                "self_sufficient": False,
                "requires_runtime_binding": True,
            }
        else:
            roots[alias] = {"kind": "package", "path": relative or ".", "self_sufficient": True}
    return {
        "schema_version": "locator-root-manifest.v1",
        "package_relative_priority": True,
        "roots": roots,
    }


def validate_inventory_locator_contract(
    inventory: dict[str, Any],
    *,
    package_root: Path,
    topic_dir: Path,
    locator_roots: dict[str, Path] | None = None,
) -> list[str]:
    """Validate location↔ledger closure, root bindings, safe source files, and freshness."""
    errors: list[str] = []
    extraction = inventory.get("extraction")
    manifest = inventory.get("root_manifest")
    ledger = extraction.get("locator_ledger") if isinstance(extraction, dict) else None
    if not isinstance(manifest, dict) or manifest.get("schema_version") != "locator-root-manifest.v1":
        errors.append("claim inventory missing locator-root-manifest.v1 root_manifest")
    if not isinstance(ledger, list):
        errors.append("claim inventory missing extraction.locator_ledger")
        return errors
    roots = locator_roots or {}
    if isinstance(manifest, dict) and isinstance(manifest.get("roots"), dict):
        manifest_roots = manifest["roots"]
        if "topic" not in manifest_roots or "package" not in manifest_roots:
            errors.append("root manifest must bind topic and package roots")
        else:
            expected_topic = _root_relative(package_root.resolve(), topic_dir.resolve(), "package")
            if manifest_roots["topic"].get("path") != expected_topic or manifest_roots["topic"].get("kind") != "topic":
                errors.append("root manifest topic binding does not match the current package")
            if manifest_roots["package"].get("path") != "." or manifest_roots["package"].get("kind") != "package":
                errors.append("root manifest package binding does not match the current package")
        for alias, record in manifest["roots"].items():
            if not isinstance(record, dict):
                errors.append(f"root manifest alias {alias} must be an object")
                continue
            if record.get("kind") == "external" and alias not in roots:
                errors.append(f"external locator root {alias} is not self-sufficient; runtime binding is required")
            elif record.get("kind") == "external" and alias in roots:
                if record.get("path") != roots[alias].resolve().as_posix():
                    errors.append(f"external locator root {alias} binding differs from root manifest")
            elif record.get("kind") == "package" and alias not in {"topic", "package"}:
                path = record.get("path")
                try:
                    _validate_safe_relative(path, f"root manifest {alias} path")
                    roots[alias] = package_root / path
                except (TypeError, ValueError) as exc:
                    errors.append(str(exc))
    expected: dict[str, dict[str, Any]] = {}
    claims = inventory.get("claims")
    if not isinstance(claims, list):
        errors.append("claim inventory claims must be an array")
        return errors
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        claim_id = str(claim.get("claim_id", ""))
        seen: set[str] = set()
        locations = claim.get("source_locations")
        if not isinstance(locations, list) or not locations:
            errors.append(f"claim {claim_id} source_locations must be a non-empty array")
            continue
        audits = inventory.get("selector_audits", {})
        for raw in locations:
            try:
                parsed_alias, _, _, _, _, canonical = _parse_locator(raw)
            except (TypeError, ValueError) as exc:
                errors.append(f"claim {claim_id} locator {raw!r}: {exc}")
                continue
            if canonical in seen:
                errors.append(f"claim {claim_id} repeats canonical locator {canonical}")
            seen.add(canonical)
            row = expected.setdefault(canonical, {"raw": raw, "claim_ids": []})
            row["claim_ids"].append(claim_id)
            if isinstance(manifest, dict) and isinstance(manifest.get("roots"), dict) and parsed_alias not in manifest["roots"]:
                errors.append(f"locator {canonical} has no root manifest binding")
            try:
                resolved = _resolve_locator(raw=raw, topic_dir=topic_dir, package_root=package_root, locator_roots=roots, selector_audits=audits if isinstance(audits, dict) else {})
                row["resolved"] = resolved
            except (OSError, UnicodeError, ValueError) as exc:
                errors.append(f"claim {claim_id} locator {raw!r}: {exc}")
    actual: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(ledger):
        if not isinstance(entry, dict):
            errors.append(f"locator ledger row {index} must be an object")
            continue
        canonical = entry.get("canonical_key")
        if not isinstance(canonical, str) or not canonical:
            errors.append(f"locator ledger row {index} missing canonical_key")
            continue
        if canonical in actual:
            errors.append(f"duplicate locator ledger canonical_key: {canonical}")
        actual[canonical] = entry
        claim_ids = entry.get("claim_ids")
        if not isinstance(claim_ids, list) or claim_ids != sorted(set(map(str, claim_ids))):
            errors.append(f"locator ledger {canonical} claim_ids must be unique and sorted")
    if set(expected) != set(actual):
        errors.append(f"locator ledger closure mismatch: expected={len(expected)} actual={len(actual)}")
    for canonical, expected_row in expected.items():
        entry = actual.get(canonical)
        if not entry or "resolved" not in expected_row:
            continue
        if entry.get("claim_ids") != sorted(set(expected_row["claim_ids"])):
            errors.append(f"locator ledger {canonical} claim_ids do not match source_locations")
        resolved = expected_row["resolved"]
        for field in ("canonical_key", "root_alias", "resolved_path", "sha256", "selector", "selector_kind", "selector_value", "line_start", "line_end", "line_count"):
            if entry.get(field) != resolved.get(field):
                errors.append(f"locator ledger {canonical} stale or mismatched field: {field}")
    if isinstance(extraction, dict):
        source_files = extraction.get("source_files", [])
        source_hashes = extraction.get("source_hashes", {})
        if not isinstance(source_files, list) or len(source_files) != len(set(map(str, source_files))):
            errors.append("source_files must be a unique array")
        elif not isinstance(source_hashes, dict) or set(map(str, source_hashes)) != set(map(str, source_files)):
            errors.append("source_files and source_hashes must have exact matching keys")
        if isinstance(source_files, list):
            for relative in source_files:
                try:
                    _validate_safe_relative(relative, "source_files")
                    source_path = resolve_topic_file(topic_dir, relative)
                    expected_hash = source_hashes.get(relative) if isinstance(source_hashes, dict) else None
                    if expected_hash != sha256_path(source_path):
                        errors.append(f"source hash mismatch: {relative}")
                except (OSError, ValueError) as exc:
                    errors.append(f"unsafe or stale source_file {relative!r}: {exc}")
    return errors


def verify_locator_ledger(
    *, package_root: Path, topic_id: str, ledger: list[dict[str, Any]], locator_roots: dict[str, Path] | None = None,
    inventory: dict[str, Any] | None = None,
) -> None:
    """Re-resolve a frozen ledger through the public contract; raises on drift."""
    topic_dir = package_root.resolve() / "research" / "topics" / safe_id(topic_id, "topic id")
    if inventory is None:
        raise ValueError("verify_locator_ledger requires the complete inventory and root manifest")
    candidate_inventory = copy.deepcopy(inventory)
    extraction = candidate_inventory.get("extraction")
    if not isinstance(extraction, dict):
        raise ValueError("verify_locator_ledger requires inventory.extraction")
    extraction["locator_ledger"] = copy.deepcopy(ledger)
    errors = validate_inventory_locator_contract(
        candidate_inventory, package_root=package_root, topic_dir=topic_dir, locator_roots=locator_roots
    )
    if errors:
        raise ValueError("locator contract is stale or invalid: " + "; ".join(errors[:5]))


def prepare_inventory(
    *,
    package_root: Path,
    topic_id: str,
    claims_file: Path,
    source_files: list[str],
    author_id: str,
    independent_auditor_id: str,
    replace: bool,
    execution_contract: str = "openai-deep-research.v1",
    locator_roots: dict[str, Path] | None = None,
) -> dict[str, Any]:
    topic_id = safe_id(topic_id, "topic id")
    locator_roots = locator_roots or {}
    for alias, root in locator_roots.items():
        if not ALIAS_RE.fullmatch(alias) or alias in {"topic", "package", "package-root"}:
            raise ValueError(f"invalid or reserved locator root alias: {alias}")
        if not root.is_dir():
            raise ValueError(f"locator root does not exist or is not a directory: {root}")
    if not author_id.strip() or not independent_auditor_id.strip():
        raise ValueError("author and independent auditor ids are required")
    if author_id.strip() == independent_auditor_id.strip():
        raise ValueError("claim inventory requires an independent auditor distinct from the author")
    if not source_files:
        raise ValueError("at least one frozen topic source file is required")
    if execution_contract not in EXECUTION_CONTRACTS:
        raise ValueError(f"execution contract must be one of {sorted(EXECUTION_CONTRACTS)}")
    if len(set(source_files)) != len(source_files):
        raise ValueError("source file list contains duplicates")
    topic_dir = package_root.resolve() / "research" / "topics" / topic_id
    if not topic_dir.is_dir():
        raise ValueError(f"topic directory not found: {topic_dir}")
    output_path = topic_dir / "claim-inventory.json"
    if output_path.exists() and not replace:
        raise ValueError(f"claim inventory already exists: {output_path}; use --replace after review")

    claims_document = load_claim_document(claims_file)
    if claims_document.get("topic_id") != topic_id:
        raise ValueError("claims file topic_id does not match --topic-id")
    if claims_document.get("reviewed_by") != independent_auditor_id.strip():
        raise ValueError("claims file reviewed_by must match the independent auditor id")
    if claims_document.get("unmapped_propositions") != 0:
        raise ValueError("claims file must explicitly attest unmapped_propositions=0")
    rows = claims_document["claims"]
    validate_claim_rows(rows)
    for relative in source_files:
        _validate_safe_relative(relative, "source_files")
    source_hashes = {relative: sha256_path(resolve_topic_file(topic_dir, relative)) for relative in source_files}
    locator_ledger: list[dict[str, Any]] = []
    locator_index: dict[str, dict[str, Any]] = {}
    selector_audits = claims_document.get("selector_audits", {})
    if selector_audits and not isinstance(selector_audits, dict):
        raise ValueError("selector_audits must be an object when provided")
    for claim in rows:
        claim_keys: set[str] = set()
        for raw_locator in claim["source_locations"]:
            resolved = _resolve_locator(
                raw=raw_locator,
                topic_dir=topic_dir,
                package_root=package_root,
                locator_roots=locator_roots,
                selector_audits=selector_audits if isinstance(selector_audits, dict) else {},
            )
            canonical = str(resolved["canonical_key"])
            if canonical in claim_keys:
                raise ValueError(f"claim {claim['claim_id']} repeats canonical locator {canonical}")
            claim_keys.add(canonical)
            if canonical in locator_index:
                locator_index[canonical]["claim_ids"].append(claim["claim_id"])
                continue
            entry = resolved
            entry["claim_ids"] = [claim["claim_id"]]
            locator_index[canonical] = entry
            locator_ledger.append(entry)
    for entry in locator_ledger:
        entry["claim_ids"] = sorted(set(entry["claim_ids"]))
    inventory = {
        "schema_version": "claim-inventory.v1",
        "topic_id": topic_id,
        "execution_contract": execution_contract,
        "root_manifest": _build_root_manifest(package_root, topic_dir, locator_roots),
        "selector_audits": selector_audits if isinstance(selector_audits, dict) else {},
        "extraction": {
            "author_id": author_id.strip(),
            "independent_auditor_id": independent_auditor_id.strip(),
            "source_files": source_files,
            "source_hashes": source_hashes,
            "locator_ledger": locator_ledger,
            "unmapped_propositions": 0,
        },
        "claims": rows,
    }
    atomic_write_json(output_path, inventory)
    return inventory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--topic-id", required=True)
    parser.add_argument("--claims-file", required=True, type=Path)
    parser.add_argument("--source-file", action="append", required=True)
    parser.add_argument("--author-id", required=True)
    parser.add_argument("--independent-auditor-id", required=True)
    parser.add_argument("--execution-contract", choices=sorted(EXECUTION_CONTRACTS), default="openai-deep-research.v1")
    parser.add_argument(
        "--locator-root",
        action="append",
        default=[],
        metavar="ALIAS=PATH",
        help="explicit allowlisted root for external locators; repeatable",
    )
    parser.add_argument("--replace", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        locator_roots: dict[str, Path] = {}
        for item in args.locator_root:
            if "=" not in item:
                raise ValueError(f"--locator-root must use ALIAS=PATH: {item}")
            alias, raw_path = item.split("=", 1)
            if not ALIAS_RE.fullmatch(alias) or alias in {"topic", "package", "package-root"}:
                raise ValueError(f"invalid or reserved locator root alias: {alias}")
            path = Path(raw_path).expanduser()
            if not path.is_dir():
                raise ValueError(f"locator root does not exist or is not a directory: {path}")
            if alias in locator_roots:
                raise ValueError(f"duplicate locator root alias: {alias}")
            locator_roots[alias] = path
        inventory = prepare_inventory(
            package_root=args.package_root,
            topic_id=args.topic_id,
            claims_file=args.claims_file,
            source_files=args.source_file,
            author_id=args.author_id,
            independent_auditor_id=args.independent_auditor_id,
            replace=args.replace,
            execution_contract=args.execution_contract,
            locator_roots=locator_roots,
        )
        print(f"PASS topic_id={inventory['topic_id']} claims={len(inventory['claims'])}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"BLOCKED-CLAIM-INVENTORY: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
