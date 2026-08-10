# TD-AP06 · Executable load-test SOP

## Research brief

Question: can the learner run a baseline, expose a retry storm and prove repair? Artifact: summaries and JSONL traces with 0/1/0 exit evidence.

## Source pack

- Google SRE cascading failures: https://sre.google/sre-book/addressing-cascading-failures/ — queues and retries as overload amplifiers.
- OpenAI rate limits: https://developers.openai.com/api/docs/guides/rate-limits — Retry-After, bounded retries and exponential backoff with jitter.
- The local fixture is original executable evidence; it does not establish production performance.

## Evidence synthesis

Fault injection must produce an observable red result. A retry storm may preserve final success while destroying latency and goodput, so the gate must include amplification and queue metrics.

## Engineering blueprint

The standard-library simulator uses open arrivals, bounded workers, deterministic model/tool steps and fixed seed. It writes one trace per task and gates success, p95 E2E, p95 queue, retry amplification and cost per success.

## Manuscript map

TD-AP06 contains exact baseline, mutation and repair commands plus report reading order and troubleshooting boundary.

## Editorial review

PASS. Rechecked the published commands, exit-code sequence and report names against the deterministic fixture. Kept the meaningful red condition: retry amplification and queue damage can fail the gate even when final task success stays high. The manuscript states that this proves the simulator and gate behavior only, not production capacity.

## Validation

PASS with fresh execution: baseline exit 0, retry-storm exit 1, repaired exit 0. Evidence is stored under the course package.
