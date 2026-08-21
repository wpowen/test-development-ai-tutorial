# Refund Agent Runbook

这是迁移练习用的只读/沙箱 runbook，不授权真实退款。

## 触发

当 `task_success_rate`、`e2e_p95_ms`、`queue_p95_ms`、`retry_amplification` 或 `duplicate_side_effect_rate` 越界时，先记录 run_id、release、model/prompt/tool schema 版本和 trace_id。

## 分流

- queue 高：停止增加重试，检查 admission、worker、优先级和 load shed。
- retry 高：确认只有一层负责 transient retry，遵守 Retry-After，并检查预算。
- 工具失败：停止写副作用，检查 schema、权限、幂等 key 和 sandbox 状态。
- HTTP 成功但任务失败：检查终态 oracle、tool trajectory、retrieval evidence 和人工升级。
- 成本高：检查 token、fan-out、cache miss 和失败后的 cost_per_success。

## 恢复

优先限流/降级/只读 fallback，必要时回滚 release；修复后用相同 workload 与 seed 复测，再增加一个未见过的 slice。没有 owner、回滚命令或真实观测证据时，结论为 `BLOCKED`，不是 PASS。
