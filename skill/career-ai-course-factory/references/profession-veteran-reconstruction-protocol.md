# Profession Veteran Reconstruction Protocol

## Purpose

Reconstruct the profession before proposing AI lessons. The “veteran” is an evidence-bounded research lens, not a claim that the model has actually held the job for ten years.

The reconstruction must answer four questions:

1. What work is really done, by whom, in what order, and with which dependencies?
2. Which artifacts and decisions create business value, reduce risk, support performance reviews, or demonstrate promotion readiness?
3. Where does the work currently lose time, quality, information, or decision confidence?
4. Which parts can AI assist, automate, transform, or create without hiding ownership and failure risk?

Do not select course topics until this gate passes.

## Independent reconstruction roles

Run these as independent passes or subagents when available. Preserve disagreements.

- `veteran-operator`: reconstructs a concrete day, week, incident, and deliverable lifecycle.
- `manager-promotion-reviewer`: identifies expected scope, performance signals, promotion evidence, and decision rights.
- `workflow-platform-engineer`: maps tools, systems, handoffs, environments, data, automation, and operational dependencies.
- `junior-observer`: records where a beginner lacks context, access, vocabulary, examples, or reusable starting material.
- `market-community-researcher`: searches occupation frameworks, job posts, public career ladders, practitioner communities, talks, blogs, courses, templates, and open-source artifacts.
- `ai-systems-engineer`: maps feasible AI interventions, required context, evaluation, security, cost, and fallback controls.
- `adversarial-critic`: challenges generic role claims, invented internal practice, unsupported prevalence, and AI proposals that cannot be verified.

No role may approve its own synthesis.

## Evidence surfaces

Use multiple source families. A large number of pages from one family does not count as breadth.

1. occupation authorities, professional bodies, government capability frameworks, and standards;
2. public employer role definitions, engineering handbooks, career ladders, and current job postings;
3. practitioner forums, issue discussions, conference talks, technical blogs, incident write-ups, and community templates;
4. GitHub repositories, reference implementations, tools, datasets, benchmarks, and their issue trackers;
5. direct course pages and learning materials, including exercises and learner feedback when public;
6. current AI model, framework, security, evaluation, and observability documentation;
7. counterevidence showing role variation, failed adoption, weak ROI, or work that should not be delegated.

Communities provide pain language and case leads, not universal prevalence. Vendor pages provide capability claims, not efficacy proof. Open pivotal sources before using them.

## Required profession reality map

Create both:

- `profession-reality-map.md` for human review;
- `research/profession-reality-map.json` for validation and downstream generation.

The map must contain:

### Role boundary and variants

- canonical role and adjacent titles;
- seniority levels and individual-contributor versus management variants;
- organization, product, industry, and regulatory contexts that materially change the job;
- public facts, supported inference, and `INTERNAL-UNKNOWN` kept separate.

### Work rhythm and workflow

Reconstruct at least:

- one ordinary workday;
- one weekly or sprint rhythm;
- one end-to-end deliverable lifecycle;
- one failure, incident, or exception path.

For each stage record trigger, actor, input, activity, dependency, tool or system, output artifact, decision, downstream consumer, failure cost, and evidence IDs.

### Artifact and dependency graph

List the artifacts that make the work reviewable: requirements, plans, designs, code, datasets, reports, dashboards, decisions, approvals, handoffs, and operational evidence. Record owners, source references, versions, acceptance rules, and downstream consumers.

Map dependencies on people, policies, data, access, environments, services, vendors, and time windows. An AI proposal that ignores a critical dependency is blocked.

### Performance and promotion signals

Separate:

- output volume from outcome or risk reduction;
- individual execution from reusable leverage;
- local delivery from cross-team influence;
- public career-framework evidence from organization-specific criteria.

Typical evidence may include reliable delivery, escaped-defect reduction, faster feedback, reusable tooling, standards, incident learning, stakeholder decisions, mentoring, and ownership breadth. Do not assert that any signal determines promotion in a target organization without internal evidence. Mark it `INTERNAL-UNKNOWN` and provide an interview or document request.

### Pain and information barriers

Classify pain as repetitive work, fragmented context, coordination delay, uncertain Oracle, diagnosis cost, data or environment setup, feedback latency, compliance risk, or missing authority. For every pain record frequency evidence, failure cost, current workaround, and what remains unknown.

Map information barriers:

- publicly obtainable knowledge;
- organization-internal policies, data, incident history, permissions, and tacit practice;
- external versus internal information gaps;
- required interviews or documents needed to close the gap.

Never invent internal process. Use `INTERNAL-UNKNOWN`, `BLOCKED`, or a bounded synthetic fixture.

### AI opportunity matrix

Classify every candidate as `retained`, `assisted`, `automated`, `transformed`, `new-work`, or `declining`.

Each candidate must include:

- current baseline and pain;
- proposed AI role;
- required inputs, access, and context;
- inspectable output or action;
- human owner and approval point;
- AI-specific failures;
- security, privacy, cost, and freshness constraints;
- baseline metric and success measure;
- smallest reusable learner material;
- failure injection or negative test;
- evidence status and confidence.

Reject “ask a chatbot to write X” unless the output enters a real artifact chain, can be checked, and changes a professional decision or handoff.

## Beginner reuse gate

Every selected opportunity must yield a starter pack a junior can use without pretending to know hidden enterprise context:

- realistic but synthetic or sanitized input fixture;
- editable prompt, Skill, schema, checklist, or adapter;
- exact command or interaction sequence;
- expected output and stop states;
- at least one seeded failure;
- repair path;
- transfer checklist for replacing the fixture with local data;
- a baseline and a post-use measure.

If the learner only receives an explanation or plausible prose, the opportunity is not ready for a course.

## Evidence-bounded veteran Agent prompt

Use this as a system-prompt template and fill the brackets from research:

```text
You are the profession-reconstruction analyst for [PROFESSION]. Work through the lens of a practitioner who understands senior-level scope, but never claim personal employment history or hidden company knowledge.

Your first job is to reconstruct the profession, not to recommend AI tools. Use opened sources and supplied internal documents. Label every material statement as FACT, PRACTITIONER-SIGNAL, INFERENCE, VENDOR-CLAIM, or INTERNAL-UNKNOWN. Cite source IDs. If a workflow varies by organization, show the variants.

Reconstruct one ordinary day, one sprint or weekly rhythm, one deliverable from trigger to downstream decision, and one failure or incident path. For every stage name the actor, input, dependency, system, artifact, decision right, failure cost, and downstream consumer.

Then map performance and promotion signals, pain points, information barriers, and current workarounds. Do not infer an internal policy, metric, data source, permission, or promotion rule. Mark it INTERNAL-UNKNOWN and state the interview question or document needed.

Only after the profession map is complete may you propose AI interventions. For each intervention preserve the professional principle, define AI authority, human gate, new failure, verification method, baseline metric, and a starter pack a junior can run. Reject generic prompt-only ideas and any proposal that cannot be made red with a meaningful defect.
```

## Completion gate

Pass only when:

- role variants and organizational variability are explicit;
- the work rhythm, deliverable lifecycle, and exception path are reconstructed;
- artifacts, dependencies, decisions, performance signals, and information barriers are connected;
- internal unknowns are visible and have closure actions;
- AI opportunities are ranked against real pain and feasible controls;
- at least one beginner starter pack has a red-green proof loop;
- a profession veteran pass and adversarial critic pass have both reviewed the map.

