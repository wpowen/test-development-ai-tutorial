#!/usr/bin/env python3
"""Scan historical claim lists without guessing their root; always reports migration-needed."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from prepare_claim_inventory import _parse_locator


def scan(package_root: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    parse_fail = 0
    missing = 0
    external_binding_needed = 0
    locator_count = 0
    for claims_file in sorted(package_root.glob("research/topics/*/claim-list.v1.json")):
        topic_id = claims_file.parent.name
        try:
            document = json.loads(claims_file.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            rows.append({"topic_id": topic_id, "status": "migration-needed", "error": str(exc)})
            continue
        topic_fail = 0
        topic_missing = 0
        for claim in document.get("claims", []) if isinstance(document, dict) else []:
            for raw in claim.get("source_locations", []) if isinstance(claim, dict) else []:
                locator_count += 1
                try:
                    alias, relative, *_ = _parse_locator(raw)
                    if alias in {"topic", "package"}:
                        root = claims_file.parent if alias == "topic" else package_root
                        if not (root / relative).is_file():
                            topic_missing += 1
                    else:
                        external_binding_needed += 1
                except (TypeError, ValueError):
                    topic_fail += 1
                    # Diagnostic-only legacy check: this does not select a root,
                    # write an inventory, or promote a source.
                    candidate = claims_file.parent / str(raw).split("#", 1)[0].split(":L", 1)[0]
                    if not candidate.is_file():
                        topic_missing += 1
        parse_fail += topic_fail
        missing += topic_missing
        rows.append({"topic_id": topic_id, "status": "migration-needed" if topic_fail or topic_missing else "legacy-review-needed", "parse_fail": topic_fail, "missing": topic_missing})
    return {
        "schema_version": "locator-migration-report.v1",
        "status": "BLOCKED-MIGRATION-NEEDED",
        "root_resolution": "none; historical locators are not implicitly resolved",
        "topics_scanned": len(rows),
        "locator_count": locator_count,
        "parse_fail": parse_fail,
        "missing": missing,
        "external_binding_needed": external_binding_needed,
        "topics": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = scan(args.package_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "topics_scanned", "locator_count", "parse_fail", "missing")}, ensure_ascii=False))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
