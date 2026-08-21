# 脱敏练习输入

业务规则：每次 AI 组件变更必须比较黄金集分片，失败由 AI 质量负责人决定阻断或限时 waiver。技术设计：CI 读取 version manifest、运行 Eval、保存失败样例和报告。若需求说“业务 owner 放行”而技术设计写“脚本自动合并”，必须记录两条 locator、影响和待裁决人，状态为 BLOCKED。学员补充 actor、input、artifact、oracle、decision、consumer，并指出 provider、模型和内部权限均为 INTERNAL-UNKNOWN。
