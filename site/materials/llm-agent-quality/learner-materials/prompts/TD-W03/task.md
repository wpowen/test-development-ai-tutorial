# TD-W03 单/多 Agent 公平实验 / task / v1.0.0

固定模型、总 Token、工具权限、任务集、重试和人工干预，多次运行后比较分布与单位成功成本。

处理固定 input.json：1) 校验输入 schema 与版本；2) 检查安全/权限是否先于动作；3) 运行本页独立 Oracle；4) 输出 failed_oracle_ids 与 evidence_refs；5) 给出可逆 repair、rollback 和 human_review_required。只输出满足 output.schema.json 的 JSON，不声称调用了外部系统。
