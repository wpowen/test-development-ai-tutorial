# AI 可观测性调查指南

遇到“慢、错、贵”时按以下顺序调查：

1. 先确认 admitted task rate、workload slice、版本和是否有流量/输入 token 变化。
2. 检查任务是否建立、queue wait 是否增长、是否被拒绝或超时。
3. 沿 task 根 Trace 查看 retrieval、generation、tool、retry 的顺序与 attempt；不要把 HTTP 200 当作业务成功。
4. 将质量、E2E/TTFT/TPOT、队列、调用放大、成本、副作用和 telemetry completeness 分开判定。
5. 记录 `symptom → hypothesis → confirming evidence → disconfirming evidence/controlled rerun`。

指标保持低基数，细节放 Trace；raw prompt、PII 和完整 tool arguments 不进入高频 label。OpenTelemetry/GenAI 字段与 provider API 可能演进，接入真实服务时必须固定 schema、版本和脱敏策略。
