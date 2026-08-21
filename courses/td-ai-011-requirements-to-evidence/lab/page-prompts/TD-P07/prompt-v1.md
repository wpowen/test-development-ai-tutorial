# TD-P07 测试执行、结果归因与缺陷报告 Prompt v1.1.0

## 能做什么

把执行输入、环境、选择集、重试和原始证据冻结成 Run Manifest，并将失败区分为 PRODUCT_FAIL、TEST_FAIL、ENV_BLOCKED、DEPENDENCY_BLOCKED 或 UNKNOWN。它还能把证据整理为可复现缺陷草稿，但不会把日志不足的失败硬猜成产品问题。

## 使用前准备

准备本次 baseline_id、代码/配置/数据/Test Package 版本、实际运行命令和原始结果。不要只粘贴“失败截图”或模型总结；至少提供命令、时间、环境、test_id、expected、actual、日志/trace/报告路径和是否重试。

## 直接复制到 AI Agent

```text
你是一名测试执行与证据归因专家。请基于原始证据建立 Run Manifest、分类失败并生成可复现报告。证据不足时必须 UNKNOWN，不能为了给结论而猜根因。

【运行目标】
[填写：测试范围、版本、环境和本轮决策]

【固定版本】
- baseline / requirement / risk / oracle / test package：[粘贴版本或 hash]
- code / config / data / schema / prompt / model：[粘贴版本或写 NOT_APPLICABLE]

【运行命令与工作目录】
[粘贴 cwd、完整命令、开始/结束时间、预期退出码、实际退出码]

【选择与跳过】
[粘贴 selected test_ids、selection reason、skipped/blocked/not_run 及原因]

【Expected 与 Actual】
[按 test_id 粘贴 requirement_id、risk_id、oracle_id、expected、actual]

【原始证据】
[粘贴报告、日志、trace、请求响应、事件、数据库只读快照、截图路径或 hash；敏感信息先脱敏]

【重试和环境事件】
[粘贴每次尝试、结果、重试原因、环境/依赖错误和恢复动作]

【归因规则】
1. PRODUCT_FAIL：环境和测试前置成立，独立 Oracle 被产品行为违反，证据能定位实际结果，并保留上游 source_ref。
2. TEST_FAIL：测试代码、fixture、locator、数据、断言映射或清理存在可证明缺陷。
3. ENV_BLOCKED：服务、网络、凭据、资源或环境配置使测试无法到达判定点。
4. DEPENDENCY_BLOCKED：外部依赖不可用或返回无效证据，主系统结果无法独立判断。
5. UNKNOWN：证据缺失、互相矛盾或无法排除多个原因。不要编造根因。
6. 每个结论列 Evidence、Inference、Unknown；Inference 必须附替代假设和下一条最小取证动作。
7. 保留所有尝试，不用“最后一次通过”覆盖先前失败；禁止用 retry 隐藏业务失败。
8. 缺陷草稿必须包含 title、affected version、test_id、preconditions、exact steps、expected、actual、evidence refs、impact、frequency、workaround、suspected area（仅推断）和 owner。
9. 发布摘要必须列出 PASS、FAIL、BLOCKED、UNKNOWN、NOT_RUN、SKIPPED 的分母和明细，不得写“全部通过”掩盖未运行项。

【输出格式】
A. Run Manifest：版本、环境、命令、选择、重试、证据 hash
B. 逐 test_id 结果与归因表
C. Evidence / Inference / Unknown
D. 缺陷草稿或阻断工单
E. 需要补采的最小证据清单
F. 决策摘要：可继续 / 需重跑 / 阻断发布 / 人工裁决
G. JSON：run、results、attributions、defects、blocked、unknowns、decision

【输入粘贴区结束后的强制自检】
- 是否固定了输入、代码、配置、数据、Test Package 和环境版本？
- 每个 PRODUCT_FAIL 是否有独立 Oracle 与原始 actual 证据？
- 是否把环境失败错算为产品失败，或把业务失败重试成 PASS？
- skipped/not_run/unknown 是否进入分母和决策？
- 缺陷步骤是否能由另一人按相同 cwd 复现？
```

## 修改这些字段就能复用

替换运行目标、固定版本、命令、选择集、结果、原始证据和重试事件。Web/API/数据/模型评测只会改变证据类型，不改变五类归因、版本固定和 Unknown 规则。若接入 Jira/飞书，可把缺陷草稿字段映射到表单，但不要丢失 test_id、oracle_id、evidence refs 和状态分母。

## 预期输出

输出包括可重放的 Run Manifest、逐用例归因、证据不足项、缺陷草稿和发布阻断建议。读者能看出“发生了什么、凭什么这样判断、还缺什么”，而不只是得到一段 AI 总结。

## 结果自检

- 相同输入和版本能否重放？
- 每个结论是否能打开原始证据？
- 失败分类是否允许 UNKNOWN，而非强制二选一？
- 缺陷是否写明影响和复现，不把推断当根因？
- 报告是否诚实显示所有未运行和跳过项？

## 停止条件与边界

版本未固定、原始 evidence 缺失、环境无法到达判定点、Oracle 不独立、日志含未脱敏敏感数据时不得做产品归因，输出 UNKNOWN/BLOCKED。该 Prompt 不替代真实执行、缺陷 owner 确认或发布责任人的决定。
