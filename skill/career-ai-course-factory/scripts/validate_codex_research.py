#!/usr/bin/env python3
"""Validate one topic's Codex-native research contract."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from codex_research_contract import validate_codex_topic
from run_claim_deep_research import safe_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--topic-id", required=True)
    parser.add_argument("--allow-missing-saturation", action="store_true")
    args = parser.parse_args()
    try:
        topic_id = safe_id(args.topic_id, "topic id")
        topic_dir = args.package_root.resolve() / "research" / "topics" / topic_id
        errors = validate_codex_topic(topic_dir, require_saturation=not args.allow_missing_saturation)
        if errors:
            raise ValueError("; ".join(errors))
        print(f"PASS-CODEX-RESEARCH topic_id={topic_id}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"BLOCKED-CODEX-RESEARCH: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
