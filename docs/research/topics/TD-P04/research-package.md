# TD-P04 · 风险策略与测试层级

## Research brief

控制问题：需求确认后，怎样决定哪些失败最重要、在哪一层验证、使用什么 Oracle，并把未覆盖风险交给具名责任人？产物是 Risk Test Plan，而不是用例数量清单。

## Source pack

- ISTQB CTAL Test Analyst v4.0：风险驱动测试、test analysis 和设计活动。
- ISO/IEC 25010:2023 页面：产品质量模型；不能直接提供项目阈值。
- Pact 文档：消费者/提供者契约与 provider verification；官方边界说明 Pact 不替代完整功能测试。
- Cucumber Gherkin：可执行示例描述可观察行为；步骤实现仍依赖项目代码。
- 历史失败模式：所有测试堆到 E2E、用例数量作为覆盖证明、严重性由模型臆造。

## Evidence synthesis

事实：不同测试层承担不同反馈速度、隔离程度和证据；契约测试不等于业务功能测试。工程综合：高风险需要同时映射测试、Oracle、监控、降级和 owner；层级选择记录纳入和排除理由。未知：目标系统的风险容忍度和生产 SLO。

## Engineering blueprint

Risk Test Plan 字段包括 risk_id、failure、impact、severity、test_levels、oracles、data、monitoring、owner 和 residual risk。订单案例覆盖重复退款、越权、已发货取消与状态/账本不一致。校验器不接受“加强测试”或空 Oracle。

## Manuscript map

页面先从失败影响建模，再用层级表做取舍，随后给 AI 候选策略的权限边界和覆盖门禁。练习要求下沉一个 E2E，而非再增加一个测试。

## Editorial review

PASS 94/100。删除“科学规划”“全面覆盖”之类结论。保留严重性未知、层级取舍和残余风险 owner，表格每行对应不同证据。

## Validation

PASS（静态）：每个高风险字段和阻断条件已映射。风险评分没有在真实缺陷分布上校准，页面没有提供可复制生产阈值。
