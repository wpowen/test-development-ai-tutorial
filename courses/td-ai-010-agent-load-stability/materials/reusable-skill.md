# 可复用 Agent 性能与稳定性 Skill

## 输入

目标 Agent 的任务切片、允许终态、模型/工具路径、真实或预测到达分布、资源与业务预算、遥测字段、权限和事故历史。

## 工作流

1. 建 workload 与业务 Oracle；2. 建指标字典；3. 锁 Trace Schema；4. 对照 open/closed；5. 找 synthetic 容量边界并归因；6. 注入 timeout/retry/degrade 故障；7. 做 soak 与快照差分；8. 定义 SLO/告警/Runbook；9. 用 baseline/fault/repair 和事故回流持续回归。

## 输出

版本化 profile、Prompt/Input/Schema/Eval/Mutation、Lab Manifest、task traces、gate summary、Evidence/Inference/Unknown 证据卡和责任人批准记录。

## Fail-closed

缺业务 Oracle、缺版本、fault 未红、repair 删除 gate、真实副作用未隔离、Prompt 越权或把 synthetic 写成 production capacity 时停止。

