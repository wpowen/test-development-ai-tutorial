# Topic Research and Tutorial Manuscript Protocol

## Purpose

Prevent a correct-looking curriculum from turning into thin, repetitive pages. A topic title, learning objective, source list, or generated summary is not instructional content. Research and write every promised topic as an independent route-aware evidence synthesis before it enters the tutorial. Topic independence means each page has its own claims, evidence mapping, adjudication, projection, and validation; it does not require duplicating a canonical external provider report.

## Two-stage contract

### Stage A: build the topic system

Create `research/topic-system.md` before writing pages. Each topic records:

`topic_id,module,controlling_question,scope,in_scope,out_of_scope,prerequisite_concepts,professional_decision,learner_artifact,verification,page_type,evidence_needs,status`

Derive topics from the profession knowledge system and coverage matrix. Do not derive them from an arbitrary lesson count. Split a topic when it asks the learner to make two independent professional decisions. Merge topics only when they share one decision, one artifact, and one verification path.

Run these checks:

- every critical profession and AI coverage cell has an owning topic;
- prerequisites form a valid learning graph;
- no topic is only a tool tour or generic model explanation;
- the topic has a realistic system/work object and failure cost;
- the learner artifact will be reused or assessed later;
- the title describes a question or decision the page actually resolves.

The full topic system may be large. It remains `planned` or `outlined` until each page passes Stage B.

### Stage B: research and write one topic

Create an independent directory for every promised topic. The split files are mandatory for public work:

```text
research/topics/<topic-id>/
├── research-brief.md
├── source-pack.csv
├── research-runs.json
├── claim-inventory.json
├── canonical-packet-refs.json
├── reuse-decisions.json
├── local-evidence.json
├── target-evidence.json
├── teaching-evidence.json
├── deep-research-receipts.json OR codex-research-receipts.json (only when this topic owns an approved external anchor/delta run)
├── contradiction-matrix.md OR codex-contradiction-matrix.md
├── research-saturation.json OR codex-research-saturation.json
├── evidence-synthesis.md
├── engineering-blueprint.md
├── manuscript.md
├── comparison.md
├── lab-manifest.json
├── projection-ledger.json
└── validation.md
```

`research-package.md` may exist only as an index. It cannot replace the split records. A generated summary, a short source list, or a manuscript-shaped page does not count as research. `canonical-packet-refs.json` and `reuse-decisions.json` reference shared external packets without copying receipt/report/saturation; local, target, and teaching evidence remain separate records.

Before using the source pack or writing the synthesis, follow `claim-level-deep-research-protocol.md`. R0 must classify every atomic proposition and select its evidence route. Only eligible external technical facts and empirical generalizations require a canonical OpenAI/ChatGPT or explicitly selected Codex research contract. A member claim may use `DIRECT-REUSE` or `SOURCE-REUSE-DELTA` only with its own transfer/adjudication/projection record; local, target, and teaching claims require their own evidence or remain blocked/unknown. `research-runs.json` is only an orchestration index and proves neither a provider call nor a Codex runtime trace.

Do not batch-generate several manuscripts from one short record or one generic packet. Research may run in parallel by evidence lane, but synthesis and publication approval happen one topic at a time. A canonical packet may supply a source asset, never a page-specific final conclusion.

Record the applicable independent evidence routes in `research-runs.json` and `comparison.md`. An external canonical anchor normally needs initial and counterevidence/gap-fill runs according to risk; a member needs a transfer comparison even when no new provider run is required; a local/target/teaching claim needs the appropriate artifact, snapshot, or human/design evidence. The comparison must list `DIRECT-REUSE`, `SOURCE-REUSE-DELTA`, `NO-REUSE`, local, target, teaching, and blocked members, with supports/cannot-support boundaries. A draft, Luna integration, or page-writing agent cannot approve its own result.

The topic route is fail-closed and follows `R0 classify/map → R1 canonical external breadth → R2 technical-document reconstruction → R3 counterevidence → R4 gap-fill → R5 local verification → R6 target evidence → R7 independent adjudication/projection`. R0 covers every page and claim without networking; R1–R4 run only for eligible canonical external units; R5–R6 cannot be replaced by web research; R7 must preserve each member's transfer, disposition, and projection. A topic may be content-complete while remaining `BLOCKED`, `UNKNOWN-EXPLICIT`, `NOT-SATURATED`, or `TARGET-REQUIRED`.

## Research brief

`research-brief.md` must define:

- the controlling learner question;
- learner level and assumed knowledge;
- the professional decision or task this topic supports;
- the system, business object, inputs, constraints, failure cost, and decision owner;
- what the topic must explain, demonstrate, let the learner do, and let the learner diagnose;
- explicit exclusions to prevent an unfocused page;
- freshness requirements and required source families;
- the learner artifact and how it will be checked.

## Evidence lanes

Select the lanes needed by the topic. A professional engineering topic normally needs at least five distinct lanes:

1. durable professional baseline or standard;
2. current AI architecture, protocol, or primary technical documentation;
3. metrics and definitions, including formulas, units, distributions, thresholds, and decision owner;
4. implementation, tool, repository, or executable artifact;
5. failure, incident, issue, counterexample, or limitation;
6. existing course/tutorial supply when positioning or teaching design is in scope;
7. practitioner workflow or public case when professional realism is claimed.

Every selected source must be opened. Store the exact URL, access date, source family, supported claim, unsupported claim, version/date, and limitation in `source-pack.csv`. Search snippets and generated answers remain leads. A packet reference does not count as a page-specific conclusion; the page must map each claim to the packet's supports/cannot-support range or to its own local/target/teaching evidence.

When a public engineering topic owns or references an applicable external canonical packet, the combined applicable packet(s) must meet the evidence floor of at least ten opened sources across five evidence lanes, five independent source families, and four source types unless a risk-specific primary-authority exception is independently recorded. The same sources must not be recounted merely because several pages reference them. A topic with only local, target, or teaching claims must not fabricate an external source count; it must close those routes or remain blocked/unknown. Source count is a floor, not a substitute for relevance, independence, scope, or cannot-prove boundaries.

## Evidence synthesis

`evidence-synthesis.md` is not a list of source summaries. Organize it by questions the learner needs answered:

- What is the concept and where are its boundaries?
- How does the non-AI or conventional baseline work?
- What changes for the AI system or profession?
- Which terms or metrics have conflicting definitions?
- What is consensus, what is implementation-specific, and what remains unknown?
- Which decisions can the evidence support?
- Which attractive claims must be rejected or narrowed?

Separate `Fact`, `Cross-source synthesis`, `Practitioner signal`, `Vendor claim`, `Inference`, and `Unknown`.

## Engineering blueprint

For engineering, operations, evaluation, or professional workflow topics, `engineering-blueprint.md` must include the applicable items below:

- system boundary and component/data-flow diagram;
- metric catalog with definition, formula, unit, aggregation, dimensions, source point, interpretation, threshold method, and failure action;
- workload or input distribution, not only an average example;
- version and environment manifest;
- tool selection matrix with interfaces, setup, strengths, blind spots, and fallback;
- data/trace/report schema;
- baseline, fault injection, repair, and regression path;
- step-by-step SOP with entry conditions, stop conditions, cleanup, and owner;
- diagnosis tree mapping observable symptoms to possible layers and confirming evidence;
- production monitoring, SLO, alert, waiver, rollback, and incident feedback when applicable;
- security, privacy, cost, and human authority boundaries.

A metric name without workload, distribution, threshold method, or decision is glossary material, not a professional blueprint.

## Manuscript contract

Write `manuscript.md` as learner-facing tutorial content. Do not expose research process as filler. Remove generic sections such as “本页完成后你会带走什么” from the reading path; keep learning outcomes as metadata for validation.

Use this reading logic when appropriate:

1. a concrete failure, decision, or question;
2. why the conventional method is insufficient or what remains valid;
3. a plain mental model and precise definitions;
4. the complete system or workflow;
5. metrics, data, architecture, tools, and decision rules;
6. a worked example with realistic values and interpretation;
7. an executable or inspectable learner action;
8. a deliberately failing case and diagnosis;
9. repair, rerun, and transfer to a different context;
10. concise source notes and evidence boundary.

Headings must answer learner questions. Avoid headings that merely describe pedagogy, such as “先把问题说清楚”, “按步骤完成”, “迁移到你的项目”, or repeated boilerplate shared across unrelated pages.

## Page-type depth gates

### Concept

Require boundaries, mechanism, structure/data flow, smallest example, counterexample, and implications for a professional decision.

### Reference

Require definitions, formula or exact semantics where applicable, unit, aggregation, dimensions, source point, comparison table, valid interpretation, invalid interpretation, threshold method, version/date, and fallback.

### Guided lab

Require prepared input, exact commands/actions, expected output after meaningful steps, saved artifact, meaningful mutation, expected red result, repair/reset, expected green result, and troubleshooting.

Every runnable or inspectable page also carries `lab-manifest.json`. It pins the working directory, repository-owned files, step kind, exact command or action, expected exit code, expected artifacts, baseline/fault/repair linkage, and evidence boundary. Validation resolves every referenced path from the declared working directory. A command that only works in an unpublished authoring tree fails.

### Diagnostic

Require symptoms, ordered decision tree, competing hypotheses, confirming/disconfirming evidence, misleading fixes, safe repair, regression check, and escalation boundary.

### Project

Require business brief, constraints, architecture, data contract, deliverables, baseline/failure/repair evidence, scoring rubric, human review, transfer, and residual risk.

## Validation

`validation.md` must answer:

- Does the manuscript fully answer the controlling question?
- Can every important claim be traced to opened evidence or explicit inference?
- Does it contain the engineering blueprint required by its page type?
- Can the learner inspect or run the artifact without hidden context?
- Is there a meaningful failure and diagnosis path?
- Are thresholds derived from the scenario rather than invented as universal values?
- Are content completeness and evidence status labelled separately?
- Does the page contain repeated generic prose that could be pasted into another profession or topic?

Any “no” blocks publication. Set the page to `outlined` until repaired.

## Code and copy affordance contract

Do not store every technical block in one undifferentiated `code` field. Each block declares one kind:

- `command`: copy-paste runnable from the declared working directory;
- `source-file`: exact excerpt from a linked repository file;
- `config`: valid JSON, YAML, TOML, SQL, or other named format with its consumer;
- `prompt`: versioned prompt file with fixed input fixture, output schema, evaluation set, model/config manifest, and boundary;
- `formula`: definition with variables, units, dimensions, aggregation, and worked values;
- `diagram`: architecture or sequence view, not executable code;
- `pseudocode`: explicitly non-runnable explanation linked to a real implementation or removed.

The viewer must label the kind. Only `command`, `source-file`, `config`, and a fully packaged `prompt` may show a copy-for-use affordance. Diagrams, formulas, and pseudocode must never be presented as runnable implementation. A page fails when the displayed command differs from the command rerun by validation.

## Model and agent routing

Use Luna or other lower-cost agents for independent source discovery, source extraction, atomic-claim candidates, field normalization, cluster and reuse candidates, competitor scanning, technical-document Markdown organization, gap ranking, cost aggregation, and page integration. Mark these outputs as proposals or integration artifacts. Luna cannot create or complete a provider response ID, raw response, source-opening event, citation trajectory, completed receipt, saturation PASS, target PASS, practitioner PASS, or learner PASS. A Luna conversation is neither an OpenAI Deep Research receipt nor a Codex runtime trace.

Use the official OpenAI/ChatGPT surface for formal external canonical research, or the separate Codex contract only when explicitly selected. The integrating model must reopen pivotal sources, reconcile definitions, build the engineering blueprint, and run validation. It cannot approve its own classification, packet, reuse decision, saturation, page, or promotion; the independent auditor and target owner remain separate.

Reject agent output when it contains an unopened URL, invented source ID, unsupported threshold, generic page boilerplate, a copied anchor disposition, or a tool recommendation without interface and limitation evidence. Cost optimization never weakens the evidence, route, transfer, or publication gate.
