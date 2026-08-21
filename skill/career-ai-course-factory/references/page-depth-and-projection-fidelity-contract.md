# Page depth and research→page projection fidelity contract

## Why this contract exists

The package already protects **user source → course package** with atom-level fidelity
(`source-assimilation-and-information-fidelity-contract.md`). It had **no equivalent
protection for the next hop**: `research package → learner-facing page`.

That gap produced a measurable failure mode. In a validated 102-page release:

| Layer | Depth |
| --- | --- |
| Per-topic `manuscript.md` | ~3000 CJK characters, gate ≥ 1200 |
| Delivered learner page | **median 1287 CJK characters, minimum 935** |
| Content gate | `JSON.stringify(page.blocks).length < 750` — counts JSON syntax |

Every gate was green. The research existed. It simply never reached the page.

A second gap compounded it: the anti-template rule is enforced as a **fixed blocklist of
literal phrases**. It catches the phrases from one retired template and nothing else. A new
per-module builder that repeats its own generic sentences across ten pages passes untouched.

A third gap: the editorial score that authorizes promotion is produced by the same
generation chain that wrote the page. The package's own axiom is *the system under test
cannot approve itself* — but page quality was the one place it self-approved.

## 1. Projection fidelity (research → page)

Every promoted page must have a `research/topics/<topic-id>/projection-ledger.json` proving
which parts of its own research package reached the learner page.
Validate the artifact with `assets/schemas/page-projection-ledger.schema.json` and include
it in the exact fourteen-file promotion inventory.

```json
{
  "topic_id": "<id>",
  "manuscript_sha256": "sha256:...",
  "page_content_sha256": "sha256:...",
  "claims": [
    {
      "claim_id": "C-01",
      "manuscript_locator": "manuscript.md#L40-L58",
      "meaning": "<protected meaning, one sentence>",
      "kind": "decision-rule | judgement-table | counterexample | failure-mode | metric-definition | threshold | boundary | artifact",
      "disposition": "projected | condensed | deferred | rejected",
      "page_target": "<page-id>#<block-title>",
      "rationale": "<required when condensed/deferred/rejected>"
    }
  ],
  "counts": {"total": 0, "projected": 0, "condensed": 0, "deferred": 0, "rejected": 0, "unaccounted": 0},
  "reviewer": "<name/role>",
  "verdict": "PASS | FAIL"
}
```

**Rules**

1. Every claim of kind `decision-rule`, `judgement-table`, `counterexample`, `failure-mode`,
   `metric-definition` or `boundary` must be `projected` or `condensed`. `deferred` and
   `rejected` are only valid for `threshold` and `artifact` kinds, and require a rationale
   plus a named owner.
2. `unaccounted` must be `0`. "Covered elsewhere" is not a disposition.
3. `condensed` requires that the protected meaning survives; dropping a constraint,
   counterexample, uncertainty, or decision boundary is `FAIL`, not condensation.
4. A page whose projection ledger is missing or `FAIL` stays `outlined`.

**This is the gate that would have caught the 1287-character page.** A manuscript with a
five-row decision table and three counterexamples cannot project into a page that carries
neither.

## 2. Page depth (structural, not cosmetic)

Depth is measured in **CJK characters of learner-facing prose** (`summary`, `why`, block
bodies, bullets, expected, warning), never in serialized JSON length.

| Page type | Minimum learner prose | Rationale |
| --- | ---: | --- |
| `concept` / 概念 | 3000 | must carry mental model + counterexample + boundary |
| `diagnostic` / 诊断 | 3500 | must carry a symptom→layer→next-check tree |
| `guided-lab` / 跟做 | 4000 | must carry runnable steps + expected + failure diagnosis |
| `project` / 项目 | 4000 | same, plus transfer conditions |
| `reference` | 2000 | lookup surface, lower narrative load |

**Required structural elements per delivered page** (each machine-checkable):

```
□ ≥ 1 judgement table   —— 「如果…则…」或「症状→层→下一步」，这是方法论与教程的分界线
□ ≥ 2 counterexamples   —— 且说明「为什么它看起来是对的」
□ ≥ 4 diagnosis rows    —— 症状 → 可能层 → 下一步检查
□ ≥ 1 page-specific material —— href 不得与同模块其它页完全相同
□ ≥ 1 plain-language model  —— 首次出现的术语必须有一句话解释或链接
□ evidence boundary with an explicit NOT_RUN list
```

**Staged adoption.** Do not raise the gate to the target value in one step; that turns an
entire validated release red and blocks publication. Required procedure:

1. Set the gate to the current measured **P25** so the release cannot regress.
2. Each time a module completes enrichment, raise the gate to the lowest value among
   completed modules.
3. Only when every module is complete, raise to the table above.
4. Record each raise with date, previous value, new value, and the modules that motivated it.

## 3. Cross-page originality (replaces the phrase blocklist)

A fixed list of banned phrases cannot survive a new template. Enforce **measured
duplication** instead.

```
For each module, compare every delivered page's learner prose sentence-by-sentence
against every other page in the same module.

  sentence_duplication_rate = duplicated sentences / total sentences

FAIL when sentence_duplication_rate > 0.20 for any page.
```

Shared **metadata** components (evidence status, prerequisite lists, source links,
completion-check scaffolding) are exempt and must be declared in
`research/shared-components.json`. Anything not declared there counts toward the rate.

Keep the literal blocklist as a cheap pre-filter, but never as the only defense.

## 4. Independent depth review

The editorial score that authorizes promotion must not be produced by the chain that wrote
the page. Required separation:

| Role | May do | May not do |
| --- | --- | --- |
| Author pass | write page, self-check against this contract | assign the promoting score |
| Depth reviewer | measure depth, duplication, projection ledger; assign score | rewrite the page |
| Owner | accept or reject residual gaps | overwrite a FAIL into PASS |

When independent subagents are unavailable, run a **separated pass with a different
prompt, a different input set (page only, no manuscript), and a recorded reviewer id**.
An author-assigned score with no reviewer id is not a promotion receipt.

## 5. Dimension-level depth (new)

A learner-facing page is a **teaching surface**, not a reference manual. When a topic family
carries a large professional method (an 8-domain architecture, a benchmark pipeline, a
career ladder), the pages must be backed by a **dimension document set** in the package:

```
methodology/dimensions/<dimension-id>/
├── 00-<research and adjudication>.md   # why this dimension needs its own method
├── 01..NN-<per-sub-domain>.md          # one per sub-domain, with tables and counterexamples
└── <evidence boundary>.md              # maturity, NOT_RUN list, numeric discipline
```

Each dimension document must separate **source observation** (has a citation, used only to
prove the problem exists and its magnitude) from **structural placeholder** (no citation,
shows the shape of a judgement, must be recalibrated). Mixing them is the most common way a
benchmark number becomes someone's production threshold.

The page then projects the dimension set; the projection ledger of §1 covers that hop too.

## 6. Failure conditions

```
FAIL  projection-ledger.json missing, FAIL, or with unaccounted > 0
FAIL  a decision-rule / judgement-table / counterexample / failure-mode / metric-definition
      / boundary claim disposed as deferred or rejected
FAIL  delivered page below the current staged depth gate
FAIL  delivered page with zero judgement tables
FAIL  sentence duplication rate > 0.20 within a module, outside declared shared components
FAIL  promoting editorial score with no independent reviewer id
FAIL  a numeric threshold presented without a source-observation / structural-placeholder label
FAIL  a dead page template left in the codebase that new authors can pick up
```

## 7. Relationship to existing contracts

| Contract | Covers | This contract adds |
| --- | --- | --- |
| `source-assimilation-and-information-fidelity-contract.md` | user source → package | package research → **page** |
| `technical-editorial-humanizer-gate.md` | expression quality, phrase blocklist | measured duplication, independent reviewer |
| `beginner-comprehension-and-direct-reuse-contract.md` | which 14 elements a lesson needs | which of them are **machine-checkable**, and their minimums |
| `catalog-promotion-and-publication-integrity-contract.md` | exact research inventory, receipts | depth and projection as promotion preconditions |

This contract does not relax any existing gate. It closes the hop none of them covered.
