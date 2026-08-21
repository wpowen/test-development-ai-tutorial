---
name: career-ai-course-factory
description: Research, assimilate user-provided professional sources, build, and validate AI-native profession courses with atom-level information-fidelity receipts, beginner term dependencies, directly reusable artifacts, topic-specific visuals, continuous learner numbering, mandatory page capability profiles, professional methods, independent Oracles, real-model and integration evidence lanes, clean-room labs, practitioner and learner gates, status supersession, curriculum-gap discovery, and publication closure. Use when discovering how AI changes a profession, incorporating supplied documents without silent omission, creating or repairing a task-oriented professional documentation system, checking whether beginners and practitioners can understand and reuse it, refreshing AI tools, or packaging validated lessons for sites, GitHub, videos, and learner materials.
---

# Career AI Course Factory

## Non-negotiable outcome

Build courses about **how AI changes the profession's real work**, not ordinary career training with an AI prompt attached. Every selected course must pass this counterfactual gate:

> If AI, an AI system under test, or an AI agent is removed, does the course lose its central problem, workflow, or deliverable?

If the answer is no, reject or rewrite the topic. “Use a chatbot to draft X” is not sufficient by itself.

The only exception is an explicitly labelled `profession-baseline` bridge or entry assessment required to prove prerequisite competence. It does not count as an AI-native course, differentiation claim, or marketable AI outcome; its job is to prevent advanced AI lessons from assuming missing professional foundations.

Do not claim professional authority. Separate sourced facts, practitioner signals, vendor claims, inference, and unknowns. High-risk professional decisions require qualified review.

## Modes

- `discover`: map the profession's AI transformation and rank 10-20 course opportunities.
- `build-course`: produce one runnable AI-native course and material pack.
- `build-series`: create a sequenced curriculum across all four AI lanes.
- `update-tools`: refresh model, framework, agent, evaluation, and fallback adapters.
- `package-video`: derive a video only after the course passes professional-utility gates.
- `build-tutorial`: turn the researched profession map into a beginner tutorial knowledge tree, tutorial pages, and a self-contained learning site.
- `research-topic`: deeply research one approved topic into an evidence synthesis, engineering blueprint, learner manuscript, and validation record.
- `validate`: run structural, evidence, AI-centrality, and execution-proof gates.

Read the references required by the selected mode:

- Research and competitors: `references/research-protocol.md`
- Multi-channel evidence and source independence: `references/multi-channel-evidence-protocol.md`
- Search routing and freshness: `references/search-and-freshness-protocol.md`
- Evidence-bounded profession veteran reconstruction: `references/profession-veteran-reconstruction-protocol.md`
- Profession/work-domain decomposition: `references/profession-decomposition-protocol.md`
- Full profession knowledge system and completeness gate: `references/profession-knowledge-system-protocol.md`
- Profession-to-AI curriculum architecture: `references/curriculum-architecture-protocol.md`
- Proactive coverage and missing-topic discovery: `references/curriculum-gap-audit-protocol.md`
- Business scenario proof: `references/business-scenario-protocol.md`
- Career/task schema and ranking: `references/career-task-schema.md`
- Course/runtime contract: `references/course-material-contract.md`
- Professional utility gates: `references/professional-utility-gates.md`
- Tool freshness: `references/tool-update-protocol.md`
- Validation status: `references/validation-rubric.md`
- Lesson experience and material handoff: `references/teaching-experience-protocol.md`
- Beginner tutorial tree, page types, and viewer: `references/tutorial-site-contract.md`
- Canonical catalog, exact promotion, executability, and artifact closure: `references/catalog-promotion-and-publication-integrity-contract.md`
- Per-topic deep research, engineering blueprint, and manuscript: `references/topic-research-and-manuscript-protocol.md`
- Claim-level ChatGPT/OpenAI Deep Research execution, receipts, contradiction review, and saturation: `references/claim-level-deep-research-protocol.md`
- Global research execution control, batch budgets, stop conditions, and completion contract: `references/research-execution-control-protocol.md`
- Auditable Codex-native multi-agent research when explicitly selected: `references/codex-research-execution-contract.md`
- Cross-lifecycle professional artifact chain: `references/professional-artifact-chain-protocol.md`
- Complete solution architecture, maturity, and traceability: `references/complete-solution-contract.md`
- Technical editorial and anti-template gate: `references/technical-editorial-humanizer-gate.md`
- Research→factory methodology acquisition: `references/profession-methodology-acquisition-protocol.md`
- Professional document interpretation: `references/professional-document-interpretation-protocol.md`
- User-source assimilation and atom-level information fidelity: `references/source-assimilation-and-information-fidelity-contract.md`
- Source exemplar functional quality and semantic parity: `references/source-exemplar-quality-and-semantic-parity-contract.md`
- Beginner comprehension and directly reusable artifacts: `references/beginner-comprehension-and-direct-reuse-contract.md`
- Topic-specific visuals and continuous learner sequence: `references/visual-knowledge-and-sequence-contract.md`
- Cross-artifact reconciliation and traceability: `references/artifact-reconciliation-and-traceability-protocol.md`
- Core/adapter boundary: `references/profession-adapter-contract.md`
- Prompt, eval, mutation package: `references/professional-prompt-package-protocol.md`
- Software testing adapter (only when declared): `references/software-testing-method-selection-adapter.md`
- Software testing career evidence and Agent architecture adapter (only when declared): `references/software-testing-career-and-agent-architecture-adapter.md`
- Mandatory page capability, real-evidence, clean-room, practitioner, learner, and status-supersession contract: `references/professional-capability-and-evidence-contract.md`
- Page depth and research→page projection fidelity: `references/page-depth-and-projection-fidelity-contract.md`

Every promised learner-facing page must have an exact record in `research/capability-profiles.json` and `research/professional-evidence.json`. Do not allow `none`, an empty capability, a title heuristic, or an undeclared page. Group declarations in `research/capability-declarations.json` must cover every page/capability pair. Keep model, integration, clean-room, practitioner, and learner evidence independent; a missing lane is not an implicit `NOT_RUN`.

When a page declares `artifact-transformation`, apply the factory contract fail-closed. The declaration is the only profession-method trigger; do not infer a method from page titles, course IDs, or profession names. Require a profession method library, per-topic transformation contracts, a versioned prompt package with eval and mutation records, and a traceability graph closing `source → claim → risk → method → oracle → case → result`. Source authority/precedence must be explicitly declared with owner and evidence; never apply a default PRD/OpenAPI/design ordering. Missing or ambiguous precedence is `BLOCKED`.

## Four mandatory AI lanes

Research all four before choosing a topic. A series should cover all four unless evidence shows one is irrelevant.

1. `use-ai-for-work`: use models or agents to improve traditional professional work.
2. `test-ai-systems`: evaluate LLM, RAG, multimodal, or agent products.
3. `agentize-work`: turn a bounded workflow into a supervised agent loop.
4. `build-ai-quality-system`: datasets, evaluation, observability, CI gates, governance, and feedback loops.

## Workflow

### 1. Define the professional outcome

Record learner level, work setting, current toolchain, recurring outputs, costly failures, privacy constraints, and one observable job result. Do not choose a tool yet.

### 1A. Freeze and fully assimilate user-provided sources

Before summarizing or designing the curriculum, follow `references/source-assimilation-and-information-fidelity-contract.md`. Copy every user-provided source into a private package-local research area, preserve its original hash, and run `scripts/build_source_assimilation_ledger.py` to inventory every section and substantive atom.

Adjudicate every item as `incorporated`, `adapted`, `rejected`, `blocked`, or `superseded`. Preserve source locator, protected meaning, target, rationale, owner, and evidence. Never delete a detailed rule because it looks organization-specific; place it in a scoped adapter, labelled example, or explicit rejection record. Consume the inventory's detected obligations: career evolution/level/promotion content forces `career-evolution-system`; Agent architecture/testing content forces `agent-architecture-testing`. Do not continue while any item is `UNMAPPED`, a required capability/adapter is undeclared, a source hash drifts, or the coverage receipt is not exact.

Then follow `references/source-exemplar-quality-and-semantic-parity-contract.md`. Create `research/source-semantic-projection.json` and preserve every incorporated/adapted atom's teaching function as an exact page, rendered visual, editable artifact, prompt package, exercise, or explicit scoped adaptation. Atom coverage alone is not quality parity.

### 2. Discover retrieval surfaces and create the search plan

Follow `references/search-and-freshness-protocol.md`. Inspect available connected resources, local files, live web search, browser access, official documentation, repositories, and platform search before choosing a route. Do not assume one named search tool exists.

Create and preserve:

- `research/search-plan.json`;
- `research/search-log.csv`;
- `research/technology-radar.json`.

The search plan must cover Chinese and English query families for role reality, current AI capabilities, profession-specific workflows, executable artifacts, failures, competitors, adoption, and counterevidence. Search-result snippets are leads only; open the selected page before adding it to the source ledger.

If live retrieval is unavailable and freshness matters, stop with `BLOCKED-FRESHNESS`. Never claim “latest” from model memory.

### 3. Research role reality, AI reality, and market supply

Follow `references/research-protocol.md` and `references/multi-channel-evidence-protocol.md`. Search in Chinese and English. Build:

- `research/source-ledger.csv`;
- `research/channel-coverage.json`;
- `research/github-artifacts.csv`;
- `research/learner-signals.csv`;
- `research/evidence-matrix.md`;
- `research/competitor-matrix.csv`;
- `research/ai-capability-map.md`;
- `research/scenarios.json`.

Use official docs and repositories for capability claims, direct course pages for competitor claims, and communities only for pain language or failure signals. Record publisher groups and source families so copied or same-vendor pages cannot masquerade as independent confirmation. GitHub stars, course enrollment, views, likes, and vendor marketing metrics are discovery or popularity signals, never efficacy proof.

### 3A. Reconstruct the profession through an evidence-bounded veteran Agent

Follow `references/profession-veteran-reconstruction-protocol.md` before decomposing work or selecting AI scenarios. The veteran framing is a research role, not evidence by itself and not a claim of personal employment history.

Create `profession-reality-map.md` and `research/profession-reality-map.json`. Reconstruct role variants, an ordinary day, a weekly or sprint rhythm, one full deliverable lifecycle, one exception path, dependencies, tools, artifacts, decision rights, failure costs, performance and promotion signals, pain points, information barriers, current workarounds, and public-versus-internal knowledge gaps.

Run independent veteran-operator, manager/promotion, workflow/platform, junior-observer, market/community, AI-systems, and adversarial-critic passes. Preserve disagreements. Do not invent target-company policies, data, access, incident history, or promotion rules; mark them `INTERNAL-UNKNOWN` with the interview question or document needed to close the gap.

Only after this map passes may the Skill classify work as `retained`, `assisted`, `automated`, `transformed`, `new-work`, or `declining`. Every selected AI opportunity must connect a real pain to an inspectable artifact, a human decision, a measurable baseline, a failure mode, and a beginner-reusable starter pack.

### 4. Decompose the profession before selecting scenarios

Follow `references/profession-decomposition-protocol.md` and build `research/profession-map.json`. Map role variants, at least five work domains, business events, work objects, artifacts, systems, decision rights, failure costs, and the end-to-end lifecycle.

Do not divide the curriculum by tools. Trace every candidate through:

`role variant -> work domain -> business event -> artifact -> failure -> AI intervention -> learner proof -> reusable material`.

### 4B. Research→factory artifact transformation (opt-in)

For an explicit `artifact-transformation` capability, run in order: acquire and freeze profession methods; interpret each professional document into typed claims; reconcile artifacts and preserve bidirectional traceability; choose methods with a recorded rationale and independent oracle; assemble versioned Prompt/Eval/Mutation packages; then run mutation and human/owner gates. Any missing source, rationale, oracle, eval, mutation, trace link, or blocked/unknown status stops downstream work. Fixture evidence remains `fixture-tested` and cannot become live or practitioner evidence.

### 4A. Build the profession knowledge system

Follow `references/profession-knowledge-system-protocol.md`. Create `industry-framework.md` and `research/profession-knowledge-system.json` before any learning architecture or course ranking.

Reconstruct five mandatory dimensions: end-to-end lifecycle, specialization families, system/work-object classes, quality/outcome attributes, and role/career evolution. Then classify AI changes as `retained`, `assisted`, `automated`, `transformed`, `new-work`, or `declining`, preserving the non-AI baseline, human accountability, new failures, controls, learner proof, source IDs, and confidence.

Build the coverage cube across lifecycle, specialization, system, outcome, and learner level. High or critical gaps block curriculum generation. This is the gate that must discover API, stability, performance, security, platform, operations, or other profession-specific specialties even when the user never names them.

### 4B. Build the profession-to-AI learning architecture

Follow `references/curriculum-architecture-protocol.md`. Create `learning-architecture.md` and `research/competency-transition-map.json` before ranking courses.

Use two explicit spines:

- the profession spine reconstructs the existing lifecycle, methods, tools, artifacts, decisions, and failure costs;
- the AI spine introduces model lifecycle, inference behavior, application patterns, capability boundaries, evaluation, agents, production quality, and benchmark literacy.

Join them with a competency transition matrix. Every course must say which existing professional principle remains valid, what AI changes, which new failure appears, what new capability is required, and how the learner proves it.

A complete series must cover the eight layer kinds in dependency order:

`profession-baseline -> ai-foundation -> ai-assisted-work -> ai-system-quality -> agent-workflow-quality -> quality-engineering -> benchmark-literacy -> capstone`.

Learners may test out of explanatory pages, but may not bypass a layer's artifact-based exit assessment. For `ai-quality-engineer`, keep LLM, RAG, Agent, Workflow, and Benchmark as explicit specialization tracks rather than one shallow “AI testing” bucket.

### 4C. Audit curriculum coverage before selecting courses

Follow `references/curriculum-gap-audit-protocol.md`. Build `research/curriculum-coverage-matrix.csv` and the human-readable `curriculum-gap-analysis.md` before creating or ranking `curriculum.json`.

The audit must use six evidence systems: industry body of knowledge, real work and practitioner evidence, AI technical frontier, open-source implementations and benchmarks, existing course supply, and failure/learner/counterevidence. More sources in one system cannot excuse a missing system.

Map every candidate learning cell across profession domain, learning layer, specialization, learner level, realistic scenario, learner artifact, exit assessment, and evidence status. Then run independent reviews from a profession veteran, AI systems engineer, evaluation/quality expert, curriculum designer, market/learner researcher, and adversarial critic. When subagents are available, preserve their independent findings; otherwise use separated passes.

Do not continue when a high or critical gap lacks a decision, a required learning layer is absent, or an AI-quality profile has no distinct LLM, RAG, Agent, Workflow, and Benchmark cells. This gate exists so the Skill discovers missing foundations and professional topics itself instead of waiting for user corrections.

### 4D. Build the complete topic system before writing pages

Follow `references/topic-research-and-manuscript-protocol.md`. Create `research/topic-system.md` from the profession knowledge system, competency transition map, and curriculum coverage matrix.

Every topic needs one controlling question, explicit scope, prerequisite concepts, a professional decision, a learner artifact, and a verification path. The topic system is the completeness surface; it may contain planned topics. It is not evidence that any page has been written.

Reject topic lists generated from an arbitrary lesson count, one-line course records, or tool names. Split topics that contain multiple independent job results. Run the coverage audit against the topic system before selecting the first manuscript.

### 4E. Design the professional artifact chain

Follow `references/professional-artifact-chain-protocol.md` before writing any lifecycle course. Reconstruct how real inputs become reviewed intermediate artifacts, executable work, evidence, decisions, and downstream updates. Every artifact must name its schema, owner, source references, version, allowed AI authority, human gate, downstream consumer, and stop states.

Reject a workflow that jumps directly from source documents to plausible prose or generated files. `UNKNOWN`, `BLOCKED`, `NOT_RUN`, and `SUPERSEDED` must remain distinct from `PASS` and `FAIL`. When a critical input, source reference, Oracle, environment, or accountable owner is missing, stop the chain instead of asking the model to infer a completion.

### 5. Build evidence-backed business scenarios

Follow `references/business-scenario-protocol.md`. A scenario is not “用 AI 写测试用例”; it names the actor, trigger, business system, business object, realistic input, current workflow, failure cost, constraints, AI intervention, inspectable output, decision or handoff, AI-specific failures, and validation plan.

Each selected scenario must triangulate three evidence classes and three independent source families:

1. profession/workflow reality;
2. current AI capability;
3. practitioner case, issue, job requirement, public artifact, or counterevidence.

Map every task and course to a stable `scenario_id`. When authentic enterprise data is unavailable, use a clearly labelled synthetic fixture; this can prove runnability, not professional prevalence or production efficacy.

### 6. Build the AI transformation map

For each task, state:

- which AI lane it belongs to;
- whether AI is assistant, system under test, agent, judge, or infrastructure;
- the non-AI baseline;
- the AI-specific failure modes;
- the learner-visible proof;
- the reusable artifact;
- the smallest runnable validation.

Reject a task when AI centrality is below 4/5, the output cannot be checked, or the learner only copies a prompt and receives plausible prose.

### 7. Analyze competitors before designing the series

Compare at least six directly relevant offerings across at least three platforms. Capture audience, promise, modules, hands-on artifact, execution proof, assessment, price/lead-generation model when public, freshness, and gaps. A long syllabus is not proof of practical value.

Derive differentiation from missing learner proof, not from a different title. Common defensible gaps include runnable fixtures, negative tests, failure injection, traceability, versioned adapters, CI gates, and post-run diagnosis.

### 8. Rank and sequence the course portfolio

Use `references/career-task-schema.md`. AI centrality, professional leverage, runnable proof, repeat reuse, and source strength are hard-weighted. Risk and verification difficulty remain separate gates. Build as many topics as the transition matrix needs; a compact series may have 10-20 topics, while a broad professional documentation system may need 20-60 smaller topics grouped by work domain and specialization.

Sequence by knowledge and artifact dependencies, not popularity:

`professional baseline -> AI foundations -> bounded assisted-work lab -> AI system evaluation -> agent/workflow evaluation -> production quality loop -> benchmark literacy -> capstone`.

Every curriculum entry records `stage_id`, `level`, `prerequisite_course_ids`, `knowledge_dependencies`, `professional_baseline`, `new_ai_capability`, `assessment`, `source_ids`, and `delivery_status`. A stage is complete only when its exit artifact passes; watching the pages is not completion.

Create a separate learner-facing `display_number` exactly equal to `1..N`; never expose internal IDs or module-local order as the sequential lesson number. Require definitions for Prompt, RAG, Agent, Workflow, Oracle, dataset, metric, and other foundation terms before any dependent page. Stable IDs remain unchanged for traceability.

### 8A. Research and synthesize every promised topic through clustered, route-aware evidence

103 个公开页面仍必须 100% 纳入 claim inventory、证据路由、独立裁决、投影定位和发布门禁；页面数量不等于外部 Deep Research 单元数量。先按 `references/claim-level-deep-research-protocol.md` 执行 R0，再决定哪些 canonical external claims 需要联网。不得先为每个页面或每个相似句子发起 provider 请求。

执行以下 R0–R7 流程：

1. **R0 全覆盖、不联网**：从当前 catalog 读取 exact page IDs，先用 `scripts/build_claim_source_manifest.py` 生成 hash-bound 的 `claim-source-manifest.v1`，再抽取每页每条原子命题，生成 `claim-cluster-map.v1`、主簇/关联簇、风险、`evidence_class`、route、适用维度、身份/范围/版本/环境/总体/区域语言/供应商字段。source manifest 必须同时绑定 topic package、canonical page assembly 和 learner/material surfaces；当前未覆盖的页面必须显式记录 `pages_expected`、`pages_with_claim_inventory`、`missing_page_count` 和 missing IDs；不能把部分 inventory 写成 103/103。
2. **R0 先路由**：`LOCAL-DETERMINISTIC`（仓库、Schema、Prompt、runner、fixture、projection、状态和教学默认值）进入本地验证；`TARGET-EVIDENCE`（真实 provider、企业权限、真实数据、生产、从业者或学习者效果）进入目标证据；`TEACHING-VALIDATION` 进入设计或人群证据；未知或高风险条件不完整时保持 `BLOCKED`/`UNKNOWN-EXPLICIT`。只有 `EXTERNAL-RESEARCH` 的 external technical fact / empirical generalization 进入 R1。
3. **R1–R4 canonical external research**：按规范化 request fingerprint 去重，只为合资格的 canonical anchor 运行正式 ChatGPT/OpenAI Deep Research；按适用风险执行 initial、技术文档重建、counterevidence 和 gap-fill。anchor 可产生 N2 canonical knowledge packet，但 packet 是共享证据资产，不是多个 claim 的 provider receipt。
4. **R5 本地验证**：使用代码、Schema、runner、fixture、运行 manifest 和 hash 证明本项目是否真的执行。外部网页、普通模型摘要和静态意图不能证明本仓库已经运行。
5. **R6 目标证据**：用目标系统快照、真实运行、授权、生产回读、从业者或学习者记录证明目标断言；缺少目标证据时阻断，不得用通用网页、fixture 或 Luna 摘要替代。
6. **R7 独立裁决与投影**：每个页面保留自己的 claim trace、`transfer decision`、适用维度、`cannot-prove`、矛盾/裁决、最终 disposition 和 projection locator。`DIRECT-REUSE` 只复用同范围来源适用性；`SOURCE-REUSE-DELTA` 必须产生本 claim 的差异工件；`NO-REUSE` 必须独立研究或阻断。anchor 的 `SATURATED` 不能自动升级成员 claim。

共享来源不等于共享结论。任何 canonical packet 都必须声明 `supports_predicates`、`cannot_prove`、来源族、版本/时间/环境/总体/区域语言/风险、反证、裁决和失效触发器；成员 claim 只能通过逐字段 transfer check 引用，不能复制 report、receipt、final disposition 或 saturation。

使用 `scripts/prepare_claim_inventory.py` 从独立审阅的 `claim-list.v1` 编译 hash-bound inventory；不得在 `unmapped_propositions` 不为 0、页面缺失、overlay 未批准或主簇/路由未知时继续研究。历史 claim list 迁移必须先运行 `scripts/propose_locator_migration.py`，再用 `scripts/apply_locator_migration.py`；后者只允许把已存在、root 明确、行号新鲜且 selector 唯一的 `AUTO-CANDIDATE` 写入正式 inventory。提案可以在明确边界内归一化 workspace/topic-relative 路径、唯一 CSV/JSON selector、唯一 canonical `tutorial/materials` 或 `content/modules` 后缀、单行/数字行范围和显式 JSON Pointer；它不得自动绑定外部 factory root。任何 `MANUAL-SELECTOR-REQUIRED`、`MISSING-SOURCE`、`LINE-RANGE-INVALID` 或异常都只能留在 proposal/pending 工件中，禁止猜 root、补默认行号或生成半真半假的正式 ledger。每个成功迁移的 inventory 还要保留 proposal hash、claim-list hash 和迁移状态，随后重新运行 locator contract、freshness、source hash 和篡改回归。每个 topic 仍需自己的 route-aware package 和 `projection-ledger.json`，但不得复制另一 topic 的 report、receipt 或 saturation 来满足文件数量。

对于 OpenAI Responses API，使用 `scripts/run_claim_deep_research.py` 仅执行已批准的 canonical anchor 或命名的 delta/gap run。模型通过 `--model` 或 `OPENAI_DEEP_RESEARCH_MODEL` 在运行时解析；不要硬编码已废弃模型。公开 web 与私有 file search/remote MCP 默认分离，混合需显式风险审阅。runner 必须保存 request、raw response、report、citations、opened sources、tool calls、hash、provider response ID 和 receipt；缺任一项就保留诊断并返回 `BLOCKED-DEEP-RESEARCH`，不得写入 completed receipt。TD-T09 已有历史 receipt 原样保留，不重写、不复制、不升级。

外部 packet 的独立 auditor 必须记录 supports/cannot-support predicates、版本/范围/环境/总体/风险、反证、矛盾、失效条件和饱和。成员 claim 仍须独立完成 transfer/adjudication/projection，不能继承 anchor 的 final disposition。运行 `scripts/validate_career_package.py <package-root>` 在 synthesis 前和 promotion 前各一次；静态验证只能证明工件一致性，不能把 fixture 或本地摘要升级为 live/provider/practitioner/learner 证据。

然后按 `references/topic-research-and-manuscript-protocol.md` 生成 topic 包。OpenAI/Codex receipt 只在其各自 execution contract 下有效，不能混用来借用成熟度。外部来源数量、反证轮和研究包门禁按适用 canonical packet 和风险计算，不得为了满足每页数量重复联网。

#### Lower-cost model boundary

Luna 或其他低成本模型可以负责长文抽取、原子命题候选、字段规范化、簇候选、来源去重候选、技术文档 Markdown 整理、缺口排序、成本汇总和页面整合。其输出必须标记为 proposal/integration artifact，并由独立 auditor 复核。Luna 不得生成、补写或冒充 provider response ID、raw response、source-open event、citation trajectory、completed receipt、saturation PASS、target PASS、practitioner PASS 或 learner PASS；Luna 对话不是 OpenAI Deep Research receipt，也不是 Codex runtime trace。

为控制重复研究成本，R0 完成后先按 canonical cluster、evidence class、风险和 unresolved dimension 合并研究单元，再由 Luna/planner 生成去重与路由 proposal；未分类、范围不清、版本/安全/目标证据缺失的命题保持 `BLOCKED-UNCLASSIFIED`，不得进入外部请求估算或批量联网。只有独立 auditor 批准 proposal 后，才可为 canonical anchor 或 decision-changing delta 创建 provider request；成员 claim 必须通过逐字段 transfer check，不能因文本相似自动复用。所有运行事件通过 `scripts/compile_research_cost_telemetry.py` 编译，`openai-chatgpt`、`openai-api`、`codex-research` 的 provider savings 与 `planner`/`luna` 的 `summary.lower_cost` 分开；缺 token baseline、重复 attempt lineage、provider/model 合法组合或失败详情时，节省值保持 `UNKNOWN`/`NOT-COMPUTABLE`，不得用 Luna 的 token 估算冒充 Deep Research 节省。

#### Global execution control

在任何命题请求前先建立并验证 `research-execution-control.v1` control artifact；它必须绑定 global goal、当前批次、命题/ canonical unit、provider surface、时间/请求/token 上限、checkpoint 和停止原因。首批只能验证一个命题，且必须在 `COMPLETED-RECEIPT`、`BLOCKED-CAPABILITY`、`BLOCKED-EVIDENCE`、`TIMEOUT` 或 `CANCELLED` 中终止。达到任一硬上限、连续两次无新证据、重复失败、缺少真实 receipt 组成部分或遇到凭证/人工/目标系统阻断时立即停止。停止状态不能升级为 PASS；只有 103/103 页面覆盖、逐命题证据闭合、独立裁决/饱和、当前发布闭包和线上回读全部通过，global goal 才能完成。详见 `references/research-execution-control-protocol.md`，并用 `scripts/validate_research_execution_control.py` 在批次开始与结束复核。

Do not generate several delivered pages by mapping a short topic record through one shared prose template. Shared metadata and viewer components are allowed; shared learner-facing paragraphs, workflow filler, or generic headings are a publication failure. A page remains `outlined` until its own research package and manuscript validation pass. `planned`, `outlined`, and `blocked` are internal production states. They may exist in the topic system, coverage matrix, and roadmap, but never in a learner-facing navigation, HTML payload, public JSON, sitemap, or release archive.

Before promotion, follow `references/catalog-promotion-and-publication-integrity-contract.md`. Require the exact route-aware research inventory and `projection-ledger.json`: canonical packet/reuse decisions for external claims, local evidence for deterministic claims, target evidence for target claims, and explicit teaching/status evidence or blocker records. Require a page-specific promotion receipt, editorial score at least 90, boundary preservation 100, and a current executability verdict of `PASS` with zero findings. An author-written status, minimum character count, successful static build, shared source list, or canonical-unit count cannot replace these receipts.

Before a page can leave `outlined`, it must also pass `references/page-depth-and-projection-fidelity-contract.md`. A thick research package is not a delivered page. Produce `research/topics/<topic-id>/projection-ledger.json` proving which decision rules, judgement tables, counterexamples, failure modes, metric definitions and boundaries from the manuscript reached the page. `unaccounted` must be `0`; those six claim kinds may never be `deferred` or `rejected`. Measure learner prose in CJK characters of `summary`, `why`, block bodies, bullets, expected and warning — never in serialized JSON length, which counts syntax. Enforce originality by measured sentence duplication within a module (fail above 20%, outside components declared in `research/shared-components.json`), not by a fixed phrase blocklist that any new template evades. The score that authorizes promotion must carry an independent reviewer id and must not come from the chain that wrote the page. Raise a depth gate in stages — set it to the current measured P25 first, then to the lowest value among completed modules — because raising it to target in one step turns a validated release red and blocks publication. Delete retired page templates from the codebase; a dead template is a defect, because the next author will pick it up.

Before a page can leave `outlined`, its research package must include an editorial review that follows `references/technical-editorial-humanizer-gate.md`. The review freezes facts, commands, fields, numbers, citations, uncertainty, and scope before changing expression. It rejects marketing claims, chatbot guidance, repeated generic headings, vague attribution, ornamental lists, and conclusions that do not change a learner action or professional decision.

### 9. Build one exemplar before scaling

The first course must produce a real artifact and a result the learner can verify locally. Prefer a small public or synthetic fixture with an honest evidence label over an untestable enterprise story.

Required proof loop:

1. capture a baseline;
2. run the AI-related workflow or evaluation harness;
3. inspect output and metrics;
4. inject a meaningful defect or regression;
5. show the check turns red;
6. repair it and show the check turns green;
7. preserve commands, versions, outputs, and remaining unknowns.

If live model credentials or a target system are unavailable, provide a deterministic offline fixture plus an optional live adapter. Label offline fixture proof precisely; never call it live-model validation.

### 9A. Design the complete solution before declaring a track complete

Follow `references/complete-solution-contract.md`. A set of pages is not a solution merely because the topics look comprehensive. Create `solution-architecture.md`, `research/solution-architecture.json`, and `human-review/04-完整方案审计.md`.

Group related pages into solution units and close the chain from business outcome through requirements, decisions, architecture, interfaces, data, AI lifecycle, implementation, testing, operations, rollout, evidence, learner artifacts, and change management. Every solution unit must assess all 25 mandatory dimensions and provide the six required architecture views. Every public page must trace to a scenario, repository-owned artifact, exact command, execution receipt, assessment, and human gate.

Keep design, execution, practitioner review, and publication maturity as separate statuses. A static page check cannot promote execution status. A green fixture cannot promote a design with missing security, deployment, observability, rollback, cost, ownership, or governance. A complete design without integration proof remains a complete design with limited evidence; it is not production-ready.

Stop and report a gap instead of writing more pages when any mandatory dimension, architecture view, decision, trace row, owner, acceptance gate, or residual risk is absent. Do not publish a pilot solution without complete design, fixture proof, and practitioner review. Do not publish a general solution without integration proof, practitioner approval, security review, and rollback evidence.

A GitHub candidate is not run evidence. When it is selected for a lab, save a structured JSON record under `research/github-runs/` with the exact repository URL, pinned commit, checked-out HEAD, setup and smoke commands, timestamp, environment, stdout/stderr, exit code, and limitations. The validator rejects borrowed report files and metadata-only candidates.

### 9B. Close professional capability and evidence lanes

Follow `references/professional-capability-and-evidence-contract.md` before promoting any page. Create exact capability profiles and evidence records for every promised page. Use only the declared capability vocabulary and require independent review evidence for the mapping.

Treat five evidence lanes separately: real model, controlled integration, clean-room learner artifact, named practitioner, and target learner. Preserve `NOT_RUN`, `PASS`, `FAIL`, or `BLOCKED` plus receipt refs and limitations for each lane. A fixture-tested page requires clean-room proof. Model-integrated and integration-tested claims require real provider and target-system receipts, not deterministic adapters. Practitioner and learner evidence require attributable humans; an agent name or editorial score does not count.

Run model behavior as a versioned matrix with repeated raw outputs, parameters, latency/cost, refusal, truncation, prompt injection, locale, long-context, and disagreement cases. Never let the model under test approve its own semantic result. Run integrations against a controlled real boundary with auth, roles, side effects, cleanup, rollback, retry, and idempotency evidence.

Execute every claimed learner command from a fresh unpacked release. Pin the exact command across manuscript, page, manifest, static export, and archive. An author-workspace path or implicit working directory is a release failure.

Track human-facing verdicts in `research/status-registry.json`. Exactly one verdict per artifact type and scope is current; newer verdicts explicitly supersede older ones and pin the current public-scope and artifact hashes.

### 9C. Give large professional methods their own dimension document set

A learner page is a teaching surface, not a reference manual. When a topic family carries a
large professional method — a multi-domain testing architecture, a benchmark pipeline with
several independently variable components, a career ladder with evidence rungs — the pages
alone cannot hold it, and compressing it into pages produces exactly the thin, repetitive
output this Skill forbids.

Build `methodology/dimensions/<dimension-id>/` with one document per sub-domain, each
carrying its own judgement tables, counterexamples, failure-to-method mapping and diagnosis
rows. Project the set onto the pages and record that hop in the projection ledger.

Separate **source observation** (has a citation; proves the problem exists and its
magnitude) from **structural placeholder** (no citation; shows the shape of a judgement and
must be recalibrated against the team's own measured distribution). Mixing them is how a
public benchmark number silently becomes someone's production threshold.

### 10. Package for direct reuse

Create the package in `references/course-material-contract.md`, follow `references/teaching-experience-protocol.md`, and apply `references/beginner-comprehension-and-direct-reuse-contract.md`. Every lesson includes outcome, source-backed concept, a plain definition before first use, mental model, worked example, counterexample, guided demonstration, learner action, observable result, failure diagnosis, transfer task, deliverable, assessment, and sources. Every claimed reusable artifact declares inputs, editable fields, invariants, outputs, adaptation steps, validation evidence, limitations, and owner. The exemplar includes runnable files, sample data, expected metrics, failure injection, verification checklist, reusable Skill, material provenance, and a lesson script that demonstrates evidence rather than narrating promises.

JSON and CSV are backend evidence, never the primary review interface. Every complete career package must also create a `human-review/` layer in the user's language:

- `README.md`: what to read first, current verdict, and explicit review questions;
- `01-调研思路与主要结论.md`: search chain, source classes, evidence, inference, and unknowns;
- `02-成果清单与课程地图.md`: work domains, scenarios, course map, and delivery status;
- `03-细化样课.md`: one fully readable lesson with business context, teacher flow, learner actions, commands, artifacts, assessment, and evidence boundary.

Lead the user to this layer. Link machine-readable files only as optional provenance or implementation detail.

Run editorial cleanup only after technical synthesis is complete. Do not use “去 AI 味” as permission to delete limits, commands, evidence, field definitions, failure paths, or uncertainty. Expression may become shorter; information and boundaries may not become weaker.

### 10A. Build the tutorial product

Follow `references/tutorial-site-contract.md`. The final learner-facing product is a tutorial knowledge system, not a long course document.

Create:

- `tutorial/README.md`;
- `tutorial/course-tree.md`;
- `tutorial/page-template.md`;
- `tutorial/tutorial-site.json`;
- `tutorial/index.html`.

Derive the navigation from knowledge prerequisites:

`profession outcome -> business scenario -> learner action -> required knowledge -> prerequisite page -> tutorial page -> artifact -> verification`.

Use concept, guided-lab, diagnostic, reference, and project pages. Every delivered page shows the learner's location, outcome, prerequisite, professional relevance, plain explanation, smallest example, learner action, expected result, common error, completion check, previous/next page, evidence status, and updated date.

Follow `references/visual-knowledge-and-sequence-contract.md`. Choose each visual from the knowledge relationship and create repository-owned SVG or Mermaid sources. Concept maps, lifecycles, sequences, architecture/data flows, diagnosis trees, metric trees, career ladders, and gate/ring diagrams are not interchangeable. Require topic-specific nodes, relationships, source refs, decision purpose, failure path, alt text, caption, rendered mobile checks, and source-to-render closure.

The HTML is the primary learning interface. It must open directly without a server, expose a grouped left course tree, search, in-page navigation, previous/next progression, copyable commands, local completion progress, mobile navigation, and honest evidence-status labels.

Keep two explicit surfaces. The internal curriculum catalog is the complete research and production backlog. The public tutorial is a projection containing only pages whose independent research package, manuscript, editorial review, density gate, learner action, verification path, and publication checks passed. Remove empty modules after projection. The public `promised_page_ids` set must equal the full public page-ID set; a visible but unpromised page is a publication failure.

A complete knowledge tree is not a distributable course. Before public or paid release, deliver at least one 8-page beginner-to-artifact path with no planned prerequisite. Each delivered page must pass the content-density and learner-action gates in the tutorial contract; the path must end in a profession-relevant artifact with preserved verification evidence. The default entry is the first beginner page, not the most impressive lab.

Do not equate a non-empty manuscript with a completed lesson. Every public page must carry a profession-specific architecture or workflow diagram, repository-owned learner materials, exact commands or actions, an observable expected result, a failure path, recovery, evidence boundary, and a completion check. Any script, config, dataset, prompt file, API example, pipeline file, dashboard definition, or runbook named by the lesson must exist in the published repository and be linked from the page. A `fixture-tested` page needs at least one real script plus a second tested fixture/config/evidence file, and its claimed command must be rerun by validation. Missing material, dead link, empty file, decorative diagram, pseudo-command, or unexecuted “实测” claim keeps the page internal.

Classify technical blocks as `command`, `source-file`, `config`, `prompt`, `formula`, `diagram`, or `pseudocode`. The learner interface must display the kind and working directory. Only verified reusable kinds may show copy-for-use controls. A prompt is a learner artifact only when the repository contains the prompt, fixed input fixture, output schema, evaluation cases, model/config manifest, and a failure result. A formula or pseudocode rendered as runnable code is a release failure.

Treat page and module IDs as exact identifiers. Routing, delivery-support attachment, status promotion, prerequisite resolution, and material assignment must use exact sets or anchored patterns; a broad prefix test such as `startsWith("TD-P")` is forbidden when IDs such as `TD-P01` and `TD-PS01` can coexist. Add a collision regression proving that a newly introduced ID cannot inherit another track's architecture, materials, status, or evidence.

Maintain one ordered `research/catalog-manifest.json` as the catalog identity authority. A pilot is a declared subset; a complete catalog is an exact ordered match. If a new release removes any previously validated public page, require an approved scope-change record rather than silently shrinking the course. Bind every architecture/material bundle to exact owner IDs and explain intentional sharing.

For a professional specialization, require the complete engineering chain rather than a tool overview: problem and failure cost -> reference architecture -> data/contracts -> implementation/configuration -> execution SOP -> telemetry and diagnosis -> gate/decision -> rollback or human escalation. Split Web, Android, iOS, API, data, performance, stability, chaos, security, CI/CD, and AI-system testing when their tools, failure modes, or evidence differ. A shared generic paragraph generator is forbidden; shared viewers, schemas, and validated fixtures are allowed.

Declare the release scope before building a public artifact. Use `validated-subset` when only a validated subset of the internal catalog is public, or `complete-catalog` when every internal catalog page is validated and public. Preserve `promised_page_ids`, `catalog_complete`, and the validation timestamp in the canonical content model and release manifest. In both modes, any planned, outlined, blocked, navigation-only, empty-module, or density-gate-failing record is forbidden from public artifacts. Under `complete-catalog`, the internal and public page sets must also match. Content completeness never upgrades its evidence status: a fully written `desk-researched` page remains desk-researched until stronger proof exists.

Treat GitHub and OpenAI Sites as two publication targets generated from one validated content source. GitHub carries versioned source, sanitized labs, reusable materials, issues, and releases. Sites carries the learner-facing experience and should remain private during review. Never maintain independent HTML, JSON, and course prose as competing truth. Do not make a public deployment until the public-safe subset and access level are explicitly confirmed.

Before release assembly, require `research/publication-closure.json` to prove that every learner-material link has the same pinned bytes in the authoring source, static export, and ZIP member. The assembled release must carry hash-pinned public projections of the catalog, page promotions, executability audit, and artifact closure.

Also project and hash-pin `SOURCE-ASSIMILATION-MANIFEST.json`, `LEARNER-USABILITY-REUSE.json`, `VISUAL-SEQUENCE-MANIFEST.json`, `CAPABILITY-PROFILES.json`, `PROFESSIONAL-EVIDENCE.json`, and `STATUS-REGISTRY.json`. Their source inventory, ordered page IDs, continuous display numbers, visual hashes, reusable-artifact contracts, and maturity boundaries must match the public tutorial exactly.

The transfer stage must name the source context, a genuinely different target context, what remains invariant, at least two things the learner must adapt, and a success criterion. A `transfer-challenge` label without this contract does not count.

### 11. Validate and adversarially review

Run:

```bash
python3 scripts/validate_career_package.py <career-package>
python3 scripts/validate_career_package.py <career-package> --verify-sources
python3 scripts/validate_career_package.py <career-package> --run-labs
python3 scripts/validate_public_release.py <public-release-directory>
```

`--verify-sources` is the live existence gate for publication-time source claims. Static validation deliberately cannot prove that a URL exists; a current course package must not be described as live-source-verified unless this command (or an equivalent trusted re-open audit) passed in the current run. Anti-bot or credential-blocked pages remain `blocked`, not silently accepted.

Then run a fresh-agent forward test when available:

- without the Skill, capture the weak baseline;
- with the Skill, ask for a course under ambiguity and time pressure;
- check that the agent rejects generic prompt-only topics;
- check that same-publisher or copied sources do not pass independence gates;
- check that a dominant publisher or source family cannot pass by adding filler sources;
- check that a channel cannot borrow evidence selected by a different or blocked query;
- check that a GitHub link without pinned run evidence cannot support a runnable-lab claim;
- check that an attractive script without learner action, failure diagnosis, transfer, and material provenance fails;
- check that a complete package without a navigable tutorial viewer fails;
- check that public navigation, HTML, JSON, sitemaps, and archives reject every planned, outlined, or blocked page and every empty module;
- check that public page IDs equal `promised_page_ids`, while unfinished catalog entries remain only in internal research artifacts;
- check the assembled release directory, not only its source package: reject internal authoring trees, incomplete course records in any public JSON, extra HTML navigation IDs, placeholder copy, learner-artifact hash drift, a manifest without page IDs, verdict and publication targets, or a release without a hash-pinned `SOLUTION-MANIFEST.json` covering every public page;
- probe every public text surface, including secondary HTML, XML, JavaScript search indexes, Markdown catalogs, YAML and CSV metadata, for serialized `planned`, `outlined`, or `blocked` learner records; do not validate only the main HTML and JSON;
- delete or rename every linked learner material in turn and prove validation fails; check that fixture-tested pages link a real tested script and preserved red/green evidence;
- reject a public lesson without a substantive architecture/workflow diagram, executable SOP, expected output, injected failure, diagnosis path and repository-owned handoff material;
- check that page order follows prerequisites rather than source publication order;
- check that the professional baseline, AI foundation, and benchmark layers cannot be omitted or moved after dependent courses;
- check that the six research systems, coverage matrix, and all six independent expert reviews cannot be omitted;
- check that lifecycle, specialization, system, outcome, and career dimensions cannot be omitted or replaced by tool categories;
- check that AI-change records cannot omit the non-AI baseline, human accountability, new failures, controls, learner proof, and evidence;
- check that a traditional specialization family cannot disappear merely because the user did not name it;
- check that metrics without workload, distribution, threshold, and decision owner cannot pass as a professional quality gate;
- check that multiple delivered pages cannot be produced from one short record and a shared generic prose template;
- check that every promised page has its own research brief, source pack, evidence synthesis, engineering blueprint, manuscript, validation record, route-aware evidence mapping, and projection ledger; canonical packets may be referenced but may not be copied as page receipts;
- check that reference pages define metric semantics, aggregation, interpretation, threshold method, and failure action instead of listing names;
- check that guided labs preserve commands, expected outputs, a meaningful red result, repair/reset, and a green rerun;
- check that learner-facing pages do not use generic pedagogical filler as a substitute for domain explanation;
- check that a high or critical gap without an explicit decision blocks curriculum generation;
- check that competitor analysis covers modules, learner artifacts, execution proof, and assessment rather than only titles and promises;
- check that an AI-quality profile exposes separate LLM, RAG, Agent, Workflow, and Benchmark tracks;
- check that benchmark lessons trace data, protocol, scorer, aggregation, uncertainty, contamination, and versioning instead of repeating leaderboard numbers;
- independently re-open at least one profession-workflow, AI-capability, and practice-artifact source for each high-priority scenario, and compare exact URLs with the ledger and search log;
- verify the generated package, lab commands, and red/green evidence;
- check that every public page has an exact non-empty professional capability profile covered by a declaration;
- check that `provider=none`, an offline adapter, missing repeated raw outputs, or model self-judgment cannot pass the real-model lane;
- check that integration PASS cannot omit target version, auth, roles, cleanup, rollback, retry, or idempotency evidence;
- check that fixture maturity fails when the final archive has not been executed from a clean unpacked directory or any learner command surface differs;
- check that practitioner evidence is attributable and role-relevant, and learner evidence has at least five target learners plus completion, time, error-recovery, and transfer measurements;
- check that stale or contradictory human verdicts fail unless the current record explicitly supersedes and hash-pins them;
- check that the public release includes and hash-pins source-assimilation, source-semantic projection, learner-usability/reuse, visual-sequence, capability, professional-evidence, and status-registry projections;
- record rationalizations and patch the general rule, never one title.

Structural validation is necessary but not professional validation. Report both.
Static provenance checks cannot prove that a network call really happened; only trusted runtime evidence or an independent live re-open can establish that. Never convert a static validator PASS into a live-research claim.

### 12. Update without losing provenance

Keep career tasks independent from tool brands. Courses reference versioned adapters. On tool/model changes, update the registry, rerun the smallest acceptance test, and append the migration impact. Do not silently rewrite old evidence.

## Stop conditions

Stop and report the gap when any applies:

- AI centrality is below 4/5;
- sources do not establish a profession-specific problem or AI capability;
- any user-provided source, section, or substantive atom is absent from `research/source-assimilation-ledger.json`, remains `UNMAPPED`, lacks a disposition target/rationale, or its frozen hash drifts;
- any incorporated/adapted source atom lacks a closed semantic-function projection, or a source visual/template/prompt/workflow is reduced to prose, an archive-only link, or an unscoped policy;
- organization-specific levels, fixed years, promotion schedules, universal thresholds, or vendor claims are copied without a scoped adapter, owner, evidence, uncertainty, and failure action;
- any mandatory research channel is missing or its claim boundary is absent;
- a scenario's evidence collapses to fewer than three publisher groups or source families;
- the profession map lacks work domains, artifacts, decision rights, or failure costs;
- the package lacks a profession-to-AI competency transition map or any of the eight learning layers;
- the package lacks a curriculum coverage matrix, human-readable gap audit, or any of the six evidence systems and six expert reviews;
- a high or critical curriculum gap has no explicit decision;
- the topic system is absent, was derived from an arbitrary lesson count, or leaves a critical coverage cell without an owner;
- a promised page lacks its own topic research package or passed manuscript validation;
- a publishable proposition lacks a claim-inventory record, valid evidence route, contradiction/adjudication record, complete applicable-dimension coverage, or terminal disposition; an external canonical anchor additionally lacks its provider receipt/counterevidence/saturation, a reused member lacks transfer/adjudication, a local claim lacks local artifact evidence, or a target claim lacks target evidence;
- a claimed Deep Research run lacks the exact OpenAI/ChatGPT surface, model or feature, response/export ID, raw response, tool-call trajectory, citations, source counts, hashes, or limitations;
- a promised page lacks an exact promotion receipt, current zero-finding executability PASS, or pinned learner-material hashes;
- delivered pages are generated from shared generic prose instead of topic-specific synthesis;
- AI foundation knowledge appears only after courses that depend on it;
- learner-facing display numbers are skipped, duplicated, module-local, or not exactly `1..N`, or a prerequisite follows its consumer;
- a technical term is used before a plain definition on the same page or an earlier prerequisite page;
- an AI-quality profile collapses LLM, RAG, Agent, Workflow, and Benchmark into one undifferentiated topic;
- current claims have no preserved search route, query, access date, and opened source;
- a business scenario lacks actor, trigger, system, business object, failure cost, or decision handoff;
- a selected scenario lacks role, AI-capability, and practitioner/artifact evidence classes;
- the course has no runnable or directly inspectable learner artifact;
- a selected GitHub lab dependency is not pinned and run-verified, with no verified fallback;
- the lesson has no learner action, failure diagnosis, transfer task, or material provenance;
- a claimed reusable artifact lacks inspectable inputs, editable fields, outputs, adaptation steps, validation evidence, limitations, or owner;
- the package has no tutorial knowledge tree or self-contained tutorial viewer;
- the package is described as distributable but its public page set does not collectively cover concept, evidence/Oracle design, guided execution, diagnosis, repair, and transfer for at least one profession-relevant artifact;
- the release scope is absent, its promised page IDs do not exactly equal the learner-facing page set, or any public artifact contains a planned, outlined, blocked, navigation-only, empty-module, or density-gate-failing record;
- a complete-catalog page set differs from the ordered canonical manifest, a pilot exposes an unknown ID, or a release silently removes a previously validated page without an approved scope-change record;
- completeness language exceeds the validated release scope or evidence status;
- publication targets are built from independently edited course copies or expose private research and production data;
- source material, tutorial link, static export, or ZIP member is missing, undeclared, or hash-divergent;
- the final public release directory has not passed `validate_public_release.py` after assembly;
- a lesson names a script, config, dataset, prompt, pipeline, dashboard or runbook that is absent, empty, unlinked, outside the public repository, or not covered by the claimed validation status;
- a page is labelled complete because prose exists, but lacks an architecture/workflow diagram, runnable handoff, expected result, failure/recovery path, and professional decision boundary;
- a page uses a decorative or shared generic diagram, lacks a repository-owned SVG/Mermaid source, required visual kind, topic-specific nodes/edges, alt/caption, source refs, or rendered mobile evidence;
- the test cannot be shown to fail on a meaningful regression;
- a current tool claim lacks a primary source and version/date;
- the workflow depends on hidden credentials without an offline path;
- professional risk lacks a human gate;
- the package is a prompt, script, slide deck, or plausible answer without execution evidence.
- an opted-in `artifact-transformation` capability lacks a method rationale, independent oracle, eval/mutation package, or non-orphan source-to-result trace;
- an opted-in capability declares `pass` while any required artifact or trace node is blocked, unknown, incomplete, refused, or schema-invalid.
- any promised page lacks an exact capability profile, declaration coverage, five-lane professional evidence record, or current status-registry coverage;
- a model or integration maturity claim lacks real provider/target receipts, independent Oracle evidence, cleanup, or rollback;
- a fixture claim has not passed clean-room execution from the final learner artifact, or its commands differ across declared surfaces;
- practitioner or learner maturity is inferred from an agent review, editorial score, anonymous feedback, or fewer than five target learners;
- multiple human-facing verdicts remain current, an older verdict is not explicitly superseded, or any verdict/scope hash drifts;
- a release omits or fails to hash-pin `SOURCE-ASSIMILATION-MANIFEST.json`, `SOURCE-SEMANTIC-PROJECTION.json`, `LEARNER-USABILITY-REUSE.json`, `VISUAL-SEQUENCE-MANIFEST.json`, `CAPABILITY-PROFILES.json`, `PROFESSIONAL-EVIDENCE.json`, or `STATUS-REGISTRY.json`.
- a testing-career or Agent-architecture capability lacks the four evidence-based responsibility states, evidence-bound self-assessment, configurable organization adapter, D0-D7 test mappings, four evidence rings, independent Oracles, or scoped metric-card/statistical semantics.

## Output language

Use the user's language. Keep commands, APIs, metric names, and conventional technical terms copyable. Explain each new term once in plain language.
