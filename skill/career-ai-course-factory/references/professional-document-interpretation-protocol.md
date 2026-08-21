# Professional document interpretation protocol

## Interpretation algorithm

1. Freeze the document version, hash, locator, authority, scope, and unknowns.
2. Extract actor, trigger, preconditions, inputs, observable outcomes, states, invariants, exceptions, non-functional constraints, and decision owner.
3. Classify each statement as `requirement`, `design`, `assumption`, or `unknown`.
4. Link every accepted claim to a source locator and record conflicts before proposing tests or prompts.

Requirements describe externally observable outcomes and constraints. Designs describe implementation choices, interfaces, dependencies, or trade-offs. A design cannot silently become a requirement; an assumption cannot be presented as evidence.

## Typed claim fields

Use `id`, `kind`, `source_refs`, `actor`, `trigger`, `preconditions`, `inputs`, `observable_outcomes`, `states/transitions`, `invariants`, `exceptions`, `nfr`, `constraints`, `owner`, `verification_methods`, `risk_refs`, `uncertainty`, `version`, and `status`. `ACCEPTED` requires resolvable source refs and an owner for material risk.

## Authority and review

Source authority or precedence must be explicitly declared with owner and evidence. Never infer a PRD/OpenAPI/design order. Missing, ambiguous, conflicting, expired, or unlocatable authority is `BLOCKED`. Raise review questions for conflicts, missing SLA/permission/retry/oracle, unsupported rules, and claims affecting money, access, state, compliance, or publication. Each question records impact, risk, owner needed, block level, closure evidence, and status.
