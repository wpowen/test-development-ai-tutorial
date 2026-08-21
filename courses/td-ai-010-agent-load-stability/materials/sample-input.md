# 样例输入与 workload 字段

统一场景包含 read_order、classify_exception、refund_review、human_handoff 四类任务。每条输入至少记录：

- task_type 与 risk_slice
- input/output token bucket
- expected tool path 与 allowed terminal states
- latency、retry、step、cost 与 side-effect budget
- fixture/workflow/prompt/tool schema version
- observed、forecast 或 synthetic-fault provenance

`lab/profiles/TD-AP01.json`～`TD-AP08.json` 分别保存每页 baseline/fault/repair 参数与 gates。固定 seed 只保证本地可复现，不代表生产任务分布。

