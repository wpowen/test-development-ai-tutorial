# TD-A03 task prompt v1

读取批准的 `TD-A03` 输入，只生成能回链 source_ref 的候选。控制问题：怎样让 TTFT、TPOT、ITL、Goodput 和 cost_per_success 的时间点、分母、切片与质量条件都可重算？ 方法：从请求、首 Token、逐 Token 和终态时间戳计算延迟；Goodput 只计质量、安全、完整性和 SLO 同时合格的请求。 Oracle：TTFT、TPOT、ITL 可由原始事件重算；Goodput 分母含所有到达；单位成功成本含失败和重试。 输出严格满足 Schema。
