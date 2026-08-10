# TD-AP03 · Workload model

## Research brief

Question: how should real Agent traffic become a replayable workload rather than repeated identical prompts? Artifact: versioned task/path/input/failure distribution.

## Source pack

- NVIDIA arrival patterns: https://docs.nvidia.com/aiperf/dev/tutorials/load-patterns-scheduling/arrival-patterns-simulating-realistic-traffic — request-rate, concurrency and burst patterns.
- k6 scenarios: https://grafana.com/docs/k6/latest/using-k6/scenarios/ — scenario executors and independent workloads.
- Google SRE handling overload: https://sre.google/sre-book/handling-overload/ — overload, queues and graceful rejection.

## Evidence synthesis

Fact: input/output length and arrival pattern materially change latency. Inference: Agent workload must add task type, tool fan-out, expected terminal state and dependency failures. Unknown: future peak mix; record forecasts separately from observed traffic.

## Engineering blueprint

Use task slices and joint distributions for token length, step count, tools, cache state and dependency behavior. Run baseline, capacity, burst, soak and fault scenarios. Store fixture version and provenance; remove PII.

## Manuscript map

TD-AP03 teaches slicing, four variable families, five test shapes and a replay record.

## Validation

PASS: workload is not an average prompt; it includes allowed terminal states, budgets and evidence limitations.
