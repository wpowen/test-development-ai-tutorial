# Professional capability and evidence contract

Use this contract for every learner-facing page. It prevents a page from bypassing professional methods by omitting a capability declaration, and prevents fixture proof from being promoted into real-model, integration, practitioner, learner, or production proof.

## Capability profile

Create `research/capability-profiles.json` with one exact record for every promised public page. A record contains:

- `page_id`;
- one or more capabilities from `profession-baseline`, `artifact-transformation`, `ai-system-evaluation`, `supervised-agent-workflow`, `ai-quality-system`, `career-evolution-system`, and `agent-architecture-testing`;
- profession-specific rationale and failure risk;
- independent reviewer, review time, and evidence references.

Do not use `none`, an empty list, a title heuristic, a prefix, or an inferred profession method. Group capability declarations remain in `research/capability-declarations.json`, but their exact topic/page coverage must contain every capability named by each page profile.

Do not rely only on author declarations. The frozen source inventory records detected professional obligations. When user-provided material contains career evolution/level/promotion systems or Agent architecture/testing systems, the corresponding `career-evolution-system` or `agent-architecture-testing` declaration and profession adapter become mandatory. Missing declarations are a fail-open attempt and block the package.

`artifact-transformation` activates the full method-library, document interpretation, source-authority, transformation-contract, prompt/eval/mutation, independent-Oracle, and source-to-result trace contract. Other capabilities do not silently inherit a testing method; their profession adapter must name its own work objects, risks, methods, oracles, and human authority.

## Five evidence lanes

Create `research/professional-evidence.json` with one exact record for every promised page. Keep five lanes separate:

1. `model`: actual provider/model/version/parameters, repeated raw outputs, scorer, independent Oracle, cost and latency;
2. `integration`: actual target system, controlled environment, authentication, permissions, cleanup, rollback, and structured receipts;
3. `clean_room`: final learner artifact executed from a fresh unpacked copy with exact command, working directory, platform, exit code, artifact hash, and every learner-facing command surface;
4. `practitioner`: named reviewer identity, relevant qualification, review scope, conflicts, date, verdict, and receipt;
5. `learner`: target learner profile, participant count, task completion, time on task, error recovery, transfer success, accessibility observations, and receipt.

Each lane uses only `NOT_RUN`, `PASS`, `FAIL`, or `BLOCKED`. Every lane records `receipt_refs` and `limitations`; `PASS` requires a repository-owned structured receipt. Unknown evidence remains `NOT_RUN` or `BLOCKED`, never an empty success.

## Model matrix

A model `PASS` requires a real provider, model and version. `provider=none`, offline fixtures, deterministic adapters, or a model-generated narrative cannot establish model execution. Run at least two repetitions and preserve one SHA-256 raw-output hash per run. For consequential model behavior, cover:

- positive and ordinary cases;
- boundaries and conflicting sources;
- missing and unauthorized inputs;
- refusal and safety behavior;
- truncation, timeout, malformed structure, and tool failure;
- prompt injection and instruction conflict;
- paraphrase, locale, and long-context variants;
- stochastic disagreement, cost, and latency.

The model under test cannot approve its own semantic result. Use an independent deterministic Oracle, a separately governed scorer with human calibration, or a qualified human decision owner. Record disagreement rather than averaging it away.

## Integration adapter

An integration `PASS` requires a controlled but real target boundary. Record endpoint or system version, environment, auth mode, tenant and role, test data, side-effect policy, retry/idempotency behavior, cleanup, rollback, logs, and receipt hashes. A local fake proves only fixture behavior. Missing credentials are a valid reason for `NOT_RUN`; they are not evidence that integration works.

## Clean-room parity

The exact command in a page, manuscript, lab manifest, tutorial projection, and archive must be identical or explicitly generated from one command contract. Execute from a fresh unpacked release, not the authoring tree. Reject:

- author-workspace paths;
- implicit current working directories;
- hidden environment variables or credentials;
- undeclared downloads;
- commands absent from any declared learner surface;
- an artifact hash that differs across source, static export, or archive.

Fixture maturity requires clean-room `PASS`. This is stronger than file existence but still does not prove real-model or enterprise integration behavior.

## Practitioner and learner gates

Practitioner evidence must be attributable and relevant to the reviewed decision. “Independent reviewer”, an agent name, or an author score is not a practitioner identity. Record qualification, scope, conflicts, requested changes, accepted residual risks, and verdict.

Learner evidence must come from target learners. `PASS` requires at least five participants for an initial course gate and preserves individual task results. Measure completion, time, errors, recovery, transfer to a different context, and accessibility obstacles. Satisfaction alone is not learning efficacy.

## Maturity transitions

- `desk-researched`: evidence-bound design; no execution claim;
- `fixture-tested`: clean-room fixture `PASS`;
- `model-integrated`: clean-room and real-model `PASS`;
- `integration-tested`: clean-room, real-model, and target-integration `PASS`;
- `practitioner-reviewed`: named practitioner lane `PASS` in addition to the claimed execution boundary;
- `production-validated`: all five lanes `PASS`, plus complete-solution production and rollback receipts.

Higher evidence can exist while the claim remains conservative. Lower evidence can never be promoted by prose, page count, editorial score, static validation, or a copied receipt.

## Status supersession

Create `research/status-registry.json`. Track every human-facing verdict from `human-review/04-*` onward with `record_id`, `artifact_type`, `scope_id`, `path`, `as_of`, current public-scope hash, artifact hash, `current|superseded`, `supersedes`, and evidence refs.

Exactly one verdict per artifact type and scope is current. A newer verdict explicitly supersedes every older verdict in the same scope. Untracked, hash-drifted, or simultaneously current verdicts fail. Never ask a reader to infer which report is newer from filenames or prose.

## Publication projection

Publish hash-pinned projections as:

- `CAPABILITY-PROFILES.json`;
- `PROFESSIONAL-EVIDENCE.json`;
- `STATUS-REGISTRY.json`.

Pin them from `RELEASE-MANIFEST.json`. Their ordered page IDs must exactly equal the public tutorial. A release may honestly carry `NOT_RUN` lanes at an allowed lower maturity, but it may not omit the lanes or exceed their evidence.

## Required adversarial regressions

Keep tests that fail when:

- a public page omits its capability profile;
- a page names `none`, an unknown capability, or a capability not covered by a declaration;
- an artifact-transformation page omits its method, authority, Oracle, eval, mutation, or trace;
- a model `PASS` uses `provider=none`, lacks repeated raw outputs, or lets the model own its Oracle;
- an integration `PASS` lacks auth, cleanup, or rollback;
- a fixture claim lacks a clean-room `PASS`;
- a learner `PASS` uses fewer than five target learners;
- a command differs across declared learner surfaces or only works in the author tree;
- two unsuperseded verdicts exist or a verdict hash drifts;
- a public release omits or fails to hash-pin any professional-evidence projection.
