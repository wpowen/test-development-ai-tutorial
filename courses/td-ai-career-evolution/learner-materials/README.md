# 职业演进学习材料包

本包是离线 fixture 课程材料，不调用网络、密钥、模型、GPU 或公司内部 policy。Prompt 默认 `provider=none`、`model_execution=NOT_RUN`。Runner 只验证结构化观察和故障检测能力。

## 快速开始

```bash
python3 scripts/career_evolution_lab.py --manifest manifests/TD-C02.json --mode cycle
```

逐页运行时，`evidence/<PAGE>/cycle.json` 必须显示 `actual_exit_codes: [0, 1, 0]`。报告中的 `evidence_level` 永远是 `PASS-FIXTURE`，不能改写为 live、practitioner 或完整课程。

## 工件边界

`fixtures/` 是可脱敏的输入；`manifests/` 声明 Oracle、故障和未知边界；`prompts/` 只产生候选工件；`schemas/` 只保证结构；`evals/` 和 `mutation/` 定义可复核检查；`evidence/` 是本地运行收据。真实岗位、阈值、组织 band、薪资、晋升和就业结果必须由外部 owner 独立验证。

## 来源专属视觉

`source-visual-manifest.json` 是职业来源图的入口，`visuals/career-visual-source.json` 是可编辑语义源。九张 SVG 分别承接职责对比、五维思维导图、来源占比示例、证据生命周期、责任阶梯、证据雷达、参数化计划、背景路径和优先级象限；它们不是同一张通用流程图的换皮。

来源中的 30/25/25/15/5、P5-P9、固定年限和晋升周期只保留为 `SOURCE-EXAMPLE`。没有组织内部规则、适用岗位、版本和具名 owner 时，状态必须保持 `INTERNAL-UNKNOWN`，不得用于推断个人职级、晋升日期或就业结果。
