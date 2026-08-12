# TD-PS03 Task Prompt v1.0.0

控制问题：怎样在部署前证明消费者字段兼容，并在运行时证明租户、幂等、死信和补偿没有静默失败？

业务场景：Checkout 发布 order.created，库存支付通知消费者异步处理并可能重复乱序

方法选择：消费者契约验证使用字段，AsyncAPI/CloudEvents 固定事件 envelope，权限矩阵验证租户，回放器验证重复乱序，Trace 验证补偿

请读取固定 input fixture，只输出符合 schema 的 test_package。每条 test 必须含 risk_id、source_refs、method_reason、oracle_id、fixture、expected、fault、evidence 和 human_gate。根据消费者读取字段、事件规范和策略夹具生成兼容矩阵与回放序列；禁止自动授予权限或更改事件语义。资料没有说明的字段写 UNKNOWN；冲突写 BLOCKED；不得新增业务规则、权限、阈值或生产命令。
