# TD-PS03 · 契约、事件与鉴权：测试跨服务边界的真实兼容性

## Research brief

业务场景是结算：Checkout 接受购物车并发布 `order.created`，库存、支付和通知异步消费。传统做法让提供者和消费者共享同一份 Mock，各自通过却不证明真实字段、权限、版本、重复投递和补偿兼容。AI 可以分析消费者代码、事件 diff 和 Trace，提出缺失契约；它不能授予租户权限、修改事件语义或关闭 blocker。研究范围是 Pact/事件 Schema、tenant isolation、幂等、乱序、死信和 Trace 诊断；消息中间件和策略引擎的实际配置仍是未知。

## Source pack

- Pact 官方文档：<https://docs.pact.io/>，支持 consumer-driven request/response contract；不能覆盖全部异步副作用。
- AsyncAPI Specification 3.0：<https://www.asyncapi.com/docs/reference/specification/v3.0.0>，定义 channel、message、operation 和协议无关的事件契约。
- CloudEvents 规范：<https://github.com/cloudevents/spec>，提供事件 envelope、唯一 ID、source/type 等跨服务基础字段。
- OWASP API Security Top 10：<https://owasp.org/API-Security/editions/2023/en/0x11-t10/>，支持对象级授权、资源消耗和错误配置等鉴权风险分类。

## Evidence synthesis

事实：消费者契约验证“这个消费者如何使用提供者”，事件 Schema 验证 envelope/载荷形状，授权测试验证身份与租户边界；三者不能用共享 Mock 合并替代。事实：同一 `event_id` 重放应不产生第二个支付意图，乱序必须落到可解释的补偿或等待状态。工程综合：把 claims、policy version、event version、consumer result、dead-letter 和最终状态放进同一 trace。

AI 变化是从多仓库代码和失败轨迹提取候选字段、兼容风险和回放序列。工程边界是所有候选先进入 schema/permission fixture，人工确认哪些字段是 required。失败模式包括删除消费者仍读取的字段、收紧枚举、跨租户消费、重复支付、事件乱序、补偿无 owner 和死信无告警。工具选型为 Pact + AsyncAPI/CloudEvents + 受控事件 broker；不把一次契约通过写成全链路证明。

## Engineering blueprint

七节点架构与页面定义一致：

| 节点 | 实施与可审计输出 |
|---|---|
| Checkout API（输入） | 输入购物车、租户、角色、token 和预期订单版本；保留身份 claims 摘要与 request hash。 |
| Auth/租户策略（门禁） | 先跑同租户成功、跨租户拒绝、角色不足、过期 token；策略决策必须可解释并无副作用。 |
| 契约 Broker（处理） | 保存消费者字段/错误契约、provider verification、事件版本兼容矩阵和变更 diff。 |
| 事件总线（处理） | 回放正常、重复、乱序、延迟和旧版本事件；记录 event ID、offset、重试和 dead-letter。 |
| 库存消费者（证据） | 检查库存预留与失败补偿状态；验证跨租户事件不会写入本地状态。 |
| 支付消费者（证据） | 以 `order_id`/`event_id` 查询支付意图计数和账本；重复事件不得第二次扣款。 |
| 死信/补偿与 Trace（人工决策） | 证据不足、版本不兼容或补偿超时自动阻断；服务 owner 人工批准兼容例外和回滚。 |

可执行物料是事件 JSON fixture、Pact consumer/provider 合同、权限矩阵、乱序回放队列和补偿报告。顺序必须是权限探针、契约验证、受控消息回放、最终状态核对。

## Manuscript map

用“两个服务都绿、真实结算失败”的共享 Mock 反例开场。然后拆 provider contract、consumer contract、event envelope、policy oracle 和副作用 oracle。展示破坏性字段变更、跨租户事件和重复 `event_id` 的最小回放，再用 Trace 诊断“支付重复”与“库存延迟”的不同路径。AI 只做 diff 聚类和候选契约草稿。

## Editorial review

页面没有把 Pact 说成消息总线或权限系统，也没有把 AsyncAPI Schema 说成业务补偿保证。保留版本、租户、幂等和死信的工程边界；真实 broker、策略版本和补偿时序标为未知。所有示例 URL 为官方入口，运行状态明确为 static-reviewed/desk-researched。

## Validation

当前状态：`desk-researched`，未接入真实 Checkout、broker、policy engine 或支付消费者。

后续可离线升级为 fixture-tested：`validate_event_envelope.py` 校验 event ID/version/tenant；`verify_consumer_contract.py` 对固定 consumer fixture 做字段兼容检查；`replay_event_order.py` 重放重复和乱序事件；`assert_tenant_isolation.py` 检查拒绝无状态写入；`build_compensation_trace.py` 验证失败、死信和人工升级的证据链。离线通过不代表真实 broker delivery guarantee。
