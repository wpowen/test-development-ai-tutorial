# Multi-Channel Evidence Protocol

## Purpose

Use different channels because they answer different questions. A source count is not evidence diversity. Ten pages copied from one vendor are one information family.

## Seven mandatory channel classes

| Channel | It can support | It cannot prove |
| --- | --- | --- |
| `profession-authority` | responsibility, workflow, competency, regulated boundary | current tool effectiveness |
| `ai-primary` | current model/tool behavior, version, API, stated limitations | adoption or professional value |
| `github-artifact` | implementation shape, releases, issues, CI, license, reproducibility | business prevalence; stars are not efficacy |
| `practitioner-failure` | pain language, edge cases, maintenance burden, failure hypotheses | population frequency from one story |
| `market-demand` | hiring/procurement/adoption signals and requested capabilities | market size or learner outcome |
| `learner-supply` | existing promises, formats, gaps, questions and downloadable artifacts | course efficacy unless outcomes are measured |
| `counterevidence` | failure boundaries, security/privacy risk, non-AI alternatives | universal rejection of the capability |

Before course ranking, all seven classes must have an opened source, preserved query, access time, source-family identity, claim boundary, and limitation.

## Search order

1. Define one profession claim, one AI claim, one learner claim, and one counterclaim to test.
2. Search Chinese and English with profession synonyms, role variants, work artifacts, failure verbs, and current AI terms.
3. Search broad engines for discovery, then search the source surface directly.
4. Open the exact page; snippets, AI summaries, mirrors, and reposts remain leads.
5. Preserve `query -> opened URL -> source ID -> scenario claim -> course artifact`.
6. Search for disconfirming evidence before accepting a scenario.

## Query families

Use combinations, not one giant query:

- role reality: `(<role synonym>) (<artifact|workflow|responsibility>) (<standard|syllabus|job>)`;
- AI intersection: `(<role>) (<LLM|RAG|agent|multimodal|eval>) (<workflow|testing|automation>)`;
- GitHub: `site:github.com (<role task>) (<tool term>)`, then inspect repository, releases, issues, discussions, CI, and license;
- failure: `(<tool/system>) (<fails|regression|incident|hallucination|maintenance>)`;
- demand: `(<role>) (<AI capability>) (<job|hiring|RFP|case study>)`;
- learner supply: `(<role>) (<AI>) (<course|tutorial|实战|训练营>)` plus platform-native search;
- counterfactual: `(<task>) (<without AI|manual baseline|limitations|security|privacy>)`.

## Independence and triangulation

Record `publisher_group`, `source_family_id`, and `channel_ids` for every source.

- Same publisher, copied press release, translated mirror, syndication, and a vendor's docs plus its own blog are not independent confirmation.
- No single publisher group or source family may supply more than 25% of a full source ledger; filler families do not cure a dominant-source research design.
- A high-priority scenario needs at least three publisher groups and three source families across profession reality, AI capability, and practice/failure evidence.
- A recurring pain claim needs either three independent practitioner/failure signals or one authoritative measurement. Otherwise label it `practitioner-signal`, not `consensus`.
- A demand claim needs at least two independent demand signals and one countercheck. Job postings show requested capability, not market size.
- A competitor gap must be observed on direct offering pages; missing public evidence is `unknown`, not “competitor lacks it”.

## GitHub artifact audit

Create `research/github-artifacts.csv`. For each candidate record:

- repository and source ID;
- exact tag or commit;
- license;
- last commit and latest release;
- issue/discussion URLs and recent unresolved failure themes;
- CI workflow/status URL;
- setup and smoke commands;
- `metadata-only|clone-failed|run-failed|run-verified`;
- run time, exit code, saved evidence path, environment, and limitation;
- whether the repository is selected for a learner lab.

`metadata-only` may support discovery. It cannot support “可运行” or “实测”. Any repository selected for the default lab must be pinned and `run-verified`, or the course must use a separately verified offline adapter.

For `run-verified`, preserve structured JSON under `research/github-runs/` with the exact repository URL, audited commit, checked-out HEAD, setup/smoke commands, run time, environment, stdout/stderr, exit code, and limits. Do not point the evidence field at an unrelated report.

## Forum and learner-signal handling

Create `research/learner-signals.csv`. Preserve direct observation separately from interpretation. Engagement counts are platform-scoped popularity signals, not demand or learning proof. Comments and issues should be coded by task, desired outcome, failure, role, and context, then clustered by independent publisher group.

## Required machine-readable outputs

- `research/channel-coverage.json`: channel purpose, query IDs, source IDs, claim boundary, status, limitations;
- `research/github-artifacts.csv`: repository audit and execution status;
- `research/learner-signals.csv`: course/community/job observations with claim labels;
- existing `source-ledger.csv`, `search-log.csv`, and scenario evidence maps.

## Fail-closed conditions

Stop ranking or downgrade the claim when:

- any mandatory channel is missing;
- a selected source was not opened;
- a channel cites a blocked query, or its source was selected by some other query but not by the query bound to that channel;
- a scenario's three evidence classes collapse to fewer than three independent source families;
- a GitHub dependency selected for a lab is not pinned and run-verified;
- one forum post is presented as prevalence;
- popularity, stars, enrollment, or vendor metrics are presented as learner efficacy;
- the named creator/account cannot be reliably identified.
