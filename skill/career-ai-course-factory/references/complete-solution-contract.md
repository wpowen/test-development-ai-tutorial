# Complete Professional Solution Contract

## Purpose

A complete course page is not a complete professional solution. A solution is complete only when a reviewer can trace a real professional problem through design, implementation, execution evidence, acceptance, human authority, operations, and change management.

Use this contract for every specialization, project, or end-to-end workflow that is presented as a solution. It applies even when several tutorial pages jointly teach one solution.

The governing chain is:

`business outcome -> requirement -> decision -> architecture -> interface/data contract -> implementation -> test/evaluation -> execution receipt -> operational decision -> learner artifact -> transfer`

Do not infer solution completeness from page count, prose length, material existence, or a successful static build.

## Required package artifacts

Create all of the following before describing any track as complete:

- `solution-architecture.md`: reader-facing solution overview, boundaries, views, decisions, gates, risks, and status;
- `research/solution-architecture.json`: canonical machine-readable solution contract;
- `human-review/04-完整方案审计.md`: plain-language verdict stating what is complete, what was executed, and what remains unproved;
- repository-owned architecture view files and execution receipts referenced by the JSON contract.

## The 25 mandatory dimensions

Every solution unit contains exactly one assessment for each dimension ID below. `not-applicable` is allowed only with a concrete rationale and reviewer. Silence is a gap.

1. `purpose-and-success`: business outcome, failure cost, measurable success, and decision owner.
2. `scope-and-non-goals`: included systems, users, environments, exclusions, and boundary conditions.
3. `stakeholders-and-decision-rights`: actors, RACI, approval, waiver, escalation, and human authority.
4. `current-state-and-baseline`: present workflow, tools, bottlenecks, baseline data, and current failure modes.
5. `use-cases-and-requirements`: primary, exception, abuse, and recovery cases plus functional and quality requirements.
6. `constraints-assumptions-dependencies`: policy, privacy, access, latency, budget, platform, organizational, and external constraints.
7. `alternatives-and-architecture-decisions`: viable options, trade-offs, chosen approach, rejected alternatives, and ADR ownership.
8. `context-and-component-architecture`: system context, responsibility boundaries, components, and external actors.
9. `runtime-workflow-and-state`: happy path, exception path, retries, timeouts, cancellation, state transitions, and human handoff.
10. `deployment-and-environments`: local, test, staging, production, network, secrets, configuration, CI/CD, container/device/Kubernetes topology as applicable.
11. `interfaces-and-integrations`: API/event/file contracts, auth, errors, rate limits, idempotency, compatibility, Jira/GitLab/Kubernetes or profession-specific integrations.
12. `data-lifecycle-and-governance`: acquisition, schema, lineage, quality, train/eval split, retention, privacy, access, deletion, drift, and data cards.
13. `ai-system-lifecycle-and-human-authority`: model/prompt/RAG/tool/agent versions, capability limits, evaluation, fallback, allowed actions, and approval boundaries.
14. `security-privacy-compliance`: assets, threats, trust boundaries, RBAC, secrets, PII, supply chain, audit, abuse, and compliance obligations.
15. `quality-test-evaluation-strategy`: risk model, test levels, datasets, oracles, slices, statistical method, regression, failure injection, flakiness, acceptance, and human review.
16. `performance-capacity-cost`: workload model, concurrency, latency distributions, throughput, tokens/tool calls, capacity, cost model, budgets, and saturation signals.
17. `reliability-resilience-disaster-recovery`: SLO, error budget, dependency failure, degradation, retry/circuit breaking, RTO/RPO, backup, recovery, and chaos scope.
18. `observability-operations-and-support`: logs, metrics, traces, semantic conventions, dashboards, alerts, on-call, runbooks, incident workflow, and feedback loop.
19. `implementation-and-repository`: code/config/data layout, versions, setup, commands, environments, ownership, and reproducible build.
20. `rollout-migration-rollback`: pilot, feature flags, compatibility, migration, canary, promotion, rollback, kill switch, and rollback evidence.
21. `delivery-plan-resourcing-ownership`: milestones, dependencies, staffing, owners, reviewers, estimates, and handoffs.
22. `risks-unknowns-technical-debt`: ranked risks, assumptions to validate, unresolved unknowns, debt, trigger, owner, and closure evidence.
23. `learner-experience-and-reusable-assets`: prerequisite, progression, demonstration, runnable materials, expected output, failure diagnosis, assessment, transfer, and direct reuse.
24. `evidence-traceability-and-acceptance`: bidirectional traceability from source and requirement to page, scenario, artifact, command, run evidence, assessment, and decision gate.
25. `evolution-versioning-and-deprecation`: version policy, refresh trigger, compatibility window, golden-set evolution, deprecation, migration, and change log.

## Mandatory architecture views

Each solution unit must provide repository-owned, substantive diagrams for all six view kinds:

- `context`: actors, external systems, solution boundary, trust boundary;
- `building-block`: components, responsibilities, stores, adapters, owners;
- `runtime`: ordered request/event/tool/human flow including failure and recovery;
- `deployment`: environments, compute, network, secrets, dependencies, telemetry;
- `data-flow`: data classes, schema/lineage, stores, retention and model/evaluation use;
- `security-trust-boundary`: entry points, privileged operations, sensitive data, controls and audit.

A list of box names does not count. Every view records purpose, nodes, edges, boundary, failure path, evidence points, and the decisions it supports.

## Decisions, interfaces, and traceability

Every solution unit records at least two architecture or operating decisions. Each decision includes context, options, choice, trade-offs, owner, status, and evidence needed to revisit it.

Every public page must participate in at least one trace row:

`coverage_cell_id -> topic_id -> page_id -> scenario_id -> artifact_ref -> command_ref -> execution_receipt_ref -> assessment_ref -> human_gate`

References are exact IDs or repository-relative paths. Required files must exist. A page, diagram, script, or receipt may be shared only when the contract explains why the same object genuinely serves both scenarios.

## Separate maturity states

Never collapse these states into one `status`:

- `design_status`: `gap`, `partial`, or `complete`;
- `execution_status`: `not-run`, `desk-researched`, `fixture-tested`, `integration-tested`, `live-tested`, or `production-validated`;
- `practitioner_review_status`: `not-reviewed`, `reviewed`, or `approved`;
- `publication_status`: `internal`, `pilot`, or `public`.

`design_status=complete` requires all 25 dimensions to be `complete` or justified `not-applicable`, all six architecture views, decisions, trace rows, acceptance gates, owners, and residual risks.

Publication minimums:

- `internal`: may expose gaps, but must label them and must not claim completeness;
- `pilot`: complete design, at least fixture-tested execution, and practitioner review;
- `public`: complete design, at least integration-tested execution, practitioner approval, rollback evidence, security review, and passed acceptance gates;
- `production-validated`: requires preserved live or production receipts and may not be inferred from fixture or integration proof.

Content completeness never promotes execution evidence. Execution success never proves architecture completeness.

## Execution receipt contract

Exit code alone is insufficient. Every claimed run links a structured receipt containing:

- receipt ID, solution ID, scenario, environment, timestamp, tool/model versions;
- exact command and working directory;
- input and configuration hashes;
- stdout/stderr or result artifact hashes;
- assertions evaluated and observed values;
- expected and actual verdict;
- failure injection, red evidence, repair, and green evidence where applicable;
- integration endpoints or adapters exercised;
- limitations and reviewer.

Fixture proof may use deterministic local systems. Integration proof must exercise at least one real adapter or controlled service boundary. Live and production proof must name the actual environment class without exposing secrets.

## Acceptance questions

A reviewer must be able to answer yes, with a linked artifact, to all of these:

1. Is the business decision and failure cost explicit?
2. Can another engineer reconstruct the architecture and runtime path?
3. Are data, interfaces, states, errors, ownership, and human authority defined?
4. Can the solution be installed or exercised without hidden context?
5. Does a meaningful injected failure turn the gate red, and does repair turn it green?
6. Are security, performance, cost, reliability, observability, rollout, and rollback operationally specified?
7. Are claims bounded by actual evidence maturity?
8. Can every public lesson be traced to an executable artifact, assessment, and decision?
9. Can a learner transfer the method to a different scenario and explain what must change?
10. Are unknowns, debt, refresh triggers, and deprecation responsibilities owned?

Any “no” keeps the solution internal or partial. Do not compensate with more prose.
