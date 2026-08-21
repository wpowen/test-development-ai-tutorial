#!/usr/bin/env python3
"""Deterministically extract an *author-pending* claim-list draft.

This is deliberately a draft compiler, not a claim adjudicator.  It only
turns assertion-like prose in frozen local sources into separately located
candidate rows.  It never assigns an auditor, risk, research dimensions, or
an approved disposition, and it never reports ``unmapped_propositions=0``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


SCRIPT_VERSION = "claim-list-author-extractor.v1"
AUTHOR_PENDING = "AUTHOR-PENDING"
DEFAULT_SOURCE_FILES = (
    "research-brief.md",
    "source-pack.csv",
    "research-runs.json",
    "evidence-synthesis.md",
    "engineering-blueprint.md",
    "manuscript.md",
    "comparison.md",
    "lab-manifest.json",
    "validation.md",
    "projection-ledger.json",
)


@dataclass(frozen=True)
class SourceText:
    relative_path: str
    path: Path
    text: str
    digest: str
    line_count: int


@dataclass(frozen=True)
class SourceSpec:
    root_alias: str
    relative_path: str
    expected_digest: str | None = None


@dataclass(frozen=True)
class Proposition:
    relative_path: str
    line_start: int
    line_end: int
    statement: str
    ordinal: int
    char_start: int
    char_end: int
    source_excerpt: str


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def _contained(root: Path, candidate: Path) -> bool:
    """Return true only for a real child of root (not root itself)."""
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return candidate != root


def _safe_relative(value: str, field: str) -> str:
    if not value or "\x00" in value:
        raise ValueError(f"{field} must be a non-empty safe relative path")
    p = Path(value)
    if p.is_absolute() or any(part in {"", ".", ".."} for part in p.parts):
        raise ValueError(f"{field} must not escape its root: {value}")
    return p.as_posix()


def _source_roots(topic_dir: Path, source_roots: dict[str, Path] | None = None) -> dict[str, Path]:
    roots = {"topic": topic_dir.resolve(strict=True)}
    for alias, root in (source_roots or {}).items():
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", alias) or alias == "topic":
            raise ValueError(f"invalid or reserved source root alias: {alias}")
        resolved = root.resolve(strict=True)
        if not resolved.is_dir():
            raise ValueError(f"source root is not a directory: {root}")
        roots[alias] = resolved
    return roots


def resolve_source(topic_dir: Path, relative_path: str, *, root_alias: str = "topic", source_roots: dict[str, Path] | None = None) -> Path:
    relative = _safe_relative(relative_path, "source file")
    roots = _source_roots(topic_dir, source_roots)
    if root_alias not in roots:
        raise ValueError(f"unknown source root alias: {root_alias}")
    root = roots[root_alias]
    candidate = (root / relative).resolve(strict=True)
    if not _contained(root, candidate) or not candidate.is_file():
        raise ValueError(f"source file escapes {root_alias} root or is not a file: {relative_path}")
    return candidate


def load_source(topic_dir: Path, spec: SourceSpec, *, source_roots: dict[str, Path] | None = None) -> SourceText:
    relative = _safe_relative(spec.relative_path, "source file")
    path = resolve_source(topic_dir, relative, root_alias=spec.root_alias, source_roots=source_roots)
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"source file is not UTF-8: {relative}") from exc
    if not text.strip():
        raise ValueError(f"source file is empty: {relative}")
    actual_digest = sha256_bytes(raw)
    if spec.expected_digest is not None and spec.expected_digest != actual_digest:
        raise ValueError(f"source manifest digest mismatch: {spec.root_alias}:{relative}")
    return SourceText(f"{spec.root_alias}:{relative}", path, text, actual_digest, len(text.splitlines()))


def _strip_markdown_prefix(line: str) -> str:
    value = line.strip()
    value = re.sub(r"^\s{0,3}(?:[-*+]\s+|\d+[.)]\s+)", "", value)
    value = re.sub(r"^\s*>\s?", "", value)
    return value.strip()


def _is_heading_or_metadata(value: str) -> bool:
    if not value or re.match(r"^#{1,6}\s+", value):
        return True
    if value.startswith("```") or value.startswith("~~~"):
        return True
    if re.fullmatch(r"[-*_`|\s:：]+", value):
        return True
    if re.fullmatch(r"https?://\S+", value):
        return True
    return False


def _is_assertion(value: str) -> bool:
    """Conservative language-independent assertion heuristic.

    A line must contain actual prose (not a heading, URL, or a bare label).
    We intentionally do not infer claim type or truth; this only decides
    whether a human should see the sentence in the draft.
    """
    if _is_heading_or_metadata(value) or value.endswith((":", "：")):
        return False
    plain = re.sub(r"[`*_\[\]()]", "", value).strip()
    has_cjk = bool(re.search(r"[\u3400-\u9fff]", plain))
    if len(plain) < (4 if has_cjk else 8):
        return False
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]*", plain)
    if has_cjk:
        return bool(re.search(r"[\u3400-\u9fff]", plain))
    return len(words) >= 3


def _csv_cells(raw_line: str) -> list[tuple[str, int, str]]:
    """Parse CSV cells while retaining exact character spans in the source."""
    spans: list[tuple[int, int]] = []
    start = 0
    quoted = False
    index = 0
    while index < len(raw_line):
        char = raw_line[index]
        if char == '"':
            if quoted and index + 1 < len(raw_line) and raw_line[index + 1] == '"':
                index += 2
                continue
            quoted = not quoted
        elif char == "," and not quoted:
            spans.append((start, index))
            start = index + 1
        index += 1
    spans.append((start, len(raw_line)))
    result: list[tuple[str, int, str]] = []
    for start, end in spans:
        token = raw_line[start:end]
        try:
            decoded = next(csv.reader([token]))[0]
        except (csv.Error, IndexError):
            decoded = token.strip()
        left = len(token) - len(token.lstrip())
        right = len(token.rstrip())
        raw_excerpt = token[left:right]
        result.append((decoded, start + left, raw_excerpt))
    return result


def _structured_cells(raw_line: str, suffix: str) -> list[tuple[str, int, str]]:
    """Return textual cells and their byte-independent character offsets.

    JSON/CSV/TS inputs are still source evidence, not executable claims.  We
    expose only human-readable string cells so the auditor can inspect the
    exact original line; keys, punctuation, and code identifiers are not
    promoted into claims.
    """
    if suffix == ".csv":
        return _csv_cells(raw_line)
    if suffix in {".json", ".ts", ".tsx", ".js", ".jsx"}:
        # Deliberately conservative: only quoted strings, not numeric values,
        # object keys, identifiers, or comments. Escapes stay in the locator
        # line and the decoded string is only used as a candidate statement.
        values: list[tuple[str, int, str]] = []
        for match in re.finditer(r"(?P<quote>['\"])(?P<value>(?:\\.|(?!\1).)*)\1", raw_line):
            value = match.group("value")
            try:
                if match.group("quote") == '"':
                    decoded = json.loads(match.group(0))
                else:
                    # Preserve non-ASCII source text. ``unicode_escape`` treats
                    # UTF-8 bytes as Latin-1 and corrupts Chinese strings.
                    decoded = re.sub(
                        r"\\(['\\\"nrt])",
                        lambda item: {"n": "\n", "r": "\r", "t": "\t"}.get(item.group(1), item.group(1)),
                        value,
                    )
            except json.JSONDecodeError:
                decoded = value
            values.append((decoded, match.start("value"), value))
        return values
    return [(raw_line, 0, raw_line)]


_TERMINATORS = re.compile(r"(?<=[。！？!?；;])|(?<=[.!?;])(?=\s|$)")
_CLAUSE_BREAK = re.compile(
    r"(?:，|,)(?=(?:并且|而且|以及|同时|但|否则|因此|从而|且|或|不能|不得|and\b|but\b|while\b|or\b))"
    r"|\s+(?=(?:and|but|while|or)\s+)",
    re.IGNORECASE,
)


def _clean_statement(value: str) -> str:
    value = re.sub(r"\s+", " ", value.strip())
    value = value.strip(" \t-•|")
    value = re.sub(r"^(?:并且|而且|以及|同时|但|否则|因此|从而|且|或)\s*|^(?:and|but|while|or)\s+", "", value, flags=re.IGNORECASE)
    value = value.rstrip("，,")
    return value


def split_atomic_sentences(value: str) -> list[str]:
    """Split terminal sentences and obvious compound clauses deterministically."""
    pieces: list[str] = []
    for sentence in _TERMINATORS.split(value):
        sentence = _clean_statement(sentence)
        if not sentence:
            continue
        clauses = []
        for part in _CLAUSE_BREAK.split(sentence):
            raw_part = re.sub(r"\s+", " ", part.strip())
            clean_part = _clean_statement(raw_part)
            # Preserve a dangling conjunction as an explicit review item so
            # the extractor cannot silently turn it into a complete claim.
            clauses.append(clean_part or raw_part)
        pieces.extend(part for part in clauses if part)
    return pieces


def extract_propositions(source: SourceText) -> tuple[list[Proposition], list[dict[str, object]]]:
    """Extract candidate atomic prose and record substantive lines needing review."""
    lines = source.text.splitlines(keepends=True)
    propositions: list[Proposition] = []
    unmapped: list[dict[str, object]] = []
    in_fence = False
    ordinal = 0
    file_offset = 0
    suffix = source.path.suffix.lower()
    fence_language = ""
    for line_no, full_line in enumerate(lines, 1):
        raw_line = full_line.rstrip("\r\n")
        line_offset = file_offset
        # Advance before any early-continue branch so all following offsets
        # remain exact even when fenced blocks are skipped as prose.
        file_offset += len(full_line)
        stripped = raw_line.strip()
        if stripped.startswith(("```", "~~~")):
            if not in_fence:
                fence_language = stripped[3:].strip()
            else:
                fence_language = ""
            in_fence = not in_fence
            continue
        if in_fence:
            if stripped:
                local = raw_line.find(stripped)
                unmapped.append({
                    "source_file": source.relative_path,
                    "line_start": line_no,
                    "line_end": line_no,
                    "char_start": line_offset + max(local, 0),
                    "char_end": line_offset + max(local, 0) + len(stripped),
                    "text": stripped,
                    "source_excerpt": stripped,
                    "evidence_kind": "fenced-code-or-command",
                    "language": fence_language or "unspecified",
                    "reason": "AUTHOR-PENDING: fenced implementation evidence requires structured author review",
                })
            continue
        if suffix in {".md", ".markdown", ".txt"}:
            # Markdown tables are split cell-by-cell; this avoids turning a
            # header or a row containing several independent assertions into
            # one giant claim. List prefixes are removed by the same path.
            cells = [(value, raw_line.find(value), value) for value in [_strip_markdown_prefix(raw_line)]]
            if "|" in raw_line and not re.fullmatch(r"\s*\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)+\|?\s*", raw_line):
                cells = []
                cell_cursor = 0
                for cell in raw_line.split("|"):
                    clean = _strip_markdown_prefix(cell)
                    if clean:
                        cell_position = raw_line.find(cell, cell_cursor)
                        if cell_position < 0:
                            cell_position = cell_cursor
                        cells.append((clean, cell_position + (len(cell) - len(cell.lstrip())), clean))
                    cell_cursor += len(cell) + 1
        else:
            cells = _structured_cells(raw_line, suffix)
        for value, local_offset, raw_excerpt in cells:
            value = _clean_statement(value)
            if _is_heading_or_metadata(value):
                continue
            if not _is_assertion(value):
                # A non-empty prose-looking label is explicitly left for the
                # author; headings and code are not propositions and are ignored.
                if value and len(value) >= 8 and not value.endswith((":", "：")):
                    unmapped.append({
                        "source_file": source.relative_path,
                        "line_start": line_no,
                        "line_end": line_no,
                        "char_start": line_offset + max(local_offset, 0),
                        "char_end": line_offset + max(local_offset, 0) + len(raw_excerpt),
                        "text": value,
                        "source_excerpt": raw_excerpt,
                        "reason": "AUTHOR-PENDING: extractor could not classify as prose assertion",
                    })
                continue
            sentences = split_atomic_sentences(value)
            cursor = 0
            for sentence in sentences:
                position = value.find(sentence, cursor)
                if position < 0:
                    position = cursor
                # Re-run the assertion gate after splitting.  A conjunction
                # fragment or a short residual is unmapped, never a claim.
                if not _is_assertion(sentence):
                    raw_position = raw_excerpt.find(sentence, min(cursor, len(raw_excerpt)))
                    if raw_position >= 0:
                        pending_excerpt = sentence
                        pending_start = line_offset + max(local_offset, 0) + raw_position
                    else:
                        pending_excerpt = raw_excerpt
                        pending_start = line_offset + max(local_offset, 0)
                    unmapped.append({
                        "source_file": source.relative_path,
                        "line_start": line_no,
                        "line_end": line_no,
                        "char_start": pending_start,
                        "char_end": pending_start + len(pending_excerpt),
                        "text": sentence,
                        "source_excerpt": pending_excerpt,
                        "reason": "AUTHOR-PENDING: split fragment failed assertion check",
                    })
                    cursor = position + len(sentence)
                    continue
                ordinal += 1
                raw_position = raw_excerpt.find(sentence, min(cursor, len(raw_excerpt)))
                if raw_position >= 0:
                    excerpt = sentence
                    start = line_offset + max(local_offset, 0) + raw_position
                else:
                    # Decoding CSV/JS escapes can make the learner-facing
                    # statement differ from the literal source bytes. Keep the
                    # exact raw cell span alongside the decoded statement.
                    excerpt = raw_excerpt
                    start = line_offset + max(local_offset, 0)
                end = start + len(excerpt)
                propositions.append(Proposition(source.relative_path, line_no, line_no, sentence, ordinal, start, end, excerpt))
                cursor = position + len(sentence)
        if suffix in {".json", ".ts", ".tsx", ".js", ".jsx"} and re.search(
            r":\s*(?:-?\d+(?:\.\d+)?|true|false|null|\[|\{)(?:\s*[,}\]]|\s*$)", raw_line, re.IGNORECASE
        ):
            unmapped.append({
                "source_file": source.relative_path,
                "line_start": line_no,
                "line_end": line_no,
                "char_start": line_offset,
                "char_end": line_offset + len(raw_line),
                "text": raw_line.strip(),
                "source_excerpt": raw_line,
                "evidence_kind": "structured-non-string-field",
                "reason": "AUTHOR-PENDING: numeric, boolean, null, array, or object field requires structured author review",
            })
    return propositions, unmapped


def stable_claim_id(topic_id: str, proposition: Proposition) -> str:
    identity = "\0".join((topic_id, proposition.relative_path, str(proposition.char_start), str(proposition.char_end), _clean_statement(proposition.statement), str(proposition.ordinal)))
    return f"{topic_id}-CLAIM-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:12].upper()}"


def load_source_manifest(topic_dir: Path, manifest_name: str) -> tuple[list[SourceSpec], str]:
    relative = _safe_relative(manifest_name, "source manifest")
    path = resolve_source(topic_dir, relative)
    if path.suffix.lower() != ".json":
        raise ValueError("source manifest must be a JSON file")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid source manifest JSON: {relative}") from exc
    if not isinstance(document, dict):
        raise ValueError("source manifest must be a JSON object")
    values = document.get("source_files", document.get("files"))
    if not isinstance(values, list) or not values:
        raise ValueError("source manifest must contain a non-empty source_files/files array")
    specs: list[SourceSpec] = []
    for index, item in enumerate(values):
        if isinstance(item, str):
            name = item
            root_alias = "topic"
            expected_digest = None
        elif isinstance(item, dict):
            name = str(item.get("path") or item.get("relative_path") or item.get("file") or "")
            root_alias = str(item.get("root_alias") or "topic")
            expected_digest = item.get("sha256")
        else:
            name = ""
        if not name:
            raise ValueError(f"source manifest entry {index} has no relative path")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", root_alias):
            raise ValueError(f"source manifest entry {index} has invalid root_alias")
        if expected_digest is not None and not re.fullmatch(r"sha256:[0-9a-f]{64}", str(expected_digest)):
            raise ValueError(f"source manifest entry {index} has invalid sha256")
        specs.append(SourceSpec(root_alias, _safe_relative(name, f"source manifest entry {index}"), str(expected_digest) if expected_digest else None))
    keys = [(item.root_alias, item.relative_path) for item in specs]
    if len(set(keys)) != len(keys):
        raise ValueError("source manifest contains duplicate source paths")
    return sorted(specs, key=lambda item: (item.root_alias, item.relative_path)), sha256_bytes(path.read_bytes())


def build_draft(
    topic_id: str,
    topic_dir: Path,
    source_files: Sequence[str | SourceSpec],
    source_manifest: str | None = None,
    source_roots: dict[str, Path] | None = None,
) -> dict[str, object]:
    topic_id = topic_id.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", topic_id):
        raise ValueError(f"unsafe topic id: {topic_id}")
    manifest_digest: str | None = None
    if source_manifest:
        manifest_files, manifest_digest = load_source_manifest(topic_dir, source_manifest)
        explicit_specs = [item if isinstance(item, SourceSpec) else SourceSpec("topic", item) for item in source_files]
        if source_files and {(item.root_alias, item.relative_path) for item in explicit_specs} != {(item.root_alias, item.relative_path) for item in manifest_files}:
            raise ValueError("explicit source files do not exactly match source manifest")
        source_files = manifest_files
    if not source_files:
        source_files = [SourceSpec("topic", name) for name in DEFAULT_SOURCE_FILES if (topic_dir / name).is_file()]
    if not source_files:
        raise ValueError("at least one source file is required")
    normalized = [item if isinstance(item, SourceSpec) else SourceSpec("topic", _safe_relative(item, "source file")) for item in source_files]
    normalized = [SourceSpec(item.root_alias, _safe_relative(item.relative_path, "source file"), item.expected_digest) for item in normalized]
    keys = [(item.root_alias, item.relative_path) for item in normalized]
    if len(set(keys)) != len(keys):
        raise ValueError("source file list contains duplicates")
    sources = [load_source(topic_dir, item, source_roots=source_roots) for item in sorted(normalized, key=lambda item: (item.root_alias, item.relative_path))]
    all_props: list[Proposition] = []
    all_unmapped: list[dict[str, object]] = []
    for source in sources:
        props, unmapped = extract_propositions(source)
        all_props.extend(props)
        all_unmapped.extend(unmapped)
    # Duplicate candidate text at distinct source locators is not silently
    # deduplicated: each occurrence is an evidence surface for the auditor.
    claims = []
    seen_ids: set[str] = set()
    for prop in sorted(all_props, key=lambda item: (item.relative_path, item.line_start, item.line_end, item.ordinal, item.statement)):
        claim_id = stable_claim_id(topic_id, prop)
        if claim_id in seen_ids:
            raise ValueError(f"stable claim id collision: {claim_id}")
        seen_ids.add(claim_id)
        claims.append({
            "claim_id": claim_id,
            "statement": prop.statement,
            "claim_type": AUTHOR_PENDING,
            "risk": AUTHOR_PENDING,
            "scope": AUTHOR_PENDING,
            "source_locations": [f"{prop.relative_path}:L{prop.line_start}-L{prop.line_end}"],
            "character_offset": {"start": prop.char_start, "end": prop.char_end},
            "source_excerpt": prop.source_excerpt,
            "required_dimensions": [AUTHOR_PENDING],
            "proposed_disposition": AUTHOR_PENDING,
            "author_status": AUTHOR_PENDING,
        })
    if not claims:
        raise ValueError("selected frozen sources produced zero claim candidates")
    # A null count is intentional: the compiler has not attested completeness.
    # The review queue is the authoritative place to decide whether all prose
    # propositions were mapped.  Never use numeric zero in an author draft.
    return {
        "schema_version": "claim-list.author.v1",
        "extractor": {"name": SCRIPT_VERSION, "deterministic": True},
        "topic_id": topic_id,
        "reviewed_by": AUTHOR_PENDING,
        "independent_review": False,
        "unmapped_propositions": {"status": AUTHOR_PENDING, "count": None, "items": all_unmapped},
        "source_files": [
            {"root_alias": source.relative_path.split(":", 1)[0], "path": source.relative_path.split(":", 1)[1], "sha256": source.digest, "line_count": source.line_count}
            for source in sources
        ],
        "source_manifest": ({"path": _safe_relative(source_manifest, "source manifest"), "sha256": manifest_digest} if source_manifest else None),
        "source_roots": [
            {"root_alias": alias, "runtime_path": str(path.resolve(strict=True))}
            for alias, path in sorted((source_roots or {}).items())
        ],
        "claims": claims,
        "status": "AUTHOR-DRAFT",
    }


def _topic_dirs(topics_root: Path, topic_ids: Sequence[str] | None) -> list[tuple[str, Path]]:
    root = topics_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("topics root must be a directory")
    if topic_ids:
        names = list(topic_ids)
        if len(names) != len(set(names)):
            raise ValueError("topic id list contains duplicates")
    else:
        names = sorted(item.name for item in root.iterdir() if item.is_dir() and not item.is_symlink())
    result: list[tuple[str, Path]] = []
    for name in sorted(names):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", name):
            raise ValueError(f"unsafe topic id: {name}")
        path = (root / name).resolve(strict=True)
        if not _contained(root, path) or not path.is_dir():
            raise ValueError(f"topic directory escapes topics root: {name}")
        result.append((name, path))
    if not result:
        raise ValueError("no topic directories selected")
    return result


def _source_names(topic_dir: Path, explicit: Sequence[str], patterns: Sequence[str], source_manifest: str | None = None) -> list[SourceSpec]:
    if explicit:
        return [SourceSpec("topic", item) for item in explicit]
    if source_manifest:
        return load_source_manifest(topic_dir, source_manifest)[0]
    if not patterns:
        return [SourceSpec("topic", name) for name in DEFAULT_SOURCE_FILES if (topic_dir / name).is_file()]
    selected: set[str] = set()
    for pattern in patterns or ("*.md",):
        for path in topic_dir.glob(pattern):
            if path.is_file() and not path.is_symlink():
                selected.add(path.relative_to(topic_dir).as_posix())
    names = sorted(selected)
    if not names:
        raise ValueError(f"no source files selected under {topic_dir}")
    return [SourceSpec("topic", name) for name in names]


def write_json(path: Path, value: dict[str, object], overwrite: bool, input_paths: Sequence[Path] = ()) -> None:
    if not re.fullmatch(r"claim-list\.author(?:[A-Za-z0-9._-]*)?\.json", path.name):
        raise ValueError("output name must match claim-list.author*.json")
    resolved_output = path.resolve()
    if any(resolved_output == source.resolve() for source in input_paths):
        raise ValueError("output must not overwrite an input source")
    if path.exists() and not overwrite:
        raise ValueError(f"output already exists; use --overwrite explicitly: {path}")
    root = path.parent.resolve(strict=True)
    if not _contained(root, path.resolve()):
        raise ValueError(f"output must be a child of topic directory: {path}")
    encoded = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(root))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass


def run(
    topics_root: Path,
    topic_ids: Sequence[str] | None,
    source_files: Sequence[str],
    source_patterns: Sequence[str],
    output_name: str,
    dry_run: bool,
    overwrite: bool,
    source_manifest: str | None = None,
    source_roots: dict[str, Path] | None = None,
) -> list[dict[str, object]]:
    output_relative = _safe_relative(output_name, "output name")
    if Path(output_relative).name != output_relative:
        raise ValueError("output name must be a file directly inside each topic directory")
    if not re.fullmatch(r"claim-list\.author(?:[A-Za-z0-9._-]*)?\.json", output_relative):
        raise ValueError("output name must match claim-list.author*.json")
    results: list[dict[str, object]] = []
    for topic_id, topic_dir in _topic_dirs(topics_root, topic_ids):
        names = _source_names(topic_dir, source_files, source_patterns, source_manifest)
        draft = build_draft(topic_id, topic_dir, names, source_manifest, source_roots)
        output_path = topic_dir / output_relative
        if not dry_run:
            input_paths = [resolve_source(topic_dir, item.relative_path, root_alias=item.root_alias, source_roots=source_roots) for item in names]
            write_json(output_path, draft, overwrite, input_paths + ([topic_dir / source_manifest] if source_manifest else []))
        results.append({
            "topic_id": topic_id,
            "source_count": len(draft["source_files"]),
            "claim_count": len(draft["claims"]),
            "unmapped_status": draft["unmapped_propositions"]["status"],
            "output": str(output_path),
            "written": not dry_run,
        })
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topics-root", required=True, type=Path)
    parser.add_argument("--source-root", action="append", default=[], metavar="ALIAS=PATH", help="allowlisted cross-root source binding; repeatable")
    parser.add_argument("--topic-id", action="append", help="repeatable; omit to process all direct topic directories")
    parser.add_argument("--source-file", action="append", default=[], help="topic-relative frozen source file; repeatable")
    parser.add_argument("--source-glob", action="append", default=[], help="topic-relative glob when --source-file is omitted")
    parser.add_argument("--source-manifest", help="topic-relative JSON manifest containing source_files/files")
    parser.add_argument("--output-name", default="claim-list.author.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        source_roots: dict[str, Path] = {}
        for binding in args.source_root:
            if "=" not in binding:
                raise ValueError(f"--source-root must use ALIAS=PATH: {binding}")
            alias, raw_path = binding.split("=", 1)
            if alias in source_roots:
                raise ValueError(f"duplicate source root alias: {alias}")
            source_roots[alias] = Path(raw_path)
        results = run(args.topics_root, args.topic_id, args.source_file, args.source_glob, args.output_name, args.dry_run, args.overwrite, args.source_manifest, source_roots)
    except (OSError, ValueError) as exc:
        print(f"BLOCKED-AUTHOR-CLAIM-DRAFT: {exc}", file=sys.stderr)
        return 2
    for result in results:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
