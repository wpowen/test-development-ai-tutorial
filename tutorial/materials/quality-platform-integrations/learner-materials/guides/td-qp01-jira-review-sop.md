# TD-QP01 Jira 基线与候选评审 SOP

验签原始 body 后写 Inbox，按 `source+id` 抑制重放，再回读 Jira issue/changelog。AI 可生成需求解析、风险和用例候选，但必须保存 model、prompt hash、revision 与 assumptions；质量负责人确认风险、Oracle 和人工 gate 后才允许执行。需求版本变化会 supersede 旧候选，不把评论或表情当审批。
