# 需求契约填写指南

配套 Schema：`schemas/requirement-contract.schema.json` ｜ 填写样例：`examples/requirement-contract.json`

## 1. 字段为什么存在（不是为了好看）

| 字段 | 支持的下游能力 | 缺失的后果 |
| --- | --- | --- |
| actors | 权限测试、越权用例 | 漏测越权 |
| preconditions | 前置状态构造、非法前置用例 | 用例无法自动准备数据 |
| trigger | 接口/事件定位 | 无法映射到自动化 |
| state_transitions | 状态转换测试 | 漏测非法转换 |
| invariants | 属性测试、变形测试、对账 | 无法写"永远成立"的断言 |
| exceptions | 负例设计、错误码契约 | 只测 happy path |
| side_effects | 幂等测试、副作用观察点 | 漏测重复副作用 |
| nfrs | 性能/容量/可用性测试 | 非功能无人负责 |
| unknowns | 阻断下游、生成待确认清单 | 模型替你补写规则 |
| source_refs | 追溯矩阵、变更影响分析 | 无法回答"这条从哪来" |

## 2. 状态取值

```
ACCEPTED  有来源支持，结构与语义均通过
UNKNOWN   文档未定义；不得补写
BLOCKED   多源冲突 / 关键状态不可观察 / 越权
```

## 3. 两道门禁必须分开留痕

| 门禁 | 检查 | 记录位置 |
| --- | --- | --- |
| A `PASS_SCHEMA` | 字段/类型/枚举/必填；source_refs 在当前 baseline 中存在 | 自动，写入报告 |
| B `PASS_SEMANTIC` | statement 与不变量被原文支持；AI 未越权补充；关键金额/权限/状态由领域 owner 逐项确认 | 人工，署名 |

**A 通过不代表 B 通过。合并成一个"通过"是本阶段最常见的事故来源。**

## 4. 提取 Prompt 的权限声明（可直接抄进 System 段）

```
角色：需求证据提取器。你只整理已提供的资料，不决定业务规则。
规则：
1. 每项事实必须给出 source_refs；没有引用则删除该事实。
2. 文档没有说明的内容写入 unknowns，不得补写。
3. 两个有效来源冲突时写入 conflicts，status=BLOCKED。
4. 只输出给定 JSON Schema；不要输出摘要、建议或测试用例。
5. 不处理任何生产密钥、真实支付账号或未脱敏个人信息。
```

⚠ 禁止出现："综合判断后采用更合理的规则"。

## 5. 常见填写错误

| 错误 | 为什么错 | 正确做法 |
| --- | --- | --- |
| invariants 写成"系统应稳定" | 不可判定 | 写 `refund_count <= 1` |
| unknowns 为空 | 真实需求不可能全部明确 | 至少找出一条 |
| 把技术实现写进 statement | 实现选择不是需求 | 移到 technical-contract |
| source_refs 指向"PRD" | 粒度太粗，无法定位 | 指向 `PRD-v3#R17` |
| exceptions 只写错误码 | 缺触发条件 | 写 `SHIPPED -> 409` |
