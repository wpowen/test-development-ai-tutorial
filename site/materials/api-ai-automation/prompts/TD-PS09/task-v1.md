# TD-PS09 Task Prompt v1.0.0

控制问题：怎样在不发生 coordinated omission 的前提下测量队列、TTFT、TPOT、E2E、任务质量与成本，并给出容量而非单次速度？

业务场景：客服 Agent 同时处理 FAQ 和高风险退款长对话，包含检索和工具 fan-out

方法选择：open-loop arrival 保持外部到达，closed-loop 诊断单用户上限，分阶段 Trace 定位 queue/model/tool，风险切片阻止均值掩盖，Goodput 将质量安全纳入容量

请读取固定 input fixture，只输出符合 schema 的 test_package。每条 test 必须含 risk_id、source_refs、method_reason、oracle_id、fixture、expected、fault、evidence 和 human_gate。从 workload、任务切片、SLO 和成本模型生成 open/closed 场景、阶段指标和容量判定；禁止发明通用阈值或忽略失败成本。资料没有说明的字段写 UNKNOWN；冲突写 BLOCKED；不得新增业务规则、权限、阈值或生产命令。
