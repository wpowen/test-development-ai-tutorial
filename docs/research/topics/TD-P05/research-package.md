# TD-P05 · 测试包与独立 Oracle

## Research brief

控制问题：怎样防止同一个模型生成错误实现和错误断言后互相证明？学习者要把风险策略转成 TestPackage，并用独立不变量和 mutation 证明测试具有检测力。

## Source pack

- ISTQB CTAL Test Analyst v4.0：测试设计、明确通过/失败条件、环境和数据。
- Pact 文档：契约交互的可验证范围和功能边界。
- Cucumber Gherkin：Given/When/Then 指向可观察结果，不应检查内部实现细节。
- NIST AI RMF Measure：记录测试集、指标、工具、结果和限制；模型 Judge 需要独立评审与持续监测。
- 对抗证据：只断言 HTTP 200；模型根据当前实现反向生成 expected；没有负控制的全绿报告。

## Evidence synthesis

事实：结构、契约、可执行示例和模型评分各自提供不同证据。工程综合：金额、权限、状态和副作用优先使用确定性 Oracle；语义 Oracle 才使用经人工标签校准的 Judge。未知：目标系统可接受的统计波动与 Judge 一致率。

## Engineering blueprint

TestPackage 记录 test_id、requirements、risks、level、fixture、actions、oracles、cleanup 和 evidence。课程植入 `allow_shipped_cancel=true`；`T-CANCEL-SHIPPED-01` 必须从预期 409 变为实际 202 并退出 1。

## Manuscript map

页面展示一条幂等测试的完整数据结构，解释四类 Oracle，提供生成任务和 mutation 命令。完成标准是已知缺陷被准确发现，不是生成多少条用例。

## Editorial review

PASS 96/100。字段、命令、状态码和退出码已冻结。删除“智能生成高质量用例”等供应商式措辞。明确同一模型自证、HTTP 200 假绿和 Judge 边界。

## Validation

PASS：离线 mutation 稳定触发单一失败测试，报告包含 requirement_id、risk_id、期望、实际和 mutation_id。没有连接真实服务或模型。
