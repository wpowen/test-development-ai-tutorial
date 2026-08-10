# Reusable Skill：API candidate-to-gate

## 输入

只接受已批准、已版本化、已脱敏的 OpenAPI/JSON Schema、业务状态规则、权限矩阵、事件规则和历史失败 trace。

## 输出契约

对每个候选输出：`case_id`、`operation_id`、`preconditions`、`steps`、`assertions`、`oracle_id`、`source_refs`、`risk`、`confidence`、`side_effect_policy`。未通过 schema、operation、权限或副作用 policy 的候选保持 `CANDIDATE`，不得进入 required gate。

## 操作循环

`parse -> generate candidates -> independent Oracle review -> sandbox execute -> mutation/replay -> human promote`。AI 可抽取、生成、聚类和归因；不能从被测实现反推 Oracle、批准发布、修改阈值或触发真实破坏性操作。

## 迁移检查

替换业务状态、角色、事件、幂等语义、数据隔离、owner 和阈值；保留版本/hash、独立 Oracle、红绿闭环和 `UNKNOWN/BLOCKED/NOT_RUN` 状态。
