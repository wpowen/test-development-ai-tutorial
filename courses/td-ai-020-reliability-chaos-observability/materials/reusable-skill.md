# 可复用能力

把任何 AI 服务拆成 task、request、generation、tool call、attempt 五个分母；为每个任务建立根 Trace，把 queue、model、retrieval、tool、retry 作为子事件。先锁定 workload、版本、seed、SLO 与成本预算，再做单变量故障；用同一 manifest 复测。

迁移时必须重建任务 oracle、允许终态、工具副作用、到达分布、价格表和阈值。保留 `UNKNOWN`、`BLOCKED`、`NOT_RUN` 与 `PASS/FAIL` 的区分，不把离线 fixture 或静态 YAML 写成生产证据。
