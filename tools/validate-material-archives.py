#!/usr/bin/env python3
"""Validate the complete learner-material projection and executable archives.

The projection is fail-closed across four hops:

1. canonical course-owned files;
2. ``site/public/materials``;
3. an optional static-export ``materials`` directory;
4. each downloadable ZIP member.

Generated report ``run_id`` values are deliberately excluded from the
canonical/source comparison, but the public, static and ZIP bytes must remain
identical. This keeps reruns reproducible without hiding learner-facing drift.
"""

from __future__ import annotations

import json
import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT.parent
MATERIALS = ROOT / "public/materials"
SOURCE_PROJECTIONS = {
    "requirements-to-evidence": PACKAGE_ROOT / "courses/td-ai-011-requirements-to-evidence/lab",
    "api-ai-automation": PACKAGE_ROOT / "courses/td-ai-022-api-ai-automation/learner-materials",
    "ui-mobile-automation": PACKAGE_ROOT / "courses/td-ai-021-ui-mobile-automation/learner-materials",
    "reliability-chaos-observability": PACKAGE_ROOT / "courses/td-ai-020-reliability-chaos-observability/learner-materials",
    # The published bundle intentionally keeps the learner-materials directory
    # because the course contains several independently runnable lab surfaces.
    "quality-platform-integrations": PACKAGE_ROOT / "courses/td-ai-023-quality-platform-integrations",
    # The public layout deliberately preserves learner-materials/ so each
    # command/prompt manifest keeps the same canonical repository path.
    "llm-agent-quality": PACKAGE_ROOT / "courses/td-ai-llm-agent-quality",
}

# New course packages use the stable ``td-ai-<bundle>/learner-materials``
# convention. Discover those projections so adding a bundle cannot silently
# create a public/ZIP-only copy that has no course-owned canonical source.
for course_dir in sorted((PACKAGE_ROOT / "courses").glob("td-ai-*")):
    bundle = course_dir.name.removeprefix("td-ai-")
    learner_materials = course_dir / "learner-materials"
    if learner_materials.is_dir() and (MATERIALS / bundle).is_dir():
        SOURCE_PROJECTIONS.setdefault(bundle, learner_materials)

SOURCE_PREFIXES = {
    "quality-platform-integrations": "learner-materials/",
    "llm-agent-quality": "learner-materials/",
}

# These are local scratch receipts, not declared learner artifacts. Every other
# canonical member must project into the public download package.
SOURCE_ONLY_EXCLUSIONS = {
    "requirements-to-evidence": {
        "reports/baseline-new.json",
        "reports/baseline-new2.json",
        "reports/mutation-new.json",
        "reports/repair-new.json",
    },
}

AGENT_SOURCE_ROOT = PACKAGE_ROOT / "courses/td-ai-010-agent-load-stability"

RELEASE_REQUIRED_ARTIFACTS = (
    "SOLUTION-MANIFEST.json",
    "CATALOG-MANIFEST.json",
    "PAGE-PROMOTION-MANIFEST.json",
    "EXECUTABILITY-MANIFEST.json",
    "ARTIFACT-CLOSURE.json",
)

RELEASE_REQUIRED_HASH_FIELDS = (
    "solution_manifest_hash",
    "catalog_manifest_hash",
    "promotion_manifest_hash",
    "executability_manifest_hash",
    "artifact_closure_hash",
)


def material_files(root: Path) -> dict[str, Path]:
    if not root.is_dir():
        raise AssertionError(f"material directory does not exist: {root}")
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }


def discover_bundles() -> tuple[str, ...]:
    """Use archives as the public bundle registry; never silently skip additions."""
    archives = sorted(path.stem for path in MATERIALS.glob("*.zip") if path.is_file())
    if not archives:
        raise AssertionError(f"no downloadable material bundles found: {MATERIALS}")
    missing_folders = [name for name in archives if not (MATERIALS / name).is_dir()]
    if missing_folders:
        raise AssertionError(f"archive has no canonical public folder: {missing_folders}")
    return tuple(archives)


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def canonical_content(path: Path, relative: str) -> bytes:
    """Return stable source bytes while preserving every learner-facing byte later."""
    content = path.read_bytes()
    if "reports" in Path(relative).parts and path.suffix == ".json":
        parsed = json.loads(content)
        if isinstance(parsed, dict) and "run_id" in parsed:
            parsed = dict(parsed)
            parsed.pop("run_id")
            return json.dumps(parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return content


def assert_projected_file(source: Path, published: Path, relative: str, bundle: str) -> None:
    if not source.is_file():
        raise AssertionError(f"canonical source missing: {bundle}:{relative} -> {source}")
    source_hash = sha256(canonical_content(source, relative))
    published_hash = sha256(canonical_content(published, relative))
    if source_hash != published_hash:
        raise AssertionError(
            f"canonical/public drift: {bundle}:{relative}; "
            f"source_sha256={source_hash}, public_sha256={published_hash}"
        )


def validate_agent_source_projection(folder: Path) -> None:
    files = material_files(folder)
    for relative, published in files.items():
        if relative == "README.md":
            # This is the one packaging-owned entry point. The canonical lab has
            # no README, so validate the commands and evidence boundary instead
            # of pretending that it is a byte-for-byte course projection.
            text = published.read_text(encoding="utf-8")
            required = (
                "agent_load_lab.py",
                "configs/baseline.json",
                "configs/retry-storm.json",
                "configs/repaired.json",
                "0 / 1 / 0",
                "不代表",
            )
            missing = [marker for marker in required if marker not in text]
            if missing:
                raise AssertionError(f"agent packaging README is incomplete; missing={missing}")
            continue
        if relative.startswith("reports/"):
            source = AGENT_SOURCE_ROOT / "evidence" / relative.removeprefix("reports/")
        else:
            source = AGENT_SOURCE_ROOT / "lab" / relative
        assert_projected_file(source, published, relative, "agent-load-stability")

    source_members = set(material_files(AGENT_SOURCE_ROOT / "lab"))
    source_members.update(
        f"reports/{relative}" for relative in material_files(AGENT_SOURCE_ROOT / "evidence")
    )
    source_members.add("README.md")
    if source_members != set(files):
        missing = sorted(source_members - set(files))
        extra = sorted(set(files) - source_members)
        raise AssertionError(
            "canonical/public member drift: agent-load-stability; "
            f"missing={missing}, extra={extra}"
        )


def validate_source_projection() -> None:
    problems: list[str] = []
    for bundle, source_root in SOURCE_PROJECTIONS.items():
        folder = MATERIALS / bundle
        public_files = material_files(folder)
        for relative, published in public_files.items():
            try:
                assert_projected_file(source_root / relative, published, relative, bundle)
            except AssertionError as exc:
                problems.append(str(exc))
        prefix = SOURCE_PREFIXES.get(bundle, "")
        source_members = {
            relative
            for relative in material_files(source_root)
            if not prefix or relative.startswith(prefix)
        }
        source_members.difference_update(SOURCE_ONLY_EXCLUSIONS.get(bundle, set()))
        if source_members != set(public_files):
            missing = sorted(source_members - set(public_files))
            extra = sorted(set(public_files) - source_members)
            problems.append(
                f"canonical/public member drift: {bundle}; missing={missing}, extra={extra}"
            )
    try:
        validate_agent_source_projection(MATERIALS / "agent-load-stability")
    except AssertionError as exc:
        problems.append(str(exc))
    if problems:
        raise AssertionError("canonical/public closure failed:\n- " + "\n- ".join(problems))


def validate_static_projection(static_root: Path, bundles: tuple[str, ...]) -> None:
    if static_root.name != "materials" and (static_root / "materials").is_dir():
        static_root = static_root / "materials"
    for bundle in bundles:
        public_folder = MATERIALS / bundle
        static_folder = static_root / bundle
        public_files = material_files(public_folder)
        static_files = material_files(static_folder)
        if set(public_files) != set(static_files):
            missing = sorted(set(public_files) - set(static_files))
            extra = sorted(set(static_files) - set(public_files))
            raise AssertionError(
                f"public/static member drift: {bundle}; missing={missing}, extra={extra}"
            )
        for relative, public_path in public_files.items():
            static_path = static_files[relative]
            if public_path.read_bytes() != static_path.read_bytes():
                raise AssertionError(
                    f"public/static content drift: {bundle}:{relative}; "
                    f"public_sha256={sha256(public_path.read_bytes())}, "
                    f"static_sha256={sha256(static_path.read_bytes())}"
                )
        public_archive = MATERIALS / f"{bundle}.zip"
        static_archive = static_root / f"{bundle}.zip"
        if not static_archive.is_file():
            raise AssertionError(f"static archive missing: {static_archive}")
        if public_archive.read_bytes() != static_archive.read_bytes():
            raise AssertionError(
                f"public/static archive drift: {bundle}.zip; "
                f"public_sha256={sha256(public_archive.read_bytes())}, "
                f"static_sha256={sha256(static_archive.read_bytes())}"
            )


def validate_release_manifest(release_root: Path) -> None:
    manifest_path = release_root / "RELEASE-MANIFEST.json"
    if not manifest_path.is_file():
        raise AssertionError(f"release manifest missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    missing_artifacts = [name for name in RELEASE_REQUIRED_ARTIFACTS if not (release_root / name).is_file()]
    missing_fields = [name for name in RELEASE_REQUIRED_HASH_FIELDS if not manifest.get(name)]
    if missing_artifacts or missing_fields:
        raise AssertionError(
            "stale release manifest claims an obsolete validation surface; "
            f"missing_artifacts={missing_artifacts}, missing_hash_fields={missing_fields}"
        )
    if manifest.get("validation_verdict") != "PASS":
        raise AssertionError("release manifest validation_verdict is not PASS")
    for field, name in zip(RELEASE_REQUIRED_HASH_FIELDS, RELEASE_REQUIRED_ARTIFACTS, strict=True):
        actual = f"sha256:{sha256((release_root / name).read_bytes())}"
        if manifest[field] != actual:
            raise AssertionError(f"stale release manifest hash: {field} does not match {name}")


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
        path.relative_to(folder).as_posix(): path.read_bytes()
        for path in folder.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    with zipfile.ZipFile(archive) as zipped:
        actual_names = {item.filename for item in zipped.infolist() if not item.is_dir()}
        rooted_names = {f"{name}/{relative}" for relative in expected}
        rootless_names = set(expected)
        if actual_names == rooted_names:
            member_name = lambda relative: f"{name}/{relative}"
        elif actual_names == rootless_names:
            member_name = lambda relative: relative
        else:
            expected_names = rooted_names if any(member.startswith(f"{name}/") for member in actual_names) else rootless_names
            missing = sorted(expected_names - actual_names)
            extra = sorted(actual_names - expected_names)
            raise AssertionError(f"stale archive {archive.name}; missing={missing}, extra={extra}")
        for relative, content in expected.items():
            member = member_name(relative)
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
    parser.add_argument(
        "--static-root",
        type=Path,
        help="Static export root or its materials directory; validates exact public/static closure.",
    )
    parser.add_argument(
        "--release-root",
        type=Path,
        help="Release directory whose PASS manifest must satisfy the current manifest/hash contract.",
    )
    parser.add_argument("--skip-labs", action="store_true", help="Skip executable red/green labs for fast closure tests.")
    parser.add_argument(
        "--skip-source",
        action="store_true",
        help="Skip canonical course projection (intended only for isolated archive fixtures).",
    )
    args = parser.parse_args()
    MATERIALS = args.materials_root.resolve()
    try:
        # Diagnose an explicitly requested legacy PASS manifest first so a
        # separate material drift cannot mask the stale-release verdict.
        if args.release_root:
            validate_release_manifest(args.release_root.resolve())
        validate_syntax()
        if not args.skip_source:
            if MATERIALS != (ROOT / "public/materials").resolve():
                raise AssertionError("custom materials_root requires --skip-source")
            validate_source_projection()
        bundles = discover_bundles()
        for bundle in bundles:
            validate_archive(bundle)
        if args.static_root:
            validate_static_projection(args.static_root.resolve(), bundles)
        if not args.skip_labs:
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
    checks = ["canonical/public projection", "ZIP member/hash closure"]
    if args.static_root:
        checks.append("public/static projection")
    if args.release_root:
        checks.append("current release manifest hashes")
    if not args.skip_labs:
        checks.append("six independent red/green labs")
    print(f"Learner materials valid: {', '.join(checks)}; {len(bundles)} dynamically discovered material bundle(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
