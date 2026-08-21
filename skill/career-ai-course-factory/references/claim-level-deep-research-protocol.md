# Claim-level ChatGPT Deep Research Protocol

## Purpose

Every publishable technical or professional proposition must be extracted as an independent atomic claim, classified, routed, independently adjudicated, and mapped to its manuscript, learner page, metric card, gate, lab, visual, or reusable artifact. The claim remains individually traceable even when an external fact is researched once as a canonical anchor and its evidence is reused under an explicit transfer decision.

Only `EXTERNAL-RESEARCH` claims whose evidence class is an external technical fact or empirical generalization enter formal ChatGPT/OpenAI Deep Research. `LOCAL-DETERMINISTIC` claims use repository, schema, runner, fixture, manifest, and hash evidence; `TARGET-EVIDENCE` claims use the real provider, target system, organization, production, practitioner, or learner evidence that they assert; `TEACHING-VALIDATION` claims use explicit design or human evidence. No route may be silently substituted for another.

A topic-level source list, two named research routes, a generated synthesis, a Luna summary, or a manually written `research-runs.json` does not prove that ChatGPT or OpenAI Deep Research was called. A formal external run needs a provider receipt, saved request and raw response, tool-call trajectory, citations, opened-source inventory, iterative expansion, contradiction adjudication, and a terminal saturation verdict. Local and target evidence need their own hashes, commands or snapshots, owners, and limitations.

This protocol is fail-closed. Research can end with a supported claim, a narrower scoped claim, an explicit unknown, or a rejected claim. It must never manufacture certainty merely to make every claim publishable.

## Official OpenAI capability boundary

OpenAI's official [Deep research API guide](https://developers.openai.com/api/docs/guides/deep-research) documents Responses API research using web search, file search, remote MCP, and optional code interpreter. It recommends background execution for long-running work and exposes search/tool calls plus inline citations in the response output.

The current official [model catalog](https://developers.openai.com/api/docs/models/all) marks the named `o3-deep-research` and `o4-mini-deep-research` models as deprecated. Therefore:

- never hardcode those model names into the course factory;
- resolve the currently available deep-research-capable model or ChatGPT feature at execution time;
- save the exact provider, surface, model or feature name, response/export ID, timestamps, tools, request hash, response hash, and limitations;
- if no current deep-research-capable surface is available, set the run to `BLOCKED-CAPABILITY`; do not substitute an ordinary summary and call it Deep Research.

Supported execution surfaces are:

1. `openai-responses-api`: a current OpenAI Responses API model with at least one research data source and saved response/tool/citation output;
2. `chatgpt-deep-research`: the ChatGPT Deep Research product with an exported report, source list, activity/trajectory evidence when available, and stable export or conversation identifier.

When the user explicitly selects Codex-native research instead of either official surface, follow `codex-research-execution-contract.md` and set `execution_contract=codex-research.v1` in the claim inventory. Its receipts, agent traces and saturation artifacts are separate. A Codex result may reach `PASS-CODEX-RESEARCH`, while `deep_research_status` remains `BLOCKED-DEEP-RESEARCH`; never convert it into an OpenAI provider receipt.

## Evidence routing and reuse boundary

R0 covers every page and every claim without making a network request. Assign one primary evidence class and an explicit route before scheduling research:

| evidence class | default route | typical evidence | external Deep Research |
|---|---|---|---|
| `LOCAL-DETERMINISTIC` | `LOCAL-VERIFY` | repository files, schemas, prompts, runner, fixture, projection, status, material and hash checks | never as proof of local execution |
| `STABLE-DEFINITION` | `EXTERNAL-RESEARCH` | standard, protocol, definition, formula, official technical semantics | canonical anchor may be shared when scope/version/predicate match |
| `SHARED-MECHANISM` | `EXTERNAL-RESEARCH` plus transfer | mechanism, state transition, public failure mode and boundary | canonical anchor plus member transfer; no copied conclusion |
| `VENDOR-VERSION` | versioned external research plus local/target check | API, model, SDK, field, limit, deprecation or tool behavior | default no direct reuse across versions/vendors |
| `NUMERIC-STATISTICAL` | external evidence or target experiment | threshold, rate, CI, performance, cost, causal or comparative result | default `NO-REUSE`; bind population, denominator, environment and uncertainty |
| `SECURITY-AUTHORITY` | external background plus local/target control evidence | privacy, ACL, authorization, compliance, abuse and human authority | background may be shared; decision and acceptance may not |
| `FAILURE-OPERATIONS` | mechanism research plus local/target replay | diagnosis, recovery, observability, rollback, incident and escalation | background may be shared; Oracle, repair and target state stay separate |
| `TEACHING-PROFESSIONAL` | design or human evidence | comprehension, transfer, role, prevalence, practitioner or learner claims | never replaced by a technical packet |
| `TARGET-EMPIRICAL` | `TARGET-EVIDENCE` | current provider, corpus, ACL, integration, production, practitioner or learner result | generic web research cannot satisfy it |

The allowed claim-level origins are `DEDICATED`, `DIRECT-REUSE`, `SOURCE-REUSE-DELTA`, `LOCAL-DETERMINISTIC`, `TARGET-EVIDENCE`, `TEACHING-VALIDATION`, and `BLOCKED`. `DIRECT-REUSE` means only that the source packet's support range is exactly applicable; it does not copy the anchor receipt, report path, final disposition, or saturation. `SOURCE-REUSE-DELTA` requires a real delta artifact. `NO-REUSE` requires independent research or a blocker. Unknown identity, scope, version, environment, population, region/language, vendor, or risk fields are treated as non-equivalent.

Shared source is not shared conclusion. A canonical packet must declare its `supports_predicates`, `cannot_prove`, source families, opened-source refs, version/time/environment/population/region, risk, counterevidence, adjudication, saturation, and invalidation triggers. Each member claim records its own transfer inputs, field-by-field decision, applicable dimensions, cannot-prove boundary, contradiction/adjudication, disposition, and projection locator. An anchor packet's `SATURATED` status never automatically promotes a member claim.

Luna or another lower-cost model may extract, normalize, cluster, deduplicate source candidates, organize technical-document Markdown, rank gaps, aggregate cost telemetry, and integrate page material. Those outputs are proposals or integration artifacts. They must not manufacture provider response IDs, raw responses, source-open events, citation trajectories, completed receipts, saturation PASS, target PASS, practitioner PASS, or learner PASS. A Luna conversation is neither an OpenAI Deep Research receipt nor a Codex runtime trace.

## Executable Responses API surface

The Skill ships `scripts/run_claim_deep_research.py` as the canonical API runner. It uses only the Python standard library, does not persist credentials, submits the response in background mode, polls the provider response until a terminal state, saves provider artifacts, and appends a receipt only after fail-closed output checks pass.

Configure the credential outside the repository and resolve the current compatible model at execution time:

```bash
export OPENAI_API_KEY='...'
export OPENAI_DEEP_RESEARCH_MODEL='<current-compatible-model>'
```

The Skill must never print, copy, commit, or write `OPENAI_API_KEY`. If the key or a current compatible model is unavailable, report `BLOCKED-CAPABILITY` or `BLOCKED-DEEP-RESEARCH`; do not substitute a normal model answer.

Run a dedicated breadth phase for one claim:

```bash
python3 scripts/run_claim_deep_research.py \
  --package-root <course-package> \
  --topic-id <topic-id> \
  --claim-id <claim-id> \
  --phase initial-deep-research \
  --round 1 \
  --prompt-file <claim-specific-instructions.md>
```

Then run counterevidence as a distinct provider request with `--phase counterevidence --round 2`. Use later `gap-fill` and `verification` phases only for named unresolved dimensions, contradictions, stale versions, or decision-changing unknowns.

Public-web research is the default. For private or organization-controlled evidence, use `--no-web` with one or more `--vector-store-id`, or with `--mcp-server-url` and `--mcp-server-label`. The runner blocks mixed public-web and private-source access unless `--allow-mixed-public-private` is explicitly passed after reviewing prompt-injection and data-exfiltration risk. `--dry-run` validates the claim, model, source configuration, and request shape without reading the credential or making a network call.

Each successful run writes:

```text
deep-research/<run-id>/
├── request.md
├── request.json
├── raw-response.json
├── report.md
├── citations.json
└── tool-calls.json
```

The raw artifacts are retained even when final validation fails. In that case the runner does not append `status=completed` to `deep-research-receipts.json`.

## What counts as a proposition

Create an atomic claim whenever a sentence or technical block asserts one independently checkable idea in any of these classes:

- definition or terminology;
- mechanism or causal relationship;
- numeric value, rate, threshold, range, or sample requirement;
- comparison, superiority, tradeoff, or recommendation;
- version, compatibility, API, field, command, or tool behavior;
- metric meaning, formula, unit, aggregation, uncertainty, or gate;
- architecture, workflow, security, privacy, performance, cost, or operations rule;
- professional responsibility, workflow reality, prevalence, career, or organizational claim;
- failure mode, diagnosis rule, recovery, rollback, or escalation boundary;
- teaching claim about beginner comprehension, reuse, transfer, or effectiveness.

Do not create claims for headings, transitions, navigation labels, or repository-local instructions whose truth is established by a deterministic file or execution check. Those still require local validation.

Split compound sentences until each claim can independently be `SUPPORTED`, `SCOPED`, `UNKNOWN`, or `REJECTED`.

## Mandatory per-topic route-aware package

Every promised topic must retain its own page-level research and projection closure. It does not need to duplicate a canonical provider report. In addition to the existing topic package, every promised topic must contain:

```text
research/topics/<topic-id>/
├── claim-inventory.json
├── canonical-packet-refs.json
├── reuse-decisions.json
├── local-evidence.json
├── target-evidence.json
├── teaching-evidence.json
├── contradiction-matrix.md
├── research-saturation.json
├── projection-ledger.json
├── deep-research-receipts.json (only when this topic owns an external anchor/delta run)
├── codex-research-receipts.json (only when Codex-native research was explicitly selected)
└── deep-research/
    └── <run-id>/
        ├── request.md
        ├── raw-response.json
        ├── report.md
        ├── citations.json
        └── tool-calls.json
```

The old `research-runs.json` remains an orchestration index. It cannot replace provider receipts or Codex runtime traces, and it cannot be used to force a provider receipt onto a local, target, or teaching claim. `canonical-packet-refs.json` points to an approved packet registry; `reuse-decisions.json` records each member's transfer; the local, target, and teaching records preserve their own artifact or human evidence and blocker states.

## Claim inventory contract

`claim-inventory.json` records:

- `schema_version`, `topic_id`;
- extraction source files and their SHA-256 hashes;
- distinct `author_id` and `independent_auditor_id`;
- `unmapped_propositions`, which must be `0`;
- every claim's `claim_id`, statement, type, risk, scope, source locations, required research dimensions, proposed publication disposition, primary cluster, evidence class, route, and evidence origin;
- identity fields used for safe transfer: subject, predicate, claim-type family, population, environment, version/time boundary, vendor/tool, region/language, authority risk, target-evidence requirement, and scope digest;
- page coverage fields: exact expected page IDs, inventory-covered page IDs, missing-page IDs/digest, and counts. A partial inventory must remain visibly partial.

The inventory must include claims from the research brief, evidence synthesis, engineering blueprint, manuscript, metric cards, labs, diagrams, and final learner projection. A later content change invalidates the inventory until extraction is rerun.

Create it through the canonical compiler, not by directly editing the final receipt:

```bash
python3 scripts/prepare_claim_inventory.py \
  --package-root <course-package> \
  --topic-id <topic-id> \
  --claims-file <independently-reviewed-claim-list.json> \
  --source-file manuscript.md \
  --source-file engineering-blueprint.md \
  --author-id <author-id> \
  --independent-auditor-id <auditor-id>
```

The input must be a `claim-list.v1` document whose `reviewed_by` matches the independent auditor and whose `unmapped_propositions` is exactly `0`. The compiler rejects duplicate claims, self-review, invalid dispositions, unsafe paths, missing sources, and overwrites without `--replace`; it freezes every declared source hash in `claim-inventory.json`.

### Legacy locator migration is a separate fail-closed step

Historical claim lists often use unqualified paths, stale line ranges, or prose selectors. Before compiling them, run:

```bash
python3 scripts/propose_locator_migration.py \
  --package-root <course-package> \
  --output <course-package>/research/locator-migration-proposal.json
```

Only rows marked `AUTO-CANDIDATE` may be applied, and only after the proposal is bound to the reviewed claim list. `scripts/apply_locator_migration.py` refuses to write an inventory if any row is manual, missing, ambiguous, or outside the current file line range. Unique CSV/JSON selectors may be converted to typed selectors; a workspace prefix may be stripped only when the resulting file exists under an allowlisted root. `MANUAL-SELECTOR-REQUIRED`, `MISSING-SOURCE`, `LINE-RANGE-INVALID`, and any failed freshness/hash check remain pending auditor work. The migration output records the proposal and claim-list hashes, but it is not research evidence and cannot satisfy a Deep Research receipt, adjudication, or saturation gate.

## Full-scene research dimensions

For every claim, mark each applicable dimension `covered` or `not-applicable` with a reason:

1. terminology and system boundary;
2. conventional or non-AI baseline;
3. professional actor, workflow, artifact, decision right, and failure cost;
4. current AI/model/application behavior;
5. architecture, interfaces, state, data, and versioning;
6. metrics, statistics, population, slices, uncertainty, and threshold method;
7. implementation, repository, commands, configuration, and reproducibility;
8. failure modes, incidents, issues, counterexamples, and disconfirming evidence;
9. security, privacy, permissions, abuse, compliance, and human authority;
10. performance, latency, capacity, reliability, and cost;
11. operations, observability, rollback, waiver, and feedback;
12. tool/vendor alternatives and non-AI alternatives;
13. regional, language, organization, and environment variation;
14. learner prerequisite, action, diagnosis, reuse, and transfer evidence.

Not every dimension applies to every claim. `not-applicable` requires a concrete rationale; blank coverage is a failure.

## Required R0–R7 research loop

### R0: full coverage, classification, and routing (no network)

Freeze every page and every atomic claim before scheduling a provider request. Record the exact claim, claim type, risk, subject, predicate, population, environment, version/time boundary, vendor/tool, region/language, and what evidence could disprove it. Assign the primary cluster, evidence class, route, required dimensions, target-evidence requirement, and current status. `pages_expected`, `pages_with_claim_inventory`, and missing page IDs must be explicit; 103-page coverage is not proven by a 30-page inventory.

Route local repository/fixture/course/status facts to local validation, target-system or human/production claims to target evidence, and teaching claims to design or human evidence. Keep unknown, high-risk, or missing-field claims `BLOCKED`/`UNKNOWN-EXPLICIT`. Only eligible external technical facts and empirical generalizations proceed to R1.

### R1: canonical Deep Research breadth run

Run one dedicated ChatGPT/OpenAI Deep Research request for each approved canonical external anchor, not one request for every page member. Cover all applicable dimensions, Chinese and English terminology when relevant, primary evidence, implementation evidence, professional practice, failure evidence, and counterevidence. Save the anchor's exact request fingerprint, source families, scope, version/environment/population boundary, supports/cannot-support predicates, and evidence bundle reference.

The provider request is still atomic at the canonical anchor level. A member claim may reference the resulting packet only after a field-by-field transfer check. Shared source caching is allowed; shared conclusions, report paths, receipts, final dispositions, and saturation are not.

### R2: primary technical-document reconstruction

Reopen pivotal standards, papers, official documentation, repositories, release notes, issues, and specifications selected by the anchor run. Prefer official Markdown endpoints when provided. Otherwise create a normalized Markdown research note with:

- source title, publisher, URL, version/date, access date, and license/usage boundary;
- original heading hierarchy;
- definitions, fields, parameters, commands, tables, limits, deprecated behavior, and error semantics relevant to the claim;
- what the source supports and cannot support;
- compliant excerpts only; do not copy a copyrighted document in full when reuse is not permitted.

### R3: counterevidence and contradiction run

Use a separate Deep Research request for the canonical anchor when its risk, empirical scope, conflict, version drift, or decision importance requires it. Look for conflicting definitions, failed implementations, issue reports, negative results, alternative methods, boundary cases, and reasons the initial conclusion may not generalize. A member's transfer decision still records its own counterevidence and cannot-prove boundary.

### R4: gap-directed expansion

Generate new Deep Research requests only from unresolved coverage dimensions, contradictions, missing primary evidence, stale versions, or decision-changing unknowns. Each round records the gap, why it can change the decision, what new evidence was sought, and what changed. `NUMERIC-STATISTICAL`, `SECURITY-AUTHORITY`, `VENDOR-VERSION`, target, teaching, and production claims default to independent/delta research or blocking; a broad cluster report cannot satisfy them.

### R5: local verification

Run the repository validator, schema checks, fixture, clean-room command, projection check, or status/hash comparison named by the route. Store command, working directory, input/output hashes, version, result, owner, and limitation. A web source cannot prove that this repository ran, and a fixture cannot prove live provider, enterprise, practitioner, learner, or production behavior.

### R6: target evidence

Collect the target-system snapshot, real provider response, authorization/roles, production run, practitioner record, or learner evidence required by the claim. Store time boundary, owner, environment, sample/population, cleanup/rollback and readback. Missing target evidence is a blocker, not an invitation to use generic web research.

### R7: independent adjudication and projection

For every anchor and member, preserve applicable dimensions, supports/cannot-prove, contradictions, transfer/adjudication, final disposition, and projection locator. Only after the route-specific evidence is closed may the factory synthesize the topic and page.

## Independent contradiction and saturation compilation

The research author, Luna integrator, packet compiler, and page author may propose an adjudication but may not approve it. A distinct auditor creates `claim-research-adjudications.v1` with every anchor and member claim, referenced run or evidence IDs, exact dimension coverage, transfer decision, contradiction records, one material-change assessment per relevant round, final disposition, and rationale. `DIRECT-REUSE` is an evidence-origin decision, not a copied terminal verdict.

Compile the terminal artifacts with:

```bash
python3 scripts/finalize_claim_research.py \
  --package-root <course-package> \
  --topic-id <topic-id> \
  --adjudications-file <independent-adjudications.json>
```

The compiler requires route-complete evidence. A canonical external anchor requires a valid initial run plus the applicable counterevidence/gap-fill/verification, exact claim and dimension coverage, valid completed run ownership, two consecutive assessed rounds with `material_change=false` or a reasoned conclusive-primary-authority exception, and conservative treatment of unresolved contradictions. A member claim requires an independently audited transfer decision, its own applicable dimensions and cannot-prove boundary, and any required delta or target/local evidence; it does not require a duplicate provider receipt. The compiler generates `contradiction-matrix.md` and `research-saturation.json`; it does not call a model to invent a PASS.

## Saturation and stopping rule

Do not use the phrase "scientific, comprehensive, and effective" as a subjective approval. A canonical external packet is terminal only when:

- every applicable research dimension is covered or justified as not applicable;
- at least one dedicated initial Deep Research run and the required independent counterevidence or gap-fill Deep Research run completed;
- pivotal sources were opened, not merely cited by a model;
- source families are independent enough for the claim risk;
- definitions, versions, population, environment, units, uncertainty, and cannot-prove boundary are explicit;
- contradictions are adjudicated or preserved as unresolved;
- two consecutive rounds add no material evidence that changes the claim, scope, decision, or confidence, unless a conclusive primary authority makes further rounds unnecessary and an independent auditor records the exception;
- no unsupported numeric, causal, comparative, universal, or effectiveness claim remains;
- the final disposition is `SUPPORTED`, `SCOPED`, `UNKNOWN-EXPLICIT`, or `REJECTED`.

`UNKNOWN-EXPLICIT` and `REJECTED` are valid scientific outcomes. They cannot be rewritten into positive course claims.

A member claim is terminal only when its transfer/adjudication records prove that the packet's supports/cannot-prove predicates, scope, version, environment, population, region/language, vendor, risk, and applicable dimensions fit that member. Any changed or unknown field requires `SOURCE-REUSE-DELTA`, `NO-REUSE`, an independent route, or an explicit blocker. The member must retain its own final disposition and projection locator; anchor saturation is never sufficient by itself.

## Deep-research receipt contract

Every formal external run in `deep-research-receipts.json` records:

`run_id,claim_ids,round,phase,provider,surface,model_or_feature,response_or_export_id,started_at,completed_at,request_path,raw_response_path,report_path,citations_path,tool_calls_path,input_sha256,output_sha256,data_sources,tool_call_count,citation_count,opened_source_count,status,limitations`

Rules:

- the initial run contains exactly one canonical anchor `claim_id`; a member claim must reference the anchor through a packet and transfer decision, never by copying the receipt or `report_path`;
- `status=completed` requires existing non-empty request, response, report, citations, and tool-call files;
- `openai-responses-api` requires an exact model and response ID;
- `chatgpt-deep-research` requires the exact feature name and a stable conversation/export identifier;
- at least one of `web_search`, `file_search`, or `remote_mcp` must be present;
- missing raw output or provider identity is `NOT_PROVEN`, not completed research;
- for `openai-responses-api`, the validator re-parses `raw-response.json` and requires its response ID, model, status, generated report, citations, opened-source count, and tool calls to agree with the receipt and derived artifacts;
- a normal model answer, local agent summary, search snippet list, or hand-authored source pack is not a deep-research receipt.
- historical TD-T09 receipts remain byte-for-byte unchanged; a new packet mapping is a sidecar and cannot rewrite provider, surface, response/export ID, round, source counts, or saturation.

## Synthesis and Markdown production

Only after each claim's route-specific evidence reaches a terminal or explicitly blocked/unknown state may the factory update:

1. `source-pack.csv`;
2. `evidence-synthesis.md`;
3. `contradiction-matrix.md`;
4. `engineering-blueprint.md`;
5. `manuscript.md`;
6. learner-page canonical content;
7. `projection-ledger.json`.

Preserve the mapping:

`page_id -> claim_id -> evidence route/origin -> canonical packet or local/target/teaching evidence -> transfer/adjudication -> pivotal sources or artifact locators -> synthesis section -> manuscript locator -> learner-page target`

Formatting and editorial cleanup happen after route-specific adjudication. They may reorganize headings, tables, examples, and explanations; they may not widen scope, strengthen uncertainty, change numbers, remove limitations, or turn a local/target/teaching blocker into an external fact.

## Promotion gate

A page remains internal when any of these is true:

- a publishable proposition is missing from the claim inventory or page-to-claim projection;
- `unmapped_propositions != 0`, the 103-page coverage record has missing pages, or a classification overlay is stale/unapproved;
- any claim lacks a valid evidence route, applicable dimensions, transfer/adjudication record, and final disposition;
- an external canonical anchor lacks the required provider receipt, counterevidence/gap-fill, opened sources, or packet saturation;
- a reused member lacks a field-by-field transfer decision, its own cannot-prove boundary, or required delta/local/target evidence;
- a local claim lacks current artifact/hash/command evidence, a target claim lacks target snapshot/run/authorization evidence, or a teaching claim lacks explicit design/human evidence;
- a receipt lacks provider identity, model/feature, response/export ID, raw output, citations, or tool trajectory;
- any required research dimension is blank;
- saturation is asserted without the required evidence or independent auditor, or an anchor saturation verdict is copied to a member;
- a claim remains materially contradicted but the learner page presents one side as settled;
- an `UNKNOWN-EXPLICIT` or `REJECTED` claim is projected as a positive fact;
- the manuscript or learner page changed after the claim inventory and saturation hashes were recorded.

This gate proves research provenance and claim discipline. It does not prove learner comprehension, practitioner acceptance, live-model behavior, enterprise integration, or production effectiveness.
