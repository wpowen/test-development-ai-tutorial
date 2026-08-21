# Software Testing Career and Agent Architecture Adapter

Read this adapter only when a course declares `career-evolution-system` or `agent-architecture-testing`.

## Career evidence system

Represent career growth as evidence and decision scope, not universal years or company bands. Use four transferable responsibility states:

1. `guided-execution`: completes a bounded task with explicit method and review;
2. `independent-scoped-ownership`: owns an artifact, risk, Oracle, result, and handoff;
3. `system-cross-team-leverage`: creates reusable controls, platforms, or standards consumed by multiple teams;
4. `strategy-governance-mentoring`: owns risk policy, decision rights, governance, talent development, and feedback loops.

For each state, define observable work, decision rights, failure cost, required artifacts, mutations/faults, consumers, reviewers, and transition evidence. Create a self-assessment that asks for evidence refs, not confidence alone, and routes gaps to prerequisite pages and projects. Company P-bands, titles, years, promotion cycles, and target percentages belong in an `organization_level_adapter`; default them to `INTERNAL-UNKNOWN` until a named owner and internal source configure them.

## Agent architecture to testing system

Map the system under test before selecting tests. The minimum architecture covers eight domains:

- `D0-evaluation-trust`: gold data, judge calibration, disagreement, construct validity, evaluator drift;
- `D1-single-agent-capability`: instruction following, planning, tool selection, task outcome;
- `D2-orchestration-multi-agent`: routing, handoff, context survival, cascade containment;
- `D3-interaction-collaboration`: clarification, interruption, takeover, confirmation fatigue, human authority;
- `D4-robustness-reliability`: retry, timeout, checkpoint, idempotency, long-horizon degradation;
- `D5-security-adversarial`: injection, permissions, identity/delegation, memory/tool/supply-chain attacks, blast radius;
- `D6-efficiency-economics`: latency, throughput, resource, token/tool/judge/human cost and tail budgets;
- `D7-business-governance`: business outcome, policy, audit, privacy, staged rollout, waiver, rollback, risk acceptance.

Every domain maps `architecture_boundary -> risk -> observable -> method -> independent Oracle -> case/fault -> evidence -> stop/decision`. Use four configurable evidence rings: deterministic offline fixture, controlled sandbox/integration, shadow or canary, and continuous online monitoring. Each ring records entry, exit, hard blocks, population/workload, statistics, owner, rollback, and evidence maturity.

Do not copy example thresholds as universal gates. Store thresholds in metric cards with task/population, numerator/denominator, slice, baseline, uncertainty, sample-size rationale, version, owner, and failure action. Distinguish `pass@k` (at least one success across attempts) from `pass^k` (all repeated executions succeed), define task/session/trajectory units and state reset, and use paired or clustered uncertainty when repetitions share tasks. Zero observed incidents must include exposure and an upper-bound interpretation; it never proves zero risk.

## Required adapter artifact

Create `research/software-testing-career-agent-adapter.json` when either capability is declared. It contains the four responsibility states, evidence-bound self-assessment dimensions, organization adapter status, D0-D7 domains, four evidence rings, domain-to-test mappings, statistical semantics, metric-card policy, page IDs, owners, evidence refs, and maturity boundaries.

## Stop conditions

Stop when career levels depend only on years or vanity counts, self-assessment has no evidence refs, an Agent page lists risks without architecture boundaries and Oracles, D0 evaluator trust is absent, thresholds lack owner/population/uncertainty, or fixture success is promoted to enterprise, practitioner, or production validity.
