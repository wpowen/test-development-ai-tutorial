#!/usr/bin/env python3
"""Check or sync the canonical factory Skill into its installed runtime copy."""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


IGNORED_NAMES = {"__pycache__"}


def _same_tree(source: Path, target: Path) -> bool:
    if not target.is_dir():
        return False
    comparison = filecmp.dircmp(source, target, ignore=sorted(IGNORED_NAMES))
    if comparison.left_only or comparison.right_only or comparison.common_funny:
        return False
    for name in comparison.common_files:
        if not filecmp.cmp(source / name, target / name, shallow=False):
            return False
    for name in comparison.common_dirs:
        if not _same_tree(source / name, target / name):
            return False
    return True


def sync(source: Path, target: Path, *, write: bool) -> bool:
    source = source.resolve(strict=True)
    target = target.expanduser().resolve()
    if source == target:
        raise ValueError("canonical and installed Skill paths must differ")
    if not write:
        return _same_tree(source, target)
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_name(f".{target.name}.sync-staging")
    if staging.exists():
        shutil.rmtree(staging)
    shutil.copytree(source, staging, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    if target.exists():
        shutil.rmtree(target)
    staging.rename(target)
    return _same_tree(source, target)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--installed", type=Path, default=Path.home() / ".codex/skills/career-ai-course-factory")
    parser.add_argument("--sync", action="store_true", help="copy canonical into installed runtime directory")
    args = parser.parse_args()
    try:
        equal = sync(args.canonical, args.installed, write=args.sync)
    except (OSError, ValueError) as exc:
        print(f"BLOCKED-SKILL-SYNC: {exc}")
        return 2
    print("PASS skill trees are identical" if equal else "BLOCKED skill trees differ")
    return 0 if equal else 1


if __name__ == "__main__":
    raise SystemExit(main())
