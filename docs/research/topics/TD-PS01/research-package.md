# TD-PS01 · API 业务契约：从 HTTP 结果到可验证副作用

## Research brief

业务场景是订单取消与退款：已支付、未发货的订单可以进入 `CANCEL_PENDING`，随后只产生一次退款意图。传统接口测试通常断言 `202`、JSON 字段和响应时间，却无法证明状态推进、幂等重放或事件消费。AI 可以从 OpenAPI、需求和失败 Trace 提出候选场景，但不能决定退款是否发生。研究边界是契约、状态机、权限、幂等和副作用证据；不把真实支付网关、账务系统或生产阈值当作已知事实。工具选型偏向 OpenAPI + Pact + 受控事件 Stub，复杂业务不变量由测试代码和账本查询承担。

## Source pack

- OpenAPI Specification 3.2.0：<https://spec.openapis.org/oas/v3.2.0.html>，提供操作、参数、响应和 webhook 的机器可读契约；不表达全部退款不变量。
- HTTP Semantics RFC 9110：<https://www.rfc-editor.org/rfc/rfc9110.html>，支持方法、状态码、幂等性和缓存语义；`202` 不等于异步业务已完成。
- Pact 官方文档：<https://docs.pact.io/>，说明 consumer-driven contract 与具体交互验证；不能替代账本和事件回归。
- CloudEvents 官方规范：<https://github.com/cloudevents/spec>，支持事件 ID、来源、类型和重复投递语义。

## Evidence synthesis

事实：HTTP 响应、Schema、业务状态和外部副作用是四类不同证据。事实：同一幂等键的重放必须与退款账本或事件账本核对，不能只比较第二次响应。工程综合：将 `status_code`、错误结构、订单状态、退款计数、事件 ID、`request_id` 和 `trace_id` 放进同一运行 Manifest，才能诊断“服务已成功但客户端超时”。

传统做法的盲区是把 Mock 返回成功当作真实副作用。AI 变化在于可从需求和 Trace 生成负例、状态转移和候选 Oracle；工程边界是候选必须经过 Schema 校验、受控执行和人工确认。失败模式包括已发货误取消、越权取消、超时后重试重复退款、事件重复/延迟、账本查询不一致。`static-reviewed` 只表示研究包和夹具结构经文档审阅，不表示目标 API 已运行。

## Engineering blueprint

七节点架构与页面定义一致：

| 节点 | 实施与可审计输出 |
|---|---|
| 调用方与幂等键（输入） | 输入订单 ID、身份 claims、`Idempotency-Key`、预置订单状态和风险等级；保存脱敏请求 hash。 |
| API Gateway（处理） | 检查鉴权、限流、method、超时和 trace 传播；输出原始响应及网关日志。 |
| 订单领域服务（处理） | 按状态机判断 `CANCEL_PENDING`、拒绝原因和并发版本；禁止由模型文本直接改变状态。 |
| 订单/退款账本（证据） | 读取前后状态、退款金额、退款次数和幂等记录；账本查询失败为 `UNKNOWN`。 |
| 事件总线与消费者（处理） | 回放成功、重复、延迟和乱序事件；校验事件 ID 与最终消费状态。 |
| Trace/日志/指标（证据） | 关联 request、trace、事件、延迟、重试和副作用计数，生成可重放 Manifest。 |
| 发布门禁（门禁/人工决策） | 越权、重复副作用、状态倒退或缺关键证据直接阻断；普通文案差异由领域 owner 人工决定。 |

可执行物料是订单取消 OpenAPI、状态/不变量清单、事件账本 Stub、四组重放数据和 Manifest schema。推荐顺序是探针、正常/拒绝、重放、依赖超时，再做最小失败重放。

## Manuscript map

先用“响应为 `202` 但退款未发生”和“客户端超时后重复退款”两个反例建立问题。随后按协议、Schema、业务、不变量/副作用四层拆 Oracle，展示同一幂等键的请求序列和账本断言。再解释 Pact 适合消费者交互而不覆盖领域账本，最后给出 Trace 到发布门禁的诊断路径。AI 辅助部分只展示候选生成、失败聚类和人工批准记录。

## Editorial review

保留订单取消、退款事件、跨角色权限和重放作为不可互换的业务细节；没有用“接口测试更智能”“自动发现所有问题”替代证据。工具选择明确了 OpenAPI/Pact/事件 Stub 的职责边界，未知项包括真实幂等实现、账本可查询性、支付网关行为和目标组织阈值。页面中的示例断言是研究设计，不宣称已执行。

## Validation

当前状态：`desk-researched`，未连接目标 API、数据库、支付网关或事件总线。

后续可离线升级为 fixture-tested：`validate_order_cancel_manifest.py` 校验四层 Oracle 和 source_ref；`replay_idempotency_fixture.py` 在内存账本中重放同一幂等键；`inject_duplicate_refund_event.py` 检查退款计数不增加；`trace_side_effect_report.py` 检查每个副作用可回链到 trace。离线通过只能证明夹具门禁和诊断结构，不证明真实支付安全。
