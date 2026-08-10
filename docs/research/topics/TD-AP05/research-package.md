# TD-AP05 · Load-test architecture and tools

## Research brief

Question: which system architecture and tool combination can generate load, observe internals and decide business success? Artifact: four-layer design and tool matrix.

## Source pack

- k6 scenarios: https://grafana.com/docs/k6/latest/using-k6/scenarios/ — API load and thresholds.
- NVIDIA GenAI-Perf: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_benchmark/genai-perf-README.html — model endpoint benchmarking.
- Phoenix: https://github.com/arize-ai/phoenix and Langfuse: https://langfuse.com/handbook/chapters/open-source — trace/evaluation products; capability only.

## Evidence synthesis

No single tool covers arrival control, model token metrics, Agent business oracle, trace diagnosis and production SLO. A composable architecture is required. Tool documentation supports interfaces, not scale or production suitability.

## Engineering blueprint

Separate workload driver, SUT/fixtures, telemetry, and evaluator/gate. Correlate with run/task/version IDs. Sandbox writes, enforce idempotency and cost/time limits. Save a run manifest.

## Manuscript map

TD-AP05 maps tasks to tool candidates, blind spots, side-effect controls and the required Manifest.

## Editorial review

PASS. Tool names remain examples within four responsibilities—load generation, SUT/fixtures, telemetry and evaluation—not endorsements or an all-in-one claim. Preserved each tool's blind spot, the run/task/version correlation fields, sandbox and idempotency controls, and the warning that product documentation does not prove scale suitability.

## Validation

PASS: selection is by responsibility and limitation, not a generic best-tool list.
