# TD-AP01 · Why Agent load is not API concurrency

## Research brief

Question: what is the correct work unit and failure model for Agent load testing? The learner is a test developer who knows API testing. The decision is whether a load result proves user-task capacity. The artifact is a task/request/model/tool boundary map. Excludes detailed metric thresholds, which belong to TD-AP02.

## Source pack

- Google SRE monitoring and cascading failures: https://sre.google/sre-book/monitoring-distributed-systems/ and https://sre.google/sre-book/addressing-cascading-failures/ — supports golden signals, queue/retry feedback loops; does not define Agent task success.
- k6 scenarios: https://grafana.com/docs/k6/latest/using-k6/scenarios/ — supports open/closed workload models; does not provide Agent business oracle.
- OpenAI Agents tracing: https://openai.github.io/openai-agents-python/tracing/ — supports model/tool/handoff spans; product capability is not production efficacy.

## Evidence synthesis

Fact: entry acceptance, Agent terminal state, model generation and tool call are different observation layers. Synthesis: the denominator must be admitted user tasks, while internal call counts quantify dynamic amplification. Unknown: the target system's path distribution and capacity.

## Engineering blueprint

Root object is `task_run`; children are queue, generation, tool, handoff and state operations. Compare open-loop arrival rate with closed-loop concurrency. Track task success, terminal state, call amplification, retry amplification and duplicate side effects.

## Manuscript map

Site page TD-AP01 covers work unit, dynamic amplification, load models and the shared order-exception scenario.

## Editorial review

PASS. Preserved the distinction among admitted tasks, HTTP requests, model calls and tool calls; kept open-loop, closed-loop and coordinated-omission terminology tied to their engineering consequences. Removed any suggestion that one concurrency number proves Agent capacity. The page still requires a task-level business oracle and labels the target path distribution as unknown.

## Validation

PASS: the page distinguishes all denominators, explains coordinated omission risk, includes a counterexample, and labels production capacity unknown.
