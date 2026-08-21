#!/usr/bin/env python3
"""Build a hash-bound, page-exact source manifest for claim extraction.

This is a provenance index only.  It does not classify claims, approve an
overlay, or create provider research receipts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_TOPIC_FILES = (
    "research-brief.md", "source-pack.csv", "research-runs.json",
    "evidence-synthesis.md", "engineering-blueprint.md", "manuscript.md",
    "comparison.md", "lab-manifest.json", "validation.md",
    "projection-ledger.json",
)
TEXT_SUFFIXES = {".md", ".markdown", ".json", ".csv", ".ts", ".tsx", ".js", ".jsx", ".svg"}


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def safe_rel(path: Path, root: Path) -> str:
    try:
        value = path.resolve(strict=True).relative_to(root.resolve(strict=True)).as_posix()
    except ValueError as exc:
        raise ValueError(f"source escapes root: {path}") from exc
    if not value or value.startswith("../"):
        raise ValueError(f"unsafe source path: {path}")
    return value


def load_catalog(path: Path) -> tuple[list[str], str]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    scope = doc.get("release_scope") if isinstance(doc.get("release_scope"), dict) else {}
    ids = scope.get("promised_page_ids") or doc.get("promised_page_ids") or doc.get("page_ids")
    if not isinstance(ids, list) or not ids or len(ids) != len(set(map(str, ids))):
        raise ValueError("catalog must contain unique promised page IDs")
    return [str(item) for item in ids], digest(path)


def candidate_files(repo: Path, page_id: str, reference_index: dict[str, list[tuple[str, Path]]] | None = None) -> list[dict[str, Any]]:
    roots = {
        "site": repo / "site" / "content",
        "content": repo / "content",
        "course": repo / "courses",
        "methodology": repo / "methodology",
        "material": repo / "site" / "public" / "materials",
    }
    selected: dict[tuple[str, str], dict[str, Any]] = {}

    def add(alias: str, path: Path, role: str) -> None:
        if not path.is_file() or path.is_symlink() or path.suffix.lower() not in TEXT_SUFFIXES:
            return
        if path.stat().st_size > 5_000_000:
            return
        root = roots[alias]
        key = (alias, safe_rel(path, root))
        selected.setdefault(key, {"root_alias": alias, "path": key[1], "sha256": digest(path), "roles": []})
        if role not in selected[key]["roles"]:
            selected[key]["roles"].append(role)

    # The topic package is the page's local evidence surface.
    topic = repo / "research" / "topics" / page_id
    for name in DEFAULT_TOPIC_FILES:
        path = topic / name
        if path.is_file():
            key = ("topic", name)
            selected[key] = {"root_alias": "topic", "path": name, "sha256": digest(path), "roles": ["topic-package"]}

    # Keep the assembly authorities even when a module file does not repeat the
    # page ID in a searchable literal.
    for path in (repo / "site" / "content" / "course.ts", repo / "site" / "content" / "page-document-contracts.ts"):
        add("site", path, "assembly-authority")

    references = reference_index.get(page_id, []) if reference_index is not None else []
    for alias, path in references:
        # Exclude giant generated/archive trees; source and public material
        # paths are intentionally included because their hashes are part of the
        # claim freshness boundary.
        add(alias, path, "page-reference")

    return sorted(selected.values(), key=lambda item: (item["root_alias"], item["path"]))


def source_root(repo: Path, alias: str, page_id: str) -> Path:
    roots = {
        "topic": repo / "research" / "topics" / page_id,
        "site": repo / "site" / "content",
        "content": repo / "content",
        "course": repo / "courses",
        "methodology": repo / "methodology",
        "material": repo / "site" / "public" / "materials",
    }
    if alias not in roots:
        raise ValueError(f"unknown source root alias: {alias}")
    return roots[alias].resolve(strict=True)


def validate_freshness(document: dict[str, Any], repo: Path) -> list[str]:
    """Re-read every manifest entry and fail closed on any source drift."""
    errors: list[str] = []
    catalog = document.get("catalog_manifest", {})
    try:
        catalog_path = (repo / str(catalog.get("path", ""))).resolve(strict=True)
        if digest(catalog_path) != catalog.get("sha256"):
            errors.append("catalog manifest digest mismatch")
    except (OSError, ValueError):
        errors.append("catalog manifest is missing or unsafe")
    seen_pages: set[str] = set()
    for page in document.get("pages", []):
        if not isinstance(page, dict):
            errors.append("page entry is not an object")
            continue
        page_id = str(page.get("page_id", ""))
        if not page_id or page_id in seen_pages:
            errors.append(f"duplicate or empty page_id: {page_id}")
        seen_pages.add(page_id)
        entries = page.get("source_files", [])
        if page.get("source_count") != len(entries):
            errors.append(f"source_count mismatch: {page_id}")
        for entry in entries:
            if not isinstance(entry, dict):
                errors.append(f"source entry is not an object: {page_id}")
                continue
            alias, relative, expected = str(entry.get("root_alias", "")), str(entry.get("path", "")), entry.get("sha256")
            try:
                root = source_root(repo, alias, page_id)
                path = (root / relative).resolve(strict=True)
                path.relative_to(root)
                actual = digest(path)
                if actual != expected:
                    errors.append(f"source hash mismatch: {page_id}:{alias}:{relative}")
            except (OSError, ValueError):
                errors.append(f"source path missing or escapes root: {page_id}:{alias}:{relative}")
    expected_ids = list(map(str, catalog.get("page_ids", [])))
    if expected_ids != sorted(seen_pages) and set(expected_ids) != seen_pages:
        errors.append("source manifest page set does not match catalog")
    return errors


def build(repo: Path, catalog_path: Path, output: Path) -> dict[str, Any]:
    repo = repo.resolve(strict=True)
    catalog_path = catalog_path.resolve(strict=True)
    if repo not in catalog_path.parents:
        raise ValueError("catalog must be inside package root")
    page_ids, catalog_digest = load_catalog(catalog_path)
    pages = []
    roots = {
        "site": repo / "site" / "content", "content": repo / "content",
        "course": repo / "courses", "methodology": repo / "methodology",
        "material": repo / "site" / "public" / "materials",
    }
    reference_index: dict[str, list[tuple[str, Path]]] = {page_id: [] for page_id in page_ids}
    # Scan each source root once; repeatedly rescanning the whole course for
    # every page would make the manifest needlessly expensive.
    for alias, root in roots.items():
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.is_symlink() or path.suffix.lower() not in TEXT_SUFFIXES or path.stat().st_size > 5_000_000:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for page_id in page_ids:
                if page_id in text:
                    reference_index[page_id].append((alias, path))
    missing_topics = []
    for page_id in page_ids:
        topic = repo / "research" / "topics" / page_id
        if not topic.is_dir():
            missing_topics.append(page_id)
        sources = candidate_files(repo, page_id, reference_index)
        if not sources:
            raise ValueError(f"page has no source files: {page_id}")
        pages.append({"page_id": page_id, "source_files": sources, "source_count": len(sources)})
    if missing_topics:
        raise ValueError("missing topic directories: " + ", ".join(missing_topics))
    document = {
        "schema_version": "claim-source-manifest.v1",
        "manifest_id": "claim-sources-" + hashlib.sha256((catalog_digest + "\0" + "\n".join(page_ids)).encode()).hexdigest()[:16],
        "catalog_manifest": {"path": safe_rel(catalog_path, repo), "sha256": catalog_digest, "page_ids": page_ids},
        "page_count": len(pages),
        "pages": pages,
        "status": "READY-SOURCE-MANIFEST",
        "cannot_prove": [
            "Claim classification, independent review, provider research, target evidence, saturation, and publication are not established by this manifest."
        ],
    }
    output = output.resolve()
    if repo not in output.parents:
        raise ValueError("output must be inside package root")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--catalog", default="research/catalog-manifest.json", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        doc = build(args.package_root, args.package_root / args.catalog if not args.catalog.is_absolute() else args.catalog, args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"BLOCKED-SOURCE-MANIFEST: {exc}")
        return 2
    print(json.dumps({"status": doc["status"], "page_count": doc["page_count"], "source_count": sum(item["source_count"] for item in doc["pages"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
