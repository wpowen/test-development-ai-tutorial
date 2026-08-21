# Software testing method-selection adapter

## Inputs and records

Accept versioned requirements/PRD, design and ADRs, OpenAPI/event schemas, state models, data contracts, terminology, risk register, historical defects, and environment constraints. Convert them to `RequirementContract`, `TestCondition`, `TestCase`, `Oracle`, `Result`, and `ReviewQuestion`; preserve source refs and explicit authority.

## Selection matrix

| Input/risk shape | Candidate method | Required selection note |
|---|---|---|
| finite domain or numeric limits | equivalence partitioning / BVA | classes, boundaries, invalid values, oracle |
| interacting conditions | decision table / combination | factors, constraints, pairwise limits, residual combinations |
| lifecycle and illegal transitions | state / N-switch | states, events, guards, transition oracle |
| cross-system business journey | scenario / CRUD | actor, trigger, side effects, handoff, rollback |
| API/schema compatibility | contract / schema | request/response, error, version, compatibility oracle |
| invariant over data or behavior | property-based | invariant, generator, shrinker, independent check |
| output relation without ground truth | metamorphic | transformation and expected relation |
| known implementation branch | white-box | branch/path target and coverage limitation |
| incomplete specification | checklist / exploratory | charter, timebox, observations, follow-up risks |

Select by risk, input shape, oracle availability, constraints, cost, and coverage—not tool count. Record rejected methods and residual risk.

## Oracle and package fields

Use layered oracles: transport, schema, source/provenance, semantic, risk/policy, and human approval. A test package records requirement/risk refs, technique, level, actions, data, environment, cleanup, oracle ID, pass/fail rule, evidence, run ID, actual status, defect/decision, and supersession.

## Mutation and maturity limits

Inject removed source refs, wrong status/permission, weakened prompt constraints, swallowed exceptions, skipped branches, and lost retry results. Record killed, survived, no-coverage, and timeout with disposition. Contract or mutation success is not production proof; fixture, integration, practitioner, and production maturity require separate receipts and gates.
