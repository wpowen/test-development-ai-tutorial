# TD-AP08 · Production stability system

## Research brief

Question: how does a one-time load test become ongoing SLO, alert, degradation and incident feedback? Artifact: production stability design and executable Runbook.

## Source pack

- Google SRE service best practices: https://sre.google/sre-book/service-best-practices/ — SLO and production readiness.
- Google monitoring/overload chapters — symptom signals, saturation and overload controls.
- OpenTelemetry GenAI observability — cross-model/tool trace linkage; evolving standard limitations.
- NIST GenAI profile: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf — risk governance and monitoring context.

## Evidence synthesis

Golden signals prove service health, not answer correctness. Agent SLO therefore uses a user-task numerator combining terminal correctness, latency, cost, policy and side-effect safety. Root-cause metrics belong in diagnosis panels unless they have a direct action.

## Engineering blueprint

Define good-task SLI, error budget and high-risk slices. Page on user symptoms/rapid burn; correlate queue, TTFT, tool, retry and cost. Predefine queue caps, retry budgets, read-only/human degradation, canary recovery and incident-to-workload feedback.

## Manuscript map

TD-AP08 covers multidimensional SLO, alert levels, protections, Runbook and release/production feedback loop.

## Validation

PASS: SLO denominator, owner, action, rollback and evidence boundary are explicit; sample thresholds are not universal claims.
