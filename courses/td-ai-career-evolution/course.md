# AI 测试工程师职业演进：责任、指标与可复用证据

这门六页课把职业演进、能力自评、组织适配、任务指标、AI 提效和资源路线改写成小白可以跟做、专家可以复核的证据链。每页都包含白话定义、反例、版本化 Prompt/Input/Schema/Eval/Mutation、精确命令和 `baseline -> fault -> repair = 0/1/0`。

## AI centrality

AI 是被测边界的一部分，而不是课末的工具清单。学员必须把传统测试能力迁移到 Prompt、模型、数据集、Eval、Judge、Trace、工具权限、成本、漂移和版本回滚。AI 可生成候选与聚合证据，但不能定义业务规则、替代独立 Oracle、批准 waiver、猜组织职级或承担发布责任。移除 AI 质量流水线后，任务指标、生成用例提效和 AI 能力迁移的核心对象不存在。

## System under test

被测系统是受控、脱敏的职业证据与 AI 质量工作流：输入需求和技术上下文，选择风险和任务族，创建独立 Oracle 与 Metric Card，运行版本化 Prompt/Input/Schema/Eval/Mutation，保存责任地图、自评计划、组织适配、提效报告和资源索引，最后交给具名人类负责人决定。离线夹具不连接真实模型、公司 policy、生产工具或招聘系统。

## Baseline and target

基线是用年限/头衔猜能力、把 F1/QPS/ROUGE 当万能指标、把候选数量当 AI 提效、让模型自评正确，或把课程完成数写成 P5–P9。目标是每个主张都有 evidence_ref 或 UNKNOWN，每个指标有分母/切片/Oracle/owner/失败动作，每个提效结论有同任务 baseline、Mutation kill 和 reviewer，每个组织映射有 policy、版本和生效日期。

## Commands

从公开学习包根目录运行；命令不需要密钥、网络、Provider、模型或 GPU。

```bash
cd learner-materials
python3 scripts/career_evolution_lab.py --manifest manifests/TD-C02.json --mode cycle
python3 scripts/career_evolution_lab.py --manifest manifests/TD-C03.json --mode cycle
python3 scripts/career_evolution_lab.py --manifest manifests/TD-C04.json --mode cycle
python3 scripts/career_evolution_lab.py --manifest manifests/TD-F05.json --mode cycle
python3 scripts/career_evolution_lab.py --manifest manifests/TD-T26.json --mode cycle
python3 scripts/career_evolution_lab.py --manifest manifests/TD-R01.json --mode cycle
```

每个 cycle 的内部退出码必须为 `[0,1,0]`；外层退出 0 只表示离线夹具检测力通过。

## Metrics and thresholds

责任页检查状态、决策权、失败代价、工件和 reviewer 完整率；自评页检查 evidence_refs、UNKNOWN、缺口路由和 30/60/90 工件；组织页检查 source/owner/version/effective_from；任务页检查 population、denominator、slices、Oracle、uncertainty、owner 和 failure_action；提效页检查 accepted-test、Mutation kill、time、cost、defect yield；资源页检查 version、checked_at、purpose、limits、fallback 和 exit_artifact。夹具数字只证明字段级检测力，不是行业、生产、绩效、薪资或晋升阈值。

## Failure injection

每个 manifest 的 `fault_patch` 只改声明的观察字段：删除 evidence_refs、计划、分母、独立 Oracle、Mutation kill、检查日期或 fallback。预期 fault 进程 exit 1、报告 verdict=FAIL 并显示 expected/actual；修复只能恢复批准观察，不能改 expected、删除检查、让 AI 自己当 Oracle 或吞掉 exit 1。若 fault 不变红，教学资产没有检测力，必须阻断。

## Human review gate

AI 质量负责人确认风险、指标分母、Oracle 来源、阈值依据、owner、waiver 到期和回滚条件；业务 owner 裁决业务规则；测试开发提供独立证据；组织内部 policy owner 决定 P5–P9 映射；招聘方独立决定岗位、绩效、薪资和录用。没有具名来源时 `INTERNAL-UNKNOWN/BLOCK` 是正确结果。

## AI-specific failure boundary

模型可能发明内部流程、把最终答案当事实、隐藏文档冲突、产生共同失败的 Oracle、泄漏敏感数据或建议无限授权。Prompt 包固定 `provider=none`、`model_execution=NOT_RUN`；Schema 通过不等于模型效果通过，离线红绿不等于 live、practitioner 或 production 通过。所有组织阈值、band、晋升和就业结论必须由外部 owner 重新取证。

## Learner artifact

学员交付六件可迁移工件：`responsibility-map.json`、`capability-self-assessment.json + 90-day-evidence-plan.md`、`organization-level-adapter.yaml`、`task-metric-card.yaml`、`productivity-experiment-report.json`、`resource-index.json`。每件工件都要有消费者、owner、版本、限制、失败动作和下一次复评；复制到新场景前只能修改明确的 editable fields。

## Evidence status

当前为 `fixture-tested`。六页 Python 标准库 runner 已本地证明 baseline=0、fault=1、repair=0，并保存逐页报告、输入 hash 和 manifest hash；zip 已通过完整性检查。真实 Provider、模型、组织 policy、生产流量、从业者评审、学习效果、晋升和就业结果均为 NOT_RUN/UNKNOWN，不得升级为 PASS-LIVE、PASS-PRACTITIONER 或完整生产课程。
