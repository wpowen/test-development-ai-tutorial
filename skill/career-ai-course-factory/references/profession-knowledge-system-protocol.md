# Profession Knowledge System Protocol

## Why this gate exists

A profession cannot be represented by a list of popular tasks or tools. Before course design, reconstruct the profession as an operating system: how work enters, how it moves, which specializations inspect it, which systems are involved, which quality or business properties matter, who decides, and how the role evolves.

The output is a durable knowledge system that can be refreshed when AI or the profession changes. It must discover missing areas proactively; it must not wait for the user to name a forgotten specialty.

## Required outputs

Create both:

- `industry-framework.md`: readable explanation, coverage verdict, important transitions, unresolved gaps, and review questions;
- `research/profession-knowledge-system.json`: machine-readable graph described below.

The JSON is the source for curriculum coverage. The Markdown is the human review surface. Neither may be replaced by a course outline.

## Five mandatory dimensions

### 1. End-to-end lifecycle

Map work from intake to production learning. Use the profession's own vocabulary, but include the equivalents of:

`intake -> analysis -> planning/design -> preparation/implementation -> execution -> evidence collection -> diagnosis -> decision/handoff -> operation/monitoring -> feedback/improvement`

Every lifecycle stage records trigger, inputs, activities, outputs, artifacts, decision gate, owner, metrics, tools, failure modes, downstream handoff, evidence IDs, and course IDs.

### 2. Specialization families

Map horizontal and vertical specialties that cut across the lifecycle. For software testing this includes, where relevant, functional, API, UI, integration, contract, data, compatibility, accessibility, security, performance, reliability, resilience, chaos, observability, release, test automation, test platform, and production quality.

For another profession, derive the families from standards, job evidence, practitioner workflows, failure evidence, and existing training supply. A user-provided list is only a lead, never the completeness boundary.

Each family records scope, protected outcome, typical risks, methods, artifacts, metrics, tools, prerequisites, lifecycle-stage IDs, system-class IDs, AI changes, evidence IDs, and course IDs.

### 3. System or work-object classes

Map the materially different things the profession acts on. Examples include documents, source code, APIs, services, data pipelines, user interfaces, distributed systems, models, retrieval systems, agents, workflows, and production telemetry.

Each class records interfaces, state, dependencies, observability points, characteristic failures, quality attributes, relevant specializations, evidence IDs, and course IDs. Do not teach a method without naming what it operates on.

### 4. Quality or outcome attributes

Map the properties the profession is accountable for: correctness, completeness, safety, security, privacy, performance, reliability, recoverability, usability, accessibility, maintainability, cost, compliance, and profession-specific outcomes.

Each attribute records definition, observable indicators, leading and lagging metrics, test or verification methods, release or decision thresholds, trade-offs, AI-specific risks, evidence IDs, and course IDs. A metric list without a decision rule is incomplete.

### 5. Role and career evolution

Map role variants and levels, current responsibilities, adjacent roles, skills that remain durable, work likely to be assisted or automated, new responsibilities created by AI, transition projects, portfolio evidence, and decision authority.

Separate observed change from forecast. Job postings and vendor reports are signals, not proof that the whole market has changed.

## AI transformation contract

Every lifecycle stage and specialization family must contain at least one `ai_change`. Each change uses one of these classes:

- `retained`: the principle and human accountability remain;
- `assisted`: AI proposes or summarizes, and a human verifies;
- `automated`: a bounded, measurable step can run automatically with a fallback;
- `transformed`: inputs, methods, evidence, or decision gates materially change;
- `new-work`: AI creates a new system, failure, or operating responsibility;
- `declining`: demand may reduce; state evidence strength and never equate this with role elimination.

Every AI change records:

`change_id,change_class,baseline_work,ai_intervention,human_accountability,new_failure_modes,required_controls,learner_proof,evidence_ids,confidence`

Reject vague statements such as “AI improves efficiency” or “AI replaces testing.” A valid change names the step, control boundary, inspectable evidence, and residual human decision.

## Coverage cube

Build a crosswalk across:

`lifecycle stage x specialization family x system class x outcome attribute x learner level`

Not every combination needs a course. Every materially relevant cell needs one of:

- `covered`: a delivered or researched course owns it;
- `planned`: a course and artifact are named;
- `not-applicable`: rationale and evidence are recorded;
- `gap`: priority, reason, owner, and decision are recorded.

The knowledge system must contain at least:

- 8 lifecycle stages;
- 6 specialization families;
- 5 system classes;
- 6 outcome attributes;
- 4 role or career levels;
- 24 coverage cells;
- all six AI change classes across the complete system when evidence supports them, with at least `retained`, `assisted`, `transformed`, and `new-work` always represented.

Counts are minimum guards, not a completeness claim. A profession veteran and adversarial reviewer must still identify missing families and false boundaries.

## Research triangulation

For every high-priority lifecycle stage or specialization, use at least three independent evidence classes:

1. profession authority: standard, syllabus, regulator, or canonical body of knowledge;
2. real work: job task, practitioner workflow, incident, issue, or public artifact;
3. AI reality: official capability documentation, primary repository, benchmark, or reproducible implementation.

Add competitor/course evidence to understand what is already taught, and learner/community evidence to understand confusion and failure language. Neither substitutes for professional or technical truth.

## Professional completeness review

Before curriculum generation, run six separated reviews:

1. lifecycle continuity: every trigger, handoff, decision, and feedback loop is connected;
2. specialization completeness: no major professional specialty is absent because it was not named by the user;
3. system diversity: the framework does not assume every job object behaves like a document or chatbot;
4. metrics and gates: every important outcome has observable indicators and a decision rule;
5. AI-change realism: retained accountability, new failures, fallbacks, and limits are explicit;
6. career coherence: beginner, practitioner, senior, platform/lead, and adjacent-role transitions have evidence-producing projects.

Any critical or high gap blocks course generation until it has a documented decision. “Add later” is not a decision unless a course, owner, prerequisite, artifact, and acceptance gate are named.

## Anti-bypass tests

The Skill must fail when:

- lifecycle analysis stops at execution and omits evidence, release, monitoring, or feedback;
- a profession is split only by tools or AI product names;
- traditional specializations are absent while AI topics look complete;
- AI transformation claims omit the non-AI baseline or human accountability;
- metrics have no workload, slice, percentile/distribution, threshold, or decision owner;
- tool lists omit versions, interfaces, limits, and fallbacks;
- career advice is a forecast presented as current fact;
- planned coverage has no course, artifact, and assessment;
- public publication happens while a critical/high knowledge-system gap is unresolved.
