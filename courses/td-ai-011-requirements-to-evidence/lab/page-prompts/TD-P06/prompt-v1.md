# TD-P06 测试用例审查与自动化适配 Prompt v1.1.0

## 能做什么

先审查 Test Package 是否可执行、可观察、可维护，再把合格用例映射到 API、契约、组件、UI 或数据自动化。它会保留 test_id、risk_id 和 oracle_id，要求显式准备/清理/证据，不允许为了转绿吞断言、加 skip、无限重试或按实际结果改写 expected。

## 使用前准备

提供经过 TD-P05 生成并人工确认的 Test Package、接口或页面定位契约、测试框架约束、环境/数据准备方式和禁止副作用。若你的团队还没选框架，可让 AI 输出框架中立的 Adapter Contract，不要让工具选择掩盖用例缺陷。

## 直接复制到 AI Agent

```text
你是一名测试开发工程师。先审查测试用例质量，再设计自动化适配器。不能修改已批准业务 Oracle，不能通过 skip、吞异常、放宽断言或无限重试制造绿色结果。

【目标适配器】
[填写：API / contract / component / web UI / mobile UI / data pipeline / framework-neutral]

【Test Package】
[粘贴 test_id、requirement_id、risk_id、method、fixture、steps、expected、oracle_id、cleanup、evidence]

【接口/页面/数据契约】
[粘贴 OpenAPI、Schema、稳定 locator、事件字段、数据库只读查询或消息契约]

【环境与工具约束】
[粘贴框架及版本、cwd、依赖、凭据策略、数据工厂、并发限制、超时和 artifact 路径]

【禁止事项】
[粘贴不可触发的真实支付/通知/删除、不可访问数据、不可修改环境；没有则写“未定义”]

【执行步骤】
1. 用例审查：检查 source_refs、risk/method/oracle、前置条件、数据、步骤、expected、证据和 cleanup；将模糊/重复/不可执行/弱 Oracle 项列为 REVIEW_FAIL。
2. 选择自动化层级并说明理由；如果更适合单元/契约，不要强行生成 UI 脚本。
3. 输出 Adapter Contract：adapter_id、supported_test_ids、inputs、setup、action mapping、assertion mapping、cleanup、evidence、timeout、retry、permissions、limitations。
4. 断言必须引用 oracle_id；传输、schema、业务状态、事件/审计和风险策略分层检查。
5. 错误必须向上传播；只允许对明确可重试的环境动作做有界重试，并记录每次结果。业务断言失败不得重试成绿。
6. locator、接口字段或数据列缺失时标 BLOCKED，不要编造。真实凭据或不可逆副作用缺控制时拒绝生成执行代码。
7. 输出 baseline、fault、repair 三个运行计划：正常实现应通过；植入一个能违反 Oracle 的 mutation 应失败；修复后恢复。写明预期退出码和证据文件。
8. 如果请求代码，生成最小可运行骨架、固定 cwd、安装/运行命令、示例 fixture、预期输出和 reset 命令；说明仍需在目标仓库适配的字段。

【输出格式】
A. 用例审查结果：PASS / REVIEW_FAIL / BLOCKED
B. Findings：finding_id、test_id、severity、evidence、repair
C. 自动化层级与方法选择理由
D. Adapter Contract
E. 文件清单与代码骨架
F. exact commands：install/setup/baseline/fault/repair/reset，含 cwd、exit code、artifacts
G. Trace Map：requirement→risk→method→oracle→case→adapter→result
H. Evidence / Inference / Unknown 与人工确认项

【输入粘贴区结束后的强制自检】
- 是否改写了 expected 或 oracle_id？如有立即 REVIEW_FAIL。
- 是否存在 catch 后不抛、无条件 skip、超大 timeout、无界 retry 或睡眠等待？
- 每个自动化用例是否保存可定位失败的原始证据？
- 命令是否有明确 cwd、依赖、退出码和产物？
- fault 是否真的违反独立 Oracle，而非只让脚本语法报错？
```

## 修改这些字段就能复用

替换目标适配器、Test Package、系统契约、环境约束和禁止事项。框架变化时只改 Adapter Contract 与代码层，不改上游 requirement/risk/oracle/test_id。对 UI 重点修改 locator 和证据；对 API 修改 endpoint/schema；对数据修改 dataset/table 和只读验证。迁移后必须重跑 baseline/fault/repair。

## 预期输出

你会得到用例审查报告、框架中立 Adapter Contract、可落地代码骨架和精确运行路径。即使暂时不生成代码，也能明确哪些字段必须由目标项目补齐以及如何验证自动化没有假绿。

## 结果自检

- 代码失败能否映射回 test_id 和 oracle_id？
- 数据准备和清理是否幂等、可重复？
- 超时和重试是否与系统语义一致？
- mutation 是否会稳定变红且 finding 可解释？
- 自动化是否避免生产凭据和未授权副作用？

## 停止条件与边界

Test Package 未审查、Oracle 不独立、接口/locator/数据契约缺失、凭据或副作用无安全控制、目标环境不可复现时必须 BLOCKED。生成代码不等于在项目中运行通过；必须保留真实执行、集成和维护责任人的独立证据。
