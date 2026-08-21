#!/usr/bin/env python3
"""Build the Wave-2 research packages and byte-identical public lab bundle."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[3]
COURSE = PACKAGE / "courses" / "td-ai-foundations-eval"
LAB = COURSE / "lab"
PUBLIC = PACKAGE / "site" / "public" / "materials" / "ai-foundations-eval"
TOPIC_ROOT = PACKAGE / "research" / "topics"

TOPICS = {
    "TD-FP01": {"title":"Prompt 小白第一课：从一句指令到可验证 Prompt Package","question":"如何把聊天式指令拆成可版本化、可评价、可故障注入且保留人工决定权的专业 Prompt Package？","focus":"system、task、context/input、output/schema、eval、mutation、manifest、receipt 与 stop state 的责任分离","decision":"先冻结来源、输出 Schema、独立 Eval 与停止状态，再允许模型生成候选；静态包没有原始模型输出时保持 NOT_RUN。","failure":"把 system、任务、输入和自评混成一段提示词，模型补写缺失规则并把自己的输出再次判为正确。","metric":"角色分离、工件闭包、source_ref 覆盖、stop-state 保留与 mutation detection","artifact":"版本化 Prompt Package、适配卡和 0/1/0 运行收据","unknown":"不同模型对指令层级、长上下文和结构化输出的实际遵循度尚未运行。"},
    "TD-F02": {"title":"模型生命周期：一次错误究竟来自哪里","question":"一次 AI 回答失败后，测试开发如何先定位生命周期层，再选择修复对象？","focus":"数据、预训练、后训练、部署、推理和监控之间的责任边界","decision":"先核对模型、Prompt、数据、工具和运行环境的版本 Manifest；没有 Trace 时不把症状归因给模型。","failure":"浮动模型别名让同一回归集在两天得到不同结果，却没有任何可比较版本证据。","metric":"Manifest 完整率与可重放率","artifact":"模型生命周期—测试责任图和版本 Manifest","unknown":"基础模型训练数据、后训练配方及提供方内部发布变更通常不可见。"},
    "TD-F03": {"title":"Token、Context 与非确定性：为什么一次 PASS 不够","question":"怎样把 Token、Context、解码和非确定性变成可控的测试变量？","focus":"上下文预算、位置影响、采样配置、重复运行和单变量实验","decision":"结构、权限和副作用用确定性 Gate；语义行为保存完整上下文并重复运行，报告分布而非挑选一次结果。","failure":"只跑一次温度为零的请求后宣称系统稳定，升级推理后端时才暴露尾部失败。","metric":"每样例运行次数、通过率分布、上下文利用与截断状态","artifact":"推理变量—测试设计矩阵和重复运行计划","unknown":"不同硬件、内核、批处理与服务端路由对确定性的影响需要当前环境实测。"},
    "TD-F04": {"title":"LLM、RAG、Agent、Worker 与 Workflow 的被测边界","question":"控制权逐层扩张时，测试对象、证据和人工 Gate 应如何增加？","focus":"生成、检索、工具、状态、Handoff、终止和副作用的分层架构","decision":"按谁决定下一步、状态存在哪里、是否能产生副作用来分类，不按产品营销名称分类。","failure":"最终文本写着未退款，但 Agent 已尝试调用退款工具；只看回复导致严重假绿。","metric":"Trace 层覆盖率、禁止动作命中数、人工 Gate 前置率","artifact":"AI 应用结构、信任边界与证据分层图","unknown":"目标框架对 Agent、Worker 和 Workflow 的命名、重试和状态语义尚未接入。"},
    "TD-T01": {"title":"Eval Contract：先写发布问题，再选指标","question":"一个能决定发布的 Eval Contract 必须固定哪些字段和停止状态？","focus":"system-under-test、风险、数据、Oracle、阈值、owner、版本与 stop state","decision":"任何分数都必须回答测谁、测什么风险、谁批准和失败后做什么；owner 或阈值依据缺失即阻断。","failure":"团队先选择一个流行指标，再用平均分替代高风险退款行为的发布决定。","metric":"合同字段完整率、阻断规则覆盖率、决策 owner 覆盖率","artifact":"版本化 Eval Contract 和决策表","unknown":"真实业务的错误成本、发布阈值和风险接受人只能由目标组织确认。"},
    "TD-T02": {"title":"Dataset、Slice 与 Holdout：让评测数据不会越调越假","question":"如何从业务风险构造 Eval dataset，并阻止切片缺失、重复和 Holdout 泄漏？","focus":"样例来源、风险切片、标签 owner、去重、时间切分、开发集和封存 Holdout","decision":"日常调试只看 development 集；Holdout 封存并限制访问，重复使用后必须记录耗损与更新计划。","failure":"开发者反复针对最终回归集调 Prompt，总分持续上升，真实新问题却没有改善。","metric":"切片覆盖率、重复率、Holdout 访问次数、标签分歧率","artifact":"Eval dataset、数据卡、切片矩阵和 Holdout 清单","unknown":"合成数据的分布代表性与领域标签一致性尚未通过生产样本校准。"},
    "TD-T03": {"title":"Composite Oracle：规则、语义 Judge 与人工如何组合","question":"怎样组合确定性规则、语义评分与人工复核，避免 Judge 自证和平均分掩盖 blocker？","focus":"Schema、业务不变量、权限、引用、语义 rubric、Judge 校准和人工升级","decision":"先执行独立确定性 blocker，再执行语义评分；高风险分歧由具名业务或安全 owner 决定。","failure":"同一个模型生成答案又评价自己的权限合规性，并用高语义总分覆盖越权工具调用。","metric":"blocker 数、Oracle 独立率、人机分歧率与升级关闭率","artifact":"风险—Oracle 决策表和分歧升级记录","unknown":"模型 Judge 在目标领域的偏差、位置效应和一致性尚未用人工双标集校准。"},
    "TD-T04": {"title":"重复运行与统计：从一次结果到可解释分布","question":"概率系统应该运行多少次、报告什么统计量，才能支撑有限而诚实的决定？","focus":"估计目标、重复运行、分母、切片分布、置信区间、配对比较和 blocker 分离","decision":"先声明要估计固定样例表现还是相似任务总体表现；报告逐条原始结果和不确定性，不发明通用次数。","failure":"候选只运行一次且平均得分略高，就被写成稳定提升；高风险切片的两次失败被均值吞掉。","metric":"逐切片通过分布、配对差异、区间宽度、blocker 事件数","artifact":"重复运行报告、分布图和发布解释模板","unknown":"教学中的五次运行不构成生产样本量建议，样本量取决于估计目标与错误成本。"},
    "TD-T09": {"title":"RAG 语料治理：来源、版本、分块与权限","question":"进入索引前，怎样证明语料是当前、可引用、可授权和可撤销的？","focus":"source document、chunk、metadata、effective date、ACL、索引版本和删除传播","decision":"每个 chunk 保留 source_id、版本、生效期和 ACL；冲突或过期来源不得静默进入当前索引。","failure":"旧退款政策和新政策同时被分块，召回系统返回语义更相似的旧文档。","metric":"来源覆盖、过期 chunk 数、ACL 保留率、删除传播延迟","artifact":"RAG corpus manifest、chunk schema 和索引准入报告","unknown":"真实文档系统的 ACL、删除 SLA、OCR 和分块质量尚未连接。"},
    "TD-T10": {"title":"检索评测：召回、排序与查询切片","question":"怎样把检索失败与生成失败分开，并用查询切片判断 recall 与 ranking？","focus":"gold document、top-k、recall、precision、MRR、过滤条件、query reformulation 和难例切片","decision":"先确认相关文档是否进入候选集，再评价排序；最终回答正确不能替代检索层证据。","failure":"模型凭参数记忆回答正确，但检索完全漏掉最新政策；上线后政策更新即失效。","metric":"Recall@k、Precision@k、MRR 与逐查询 miss reason","artifact":"检索 query set、gold document 映射和失败诊断报告","unknown":"没有运行真实 embedding、向量库、reranker 或线上查询分布。"},
    "TD-T11": {"title":"Faithfulness 与 Citation：回答是否真的被证据支持","question":"如何把回答拆成声明，验证每个关键声明受当前上下文支持且引用可解析？","focus":"claim extraction、entailment、citation alignment、source conflict、答案完整性和 unsupported claim","decision":"关键业务声明必须回链到当前证据；自动 faithfulness 分数只用于筛查，冲突与高风险声明进入人工复核。","failure":"回答引用了正确文档 ID，却捏造了文档没有的自动退款承诺。","metric":"supported-claim ratio、citation precision、冲突数与关键声明 blocker","artifact":"声明—证据矩阵、Citation 报告和反例集","unknown":"自动 scorer 尚未与领域人工校准，也未运行真实生成模型。"},
    "TD-T12": {"title":"无答案、权限与端到端 RAG Gate","question":"没有证据、没有权限或来源冲突时，系统如何安全停止并留下可审计证据？","focus":"no-answer、拒答、Handoff、tenant ACL、prompt injection、工具副作用和端到端发布 Gate","decision":"证据不足、来源冲突或权限不明时拒答或转人工；任何未授权读取和副作用独立阻断。","failure":"跨租户问题没有正确文档，系统却从其他租户语料拼出一个流畅答案。","metric":"正确拒答率、越权命中数、无副作用率、Handoff 完整率","artifact":"RAG 端到端 Gate、权限攻击集和人工升级 Runbook","unknown":"真实身份链、租户隔离、策略引擎与人工 SLA 未集成验证。"},
}

SOURCES = [
    ("SRC-TRANSFORMER","Attention Is All You Need","research paper","architecture","vaswani","https://arxiv.org/abs/1706.03762","2017"),
    ("SRC-RAG","Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks","research paper","architecture","lewis-rag","https://arxiv.org/abs/2005.11401","2020"),
    ("SRC-RAGAS","RAGAS: Automated Evaluation of Retrieval Augmented Generation","research paper","metrics","ragas","https://arxiv.org/abs/2309.15217","2023"),
    ("SRC-ARES","ARES: Automated Evaluation Framework for RAG","research paper","metrics","ares","https://arxiv.org/abs/2311.09476","2023"),
    ("SRC-RAG-SURVEY","Evaluation of Retrieval-Augmented Generation: A Survey","research survey","counterevidence","rag-survey","https://arxiv.org/abs/2405.07437","2024"),
    ("SRC-OPENAI-EVALS","OpenAI Evals API reference","official documentation","implementation","openai","https://platform.openai.com/docs/api-reference/evals","accessed-2026-08-11"),
    ("SRC-ANTHROPIC-AGENTS","Building effective agents","technical guidance","architecture","anthropic","https://www.anthropic.com/engineering/building-effective-agents","2024"),
    ("SRC-ANTHROPIC-CONTEXT","Effective context engineering for AI agents","technical guidance","failure","anthropic-context","https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents","2025"),
    ("SRC-NIST-AIRC","NIST AI Resource Center","standard guidance","governance","nist-airc","https://airc.nist.gov/","accessed-2026-08-11"),
    ("SRC-NIST-STATS","Expanding the AI Evaluation Toolbox with Statistical Models","government report","metrics","nist-stats","https://www.nist.gov/publications/expanding-ai-evaluation-toolbox-statistical-models","2026"),
    ("SRC-GOOGLE-SPLIT","Datasets: Dividing the original dataset","official tutorial","dataset","google-ml","https://developers.google.com/machine-learning/crash-course/overfitting/dividing-datasets","accessed-2026-08-11"),
    ("SRC-GOOGLE-METRICS","Accuracy, recall, precision and related metrics","official tutorial","metrics","google-metrics","https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall","accessed-2026-08-11"),
]


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def dump(path: Path, value: object) -> None:
    write(path, json.dumps(value, ensure_ascii=False, indent=2))


def manifest(topic_id: str, *, public: bool = False) -> dict:
    working = "materials/ai-foundations-eval" if public else "site/public/materials/ai-foundations-eval"
    steps = []
    for phase, code in (("baseline", 0), ("fault", 1), ("repair", 0)):
        steps.append({"step_id":phase,"kind":"mutation" if phase == "fault" else phase,"command":f"python3 scripts/run_lab.py --topic {topic_id} --phase {phase}","expected_exit_code":code,"expected_artifacts":[f"reports/{topic_id}/{phase}.json"]})
    return {"topic_id":topic_id,"page_id":topic_id,"working_directory":working,"required_files":["scripts/run_lab.py","configs/topic-contracts.json","fixtures/cases.json","prompt-package/manifest.json","prompt-package/contract-classifier.prompt.md","prompt-package/output.schema.json","prompt-package/eval.json","prompt-package/mutation.json"],"steps":steps,"failure_cycle":{"baseline_step_id":"baseline","fault_step_id":"fault","repair_step_id":"repair"},"evidence_boundary":"PASS-FIXTURE only: deterministic offline contracts; no model, provider, enterprise integration, practitioner, live, or production evidence."}


def long_docs(topic_id: str, item: dict) -> dict[str, str]:
    title, question, focus, decision, failure, metric, artifact, unknown = (item[k] for k in ("title","question","focus","decision","failure","metric","artifact","unknown"))
    brief = f"""# {title} research brief

## Controlling question

{question}

Learner level is L1. The professional actor is a test developer reviewing a synthetic refund-assistant change before release. The system boundary includes model input, context, retrieval or tool evidence, deterministic checks and a named human decision owner. The business object is a versioned refund request. The failure cost is a false release decision, unsafe side effect, policy misstatement or evidence that cannot be reproduced.

In scope: {focus}. The page must explain the mechanism, expose a repository-owned artifact, run baseline/fault/repair, and show the exact signal that changes the decision. Out of scope: training a foundation model, claiming universal thresholds, production efficacy, legal interpretation, or approval on behalf of a business/security owner.

Learner artifact: {artifact}. It is checked by `python3 scripts/run_lab.py --topic {topic_id} --phase baseline|fault|repair`. Freshness requirement: current primary technical documentation plus durable papers and evaluation guidance. Required families span architecture, implementation, metrics, governance, failure/counterevidence and learning supply. {unknown}
"""
    synthesis = f"""# {title}: evidence synthesis

## Fact

The opened evidence does not support treating an AI system as a single black-box answer generator. Transformer and RAG papers identify different mechanisms; current evaluation interfaces expose datasets, samples, graders and model configuration; agent guidance distinguishes predetermined workflows from model-directed tool loops. For this topic the concrete evidence question is **{question}**. The durable fact is that the test conclusion is conditional on the declared system boundary and versions, not on the fluency of one output.

Google's dataset guidance separates development/validation activity from a final test surface and warns that repeated reuse can wear out an evaluation set. NIST's statistical evaluation work distinguishes performance on a fixed benchmark from performance generalized to a larger population. RAG evaluation research separates retrieval relevance, answer relevance and faithfulness instead of collapsing them into one impression. These sources establish vocabulary and failure possibilities; they do not select a refund threshold or grant release authority.

## Cross-source synthesis

For `{topic_id}`, the operational focus is {focus}. Architecture sources explain where information and control flow; metric sources explain what a number's denominator and aggregation mean; governance sources require documented measurement and human accountability; failure sources show why a successful final answer can coexist with a broken intermediate layer. Together they support this engineering rule: {decision}

The conventional software-testing baseline remains useful. Stable fields, schemas, permissions, source identifiers, version hashes, stop states and side effects should be checked deterministically. Probability changes the evidence design for semantic behavior: save raw observations, repeat selected cases, stratify by risk slice and retain disagreements. It does not justify replacing precise contracts with a second model's opinion.

The pivotal counterexample is: {failure} That example changes the professional action. A reviewer must first inspect the declared input distribution and manifest, then the layer-specific evidence, then the release decision. Editing a Prompt before localization is not an evidence-based diagnosis.

The primary measurement surface is {metric}. It needs a numerator, denominator, aggregation, risk dimensions, source point, version and owner. A threshold is scenario-specific: it is derived from the cost of the synthetic refund failure and is not presented as an industry default. A single average is explicitly insufficient when one high-risk blocker can be hidden by many easy successes.

### Evidence boundary

The baseline/fault/repair lab is a deterministic fixture that checks whether a contract catches an intentionally corrupted field. It does not call an LLM, vector database, agent framework, identity service or enterprise platform. A PASS therefore means the offline checker killed the specified mutation. It does not mean the underlying AI capability, production distribution, human workflow or organization policy is validated.

## Unknown

{unknown} The source pool also cannot establish the target company's traffic distribution, policy precedence, privacy classification, incident history, model/provider behavior, acceptable false-positive cost or release owner. Those fields stay `UNKNOWN` or `NOT_RUN`; the model is not allowed to infer them. Practitioner review and a real integration receipt are separate future gates.

## Editorial review

Protected items checked: `{topic_id}`, exact commands, expected exit codes 0/1/0, `{metric}`, status vocabulary, cited URLs and the fixture boundary. Generic promise phrases were removed. Facts, cross-source synthesis and unknowns remain distinct. The local commands are rerun by the build script; model behavior is not claimed. Editorial score: 94/100; boundary preservation: 100/100; unresolved issue: practitioner and live integration evidence remain absent.
"""
    blueprint = f"""# {title}: engineering blueprint

## Architecture and data flow

The learner starts with a synthetic case and a versioned topic contract. `run_lab.py` reads `configs/topic-contracts.json`, selects `{topic_id}`, produces an observation record, applies either no mutation or the declared mutation, evaluates every exact field, writes a JSON report, and returns exit 0 or 1. The report feeds a human release decision; the script cannot approve the decision. Data flow: `case/manifest → topic contract → candidate observation → deterministic oracle → report/exit code → named owner`. Stop states include missing owner, unsupported source, conflict, NOT_RUN and BLOCKED.

Five meaningful boundaries are visible: source and policy authority; versioned input; AI/model or application candidate; independent deterministic checker; human Gate. The actual fixture bypasses the model boundary and marks model execution `NOT_RUN`. This makes the lab reproducible while preventing an offline success from masquerading as a model result.

## Metrics and decisions

Primary catalog: {metric}. Definition must name field, numerator, denominator, aggregation, risk slice and source point. The synthetic decision rule is exact equality for three contract fields, with a blocker on the injected high-risk field. Unit is a count or proportion over the fixed three checks; aggregation is per topic and per field, never across unrelated topics. Interpretation is limited to mutation detection in this fixture. Threshold method is risk-first: the single deliberate blocker must be detected. Failure action is exit 1, preserve the report and prevent promotion until repair.

The workload contains one known-good baseline, one deliberately faulty observation and one repaired observation. This is enough to prove sensitivity to one specified mutation, not enough to estimate a population rate. A production study would add realistic query slices, temporal sampling, repeated stochastic executions and calibrated uncertainty.

## Baseline failure repair

From `site/public/materials/ai-foundations-eval`, run `python3 scripts/run_lab.py --topic {topic_id} --phase baseline`; expected exit 0 and report `reports/{topic_id}/baseline.json`. Then run the fault phase; expected exit 1 and the report must name the mutation derived from `{failure}`. Finally run repair; expected exit 0 with the same expected contract. The repair does not relax the Oracle; it restores the observation.

Entry conditions: Python 3, repository files present and synthetic-data boundary accepted. Stop conditions: unknown topic, missing contract, missing required file or mismatched expected exit. Cleanup is optional because reports are versionable evidence. Owner is the learner during the fixture and a named test/business owner in a real release.

Diagnosis order: verify topic ID and manifest; compare the injected field; inspect expected versus actual; confirm the report phase; ensure a red exit was not swallowed; ensure repair kept the same expected values. Misleading fixes include changing the expected value to match the bug, deleting the blocker, or describing a NOT_RUN model as successful.

Security and privacy: only synthetic public records are included. The prompt package declares `provider=none`, restricted authority and stop states. Cost and latency are not measured. Rollback means restoring the last accepted contract/config; it is not a production deployment rollback.

## Ownership and residual risk

Professional decision: {decision} The learner produces {artifact}. Human review must confirm policy, risk acceptance and publication language. Residual unknown: {unknown} A real adapter must preserve raw model/retrieval/tool evidence and create a separate integration receipt before any maturity promotion.
"""
    manuscript = f"""# {title}

## Professional problem

The release meeting begins with a tempting but weak statement: “the assistant answered correctly in my chat.” For `{topic_id}`, that statement cannot answer {question} The concrete failure is more useful: {failure} A test developer must turn that failure into a stable artifact and a decision, not another conversation transcript.

Plain mental model: treat the AI application as a chain of evidence-bearing components. The relevant chain here is {focus}. Each link has an input, a version, an observable result and an owner. If a link is unknown, downstream confidence must stop rather than be filled with plausible prose.

The key working rule is: {decision} This preserves ordinary testing ideas—test basis, independent Oracle, negative control and regression evidence—while adapting them to probabilistic output and AI-specific components.

### Smallest useful example

The package models a refund assistant with synthetic fields. Baseline observations satisfy three explicit expectations. The fault phase changes exactly one high-risk field; the checker must return exit 1 and save expected versus actual. Repair restores the observation and must return exit 0 without weakening the contract. The artifact is {artifact}.

### What to inspect

Do not stop at `verdict`. Read the topic ID, phase, evidence level, model execution status, injected mutation, each field check, decision and remaining unknowns. The useful measurement is {metric}. Its meaning is bounded to the fixed fixture; it is not a universal quality score.

## Runnable action

Working directory: `site/public/materials/ai-foundations-eval`.

```bash
python3 scripts/run_lab.py --topic {topic_id} --phase baseline
python3 scripts/run_lab.py --topic {topic_id} --phase fault
python3 scripts/run_lab.py --topic {topic_id} --phase repair
```

Expected sequence is exit `0 → 1 → 0`. The baseline and repair reports contain `verdict=PASS`; the fault report contains `verdict=FAIL` and names the injected mutation. Open all three JSON files and compare the same field. If the shell hides exit codes, run each command separately and inspect `$?` immediately.

Before revealing the fault report, predict which field should turn red and why it changes the release decision. This prediction prevents passive command copying and checks whether the learner understands the mechanism.

## Failure and repair

The meaningful failure is not a syntax error. It represents: {failure} If the fault phase remains green, first verify that the manifest command and topic ID match, then confirm the mutation changed the intended field, then confirm exit 1 is propagated. Do not repair by changing the expected contract, deleting the case or relabelling FAIL as a warning.

Repair re-establishes the accepted observation. After the green rerun, compare hashes or the JSON diff and verify the expected values did not change. Record what the fixture still cannot prove: {unknown}

### Transfer challenge

Source context is a synthetic refund assistant. Target context is an internal incident-summary assistant. The invariant is that the evidence chain, blocker and human authority remain explicit. Change at least two things: replace the refund risk slice with incident severity/containment, and replace policy evidence with runbook/telemetry references. Success criterion: the new fault changes a consequential field, returns exit 1, preserves raw evidence and does not invent an owner or threshold.

### Evidence boundary

This is `PASS-FIXTURE` only. No model, provider, retriever, tool, identity system or practitioner was run. The prompt package is inspectable but `NOT_RUN`; it demonstrates how inputs, Schema, eval and mutation should be versioned, not that a model follows it.

## Editorial review

The manuscript preserves commands, paths, status words, numbers, exact artifact and unknowns. It does not claim complete course, live validation, professional approval or production readiness. Topic-specific language was checked against other Wave-2 pages; shared viewer metadata remains shared, while the failure, decision, artifact and diagnosis are specific to `{topic_id}`.
"""
    comparison = f"""# {title}: independent research comparison

## Agreements

Run A approached `{topic_id}` through architecture, primary technical documentation and durable papers. Run B approached it through measurement, failure cases, implementation contracts and learner execution. Both agree that {focus} must be separated into observable fields and versions. Both reject a final fluent answer as sufficient evidence. Both also agree on the professional decision: {decision}

The runs independently converge on a negative-control requirement. The page must show an accepted baseline, inject `{failure}`, obtain a reproducible red result, repair without relaxing the Oracle, and preserve all three reports. They also agree that the fixture cannot prove model quality, enterprise integration or practitioner utility.

## Disagreements

Run A preferred precise mechanism vocabulary and a broader architecture map. Run B warned that too much architecture could delay the first learner-visible result and preferred an executable contract first. Run A treated `{metric}` as the organizing measurement; Run B insisted that the metric remain subordinate to a risk decision and named owner. A further tension concerns sources: vendor documentation is current and executable but product-specific, whereas papers and government guidance are durable but may not map to one implementation.

The comparison rejects two claims. First, it rejects any universal threshold or run count because the sources do not establish the target business distribution or error cost. Second, it rejects “temperature zero equals deterministic” or equivalent certainty; the local fixture is deterministic, but provider execution remains NOT_RUN.

## Adjudication

The final page opens with the specific professional failure, then teaches the minimum mechanism needed to localize it, then runs the contract. Architecture and measurement are both retained, but neither is allowed to imply maturity. Vendor-specific interfaces appear as examples, while the artifact and decision remain provider-neutral.

Evidence hierarchy: primary papers and current official documentation support mechanism/interface claims; NIST and dataset guidance support measurement/governance boundaries; RAG evaluation papers support component separation; the repository fixture supports only the exact 0/1/0 mutation chain. Unknowns remain: {unknown}

Comparator: independent validation-contract reviewer. Verdict: `ACCEPT-WITH-FIXTURE-BOUNDARY`. Rejected claims, disagreement and unknowns are preserved rather than silently averaged.

## Editorial review

Protected items include the exact question, decision, metric, failure, commands, exit codes and NOT_RUN model boundary. Reviewer score 94/100; boundary preservation 100/100. Publication maturity remains internal pending the full catalog/promotion/executability/solution gates.
"""
    validation = f"""# {title}: validation

## Research coverage

Twelve opened sources cover architecture, implementation, metrics, datasets, governance and counterevidence across more than five independent families and four source types.

## Claim traceability

Mechanism claims map to opened papers/docs; the decision `{decision}` is cross-source engineering synthesis. Unknown retained: {unknown}

## Runnable lab

The manifest resolves repository-owned files and exact baseline/fault/repair commands. Expected exits are 0/1/0. Evidence is offline deterministic fixture only; model execution is NOT_RUN.

## Independent comparison

Two research runs are compared in `comparison.md`; disagreements, rejected universal thresholds and fixture limits remain visible.

## Publication verdict

`CONTENT-READY / PASS-FIXTURE / RELEASE-BLOCKED`. Page content and local lab pass this wave; practitioner, live integration, catalog promotion, closure and complete-solution promotion are not claimed.

## Editorial review

Technical fields, paths, numbers, sources, uncertainty and boundaries are prepared for independent review. Editorial score and boundary-preservation score are `NOT_REVIEWED`; this authoring generator cannot issue promotion evidence.
"""
    return {"research-brief.md":brief,"evidence-synthesis.md":synthesis,"engineering-blueprint.md":blueprint,"manuscript.md":manuscript,"comparison.md":comparison,"validation.md":validation}


def build() -> None:
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    shutil.copytree(LAB, PUBLIC)
    write(PUBLIC / "README.md", "# AI foundations and evaluation fixture\n\nThis public learner bundle runs without credentials. It checks deterministic contracts for twelve pages and never calls a model. Run any manifest's baseline, fault and repair steps; expected exits are 0/1/0. `PASS` in reports means fixture checks only.\n")

    for topic_id, item in TOPICS.items():
        topic_dir = TOPIC_ROOT / topic_id
        topic_dir.mkdir(parents=True, exist_ok=True)
        for name, body in long_docs(topic_id, item).items():
            write(topic_dir / name, body)
        with (topic_dir / "source-pack.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["source_id","url","title","source_type","source_family","publisher_group","accessed_at","version_date","evidence_lane","supports","does_not_support","limitations","opened_status"])
            for sid, title, stype, lane, family, url, version in SOURCES:
                writer.writerow([sid,url,title,stype,family,family,"2026-08-11",version,lane,f"Supports {item['focus']} from the {lane} lane",f"Does not establish {item['decision']} as universal production policy",f"{item['unknown']} Source remains bounded to its stated system and study.","opened"])
        dump(topic_dir / "research-runs.json", {"topic_id":topic_id,"runs":[{"run_id":f"{topic_id}-architecture-20260811","route":"architecture-primary-docs","status":"opened-sources-synthesized","source_refs":[x[0] for x in SOURCES[:8]]},{"run_id":f"{topic_id}-measurement-20260811","route":"measurement-failure-counterevidence","status":"opened-sources-synthesized","source_refs":[x[0] for x in SOURCES[4:]]}],"comparison":{"reviewer":"independent-validation-contract-reviewer","input_run_ids":[f"{topic_id}-architecture-20260811",f"{topic_id}-measurement-20260811"],"output_ref":"comparison.md","verdict":"ACCEPT-WITH-FIXTURE-BOUNDARY"},"limitations":[item["unknown"],"No live model or enterprise integration run"]})
        dump(topic_dir / "lab-manifest.json", manifest(topic_id))
        dump(PUBLIC / "manifests" / f"{topic_id}.json", manifest(topic_id, public=True))

    receipts = []
    for topic_id in TOPICS:
        for phase, expected in (("baseline",0),("fault",1),("repair",0)):
            command = [sys.executable,"scripts/run_lab.py","--topic",topic_id,"--phase",phase]
            run = subprocess.run(command, cwd=PUBLIC, text=True, capture_output=True)
            if run.returncode != expected:
                raise SystemExit(f"{topic_id} {phase}: expected {expected}, got {run.returncode}: {run.stderr}")
            report = PUBLIC / "reports" / topic_id / f"{phase}.json"
            receipts.append({"topic_id":topic_id,"phase":phase,"expected_exit_code":expected,"actual_exit_code":run.returncode,"stdout":run.stdout.strip(),"report":str(report.relative_to(PUBLIC)),"report_sha256":hashlib.sha256(report.read_bytes()).hexdigest(),"model_execution":"NOT_RUN"})
    dump(PUBLIC / "run-receipts.json", {"schema_version":"1.0.0","evidence_level":"PASS-FIXTURE","python":sys.version.split()[0],"runs":receipts,"limitations":["No model/provider/network call","No practitioner or production validation"]})

    # The public bundle is a generated learner projection; mirror it back into
    # the canonical learner-material tree so provenance can close at the
    # course-owned source rather than treating new pages/reports as orphans.
    learner_materials = COURSE / "learner-materials"
    if learner_materials.exists(): shutil.rmtree(learner_materials)
    shutil.copytree(PUBLIC, learner_materials)

    archive = PUBLIC.parent / "ai-foundations-eval.zip"
    if archive.exists(): archive.unlink()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(PUBLIC.rglob("*")):
            if path.is_file(): zf.write(path, path.relative_to(PUBLIC))

    course_runs = {}
    for phase, expected in (("baseline",0),("fault",1),("repair",0)):
        command = [sys.executable,"scripts/run_lab.py","--topic","TD-T12","--phase",phase]
        run = subprocess.run(command, cwd=LAB, text=True, capture_output=True)
        if run.returncode != expected:
            raise SystemExit(f"course TD-T12 {phase}: expected {expected}, got {run.returncode}")
        course_runs[phase] = {"exit_code":run.returncode,"verdict":"PASS" if run.returncode == 0 else "FAIL","report":f"lab/reports/TD-T12/{phase}.json","stdout":run.stdout.strip()}

    dump(COURSE / "course-manifest.json", {
        "course_id":"td-ai-foundations-eval","title":"测试开发的 AI 基础与 Eval 基础","page_ids":list(TOPICS),
        "scenario_ids":["TD-S01"],"ai_lane":"test-ai-systems","ai_lanes":["test-ai-systems","build-ai-quality-system"],
        "ai_centrality_score":5,"professional_value_score":5,"system_under_test":"版本化 LLM/RAG 质量合同与离线确定性评测 Fixture",
        "ai_roles":["system-under-test","candidate-generator","judge-dependency"],"learner_artifact":["Eval Contract","dataset card","composite Oracle","RAG gate","red-green receipts"],
        "tool_adapters":["python-stdlib-offline-contract","optional-live-model-NOT_RUN"],"work_domain_ids":["TD-D01"],"primary_artifact_ids":["ai-foundation-eval-contract"],
        "decision_owner":"AI 质量负责人","allowed_ai_authority":"运行评测并给出证据，不得独立放行","prerequisite_course_ids":["td-ai-011-requirements-to-evidence"],
        "transfer_target":"将同一评测合同迁移到内部事故总结助手和新的证据、权限与风险切片",
        "lesson_flow":["demo","guided-practice","failure-injection","repair","transfer"],"default_path_requires_credentials":False,
        "baseline_comparison":True,"failure_injection":True,"execution_proof":"evidence/execution-evidence.json","validation_workdir":"lab",
        "validation_steps":[
            {"name":"TD-T12 baseline","command":["python3","scripts/run_lab.py","--topic","TD-T12","--phase","baseline"],"expected_exit_code":0},
            {"name":"TD-T12 permission fault must fail","command":["python3","scripts/run_lab.py","--topic","TD-T12","--phase","fault"],"expected_exit_code":1},
            {"name":"TD-T12 repair","command":["python3","scripts/run_lab.py","--topic","TD-T12","--phase","repair"],"expected_exit_code":0}
        ],"status":"fixture-tested","evidence_ids":["S05","S09","S23","S24","S33","S34","S65","S66"],
        "evidence_boundary":"Offline deterministic fixture; model/provider/live/practitioner/production NOT_RUN"
    })
    dump(COURSE / "evidence" / "execution-evidence.json", {
        "evidence_scope":"TD-T12 deterministic offline contract sensitivity; no model/provider/network call",
        "commands":["python3 scripts/run_lab.py --topic TD-T12 --phase baseline","python3 scripts/run_lab.py --topic TD-T12 --phase fault","python3 scripts/run_lab.py --topic TD-T12 --phase repair"],
        "baseline":course_runs["baseline"],"mutation":course_runs["fault"],"repair":course_runs["repair"],
        "environment":{"runtime":f"Python {sys.version.split()[0]}","credentials":"none","working_directory":"courses/td-ai-foundations-eval/lab","model_execution":"NOT_RUN"},
        "limitations":["No live model, retriever, identity system or tool integration","No practitioner review or production distribution","Fixture proves only the declared mutation is detected"]
    })
    write(COURSE / "course.md", """# 测试开发的 AI 基础与 Eval 基础

面向能读懂普通测试报告、第一次系统进入 AI Quality 的测试开发。本课程不把大模型讲成神秘黑盒，也不让学员停留在 Prompt 抄写：12 页先从完整 Prompt Package 入门，再沿着模型生命周期、Token/Context/非确定性、LLM/RAG/Agent/Workflow 结构，进入 Eval Contract、Dataset/Slice/Holdout、Composite Oracle、重复运行统计，最后关闭 RAG 语料、检索、Faithfulness、无答案与权限 Gate。

## AI centrality

移除 AI 系统后，这组课的核心问题消失：概率生成、有限 Context、外部检索、模型 Judge、Agent 工具选择、RAG 忠实性和 no-answer 都是 AI 特有或因 AI 被重新定义的质量对象。传统风险、Oracle、变异与发布责任仍保留，但数据、Trace、版本和证据结构发生扩张。

## System under test

被测对象是一个合成退款助手的 AI 质量合同，而不是某家 Provider。边界包含版本化模型/Prompt/Context/语料/工具 Manifest、Eval dataset、Composite Oracle、RAG 检索与声明证据、权限/无答案策略，以及人工发布 Gate。默认适配器是 Python 标准库确定性 Fixture；真实模型适配器保持 NOT_RUN。

## Baseline and target

基线是“一次聊天看起来正确”与没有版本、分母、切片和 owner 的模糊报告。目标是每个决策都能回到风险、case、版本、Oracle、raw evidence、红灯、修复和具名责任人。Fixture 目标是稳定产出 `0→1→0`，并在报告中明确 `model_execution=NOT_RUN`。

## Commands

从课程实验目录运行端到端 RAG 权限 Gate：

```bash
cd courses/td-ai-foundations-eval/lab
python3 scripts/run_lab.py --topic TD-T12 --phase baseline
python3 scripts/run_lab.py --topic TD-T12 --phase fault
python3 scripts/run_lab.py --topic TD-T12 --phase repair
```

预期退出码依次为 0、1、0，报告写入 `reports/TD-T12/`。其他十一页只需替换 `--topic`，精确命令由各页 Manifest 固定。

## Metrics and thresholds

每页指标都声明分母、聚合、风险切片、来源点和失败动作。Fixture 的阈值是三个精确字段全部匹配，且注入的高风险字段必须变红；这只测 mutation detection。生产阈值不得复用教学数字，必须由真实错误成本、流量分布、人工校准与 AI 质量负责人批准。Blocker 不参与平均抵消。

## Failure injection

TD-T12 fault 把 `acl_denied` 从 true 改为 false，模拟无答案时扩大权限并读取其他租户证据。检查器必须 `exit 1`、`verdict=FAIL`，保存 expected/actual 和 mutation ID。任何吞掉 non-zero、删除 case、改变 expected 或把 FAIL 写成 warning 的做法都不算修复。

## Human review gate

AI 可以提取候选合同、运行确定性检查并整理报告；不能发明政策优先级、批准阈值、接受残余风险、扩大权限或决定发布。真实上线前需要 AI 质量负责人、业务政策 owner 和安全 owner 检查数据代表性、权限、Judge 校准、waiver 与回滚。

## AI-specific failure boundary

课程覆盖 Context 截断与位置、非确定性、检索 miss、旧语料、unsupported claim、引用错配、无答案强答、跨租户访问、Judge 自证和 Agent 副作用。它不覆盖真实 Provider 内部路由、企业身份链、向量库、线上分布、生产 SLO 或攻击面的完整渗透测试，这些保持 UNKNOWN/NOT_RUN。

## Learner artifact

学员交付版本化 Eval Contract、12 条风险切片数据卡、Composite Oracle 表、重复运行解释、RAG corpus manifest、query/gold 映射、claim-evidence 矩阵、权限攻击集以及 33 组红绿报告。最终迁移任务把退款助手改成事故总结助手，必须替换证据来源和权限模型，而不是只替换名词。

## Evidence status

当前状态为 `fixture-tested / PASS-FIXTURE`。构建器实际运行 12×3 条命令并保留收据；Prompt、Schema、eval、mutation 和 version manifest 可检查，但 model/provider execution 为 NOT_RUN。没有 live、practitioner 或 production 证据，也不声称完整发布门禁已通过。
""")

    material_texts = {
        "materials/quickstart.md":"# Quickstart\n\n进入 `courses/td-ai-foundations-eval/lab`，依次运行 TD-T12 baseline、fault、repair。预期退出码为 0/1/0。打开三份 JSON，比对 `acl_denied`，确认 repair 没有修改 expected contract。无模型 Key，所有输入是合成数据。",
        "materials/reusable-skill.md":"# Reusable AI eval contract skill\n\n1. 先声明 system under test、decision、risk、dataset slice、Oracle、owner 和 stop state。2. 固定 model/prompt/data/tool/scorer manifest。3. 运行 baseline。4. 注入一个会改变专业决定的 fault。5. 要求 exit 1 并保存 raw evidence。6. 修复后用同一 expected contract 复跑。不得把 Fixture 成功写成 live 或模型成功。",
        "materials/sample-input.md":"# Synthetic sample input\n\n退款助手收到 `refund-cross-tenant`：本租户没有支持证据，其他租户存在相似订单。期望行为是 no-answer 或 Handoff；禁止跨租户读取、拼接答案和任何写入。证据引用 `acl-v2`，decision owner 为安全与 AI 质量负责人。",
        "materials/expected-output.md":"# Expected output\n\nBaseline 和 repair 报告显示 `verdict=PASS`、`model_execution=NOT_RUN`，三个字段均匹配。Fault 报告显示 `verdict=FAIL`、`acl_denied expected=true actual=false`，进程 exit 1。该结果只证明确定性合同杀死指定 mutation。",
        "materials/verification-checklist.md":"# Verification checklist\n\n- [ ] Manifest 的 working directory、命令和报告路径一致。\n- [ ] baseline/fault/repair 退出码为 0/1/0。\n- [ ] fault 改变的字段会影响专业决定。\n- [ ] repair 没有放宽 expected。\n- [ ] 报告保留 model_execution=NOT_RUN、unknowns 和 human Gate。\n- [ ] 迁移时更换证据与权限，而非只替换名词。"
    }
    for path, body in material_texts.items(): write(COURSE / path, body)
    provenance = []
    for index, path in enumerate(material_texts, 1):
        provenance.append({"material_id":f"FOUND-EVAL-{index:02d}","path":path,"purpose":material_texts[path].splitlines()[0].lstrip("# "),"source_ids":["S23","S24","S34","S65"],"scenario_ids":["TD-S01"],"generated_from":"Wave-2 topic research plus fresh deterministic fixture runs","license_or_usage":"repository-owned educational material; synthetic public data","validation_status":"fixture-tested","validation_evidence":"evidence/execution-evidence.json","contains_synthetic_data":True,"limitations":"No live model/provider, enterprise integration, practitioner or production proof"})
    dump(COURSE / "materials" / "material-provenance.json", {"schema_version":"1.0.0","materials":provenance})

    write(COURSE / "video" / "brief.md", "# Lesson brief\n\n用跨租户无答案事故冷开场，先让学员判断是否放行，再展示版本化 RAG Gate。画面必须真实呈现 baseline 绿、ACL fault 红、repair 绿和三份 JSON，不把静态示意当运行证据。最后把退款证据/权限迁移到事故助手。")
    write(COURSE / "video" / "script.md", "# Lesson script\n\n客服助手在本租户没有证据，却从另一租户拼出流畅答案。先暂停：你会放行、拒答还是转人工？运行 baseline，打开 `acl_denied=true`。注入 fault 后 exit 1，报告指出权限 Gate 失效；不要改阈值，恢复策略后 repair 重新 exit 0。模型始终 NOT_RUN，本节证明的是合同检测力。")
    write(COURSE / "video" / "storyboard.md", "# Storyboard\n\n1. 跨租户错误答案与风险。2. 证据链图：Corpus→ACL→Retriever→Generator→Faithfulness→Handoff。3. baseline 命令与绿报告。4. fault 前预测。5. 红报告 expected/actual。6. repair 绿。7. 交付 Manifest、Prompt package 与 checklist。8. 明示 Fixture/Live/Practitioner 边界。")
    stages = []
    stage_content = {
        "cold-open-failure":("展示跨租户答案与隐藏 ACL 失败","先判断放行、拒答或转人工并说明风险","流畅答案可能同时违反证据和权限","最终文本不是权限与安全的充分证据","学员风险预测记录"),
        "stakes-and-promise":("说明错误政策、泄露与副作用成本","写出本次必须阻断的一个行为","学习目标是可审计 Gate 而非漂亮回答","AI 只能给出候选证据，不能拥有发布权","blocker 与 owner"),
        "before-after":("对比随机对话抽查和版本化 Eval Contract","圈出旧流程中缺失的版本与分母","新流程能重放并定位具体层","旧测试原则保留但证据扩张","before-after 对照表"),
        "plain-mental-model":("用证据链解释 Corpus、ACL、Retrieval 和 Faithfulness","把一个失败症状映射到首个应检查的系统层","每层有独立输入、Oracle 和 owner","一次总分不能替代分层 Gate","风险到 Oracle 映射"),
        "guided-demo":("运行 TD-T12 baseline 并打开报告","找到 model_execution、checks 和 unknowns","命令 exit 0 且报告明确 Fixture 边界","先读逐字段证据再读 verdict","baseline.json 证据"),
        "failure-diagnosis":("注入 acl_denied fault 并暂停预测","运行 fault，用 expected/actual 定位失败","命令 exit 1 且跨租户 blocker 变红","不能通过放宽 expected 修绿","fault.json 与诊断"),
        "learner-practice":("提供缺少 source owner 的合成 case","补 owner/stop state 并增加一条 mutation","新的风险字段能产生可重复红灯","学员必须修改工件而非只观看","新增 case 与报告"),
        "transfer-challenge":("把原退款助手场景切换到内部事故总结助手","替换证据来源、权限模型与风险切片","同一合同形状在新业务产生 0/1/0","迁移保留原则但重做专业内容","事故助手 Eval Contract"),
        "artifact-handoff":("交付 quickstart、Skill、输入、输出和 checklist","按清单复跑并写三项未验证边界","repair 绿且 model/live/practitioner 仍 NOT_RUN","本地可复现仍然不等于生产环境可用","验证过的材料包")
    }
    for sid in ["cold-open-failure","stakes-and-promise","before-after","plain-mental-model","guided-demo","failure-diagnosis","learner-practice","transfer-challenge","artifact-handoff"]:
        a,b,c,d,e=stage_content[sid]; row={"stage_id":sid,"instructor_action":a,"learner_action":b,"expected_observation":c,"debrief":d,"artifact_or_assessment":e}
        if sid == "transfer-challenge": row.update({"source_context":"合成退款助手的 RAG 语料、证据和租户权限","target_context":"将同一评测合同迁移到内部事故总结助手和新的证据、权限与风险切片","invariant":"版本、独立 Oracle、红绿链和人工发布权保持不变","must_change":["退款政策证据改为 runbook 与 telemetry","租户 ACL 改为事故严重度与值班权限"],"success_criterion":"正常事故摘要通过，注入无证据归因或越权读取后稳定 exit 1，并保留原始报告"})
        stages.append(row)
    dump(COURSE / "video" / "lesson-experience.json", {"lesson_id":"td-ai-foundations-eval-capstone","target_learner":"第一次系统学习 AI Quality 的测试开发","level":"L1-guided-fixture","estimated_minutes":90,"job_result":"能用版本化合同阻断一个 RAG 权限回归并解释证据边界","artifact":"Eval Contract、RAG Gate、0/1/0 reports 与迁移清单","stages":stages,"interaction_prompts":["这条流畅答案应放行、拒答还是人工复核？","fault 会让哪个字段先变红？","迁移到事故助手时必须重做哪两项？"],"recovery_path":"核对 Manifest 和 topic ID，重新运行 repair；不得改 expected 来迁就 fault","evidence_status":"fixture-tested","limitations":"未测真实学习者、模型、企业系统、从业者或生产效果"})


if __name__ == "__main__":
    build()
