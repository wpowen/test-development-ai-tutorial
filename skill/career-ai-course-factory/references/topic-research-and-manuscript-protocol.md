# Topic Research and Tutorial Manuscript Protocol

## Purpose

Prevent a correct-looking curriculum from turning into thin, repetitive pages. A topic title, learning objective, source list, or generated summary is not instructional content. Research and write every promised topic as an independent evidence synthesis before it enters the tutorial.

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

Create `research/topics/<topic-id>/research-package.md` with six mandatory sections:

```text
## Research brief
## Source pack
## Evidence synthesis
## Engineering blueprint
## Manuscript map
## Validation
```

The sections may be split into the six same-named files when a topic becomes large. The single-file form is the minimum auditable unit and must preserve source URLs, claim support, limitations, blueprint fields, manuscript mapping, and validation results; it is not permission to collapse several topics into one generic package.

Do not batch-generate several manuscripts from one short record. Research may run in parallel by evidence lane, but synthesis and publication approval happen one topic at a time.

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

Every selected source must be opened. Store the exact URL, access date, source family, supported claim, unsupported claim, version/date, and limitation in `source-pack.csv`. Search snippets and generated answers remain leads.

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

## Model and agent routing

Use lower-cost agents for independent source discovery, source extraction, competitor scanning, and counterevidence. Do not let a draft agent approve its own page. The integrating model must reopen pivotal sources, reconcile definitions, build the engineering blueprint, and run validation.

Reject agent output when it contains an unopened URL, invented source ID, unsupported threshold, generic page boilerplate, or a tool recommendation without interface and limitation evidence. Cost optimization never weakens the evidence or publication gate.
