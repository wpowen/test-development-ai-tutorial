# TD-AP02 · Agent performance metric tree

## Research brief

Question: which metrics jointly prove that an Agent is fast, correct, stable and economical? The artifact is a metric dictionary with formula, denominator, dimension, source and action.

## Source pack

- NVIDIA AIPerf metrics: https://docs.nvidia.com/aiperf/reference/ai-perf-metrics-reference — TTFT/TTFO/ITL/throughput semantics.
- vLLM metrics: https://docs.vllm.ai/en/latest/design/metrics/ and https://docs.vllm.ai/en/latest/features/per_request_metrics/ — queue, TTFT, ITL, E2E and scheduler signals.
- LangSmith trajectory evals: https://docs.langchain.com/langsmith/trajectory-evals — final, trajectory and step evaluation levels.
- OpenAI Agents usage: https://openai.github.io/openai-agents-python/usage/ — usage aggregation across model calls and handoffs.

## Evidence synthesis

Consensus: model latency must be decomposed and normalized by token lengths; Agent success cannot be inferred from generation success. Synthesis: Goodput combines task correctness, latency and cost budgets. Vendor-specific naming must be mapped in a versioned dictionary.

## Engineering blueprint

Four layers: service golden signals; model TTFT/TTFO/ITL/E2E; trajectory task success/steps/tools/retries; cost per successful and quality-adjusted task. Every ratio names its denominator and every alert maps to an owner action.

## Manuscript map

TD-AP02 includes exact metric tables, formulas, valid interpretation, invalid interpretation and threshold method.

## Editorial review

PASS. Checked TTFT, TTFO, ITL, E2E, throughput, task success, retry amplification and cost denominators against the cited definitions. Kept goodput as a locally defined composite rather than a vendor standard. No universal threshold or unsupported benchmark number remains; every metric is connected to a workload slice, decision and owner action.

## Validation

PASS: no universal threshold is invented; all critical metrics include semantics and decision use.
