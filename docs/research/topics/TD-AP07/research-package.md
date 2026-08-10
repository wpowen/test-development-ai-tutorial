# TD-AP07 · Failure diagnosis

## Research brief

Question: how can an engineer distinguish queue saturation, long Prefill, slow Decode, tool dependency failure, retry storm and Agent loops? Artifact: evidence-backed diagnosis record.

## Source pack

- vLLM metrics: https://docs.vllm.ai/en/latest/design/metrics/ — queue, scheduler, TTFT, ITL and cache metrics.
- NVIDIA metrics/arrival patterns: https://docs.nvidia.com/aiperf/reference/ai-perf-metrics-reference — model metric semantics and load pattern implications.
- Google cascading failures and OpenAI rate limits — retry feedback and safe retry behavior.

## Evidence synthesis

Correlation narrows candidates but does not prove causality. Compare equal workloads and change one variable. Closed-loop tests can hide overload by lowering arrival rate as latency increases.

## Engineering blueprint

Map symptom combinations to hypotheses, confirming and disconfirming evidence, and a controlled rerun. Stop feedback loops before root-cause work. Retry budgets span gateway, SDK, Agent and tool layers.

## Manuscript map

TD-AP07 includes a symptom matrix, coordinated omission, retry budget and incident repair order.

## Editorial review

PASS. Preserved the separation of symptom, hypothesis, confirming evidence, disconfirming evidence and controlled rerun. The page does not equate correlation with causality or recommend deleting thresholds to make a test pass. Retry budgets still span all layers, and emergency feedback-loop controls precede deeper diagnosis.

## Validation

PASS: it separates symptom/hypothesis/test, rejects threshold deletion and preserves quality/cost gates.
