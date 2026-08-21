# Codex Research Execution Contract

## Purpose

Provide a fail-closed, auditable research surface when the user explicitly selects Codex-native research instead of an OpenAI/ChatGPT Deep Research provider run. Codex research is a multi-agent orchestration receipt; it must never be labelled as OpenAI Deep Research.

## Explicit selection

The claim inventory must declare exactly one execution contract:

```json
{"execution_contract": "codex-research.v1"}
```

Missing selection defaults to `openai-deep-research.v1` for backward compatibility. A topic may not combine the two receipt types to borrow maturity.

## Runtime-observed trace

Every run supplies a `codex-runtime-trace.v1` object with:

- one run, topic, atomic claim, phase and round;
- a runtime-observed orchestrator identity, session and trace ID;
- runtime-observed agent identity, role, parent invocation, runtime, session, independence group, prompt hash, visible-context hash, input-artifact hashes and output hash;
- explicit artifact-read and source-open events;
- citations mapped to an opening-event ID from the same agent and URL;
- one integrator, which is excluded from independent evidence counts;
- limitations and terminal status.
- a runtime-issued RSA-SHA256 attestation over the canonical trace payload. The compiler verifies it against a separately configured trusted public key and records the trust-root hash in the receipt.

An agent label or author-written name is not identity evidence. A citation, search result, or source URL is not an opening event. Caller-authored `runtime_observed_*` fields without a valid signature are rejected.

## Independence rules

- `initial-research` contains exactly one claim and at least two evidence agents.
- Initial evidence agents use distinct runtime identities, sessions, independence groups and visible-context hashes and cannot read one another's output.
- `counterevidence` uses fresh agents, sessions and contexts; it may read the frozen claim inventory and original sources, but not a prior report, synthesis, contradiction matrix, adjudication or saturation artifact.
- Gap-fill and verification runs remain claim-scoped and preserve their input/output hashes.
- Integrators and adjudicators never count as independent evidence agents.

## Artifacts

The compiler writes:

```text
research/topics/<topic-id>/
├── codex-research-receipts.json
├── codex-contradiction-matrix.md
├── codex-research-saturation.json
└── codex-research/<run-id>/
    ├── raw-trace.json
    ├── agent-trace.json
    ├── source-openings.json
    └── citations.json
```

Use:

```bash
python3 scripts/compile_codex_research.py \
  --package-root <course-package> \
  --topic-id <topic-id> \
  --claim-id <claim-id> \
  --phase initial-research \
  --round 1 \
  --trace-file <runtime-trace.json> \
  --attestation-public-key <trusted-runtime-public-key.pem>

python3 scripts/finalize_codex_research.py \
  --package-root <course-package> \
  --topic-id <topic-id> \
  --adjudications-file <independent-adjudications.json>

python3 scripts/validate_codex_research.py \
  --package-root <course-package> \
  --topic-id <topic-id>
```

## Saturation and status

Saturation requires initial research, fresh counterevidence or gap-fill, full dimension coverage, source openings, contradiction adjudication, and two consecutive no-material-change rounds or a documented conclusive-primary-authority exception. Repeated output from the same agent, context or source set is not saturation.

Successful Codex research records:

```yaml
research_status: PASS-CODEX-RESEARCH
deep_research_status: BLOCKED-DEEP-RESEARCH
```

It does not prove learner comprehension, practitioner acceptance, live model behavior, integration or production effectiveness.

## Stop conditions

Stop with `BLOCKED-CODEX-RESEARCH` when identity, cryptographic runtime attestation, configured trust root, context, trace, hash, source-open mapping, fresh counterevidence, independent auditor, contradiction handling or saturation evidence is missing or inconsistent. Counterevidence may read only the frozen claim inventory and declared original sources; reading any prior `codex-research/<run-id>/` artifact is a hard failure.
