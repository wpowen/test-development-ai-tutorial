# Profession-to-AI Curriculum Architecture Protocol

## Controlling idea

A profession-specific AI curriculum needs two spines that meet deliberately:

1. the profession spine: lifecycle, work domains, methods, tools, artifacts, decisions, and failure costs;
2. the AI spine: model lifecycle, inference behavior, application architecture, evaluation, agents, production quality, and benchmark literacy.

Do not start from a list of AI tools or fashionable topics. Build the learner's transition from an existing professional baseline to new AI responsibilities. A learner may test out of a foundation stage, but the stage artifact and exit assessment may not be skipped.

## Required artifacts

Create both:

- `learning-architecture.md`: the primary human-readable explanation of the progression;
- `research/competency-transition-map.json`: the machine-checkable dependency and coverage record.

The Markdown must contain:

- `## Learner transformation`
- `## Professional baseline`
- `## AI foundations`
- `## Capability transition matrix`
- `## Learning stages`
- `## Specialization tracks`
- `## Benchmark literacy`
- `## Exit gates`

## Step 1: Reconstruct the profession before adding AI

Map the pre-AI profession as an experienced practitioner would teach it:

- end-to-end lifecycle and handoffs;
- stable work domains and recurring business events;
- methods, heuristics, and decision rules;
- current toolchain and automation surfaces;
- inputs, outputs, records, code, data, and approvals;
- quality criteria, failure modes, and failure costs;
- junior, intermediate, senior, and specialist differences.

The professional baseline is not a generic introduction. It answers: what must still be true if every AI tool is removed?

## Step 2: Define the minimum AI foundation

Teach only the model knowledge needed to reason about the profession, but teach it before depending on it. Cover:

- model lifecycle: data, pre-training, post-training/alignment, evaluation, deployment, inference, and monitoring;
- core primitives: tokens, representations/embeddings, attention/context, probabilistic decoding, prompts, tool calls, memory/state, and traces;
- application patterns: direct LLM, structured output, RAG, multimodal, agent, multi-agent, and workflow orchestration;
- capability boundaries: non-determinism, hallucination, stale knowledge, context limits, prompt sensitivity, tool error, excessive agency, privacy, latency, and cost;
- testing implications: observable inputs/outputs, versioned dependencies, oracle choices, datasets, slices, failure injection, and human review.

Do not turn the course into a model-training degree. Every foundation concept must link to a professional decision, failure, or test artifact.

## Step 3: Build the capability transition matrix

For each important baseline competency, record:

`baseline_competency -> retained_principle -> AI_change -> new_ai_capability -> new_failure_modes -> learner_artifact -> assessment -> course_ids`

Examples of valid transitions:

- deterministic assertion -> risk-based oracle -> semantic/probabilistic output -> composite oracle and calibrated judge;
- test case repository -> regression asset -> eval dataset -> provenance, slices, holdout, contamination controls;
- UI/API automation -> executable evidence -> tool-using agent -> trajectory, permission, state, and side-effect checks;
- CI pass/fail -> release decision -> model/prompt/data versions -> statistical gates, waivers, drift, and rollback.

Reject a transition when it merely adds “ask an AI tool” without a new professional control or inspectable result.

## Step 4: Use the eight-layer learning ladder

Every complete professional series covers these layer kinds in dependency order. Courses may combine adjacent layers, but the architecture cannot omit them.

1. `profession-baseline`: reconstruct the existing profession and prove entry competence.
2. `ai-foundation`: understand model behavior and AI application structure well enough to diagnose failures.
3. `ai-assisted-work`: use AI in existing work while preserving professional controls and comparing against the non-AI baseline.
4. `ai-system-quality`: test LLM, RAG, multimodal, or other AI systems with datasets, oracles, metrics, and human calibration.
5. `agent-workflow-quality`: test tools, state, trajectories, handoffs, permissions, side effects, and end-to-end workflow invariants.
6. `quality-engineering`: version, automate, observe, gate, monitor, waive, roll back, and learn from production.
7. `benchmark-literacy`: explain how benchmark tasks, data, prompts, scorers, aggregation, uncertainty, contamination checks, and leaderboards produce a score.
8. `capstone`: integrate earlier artifacts into a profession-relevant system and defend a decision with evidence.

Each layer records prerequisites, required concepts, learner-owned artifact, exit assessment, failure injection, source IDs, and the courses that satisfy it.

## Step 5: Select an architecture profile

Set `architecture_profile` in the transition map:

- `ai-enabled-practitioner`: AI augments a profession; require at least two relevant specialization tracks.
- `ai-builder`: the learner designs and operates AI applications; require LLM/application, agent/workflow, and production-quality tracks.
- `ai-quality-engineer`: the learner validates AI systems; require `llm-quality`, `rag-quality`, `agent-quality`, `workflow-quality`, and `benchmark-engineering` tracks.

Profile selection changes depth, not evidence discipline.

## Step 6: Design courses as connected artifact transformations

Every curriculum entry records:

- `stage_id` and `level`;
- `prerequisite_course_ids`;
- `knowledge_dependencies`;
- `professional_baseline` being retained;
- `new_ai_capability` being added;
- learner artifact and assessment;
- source IDs and delivery status.

Earlier artifacts must be reused later. A course sequence that repeatedly starts from a new prompt is not a system.

## Step 7: Teach benchmark scores as a pipeline

Any benchmark or leaderboard lesson must expose:

`construct -> sample -> label/reference -> split/holdout -> prompt/protocol -> run -> scorer -> aggregate -> uncertainty -> contamination audit -> report/version`

Require learners to reproduce at least one score on a tiny open fixture, change one protocol choice, and explain why the score changed. Cover pass@k, exact match, judge-based scores, task success, cost/latency, confidence intervals, dataset leakage, and version comparability only where relevant.

A leaderboard number without task definition, data lineage, evaluator version, and uncertainty is a claim, not a professional conclusion.

## Exit gates

Reject a complete-series claim when any applies:

- the professional baseline is missing or reduced to a job title;
- AI foundations are taught after courses that depend on them;
- a learner can skip a stage without passing its artifact-based exit assessment;
- course prerequisites are titles rather than knowledge and artifact dependencies;
- LLM, RAG, Agent, Workflow, and Benchmark are flattened into one generic “AI testing” module for an AI-quality profile;
- benchmark scores are presented without the data/protocol/scorer/aggregation chain;
- senior-level decisions, handoffs, permissions, and failure costs are absent;
- later courses do not reuse earlier artifacts;
- planned modules are presented as delivered instruction.
