# AI Agent 测试架构系统：D0-D7 与四证据环

## 课程结果

这是一条面向小白的 11 页实践链：先把 Agent 的组件、状态、权限和副作用画清楚，再按 D0–D7 和四证据环选择 Oracle。完成后，学习者能够把一个“最终回答看起来正确”的 Agent 拆成可观测的 outcome、step、trajectory、handoff、budget、安全和治理证据，并交付独立 Oracle、Metric Card、0/1/0 报告和迁移清单。当前课程只证明确定性离线 fixture 可重放；真实模型、企业集成、从业者和学习者证据均为 NOT_RUN。

## 学习者与前置条件

适合第一次系统学习 AI Agent 测试、会读 JSON/命令行并了解基本测试用例的测试开发新人。前置只要求 Python 3.9+ 标准库和“输入—动作—预期—失败”思维；不要求 API Key、模型额度、MCP、浏览器、队列或金融账户。先阅读 `materials/README.md`、`materials/beginner-reuse-checklist.md`，再按 TD-AG-00 → TD-AG-10 顺序学习。

## AI centrality

AI 是被测系统的一部分，而不是装饰性的写作助手：Judge、轨迹、工具调用、委托、状态记忆、预算和业务治理都会改变行为。模型只能提出候选证据或修复，不能批准自己的 Oracle、改变 expected、扩大权限、解除 blocker 或发布。独立策略 Oracle 与具名人工 owner 必须在模型外成立。

## System under test

被测边界包含输入/风险、模型或 Agent、Workflow/Worker、工具 schema、身份/tenant/scope、检索与记忆、队列和状态、人工交接、业务终态以及不可逆副作用。先看架构图，再决定测试层：D0 测评估器，D1 测 span，D2 测编排，D3 测人机控制，D4 测可靠性分布，D5 测安全，D6 测经济性，D7 测业务治理。

## Baseline and target

每页都有同一确定性合同的 baseline → fault → repair：baseline 退出 0，命名故障退出 1，恢复同一合同后退出 0。target 不是“分数变高”，而是故障能被独立 Oracle 稳定杀死、证据可回指、owner 和 stop_state 完整。任何高危 blocker、D0 评估失效、权限缺失或统计证据不足都 fail-closed。

## Commands

在课程包根目录执行以下命令，不需要 API Key：

```bash
python3 lab/agent_architecture_lab.py --topic TD-AG-00 --phase baseline --report lab/reports/td-ag-00/baseline.json   # 退出 0
python3 lab/agent_architecture_lab.py --topic TD-AG-00 --phase fault --report lab/reports/td-ag-00/fault.json       # 退出 1，这是预期红灯
python3 lab/agent_architecture_lab.py --topic TD-AG-00 --phase repair --report lab/reports/td-ag-00/repair.json     # 退出 0
```

也可以运行整页 cycle：

```bash
python3 lab/agent_architecture_lab.py --topic TD-AG-06 --phase cycle --report-dir lab/reports/td-ag-06
```

cycle 必须输出 `observed_exit_codes=[0,1,0]`，并生成 `baseline.json`、`fault.json`、`repair.json` 和 `cycle-summary.json`。TD-AG-00 至 TD-AG-10 只替换 `--topic`，不要改 expected 或吞掉故障。

## Metrics and thresholds

指标必须写入场景化 Metric Card，包含 population、分母、版本、workload、状态重置、owner、统计方法和失败动作。D4 区分 pass@k 与 pass^k，按任务聚类而不是把重复运行当作独立样本；D6 分开 P95/P99、goodput、步骤成本和成本尾部；D5 的 ASR/阻断率必须带攻击总体和暴露量。示例数值不是通用门槛，不能跨业务或版本搬运。

## Failure injection

每页的 runner 注入一个命名故障：例如删除 D0 Oracle、增加禁止工具调用、破坏 handoff stop reason、关闭 tenant isolation、移除 hard budget 或绕过 business rule。fault 报告必须返回 `verdict=FAIL`、非零退出码和 `failed_oracle_ids`；repair 只恢复 canonical state，不能调低阈值、删 Oracle、扩大权限、增加无限重试或把 NOT_RUN 改成 PASS。

## Human review gate

客服 Agent 产品与质量负责人拥有业务 Oracle、权限、风险接受、回滚和发布决定。人工审核必须读取原始输入、版本、trace/span、工具参数、失败 Oracle、成本和 residual risk；模型、Judge、healer 或 reviewer Agent 不能批准自己的期望、waiver 或发布。四证据环之间不能越级：离线 fixture 通过不代表沙箱、影子或线上通过。

## AI-specific failure boundary

本包未调用真实 provider/model、浏览器、MCP、队列、交易后端或线上流量。确定性 runner 只证明声明的 mutation 可被独立 Oracle 稳定检测；不证明模型质量、实时延迟、真实安全、生产容量、从业者可用性或学习效果。缺输入、owner、Oracle、统计单位或回滚证据时，结论保持 `UNKNOWN`、`BLOCKED` 或 `NOT_RUN`。

## Learner artifact

学习者最终交付：D0–D7 架构图、风险登记册、Metric Card、Judge Card、trajectory ledger、handoff contract、安全套件、四环 release plan、baseline/fault/repair receipts 和迁移清单。迁移到内部事故总结 Agent 时必须重新定义业务 Oracle、风险切片、工具权限、owner、数据边界和回滚；不能只替换标题或复制示例阈值。

## Evidence status

当前成熟度为 `fixture-tested`。标准库 runner 的 11 个 topic 均已重放为 `0/1/0`；模型、真实 Agent/工具、MCP/浏览器/队列、线上 shadow/online、从业者评审和学习者迁移均 `NOT_RUN`。在所有缺失证据补齐前，不得写成 live-tested、practitioner-reviewed、production-validated 或完整课程。
