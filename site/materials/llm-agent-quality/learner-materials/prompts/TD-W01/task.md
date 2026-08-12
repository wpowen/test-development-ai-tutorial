# TD-W01 Agent/Worker/Workflow 边界 / task / v1.0.0

按下一步控制权、状态 owner、队列和副作用区分组件，不按营销命名或是否含模型猜测。

处理固定 input.json：1) 校验输入 schema 与版本；2) 检查安全/权限是否先于动作；3) 运行本页独立 Oracle；4) 输出 failed_oracle_ids 与 evidence_refs；5) 给出可逆 repair、rollback 和 human_review_required。只输出满足 output.schema.json 的 JSON，不声称调用了外部系统。
