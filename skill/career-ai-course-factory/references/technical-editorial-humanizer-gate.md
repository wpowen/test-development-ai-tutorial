# Technical editorial and humanizer gate

Apply this gate after research, engineering design, examples, commands, and evidence boundaries are complete. It changes expression only. It must not add or remove facts.

## 1. Freeze technical content

Before editing, inventory and protect:

- claims, causal relationships, uncertainty, and source attribution;
- commands, code, parameters, paths, API names, schemas, and field names;
- versions, dates, thresholds, counts, units, comparison operators, and exit codes;
- prerequisites, limits, exclusions, failure behavior, permissions, and security constraints;
- citations, URLs, source IDs, evidence status, and validation gaps.

If any protected item must change, return to technical review. Do not hide a technical change inside a prose cleanup.

## 2. Require useful sentence content

Each explanatory section should name at least three of these when relevant:

- professional actor;
- trigger or condition;
- action or decision;
- input or artifact;
- observable result;
- failure consequence;
- evidence or source;
- downstream consumer.

Delete a paragraph when it only promises that the page is important, complete, systematic, easy, or valuable. Replace vague transitions with the actual next action.

## 3. Reject template language

Delivered learner pages must not rely on repeated generic headings or paragraphs such as:

- “本页完成后” and “你会带走” billboards;
- “先把真实问题说清楚”;
- “按证据顺序完成工作流”;
- “在最小业务场景里亲手做一次”;
- “迁移到你的项目”;
- “轮到你动手”;
- “值得注意的是”, “让我们”, “你会发现”, or “相信你已经”;
- unsupported “业内普遍认为”, “最佳实践”, “显著提升”, “全面掌握”, or “轻松上手”.

Use a repeated viewer component only for stable metadata such as evidence status, source links, prerequisites, and completion checks. Learner-facing explanations and section headings must be written for the specific professional problem.

## 4. Preserve useful structure

Do not remove a list merely because it has three items. Keep lists when each item has distinct technical meaning, such as preconditions, actions, and expected results. Remove ornamental parallelism that repeats one idea with different adjectives.

Prefer direct technical wording:

- name the subject and action;
- keep one causal claim per sentence when possible;
- state the condition before the consequence;
- use an exact field, command, or example instead of a motivational sentence;
- state `unknown`, `blocked`, `not run`, or `not validated` explicitly.

## 5. Two-pass review

### Technical fidelity pass

Compare the edited page with the evidence synthesis and protected-item inventory. Require:

- 100% field, command, number, boundary, and citation preservation;
- zero new unsupported facts;
- zero weakened conditions or uncertainty;
- every pivotal claim mapped to a source or labelled engineering synthesis;
- every exercise mapped to an observable artifact or result.

### Editorial pass

Check:

- no repeated generic prose across delivered pages;
- no promotional or chatbot phrasing;
- no vague attribution;
- no conclusion that merely tells the learner the topic is useful;
- headings describe the actual professional action or decision;
- paragraphs remain readable without hiding technical constraints.

## 6. Research-package record

Each promised topic must add `## Editorial review` to its research package and record:

- protected technical items checked;
- generic/template phrase scan;
- facts, inference, and unknowns preserved;
- commands and examples re-run or linked to execution evidence;
- reviewer score and unresolved issues.

The page's `promotion-receipt.json` records the editorial score, boundary-preservation score, current executability-audit hash, exact fourteen-file research inventory including claim-level Deep Research receipts and `projection-ledger.json`, and learner-material hashes. It is a promotion receipt, not permission to rewrite the protected-item inventory. Any protected-item change returns to technical review and must not be hidden by regenerating hashes.

Publication requires all hard gates plus an editorial score of at least 90/100, with full marks for boundary preservation. A lower score keeps the page `outlined`.

The governing rule is: expression may become shorter; information cannot become smaller, and the applicability boundary cannot become wider.
