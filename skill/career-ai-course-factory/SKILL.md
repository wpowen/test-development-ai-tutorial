---
name: career-ai-course-factory
description: Research and build AI-native, profession-specific course systems with proactive curriculum-gap discovery, multi-platform competitor evidence, runnable labs, reusable Skills, failure-injection proof, and versioned tool adapters. Use when discovering how AI changes a profession, creating a professional learning pathway, building a practical course for one occupation, refreshing AI tools, or packaging validated lessons into videos and learner materials.
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
- Per-topic deep research, engineering blueprint, and manuscript: `references/topic-research-and-manuscript-protocol.md`

## Four mandatory AI lanes

Research all four before choosing a topic. A series should cover all four unless evidence shows one is irrelevant.

1. `use-ai-for-work`: use models or agents to improve traditional professional work.
2. `test-ai-systems`: evaluate LLM, RAG, multimodal, or agent products.
3. `agentize-work`: turn a bounded workflow into a supervised agent loop.
4. `build-ai-quality-system`: datasets, evaluation, observability, CI gates, governance, and feedback loops.

## Workflow

### 1. Define the professional outcome

Record learner level, work setting, current toolchain, recurring outputs, costly failures, privacy constraints, and one observable job result. Do not choose a tool yet.

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

### 4. Decompose the profession before selecting scenarios

Follow `references/profession-decomposition-protocol.md` and build `research/profession-map.json`. Map role variants, at least five work domains, business events, work objects, artifacts, systems, decision rights, failure costs, and the end-to-end lifecycle.

Do not divide the curriculum by tools. Trace every candidate through:

`role variant -> work domain -> business event -> artifact -> failure -> AI intervention -> learner proof -> reusable material`.

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

Use `references/career-task-schema.md`. AI centrality, professional leverage, runnable proof, repeat reuse, and source strength are hard-weighted. Risk and verification difficulty remain separate gates. Build as many courses as the transition matrix needs; 10-20 is a compact series, while a professional pathway may require 20-60 smaller topics grouped into stages and specialization tracks.

Sequence by knowledge and artifact dependencies, not popularity:

`professional baseline -> AI foundations -> bounded assisted-work lab -> AI system evaluation -> agent/workflow evaluation -> production quality loop -> benchmark literacy -> capstone`.

Every curriculum entry records `stage_id`, `level`, `prerequisite_course_ids`, `knowledge_dependencies`, `professional_baseline`, `new_ai_capability`, `assessment`, `source_ids`, and `delivery_status`. A stage is complete only when its exit artifact passes; watching the pages is not completion.

### 8A. Research and synthesize every promised topic independently

For each page promised by the release scope, create `research/topics/<topic-id>/research-brief.md`, `source-pack.csv`, `evidence-synthesis.md`, `engineering-blueprint.md`, `manuscript.md`, and `validation.md` by following `references/topic-research-and-manuscript-protocol.md`.

Use search and lower-cost agents to divide evidence lanes, not to mass-produce final pages. The integrating pass must reopen pivotal sources, resolve conflicting definitions, create the engineering design, and reject unsupported thresholds or generic prose.

Do not generate several delivered pages by mapping a short topic record through one shared prose template. Shared metadata and viewer components are allowed; shared learner-facing paragraphs, workflow filler, or generic headings are a publication failure. A page remains `outlined` until its own research package and manuscript validation pass.

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

A GitHub candidate is not run evidence. When it is selected for a lab, save a structured JSON record under `research/github-runs/` with the exact repository URL, pinned commit, checked-out HEAD, setup and smoke commands, timestamp, environment, stdout/stderr, exit code, and limitations. The validator rejects borrowed report files and metadata-only candidates.

### 10. Package for direct reuse

Create the package in `references/course-material-contract.md` and follow `references/teaching-experience-protocol.md`. Every lesson includes outcome, source-backed concept, guided demonstration, learner action, failure diagnosis, transfer task, deliverable, assessment, and sources. The exemplar includes runnable files, sample data, expected metrics, failure injection, verification checklist, reusable Skill, material provenance, and a lesson script that demonstrates evidence rather than narrating promises.

JSON and CSV are backend evidence, never the primary review interface. Every complete career package must also create a `human-review/` layer in the user's language:

- `README.md`: what to read first, current verdict, and explicit review questions;
- `01-调研思路与主要结论.md`: search chain, source classes, evidence, inference, and unknowns;
- `02-成果清单与课程地图.md`: work domains, scenarios, course map, and delivery status;
- `03-细化样课.md`: one fully readable lesson with business context, teacher flow, learner actions, commands, artifacts, assessment, and evidence boundary.

Lead the user to this layer. Link machine-readable files only as optional provenance or implementation detail.

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

The HTML is the primary learning interface. It must open directly without a server, expose a grouped left course tree, search, in-page navigation, previous/next progression, copyable commands, local completion progress, mobile navigation, and honest delivery-status labels. Planned pages stay visible but cannot look delivered.

A complete knowledge tree is not a distributable course. Before public or paid release, deliver at least one 8-page beginner-to-artifact path with no planned prerequisite. Each delivered page must pass the content-density and learner-action gates in the tutorial contract; the path must end in a profession-relevant artifact with preserved verification evidence. The default entry is the first beginner page, not the most impressive lab.

Declare the release scope before building a public artifact. Use `pilot-path` when only a named subset is promised, or `complete-catalog` when every catalog page is promised. Preserve `promised_page_ids`, `catalog_complete`, and the validation timestamp in the canonical content model and release manifest. Under `complete-catalog`, any planned, outlined, blocked, navigation-only, or density-gate-failing page blocks build and publication. Content completeness never upgrades its evidence status: a fully written `desk-researched` page remains desk-researched until stronger proof exists.

Treat GitHub and OpenAI Sites as two publication targets generated from one validated content source. GitHub carries versioned source, sanitized labs, reusable materials, issues, and releases. Sites carries the learner-facing experience and should remain private during review. Never maintain independent HTML, JSON, and course prose as competing truth. Do not make a public deployment until the public-safe subset and access level are explicitly confirmed.

The transfer stage must name the source context, a genuinely different target context, what remains invariant, at least two things the learner must adapt, and a success criterion. A `transfer-challenge` label without this contract does not count.

### 11. Validate and adversarially review

Run:

```bash
python3 scripts/validate_career_package.py <career-package>
python3 scripts/validate_career_package.py <career-package> --verify-sources
python3 scripts/validate_career_package.py <career-package> --run-labs
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
- check that planned navigation items cannot masquerade as delivered pages;
- check that page order follows prerequisites rather than source publication order;
- check that the professional baseline, AI foundation, and benchmark layers cannot be omitted or moved after dependent courses;
- check that the six research systems, coverage matrix, and all six independent expert reviews cannot be omitted;
- check that lifecycle, specialization, system, outcome, and career dimensions cannot be omitted or replaced by tool categories;
- check that AI-change records cannot omit the non-AI baseline, human accountability, new failures, controls, learner proof, and evidence;
- check that a traditional specialization family cannot disappear merely because the user did not name it;
- check that metrics without workload, distribution, threshold, and decision owner cannot pass as a professional quality gate;
- check that multiple delivered pages cannot be produced from one short record and a shared generic prose template;
- check that every promised page has its own research brief, source pack, evidence synthesis, engineering blueprint, manuscript, and validation record;
- check that reference pages define metric semantics, aggregation, interpretation, threshold method, and failure action instead of listing names;
- check that guided labs preserve commands, expected outputs, a meaningful red result, repair/reset, and a green rerun;
- check that learner-facing pages do not use generic pedagogical filler as a substitute for domain explanation;
- check that a high or critical gap without an explicit decision blocks curriculum generation;
- check that competitor analysis covers modules, learner artifacts, execution proof, and assessment rather than only titles and promises;
- check that an AI-quality profile exposes separate LLM, RAG, Agent, Workflow, and Benchmark tracks;
- check that benchmark lessons trace data, protocol, scorer, aggregation, uncertainty, contamination, and versioning instead of repeating leaderboard numbers;
- independently re-open at least one profession-workflow, AI-capability, and practice-artifact source for each high-priority scenario, and compare exact URLs with the ledger and search log;
- verify the generated package, lab commands, and red/green evidence;
- record rationalizations and patch the general rule, never one title.

Structural validation is necessary but not professional validation. Report both.
Static provenance checks cannot prove that a network call really happened; only trusted runtime evidence or an independent live re-open can establish that. Never convert a static validator PASS into a live-research claim.

### 12. Update without losing provenance

Keep career tasks independent from tool brands. Courses reference versioned adapters. On tool/model changes, update the registry, rerun the smallest acceptance test, and append the migration impact. Do not silently rewrite old evidence.

## Stop conditions

Stop and report the gap when any applies:

- AI centrality is below 4/5;
- sources do not establish a profession-specific problem or AI capability;
- any mandatory research channel is missing or its claim boundary is absent;
- a scenario's evidence collapses to fewer than three publisher groups or source families;
- the profession map lacks work domains, artifacts, decision rights, or failure costs;
- the package lacks a profession-to-AI competency transition map or any of the eight learning layers;
- the package lacks a curriculum coverage matrix, human-readable gap audit, or any of the six evidence systems and six expert reviews;
- a high or critical curriculum gap has no explicit decision;
- the topic system is absent, was derived from an arbitrary lesson count, or leaves a critical coverage cell without an owner;
- a promised page lacks its own topic research package or passed manuscript validation;
- delivered pages are generated from shared generic prose instead of topic-specific synthesis;
- AI foundation knowledge appears only after courses that depend on it;
- an AI-quality profile collapses LLM, RAG, Agent, Workflow, and Benchmark into one undifferentiated topic;
- current claims have no preserved search route, query, access date, and opened source;
- a business scenario lacks actor, trigger, system, business object, failure cost, or decision handoff;
- a selected scenario lacks role, AI-capability, and practitioner/artifact evidence classes;
- the course has no runnable or directly inspectable learner artifact;
- a selected GitHub lab dependency is not pinned and run-verified, with no verified fallback;
- the lesson has no learner action, failure diagnosis, transfer task, or material provenance;
- the package has no tutorial knowledge tree or self-contained tutorial viewer;
- the package is described as distributable but has no complete 8-page beginner-to-artifact path;
- the release scope is absent, its promised page IDs do not match the learner-facing artifacts, or a complete-catalog release contains an incomplete page;
- completeness language exceeds the validated release scope or evidence status;
- publication targets are built from independently edited course copies or expose private research and production data;
- the test cannot be shown to fail on a meaningful regression;
- a current tool claim lacks a primary source and version/date;
- the workflow depends on hidden credentials without an offline path;
- professional risk lacks a human gate;
- the package is a prompt, script, slide deck, or plausible answer without execution evidence.

## Output language

Use the user's language. Keep commands, APIs, metric names, and conventional technical terms copyable. Explain each new term once in plain language.
