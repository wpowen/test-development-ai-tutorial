# TD-PS10 Task Prompt v1.0.0

控制问题：怎样证明每层 deadline 和 retry budget 有界，过载时安全拒绝或只读降级，恢复后不会产生洪峰与重复副作用？

业务场景：订单助手依赖模型、检索和退款工具，局部超时可能触发多层重试与队列级联

方法选择：deadline 传播控制等待，指数退避+jitter 降低同步重试，retry budget 限制放大，熔断和 load shedding 保护容量，只读 fallback 保护资金副作用

请读取固定 input fixture，只输出符合 schema 的 test_package。每条 test 必须含 risk_id、source_refs、method_reason、oracle_id、fixture、expected、fault、evidence 和 human_gate。读取依赖图、deadline、retry policy、队列和副作用规则，生成故障矩阵与降级断言；禁止建议无限重试或放宽写权限。资料没有说明的字段写 UNKNOWN；冲突写 BLOCKED；不得新增业务规则、权限、阈值或生产命令。
