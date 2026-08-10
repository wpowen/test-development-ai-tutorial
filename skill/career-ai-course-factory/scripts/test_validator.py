#!/usr/bin/env python3
"""Regression tests for fail-closed AI course package gates."""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from validate_career_package import COURSE_FILES, COURSE_MARKERS, validate, verify_source_urls


def write(path: Path, content: str = "ok") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def dump(path: Path, data: object) -> None:
    write(path, json.dumps(data))


def build_valid(root: Path) -> None:
    for name in ["career-profile.md", "course-map.md", "update-log.md"]:
        write(root / name)
    write(root / "profession-reality-map.md", "# Profession reality map\n\nEvidence-bounded role, workflow, artifact, pain, promotion and AI opportunity reconstruction.\n")
    write(root / "validation-report.md", "## Evidence\n## Inference\n## Unknown\n## Professional utility verdict\n## Not tested\n")
    readable_body = "这是一份给课程负责人直接阅读和判断的中文评审内容，包含职业问题、AI 作用、业务场景、证据状态、学员产物、操作步骤、失败边界和下一步决策。" * 8
    architecture_body = "本阶段说明职业原有能力、AI 带来的变化、新失败模式、前置知识、学习者工件、故障注入和阶段退出标准。" * 16
    write(root / "learning-architecture.md", "# Learning architecture\n\n" + "\n\n".join(
        f"{marker}\n\n{architecture_body}" for marker in [
            "## Learner transformation", "## Professional baseline", "## AI foundations",
            "## Capability transition matrix", "## Learning stages", "## Specialization tracks",
            "## Benchmark literacy", "## Exit gates",
        ]
    ))
    write(root / "human-review/README.md", f"# 评审入口\n\n## 先看什么\n\n{readable_body}\n\n## 当前结论\n\n{readable_body}\n\n## 如何判断\n\n{readable_body}")
    write(root / "human-review/01-调研思路与主要结论.md", f"# 调研\n\n## 调研链路\n\n{readable_body}\n\n## 主要结论\n\n{readable_body}\n\n## Evidence\n\n{readable_body}\n\n## Inference\n\n{readable_body}\n\n## Unknown\n\n{readable_body}")
    write(root / "human-review/02-成果清单与课程地图.md", f"# 成果\n\n## 职业工作域\n\n{readable_body}\n\n## 场景清单\n\n{readable_body}\n\n## 课程地图\n\n{readable_body}\n\n## 交付状态\n\n{readable_body}")
    write(root / "human-review/03-细化样课.md", f"# 样课\n\n## 业务场景\n\n{readable_body}\n\n## 学完能得到什么\n\n{readable_body}\n\n## 上课流程\n\n{readable_body}\n\n## 学员实操\n\n{readable_body}\n\n## 验证标准\n\n{readable_body}\n\n## 证据边界\n\n{readable_body}")
    write(root / "tutorial/README.md", f"# Tutorial\n\n## 如何学习\n\n{readable_body}\n\n## 教程结构\n\n{readable_body}\n\n## 当前完成度\n\n{readable_body}")
    write(root / "tutorial/course-tree.md", f"# Tree\n\n## 学习路线\n\n{readable_body}\n\n## 模块\n\n{readable_body}\n\n## 页面状态\n\n{readable_body}")
    write(root / "tutorial/page-template.md", f"# Template\n\n## 页面顶部\n\n{readable_body}\n\n## 通俗解释\n\n{readable_body}\n\n## 自己动手\n\n{readable_body}\n\n## 完成检查\n\n{readable_body}\n\n## 证据边界\n\n{readable_body}")
    tutorial_modules = [
        {"module_id":f"module-{index}","title":f"Module {index}","learner_result":"complete a professional result","order":index}
        for index in range(4)
    ]
    tutorial_pages = []
    for index in range(15):
        delivered = index == 0
        tutorial_pages.append({
            "page_id":f"page-{index}","slug":f"page-{index}","module_id":f"module-{min(index // 4, 3)}",
            "title":f"Tutorial page {index}","page_type":"guided-lab" if delivered else "concept","level":"L1",
            "order":index,"prerequisite_ids":[] if index == 0 else [f"page-{index-1}"],"scenario_ids":["scenario-0"],
            "learner_result":"produce a checked result","artifact":"report","keywords":["AI","quality"],
            "evidence_status":"fixture-tested" if delivered else "desk-researched",
            "delivery_status":"fixture-tested" if delivered else "planned","updated_at":"2026-01-01",
            "source_ids":["S0"],"previous_page_id":"" if index == 0 else f"page-{index-1}",
            "next_page_id":"" if index == 14 else f"page-{index+1}",
            **({"content_sections":{"outcome":"build a gate","professional_relevance":"release evidence","plain_explanation":"a gate is a repeatable check","smallest_example":"one case","learner_action":"run the command","expected_result":"visible PASS","common_errors":"empty evidence","completion_check":"red green proof","evidence_boundary":"fixture only"}} if delivered else {})
        })
    dump(root / "tutorial/tutorial-site.json", {"tutorial_id":"career-ai","title":"Career AI Tutorial","audience":"beginner","updated_at":"2026-01-01","default_page_id":"page-0","release_scope":{"mode":"pilot-path","promised_page_ids":["page-0"],"catalog_complete":False,"validated_at":"2026-01-01"},"modules":tutorial_modules,"pages":tutorial_pages})
    page_id_blob = " ".join(page["page_id"] for page in tutorial_pages)
    html = f'''<!doctype html><html><head><meta charset="utf-8"><title>Tutorial</title><style>{"body{{color:#222}}" * 500}</style></head><body><input id="tutorial-search"><nav id="course-nav">{page_id_blob}</nav><main id="tutorial-content">{readable_body * 10}</main><aside id="page-toc"></aside><div id="progress-bar"></div><script>const COURSE_DATA = {json.dumps(tutorial_pages)};</script></body></html>'''
    write(root / "tutorial/index.html", html)
    write(root / "research/topics/page-0/research-package.md", "# Page 0 research\n\n## Research brief\n\nScoped learner question and decision.\n\n## Source pack\n\nOpened primary sources with limitations.\n\n## Evidence synthesis\n\nFacts, synthesis and unknowns.\n\n## Engineering blueprint\n\nMetrics, data, workflow and failure path.\n\n## Manuscript map\n\nMaps evidence into the learner page.\n\n## Editorial review\n\nPASS: protected fields, commands, limits and citations preserved; no generic template prose.\n\n## Validation\n\nPASS: claims, actions and boundaries checked.\n")
    write(root / "research/evidence-matrix.md", "## Evidence\n## Competitor observations\n## Vendor claims\n## Inference\n## Unknown\n")
    write(root / "research/ai-capability-map.md", "\n".join(["use-ai-for-work", "test-ai-systems", "agentize-work", "build-ai-quality-system"]))

    framework_body = "本节解释职业的输入、活动、工件、决策、指标、工具、失败、AI 变化、人工责任、学习产物和证据边界，并说明它怎样与其他职业维度形成可审计的能力闭环。" * 16
    write(root / "industry-framework.md", "# Industry framework\n\n" + "\n\n".join(
        f"{marker}\n\n{framework_body}" for marker in [
            "## End-to-end lifecycle", "## Specialization families", "## System and work-object classes",
            "## Quality and outcome attributes", "## AI transformation", "## Role and career evolution",
            "## Coverage verdict", "## Critical gaps",
        ]
    ))
    lifecycle_ids = [f"life-{index}" for index in range(8)]
    family_ids = [f"family-{index}" for index in range(6)]
    system_ids = [f"system-{index}" for index in range(5)]
    attribute_ids = [f"attribute-{index}" for index in range(6)]
    change_classes = ["retained", "assisted", "automated", "transformed", "new-work", "declining"]

    def ai_change(index: int) -> dict[str, object]:
        return {
            "change_id":f"change-{index}", "change_class":change_classes[index % len(change_classes)],
            "baseline_work":"a bounded professional step with an inspectable artifact",
            "ai_intervention":"AI proposes or executes a bounded step under an explicit control",
            "human_accountability":"the qualified owner verifies evidence and owns the decision",
            "new_failure_modes":["plausible unsupported output", "stale or unsafe action"],
            "required_controls":["versioned input and output", "fallback and human approval"],
            "learner_proof":"a seeded failure is detected and repaired", "evidence_ids":["S0", "S1"],
            "confidence":"medium",
        }

    dump(root / "research/profession-knowledge-system.json", {
        "profession_id":"c", "as_of":"2026-01-01",
        "lifecycle_stages":[{
            "stage_id":stage_id, "name":f"lifecycle {index}", "trigger":"a verifiable business event",
            "inputs":["versioned input"], "activities":["analyze", "verify"], "outputs":["decision evidence"],
            "artifacts":["report"], "decision_gate":"named owner accepts or rejects", "owner":"quality owner",
            "metrics":["risk coverage", "failure rate"], "tools":["versioned professional tool"],
            "failure_modes":["missing evidence", "wrong handoff"], "downstream_handoff":"next lifecycle owner",
            "evidence_ids":["S0", "S1"], "course_ids":["example" if index == 0 else f"c{min(index, 7)}"],
            "ai_changes":[ai_change(index)],
        } for index, stage_id in enumerate(lifecycle_ids)],
        "specialization_families":[{
            "family_id":family_id, "name":f"specialization {index}", "scope":"cross-lifecycle professional specialty",
            "protected_outcome":"a measurable quality outcome", "risks":["critical failure"],
            "methods":["risk analysis", "failure injection"], "artifacts":["specialty report"],
            "metrics":["p95 indicator", "error rate"], "tools":["specialty tool"], "prerequisites":["professional baseline"],
            "lifecycle_stage_ids":[lifecycle_ids[index % len(lifecycle_ids)]], "system_class_ids":[system_ids[index % len(system_ids)]],
            "evidence_ids":["S0", "S1"], "course_ids":["example" if index == 0 else f"c{index}"],
            "ai_changes":[ai_change(index + 8)],
        } for index, family_id in enumerate(family_ids)],
        "system_classes":[{
            "system_class_id":system_id, "name":f"system {index}", "interfaces":["versioned interface"],
            "state":["observable state"], "dependencies":["external dependency"], "observability_points":["metric", "trace"],
            "characteristic_failures":["timeout", "incorrect state"], "quality_attribute_ids":[attribute_ids[index % len(attribute_ids)]],
            "specialization_family_ids":[family_ids[index % len(family_ids)]], "evidence_ids":["S0", "S1"],
            "course_ids":["example" if index == 0 else f"c{index}"],
        } for index, system_id in enumerate(system_ids)],
        "outcome_attributes":[{
            "attribute_id":attribute_id, "name":f"attribute {index}", "definition":"observable professional outcome",
            "observable_indicators":["user-visible result"], "leading_metrics":["risk coverage"], "lagging_metrics":["escaped failures"],
            "verification_methods":["controlled experiment"], "decision_thresholds":["workload-specific SLO and named owner"],
            "tradeoffs":["quality versus cost"], "ai_specific_risks":["non-deterministic regression"],
            "evidence_ids":["S0", "S1"], "course_ids":["example" if index == 0 else f"c{index}"],
        } for index, attribute_id in enumerate(attribute_ids)],
        "role_evolution":[{
            "role_id":f"role-{index}", "level":f"level-{index}", "current_responsibilities":["own professional evidence"],
            "durable_skills":["risk judgment"], "assisted_or_automated_work":["bounded drafting and execution"],
            "new_ai_responsibilities":["evaluate AI-specific failures"], "adjacent_roles":["platform quality"],
            "transition_projects":["build a red-green quality gate"], "portfolio_evidence":["versioned report"],
            "decision_authority":"authority grows with level", "evidence_ids":["S0", "S1"],
            "course_ids":["example" if index == 0 else f"c{index}"], "forecast_boundary":"signal, not market-wide proof",
        } for index in range(4)],
        "coverage_cells":[{
            "cell_id":f"knowledge-cell-{index}", "lifecycle_stage_id":lifecycle_ids[index % len(lifecycle_ids)],
            "specialization_family_id":family_ids[index % len(family_ids)], "system_class_id":system_ids[index % len(system_ids)],
            "outcome_attribute_id":attribute_ids[index % len(attribute_ids)], "learner_level":f"L{1 + index % 4}",
            "status":"covered" if index == 0 else "planned", "priority":"high" if index % 7 == 0 else "medium",
            "rationale":"material profession combination requires explicit learner proof", "course_ids":["example" if index == 0 else f"c{1 + index % 7}"],
            "learner_artifact":"checked professional artifact", "assessment":"seeded failure must be detected",
            "evidence_ids":["S0", "S1"],
        } for index in range(24)],
        "critical_gaps":[],
        "review_status":{
            "lifecycle_continuity":"pass", "specialization_completeness":"pass", "system_diversity":"pass",
            "metrics_and_gates":"pass", "ai_change_realism":"pass", "career_coherence":"pass",
        },
    })

    ledger_fields = ["id", "title", "creator", "source_type", "platform", "language", "year", "url", "access_date", "evidence_tier", "publisher_group", "source_family_id", "channel_ids", "relevance", "credibility", "used_for", "limitations"]
    (root / "research").mkdir(parents=True, exist_ok=True)
    channel_by_index = {
        0:"ai-primary", 1:"profession-authority", 2:"practitioner-failure", 3:"ai-primary;github-artifact",
        4:"ai-primary;github-artifact", 5:"counterevidence", 6:"market-demand", 7:"market-demand",
        8:"market-demand", 9:"market-demand", 10:"market-demand", 11:"learner-supply",
        12:"learner-supply", 13:"learner-supply", 14:"learner-supply",
    }
    ledger_rows = []
    with (root / "research/source-ledger.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ledger_fields)
        writer.writeheader()
        for index in range(24):
            source_type = {0:"official documentation", 1:"professional syllabus", 2:"practitioner article", 3:"primary repository", 4:"primary repository", 5:"standard", 6:"job posting", 7:"job posting", 8:"job posting", 9:"job posting", 10:"job posting", 11:"course", 12:"video course", 13:"commercial course", 14:"course", 20:"official documentation", 21:"standard", 22:"practitioner session", 23:"industry report"}.get(index, "community discussion")
            url = {3:"https://github.com/openai/evals", 4:"https://github.com/browser-use/browser-use"}.get(index, f"https://source{index}.example.org/item")
            row = {"id":f"S{index}","title":f"title {index}","creator":f"creator {index}","source_type":source_type,"platform":f"p{index % 7}","language":"zh" if index == 0 else "en","year":"2026","url":url,"access_date":"2026-01-01","evidence_tier":"primary","publisher_group":f"publisher-{index}","source_family_id":f"family-{index}","channel_ids":channel_by_index.get(index, "practitioner-failure" if index < 20 else "counterevidence"),"relevance":"relevant","credibility":"high","used_for":"validation","limitations":"bounded evidence"}
            ledger_rows.append(row)
            writer.writerow(row)

    competitor_fields = ["id", "platform", "offering", "audience", "promise", "ai_lane", "modules", "hands_on_artifact", "execution_proof", "assessment", "freshness", "commercial_model", "url", "access_date", "gap", "claim_status"]
    with (root / "research/competitor-matrix.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=competitor_fields)
        writer.writeheader()
        for index in range(6):
            writer.writerow({"id":f"C{index}","platform":f"cp{index % 3}","offering":"o","audience":"a","promise":"p","ai_lane":"test-ai-systems","modules":"m","hands_on_artifact":"h","execution_proof":"e","assessment":"a","freshness":"f","commercial_model":"c","url":"https://example.com","access_date":"2026-01-01","gap":"g","claim_status":"observed"})

    dump(root / "research/search-plan.json", {
        "profession":"c", "generated_at":"2026-01-01T00:00:00Z", "research_question":"c x AI",
        "freshness_required":True, "run_scope":"full",
        "available_surfaces":[
            {"surface_id":f"SURF-{i}","surface":f"surface{i}","is_live":i == 0,"status":"available","attempted_at":"2026-01-01T00:00:00Z","evidence":f"log-{i}","limits":"none"}
            for i in range(3)
        ],
        "query_families":[{"family":f"f{i}","languages":["zh","en"],"purpose":"p"} for i in range(5)],
        "freshness_policy":[{"claim_type":"tool","max_age_days":90}],
        "stop_conditions":["BLOCKED-FRESHNESS"], "run_status":"complete",
    })
    search_fields = ["id", "query", "language", "research_lane", "surface_attempt_id", "search_surface", "run_at", "result_count", "selected_source_ids", "opened_urls", "exclusion_notes", "status"]
    with (root / "research/search-log.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=search_fields)
        writer.writeheader()
        for index in range(8):
            selected = ledger_rows[index * 3:(index + 1) * 3]
            writer.writerow({"id":f"Q{index}","query":f"exact query {index}","language":"zh" if index == 0 else "en","research_lane":f"f{index % 5}","surface_attempt_id":f"SURF-{index % 3}","search_surface":f"surface{index % 3}","run_at":"2026-01-01T00:00:00Z","result_count":"10","selected_source_ids":";".join(row["id"] for row in selected),"opened_urls":";".join(row["url"] for row in selected),"exclusion_notes":"none","status":"selected"})

    channel_sources = {
        channel:[row["id"] for row in ledger_rows if channel in row["channel_ids"].split(";")]
        for channel in ["profession-authority", "ai-primary", "github-artifact", "practitioner-failure", "market-demand", "learner-supply", "counterevidence"]
    }
    dump(root / "research/channel-coverage.json", {"profession":"c", "generated_at":"2026-01-01T00:00:00Z", "channels":[
        {"channel_id":channel,"purpose":"purpose","source_ids":source_ids,"query_ids":sorted({f"Q{int(source_id[1:]) // 3}" for source_id in source_ids}),"claim_boundary":"bounded","status":"complete","limitations":"limits"}
        for channel, source_ids in channel_sources.items()
    ]})
    github_fields = ["artifact_id", "source_id", "repo_url", "commit_or_tag", "license", "last_commit_at", "release_or_commit_url", "issues_url", "ci_url", "setup_command", "smoke_command", "run_status", "run_at", "exit_code", "evidence_path", "selected_for_lab", "limitations"]
    with (root / "research/github-artifacts.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=github_fields); writer.writeheader()
        writer.writerow({"artifact_id":"G1","source_id":"S3","repo_url":"https://github.com/openai/evals","commit_or_tag":"abc123","license":"MIT","last_commit_at":"2026-01-01T00:00:00Z","release_or_commit_url":"https://github.com/openai/evals/commit/abc123","issues_url":"https://github.com/openai/evals/issues","ci_url":"https://github.com/openai/evals/actions","setup_command":"pip install -e .","smoke_command":"tool --help","run_status":"metadata-only","run_at":"not-run","exit_code":"not-run","evidence_path":"not-run","selected_for_lab":"false","limitations":"not selected"})
        writer.writerow({"artifact_id":"G2","source_id":"S4","repo_url":"https://github.com/browser-use/browser-use","commit_or_tag":"def456","license":"MIT","last_commit_at":"2026-01-01T00:00:00Z","release_or_commit_url":"https://github.com/browser-use/browser-use/commit/def456","issues_url":"https://github.com/browser-use/browser-use/issues","ci_url":"https://github.com/browser-use/browser-use/actions","setup_command":"uv sync","smoke_command":"tool --help","run_status":"metadata-only","run_at":"not-run","exit_code":"not-run","evidence_path":"not-run","selected_for_lab":"false","limitations":"not selected"})
    job_fields = ["job_id", "source_id", "employer", "title", "location", "posted_or_observed_at", "original_url", "task_terms", "ai_terms", "duplicate_group", "claim_status", "limitations"]
    with (root / "research/job-signals.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=job_fields); writer.writeheader()
        for index in range(5):
            writer.writerow({"job_id":f"J{index}","source_id":f"S{6+index}","employer":f"employer-{index}","title":"AI quality","location":"remote","posted_or_observed_at":"2026-01-01","original_url":f"https://jobs{index}.example.org/item","task_terms":"eval","ai_terms":"LLM","duplicate_group":f"job-{index}","claim_status":"employer-claim","limitations":"signal only"})
    learner_fields = ["signal_id", "source_id", "platform", "content_url", "signal_type", "direct_observation", "learner_question", "requested_outcome", "pain_language", "engagement_metric", "metric_scope", "observed_at", "claim_status", "limitations"]
    with (root / "research/learner-signals.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=learner_fields); writer.writeheader()
        for index in range(4):
            writer.writerow({"signal_id":f"L{index}","source_id":f"S{11+index}","platform":f"course-platform-{index}","content_url":ledger_rows[11+index]["url"],"signal_type":"course-page","direct_observation":"course exists","learner_question":"how","requested_outcome":"artifact","pain_language":"unknown","engagement_metric":"not-used","metric_scope":"not efficacy","observed_at":"2026-01-01","claim_status":"observed","limitations":"supply only"})

    lanes = ["use-ai-for-work", "test-ai-systems", "agentize-work", "build-ai-quality-system"]
    dump(root / "research/technology-radar.json", {"profession":"c", "technologies":[{
        "technology_id":f"tech-{index}","name":"tech","category":"eval","capability":"capability",
        "ai_lane":lanes[index % 4],"official_source":"https://example.com/official","version_or_release":"2026-01",
        "last_verified":"2026-01-01","maturity":"stable","status":"current","setup":"local",
        "limits":["limit"],"security":"review","scenario_ids":[f"scenario-{index}"],"course_ids":["c0"],
        "fallbacks":["manual"],"refresh_trigger":"release","evidence_ids":[f"S{index}"]
    } for index in range(8)]})
    dump(root / "research/scenarios.json", {"profession":"c", "scenarios":[{
        "scenario_id":f"scenario-{index}","title":"business result","ai_lane":lanes[index % 4],
        "actor":"senior tester","work_setting":"product team","trigger":"release candidate",
        "business_system":"customer support system","business_object":"release","inputs":["trace"],
        "current_workflow":"manual review","pain_and_failure_cost":"escaped defect","constraints":["privacy"],
        "ai_intervention":"evaluate AI system","ai_role":"system-under-test","outputs":["report"],
        "decision_or_handoff":"release owner approves","ai_specific_failures":["hallucination"],
        "privacy_security":"sanitized fixture","evidence_ids":["S0","S1","S2"],
        "evidence_classes":["profession-workflow","ai-capability","practice-artifact"],
        "evidence_map":{"profession-workflow":["S1"],"ai-capability":["S0"],"practice-artifact":["S2"]},
        "semantic_contract":{"actor_role":"senior test engineer","actor_seniority":"release owner","business_domain":"customer support","system_name_or_class":"RAG support system","failure_impact":"escaped incorrect answer","observable_indicator":"release gate failure rate","measurement_status":"measured","decision_owner":"quality lead","decision":"release or block","allowed_ai_authority":"score evidence only","human_approval_required":True},
        "artifact":"report.json","demo_fixture":"synthetic","validation_plan":["baseline","failure","repair"],
        "scores":{"ai_centrality":5,"business_specificity":5,"artifact_accessibility":4,"testability":5},
        "evidence_status":"fixture-tested"
    } for index in range(8)]})
    dump(root / "research/profession-map.json", {"profession_id":"c","canonical_name":"career","taxonomy":[{"system":"test","id":"c"}],"as_of":"2026-01-01","role_variants":[{"id":"v1"},{"id":"v2"}],"lifecycle":["intake","release"],"work_domains":[
        {"domain_id":f"d{index}","name":"domain","job_result":"result","business_events":["event"],"artifacts":["artifact"],"systems":["system"],"decision_rights":["human"],"failure_costs":["cost"],"ai_lanes":[lanes[index % 4]],"scenario_ids":[f"scenario-{index}"] + ([f"scenario-{index+5}"] if index < 3 else []),"evidence_ids":["S0","S1"]}
        for index in range(5)
    ]})
    dump(root / "research/profession-reality-map.json", {
        "profession_id":"c", "as_of":"2026-01-01", "review_status":"desk-researched",
        "role_variants":[{"id":"associate"},{"id":"senior"},{"id":"lead"}],
        "work_rhythms":[{"id":"day"},{"id":"sprint"},{"id":"incident"}],
        "workflow_stages":[{"stage_id":f"work-{index}"} for index in range(6)],
        "dependencies":[{"id":f"dep-{index}"} for index in range(5)],
        "artifacts":[{"id":f"artifact-{index}"} for index in range(6)],
        "performance_and_promotion":{"public_signals":["reliable delivery", "reusable leverage"], "internal_status":"INTERNAL-UNKNOWN"},
        "pain_points":[{"id":f"pain-{index}"} for index in range(5)],
        "information_barriers":[{"id":"public"},{"id":"internal"},{"id":"tacit"}],
        "ai_opportunities":[{
            "opportunity_id":f"opp-{index}", "work_stage_id":f"work-{index % 6}",
            "change_class":["retained", "assisted", "automated", "transformed", "new-work"][index],
            "baseline_pain":"slow and fragmented work", "ai_role":"bounded assistant",
            "inspectable_output":"versioned artifact", "human_gate":"named owner approves",
            "ai_failures":["unsupported output"], "baseline_metric":"elapsed time and escaped errors",
            "success_measure":"faster work without lower detection", "starter_material":"fixture and validated Skill",
            "evidence_status":"desk-researched",
        } for index in range(5)],
        "beginner_reuse_pack":{"fixture":"synthetic", "failure_injection":"seeded defect", "transfer_checklist":"replace local inputs safely"},
        "source_ids":["S0","S1","S2"],
    })

    layer_kinds = [
        "profession-baseline", "ai-foundation", "ai-assisted-work", "ai-system-quality",
        "agent-workflow-quality", "quality-engineering", "benchmark-literacy", "capstone",
    ]
    stage_ids = [f"stage-{index + 1}" for index in range(len(layer_kinds))]
    dump(root / "research/competency-transition-map.json", {
        "profession_id":"c", "architecture_profile":"ai-quality-engineer", "audience":"professional learner",
        "as_of":"2026-01-01",
        "professional_baseline":{
            "lifecycle_stages":["intake","risk","design","execute","release","operate"],
            "work_domains":["requirements","automation","data","diagnosis","release"],
            "methods":["risk based testing","boundary analysis","state testing","mutation testing"],
            "tools_and_artifacts":["test plan","automation suite","trace","CI gate"],
            "quality_decisions":["scope","release","rollback"],
            "entry_assessment":"submit an executable baseline suite that fails on a seeded defect",
        },
        "ai_foundations":{
            "model_lifecycle":["data","pretraining","post-training","evaluation","deployment","inference","monitoring"],
            "core_primitives":["tokens","embeddings","attention","context","decoding","tool calls","state","trace"],
            "application_patterns":["LLM","RAG","multimodal","agent","workflow"],
            "capability_boundaries":["non-determinism","hallucination","context limit","prompt sensitivity","tool error","privacy","latency"],
            "test_implications":["versioning","dataset","slice","composite oracle","failure injection","human review"],
        },
        "transition_matrix":[{
            "transition_id":f"transition-{index}", "baseline_competency":"professional testing",
            "retained_principle":"evidence before release", "ai_change":"probabilistic and tool-using system",
            "new_ai_capability":"evaluate versioned AI behavior", "new_failure_modes":["hallucination","unsafe action"],
            "learner_artifact":"versioned evaluation asset", "assessment":"seeded regression must fail",
            "course_ids":["example"],
        } for index in range(6)],
        "learning_stages":[{
            "stage_id":stage_ids[index], "layer_kind":kind, "order":index + 1, "title":kind,
            "learner_transformation":"advance through one evidence-backed capability layer",
            "prerequisite_stage_ids":[] if index == 0 else [stage_ids[index - 1]],
            "required_concepts":["concept a","concept b"], "learner_artifact":f"artifact-{index}",
            "exit_assessment":"artifact catches a seeded regression", "failure_injection":"meaningful defect",
            "course_ids":["example" if index == 0 else f"c{index}"], "source_ids":["S0","S1"],
        } for index, kind in enumerate(layer_kinds)],
        "specialization_tracks":[{
            "track_id":f"track-{index}", "track_kind":kind, "title":kind,
            "prerequisite_stage_ids":["stage-4"], "course_ids":["example"],
            "capstone_artifact":"specialized quality report", "source_ids":["S0"],
        } for index, kind in enumerate(["llm-quality","rag-quality","agent-quality","workflow-quality","benchmark-engineering"])],
        "source_ids":["S0","S1"],
    })

    audit_body = "本段基于独立来源说明职业能力、AI 技术、真实工作、竞品供给、失败证据、课程决策与尚未验证的边界，避免因为标题存在就误判为能力已经覆盖。" * 12
    write(root / "curriculum-gap-analysis.md", "# Curriculum gap analysis\n\n" + "\n\n".join(
        f"{marker}\n\n{audit_body}" for marker in [
            "## Research corpus", "## Industry body of knowledge",
            "## Real work and practitioner evidence", "## Existing course supply",
            "## AI technology and benchmark frontier", "## Coverage matrix",
            "## Missing and overrepresented topics", "## Expert review",
            "### Profession veteran", "### AI systems engineer",
            "### Evaluation and quality expert", "### Curriculum designer",
            "### Market and learner researcher", "### Adversarial critic",
            "## Curriculum decisions", "## Remaining unknowns",
        ]
    ))
    coverage_fields = [
        "cell_id", "profession_domain_id", "layer_kind", "specialization_kind",
        "learner_level", "topic", "required_by_source_ids", "competitor_ids", "course_ids",
        "learner_artifact", "exit_assessment", "evidence_status", "coverage_status",
        "priority", "gap_reason", "decision",
    ]
    specializations = ["llm-quality", "rag-quality", "agent-quality", "workflow-quality", "benchmark-engineering"]
    with (root / "research/curriculum-coverage-matrix.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=coverage_fields)
        writer.writeheader()
        for index in range(24):
            layer_index = index // 3
            writer.writerow({
                "cell_id":f"CELL-{index:02d}", "profession_domain_id":f"d{index % 5}",
                "layer_kind":layer_kinds[layer_index],
                "specialization_kind":specializations[index % len(specializations)] if layer_index >= 3 else "",
                "learner_level":f"L{min(layer_index, 4)}", "topic":f"audited capability {index}",
                "required_by_source_ids":f"S{index % 3};S{3 + index % 3}",
                "competitor_ids":f"C{index % 6}",
                "course_ids":"example" if layer_index == 0 else f"c{layer_index}",
                "learner_artifact":f"artifact-{index}", "exit_assessment":"seeded regression must fail",
                "evidence_status":"desk-researched", "coverage_status":"covered" if index == 0 else "planned",
                "priority":"high" if index % 4 == 0 else "medium", "gap_reason":"",
                "decision":"retain as an assessed dependency",
            })

    task = {
        "task_id":"t","career_id":"c","scenario_id":"scenario-0","title":"AI task","ai_lane":"test-ai-systems","ai_role":"system-under-test","system_under_test":"LLM","professional_problem":"p","inputs":["i"],"non_ai_baseline":"b","ai_workflow":"w","ai_specific_failures":["f"],"learner_proof":"proof","deliverables":["d"],"scores":{"ai_centrality":5,"professional_leverage":5,"runnable_proof":5,"source_strength":5},"acceptance_criteria":["a"],"human_gate":"h","privacy_notes":"p","status":"fixture-tested","evidence_ids":["S0"]
    }
    dump(root / "tasks.json", {"tasks":[task]})
    courses = [{
        "course_id":"example" if i == 0 else f"c{i}", "title":"title",
        "stage_id":stage_ids[min(i, len(stage_ids) - 1)], "level":f"L{min(i, 4)}",
        "ai_lane":lane, "prerequisite_course_ids":[] if i == 0 else ["example"],
        "knowledge_dependencies":["professional evidence","AI behavior"],
        "professional_baseline":"retain risk-based quality decisions", "new_ai_capability":"evaluate AI behavior",
        "learner_artifact":["a"], "assessment":"seeded regression must fail", "proof":"p",
        "source_ids":["S0"], "delivery_status":"fixture-tested" if i == 0 else "planned",
    } for i, lane in enumerate((["use-ai-for-work", "test-ai-systems", "agentize-work", "build-ai-quality-system"] * 3)[:10])]
    dump(root / "curriculum.json", {"courses":courses})
    dump(root / "tools/tool-registry.json", {"tools":[]})

    course = root / "courses/example"
    for relative in COURSE_FILES:
        if relative.endswith(".json"):
            continue
        write(course / relative, "This learner-facing material contains commands, expected observations, failure boundaries, and a reusable artifact. " * 3)
    course_sections = []
    for marker in COURSE_MARKERS:
        body = "This section explains a concrete professional input, observable output, learner action, verification rule, human decision boundary, and transfer condition. " * 2
        if marker == "## Commands":
            body += "\n```bash\npython3 scripts/evaluate.py\n```\n"
        if marker == "## Failure injection":
            body += "The injected regression must FAIL with a non-zero exit code and produce a red report."
        course_sections.append(f"{marker}\n\n{body}")
    write(course / "course.md", "# Complete fixture course\n\n" + "\n\n".join(course_sections))
    manifest = {"course_id":"example","title":"AI eval","scenario_ids":["scenario-0"],"ai_lane":"test-ai-systems","ai_centrality_score":5,"professional_value_score":5,"system_under_test":"LLM","ai_roles":["system-under-test"],"learner_artifact":["eval"],"tool_adapters":["offline"],"work_domain_ids":["d0"],"primary_artifact_ids":["artifact"],"decision_owner":"quality lead","allowed_ai_authority":"score evidence only","prerequisite_course_ids":["intro"],"transfer_target":"neighbor scenario","lesson_flow":["demo","guided-practice","failure-injection","repair","transfer"],"default_path_requires_credentials":False,"baseline_comparison":True,"failure_injection":True,"execution_proof":"evidence/execution-evidence.json","validation_workdir":"lab","validation_steps":[{"name":"baseline","command":["python3","ok.py"],"expected_exit_code":0},{"name":"mutation","command":["python3","bad.py"],"expected_exit_code":1},{"name":"repair","command":["python3","ok.py"],"expected_exit_code":0}],"status":"fixture-tested","evidence_ids":["S0"]}
    dump(course / "course-manifest.json", manifest)
    write(course / "lab/ok.py", "raise SystemExit(0)")
    write(course / "lab/bad.py", "raise SystemExit(1)")
    proof = {"evidence_scope":"fixture","commands":["baseline","mutation","repair"],"baseline":{"exit_code":0,"verdict":"PASS"},"mutation":{"exit_code":1,"verdict":"FAIL"},"repair":{"exit_code":0,"verdict":"PASS"},"environment":{},"limitations":["fixture"]}
    dump(course / "evidence/execution-evidence.json", proof)
    dump(course / "materials/material-provenance.json", {"materials":[
        {"material_id":f"M{index}","path":path,"purpose":"learner use","source_ids":["S0"],"scenario_ids":["scenario-0"],"generated_from":["fixture"],"license_or_usage":"original","validation_status":"fixture-tested","validation_evidence":["proof"],"contains_synthetic_data":True,"limitations":"fixture"}
        for index, path in enumerate(["materials/quickstart.md","materials/reusable-skill.md","materials/sample-input.md","materials/expected-output.md","materials/verification-checklist.md"])
    ]})
    stage_ids = ["cold-open-failure", "stakes-and-promise", "before-after", "plain-mental-model", "guided-demo", "failure-diagnosis", "learner-practice", "transfer-challenge", "artifact-handoff"]
    dump(course / "video/lesson-experience.json", {"lesson_id":"lesson","target_learner":"beginner tester","level":"L2-control-and-check","estimated_minutes":10,"job_result":"build a gate","artifact":"report","stages":[
        {"stage_id":stage,"instructor_action":"show concrete professional evidence","learner_action":"predict and perform the required action","expected_observation":"a visible machine-checkable result","debrief":"explain the professional and AI boundary","artifact_or_assessment":"a saved learner-owned assessment artifact", **({"source_context":"customer support refund policy","target_context":"neighbor scenario","invariant":"the release decision remains evidence based","must_change":["dataset","risk threshold"],"success_criterion":"the new scenario fails on its own seeded regression"} if stage == "transfer-challenge" else {})} for stage in stage_ids
    ],"interaction_prompts":["predict","diagnose","transfer"],"recovery_path":"reset fixture","evidence_status":"fixture-tested","limitations":"not learner-tested"})


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        build_valid(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual(validate(self.root), [])

    def test_missing_professional_baseline_layer_fails(self) -> None:
        path = self.root / "research/competency-transition-map.json"
        data = json.loads(path.read_text())
        data["learning_stages"] = data["learning_stages"][1:]
        for index, stage in enumerate(data["learning_stages"]):
            stage["order"] = index + 1
            stage["prerequisite_stage_ids"] = [] if index == 0 else [data["learning_stages"][index - 1]["stage_id"]]
        dump(path, data)
        self.assertTrue(any("eight learning stages" in error or "eight-layer" in error for error in validate(self.root)))

    def test_profession_knowledge_system_requires_specialization_families(self) -> None:
        path = self.root / "research/profession-knowledge-system.json"
        data = json.loads(path.read_text())
        data["specialization_families"] = data["specialization_families"][:2]
        dump(path, data)
        self.assertTrue(any("at least 6 specialization families" in error for error in validate(self.root)))

    def test_profession_ai_change_cannot_omit_human_accountability(self) -> None:
        path = self.root / "research/profession-knowledge-system.json"
        data = json.loads(path.read_text())
        data["lifecycle_stages"][0]["ai_changes"][0]["human_accountability"] = ""
        dump(path, data)
        self.assertTrue(any("human_accountability" in error for error in validate(self.root)))

    def test_profession_metric_needs_decision_threshold(self) -> None:
        path = self.root / "research/profession-knowledge-system.json"
        data = json.loads(path.read_text())
        data["outcome_attributes"][0]["decision_thresholds"] = []
        dump(path, data)
        self.assertTrue(any("needs decision thresholds" in error for error in validate(self.root)))

    def test_profession_high_gap_cannot_remain_unresolved(self) -> None:
        path = self.root / "research/profession-knowledge-system.json"
        data = json.loads(path.read_text())
        data["critical_gaps"] = [{
            "gap_id":"gap-1", "priority":"high", "description":"missing specialty", "decision":"unresolved",
            "owner":"curriculum owner", "acceptance_gate":"specialty artifact and assessment exist",
        }]
        dump(path, data)
        self.assertTrue(any("unresolved high gap" in error for error in validate(self.root)))

    def test_ai_quality_profile_requires_distinct_specializations(self) -> None:
        path = self.root / "research/competency-transition-map.json"
        data = json.loads(path.read_text())
        data["specialization_tracks"] = data["specialization_tracks"][:2]
        dump(path, data)
        self.assertTrue(any("misses specialization tracks" in error for error in validate(self.root)))

    def test_gap_audit_requires_all_independent_review_roles(self) -> None:
        path = self.root / "curriculum-gap-analysis.md"
        write(path, path.read_text().replace("### Adversarial critic", "### General review"))
        self.assertTrue(any("missing independent review" in error for error in validate(self.root)))

    def test_high_priority_gap_without_decision_fails(self) -> None:
        path = self.root / "research/curriculum-coverage-matrix.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rows[0].update({"coverage_status":"gap", "priority":"high", "gap_reason":"missing lab", "decision":"", "course_ids":"", "learner_artifact":"", "exit_assessment":""})
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        self.assertTrue(any("unresolved high-priority gap" in error for error in validate(self.root)))

    def test_coverage_matrix_requires_all_learning_layers(self) -> None:
        path = self.root / "research/curriculum-coverage-matrix.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            if row["layer_kind"] == "benchmark-literacy":
                row["layer_kind"] = "quality-engineering"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        self.assertTrue(any("misses learning layers" in error for error in validate(self.root)))

    def test_missing_human_review_entry_fails(self) -> None:
        (self.root / "human-review/README.md").unlink()
        self.assertTrue(any("missing human-readable review file" in error for error in validate(self.root)))

    def test_complete_package_without_tutorial_viewer_fails(self) -> None:
        (self.root / "tutorial/index.html").unlink()
        self.assertTrue(any("missing tutorial file: tutorial/index.html" in error for error in validate(self.root)))

    def test_planned_tutorial_page_cannot_claim_delivered_without_sections(self) -> None:
        path = self.root / "tutorial/tutorial-site.json"
        data = json.loads(path.read_text())
        data["pages"][1]["delivery_status"] = "fixture-tested"
        dump(path, data)
        self.assertTrue(any("lacks required content sections" in error for error in validate(self.root)))

    def test_first_tutorial_page_may_have_no_prerequisite(self) -> None:
        path = self.root / "tutorial/tutorial-site.json"
        data = json.loads(path.read_text())
        self.assertEqual(data["pages"][0]["prerequisite_ids"], [])
        self.assertFalse(any("tutorial page 0 prerequisite_ids" in error for error in validate(self.root)))

    def test_promised_tutorial_page_requires_independent_research_package(self) -> None:
        (self.root / "research/topics/page-0/research-package.md").unlink()
        self.assertTrue(any("page-0 missing per-topic research package" in error for error in validate(self.root)))

    def test_promised_tutorial_page_requires_editorial_review(self) -> None:
        path = self.root / "research/topics/page-0/research-package.md"
        path.write_text(path.read_text().replace("## Editorial review", "## Editorial notes"))
        self.assertTrue(any("## Editorial review" in error for error in validate(self.root)))

    def test_complete_catalog_cannot_contain_planned_pages(self) -> None:
        path = self.root / "tutorial/tutorial-site.json"
        data = json.loads(path.read_text())
        data["release_scope"] = {
            "mode":"complete-catalog",
            "promised_page_ids":[page["page_id"] for page in data["pages"]],
            "catalog_complete":True,
            "validated_at":"2026-01-01",
        }
        dump(path, data)
        self.assertTrue(any("complete-catalog contains incomplete pages" in error for error in validate(self.root)))

    def test_decorative_ai_fails(self) -> None:
        data = json.loads((self.root / "tasks.json").read_text())
        data["tasks"][0]["scores"]["ai_centrality"] = 3
        dump(self.root / "tasks.json", data)
        self.assertTrue(any("AI centrality" in error for error in validate(self.root)))

    def test_fake_mutation_proof_fails(self) -> None:
        path = self.root / "courses/example/evidence/execution-evidence.json"
        data = json.loads(path.read_text())
        data["mutation"] = {"exit_code":0,"verdict":"PASS"}
        dump(path, data)
        self.assertTrue(any("mutation evidence" in error for error in validate(self.root)))

    def test_too_few_competitor_platforms_fails(self) -> None:
        path = self.root / "research/competitor-matrix.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            row["platform"] = "one"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        self.assertTrue(any("3 platforms" in error for error in validate(self.root)))

    def test_selected_search_without_opened_source_fails(self) -> None:
        path = self.root / "research/search-log.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rows[0]["opened_urls"] = ""
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        self.assertTrue(any("opened URL" in error for error in validate(self.root)))

    def test_scenario_without_three_class_evidence_fails(self) -> None:
        path = self.root / "research/scenarios.json"
        data = json.loads(path.read_text())
        data["scenarios"][0]["evidence_classes"] = ["ai-capability"]
        dump(path, data)
        self.assertTrue(any("three-class evidence" in error for error in validate(self.root)))

    def test_complete_without_live_retrieval_fails_closed(self) -> None:
        path = self.root / "research/search-plan.json"
        data = json.loads(path.read_text())
        for surface in data["available_surfaces"]:
            surface["is_live"] = False
        dump(path, data)
        self.assertTrue(any("BLOCKED-FRESHNESS" in error for error in validate(self.root)))

    def test_full_research_cannot_disable_freshness(self) -> None:
        path = self.root / "research/search-plan.json"
        data = json.loads(path.read_text())
        data["freshness_required"] = False
        dump(path, data)
        self.assertTrue(any("freshness_required=true" in error for error in validate(self.root)))

    def test_smoke_scope_cannot_validate_complete_package(self) -> None:
        path = self.root / "research/search-plan.json"
        data = json.loads(path.read_text())
        data["run_scope"] = "smoke"
        dump(path, data)
        self.assertTrue(any("run_scope full" in error for error in validate(self.root)))

    def test_unknown_surface_attempt_fails(self) -> None:
        path = self.root / "research/search-log.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rows[0]["surface_attempt_id"] = "INVENTED"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        self.assertTrue(any("unknown surface_attempt_id" in error for error in validate(self.root)))

    def test_evidence_class_must_bind_to_compatible_source(self) -> None:
        path = self.root / "research/scenarios.json"
        data = json.loads(path.read_text())
        data["scenarios"][0]["evidence_map"]["ai-capability"] = ["S2"]
        dump(path, data)
        self.assertTrue(any("does not support ai-capability" in error for error in validate(self.root)))

    def test_placeholder_semantic_contract_fails(self) -> None:
        path = self.root / "research/scenarios.json"
        data = json.loads(path.read_text())
        data["scenarios"][0]["semantic_contract"]["system_name_or_class"] = "某系统"
        dump(path, data)
        self.assertTrue(any("contains placeholder" in error for error in validate(self.root)))

    def test_duplicate_source_url_fails_independence(self) -> None:
        path = self.root / "research/source-ledger.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rows[1]["url"] = rows[0]["url"]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        self.assertTrue(any("duplicate canonical URLs" in error for error in validate(self.root)))

    def test_same_source_family_cannot_triangulate_scenario(self) -> None:
        path = self.root / "research/source-ledger.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for index in [1, 2]:
            rows[index]["publisher_group"] = rows[0]["publisher_group"]
            rows[index]["source_family_id"] = rows[0]["source_family_id"]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        errors = validate(self.root)
        self.assertTrue(any("independent publisher groups" in error or "independent source families" in error for error in errors))

    def test_channel_declared_without_executed_query_fails(self) -> None:
        path = self.root / "research/channel-coverage.json"
        data = json.loads(path.read_text())
        data["channels"][0]["query_ids"] = ["Q-INVENTED"]
        dump(path, data)
        self.assertTrue(any("unknown query IDs" in error for error in validate(self.root)))

    def test_selected_github_artifact_without_run_fails(self) -> None:
        path = self.root / "research/github-artifacts.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rows[0]["selected_for_lab"] = "true"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        self.assertTrue(any("selected for lab is not run-verified" in error for error in validate(self.root)))

    def test_incomplete_lesson_arc_fails(self) -> None:
        path = self.root / "courses/example/video/lesson-experience.json"
        data = json.loads(path.read_text())
        data["stages"] = [stage for stage in data["stages"] if stage["stage_id"] != "transfer-challenge"]
        dump(path, data)
        self.assertTrue(any("invalid or incomplete stage order" in error for error in validate(self.root)))

    def test_material_with_unknown_source_fails(self) -> None:
        path = self.root / "courses/example/materials/material-provenance.json"
        data = json.loads(path.read_text())
        data["materials"][0]["source_ids"] = ["S-INVENTED"]
        dump(path, data)
        self.assertTrue(any("missing or unknown source IDs" in error for error in validate(self.root)))

    def test_marker_only_course_fails(self) -> None:
        write(self.root / "courses/example/course.md", "\n".join(COURSE_MARKERS))
        self.assertTrue(any("too thin to teach" in error for error in validate(self.root)))

    def test_filler_families_do_not_hide_source_concentration(self) -> None:
        path = self.root / "research/source-ledger.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows[:15]:
            row["source_family_id"] = "dominant-family"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        self.assertTrue(any("over-concentrated" in error for error in validate(self.root)))

    def test_channel_cannot_borrow_sources_from_unbound_query(self) -> None:
        path = self.root / "research/channel-coverage.json"
        data = json.loads(path.read_text())
        data["channels"][0]["query_ids"] = ["Q7"]
        dump(path, data)
        self.assertTrue(any("not selected by its bound queries" in error for error in validate(self.root)))

    def test_channel_cannot_rely_on_blocked_query(self) -> None:
        coverage_path = self.root / "research/channel-coverage.json"
        coverage = json.loads(coverage_path.read_text())
        query_id = coverage["channels"][0]["query_ids"][0]
        path = self.root / "research/search-log.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            if row["id"] == query_id:
                row["status"] = "blocked"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        self.assertTrue(any("did not select evidence" in error for error in validate(self.root)))

    def test_github_run_evidence_cannot_borrow_arbitrary_file(self) -> None:
        path = self.root / "research/github-artifacts.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rows[0].update({"selected_for_lab":"true", "run_status":"run-verified", "exit_code":"0", "evidence_path":"validation-report.md"})
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        errors = validate(self.root)
        self.assertTrue(any("research/github-runs" in error or "structured JSON" in error for error in errors))

    def test_profession_map_cannot_omit_scenario(self) -> None:
        path = self.root / "research/profession-map.json"
        data = json.loads(path.read_text())
        for domain in data["work_domains"]:
            domain["scenario_ids"] = [scenario for scenario in domain["scenario_ids"] if scenario != "scenario-0"]
        dump(path, data)
        self.assertTrue(any("not mapped to a primary profession domain" in error for error in validate(self.root)))

    def test_profession_reality_map_is_required(self) -> None:
        (self.root / "research/profession-reality-map.json").unlink()
        self.assertTrue(any("profession-reality-map.json" in error for error in validate(self.root)))

    def test_profession_reality_map_rejects_shallow_ai_opportunity(self) -> None:
        path = self.root / "research/profession-reality-map.json"
        data = json.loads(path.read_text())
        data["ai_opportunities"][0].pop("human_gate")
        dump(path, data)
        self.assertTrue(any("profession AI opportunity 0 missing field: human_gate" in error for error in validate(self.root)))

    def test_long_marker_shell_course_still_fails(self) -> None:
        text = "# Decorative course\n\n" + "\n\n".join(
            f"{marker}\n\n" + ("polished but non-actionable prose " * 12) for marker in COURSE_MARKERS
        )
        write(self.root / "courses/example/course.md", text)
        self.assertTrue(any("runnable command block" in error for error in validate(self.root)))

    def test_transfer_label_without_transfer_contract_fails(self) -> None:
        path = self.root / "courses/example/video/lesson-experience.json"
        data = json.loads(path.read_text())
        stage = next(item for item in data["stages"] if item["stage_id"] == "transfer-challenge")
        for field in ["source_context", "target_context", "invariant", "must_change", "success_criterion"]:
            stage.pop(field, None)
        dump(path, data)
        self.assertTrue(any("transfer challenge missing field" in error for error in validate(self.root)))

    def test_live_source_check_rejects_nonexistent_url(self) -> None:
        path = self.root / "research/source-ledger.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rows[0]["url"] = "http://127.0.0.1:9/does-not-exist"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        self.assertTrue(any("failed live URL verification" in error for error in verify_source_urls(self.root, {"S0"})))


if __name__ == "__main__":
    unittest.main()
