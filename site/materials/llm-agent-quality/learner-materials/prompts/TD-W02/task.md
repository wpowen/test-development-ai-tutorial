# TD-W02 状态、循环、重试、Handoff 与终止 / task / v1.0.0

重复投递只产生一次副作用；checkpoint、owner、预算上限、stop reason 和人工 handoff 必须可观察。

处理固定 input.json：1) 校验输入 schema 与版本；2) 检查安全/权限是否先于动作；3) 运行本页独立 Oracle；4) 输出 failed_oracle_ids 与 evidence_refs；5) 给出可逆 repair、rollback 和 human_review_required。只输出满足 output.schema.json 的 JSON，不声称调用了外部系统。
