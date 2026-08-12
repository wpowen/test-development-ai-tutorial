# TD-PS08 Task Prompt v1.0.0

控制问题：怎样证明迁移前后行数、键、金额、状态语义和 CDC offset 一致，并在部分失败时安全停止或回滚？

业务场景：订单表从 status 字符串迁移到 status_code 与状态维表，同时进行双读、回填和 CDC

方法选择：expand-contract 降低兼容风险，约束与 checksum 验证静态完整性，分片回填和高水位验证进度，CDC 对账处理并发变化，影子读比较语义

请读取固定 input fixture，只输出符合 schema 的 test_package。每条 test 必须含 risk_id、source_refs、method_reason、oracle_id、fixture、expected、fault、evidence 和 human_gate。读取 DDL、数据字典、约束、回填计划和 CDC manifest，输出前置检查、分片 Oracle、停机条件、回滚与对账 SQL；不得建议直接 DROP 生产列。资料没有说明的字段写 UNKNOWN；冲突写 BLOCKED；不得新增业务规则、权限、阈值或生产命令。
