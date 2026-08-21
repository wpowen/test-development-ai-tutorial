#!/usr/bin/env python3
"""Create an honest, incomplete shell for an AI-native career course package."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


LEDGER_COLUMNS = ["id", "title", "creator", "source_type", "platform", "language", "year", "url", "access_date", "evidence_tier", "publisher_group", "source_family_id", "channel_ids", "relevance", "credibility", "used_for", "limitations"]
COMPETITOR_COLUMNS = ["id", "platform", "offering", "audience", "promise", "ai_lane", "modules", "hands_on_artifact", "execution_proof", "assessment", "freshness", "commercial_model", "url", "access_date", "gap", "claim_status"]
SEARCH_LOG_COLUMNS = ["id", "query", "language", "research_lane", "surface_attempt_id", "search_surface", "run_at", "result_count", "selected_source_ids", "opened_urls", "exclusion_notes", "status"]
COVERAGE_COLUMNS = ["cell_id", "profession_domain_id", "layer_kind", "specialization_kind", "learner_level", "topic", "required_by_source_ids", "competitor_ids", "course_ids", "learner_artifact", "exit_assessment", "evidence_status", "coverage_status", "priority", "gap_reason", "decision"]
GITHUB_COLUMNS = ["artifact_id", "source_id", "repo_url", "commit_or_tag", "license", "last_commit_at", "release_or_commit_url", "issues_url", "ci_url", "setup_command", "smoke_command", "run_status", "run_at", "exit_code", "evidence_path", "selected_for_lab", "limitations"]
JOB_COLUMNS = ["job_id", "source_id", "employer", "title", "location", "posted_or_observed_at", "original_url", "task_terms", "ai_terms", "duplicate_group", "claim_status", "limitations"]
LEARNER_COLUMNS = ["signal_id", "source_id", "platform", "content_url", "signal_type", "direct_observation", "learner_question", "requested_outcome", "pain_language", "engagement_metric", "metric_scope", "observed_at", "claim_status", "limitations"]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--career-slug", required=True)
    parser.add_argument("--career-name", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.output
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty directory: {root}")
    root.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()

    write(root / "career-profile.md", f"# {args.career_name} × AI\n\nStatus: scaffold; research not run.\n\n## Role reality\n\nTODO\n\n## AI transformation thesis\n\nTODO\n\n## Boundaries\n\nTODO")
    write(root / "profession-reality-map.md", f"# {args.career_name} profession reality map\n\nStatus: BLOCKED. Role variants, rhythms, lifecycle, artifacts, dependencies, decision rights, pain, promotion signals, and AI opportunities have not been researched.")
    write(root / "course-map.md", f"# {args.career_name} × AI course map\n\nNo course has passed AI-centrality or utility gates.")
    write(root / "industry-framework.md", f"""# {args.career_name} profession knowledge system

Status: scaffold; profession completeness research not run.

## End-to-end lifecycle

TODO

## Specialization families

TODO

## System and work-object classes

TODO

## Quality and outcome attributes

TODO

## AI transformation

TODO

## Role and career evolution

TODO

## Coverage verdict

FAIL: not researched.

## Critical gaps

All dimensions remain unknown.
""")
    write(root / "learning-architecture.md", f"""# {args.career_name} × AI learning architecture

Status: scaffold; research not run.

## Learner transformation

TODO

## Professional baseline

TODO

## AI foundations

TODO

## Capability transition matrix

TODO

## Learning stages

TODO

## Specialization tracks

TODO

## Benchmark literacy

TODO

## Exit gates

TODO
""")
    write(root / "curriculum-gap-analysis.md", f"""# {args.career_name} × AI curriculum gap analysis

Status: scaffold; the six-system audit has not run.

## Research corpus

TODO

## Industry body of knowledge

TODO

## Real work and practitioner evidence

TODO

## Existing course supply

TODO

## AI technology and benchmark frontier

TODO

## Coverage matrix

TODO

## Missing and overrepresented topics

TODO

## Expert review

### Profession veteran

TODO

### AI systems engineer

TODO

### Evaluation and quality expert

TODO

### Curriculum designer

TODO

### Market and learner researcher

TODO

### Adversarial critic

TODO

## Curriculum decisions

TODO

## Remaining unknowns

Research and review have not run.
""")
    write(root / "solution-architecture.md", f"""# {args.career_name} × AI complete solution architecture

Status: GAP. No solution unit has passed the complete-solution contract.

## Solution units

None designed.

## Scope and boundaries

Unknown until profession and scenario research are complete.

## Architecture views

Context, building-block, runtime, deployment, data-flow, and security trust-boundary views are missing.

## Decisions and trade-offs

No architecture decision has been accepted.

## Traceability

No requirement-to-page-to-execution trace exists.

## Acceptance gates

Design, functional, security, performance, reliability, operations, rollback, and learner-transfer gates are unknown.

## Maturity and evidence

Design: gap. Execution: not-run. Practitioner review: not-reviewed. Publication: internal.

## Risks and unknowns

All implementation, operation, evidence, ownership, and adoption risks remain open.
""")
    write(root / "research/evidence-matrix.md", "# Evidence matrix\n\n## Evidence\n\nNone.\n\n## Competitor observations\n\nNone.\n\n## Vendor claims\n\nNone.\n\n## Inference\n\nNone.\n\n## Unknown\n\nResearch not run.")
    write(root / "research/ai-capability-map.md", "# AI capability map\n\n- use-ai-for-work: TODO\n- test-ai-systems: TODO\n- agentize-work: TODO\n- build-ai-quality-system: TODO")
    for path, columns in [
        (root / "research/source-ledger.csv", LEDGER_COLUMNS),
        (root / "research/competitor-matrix.csv", COMPETITOR_COLUMNS),
        (root / "research/search-log.csv", SEARCH_LOG_COLUMNS),
        (root / "research/curriculum-coverage-matrix.csv", COVERAGE_COLUMNS),
        (root / "research/github-artifacts.csv", GITHUB_COLUMNS),
        (root / "research/job-signals.csv", JOB_COLUMNS),
        (root / "research/learner-signals.csv", LEARNER_COLUMNS),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            csv.writer(handle).writerow(columns)
    write(root / "research/search-plan.json", json.dumps({
        "profession": args.career_slug,
        "generated_at": today,
        "research_question": f"How AI changes {args.career_name}",
        "freshness_required": True,
        "run_scope": "full",
        "available_surfaces": [],
        "query_families": [],
        "freshness_policy": [],
        "stop_conditions": ["BLOCKED-FRESHNESS"],
        "run_status": "planned",
    }, ensure_ascii=False, indent=2))
    write(root / "research/technology-radar.json", json.dumps({"profession": args.career_slug, "technologies": []}, ensure_ascii=False, indent=2))
    write(root / "research/channel-coverage.json", json.dumps({"profession": args.career_slug, "generated_at": today, "channels": []}, ensure_ascii=False, indent=2))
    write(root / "research/profession-reality-map.json", json.dumps({
        "profession_id": args.career_slug, "as_of": today, "review_status": "blocked",
        "role_variants": [], "work_rhythms": [], "workflow_stages": [], "dependencies": [],
        "artifacts": [], "performance_and_promotion": {}, "pain_points": [], "information_barriers": [],
        "ai_opportunities": [], "beginner_reuse_pack": {}, "source_ids": [],
    }, ensure_ascii=False, indent=2))
    write(root / "research/profession-map.json", json.dumps({
        "profession_id": args.career_slug, "canonical_name": args.career_name, "taxonomy": [],
        "as_of": today, "role_variants": [], "lifecycle": [], "work_domains": [],
    }, ensure_ascii=False, indent=2))
    write(root / "research/scenarios.json", json.dumps({"profession": args.career_slug, "scenarios": []}, ensure_ascii=False, indent=2))
    write(root / "research/solution-architecture.json", json.dumps({
        "schema_version": "1.0", "profession_id": args.career_slug, "as_of": today, "solution_units": []
    }, ensure_ascii=False, indent=2))
    write(root / "research/capability-declarations.json", json.dumps({
        "schema_version": "1.0", "capabilities": []
    }, ensure_ascii=False, indent=2))
    write(root / "research/capability-profiles.json", json.dumps({
        "schema_version": "1.0", "pages": []
    }, ensure_ascii=False, indent=2))
    write(root / "research/professional-evidence.json", json.dumps({
        "schema_version": "1.0", "pages": []
    }, ensure_ascii=False, indent=2))
    write(root / "research/status-registry.json", json.dumps({
        "schema_version": "1.0", "records": []
    }, ensure_ascii=False, indent=2))
    write(root / "research/competency-transition-map.json", json.dumps({
        "profession_id": args.career_slug,
        "architecture_profile": "ai-enabled-practitioner",
        "audience": "TODO",
        "as_of": today,
        "professional_baseline": {},
        "ai_foundations": {},
        "transition_matrix": [],
        "learning_stages": [],
        "specialization_tracks": [],
        "source_ids": [],
    }, ensure_ascii=False, indent=2))
    write(root / "research/profession-knowledge-system.json", json.dumps({
        "profession_id": args.career_slug,
        "as_of": today,
        "lifecycle_stages": [],
        "specialization_families": [],
        "system_classes": [],
        "outcome_attributes": [],
        "role_evolution": [],
        "coverage_cells": [],
        "critical_gaps": [{
            "gap_id": "scaffold-not-researched",
            "priority": "critical",
            "description": "Profession knowledge system has not been researched.",
            "decision": "unresolved",
            "owner": "course owner",
            "acceptance_gate": "All five dimensions and independent reviews pass.",
        }],
        "review_status": {
            "lifecycle_continuity": "not-run",
            "specialization_completeness": "not-run",
            "system_diversity": "not-run",
            "metrics_and_gates": "not-run",
            "ai_change_realism": "not-run",
            "career_coherence": "not-run",
        },
    }, ensure_ascii=False, indent=2))
    (root / "courses").mkdir()
    write(root / "tasks.json", json.dumps({"career_id": args.career_slug, "tasks": []}, ensure_ascii=False, indent=2))
    write(root / "curriculum.json", json.dumps({"career_id": args.career_slug, "courses": []}, ensure_ascii=False, indent=2))
    write(root / "tools/tool-registry.json", json.dumps({"last_verified": today, "tools": []}, ensure_ascii=False, indent=2))
    write(root / "validation-report.md", "# Validation report\n\nVerdict: FAIL-STRUCTURE (scaffold only).\n\n## Evidence\n\nNone.\n\n## Inference\n\nNone.\n\n## Unknown\n\nAll professional and AI claims.\n\n## Professional utility verdict\n\nNot evaluated.\n\n## Not tested\n\nResearch, lab, model, and practitioner review.")
    review_stub = "当前是未调研脚手架。所有职业事实、AI 能力、课程决策、运行证据和发布资格均为未知，不允许据此生成公开课程或商业宣传。"
    write(root / "human-review/README.md", f"# 评审入口\n\n## 先看什么\n\n{review_stub}\n\n## 当前结论\n\nFAIL。{review_stub}\n\n## 如何判断\n\n运行验证器并逐项关闭缺口。{review_stub}")
    write(root / "human-review/01-调研思路与主要结论.md", f"# 调研\n\n## 调研链路\n\n{review_stub}\n\n## 主要结论\n\n无。\n\n## Evidence\n\n无。\n\n## Inference\n\n无。\n\n## Unknown\n\n{review_stub}")
    write(root / "human-review/02-成果清单与课程地图.md", f"# 成果\n\n## 职业工作域\n\n未知。\n\n## 场景清单\n\n未知。\n\n## 课程地图\n\n未生成。\n\n## 交付状态\n\n{review_stub}")
    write(root / "human-review/03-细化样课.md", f"# 样课\n\n## 业务场景\n\n未知。\n\n## 学完能得到什么\n\n未知。\n\n## 上课流程\n\n未设计。\n\n## 学员实操\n\n未设计。\n\n## 验证标准\n\n未设计。\n\n## 证据边界\n\n{review_stub}")
    write(root / "human-review/04-完整方案审计.md", "# 完整方案审计\n\n## 方案单元\n\n尚未设计。\n\n## 完整性结论\n\n不通过：25 个方案维度尚未评审。\n\n## 运行证据\n\n未运行。\n\n## 架构与决策\n\n六类架构视图和 ADR 均缺失。\n\n## 缺口与风险\n\n全部未知，当前只能作为内部脚手架。\n\n## 发布门禁\n\n不允许发布为试点或完整方案。")
    (root / "architecture").mkdir(exist_ok=True)
    write(root / "tutorial/README.md", f"# {args.career_name} × AI tutorial\n\n## 如何学习\n\n尚不可学习。\n\n## 教程结构\n\n尚未生成。\n\n## 当前完成度\n\nFAIL：调研与方案门禁未通过。")
    write(root / "tutorial/course-tree.md", "# Course tree\n\n## 内容组织\n\n未生成。\n\n## 模块\n\n未生成。\n\n## 页面状态\n\n无可发布页面。")
    write(root / "tutorial/page-template.md", "# Page template\n\n## 页面顶部\n\nTODO\n\n## 通俗解释\n\nTODO\n\n## 自己动手\n\nTODO\n\n## 完成检查\n\nTODO\n\n## 证据边界\n\n未验证。")
    write(root / "tutorial/tutorial-site.json", json.dumps({
        "tutorial_id": args.career_slug, "title": f"{args.career_name} × AI", "audience": "unknown",
        "updated_at": today, "default_page_id": "", "release_scope": {"mode": "internal", "promised_page_ids": [], "catalog_complete": False, "validated_at": today},
        "modules": [], "pages": [],
    }, ensure_ascii=False, indent=2))
    write(root / "tutorial/index.html", "<!doctype html><html lang=\"zh-CN\"><meta charset=\"utf-8\"><title>Not ready</title><body><p>课程尚未通过完整方案门禁。</p></body></html>")
    write(root / "update-log.md", f"# Update log\n\n- {today}: Created fail-closed AI-native scaffold.")
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
