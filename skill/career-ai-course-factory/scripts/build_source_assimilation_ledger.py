#!/usr/bin/env python3
"""Inventory Markdown/text sources into a fail-closed assimilation ledger scaffold."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LIST_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
OBLIGATION_PATTERNS = {
    "career-evolution-system": [
        re.compile(pattern, re.IGNORECASE) for pattern in (
            r"职业(?:发展|演进|定位|阶段|路径)", r"职级", r"晋升", r"P5\s*[-–—~至到]\s*P9",
            r"career\s+(?:development|evolution|ladder|level|path)", r"promotion\s+(?:criteria|cycle|path)",
        )
    ],
    "agent-architecture-testing": [
        re.compile(pattern, re.IGNORECASE) for pattern in (
            r"AI\s*Agent.{0,24}(?:架构|测试|评测)", r"Agent.{0,24}(?:架构|测试维度|测试体系)",
            r"(?:多\s*Agent|multi[- ]agent).{0,24}(?:编排|交接|orchestration|handoff)",
            r"agent\s+architecture", r"D0.{0,80}D1.{0,80}D2",
        )
    ],
}


def digest_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def detect_source_obligations(text: str) -> list[str]:
    return sorted(
        obligation for obligation, patterns in OBLIGATION_PATTERNS.items()
        if any(pattern.search(text) for pattern in patterns)
    )


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value.lower()).strip("-")
    return slug[:64] or "section"


def _coverage_item(item_id: str, source_id: str, locator: str, start: int, end: int, text: str, kind: str) -> dict[str, Any]:
    return {
        "id": item_id,
        "source_id": source_id,
        "locator": locator,
        "start_line": start,
        "end_line": end,
        "sha256": digest_text(text),
        "kind": kind,
        "meaning": "",
        "claim_type": "content",
        "disposition": "UNMAPPED",
        "target_refs": [],
        "rationale": "",
        "owner": "",
        "evidence_refs": [],
    }


def inventory_source(path: Path, source_id: str, package_root: Path | None = None) -> dict[str, Any]:
    path = path.resolve()
    package_root = package_root.resolve() if package_root is not None else None
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    heading_rows: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines, start=1):
        match = HEADING_RE.match(line)
        if match:
            heading_rows.append((index, len(match.group(1)), match.group(2).strip()))
    if not heading_rows:
        heading_rows = [(1, 0, "Document")]

    sections: list[dict[str, Any]] = []
    atoms: list[dict[str, Any]] = []
    for section_index, (start, level, title) in enumerate(heading_rows, start=1):
        end = (heading_rows[section_index][0] - 1) if section_index < len(heading_rows) else max(1, len(lines))
        section_text = "\n".join(lines[start - 1:end])
        section_id = f"{source_id}-section-{section_index:04d}-{_slug(title)}"
        section = _coverage_item(section_id, source_id, f"{title} (L{start}-L{end})", start, end, section_text, "section")
        section["level"] = level
        section["title"] = title
        sections.append(section)

        body_start = start + (1 if level else 0)
        cursor = body_start
        atom_index = 0
        while cursor <= end:
            line = lines[cursor - 1]
            if not line.strip() or HEADING_RE.match(line):
                cursor += 1
                continue
            atom_start = cursor
            if line.lstrip().startswith("```"):
                kind = "code"
                cursor += 1
                while cursor <= end and not lines[cursor - 1].lstrip().startswith("```"):
                    cursor += 1
                cursor = min(end + 1, cursor + 1)
            elif line.lstrip().startswith("|"):
                kind = "table"
                cursor += 1
                while cursor <= end and lines[cursor - 1].lstrip().startswith("|"):
                    cursor += 1
            elif LIST_RE.match(line):
                kind = "list"
                cursor += 1
                while cursor <= end and (LIST_RE.match(lines[cursor - 1]) or lines[cursor - 1].startswith(("  ", "\t"))):
                    cursor += 1
            else:
                kind = "paragraph"
                cursor += 1
                while cursor <= end:
                    candidate = lines[cursor - 1]
                    if not candidate.strip() or HEADING_RE.match(candidate) or candidate.lstrip().startswith(("```", "|")) or LIST_RE.match(candidate):
                        break
                    cursor += 1
            atom_end = cursor - 1
            atom_text = "\n".join(lines[atom_start - 1:atom_end]).strip()
            if atom_text:
                atom_index += 1
                atom_id = f"{source_id}-atom-{section_index:04d}-{atom_index:04d}"
                atom = _coverage_item(atom_id, source_id, f"{title}#{atom_index} (L{atom_start}-L{atom_end})", atom_start, atom_end, atom_text, kind)
                atom["section_id"] = section_id
                atoms.append(atom)

    suffix = path.suffix.lower()
    source_format = "markdown" if suffix in {".md", ".markdown"} else "text" if suffix in {".txt", ".text"} else "other"
    source_path = path.relative_to(package_root).as_posix() if package_root is not None else str(path)
    return {
        "source": {
            "source_id": source_id,
            "path": source_path,
            "sha256": digest_file(path),
            "authority": "USER-PROVIDED-UNADJUDICATED",
            "scope": "candidate professional input; not universal policy",
            "owner": "UNASSIGNED",
            "format": source_format,
            "detected_obligations": detect_source_obligations(text),
        },
        "sections": sections,
        "atoms": atoms,
    }


def build_ledger(sources: list[tuple[str, Path]], package_root: Path | None = None) -> dict[str, Any]:
    inventories = [inventory_source(path, source_id, package_root) for source_id, path in sources]
    sections = [item for inventory in inventories for item in inventory["sections"]]
    atoms = [item for inventory in inventories for item in inventory["atoms"]]
    return {
        "schema_version": "1.0",
        "inventory_version": "source-assimilation-v1",
        "sources": [inventory["source"] for inventory in inventories],
        "sections": sections,
        "atoms": atoms,
        "coverage_receipt": {
            "source_count": len(inventories),
            "section_count": len(sections),
            "atom_count": len(atoms),
            "accounted_section_count": 0,
            "accounted_atom_count": 0,
            "disposition_counts": {"UNMAPPED": len(sections) + len(atoms)},
            "unaccounted_ids": [item["id"] for item in sections + atoms],
            "inventory_command": "",
            "reviewer": "",
            "reviewed_at": "",
            "verdict": "BLOCKED",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", required=True, help="SOURCE_ID=PATH; repeat for every source")
    parser.add_argument("--output", required=True)
    parser.add_argument("--package-root", default=".", help="Package root containing frozen source copies")
    args = parser.parse_args()
    package_root = Path(args.package_root).expanduser().resolve()
    sources: list[tuple[str, Path]] = []
    for value in args.source:
        source_id, separator, raw_path = value.partition("=")
        if not separator or not source_id.strip() or not raw_path.strip():
            parser.error("--source must use SOURCE_ID=PATH")
        path = Path(raw_path).expanduser().resolve()
        if not path.is_file():
            parser.error(f"source file does not exist: {path}")
        try:
            path.relative_to(package_root)
        except ValueError:
            parser.error(f"source must be a frozen package-local file under {package_root}: {path}")
        sources.append((source_id.strip(), path))
    ledger = build_ledger(sources, package_root)
    ledger["coverage_receipt"]["inventory_command"] = " ".join(["build_source_assimilation_ledger.py"] + [f"--source {source_id}={path}" for source_id, path in sources])
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"BLOCKED: wrote {len(ledger['sections'])} sections and {len(ledger['atoms'])} atoms to {output}; adjudicate every UNMAPPED item")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
