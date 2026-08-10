#!/usr/bin/env python3
"""Fail-closed validator for AI-native profession course packages."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


REQUIRED_ROOT = [
    "career-profile.md", "tasks.json", "curriculum.json", "course-map.md",
    "profession-reality-map.md", "industry-framework.md", "learning-architecture.md", "curriculum-gap-analysis.md", "validation-report.md", "update-log.md",
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
}
REQUIRED_TUTORIAL_MARKDOWN = {
    "tutorial/README.md": ["## 如何学习", "## 教程结构", "## 当前完成度"],
    "tutorial/course-tree.md": ["## 学习路线", "## 模块", "## 页面状态"],
    "tutorial/page-template.md": ["## 页面顶部", "## 通俗解释", "## 自己动手", "## 完成检查", "## 证据边界"],
}
REQUIRED_RESEARCH = [
    "source-ledger.csv", "search-plan.json", "search-log.csv", "technology-radar.json",
    "channel-coverage.json", "profession-reality-map.json", "profession-map.json", "profession-knowledge-system.json", "github-artifacts.csv", "job-signals.csv",
    "learner-signals.csv", "scenarios.json", "evidence-matrix.md", "competitor-matrix.csv",
    "ai-capability-map.md", "competency-transition-map.json", "curriculum-coverage-matrix.csv",
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


def require_fields(record: dict[str, Any], fields: list[str], label: str, errors: list[str]) -> None:
    for field in fields:
        value = record.get(field)
        if value is None or value == "" or value == []:
            errors.append(f"{label} missing field: {field}")


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
            if manifest.get("ai_lane") not in AI_LANES:
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
        "page_id", "slug", "module_id", "title", "page_type", "level", "order",
        "scenario_ids", "learner_result", "artifact", "keywords",
        "evidence_status", "delivery_status", "updated_at", "source_ids",
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
            package_path = root / "research" / "topics" / page_id / "research-package.md"
            if not package_path.is_file():
                errors.append(f"tutorial promised page {page_id} missing per-topic research package")
            else:
                package_text = package_path.read_text(encoding="utf-8")
                for marker in ["## Research brief", "## Source pack", "## Evidence synthesis", "## Engineering blueprint", "## Manuscript map", "## Editorial review", "## Validation"]:
                    if marker not in package_text:
                        errors.append(f"tutorial promised page {page_id} research package missing marker: {marker}")
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
    if "<script src=\"http" in lowered or "<link" in lowered and "href=\"http" in lowered:
        errors.append("tutorial/index.html must not depend on remote scripts or styles")
    if re.search(r'"(?:status|delivery_status)"\s*:\s*"(?:planned|outlined|blocked)"', html):
        errors.append("tutorial/index.html exposes incomplete public pages")
    if any(marker in html for marker in ["仅保留知识位置", "本页尚未开发", "本页尚未通过逐题研究"]):
        errors.append("tutorial/index.html exposes incomplete-page placeholders")
    for page_id in page_ids:
        if page_id not in html:
            errors.append(f"tutorial/index.html does not embed page: {page_id}")


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
    validate_profession_knowledge_system(root, errors)
    validate_curriculum_gap_audit(root, errors)
    validate_tasks_and_curriculum(root, errors)
    validate_courses(root, errors)
    validate_tutorial(root, errors)
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
