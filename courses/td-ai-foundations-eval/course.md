# 测试开发的 AI 基础与 Eval 基础

面向能读懂普通测试报告、第一次系统进入 AI Quality 的测试开发。本课程不把大模型讲成神秘黑盒，也不让学员停留在 Prompt 抄写：12 页先从完整 Prompt Package 入门，再沿着模型生命周期、Token/Context/非确定性、LLM/RAG/Agent/Workflow 结构，进入 Eval Contract、Dataset/Slice/Holdout、Composite Oracle、重复运行统计，最后关闭 RAG 语料、检索、Faithfulness、无答案与权限 Gate。

## AI centrality

移除 AI 系统后，这组课的核心问题消失：概率生成、有限 Context、外部检索、模型 Judge、Agent 工具选择、RAG 忠实性和 no-answer 都是 AI 特有或因 AI 被重新定义的质量对象。传统风险、Oracle、变异与发布责任仍保留，但数据、Trace、版本和证据结构发生扩张。

## System under test

被测对象是一个合成退款助手的 AI 质量合同，而不是某家 Provider。边界包含版本化模型/Prompt/Context/语料/工具 Manifest、Eval dataset、Composite Oracle、RAG 检索与声明证据、权限/无答案策略，以及人工发布 Gate。默认适配器是 Python 标准库确定性 Fixture；真实模型适配器保持 NOT_RUN。

## Baseline and target

基线是“一次聊天看起来正确”与没有版本、分母、切片和 owner 的模糊报告。目标是每个决策都能回到风险、case、版本、Oracle、raw evidence、红灯、修复和具名责任人。Fixture 目标是稳定产出 `0→1→0`，并在报告中明确 `model_execution=NOT_RUN`。

## Commands

从课程实验目录运行端到端 RAG 权限 Gate：

```bash
cd courses/td-ai-foundations-eval/lab
python3 scripts/run_lab.py --topic TD-T12 --phase baseline
python3 scripts/run_lab.py --topic TD-T12 --phase fault
python3 scripts/run_lab.py --topic TD-T12 --phase repair
```

预期退出码依次为 0、1、0，报告写入 `reports/TD-T12/`。其他十一页只需替换 `--topic`，精确命令由各页 Manifest 固定。

## Metrics and thresholds

每页指标都声明分母、聚合、风险切片、来源点和失败动作。Fixture 的阈值是三个精确字段全部匹配，且注入的高风险字段必须变红；这只测 mutation detection。生产阈值不得复用教学数字，必须由真实错误成本、流量分布、人工校准与 AI 质量负责人批准。Blocker 不参与平均抵消。

## Failure injection

TD-T12 fault 把 `acl_denied` 从 true 改为 false，模拟无答案时扩大权限并读取其他租户证据。检查器必须 `exit 1`、`verdict=FAIL`，保存 expected/actual 和 mutation ID。任何吞掉 non-zero、删除 case、改变 expected 或把 FAIL 写成 warning 的做法都不算修复。

## Human review gate

AI 可以提取候选合同、运行确定性检查并整理报告；不能发明政策优先级、批准阈值、接受残余风险、扩大权限或决定发布。真实上线前需要 AI 质量负责人、业务政策 owner 和安全 owner 检查数据代表性、权限、Judge 校准、waiver 与回滚。

## AI-specific failure boundary

课程覆盖 Context 截断与位置、非确定性、检索 miss、旧语料、unsupported claim、引用错配、无答案强答、跨租户访问、Judge 自证和 Agent 副作用。它不覆盖真实 Provider 内部路由、企业身份链、向量库、线上分布、生产 SLO 或攻击面的完整渗透测试，这些保持 UNKNOWN/NOT_RUN。

## Learner artifact

学员交付版本化 Eval Contract、12 条风险切片数据卡、Composite Oracle 表、重复运行解释、RAG corpus manifest、query/gold 映射、claim-evidence 矩阵、权限攻击集以及 33 组红绿报告。最终迁移任务把退款助手改成事故总结助手，必须替换证据来源和权限模型，而不是只替换名词。

## Evidence status

当前状态为 `fixture-tested / PASS-FIXTURE`。构建器实际运行 12×3 条命令并保留收据；Prompt、Schema、eval、mutation 和 version manifest 可检查，但 model/provider execution 为 NOT_RUN。没有 live、practitioner 或 production 证据，也不声称完整发布门禁已通过。
