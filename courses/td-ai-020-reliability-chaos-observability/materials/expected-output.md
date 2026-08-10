# 预期输出

`evidence/baseline/summary.json` 与 `evidence/repaired/summary.json` 应有 `gate_pass: true`；`evidence/latency-retry-fault/summary.json` 应有 `gate_pass: false`。三份报告都应具备任务成功率、p95、调用放大、成本、队列和重试字段，并由 `traces.jsonl` 提供 task/trace/attempt 级证据。

故障报告的红色原因至少应包括 queue p95、E2E p95、retry amplification、call amplification 或 task success 中的一项；不要只检查进程是否完成。
