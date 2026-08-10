# TD-AP04 · Trace and data schema

## Research brief

Question: what telemetry lets an engineer explain one slow or incorrect Agent task? Artifact: task-rooted Trace and storage schema with privacy policy.

## Source pack

- OTel GenAI conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/ and registry https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/ — standard operations/attributes; conventions remain in development.
- OpenAI Agents tracing: https://openai.github.io/openai-agents-python/tracing/ — generation, tool, handoff and guardrail traces.
- OTel 2026 GenAI observability: https://opentelemetry.io/blog/2026/genai-observability/ — agent root and child-span pattern.

## Evidence synthesis

Standard fields cover model, operation, tool and token basics. There is no stable universal field set for task verifier, retry attempt, queue wait, cost, branch and handoff attribution. Do not invent new `gen_ai.*`; use `app.*` extensions and lock the semconv version.

## Engineering blueprint

Root `invoke_agent`/application workflow span; child generation, retrieval, tool, handoff and state spans. Metrics stay low-cardinality; Trace carries task-level dimensions. Compute wall-clock critical path rather than summing parallel children. Redact content by default.

## Manuscript map

TD-AP04 includes span tree, signal responsibility, minimum tables, critical-path diagnosis and privacy controls.

## Editorial review

PASS. Protected the cited OpenTelemetry semantic-convention status and separated standard `gen_ai.*` fields from application extensions. Kept wall-clock critical-path analysis instead of adding parallel child durations. The page does not ask learners to log prompts, credentials or PII by default, and it preserves sampling, retention and access controls.

## Validation

PASS: standard and custom fields are separated; evolving semantics and privacy are explicit.
