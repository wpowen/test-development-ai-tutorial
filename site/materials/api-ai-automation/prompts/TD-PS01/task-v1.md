# TD-PS01 Task Prompt v1.0.0

控制问题：怎样证明 202 响应、订单状态、退款账本和事件消费属于同一次合法取消，而不是只证明 HTTP 成功？

业务场景：已支付未发货订单取消后异步退款，客户端超时重试不能生成第二笔退款

方法选择：分层使用 HTTP 语义、OpenAPI Schema、领域状态机、副作用账本和 Trace；因为任一单层都无法证明异步资金结果

请读取固定 input fixture，只输出符合 schema 的 test_package。每条 test 必须含 risk_id、source_refs、method_reason、oracle_id、fixture、expected、fault、evidence 和 human_gate。从 OpenAPI、状态机和账本夹具生成带 source_ref 的四层 API 测试包；未知规则输出 UNKNOWN，冲突输出 BLOCKED。资料没有说明的字段写 UNKNOWN；冲突写 BLOCKED；不得新增业务规则、权限、阈值或生产命令。
