#!/usr/bin/env python3
"""Fail-closed validation for learner-facing career-course release archives."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any


INCOMPLETE = {"planned", "outlined", "blocked"}
PLACEHOLDERS = ("仅保留知识位置", "本页尚未开发", "本页尚未通过逐题研究", "仅提纲")
PUBLIC_TEXT_SUFFIXES = {
    ".html", ".htm", ".xml", ".js", ".mjs", ".cjs", ".md", ".txt",
    ".yaml", ".yml", ".csv",
}
REQUIRED_MANIFEST_FIELDS = {
    "schema_version", "source_commit", "release_scope", "catalog_complete",
    "page_count", "delivered_page_count", "promised_page_ids", "content_hash",
    "validation_verdict", "publication_targets", "learner_artifact_roots", "solution_manifest_hash",
    "catalog_manifest_hash", "promotion_manifest_hash", "executability_manifest_hash", "artifact_closure_hash",
    "capability_profiles_hash", "professional_evidence_hash", "status_registry_hash",
    "source_assimilation_hash", "source_semantic_projection_hash",
    "learner_usability_reuse_hash", "visual_sequence_hash",
}
SOLUTION_VIEW_KINDS = {"context", "building-block", "runtime", "deployment", "data-flow", "security-trust-boundary"}
EXECUTION_STATUSES = ["not-run", "desk-researched", "fixture-tested", "integration-tested", "live-tested", "production-validated"]
REVIEW_STATUSES = ["not-reviewed", "reviewed", "approved"]


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


def file_hash(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


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


def is_public_file(root: Path, path: Path) -> bool:
    parts = path.relative_to(root).parts
    return "skill" not in parts and ".github" not in parts and path.is_file()


def find_incomplete_text(text: str) -> list[str]:
    """Find serialized learner-state leaks without rejecting ordinary prose."""
    findings: list[str] = []
    statuses = "|".join(sorted(INCOMPLETE))
    patterns = {
        "delivery status": rf"(?i)(?:[\"']?delivery[_-]?status[\"']?|deliveryStatus)\s*[:=]\s*[\"']?({statuses})\b",
        "learner status": rf"(?i)(?:[\"']?status[\"']?\s*:|data-status\s*=)\s*[\"']?({statuses})\b",
        "XML status": rf"(?i)<(?:delivery[_-]?status|status)>\s*({statuses})\s*</",
    }
    for label, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            findings.append(f"serialized incomplete {label}={match.group(1).lower()}")
    return findings


def strip_markdown_code_fences(text: str) -> str:
    """Exclude fenced examples while retaining frontmatter and learner-facing prose."""
    return re.sub(r"(?ms)^\s*(```|~~~).*?^\s*\1\s*$", "", text)


def validate_release(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"release does not exist: {root}"]
    if (root / "course-package").exists():
        errors.append("public release must not include the internal course-package authoring tree")

    manifest_path = root / "RELEASE-MANIFEST.json"
    solution_manifest_path = root / "SOLUTION-MANIFEST.json"
    catalog_manifest_path = root / "CATALOG-MANIFEST.json"
    promotion_manifest_path = root / "PAGE-PROMOTION-MANIFEST.json"
    executability_manifest_path = root / "EXECUTABILITY-MANIFEST.json"
    artifact_closure_path = root / "ARTIFACT-CLOSURE.json"
    capability_profiles_path = root / "CAPABILITY-PROFILES.json"
    professional_evidence_path = root / "PROFESSIONAL-EVIDENCE.json"
    status_registry_path = root / "STATUS-REGISTRY.json"
    source_assimilation_path = root / "SOURCE-ASSIMILATION-MANIFEST.json"
    source_semantic_projection_path = root / "SOURCE-SEMANTIC-PROJECTION.json"
    learner_usability_path = root / "LEARNER-USABILITY-REUSE.json"
    visual_sequence_path = root / "VISUAL-SEQUENCE-MANIFEST.json"
    tutorial_path = root / "tutorial/tutorial-site.json"
    html_path = root / "site/index.html"
    for path in (
        manifest_path, solution_manifest_path, catalog_manifest_path, promotion_manifest_path,
        executability_manifest_path, artifact_closure_path, capability_profiles_path,
        professional_evidence_path, status_registry_path, source_assimilation_path,
        source_semantic_projection_path, learner_usability_path, visual_sequence_path,
        tutorial_path, html_path,
    ):
        if not path.is_file():
            errors.append(f"missing public release artifact: {path.relative_to(root)}")
    if errors:
        return errors

    manifest = load_json(manifest_path, errors)
    solution_manifest = load_json(solution_manifest_path, errors)
    catalog_manifest = load_json(catalog_manifest_path, errors)
    promotion_manifest = load_json(promotion_manifest_path, errors)
    executability_manifest = load_json(executability_manifest_path, errors)
    artifact_closure = load_json(artifact_closure_path, errors)
    capability_profiles = load_json(capability_profiles_path, errors)
    professional_evidence = load_json(professional_evidence_path, errors)
    status_registry = load_json(status_registry_path, errors)
    source_assimilation = load_json(source_assimilation_path, errors)
    source_semantic_projection = load_json(source_semantic_projection_path, errors)
    learner_usability = load_json(learner_usability_path, errors)
    visual_sequence = load_json(visual_sequence_path, errors)
    tutorial = load_json(tutorial_path, errors)
    if not all(isinstance(item, dict) for item in (
        manifest, solution_manifest, catalog_manifest, promotion_manifest,
        executability_manifest, artifact_closure, capability_profiles,
        professional_evidence, status_registry, source_assimilation, learner_usability,
        source_semantic_projection, visual_sequence, tutorial,
    )):
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
    if source_assimilation.get("verdict") != "PASS" or source_assimilation.get("unaccounted_ids") != [] or source_assimilation.get("accounted_section_count") != source_assimilation.get("section_count") or source_assimilation.get("accounted_atom_count") != source_assimilation.get("atom_count"):
        errors.append("public source assimilation manifest must PASS with exact section/atom closure")
    semantic_coverage = source_semantic_projection.get("coverage")
    semantic_units = source_semantic_projection.get("units")
    if source_semantic_projection.get("verdict") != "PASS" or not isinstance(semantic_coverage, dict) or semantic_coverage.get("verdict") != "PASS" or semantic_coverage.get("unaccounted_source_item_ids") != []:
        errors.append("public source semantic projection must PASS with zero unaccounted source items")
    if not isinstance(semantic_units, list) or not semantic_units:
        errors.append("public source semantic projection needs semantic units")
        semantic_units = []
    for index, unit in enumerate(semantic_units):
        if not isinstance(unit, dict):
            errors.append(f"public source semantic projection unit {index} is not an object")
            continue
        unit_pages = unit.get("page_ids")
        if not isinstance(unit_pages, list) or not unit_pages or set(map(str, unit_pages)) - set(page_ids):
            errors.append(f"public source semantic projection unit {index} needs known page_ids")
        function_kind = str(unit.get("function_kind", ""))
        status = str(unit.get("status", "")).lower()
        for field in ("visual_refs", "reusable_asset_refs", "exercise_refs"):
            refs = unit.get(field)
            if not isinstance(refs, list):
                errors.append(f"public source semantic projection unit {index} {field} must be a list")
                continue
            for ref in refs:
                path = (root / str(ref)).resolve()
                try:
                    path.relative_to(root.resolve())
                except ValueError:
                    errors.append(f"public source semantic projection unit {index} {field} escapes release root")
                else:
                    if not path.is_file():
                        errors.append(f"public source semantic projection unit {index} references missing {field}: {ref}")
        if function_kind == "visual" and status in {"projected", "adapted"} and not unit.get("visual_refs"):
            errors.append(f"public source semantic projection unit {index} visual function lacks a rendered visual")
        if function_kind in {"template", "prompt-package", "checklist", "self-assessment"} and status in {"projected", "adapted"} and not unit.get("reusable_asset_refs"):
            errors.append(f"public source semantic projection unit {index} reusable function lacks a learner asset")
    learner_pages = [str(item.get("page_id", "")) for item in learner_usability.get("pages", []) if isinstance(item, dict)]
    visual_pages = [str(item.get("page_id", "")) for item in visual_sequence.get("pages", []) if isinstance(item, dict)]
    if learner_pages != page_ids:
        errors.append("learner usability/reuse page IDs must exactly equal public page IDs")
    if visual_pages != page_ids or visual_sequence.get("ordered_page_ids") != page_ids:
        errors.append("visual sequence page IDs must exactly equal public page IDs")
    learner_by_id = {str(item.get("page_id", "")): item for item in learner_usability.get("pages", []) if isinstance(item, dict)}
    visual_by_id = {str(item.get("page_id", "")): item for item in visual_sequence.get("pages", []) if isinstance(item, dict)}
    for index, page in enumerate(pages, start=1):
        page_id = str(page.get("page_id", "")) if isinstance(page, dict) else ""
        learner_page = learner_by_id.get(page_id, {})
        visual_page = visual_by_id.get(page_id, {})
        if page.get("display_number") != index or learner_page.get("display_number") != index or visual_page.get("display_number") != index:
            errors.append(f"public page {page_id} display_number must be contiguous and consistent")
        for visual in visual_page.get("visuals", []) if isinstance(visual_page.get("visuals"), list) else []:
            source_path = str(visual.get("source_path", "")) if isinstance(visual, dict) else ""
            if not source_path or not (root / source_path).is_file():
                errors.append(f"public page {page_id} visual source is missing: {source_path or '<empty>'}")

    if manifest.get("solution_manifest_hash") != file_hash(solution_manifest_path):
        errors.append("release manifest solution_manifest_hash does not match SOLUTION-MANIFEST.json")
    for field, path in (
        ("catalog_manifest_hash", catalog_manifest_path),
        ("promotion_manifest_hash", promotion_manifest_path),
        ("executability_manifest_hash", executability_manifest_path),
        ("artifact_closure_hash", artifact_closure_path),
        ("capability_profiles_hash", capability_profiles_path),
        ("professional_evidence_hash", professional_evidence_path),
        ("status_registry_hash", status_registry_path),
        ("source_assimilation_hash", source_assimilation_path),
        ("source_semantic_projection_hash", source_semantic_projection_path),
        ("learner_usability_reuse_hash", learner_usability_path),
        ("visual_sequence_hash", visual_sequence_path),
    ):
        if manifest.get(field) != file_hash(path):
            errors.append(f"release manifest {field} does not match {path.name}")

    catalog_ids = catalog_manifest.get("page_ids")
    if not isinstance(catalog_ids, list) or not catalog_ids or not all(isinstance(item, str) and item for item in catalog_ids):
        errors.append("public catalog manifest page_ids must be a non-empty exact-ID list")
        catalog_ids = []
    if len(set(catalog_ids)) != len(catalog_ids):
        errors.append("public catalog manifest page_ids must be unique")
    if set(page_ids) - set(catalog_ids):
        errors.append("public page IDs are absent from the canonical catalog manifest")
    if release_scope.get("mode") == "complete-catalog" and page_ids != catalog_ids:
        errors.append("complete-catalog public page IDs must exactly equal the canonical catalog manifest")
    previous_ids = catalog_manifest.get("previous_validated_page_ids")
    removed_ids = set(previous_ids) - set(page_ids) if isinstance(previous_ids, list) else set()
    if removed_ids:
        scope_change_ref = catalog_manifest.get("scope_change_ref")
        scope_change_path = (root / str(scope_change_ref)).resolve() if isinstance(scope_change_ref, str) else root / "__missing__"
        try:
            scope_change_path.relative_to(root.resolve())
        except ValueError:
            scope_change_path = root / "__missing__"
        if not scope_change_path.is_file():
            errors.append("public release scope shrank without a packaged approved scope-change record")
        else:
            change = load_json(scope_change_path, errors)
            if not isinstance(change, dict):
                errors.append("packaged scope-change record must be valid JSON")
            else:
                if change.get("previous_page_ids") != previous_ids or change.get("current_page_ids") != page_ids:
                    errors.append("packaged scope-change record does not match previous and current ordered page IDs")
                if set(map(str, change.get("removed_page_ids", []))) != removed_ids:
                    errors.append("packaged scope-change removed_page_ids does not match the release shrink")
                if str(change.get("verdict", "")).upper() != "APPROVED" or not change.get("approved_by") or not change.get("approved_at") or not change.get("rationale"):
                    errors.append("packaged scope-change record must carry rationale, approval, and APPROVED verdict")
            if manifest.get("scope_change_hash") != file_hash(scope_change_path):
                errors.append("release manifest scope_change_hash does not match the packaged scope-change record")

    promotion_pages = promotion_manifest.get("pages")
    if not isinstance(promotion_pages, list):
        errors.append("promotion manifest pages must be a list")
        promotion_pages = []
    promotion_ids = [str(item.get("page_id", "")) for item in promotion_pages if isinstance(item, dict)]
    if promotion_ids != page_ids:
        errors.append("promotion manifest page IDs must exactly equal public page IDs")
    promotion_by_id = {str(item.get("page_id", "")): item for item in promotion_pages if isinstance(item, dict)}

    executable_pages = executability_manifest.get("pages")
    for field in ("schema_version", "audit_id", "audited_at", "pages"):
        if not executability_manifest.get(field):
            errors.append(f"executability manifest missing field: {field}")
    if not isinstance(executable_pages, list):
        errors.append("executability manifest pages must be a list")
        executable_pages = []
    executable_ids = [str(item.get("page_id", "")) for item in executable_pages if isinstance(item, dict)]
    if executable_ids != page_ids:
        errors.append("executability manifest page IDs must exactly equal public page IDs")
    executable_by_id = {str(item.get("page_id", "")): item for item in executable_pages if isinstance(item, dict)}
    for page_id in page_ids:
        execution = executable_by_id.get(page_id)
        if execution is None or str(execution.get("verdict", "")).upper() != "PASS" or execution.get("finding_count") != 0:
            errors.append(f"public page {page_id} executability must PASS with zero findings")
        promotion = promotion_by_id.get(page_id)
        if promotion is None:
            continue
        if str(promotion.get("verdict", "")).upper() != "PASS" or promotion.get("research_package_complete") is not True:
            errors.append(f"public page {page_id} promotion must PASS with a complete research package")
        if not isinstance(promotion.get("editorial_score"), (int, float)) or promotion.get("editorial_score", 0) < 90:
            errors.append(f"public page {page_id} promotion editorial_score must be at least 90")
        if promotion.get("boundary_preservation_score") != 100:
            errors.append(f"public page {page_id} promotion boundary_preservation_score must be 100")
        if str(promotion.get("executability_verdict", "")).upper() != "PASS":
            errors.append(f"public page {page_id} promotion must preserve executability PASS")

    profile_pages = capability_profiles.get("pages")
    if not isinstance(profile_pages, list):
        errors.append("capability profiles pages must be a list")
        profile_pages = []
    profile_ids = [str(item.get("page_id", "")) for item in profile_pages if isinstance(item, dict)]
    if profile_ids != page_ids:
        errors.append("capability profile page IDs must exactly equal public page IDs")
    allowed_capabilities = {
        "profession-baseline", "artifact-transformation", "ai-system-evaluation",
        "supervised-agent-workflow", "ai-quality-system", "career-evolution-system",
        "agent-architecture-testing",
    }
    for profile in profile_pages:
        if not isinstance(profile, dict):
            continue
        page_id = str(profile.get("page_id", ""))
        capabilities = profile.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities or any(str(item).lower() not in allowed_capabilities for item in capabilities):
            errors.append(f"public page {page_id} lacks a valid professional capability profile")
        for field in ("rationale", "risk", "reviewer", "reviewed_at", "evidence_refs"):
            if profile.get(field) in (None, "", []):
                errors.append(f"public page {page_id} capability profile missing field: {field}")

    evidence_pages = professional_evidence.get("pages")
    if not isinstance(evidence_pages, list):
        errors.append("professional evidence pages must be a list")
        evidence_pages = []
    evidence_ids = [str(item.get("page_id", "")) for item in evidence_pages if isinstance(item, dict)]
    if evidence_ids != page_ids:
        errors.append("professional evidence page IDs must exactly equal public page IDs")
    evidence_statuses = {"NOT_RUN", "PASS", "FAIL", "BLOCKED"}
    for record in evidence_pages:
        if not isinstance(record, dict):
            continue
        page_id = str(record.get("page_id", ""))
        lane_status: dict[str, str] = {}
        for lane in ("model", "integration", "clean_room", "practitioner", "learner"):
            lane_record = record.get(lane)
            if not isinstance(lane_record, dict):
                errors.append(f"public page {page_id} professional evidence missing lane: {lane}")
                continue
            status = str(lane_record.get("status", "")).upper()
            lane_status[lane] = status
            if status not in evidence_statuses:
                errors.append(f"public page {page_id} professional evidence {lane} has invalid status")
            receipts = lane_record.get("receipt_refs")
            if not isinstance(receipts, list) or (status == "PASS" and not receipts):
                errors.append(f"public page {page_id} professional evidence {lane} has invalid receipt_refs")
            if not lane_record.get("limitations"):
                errors.append(f"public page {page_id} professional evidence {lane} missing limitations")
        model = record.get("model", {})
        if isinstance(model, dict) and str(model.get("status", "")).upper() == "PASS":
            if str(model.get("provider", "")).strip().lower() in {"", "none", "offline", "fixture", "deterministic"}:
                errors.append(f"public page {page_id} model PASS cannot use provider none/offline")
            if str(model.get("oracle_owner", "")).strip().lower() in {"model-under-test", "model under test", "self", "same-model"}:
                errors.append(f"public page {page_id} model under test cannot own its oracle")
        maturity = str(record.get("maturity_claim", "")).lower()
        if maturity == "fixture-tested" and lane_status.get("clean_room") != "PASS":
            errors.append(f"public page {page_id} fixture-tested maturity lacks clean_room PASS")
        if maturity == "model-integrated" and (lane_status.get("model") != "PASS" or lane_status.get("clean_room") != "PASS"):
            errors.append(f"public page {page_id} model-integrated maturity lacks model and clean_room PASS")
        if maturity == "integration-tested" and any(lane_status.get(lane) != "PASS" for lane in ("model", "integration", "clean_room")):
            errors.append(f"public page {page_id} integration-tested maturity lacks model, integration, or clean_room PASS")
        if maturity == "practitioner-reviewed" and lane_status.get("practitioner") != "PASS":
            errors.append(f"public page {page_id} practitioner-reviewed maturity lacks practitioner PASS")
        if maturity == "production-validated" and any(lane_status.get(lane) != "PASS" for lane in ("model", "integration", "clean_room", "practitioner", "learner")):
            errors.append(f"public page {page_id} production maturity lacks complete professional evidence")

    status_records = status_registry.get("records")
    if not isinstance(status_records, list) or not status_records:
        errors.append("status registry needs at least one record")
        status_records = []
    status_groups: dict[tuple[str, str], int] = {}
    for record in status_records:
        if not isinstance(record, dict):
            continue
        if record.get("page_ids") != page_ids:
            errors.append(f"status registry {record.get('record_id', '<unknown>')} page_ids differ from public scope")
        key = (str(record.get("artifact_type", "")), str(record.get("scope_id", "")))
        if record.get("status") == "current":
            status_groups[key] = status_groups.get(key, 0) + 1
        path_value = str(record.get("path", ""))
        if not path_value or not (root / path_value).is_file():
            errors.append(f"status registry {record.get('record_id', '<unknown>')} references missing artifact")
        evidence_refs = record.get("evidence_refs")
        if not isinstance(evidence_refs, list) or not evidence_refs or any(not (root / str(ref)).is_file() for ref in evidence_refs):
            errors.append(f"status registry {record.get('record_id', '<unknown>')} has missing evidence refs")
    if any(count != 1 for count in status_groups.values()) or not status_groups:
        errors.append("status registry must have exactly one current record per verdict scope")

    if artifact_closure.get("canonical_catalog_ref") != "CATALOG-MANIFEST.json" or artifact_closure.get("canonical_catalog_hash") != file_hash(catalog_manifest_path):
        errors.append("artifact closure does not pin the current canonical catalog manifest")
    if artifact_closure.get("tutorial_ref") != "tutorial/tutorial-site.json" or artifact_closure.get("tutorial_hash") != file_hash(tutorial_path):
        errors.append("artifact closure does not pin the current tutorial source")
    archive_ref = artifact_closure.get("archive_ref")
    archive_path = (root / str(archive_ref)).resolve() if isinstance(archive_ref, str) else root / "__missing__"
    try:
        archive_path.relative_to(root.resolve())
    except ValueError:
        errors.append("artifact closure archive_ref escapes release root")
        archive_path = root / "__missing__"
    material_entries = artifact_closure.get("material_entries")
    if not isinstance(material_entries, list):
        errors.append("artifact closure material_entries must be a list")
        material_entries = []
    expected_pairs = {
        (page_id, str(material.get("href", "")))
        for page_id, page in zip(page_ids, pages) if isinstance(page, dict)
        for material in page.get("materials", []) if isinstance(material, dict)
    }
    actual_pairs = {
        (str(entry.get("page_id", "")), str(entry.get("href", "")))
        for entry in material_entries if isinstance(entry, dict)
    }
    if actual_pairs != expected_pairs or len(material_entries) != len(expected_pairs):
        errors.append("artifact closure entries must exactly cover every public page-material link")
    archive_members: dict[str, bytes] = {}
    if not archive_path.is_file():
        errors.append("artifact closure archive is missing")
    else:
        try:
            with zipfile.ZipFile(archive_path) as archive:
                infos = [item for item in archive.infolist() if not item.is_dir()]
                if any(Path(info.filename).is_absolute() or ".." in Path(info.filename).parts for info in infos):
                    errors.append("artifact closure archive contains an unsafe path")
                archive_members = {info.filename: archive.read(info) for info in infos}
        except zipfile.BadZipFile as exc:
            errors.append(f"artifact closure archive is invalid: {exc}")
    declared_members: set[str] = set()
    for index, entry in enumerate(material_entries):
        if not isinstance(entry, dict):
            errors.append(f"artifact closure entry {index} is not an object")
            continue
        href = str(entry.get("href", ""))
        dist_ref = str(entry.get("dist_ref", ""))
        expected_hash = str(entry.get("sha256", ""))
        if dist_ref != f"site/{href}":
            errors.append(f"artifact closure dist_ref does not match tutorial href: {href}")
        dist_path = (root / dist_ref).resolve()
        try:
            dist_path.relative_to(root.resolve())
        except ValueError:
            errors.append(f"artifact closure dist_ref escapes release root: {dist_ref}")
        else:
            if not dist_path.is_file() or file_hash(dist_path) != expected_hash:
                errors.append(f"artifact closure hash mismatch for dist_ref: {dist_ref}")
        member = str(entry.get("archive_member", ""))
        declared_members.add(member)
        member_bytes = archive_members.get(member)
        member_hash = f"sha256:{hashlib.sha256(member_bytes).hexdigest()}" if member_bytes is not None else ""
        if member_hash != expected_hash:
            errors.append(f"artifact closure hash mismatch for archive member: {member}")
        promotion = promotion_by_id.get(str(entry.get("page_id", "")))
        if isinstance(promotion, dict):
            hashes = promotion.get("material_hashes")
            if not isinstance(hashes, dict) or hashes.get(href) != expected_hash:
                errors.append(f"public page {entry.get('page_id')} promotion material hash mismatch: {href}")
    if archive_members and set(archive_members) != declared_members:
        errors.append("artifact closure archive members must exactly equal declared members")
    solution_units = solution_manifest.get("solution_units")
    if not isinstance(solution_units, list) or not solution_units:
        errors.append("solution manifest needs at least one public solution unit")
        solution_units = []
    mapped_solution_pages: set[str] = set()
    for index, unit in enumerate(solution_units):
        label = f"public solution unit {index}"
        if not isinstance(unit, dict):
            errors.append(f"{label} is not an object")
            continue
        required = {
            "solution_id", "page_ids", "design_status", "execution_status", "practitioner_review_status",
            "publication_status", "architecture_view_kinds", "acceptance_gate_status",
            "execution_receipt_refs", "residual_risk_count",
        }
        missing = required - set(unit)
        if missing:
            errors.append(f"{label} missing fields: {', '.join(sorted(missing))}")
            continue
        unit_pages = unit.get("page_ids")
        if not isinstance(unit_pages, list) or not unit_pages:
            errors.append(f"{label} needs page_ids")
            unit_pages = []
        unknown_pages = set(map(str, unit_pages)) - set(page_ids)
        if unknown_pages:
            errors.append(f"{label} references unknown page IDs: {', '.join(sorted(unknown_pages))}")
        mapped_solution_pages.update(map(str, unit_pages))
        view_kinds = set(map(str, unit.get("architecture_view_kinds", []))) if isinstance(unit.get("architecture_view_kinds"), list) else set()
        if view_kinds != SOLUTION_VIEW_KINDS:
            errors.append(f"{label} does not carry all six architecture view kinds")
        design_status = unit.get("design_status")
        execution_status = unit.get("execution_status")
        review_status = unit.get("practitioner_review_status")
        publication_status = unit.get("publication_status")
        execution_rank = EXECUTION_STATUSES.index(execution_status) if execution_status in EXECUTION_STATUSES else -1
        review_rank = REVIEW_STATUSES.index(review_status) if review_status in REVIEW_STATUSES else -1
        if publication_status == "pilot":
            if design_status != "complete" or execution_rank < 2 or review_rank < 1:
                errors.append(f"{label} pilot release lacks complete design, fixture proof, or practitioner review")
        elif publication_status == "public":
            if design_status != "complete" or execution_rank < 3 or review_status != "approved" or unit.get("acceptance_gate_status") != "pass":
                errors.append(f"{label} public release lacks integration proof, approval, or passed gates")
        else:
            errors.append(f"{label} must be pilot or public")
        receipt_refs = unit.get("execution_receipt_refs")
        if execution_rank >= 2 and (not isinstance(receipt_refs, list) or not receipt_refs):
            errors.append(f"{label} claims tested execution without receipts")
        for receipt_ref in receipt_refs if isinstance(receipt_refs, list) else []:
            receipt_path = (root / str(receipt_ref)).resolve()
            try:
                receipt_path.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{label} receipt escapes release root")
            else:
                if not receipt_path.is_file() or receipt_path.suffix != ".json":
                    errors.append(f"{label} references missing structured receipt: {receipt_ref}")
        if not isinstance(unit.get("residual_risk_count"), int) or unit.get("residual_risk_count") < 1:
            errors.append(f"{label} must disclose residual risks")
    unmapped_solution_pages = set(page_ids) - mapped_solution_pages
    if unmapped_solution_pages:
        errors.append(f"public pages are missing complete-solution coverage: {', '.join(sorted(unmapped_solution_pages))}")

    incomplete_pages = [
        page_id for page_id, page in zip(page_ids, pages)
        if isinstance(page, dict) and str(page.get("delivery_status", "")).lower() in INCOMPLETE
    ]
    if incomplete_pages:
        errors.append(f"public tutorial contains incomplete pages: {', '.join(incomplete_pages)}")

    for index, page in enumerate(pages):
        if not isinstance(page, dict):
            continue
        architecture = page.get("architecture")
        if not isinstance(architecture, dict) or not isinstance(architecture.get("nodes"), list) or len(architecture.get("nodes", [])) < 5:
            errors.append(f"public tutorial page {index} lacks a substantive architecture/workflow diagram")
        materials = page.get("materials")
        if not isinstance(materials, list) or not materials:
            errors.append(f"public tutorial page {index} lacks learner-facing materials")
            continue
        tested = 0
        has_script = False
        for material_index, material in enumerate(materials):
            label = f"public tutorial page {index} material {material_index}"
            if not isinstance(material, dict):
                errors.append(f"{label} is not an object")
                continue
            href = str(material.get("href", ""))
            if not href or href.startswith(("http://", "https://", "//")) or ".." in Path(href).parts:
                errors.append(f"{label} must reference a repository-owned relative file")
            elif not (root / "site" / href).is_file() or (root / "site" / href).stat().st_size == 0:
                errors.append(f"{label} references missing or empty file: site/{href}")
            else:
                material_path = root / "site" / href
                try:
                    if material.get("kind") == "script" and material_path.suffix == ".py":
                        compile(material_path.read_text(encoding="utf-8"), str(material_path), "exec")
                    if material_path.suffix == ".json":
                        json.loads(material_path.read_text(encoding="utf-8"))
                    if material.get("kind") == "archive" and material_path.suffix == ".zip":
                        with zipfile.ZipFile(material_path) as zipped:
                            names = [item.filename for item in zipped.infolist() if not item.is_dir()]
                            if not names:
                                errors.append(f"{label} archive is empty")
                            if any(Path(name).is_absolute() or ".." in Path(name).parts for name in names):
                                errors.append(f"{label} archive contains an unsafe path")
                except (SyntaxError, UnicodeDecodeError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
                    errors.append(f"{label} cannot be parsed: {exc}")
            if material.get("validation") == "fixture-tested":
                tested += 1
            if material.get("kind") == "script":
                has_script = True
        if page.get("delivery_status") == "fixture-tested" and (tested < 2 or not has_script):
            errors.append(f"public fixture-tested page {index} needs two tested materials including a script")

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
        if path == manifest_path or not is_public_file(root, path):
            continue
        data = load_json(path, errors)
        if data is None:
            continue
        for problem in find_incomplete_records(data):
            errors.append(f"public JSON {path.relative_to(root)} {problem}")

    for path in root.rglob("*"):
        if not is_public_file(root, path) or path.suffix.lower() not in PUBLIC_TEXT_SUFFIXES:
            continue
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(marker in text for marker in PLACEHOLDERS):
            errors.append(f"public artifact exposes placeholder copy: {relative}")
        state_text = strip_markdown_code_fences(text) if path.suffix.lower() == ".md" else text
        for finding in find_incomplete_text(state_text):
            errors.append(f"public artifact {relative} {finding}")
        if path.suffix.lower() in {".html", ".htm"}:
            for attribute in ("data-page-id", "data-id", "data-go"):
                for value in re.findall(rf'{attribute}=["\']([^"\']+)["\']', text):
                    if value not in page_ids and not value.startswith("${"):
                        errors.append(f"public HTML {relative} exposes unknown {attribute}={value}")

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
