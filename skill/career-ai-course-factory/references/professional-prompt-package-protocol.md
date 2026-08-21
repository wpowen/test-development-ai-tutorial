# Professional prompt package protocol

## Directory and manifest

Use a stable directory such as `prompt-package/` containing `manifest.json`, `eval.json`, `mutation.json`, raw outputs, scorer/config, and run receipts. The manifest records `package_id`, version, purpose, authority, template/input/output hashes, model/provider/version, parameters/seed, tools and permissions, privacy level, eval set, expected statuses, stop states, review owner, limitations, and superseded package.

## State machine

Run outputs retain status and raw bytes. Valid transitions include `NOT_RUN → PASS_SCHEMA → PASS_SEMANTIC` or `FAIL`; `SCHEMA_INVALID` may retry with receipt; `REFUSED` preserves reason; `INCOMPLETE` marks truncation/timeout; `SOURCE_CONFLICT`, `UNSUPPORTED_RULE`, and `SEMANTIC_UNKNOWN` require review; `BLOCKED` stops downstream. None may be normalized into an empty success.

## Evaluation and receipts

Eval cases cover positive, boundary, conflict, missing, unauthorized, refusal, truncation, and paraphrase/locale variants. Each case records input hash, expected status, oracle type, assertion/threshold, risk, result, scorer version, and evidence. A run receipt records environment, model/prompt/tool versions, retries, timestamps, logs, raw output hashes, limitations, and residual risk. Model self-judgment is not an independent oracle.

A model-integrated claim requires a real provider/model/version, at least two repeated runs, one preserved raw-output hash per run, scorer version, parameter manifest, cost/latency, and explicit refusal, truncation, prompt-injection, locale, and long-context coverage. `provider=none`, an offline deterministic adapter, or generated prose remains `NOT_RUN` for the model lane.

## Mutation and human review

Mutation/fault cases include loosened constraints, removed source refs, wrong status/permission oracle, swallowed errors, skipped conditions, and retry-result loss. Record expected/actual status, killed/survived/no-coverage/timeout, repair, and residual risk. Human review questions cover unsupported claims, consequential decisions, conflicts, and release authority; unresolved blockers prevent maturity or publication.
