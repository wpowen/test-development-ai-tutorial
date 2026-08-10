# 样例输入

本课使用 120 条合成 AI 任务，固定 seed 42。每条任务包含一个 retrieval call、一个模型阶段和一个工具阶段；工具是幂等的只读 stub，允许终态为 `completed`、`timeout` 或 `dependency_failed`。配置中的 latency、failure rate、attempt 上限、backoff 和到达间隔构成可审计 workload。

故障场景有意让到达速率超过修复后的可持续处理能力，并提高 transient tool failure，使队列和重试反馈环显性化。数据不代表任何真实用户、模型或企业任务分布。
