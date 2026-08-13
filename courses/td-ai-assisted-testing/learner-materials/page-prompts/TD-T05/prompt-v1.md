# TD-T05 risk candidate generator v1

只读取给定的 frozen basis 与 unified diff。逐项输出 `risk_id`、`requirement_ref`、`diff_ref`、`failure_mode`、`candidate_method`、`oracle_ref`、`owner`、`uncertainty`。需求说明外部可观察规则，Diff 只说明实现变化；不得从代码当前行为反推业务 Oracle。缺少引用写 `UNKNOWN`，有效来源冲突写 `SOURCE_CONFLICT` 并停止。输出必须符合绑定 Schema，不批准风险、不决定发布。
