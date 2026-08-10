# TD-P07 · 执行证据与失败归因

## Research brief

控制问题：一次测试结果需要保存哪些输入、环境、选择集、重试和原始证据，才能区分产品失败、测试失败、环境阻塞与未知？产物是 Run Manifest 和可复现报告。

## Source pack

- ISO/IEC/IEEE 29119-2 页面：测试过程和产生的工作产品；公开页面不提供项目字段模板。
- Playwright Test Agents：healer 会运行测试并提出修复；skip 和修复结果仍需审核。
- OpenTelemetry Signals 与 W3C Trace Context：跨组件关联 trace 的公共机制；不定义订单业务状态。
- NIST AI RMF Measure：记录测试数据、工具、结果和限制，支持独立评审和持续监测。
- 失败样例：绿色截图没有 code SHA、selected tests、skip、retry 或原始日志。

## Evidence synthesis

事实：测试结果是过程工件，Trace 可连接跨服务操作。工程综合：Run Manifest 固定代码、需求、测试包、数据、环境和命令；状态至少分 PRODUCT_FAIL、TEST_FAIL、ENV_BLOCKED、DEPENDENCY_BLOCKED 和 UNKNOWN。未知：企业日志留存与 PII 政策。

## Engineering blueprint

执行器输出 input hashes、selected_test_ids、skipped、retries、结果和 boundary。课程分别保存 baseline、mutation、repair；mutation 失败必须引用测试、需求、风险和实际响应。没有关键版本时返回 NOT_RUN/BLOCKED。

## Manuscript map

页面从 Run Manifest 开始，用状态表解释归因，再给三态命令和报告审计项。避免把 AI 生成摘要作为原始证据替代品。

## Editorial review

PASS 95/100。保留 SHA、hash、重试、退出码和 UNKNOWN 语义。删除“清晰直观报告”等形容词，改成报告必须包含的字段。

## Validation

PASS：三份离线报告保存输入 hash、选择集、零 skip、零 retry、实际值和 synthetic 边界。未验证真实分布式 Trace 和企业留存策略。
