# TD-T05 · Editorial research package

## Scope and lineage

本页索引 research-brief、source-pack、evidence-synthesis、engineering-blueprint、manuscript、comparison、research-runs 与 validation。研究事实必须回链打开来源；方法组合属于 Inference；真实仓库、模型或生产结果保持 Unknown/NOT_RUN。

## Editorial review

- 受保护专业细节：需求版本、设计冲突、代码 hunk、独立 Oracle 与 owner 引用。
- 方法选择理由：风险候选必须能同时回链 requirement_ref、diff_ref 与 oracle_id；缺一项就停止，而不是让模型补一条听起来合理的 SLA。
- 人工化检查：标题、场景、命令、预期退出码和失败诊断均绑定 TD-T05，没有用“AI 提效”或“自动覆盖”替代专业判断。
- 证据边界：本页只到 fixture-tested；没有 live 模型、真实项目集成、从业者签字、publication 或 production validation。

## Contract markers

Prompt、Input、Schema、Eval、Mutation 与 Critic 各自版本化；Oracle 位于生成器之外。validation.md 只保留研究覆盖、可追溯、实验、比较和发布裁决合同，不在本记录中推测编辑分数。
