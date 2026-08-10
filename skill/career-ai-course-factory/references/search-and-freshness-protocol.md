# Search Routing and Freshness Protocol

## Purpose

Prove that profession × AI recommendations come from a reproducible, current search process. Do not hard-code one search provider: first discover the retrieval surfaces available in the current runtime.

## Retrieval routing

Use the strongest in-scope surface available, and record each attempted route:

1. user-connected or internal resources when explicitly in scope;
2. local repositories, manifests, changelogs, documentation, fixtures, and runtime evidence;
3. live web search;
4. browser or direct platform navigation;
5. official documentation, release notes, standards, and primary repositories;
6. direct course, job, community, issue, talk, or postmortem pages.

Search tools discover leads. Open the selected source page before citing it. Search snippets, AI summaries, inaccessible pages, and copied aggregations never enter the source ledger as evidence.

If the request requires current information but no live route works, set the run status to `BLOCKED-FRESHNESS`, list attempted surfaces, and stop before course ranking. Model memory may generate query ideas, not current claims.

`run_scope=smoke` may test search behavior and one scenario, but it cannot validate a complete package or unlock course ranking. `run_scope=full` plus `run_status=complete` is required for a complete package. A freshness-required run cannot be complete unless at least one `is_live=true` surface has a recorded successful attempt and evidence.

## Required artifacts

### `research/search-plan.json`

Required fields:

```json
{
  "profession": "stable profession id",
  "generated_at": "ISO-8601 timestamp",
  "research_question": "profession × AI question",
  "freshness_required": true,
  "run_scope": "smoke|full",
  "available_surfaces": [{"surface_id": "surf-01", "surface": "live-web", "is_live": true, "status": "available", "attempted_at": "ISO-8601", "evidence": "opened URL or local log", "limits": "..."}],
  "query_families": [{"family": "role-reality", "languages": ["zh", "en"], "purpose": "..."}],
  "freshness_policy": [{"claim_type": "fast-changing technology", "max_age_days": 90}],
  "stop_conditions": ["BLOCKED-FRESHNESS when current claims cannot be verified"],
  "run_status": "planned|running|partial|complete|blocked"
}
```

### `research/search-log.csv`

Required columns:

`id,query,language,research_lane,surface_attempt_id,search_surface,run_at,result_count,selected_source_ids,opened_urls,exclusion_notes,status`

Use `status` values `selected`, `leads-only`, `no-usable-result`, or `blocked`. Log exact queries, not summaries. Preserve failed and noisy searches because they explain coverage gaps and query refinement.

## Query families

Run Chinese and English query families where both ecosystems matter:

- `role-reality`: responsibilities, artifacts, workflows, job requirements, standards;
- `latest-capability`: official releases, model/tool/framework capabilities, deprecations;
- `profession-ai-workflow`: profession + AI/LLM/RAG/Agent/evaluation/automation;
- `artifact-and-code`: repositories, example projects, datasets, templates, CI configs;
- `failure-and-counterevidence`: issues, postmortems, security failures, maintenance cost;
- `competitor-supply`: direct courses, tutorials, memberships, consulting offers;
- `adoption-and-demand`: jobs, skills, practitioner questions, buyer/user language;
- `privacy-and-governance`: data boundaries, standards, human review, prohibited use.

Do not stop after a broad query. Refine with profession terms, business systems, AI architecture, artifact types, and primary-source domain filters.

## Freshness policy

- Fast-changing model, agent, framework, or release claim: verify against a current official source; target 90 days when the source exposes dates, and always record version/access date.
- Current capability, job, adoption, or competitor claim: prioritize sources from the last 12 months.
- Practitioner pain, issue, and counterevidence: prioritize the last 24 months unless the failure is canonical and still applicable.
- Standard or durable method: verify the latest edition; older foundational material is allowed with `durable` or `historical` status.

If a source has no publication date, record access date and mark the date limitation. “Current” means current at the recorded access date, not permanently current.

## Technology radar

Create `research/technology-radar.json` with at least eight candidates for a full profession package. Required fields per item:

`technology_id,name,category,capability,ai_lane,official_source,version_or_release,last_verified,maturity,status,setup,limits,security,scenario_ids,course_ids,fallbacks,refresh_trigger,evidence_ids`

Allowed status: `current`, `watch`, `experimental`, `stale`, `deprecated`, `blocked`. Newest is not automatically best. Select technology only when it enables an observable business outcome and has a fallback or explicit dependency risk.

## Search completion gate

Before scenario ranking:

- at least eight exact queries are logged across five query families;
- both Chinese and English are represented when relevant;
- at least three retrieval surfaces or source channels are attempted;
- every search-log row references a declared `surface_attempt_id` with timestamp and evidence;
- all selected sources have opened URLs and source-ledger IDs;
- every `current` technology has an official source and verification date;
- unresolved freshness gaps are explicit and do not undermine the promised outcome.
