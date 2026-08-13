# 样例输入：订单取消与退款

夹具使用的六份输入位于 `examples/`，全部为合成数据，不含任何真实个人信息、支付账号或密钥。

## 业务设定

买家可以取消未发货订单；已支付订单取消后异步退款。设定中**故意保留一处冲突**：PRD 禁止已发货订单取消，旧技术方案仍写 `SHIPPED` 可取消。正确处理不是让模型选一个更合理的说法，而是把该条标成 `BLOCKED` 并指名升级责任人。

## 六份输入

| 文件 | 内容 | 对应阶段 |
| --- | --- | --- |
| `examples/source-manifest.json` | 5 份来源（PRD、技术方案、OpenAPI、状态机、模型清单）含版本、owner、hash、敏感级、优先级；2 条 `UNKNOWN` | S1 |
| `examples/requirement-contract.json` | REQ-CANCEL-001 的完整契约，含不变量、异常、副作用、未知与语义复核署名 | S2 |
| `examples/risk-register.json` | 7 条风险，含 3 类 AI 特有风险源与 1 条带具名接受人的降档记录 | S4 |
| `examples/oracle-design-record.json` | 6 条 Oracle 记录，标注层组合、独立来源与明确排除的层 | S5 |
| `examples/run-receipts.json` | baseline / fault / repair 三段收据，含 lineage 五要素 | S8 |
| `examples/waivers.json` | 1 条有效 Waiver，含补偿控制、过期时间与回滚条件 | S9 |

## 关键字段速查

```text
source-manifest   baseline_id / frozen_at / precedence_rule / conflicts[] / unknowns[]
requirement       status / invariants[] / side_effects[] / unknowns[] / semantic_review
risk              impact × likelihood × detectability = rpn / tier / layer / oracle_source
oracle            oracle_layers[] / independent_sources[] / excluded_layers[] / blocker
run receipt       phase / model / dataset_version / prompt_version / failed_oracle_ids / verdict
waiver            compensating_controls[] / expires_at / on_expiry / rollback_condition
```

## 替换成你自己的输入

保持字段结构不变，替换业务对象、来源 ID、风险内容与 Oracle 来源。至少要改两处配置：`baseline_id` 与 `precedence_rule`（来源优先级规则是你组织特有的，不能照抄）。
