# TD-P01 · 测试依据与来源冻结

## Research brief

控制问题：在 AI 读取 PRD、技术方案和接口文档之前，测试负责人怎样证明输入是当前版本、可以引用并且没有被静默合并的冲突？学习者要决定资料包能否进入需求抽取。产物是 Test Basis Pack；不讨论测试用例生成。

## Source pack

- ISO/IEC/IEEE 29148 页面：需求工程信息项和内容框架；标准预览不能替代全文条款。
- ISTQB CTFL 4.0.1：test basis、traceability 和 work product 关系；它不规定企业文档优先级。
- OpenAPI 3.2：接口契约的机器可读坐标；接口 Schema 不包含全部业务语义。
- Playwright Test Agents：planner 可接收 PRD 和 seed test；官方同时要求重新生成或验证产物，不能把 Agent 计划当成批准需求。
- 对抗证据：PRD 与旧技术方案故意给出相反的 SHIPPED 取消规则。

## Evidence synthesis

事实：测试依据可能来自多种有版本的工作产品，追溯需要从测试回到 basis。工程综合：为每份资料记录 owner、hash、有效版本和段落级 source_ref，并在抽取前定义来源优先级。未知：具体组织由谁批准业务语义和技术细节。冲突未解决时的正确状态是 BLOCKED，不是让模型选择“更合理”的版本。

## Engineering blueprint

输入为 PRD、技术方案、OpenAPI、状态机、术语表、变更范围和历史缺陷。输出 `basis.json`，包含 `baseline_id`、`sources[]`、`precedence_rule`、`conflicts[]`。验证器检查关键字段、引用坐标和冲突；冲突存在时退出码 2，并禁止生成 TestPackage。

## Manuscript map

页面先用订单取消冲突解释风险，再给 source manifest、提取 Agent 权限和两条命令。学习者亲手注入冲突，看到下游目录不产生新测试资产。

## Editorial review

PASS 94/100。已冻结字段、命令、退出码、来源和 synthetic 边界。删除“全面梳理”“让 AI 帮你”等空泛表达。标题分别对应冻结版本、分配引用、限制权限和执行门禁；没有使用共享模板段落。

## Validation

PASS：离线夹具 `validate-basis` 在干净输入返回 0；注入文档冲突后 `all` 返回 2。该结果只证明阻断机制可运行，不证明资料包代表真实企业流程。
