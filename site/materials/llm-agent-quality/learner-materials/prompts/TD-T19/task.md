# TD-T19 自愈反作弊 / task / v1.0.0

healer 只可提出有证据的 locator 候选；不得删除 Oracle、改变期望或跳过步骤，且必须继续杀死原变异。

处理固定 input.json：1) 校验输入 schema 与版本；2) 检查安全/权限是否先于动作；3) 运行本页独立 Oracle；4) 输出 failed_oracle_ids 与 evidence_refs；5) 给出可逆 repair、rollback 和 human_review_required。只输出满足 output.schema.json 的 JSON，不声称调用了外部系统。
