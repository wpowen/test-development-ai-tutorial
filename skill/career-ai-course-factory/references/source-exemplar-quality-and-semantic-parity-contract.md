# Source Exemplar Quality and Semantic Parity Contract

## Purpose

User-provided examples define a functional quality envelope, not a word-count target. A course may be shorter, reorganized, or corrected, but it must not silently reduce a detailed framework, visual, template, decision rule, worked example, exercise, resource index, glossary, or uncertainty boundary to a title and a paragraph.

This contract protects `frozen source -> semantic teaching function -> learner page / visual / reusable artifact / exercise`. It complements the atom ledger, which proves that text was dispositioned but cannot by itself prove that the source's teaching function survived.

## Required artifact

Create `research/source-semantic-projection.json` after `research/source-assimilation-ledger.json` and before curriculum or page writing. Validate it with `assets/schemas/source-semantic-projection.schema.json`.

Each incorporated or adapted source atom must appear in at least one semantic unit. A unit records:

- source item IDs and the protected teaching function;
- one function kind: concept model, comparison, workflow, decision rule, metric definition, threshold policy, career ladder, self-assessment, visual, template, prompt package, checklist, worked example, counterexample, exercise, source resource, reference claim, glossary, or risk boundary;
- exact learner-facing page targets;
- exact rendered visual, reusable asset, and exercise targets where applicable;
- whether the function is directly projected, adapted, blocked, rejected, or superseded;
- adaptation scope, owner, verification, and remaining uncertainty.

`PASS` requires exact coverage of all incorporated/adapted atoms, exact targets in the form `tutorial/tutorial-site.json#<page-id>#content_sections.<field-or-index>`, closed counts, current source-ledger hash, and a reviewer identity different from `author_id`.

## Functional parity rules

1. A source visual must remain a rendered, topic-specific visual with source, alt text, caption, nodes, edges, and an explanation of how to read it. Prose or a download-only archive is not visual projection.
2. A template, checklist, self-assessment, or prompt-like source must become an editable repository-owned learner artifact. Mentioning its fields in prose is not direct reuse.
3. A workflow must preserve actors, inputs, transitions, decisions, outputs, failure paths, and handoffs. A linear list that removes branches or owners fails.
4. A decision or metric system must preserve the question it answers, population, unit, numerator/denominator, slice, uncertainty, owner, and failure action.
5. A prompt package must include versioned system/task/critic prompts, fixed input, output Schema, eval set, mutation set, manifest, expected result, adaptation card, and refusal/Unknown behavior. A single generic prompt is not parity.
6. Worked examples and counterexamples must retain observable inputs, expected results, diagnosis, repair, and rerun. A plausible narrative is not an example.
7. Resource lists and glossaries must remain navigable learner surfaces when they are incorporated; dumping links into research evidence does not project them.
8. Organization levels, years, promotion schedules, weights, thresholds, vendor statistics, and legal claims are never promoted merely because the source is detailed. They must be independently supported for the declared scope, parameterized through an owner-controlled adapter/Metric Card, labelled as a source example or hypothesis, or blocked/rejected with the locator preserved.

## Page projection

Every promoted page also validates `research/topics/<topic-id>/projection-ledger.json` with `assets/schemas/page-projection-ledger.schema.json`. The ledger hash-pins the current manuscript and learner-facing `content_sections`, then maps each protected decision rule, judgement table, counterexample, failure mode, metric definition, threshold, boundary, and artifact to an existing `<page-id>#content_sections.<field-or-index>` target. It records separate `author_id` and `reviewer` identities.

Decision rules, judgement tables, counterexamples, failure modes, metric definitions, and boundaries may be projected or faithfully condensed; they may not be deferred or rejected from a delivered page. Counts must close with `unaccounted=0` and an independent reviewer must issue the verdict.

## Quality-parity acceptance

Do not claim “same quality” from prose length, page count, or source coverage alone. Require all six dimensions:

1. semantic-function coverage;
2. decision utility and professional correctness;
3. direct reuse with adaptation and verification;
4. visual and process intelligibility;
5. beginner terms, examples, failure repair, and transfer;
6. evidence authority, uncertainty, and maturity boundaries.

The target can exceed the example by correcting weak statistics and adding runnable proof. It must not fall below the example's useful functional coverage.

## Failure conditions

Fail on a missing projection artifact, source-ledger hash drift, unaccounted incorporated/adapted atom, prose-only visual, non-editable template, incomplete prompt package, generic shared diagram, unscoped numeric policy, missing page target, deferred critical claim, stale manuscript/page hash, self-approved verdict, or a “same quality” claim based only on volume.
