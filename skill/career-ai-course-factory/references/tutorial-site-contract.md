# Tutorial Site Contract

## Purpose

The learner-facing product is a navigable tutorial system, not a book manuscript, report, slide deck, JSON dashboard, or one long lesson document. Use the interaction model of beginner tutorial sites: a persistent course tree, one problem per page, plain explanations, examples, practice, checks, and clear progression.

Do not copy another site's visual design, wording, or proprietary content. Reuse only high-level educational mechanisms.

## Required outputs

```text
tutorial/
├── README.md                  # course promise and how to use the tutorial
├── course-tree.md             # human-readable modules, pages, prerequisites, status
├── page-template.md           # canonical page contract
├── tutorial-site.json         # stable machine-readable navigation and page metadata
└── index.html                 # self-contained local tutorial viewer
```

The HTML must open directly without a server. It must not depend on remote JavaScript, CSS, fonts, APIs, or hidden credentials.

## Knowledge-tree design

Build pages from knowledge dependencies, not tool names. Trace:

`profession outcome -> business scenario -> learner action -> required concept -> prerequisite -> tutorial page -> learner artifact -> verification`.

The internal knowledge tree must include:

- at least 4 modules;
- at least 15 pages for a full profession tutorial;
- stable `page_id`, slug, title, page type, level, prerequisite IDs, scenario IDs, learner result, artifact, evidence status, delivery status, and updated date;
- no prerequisite cycles;
- every non-foundation page reachable from a beginner entry page;
- exactly one primary next page for the default route.

The internal tree may contain `planned`, `outlined`, and `blocked` records so curriculum gaps remain visible to maintainers. These records must not be serialized into any learner-facing navigation, HTML payload, public JSON, sitemap, search index, or release archive. A title in an internal tree is not a delivered tutorial page.

The public projection must also be covered by `research/solution-architecture.json` as defined in `complete-solution-contract.md`. Page-level architecture is necessary but insufficient: every public page belongs to a pilot or public solution unit with complete design, exact traceability, owned decisions, acceptance gates, and evidence maturity that meets the publication level. A navigation tree cannot substitute for a deployment view, threat model, operational design, rollback path, or execution receipt.

## Minimum distributable learning path

A complete knowledge tree is not yet a distributable product. Before a public or paid release, require at least one end-to-end learner path that:

- starts from a beginner entry page rather than a showcase lesson;
- contains at least 8 delivered pages with no planned prerequisite;
- ends in one profession-relevant artifact that has been run or otherwise verified;
- includes concept, data/oracle design, guided execution, diagnosis, repair, and transfer;
- has a route manifest that controls the default page and next/previous path;
- exposes the same page IDs, statuses, sources, and evidence boundary in every publication target.
- links every named script, config, dataset, prompt file, pipeline, dashboard or runbook to a real repository-owned file.
- contains a substantive architecture or workflow diagram and an executable profession-specific SOP on every public page.

Every delivered page on that path must have at least 4 substantive teaching blocks, 3 observable outcomes, 3 learner actions, 3 completion checks, source notes, a non-trivial evidence boundary, a meaningful five-node architecture/workflow diagram, and at least one repository-owned handoff material. A guided lab must include exact input or commands and observable expected results. A fixture-tested guided lab must link a real script plus at least one tested fixture/config/evidence file, contain at least two runnable/observable steps, and retain its execution evidence.

Page and module IDs are exact keys, not loose prefixes. Course grouping, support-material injection, public-status promotion, prerequisites, and navigation must use exact membership or anchored patterns. Validate a prefix-collision fixture so a new specialization ID cannot silently inherit another track's materials, architecture, or completion status.

Do not publicly label the full profession tutorial complete while only the first path is delivered. Preserve the full knowledge tree internally and publish only the validated path or subset.

## Release-scope contract

Every generated tutorial and release manifest must declare one release scope. Scope is a machine-checkable promise, not marketing copy.

- `pilot-path`: only a validated subset of the internal catalog is public. Other catalog entries may remain incomplete internally, but are absent from every learner-facing artifact.
- `complete-catalog`: every page in the declared catalog is promised as delivered. `planned`, `outlined`, `blocked`, navigation-only, or section-plan-only pages are forbidden.

The manifest records `mode`, `promised_page_ids`, `catalog_complete`, and `validated_at`. For every public release, `promised_page_ids` must exactly equal the public page-ID set. Validators must fail when a public page is missing, incomplete, unpromised, has unresolved prerequisites, lacks required teaching blocks/actions/checks/sources, or is absent from a publication target. Public modules with no public page are forbidden. For `complete-catalog`, the public page set must also equal the internal catalog and `catalog_complete` must be true.

The assembled release also includes `SOLUTION-MANIFEST.json`, a public-safe projection of the canonical complete-solution contract. It records the exact pages covered by each solution unit, separate design/execution/review/publication maturity, all six architecture-view kinds, acceptance status, execution-receipt paths, and residual-risk count. `RELEASE-MANIFEST.json` pins its hash. Every public page must be covered by a pilot or public solution unit; a release without this closure fails even when its HTML builds.

Use `catalog-promotion-and-publication-integrity-contract.md` for the machine gate. The internal catalog must come from one ordered `research/catalog-manifest.json`; a complete catalog is an exact ordered equality check, not a minimum page count. A public-set shrink requires an approved scope-change record. Every public page also needs its own promotion receipt and a current executability `PASS` with zero findings.

Content completeness and evidence strength are independent. A `desk-researched` page can be complete instructional content while still being unverified in production; the interface must preserve that evidence boundary. Never upgrade `desk-researched` to `fixture-tested`, `live-tested`, or `practitioner-reviewed` merely because the page is fully written.

Reject words such as “完整课程”, “全量”, “全部完成”, or equivalent public claims whenever the release-scope gate does not pass. A page title, outline, JSON record, or navigation item never counts as completed instruction.

## Single-source publishing

GitHub and OpenAI Sites are publication targets, not separate course authoring surfaces. Keep one canonical content model and generate both targets from the same validated commit.

- GitHub provides the versioned source, reusable materials, labs, issues, and release history.
- OpenAI Sites provides the learner-facing tutorial experience and may be private during review.
- Generated HTML, navigation manifests, and release summaries must not become independent manually edited truth.
- Public outputs include only sanitized tutorials, fixtures, source notes, and declared evidence. Keep credentials, production data, private research notes, and unapproved reviews out of public artifacts.
- Record `content_version`, source commit, build ID, content hash, validation verdict, and publication targets in each release manifest.
- Pin the public catalog, promotion, executability, and artifact-closure manifest hashes in `RELEASE-MANIFEST.json`.
- The final public archive records the exact ordered public page IDs and learner-artifact roots. Recompute the content hash after assembly, then validate the assembled archive. Validating the authoring package alone is insufficient.
- For every learner-material link, compare the authoring source, static-export file, and ZIP member against one declared SHA-256 value; missing, extra, unsafe, or divergent archive members fail.
- Keep the internal authoring package, planned curriculum records, private topic backlog, and maintainer-only research outside public distribution archives. Publish only validated tutorial data, learner pages, sanitized evidence, labs, and the reusable Skill implementation.

## Five page types

### Concept page

Answers: “What is this, and why does it matter to my work?”

Required blocks:

- one-sentence definition;
- work-relevant analogy;
- simple structure or flow;
- vocabulary;
- smallest example and counterexample;
- knowledge check;
- summary.

### Guided lab page

Answers: “How do I complete this once from zero?”

Required blocks:

- prerequisite and time;
- business context;
- prepared input;
- exact steps or commands;
- expected output after each meaningful step;
- failure injection;
- repair/reset;
- downloadable or copyable artifact;
- completion checklist.

### Diagnostic page

Answers: “Why did it fail, and how do I locate the cause?”

Required blocks:

- observable symptoms;
- decision tree or ordered checks;
- common root causes;
- misleading fixes and counterexamples;
- repair and regression check;
- escalation boundary.

### Reference page

Answers: “What does this field, metric, setting, or adapter mean?”

Required blocks:

- definitions and comparison table;
- valid values or decision rules;
- version/date;
- limits and fallback;
- primary sources.

### Project page

Answers: “Can I complete a real professional task independently?”

Required blocks:

- business brief;
- inputs and constraints;
- required deliverables;
- baseline/failure/repair evidence;
- scoring rubric;
- transfer challenge;
- human review gate;
- evidence status.

## Every delivered page must show

1. Where the learner is in the course tree.
2. What the learner will be able to do.
3. Prerequisite pages.
4. Why the page matters to the profession.
5. A plain-language explanation before jargon.
6. A smallest useful example.
7. A learner action, not only reading.
8. Expected observable result.
9. Common errors or counterexample.
10. A completion check.
11. Previous and next page.
12. Updated date and evidence status.

## Viewer requirements

`tutorial/index.html` must provide:

- persistent grouped left navigation;
- active page and module indication;
- central tutorial content;
- in-page table of contents on wide screens;
- search over page titles and keywords;
- previous/next navigation based on the course tree, not publication chronology;
- copy buttons for commands and reusable snippets;
- local completion checkboxes and progress indicator;
- responsive mobile navigation;
- visible `desk-researched`, `fixture-tested`, `live-tested`, and `practitioner-reviewed` labels;
- an evidence boundary block on every delivered lab or project page.

Do not publish incomplete pages. Keep their learning goal, dependency, owner, and status in internal curriculum artifacts until every publication gate passes.

## Research-to-page traceability

Each delivered page records `source_ids` and `scenario_ids` in `tutorial-site.json`. The human page shows concise source notes, while detailed provenance remains in the research ledger.

A page can have these internal production and evidence states:

- `planned`: title and role in the tree only;
- `outlined`: outcome, prerequisites, page type, and section plan;
- `desk-researched`: content supported by opened sources but not run;
- `fixture-tested`: included lab passed on a deterministic fixture;
- `live-tested`: current external system or model was run;
- `practitioner-reviewed`: a relevant practitioner reviewed the page and task;
- `production-validated`: evidence comes from a real production workflow.

Only `desk-researched`, `fixture-tested`, `live-tested`, `practitioner-reviewed`, and `production-validated` pages may enter the public tutorial. Evidence strength remains visible and must not be inflated.

## Fail-closed rules

Reject a complete tutorial package when:

- it only provides documents and no navigable tutorial viewer;
- the navigation is a flat list without modules or prerequisites;
- pages are organized primarily by tool brand;
- one page tries to teach multiple independent job results;
- a delivered page lacks learner action, expected result, common error, or completion check;
- a public artifact contains a planned, outlined, blocked, navigation-only, or section-plan-only page;
- a public module has no public page;
- public page IDs do not exactly equal `promised_page_ids`;
- a lab has no failure injection or reset path;
- previous/next links ignore prerequisite order;
- the HTML requires a dev server or remote dependency;
- research sources cannot be traced to scenarios and delivered pages.
- release scope is missing, a promised page is not delivered, or a `complete-catalog` release contains any incomplete page;
- public completeness claims disagree with the validated release scope.
- the assembled public release contains an internal authoring tree, incomplete course record, extra navigation/search page, placeholder copy, cross-target page-ID drift, or content hash mismatch;
- the release manifest omits ordered promised page IDs, learner-artifact roots, validation verdict, content hash, or publication targets.
