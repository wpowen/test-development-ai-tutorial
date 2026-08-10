# Professional artifact chain protocol

Use this protocol when a course covers a professional lifecycle rather than one isolated tool operation.

## Why this gate exists

A model can turn a source document into a convincing answer without producing anything a downstream worker can safely use. A professional course must show how one verified artifact becomes the input to the next job step, where work stops, and who owns the decision.

## Required chain model

For the selected professional workflow, identify:

1. source inputs and their precedence;
2. structured interpretation;
3. review and unresolved questions;
4. risk or decision model;
5. executable specification or work package;
6. execution adapter;
7. raw and summarized evidence;
8. professional decision;
9. change, feedback, or regression update.

The names vary by profession. Preserve the shape even when some stages are manual.

## Artifact contract

Every artifact records:

- `artifact_id` and `artifact_type`;
- `schema_version` and `content_hash`;
- `parent_artifact_ids`;
- source references at paragraph, page, record, or schema-pointer level;
- responsible owner and required reviewers;
- status: `DRAFT`, `ACCEPTED`, `UNKNOWN`, `BLOCKED`, `NOT_RUN`, `FAILED`, `PASSED`, or `SUPERSEDED` as applicable;
- facts, inferences, unknowns, and conflicts as separate fields;
- allowed AI actions and prohibited AI decisions;
- human gate and the evidence needed to close it;
- downstream consumer and exact fields it consumes;
- version or change event that invalidates the artifact.

Do not merge several lifecycle artifacts into an unstructured report. If the next step cannot consume a stable field, the current artifact is not finished.

## Source and conflict rules

- Pin document versions, repository commits, interface schemas, model/prompt/tool versions, and retrieval dates.
- Define source precedence before synthesis.
- Every material rule needs a source reference. Unreferenced suggestions stay `INFERRED` or `UNKNOWN`.
- A semantic conflict between current sources is `BLOCKED`; a model may identify it but may not choose the winning rule.
- Closing a conflict creates a new version. Do not overwrite the historical artifact.

## AI authority

AI may extract, classify, compare, generate candidates, execute bounded tools, cluster evidence, and draft reports when the action is inspectable and reversible.

AI may not silently invent professional policy, define a high-risk Oracle from the implementation it is testing, accept residual risk, approve a release, waive a failure, or execute an irreversible production side effect without explicit authority.

Separate the generator from the critic or verifier for high-risk artifacts. At least one important Oracle, labelled example, contract, invariant, or mutation must be independent of the generated implementation.

## Negative controls

The exemplar must include at least two different failure classes:

- an upstream evidence failure such as missing input, source conflict, unsupported rule, or unknown owner; this must stop downstream generation;
- a downstream product or workflow defect; an accepted specification must detect it and produce a reproducible failure.

Where applicable add environment, dependency, permission, privacy, and version-drift controls. Preserve `UNKNOWN` and `BLOCKED` instead of forcing binary pass/fail.

## Completion gate

Fail the course when any promised lifecycle stage lacks:

- a named input and output artifact;
- a stable schema or field list;
- a downstream consumer;
- an observable failure path;
- a human owner for professional decisions;
- a version/change rule;
- one runnable or inspectable example.

The final learner proof is an artifact chain with a baseline, a meaningful red result, a repair, raw evidence, and explicit remaining unknowns. A prompt, screenshot, generated file count, or polished summary is not sufficient.
