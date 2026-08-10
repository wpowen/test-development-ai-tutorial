# Curriculum Gap Audit Protocol

Use this protocol before course ranking or lesson writing. Its purpose is to make the Skill discover missing professional and AI knowledge without waiting for the user to name each missing topic.

## Research corpus

Build six independent evidence systems. A long source list from one system does not compensate for a missing system.

1. **Industry body of knowledge**: standards, certifications, role frameworks, textbooks, professional associations, and established methods. Reconstruct what competent practitioners already do before adding AI.
2. **Real work and practitioner evidence**: job descriptions, engineering blogs, conference talks, public case studies, issue trackers, incidents, and observable work artifacts. Capture decisions, constraints, failure costs, and adoption friction.
3. **AI technology and research frontier**: primary papers, official model/framework documentation, release notes, evaluation research, security guidance, and current architecture patterns. Record dates and versions.
4. **Open-source implementation and benchmarks**: repositories, harnesses, datasets, benchmark protocols, CI examples, issues, and pinned runnable artifacts. A repository link is not execution proof.
5. **Existing course supply**: official courses, paid courses, creator series, tutorials, syllabi, assignments, learner artifacts, assessments, and commercial promises across at least three platforms. Compare depth and proof, not titles.
6. **Failure, learner, and counterevidence**: practitioner complaints, postmortems, forum questions, course reviews, failure reports, adversarial research, and evidence that an attractive AI use case is unsafe, brittle, unnecessary, or already commoditized.

Each important curriculum decision must cite evidence from the systems that logically support it. Do not use a course page to prove technical capability or a framework document to prove learner demand.

## Coverage matrix

Create `research/curriculum-coverage-matrix.csv` before `curriculum.json`. Each row is an auditable learning cell:

`profession domain × learning layer × specialization × learner level × real scenario × learner artifact × exit assessment × evidence status`.

Required columns:

- `cell_id`
- `profession_domain_id`
- `layer_kind`
- `specialization_kind`
- `learner_level`
- `topic`
- `required_by_source_ids`
- `competitor_ids`
- `course_ids`
- `learner_artifact`
- `exit_assessment`
- `evidence_status`
- `coverage_status`
- `priority`
- `gap_reason`
- `decision`

Allowed coverage states:

- `covered`: a delivered or designed course addresses the cell and has an artifact plus assessment;
- `planned`: the cell is accepted into the roadmap with course IDs, artifact, and assessment;
- `gap`: evidence says the capability matters but the curriculum does not yet cover it;
- `rejected`: evidence was reviewed and the topic was intentionally excluded with a reason.

Do not hide gaps by giving them course titles. `planned` means the learning contract exists; `gap` means it does not. Critical and high-priority gaps require an explicit decision before the curriculum can pass.

## Automatic gap tests

The audit must actively search for these failure patterns:

- professional baseline omitted or reduced to generic workflow language;
- AI foundations taught after tools that depend on them;
- tool-centric modules with no retained professional principle or new failure mode;
- traditional work, AI-assisted work, testing AI systems, Agent/Workflow quality, production quality, and Benchmark engineering collapsed into one level;
- LLM, RAG, Agent, Workflow, security, observability, and Benchmark topics mentioned but not separated into assessable capabilities;
- a competitor gap claimed without inspecting competitor modules, assignments, artifacts, and assessments;
- source volume mistaken for source independence;
- current tools or model behavior supported only by stale tutorials or secondary summaries;
- concepts with no realistic business scenario, learner-owned artifact, failure injection, or exit assessment;
- benchmark scores taught without data provenance, split, harness, prompt, permissions, scorer, aggregation, uncertainty, contamination, and version;
- only happy-path demos, no incidents, failure reports, adversarial evidence, or counterevidence;
- claims of practical value supported only by synthetic fixtures;
- a large knowledge tree with only one runnable learning path;
- missing capstone that integrates the profession lifecycle and AI quality lifecycle.

## Independent expert review

Run six reviews after the first coverage matrix and before final sequencing. When subagents are available, use independent contexts; otherwise run separated passes and preserve each finding. Reviewers may reject or reorder topics but must not silently edit evidence status.

### Profession veteran

Check lifecycle completeness, role variants, real artifacts, decision rights, operational constraints, failure costs, and whether an experienced practitioner would recognize the work.

### AI systems engineer

Check model lifecycle, inference, RAG, tools, Agent/Workflow architecture, state, security, observability, deployment, and version dependencies.

### Evaluation and quality expert

Check Oracle design, datasets, slices, holdouts, judges, mutation, statistical validity, CI gates, traces, drift, incidents, and benchmark reproducibility.

### Curriculum designer

Check prerequisite order, cognitive load, concept-to-practice progression, artifact reuse, failure diagnosis, transfer, assessment, and capstone integration.

### Market and learner researcher

Check existing course supply, learner language, adoption friction, willingness-to-learn signals, format expectations, and whether differentiation is visible in learner outcomes.

### Adversarial critic

Search for overclaiming, decorative AI, unverified tools, source monoculture, missing counterevidence, unsafe automation, fake practical proof, and topics added only because they sound current.

## Curriculum decisions

Create `curriculum-gap-analysis.md` for human review. It must contain:

- `## Research corpus`
- `## Industry body of knowledge`
- `## Real work and practitioner evidence`
- `## Existing course supply`
- `## AI technology and benchmark frontier`
- `## Coverage matrix`
- `## Missing and overrepresented topics`
- `## Expert review` with all six reviewer headings
- `## Curriculum decisions`
- `## Remaining unknowns`

For every high-impact change, state the evidence, inference, decision, affected stages, and validation still missing. Preserve rejected ideas so future refreshes do not repeat the same weak direction.

## Refresh behavior

Re-run the affected matrix cells when any of these changes:

- profession standards or role responsibilities;
- a model, framework, evaluation method, or security recommendation;
- a benchmark protocol, dataset, harness, or leaderboard rule;
- a major course competitor or creator format;
- practitioner incidents, adoption patterns, or learner questions;
- the delivery status of a course or lab.

Never regenerate the whole curriculum blindly. Re-open changed sources, update affected cells, rerun the six reviews, then propagate approved changes through prerequisites, materials, tutorial pages, and validation.

## Fail-closed gate

Do not rank or generate courses when:

- any of the six evidence systems is absent;
- the matrix does not cover all required learning layers;
- an AI-quality profile lacks explicit LLM, RAG, Agent, Workflow, and Benchmark cells;
- a high or critical gap has no decision;
- any reviewer is missing;
- the human-readable analysis does not separate evidence, inference, decision, and unknowns.

