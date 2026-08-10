#!/usr/bin/env python3
"""Validate downloadable labs, archives, syntax and red/green execution paths."""

from __future__ import annotations

import json
import argparse
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ROOT / "public/materials"
BUNDLES = (
    "requirements-to-evidence",
    "agent-load-stability",
    "api-ai-automation",
    "ui-mobile-automation",
    "reliability-chaos-observability",
    "quality-platform-integrations",
)


def run(command: list[str], cwd: Path, expected: int) -> None:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if completed.returncode != expected:
        raise AssertionError(
            f"expected exit {expected}, got {completed.returncode}: {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


def validate_archive(name: str) -> None:
    folder = MATERIALS / name
    archive = MATERIALS / f"{name}.zip"
    if not folder.is_dir() or not archive.is_file():
        raise AssertionError(f"missing material folder or archive for {name}")
    expected = {
        f"{name}/{path.relative_to(folder).as_posix()}": path.read_bytes()
        for path in folder.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    with zipfile.ZipFile(archive) as zipped:
        actual_names = {item.filename for item in zipped.infolist() if not item.is_dir()}
        if actual_names != set(expected):
            missing = sorted(set(expected) - actual_names)
            extra = sorted(actual_names - set(expected))
            raise AssertionError(f"stale archive {archive.name}; missing={missing}, extra={extra}")
        for member, content in expected.items():
            if zipped.read(member) != content:
                raise AssertionError(f"archive content drift: {archive.name}:{member}")


def validate_syntax() -> None:
    for path in MATERIALS.rglob("*.py"):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    for path in MATERIALS.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))


def validate_requirements_lab(temp: Path) -> None:
    lab = temp / "requirements"
    shutil.copytree(MATERIALS / "requirements-to-evidence", lab)
    run([sys.executable, "pipeline.py", "reset"], lab, 0)
    run([sys.executable, "pipeline.py", "all", "--report", "reports/ci-baseline.json"], lab, 0)
    run([sys.executable, "pipeline.py", "inject-code-defect"], lab, 0)
    run([sys.executable, "pipeline.py", "all", "--report", "reports/ci-mutation.json"], lab, 1)
    run([sys.executable, "pipeline.py", "repair"], lab, 0)
    run([sys.executable, "pipeline.py", "all", "--report", "reports/ci-repair.json"], lab, 0)


def validate_agent_lab(temp: Path) -> None:
    lab = MATERIALS / "agent-load-stability"
    cases = (("baseline", 0), ("retry-storm", 1), ("repaired", 0))
    for name, expected in cases:
        run([
            sys.executable, "agent_load_lab.py", "--config", f"configs/{name}.json",
            "--output", str(temp / f"agent-{name}"),
        ], lab, expected)


def validate_api_lab(temp: Path) -> None:
    lab = temp / "api-ai-automation"
    shutil.copytree(MATERIALS / "api-ai-automation", lab)
    for mode, expected in (("baseline", 0), ("mutation", 1), ("repair", 0)):
        run([
            sys.executable, "scripts/api_automation.py", mode,
            "--report", f"reports/ci-{mode}.json",
        ], lab, expected)


def validate_ui_lab(temp: Path) -> None:
    lab = temp / "ui-mobile-automation"
    shutil.copytree(MATERIALS / "ui-mobile-automation", lab)
    run([sys.executable, "scripts/ui_contract_lab.py", "validate"], lab, 0)
    for mode, expected in (("baseline", 0), ("mutation", 1), ("repair", 0)):
        run([
            sys.executable, "scripts/ui_contract_lab.py", mode,
            "--report", f"reports/ci-{mode}.json",
        ], lab, expected)


def validate_reliability_lab(temp: Path) -> None:
    lab = temp / "reliability-chaos-observability"
    shutil.copytree(MATERIALS / "reliability-chaos-observability", lab)
    for config, expected in (("baseline", 0), ("fault", 1), ("repaired", 0)):
        run([
            sys.executable, "scripts/reliability_lab.py",
            "--config", f"configs/{config}.json",
            "--output", f"evidence/ci-{config}",
        ], lab, expected)


def validate_quality_platform_lab(temp: Path) -> None:
    copied = temp / "quality-platform-integrations"
    shutil.copytree(MATERIALS / "quality-platform-integrations", copied)
    lab = copied / "learner-materials"
    for mode, expected in (("baseline", 0), ("mutation", 1), ("repair", 0)):
        run([
            sys.executable, "scripts/quality_platform.py", mode,
            "--report", f"reports/ci-{mode}.json",
        ], lab, expected)
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], lab, 0)


def main() -> int:
    global MATERIALS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "materials_root",
        nargs="?",
        type=Path,
        default=MATERIALS,
        help="Material directory containing bundle folders and matching zip archives.",
    )
    args = parser.parse_args()
    MATERIALS = args.materials_root.resolve()
    try:
        validate_syntax()
        for bundle in BUNDLES:
            validate_archive(bundle)
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            validate_requirements_lab(temp)
            validate_agent_lab(temp)
            validate_api_lab(temp)
            validate_ui_lab(temp)
            validate_reliability_lab(temp)
            validate_quality_platform_lab(temp)
    except (AssertionError, OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        print(f"Learner materials invalid: {exc}", file=sys.stderr)
        return 1
    print("Learner materials valid: syntax, archive parity, and six independent red/green labs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
