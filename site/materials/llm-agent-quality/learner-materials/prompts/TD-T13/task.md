# TD-T13 版本 A/B 可比性 / task / v1.0.0

只比较一个版本变量，冻结数据、Prompt、检索、工具、Scorer 与预算；高风险 blocker 优先于平均分。

处理固定 input.json：1) 校验输入 schema 与版本；2) 检查安全/权限是否先于动作；3) 运行本页独立 Oracle；4) 输出 failed_oracle_ids 与 evidence_refs；5) 给出可逆 repair、rollback 和 human_review_required。只输出满足 output.schema.json 的 JSON，不声称调用了外部系统。
