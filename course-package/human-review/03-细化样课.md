# 细化样课：AI 如何把需求文档变成可执行测试证据

这份样课供你直接判断课程是否有生产力价值。它使用虚构的订单取消资料，不接生产系统，也不把模型输出当成已批准需求。

## 业务场景

团队准备上线订单取消接口。产品文档写明：买家可以取消已支付但未发货的订单；已发货订单必须拒绝。旧技术方案仍保留“SHIPPED 可取消”的历史逻辑。接口契约定义了 `202`、`403` 和 `409`，但没有说明退款最晚完成时间。

如果把三份文件直接交给大模型并要求“生成完整测试用例”，模型很可能做两件危险的事：自行选择一条冲突规则；补出一个看似合理的退款 SLA。生成结果会很整齐，却没有业务授权。

本课把这件工作拆成八步：

```text
测试依据 -> 需求契约 -> 评审问题 -> 风险策略
-> 测试包与 Oracle -> 自动化适配器 -> 执行证据 -> 变更回归
```

## 学完能得到什么

学习者会留下九个可追溯工件，并能解释输入冲突为什么是 `BLOCKED`、产品缺陷为什么是 `FAIL`、修复后为什么可以成为发布候选。课程不承诺替代产品评审，也不把生成用例数量当成结果。

## 上课流程

## 第一课：冻结测试依据

学习者先建立 `basis.json`，为 PRD、技术方案和 OpenAPI 记录 owner、版本、hash 与段落引用。来源优先级提前写清楚：已批准 PRD 决定业务语义，当前技术方案和接口契约决定实现细节；语义冲突必须评审。

运行：

```bash
cd courses/td-ai-011-requirements-to-evidence/lab
python3 pipeline.py reset
python3 pipeline.py validate-basis
```

干净夹具返回 `PASS`。随后注入文档冲突：

```bash
python3 pipeline.py inject-doc-conflict
python3 pipeline.py all
```

预期退出码是 `2`，状态为 `BLOCKED`。报告必须列出 `PRD-v3#R17`、`TECH-a13f#S04` 和需要回答问题的产品 owner。测试生成不能继续。

这一步验证的是停止能力。系统没有权力用“综合理解”覆盖冲突。

## 第二课：形成 Requirement Contract

问题关闭后，提取 Agent 只输出结构化契约：

```json
{
  "requirement_id": "REQ-CANCEL-002",
  "status": "ACCEPTED",
  "statement": "SHIPPED 订单取消返回 409，订单状态保持不变",
  "source_refs": [
    "PRD-v3#R17",
    "OPENAPI-v7#/cancel/responses/409"
  ]
}
```

模型没有看到退款时限，因此该字段必须放入 `unknowns`。不能填 24 小时、48 小时或“尽快”。Structured Outputs 可以约束 JSON 形状，但不能证明 statement 的业务含义正确；契约还要经过引用校验和领域 owner 复核。

负控制：

```bash
python3 pipeline.py reset
python3 pipeline.py inject-unsupported-rule
python3 pipeline.py validate-contract
```

校验器指出 `refund_timeout_hours` 没有来源，并返回 `BLOCKED`。

## 第三课：把评审问题变成可关闭工件

课程不接受“请完善异常场景”。评审问题必须带证据、影响、owner 和关闭条件：

```json
{
  "question_id": "RQ-007",
  "type": "SOURCE_CONFLICT",
  "question": "订单进入 SHIPPED 后是否仍允许取消？",
  "source_refs": ["PRD-v3#R17", "TECH-a13f#S04"],
  "impact": "决定 409 用例、退款副作用与仓配回滚",
  "owner": "product-owner-order",
  "status": "OPEN",
  "close_with": "批准后的 PRD 段落和 Requirement Contract 新版本"
}
```

关闭问题会生成新契约版本。旧版本标记 `SUPERSEDED`，不覆盖历史。

## 第四课：先做风险策略，再生成用例

测试负责人从业务失败出发：重复退款、越权取消、已发货仍取消、账本与订单状态不一致。每个高风险必须映射到测试层级、Oracle、监控和 owner。

例如重复退款不需要首先写十条 UI 用例。它更适合在组件和服务集成层验证：

```text
refund_operation_count(order_id) <= 1
refund_total <= captured_amount
```

少量关键用户旅程进入 E2E。用例数量不作为覆盖证明。

## 第五课：固定独立 Oracle

AI 可以根据已批准契约生成候选 TestPackage，但不能从当前实现反向推导预期结果。已发货取消测试的关键部分是：

```json
{
  "test_id": "T-CANCEL-SHIPPED-01",
  "requirement_ids": ["REQ-CANCEL-002"],
  "risk_ids": ["RISK-INVALID-STATE"],
  "fixture": {"owner": true, "state": "SHIPPED"},
  "expected": {"status_code": 409, "refund_count": 0, "state": "SHIPPED"}
}
```

HTTP 200/202 不是业务正确性的充分证据。状态、账本、事件和权限才是关键 Oracle。

## 第六课：接入自动化适配器

TestPackage 再转成 API、契约、集成或 UI 测试。生成器只读取已批准工件，不修改 Oracle。代码审查要找空断言、吞异常、自动 skip、固定 sleep 和 healer 放宽业务断言。

每个函数保留：

```text
test_id -> requirement_ids -> risk_ids -> oracle_ids -> source_refs
```

因此需求或接口变化后，可以按业务影响选择回归集，而不是只按文件名猜测。

## 第七课：保存运行证据

每次运行保存代码、需求 baseline、测试包、数据和实现 hash，以及 selected tests、skip、retry 和原始结果。状态分为 `PASS`、`PRODUCT_FAIL`、`TEST_FAIL`、`ENV_BLOCKED` 和 `UNKNOWN`；证据不足时不能强制判绿。

## 第八课：跑完整三态实验

```bash
python3 pipeline.py reset
python3 pipeline.py all --report reports/baseline.json
python3 pipeline.py inject-code-defect
python3 pipeline.py all --report reports/mutation.json
python3 pipeline.py repair
python3 pipeline.py all --report reports/repair.json
```

本地实跑结果为：

| 阶段 | 退出码 | 结果 | 关键证据 |
| --- | ---: | --- | --- |
| Baseline | 0 | PASS | 三条测试通过 |
| Mutation | 1 | FAIL | `T-CANCEL-SHIPPED-01` 期望 409、实际 202 |
| Repair | 0 | PASS | 同一测试包重新通过 |

这证明测试对一个已知缺陷有检测力。它不证明模型能正确解析真实企业 PRD，也不证明生产发布安全。

## 学员实操

- Test Basis Pack；
- Requirement Contract；
- Review Question Pack；
- Risk Test Plan；
- TestPackage 与 Oracle；
- 自动化追溯索引；
- baseline、mutation、repair 三份 Run Manifest；
- Evidence Pack 和一次 Impact Set。

## 验证标准

评分不看文档长度，检查四件事：冲突是否阻断、关键规则是否有来源、已知缺陷是否变红、发布决定是否仍由具名责任人承担。

## 证据边界

已完成确定性离线夹具的 `PASS → FAIL → PASS`，并验证文档冲突返回 `BLOCKED`。没有调用真实模型、真实支付服务或企业文档；没有完成从业者盲评、学员效果和生产缺陷发现率验证。
