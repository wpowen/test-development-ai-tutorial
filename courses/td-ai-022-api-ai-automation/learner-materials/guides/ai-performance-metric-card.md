# AI API 性能指标卡

AI/Agent API 不能只看 HTTP p95。一次用户任务会展开为模型、检索、工具、队列、重试和流式事件；HTTP 200 可能对应错误工具、重复扣款或超预算。

| 指标 | 分母/聚合 | 解释 | 阈值方法 | 失败动作 |
|---|---|---|---|---|
| task success rate | 正确完成任务数 / 总任务数 | 业务结果，而非请求成功 | 按风险 slice 与历史基线设门槛 | 阻断，按任务类型下钻 |
| E2E p95 | 每个完整任务从接受到终态的延迟 | 包含排队、模型、工具和重试 | 从用户 SLO 与高峰分布校准 | 看 queue/tool/model span |
| first-event p95 | 请求到首个有效语义事件 | 流式接口的可感知响应 | 按交互体验目标校准 | 检查排队和首 token/tool event |
| tool retry amplification | 工具 attempt 数 / 逻辑工具调用数 | 重试风暴与费用放大 | 结合依赖错误率和重试预算 | 限流、退避、熔断或修依赖 |
| duplicate side-effect rate | 重复副作用 / 写操作任务 | 幂等和 exactly-once 风险 | 涉及资金时通常为 0 | 立即阻断并核查账本 |
| cost per success | 总估算成本 / 正确且满足 SLO 的任务 | 防止低成功率下平均成本失真 | 结合价格版本和单位经济性 | 比较模型、步骤、缓存和重试 |
| goodput | 单位时间内正确且满足 SLO/成本的任务 | 可持续有效吞吐 | 在固定 workload 下测容量曲线 | 降载或增加容量，不能只看 RPS |

## 切片要求

至少按 `scenario_id`、模型版本、Prompt 版本、tool schema 版本、错误类型、并发和终态切片。平均值不能掩盖高风险支付路径，也不能把失败任务排除在延迟/成本之外。

## 使用本包配置

`configs/ai-performance-workload.yaml` 给出合成 workload、必需维度和教学阈值。它是可复用输入模板，不是实测容量结果。接入 k6 时，checks 用于记录单次判断，thresholds 才决定非零退出码；流式和 Agent 指标通常还需要自定义事件 reducer 与 trace 汇总。

## 状态和边界

该 workload 与 k6 适配为 `static-reviewed/NOT_RUN`。没有 live model、支付工具、并发服务、费用账单或生产流量，因此不能从配置推断容量、成本、质量或 ROI。阈值 owner 是 AI quality 与 checkout service owner，AI 只能分析候选根因，不能自动降低门槛或接受资金副作用风险。
