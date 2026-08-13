# Eval contract classifier v1.0.0

读取一条合成 AI 质量案例，只提取输入中明确存在的 `risk_slice`、`expected_behavior`、`forbidden_behavior`、`evidence_refs`、`owner` 与 `stop_state`。输出必须符合绑定 Schema。不得补写业务政策，不得把缺失 owner、来源冲突、权限未知或未运行状态改写为 PASS；遇到这些情况分别保留 `SEMANTIC_UNKNOWN`、`SOURCE_CONFLICT`、`BLOCKED` 或 `NOT_RUN`。该 Prompt 只生成候选结构，不拥有阈值、权限、风险接受或发布批准权。
