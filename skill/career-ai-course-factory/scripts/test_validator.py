#!/usr/bin/env python3
"""Regression tests for fail-closed AI course package gates."""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from validate_career_package import COURSE_FILES, COURSE_MARKERS, validate, verify_source_urls
from build_source_assimilation_ledger import inventory_source


def write(path: Path, content: str = "ok") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def dump(path: Path, data: object) -> None:
    write(path, json.dumps(data))


def sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


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
    write(root / "human-review/04-完整方案审计.md", f"# 完整方案审计\n\n## 方案单元\n\n{readable_body}\n\n## 完整性结论\n\n{readable_body}\n\n## 运行证据\n\n{readable_body}\n\n## 架构与决策\n\n{readable_body}\n\n## 缺口与风险\n\n{readable_body}\n\n## 发布门禁\n\n{readable_body}")
    solution_body = "This section defines concrete scope, actors, architecture boundaries, runtime failure handling, evidence, ownership, acceptance, unresolved risks, and the exact maturity claim for the professional solution. " * 14
    write(root / "solution-architecture.md", "# Solution architecture\n\n" + "\n\n".join(
        f"{marker}\n\n{solution_body}" for marker in [
            "## Solution units", "## Scope and boundaries", "## Architecture views",
            "## Decisions and trade-offs", "## Traceability", "## Acceptance gates",
            "## Maturity and evidence", "## Risks and unknowns",
        ]
    ))
    write(root / "tutorial/README.md", f"# Tutorial\n\n## 如何使用\n\n{readable_body}\n\n## 教程结构\n\n{readable_body}\n\n## 当前完成度\n\n{readable_body}")
    write(root / "tutorial/course-tree.md", f"# Tree\n\n## 文档导航\n\n{readable_body}\n\n## 模块\n\n{readable_body}\n\n## 页面状态\n\n{readable_body}")
    write(root / "tutorial/page-template.md", f"# Template\n\n## 页面顶部\n\n{readable_body}\n\n## 通俗解释\n\n{readable_body}\n\n## 自己动手\n\n{readable_body}\n\n## 完成检查\n\n{readable_body}\n\n## 证据边界\n\n{readable_body}")
    tutorial_modules = [
        {"module_id":f"module-{index}","title":f"Module {index}","learner_result":"complete a professional result","order":index}
        for index in range(4)
    ]
    tutorial_pages = []
    for index in range(15):
        tutorial_pages.append({
            "page_id":f"page-{index}","slug":f"page-{index}","module_id":f"module-{min(index // 4, 3)}",
            "title":f"Tutorial page {index}","document_type":"professional-how-to","reader_job":"do",
            "audience":["practitioner"],
            "scope":{"inScope":["execute the bounded fixture"],"outOfScope":["production effectiveness"],"assumptions":["fixture inputs are available"]},
            "claims":["The bounded fixture demonstrates the documented procedure."],
            "document_contract":{
                "documentType":"professional-how-to","readerJob":"do","audience":["practitioner"],
                "scope":{"inScope":["execute the bounded fixture"],"outOfScope":["production effectiveness"],"assumptions":["fixture inputs are available"]},
                "claims":["The bounded fixture demonstrates the documented procedure."],
                "procedure":{"prerequisites":[],"inputs":["fixture"],"steps":["run"],"expectedResults":["PASS"],"recovery":["preserve failure evidence"],"rollback":"restore the fixture"},
            },
            "delivery_mode":"guided-lab","level":"L1",
            "order":index,"display_number":index + 1,"prerequisite_ids":[] if index == 0 else [f"page-{index-1}"],"scenario_ids":["scenario-0"],
            "learner_result":"produce a checked result","artifact":"report","keywords":["AI","quality"],
            "evidence_status":"fixture-tested", "delivery_status":"fixture-tested","updated_at":"2026-01-01",
            "source_ids":["S0"],"previous_page_id":"" if index == 0 else f"page-{index-1}",
            "next_page_id":"" if index == 14 else f"page-{index+1}",
            "architecture":{"title":"Evidence workflow","caption":"A complete professional workflow with explicit evidence and decision boundaries.","nodes":["input","analysis","artifact","execution","decision"]},
            "materials":[{"title":"Runnable fixture","description":"A repository-owned tested script for the lesson.","href":"materials/example.py","kind":"script","validation":"fixture-tested"},{"title":"Fixture input","description":"A versioned learner input.","href":"materials/input.json","kind":"fixture","validation":"fixture-tested"}],
            "content_sections":{"outcome":"build a gate","professional_relevance":"release evidence","plain_explanation":"a gate is a repeatable check","smallest_example":"one case","learner_action":"run the command","expected_result":"visible PASS","common_errors":"empty evidence","completion_check":"red green proof","evidence_boundary":"fixture only"}
        })
    write(root / "site/public/materials/example.py", "print('PASS')\n")
    write(root / "site/public/materials/input.json", "{}\n")
    for index in range(15):
        write(root / f"site/public/visuals/page-{index}.svg", f'<svg xmlns="http://www.w3.org/2000/svg"><title>Page {index} evidence flow</title><text x="10" y="20">input analysis artifact evidence decision</text></svg>\n')
    tutorial_ids = [page["page_id"] for page in tutorial_pages]
    dump(root / "tutorial/tutorial-site.json", {"tutorial_id":"career-ai","title":"Career AI Tutorial","audience":"beginner","updated_at":"2026-01-01","default_page_id":"page-0","release_scope":{"mode":"validated-subset","promised_page_ids":tutorial_ids,"catalog_complete":False,"validated_at":"2026-01-01"},"modules":tutorial_modules,"pages":tutorial_pages})
    dump(root / "research/catalog-manifest.json", {
        "schema_version":"1.0", "catalog_id":"career-ai", "content_version":"2026.1",
        "page_ids":tutorial_ids, "previous_validated_page_ids":tutorial_ids,
        "pages":[{"page_id":page_id,"support_bundle_id":"shared-example"} for page_id in tutorial_ids],
    })
    dump(root / "research/support-ownership.json", {
        "schema_version":"1.0", "bundles":[{
            "bundle_id":"shared-example", "owner_page_ids":tutorial_ids, "shared":True,
            "applicability":"The same deterministic fixture is intentionally reused by every validator fixture page.",
            "material_refs":["materials/example.py", "materials/input.json"],
        }],
    })
    dump(root / "research/executability-audit.json", {
        "schema_version":"1.0", "audit_id":"exec-2026-01-01", "audited_at":"2026-01-01T00:00:00Z",
        "pages":[{"page_id":page_id,"verdict":"PASS","finding_count":0} for page_id in tutorial_ids],
    })
    page_id_blob = " ".join(page["page_id"] for page in tutorial_pages)
    html = f'''<!doctype html><html><head><meta charset="utf-8"><title>Tutorial</title><style>{"body{{color:#222}}" * 500}</style></head><body><input id="tutorial-search"><nav id="course-nav">{page_id_blob}</nav><main id="tutorial-content">{readable_body * 10}</main><aside id="page-toc"></aside><div id="progress-bar"></div><script>const COURSE_DATA = {json.dumps(tutorial_pages)};</script></body></html>'''
    write(root / "tutorial/index.html", html)
    for page in tutorial_pages:
        topic_dir = root / f"research/topics/{page['page_id']}"
        write(topic_dir / "research-brief.md", "# Research brief\n\nControlling question, learner baseline, professional decision, system boundary, failure cost, exclusions, freshness and learner proof.\n")
        source_fields = ["source_id", "url", "title", "source_type", "source_family", "publisher_group", "accessed_at", "version_date", "evidence_lane", "supports", "does_not_support", "limitations", "opened_status"]
        with (topic_dir / "source-pack.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=source_fields)
            writer.writeheader()
            lanes = ["professional-baseline", "ai-primary", "implementation", "practitioner-failure", "competitor-course"]
            types = ["standard", "official-doc", "repository", "issue-discussion", "course"]
            for source_index in range(10):
                writer.writerow({
                    "source_id":f"{page['page_id']}-S{source_index}", "url":f"https://topic-source{source_index}.example.org/item",
                    "title":f"topic source {source_index}", "source_type":types[source_index % len(types)],
                    "source_family":f"topic-family-{source_index}", "publisher_group":f"topic-publisher-{source_index}",
                    "accessed_at":"2026-01-01", "version_date":"2026-01-01", "evidence_lane":lanes[source_index % len(lanes)],
                    "supports":"a bounded topic claim", "does_not_support":"production effectiveness",
                    "limitations":"synthetic validator fixture", "opened_status":"opened",
                })
        topic_body = "This independent topic record reconciles professional baseline, primary AI documentation, implementation evidence, practitioner failure, competitor teaching, counterevidence, metrics, architecture, interfaces, operations, security, learner action, failure injection, repair, and evidence limits. " * 8
        write(topic_dir / "evidence-synthesis.md", "# Evidence synthesis\n\n## Fact\n\n" + topic_body + "\n\n## Cross-source synthesis\n\n" + topic_body + "\n\n## Unknown\n\n" + topic_body)
        write(topic_dir / "engineering-blueprint.md", "# Engineering blueprint\n\n## Architecture and data flow\n\n" + topic_body + "\n\n## Metrics and decisions\n\n" + topic_body + "\n\n## Baseline failure repair\n\n" + topic_body)
        manuscript_chain = "The selected method links risk to an independent Oracle, a versioned Prompt, an Eval, and a Mutation that must turn the fixture red. Run `python3 materials/example.py` from `site/public` and preserve the observable exit code. "
        write(topic_dir / "manuscript.md", "# Learner manuscript\n\n## Professional problem\n\n" + manuscript_chain + topic_body + "\n\n## Runnable action\n\n" + topic_body + "\n\n## Failure and repair\n\n" + topic_body)
        write(topic_dir / "comparison.md", "# Independent comparison\n\n## Agreements\n\n" + topic_body + "\n\n## Disagreements\n\n" + topic_body + "\n\n## Adjudication\n\n" + topic_body)
        write(topic_dir / "validation.md", "# Validation\n\n## Research coverage\n\nPASS: all required evidence lanes and source limits were reviewed.\n\n## Claim traceability\n\nPASS: pivotal claims trace to opened sources or explicit inference.\n\n## Runnable lab\n\nPASS: baseline, fault and repair steps have repository-owned files and observable results.\n\n## Independent comparison\n\nPASS: an independent reviewer compared two research runs and adjudicated disagreements.\n\n## Publication verdict\n\nPASS: fixture-level publication only; no production effectiveness claim.\n")
        dump(topic_dir / "research-runs.json", {
            "topic_id":page["page_id"],
            "runs":[
                {"run_id":"official-and-standard", "lane":"primary", "role":"researcher", "output_ref":"source-pack.csv", "status":"complete"},
                {"run_id":"implementation-and-failure", "lane":"implementation", "role":"researcher", "output_ref":"evidence-synthesis.md", "status":"complete"},
            ],
            "comparison":{"reviewer":"independent-critic", "input_run_ids":["official-and-standard", "implementation-and-failure"], "output_ref":"comparison.md", "verdict":"pass"},
        })
        claim_ids = ["C-01", "C-02", "C-03"]
        dump(topic_dir / "claim-inventory.json", {
            "schema_version":"claim-inventory.v1", "topic_id":page["page_id"],
            "root_manifest":{"schema_version":"locator-root-manifest.v1", "package_relative_priority":True, "roots":{"topic":{"kind":"topic", "path":f"research/topics/{page['page_id']}"}, "package":{"kind":"package", "path":"."}}},
            "extraction":{
                "author_id":"course-author", "independent_auditor_id":"claim-auditor",
                "source_files":["manuscript.md"],
                "source_hashes":{"manuscript.md":sha256(topic_dir / "manuscript.md")},
                "locator_ledger":[{"locator":"topic:manuscript.md", "canonical_key":"topic:manuscript.md", "root_alias":"topic", "resolved_path":"manuscript.md", "sha256":sha256(topic_dir / "manuscript.md"), "selector":None, "selector_kind":None, "selector_value":None, "line_start":None, "line_end":None, "line_count":len((topic_dir / "manuscript.md").read_text().splitlines()), "claim_ids":claim_ids}],
                "unmapped_propositions":0,
            },
            "claims":[
                {"claim_id":claim_id, "statement":f"Independent proposition {claim_id}", "claim_type":"decision-rule", "risk":"high", "scope":"synthetic validator fixture", "source_locations":["topic:manuscript.md"], "required_dimensions":["terminology-boundary", "counterevidence"], "proposed_disposition":"SCOPED"}
                for claim_id in claim_ids
            ],
        })
        deep_runs = []
        saturation_claims = []
        for claim_id in claim_ids:
            run_ids = []
            for round_number, phase in ((1, "initial-deep-research"), (2, "counterevidence")):
                run_id = f"{claim_id.lower()}-r{round_number}"
                run_ids.append(run_id)
                run_dir = topic_dir / "deep-research" / run_id
                write(run_dir / "request.md", f"# Request\n\nResearch only {claim_id}.\n")
                dump(run_dir / "raw-response.json", {
                    "id":f"resp_{run_id}", "status":"completed", "model":"deep-research-test-model",
                    "output":[
                        {"type":"web_search_call", "id":f"ws_{run_id}", "status":"completed", "action":{"type":"open_page", "url":"https://example.com/source", "sources":[{"url":"https://example.com/source"}]}},
                        {"type":"message", "role":"assistant", "content":[{"type":"output_text", "text":f"Evidence and counterevidence for {claim_id}.", "annotations":[{"type":"url_citation", "url":"https://example.com/source", "title":"Source", "start_index":0, "end_index":8}]}]},
                    ],
                })
                write(run_dir / "report.md", f"Evidence and counterevidence for {claim_id}.\n")
                dump(run_dir / "citations.json", {"citations":[{"url":"https://example.com/source", "title":"Source", "start_index":0, "end_index":8}]})
                dump(run_dir / "tool-calls.json", {"calls":[{"type":"web_search_call", "id":f"ws_{run_id}", "status":"completed", "action":{"type":"open_page", "url":"https://example.com/source", "sources":[{"url":"https://example.com/source"}]}}]})
                dump(run_dir / "source-opening-ledger.json", {
                    "schema_version":"source-opening-ledger.v1", "run_id":run_id,
                    "response_or_export_id":f"resp_{run_id}",
                    "discovered_urls":["https://example.com/source"],
                    "cited_urls":["https://example.com/source"],
                    "opening_events":[{
                        "event_id":f"ws_{run_id}", "tool_call_id":f"ws_{run_id}",
                        "action_type":"open_page", "timestamp":"", "url":"https://example.com/source",
                    }],
                    "discovered_source_count":1, "cited_source_count":1, "opened_source_count":1,
                    "limitations":[],
                })
                deep_runs.append({
                    "run_id":run_id, "claim_ids":[claim_id], "round":round_number, "phase":phase,
                    "provider":"openai", "surface":"openai-responses-api", "model_or_feature":"deep-research-test-model",
                    "response_or_export_id":f"resp_{run_id}", "started_at":"2026-01-01T00:00:00Z", "completed_at":"2026-01-01T00:01:00Z",
                    "request_path":f"deep-research/{run_id}/request.md", "raw_response_path":f"deep-research/{run_id}/raw-response.json",
                    "report_path":f"deep-research/{run_id}/report.md", "citations_path":f"deep-research/{run_id}/citations.json",
                    "tool_calls_path":f"deep-research/{run_id}/tool-calls.json",
                    "source_opening_ledger_path":f"deep-research/{run_id}/source-opening-ledger.json",
                    "input_sha256":sha256(run_dir / "request.md"), "output_sha256":sha256(run_dir / "raw-response.json"),
                    "data_sources":["web_search"], "tool_call_count":1, "citation_count":1,
                    "discovered_source_count":1, "cited_source_count":1, "opened_source_count":1,
                    "status":"completed", "limitations":["synthetic validator receipt"],
                })
            saturation_claims.append({
                "claim_id":claim_id, "run_ids":run_ids,
                "coverage_dimensions":[
                    {"dimension":"terminology-boundary", "status":"covered", "evidence_or_reason":run_ids[0]},
                    {"dimension":"counterevidence", "status":"covered", "evidence_or_reason":run_ids[1]},
                ],
                "contradiction_status":"resolved", "two_consecutive_rounds_without_material_change":True,
                "conclusive_primary_authority_exception":False, "final_disposition":"SCOPED", "verdict":"SATURATED",
                "round_assessments":[
                    {"run_id":run_ids[0], "material_change":False, "assessment":"The initial fixture stayed within its declared scope."},
                    {"run_id":run_ids[1], "material_change":False, "assessment":"The counterevidence fixture did not change the bounded disposition."},
                ],
                "rationale":"The fixture preserves scope and counterevidence.",
            })
        dump(topic_dir / "deep-research-receipts.json", {
            "schema_version":"deep-research-receipts.v1", "topic_id":page["page_id"], "runs":deep_runs,
        })
        write(topic_dir / "contradiction-matrix.md", "# Contradiction matrix\n\n## Claims\n\n" + "\n".join(f"### {claim_id}\n\nFixture contradictions are scoped and adjudicated.\n" for claim_id in claim_ids))
        dump(topic_dir / "research-saturation.json", {
            "schema_version":"research-saturation.v1", "topic_id":page["page_id"],
            "independent_auditor_id":"claim-auditor", "claims":saturation_claims, "overall_verdict":"PASS",
        })
        dump(topic_dir / "lab-manifest.json", {
            "topic_id":page["page_id"], "page_id":page["page_id"], "working_directory":"site/public",
            "required_files":["materials/example.py", "materials/input.json"],
            "steps":[
                {"step_id":"baseline", "kind":"command", "command":"python3 materials/example.py", "expected_exit_code":0, "expected_artifacts":["materials/input.json"]},
                {"step_id":"fault", "kind":"mutation", "command":"python3 materials/example.py --fault", "expected_exit_code":1, "expected_artifacts":["materials/input.json"]},
                {"step_id":"repair", "kind":"command", "command":"python3 materials/example.py", "expected_exit_code":0, "expected_artifacts":["materials/input.json"]},
            ],
            "failure_cycle":{"baseline_step_id":"baseline", "fault_step_id":"fault", "repair_step_id":"repair"},
            "evidence_boundary":"synthetic fixture only",
        })
        dump(topic_dir / "promotion-receipt.json", {
            "schema_version":"1.0", "page_id":page["page_id"], "verdict":"PASS",
            "research_package_files":[
                "research-brief.md", "source-pack.csv", "research-runs.json", "evidence-synthesis.md",
                "engineering-blueprint.md", "manuscript.md", "comparison.md", "lab-manifest.json", "validation.md",
                "projection-ledger.json", "claim-inventory.json", "deep-research-receipts.json",
                "contradiction-matrix.md", "research-saturation.json",
            ],
            "editorial_score":95, "boundary_preservation_score":100,
            "executability_audit_ref":"research/executability-audit.json",
            "executability_audit_hash":sha256(root / "research/executability-audit.json"),
            "material_hashes":{
                "materials/example.py":sha256(root / "site/public/materials/example.py"),
                "materials/input.json":sha256(root / "site/public/materials/input.json"),
            },
            "validated_at":"2026-01-01T00:00:00Z", "reviewer":"independent-fixture-reviewer",
        })
        write(topic_dir / "research-package.md", f"# {page['page_id']} research index\n\nSee the mandatory split research files, independent comparison, research-run provenance and lab manifest in this directory.\n")

        page_content_hash = "sha256:" + hashlib.sha256(
            json.dumps(page["content_sections"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        dump(topic_dir / "projection-ledger.json", {
            "schema_version":"1.0", "topic_id":page["page_id"],
            "author_id":"course-author",
            "manuscript_sha256":sha256(topic_dir / "manuscript.md"),
            "page_content_sha256":page_content_hash,
            "claims":[
                {"claim_id":"C-01", "manuscript_locator":"manuscript.md#Professional problem", "meaning":"The independent Oracle must reject a plausible but unsupported result.", "kind":"decision-rule", "disposition":"projected", "page_target":f"{page['page_id']}#content_sections.completion_check", "rationale":"The completion check preserves the decision rule.", "owner":"course owner"},
                {"claim_id":"C-02", "manuscript_locator":"manuscript.md#Failure and repair", "meaning":"A seeded fault must turn the validation red before repair.", "kind":"failure-mode", "disposition":"projected", "page_target":f"{page['page_id']}#content_sections.common_errors", "rationale":"The learner page preserves the failure path.", "owner":"course owner"},
                {"claim_id":"C-03", "manuscript_locator":"manuscript.md#Evidence boundary", "meaning":"Fixture evidence does not prove live or production validity.", "kind":"boundary", "disposition":"projected", "page_target":f"{page['page_id']}#content_sections.evidence_boundary", "rationale":"The evidence boundary remains explicit.", "owner":"course owner"},
            ],
            "counts":{"total":3,"projected":3,"condensed":0,"deferred":0,"rejected":0,"unaccounted":0},
            "reviewer":"independent projection reviewer", "verdict":"PASS",
        })

    dump(root / "research/capability-declarations.json", {
        "schema_version":"1.0",
        "capabilities":[{
            "capability":"ai-system-evaluation", "topics":tutorial_ids,
            "status":"fixture-tested", "owner":"quality lead",
            "evidence":["research/executability-audit.json"],
        }],
    })
    dump(root / "research/capability-profiles.json", {
        "schema_version":"1.0",
        "pages":[{
            "page_id":page_id, "capabilities":["ai-system-evaluation"],
            "rationale":"The lesson evaluates an AI-related behavior through an independent deterministic gate.",
            "risk":"A plausible result could pass without observable evidence.",
            "reviewer":"independent capability reviewer", "reviewed_at":"2026-01-01T00:00:00Z",
            "evidence_refs":[f"research/topics/{page_id}/lab-manifest.json"],
        } for page_id in tutorial_ids],
    })
    dump(root / "research/professional-evidence.json", {
        "schema_version":"1.0",
        "pages":[{
            "page_id":page_id, "maturity_claim":"fixture-tested",
            "model":{"status":"NOT_RUN", "receipt_refs":[], "limitations":"No real model or provider was invoked."},
            "integration":{"status":"NOT_RUN", "receipt_refs":[], "limitations":"No enterprise target system was invoked."},
            "clean_room":{
                "status":"PASS", "receipt_refs":[f"research/topics/{page_id}/lab-manifest.json"],
                "limitations":"Fresh deterministic fixture only.", "command":"python3 materials/example.py",
                "working_directory":"site/public", "expected_exit_code":0,
                "artifact_hash":sha256(root / "site/public/materials/example.py"),
                "platforms":["python3"],
                "command_surfaces":[f"research/topics/{page_id}/manuscript.md", f"research/topics/{page_id}/lab-manifest.json"],
            },
            "practitioner":{"status":"NOT_RUN", "receipt_refs":[], "limitations":"No qualified practitioner review."},
            "learner":{"status":"NOT_RUN", "receipt_refs":[], "limitations":"No novice learning-effect study."},
        } for page_id in tutorial_ids],
    })
    write(root / "research/user-input/source.md", "# Quality evidence\n\nUse evidence-bound quality decisions.\n\n## System boundary\n\nMap inputs, risks, Oracles, faults, and decisions.\n")
    source_inventory = inventory_source(root / "research/user-input/source.md", "USER-1", root)
    source_inventory["source"].update({"authority":"user input", "scope":"fixture-scoped candidate guidance", "owner":"course owner"})
    for item in source_inventory["sections"] + source_inventory["atoms"]:
        item.update({
            "meaning":"Preserve the user-provided professional rule and its evidence boundary.",
            "disposition":"incorporated", "target_refs":["tutorial/tutorial-site.json"],
            "rationale":"The bounded concept is taught directly and remains source-labelled.",
            "owner":"course owner", "evidence_refs":["research/user-input/source.md"],
        })
    disposition_count = len(source_inventory["sections"]) + len(source_inventory["atoms"])
    dump(root / "research/source-assimilation-ledger.json", {
        "schema_version":"1.0", "inventory_version":"source-assimilation-v1",
        "sources":[source_inventory["source"]], "sections":source_inventory["sections"], "atoms":source_inventory["atoms"],
        "coverage_receipt":{
            "source_count":1, "section_count":len(source_inventory["sections"]), "atom_count":len(source_inventory["atoms"]),
            "accounted_section_count":len(source_inventory["sections"]), "accounted_atom_count":len(source_inventory["atoms"]),
            "disposition_counts":{"incorporated":disposition_count}, "unaccounted_ids":[],
            "inventory_command":"python3 scripts/build_source_assimilation_ledger.py --package-root . --source USER-1=research/user-input/source.md --output research/source-assimilation-ledger.json",
            "reviewer":"independent source coverage reviewer", "reviewed_at":"2026-01-01T00:00:00Z", "verdict":"PASS",
        },
    })
    dump(root / "research/source-semantic-projection.json", {
        "schema_version":"1.0", "source_ledger_ref":"research/source-assimilation-ledger.json",
        "author_id":"course-author",
        "source_ledger_sha256":sha256(root / "research/source-assimilation-ledger.json"),
        "units":[
            {"unit_id":"SEM-01", "source_item_ids":[source_inventory["atoms"][0]["id"]], "function_kind":"concept-model", "protected_function":"Teach the evidence-bound quality decision as a plain mental model.", "page_refs":["tutorial/tutorial-site.json#page-0#content_sections.plain_explanation"], "visual_refs":[], "reusable_asset_refs":["site/public/materials/input.json"], "exercise_refs":["research/learner-usability-reuse.json"], "adaptation":{"mode":"direct", "scope":"fixture"}, "verification":"The learner page states the independent evidence decision.", "owner":"course owner", "status":"projected"},
            {"unit_id":"SEM-02", "source_item_ids":[source_inventory["atoms"][1]["id"]], "function_kind":"visual", "protected_function":"Show the system boundary as a visible input-to-decision flow.", "page_refs":["tutorial/tutorial-site.json#page-0#content_sections.professional_relevance"], "visual_refs":["site/public/visuals/page-0.svg"], "reusable_asset_refs":[], "exercise_refs":[], "adaptation":{"mode":"direct", "scope":"fixture"}, "verification":"The SVG preserves the boundary nodes and flow.", "owner":"course owner", "status":"projected"},
            {"unit_id":"SEM-03", "source_item_ids":[source_inventory["atoms"][0]["id"]], "function_kind":"template", "protected_function":"Give the learner an editable input artifact instead of prose only.", "page_refs":["tutorial/tutorial-site.json#page-0#content_sections.learner_action"], "visual_refs":[], "reusable_asset_refs":["site/public/materials/input.json"], "exercise_refs":["research/learner-usability-reuse.json"], "adaptation":{"mode":"direct", "scope":"fixture"}, "verification":"The input file is repository-owned and referenced by the learner action.", "owner":"course owner", "status":"projected"},
            {"unit_id":"SEM-04", "source_item_ids":[source_inventory["atoms"][1]["id"]], "function_kind":"threshold-policy", "protected_function":"Keep numeric policy scoped to the fixture rather than universalizing it.", "page_refs":["tutorial/tutorial-site.json#page-0#content_sections.evidence_boundary"], "visual_refs":[], "reusable_asset_refs":["site/public/materials/input.json"], "exercise_refs":[], "adaptation":{"mode":"parameterized", "scope":"fixture", "owner":"quality lead", "evidence_ref":"research/user-input/source.md", "uncertainty":"No production calibration."}, "verification":"The page labels the threshold as fixture-scoped.", "owner":"quality lead", "status":"adapted"},
        ],
        "coverage":{"required_source_item_ids":[item["id"] for item in source_inventory["atoms"]], "covered_source_item_ids":[item["id"] for item in source_inventory["atoms"]], "unaccounted_source_item_ids":[], "function_counts":{"concept-model":1,"visual":1,"template":1,"threshold-policy":1}, "verdict":"PASS"},
        "reviewer":"independent semantic projection reviewer", "reviewed_at":"2026-01-01T00:00:00Z", "verdict":"PASS",
    })
    dump(root / "research/learner-usability-reuse.json", {
        "schema_version":"1.0", "verdict":"PASS-DESIGN",
        "learner_evidence_boundary":{"status":"NOT_RUN", "limitations":"No observed target learner comprehension or transfer study."},
        "pages":[{
            "page_id":page_id, "display_number":index + 1,
            "prerequisite_ids":[] if index == 0 else [f"page-{index-1}"], "assumed_knowledge":["ai"],
            "terms_introduced":[{"term":f"concept-{index}", "plain_definition":"A bounded observable professional quality concept.", "first_use_ref":f"research/topics/{page_id}/manuscript.md"}],
            "terms_used":[f"concept-{index}"], "mental_model":"Input passes through an independent check before a human decision.",
            "worked_example":{"input":"one valid fixture", "expected_observation":"the baseline returns PASS and preserves evidence"},
            "counterexample":{"input":"one seeded regression", "expected_observation":"the fault run returns non-zero and names the finding"},
            "learner_action":{"input_ref":"site/public/materials/input.json", "action":"run the repository-owned fixture", "expected_result":"an observable red-green result"},
            "failure_diagnosis":{"symptom":"fault did not turn red", "diagnosis_steps":["check fixture", "check Oracle"], "repair":"restore the independent assertion", "rerun_check":"baseline 0, fault 1, repair 0"},
            "comprehension_checks":[{"question":"Why is plausible prose insufficient?", "expected_answer":"It lacks an independent observable Oracle.", "common_misconception":"The model can approve its own answer."}],
            "reusable_artifacts":[{
                "artifact_id":f"artifact-{page_id}", "path":"site/public/materials/example.py", "purpose":"run a bounded quality gate",
                "inputs":["fixture input"], "editable_fields":["scenario binding", "expected invariant"], "outputs":["exit code", "evidence record"],
                "adaptation_steps":["replace the scenario fixture and update the source refs", "run the fault and repair cycle and preserve evidence"],
                "validation":{"method":"python3 site/public/materials/example.py", "expected_evidence":"baseline exit 0 and a seeded fault must turn red"},
                "limitations":"synthetic fixture; no enterprise or live-model proof", "owner":"learner with reviewer",
            }],
        } for index, page_id in enumerate(tutorial_ids)],
    })
    dump(root / "research/visual-sequence-manifest.json", {
        "schema_version":"1.0", "ordered_page_ids":tutorial_ids, "verdict":"PASS",
        "pages":[{
            "page_id":page_id, "display_number":index + 1,
            "prerequisite_ids":[] if index == 0 else [f"page-{index-1}"],
            "knowledge_relationship":"input to evidence to human decision",
            "required_visual_kinds":["evidence-flow"],
            "visuals":[{
                "visual_id":f"visual-{page_id}", "kind":"evidence-flow", "purpose":"show the topic-specific evidence decision path",
                "source_path":f"site/public/visuals/{page_id}.svg", "alt_text":f"{page_id} input, analysis, artifact, evidence and decision flow",
                "caption":"The fixture demonstrates the evidence path but does not prove live or production validity.",
                "nodes":[f"{page_id}-input", f"{page_id}-analysis", f"{page_id}-artifact", f"{page_id}-evidence", f"{page_id}-decision"],
                "edges":["input->analysis", "analysis->artifact", "artifact->evidence", "evidence->decision"],
                "source_refs":[f"research/topics/{page_id}/engineering-blueprint.md"],
            }],
        } for index, page_id in enumerate(tutorial_ids)],
    })
    review_path = root / "human-review/04-完整方案审计.md"
    scope_hash = "sha256:" + hashlib.sha256(json.dumps(tutorial_ids, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    dump(root / "research/status-registry.json", {
        "schema_version":"1.0",
        "records":[{
            "record_id":"course-verdict-current", "artifact_type":"course-verdict", "scope_id":"public-tutorial",
            "path":"human-review/04-完整方案审计.md", "as_of":"2026-01-01T00:00:00Z",
            "scope_hash":scope_hash, "artifact_hash":sha256(review_path), "status":"current",
            "supersedes":[], "evidence_refs":["research/executability-audit.json"],
        }],
    })
    write(root / "dist/site/materials/example.py", (root / "site/public/materials/example.py").read_text())
    write(root / "dist/site/materials/input.json", (root / "site/public/materials/input.json").read_text())
    archive_path = root / "dist/course-release.zip"
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.write(root / "dist/site/materials/example.py", "site/materials/example.py")
        archive.write(root / "dist/site/materials/input.json", "site/materials/input.json")
    dump(root / "research/publication-closure.json", {
        "schema_version":"1.0",
        "canonical_source_ref":"research/catalog-manifest.json",
        "canonical_source_hash":sha256(root / "research/catalog-manifest.json"),
        "tutorial_ref":"tutorial/tutorial-site.json",
        "tutorial_hash":sha256(root / "tutorial/tutorial-site.json"),
        "static_export_root":"dist/site", "archive_ref":"dist/course-release.zip",
        "material_entries":[
            {
                "page_id":page["page_id"], "href":material["href"],
                "source_ref":f"site/public/{material['href']}",
                "dist_ref":f"dist/site/{material['href']}",
                "archive_member":f"site/{material['href']}",
                "sha256":sha256(root / f"site/public/{material['href']}"),
            }
            for page in tutorial_pages for material in page["materials"]
        ],
    })
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
    proof = {
        "receipt_id":"receipt-fixture", "solution_id":"solution-0", "scenario_id":"scenario-0",
        "evidence_scope":"fixture", "environment":{"runtime":"python3", "class":"local deterministic fixture"},
        "run_at":"2026-01-01T00:00:00Z", "tools":[{"name":"python", "version":"3.x"}],
        "command":["python3 ok.py", "python3 bad.py", "python3 ok.py"], "commands":["baseline","mutation","repair"],
        "working_directory":"courses/example/lab", "input_hashes":{"input":"sha256:fixture"},
        "output_hashes":{"report":"sha256:fixture-output"},
        "assertions":[{"name":"baseline passes", "expected":0, "observed":0}, {"name":"mutation fails", "expected":1, "observed":1}, {"name":"repair passes", "expected":0, "observed":0}],
        "expected_verdict":"red-green-pass", "actual_verdict":"red-green-pass",
        "failure_injection":"bad.py exits non-zero", "red_evidence":{"exit_code":1, "verdict":"FAIL"},
        "repair":"restore ok.py path", "green_evidence":{"exit_code":0, "verdict":"PASS"},
        "baseline":{"exit_code":0,"verdict":"PASS"},"mutation":{"exit_code":1,"verdict":"FAIL"},"repair_result":{"exit_code":0,"verdict":"PASS"},
        "repair":{"exit_code":0,"verdict":"PASS"}, "reviewer":"fixture maintainer", "limitations":["fixture only; no live adapter"]
    }
    dump(course / "evidence/execution-evidence.json", proof)
    dump(course / "materials/material-provenance.json", {"materials":[
        {"material_id":f"M{index}","path":path,"purpose":"learner use","source_ids":["S0"],"scenario_ids":["scenario-0"],"generated_from":["fixture"],"license_or_usage":"original","validation_status":"fixture-tested","validation_evidence":["proof"],"contains_synthetic_data":True,"limitations":"fixture"}
        for index, path in enumerate(["materials/quickstart.md","materials/reusable-skill.md","materials/sample-input.md","materials/expected-output.md","materials/verification-checklist.md"])
    ]})
    stage_ids = ["cold-open-failure", "stakes-and-promise", "before-after", "plain-mental-model", "guided-demo", "failure-diagnosis", "learner-practice", "transfer-challenge", "artifact-handoff"]
    dump(course / "video/lesson-experience.json", {"lesson_id":"lesson","target_learner":"beginner tester","level":"L2-control-and-check","estimated_minutes":10,"job_result":"build a gate","artifact":"report","stages":[
        {"stage_id":stage,"instructor_action":"show concrete professional evidence","learner_action":"predict and perform the required action","expected_observation":"a visible machine-checkable result","debrief":"explain the professional and AI boundary","artifact_or_assessment":"a saved learner-owned assessment artifact", **({"source_context":"customer support refund policy","target_context":"neighbor scenario","invariant":"the release decision remains evidence based","must_change":["dataset","risk threshold"],"success_criterion":"the new scenario fails on its own seeded regression"} if stage == "transfer-challenge" else {})} for stage in stage_ids
    ],"interaction_prompts":["predict","diagnose","transfer"],"recovery_path":"reset fixture","evidence_status":"fixture-tested","limitations":"not learner-tested"})

    dimension_ids = [
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
    ]
    view_kinds = ["context", "building-block", "runtime", "deployment", "data-flow", "security-trust-boundary"]
    architecture_views = []
    for kind in view_kinds:
        artifact_ref = f"architecture/{kind}.md"
        write(root / artifact_ref, f"# {kind}\n\n```mermaid\nflowchart LR\nA[Actor] --> B[Input boundary]\nB --> C[Processing]\nC --> D[Evidence store]\nD --> E[Human decision]\nC --> F[Failure handler]\nF --> E\n```\n\nThis view defines the solution boundary, five owned components, ordered evidence flow, failure containment, telemetry points, and the human decision. It supports accepted decisions ADR-1 and ADR-2 and states what remains outside the fixture proof.\n")
        architecture_views.append({
            "view_id":f"view-{kind}", "kind":kind, "title":f"{kind} view",
            "purpose":"show owned boundaries, evidence, failure handling, and the decision supported by this view",
            "artifact_ref":artifact_ref, "nodes":["actor","input","processing","evidence","human-decision","failure-handler"],
            "edges":["actor->input","input->processing","processing->evidence","evidence->human-decision","processing->failure-handler"],
            "boundary":"local fixture boundary with external actor and explicit human approval",
            "failure_path":"processing routes a seeded failure to containment and blocks the decision",
            "evidence_points":["command result","red report","green report"], "decision_ids":["ADR-1","ADR-2"],
        })
    dimensions = [{
        "dimension_id":dimension_id, "status":"complete",
        "question":f"How does {dimension_id} constrain the professional solution and its acceptance decision?",
        "decision":f"The fixture solution records an owned, reviewable and testable decision for {dimension_id}, with limits kept explicit.",
        "artifact_refs":["solution-architecture.md"], "evidence_refs":["receipt-fixture"], "reviewer":"fixture practitioner",
    } for dimension_id in dimension_ids]
    decisions = [
        {"decision_id":"ADR-1","context":"The learner needs deterministic red-green evidence without credentials.","options":["local deterministic fixture","uncontrolled live model"],"choice":"Use a local deterministic fixture as the default path.","tradeoffs":"Reproducibility is gained while live-model validity remains unproved.","owner":"quality lead","status":"accepted","revisit_evidence":"A controlled live adapter with preserved receipts."},
        {"decision_id":"ADR-2","context":"A human must own release interpretation after automated evidence is produced.","options":["automatic release","human evidence gate"],"choice":"Require the quality lead to approve the evidence gate.","tradeoffs":"Safer authority boundary with additional review latency.","owner":"quality lead","status":"accepted","revisit_evidence":"Approved policy for bounded automatic action."},
    ]
    traces = [{
        "coverage_cell_id":"CELL-00", "topic_id":page["page_id"], "page_id":page["page_id"],
        "scenario_id":"scenario-0", "artifact_ref":"site/public/materials/input.json",
        "command_ref":"site/public/materials/example.py", "execution_receipt_ref":"receipt-fixture",
        "assessment_ref":"courses/example/evidence/execution-evidence.json", "human_gate":"quality lead accepts the red-green evidence",
    } for page in tutorial_pages]
    acceptance_gates = [{
        "gate_id":f"gate-{kind}", "gate_kind":kind,
        "criterion":f"The {kind} decision has an inspectable artifact, evidence boundary, owner, and passing observation.",
        "evidence_ref":"courses/example/evidence/execution-evidence.json", "owner":"quality lead", "status":"pass",
    } for kind in ["design","functional","security","performance","reliability","operations","rollback","learner-transfer"]]
    dump(root / "research/solution-architecture.json", {
        "schema_version":"1.0", "profession_id":"c", "as_of":"2026-01-01",
        "solution_units":[{
            "solution_id":"solution-0", "title":"Deterministic AI quality gate", "business_outcome":"block a seeded AI regression before release",
            "failure_cost":"an unsupported AI result reaches a user or an operator decision", "owner":"quality lead", "reviewers":["fixture practitioner"],
            "scenario_ids":["scenario-0"], "page_ids":[page["page_id"] for page in tutorial_pages], "course_ids":["example"],
            "design_status":"complete", "execution_status":"fixture-tested", "practitioner_review_status":"reviewed", "publication_status":"pilot",
            "dimensions":dimensions, "architecture_views":architecture_views, "decisions":decisions, "traceability":traces,
            "execution_receipts":[{"receipt_id":"receipt-fixture","kind":"fixture","artifact_ref":"courses/example/evidence/execution-evidence.json","status":"pass","limitations":"local deterministic fixture only","reviewer":"fixture practitioner"}],
            "acceptance_gates":acceptance_gates,
            "residual_risks":[{"risk_id":"risk-live-adapter","severity":"medium","trigger":"the fixture is generalized to a live model","mitigation":"run a controlled integration adapter and re-review thresholds","owner":"quality lead","status":"open"}],
        }],
    })


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        build_valid(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual(validate(self.root), [])

    def test_blocked_cluster_route_manifest_is_consumed_by_package_gate(self) -> None:
        path = self.root / "research/research-cluster-redesign-2026-08-20/research-route-dry-run.json"
        dump(path, {
            "schema_version": "research-route-dry-run-manifest.v1", "dry_run_id": "dry-1", "generated_at": "now",
            "input_inventory_digests": ["sha256:" + "a" * 64], "map_digest": "sha256:" + "b" * 64,
            "status": "BLOCKED", "counts": {"missing_page_count": 0, "unexpected_page_count": 0},
            "routes": {"BLOCKED-UNCLASSIFIED": 1}, "reuse": {}, "invalidation": {}, "unclassified_count": 1,
        })
        errors = validate(self.root)
        self.assertTrue(any("cluster route manifest" in error and "not release-ready" in error for error in errors), errors)

    def test_clustered_source_manifest_requires_route_manifest(self) -> None:
        dump(self.root / "research/claim-source-manifest-2026-08-20.json", {"schema_version": "claim-source-manifest.v1"})
        errors = validate(self.root)
        self.assertTrue(any("claim-source manifest exists without a route dry-run manifest" in error for error in errors), errors)

    def test_user_source_cannot_be_silently_omitted(self) -> None:
        path = self.root / "research/source-assimilation-ledger.json"
        data = json.loads(path.read_text())
        data["atoms"] = data["atoms"][:-1]
        data["coverage_receipt"]["atom_count"] -= 1
        data["coverage_receipt"]["accounted_atom_count"] -= 1
        dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("atom inventory does not exactly match frozen sources" in error for error in errors), errors)

    def test_user_source_unmapped_atom_blocks_completion(self) -> None:
        path = self.root / "research/source-assimilation-ledger.json"
        data = json.loads(path.read_text())
        data["atoms"][0]["disposition"] = "UNMAPPED"
        dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("unmapped or invalid disposition" in error for error in errors), errors)

    def test_adapted_source_needs_a_real_learner_target(self) -> None:
        path = self.root / "research/source-assimilation-ledger.json"
        data = json.loads(path.read_text())
        data["atoms"][0].update({"disposition":"adapted", "target_refs":[]})
        dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("adapted item needs learner-facing target_refs" in error for error in errors), errors)

    def test_source_semantic_projection_is_mandatory(self) -> None:
        path = self.root / "research/source-semantic-projection.json"
        if path.exists():
            path.unlink()
        errors = validate(self.root)
        self.assertTrue(any("missing research/source-semantic-projection.json" in error for error in errors), errors)

    def test_source_semantic_projection_requires_exact_page_anchor(self) -> None:
        path = self.root / "research/source-semantic-projection.json"
        data = json.loads(path.read_text())
        data["units"][0]["page_refs"] = ["tutorial/tutorial-site.json"]
        dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("exact page and content anchor" in error for error in errors), errors)

    def test_source_semantic_projection_reviewer_must_be_independent(self) -> None:
        path = self.root / "research/source-semantic-projection.json"
        data = json.loads(path.read_text()); data["reviewer"] = data["author_id"]; dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("reviewer must be independent" in error for error in errors), errors)

    def test_source_visual_cannot_be_reduced_to_prose_only(self) -> None:
        path = self.root / "research/source-semantic-projection.json"
        data = json.loads(path.read_text())
        visual = next(item for item in data["units"] if item["function_kind"] == "visual")
        visual["visual_refs"] = []
        dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("visual function needs a rendered visual target" in error for error in errors), errors)

    def test_source_template_needs_a_directly_reusable_asset(self) -> None:
        path = self.root / "research/source-semantic-projection.json"
        data = json.loads(path.read_text())
        template = next(item for item in data["units"] if item["function_kind"] == "template")
        template["reusable_asset_refs"] = []
        dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("template function needs a reusable asset" in error for error in errors), errors)

    def test_unscoped_numeric_policy_cannot_be_projected_as_universal_truth(self) -> None:
        path = self.root / "research/source-semantic-projection.json"
        data = json.loads(path.read_text())
        threshold = next(item for item in data["units"] if item["function_kind"] == "threshold-policy")
        threshold["adaptation"] = {"mode":"direct", "scope":"universal"}
        dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("threshold-policy must be scoped, parameterized, blocked, or rejected" in error for error in errors), errors)

    def test_promoted_page_needs_research_to_page_projection_ledger(self) -> None:
        path = self.root / "research/topics/page-0/projection-ledger.json"
        if path.exists():
            path.unlink()
        errors = validate(self.root)
        self.assertTrue(any("page-0 missing projection-ledger.json" in error for error in errors), errors)

    def test_critical_research_claim_cannot_be_deferred_from_page(self) -> None:
        path = self.root / "research/topics/page-0/projection-ledger.json"
        data = json.loads(path.read_text())
        data["claims"][0]["disposition"] = "deferred"
        dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("critical claim cannot be deferred or rejected" in error for error in errors), errors)

    def test_projection_ledger_hashes_must_match_current_manuscript_and_page(self) -> None:
        path = self.root / "research/topics/page-0/projection-ledger.json"
        data = json.loads(path.read_text())
        data["manuscript_sha256"] = "sha256:" + "0" * 64
        dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("manuscript hash drift" in error for error in errors), errors)

    def test_projection_ledger_rejects_fake_page_anchor(self) -> None:
        path = self.root / "research/topics/page-0/projection-ledger.json"
        data = json.loads(path.read_text()); data["claims"][0]["page_target"] = "page-0#content_sections.does_not_exist"; dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("references a missing learner-page anchor" in error for error in errors), errors)

    def test_projection_ledger_reviewer_must_be_independent(self) -> None:
        path = self.root / "research/topics/page-0/projection-ledger.json"
        data = json.loads(path.read_text()); data["reviewer"] = data["author_id"]; dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("projection reviewer must be independent" in error for error in errors), errors)

    def test_tutorial_display_numbers_must_be_contiguous(self) -> None:
        path = self.root / "tutorial/tutorial-site.json"
        data = json.loads(path.read_text())
        data["pages"][1]["display_number"] = 76
        dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("display_number must be contiguous 1..N" in error for error in errors), errors)

    def test_beginner_term_must_be_explained_before_use(self) -> None:
        path = self.root / "research/learner-usability-reuse.json"
        data = json.loads(path.read_text())
        data["pages"][0]["terms_used"].append("rag")
        dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("uses terms before introduction" in error for error in errors), errors)

    def test_reusable_artifact_needs_adaptation_and_validation(self) -> None:
        path = self.root / "research/learner-usability-reuse.json"
        data = json.loads(path.read_text())
        data["pages"][0]["reusable_artifacts"][0]["editable_fields"] = []
        data["pages"][0]["reusable_artifacts"][0]["validation"] = {}
        dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("needs non-empty editable_fields" in error for error in errors), errors)
        self.assertTrue(any("validation needs method and expected_evidence" in error for error in errors), errors)

    def test_visual_manifest_needs_real_topic_specific_source(self) -> None:
        path = self.root / "research/visual-sequence-manifest.json"
        data = json.loads(path.read_text())
        data["pages"][1]["visuals"][0]["source_path"] = data["pages"][0]["visuals"][0]["source_path"]
        dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("reuses a visual path" in error for error in errors), errors)

    def test_agent_architecture_capability_requires_d0_to_d7_adapter(self) -> None:
        path = self.root / "research/capability-declarations.json"
        data = json.loads(path.read_text())
        data["capabilities"].append({
            "capability":"agent-architecture-testing", "topics":["page-0"],
            "status":"fixture-tested", "owner":"agent quality owner", "evidence":["research/user-input/source.md"],
        })
        profile_path = self.root / "research/capability-profiles.json"
        profiles = json.loads(profile_path.read_text())
        profiles["pages"][0]["capabilities"].append("agent-architecture-testing")
        dump(profile_path, profiles)
        dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("missing research/software-testing-career-agent-adapter.json" in error for error in errors), errors)

    def test_source_content_cannot_bypass_career_agent_capability_declaration(self) -> None:
        source_path = self.root / "research/user-input/source.md"
        source_path.write_text(source_path.read_text() + "\n## AI Agent 测试架构\n\n职业发展、职级定位和 Agent 架构需要独立测试体系。\n")
        inventory = inventory_source(source_path, "USER-1", self.root)
        inventory["source"].update({"authority":"user input", "scope":"fixture-scoped candidate guidance", "owner":"course owner"})
        for item in inventory["sections"] + inventory["atoms"]:
            item.update({
                "meaning":"Preserve the user-provided professional rule and its evidence boundary.",
                "disposition":"incorporated", "target_refs":["tutorial/tutorial-site.json"],
                "rationale":"The bounded concept is taught directly and remains source-labelled.",
                "owner":"course owner", "evidence_refs":["research/user-input/source.md"],
            })
        total = len(inventory["sections"]) + len(inventory["atoms"])
        dump(self.root / "research/source-assimilation-ledger.json", {
            "schema_version":"1.0", "inventory_version":"source-assimilation-v1",
            "sources":[inventory["source"]], "sections":inventory["sections"], "atoms":inventory["atoms"],
            "coverage_receipt":{
                "source_count":1, "section_count":len(inventory["sections"]), "atom_count":len(inventory["atoms"]),
                "accounted_section_count":len(inventory["sections"]), "accounted_atom_count":len(inventory["atoms"]),
                "disposition_counts":{"incorporated":total}, "unaccounted_ids":[], "inventory_command":"fixture inventory",
                "reviewer":"independent reviewer", "reviewed_at":"2026-01-01T00:00:00Z", "verdict":"PASS",
            },
        })
        errors = validate(self.root)
        self.assertTrue(any("source-detected professional obligations need explicit capability declarations" in error for error in errors), errors)
        self.assertTrue(any("missing research/software-testing-career-agent-adapter.json" in error for error in errors), errors)
        (self.root / "research/capability-declarations.json").unlink()
        errors_without_declaration_file = validate(self.root)
        self.assertTrue(any("source-detected professional obligations need explicit capability declarations" in error for error in errors_without_declaration_file), errors_without_declaration_file)
        self.assertTrue(any("missing research/software-testing-career-agent-adapter.json" in error for error in errors_without_declaration_file), errors_without_declaration_file)

    def test_complete_catalog_must_equal_independent_canonical_manifest(self) -> None:
        tutorial_path = self.root / "tutorial/tutorial-site.json"
        tutorial = json.loads(tutorial_path.read_text())
        tutorial["release_scope"].update({"mode":"complete-catalog", "catalog_complete":True})
        dump(tutorial_path, tutorial)
        catalog_path = self.root / "research/catalog-manifest.json"
        catalog = json.loads(catalog_path.read_text())
        catalog["page_ids"].append("page-not-published")
        catalog["pages"].append({"page_id":"page-not-published", "support_bundle_id":"shared-example"})
        dump(catalog_path, catalog)
        self.assertTrue(any("complete-catalog public page set must exactly equal canonical catalog" in error for error in validate(self.root)))

    def test_scope_shrink_requires_approved_change_record(self) -> None:
        tutorial_path = self.root / "tutorial/tutorial-site.json"
        tutorial = json.loads(tutorial_path.read_text())
        tutorial["pages"] = tutorial["pages"][:-1]
        tutorial["release_scope"]["promised_page_ids"] = [page["page_id"] for page in tutorial["pages"]]
        dump(tutorial_path, tutorial)
        self.assertTrue(any("release scope shrank without an approved scope-change record" in error for error in validate(self.root)))

    def test_approved_scope_shrink_record_satisfies_scope_gate(self) -> None:
        tutorial_path = self.root / "tutorial/tutorial-site.json"
        tutorial = json.loads(tutorial_path.read_text())
        previous_ids = tutorial["release_scope"]["promised_page_ids"]
        tutorial["pages"] = tutorial["pages"][:-1]
        current_ids = [page["page_id"] for page in tutorial["pages"]]
        tutorial["release_scope"].update({
            "promised_page_ids":current_ids,
            "scope_change_ref":"research/scope-changes/remove-page-14.json",
        })
        dump(tutorial_path, tutorial)
        dump(self.root / "research/scope-changes/remove-page-14.json", {
            "change_id":"remove-page-14", "previous_page_ids":previous_ids, "current_page_ids":current_ids,
            "removed_page_ids":["page-14"], "rationale":"The page is withdrawn until its material is revalidated.",
            "approved_by":"course-owner", "approved_at":"2026-01-02T00:00:00Z", "verdict":"APPROVED",
        })
        errors = validate(self.root)
        self.assertFalse(any("release scope shrank without an approved scope-change record" in error for error in errors), errors)

    def test_support_bundle_must_use_exact_id_ownership(self) -> None:
        path = self.root / "research/support-ownership.json"
        data = json.loads(path.read_text())
        data["bundles"][0]["owner_page_ids"] = ["page-*"]
        dump(path, data)
        self.assertTrue(any("support owner must be an exact canonical page ID" in error for error in validate(self.root)))

    def test_promised_page_requires_promotion_receipt_and_nine_file_inventory(self) -> None:
        receipt = self.root / "research/topics/page-0/promotion-receipt.json"
        receipt.unlink()
        self.assertTrue(any("missing promotion-receipt.json" in error for error in validate(self.root)))

    def test_promised_page_cannot_pass_failed_executability_audit(self) -> None:
        path = self.root / "research/executability-audit.json"
        data = json.loads(path.read_text())
        data["pages"][0].update({"verdict":"FAIL", "finding_count":1})
        dump(path, data)
        self.assertTrue(any("page page-0 executability audit must PASS with zero findings" in error for error in validate(self.root)))

    def test_publication_closure_rejects_static_export_hash_drift(self) -> None:
        write(self.root / "dist/site/materials/example.py", "print('DRIFT')\n")
        self.assertTrue(any("publication closure hash mismatch for dist_ref" in error for error in validate(self.root)))

    def test_publication_closure_rejects_zip_member_hash_drift(self) -> None:
        archive_path = self.root / "dist/course-release.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("site/materials/example.py", "print('DRIFT')\n")
            archive.write(self.root / "dist/site/materials/input.json", "site/materials/input.json")
        self.assertTrue(any("publication closure hash mismatch for archive member" in error for error in validate(self.root)))

    def test_complete_package_requires_solution_contract(self) -> None:
        (self.root / "research/solution-architecture.json").unlink()
        self.assertTrue(any("solution-architecture.json" in error for error in validate(self.root)))

    def test_solution_cannot_omit_mandatory_dimension(self) -> None:
        path = self.root / "research/solution-architecture.json"
        data = json.loads(path.read_text())
        data["solution_units"][0]["dimensions"] = data["solution_units"][0]["dimensions"][:-1]
        dump(path, data)
        self.assertTrue(any("misses mandatory solution dimensions" in error for error in validate(self.root)))

    def test_solution_cannot_omit_deployment_view(self) -> None:
        path = self.root / "research/solution-architecture.json"
        data = json.loads(path.read_text())
        data["solution_units"][0]["architecture_views"] = [
            view for view in data["solution_units"][0]["architecture_views"] if view["kind"] != "deployment"
        ]
        dump(path, data)
        self.assertTrue(any("misses mandatory architecture views" in error for error in validate(self.root)))

    def test_complete_design_cannot_hide_gap_dimension(self) -> None:
        path = self.root / "research/solution-architecture.json"
        data = json.loads(path.read_text())
        data["solution_units"][0]["dimensions"][0]["status"] = "gap"
        dump(path, data)
        self.assertTrue(any("claims complete design" in error for error in validate(self.root)))

    def test_pilot_needs_practitioner_review(self) -> None:
        path = self.root / "research/solution-architecture.json"
        data = json.loads(path.read_text())
        data["solution_units"][0]["practitioner_review_status"] = "not-reviewed"
        dump(path, data)
        self.assertTrue(any("pilot publication needs" in error for error in validate(self.root)))

    def test_internal_solution_maps_local_pages_without_faking_publication(self) -> None:
        path = self.root / "research/solution-architecture.json"
        data = json.loads(path.read_text())
        unit = data["solution_units"][0]
        unit["publication_status"] = "internal"
        unit["practitioner_review_status"] = "not-reviewed"
        dump(path, data)
        errors = validate(self.root)
        self.assertFalse(any("not mapped to a traced solution unit" in error for error in errors), errors)

    def test_public_solution_needs_integration_proof(self) -> None:
        path = self.root / "research/solution-architecture.json"
        data = json.loads(path.read_text())
        data["solution_units"][0]["publication_status"] = "public"
        data["solution_units"][0]["practitioner_review_status"] = "approved"
        dump(path, data)
        self.assertTrue(any("public publication needs" in error for error in validate(self.root)))

    def test_every_public_page_needs_solution_trace(self) -> None:
        path = self.root / "research/solution-architecture.json"
        data = json.loads(path.read_text())
        data["solution_units"][0]["traceability"] = data["solution_units"][0]["traceability"][:-1]
        dump(path, data)
        self.assertTrue(any("without end-to-end traceability" in error for error in validate(self.root)))

    def test_execution_receipt_needs_observed_assertions(self) -> None:
        path = self.root / "courses/example/evidence/execution-evidence.json"
        data = json.loads(path.read_text())
        data["assertions"] = []
        dump(path, data)
        self.assertTrue(any("payload needs observed assertions" in error for error in validate(self.root)))

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

    def test_tutorial_embedded_urls_are_not_runtime_dependencies(self) -> None:
        path = self.root / "tutorial/index.html"
        html = path.read_text(encoding="utf-8")
        html = html.replace(
            "</head>",
            '<link rel="icon" href="data:,"><script>const documentationUrl = "https://example.org/docs";</script></head>',
        )
        path.write_text(html, encoding="utf-8")
        self.assertFalse(any("remote scripts or styles" in error for error in validate(self.root)))

    def test_tutorial_remote_runtime_dependency_fails(self) -> None:
        path = self.root / "tutorial/index.html"
        html = path.read_text(encoding="utf-8")
        html = html.replace("</head>", '<link rel="stylesheet" href="https://cdn.example.org/site.css"></head>')
        path.write_text(html, encoding="utf-8")
        self.assertTrue(any("remote scripts or styles" in error for error in validate(self.root)))

    def test_public_tutorial_cannot_contain_incomplete_page(self) -> None:
        path = self.root / "tutorial/tutorial-site.json"
        data = json.loads(path.read_text())
        data["pages"][1]["delivery_status"] = "outlined"
        dump(path, data)
        self.assertTrue(any("public tutorial contains incomplete pages" in error for error in validate(self.root)))

    def test_public_release_must_promise_every_visible_page(self) -> None:
        path = self.root / "tutorial/tutorial-site.json"
        data = json.loads(path.read_text())
        data["release_scope"]["promised_page_ids"] = data["release_scope"]["promised_page_ids"][:-1]
        dump(path, data)
        self.assertTrue(any("must equal the public page set" in error for error in validate(self.root)))

    def test_public_tutorial_cannot_contain_empty_module(self) -> None:
        path = self.root / "tutorial/tutorial-site.json"
        data = json.loads(path.read_text())
        data["modules"].append({"module_id":"empty-module","title":"Empty","learner_result":"none","order":99})
        dump(path, data)
        self.assertTrue(any("contains empty modules" in error for error in validate(self.root)))

    def test_delivered_tutorial_page_requires_real_material_file(self) -> None:
        (self.root / "site/public/materials/example.py").unlink()
        self.assertTrue(any("references missing file" in error for error in validate(self.root)))

    def test_delivered_tutorial_page_requires_architecture(self) -> None:
        path = self.root / "tutorial/tutorial-site.json"
        data = json.loads(path.read_text())
        del data["pages"][0]["architecture"]
        dump(path, data)
        self.assertTrue(any("lacks an architecture" in error for error in validate(self.root)))

    def test_first_tutorial_page_may_have_no_prerequisite(self) -> None:
        path = self.root / "tutorial/tutorial-site.json"
        data = json.loads(path.read_text())
        self.assertEqual(data["pages"][0]["prerequisite_ids"], [])
        self.assertFalse(any("tutorial page 0 prerequisite_ids" in error for error in validate(self.root)))

    def test_promised_tutorial_page_requires_independent_research_package(self) -> None:
        (self.root / "research/topics/page-0/research-brief.md").unlink()
        self.assertTrue(any("page-0 missing research-brief.md" in error for error in validate(self.root)))

    def test_promised_tutorial_page_requires_editorial_review(self) -> None:
        path = self.root / "research/topics/page-0/validation.md"
        path.write_text(path.read_text().replace("## Independent comparison", "## Draft comparison"))
        self.assertTrue(any("Independent comparison" in error for error in validate(self.root)))

    def test_topic_manuscript_accepts_topic_specific_headings(self) -> None:
        path = self.root / "research/topics/page-0/manuscript.md"
        text = path.read_text()
        text = text.replace("## Professional problem", "## 先识别退款状态冲突")
        text = text.replace("## Runnable action", "## 运行负控制并回读证据")
        text = text.replace("## Failure and repair", "## 诊断红灯并修复追踪链")
        write(path, text)
        ledger_path = self.root / "research/topics/page-0/projection-ledger.json"
        ledger = json.loads(ledger_path.read_text())
        ledger["manuscript_sha256"] = sha256(path)
        dump(ledger_path, ledger)
        inventory_path = self.root / "research/topics/page-0/claim-inventory.json"
        inventory = json.loads(inventory_path.read_text())
        inventory["extraction"]["source_hashes"]["manuscript.md"] = sha256(path)
        inventory["extraction"]["locator_ledger"][0]["sha256"] = sha256(path)
        dump(inventory_path, inventory)
        self.assertEqual(validate(self.root), [])

    def test_topic_manuscript_rejects_missing_problem_action_repair_semantics(self) -> None:
        path = self.root / "research/topics/page-0/manuscript.md"
        text = path.read_text()
        text = text.replace("Professional problem", "Context")
        text = text.replace("Runnable action", "Notes")
        text = text.replace("Failure and repair", "Appendix")
        text = text.replace("risk", "scope")
        text = text.replace("repair", "change")
        text = text.replace("failure", "difference")
        write(path, text)
        errors = validate(self.root)
        self.assertTrue(any("missing semantic section" in error for error in errors), errors)

    def test_promised_tutorial_page_requires_split_research_files(self) -> None:
        (self.root / "research/topics/page-0/source-pack.csv").unlink()
        self.assertTrue(any("source-pack.csv" in error for error in validate(self.root)))

    def test_topic_source_pack_requires_five_evidence_lanes(self) -> None:
        path = self.root / "research/topics/page-0/source-pack.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            row["evidence_lane"] = "ai-primary"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        self.assertTrue(any("5 evidence lanes" in error for error in validate(self.root)))

    def test_topic_research_requires_independent_comparison_runs(self) -> None:
        path = self.root / "research/topics/page-0/research-runs.json"
        data = json.loads(path.read_text())
        data["runs"] = data["runs"][:1]
        dump(path, data)
        self.assertTrue(any("two independent research runs" in error for error in validate(self.root)))

    def test_topic_research_requires_claim_inventory(self) -> None:
        (self.root / "research/topics/page-0/claim-inventory.json").unlink()
        self.assertTrue(any("claim-inventory.json" in error for error in validate(self.root)))

    def test_deep_research_receipt_requires_provider_response_identity(self) -> None:
        path = self.root / "research/topics/page-0/deep-research-receipts.json"
        data = json.loads(path.read_text())
        data["runs"][0]["response_or_export_id"] = ""
        dump(path, data)
        self.assertTrue(any("response_or_export_id" in error for error in validate(self.root)))

    def test_deep_research_receipt_must_match_raw_provider_response(self) -> None:
        path = self.root / "research/topics/page-0/deep-research/c-01-r1/raw-response.json"
        data = json.loads(path.read_text())
        data["id"] = "resp_tampered"
        dump(path, data)
        receipt_path = self.root / "research/topics/page-0/deep-research-receipts.json"
        receipts = json.loads(receipt_path.read_text())
        run = next(item for item in receipts["runs"] if item["run_id"] == "c-01-r1")
        run["output_sha256"] = sha256(path)
        dump(receipt_path, receipts)
        self.assertTrue(any("raw response id mismatch" in error for error in validate(self.root)))

    def test_deep_research_receipt_cannot_claim_missing_raw_citations(self) -> None:
        path = self.root / "research/topics/page-0/deep-research/c-01-r1/raw-response.json"
        data = json.loads(path.read_text())
        data["output"][1]["content"][0]["annotations"] = []
        dump(path, data)
        receipt_path = self.root / "research/topics/page-0/deep-research-receipts.json"
        receipts = json.loads(receipt_path.read_text())
        run = next(item for item in receipts["runs"] if item["run_id"] == "c-01-r1")
        run["output_sha256"] = sha256(path)
        dump(receipt_path, receipts)
        self.assertTrue(any("raw response citation count mismatch" in error for error in validate(self.root)))

    def test_search_sources_cannot_be_promoted_to_opened_sources(self) -> None:
        raw_path = self.root / "research/topics/page-0/deep-research/c-01-r1/raw-response.json"
        raw = json.loads(raw_path.read_text())
        raw["output"][0]["action"] = {
            "type":"search", "query":"bounded claim",
            "sources":[{"url":"https://example.com/source"}],
        }
        dump(raw_path, raw)
        tool_path = self.root / "research/topics/page-0/deep-research/c-01-r1/tool-calls.json"
        tools = json.loads(tool_path.read_text())
        tools["calls"][0]["action"] = raw["output"][0]["action"]
        dump(tool_path, tools)
        receipt_path = self.root / "research/topics/page-0/deep-research-receipts.json"
        receipts = json.loads(receipt_path.read_text())
        run = next(item for item in receipts["runs"] if item["run_id"] == "c-01-r1")
        run["output_sha256"] = sha256(raw_path)
        dump(receipt_path, receipts)
        self.assertTrue(any("raw response opened source count mismatch" in error for error in validate(self.root)))

    def test_source_opening_ledger_must_match_raw_open_events(self) -> None:
        path = self.root / "research/topics/page-0/deep-research/c-01-r1/source-opening-ledger.json"
        data = json.loads(path.read_text())
        data["opening_events"][0]["url"] = "https://example.com/citation-only"
        dump(path, data)
        self.assertTrue(any("source-opening ledger opening_events mismatch" in error for error in validate(self.root)))

    def test_deep_research_citation_artifact_must_match_raw_content(self) -> None:
        path = self.root / "research/topics/page-0/deep-research/c-01-r1/citations.json"
        data = json.loads(path.read_text())
        data["citations"][0]["url"] = "https://example.com/tampered"
        dump(path, data)
        self.assertTrue(any("citations artifact does not match raw response" in error for error in validate(self.root)))

    def test_deep_research_tool_artifact_must_match_raw_content(self) -> None:
        path = self.root / "research/topics/page-0/deep-research/c-01-r1/tool-calls.json"
        data = json.loads(path.read_text())
        data["calls"][0]["action"]["url"] = "https://example.com/tampered"
        dump(path, data)
        self.assertTrue(any("tool-call artifact does not match raw response" in error for error in validate(self.root)))

    def test_each_claim_requires_dedicated_initial_deep_research_run(self) -> None:
        path = self.root / "research/topics/page-0/deep-research-receipts.json"
        data = json.loads(path.read_text())
        initial = next(run for run in data["runs"] if run["phase"] == "initial-deep-research")
        initial["claim_ids"].append("C-02")
        dump(path, data)
        self.assertTrue(any("initial Deep Research run must cover exactly one claim" in error for error in validate(self.root)))

    def test_each_claim_requires_counterevidence_or_gap_fill_run(self) -> None:
        path = self.root / "research/topics/page-0/deep-research-receipts.json"
        data = json.loads(path.read_text())
        data["runs"] = [run for run in data["runs"] if not (run["claim_ids"] == ["C-01"] and run["phase"] == "counterevidence")]
        dump(path, data)
        self.assertTrue(any("C-01 lacks counterevidence or gap-fill Deep Research" in error for error in validate(self.root)))

    def test_research_saturation_requires_no_material_change_or_primary_exception(self) -> None:
        path = self.root / "research/topics/page-0/research-saturation.json"
        data = json.loads(path.read_text())
        data["claims"][0]["two_consecutive_rounds_without_material_change"] = False
        dump(path, data)
        self.assertTrue(any("saturation lacks two stable rounds or a primary-authority exception" in error for error in validate(self.root)))

    def test_topic_lab_manifest_rejects_missing_repository_file(self) -> None:
        path = self.root / "research/topics/page-0/lab-manifest.json"
        data = json.loads(path.read_text())
        data["required_files"].append("materials/does-not-exist.py")
        dump(path, data)
        self.assertTrue(any("lab manifest references missing file" in error for error in validate(self.root)))

    def test_complete_catalog_cannot_contain_planned_pages(self) -> None:
        path = self.root / "tutorial/tutorial-site.json"
        data = json.loads(path.read_text())
        data["pages"][1]["delivery_status"] = "planned"
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

    def test_course_manifest_ai_lane_wrong_type_fails_without_crashing(self) -> None:
        path = self.root / "courses/example/course-manifest.json"
        data = json.loads(path.read_text())
        data["ai_lane"] = ["test-ai-systems"]
        dump(path, data)
        self.assertTrue(any("manifest has invalid ai_lane" in error for error in validate(self.root)))

    def test_live_source_check_rejects_nonexistent_url(self) -> None:
        path = self.root / "research/source-ledger.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rows[0]["url"] = "http://127.0.0.1:9/does-not-exist"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        self.assertTrue(any("failed live URL verification" in error for error in verify_source_urls(self.root, {"S0"})))

    def _opt_in_artifact_transformation(self) -> None:
        dump(self.root / "research/capability-declarations.json", {"capabilities": [{"capability": "artifact-transformation", "topics": ["topic-a"], "status": "pass"}]})
        dump(self.root / "research/profession-method-library.json", {"source_authority": "owner-approved authority rule", "owner": "method-owner", "evidence": ["S1"], "methods": [{"id": "m1", "rationale": "risk and oracle fit", "method": "boundary"}]})
        dump(self.root / "research/topics/topic-a/transformation-contract.json", {"topic": "topic-a", "status": "fixture-tested", "source_refs": ["s1"], "source_authority": "topic owner authority rule", "authority_owner": "topic-owner", "authority_evidence": ["S1"]})
        dump(self.root / "research/prompt-package/manifest.json", {"package_id": "p1", "version": "1", "purpose": "transform", "eval_set_id": "e1", "stop_states": ["BLOCKED"], "review_owner": "owner"})
        dump(self.root / "research/prompt-package/eval.json", {"items": [{"id": "e1", "status": "PASS_SCHEMA"}]})
        dump(self.root / "research/prompt-package/mutation.json", {"items": [{"id": "mu1", "status": "killed"}]})
        links = [{"id": f"{kind}-1", "kind": kind, "refs": [] if kind == "source" else [f"{prev}-1"]} for kind, prev in [("source", ""), ("claim", "source"), ("risk", "claim"), ("method", "risk"), ("oracle", "method"), ("case", "oracle"), ("result", "case")]]
        dump(self.root / "research/traceability.json", {"links": links})

    def test_opt_in_missing_method_rationale_fails(self) -> None:
        self._opt_in_artifact_transformation()
        path = self.root / "research/profession-method-library.json"
        data = json.loads(path.read_text()); data["methods"][0].pop("rationale"); dump(path, data)
        self.assertTrue(any("missing method rationale" in error for error in validate(self.root)))

    def test_opt_in_missing_source_authority_fails(self) -> None:
        self._opt_in_artifact_transformation()
        path = self.root / "research/profession-method-library.json"; data = json.loads(path.read_text()); data.pop("source_authority"); dump(path, data)
        self.assertTrue(any("missing explicit source authority/precedence" in error for error in validate(self.root)))

    def test_opt_in_missing_oracle_fails(self) -> None:
        self._opt_in_artifact_transformation()
        path = self.root / "research/traceability.json"; data = json.loads(path.read_text()); data["links"] = [item for item in data["links"] if item["kind"] != "oracle"]; dump(path, data)
        self.assertTrue(any("missing oracle node" in error for error in validate(self.root)))

    def test_opt_in_orphan_trace_fails(self) -> None:
        self._opt_in_artifact_transformation()
        path = self.root / "research/traceability.json"; data = json.loads(path.read_text()); data["links"][-1]["refs"] = ["does-not-exist"]; dump(path, data)
        self.assertTrue(any("orphan reference" in error for error in validate(self.root)))

    def test_opt_in_blocked_cannot_declare_pass(self) -> None:
        self._opt_in_artifact_transformation()
        path = self.root / "research/traceability.json"; data = json.loads(path.read_text()); data["links"][2]["status"] = "BLOCKED"; dump(path, data)
        self.assertTrue(any("blocked status cannot be declared passing" in error for error in validate(self.root)))

    def test_opt_in_missing_prompt_eval_and_mutation_fails(self) -> None:
        self._opt_in_artifact_transformation()
        (self.root / "research/prompt-package/eval.json").unlink(); (self.root / "research/prompt-package/mutation.json").unlink()
        errors = validate(self.root)
        self.assertTrue(any("missing eval artifact" in error for error in errors))
        self.assertTrue(any("missing mutation artifact" in error for error in errors))

    def test_fixture_status_cannot_claim_higher_maturity_via_capability(self) -> None:
        self._opt_in_artifact_transformation()
        path = self.root / "research/capability-declarations.json"; data = json.loads(path.read_text()); data["capabilities"][0]["status"] = "production-validated"; dump(path, data)
        path = self.root / "research/topics/topic-a/transformation-contract.json"; data = json.loads(path.read_text()); data["status"] = "fixture-tested"; dump(path, data)
        self.assertTrue(any("above fixture/topic evidence" in error for error in validate(self.root)))

    def test_public_pages_require_exact_capability_profiles(self) -> None:
        (self.root / "research/capability-profiles.json").unlink()
        self.assertTrue(any("missing research/capability-profiles.json" in error for error in validate(self.root)))

    def test_capability_profile_rejects_unknown_or_empty_capability(self) -> None:
        path = self.root / "research/capability-profiles.json"
        data = json.loads(path.read_text()); data["pages"][0]["capabilities"] = ["none"]; dump(path, data)
        self.assertTrue(any("must declare at least one professional capability" in error for error in validate(self.root)))

    def test_capability_declaration_must_cover_profile(self) -> None:
        path = self.root / "research/capability-declarations.json"
        data = json.loads(path.read_text()); data["capabilities"][0]["topics"] = data["capabilities"][0]["topics"][1:]; dump(path, data)
        self.assertTrue(any("page page-0 capability ai-system-evaluation is not covered" in error for error in validate(self.root)))

    def test_public_pages_require_professional_evidence_records(self) -> None:
        path = self.root / "research/professional-evidence.json"
        data = json.loads(path.read_text()); data["pages"] = data["pages"][1:]; dump(path, data)
        self.assertTrue(any("professional evidence missing public page: page-0" in error for error in validate(self.root)))

    def test_model_pass_rejects_provider_none_and_self_oracle(self) -> None:
        path = self.root / "research/professional-evidence.json"
        data = json.loads(path.read_text()); model = data["pages"][0]["model"]
        model.update({"status":"PASS", "provider":"none", "model":"offline", "version":"1", "parameters":{}, "repeats":2,
                      "raw_output_hashes":["sha256:" + "a" * 64, "sha256:" + "b" * 64], "scorer_ref":"scorer.json",
                      "oracle_owner":"model-under-test", "receipt_refs":["receipt.json"]})
        dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("model PASS cannot use provider none" in error for error in errors))
        self.assertTrue(any("model under test cannot own its oracle" in error for error in errors))

    def test_fixture_claim_requires_clean_room_pass(self) -> None:
        path = self.root / "research/professional-evidence.json"
        data = json.loads(path.read_text()); data["pages"][0]["clean_room"]["status"] = "NOT_RUN"; dump(path, data)
        self.assertTrue(any("fixture-tested maturity requires clean_room PASS" in error for error in validate(self.root)))

    def test_clean_room_command_must_match_every_declared_surface(self) -> None:
        path = self.root / "research/professional-evidence.json"
        data = json.loads(path.read_text()); data["pages"][0]["clean_room"]["command"] = "python3 missing.py"; dump(path, data)
        self.assertTrue(any("clean-room command is absent from surface" in error for error in validate(self.root)))

    def test_learner_pass_requires_minimum_novice_evidence(self) -> None:
        path = self.root / "research/professional-evidence.json"
        data = json.loads(path.read_text()); learner = data["pages"][0]["learner"]
        learner.update({"status":"PASS", "participants":2, "target_profile":"beginner testers", "task_completion_rate":1.0,
                        "transfer_success_rate":1.0, "time_on_task_minutes":5, "error_recovery_rate":1.0,
                        "receipt_refs":["learner-study.json"], "limitations":"small sample"})
        dump(path, data)
        self.assertTrue(any("learner PASS needs at least 5 target learners" in error for error in validate(self.root)))

    def test_status_registry_rejects_untracked_verdict_and_hash_drift(self) -> None:
        write(self.root / "human-review/05-第二份验收.md", "# Verdict\n\n" + "current verdict evidence " * 80)
        path = self.root / "research/status-registry.json"
        data = json.loads(path.read_text()); data["records"][0]["artifact_hash"] = "sha256:" + "0" * 64; dump(path, data)
        errors = validate(self.root)
        self.assertTrue(any("untracked human-review verdict" in error for error in errors))
        self.assertTrue(any("status artifact hash mismatch" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
