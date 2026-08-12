# TD-T18 Browser Agent 证据链 / task / v1.0.0

planner 风险 ID、generator 业务 Oracle、浏览器 Trace 与后端变异共同证明检测力；只看按钮可见不合格。

处理固定 input.json：1) 校验输入 schema 与版本；2) 检查安全/权限是否先于动作；3) 运行本页独立 Oracle；4) 输出 failed_oracle_ids 与 evidence_refs；5) 给出可逆 repair、rollback 和 human_review_required。只输出满足 output.schema.json 的 JSON，不声称调用了外部系统。
