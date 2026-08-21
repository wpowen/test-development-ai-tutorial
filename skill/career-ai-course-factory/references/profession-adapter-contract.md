# Profession adapter contract

## Boundary

The generic core owns input hashes and locators, schemas, state propagation, traceability, evaluation records, run receipts, mutation semantics, maturity labels, and human gates. It must not encode a profession's titles, tools, project IDs, or document assumptions.

## Adapter interface

An adapter declares `adapter_id`, supported capability, version, owner, source authority/precedence with evidence, method library, document vocabulary, work-object/artifact types, risk taxonomy, selection rules, independent oracle types, mutation patterns, privacy limits, and fallback. Each method includes rationale, applicability, infeasible combinations, cost, residual risk, and source refs. Each oracle names its independent authority and decision threshold.

## Gates and maturity

Capability mapping is mandatory and explicit at page/topic level through `capability-profiles.json`; profession methods remain activated only by the declared capability, never inferred from a title. Once activated, missing method rationale, source authority, oracle, prompt/eval/mutation trace, or human owner fails closed. Every page also carries model, integration, clean-room, practitioner, and learner lanes. `PASS_SCHEMA` proves structure only. `fixture-tested`, `model-integrated`, `integration-tested`, `practitioner-reviewed`, and `production-validated` require their own receipts; no status is inferred or upgraded from prose.
