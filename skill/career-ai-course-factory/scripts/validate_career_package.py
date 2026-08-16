#!/usr/bin/env python3
"""Fail-closed validator for AI-native profession course packages."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from build_source_assimilation_ledger import inventory_source


REQUIRED_ROOT = [
    "career-profile.md", "tasks.json", "curriculum.json", "course-map.md",
    "profession-reality-map.md", "industry-framework.md", "learning-architecture.md", "curriculum-gap-analysis.md", "solution-architecture.md", "validation-report.md", "update-log.md",
]
LEARNING_ARCHITECTURE_MARKERS = [
    "## Learner transformation", "## Professional baseline", "## AI foundations",
    "## Capability transition matrix", "## Learning stages", "## Specialization tracks",
    "## Benchmark literacy", "## Exit gates",
]
REQUIRED_HUMAN_REVIEW = {
    "human-review/README.md": ["## 先看什么", "## 当前结论", "## 如何判断"],
    "human-review/01-调研思路与主要结论.md": ["## 调研链路", "## 主要结论", "## Evidence", "## Inference", "## Unknown"],
    "human-review/02-成果清单与课程地图.md": ["## 职业工作域", "## 场景清单", "## 课程地图", "## 交付状态"],
    "human-review/03-细化样课.md": ["## 业务场景", "## 学完能得到什么", "## 上课流程", "## 学员实操", "## 验证标准", "## 证据边界"],
    "human-review/04-完整方案审计.md": ["## 方案单元", "## 完整性结论", "## 运行证据", "## 架构与决策", "## 缺口与风险", "## 发布门禁"],
}
REQUIRED_TUTORIAL_MARKDOWN = {
    "tutorial/README.md": ["## 如何学习", "## 教程结构", "## 当前完成度"],
    "tutorial/course-tree.md": ["## 学习路线", "## 模块", "## 页面状态"],
    "tutorial/page-template.md": ["## 页面顶部", "## 通俗解释", "## 自己动手", "## 完成检查", "## 证据边界"],
}
REQUIRED_TOPIC_RESEARCH_FILES = {
    "research-brief.md": ["Controlling question"],
    "evidence-synthesis.md": ["## Fact", "## Cross-source synthesis", "## Unknown"],
    "engineering-blueprint.md": ["## Architecture and data flow", "## Metrics and decisions", "## Baseline failure repair"],
    # Manuscript headings are intentionally topic-specific. Their semantic
    # contract is validated separately so the gate does not reward eighty-five
    # pages repeating the same English template headings.
    "manuscript.md": [],
    "comparison.md": ["## Agreements", "## Disagreements", "## Adjudication"],
    "validation.md": ["## Research coverage", "## Claim traceability", "## Runnable lab", "## Independent comparison", "## Publication verdict"],
}
REQUIRED_TOPIC_SOURCE_COLUMNS = [
    "source_id", "url", "title", "source_type", "source_family", "publisher_group",
    "accessed_at", "version_date", "evidence_lane", "supports", "does_not_support",
    "limitations", "opened_status",
]
PROMOTION_RESEARCH_PACKAGE_FILES = {
    "research-brief.md", "source-pack.csv", "research-runs.json", "evidence-synthesis.md",
    "engineering-blueprint.md", "manuscript.md", "comparison.md", "lab-manifest.json", "validation.md",
    "projection-ledger.json",
}
REQUIRED_RESEARCH = [
    "source-ledger.csv", "search-plan.json", "search-log.csv", "technology-radar.json",
    "channel-coverage.json", "profession-reality-map.json", "profession-map.json", "profession-knowledge-system.json", "github-artifacts.csv", "job-signals.csv",
    "learner-signals.csv", "scenarios.json", "evidence-matrix.md", "competitor-matrix.csv",
    "ai-capability-map.md", "competency-transition-map.json", "curriculum-coverage-matrix.csv",
    "solution-architecture.json",
]
GAP_ANALYSIS_MARKERS = [
    "## Research corpus", "## Industry body of knowledge",
    "## Real work and practitioner evidence", "## Existing course supply",
    "## AI technology and benchmark frontier", "## Coverage matrix",
    "## Missing and overrepresented topics", "## Expert review",
    "## Curriculum decisions", "## Remaining unknowns",
]
EXPERT_REVIEW_MARKERS = [
    "### Profession veteran", "### AI systems engineer",
    "### Evaluation and quality expert", "### Curriculum designer",
    "### Market and learner researcher", "### Adversarial critic",
]
COVERAGE_COLUMNS = [
    "cell_id", "profession_domain_id", "layer_kind", "specialization_kind",
    "learner_level", "topic", "required_by_source_ids", "competitor_ids", "course_ids",
    "learner_artifact", "exit_assessment", "evidence_status", "coverage_status",
    "priority", "gap_reason", "decision",
]
REQUIRED_LEDGER_COLUMNS = [
    "id", "title", "creator", "source_type", "platform", "language", "year", "url",
    "access_date", "evidence_tier", "publisher_group", "source_family_id", "channel_ids",
    "relevance", "credibility", "used_for", "limitations",
]
REQUIRED_COMPETITOR_COLUMNS = [
    "id", "platform", "offering", "audience", "promise", "ai_lane", "modules",
    "hands_on_artifact", "execution_proof", "assessment", "freshness", "commercial_model",
    "url", "access_date", "gap", "claim_status",
]
REQUIRED_SEARCH_LOG_COLUMNS = [
    "id", "query", "language", "research_lane", "surface_attempt_id", "search_surface", "run_at",
    "result_count", "selected_source_ids", "opened_urls", "exclusion_notes", "status",
]
REQUIRED_CHANNELS = {
    "profession-authority", "ai-primary", "github-artifact", "practitioner-failure",
    "market-demand", "learner-supply", "counterevidence",
}
REQUIRED_GITHUB_COLUMNS = [
    "artifact_id", "source_id", "repo_url", "commit_or_tag", "license", "last_commit_at",
    "release_or_commit_url", "issues_url", "ci_url", "setup_command", "smoke_command",
    "run_status", "run_at", "exit_code", "evidence_path", "selected_for_lab", "limitations",
]
REQUIRED_JOB_COLUMNS = [
    "job_id", "source_id", "employer", "title", "location", "posted_or_observed_at",
    "original_url", "task_terms", "ai_terms", "duplicate_group", "claim_status", "limitations",
]
REQUIRED_LEARNER_SIGNAL_COLUMNS = [
    "signal_id", "source_id", "platform", "content_url", "signal_type", "direct_observation",
    "learner_question", "requested_outcome", "pain_language", "engagement_metric",
    "metric_scope", "observed_at", "claim_status", "limitations",
]
SEARCH_STATUSES = {"selected", "leads-only", "no-usable-result", "blocked"}
TECH_STATUSES = {"current", "watch", "experimental", "stale", "deprecated", "blocked"}
SCENARIO_EVIDENCE_CLASSES = {"profession-workflow", "ai-capability", "practice-artifact"}
SCENARIO_STATUSES = {
    "hypothesis", "desk-researched", "fixture-tested", "live-tested",
    "practitioner-reviewed", "production-validated", "blocked",
}
EVIDENCE_TYPE_TOKENS = {
    "profession-workflow": {"professional", "job", "standard", "industry", "practitioner", "government", "role"},
    "ai-capability": {"official", "primary", "standard", "repository"},
    "practice-artifact": {"practitioner", "community", "issue", "case", "job", "dataset", "repository", "counterevidence", "postmortem", "research"},
}
SEMANTIC_FIELDS = [
    "actor_role", "actor_seniority", "business_domain", "system_name_or_class",
    "failure_impact", "observable_indicator", "measurement_status", "decision_owner",
    "decision", "allowed_ai_authority", "human_approval_required",
]
PLACEHOLDER_TOKENS = {"todo", "tbd", "n/a", "na", "某职业", "某系统", "待补充", "placeholder"}
GENERIC_SEMANTIC_VALUES = {
    "role", "system", "impact", "indicator", "owner", "decision", "authority",
    "角色", "系统", "影响", "指标", "负责人", "决策", "权限", "业务场景",
}
ALLOWED_SOURCE_TYPES = {
    "official documentation", "primary repository", "standard", "course",
    "practitioner article", "practitioner session", "video course", "commercial article",
    "commercial course", "industry report", "community discussion", "counterevidence",
    "professional syllabus", "research paper", "job posting", "government workflow",
    "public dataset", "issue tracker", "case study", "postmortem",
}
AI_LANES = {"use-ai-for-work", "test-ai-systems", "agentize-work", "build-ai-quality-system"}
ARCHITECTURE_PROFILES = {"ai-enabled-practitioner", "ai-builder", "ai-quality-engineer"}
LEARNING_LAYER_KINDS = [
    "profession-baseline", "ai-foundation", "ai-assisted-work", "ai-system-quality",
    "agent-workflow-quality", "quality-engineering", "benchmark-literacy", "capstone",
]
AI_QUALITY_SPECIALIZATIONS = {
    "llm-quality", "rag-quality", "agent-quality", "workflow-quality", "benchmark-engineering",
}
AI_CHANGE_CLASSES = {"retained", "assisted", "automated", "transformed", "new-work", "declining"}
MANDATORY_AI_CHANGE_CLASSES = {"retained", "assisted", "transformed", "new-work"}
KNOWLEDGE_CELL_STATUSES = {"covered", "planned", "not-applicable", "gap"}
COVERAGE_STATUSES = {"covered", "planned", "gap", "rejected"}
COVERAGE_PRIORITIES = {"critical", "high", "medium", "low"}
VALID_STATUSES = {
    "designed", "desk-researched", "fixture-tested", "live-tested",
    "practitioner-reviewed", "production-validated", "blocked",
}
COURSE_FILES = [
    "course-manifest.json", "course.md", "materials/quickstart.md",
    "materials/reusable-skill.md", "materials/sample-input.md",
    "materials/expected-output.md", "materials/verification-checklist.md", "materials/material-provenance.json",
    "evidence/execution-evidence.json", "video/brief.md", "video/script.md", "video/storyboard.md",
    "video/lesson-experience.json",
]
LESSON_STAGES = [
    "cold-open-failure", "stakes-and-promise", "before-after", "plain-mental-model",
    "guided-demo", "failure-diagnosis", "learner-practice", "transfer-challenge", "artifact-handoff",
]
TUTORIAL_PAGE_TYPES = {"concept", "guided-lab", "diagnostic", "reference", "project"}
TUTORIAL_DELIVERY_STATUSES = {
    "planned", "outlined", "desk-researched", "fixture-tested", "live-tested",
    "practitioner-reviewed", "production-validated", "blocked",
}
TRANSFER_FIELDS = ["source_context", "target_context", "invariant", "must_change", "success_criterion"]
COURSE_MARKERS = [
    "## AI centrality", "## System under test", "## Baseline and target",
    "## Commands", "## Metrics and thresholds", "## Failure injection",
    "## Human review gate", "## AI-specific failure boundary",
    "## Learner artifact", "## Evidence status",
]

SOLUTION_ARCHITECTURE_MARKERS = [
    "## Solution units", "## Scope and boundaries", "## Architecture views",
    "## Decisions and trade-offs", "## Traceability", "## Acceptance gates",
    "## Maturity and evidence", "## Risks and unknowns",
]
SOLUTION_DIMENSION_IDS = {
    "purpose-and-success", "scope-and-non-goals", "stakeholders-and-decision-rights",
    "current-state-and-baseline", "use-cases-and-requirements", "constraints-assumptions-dependencies",
    "alternatives-and-architecture-decisions", "context-and-component-architecture",
    "runtime-workflow-and-state", "deployment-and-environments", "interfaces-and-integrations",
    "data-lifecycle-and-governance", "ai-system-lifecycle-and-human-authority",
    "security-privacy-compliance", "quality-test-evaluation-strategy", "performance-capacity-cost",
    "reliability-resilience-disaster-recovery", "observability-operations-and-support",
    "implementation-and-repository", "rollout-migration-rollback", "delivery-plan-resourcing-ownership",
    "risks-unknowns-technical-debt", "learner-experience-and-reusable-assets",
    "evidence-traceability-and-acceptance", "evolution-versioning-and-deprecation",
}
SOLUTION_VIEW_KINDS = {
    "context", "building-block", "runtime", "deployment", "data-flow", "security-trust-boundary",
}
SOLUTION_DIMENSION_STATUSES = {"complete", "partial", "gap", "not-applicable"}
SOLUTION_DESIGN_STATUSES = {"complete", "partial", "gap"}
SOLUTION_EXECUTION_STATUSES = [
    "not-run", "desk-researched", "fixture-tested", "integration-tested", "live-tested", "production-validated",
]
SOLUTION_REVIEW_STATUSES = ["not-reviewed", "reviewed", "approved"]
SOLUTION_PUBLICATION_STATUSES = {"internal", "pilot", "public"}

# Professional capability declarations are mandatory for learner-facing pages.
# Capability-specific deep contracts remain activated explicitly; never infer a
# profession method or source-authority rule from a title or identifier.
CAPABILITY_DECLARATION_FILES = ("research/capability-declarations.json", "research/capabilities.json", "capabilities.json")
PROFESSIONAL_CAPABILITIES = {
    "profession-baseline", "artifact-transformation", "ai-system-evaluation",
    "supervised-agent-workflow", "ai-quality-system", "career-evolution-system",
    "agent-architecture-testing",
}
EVIDENCE_LANES = ("model", "integration", "clean_room", "practitioner", "learner")
EVIDENCE_STATUSES = {"NOT_RUN", "PASS", "FAIL", "BLOCKED"}
BLOCKED_CONTRACT_STATUSES = {"blocked", "unknown", "incomplete", "schema_invalid", "source_conflict", "semantic_unknown", "refused"}
DEFAULT_PRECEDENCE_MARKERS = {"default", "infer", "inferred", "automatic", "auto", "prd > openapi", "openapi > design", "document type order"}
ASSIMILATION_DISPOSITIONS = {"incorporated", "adapted", "rejected", "blocked", "superseded"}
SEMANTIC_FUNCTION_KINDS = {
    "concept-model", "comparison", "workflow", "decision-rule", "metric-definition",
    "threshold-policy", "career-ladder", "self-assessment", "visual", "template",
    "prompt-package", "checklist", "worked-example", "counterexample", "exercise",
    "source-resource", "reference-claim", "glossary", "risk-boundary",
}
SEMANTIC_PROJECTION_STATUSES = {"projected", "adapted", "rejected", "blocked", "superseded"}
PAGE_PROJECTION_CLAIM_KINDS = {
    "decision-rule", "judgement-table", "counterexample", "failure-mode",
    "metric-definition", "threshold", "boundary", "artifact",
}
PAGE_PROJECTION_CRITICAL_KINDS = {
    "decision-rule", "judgement-table", "counterexample", "failure-mode",
    "metric-definition", "boundary",
}
VISUAL_EXTENSIONS = {".svg", ".mmd", ".mermaid"}
AGENT_ARCHITECTURE_DOMAINS = {
    "D0-evaluation-trust", "D1-single-agent-capability", "D2-orchestration-multi-agent",
    "D3-interaction-collaboration", "D4-robustness-reliability", "D5-security-adversarial",
    "D6-efficiency-economics", "D7-business-governance",
}
CAREER_RESPONSIBILITY_STATES = {
    "guided-execution", "independent-scoped-ownership", "system-cross-team-leverage",
    "strategy-governance-mentoring",
}
AGENT_EVIDENCE_RINGS = {"offline-fixture", "controlled-integration", "shadow-canary", "continuous-online"}


def load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"cannot parse {path.name}: {exc}")
        return None


def load_csv(path: Path, errors: list[str]) -> tuple[list[dict[str, str]], list[str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            return list(reader), list(reader.fieldnames or [])
    except Exception as exc:
        errors.append(f"cannot read {path.name}: {exc}")
        return [], []


def _records(data: Any, key: str) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        value = data.get(key, data.get("items", data.get("records", data.get("cases", data.get("evaluations", data.get("mutations", data.get("nodes", [])))))))
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _load_json_if_exists(root: Path, relative: str, errors: list[str]) -> Any:
    path = root / relative
    return load_json(path, errors) if path.is_file() else None


def validate_capability_contract(root: Path, errors: list[str]) -> None:
    """Validate explicitly opted-in research→factory artifact transformation contracts."""
    declaration_path = next((root / name for name in CAPABILITY_DECLARATION_FILES if (root / name).is_file()), None)
    if declaration_path is None:
        return
    declarations = _records(load_json(declaration_path, errors), "capabilities")
    if not declarations:
        errors.append(f"{declaration_path.relative_to(root)} must declare at least one capability")
        return
    for index, declaration in enumerate(declarations):
        capability = str(declaration.get("capability", declaration.get("capability_id", declaration.get("name", "")))).strip().lower()
        if capability != "artifact-transformation":
            continue
        label = f"artifact-transformation capability {index}"
        topics = declaration.get("topics", declaration.get("topic_ids", []))
        pages = declaration.get("pages", declaration.get("page_ids", []))
        if not isinstance(topics, list) or not topics:
            topics = [str(item) for item in pages if item]
        method_path = str(declaration.get("method_library", "research/profession-method-library.json"))
        method = _load_json_if_exists(root, method_path, errors)
        if not isinstance(method, (dict, list)):
            errors.append(f"{label} missing profession method library: {method_path}")
        else:
            methods = _records(method, "methods")
            if not methods:
                errors.append(f"{label} profession method library has no methods")
            authority = method.get("source_authority", method.get("precedence")) if isinstance(method, dict) else None
            if not authority:
                errors.append(f"{label} method library missing explicit source authority/precedence")
            elif any(marker in str(authority).lower() for marker in DEFAULT_PRECEDENCE_MARKERS):
                errors.append(f"{label} method library uses inferred/default source precedence")
            if isinstance(method, dict) and (not method.get("owner") or not method.get("evidence")):
                errors.append(f"{label} method library source authority needs owner and evidence")
            for method_index, item in enumerate(methods):
                if not str(item.get("rationale", item.get("method_rationale", ""))).strip():
                    errors.append(f"{label} method {method_index} missing method rationale")
        topic_statuses: list[str] = []
        for topic in topics:
            contract_path = str(declaration.get("transformation_contracts", {}).get(topic, f"research/topics/{topic}/transformation-contract.json")) if isinstance(declaration.get("transformation_contracts"), dict) else f"research/topics/{topic}/transformation-contract.json"
            contract = _load_json_if_exists(root, contract_path, errors)
            if not isinstance(contract, dict):
                errors.append(f"{label} topic {topic} missing transformation contract: {contract_path}")
            elif str(contract.get("status", "")).lower() in BLOCKED_CONTRACT_STATUSES:
                errors.append(f"{label} topic {topic} transformation contract is blocked")
            elif isinstance(contract, dict):
                topic_statuses.append(str(contract.get("status", "")).lower())
                authority = contract.get("source_authority", contract.get("precedence"))
                if not authority:
                    errors.append(f"{label} topic {topic} missing explicit source authority/precedence")
                elif any(marker in str(authority).lower() for marker in DEFAULT_PRECEDENCE_MARKERS):
                    errors.append(f"{label} topic {topic} uses inferred/default source precedence")
                if not contract.get("authority_owner", contract.get("owner")) or not contract.get("authority_evidence", contract.get("evidence")):
                    errors.append(f"{label} topic {topic} source authority needs owner and evidence")
        maturity_rank = {"designed": 0, "fixture-tested": 1, "model-integrated": 2, "integration-tested": 3, "practitioner-reviewed": 4, "production-validated": 5}
        declared_status = str(declaration.get("status", "")).lower()
        if topic_statuses and declared_status in maturity_rank and any(maturity_rank.get(status, -1) < maturity_rank[declared_status] for status in topic_statuses):
            errors.append(f"{label} declares {declared_status} above fixture/topic evidence")
        package_dir = str(declaration.get("prompt_package_dir", "research/prompt-package"))
        required = {
            "manifest": str(declaration.get("prompt_manifest", f"{package_dir}/manifest.json")),
            "eval": str(declaration.get("prompt_eval", f"{package_dir}/eval.json")),
            "mutation": str(declaration.get("prompt_mutation", f"{package_dir}/mutation.json")),
            "traceability": str(declaration.get("traceability", "research/traceability.json")),
        }
        loaded: dict[str, Any] = {}
        for kind, relative in required.items():
            loaded[kind] = _load_json_if_exists(root, relative, errors)
            if loaded[kind] is None:
                errors.append(f"{label} missing {kind} artifact: {relative}")
        manifest = loaded.get("manifest")
        if isinstance(manifest, dict):
            for field in ("package_id", "version", "eval_set_id", "stop_states"):
                if not manifest.get(field):
                    errors.append(f"{label} prompt package manifest missing field: {field}")
        for kind in ("eval", "mutation"):
            if isinstance(loaded.get(kind), dict) and not _records(loaded[kind], "items"):
                errors.append(f"{label} prompt {kind} has no records")
        trace = loaded.get("traceability")
        if isinstance(trace, dict):
            edges = _records(trace, "links") or _records(trace, "trace"); ids = {str(item.get("id")) for item in edges if item.get("id")}
            chain = ("source", "claim", "risk", "method", "oracle", "case", "result")
            for node_kind in chain:
                nodes = [item for item in edges if item.get("kind", item.get("type")) == node_kind]
                if not nodes:
                    errors.append(f"{label} traceability missing {node_kind} node")
            for item in edges:
                refs = item.get("refs", item.get("depends_on", []))
                if item.get("kind", item.get("type")) != "source" and (not isinstance(refs, list) or not refs):
                    errors.append(f"{label} traceability has orphan {item.get('kind', item.get('type'))} node")
                if isinstance(refs, list) and any(str(ref) not in ids for ref in refs):
                    errors.append(f"{label} traceability contains orphan reference")
            statuses = [str(item.get("status", "")).lower() for item in edges]
            if any(status in BLOCKED_CONTRACT_STATUSES for status in statuses) and str(declaration.get("status", "")).lower() in {"pass", "passed", "complete"}:
                errors.append(f"{label} blocked status cannot be declared passing")


def _ordered_public_page_ids(root: Path, errors: list[str]) -> list[str]:
    tutorial_path = root / "tutorial/tutorial-site.json"
    if not tutorial_path.is_file():
        return []
    tutorial = load_json(tutorial_path, errors)
    if not isinstance(tutorial, dict):
        return []
    release_scope = tutorial.get("release_scope", {})
    promised = release_scope.get("promised_page_ids", []) if isinstance(release_scope, dict) else []
    if isinstance(promised, list) and promised:
        return [str(item) for item in promised if str(item).strip()]
    return [str(item.get("page_id")) for item in _records(tutorial, "pages") if item.get("page_id")]


def _sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _valid_sha256(value: Any) -> bool:
    return bool(re.fullmatch(r"sha256:[0-9a-f]{64}", str(value or "")))


def _resolve_package_ref(root: Path, relative: Any, label: str, errors: list[str]) -> Path | None:
    value = str(relative or "").strip()
    if not value:
        errors.append(f"{label} missing package-relative path")
        return None
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        errors.append(f"{label} path escapes package root: {value}")
        return None
    if not path.is_file():
        errors.append(f"{label} references missing file: {value}")
        return None
    return path


def _value_at_path(value: Any, path_parts: list[str]) -> tuple[bool, Any]:
    current = value
    for part in path_parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return False, None
    return current not in (None, "", []), current


def _tutorial_page_anchor_exists(root: Path, value: Any, expected_page_id: str | None = None) -> bool:
    ref = str(value or "").strip()
    parts = ref.split("#")
    if len(parts) == 3:
        file_ref, page_id, anchor = parts
        if file_ref != "tutorial/tutorial-site.json":
            return False
    elif len(parts) == 2 and expected_page_id is not None:
        page_id, anchor = parts
    else:
        return False
    if expected_page_id is not None and page_id != expected_page_id:
        return False
    if not anchor.startswith("content_sections."):
        return False
    tutorial_path = root / "tutorial/tutorial-site.json"
    if not tutorial_path.is_file():
        return False
    try:
        tutorial = json.loads(tutorial_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    page = next((item for item in _records(tutorial, "pages") if str(item.get("page_id", "")) == page_id), None)
    if not isinstance(page, dict):
        return False
    exists, _ = _value_at_path(page, anchor.split("."))
    return exists


def _reviewer_is_independent(author_id: Any, reviewer: Any) -> bool:
    author = re.sub(r"[^a-z0-9]+", "", str(author_id or "").lower())
    review = re.sub(r"[^a-z0-9]+", "", str(reviewer or "").lower())
    if not author or not review or author == review:
        return False
    return not any(marker in review for marker in ("selfreview", "authorself", "samemodel", "modelundertest"))


def validate_source_assimilation_contract(root: Path, errors: list[str]) -> None:
    """Prove that every frozen user-source section and content atom has an explicit disposition."""
    path = root / "research/source-assimilation-ledger.json"
    if not path.is_file():
        errors.append("missing research/source-assimilation-ledger.json for user-source completeness")
        return
    data = load_json(path, errors)
    if not isinstance(data, dict):
        return
    require_fields(data, ["schema_version", "inventory_version", "sources", "sections", "atoms", "coverage_receipt"], "source assimilation ledger", errors)
    sources = _records(data, "sources")
    sections = _records(data, "sections")
    atoms = _records(data, "atoms")
    if not sources or not sections or not atoms:
        errors.append("source assimilation ledger needs sources, sections, and content atoms")
        return

    source_ids: set[str] = set()
    frozen_inventories: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources):
        label = f"source assimilation source {index}"
        require_fields(source, ["source_id", "path", "sha256", "authority", "scope", "owner", "format"], label, errors)
        source_id = str(source.get("source_id", "")).strip()
        if not source_id or source_id in source_ids:
            errors.append(f"{label} has empty or duplicate source_id")
            continue
        source_ids.add(source_id)
        frozen_path = _resolve_package_ref(root, source.get("path"), label, errors)
        if frozen_path is None:
            continue
        if "sha256:" + hashlib.sha256(frozen_path.read_bytes()).hexdigest() != str(source.get("sha256", "")):
            errors.append(f"{label} frozen source hash drift")
        try:
            frozen_inventories[source_id] = inventory_source(frozen_path, source_id, root)
        except Exception as exc:
            errors.append(f"{label} cannot be inventoried: {exc}")

    def validate_items(items: list[dict[str, Any]], kind: str) -> set[str]:
        ids: set[str] = set()
        for index, item in enumerate(items):
            label = f"source assimilation {kind} {index}"
            require_fields(item, ["id", "source_id", "locator", "start_line", "end_line", "sha256", "meaning", "disposition", "target_refs", "rationale", "owner", "evidence_refs"], label, errors)
            item_id = str(item.get("id", "")).strip()
            if not item_id or item_id in ids:
                errors.append(f"{label} has empty or duplicate id")
            ids.add(item_id)
            if str(item.get("source_id", "")) not in source_ids:
                errors.append(f"{label} references unknown source_id")
            disposition = str(item.get("disposition", "")).lower()
            if disposition not in ASSIMILATION_DISPOSITIONS:
                errors.append(f"{label} has unmapped or invalid disposition")
                continue
            target_refs = item.get("target_refs", [])
            evidence_refs = item.get("evidence_refs", [])
            if disposition in {"incorporated", "adapted"}:
                if not isinstance(target_refs, list) or not target_refs:
                    errors.append(f"{label} {disposition} item needs learner-facing target_refs")
                else:
                    for ref in target_refs:
                        _resolve_package_ref(root, ref, f"{label} target", errors)
            if disposition in {"rejected", "blocked", "superseded"}:
                if not str(item.get("rationale", "")).strip() or not str(item.get("owner", "")).strip():
                    errors.append(f"{label} {disposition} item needs rationale and owner")
                if not isinstance(evidence_refs, list) or not evidence_refs:
                    errors.append(f"{label} {disposition} item needs evidence or closure refs")
                else:
                    for ref in evidence_refs:
                        _resolve_package_ref(root, ref, f"{label} evidence", errors)
            if not str(item.get("meaning", "")).strip():
                errors.append(f"{label} missing protected meaning")
        return ids

    section_ids = validate_items(sections, "section")
    atom_ids = validate_items(atoms, "atom")
    expected_section_ids = {item["id"] for inventory in frozen_inventories.values() for item in inventory["sections"]}
    expected_atom_ids = {item["id"] for inventory in frozen_inventories.values() for item in inventory["atoms"]}
    if section_ids != expected_section_ids:
        errors.append("source assimilation section inventory does not exactly match frozen sources")
    if atom_ids != expected_atom_ids:
        errors.append("source assimilation atom inventory does not exactly match frozen sources")
    indexed_sections = {item.get("id"): item for inventory in frozen_inventories.values() for item in inventory["sections"]}
    indexed_atoms = {item.get("id"): item for inventory in frozen_inventories.values() for item in inventory["atoms"]}
    for item in sections + atoms:
        expected = indexed_sections.get(item.get("id")) or indexed_atoms.get(item.get("id"))
        if expected and any(item.get(field) != expected.get(field) for field in ("source_id", "locator", "start_line", "end_line", "sha256")):
            errors.append(f"source assimilation item {item.get('id')} locator or content hash drift")

    receipt = data.get("coverage_receipt")
    if not isinstance(receipt, dict):
        errors.append("source assimilation ledger missing coverage_receipt object")
        return
    receipt_fields = ["source_count", "section_count", "atom_count", "accounted_section_count", "accounted_atom_count", "disposition_counts", "unaccounted_ids", "inventory_command", "reviewer", "reviewed_at", "verdict"]
    for field in receipt_fields:
        if field not in receipt or (field != "unaccounted_ids" and receipt.get(field) in (None, "")):
            errors.append(f"source assimilation coverage receipt missing field: {field}")
    expected_counts = (len(sources), len(sections), len(atoms), len(section_ids), len(atom_ids))
    actual_counts = tuple(receipt.get(field) for field in ("source_count", "section_count", "atom_count", "accounted_section_count", "accounted_atom_count"))
    if actual_counts != expected_counts:
        errors.append("source assimilation coverage receipt counts do not close")
    if receipt.get("unaccounted_ids") != [] or receipt.get("verdict") != "PASS":
        errors.append("source assimilation coverage must PASS with zero unaccounted IDs")


def validate_source_semantic_projection_contract(root: Path, errors: list[str]) -> None:
    """Prove that source teaching functions survive as pages, visuals, reusable assets, and exercises."""
    assimilation_path = root / "research/source-assimilation-ledger.json"
    if not assimilation_path.is_file():
        return
    path = root / "research/source-semantic-projection.json"
    if not path.is_file():
        errors.append("missing research/source-semantic-projection.json for source-function fidelity")
        return
    data = load_json(path, errors)
    assimilation = load_json(assimilation_path, errors)
    if not isinstance(data, dict) or not isinstance(assimilation, dict):
        return
    require_fields(data, [
        "schema_version", "source_ledger_ref", "source_ledger_sha256", "units",
        "coverage", "author_id", "reviewer", "reviewed_at", "verdict",
    ], "source semantic projection", errors)
    if not _reviewer_is_independent(data.get("author_id"), data.get("reviewer")):
        errors.append("source semantic projection reviewer must be independent from the author")
    if data.get("source_ledger_ref") != "research/source-assimilation-ledger.json":
        errors.append("source semantic projection must reference research/source-assimilation-ledger.json")
    expected_ledger_hash = "sha256:" + hashlib.sha256(assimilation_path.read_bytes()).hexdigest()
    if data.get("source_ledger_sha256") != expected_ledger_hash:
        errors.append("source semantic projection source ledger hash drift")

    source_items = {
        str(item.get("id")): item
        for item in _records(assimilation, "atoms")
        if item.get("id")
    }
    required_source_ids = {
        item_id for item_id, item in source_items.items()
        if str(item.get("disposition", "")).lower() in {"incorporated", "adapted"}
    }
    units = _records(data, "units")
    seen_unit_ids: set[str] = set()
    covered_source_ids: set[str] = set()
    function_counts: Counter[str] = Counter()
    for index, unit in enumerate(units):
        label = f"source semantic projection unit {index}"
        require_fields(unit, [
            "unit_id", "source_item_ids", "function_kind", "protected_function", "page_refs",
            "adaptation", "verification", "owner", "status",
        ], label, errors)
        for field in ("visual_refs", "reusable_asset_refs", "exercise_refs"):
            if field not in unit:
                errors.append(f"{label} missing field: {field}")
        unit_id = str(unit.get("unit_id", "")).strip()
        if not unit_id or unit_id in seen_unit_ids:
            errors.append(f"{label} has empty or duplicate unit_id")
        seen_unit_ids.add(unit_id)
        source_ids = unit.get("source_item_ids")
        if not isinstance(source_ids, list) or not source_ids:
            errors.append(f"{label} needs source_item_ids")
            source_ids = []
        for source_id in source_ids:
            source_id = str(source_id)
            if source_id not in source_items:
                errors.append(f"{label} references unknown source item: {source_id}")
            else:
                covered_source_ids.add(source_id)
        function_kind = str(unit.get("function_kind", ""))
        if function_kind not in SEMANTIC_FUNCTION_KINDS:
            errors.append(f"{label} has invalid function_kind: {function_kind}")
        else:
            function_counts[function_kind] += 1
        status = str(unit.get("status", "")).lower()
        if status not in SEMANTIC_PROJECTION_STATUSES:
            errors.append(f"{label} has invalid status")
        page_refs = unit.get("page_refs")
        if status in {"projected", "adapted"}:
            if not isinstance(page_refs, list) or not page_refs:
                errors.append(f"{label} projected/adapted function needs a learner-facing page target")
            else:
                for ref in page_refs:
                    if not _tutorial_page_anchor_exists(root, ref):
                        errors.append(f"{label} page_ref needs an exact page and content anchor: {ref}")
        for field in ("visual_refs", "reusable_asset_refs", "exercise_refs"):
            refs = unit.get(field)
            if not isinstance(refs, list):
                errors.append(f"{label} {field} must be a list")
                continue
            for ref in refs:
                _resolve_package_ref(root, ref, f"{label} {field}", errors)
        if function_kind == "visual" and status in {"projected", "adapted"} and not unit.get("visual_refs"):
            errors.append(f"{label} visual function needs a rendered visual target")
        if function_kind in {"template", "prompt-package", "checklist", "self-assessment"} and status in {"projected", "adapted"} and not unit.get("reusable_asset_refs"):
            errors.append(f"{label} {function_kind} function needs a reusable asset")
        if function_kind == "exercise" and status in {"projected", "adapted"} and not unit.get("exercise_refs"):
            errors.append(f"{label} exercise function needs an exercise target")
        adaptation = unit.get("adaptation")
        if not isinstance(adaptation, dict) or not adaptation.get("mode") or not adaptation.get("scope"):
            errors.append(f"{label} needs an explicit adaptation mode and scope")
        if function_kind == "threshold-policy" and status in {"projected", "adapted"}:
            if not isinstance(adaptation, dict) or adaptation.get("mode") not in {"scoped", "parameterized", "blocked", "rejected"} or str(adaptation.get("scope", "")).lower() in {"", "universal"}:
                errors.append(f"{label} threshold-policy must be scoped, parameterized, blocked, or rejected")
            elif not all(adaptation.get(field) for field in ("owner", "evidence_ref", "uncertainty")):
                errors.append(f"{label} threshold-policy adaptation needs owner, evidence_ref, and uncertainty")
        if status in {"blocked", "rejected", "superseded"} and not str(unit.get("verification", "")).strip():
            errors.append(f"{label} non-projected function needs closure evidence in verification")

    coverage = data.get("coverage")
    if not isinstance(coverage, dict):
        errors.append("source semantic projection missing coverage object")
        return
    require_fields(coverage, [
        "required_source_item_ids", "covered_source_item_ids", "function_counts", "verdict",
    ], "source semantic projection coverage", errors)
    if "unaccounted_source_item_ids" not in coverage:
        errors.append("source semantic projection coverage missing field: unaccounted_source_item_ids")
    declared_required = {str(item) for item in coverage.get("required_source_item_ids", [])}
    declared_covered = {str(item) for item in coverage.get("covered_source_item_ids", [])}
    if declared_required != required_source_ids:
        errors.append("source semantic projection required source set does not match incorporated/adapted source items")
    if declared_covered != covered_source_ids:
        errors.append("source semantic projection covered source set does not match its units")
    if required_source_ids - covered_source_ids or coverage.get("unaccounted_source_item_ids") != []:
        errors.append("source semantic projection must account for every incorporated/adapted source item")
    if coverage.get("function_counts") != dict(function_counts):
        errors.append("source semantic projection function counts do not close")
    if data.get("verdict") != "PASS" or coverage.get("verdict") != "PASS":
        errors.append("source semantic projection must PASS before course promotion")


def _page_content_hash(page: dict[str, Any]) -> str:
    content = page.get("content_sections", {})
    serialized = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return _sha256_text(serialized)


def validate_page_projection_ledger(root: Path, page: dict[str, Any], errors: list[str]) -> None:
    page_id = str(page.get("page_id", "")).strip()
    topic_dir = root / "research/topics" / page_id
    path = topic_dir / "projection-ledger.json"
    if not path.is_file():
        errors.append(f"{page_id} missing projection-ledger.json for research-to-page fidelity")
        return
    data = load_json(path, errors)
    if not isinstance(data, dict):
        return
    require_fields(data, [
        "schema_version", "topic_id", "manuscript_sha256", "page_content_sha256",
        "claims", "counts", "author_id", "reviewer", "verdict",
    ], f"{page_id} projection ledger", errors)
    if not _reviewer_is_independent(data.get("author_id"), data.get("reviewer")):
        errors.append(f"{page_id} projection reviewer must be independent from the author")
    if data.get("topic_id") != page_id:
        errors.append(f"{page_id} projection ledger topic_id mismatch")
    manuscript_path = topic_dir / "manuscript.md"
    if manuscript_path.is_file():
        expected = "sha256:" + hashlib.sha256(manuscript_path.read_bytes()).hexdigest()
        if data.get("manuscript_sha256") != expected:
            errors.append(f"{page_id} projection ledger manuscript hash drift")
    if data.get("page_content_sha256") != _page_content_hash(page):
        errors.append(f"{page_id} projection ledger page content hash drift")
    claims = _records(data, "claims")
    if not claims:
        errors.append(f"{page_id} projection ledger needs protected research claims")
    dispositions: Counter[str] = Counter()
    claim_ids: set[str] = set()
    for index, claim in enumerate(claims):
        label = f"{page_id} projection claim {index}"
        require_fields(claim, [
            "claim_id", "manuscript_locator", "meaning", "kind", "disposition",
            "rationale", "owner",
        ], label, errors)
        if "page_target" not in claim:
            errors.append(f"{label} missing field: page_target")
        claim_id = str(claim.get("claim_id", "")).strip()
        if not claim_id or claim_id in claim_ids:
            errors.append(f"{label} has empty or duplicate claim_id")
        claim_ids.add(claim_id)
        kind = str(claim.get("kind", ""))
        disposition = str(claim.get("disposition", ""))
        if kind not in PAGE_PROJECTION_CLAIM_KINDS:
            errors.append(f"{label} has invalid kind")
        if disposition not in {"projected", "condensed", "deferred", "rejected"}:
            errors.append(f"{label} has invalid disposition")
        else:
            dispositions[disposition] += 1
        if kind in PAGE_PROJECTION_CRITICAL_KINDS and disposition in {"deferred", "rejected"}:
            errors.append(f"{label} critical claim cannot be deferred or rejected")
        if disposition in {"projected", "condensed"} and not _tutorial_page_anchor_exists(root, claim.get("page_target"), page_id):
            errors.append(f"{label} references a missing learner-page anchor")
        if disposition in {"condensed", "deferred", "rejected"} and not str(claim.get("rationale", "")).strip():
            errors.append(f"{label} needs a disposition rationale")
    counts = data.get("counts")
    expected_counts = {
        "total":len(claims), "projected":dispositions["projected"],
        "condensed":dispositions["condensed"], "deferred":dispositions["deferred"],
        "rejected":dispositions["rejected"], "unaccounted":0,
    }
    if counts != expected_counts:
        errors.append(f"{page_id} projection ledger counts do not close")
    if not str(data.get("reviewer", "")).strip() or data.get("verdict") != "PASS":
        errors.append(f"{page_id} projection ledger needs an independent reviewer and PASS verdict")


def validate_learner_usability_and_reuse_contract(root: Path, errors: list[str]) -> None:
    public_ids = _ordered_public_page_ids(root, errors)
    if not public_ids:
        return
    path = root / "research/learner-usability-reuse.json"
    if not path.is_file():
        errors.append("missing research/learner-usability-reuse.json for beginner comprehension and direct reuse")
        return
    data = load_json(path, errors)
    if not isinstance(data, dict):
        return
    require_fields(data, ["schema_version", "pages", "learner_evidence_boundary", "verdict"], "learner usability and reuse", errors)
    pages = _records(data, "pages")
    by_id = {str(item.get("page_id", "")): item for item in pages if item.get("page_id")}
    if set(by_id) != set(public_ids) or len(by_id) != len(pages):
        errors.append("learner usability page set must exactly equal promised public page set")
    introduced_by_page: dict[str, set[str]] = {}
    seen_terms: set[str] = set()
    for number, page_id in enumerate(public_ids, start=1):
        page = by_id.get(page_id)
        if not page:
            continue
        label = f"learner usability page {page_id}"
        page_fields = ["page_id", "display_number", "prerequisite_ids", "assumed_knowledge", "terms_introduced", "terms_used", "mental_model", "worked_example", "counterexample", "learner_action", "failure_diagnosis", "comprehension_checks", "reusable_artifacts"]
        for field in page_fields:
            if field not in page or (field not in {"prerequisite_ids", "assumed_knowledge", "terms_introduced", "terms_used"} and page.get(field) in (None, "")):
                errors.append(f"{label} missing field: {field}")
        if page.get("display_number") != number:
            errors.append(f"{label} display_number must be contiguous 1..N")
        introduced = _records(page, "terms_introduced")
        introduced_terms: set[str] = set()
        for index, term in enumerate(introduced):
            require_fields(term, ["term", "plain_definition", "first_use_ref"], f"{label} introduced term {index}", errors)
            if term.get("term"):
                introduced_terms.add(str(term["term"]).strip().lower())
        introduced_by_page[page_id] = introduced_terms
        available = seen_terms | introduced_terms | {str(item).strip().lower() for item in page.get("assumed_knowledge", []) if str(item).strip()}
        used = {str(item).strip().lower() for item in page.get("terms_used", []) if str(item).strip()}
        missing_terms = used - available
        if missing_terms:
            errors.append(f"{label} uses terms before introduction: {', '.join(sorted(missing_terms))}")
        seen_terms.update(introduced_terms)
        for field in ("worked_example", "counterexample"):
            value = page.get(field)
            if not isinstance(value, dict) or not value.get("input") or not value.get("expected_observation"):
                errors.append(f"{label} {field} needs input and expected_observation")
        action = page.get("learner_action")
        if not isinstance(action, dict) or not action.get("input_ref") or not action.get("action") or not action.get("expected_result"):
            errors.append(f"{label} learner_action needs input_ref, action, and expected_result")
        elif _resolve_package_ref(root, action.get("input_ref"), f"{label} learner action", errors) is None:
            pass
        diagnosis = page.get("failure_diagnosis")
        if not isinstance(diagnosis, dict) or not all(diagnosis.get(field) for field in ("symptom", "diagnosis_steps", "repair", "rerun_check")):
            errors.append(f"{label} failure_diagnosis needs symptom, diagnosis_steps, repair, and rerun_check")
        checks = page.get("comprehension_checks")
        if not isinstance(checks, list) or not checks:
            errors.append(f"{label} needs comprehension checks")
        else:
            for index, check in enumerate(checks):
                if not isinstance(check, dict) or not all(check.get(field) for field in ("question", "expected_answer", "common_misconception")):
                    errors.append(f"{label} comprehension check {index} is incomplete")
        artifacts = page.get("reusable_artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            errors.append(f"{label} needs at least one reusable artifact")
        else:
            for index, artifact in enumerate(artifacts):
                artifact_label = f"{label} reusable artifact {index}"
                if not isinstance(artifact, dict):
                    errors.append(f"{artifact_label} is not an object")
                    continue
                require_fields(artifact, ["artifact_id", "path", "purpose", "inputs", "editable_fields", "outputs", "adaptation_steps", "validation", "limitations", "owner"], artifact_label, errors)
                _resolve_package_ref(root, artifact.get("path"), artifact_label, errors)
                for field in ("inputs", "editable_fields", "outputs"):
                    if not isinstance(artifact.get(field), list) or not artifact.get(field):
                        errors.append(f"{artifact_label} needs non-empty {field}")
                if not isinstance(artifact.get("adaptation_steps"), list) or len(artifact.get("adaptation_steps", [])) < 2:
                    errors.append(f"{artifact_label} needs scenario adaptation and validation steps")
                validation = artifact.get("validation")
                if not isinstance(validation, dict) or not validation.get("method") or not validation.get("expected_evidence"):
                    errors.append(f"{artifact_label} validation needs method and expected_evidence")
    boundary = data.get("learner_evidence_boundary")
    if not isinstance(boundary, dict) or boundary.get("status") not in EVIDENCE_STATUSES or not boundary.get("limitations"):
        errors.append("learner usability contract needs explicit learner evidence status and limitations")


def validate_visual_sequence_contract(root: Path, errors: list[str]) -> None:
    public_ids = _ordered_public_page_ids(root, errors)
    if not public_ids:
        return
    path = root / "research/visual-sequence-manifest.json"
    if not path.is_file():
        errors.append("missing research/visual-sequence-manifest.json for continuous numbering and topic visuals")
        return
    data = load_json(path, errors)
    if not isinstance(data, dict):
        return
    require_fields(data, ["schema_version", "ordered_page_ids", "pages", "verdict"], "visual sequence manifest", errors)
    if data.get("ordered_page_ids") != public_ids:
        errors.append("visual sequence ordered_page_ids must exactly equal promised navigation order")
    pages = _records(data, "pages")
    by_id = {str(item.get("page_id", "")): item for item in pages if item.get("page_id")}
    if set(by_id) != set(public_ids) or len(by_id) != len(pages):
        errors.append("visual sequence page set must exactly equal promised public page set")
    visual_paths: set[str] = set()
    index_by_id = {page_id: index for index, page_id in enumerate(public_ids, start=1)}
    tutorial = load_json(root / "tutorial/tutorial-site.json", errors)
    tutorial_by_id = {str(page.get("page_id")): page for page in _records(tutorial, "pages")} if isinstance(tutorial, dict) else {}
    for number, page_id in enumerate(public_ids, start=1):
        page = by_id.get(page_id)
        if not page:
            continue
        label = f"visual sequence page {page_id}"
        page_fields = ["page_id", "display_number", "prerequisite_ids", "knowledge_relationship", "required_visual_kinds", "visuals"]
        for field in page_fields:
            if field not in page or (field != "prerequisite_ids" and page.get(field) in (None, "")):
                errors.append(f"{label} missing field: {field}")
        if page.get("display_number") != number:
            errors.append(f"{label} display_number must be contiguous 1..N")
        tutorial_page = tutorial_by_id.get(page_id, {})
        expected_prereqs = tutorial_page.get("prerequisite_ids", []) if isinstance(tutorial_page, dict) else []
        if page.get("prerequisite_ids") != expected_prereqs:
            errors.append(f"{label} prerequisite_ids drift from tutorial source")
        for dependency in page.get("prerequisite_ids", []):
            if index_by_id.get(str(dependency), number) >= number:
                errors.append(f"{label} prerequisite must appear earlier in navigation")
        required_kinds = set(page.get("required_visual_kinds", [])) if isinstance(page.get("required_visual_kinds"), list) else set()
        provided_kinds: set[str] = set()
        visuals = page.get("visuals")
        if not isinstance(visuals, list) or not visuals:
            errors.append(f"{label} needs topic-specific visual artifacts")
            continue
        for index, visual in enumerate(visuals):
            visual_label = f"{label} visual {index}"
            if not isinstance(visual, dict):
                errors.append(f"{visual_label} is not an object")
                continue
            require_fields(visual, ["visual_id", "kind", "purpose", "source_path", "alt_text", "caption", "nodes", "edges", "source_refs"], visual_label, errors)
            provided_kinds.add(str(visual.get("kind", "")))
            source_path = str(visual.get("source_path", ""))
            resolved = _resolve_package_ref(root, source_path, visual_label, errors)
            if resolved and resolved.suffix.lower() not in VISUAL_EXTENSIONS:
                errors.append(f"{visual_label} must use a repository-owned SVG or Mermaid source")
            if source_path in visual_paths:
                errors.append(f"{visual_label} reuses a visual path across unrelated pages")
            visual_paths.add(source_path)
            if not isinstance(visual.get("nodes"), list) or len(visual.get("nodes", [])) < 5:
                errors.append(f"{visual_label} needs at least 5 meaningful nodes")
            if not isinstance(visual.get("edges"), list) or len(visual.get("edges", [])) < 4:
                errors.append(f"{visual_label} needs at least 4 meaningful relationships")
            if not isinstance(visual.get("source_refs"), list) or not visual.get("source_refs"):
                errors.append(f"{visual_label} needs source refs")
        if not required_kinds or not required_kinds.issubset(provided_kinds):
            errors.append(f"{label} does not satisfy required visual kinds")
    if data.get("verdict") != "PASS":
        errors.append("visual sequence manifest verdict must PASS")


def validate_software_testing_adapter_contract(root: Path, errors: list[str]) -> None:
    declaration_path = next((root / name for name in CAPABILITY_DECLARATION_FILES if (root / name).is_file()), None)
    declarations = _records(load_json(declaration_path, errors), "capabilities") if declaration_path is not None else []
    active = {str(item.get("capability", item.get("capability_id", ""))).strip().lower() for item in declarations}
    required_from_sources: set[str] = set()
    assimilation_path = root / "research/source-assimilation-ledger.json"
    if assimilation_path.is_file():
        assimilation = load_json(assimilation_path, errors)
        for source in _records(assimilation, "sources") if isinstance(assimilation, dict) else []:
            required_from_sources.update(str(item).strip().lower() for item in source.get("detected_obligations", []) if str(item).strip())
    triggered = active.intersection({"career-evolution-system", "agent-architecture-testing"}) | required_from_sources
    if not triggered:
        return
    missing_declarations = required_from_sources - active
    if missing_declarations:
        errors.append(f"source-detected professional obligations need explicit capability declarations: {', '.join(sorted(missing_declarations))}")
    path = root / "research/software-testing-career-agent-adapter.json"
    if not path.is_file():
        errors.append("declared career/agent architecture capability missing research/software-testing-career-agent-adapter.json")
        return
    data = load_json(path, errors)
    if not isinstance(data, dict):
        return
    require_fields(data, ["schema_version", "responsibility_states", "self_assessment", "organization_level_adapter", "agent_domains", "evidence_rings", "domain_test_mappings", "statistical_semantics", "metric_card_policy", "owners", "evidence_refs", "maturity_boundary"], "software testing career/agent adapter", errors)
    states = {str(item.get("state_id", "")) for item in _records(data, "responsibility_states")}
    if states != CAREER_RESPONSIBILITY_STATES:
        errors.append("software testing career adapter must define the four evidence-based responsibility states")
    for index, item in enumerate(_records(data, "self_assessment")):
        require_fields(item, ["dimension_id", "question", "evidence_refs", "gap_route_page_ids", "reviewer"], f"career self-assessment dimension {index}", errors)
    organization = data.get("organization_level_adapter")
    if not isinstance(organization, dict) or organization.get("status") not in {"INTERNAL-UNKNOWN", "CONFIGURED"} or not organization.get("owner") or not organization.get("evidence_refs"):
        errors.append("organization level adapter needs explicit INTERNAL-UNKNOWN/CONFIGURED status, owner, and evidence refs")
    domains = {str(item.get("domain_id", "")) for item in _records(data, "agent_domains")}
    if domains != AGENT_ARCHITECTURE_DOMAINS:
        errors.append("agent architecture adapter must define exact D0-D7 domains")
    rings = {str(item.get("ring_id", "")) for item in _records(data, "evidence_rings")}
    if rings != AGENT_EVIDENCE_RINGS:
        errors.append("agent architecture adapter must define four evidence rings")
    for index, mapping in enumerate(_records(data, "domain_test_mappings")):
        require_fields(mapping, ["domain_id", "architecture_boundary", "risks", "observables", "methods", "independent_oracles", "cases_faults", "evidence_refs", "stop_decision"], f"agent domain test mapping {index}", errors)
    if {str(item.get("domain_id", "")) for item in _records(data, "domain_test_mappings")} != AGENT_ARCHITECTURE_DOMAINS:
        errors.append("agent architecture adapter must map every D0-D7 domain to test evidence")
    stats = data.get("statistical_semantics")
    if not isinstance(stats, dict) or not all(stats.get(field) for field in ("pass_at_k", "pass_power_k", "repeat_unit", "state_reset", "uncertainty_method")):
        errors.append("agent architecture adapter must distinguish pass@k/pass^k and define repeated-run uncertainty")
    policy = data.get("metric_card_policy")
    required_metric_fields = {"task_population", "numerator", "denominator", "slice", "baseline", "uncertainty", "sample_size_rationale", "version", "owner", "failure_action"}
    if not isinstance(policy, dict) or set(policy.get("required_fields", [])) != required_metric_fields or policy.get("universal_thresholds_allowed") is not False:
        errors.append("agent architecture metric-card policy must reject universal thresholds and require scoped decision fields")


def validate_professional_capability_and_evidence_contract(root: Path, errors: list[str]) -> None:
    """Require every learner-facing page to declare capability and evidence boundaries."""
    public_ids = _ordered_public_page_ids(root, errors)
    if not public_ids:
        return
    public_set = set(public_ids)

    declaration_path = next((root / name for name in CAPABILITY_DECLARATION_FILES if (root / name).is_file()), None)
    if declaration_path is None:
        errors.append("missing research/capability-declarations.json for learner-facing pages")
        declarations: list[dict[str, Any]] = []
    else:
        declarations = _records(load_json(declaration_path, errors), "capabilities")
    declared_coverage: dict[str, set[str]] = {}
    for index, declaration in enumerate(declarations):
        capability = str(declaration.get("capability", declaration.get("capability_id", ""))).strip().lower()
        if capability not in PROFESSIONAL_CAPABILITIES:
            errors.append(f"capability declaration {index} has unsupported capability: {capability or '<empty>'}")
            continue
        topics = declaration.get("topics", declaration.get("topic_ids", declaration.get("pages", declaration.get("page_ids", []))))
        if not isinstance(topics, list) or not topics:
            errors.append(f"capability declaration {index} must name exact topic/page IDs")
            continue
        if not declaration.get("owner") or not declaration.get("evidence"):
            errors.append(f"capability declaration {index} needs owner and evidence")
        declared_coverage.setdefault(capability, set()).update(str(item) for item in topics)

    profile_path = root / "research/capability-profiles.json"
    profile_by_page: dict[str, dict[str, Any]] = {}
    if not profile_path.is_file():
        errors.append("missing research/capability-profiles.json for learner-facing pages")
    else:
        profiles = _records(load_json(profile_path, errors), "pages")
        for index, profile in enumerate(profiles):
            page_id = str(profile.get("page_id", "")).strip()
            if not page_id:
                errors.append(f"capability profile {index} missing page_id")
                continue
            if page_id in profile_by_page:
                errors.append(f"duplicate capability profile for page: {page_id}")
                continue
            profile_by_page[page_id] = profile
            capabilities = profile.get("capabilities", [])
            if not isinstance(capabilities, list) or not capabilities or any(str(item).lower() not in PROFESSIONAL_CAPABILITIES for item in capabilities):
                errors.append(f"capability profile {page_id} must declare at least one professional capability")
                continue
            if len({str(item).lower() for item in capabilities}) != len(capabilities):
                errors.append(f"capability profile {page_id} contains duplicate capabilities")
            for field in ("rationale", "risk", "reviewer", "reviewed_at", "evidence_refs"):
                if not profile.get(field):
                    errors.append(f"capability profile {page_id} missing field: {field}")
            for capability in {str(item).lower() for item in capabilities}:
                if page_id not in declared_coverage.get(capability, set()):
                    errors.append(f"page {page_id} capability {capability} is not covered by capability declarations")
        missing_profiles = public_set - set(profile_by_page)
        extra_profiles = set(profile_by_page) - public_set
        for page_id in sorted(missing_profiles):
            errors.append(f"capability profile missing public page: {page_id}")
        for page_id in sorted(extra_profiles):
            errors.append(f"capability profile references non-public page: {page_id}")

    evidence_path = root / "research/professional-evidence.json"
    evidence_by_page: dict[str, dict[str, Any]] = {}
    if not evidence_path.is_file():
        errors.append("missing research/professional-evidence.json for learner-facing pages")
    else:
        evidence_records = _records(load_json(evidence_path, errors), "pages")
        for index, record in enumerate(evidence_records):
            page_id = str(record.get("page_id", "")).strip()
            if not page_id:
                errors.append(f"professional evidence record {index} missing page_id")
                continue
            if page_id in evidence_by_page:
                errors.append(f"duplicate professional evidence record for page: {page_id}")
                continue
            evidence_by_page[page_id] = record
            maturity = str(record.get("maturity_claim", "")).strip().lower()
            if maturity not in {"desk-researched", "fixture-tested", "model-integrated", "integration-tested", "practitioner-reviewed", "production-validated"}:
                errors.append(f"professional evidence {page_id} has invalid maturity_claim")
            lane_status: dict[str, str] = {}
            for lane in EVIDENCE_LANES:
                lane_record = record.get(lane)
                if not isinstance(lane_record, dict):
                    errors.append(f"professional evidence {page_id} missing lane: {lane}")
                    continue
                status = str(lane_record.get("status", "")).upper()
                lane_status[lane] = status
                if status not in EVIDENCE_STATUSES:
                    errors.append(f"professional evidence {page_id} {lane} has invalid status")
                receipts = lane_record.get("receipt_refs")
                if not isinstance(receipts, list):
                    errors.append(f"professional evidence {page_id} {lane} receipt_refs must be a list")
                if status == "PASS" and (not isinstance(receipts, list) or not receipts):
                    errors.append(f"professional evidence {page_id} {lane} PASS needs receipt_refs")
                if not str(lane_record.get("limitations", "")).strip():
                    errors.append(f"professional evidence {page_id} {lane} missing limitations")

            model = record.get("model", {})
            if isinstance(model, dict) and str(model.get("status", "")).upper() == "PASS":
                provider = str(model.get("provider", "")).strip().lower()
                if provider in {"", "none", "offline", "fixture", "deterministic"}:
                    errors.append(f"professional evidence {page_id} model PASS cannot use provider none/offline")
                for field in ("model", "version", "parameters", "repeats", "raw_output_hashes", "scorer_ref", "oracle_owner"):
                    if model.get(field) in (None, "", [], {}):
                        errors.append(f"professional evidence {page_id} model PASS missing field: {field}")
                repeats = model.get("repeats")
                raw_hashes = model.get("raw_output_hashes", [])
                if not isinstance(repeats, int) or repeats < 2:
                    errors.append(f"professional evidence {page_id} model PASS needs at least 2 repeated runs")
                if not isinstance(raw_hashes, list) or not isinstance(repeats, int) or len(raw_hashes) < repeats or any(not _valid_sha256(item) for item in raw_hashes):
                    errors.append(f"professional evidence {page_id} model PASS needs one valid raw output hash per run")
                if str(model.get("oracle_owner", "")).strip().lower() in {"model-under-test", "model under test", "self", "same-model"}:
                    errors.append(f"professional evidence {page_id} model under test cannot own its oracle")

            integration = record.get("integration", {})
            if isinstance(integration, dict) and str(integration.get("status", "")).upper() == "PASS":
                for field in ("target_system", "environment", "auth_mode", "cleanup", "rollback"):
                    if not integration.get(field):
                        errors.append(f"professional evidence {page_id} integration PASS missing field: {field}")

            clean_room = record.get("clean_room", {})
            if isinstance(clean_room, dict) and str(clean_room.get("status", "")).upper() == "PASS":
                for field in ("command", "working_directory", "expected_exit_code", "artifact_hash", "platforms", "command_surfaces"):
                    if clean_room.get(field) in (None, "", [], {}):
                        errors.append(f"professional evidence {page_id} clean_room PASS missing field: {field}")
                if not _valid_sha256(clean_room.get("artifact_hash")):
                    errors.append(f"professional evidence {page_id} clean_room artifact_hash must be sha256")
                command = str(clean_room.get("command", ""))
                surfaces = clean_room.get("command_surfaces", [])
                if isinstance(surfaces, list):
                    for surface in surfaces:
                        surface_path = root / str(surface)
                        if not surface_path.is_file():
                            errors.append(f"professional evidence {page_id} clean-room surface missing: {surface}")
                        elif command and command not in surface_path.read_text(encoding="utf-8"):
                            errors.append(f"professional evidence {page_id} clean-room command is absent from surface: {surface}")

            practitioner = record.get("practitioner", {})
            if isinstance(practitioner, dict) and str(practitioner.get("status", "")).upper() == "PASS":
                for field in ("reviewer_identity", "qualification", "scope", "reviewed_at", "verdict", "conflicts"):
                    if practitioner.get(field) in (None, "", []):
                        errors.append(f"professional evidence {page_id} practitioner PASS missing field: {field}")

            learner = record.get("learner", {})
            if isinstance(learner, dict) and str(learner.get("status", "")).upper() == "PASS":
                if not isinstance(learner.get("participants"), int) or learner.get("participants", 0) < 5:
                    errors.append(f"professional evidence {page_id} learner PASS needs at least 5 target learners")
                for field in ("target_profile", "task_completion_rate", "transfer_success_rate", "time_on_task_minutes", "error_recovery_rate"):
                    if learner.get(field) in (None, ""):
                        errors.append(f"professional evidence {page_id} learner PASS missing field: {field}")

            if maturity == "fixture-tested" and lane_status.get("clean_room") != "PASS":
                errors.append(f"professional evidence {page_id} fixture-tested maturity requires clean_room PASS")
            if maturity == "model-integrated" and (lane_status.get("clean_room") != "PASS" or lane_status.get("model") != "PASS"):
                errors.append(f"professional evidence {page_id} model-integrated maturity requires clean_room and model PASS")
            if maturity == "integration-tested" and (lane_status.get("clean_room") != "PASS" or lane_status.get("model") != "PASS" or lane_status.get("integration") != "PASS"):
                errors.append(f"professional evidence {page_id} integration-tested maturity requires clean_room, model, and integration PASS")
            if maturity == "practitioner-reviewed" and lane_status.get("practitioner") != "PASS":
                errors.append(f"professional evidence {page_id} practitioner-reviewed maturity requires practitioner PASS")
            if maturity == "production-validated" and any(lane_status.get(lane) != "PASS" for lane in EVIDENCE_LANES):
                errors.append(f"professional evidence {page_id} production-validated maturity requires every evidence lane PASS")

        for page_id in sorted(public_set - set(evidence_by_page)):
            errors.append(f"professional evidence missing public page: {page_id}")
        for page_id in sorted(set(evidence_by_page) - public_set):
            errors.append(f"professional evidence references non-public page: {page_id}")


def validate_status_supersession_contract(root: Path, errors: list[str]) -> None:
    """Reject stale, contradictory, or untracked human-facing verdicts."""
    public_ids = _ordered_public_page_ids(root, errors)
    if not public_ids:
        return
    registry_path = root / "research/status-registry.json"
    if not registry_path.is_file():
        errors.append("missing research/status-registry.json for human-facing verdicts")
        return
    records = _records(load_json(registry_path, errors), "records")
    by_id: dict[str, dict[str, Any]] = {}
    tracked_paths: set[str] = set()
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    expected_scope_hash = _sha256_text(json.dumps(public_ids, ensure_ascii=False, separators=(",", ":")))
    for index, record in enumerate(records):
        record_id = str(record.get("record_id", "")).strip()
        if not record_id or record_id in by_id:
            errors.append(f"status registry record {index} needs a unique record_id")
            continue
        by_id[record_id] = record
        path_value = str(record.get("path", "")).strip()
        tracked_paths.add(path_value)
        for field in ("artifact_type", "scope_id", "path", "as_of", "scope_hash", "artifact_hash", "status", "evidence_refs"):
            if record.get(field) in (None, "", []):
                errors.append(f"status registry {record_id} missing field: {field}")
        if record.get("status") not in {"current", "superseded"}:
            errors.append(f"status registry {record_id} has invalid status")
        if record.get("scope_hash") != expected_scope_hash:
            errors.append(f"status registry {record_id} scope hash does not match current public scope")
        artifact_path = root / path_value
        if not artifact_path.is_file():
            errors.append(f"status registry {record_id} artifact path is missing: {path_value}")
        else:
            actual_hash = "sha256:" + hashlib.sha256(artifact_path.read_bytes()).hexdigest()
            if record.get("artifact_hash") != actual_hash:
                errors.append(f"status artifact hash mismatch: {record_id}")
        key = (str(record.get("artifact_type", "")), str(record.get("scope_id", "")))
        groups.setdefault(key, []).append(record)

    verdict_files = {
        str(path.relative_to(root))
        for path in (root / "human-review").glob("0[4-9]-*.md")
        if path.is_file()
    }
    for path in sorted(verdict_files - tracked_paths):
        errors.append(f"untracked human-review verdict: {path}")

    for key, group in groups.items():
        current = [record for record in group if record.get("status") == "current"]
        if len(current) != 1:
            errors.append(f"status registry {key[0]}/{key[1]} must have exactly one current record")
            continue
        superseded_ids = {str(record.get("record_id")) for record in group if record.get("status") == "superseded"}
        declared = set(str(item) for item in current[0].get("supersedes", []))
        if superseded_ids - declared:
            errors.append(f"status registry current record does not supersede every older verdict: {key[0]}/{key[1]}")


def require_fields(record: dict[str, Any], fields: list[str], label: str, errors: list[str]) -> None:
    for field in fields:
        value = record.get(field)
        if value is None or value == "" or value == []:
            errors.append(f"{label} missing field: {field}")


def validate_topic_manuscript(text: str, label: str, errors: list[str]) -> None:
    """Require a teachable problem/action/repair chain without fixed headings."""
    headings = re.findall(r"^##\s+\S.*$", text, flags=re.MULTILINE)
    if len(headings) < 3:
        errors.append(f"{label} needs at least three substantive H2 sections")

    semantic_signals = {
        "professional problem": r"professional problem|problem|问题|风险|冲突|故障|失败",
        "runnable action": r"runnable action|action|运行|执行|复制|命令|跟做",
        "failure and repair": r"failure and repair|repair|失败|修复|诊断|恢复",
    }
    for signal, pattern in semantic_signals.items():
        if not re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"{label} missing semantic section: {signal}")

    method_chain_patterns = [
        r"method|方法|决策表|状态机|边界|切片|风险",
        r"oracle",
        r"prompt",
        r"eval",
        r"mutation|变异",
    ]
    method_chain_count = sum(
        bool(re.search(pattern, text, flags=re.IGNORECASE))
        for pattern in method_chain_patterns
    )
    if method_chain_count < 2:
        errors.append(
            f"{label} needs at least two explicit method/oracle/prompt/eval/mutation signals"
        )


def validate_topic_research(root: Path, page_id: str, errors: list[str]) -> None:
    topic_dir = root / "research" / "topics" / page_id
    if not topic_dir.is_dir():
        errors.append(f"tutorial promised page {page_id} missing per-topic research directory")
        return

    minimum_lengths = {
        "research-brief.md": 120,
        "evidence-synthesis.md": 1200,
        "engineering-blueprint.md": 1200,
        "manuscript.md": 1200,
        "comparison.md": 800,
        "validation.md": 180,
    }
    for filename, markers in REQUIRED_TOPIC_RESEARCH_FILES.items():
        path = topic_dir / filename
        if not path.is_file():
            errors.append(f"tutorial promised page {page_id} missing {filename}")
            continue
        text = path.read_text(encoding="utf-8")
        if len(text.strip()) < minimum_lengths[filename]:
            errors.append(f"tutorial promised page {page_id} {filename} is too thin")
        for marker in markers:
            if marker not in text:
                errors.append(f"tutorial promised page {page_id} {filename} missing marker: {marker}")
        if filename == "manuscript.md":
            validate_topic_manuscript(
                text,
                f"tutorial promised page {page_id} manuscript.md",
                errors,
            )

    source_pack = topic_dir / "source-pack.csv"
    if not source_pack.is_file():
        errors.append(f"tutorial promised page {page_id} missing source-pack.csv")
    else:
        rows, columns = load_csv(source_pack, errors)
        missing_columns = set(REQUIRED_TOPIC_SOURCE_COLUMNS) - set(columns)
        if missing_columns:
            errors.append(f"tutorial promised page {page_id} source-pack.csv missing columns: {', '.join(sorted(missing_columns))}")
        if len(rows) < 10:
            errors.append(f"tutorial promised page {page_id} source pack needs at least 10 opened sources")
        lanes = {row.get("evidence_lane", "").strip() for row in rows if row.get("evidence_lane", "").strip()}
        families = {row.get("source_family", "").strip() for row in rows if row.get("source_family", "").strip()}
        source_types = {row.get("source_type", "").strip() for row in rows if row.get("source_type", "").strip()}
        if len(lanes) < 5:
            errors.append(f"tutorial promised page {page_id} source pack needs at least 5 evidence lanes")
        if len(families) < 5:
            errors.append(f"tutorial promised page {page_id} source pack needs at least 5 source families")
        if len(source_types) < 4:
            errors.append(f"tutorial promised page {page_id} source pack needs at least 4 source types")
        for index, row in enumerate(rows):
            if not is_http_url(row.get("url", "")):
                errors.append(f"tutorial promised page {page_id} source row {index} has invalid direct URL")
            if row.get("opened_status", "").strip().lower() != "opened":
                errors.append(f"tutorial promised page {page_id} source row {index} was not opened")
            if not row.get("supports", "").strip() or not row.get("limitations", "").strip():
                errors.append(f"tutorial promised page {page_id} source row {index} lacks claim support or limitations")

    research_runs_path = topic_dir / "research-runs.json"
    research_runs = load_json(research_runs_path, errors) if research_runs_path.is_file() else None
    if research_runs is None:
        errors.append(f"tutorial promised page {page_id} missing or invalid research-runs.json")
    elif isinstance(research_runs, dict):
        runs = research_runs.get("runs", [])
        run_ids = {str(run.get("run_id")) for run in runs if isinstance(run, dict) and run.get("run_id")}
        if len(run_ids) < 2:
            errors.append(f"tutorial promised page {page_id} needs at least two independent research runs")
        comparison = research_runs.get("comparison")
        if not isinstance(comparison, dict):
            errors.append(f"tutorial promised page {page_id} missing independent comparison record")
        else:
            require_fields(comparison, ["reviewer", "input_run_ids", "output_ref", "verdict"], f"tutorial promised page {page_id} comparison", errors)
            input_run_ids = set(map(str, comparison.get("input_run_ids", []))) if isinstance(comparison.get("input_run_ids"), list) else set()
            if len(input_run_ids) < 2 or not input_run_ids.issubset(run_ids):
                errors.append(f"tutorial promised page {page_id} comparison must reference two completed research runs")

    lab_manifest_path = topic_dir / "lab-manifest.json"
    lab = load_json(lab_manifest_path, errors) if lab_manifest_path.is_file() else None
    if lab is None:
        errors.append(f"tutorial promised page {page_id} missing or invalid lab-manifest.json")
    elif isinstance(lab, dict):
        require_fields(lab, ["topic_id", "page_id", "working_directory", "required_files", "steps", "failure_cycle", "evidence_boundary"], f"tutorial promised page {page_id} lab manifest", errors)
        base = root / str(lab.get("working_directory", ""))
        required_files = lab.get("required_files", [])
        if not isinstance(required_files, list) or not required_files:
            errors.append(f"tutorial promised page {page_id} lab manifest requires repository files")
        else:
            for relative_path in required_files:
                candidate = base / str(relative_path)
                if not candidate.is_file() or candidate.stat().st_size == 0:
                    errors.append(f"tutorial promised page {page_id} lab manifest references missing file: {relative_path}")
        steps = lab.get("steps", [])
        step_ids: set[str] = set()
        if not isinstance(steps, list) or len(steps) < 3:
            errors.append(f"tutorial promised page {page_id} lab manifest needs baseline, fault and repair steps")
        else:
            for index, step in enumerate(steps):
                if not isinstance(step, dict):
                    errors.append(f"tutorial promised page {page_id} lab step {index} must be an object")
                    continue
                require_fields(step, ["step_id", "kind", "command", "expected_exit_code", "expected_artifacts"], f"tutorial promised page {page_id} lab step {index}", errors)
                if step.get("step_id"):
                    step_ids.add(str(step["step_id"]))
        cycle = lab.get("failure_cycle")
        if not isinstance(cycle, dict):
            errors.append(f"tutorial promised page {page_id} lab manifest missing failure cycle")
        else:
            require_fields(cycle, ["baseline_step_id", "fault_step_id", "repair_step_id"], f"tutorial promised page {page_id} failure cycle", errors)
            for step_ref in cycle.values():
                if str(step_ref) not in step_ids:
                    errors.append(f"tutorial promised page {page_id} failure cycle references unknown step: {step_ref}")


def file_sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def resolve_package_ref(root: Path, relative: Any, label: str, errors: list[str]) -> Path | None:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        errors.append(f"{label} must be a non-empty repository-relative path")
        return None
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        errors.append(f"{label} escapes package root")
        return None
    return candidate


def validate_catalog_publication_contract(root: Path, errors: list[str]) -> None:
    """Close canonical catalog, promotion, executability, and publication-artifact gates."""
    required = {
        "catalog manifest": root / "research/catalog-manifest.json",
        "support ownership": root / "research/support-ownership.json",
        "executability audit": root / "research/executability-audit.json",
        "publication closure": root / "research/publication-closure.json",
        "tutorial": root / "tutorial/tutorial-site.json",
    }
    for label, path in required.items():
        if not path.is_file():
            errors.append(f"missing {label}: {path.relative_to(root)}")
    if any(not path.is_file() for path in required.values()):
        return

    catalog = load_json(required["catalog manifest"], errors)
    ownership = load_json(required["support ownership"], errors)
    audit = load_json(required["executability audit"], errors)
    closure = load_json(required["publication closure"], errors)
    tutorial = load_json(required["tutorial"], errors)
    if not all(isinstance(item, dict) for item in (catalog, ownership, audit, closure, tutorial)):
        return

    catalog_ids = catalog.get("page_ids")
    catalog_pages = catalog.get("pages")
    if not isinstance(catalog_ids, list) or not catalog_ids or not all(isinstance(item, str) and item for item in catalog_ids):
        errors.append("canonical catalog page_ids must be a non-empty exact-ID list")
        catalog_ids = []
    if len(set(catalog_ids)) != len(catalog_ids):
        errors.append("canonical catalog page_ids must be unique")
    canonical_set = set(catalog_ids)
    if not isinstance(catalog_pages, list):
        errors.append("canonical catalog pages must be a list")
        catalog_pages = []
    catalog_record_ids = [str(item.get("page_id", "")) for item in catalog_pages if isinstance(item, dict)]
    if catalog_record_ids != catalog_ids:
        errors.append("canonical catalog page records must exactly equal ordered page_ids")

    pages = tutorial.get("pages")
    release_scope = tutorial.get("release_scope")
    if not isinstance(pages, list) or not isinstance(release_scope, dict):
        return
    public_ids = [str(page.get("page_id", "")) for page in pages if isinstance(page, dict)]
    public_set = set(public_ids)
    if public_set - canonical_set:
        errors.append(f"public pages are absent from canonical catalog: {', '.join(sorted(public_set - canonical_set))}")
    if release_scope.get("mode") == "complete-catalog" and public_ids != catalog_ids:
        errors.append("complete-catalog public page set must exactly equal canonical catalog")

    previous_ids = catalog.get("previous_validated_page_ids")
    if not isinstance(previous_ids, list) or not all(isinstance(item, str) and item for item in previous_ids):
        errors.append("canonical catalog previous_validated_page_ids must be an exact-ID list")
        previous_ids = []
    removed_ids = set(previous_ids) - public_set
    if removed_ids:
        scope_change_ref = release_scope.get("scope_change_ref") or catalog.get("scope_change_ref")
        scope_change_path = resolve_package_ref(root, scope_change_ref, "scope-change record", errors) if scope_change_ref else None
        if scope_change_path is None or not scope_change_path.is_file():
            errors.append("release scope shrank without an approved scope-change record")
        else:
            change = load_json(scope_change_path, errors)
            if isinstance(change, dict):
                require_fields(change, [
                    "change_id", "previous_page_ids", "current_page_ids", "removed_page_ids",
                    "rationale", "approved_by", "approved_at", "verdict",
                ], "scope-change record", errors)
                if change.get("previous_page_ids") != previous_ids or change.get("current_page_ids") != public_ids:
                    errors.append("scope-change record does not match previous and current ordered page IDs")
                if set(map(str, change.get("removed_page_ids", []))) != removed_ids:
                    errors.append("scope-change record removed_page_ids does not match the scope shrink")
                if str(change.get("verdict", "")).upper() != "APPROVED":
                    errors.append("scope-change record verdict must be APPROVED")

    bundles = ownership.get("bundles")
    if not isinstance(bundles, list) or not bundles:
        errors.append("support ownership needs at least one bundle")
        bundles = []
    bundle_by_id: dict[str, dict[str, Any]] = {}
    for index, bundle in enumerate(bundles):
        label = f"support bundle {index}"
        if not isinstance(bundle, dict):
            errors.append(f"{label} is not an object")
            continue
        require_fields(bundle, ["bundle_id", "owner_page_ids", "shared", "applicability", "material_refs"], label, errors)
        bundle_id = str(bundle.get("bundle_id", ""))
        if not bundle_id or bundle_id in bundle_by_id:
            errors.append(f"{label} bundle_id must be present and unique")
            continue
        bundle_by_id[bundle_id] = bundle
        owners = bundle.get("owner_page_ids")
        if not isinstance(owners, list) or not owners:
            errors.append(f"{label} owner_page_ids must be a non-empty exact-ID list")
            owners = []
        for owner in owners:
            if not isinstance(owner, str) or owner not in canonical_set:
                errors.append(f"support owner must be an exact canonical page ID: {owner}")
        if len(set(map(str, owners))) != len(owners):
            errors.append(f"{label} owner_page_ids must be unique")
        if bundle.get("shared") is False and len(owners) != 1:
            errors.append(f"{label} non-shared bundle must have exactly one owner")
        if bundle.get("shared") is True and len(owners) > 1 and len(str(bundle.get("applicability", "")).strip()) < 30:
            errors.append(f"{label} shared bundle needs a substantive applicability rationale")
        refs = bundle.get("material_refs")
        if not isinstance(refs, list) or not refs or len(set(map(str, refs))) != len(refs):
            errors.append(f"{label} material_refs must be a non-empty unique list")

    page_record_by_id = {str(item.get("page_id", "")): item for item in catalog_pages if isinstance(item, dict)}
    tutorial_by_id = {str(item.get("page_id", "")): item for item in pages if isinstance(item, dict)}
    for page_id in catalog_ids:
        record = page_record_by_id.get(page_id, {})
        bundle_id = str(record.get("support_bundle_id", ""))
        bundle = bundle_by_id.get(bundle_id)
        if bundle is None:
            errors.append(f"canonical page {page_id} references unknown support bundle: {bundle_id}")
            continue
        owners = set(map(str, bundle.get("owner_page_ids", []))) if isinstance(bundle.get("owner_page_ids"), list) else set()
        if page_id not in owners:
            errors.append(f"canonical page {page_id} is not an exact owner of support bundle {bundle_id}")
        public_page = tutorial_by_id.get(page_id)
        if public_page is not None:
            hrefs = [str(item.get("href", "")) for item in public_page.get("materials", []) if isinstance(item, dict)]
            refs = list(map(str, bundle.get("material_refs", []))) if isinstance(bundle.get("material_refs"), list) else []
            if hrefs != refs:
                errors.append(f"public page {page_id} materials do not exactly match its owned support bundle")

    audit_pages = audit.get("pages")
    require_fields(audit, ["schema_version", "audit_id", "audited_at", "pages"], "executability audit", errors)
    if not is_iso_timestamp(str(audit.get("audited_at", ""))):
        errors.append("executability audit audited_at must be an ISO timestamp")
    if not isinstance(audit_pages, list):
        errors.append("executability audit pages must be a list")
        audit_pages = []
    audit_by_id: dict[str, dict[str, Any]] = {}
    for item in audit_pages:
        if not isinstance(item, dict):
            continue
        page_id = str(item.get("page_id", ""))
        if not page_id or page_id in audit_by_id:
            errors.append("executability audit page IDs must be present and unique")
        audit_by_id[page_id] = item
    for page_id in public_ids:
        item = audit_by_id.get(page_id)
        if item is None or str(item.get("verdict", "")).upper() != "PASS" or item.get("finding_count") != 0:
            errors.append(f"page {page_id} executability audit must PASS with zero findings")

        receipt_path = root / "research/topics" / page_id / "promotion-receipt.json"
        if not receipt_path.is_file():
            errors.append(f"tutorial promised page {page_id} missing promotion-receipt.json")
            continue
        receipt = load_json(receipt_path, errors)
        if not isinstance(receipt, dict):
            continue
        require_fields(receipt, [
            "schema_version", "page_id", "verdict", "research_package_files", "editorial_score",
            "boundary_preservation_score", "executability_audit_ref", "executability_audit_hash",
            "material_hashes", "validated_at", "reviewer",
        ], f"tutorial promised page {page_id} promotion receipt", errors)
        if str(receipt.get("page_id", "")) != page_id or str(receipt.get("verdict", "")).upper() != "PASS":
            errors.append(f"tutorial promised page {page_id} promotion receipt must belong to the page and PASS")
        inventory = set(map(str, receipt.get("research_package_files", []))) if isinstance(receipt.get("research_package_files"), list) else set()
        if inventory != PROMOTION_RESEARCH_PACKAGE_FILES:
            errors.append(f"tutorial promised page {page_id} promotion receipt must inventory the exact ten-file research package")
        if not isinstance(receipt.get("editorial_score"), (int, float)) or receipt.get("editorial_score", 0) < 90:
            errors.append(f"tutorial promised page {page_id} promotion receipt editorial_score must be at least 90")
        if receipt.get("boundary_preservation_score") != 100:
            errors.append(f"tutorial promised page {page_id} promotion receipt boundary_preservation_score must be 100")
        if receipt.get("executability_audit_ref") != "research/executability-audit.json" or receipt.get("executability_audit_hash") != file_sha256(required["executability audit"]):
            errors.append(f"tutorial promised page {page_id} promotion receipt does not pin the current executability audit")
        material_hashes = receipt.get("material_hashes")
        page = tutorial_by_id.get(page_id, {})
        page_hrefs = [str(item.get("href", "")) for item in page.get("materials", []) if isinstance(item, dict)]
        if not isinstance(material_hashes, dict) or set(material_hashes) != set(page_hrefs):
            errors.append(f"tutorial promised page {page_id} promotion receipt material hashes must exactly cover page materials")
        else:
            for href, expected_hash in material_hashes.items():
                material_path = root / "site/public" / href
                if not material_path.is_file() or expected_hash != file_sha256(material_path):
                    errors.append(f"tutorial promised page {page_id} promotion receipt material hash mismatch: {href}")

    require_fields(closure, [
        "schema_version", "canonical_source_ref", "canonical_source_hash", "tutorial_ref", "tutorial_hash",
        "static_export_root", "archive_ref", "material_entries",
    ], "publication closure", errors)
    if closure.get("canonical_source_ref") != "research/catalog-manifest.json" or closure.get("canonical_source_hash") != file_sha256(required["catalog manifest"]):
        errors.append("publication closure does not pin the current canonical catalog")
    if closure.get("tutorial_ref") != "tutorial/tutorial-site.json" or closure.get("tutorial_hash") != file_sha256(required["tutorial"]):
        errors.append("publication closure does not pin the current tutorial source")
    archive_path = resolve_package_ref(root, closure.get("archive_ref"), "publication closure archive_ref", errors)
    static_root = str(closure.get("static_export_root", "")).rstrip("/")
    entries = closure.get("material_entries")
    if not isinstance(entries, list):
        errors.append("publication closure material_entries must be a list")
        entries = []
    expected_pairs = {
        (page_id, str(material.get("href", "")))
        for page_id, page in tutorial_by_id.items()
        for material in page.get("materials", []) if isinstance(material, dict)
    }
    actual_pairs = {
        (str(entry.get("page_id", "")), str(entry.get("href", "")))
        for entry in entries if isinstance(entry, dict)
    }
    if actual_pairs != expected_pairs or len(entries) != len(expected_pairs):
        errors.append("publication closure material entries must exactly cover every page-material link")
    archive_members: dict[str, bytes] = {}
    if archive_path is None or not archive_path.is_file():
        errors.append("publication closure archive is missing")
    else:
        try:
            with zipfile.ZipFile(archive_path) as archive:
                infos = [info for info in archive.infolist() if not info.is_dir()]
                if any(Path(info.filename).is_absolute() or ".." in Path(info.filename).parts for info in infos):
                    errors.append("publication closure archive contains an unsafe path")
                archive_members = {info.filename: archive.read(info) for info in infos}
        except zipfile.BadZipFile as exc:
            errors.append(f"publication closure archive is invalid: {exc}")
    declared_archive_members: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"publication closure material entry {index} is not an object")
            continue
        require_fields(entry, ["page_id", "href", "source_ref", "dist_ref", "archive_member", "sha256"], f"publication closure material entry {index}", errors)
        href = str(entry.get("href", ""))
        expected_hash = str(entry.get("sha256", ""))
        if entry.get("source_ref") != f"site/public/{href}":
            errors.append(f"publication closure source_ref does not match tutorial href: {href}")
        if entry.get("dist_ref") != f"{static_root}/{href}":
            errors.append(f"publication closure dist_ref does not match static export root: {href}")
        source_path = resolve_package_ref(root, entry.get("source_ref"), f"publication closure source_ref {index}", errors)
        dist_path = resolve_package_ref(root, entry.get("dist_ref"), f"publication closure dist_ref {index}", errors)
        if source_path is None or not source_path.is_file() or file_sha256(source_path) != expected_hash:
            errors.append(f"publication closure hash mismatch for source_ref: {entry.get('source_ref')}")
        if dist_path is None or not dist_path.is_file() or file_sha256(dist_path) != expected_hash:
            errors.append(f"publication closure hash mismatch for dist_ref: {entry.get('dist_ref')}")
        member = str(entry.get("archive_member", ""))
        declared_archive_members.add(member)
        member_bytes = archive_members.get(member)
        member_hash = f"sha256:{hashlib.sha256(member_bytes).hexdigest()}" if member_bytes is not None else ""
        if member_hash != expected_hash:
            errors.append(f"publication closure hash mismatch for archive member: {member}")
    if archive_members and set(archive_members) != declared_archive_members:
        errors.append("publication closure archive members must exactly equal declared material members")


def is_placeholder(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value.strip().lower()
    return any(token in normalized for token in PLACEHOLDER_TOKENS)


def is_http_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def is_iso_timestamp(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except (AttributeError, ValueError):
        return False


def section_body(markdown: str, marker: str) -> str:
    """Return a level-two section body without accepting content from the next section."""
    start = markdown.find(marker)
    if start < 0:
        return ""
    body_start = start + len(marker)
    next_section = markdown.find("\n## ", body_start)
    return markdown[body_start:next_section if next_section >= 0 else len(markdown)].strip()


def fetch_url_status(url: str, timeout: float = 12.0) -> tuple[int | None, int, str]:
    """Live URL check. This is deliberately separate from static provenance validation."""
    request = Request(url, headers={"User-Agent": "career-ai-course-factory-validator/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            sample = response.read(4096)
            return getattr(response, "status", 200), len(sample), ""
    except HTTPError as exc:
        return exc.code, 0, str(exc)
    except (URLError, TimeoutError, ValueError) as exc:
        return None, 0, str(exc)


def validate_research(root: Path, errors: list[str]) -> None:
    research = root / "research"
    for name in REQUIRED_RESEARCH:
        if not (research / name).is_file():
            errors.append(f"missing research file: research/{name}")

    ledger = research / "source-ledger.csv"
    ledger_ids: set[str] = set()
    ledger_by_id: dict[str, dict[str, str]] = {}
    publisher_by_id: dict[str, str] = {}
    family_by_id: dict[str, str] = {}
    source_channels: set[str] = set()
    if ledger.is_file():
        rows, fields = load_csv(ledger, errors)
        ledger_ids = {row.get("id", "").strip() for row in rows if row.get("id")}
        ledger_by_id = {row.get("id", "").strip(): row for row in rows if row.get("id")}
        for field in REQUIRED_LEDGER_COLUMNS:
            if field not in fields:
                errors.append(f"source ledger missing column: {field}")
        if len(rows) < 20:
            errors.append(f"source ledger needs at least 20 sources, found {len(rows)}")
        platforms = {row.get("platform", "").strip().lower() for row in rows if row.get("platform")}
        if len(platforms) < 5:
            errors.append(f"source ledger needs at least 5 platforms, found {len(platforms)}")
        primary_count = sum(
            any(token in row.get("source_type", "").lower() for token in ("official", "primary", "standard", "repository"))
            for row in rows
        )
        if primary_count < 4:
            errors.append(f"source ledger needs at least 4 primary capability sources, found {primary_count}")
        publishers = {row.get("publisher_group", "").strip() for row in rows if row.get("publisher_group")}
        if len(publishers) < 6:
            errors.append(f"source ledger needs at least 6 independent publisher groups, found {len(publishers)}")
        families = {row.get("source_family_id", "").strip() for row in rows if row.get("source_family_id")}
        if len(families) < 10:
            errors.append(f"source ledger needs at least 10 source families, found {len(families)}")
        for label, field in [("publisher group", "publisher_group"), ("source family", "source_family_id")]:
            counts = Counter(row.get(field, "").strip() for row in rows if row.get(field, "").strip())
            if counts:
                name, count = counts.most_common(1)[0]
                if count / len(rows) > 0.25:
                    errors.append(f"source ledger is over-concentrated: {label} {name} supplies {count}/{len(rows)} sources")
        languages = {row.get("language", "").strip().lower() for row in rows}
        if not ({"zh", "中文"} & languages and {"en", "英文"} & languages):
            errors.append("source ledger must include both Chinese and English sources")
        for index, row in enumerate(rows):
            source_id = row.get("id", "").strip()
            if row.get("source_type", "").strip().lower() not in ALLOWED_SOURCE_TYPES:
                errors.append(f"source ledger row {index} has unsupported source_type: {row.get('source_type')}")
            if not is_http_url(row.get("url", "")):
                errors.append(f"source ledger row {index} has invalid URL")
            for field in ["publisher_group", "source_family_id", "channel_ids"]:
                if not row.get(field, "").strip():
                    errors.append(f"source ledger row {index} missing value: {field}")
            if source_id:
                publisher_by_id[source_id] = row.get("publisher_group", "").strip()
                family_by_id[source_id] = row.get("source_family_id", "").strip()
            channels = {item.strip() for item in row.get("channel_ids", "").split(";") if item.strip()}
            unknown_channels = channels - REQUIRED_CHANNELS
            if unknown_channels:
                errors.append(f"source ledger row {index} has unknown channel IDs: {', '.join(sorted(unknown_channels))}")
            source_channels.update(channels)
        urls = [row.get("url", "").strip() for row in rows if row.get("url")]
        duplicate_urls = sorted({url for url in urls if urls.count(url) > 1})
        if duplicate_urls:
            errors.append(f"source ledger contains duplicate canonical URLs: {', '.join(duplicate_urls[:3])}")
        missing_channels = REQUIRED_CHANNELS - source_channels
        if missing_channels:
            errors.append(f"source ledger misses mandatory channels: {', '.join(sorted(missing_channels))}")

    competitors = research / "competitor-matrix.csv"
    if competitors.is_file():
        rows, fields = load_csv(competitors, errors)
        for field in REQUIRED_COMPETITOR_COLUMNS:
            if field not in fields:
                errors.append(f"competitor matrix missing column: {field}")
        if len(rows) < 6:
            errors.append(f"competitor matrix needs at least 6 offerings, found {len(rows)}")
        platforms = {row.get("platform", "").strip().lower() for row in rows if row.get("platform")}
        if len(platforms) < 3:
            errors.append(f"competitor matrix needs at least 3 platforms, found {len(platforms)}")
        bad_status = sorted({row.get("claim_status", "") for row in rows} - {"observed", "vendor-claim", "inferred", "unknown"})
        if bad_status:
            errors.append(f"competitor matrix has invalid claim_status: {', '.join(bad_status)}")

    evidence = research / "evidence-matrix.md"
    if evidence.is_file():
        text = evidence.read_text(encoding="utf-8")
        for marker in ["## Evidence", "## Competitor observations", "## Vendor claims", "## Inference", "## Unknown"]:
            if marker not in text:
                errors.append(f"evidence matrix missing marker: {marker}")
    capability = research / "ai-capability-map.md"
    if capability.is_file():
        text = capability.read_text(encoding="utf-8")
        for lane in AI_LANES:
            if lane not in text:
                errors.append(f"AI capability map missing lane: {lane}")

    search_plan_path = research / "search-plan.json"
    surface_by_id: dict[str, dict[str, Any]] = {}
    if search_plan_path.is_file():
        plan = load_json(search_plan_path, errors)
        if isinstance(plan, dict):
            require_fields(plan, [
                "profession", "generated_at", "research_question", "available_surfaces",
                "freshness_required", "run_scope", "query_families", "freshness_policy",
                "stop_conditions", "run_status",
            ], "search plan", errors)
            surfaces = plan.get("available_surfaces", [])
            if not isinstance(surfaces, list) or not surfaces:
                errors.append("search plan must record at least one available retrieval surface")
            else:
                for index, item in enumerate(surfaces):
                    if not isinstance(item, dict):
                        errors.append(f"search surface {index} is not an object")
                        continue
                    require_fields(item, ["surface_id", "surface", "is_live", "status", "attempted_at", "evidence", "limits"], f"search surface {index}", errors)
                    surface_id = item.get("surface_id")
                    if surface_id in surface_by_id:
                        errors.append(f"duplicate search surface_id: {surface_id}")
                    elif surface_id:
                        surface_by_id[surface_id] = item
                    if item.get("status") not in {"available", "unavailable", "blocked"}:
                        errors.append(f"search surface {index} has invalid status: {item.get('status')}")
                    if not isinstance(item.get("is_live"), bool):
                        errors.append(f"search surface {index} is_live must be boolean")
            families = plan.get("query_families", [])
            if not isinstance(families, list) or len(families) < 5:
                errors.append("search plan needs at least 5 query families")
            if plan.get("run_scope") != "full":
                errors.append(f"complete package validation requires run_scope full, found {plan.get('run_scope')}")
            if plan.get("freshness_required") is not True:
                errors.append("complete profession-by-AI research must set freshness_required=true")
            if plan.get("run_status") == "blocked":
                errors.append("BLOCKED-FRESHNESS: search plan is blocked and cannot unlock course ranking")
            elif plan.get("run_status") != "complete":
                errors.append(f"search plan run_status must be complete, found {plan.get('run_status')}")
            if plan.get("freshness_required") is True:
                live_success = any(
                    item.get("is_live") is True and item.get("status") == "available"
                    and item.get("attempted_at") and item.get("evidence")
                    for item in surface_by_id.values()
                )
                if not live_success:
                    errors.append("BLOCKED-FRESHNESS: current claims require a successful evidenced live retrieval surface")

    search_log_path = research / "search-log.csv"
    selected_source_ids: set[str] = set()
    search_log_ids: set[str] = set()
    search_row_by_id: dict[str, dict[str, str]] = {}
    selected_by_query: dict[str, set[str]] = {}
    if search_log_path.is_file():
        rows, fields = load_csv(search_log_path, errors)
        search_log_ids = {row.get("id", "").strip() for row in rows if row.get("id")}
        search_row_by_id = {row.get("id", "").strip(): row for row in rows if row.get("id")}
        for field in REQUIRED_SEARCH_LOG_COLUMNS:
            if field not in fields:
                errors.append(f"search log missing column: {field}")
        if len(rows) < 8:
            errors.append(f"search log needs at least 8 exact queries, found {len(rows)}")
        lanes = {row.get("research_lane", "").strip() for row in rows if row.get("research_lane")}
        if len(lanes) < 5:
            errors.append(f"search log needs at least 5 query families, found {len(lanes)}")
        surface_attempts = {row.get("surface_attempt_id", "").strip() for row in rows if row.get("surface_attempt_id")}
        if len(surface_attempts) < 3:
            errors.append(f"search log needs at least 3 evidenced retrieval surface attempts, found {len(surface_attempts)}")
        languages = {row.get("language", "").strip().lower() for row in rows}
        if not ("zh" in languages and "en" in languages):
            errors.append("search log must include Chinese and English queries")
        bad_status = sorted({row.get("status", "") for row in rows} - SEARCH_STATUSES)
        if bad_status:
            errors.append(f"search log has invalid status: {', '.join(bad_status)}")
        for index, row in enumerate(rows):
            for field in ["id", "query", "language", "research_lane", "surface_attempt_id", "search_surface", "run_at", "result_count", "exclusion_notes", "status"]:
                if not row.get(field, "").strip():
                    errors.append(f"search log row {index} missing value: {field}")
            if len(row.get("query", "").strip()) < 8:
                errors.append(f"search log row {index} query is too weak")
            if not is_iso_timestamp(row.get("run_at", "")):
                errors.append(f"search log row {index} has invalid run_at timestamp")
            try:
                if int(row.get("result_count", "")) < 0:
                    raise ValueError
            except ValueError:
                errors.append(f"search log row {index} result_count must be a non-negative integer")
            surface_id = row.get("surface_attempt_id", "").strip()
            if surface_id not in surface_by_id:
                errors.append(f"search log row {index} references unknown surface_attempt_id: {surface_id}")
            elif row.get("search_surface", "").strip() != str(surface_by_id[surface_id].get("surface", "")).strip():
                errors.append(f"search log row {index} search_surface does not match declared surface attempt")
            if row.get("status") == "selected":
                opened_urls = {item.strip() for item in row.get("opened_urls", "").split(";") if item.strip()}
                if not opened_urls:
                    errors.append(f"search log row {index} selected a source without an opened URL")
                for opened_url in opened_urls:
                    if not is_http_url(opened_url):
                        errors.append(f"search log row {index} has invalid opened URL: {opened_url}")
                selected = {item.strip() for item in row.get("selected_source_ids", "").split(";") if item.strip()}
                selected_by_query[row.get("id", "").strip()] = selected
                selected_source_ids.update(selected)
                unknown = selected - ledger_ids
                if not selected:
                    errors.append(f"search log row {index} selected a source without a source-ledger ID")
                if unknown:
                    errors.append(f"search log row {index} references unknown source IDs: {', '.join(sorted(unknown))}")
                for source_id in selected & ledger_ids:
                    ledger_url = ledger_by_id[source_id].get("url", "").strip()
                    if ledger_url not in opened_urls:
                        errors.append(f"search log row {index} source {source_id} ledger URL is not among opened URLs")

    coverage_path = research / "channel-coverage.json"
    if coverage_path.is_file():
        coverage = load_json(coverage_path, errors)
        require_fields(coverage, ["profession", "generated_at", "channels"], "channel coverage", errors) if isinstance(coverage, dict) else None
        channel_records = coverage.get("channels") if isinstance(coverage, dict) else None
        if not isinstance(channel_records, list):
            errors.append("channel coverage must contain a channels list")
        else:
            covered: set[str] = set()
            for index, record in enumerate(channel_records):
                if not isinstance(record, dict):
                    errors.append(f"channel coverage row {index} is not an object")
                    continue
                require_fields(record, ["channel_id", "purpose", "source_ids", "query_ids", "claim_boundary", "status", "limitations"], f"channel coverage row {index}", errors)
                channel_id = record.get("channel_id")
                if channel_id in covered:
                    errors.append(f"duplicate channel coverage record: {channel_id}")
                elif channel_id:
                    covered.add(channel_id)
                if record.get("status") != "complete":
                    errors.append(f"channel {channel_id} is not complete")
                source_ids = set(record.get("source_ids", [])) if isinstance(record.get("source_ids"), list) else set()
                query_ids = set(record.get("query_ids", [])) if isinstance(record.get("query_ids"), list) else set()
                if not source_ids or not query_ids:
                    errors.append(f"channel {channel_id} must bind opened sources and executed queries")
                unknown_sources = source_ids - selected_source_ids
                if unknown_sources:
                    errors.append(f"channel {channel_id} uses unselected or unopened sources: {', '.join(sorted(unknown_sources))}")
                unknown_queries = query_ids - search_log_ids
                if unknown_queries:
                    errors.append(f"channel {channel_id} references unknown query IDs: {', '.join(sorted(unknown_queries))}")
                non_selected_queries = {
                    query_id for query_id in query_ids & search_log_ids
                    if search_row_by_id.get(query_id, {}).get("status") != "selected"
                }
                if non_selected_queries:
                    errors.append(f"channel {channel_id} relies on queries that did not select evidence: {', '.join(sorted(non_selected_queries))}")
                sources_selected_by_bound_queries = set().union(
                    *(selected_by_query.get(query_id, set()) for query_id in query_ids)
                ) if query_ids else set()
                unbound_sources = source_ids - sources_selected_by_bound_queries
                if unbound_sources:
                    errors.append(f"channel {channel_id} sources are not selected by its bound queries: {', '.join(sorted(unbound_sources))}")
                mismatched = {source_id for source_id in source_ids if channel_id not in set(ledger_by_id.get(source_id, {}).get("channel_ids", "").split(";"))}
                if mismatched:
                    errors.append(f"channel {channel_id} includes sources not tagged for that channel: {', '.join(sorted(mismatched))}")
            missing = REQUIRED_CHANNELS - covered
            if missing:
                errors.append(f"channel coverage misses mandatory channels: {', '.join(sorted(missing))}")

    github_path = research / "github-artifacts.csv"
    if github_path.is_file():
        rows, fields = load_csv(github_path, errors)
        for field in REQUIRED_GITHUB_COLUMNS:
            if field not in fields:
                errors.append(f"github artifacts missing column: {field}")
        if len(rows) < 2:
            errors.append(f"github artifacts need at least 2 candidates, found {len(rows)}")
        owners = set()
        for index, row in enumerate(rows):
            for field in REQUIRED_GITHUB_COLUMNS:
                if not row.get(field, "").strip():
                    errors.append(f"github artifact row {index} missing value: {field}")
            source_id = row.get("source_id", "").strip()
            if source_id not in ledger_ids:
                errors.append(f"github artifact row {index} references unknown source: {source_id}")
            elif "repository" not in ledger_by_id[source_id].get("source_type", "").lower():
                errors.append(f"github artifact row {index} source is not a primary repository")
            repo_url = row.get("repo_url", "").strip()
            if not is_http_url(repo_url) or "github.com" not in urlparse(repo_url).netloc:
                errors.append(f"github artifact row {index} has invalid GitHub URL")
            parts = [part for part in urlparse(repo_url).path.split("/") if part]
            if parts:
                owners.add(parts[0].lower())
            if row.get("run_status") not in {"metadata-only", "clone-failed", "run-failed", "run-verified"}:
                errors.append(f"github artifact row {index} has invalid run_status")
            selected = row.get("selected_for_lab", "").strip().lower() == "true"
            if selected:
                if row.get("run_status") != "run-verified":
                    errors.append(f"github artifact row {index} selected for lab is not run-verified")
                try:
                    if int(row.get("exit_code", "")) != 0:
                        errors.append(f"github artifact row {index} selected for lab did not exit 0")
                except ValueError:
                    errors.append(f"github artifact row {index} selected for lab has invalid exit_code")
                evidence_path = root / row.get("evidence_path", "")
                expected_root = (root / "research/github-runs").resolve()
                try:
                    evidence_path.resolve().relative_to(expected_root)
                except ValueError:
                    errors.append(f"github artifact row {index} run evidence must live under research/github-runs")
                if not evidence_path.is_file():
                    errors.append(f"github artifact row {index} selected for lab lacks saved run evidence")
                else:
                    run_evidence = load_json(evidence_path, errors)
                    if not isinstance(run_evidence, dict):
                        errors.append(f"github artifact row {index} run evidence must be structured JSON")
                    else:
                        require_fields(run_evidence, [
                            "artifact_id", "repo_url", "commit_or_tag", "run_at", "checkout_head",
                            "setup_command", "smoke_command", "exit_code", "stdout", "stderr",
                            "environment", "limitations",
                        ], f"github artifact row {index} run evidence", errors)
                        exact_matches = {
                            "artifact_id": row.get("artifact_id"),
                            "repo_url": repo_url,
                            "commit_or_tag": row.get("commit_or_tag"),
                            "checkout_head": row.get("commit_or_tag"),
                            "setup_command": row.get("setup_command"),
                            "smoke_command": row.get("smoke_command"),
                        }
                        for field, expected in exact_matches.items():
                            if run_evidence.get(field) != expected:
                                errors.append(f"github artifact row {index} run evidence {field} does not match audited artifact")
                        if run_evidence.get("exit_code") != 0:
                            errors.append(f"github artifact row {index} run evidence exit_code must be 0")
                        if not is_iso_timestamp(str(run_evidence.get("run_at", ""))):
                            errors.append(f"github artifact row {index} run evidence has invalid run_at")
        if len(owners) < 2:
            errors.append(f"github artifacts need candidates from at least 2 owners, found {len(owners)}")

    jobs_path = research / "job-signals.csv"
    if jobs_path.is_file():
        rows, fields = load_csv(jobs_path, errors)
        for field in REQUIRED_JOB_COLUMNS:
            if field not in fields:
                errors.append(f"job signals missing column: {field}")
        if len(rows) < 5:
            errors.append(f"job signals need at least 5 original postings, found {len(rows)}")
        employers = {row.get("employer", "").strip().lower() for row in rows if row.get("employer")}
        if len(employers) < 3:
            errors.append(f"job signals need at least 3 employers, found {len(employers)}")
        duplicate_groups = [row.get("duplicate_group", "").strip() for row in rows if row.get("duplicate_group")]
        if len(set(duplicate_groups)) != len(duplicate_groups):
            errors.append("job signals contain syndicated duplicate groups")
        for index, row in enumerate(rows):
            for field in REQUIRED_JOB_COLUMNS:
                if not row.get(field, "").strip():
                    errors.append(f"job signal row {index} missing value: {field}")
            if row.get("source_id", "") not in ledger_ids:
                errors.append(f"job signal row {index} references unknown source")
            if not is_http_url(row.get("original_url", "")):
                errors.append(f"job signal row {index} has invalid original URL")
            if row.get("claim_status") not in {"observed", "employer-claim", "unknown"}:
                errors.append(f"job signal row {index} has invalid claim_status")

    learner_path = research / "learner-signals.csv"
    if learner_path.is_file():
        rows, fields = load_csv(learner_path, errors)
        for field in REQUIRED_LEARNER_SIGNAL_COLUMNS:
            if field not in fields:
                errors.append(f"learner signals missing column: {field}")
        if len(rows) < 4:
            errors.append(f"learner signals need at least 4 observations, found {len(rows)}")
        platforms = {row.get("platform", "").strip().lower() for row in rows if row.get("platform")}
        if len(platforms) < 3:
            errors.append(f"learner signals need at least 3 platforms, found {len(platforms)}")
        for index, row in enumerate(rows):
            for field in REQUIRED_LEARNER_SIGNAL_COLUMNS:
                if not row.get(field, "").strip():
                    errors.append(f"learner signal row {index} missing value: {field}")
            if row.get("source_id", "") not in ledger_ids:
                errors.append(f"learner signal row {index} references unknown source")
            if row.get("claim_status") not in {"observed", "vendor-claim", "inferred", "unknown"}:
                errors.append(f"learner signal row {index} has invalid claim_status")

    profession_reality_path = research / "profession-reality-map.json"
    if profession_reality_path.is_file():
        reality = load_json(profession_reality_path, errors)
        if isinstance(reality, dict):
            require_fields(reality, [
                "profession_id", "as_of", "review_status", "role_variants", "work_rhythms",
                "workflow_stages", "dependencies", "artifacts", "performance_and_promotion",
                "pain_points", "information_barriers", "ai_opportunities", "beginner_reuse_pack",
                "source_ids",
            ], "profession reality map", errors)
            minimums = {
                "role_variants": 3, "work_rhythms": 3, "workflow_stages": 6,
                "dependencies": 5, "artifacts": 6, "pain_points": 5,
                "information_barriers": 3, "ai_opportunities": 5,
            }
            for field, minimum in minimums.items():
                values = reality.get(field)
                if not isinstance(values, list) or len(values) < minimum:
                    errors.append(f"profession reality map needs at least {minimum} {field}")
            if reality.get("review_status") not in {"desk-researched", "practitioner-reviewed"}:
                errors.append("profession reality map has invalid review_status")
            source_ids = set(reality.get("source_ids", [])) if isinstance(reality.get("source_ids"), list) else set()
            if len(source_ids) < 3 or source_ids - ledger_ids:
                errors.append("profession reality map needs at least 3 known source IDs")
            opportunities = reality.get("ai_opportunities", [])
            for index, opportunity in enumerate(opportunities if isinstance(opportunities, list) else []):
                if not isinstance(opportunity, dict):
                    errors.append(f"profession AI opportunity {index} is not an object")
                    continue
                require_fields(opportunity, [
                    "opportunity_id", "work_stage_id", "change_class", "baseline_pain",
                    "ai_role", "inspectable_output", "human_gate", "ai_failures",
                    "baseline_metric", "success_measure", "starter_material", "evidence_status",
                ], f"profession AI opportunity {index}", errors)
                if opportunity.get("change_class") not in {"retained", "assisted", "automated", "transformed", "new-work", "declining"}:
                    errors.append(f"profession AI opportunity {index} has invalid change_class")

    profession_domain_by_scenario: dict[str, str] = {}
    profession_map_path = research / "profession-map.json"
    if profession_map_path.is_file():
        profession_map = load_json(profession_map_path, errors)
        if isinstance(profession_map, dict):
            require_fields(profession_map, ["profession_id", "canonical_name", "taxonomy", "as_of", "role_variants", "work_domains", "lifecycle"], "profession map", errors)
            if not isinstance(profession_map.get("role_variants"), list) or len(profession_map.get("role_variants", [])) < 2:
                errors.append("profession map needs at least 2 role variants")
            domains = profession_map.get("work_domains")
            if not isinstance(domains, list) or len(domains) < 5:
                errors.append("profession map needs at least 5 work domains")
            else:
                seen_domains: set[str] = set()
                for index, domain in enumerate(domains):
                    if not isinstance(domain, dict):
                        errors.append(f"profession domain {index} is not an object")
                        continue
                    require_fields(domain, ["domain_id", "name", "job_result", "business_events", "artifacts", "systems", "decision_rights", "failure_costs", "ai_lanes", "scenario_ids", "evidence_ids"], f"profession domain {index}", errors)
                    domain_id = domain.get("domain_id")
                    if domain_id in seen_domains:
                        errors.append(f"duplicate profession domain_id: {domain_id}")
                    elif domain_id:
                        seen_domains.add(domain_id)
                    evidence_ids = set(domain.get("evidence_ids", [])) if isinstance(domain.get("evidence_ids"), list) else set()
                    if not evidence_ids or evidence_ids - ledger_ids:
                        errors.append(f"profession domain {index} has missing or unknown evidence IDs")
                    lanes = set(domain.get("ai_lanes", [])) if isinstance(domain.get("ai_lanes"), list) else set()
                    if not lanes or lanes - AI_LANES:
                        errors.append(f"profession domain {index} has missing or invalid AI lanes")
                    for scenario_id in domain.get("scenario_ids", []) if isinstance(domain.get("scenario_ids"), list) else []:
                        if scenario_id in profession_domain_by_scenario:
                            errors.append(f"scenario {scenario_id} has more than one primary profession domain")
                        else:
                            profession_domain_by_scenario[scenario_id] = str(domain_id)

    radar_path = research / "technology-radar.json"
    if radar_path.is_file():
        radar = load_json(radar_path, errors)
        technologies = radar.get("technologies") if isinstance(radar, dict) else None
        if not isinstance(technologies, list) or len(technologies) < 8:
            errors.append("technology radar must contain at least 8 candidates")
        else:
            fields = [
                "technology_id", "name", "category", "capability", "ai_lane", "official_source",
                "version_or_release", "last_verified", "maturity", "status", "setup", "limits",
                "security", "scenario_ids", "course_ids", "fallbacks", "refresh_trigger", "evidence_ids",
            ]
            for index, item in enumerate(technologies):
                if not isinstance(item, dict):
                    errors.append(f"technology {index} is not an object")
                    continue
                require_fields(item, fields, f"technology {index}", errors)
                if item.get("ai_lane") not in AI_LANES:
                    errors.append(f"technology {index} has invalid ai_lane: {item.get('ai_lane')}")
                if item.get("status") not in TECH_STATUSES:
                    errors.append(f"technology {index} has invalid status: {item.get('status')}")
                if item.get("status") == "current" and (not item.get("official_source") or not item.get("last_verified")):
                    errors.append(f"technology {index} current claim lacks official source or verification date")

    scenarios_path = research / "scenarios.json"
    if scenarios_path.is_file():
        data = load_json(scenarios_path, errors)
        scenarios = data.get("scenarios") if isinstance(data, dict) else None
        if not isinstance(scenarios, list) or len(scenarios) < 8:
            errors.append("scenarios.json must contain at least 8 business scenarios")
        else:
            fields = [
                "scenario_id", "title", "ai_lane", "actor", "work_setting", "trigger",
                "business_system", "business_object", "inputs", "current_workflow",
                "pain_and_failure_cost", "constraints", "ai_intervention", "ai_role", "outputs",
                "decision_or_handoff", "ai_specific_failures", "privacy_security", "evidence_ids",
                "evidence_classes", "evidence_map", "semantic_contract", "artifact", "demo_fixture",
                "validation_plan", "scores", "evidence_status",
            ]
            lanes: set[str] = set()
            for index, scenario in enumerate(scenarios):
                if not isinstance(scenario, dict):
                    errors.append(f"scenario {index} is not an object")
                    continue
                require_fields(scenario, fields, f"scenario {index}", errors)
                lane = scenario.get("ai_lane")
                lanes.add(lane)
                if lane not in AI_LANES:
                    errors.append(f"scenario {index} has invalid ai_lane: {lane}")
                classes = set(scenario.get("evidence_classes", [])) if isinstance(scenario.get("evidence_classes"), list) else set()
                if not SCENARIO_EVIDENCE_CLASSES.issubset(classes):
                    errors.append(f"scenario {index} lacks three-class evidence triangulation")
                evidence_ids = set(scenario.get("evidence_ids", [])) if isinstance(scenario.get("evidence_ids"), list) else set()
                if len(evidence_ids) < 3:
                    errors.append(f"scenario {index} needs at least 3 evidence IDs")
                unknown = evidence_ids - ledger_ids
                if unknown:
                    errors.append(f"scenario {index} references unknown source IDs: {', '.join(sorted(unknown))}")
                publishers = {publisher_by_id.get(source_id, "") for source_id in evidence_ids if publisher_by_id.get(source_id)}
                families = {family_by_id.get(source_id, "") for source_id in evidence_ids if family_by_id.get(source_id)}
                if len(publishers) < 3:
                    errors.append(f"scenario {index} needs at least 3 independent publisher groups")
                if len(families) < 3:
                    errors.append(f"scenario {index} needs at least 3 independent source families")
                scenario_id = scenario.get("scenario_id")
                if scenario_id not in profession_domain_by_scenario:
                    errors.append(f"scenario {index} is not mapped to a primary profession domain")
                evidence_map = scenario.get("evidence_map", {})
                if not isinstance(evidence_map, dict):
                    errors.append(f"scenario {index} evidence_map must be an object")
                else:
                    for evidence_class in SCENARIO_EVIDENCE_CLASSES:
                        mapped = evidence_map.get(evidence_class, [])
                        mapped_ids = set(mapped) if isinstance(mapped, list) else set()
                        if not mapped_ids:
                            errors.append(f"scenario {index} evidence_map missing class: {evidence_class}")
                            continue
                        if not mapped_ids.issubset(evidence_ids):
                            errors.append(f"scenario {index} evidence_map {evidence_class} is not included in evidence_ids")
                        unopened = mapped_ids - selected_source_ids
                        if unopened:
                            errors.append(f"scenario {index} {evidence_class} uses sources without opened selected search evidence: {', '.join(sorted(unopened))}")
                        for source_id in mapped_ids & ledger_ids:
                            source_type = ledger_by_id[source_id].get("source_type", "").lower()
                            if not any(token in source_type for token in EVIDENCE_TYPE_TOKENS[evidence_class]):
                                errors.append(f"scenario {index} source {source_id} type does not support {evidence_class}")
                semantic = scenario.get("semantic_contract", {})
                if not isinstance(semantic, dict):
                    errors.append(f"scenario {index} semantic_contract must be an object")
                else:
                    require_fields(semantic, SEMANTIC_FIELDS, f"scenario {index} semantic_contract", errors)
                    for field in SEMANTIC_FIELDS:
                        if is_placeholder(semantic.get(field)):
                            errors.append(f"scenario {index} semantic_contract contains placeholder: {field}")
                        if field != "human_approval_required":
                            value = semantic.get(field)
                            if not isinstance(value, str):
                                errors.append(f"scenario {index} semantic_contract field must be string: {field}")
                            elif value.strip().lower() in GENERIC_SEMANTIC_VALUES or len(value.strip()) < 4:
                                errors.append(f"scenario {index} semantic_contract field is too generic: {field}")
                    if semantic.get("measurement_status") not in {"unmeasured", "estimated", "measured"}:
                        errors.append(f"scenario {index} has invalid measurement_status")
                    if not isinstance(semantic.get("human_approval_required"), bool):
                        errors.append(f"scenario {index} human_approval_required must be boolean")
                    if scenario.get("evidence_status") == "production-validated" and semantic.get("measurement_status") != "measured":
                        errors.append(f"scenario {index} production validation requires measured failure evidence")
                if scenario.get("evidence_status") not in SCENARIO_STATUSES:
                    errors.append(f"scenario {index} has invalid evidence_status: {scenario.get('evidence_status')}")
                scores = scenario.get("scores", {})
                for field, minimum in {"ai_centrality": 4, "business_specificity": 4, "artifact_accessibility": 3, "testability": 3}.items():
                    if not isinstance(scores.get(field), int) or scores.get(field, 0) < minimum:
                        errors.append(f"scenario {index} fails {field} gate")
                validation_plan = scenario.get("validation_plan", [])
                if not isinstance(validation_plan, list) or len(validation_plan) < 3:
                    errors.append(f"scenario {index} needs baseline, failure, and repair validation steps")
            missing = AI_LANES - lanes
            if missing:
                errors.append(f"business scenarios miss AI lanes: {', '.join(sorted(missing))}")


def validate_curriculum_gap_audit(root: Path, errors: list[str]) -> None:
    analysis_path = root / "curriculum-gap-analysis.md"
    if analysis_path.is_file():
        analysis = analysis_path.read_text(encoding="utf-8")
        if len(analysis.strip()) < 3000:
            errors.append("curriculum-gap-analysis.md is too thin for a six-system professional audit")
        for marker in GAP_ANALYSIS_MARKERS:
            if marker not in analysis:
                errors.append(f"curriculum gap analysis missing marker: {marker}")
        for marker in EXPERT_REVIEW_MARKERS:
            if marker not in analysis:
                errors.append(f"curriculum gap analysis missing independent review: {marker}")

    ledger_path = root / "research/source-ledger.csv"
    competitor_path = root / "research/competitor-matrix.csv"
    matrix_path = root / "research/curriculum-coverage-matrix.csv"
    architecture_path = root / "research/competency-transition-map.json"
    ledger_rows, _ = load_csv(ledger_path, errors) if ledger_path.is_file() else ([], [])
    competitor_rows, _ = load_csv(competitor_path, errors) if competitor_path.is_file() else ([], [])
    source_ids = {row.get("id", "").strip() for row in ledger_rows if row.get("id")}
    competitor_ids = {row.get("id", "").strip() for row in competitor_rows if row.get("id")}

    profile = ""
    if architecture_path.is_file():
        architecture = load_json(architecture_path, errors)
        if isinstance(architecture, dict):
            profile = str(architecture.get("architecture_profile", ""))

    if not matrix_path.is_file():
        return
    rows, fields = load_csv(matrix_path, errors)
    for field in COVERAGE_COLUMNS:
        if field not in fields:
            errors.append(f"curriculum coverage matrix missing column: {field}")
    if len(rows) < 24:
        errors.append(f"curriculum coverage matrix needs at least 24 learning cells, found {len(rows)}")

    seen_cells: set[str] = set()
    seen_layers: set[str] = set()
    seen_specializations: set[str] = set()
    for index, row in enumerate(rows):
        cell_id = row.get("cell_id", "").strip()
        if not cell_id:
            errors.append(f"curriculum coverage row {index} missing cell_id")
        elif cell_id in seen_cells:
            errors.append(f"duplicate curriculum coverage cell_id: {cell_id}")
        else:
            seen_cells.add(cell_id)

        for field in ["profession_domain_id", "layer_kind", "learner_level", "topic", "evidence_status", "coverage_status", "priority"]:
            if not row.get(field, "").strip():
                errors.append(f"curriculum coverage row {index} missing value: {field}")
        layer = row.get("layer_kind", "").strip()
        seen_layers.add(layer)
        if layer not in LEARNING_LAYER_KINDS:
            errors.append(f"curriculum coverage row {index} has invalid layer_kind: {layer}")
        specialization = row.get("specialization_kind", "").strip()
        if specialization:
            seen_specializations.add(specialization)

        status = row.get("coverage_status", "").strip()
        priority = row.get("priority", "").strip()
        if status not in COVERAGE_STATUSES:
            errors.append(f"curriculum coverage row {index} has invalid coverage_status: {status}")
        if priority not in COVERAGE_PRIORITIES:
            errors.append(f"curriculum coverage row {index} has invalid priority: {priority}")

        required_sources = {item.strip() for item in row.get("required_by_source_ids", "").split(";") if item.strip()}
        if not required_sources:
            errors.append(f"curriculum coverage row {index} has no supporting source IDs")
        unknown_sources = required_sources - source_ids
        if unknown_sources:
            errors.append(f"curriculum coverage row {index} references unknown source IDs: {', '.join(sorted(unknown_sources))}")
        used_competitors = {item.strip() for item in row.get("competitor_ids", "").split(";") if item.strip()}
        unknown_competitors = used_competitors - competitor_ids
        if unknown_competitors:
            errors.append(f"curriculum coverage row {index} references unknown competitor IDs: {', '.join(sorted(unknown_competitors))}")

        if status in {"covered", "planned"}:
            for field in ["course_ids", "learner_artifact", "exit_assessment", "decision"]:
                if not row.get(field, "").strip():
                    errors.append(f"curriculum coverage row {index} {status} cell missing value: {field}")
        if status == "gap":
            if not row.get("gap_reason", "").strip():
                errors.append(f"curriculum coverage row {index} gap lacks gap_reason")
            if priority in {"critical", "high"} and not row.get("decision", "").strip():
                errors.append(f"curriculum coverage row {index} unresolved {priority}-priority gap lacks decision")
        if status == "rejected" and (not row.get("gap_reason", "").strip() or not row.get("decision", "").strip()):
            errors.append(f"curriculum coverage row {index} rejected cell needs reason and decision")

    missing_layers = set(LEARNING_LAYER_KINDS) - seen_layers
    if missing_layers:
        errors.append(f"curriculum coverage matrix misses learning layers: {', '.join(sorted(missing_layers))}")
    if profile == "ai-quality-engineer":
        missing_specializations = AI_QUALITY_SPECIALIZATIONS - seen_specializations
        if missing_specializations:
            errors.append(f"curriculum coverage matrix misses AI-quality specializations: {', '.join(sorted(missing_specializations))}")


def validate_profession_knowledge_system(root: Path, errors: list[str]) -> None:
    framework_path = root / "industry-framework.md"
    if framework_path.is_file():
        framework = framework_path.read_text(encoding="utf-8")
        if len(framework.strip()) < 2500:
            errors.append("industry-framework.md is too thin to explain a full profession system")
        for marker in [
            "## End-to-end lifecycle", "## Specialization families", "## System and work-object classes",
            "## Quality and outcome attributes", "## AI transformation", "## Role and career evolution",
            "## Coverage verdict", "## Critical gaps",
        ]:
            if marker not in framework:
                errors.append(f"industry-framework.md missing marker: {marker}")

    path = root / "research/profession-knowledge-system.json"
    if not path.is_file():
        return
    data = load_json(path, errors)
    if not isinstance(data, dict):
        return
    require_fields(data, [
        "profession_id", "as_of", "lifecycle_stages", "specialization_families",
        "system_classes", "outcome_attributes", "role_evolution", "coverage_cells",
        "review_status",
    ], "profession knowledge system", errors)

    ledger_path = root / "research/source-ledger.csv"
    ledger_rows, _ = load_csv(ledger_path, errors) if ledger_path.is_file() else ([], [])
    source_ids = {row.get("id", "").strip() for row in ledger_rows if row.get("id")}
    course_path = root / "curriculum.json"
    course_data = load_json(course_path, errors) if course_path.is_file() else None
    course_ids = {
        str(course.get("course_id", "")) for course in course_data.get("courses", [])
        if isinstance(course_data, dict) and isinstance(course, dict) and course.get("course_id")
    } if isinstance(course_data, dict) else set()

    lifecycle = data.get("lifecycle_stages")
    families = data.get("specialization_families")
    systems = data.get("system_classes")
    attributes = data.get("outcome_attributes")
    roles = data.get("role_evolution")
    cells = data.get("coverage_cells")
    minimums = [
        ("lifecycle stages", lifecycle, 8), ("specialization families", families, 6),
        ("system classes", systems, 5), ("outcome attributes", attributes, 6),
        ("role evolution levels", roles, 4), ("coverage cells", cells, 24),
    ]
    for label, values, minimum in minimums:
        if not isinstance(values, list) or len(values) < minimum:
            errors.append(f"profession knowledge system needs at least {minimum} {label}")

    seen_change_classes: set[str] = set()
    lifecycle_ids: set[str] = set()
    family_ids: set[str] = set()
    system_ids: set[str] = set()
    attribute_ids: set[str] = set()

    change_fields = [
        "change_id", "change_class", "baseline_work", "ai_intervention", "human_accountability",
        "new_failure_modes", "required_controls", "learner_proof", "evidence_ids", "confidence",
    ]

    def validate_evidence_and_courses(item: dict[str, Any], label: str, require_courses: bool = True) -> None:
        evidence = item.get("evidence_ids")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{label} needs evidence_ids")
        elif set(evidence) - source_ids:
            errors.append(f"{label} references unknown evidence IDs")
        if require_courses:
            courses = item.get("course_ids")
            if not isinstance(courses, list):
                errors.append(f"{label} course_ids must be a list")
            elif set(str(value) for value in courses) - course_ids:
                errors.append(f"{label} references unknown course IDs")

    def validate_changes(item: dict[str, Any], label: str) -> None:
        changes = item.get("ai_changes")
        if not isinstance(changes, list) or not changes:
            errors.append(f"{label} needs at least one AI change")
            return
        for change_index, change in enumerate(changes):
            if not isinstance(change, dict):
                errors.append(f"{label} AI change {change_index} is not an object")
                continue
            require_fields(change, change_fields, f"{label} AI change {change_index}", errors)
            change_class = str(change.get("change_class", ""))
            seen_change_classes.add(change_class)
            if change_class not in AI_CHANGE_CLASSES:
                errors.append(f"{label} AI change {change_index} has invalid change_class: {change_class}")
            for list_field in ["new_failure_modes", "required_controls", "evidence_ids"]:
                if not isinstance(change.get(list_field), list) or not change.get(list_field):
                    errors.append(f"{label} AI change {change_index} needs non-empty {list_field}")
            evidence = set(change.get("evidence_ids", [])) if isinstance(change.get("evidence_ids"), list) else set()
            if evidence - source_ids:
                errors.append(f"{label} AI change {change_index} references unknown evidence IDs")

    if isinstance(lifecycle, list):
        lifecycle_fields = [
            "stage_id", "name", "trigger", "inputs", "activities", "outputs", "artifacts", "decision_gate",
            "owner", "metrics", "tools", "failure_modes", "downstream_handoff", "evidence_ids", "course_ids", "ai_changes",
        ]
        for index, stage in enumerate(lifecycle):
            if not isinstance(stage, dict):
                errors.append(f"lifecycle stage {index} is not an object")
                continue
            require_fields(stage, lifecycle_fields, f"lifecycle stage {index}", errors)
            stage_id = str(stage.get("stage_id", ""))
            if stage_id in lifecycle_ids:
                errors.append(f"duplicate lifecycle stage_id: {stage_id}")
            lifecycle_ids.add(stage_id)
            for list_field in ["inputs", "activities", "outputs", "artifacts", "metrics", "tools", "failure_modes"]:
                if not isinstance(stage.get(list_field), list) or not stage.get(list_field):
                    errors.append(f"lifecycle stage {index} needs non-empty {list_field}")
            validate_evidence_and_courses(stage, f"lifecycle stage {index}")
            validate_changes(stage, f"lifecycle stage {index}")

    if isinstance(families, list):
        family_fields = [
            "family_id", "name", "scope", "protected_outcome", "risks", "methods", "artifacts", "metrics", "tools",
            "prerequisites", "lifecycle_stage_ids", "system_class_ids", "evidence_ids", "course_ids", "ai_changes",
        ]
        for index, family in enumerate(families):
            if not isinstance(family, dict):
                errors.append(f"specialization family {index} is not an object")
                continue
            require_fields(family, family_fields, f"specialization family {index}", errors)
            family_id = str(family.get("family_id", ""))
            if family_id in family_ids:
                errors.append(f"duplicate specialization family_id: {family_id}")
            family_ids.add(family_id)
            validate_evidence_and_courses(family, f"specialization family {index}")
            validate_changes(family, f"specialization family {index}")

    if isinstance(systems, list):
        system_fields = [
            "system_class_id", "name", "interfaces", "state", "dependencies", "observability_points",
            "characteristic_failures", "quality_attribute_ids", "specialization_family_ids", "evidence_ids", "course_ids",
        ]
        for index, system in enumerate(systems):
            if not isinstance(system, dict):
                errors.append(f"system class {index} is not an object")
                continue
            require_fields(system, system_fields, f"system class {index}", errors)
            system_id = str(system.get("system_class_id", ""))
            if system_id in system_ids:
                errors.append(f"duplicate system_class_id: {system_id}")
            system_ids.add(system_id)
            validate_evidence_and_courses(system, f"system class {index}")

    if isinstance(attributes, list):
        attribute_fields = [
            "attribute_id", "name", "definition", "observable_indicators", "leading_metrics", "lagging_metrics",
            "verification_methods", "decision_thresholds", "tradeoffs", "ai_specific_risks", "evidence_ids", "course_ids",
        ]
        for index, attribute in enumerate(attributes):
            if not isinstance(attribute, dict):
                errors.append(f"outcome attribute {index} is not an object")
                continue
            require_fields(attribute, attribute_fields, f"outcome attribute {index}", errors)
            attribute_id = str(attribute.get("attribute_id", ""))
            if attribute_id in attribute_ids:
                errors.append(f"duplicate outcome attribute_id: {attribute_id}")
            attribute_ids.add(attribute_id)
            if not isinstance(attribute.get("decision_thresholds"), list) or not attribute.get("decision_thresholds"):
                errors.append(f"outcome attribute {index} needs decision thresholds")
            validate_evidence_and_courses(attribute, f"outcome attribute {index}")

    if isinstance(roles, list):
        role_fields = [
            "role_id", "level", "current_responsibilities", "durable_skills", "assisted_or_automated_work",
            "new_ai_responsibilities", "adjacent_roles", "transition_projects", "portfolio_evidence", "decision_authority",
            "evidence_ids", "course_ids", "forecast_boundary",
        ]
        for index, role in enumerate(roles):
            if not isinstance(role, dict):
                errors.append(f"role evolution {index} is not an object")
                continue
            require_fields(role, role_fields, f"role evolution {index}", errors)
            validate_evidence_and_courses(role, f"role evolution {index}")

    if isinstance(families, list):
        for index, family in enumerate(families):
            if not isinstance(family, dict):
                continue
            if set(family.get("lifecycle_stage_ids", [])) - lifecycle_ids:
                errors.append(f"specialization family {index} references unknown lifecycle stages")
            if set(family.get("system_class_ids", [])) - system_ids:
                errors.append(f"specialization family {index} references unknown system classes")
    if isinstance(systems, list):
        for index, system in enumerate(systems):
            if not isinstance(system, dict):
                continue
            if set(system.get("quality_attribute_ids", [])) - attribute_ids:
                errors.append(f"system class {index} references unknown outcome attributes")
            if set(system.get("specialization_family_ids", [])) - family_ids:
                errors.append(f"system class {index} references unknown specialization families")

    if isinstance(cells, list):
        seen_cells: set[str] = set()
        for index, cell in enumerate(cells):
            if not isinstance(cell, dict):
                errors.append(f"knowledge coverage cell {index} is not an object")
                continue
            require_fields(cell, [
                "cell_id", "lifecycle_stage_id", "specialization_family_id", "system_class_id",
                "outcome_attribute_id", "learner_level", "status", "priority", "rationale",
            ], f"knowledge coverage cell {index}", errors)
            cell_id = str(cell.get("cell_id", ""))
            if cell_id in seen_cells:
                errors.append(f"duplicate knowledge coverage cell_id: {cell_id}")
            seen_cells.add(cell_id)
            if cell.get("status") not in KNOWLEDGE_CELL_STATUSES:
                errors.append(f"knowledge coverage cell {index} has invalid status: {cell.get('status')}")
            if cell.get("lifecycle_stage_id") not in lifecycle_ids or cell.get("specialization_family_id") not in family_ids or cell.get("system_class_id") not in system_ids or cell.get("outcome_attribute_id") not in attribute_ids:
                errors.append(f"knowledge coverage cell {index} references an unknown dimension")
            status = cell.get("status")
            if status in {"covered", "planned"}:
                require_fields(cell, ["course_ids", "learner_artifact", "assessment", "evidence_ids"], f"knowledge coverage cell {index}", errors)
                validate_evidence_and_courses(cell, f"knowledge coverage cell {index}")
            if status == "gap" and cell.get("priority") in {"critical", "high"}:
                require_fields(cell, ["owner", "decision"], f"knowledge coverage cell {index}", errors)
            if status == "not-applicable" and len(str(cell.get("rationale", "")).strip()) < 12:
                errors.append(f"knowledge coverage cell {index} not-applicable rationale is too thin")

    missing_changes = MANDATORY_AI_CHANGE_CLASSES - seen_change_classes
    if missing_changes:
        errors.append(f"profession knowledge system misses mandatory AI change classes: {', '.join(sorted(missing_changes))}")

    critical_gaps = data.get("critical_gaps")
    if not isinstance(critical_gaps, list):
        errors.append("profession knowledge system critical_gaps must be a list")
    else:
        for index, gap in enumerate(critical_gaps):
            if not isinstance(gap, dict):
                errors.append(f"critical gap {index} is not an object")
                continue
            require_fields(gap, ["gap_id", "priority", "description", "decision", "owner", "acceptance_gate"], f"critical gap {index}", errors)
            if gap.get("priority") in {"critical", "high"} and gap.get("decision") in {"unresolved", "", None}:
                errors.append(f"profession knowledge system has unresolved {gap.get('priority')} gap: {gap.get('gap_id')}")

    review_status = data.get("review_status")
    if not isinstance(review_status, dict):
        errors.append("profession knowledge system review_status must be an object")
    else:
        for review in ["lifecycle_continuity", "specialization_completeness", "system_diversity", "metrics_and_gates", "ai_change_realism", "career_coherence"]:
            if review_status.get(review) not in {"pass", "conditional-pass"}:
                errors.append(f"profession knowledge system review did not pass: {review}")


def validate_tasks_and_curriculum(root: Path, errors: list[str]) -> None:
    scenario_data = load_json(root / "research/scenarios.json", errors) if (root / "research/scenarios.json").is_file() else None
    scenario_records = scenario_data.get("scenarios", []) if isinstance(scenario_data, dict) else []
    scenario_by_id = {
        item.get("scenario_id"): item for item in scenario_records
        if isinstance(item, dict) and item.get("scenario_id")
    }
    scenario_ids = {
        item.get("scenario_id") for item in scenario_records
        if isinstance(item, dict) and item.get("scenario_id")
    }
    tasks_data = load_json(root / "tasks.json", errors) if (root / "tasks.json").is_file() else None
    tasks = tasks_data.get("tasks") if isinstance(tasks_data, dict) else tasks_data
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks.json must contain a non-empty tasks list")
    else:
        required = [
            "task_id", "career_id", "scenario_id", "title", "ai_lane", "ai_role", "system_under_test",
            "professional_problem", "inputs", "non_ai_baseline", "ai_workflow",
            "ai_specific_failures", "learner_proof", "deliverables", "scores",
            "acceptance_criteria", "human_gate", "privacy_notes", "status", "evidence_ids",
        ]
        for index, task in enumerate(tasks):
            if not isinstance(task, dict):
                errors.append(f"task {index} is not an object")
                continue
            require_fields(task, required, f"task {index}", errors)
            if task.get("ai_lane") not in AI_LANES:
                errors.append(f"task {index} has invalid ai_lane: {task.get('ai_lane')}")
            if task.get("scenario_id") not in scenario_ids:
                errors.append(f"task {index} references unknown scenario_id: {task.get('scenario_id')}")
            elif any(field in task for field in ["business_event", "decision_owner", "allowed_ai_authority"]):
                scenario = scenario_by_id[task.get("scenario_id")]
                semantic = scenario.get("semantic_contract", {})
                if task.get("decision_owner") and task.get("decision_owner") != semantic.get("decision_owner"):
                    errors.append(f"task {index} decision_owner does not match scenario")
                if task.get("allowed_ai_authority") and task.get("allowed_ai_authority") != semantic.get("allowed_ai_authority"):
                    errors.append(f"task {index} allowed_ai_authority does not match scenario")
                if task.get("business_event") and task.get("business_event") != scenario.get("trigger"):
                    errors.append(f"task {index} business_event does not match scenario trigger")
            scores = task.get("scores", {})
            for field in ["ai_centrality", "professional_leverage", "runnable_proof", "source_strength"]:
                if not isinstance(scores.get(field), int):
                    errors.append(f"task {index} score missing or non-integer: {field}")
            if isinstance(scores.get("ai_centrality"), int) and scores["ai_centrality"] < 4:
                errors.append(f"task {index} fails AI centrality gate: {scores['ai_centrality']} < 4")
            if isinstance(scores.get("runnable_proof"), int) and scores["runnable_proof"] < 3:
                errors.append(f"task {index} fails runnable proof gate: {scores['runnable_proof']} < 3")

    architecture_path = root / "research/competency-transition-map.json"
    architecture = load_json(architecture_path, errors) if architecture_path.is_file() else None
    stage_ids: set[str] = set()
    stage_order: dict[str, int] = {}
    if isinstance(architecture, dict):
        require_fields(architecture, [
            "profession_id", "architecture_profile", "audience", "as_of", "professional_baseline",
            "ai_foundations", "transition_matrix", "learning_stages", "specialization_tracks", "source_ids",
        ], "competency transition map", errors)
        profile = architecture.get("architecture_profile")
        if profile not in ARCHITECTURE_PROFILES:
            errors.append(f"competency transition map has invalid architecture_profile: {profile}")

        baseline = architecture.get("professional_baseline")
        if not isinstance(baseline, dict):
            errors.append("competency transition map professional_baseline must be an object")
        else:
            for field, minimum in {
                "lifecycle_stages": 5, "work_domains": 5, "methods": 4,
                "tools_and_artifacts": 4, "quality_decisions": 3,
            }.items():
                values = baseline.get(field)
                if not isinstance(values, list) or len(values) < minimum:
                    errors.append(f"professional baseline needs at least {minimum} {field}")
            if not str(baseline.get("entry_assessment", "")).strip():
                errors.append("professional baseline needs an artifact-based entry_assessment")

        foundations = architecture.get("ai_foundations")
        if not isinstance(foundations, dict):
            errors.append("competency transition map ai_foundations must be an object")
        else:
            for field, minimum in {
                "model_lifecycle": 5, "core_primitives": 6, "application_patterns": 4,
                "capability_boundaries": 6, "test_implications": 5,
            }.items():
                values = foundations.get(field)
                if not isinstance(values, list) or len(values) < minimum:
                    errors.append(f"AI foundations need at least {minimum} {field}")

        transitions = architecture.get("transition_matrix")
        transition_fields = [
            "transition_id", "baseline_competency", "retained_principle", "ai_change",
            "new_ai_capability", "new_failure_modes", "learner_artifact", "assessment", "course_ids",
        ]
        if not isinstance(transitions, list) or len(transitions) < 6:
            errors.append("competency transition map needs at least 6 professional-to-AI transitions")
        else:
            for index, transition in enumerate(transitions):
                if not isinstance(transition, dict):
                    errors.append(f"competency transition {index} is not an object")
                    continue
                require_fields(transition, transition_fields, f"competency transition {index}", errors)
                if not isinstance(transition.get("new_failure_modes"), list) or len(transition.get("new_failure_modes", [])) < 2:
                    errors.append(f"competency transition {index} needs at least two AI-specific failure modes")

        stages = architecture.get("learning_stages")
        seen_layer_kinds: list[str] = []
        if not isinstance(stages, list) or len(stages) < len(LEARNING_LAYER_KINDS):
            errors.append("competency transition map needs all eight learning stages")
        else:
            for index, stage in enumerate(stages):
                if not isinstance(stage, dict):
                    errors.append(f"learning stage {index} is not an object")
                    continue
                require_fields(stage, [
                    "stage_id", "layer_kind", "order", "title", "learner_transformation",
                    "required_concepts", "learner_artifact",
                    "exit_assessment", "failure_injection", "course_ids", "source_ids",
                ], f"learning stage {index}", errors)
                stage_id = str(stage.get("stage_id", ""))
                if stage_id in stage_ids:
                    errors.append(f"duplicate learning stage_id: {stage_id}")
                elif stage_id:
                    stage_ids.add(stage_id)
                    stage_order[stage_id] = int(stage.get("order", -1)) if isinstance(stage.get("order"), int) else -1
                seen_layer_kinds.append(str(stage.get("layer_kind", "")))
                if stage.get("order") != index + 1:
                    errors.append(f"learning stage {stage_id or index} order must be {index + 1}")
                if not isinstance(stage.get("required_concepts"), list) or len(stage.get("required_concepts", [])) < 2:
                    errors.append(f"learning stage {stage_id or index} needs at least two required concepts")
                if not isinstance(stage.get("prerequisite_stage_ids"), list):
                    errors.append(f"learning stage {stage_id or index} prerequisite_stage_ids must be a list")
                if not isinstance(stage.get("course_ids"), list) or not stage.get("course_ids"):
                    errors.append(f"learning stage {stage_id or index} needs at least one course")
            if seen_layer_kinds[:len(LEARNING_LAYER_KINDS)] != LEARNING_LAYER_KINDS:
                errors.append("learning stages must follow the eight-layer dependency order")
            for index, stage in enumerate(stages):
                if not isinstance(stage, dict):
                    continue
                current_order = stage.get("order", -1)
                for dependency in stage.get("prerequisite_stage_ids", []):
                    if dependency not in stage_order:
                        errors.append(f"learning stage {stage.get('stage_id')} references unknown prerequisite stage {dependency}")
                    elif stage_order[dependency] >= current_order:
                        errors.append(f"learning stage {stage.get('stage_id')} prerequisite {dependency} must appear earlier")

        tracks = architecture.get("specialization_tracks")
        if not isinstance(tracks, list) or len(tracks) < 2:
            errors.append("competency transition map needs at least two specialization tracks")
        else:
            track_kinds = set()
            for index, track in enumerate(tracks):
                if not isinstance(track, dict):
                    errors.append(f"specialization track {index} is not an object")
                    continue
                require_fields(track, ["track_id", "track_kind", "title", "prerequisite_stage_ids", "course_ids", "capstone_artifact", "source_ids"], f"specialization track {index}", errors)
                track_kinds.add(track.get("track_kind"))
            if profile == "ai-quality-engineer":
                missing_tracks = AI_QUALITY_SPECIALIZATIONS - track_kinds
                if missing_tracks:
                    errors.append(f"AI quality architecture misses specialization tracks: {', '.join(sorted(missing_tracks))}")

    architecture_markdown = root / "learning-architecture.md"
    if architecture_markdown.is_file():
        text = architecture_markdown.read_text(encoding="utf-8")
        if len(text.strip()) < 2000:
            errors.append("learning-architecture.md is too thin to explain a professional progression")
        for marker in LEARNING_ARCHITECTURE_MARKERS:
            if marker not in text:
                errors.append(f"learning-architecture.md missing marker: {marker}")

    curriculum = load_json(root / "curriculum.json", errors) if (root / "curriculum.json").is_file() else None
    courses = curriculum.get("courses") if isinstance(curriculum, dict) else None
    if not isinstance(courses, list) or len(courses) < 10:
        errors.append("curriculum.json must contain at least 10 courses")
    else:
        lanes = {course.get("ai_lane") for course in courses if isinstance(course, dict)}
        missing = AI_LANES - lanes
        if missing:
            errors.append(f"curriculum misses AI lanes: {', '.join(sorted(missing))}")
        for index, course in enumerate(courses):
            if isinstance(course, dict):
                require_fields(course, [
                    "course_id", "title", "stage_id", "level", "ai_lane",
                    "knowledge_dependencies", "professional_baseline", "new_ai_capability",
                    "learner_artifact", "assessment", "proof", "source_ids", "delivery_status",
                ], f"curriculum course {index}", errors)
                if stage_ids and course.get("stage_id") not in stage_ids:
                    errors.append(f"curriculum course {index} references unknown stage_id: {course.get('stage_id')}")
                if not isinstance(course.get("knowledge_dependencies"), list) or not course.get("knowledge_dependencies"):
                    errors.append(f"curriculum course {index} needs explicit knowledge_dependencies")
                if not isinstance(course.get("prerequisite_course_ids"), list):
                    errors.append(f"curriculum course {index} prerequisite_course_ids must be a list")
                if not isinstance(course.get("source_ids"), list) or not course.get("source_ids"):
                    errors.append(f"curriculum course {index} needs source_ids")
                if course.get("delivery_status") not in {"planned", "researched", "fixture-tested", "live-tested", "practitioner-reviewed", "blocked"}:
                    errors.append(f"curriculum course {index} has invalid delivery_status")
                if course.get("delivery_status") in {"fixture-tested", "live-tested", "practitioner-reviewed"}:
                    manifest_path = root / "courses" / str(course.get("course_id", "")).lower() / "course-manifest.json"
                    if not manifest_path.is_file():
                        errors.append(f"curriculum course {index} claims {course.get('delivery_status')} without a built course package")


def validate_execution(course: Path, manifest: dict[str, Any], errors: list[str]) -> None:
    proof_path = course / str(manifest.get("execution_proof", ""))
    if not proof_path.is_file():
        errors.append(f"{course.name} execution proof file not found: {manifest.get('execution_proof')}")
        return
    proof = load_json(proof_path, errors)
    if not isinstance(proof, dict):
        return
    require_fields(proof, ["evidence_scope", "commands", "baseline", "mutation", "repair", "environment", "limitations"], f"{course.name} execution evidence", errors)
    commands = proof.get("commands")
    if not isinstance(commands, list) or len(commands) < 3:
        errors.append(f"{course.name} must record baseline, mutation, and repair commands")
    baseline = proof.get("baseline", {})
    mutation = proof.get("mutation", {})
    repair = proof.get("repair", {})
    if baseline.get("exit_code") != 0 or baseline.get("verdict") != "PASS":
        errors.append(f"{course.name} baseline evidence must be PASS with exit_code 0")
    if mutation.get("exit_code") == 0 or mutation.get("verdict") != "FAIL":
        errors.append(f"{course.name} mutation evidence must be FAIL with non-zero exit_code")
    if repair.get("exit_code") != 0 or repair.get("verdict") != "PASS":
        errors.append(f"{course.name} repair evidence must return to PASS")


def validate_courses(root: Path, errors: list[str]) -> None:
    scenario_data = load_json(root / "research/scenarios.json", errors) if (root / "research/scenarios.json").is_file() else None
    scenario_by_id = {
        item.get("scenario_id"): item
        for item in (scenario_data.get("scenarios", []) if isinstance(scenario_data, dict) else [])
        if isinstance(item, dict) and item.get("scenario_id")
    }
    ledger_rows, _ = load_csv(root / "research/source-ledger.csv", errors) if (root / "research/source-ledger.csv").is_file() else ([], [])
    ledger_ids = {row.get("id", "").strip() for row in ledger_rows if row.get("id")}
    course_root = root / "courses"
    if not course_root.is_dir():
        errors.append("missing directory: courses")
        return
    course_dirs = sorted(path for path in course_root.iterdir() if path.is_dir())
    if not course_dirs:
        errors.append("at least one fully built exemplar course is required")
    for course in course_dirs:
        for relative in COURSE_FILES:
            if not (course / relative).is_file():
                errors.append(f"{course.name} missing {relative}")
        manifest_path = course / "course-manifest.json"
        manifest = load_json(manifest_path, errors) if manifest_path.is_file() else None
        if isinstance(manifest, dict):
            require_fields(manifest, [
                "course_id", "title", "scenario_ids", "ai_lane", "ai_centrality_score", "professional_value_score",
                "system_under_test", "ai_roles", "learner_artifact", "tool_adapters",
                "default_path_requires_credentials", "baseline_comparison", "failure_injection",
                "execution_proof", "validation_workdir", "validation_steps", "status", "evidence_ids",
                "work_domain_ids", "primary_artifact_ids", "decision_owner", "allowed_ai_authority",
                "prerequisite_course_ids", "transfer_target", "lesson_flow",
            ], f"{course.name} manifest", errors)
            ai_lane = manifest.get("ai_lane")
            if not isinstance(ai_lane, str) or ai_lane not in AI_LANES:
                errors.append(f"{course.name} manifest has invalid ai_lane")
            if not isinstance(manifest.get("scenario_ids"), list) or not manifest.get("scenario_ids"):
                errors.append(f"{course.name} manifest must reference at least one business scenario")
            else:
                unknown_scenarios = set(manifest.get("scenario_ids", [])) - set(scenario_by_id)
                if unknown_scenarios:
                    errors.append(f"{course.name} manifest references unknown scenarios: {', '.join(sorted(unknown_scenarios))}")
                for scenario_id in set(manifest.get("scenario_ids", [])) & set(scenario_by_id):
                    semantic = scenario_by_id[scenario_id].get("semantic_contract", {})
                    if manifest.get("decision_owner") != semantic.get("decision_owner"):
                        errors.append(f"{course.name} decision_owner does not match scenario {scenario_id}")
                    if manifest.get("allowed_ai_authority") != semantic.get("allowed_ai_authority"):
                        errors.append(f"{course.name} allowed_ai_authority does not match scenario {scenario_id}")
            if manifest.get("ai_centrality_score", 0) < 4:
                errors.append(f"{course.name} fails AI centrality gate")
            if manifest.get("professional_value_score", 0) < 4:
                errors.append(f"{course.name} fails professional value gate")
            if manifest.get("default_path_requires_credentials") is not False:
                errors.append(f"{course.name} default path must not require hidden credentials")
            if manifest.get("baseline_comparison") is not True or manifest.get("failure_injection") is not True:
                errors.append(f"{course.name} must include baseline comparison and failure injection")
            if manifest.get("status") not in VALID_STATUSES:
                errors.append(f"{course.name} has invalid status: {manifest.get('status')}")
            steps = manifest.get("validation_steps")
            if not isinstance(steps, list) or len(steps) < 3:
                errors.append(f"{course.name} must define at least three structured validation_steps")
            else:
                for index, step in enumerate(steps):
                    if not isinstance(step, dict):
                        errors.append(f"{course.name} validation step {index} is not an object")
                        continue
                    require_fields(step, ["name", "command", "expected_exit_code"], f"{course.name} validation step {index}", errors)
                    command = step.get("command")
                    if not isinstance(command, list) or not command or not all(isinstance(item, str) and item for item in command):
                        errors.append(f"{course.name} validation step {index} command must be a non-empty string array")
                    if not isinstance(step.get("expected_exit_code"), int):
                        errors.append(f"{course.name} validation step {index} expected_exit_code must be integer")
            if manifest.get("status") in {"fixture-tested", "live-tested", "practitioner-reviewed", "production-validated"}:
                validate_execution(course, manifest, errors)
            lesson_flow = manifest.get("lesson_flow")
            if lesson_flow != ["demo", "guided-practice", "failure-injection", "repair", "transfer"]:
                errors.append(f"{course.name} manifest lesson_flow must be demo -> guided-practice -> failure-injection -> repair -> transfer")

        course_md = course / "course.md"
        if course_md.is_file():
            text = course_md.read_text(encoding="utf-8")
            for marker in COURSE_MARKERS:
                if marker not in text:
                    errors.append(f"{course.name}/course.md missing marker: {marker}")
                elif len(section_body(text, marker)) < 80:
                    errors.append(f"{course.name}/course.md section is too thin: {marker}")
            if "TODO" in text:
                errors.append(f"{course.name}/course.md contains TODO")
            if len(text.strip()) < 1500:
                errors.append(f"{course.name}/course.md is too thin to teach the required workflow")
            commands = section_body(text, "## Commands")
            if "```" not in commands or not any(token in commands for token in ["python", "npm", "npx", "uv ", "docker", "curl"]):
                errors.append(f"{course.name}/course.md Commands must contain a runnable command block")
            failure = section_body(text, "## Failure injection")
            if not any(token in failure.lower() for token in ["fail", "失败", "exit", "变红", "non-zero"]):
                errors.append(f"{course.name}/course.md Failure injection must define an observable failing result")

        provenance_path = course / "materials/material-provenance.json"
        if provenance_path.is_file():
            provenance = load_json(provenance_path, errors)
            materials = provenance.get("materials") if isinstance(provenance, dict) else None
            if not isinstance(materials, list) or len(materials) < 5:
                errors.append(f"{course.name} material provenance needs at least 5 learner-facing materials")
            else:
                for index, material in enumerate(materials):
                    if not isinstance(material, dict):
                        errors.append(f"{course.name} material provenance row {index} is not an object")
                        continue
                    require_fields(material, ["material_id", "path", "purpose", "source_ids", "scenario_ids", "generated_from", "license_or_usage", "validation_status", "validation_evidence", "contains_synthetic_data", "limitations"], f"{course.name} material provenance row {index}", errors)
                    material_path = course / str(material.get("path", ""))
                    if not material_path.is_file():
                        errors.append(f"{course.name} material provenance row {index} points to missing file")
                    elif len(material_path.read_text(encoding="utf-8").strip()) < 80:
                        errors.append(f"{course.name} material provenance row {index} points to a content-free material")
                    source_ids = set(material.get("source_ids", [])) if isinstance(material.get("source_ids"), list) else set()
                    if not source_ids or source_ids - ledger_ids:
                        errors.append(f"{course.name} material provenance row {index} has missing or unknown source IDs")
                    scenario_ids = set(material.get("scenario_ids", [])) if isinstance(material.get("scenario_ids"), list) else set()
                    if not scenario_ids or scenario_ids - set(scenario_by_id):
                        errors.append(f"{course.name} material provenance row {index} has missing or unknown scenario IDs")
                    if material.get("validation_status") not in {"static-reviewed", "fixture-tested", "live-tested", "practitioner-reviewed", "blocked"}:
                        errors.append(f"{course.name} material provenance row {index} has invalid validation_status")
                    if not isinstance(material.get("contains_synthetic_data"), bool):
                        errors.append(f"{course.name} material provenance row {index} contains_synthetic_data must be boolean")

        lesson_path = course / "video/lesson-experience.json"
        if lesson_path.is_file():
            lesson = load_json(lesson_path, errors)
            if isinstance(lesson, dict):
                require_fields(lesson, ["lesson_id", "target_learner", "level", "estimated_minutes", "job_result", "artifact", "stages", "interaction_prompts", "recovery_path", "evidence_status", "limitations"], f"{course.name} lesson experience", errors)
                stages = lesson.get("stages")
                stage_ids = [stage.get("stage_id") for stage in stages if isinstance(stage, dict)] if isinstance(stages, list) else []
                if stage_ids != LESSON_STAGES:
                    errors.append(f"{course.name} lesson experience has invalid or incomplete stage order")
                if isinstance(stages, list):
                    for index, stage in enumerate(stages):
                        if not isinstance(stage, dict):
                            errors.append(f"{course.name} lesson stage {index} is not an object")
                            continue
                        require_fields(stage, ["stage_id", "instructor_action", "learner_action", "expected_observation", "debrief", "artifact_or_assessment"], f"{course.name} lesson stage {index}", errors)
                        for field in ["instructor_action", "learner_action", "expected_observation", "debrief", "artifact_or_assessment"]:
                            minimum = 6 if field == "artifact_or_assessment" else 12
                            if len(str(stage.get(field, "")).strip()) < minimum:
                                errors.append(f"{course.name} lesson stage {index} has weak instructional content: {field}")
                        if stage.get("stage_id") == "transfer-challenge":
                            require_fields(stage, TRANSFER_FIELDS, f"{course.name} transfer challenge", errors)
                            if stage.get("source_context") == stage.get("target_context"):
                                errors.append(f"{course.name} transfer challenge must change business context")
                            must_change = stage.get("must_change")
                            if not isinstance(must_change, list) or len(must_change) < 2:
                                errors.append(f"{course.name} transfer challenge must name at least two adaptations")
                            if manifest and stage.get("target_context") and stage.get("target_context") not in str(manifest.get("transfer_target", "")):
                                errors.append(f"{course.name} transfer challenge target does not match manifest transfer_target")
                if not isinstance(lesson.get("interaction_prompts"), list) or len(lesson.get("interaction_prompts", [])) < 3:
                    errors.append(f"{course.name} lesson experience needs at least 3 learner interactions")


def validate_tutorial(root: Path, errors: list[str]) -> None:
    for relative, markers in REQUIRED_TUTORIAL_MARKDOWN.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing tutorial file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        if len(text.strip()) < 500:
            errors.append(f"tutorial file is too thin: {relative}")
        for marker in markers:
            if marker not in text:
                errors.append(f"tutorial file {relative} missing marker: {marker}")

    data_path = root / "tutorial/tutorial-site.json"
    html_path = root / "tutorial/index.html"
    if not data_path.is_file():
        errors.append("missing tutorial file: tutorial/tutorial-site.json")
        return
    if not html_path.is_file():
        errors.append("missing tutorial file: tutorial/index.html")
        return

    data = load_json(data_path, errors)
    if not isinstance(data, dict):
        return
    require_fields(data, ["tutorial_id", "title", "audience", "updated_at", "default_page_id", "release_scope", "modules", "pages"], "tutorial site", errors)
    modules = data.get("modules")
    pages = data.get("pages")
    if not isinstance(modules, list) or not modules:
        errors.append("tutorial site needs at least one public module")
        modules = []
    if not isinstance(pages, list) or not pages:
        errors.append("tutorial site needs at least one public page")
        pages = []

    module_ids: set[str] = set()
    for index, module in enumerate(modules):
        if not isinstance(module, dict):
            errors.append(f"tutorial module {index} is not an object")
            continue
        require_fields(module, ["module_id", "title", "learner_result", "order"], f"tutorial module {index}", errors)
        module_id = str(module.get("module_id", ""))
        if module_id in module_ids:
            errors.append(f"duplicate tutorial module_id: {module_id}")
        module_ids.add(module_id)

    page_ids: set[str] = set()
    slugs: set[str] = set()
    page_by_id: dict[str, dict[str, Any]] = {}
    page_fields = [
        "page_id", "slug", "module_id", "title", "page_type", "level", "order", "display_number",
        "scenario_ids", "learner_result", "artifact", "keywords",
        "evidence_status", "delivery_status", "updated_at", "source_ids",
        "architecture", "materials",
    ]
    for index, page in enumerate(pages):
        if not isinstance(page, dict):
            errors.append(f"tutorial page {index} is not an object")
            continue
        require_fields(page, page_fields, f"tutorial page {index}", errors)
        page_id = str(page.get("page_id", ""))
        slug = str(page.get("slug", ""))
        if page_id in page_ids:
            errors.append(f"duplicate tutorial page_id: {page_id}")
        if slug in slugs:
            errors.append(f"duplicate tutorial page slug: {slug}")
        page_ids.add(page_id)
        slugs.add(slug)
        page_by_id[page_id] = page
        if page.get("display_number") != index + 1:
            errors.append(f"tutorial page {index} display_number must be contiguous 1..N")
        if page.get("module_id") not in module_ids:
            errors.append(f"tutorial page {index} references unknown module_id")
        if page.get("page_type") not in TUTORIAL_PAGE_TYPES:
            errors.append(f"tutorial page {index} has invalid page_type")
        if page.get("delivery_status") not in TUTORIAL_DELIVERY_STATUSES:
            errors.append(f"tutorial page {index} has invalid delivery_status")
        if "prerequisite_ids" not in page or not isinstance(page.get("prerequisite_ids"), list):
            errors.append(f"tutorial page {index} prerequisite_ids must be a list")
        if not isinstance(page.get("keywords"), list) or len(page.get("keywords", [])) < 2:
            errors.append(f"tutorial page {index} needs at least two search keywords")
        if page.get("delivery_status") not in {"planned", "outlined", "blocked"}:
            sections = page.get("content_sections")
            required_sections = {
                "outcome", "professional_relevance", "plain_explanation", "smallest_example",
                "learner_action", "expected_result", "common_errors", "completion_check", "evidence_boundary",
            }
            if not isinstance(sections, dict) or not required_sections.issubset(sections):
                errors.append(f"tutorial delivered page {index} lacks required content sections")
            architecture = page.get("architecture")
            if not isinstance(architecture, dict):
                errors.append(f"tutorial delivered page {index} lacks an architecture/workflow diagram")
            else:
                require_fields(architecture, ["title", "caption", "nodes"], f"tutorial page {index} architecture", errors)
                if not isinstance(architecture.get("nodes"), list) or len(architecture.get("nodes", [])) < 5:
                    errors.append(f"tutorial page {index} architecture needs at least 5 nodes")
            materials = page.get("materials")
            if not isinstance(materials, list) or not materials:
                errors.append(f"tutorial delivered page {index} needs learner-facing materials")
            else:
                tested_materials = 0
                has_script = False
                seen_hrefs: set[str] = set()
                for material_index, material in enumerate(materials):
                    label = f"tutorial page {index} material {material_index}"
                    if not isinstance(material, dict):
                        errors.append(f"{label} is not an object")
                        continue
                    require_fields(material, ["title", "description", "href", "kind", "validation"], label, errors)
                    href = str(material.get("href", ""))
                    if href in seen_hrefs:
                        errors.append(f"{label} repeats href {href}")
                    seen_hrefs.add(href)
                    if href.startswith(("http://", "https://", "//")) or ".." in Path(href).parts:
                        errors.append(f"{label} must reference a repository-owned relative path")
                    elif href and not (root / "site/public" / href).is_file():
                        errors.append(f"{label} references missing file: site/public/{href}")
                    if material.get("kind") not in {"script", "config", "fixture", "guide", "evidence", "archive"}:
                        errors.append(f"{label} has invalid kind")
                    if material.get("validation") not in {"static-reviewed", "fixture-tested"}:
                        errors.append(f"{label} has invalid validation")
                    if material.get("validation") == "fixture-tested":
                        tested_materials += 1
                    if material.get("kind") == "script":
                        has_script = True
                if page.get("delivery_status") == "fixture-tested" and (tested_materials < 2 or not has_script):
                    errors.append(f"tutorial fixture-tested page {index} needs two tested materials including a script")

    incomplete_public = {
        page_id for page_id, page in page_by_id.items()
        if page.get("delivery_status") in {"planned", "outlined", "blocked"}
    }
    if incomplete_public:
        errors.append(f"public tutorial contains incomplete pages: {', '.join(sorted(incomplete_public))}")

    used_module_ids = {
        str(page.get("module_id")) for page in pages
        if isinstance(page, dict) and page.get("module_id")
    }
    empty_module_ids = module_ids - used_module_ids
    if empty_module_ids:
        errors.append(f"public tutorial contains empty modules: {', '.join(sorted(empty_module_ids))}")

    for index, page in enumerate(pages):
        if not isinstance(page, dict):
            continue
        page_id = str(page.get("page_id", ""))
        prerequisites = set(page.get("prerequisite_ids", [])) if isinstance(page.get("prerequisite_ids"), list) else set()
        unknown = prerequisites - page_ids
        if unknown:
            errors.append(f"tutorial page {index} references unknown prerequisites: {', '.join(sorted(unknown))}")
        if page_id in prerequisites:
            errors.append(f"tutorial page {index} cannot require itself")
        for field in ["previous_page_id", "next_page_id"]:
            target = page.get(field)
            if target not in {None, ""} and target not in page_ids:
                errors.append(f"tutorial page {index} {field} references unknown page")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(page_id: str) -> None:
        if page_id in visiting:
            errors.append(f"tutorial prerequisite cycle detected at {page_id}")
            return
        if page_id in visited or page_id not in page_by_id:
            return
        visiting.add(page_id)
        for dependency in page_by_id[page_id].get("prerequisite_ids", []):
            visit(str(dependency))
        visiting.remove(page_id)
        visited.add(page_id)

    for page_id in page_ids:
        visit(page_id)

    if data.get("default_page_id") not in page_ids:
        errors.append("tutorial default_page_id references unknown page")
    delivered = [page for page in pages if isinstance(page, dict) and page.get("delivery_status") not in {"planned", "outlined", "blocked"}]
    if not delivered:
        errors.append("tutorial site needs at least one delivered page")

    release_scope = data.get("release_scope")
    if not isinstance(release_scope, dict):
        errors.append("tutorial release_scope must be an object")
    else:
        require_fields(release_scope, ["mode", "promised_page_ids", "catalog_complete", "validated_at"], "tutorial release_scope", errors)
        mode = release_scope.get("mode")
        promised_ids = release_scope.get("promised_page_ids")
        if mode not in {"pilot-path", "complete-catalog"}:
            errors.append("tutorial release_scope mode must be pilot-path or complete-catalog")
        if not isinstance(promised_ids, list) or not promised_ids:
            errors.append("tutorial release_scope promised_page_ids must be a non-empty list")
            promised_ids = []
        promised_set = {str(page_id) for page_id in promised_ids}
        if len(promised_set) != len(promised_ids):
            errors.append("tutorial release_scope promised_page_ids must be unique")
        if promised_set != page_ids:
            errors.append("tutorial release_scope promised_page_ids must equal the public page set")
        unknown_promised = promised_set - page_ids
        if unknown_promised:
            errors.append(f"tutorial release_scope references unknown pages: {', '.join(sorted(unknown_promised))}")
        incomplete_promised = {
            page_id for page_id in promised_set
            if page_id in page_by_id and page_by_id[page_id].get("delivery_status") in {"planned", "outlined", "blocked"}
        }
        if incomplete_promised:
            errors.append(f"tutorial release_scope promises incomplete pages: {', '.join(sorted(incomplete_promised))}")
        for page_id in promised_set:
            if page_id not in page_by_id:
                continue
            validate_topic_research(root, page_id, errors)
            validate_page_projection_ledger(root, page_by_id[page_id], errors)
            for dependency in page_by_id[page_id].get("prerequisite_ids", []):
                dependency_page = page_by_id.get(str(dependency))
                if dependency_page and dependency_page.get("delivery_status") in {"planned", "outlined", "blocked"}:
                    errors.append(f"tutorial promised page {page_id} has incomplete prerequisite {dependency}")
        if mode == "complete-catalog":
            if len(modules) < 4:
                errors.append("complete-catalog tutorial needs at least 4 modules")
            if len(pages) < 15:
                errors.append("complete-catalog tutorial needs at least 15 pages")
            if release_scope.get("catalog_complete") is not True:
                errors.append("complete-catalog release_scope must set catalog_complete=true")
            if promised_set != page_ids:
                errors.append("complete-catalog promised_page_ids must equal the full tutorial catalog")
            incomplete_catalog = {
                page_id for page_id, page in page_by_id.items()
                if page.get("delivery_status") in {"planned", "outlined", "blocked"}
            }
            if incomplete_catalog:
                errors.append(f"complete-catalog contains incomplete pages: {', '.join(sorted(incomplete_catalog))}")
        else:
            if len(pages) < 8:
                errors.append("pilot-path public tutorial needs at least 8 delivered pages")
            if release_scope.get("catalog_complete") is not False:
                errors.append("pilot-path release_scope must set catalog_complete=false")

    html = html_path.read_text(encoding="utf-8")
    if len(html.strip()) < 8000:
        errors.append("tutorial/index.html is too thin to provide the learning experience")
    for marker in ["id=\"course-nav\"", "id=\"tutorial-content\"", "id=\"page-toc\"", "id=\"tutorial-search\"", "id=\"progress-bar\"", "COURSE_DATA"]:
        if marker not in html:
            errors.append(f"tutorial/index.html missing viewer marker: {marker}")
    lowered = html.lower()
    # Inspect the actual element attributes only. Embedded COURSE_DATA and
    # learner text may legitimately contain documentation URLs; those are not
    # remote runtime dependencies.
    if re.search(r"<script\b[^>]*\bsrc=[\"']https?://", lowered) or re.search(
        r"<link\b[^>]*\bhref=[\"']https?://", lowered
    ):
        errors.append("tutorial/index.html must not depend on remote scripts or styles")
    if re.search(r'"(?:status|delivery_status)"\s*:\s*"(?:planned|outlined|blocked)"', html):
        errors.append("tutorial/index.html exposes incomplete public pages")
    if any(marker in html for marker in ["仅保留知识位置", "本页尚未开发", "本页尚未通过逐题研究"]):
        errors.append("tutorial/index.html exposes incomplete-page placeholders")
    for page_id in page_ids:
        if page_id not in html:
            errors.append(f"tutorial/index.html does not embed page: {page_id}")


def validate_solution_architecture(root: Path, errors: list[str]) -> None:
    """Prove that learner-facing tracks form complete, traceable professional solutions."""
    overview_path = root / "solution-architecture.md"
    if overview_path.is_file():
        overview = overview_path.read_text(encoding="utf-8")
        if len(overview.strip()) < 1800:
            errors.append("solution-architecture.md is too thin for a complete solution review")
        for marker in SOLUTION_ARCHITECTURE_MARKERS:
            if marker not in overview:
                errors.append(f"solution-architecture.md missing marker: {marker}")

    contract_path = root / "research/solution-architecture.json"
    if not contract_path.is_file():
        return
    contract = load_json(contract_path, errors)
    if not isinstance(contract, dict):
        return
    require_fields(contract, ["schema_version", "profession_id", "as_of", "solution_units"], "solution architecture", errors)
    units = contract.get("solution_units")
    if not isinstance(units, list) or not units:
        errors.append("solution architecture needs at least one solution unit")
        return

    tutorial = load_json(root / "tutorial/tutorial-site.json", errors) if (root / "tutorial/tutorial-site.json").is_file() else {}
    scenarios = load_json(root / "research/scenarios.json", errors) if (root / "research/scenarios.json").is_file() else {}
    curriculum = load_json(root / "curriculum.json", errors) if (root / "curriculum.json").is_file() else {}
    coverage_rows, _ = load_csv(root / "research/curriculum-coverage-matrix.csv", errors) if (root / "research/curriculum-coverage-matrix.csv").is_file() else ([], [])
    ledger_rows, _ = load_csv(root / "research/source-ledger.csv", errors) if (root / "research/source-ledger.csv").is_file() else ([], [])
    source_ids = {row.get("id", "").strip() for row in ledger_rows if row.get("id", "").strip()}
    public_page_ids = {
        str(page.get("page_id")) for page in tutorial.get("pages", [])
        if isinstance(page, dict) and page.get("page_id")
    } if isinstance(tutorial, dict) else set()
    scenario_ids = {
        str(item.get("scenario_id")) for item in scenarios.get("scenarios", [])
        if isinstance(item, dict) and item.get("scenario_id")
    } if isinstance(scenarios, dict) else set()
    course_ids = {
        str(item.get("course_id")) for item in curriculum.get("courses", [])
        if isinstance(item, dict) and item.get("course_id")
    } if isinstance(curriculum, dict) else set()
    coverage_ids = {row.get("cell_id", "").strip() for row in coverage_rows if row.get("cell_id", "").strip()}

    mapped_public_pages: set[str] = set()
    solution_ids: set[str] = set()
    for index, unit in enumerate(units):
        label = f"solution unit {index}"
        if not isinstance(unit, dict):
            errors.append(f"{label} is not an object")
            continue
        require_fields(unit, [
            "solution_id", "title", "business_outcome", "failure_cost", "owner", "reviewers",
            "scenario_ids", "page_ids", "course_ids", "design_status", "execution_status",
            "practitioner_review_status", "publication_status", "dimensions", "architecture_views",
            "decisions", "traceability", "execution_receipts", "acceptance_gates", "residual_risks",
        ], label, errors)
        solution_id = str(unit.get("solution_id", ""))
        if solution_id in solution_ids:
            errors.append(f"duplicate solution_id: {solution_id}")
        solution_ids.add(solution_id)

        design_status = unit.get("design_status")
        execution_status = unit.get("execution_status")
        review_status = unit.get("practitioner_review_status")
        publication_status = unit.get("publication_status")
        if design_status not in SOLUTION_DESIGN_STATUSES:
            errors.append(f"{label} has invalid design_status")
        if execution_status not in SOLUTION_EXECUTION_STATUSES:
            errors.append(f"{label} has invalid execution_status")
        if review_status not in SOLUTION_REVIEW_STATUSES:
            errors.append(f"{label} has invalid practitioner_review_status")
        if publication_status not in SOLUTION_PUBLICATION_STATUSES:
            errors.append(f"{label} has invalid publication_status")
        if not isinstance(unit.get("reviewers"), list) or not unit.get("reviewers"):
            errors.append(f"{label} needs named reviewers")

        unit_page_ids = {str(item) for item in unit.get("page_ids", []) if str(item)} if isinstance(unit.get("page_ids"), list) else set()
        unit_scenario_ids = {str(item) for item in unit.get("scenario_ids", []) if str(item)} if isinstance(unit.get("scenario_ids"), list) else set()
        unit_course_ids = {str(item) for item in unit.get("course_ids", []) if str(item)} if isinstance(unit.get("course_ids"), list) else set()
        unknown_pages = unit_page_ids - public_page_ids
        unknown_scenarios = unit_scenario_ids - scenario_ids
        unknown_courses = unit_course_ids - course_ids
        if unknown_pages:
            errors.append(f"{label} references unknown page IDs: {', '.join(sorted(unknown_pages))}")
        if unknown_scenarios:
            errors.append(f"{label} references unknown scenario IDs: {', '.join(sorted(unknown_scenarios))}")
        if unknown_courses:
            errors.append(f"{label} references unknown course IDs: {', '.join(sorted(unknown_courses))}")
        # Local learner visibility is a coverage claim, not a practitioner or
        # external-publication claim. Every visible page must belong to a
        # traced solution unit regardless of publication maturity; the stricter
        # pilot/public gates below remain unchanged.
        mapped_public_pages.update(unit_page_ids)

        dimensions = unit.get("dimensions")
        seen_dimensions: set[str] = set()
        incomplete_dimensions: set[str] = set()
        dimension_evidence_refs: set[str] = set()
        if not isinstance(dimensions, list):
            errors.append(f"{label} dimensions must be a list")
            dimensions = []
        for dimension_index, dimension in enumerate(dimensions):
            dimension_label = f"{label} dimension {dimension_index}"
            if not isinstance(dimension, dict):
                errors.append(f"{dimension_label} is not an object")
                continue
            require_fields(dimension, ["dimension_id", "status", "question", "decision", "artifact_refs", "evidence_refs", "reviewer"], dimension_label, errors)
            dimension_id = str(dimension.get("dimension_id", ""))
            if dimension_id in seen_dimensions:
                errors.append(f"{label} has duplicate dimension: {dimension_id}")
            seen_dimensions.add(dimension_id)
            status = dimension.get("status")
            if status not in SOLUTION_DIMENSION_STATUSES:
                errors.append(f"{dimension_label} has invalid status")
            if status in {"partial", "gap"}:
                incomplete_dimensions.add(dimension_id)
            if status == "not-applicable" and (not dimension.get("rationale") or not dimension.get("reviewer")):
                errors.append(f"{dimension_label} not-applicable needs rationale and reviewer")
            if status == "complete":
                if len(str(dimension.get("question", "")).strip()) < 20 or len(str(dimension.get("decision", "")).strip()) < 20:
                    errors.append(f"{dimension_label} complete assessment is too thin")
                if not isinstance(dimension.get("artifact_refs"), list) or not dimension.get("artifact_refs"):
                    errors.append(f"{dimension_label} complete assessment needs artifact_refs")
                else:
                    for artifact_ref in map(str, dimension.get("artifact_refs", [])):
                        artifact_path = (root / artifact_ref).resolve()
                        try:
                            artifact_path.relative_to(root.resolve())
                        except ValueError:
                            errors.append(f"{dimension_label} artifact_ref escapes package root")
                        else:
                            if not artifact_path.is_file():
                                errors.append(f"{dimension_label} references missing artifact: {artifact_ref}")
                if not isinstance(dimension.get("evidence_refs"), list) or not dimension.get("evidence_refs"):
                    errors.append(f"{dimension_label} complete assessment needs evidence_refs")
                else:
                    dimension_evidence_refs.update(map(str, dimension.get("evidence_refs", [])))
        missing_dimensions = SOLUTION_DIMENSION_IDS - seen_dimensions
        extra_dimensions = seen_dimensions - SOLUTION_DIMENSION_IDS
        if missing_dimensions:
            errors.append(f"{label} misses mandatory solution dimensions: {', '.join(sorted(missing_dimensions))}")
        if extra_dimensions:
            errors.append(f"{label} has unknown solution dimensions: {', '.join(sorted(extra_dimensions))}")

        decisions = unit.get("decisions")
        decision_ids: set[str] = set()
        accepted_decisions = 0
        if not isinstance(decisions, list) or len(decisions) < 2:
            errors.append(f"{label} needs at least two explicit decisions")
            decisions = []
        for decision_index, decision in enumerate(decisions):
            decision_label = f"{label} decision {decision_index}"
            if not isinstance(decision, dict):
                errors.append(f"{decision_label} is not an object")
                continue
            require_fields(decision, ["decision_id", "context", "options", "choice", "tradeoffs", "owner", "status", "revisit_evidence"], decision_label, errors)
            decision_id = str(decision.get("decision_id", ""))
            if decision_id in decision_ids:
                errors.append(f"{label} has duplicate decision_id: {decision_id}")
            decision_ids.add(decision_id)
            if decision.get("status") == "accepted":
                accepted_decisions += 1
            elif decision.get("status") not in {"proposed", "rejected", "superseded"}:
                errors.append(f"{decision_label} has invalid status")
            if not isinstance(decision.get("options"), list) or len(decision.get("options", [])) < 2:
                errors.append(f"{decision_label} needs at least two options")

        views = unit.get("architecture_views")
        seen_view_kinds: set[str] = set()
        if not isinstance(views, list):
            errors.append(f"{label} architecture_views must be a list")
            views = []
        for view_index, view in enumerate(views):
            view_label = f"{label} architecture view {view_index}"
            if not isinstance(view, dict):
                errors.append(f"{view_label} is not an object")
                continue
            require_fields(view, ["view_id", "kind", "title", "purpose", "artifact_ref", "nodes", "edges", "boundary", "failure_path", "evidence_points", "decision_ids"], view_label, errors)
            kind = str(view.get("kind", ""))
            if kind in seen_view_kinds:
                errors.append(f"{label} has duplicate architecture view kind: {kind}")
            seen_view_kinds.add(kind)
            if kind not in SOLUTION_VIEW_KINDS:
                errors.append(f"{view_label} has invalid kind")
            if not isinstance(view.get("nodes"), list) or len(view.get("nodes", [])) < 5:
                errors.append(f"{view_label} needs at least five meaningful nodes")
            if not isinstance(view.get("edges"), list) or len(view.get("edges", [])) < 4:
                errors.append(f"{view_label} needs at least four explicit edges")
            unknown_decisions = set(map(str, view.get("decision_ids", []))) - decision_ids if isinstance(view.get("decision_ids"), list) else set()
            if unknown_decisions:
                errors.append(f"{view_label} references unknown decisions: {', '.join(sorted(unknown_decisions))}")
            artifact_ref = str(view.get("artifact_ref", ""))
            artifact_path = (root / artifact_ref).resolve()
            try:
                artifact_path.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{view_label} artifact_ref escapes package root")
            else:
                if not artifact_path.is_file():
                    errors.append(f"{view_label} references missing artifact: {artifact_ref}")
                else:
                    artifact_text = artifact_path.read_text(encoding="utf-8", errors="replace")
                    if len(artifact_text.strip()) < 250:
                        errors.append(f"{view_label} artifact is too thin: {artifact_ref}")
                    if not any(marker in artifact_text for marker in ["```mermaid", "@startuml", "digraph ", "```d2"]):
                        errors.append(f"{view_label} artifact lacks a machine-renderable diagram: {artifact_ref}")
        missing_views = SOLUTION_VIEW_KINDS - seen_view_kinds
        if missing_views:
            errors.append(f"{label} misses mandatory architecture views: {', '.join(sorted(missing_views))}")

        receipts = unit.get("execution_receipts")
        receipt_ids: set[str] = set()
        receipt_kinds: set[str] = set()
        if not isinstance(receipts, list):
            errors.append(f"{label} execution_receipts must be a list")
            receipts = []
        for receipt_index, receipt in enumerate(receipts):
            receipt_label = f"{label} execution receipt {receipt_index}"
            if not isinstance(receipt, dict):
                errors.append(f"{receipt_label} is not an object")
                continue
            require_fields(receipt, ["receipt_id", "kind", "artifact_ref", "status", "limitations", "reviewer"], receipt_label, errors)
            receipt_id = str(receipt.get("receipt_id", ""))
            receipt_ids.add(receipt_id)
            receipt_kinds.add(str(receipt.get("kind", "")))
            receipt_ref = str(receipt.get("artifact_ref", ""))
            receipt_path = (root / receipt_ref).resolve()
            try:
                receipt_path.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{receipt_label} artifact_ref escapes package root")
            else:
                if not receipt_path.is_file():
                    errors.append(f"{receipt_label} references missing artifact: {receipt_ref}")
                elif receipt_path.suffix != ".json":
                    errors.append(f"{receipt_label} must reference structured JSON evidence")
                else:
                    receipt_data = load_json(receipt_path, errors)
                    if isinstance(receipt_data, dict):
                        require_fields(receipt_data, [
                            "receipt_id", "solution_id", "scenario_id", "environment", "run_at", "tools",
                            "command", "working_directory", "input_hashes", "output_hashes", "assertions",
                            "expected_verdict", "actual_verdict", "limitations", "reviewer",
                        ], f"{receipt_label} payload", errors)
                        if str(receipt_data.get("solution_id", "")) != solution_id:
                            errors.append(f"{receipt_label} payload belongs to another solution")
                        if str(receipt_data.get("receipt_id", "")) != receipt_id:
                            errors.append(f"{receipt_label} payload receipt_id does not match contract")
                        if not isinstance(receipt_data.get("assertions"), list) or not receipt_data.get("assertions"):
                            errors.append(f"{receipt_label} payload needs observed assertions")
                        if receipt.get("kind") == "fixture":
                            require_fields(receipt_data, ["failure_injection", "red_evidence", "repair", "green_evidence"], f"{receipt_label} fixture payload", errors)
        if execution_status in SOLUTION_EXECUTION_STATUSES[2:] and not receipts:
            errors.append(f"{label} claims {execution_status} without execution receipts")
        if execution_status in SOLUTION_EXECUTION_STATUSES[3:] and not receipt_kinds.intersection({"integration", "live", "production"}):
            errors.append(f"{label} claims {execution_status} without integration or stronger receipt")
        for evidence_ref in dimension_evidence_refs:
            if evidence_ref in receipt_ids or evidence_ref in source_ids:
                continue
            evidence_path = (root / evidence_ref).resolve()
            try:
                evidence_path.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{label} dimension evidence_ref escapes package root: {evidence_ref}")
            else:
                if not evidence_path.is_file():
                    errors.append(f"{label} dimension evidence_ref is unknown or missing: {evidence_ref}")

        traces = unit.get("traceability")
        traced_pages: set[str] = set()
        if not isinstance(traces, list) or not traces:
            errors.append(f"{label} needs traceability rows")
            traces = []
        trace_fields = [
            "coverage_cell_id", "topic_id", "page_id", "scenario_id", "artifact_ref", "command_ref",
            "execution_receipt_ref", "assessment_ref", "human_gate",
        ]
        for trace_index, trace in enumerate(traces):
            trace_label = f"{label} trace {trace_index}"
            if not isinstance(trace, dict):
                errors.append(f"{trace_label} is not an object")
                continue
            require_fields(trace, trace_fields, trace_label, errors)
            page_id = str(trace.get("page_id", ""))
            traced_pages.add(page_id)
            if page_id not in unit_page_ids:
                errors.append(f"{trace_label} page_id is not owned by its solution unit")
            if str(trace.get("scenario_id", "")) not in unit_scenario_ids:
                errors.append(f"{trace_label} scenario_id is not owned by its solution unit")
            if str(trace.get("coverage_cell_id", "")) not in coverage_ids:
                errors.append(f"{trace_label} references unknown coverage_cell_id")
            if str(trace.get("execution_receipt_ref", "")) not in receipt_ids:
                if not (execution_status in {"not-run", "desk-researched"} and str(trace.get("execution_receipt_ref", "")) == "NOT_RUN"):
                    errors.append(f"{trace_label} references unknown execution receipt")
            for field in ["artifact_ref", "command_ref", "assessment_ref"]:
                relative = str(trace.get(field, ""))
                target = (root / relative).resolve()
                try:
                    target.relative_to(root.resolve())
                except ValueError:
                    errors.append(f"{trace_label} {field} escapes package root")
                else:
                    if not target.is_file():
                        errors.append(f"{trace_label} references missing {field}: {relative}")
        missing_trace_pages = unit_page_ids - traced_pages
        if missing_trace_pages:
            errors.append(f"{label} has public pages without end-to-end traceability: {', '.join(sorted(missing_trace_pages))}")

        gates = unit.get("acceptance_gates")
        required_gate_kinds = {"design", "functional", "security", "performance", "reliability", "operations", "rollback", "learner-transfer"}
        gate_kinds: set[str] = set()
        failed_gates = False
        if not isinstance(gates, list):
            errors.append(f"{label} acceptance_gates must be a list")
            gates = []
        for gate_index, gate in enumerate(gates):
            gate_label = f"{label} acceptance gate {gate_index}"
            if not isinstance(gate, dict):
                errors.append(f"{gate_label} is not an object")
                continue
            require_fields(gate, ["gate_id", "gate_kind", "criterion", "evidence_ref", "owner", "status"], gate_label, errors)
            gate_kinds.add(str(gate.get("gate_kind", "")))
            if gate.get("status") not in {"pass", "conditional", "fail", "unknown"}:
                errors.append(f"{gate_label} has invalid status")
            if gate.get("status") != "pass":
                failed_gates = True
            evidence_ref = str(gate.get("evidence_ref", ""))
            if evidence_ref not in receipt_ids and evidence_ref not in source_ids:
                evidence_path = (root / evidence_ref).resolve()
                try:
                    evidence_path.relative_to(root.resolve())
                except ValueError:
                    errors.append(f"{gate_label} evidence_ref escapes package root")
                else:
                    if not evidence_path.is_file():
                        errors.append(f"{gate_label} references missing evidence: {evidence_ref}")
        missing_gate_kinds = required_gate_kinds - gate_kinds
        if missing_gate_kinds:
            errors.append(f"{label} misses acceptance gate kinds: {', '.join(sorted(missing_gate_kinds))}")

        risks = unit.get("residual_risks")
        if not isinstance(risks, list) or not risks:
            errors.append(f"{label} needs owned residual risks")
        else:
            for risk_index, risk in enumerate(risks):
                if not isinstance(risk, dict):
                    errors.append(f"{label} residual risk {risk_index} is not an object")
                    continue
                require_fields(risk, ["risk_id", "severity", "trigger", "mitigation", "owner", "status"], f"{label} residual risk {risk_index}", errors)

        if design_status == "complete":
            if missing_dimensions or extra_dimensions or incomplete_dimensions:
                errors.append(f"{label} claims complete design with missing, unknown, partial, or gap dimensions")
            if missing_views or accepted_decisions < 2 or missing_trace_pages or missing_gate_kinds:
                errors.append(f"{label} claims complete design without complete views, accepted decisions, traceability, or gates")
        if publication_status == "pilot":
            execution_rank = SOLUTION_EXECUTION_STATUSES.index(execution_status) if execution_status in SOLUTION_EXECUTION_STATUSES else -1
            review_rank = SOLUTION_REVIEW_STATUSES.index(review_status) if review_status in SOLUTION_REVIEW_STATUSES else -1
            if design_status != "complete" or execution_rank < 2 or review_rank < 1:
                errors.append(f"{label} pilot publication needs complete design, fixture proof, and practitioner review")
        if publication_status == "public":
            execution_rank = SOLUTION_EXECUTION_STATUSES.index(execution_status) if execution_status in SOLUTION_EXECUTION_STATUSES else -1
            if design_status != "complete" or execution_rank < 3 or review_status != "approved" or failed_gates:
                errors.append(f"{label} public publication needs complete design, integration proof, practitioner approval, and passed gates")
        if execution_status == "production-validated" and (review_status != "approved" or "production" not in receipt_kinds):
            errors.append(f"{label} production-validated claim needs practitioner approval and production receipt")

    unmapped_public_pages = public_page_ids - mapped_public_pages
    if unmapped_public_pages:
        errors.append(f"public tutorial pages are not mapped to a traced solution unit: {', '.join(sorted(unmapped_public_pages))}")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"package does not exist: {root}"]
    for name in REQUIRED_ROOT:
        if not (root / name).is_file():
            errors.append(f"missing root file: {name}")
    for relative, markers in REQUIRED_HUMAN_REVIEW.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing human-readable review file: {relative}")
            continue
        review_text = path.read_text(encoding="utf-8")
        if len(review_text.strip()) < 600:
            errors.append(f"human-readable review file is too thin: {relative}")
        for marker in markers:
            if marker not in review_text:
                errors.append(f"human-readable review file {relative} missing marker: {marker}")
    if not (root / "tools/tool-registry.json").is_file():
        errors.append("missing tool registry: tools/tool-registry.json")
    validate_research(root, errors)
    validate_capability_contract(root, errors)
    validate_professional_capability_and_evidence_contract(root, errors)
    validate_source_assimilation_contract(root, errors)
    validate_source_semantic_projection_contract(root, errors)
    validate_learner_usability_and_reuse_contract(root, errors)
    validate_visual_sequence_contract(root, errors)
    validate_software_testing_adapter_contract(root, errors)
    validate_status_supersession_contract(root, errors)
    validate_profession_knowledge_system(root, errors)
    validate_curriculum_gap_audit(root, errors)
    validate_tasks_and_curriculum(root, errors)
    validate_courses(root, errors)
    validate_tutorial(root, errors)
    validate_catalog_publication_contract(root, errors)
    validate_solution_architecture(root, errors)
    report = root / "validation-report.md"
    if report.is_file():
        text = report.read_text(encoding="utf-8")
        for marker in ["## Evidence", "## Inference", "## Unknown", "## Professional utility verdict", "## Not tested"]:
            if marker not in text:
                errors.append(f"validation report missing marker: {marker}")
    return errors


def verify_source_urls(root: Path, source_ids: set[str] | None = None) -> list[str]:
    """Re-open ledger URLs so a syntactically valid but nonexistent source cannot pass live validation."""
    errors: list[str] = []
    ledger = root / "research/source-ledger.csv"
    if not ledger.is_file():
        return ["cannot verify source URLs without research/source-ledger.csv"]
    rows, _ = load_csv(ledger, errors)
    targets = [row for row in rows if source_ids is None or row.get("id", "").strip() in source_ids]
    if source_ids is not None:
        found = {row.get("id", "").strip() for row in targets}
        missing = source_ids - found
        if missing:
            errors.append(f"cannot live-verify unknown source IDs: {', '.join(sorted(missing))}")
    with ThreadPoolExecutor(max_workers=min(8, max(1, len(targets)))) as pool:
        futures = {pool.submit(fetch_url_status, row.get("url", "")): row for row in targets}
        for future in as_completed(futures):
            row = futures[future]
            source_id = row.get("id", "").strip()
            try:
                status, sample_size, detail = future.result()
            except Exception as exc:
                errors.append(f"source {source_id} live verification crashed: {exc}")
                continue
            if status is None or status < 200 or status >= 400:
                errors.append(f"source {source_id} failed live URL verification: status={status} detail={detail}")
            elif sample_size < 64:
                errors.append(f"source {source_id} live URL returned too little content to audit: {sample_size} bytes")
    return errors


def run_labs(root: Path) -> list[str]:
    """Execute structured validation commands only when explicitly requested."""
    errors: list[str] = []
    for course in sorted(path for path in (root / "courses").iterdir() if path.is_dir()):
        manifest_path = course / "course-manifest.json"
        if not manifest_path.is_file():
            continue
        manifest = load_json(manifest_path, errors)
        if not isinstance(manifest, dict):
            continue
        workdir = (course / str(manifest.get("validation_workdir", ""))).resolve()
        try:
            workdir.relative_to(course.resolve())
        except ValueError:
            errors.append(f"{course.name} validation_workdir escapes course directory")
            continue
        if not workdir.is_dir():
            errors.append(f"{course.name} validation_workdir does not exist: {workdir}")
            continue
        for step in manifest.get("validation_steps", []):
            command = step.get("command", [])
            if not isinstance(command, list) or not command:
                continue
            try:
                result = subprocess.run(command, cwd=workdir, text=True, capture_output=True, timeout=120, check=False)
            except Exception as exc:
                errors.append(f"{course.name} runtime step {step.get('name')} could not run: {exc}")
                continue
            expected = step.get("expected_exit_code")
            print(f"LAB {course.name} :: {step.get('name')} :: exit {result.returncode} (expected {expected})")
            if result.stdout.strip():
                print(result.stdout.strip())
            if result.stderr.strip():
                print(result.stderr.strip(), file=sys.stderr)
            if result.returncode != expected:
                errors.append(f"{course.name} runtime step {step.get('name')} exited {result.returncode}, expected {expected}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--run-labs", action="store_true", help="execute manifest validation_steps after static gates pass")
    parser.add_argument("--verify-sources", action="store_true", help="live re-open every source-ledger URL; required before current-source publication")
    args = parser.parse_args()
    errors = validate(args.package)
    if not errors and args.run_labs:
        errors.extend(run_labs(args.package))
    if not errors and args.verify_sources:
        errors.extend(verify_source_urls(args.package))
    if errors:
        print("AI-native career package invalid:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("AI-native career package valid!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
