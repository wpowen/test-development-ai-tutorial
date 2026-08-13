# Source Assimilation and Information Fidelity Contract

## Purpose

User-provided documents are first-class sources, not optional inspiration. Never summarize, outline, or write pages before proving where every source section and substantive content atom goes. A shorter expression is allowed only after the protected meaning, constraints, uncertainty, examples, and decision impact are preserved.

## Required artifact

Create `research/source-assimilation-ledger.json` from frozen package-local copies of every user-provided source. Generate the initial inventory with `scripts/build_source_assimilation_ledger.py`; the generated `UNMAPPED` state is intentionally blocking.

For every source, preserve its package-relative path, SHA-256, authority, scope, owner, format, and complete section inventory. For every non-empty content atom under a section, preserve its kind, line range, hash, concise meaning, and disposition.

The deterministic inventory also records source-detected professional obligations. Career evolution, level, promotion, self-positioning, Agent architecture, or Agent testing material must trigger the corresponding capability declaration and specialized adapter; an author cannot bypass the deeper contract by omitting a declaration.

Allowed dispositions are:

- `incorporated`: taught directly with exact target page/block/artifact references;
- `adapted`: retained but parameterized, narrowed, or translated for the target profession; record the transformation and owner;
- `rejected`: not taught as guidance because it is unsupported, unsafe, stale, irrelevant, or contradicted; record the reason and evidence;
- `blocked`: potentially important but cannot yet be resolved; record owner, closure evidence, and downstream impact;
- `superseded`: replaced by a newer or stronger source; record the replacement.

`UNMAPPED`, silent omission, “covered elsewhere,” and a page title without a block/artifact target fail the contract. `incorporated` and `adapted` require learner-facing targets. `rejected`, `blocked`, and `superseded` require a rationale, owner, and evidence or closure reference. All sections and atoms must be accounted for; an overall summary cannot substitute for atom-level coverage.

## Authority-preserving adaptation

Do not turn user material into universal truth merely because it is detailed. Organization-specific levels, fixed years, promotion schedules, thresholds, percentages, and vendor claims must be one of:

1. supported by authoritative evidence for the declared scope;
2. converted into an explicit organization or metric-card adapter with owner, population, denominator, version, uncertainty, and failure action;
3. retained as a labelled example or hypothesis;
4. rejected or blocked with the original source locator preserved.

This rule preserves information without laundering weak claims into policy.

## Coverage receipt

The ledger records exact source, section, and atom counts; accounted counts; disposition counts; unaccounted IDs; the inventory command and version; reviewer; reviewed timestamp; and verdict. `PASS` requires exact inventory closure, zero `UNMAPPED`, zero unaccounted IDs, frozen hashes, and resolvable targets/evidence.

Atom closure is necessary but not sufficient. Before authoring, apply `source-exemplar-quality-and-semantic-parity-contract.md` and create `research/source-semantic-projection.json` so incorporated/adapted atoms retain their visual, template, prompt, workflow, decision, example, exercise, glossary, or risk-boundary function.

## Anti-bypass tests

Fail when a source heading or atom is missing from the ledger, a source hash drifts, a target does not exist, a fixed policy is copied without scope/owner, a rejected item has no rationale, or a rewritten page drops a protected definition, constraint, example, uncertainty, or decision boundary.
