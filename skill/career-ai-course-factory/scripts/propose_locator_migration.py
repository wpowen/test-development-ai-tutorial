#!/usr/bin/env python3
"""Propose safe legacy locator rewrites without mutating formal inventories."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

LINE = re.compile(r"^(?P<path>.+?):L(?P<start>[1-9][0-9]*)-L(?P<end>[1-9][0-9]*)$")
LINE_SELECTOR = re.compile(r"^(?P<path>.+?):L(?P<start>[1-9][0-9]*)-L(?P<end>[1-9][0-9]*)#(?P<selector>.+)$")
SINGLE_LINE = re.compile(r"^(?P<path>.+?):L(?P<line>[1-9][0-9]*)$")
PLAIN_LINE_RANGE = re.compile(r"^(?P<path>.+?):(?P<start>[1-9][0-9]*)-(?P<end>[1-9][0-9]*)$")


def _package_relative_variants(package_root: Path, raw_path: str) -> list[tuple[str, str]]:
    """Return safe path variants for legacy locators.

    Historical claim lists were sometimes generated from the workspace root
    and therefore stored paths such as ``outputs/test-development-ai-v2/site``
    even though the package validator runs with ``test-development-ai-v2`` as
    its root.  The old proposal treated these as missing sources.  We may
    strip only an exact path-component prefix ending in the current package
    root's components; we never guess a different file or root.
    """
    normalized = Path(raw_path)
    variants: list[tuple[str, str]] = [(raw_path, raw_path)]
    package_parts = package_root.resolve().parts
    raw_parts = normalized.parts
    # A legacy locator is relative, but its components can include the
    # workspace's ``outputs/<package>`` prefix.  Find an exact suffix match
    # for the package root components and keep only the package-relative tail.
    for index in range(len(raw_parts)):
        if tuple(raw_parts[index : index + len(package_parts)]) == package_parts:
            tail = Path(*raw_parts[index + len(package_parts) :]).as_posix()
            if tail and (tail, tail) not in variants:
                variants.append((raw_path, tail))
    # The common relative form starts at ``outputs`` while package_root may
    # itself be nested under a different absolute prefix.  Match the final
    # package directory name as a conservative fallback only when the direct
    # package-relative candidate exists.
    package_name = package_root.name
    marker = f"/{package_name}/"
    if marker in f"/{raw_path}":
        tail = f"/{raw_path}".split(marker, 1)[1]
        if tail and (raw_path, tail) not in variants:
            variants.append((raw_path, tail))
    return variants


def _unique_tutorial_material_candidate(package_root: Path, raw_path: str) -> tuple[str, str, Path] | None:
    """Resolve an unqualified learner-material path only when canonical.

    Legacy claims often wrote ``fixtures/...`` or ``prompts/...`` without the
    ``tutorial/materials/<bundle>/`` prefix. We search that canonical source
    tree only and accept exactly one suffix match; generated projections and
    archived dist copies are intentionally excluded.
    """
    materials = package_root / "tutorial" / "materials"
    if not materials.is_dir() or raw_path.startswith((".", "/")):
        return None
    raw_parts = Path(raw_path.split("#", 1)[0]).parts
    if not raw_parts or any(part in {".", ".."} for part in raw_parts):
        return None
    candidates: list[Path] = []
    for path in materials.rglob(raw_parts[-1]):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(materials).parts
        if len(relative_parts) >= len(raw_parts) and tuple(relative_parts[-len(raw_parts):]) == tuple(raw_parts):
            candidates.append(path)
    if len(candidates) != 1:
        return None
    candidate = candidates[0]
    return "package", candidate.relative_to(package_root).as_posix(), candidate


def _unique_canonical_module_candidate(package_root: Path, raw_path: str) -> tuple[str, str, Path] | None:
    """Resolve a bare module filename only within canonical content modules."""
    if "/" in raw_path or raw_path.startswith((".", "/")):
        return None
    modules = package_root / "content" / "modules"
    if not modules.is_dir():
        return None
    candidates = [path for path in modules.rglob(raw_path) if path.is_file()]
    if len(candidates) != 1:
        return None
    candidate = candidates[0]
    return "package", candidate.relative_to(package_root).as_posix(), candidate


def _existing_candidate(package_root: Path, topic_dir: Path, raw_path: str) -> tuple[str, str, Path] | None:
    """Resolve an existing topic/package file without selecting a new root."""
    # Some historical lists used a topic-relative traversal such as
    # ``../../../content/...``.  Resolve it from the topic directory, then
    # accept it only if the result is still inside the current package root.
    # This preserves the old intent without allowing an external path to be
    # silently rebound.
    if ".." in Path(raw_path).parts:
        try:
            topic_anchored = (topic_dir / raw_path).resolve()
            if topic_anchored.is_file() and package_root.resolve() in topic_anchored.parents:
                return "package", topic_anchored.relative_to(package_root.resolve()).as_posix(), topic_anchored
        except (OSError, ValueError):
            pass
    for _, relative in _package_relative_variants(package_root, raw_path):
        topic_path = (topic_dir / relative).resolve()
        if topic_path.is_file() and topic_dir.resolve() in topic_path.parents:
            return "topic", Path(relative).as_posix(), topic_path
        package_path = (package_root / relative).resolve()
        if package_path.is_file() and package_root.resolve() in package_path.parents:
            return "package", Path(relative).as_posix(), package_path
    material_candidate = _unique_tutorial_material_candidate(package_root, raw_path)
    if material_candidate is not None:
        return material_candidate
    module_candidate = _unique_canonical_module_candidate(package_root, raw_path)
    if module_candidate is not None:
        return module_candidate
    return None


def _line_range_is_valid(path: Path, start: int, end: int) -> bool:
    try:
        line_count = len(path.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeError):
        return False
    return 1 <= start <= end <= line_count


def _json_pointer_token(value: str) -> str:
    return str(value).replace("~", "~0").replace("/", "~1")


def _unique_json_pointer_matches(value: Any, wanted: str, pointer: str = "") -> list[str]:
    matches: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_pointer = f"{pointer}/{_json_pointer_token(key)}"
            matches.extend(_unique_json_pointer_matches(child, wanted, child_pointer))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            matches.extend(_unique_json_pointer_matches(child, wanted, f"{pointer}/{index}"))
    elif isinstance(value, str) and value == wanted:
        matches.append(pointer or "/")
    return matches


def _unique_json_key_matches(value: Any, wanted: str, pointer: str = "") -> list[str]:
    matches: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_pointer = f"{pointer}/{_json_pointer_token(key)}"
            if str(key) == wanted:
                matches.append(child_pointer)
            matches.extend(_unique_json_key_matches(child, wanted, child_pointer))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            matches.extend(_unique_json_key_matches(child, wanted, f"{pointer}/{index}"))
    return matches


def _json_pointer_exists(value: Any, pointer: str) -> bool:
    if pointer in {"", "/"}:
        return pointer == "" or value is not None
    if not pointer.startswith("/"):
        return False
    current = value
    for token in pointer[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        try:
            current = current[int(token)] if isinstance(current, list) else current[token]
        except (KeyError, IndexError, TypeError, ValueError):
            return False
    return True


def _legacy_json_selector_pointer(value: Any, selector: str) -> str | None:
    """Translate an explicit legacy path selector when it resolves uniquely.

    Supported forms are deliberately narrow: ``key[index]``,
    ``key[field=value]`` and ``key[value]`` where the latter matches one of a
    fixed set of conventional ID fields. Ranges, prose, and ambiguous arrays
    remain manual review items.
    """
    if not selector or " " in selector:
        return None
    parts = selector.split(".")
    current = value
    pointer = ""
    id_fields = ("id", "claim_id", "case_id", "test_id", "requirement_id", "block_id", "metric_id", "artifact_id", "name", "key")
    for part in parts:
        match = re.fullmatch(r"([A-Za-z0-9_-]+)(?:\[([^\]]+)\])?", part)
        if not match or not isinstance(current, dict):
            return None
        key, bracket = match.group(1), match.group(2)
        actual_key = "id" if key == "page_id" and key not in current and "id" in current else key
        if actual_key not in current:
            return None
        current = current[actual_key]
        pointer += "/" + _json_pointer_token(actual_key)
        if bracket is None:
            continue
        if isinstance(current, list) and bracket.isdigit():
            index = int(bracket)
            if index >= len(current):
                return None
            current = current[index]
            pointer += f"/{index}"
            continue
        if isinstance(current, list) and (re.fullmatch(r"\d+-\d+", bracket) or re.fullmatch(r"\d+(?:,\d+)+", bracket)):
            return None
        if not isinstance(current, list):
            return None
        matches: list[tuple[int, Any]] = []
        if "=" in bracket:
            field, expected = bracket.split("=", 1)
            for index, item in enumerate(current):
                actual_field = "id" if field == "page_id" and isinstance(item, dict) and field not in item and "id" in item else field
                if isinstance(item, dict) and str(item.get(actual_field)) == expected:
                    matches.append((index, item))
        else:
            for index, item in enumerate(current):
                if isinstance(item, dict) and any(str(item.get(field)) == bracket for field in id_fields):
                    matches.append((index, item))
        if len(matches) != 1:
            return None
        index, current = matches[0]
        pointer += f"/{index}"
    return pointer if _json_pointer_exists(value, pointer) else None


def _legacy_json_selector_pointers(value: Any, selector: str) -> list[str] | None:
    """Expand explicit JSON array indices/ranges into unique pointers."""
    if not selector or " " in selector:
        return None
    parts = selector.split(".")
    states: list[tuple[Any, str]] = [(value, "")]
    id_fields = ("id", "claim_id", "case_id", "test_id", "requirement_id", "block_id", "metric_id", "artifact_id", "name", "key")
    for part in parts:
        match = re.fullmatch(r"([A-Za-z0-9_-]+)(?:\[([^\]]+)\])?", part)
        if not match:
            return None
        key, bracket = match.group(1), match.group(2)
        next_states: list[tuple[Any, str]] = []
        for current, pointer in states:
            actual_key = "id" if isinstance(current, dict) and key == "page_id" and key not in current and "id" in current else key
            if not isinstance(current, dict) or actual_key not in current:
                return None
            child = current[actual_key]
            child_pointer = pointer + "/" + _json_pointer_token(actual_key)
            if bracket is None:
                next_states.append((child, child_pointer))
                continue
            if not isinstance(child, list):
                return None
            indices: list[int] = []
            if re.fullmatch(r"\d+", bracket):
                indices = [int(bracket)]
            elif re.fullmatch(r"\d+-\d+", bracket) or re.fullmatch(r"(?:\d+|\d+-\d+)(?:,(?:\d+|\d+-\d+))+", bracket):
                for token in bracket.split(","):
                    if re.fullmatch(r"\d+", token):
                        indices.append(int(token))
                    else:
                        start, end = map(int, token.split("-", 1))
                        if start > end or end - start > 100:
                            return None
                        indices.extend(range(start, end + 1))
                if len(indices) != len(set(indices)):
                    return None
                indices = sorted(indices)
            elif "=" in bracket:
                field, expected = bracket.split("=", 1)
                actual_field = "id"
                matches = [(index, item) for index, item in enumerate(child) if isinstance(item, dict) and str(item.get(actual_field if field == "page_id" and field not in item else field)) == expected]
                if len(matches) != 1:
                    return None
                indices = [matches[0][0]]
            else:
                wanted = bracket.split(",")
                for item_wanted in wanted:
                    matches = [(index, item) for index, item in enumerate(child) if isinstance(item, dict) and any(str(item.get(field)) == item_wanted for field in id_fields)]
                    if len(matches) != 1:
                        return None
                    indices.append(matches[0][0])
                if len(indices) != len(set(indices)):
                    return None
                indices = sorted(indices)
            if len(indices) > 100:
                return None
            for index in indices:
                if index < 0 or index >= len(child):
                    return None
                next_states.append((child[index], f"{child_pointer}/{index}"))
        states = next_states
        if not states:
            return None
    pointers = [pointer for _, pointer in states if _json_pointer_exists(value, pointer)]
    return pointers if len(pointers) == len(states) and len(set(pointers)) == len(pointers) else None


def _typed_selector_candidate(alias: str, relative: str, path: Path, selector: str) -> dict[str, Any] | None:
    """Return a selector-backed candidate only when the selector is unique."""
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown"}:
        headings = [
            match.group(1).strip()
            for match in re.finditer(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", path.read_text(encoding="utf-8"), re.MULTILINE)
        ]
        if headings.count(selector.strip()) == 1:
            return {"kind": "md", "value": selector.strip()}
    if suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
            fieldnames = list(rows[0].keys()) if rows else []
        matches = [(column, row) for row in rows for column in fieldnames if row.get(column) == selector]
        if len(matches) == 1:
            return {"kind": "csv", "value": f"key={matches[0][0]}={selector}"}
    if suffix == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return None
        matches = _unique_json_pointer_matches(data, selector)
        if len(matches) == 1:
            return {"kind": "json", "value": matches[0]}
        key_matches = _unique_json_key_matches(data, selector)
        if len(key_matches) == 1:
            return {"kind": "json", "value": key_matches[0]}
        legacy_pointer = _legacy_json_selector_pointer(data, selector)
        if legacy_pointer is not None:
            return {"kind": "json", "value": legacy_pointer}
        legacy_pointers = _legacy_json_selector_pointers(data, selector)
        if legacy_pointers:
            return {"kind": "json", "value": legacy_pointers[0], "values": legacy_pointers}
    return None


def candidate(package_root: Path, topic_dir: Path, raw: str) -> dict[str, Any]:
    raw = str(raw).strip()
    line_selector = LINE_SELECTOR.fullmatch(raw)
    if line_selector:
        path = line_selector.group("path")
        start, end = int(line_selector.group("start")), int(line_selector.group("end"))
        selector = line_selector.group("selector")
        resolved = _existing_candidate(package_root, topic_dir, path)
        if resolved is None:
            return {"raw": raw, "status": "MISSING-SOURCE"}
        alias, relative, candidate_path = resolved
        if not _line_range_is_valid(candidate_path, start, end):
            return {"raw": raw, "status": "LINE-RANGE-INVALID", "root_alias": alias, "path": relative, "line_start": start, "line_end": end, "line_count": len(candidate_path.read_text(encoding="utf-8").splitlines())}
        if candidate_path.suffix.lower() != ".json" or not selector.startswith("/"):
            return {"raw": raw, "status": "MANUAL-SELECTOR-REQUIRED", "root_alias": alias, "path": relative}
        try:
            data = json.loads(candidate_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return {"raw": raw, "status": "MANUAL-SELECTOR-REQUIRED", "root_alias": alias, "path": relative}
        if not _json_pointer_exists(data, selector):
            return {"raw": raw, "status": "MANUAL-SELECTOR-REQUIRED", "root_alias": alias, "path": relative}
        return {"raw": raw, "status": "AUTO-CANDIDATE", "proposed": f"{alias}:{relative}:L{start}-L{end}#json:{selector}", "root_alias": alias, "selector_kind": "json", "selector_value": selector, **({"normalized_from": path} if relative != path else {})}
    match = LINE.fullmatch(raw)
    if match:
        path, start, end = match.group("path"), int(match.group("start")), int(match.group("end"))
        resolved = _existing_candidate(package_root, topic_dir, path)
        if resolved is not None:
            alias, relative, _ = resolved
            if not _line_range_is_valid(resolved[2], start, end):
                return {"raw": raw, "status": "LINE-RANGE-INVALID", "root_alias": alias, "path": relative, "line_start": start, "line_end": end, "line_count": len(resolved[2].read_text(encoding="utf-8").splitlines())}
            row = {"raw": raw, "status": "AUTO-CANDIDATE", "proposed": f"{alias}:{relative}:L{start}-L{end}", "root_alias": alias}
            if relative != path:
                row["normalized_from"] = path
            return row
        return {"raw": raw, "status": "MISSING-SOURCE"}
    single = SINGLE_LINE.fullmatch(raw)
    if single:
        path, line = single.group("path"), int(single.group("line"))
        resolved = _existing_candidate(package_root, topic_dir, path)
        if resolved is None:
            return {"raw": raw, "status": "MISSING-SOURCE"}
        alias, relative, candidate_path = resolved
        if not _line_range_is_valid(candidate_path, line, line):
            return {"raw": raw, "status": "LINE-RANGE-INVALID", "root_alias": alias, "path": relative, "line_start": line, "line_end": line, "line_count": len(candidate_path.read_text(encoding="utf-8").splitlines())}
        row = {"raw": raw, "status": "AUTO-CANDIDATE", "proposed": f"{alias}:{relative}:L{line}-L{line}", "root_alias": alias}
        if relative != path:
            row["normalized_from"] = path
        return row
    plain_range = PLAIN_LINE_RANGE.fullmatch(raw)
    if plain_range:
        path, start, end = plain_range.group("path"), int(plain_range.group("start")), int(plain_range.group("end"))
        resolved = _existing_candidate(package_root, topic_dir, path)
        if resolved is None:
            return {"raw": raw, "status": "MISSING-SOURCE"}
        alias, relative, candidate_path = resolved
        if not _line_range_is_valid(candidate_path, start, end):
            return {"raw": raw, "status": "LINE-RANGE-INVALID", "root_alias": alias, "path": relative, "line_start": start, "line_end": end, "line_count": len(candidate_path.read_text(encoding="utf-8").splitlines())}
        row = {"raw": raw, "status": "AUTO-CANDIDATE", "proposed": f"{alias}:{relative}:L{start}-L{end}", "root_alias": alias}
        if relative != path:
            row["normalized_from"] = path
        return row
    # Preserve explicit legacy JSON Pointer selectors such as
    # ``.../manifest.json#/package_id``.  The pointer must resolve uniquely
    # in the actual file; no selector is inferred from a prose label here.
    if "#" in raw:
        path, pointer = raw.split("#", 1)
        resolved = _existing_candidate(package_root, topic_dir, path)
        if resolved is not None and resolved[2].suffix.lower() == ".json" and pointer.startswith("/"):
            try:
                data = json.loads(resolved[2].read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                data = None
            if data is not None and _json_pointer_exists(data, pointer):
                alias, relative, _ = resolved
                return {"raw": raw, "status": "AUTO-CANDIDATE", "proposed": f"{alias}:{relative}#json:{pointer}", "root_alias": alias, "selector_kind": "json", "selector_value": pointer, **({"normalized_from": path} if relative != path else {})}
        return {"raw": raw, "status": "MANUAL-SELECTOR-REQUIRED" if resolved is not None else "MISSING-SOURCE", "path": path}
    # A colon without a typed line range is often an opaque prose selector
    # (for example `course.ts:TD-P02 course entry`). Never guess its meaning.
    if ":" in raw:
        path = raw.split(":", 1)[0]
        resolved = _existing_candidate(package_root, topic_dir, path)
        if resolved is not None:
            alias, relative, _ = resolved
            selector = raw.split(":", 1)[1].strip()
            typed = _typed_selector_candidate(alias, relative, resolved[2], selector)
            if typed is not None:
                values = typed.get("values") or [typed["value"]]
                proposed_locators = [f"{alias}:{relative}#{typed['kind']}:{value}" for value in values]
                row = {"raw": raw, "status": "AUTO-CANDIDATE", "root_alias": alias, "selector_kind": typed["kind"], "selector_value": typed["value"], **({"normalized_from": path} if relative != path else {})}
                if len(proposed_locators) == 1:
                    row["proposed"] = proposed_locators[0]
                else:
                    row["proposed_locators"] = proposed_locators
                return row
            return {"raw": raw, "status": "MANUAL-SELECTOR-REQUIRED", "path": relative, "root_alias": alias, **({"normalized_from": path} if relative != path else {})}
    resolved = _existing_candidate(package_root, topic_dir, raw)
    if resolved is not None:
        alias, relative, _ = resolved
        row = {"raw": raw, "status": "AUTO-CANDIDATE", "proposed": f"{alias}:{relative}", "root_alias": alias}
        if relative != raw:
            row["normalized_from"] = raw
        return row
    return {"raw": raw, "status": "MISSING-SOURCE"}


def propose(package_root: Path) -> dict[str, Any]:
    package_root = package_root.resolve(strict=True)
    topics = []
    totals = {"locators": 0, "auto_candidates": 0, "manual_selector": 0, "ambiguous": 0, "missing": 0, "line_range_invalid": 0}
    for path in sorted(package_root.glob("research/topics/*/claim-list.v1.json")):
        topic_id, topic_dir = path.parent.name, path.parent
        document = json.loads(path.read_text(encoding="utf-8"))
        rows = []
        for claim in document.get("claims", []):
            for raw in claim.get("source_locations", []):
                item = candidate(package_root, topic_dir, str(raw)); item["claim_id"] = claim.get("claim_id")
                rows.append(item); totals["locators"] += 1
                key = {"AUTO-CANDIDATE":"auto_candidates", "MANUAL-SELECTOR-REQUIRED":"manual_selector", "AMBIGUOUS-ROOT":"ambiguous", "MISSING-SOURCE":"missing", "LINE-RANGE-INVALID":"line_range_invalid"}.get(item["status"])
                if key: totals[key] += 1
        topics.append({"topic_id": topic_id, "locator_count": len(rows), "rows": rows})
    return {"schema_version": "locator-migration-proposal.v1", "status": "PROPOSAL-ONLY", "totals": totals, "topics": topics, "cannot_prove": ["This proposal does not prove selector uniqueness, source freshness, claim completeness, or formal inventory readiness."]}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--package-root", required=True, type=Path); parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        document = propose(args.package_root)
        args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"BLOCKED-LOCATOR-MIGRATION: {exc}"); return 2
    print(json.dumps({"status": document["status"], **document["totals"]}, ensure_ascii=False)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
