# Artifact reconciliation and traceability protocol

## Graph contract

Represent nodes with `id`, `kind`, `version`, `status`, `owner`, `source_refs`, and content hash. Core kinds are `source`, `claim`, `risk`, `method`, `oracle`, `case`, and `result`; edges use `refs`/`depends_on`, direction, rationale, and evidence. A result may also point to run receipt, mutation, review, and superseded IDs.

## Closure and reconciliation algorithm

Build forward links from source to result and reverse indexes from result to source. For every accepted result, traverse and verify the complete chain `source → claim → risk → method → oracle → case → result`; verify each reverse link returns to the originating node. A node with no valid predecessor/successor is an orphan and remains exploratory, not coverage. Compare duplicate claims by version/hash, retain conflicts, and require an adjudication decision.

## Change and supersession

When a source, prompt, method, oracle, or case changes, mark the prior node `SUPERSEDED`, preserve its hash and reason, and re-run affected descendants. Never overwrite old evidence or borrow a result from an unrelated branch. Broken locators, unknown hashes, or changed authority invalidate dependent results.

## Stop states

Propagate `BLOCKED`, `UNKNOWN`, `SCHEMA_INVALID`, `REFUSED`, `INCOMPLETE`, `SOURCE_CONFLICT`, `UNSUPPORTED_RULE`, and `SEMANTIC_UNKNOWN` downstream. No publication or maturity upgrade is allowed while any required path carries a stop state.
