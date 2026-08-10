# AI-Native Profession Research Protocol

## Controlling question

> How is AI changing this profession's core work, what new quality problems does it create, and what can a learner run or inspect to prove a useful result?

Do not begin with generic workplace pain. Begin with the intersection of professional work and current AI capabilities, systems, agents, evaluation, and governance.

First run `search-and-freshness-protocol.md`, `multi-channel-evidence-protocol.md`, and `profession-decomposition-protocol.md`; then use `business-scenario-protocol.md` to convert evidence into scenarios. Source quotas do not replace a reproducible search log, source-family independence, profession map, or scenario triangulation.

## Required research lanes

For a new profession, cover all lanes:

1. **Role reality**: job descriptions, standards, professional bodies, public workflows, practitioner artifacts.
2. **AI-assisted work**: official model/tool docs and repositories showing how AI changes existing tasks.
3. **AI systems in the domain**: LLM, RAG, agent, multimodal, decision-support, or automation products the profession must build, test, use, or govern.
4. **Agentic workflow**: bounded planning, tool use, execution, healing, approval, and traceability loops.
5. **AI quality system**: datasets, evals, red teaming, CI/CD, observability, cost/latency, drift, privacy, and human review.
6. **Course competitors**: direct course/product pages across multiple platforms, not search snippets.
7. **Practitioner pain**: forums, issue trackers, talks, reviews, and postmortems; use for signals, not universal facts.
8. **Counterevidence**: brittleness, false confidence, security/privacy failures, maintenance cost, and tasks that remain human-only.

## Minimum coverage gate

Before discovery ranking, collect at least:

- 20 usable sources from at least 6 independent publishers;
- all seven channel classes in `channel-coverage.json`;
- 4 primary capability sources (official docs, standards, or primary repositories);
- 2 GitHub candidates from different owners, with metadata audits;
- 5 original job postings from at least 3 employers, deduplicated across ATS mirrors;
- 4 course competitors across 3 platforms;
- 3 practitioner/community or issue-tracker signals;
- 2 counterevidence/failure sources;
- Chinese and English sources when both ecosystems matter.

For a package claiming validated practical use, require at least one selected GitHub or public artifact to be pinned and run-verified, unless the exemplar has an independently verified offline implementation. Every source records access date, source type, platform, language, evidence tier, publisher group, source family, channel classes, use, and limitations. Search snippets and inaccessible pages are leads only.

## Competitor matrix

Create `research/competitor-matrix.csv` with:

`id,platform,offering,audience,promise,ai_lane,modules,hands_on_artifact,execution_proof,assessment,freshness,commercial_model,url,access_date,gap,claim_status`

Use `claim_status` values `observed`, `vendor-claim`, `inferred`, or `unknown`. Do not treat enrollment, marketing multipliers, or completion badges as outcome proof.

## AI capability map

Create `research/ai-capability-map.md` and cover all four AI lanes. For every candidate capability record:

- professional task and user;
- AI role;
- input and output;
- tool/model/framework evidence;
- professional failure modes;
- learner proof;
- privacy/security boundary;
- freshness trigger;
- course opportunity.

## Evidence labels

- **Fact**: directly supported by a primary or authoritative source.
- **Observed competitor feature**: visible on a direct offering page; not proof of learner outcome.
- **Practitioner signal**: role-specific report, issue, or discussion; not universal prevalence.
- **Consensus**: independent source clusters support the claim.
- **Vendor claim**: preserve attribution and do not use as efficacy proof.
- **Inference**: synthesis with reasoning shown.
- **Unknown**: unresolved; never present as a result.

## Source ledger

Required columns:

`id,title,creator,source_type,platform,language,year,url,access_date,evidence_tier,publisher_group,source_family_id,channel_ids,relevance,credibility,used_for,limitations`

Prefer official docs for current capability, repositories for executable behavior, standards for risk frameworks, direct course pages for competition, and community sources for pain wording and failure examples.

## Search completion test

Research is complete enough to design when:

- every high-priority course has at least one profession source and one AI capability source;
- every high-priority scenario has profession-workflow, AI-capability, and practice-artifact evidence classes;
- each major tool claim has a current primary source;
- every claimed market gap appears in the competitor matrix;
- at least one source challenges the recommended workflow;
- unknowns are explicit and do not undermine the course promise.
