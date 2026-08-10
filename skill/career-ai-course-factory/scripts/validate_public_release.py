#!/usr/bin/env python3
"""Fail-closed validation for learner-facing career-course release archives."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


INCOMPLETE = {"planned", "outlined", "blocked"}
PLACEHOLDERS = ("仅保留知识位置", "本页尚未开发", "本页尚未通过逐题研究", "仅提纲")
REQUIRED_MANIFEST_FIELDS = {
    "schema_version", "source_commit", "release_scope", "catalog_complete",
    "page_count", "delivered_page_count", "promised_page_ids", "content_hash",
    "validation_verdict", "publication_targets", "learner_artifact_roots",
}


def load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read JSON {path}: {exc}")
        return None


def normalized_hash(root: Path, artifact_roots: list[str]) -> str:
    digest = hashlib.sha256()
    files: list[Path] = []
    for relative in artifact_roots:
        base = root / relative
        if base.is_file():
            files.append(base)
        elif base.is_dir():
            files.extend(path for path in base.rglob("*") if path.is_file())
    for path in sorted(files, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        content = path.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return f"sha256:{digest.hexdigest()}"


def find_incomplete_records(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        delivery = str(value.get("delivery_status", "")).lower()
        status = str(value.get("status", "")).lower()
        if delivery in INCOMPLETE:
            errors.append(f"{path} has incomplete delivery_status={delivery}")
        if status in INCOMPLETE and any(key in value for key in ("page_id", "module_id", "slug", "learner_result")):
            errors.append(f"{path} has incomplete learner record status={status}")
        for key, child in value.items():
            errors.extend(find_incomplete_records(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(find_incomplete_records(child, f"{path}[{index}]"))
    return errors


def validate_release(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"release does not exist: {root}"]
    if (root / "course-package").exists():
        errors.append("public release must not include the internal course-package authoring tree")

    manifest_path = root / "RELEASE-MANIFEST.json"
    tutorial_path = root / "tutorial/tutorial-site.json"
    html_path = root / "site/index.html"
    for path in (manifest_path, tutorial_path, html_path):
        if not path.is_file():
            errors.append(f"missing public release artifact: {path.relative_to(root)}")
    if errors:
        return errors

    manifest = load_json(manifest_path, errors)
    tutorial = load_json(tutorial_path, errors)
    if not isinstance(manifest, dict) or not isinstance(tutorial, dict):
        return errors

    missing_manifest = REQUIRED_MANIFEST_FIELDS - set(manifest)
    if missing_manifest:
        errors.append(f"release manifest missing fields: {', '.join(sorted(missing_manifest))}")

    pages = tutorial.get("pages")
    modules = tutorial.get("modules")
    release_scope = tutorial.get("release_scope")
    if not isinstance(pages, list) or not pages:
        errors.append("public tutorial needs pages")
        pages = []
    if not isinstance(modules, list) or not modules:
        errors.append("public tutorial needs modules")
        modules = []
    if not isinstance(release_scope, dict):
        errors.append("public tutorial release_scope must be an object")
        release_scope = {}

    page_ids = [str(page.get("page_id", "")) for page in pages if isinstance(page, dict)]
    if len(page_ids) != len(pages) or not all(page_ids) or len(set(page_ids)) != len(page_ids):
        errors.append("public tutorial page IDs must be present and unique")
    promised_ids = release_scope.get("promised_page_ids")
    if not isinstance(promised_ids, list) or promised_ids != page_ids:
        errors.append("tutorial promised_page_ids must exactly equal ordered public page IDs")
    if manifest.get("promised_page_ids") != page_ids:
        errors.append("release manifest promised_page_ids must exactly equal ordered public page IDs")
    if manifest.get("page_count") != len(page_ids) or manifest.get("delivered_page_count") != len(page_ids):
        errors.append("release manifest page counts must equal the public delivered page count")

    incomplete_pages = [
        page_id for page_id, page in zip(page_ids, pages)
        if isinstance(page, dict) and str(page.get("delivery_status", "")).lower() in INCOMPLETE
    ]
    if incomplete_pages:
        errors.append(f"public tutorial contains incomplete pages: {', '.join(incomplete_pages)}")

    module_ids = {str(module.get("module_id", "")) for module in modules if isinstance(module, dict)}
    used_modules = {str(page.get("module_id", "")) for page in pages if isinstance(page, dict)}
    empty_modules = module_ids - used_modules
    if empty_modules:
        errors.append(f"public tutorial contains empty modules: {', '.join(sorted(empty_modules))}")
    if used_modules - module_ids:
        errors.append(f"public pages reference unknown modules: {', '.join(sorted(used_modules - module_ids))}")

    html = html_path.read_text(encoding="utf-8")
    match = re.search(r"const COURSE_DATA=(\{.*?\});const DATA=COURSE_DATA", html, re.DOTALL)
    if not match:
        errors.append("site/index.html lacks parseable embedded COURSE_DATA")
    else:
        try:
            embedded = json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            errors.append(f"site/index.html COURSE_DATA is invalid JSON: {exc}")
        else:
            embedded_ids = [str(page.get("id", "")) for page in embedded.get("pages", []) if isinstance(page, dict)]
            if embedded_ids != page_ids:
                errors.append("site/index.html page IDs differ from tutorial/tutorial-site.json")
            embedded_modules = {str(module.get("id", "")) for module in embedded.get("modules", []) if isinstance(module, dict)}
            if embedded_modules != module_ids:
                errors.append("site/index.html module IDs differ from tutorial/tutorial-site.json")
            for problem in find_incomplete_records(embedded, "COURSE_DATA"):
                errors.append(f"site/index.html {problem}")

    for attribute in ("data-page-id", "data-id", "data-go"):
        for value in re.findall(rf'{attribute}=["\']([^"\']+)["\']', html):
            if value not in page_ids and not value.startswith("${"):
                errors.append(f"site/index.html exposes unknown {attribute}={value}")
    if any(marker in html for marker in PLACEHOLDERS):
        errors.append("site/index.html exposes incomplete-page placeholder copy")

    artifact_roots = manifest.get("learner_artifact_roots")
    if not isinstance(artifact_roots, list) or not artifact_roots or not all(isinstance(item, str) for item in artifact_roots):
        errors.append("release manifest learner_artifact_roots must be a non-empty string list")
        artifact_roots = []
    for relative in artifact_roots:
        if not (root / relative).exists():
            errors.append(f"learner artifact root does not exist: {relative}")
    if artifact_roots:
        actual_hash = normalized_hash(root, artifact_roots)
        if manifest.get("content_hash") != actual_hash:
            errors.append("release manifest content_hash does not match learner artifacts")

    if manifest.get("validation_verdict") != "PASS":
        errors.append("release manifest validation_verdict must be PASS")
    targets = manifest.get("publication_targets")
    if not isinstance(targets, list) or not {"github-pages", "chatgpt-site"}.issubset(set(targets)):
        errors.append("release manifest must declare github-pages and chatgpt-site publication targets")

    for path in root.rglob("*.json"):
        if path == manifest_path or "skill" in path.relative_to(root).parts or ".github" in path.relative_to(root).parts:
            continue
        data = load_json(path, errors)
        if data is None:
            continue
        for problem in find_incomplete_records(data):
            errors.append(f"public JSON {path.relative_to(root)} {problem}")

    for relative in artifact_roots:
        base = root / relative
        candidates = [base] if base.is_file() else list(base.rglob("*")) if base.is_dir() else []
        for path in candidates:
            if path.is_file() and path.suffix.lower() in {".html", ".md", ".txt", ".json"}:
                text = path.read_text(encoding="utf-8", errors="replace")
                if any(marker in text for marker in PLACEHOLDERS):
                    errors.append(f"learner artifact exposes placeholder copy: {path.relative_to(root)}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release", type=Path)
    args = parser.parse_args()
    errors = validate_release(args.release.resolve())
    if errors:
        print("Public release invalid:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    print("Public release valid!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
