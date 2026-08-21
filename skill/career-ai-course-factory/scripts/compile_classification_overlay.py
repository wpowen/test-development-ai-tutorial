#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compile a deterministic, pending claim-level classification overlay.

The output is a proposal input for an independent auditor.  It never marks
the overlay approved and never creates a research receipt or saturation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from build_claim_source_manifest import validate_freshness

NORMALIZATION_VERSION = "nfkc-casefold-punct-space.v1"
CLUSTER_ORDER = ("K12", "K07", "K08", "K05", "K06", "K04", "K03", "K09", "K10", "K11", "K02", "K01")
ROUTES = ("LOCAL-VERIFY", "EXTERNAL-RESEARCH", "TARGET-EVIDENCE", "TEACHING-VALIDATION", "BLOCKED-UNCLASSIFIED")


def file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = re.sub(r"[，。！？；：、（）【】《》“”‘’「」…—–·,.;:!?()\[\]{}<>\"'`*_#|/\\]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def classify(statement: str) -> tuple[str, str, str, str]:
    text = normalize(statement)
    # Very short English fragments are usually truncated labels or incomplete
    # source material rather than actionable claims.  Keep them blocked until
    # an auditor supplies the missing predicate/context.
    english_tokens = re.findall(r"[a-z0-9]+", text)
    if len(english_tokens) <= 5 and len(english_tokens) >= 2 and not re.search(
        r"\b(?:is|are|was|were|has|have|does|do|can|must|should|returns?|supports?|behav(?:e|ior)|works?|measured|observed|improves?|reduces?|increases?)\b",
        text,
    ) and len(english_tokens) == len(text.split()) and not re.search(
        r"repository|fixture|validator|runner|projection|hash|manifest|outbox|receipt|adapter|fault report|verdict|closure|copied paths|model-config|material closure|workflow|owner|save|compare|expected|actual|values|field|repair|canonical state|static|maturity|td-[a-z0-9-]+",
        text,
    ):
        return "K00", "UNCLASSIFIED", "BLOCKED-UNCLASSIFIED", "short English fragment lacks an explicit predicate"
    patterns = {
        "K12": r"claim|inventory|receipt|saturation|projection|publication|release|validator|schema|manifest|factory|research|evidence|course metric-card|fault report|verdict|offline|fixture|readme|exit code|expected exit|same expected contract|maturity|course evidence|entry conditions|python|repository files|deterministic runner|control contract|pytest|integration|test contract|research topics|source pack|source-pack|审计|命题|收据|饱和|投影|发布|门禁|工厂|研究|课程工程化|课程指标卡|故障报告|离线|夹具|退出码|成熟度|入口条件|仓库文件|确定性 runner|控制契约|测试合同|来源包",
        "K07": r"security|privacy|acl|authorization|permission|tenant|compliance|prompt injection|nist|governance|risk|越权|隐私|权限|安全|合规|授权|治理|风险|审计日志",
        "K08": r"performance|latency|throughput|capacity|cost|reliability|availability|slo|p95|p99|性能|延迟|吞吐|容量|成本|可靠性|稳定性|阈值",
        "K05": r"rag|retrieval|retriever|reranker|chunk|embedding|vector|knowledge|corpus|metadata|deletion|索引|检索|知识库|向量|语料|切片",
        "K06": r"agent|tool|state|retry|handoff|side effect|workflow loop|workflow owner|save expected|compare same|expected actual|same field|ensure repair|same expected values|outbox|receipt|adapter|发件箱|回读|适配器|代理|工具|状态|重试|交接|副作用|工作流|重复写|批准流程",
        "K04": r"evaluation|eval|oracle|failed_oracle_ids|pass@k|metric|benchmark|statistical|confidence|recall|precision|f1|ndcg|mrr|score|mean|average|mutation|failure localization|llm judge|judge|double blind|order flip|calibration|人工双标|顺序翻转|事实反例|校准|共同接受|均值|平均|人工审查|发现率|失败可定位|得分|评测|指标|统计|置信|基准|样本",
        "K03": r"model|api|sdk|provider|prompt|token|context|inference|llm|model update|模型更新|replacement|替换|模型|接口|协议|提示|令牌|上下文|推理",
        "K09": r"trace|lineage|replay|version|hash|provenance|observability|telemetry|血缘|重放|版本|哈希|溯源|可观测",
        "K10": r"platform|integration|browser|mobile|client|device|database|ci/cd|production|live|provider response|enterprise|target system|平台|集成|浏览器|移动|客户端|设备|数据库|真实|生产|企业|目标系统",
        "K11": r"career|promotion|learner|teaching|practitioner|transfer|职业|晋升|学习者|教学|从业者|迁移",
        "K02": r"lifecycle|workflow|artifact|business|decision|role|deliverable|生命周期|工作流|工件|业务|决策|角色|交付",
        "K01": r"definition|terminology|baseline|scope|boundary|定义|术语|基线|范围|边界",
    }
    cluster = next((key for key in CLUSTER_ORDER if re.search(patterns[key], text)), "K00")
    if cluster == "K00":
        return "K00", "UNCLASSIFIED", "BLOCKED-UNCLASSIFIED", "no safe cluster predicate"
    negative_status = re.search(r"\b(?:not|no|without|never|cannot|unknown|not_run|blocked|excluded|only proves|does not prove|unsupported|reject|out of scope|does not claim|does not connect|fixture only|not in evidence)\b|未|无|不是|不含|不能|不得|没有|尚未|未运行|未通过|排除|仅证明|不证明|不支持|不代表|不等于|不构成|不覆盖|不提供|局限|仅支持|局部方法|范围外|不声称|不连接|不在本页证据|不在证据", text)
    provenance_status = re.search(r"opened source|opened 来源|source coverage|source list|projected|projection|page evidence|evidence boundary|limits preserved|teaching block|publication verdict|fixture tested|fixture-tested|static|maturity|course metric-card|fault report|verdict|closure|copied paths|model-config|material closure|course evidence-boundary owner|claim-level research owner|deferred|manuscript|eval set|eval-set|eval 集|eval集|readme|live-tested|practitioner-reviewed|production-validated|research-runs|research runs|independent run|research protocol|oracle ref|available input fields|prompt|schema|workflow owner|save expected|compare same field|expected actual|repair|canonical state|expected values|expected exit|same expected contract|cycle|risk trace|mutation report|reusable-artifact owner|unauthorized|工件链|风险地图|生产回归资产|run lab|run_lab|baseline observations|static fields|random runs|opened source|offline supply chain|离线供应链|供应链合同|研究分两次|打开十个来源|pytest|integration|test contract|research topics|source pack|source-pack|evidence[ ]+td-[a-z0-9-]+|courses[ ]+|learner-materials|ci|gate|依赖顺序|cannot prove|does not claim|不能证明|不声称|真实表格|评测集|待命题级研究|正式综合|退出码|发布后读回|状态才可能|从业者复核|文件闭包|来源覆盖|来源清单|投影|页面证据|边界保留|路径|section|文档|规范|目标系统边界|成熟度|稿件|课程材料|本包不声称", text)
    local_status = re.search(r"repository|fixture|synthetic|validator|runner|projection|hash|manifest|course|content/|site/|material|page|publication|verdict|closure|copied paths|model-config|material closure|outbox|receipt|adapter|course evidence-boundary owner|claim-level research owner|deferred|manuscript|eval set|eval-set|eval 集|eval集|readme|live-tested|practitioner-reviewed|production-validated|maturity|fault report|research-runs|research runs|independent run|research protocol|oracle ref|available input fields|prompt|schema|workflow owner|save expected|compare same field|expected actual|repair|canonical state|expected values|expected exit|same expected contract|cycle|risk trace|mutation report|reusable-artifact owner|unauthorized|工件链|风险地图|生产回归资产|run lab|run_lab|baseline observations|static fields|random runs|opened source|opened 来源|offline supply chain|离线供应链|供应链合同|研究分两次|打开十个来源|pytest|integration|test contract|research topics|source pack|source-pack|evidence[ ]+td-[a-z0-9-]+|courses[ ]+|learner-materials|pr smoke|nightly regression|release-candidate|release gate|ci|gate|依赖顺序|td-[a-z0-9-]+|真实表格|评测集|待命题级研究|正式综合|退出码|发布后读回|状态才可能|从业者复核|不能证明|不声称|不在本页证据|不在证据|本仓库|代码|样例|故障注入|门禁|状态|边界|路径|页面|来源|文件闭包|发件箱|回读|适配器|成熟度|稿件|课程材料|本包不声称", text)
    evaluation_method = re.search(r"pass@k|failed_oracle_ids|oracle|均值|平均|mutation|failure localization|llm judge|judge|double blind|order flip|calibration|人工双标|共同接受|评测集|eval set|eval-set|score|得分|ttft|tpot|cost-per-success|fixed workload|leaderboard|run protocol|运行协议|rebaseline|production-quality", text)
    teaching_exercise = re.search(r"选择传统测试|写 dataset|写 dataset eval trace|工件设计|练习|exercise|learning artifact|教学练习", text)
    current_target_observation = re.search(r"当前(?:生产|目标)?系统|目标系统(?:已|中)|live system|live model|live agent|live tools|live practitioner|production system|observed|returned|returns?|返回|观察到|实测|真实环境.*执行|真实集群.*执行|practitioner (?:was )?(?:run|reviewed)|从业者(?:已)?复核", text)
    if local_status and (negative_status or provenance_status):
        route = "LOCAL-VERIFY"
    elif negative_status and re.search(r"model update|模型更新|replacement|替换", text):
        route = "EXTERNAL-RESEARCH"
    elif negative_status or provenance_status:
        return "K00", "UNCLASSIFIED", "BLOCKED-UNCLASSIFIED", "negative/status boundary requires explicit local or target adjudication"
    elif teaching_exercise:
        route = "TEACHING-VALIDATION"
    elif evaluation_method and not current_target_observation:
        route = "EXTERNAL-RESEARCH"
    elif re.search(r"\b(?:production|live provider|provider response|provider-side|practitioner)\b|\benterprise\b|\btarget system\b|真实|生产|企业|目标系统|从业者|学习者效果", text) and re.search(r"\b(?:returns?|supports?|behavio?r|capabilit(?:y|ies)|works?|run|measured|observed|response)\b|行为|能力|返回|支持|执行|测得|观察", text):
        route = "TARGET-EVIDENCE"
    elif re.search(r"learner|teaching|practitioner|教学|学习者|从业者|迁移", text):
        route = "TEACHING-VALIDATION"
    elif re.search(r"repository|fixture|synthetic|validator|runner|projection|hash|manifest|outbox|receipt|adapter|course metric-card|fault report|verdict|closure|copied paths|model-config|material closure|本仓库|代码|样例|故障注入|发件箱|回读|适配器|文件闭包", text):
        route = "LOCAL-VERIFY"
    else:
        route = "EXTERNAL-RESEARCH"
    evidence = {
        "LOCAL-VERIFY": "LOCAL-DETERMINISTIC",
        "EXTERNAL-RESEARCH": "SHARED-MECHANISM",
        "TARGET-EVIDENCE": "TARGET-EMPIRICAL",
        "TEACHING-VALIDATION": "TEACHING-PROFESSIONAL",
    }[route]
    risk = "high" if cluster in {"K07", "K08"} or route == "TARGET-EVIDENCE" else "medium"
    return cluster, evidence, route, f"deterministic {NORMALIZATION_VERSION} proposal; independent review required ({risk})"


def compile_overlay(topics_root: Path, output: Path, source_manifest_path: Path | None = None) -> dict[str, Any]:
    topics_root = topics_root.resolve(strict=True)
    paths = sorted(topics_root.glob("*/claim-list.author.draft-2026-08-20.json"))
    if not paths:
        raise ValueError("no author draft claim lists found")
    claims: list[dict[str, Any]] = []
    source_digests = [file_digest(path) for path in paths]
    source_manifest_digest = None
    source_manifest_rel = None
    source_manifest = None
    if source_manifest_path is not None:
        source_manifest_path = source_manifest_path.resolve(strict=True)
        source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
        if source_manifest.get("schema_version") != "claim-source-manifest.v1":
            raise ValueError("source manifest has unsupported schema_version")
        source_manifest_digest = file_digest(source_manifest_path)
        freshness_errors = validate_freshness(source_manifest, topics_root.parents[1])
        if freshness_errors:
            raise ValueError("source manifest freshness failed: " + "; ".join(freshness_errors[:5]))
        try:
            source_manifest_rel = source_manifest_path.relative_to(topics_root.parents[1]).as_posix()
        except ValueError:
            source_manifest_rel = source_manifest_path.name
        pages_by_id = {str(item.get("page_id")): item for item in source_manifest.get("pages", []) if isinstance(item, dict)}
        for path in paths:
            topic_id = path.parent.name
            page = pages_by_id.get(topic_id)
            if page is None:
                raise ValueError(f"source manifest missing page: {topic_id}")
            declared = {(str(item.get("root_alias")), str(item.get("path")), str(item.get("sha256"))) for item in page.get("source_files", []) if isinstance(item, dict)}
            draft = json.loads(path.read_text(encoding="utf-8"))
            for item in draft.get("source_files", []):
                key = (str(item.get("root_alias", "topic")), str(item.get("path", "")), str(item.get("sha256", "")))
                if key not in declared:
                    raise ValueError(f"draft source is not bound by source manifest: {topic_id}:{key[0]}:{key[1]}")
    seen: set[str] = set()
    for path in paths:
        document = json.loads(path.read_text(encoding="utf-8"))
        if document.get("schema_version") != "claim-list.author.v1" or document.get("independent_review") is not False:
            raise ValueError(f"source is not an unreviewed author draft: {path}")
        for row in document.get("claims", []):
            claim_id = str(row.get("claim_id", ""))
            if not claim_id or claim_id in seen:
                raise ValueError(f"duplicate or empty claim_id: {claim_id}")
            seen.add(claim_id)
            cluster, evidence, route, reason = classify(str(row.get("statement", "")))
            # Keep the pending proposal structurally explicit.  Unknown
            # semantic fields are represented as UNKNOWN-EXPLICIT rather than
            # omitted or guessed; an auditor must replace them before approval.
            required_dimensions = row.get("required_dimensions") if isinstance(row.get("required_dimensions"), list) else []
            claim_type = str(row.get("claim_type") or "UNKNOWN-EXPLICIT")
            scope = str(row.get("scope") or "UNKNOWN-EXPLICIT")
            risk = str(row.get("risk") or "unknown")
            claims.append({
                "claim_id": claim_id, "evidence_class": evidence,
                "risk": "unknown" if cluster == "K00" else ("high" if cluster in {"K07", "K08"} or route == "TARGET-EVIDENCE" else risk if risk in {"low", "medium", "high", "critical"} else "medium"),
                "primary_cluster_id": cluster, "related_cluster_ids": [],
                "source_family_policy": "pending-review", "classification_reason": reason,
                "target_evidence_required": route == "TARGET-EVIDENCE", "route": route,
                "subject": "UNKNOWN-EXPLICIT", "predicate": "UNKNOWN-EXPLICIT", "object": "UNKNOWN-EXPLICIT",
                "claim_type_family": claim_type, "scope": scope, "version": "UNKNOWN-EXPLICIT",
                "time_boundary": "UNKNOWN-EXPLICIT", "vendor_or_tool": "UNKNOWN-EXPLICIT",
                "environment": "UNKNOWN-EXPLICIT", "population": "UNKNOWN-EXPLICIT",
                "region_language": "UNKNOWN-EXPLICIT", "authority_risk": risk,
                "required_dimensions": [str(item) for item in required_dimensions if str(item).strip()],
                "execution_contract": "openai-deep-research.v1",
                "local_validation_locators": [str(item) for item in row.get("source_locations", []) if str(item).strip()] if isinstance(row.get("source_locations"), list) else [],
            })
    claims.sort(key=lambda item: item["claim_id"])
    manifest_digest = "sha256:" + hashlib.sha256("\n".join(source_digests).encode()).hexdigest()
    document = {
        "schema_version": "classification-overlay.v1",
        "overlay_id": "overlay-" + hashlib.sha256((manifest_digest + NORMALIZATION_VERSION).encode()).hexdigest()[:16],
        "source_inventory_digests": source_digests,
        "generated_by": "luna-classification-proposal",
        "reviewed_by": "pending-independent-auditor",
        "independent_review": False,
        "review_status": "pending",
        "claim_count": len(claims),
        "normalization_version": NORMALIZATION_VERSION,
        "input_manifest_digest": manifest_digest,
        "claim_source_manifest_path": source_manifest_rel,
        "claim_source_manifest_digest": source_manifest_digest,
        "claims": claims,
    }
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    counts = Counter(item["primary_cluster_id"] for item in claims)
    routes = Counter(item["route"] for item in claims)
    normalized = defaultdict(list)
    for path in paths:
        for row in json.loads(path.read_text(encoding="utf-8")).get("claims", []):
            normalized[normalize(str(row.get("statement", "")))].append(str(row.get("claim_id", "")))
    duplicate_groups = [ids for ids in normalized.values() if len(ids) > 1]
    return {"claim_count": len(claims), "topic_count": len(paths), "cluster_counts": dict(sorted(counts.items())), "route_counts": dict(sorted(routes.items())), "unique_normalized_statements": len(normalized), "duplicate_groups": len(duplicate_groups), "duplicate_claims": sum(len(ids) for ids in duplicate_groups), "normalization_version": NORMALIZATION_VERSION}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topics-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source-manifest", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(compile_overlay(args.topics_root, args.output, args.source_manifest), ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"BLOCKED-CLASSIFICATION-OVERLAY: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
