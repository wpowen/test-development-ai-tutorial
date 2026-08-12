# TD-PS11 Task Prompt v1.0.0

控制问题：怎样让 symptom、fault event、跨服务 Trace、质量切片和恢复检查属于同一证据链，并在 telemetry 缺失时保持 UNKNOWN？

业务场景：生产客服 Agent 质量下降可能来自索引、工具、模型、队列或观测丢失，需要在隔离范围内验证

方法选择：OTel/W3C 传播连接任务，版本字段区分变化，trace completeness 先验证观测能力，Chaos Experiment Card 固定授权和 blast radius，单变量注入支持归因

请读取固定 input fixture，只输出符合 schema 的 test_package。每条 test 必须含 risk_id、source_refs、method_reason、oracle_id、fixture、expected、fault、evidence 和 human_gate。读取 Trace schema、脱敏策略、实验授权和 SLO，输出单变量实验卡、观测字段、停止条件与复验；生产 selector 缺失时必须 BLOCKED。资料没有说明的字段写 UNKNOWN；冲突写 BLOCKED；不得新增业务规则、权限、阈值或生产命令。
