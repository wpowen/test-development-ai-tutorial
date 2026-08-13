# AI 质量系统、Benchmark 与 Capstone

面向已经理解 AI/Eval 基础、希望把零散评测升级成工程质量系统的测试开发。十二页从 CI 分层门禁、版本 lineage、Trace-to-regression、质量/延迟/成本联合 Gate、漂移/waiver/回滚，进入 Benchmark 任务、数据、协议、Scorer、聚合、Split/Holdout、Metrics/CI、Harness 敏感性、污染/不确定性和公共到企业迁移，最后由 Capstone 消费全链工件。

## AI centrality

移除 AI 后，这门课的核心被测对象就不存在：Prompt、有限 Context、知识索引、模型 Judge、Agent 工具选择、Harness 协议敏感性、训练污染和 Token 成本都是 AI 系统新增或被重新定义的质量面。传统 CI、test basis、独立 Oracle、负控、回归和事故闭环仍保留，但必须扩张版本图、Trace 和统计证据。

## System under test

被测对象是一个合成退款 RAG+Agent 的版本化 release candidate，以及负责评测它的 CI/Benchmark 质量系统。边界包括 PRD/Risk、Dataset/Split、Prompt/Input/Schema、模型和知识/工具版本、Composite Oracle、Harness、逐题报告、质量/延迟/成本 Gate、waiver 与 rollback。真实模型、企业 CI、身份和副作用系统保持边界外。

## Baseline and target

基线是手工聊天抽查、浮动版本、只看平均分和没有退出码的假绿报告。目标是每个发布判断都能回到当前 SHA、完整 lineage、风险切片、逐条 raw evidence、独立 Oracle、首次红灯、修复和具名 owner。Fixture 目标严格限定为同一合同下稳定复现 `0→1→0`，不把本地绿灯写成模型或生产成功。

## Commands

从课程 lab 运行 Capstone 的三阶段合同；三条命令必须分别执行并立即检查退出码：

```bash
cd courses/td-ai-quality-benchmark/lab
python3 scripts/run_lab.py --topic TD-T25 --phase baseline
python3 scripts/run_lab.py --topic TD-T25 --phase fault
python3 scripts/run_lab.py --topic TD-T25 --phase repair
```

预期退出码依次为 0、1、0，报告位于 `reports/TD-T25/`。完整公开包对十二页共实际运行 36 条命令，并在 `run-receipts.json` 保存命令、预期/实际退出码和报告 SHA-256。

## Metrics and thresholds

每页指标必须声明单位、numerator、denominator、aggregation、risk slice、measurement point、version、owner 和 failure action。CI 先检查 blocker，再看风险切片阈值，最后才展示总体分；安全 blocker 不被简单样例平均抵消。质量、p95/p99 延迟和 cost-per-success 使用独立硬门禁。本地阈值只是三个固定字段精确匹配，不能复用为企业生产默认值。

## Failure injection

TD-T25 fault 将 `capstone_trace_complete` 从 true 改为 false，模拟 Capstone 只交最终绿报告却缺少全链 trace closure。脚本必须 `exit 1`、`verdict=FAIL` 并保存 expected/actual；baseline 与 repair 必须为 PASS。Repair 只能恢复 observation，不能修改 expected、删除 blocker、吞掉 non-zero 或把 FAIL 改成 warning。

## Human review gate

AI 的权限是“自动运行和比较评测，不得自动批准例外”。AI 可以整理候选合同、执行确定性检查和生成比较报告；AI 不能决定业务 Oracle、风险容忍、阈值、waiver、权限扩大、污染接受或发布。AI 质量负责人拥有阻断或批准有期限 waiver 的决定权，领域和安全 owner 必须复核各自规则。

## AI-specific failure boundary

课程覆盖 Prompt/模型/知识/工具版本漂移、Judge 波动、数据集泄漏、Harness 混杂、检索与工具 Trace 断链、总体均值掩盖 blocker、p99 与重试成本退化、waiver 永不过期以及隐藏测试污染。它不覆盖真实 Provider 内部路由、线上流量、企业 secret、身份链、生产副作用、完整攻击面或真实事故响应，这些保持 UNKNOWN/NOT_RUN。

## Learner artifact

学员交付分层 CI workflow、lineage graph、脱敏 Trace-to-regression 记录、质量/延迟/成本联合 Gate、漂移/waiver/rollback Runbook、Dataset Card、representative/challenge/regression/sealed-holdout 四类集合、Metric Card、Harness 单变量实验、污染审计、企业内部 Benchmark，以及 Prompt/Input/Schema/Eval/Mutation 包、36 条 receipts、bundle owners 和 ZIP hash closure。迁移挑战把退款助手换成事故总结助手，必须重做专业证据和权限而非只替换名词。

## Evidence status

当前状态是 `fixture-tested / PASS-FIXTURE release candidate`。证据只证明 Python 标准库 checker 能杀死十二个已声明 mutation，公开目录和 ZIP member 的 SHA-256 一致。Prompt 包的 provider=none、model=NOT_RUN；真实模型、RAG/Agent、企业集成、从业者评审、publication 与 production 全部 NOT_RUN。因此 Capstone 不能被表述为完整发布、生产就绪或从业者验证。
